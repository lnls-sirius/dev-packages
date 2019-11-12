"""Main cycle module."""

import sys as _sys
import time as _time
import logging as _log
import threading as _thread
from epics import PV as _PV
from siriuspy.namesys import Filter as _Filter, SiriusPVName as _PVName
from siriuspy.search import PSSearch as _PSSearch
from .conn import Timing, PSCycler, LinacPSCycler
from .bo_cycle_data import DEFAULT_RAMP_DURATION
from .util import get_sections as _get_sections, \
    get_trigger_by_psname as _get_trigger_by_psname

TIMEOUT_SLEEP = 0.1
TIMEOUT_CHECK = 20


class CycleController:
    """Class to perform automated cycle procedure."""

    def __init__(self, cyclers=dict(), timing=None,
                 is_bo=False, ramp_config=None, logger=None):
        """Initialize."""
        # cyclers
        self.cyclers = cyclers
        ps2cycle = self._psnames_2_cycle()
        ps2ramp = self._psnames_2_ramp()
        if cyclers and (ps2cycle and ps2ramp):
            raise Exception('Can not cycle Booster with other accelerators!')
        self._mode = 'Ramp' if ps2ramp else 'Cycle'

        if not cyclers:
            psnames = ps2ramp if is_bo else ps2cycle
            for name in psnames:
                if 'LI' in name:
                    self.cyclers[name] = LinacPSCycler(name)
                else:
                    self.cyclers[name] = PSCycler(name, ramp_config)

        # timing connector
        self._sections = _get_sections(self.psnames)
        self._only_linac = (len(self._sections) == 1) and \
                           (self._sections[0] == 'LI')
        # TODO: remove following lines when TI is ok for SI
        self._only_si = (len(self._sections) == 1) and \
                        (self._sections[0] == 'SI')
        # if not self._only_linac:
        if not self._only_linac and not self._only_si:
            self._timing = timing if timing is not None else Timing()
            self._triggers = _get_trigger_by_psname(self.psnames)

        # egun pv
        if 'LI-01:PS-Spect' in self.psnames:
            self._pv_egun = _PV('LI-01:EG-TriggerPS:enablereal',
                                connection_timeout=0.05)

        # duration
        d = 0
        for ps in self.psnames:
            d = max(d, self.cyclers[ps].cycle_duration(self._mode))
        self._cycle_duration = d

        # task sizes
        self.prepare_timing_size = 3
        self.prepare_timing_max_duration = 15

        self.prepare_ps_size = 2*len(self.psnames)+1
        self.prepare_ps_max_duration = 20

        self.cycle_size = (len(self.psnames)+3 +  # check params
                           len(self.psnames) +    # check opmode
                           1+round(self._cycle_duration) +  # cycle
                           len(self.psnames) +  # check final
                           len(self.psnames)+2)  # reset subsystems
        self.cycle_max_duration = (
                           2 +  # check params
                           2 +  # check opmode
                           TIMEOUT_CHECK*3 +  # wait for timing trigger
                           round(self._cycle_duration) +  # cycle
                           2 +  # check final
                           2)   # reset subsystems

        # logger
        self._logger = logger
        self._logger_message = ''
        if not logger:
            _log.basicConfig(format='%(asctime)s | %(message)s',
                             datefmt='%F %T', level=_log.INFO,
                             stream=_sys.stdout)

    @property
    def psnames(self):
        """Power supplies to cycle."""
        return self.cyclers.keys()

    @property
    def mode(self):
        """Mode."""
        return self._mode

    def config_all_pwrsupplies(self, ppty):
        """Prepare power supplies to cycle according to mode."""
        if ppty == 'opmode':
            psnames = [ps for ps in self.psnames if 'LI' not in ps]
        else:
            psnames = self.psnames
        threads = list()
        for psname in psnames:
            t = _thread.Thread(
                target=self.config_pwrsupply, args=(psname, ppty), daemon=True)
            self._update_log('Preparing '+psname+' '+ppty+'...')
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def config_pwrsupply(self, psname, ppty):
        """Prepare power supplies parameters."""
        if ppty == 'parameters':
            self.cyclers[psname].prepare(self.mode)
        elif ppty == 'opmode' and 'LI' not in psname:
            self.cyclers[psname].set_opmode_cycle(self.mode)

    def config_timing(self):
        """Prepare timing to cycle according to mode."""
        if self._only_linac:
            return
        # TODO: remove following lines when TI is updated for SI
        if self._only_si:
            return
        self._timing.turnoff()
        self._update_log('Preparing Timing...')
        self._timing.prepare(self.mode, self._triggers)
        self._update_log(done=True)

    def check_all_pwrsupplies(self, ppty):
        """Check all power supplies according to mode."""
        if ppty == 'opmode':
            psnames = [ps for ps in self.psnames if 'LI' not in ps]
        else:
            psnames = self.psnames
        threads = list()
        self._checks_result = dict()
        for psname in psnames:
            t = _thread.Thread(
                target=self.check_pwrsupply,
                args=(psname, ppty), daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        status = True
        for psname in psnames:
            self._update_log('Checking '+psname+' '+ppty+'...')
            if self._checks_result[psname]:
                self._update_log(done=True)
            else:
                self._update_log(psname+' is not ready.', error=True)
                status &= False
        return status

    def check_pwrsupply(self, psname, ppty):
        """Check power supply."""
        t0 = _time.time()
        cycler = self.cyclers[psname]
        r = False
        while _time.time()-t0 < TIMEOUT_CHECK:
            if ppty == 'parameters':
                r = cycler.is_prepared(self.mode)
            elif ppty == 'opmode':
                r = cycler.check_opmode_cycle(self.mode)
            if r:
                break
            _time.sleep(TIMEOUT_SLEEP)
        self._checks_result[psname] = r

    def check_timing(self):
        """Check timing preparation."""
        if self._only_linac:
            return True
        # TODO: remove following lines when TI is updated for SI
        if self._only_si:
            return True

        self._update_log('Checking Timing...')
        t0 = _time.time()
        while _time.time()-t0 < TIMEOUT_CHECK/2:
            status = self._timing.check(self.mode, self._triggers)
            if status:
                break
            _time.sleep(TIMEOUT_SLEEP)
        if not status:
            self._update_log('Timing is not configured.', error=True)
            return False
        else:
            self._update_log(done=True)
            return True

    def check_egun_off(self):
        if 'LI-01:PS-Spect' in self.psnames:
            status = (self._pv_egun.value == 0)
            if not status:
                self._update_log(
                    'Linac EGun pulse is enabled! '
                    'Please disable it.', error=True)
            return status
        else:
            return True

    def pulse_si_pwrsupplies(self):
        """Send sync pulse to power supplies."""
        psnames = [ps for ps in self.psnames
                   if ('SI' in ps)]  # and 'Fam' not in ps)]
        threads = list()
        for psname in psnames:
            t = _thread.Thread(
                target=self.pulse_pwrsupply, args=(psname, ), daemon=True)
            self._update_log('Pulsing '+psname+'...')
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def pulse_pwrsupply(self, psname):
        """Send sync pulse to power supply."""
        self.cyclers[psname].pulse()

    def init(self):
        """Trigger timing according to mode to init cycling."""
        # initialize dict to check which ps is cycling
        self._is_cycling_dict = dict()
        for psname in self.psnames:
            self._is_cycling_dict[psname] = True
        self._li_threads = list()
        for psname in self.psnames_li:
            cycler = self.cyclers[psname]
            t = _thread.Thread(target=cycler.cycle, daemon=True)
            self._li_threads.append(t)
            t.start()

        psnames = [ps for ps in self.psnames if 'LI' not in ps]
        if not psnames:
            return
        self._update_log('Triggering timing...')
        # TODO: remove the following line when SI timing is ok
        self.pulse_si_pwrsupplies()
        self._timing.trigger(self.mode)
        self._update_log(done=True)

    def wait(self):
        """Wait/Sleep while cycling according to mode."""
        self._update_log('Waiting for cycling...')
        t0 = _time.time()
        keep_waiting = True
        while keep_waiting:
            # update remaining time
            _time.sleep(1)
            if self.mode == 'Cycle':
                t = round(self._cycle_duration - (_time.time()-t0))
            else:
                t = round(self._cycle_duration -
                          self._timing.get_cycle_count() *
                          DEFAULT_RAMP_DURATION/1000000)
            self._update_log('Remaining time: {}s...'.format(t))

            # verify if power supplies started to cycle
            if (self.mode == 'Cycle') and (5 < _time.time() - t0 < 6):
                for psname in self.psnames:
                    if _PVName(psname).sec == 'LI':
                        continue
                    if not self.cyclers[psname].get_cycle_enable():
                        self._update_log(psname + ' is not cycling!',
                                         warning=True)
                        self._is_cycling_dict[psname] = False
            if all([v is False for v in self._is_cycling_dict.values()]):
                self._update_log(
                    'All power supplies failed. Stopping.', error=True)
                return False

            # update keep_waiting
            if self.mode == 'Cycle':
                keep_waiting = _time.time() - t0 < self._cycle_duration
            else:
                keep_waiting = not self._timing.check_ramp_end()

        self._update_log(done=True)
        return True

    def check_all_pwrsupplies_final_state(self):
        """Check all power supplies final state according to mode."""
        threads = list()
        self._checks_final_result = dict()
        for psname in self.psnames:
            t = _thread.Thread(
                target=self.check_pwrsupplies_final_state,
                args=(psname, ), daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        for psname in self.psnames:
            self._update_log('Checking '+psname+' state...')
            has_prob = self._checks_final_result[psname]
            if has_prob == 0:
                self._update_log(done=True)
            elif has_prob == 1:
                self._update_log(
                    'Verify the number of pulses '+psname+' received!',
                    error=True)
            elif has_prob == 2 and self._is_cycling_dict[psname]:
                self._update_log(
                    'Verify '+psname+' OpMode! SlowRef command was sent...',
                    warning=True)
            elif has_prob == 3 and self._is_cycling_dict[psname]:
                self._update_log(psname+' is finishing cycling...',
                                 warning=True)
            elif has_prob == 4:
                self._update_log(psname+' has interlock problems.',
                                 error=True)
        return True

    def check_pwrsupplies_final_state(self, psname):
        """Check power supplies final state."""
        self._checks_final_result[psname] = \
            self.cyclers[psname].check_final_state(self.mode)

    def reset_all_subsystems(self):
        """Reset all subsystems."""
        if self._only_linac:
            return
        self._update_log('Setting power supplies to SlowRef...')
        threads = list()
        for ps in self.psnames:
            if 'LI' in ps:
                continue
            t = _thread.Thread(
                target=self.cyclers[ps].set_opmode_slowref, daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        self._update_log('Restoring Timing initial state...')
        self._timing.restore_initial_state()
        self._update_log(done=True)

    # --- main commands ---

    def prepare_timing(self):
        self.config_timing()
        if not self.check_timing():
            return
        self._update_log('Timing preparation finished!')

    def prepare_pwrsupplies_parameters(self):
        """Prepare to cycle."""
        self.config_all_pwrsupplies('parameters')
        if not self.check_all_pwrsupplies('parameters'):
            self._update_log(
                'There are power supplies not configured to cycle.',
                error=True)
            return
        self._update_log('Power supplies parameters preparation finished!')

    def prepare_pwrsupplies_opmode(self):
        """Prepare to cycle."""
        self.config_all_pwrsupplies('opmode')
        if not self.check_all_pwrsupplies('opmode'):
            self._update_log(
                'There are power supplies with wrong opmode.',
                error=True)
            return
        self._update_log('Power supplies OpMode preparation finished!')

    def cycle(self):
        """Cycle."""
        # check
        if not self.check_egun_off():
            return
        if not self.check_timing():
            return
        if not self.check_all_pwrsupplies('parameters'):
            self._update_log(
                'There are power supplies not configured to cycle. Stopping.',
                error=True)
            return
        if not self.check_all_pwrsupplies('opmode'):
            self._update_log(
                'There are power supplies with wrong opmode. Stopping.',
                error=True)
            return

        self.init()
        if not self.wait():
            return
        self.check_all_pwrsupplies_final_state()
        _time.sleep(4)  # TODO: replace by checks
        self.reset_all_subsystems()

        # Indicate cycle end
        self._update_log('Cycle finished!')

    # --- private methods ---

    def _psnames_2_cycle(self):
        """Return psnames to cycle."""
        if self.cyclers:
            psnames = _Filter.process_filters(
                self.cyclers.keys(),
                filters={'sec': '(TB|TS|SI)', 'dis': 'PS'})
            lipsnames = _Filter.process_filters(
                self.cyclers.keys(),
                filters={'sec': 'LI', 'dis': 'PS'})
        else:
            psnames = _PSSearch.get_psnames({'sec': '(TB|TS|SI)', 'dis': 'PS'})
            lipsnames = _PSSearch.get_psnames({'sec': 'LI', 'dis': 'PS'})
        psnames.extend(lipsnames)
        self.psnames_li = lipsnames
        return psnames

    def _psnames_2_ramp(self):
        """Return psnames to ramp."""
        if self.cyclers:
            psnames = _Filter.process_filters(
                self.cyclers.keys(), filters={'sec': 'BO', 'dis': 'PS'})
        else:
            psnames = _PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})
        return psnames

    def _update_log(self, message='', done=False, warning=False, error=False):
        self._logger_message = message
        if self._logger:
            self._logger.update(message, done, warning, error)
        else:
            if done and not message:
                message = 'Done.'
            _log.info(message)
