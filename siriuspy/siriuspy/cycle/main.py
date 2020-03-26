"""Main cycle module."""

import sys as _sys
from copy import deepcopy as _dcopy
import time as _time
import logging as _log
import threading as _thread
from epics import PV as _PV

from ..namesys import Filter as _Filter, SiriusPVName as _PVName
from ..search import PSSearch as _PSSearch

from .conn import Timing, PSCycler, LinacPSCycler
from .bo_cycle_data import DEFAULT_RAMP_DURATION
from .util import get_sections as _get_sections, \
    get_trigger_by_psname as _get_trigger_by_psname

TIMEOUT_SLEEP = 0.1
TIMEOUT_CHECK = 20
TIMEOUT_CONN = 0.5
TIMEOUT_CHECK_SI_CURRENTS = 41


class CycleController:
    """Class to perform automated cycle procedure."""

    def __init__(self, cyclers=dict(), timing=None,
                 is_bo=False, ramp_config=None, logger=None):
        """Initialize."""
        self._checks_result = dict()

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
        if not self._only_linac:
            self._timing = timing if timing is not None else Timing()
            self._triggers = _get_trigger_by_psname(self.psnames)

        # egun pv
        if 'LI-01:PS-Spect' in self.psnames:
            self._pv_egun = _PV('LI-01:EG-TriggerPS:enablereal',
                                connection_timeout=0.05)

        # duration
        duration = 0
        for psname in self.psnames:
            duration = max(
                duration, self.cyclers[psname].cycle_duration(self._mode))
        self._cycle_duration = duration

        # task sizes
        self.prepare_timing_size = 3
        self.prepare_timing_max_duration = 15

        self.prepare_ps_size = 2*len(self.psnames)+1
        self.prepare_ps_max_duration = 20
        if 'SI' in self._sections:
            # set and check currents to zero
            self.prepare_ps_size += 3*len(self.psnames)
            self.prepare_ps_max_duration += \
                TIMEOUT_CHECK + TIMEOUT_CHECK_SI_CURRENTS

        self.cycle_size = (len(self.psnames)+3 +  # check params
                           len(self.psnames) +    # check opmode
                           1+round(self._cycle_duration) +  # cycle
                           len(self.psnames) +  # check final
                           len(self.psnames)+2)  # reset subsystems
        self.cycle_max_duration = (
            5 +  # check params
            5 +  # check opmode
            TIMEOUT_CHECK*3 +  # wait for timing trigger
            round(self._cycle_duration) +  # cycle
            5 +  # check final
            5)   # reset subsystems

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
        return list(self.cyclers.keys())

    @property
    def mode(self):
        """Mode."""
        return self._mode

    def set_check_si_pwrsupplies_currents_zero(self):
        """Zero currents of all SI power supplies."""
        if 'SI' not in self._sections:
            return

        psnames = _PSSearch.get_psnames(
            {'sec': 'SI', 'dis': 'PS', 'dev': '(B|Q|S|CH|CV)'})

        # create cyclers, if needed
        cyclers = dict()
        for psname in psnames:
            if psname in self.cyclers:
                cyclers[psname] = self.cyclers[psname]
            else:
                self._update_log('Connecting to '+psname+'...')
                cyclers[psname] = PSCycler(psname)

        # wait for connections
        for cycler in cyclers.values():
            cycler.wait_for_connection()

        # set currents to zero
        for psname, cycler in cyclers.items():
            self._update_log('Setting '+psname+' current to zero...')
            cycler.set_current_zero()

        # check currents zero
        need_check = _dcopy(psnames)
        self._checks_result = dict()
        time = _time.time()
        while _time.time() - time < TIMEOUT_CHECK_SI_CURRENTS:
            for psname in psnames:
                if psname not in need_check:
                    continue
                if cyclers[psname].check_current_zero():
                    need_check.remove(psname)
                    self._checks_result[psname] = True
            if not need_check:
                break
            _time.sleep(TIMEOUT_SLEEP)
        for psname in need_check:
            self._checks_result[psname] = False

        status = True
        for psname in psnames:
            self._update_log('Checking '+psname+' currents...')
            if self._checks_result[psname]:
                self._update_log(done=True)
            else:
                self._update_log(psname+' current is not zero.', error=True)
                status &= False
        return status

    def config_all_pwrsupplies(self, ppty):
        """Prepare power supplies to cycle according to mode."""
        if ppty == 'opmode':
            psnames = [ps for ps in self.psnames if 'LI' not in ps]
        else:
            psnames = self.psnames
        threads = list()
        for psname in psnames:
            if ppty == 'parameters':
                target = self.cyclers[psname].prepare
            elif ppty == 'opmode' and 'LI' not in psname:
                target = self.cyclers[psname].set_opmode_cycle
            thread = _thread.Thread(
                target=target, args=(self.mode, ), daemon=True)
            self._update_log('Preparing '+psname+' '+ppty+'...')
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    def config_timing(self):
        """Prepare timing to cycle according to mode."""
        if self._only_linac:
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
        need_check = _dcopy(psnames)

        self._checks_result = dict()
        time = _time.time()
        while _time.time() - time < TIMEOUT_CHECK:
            for psname in psnames:
                if psname not in need_check:
                    continue
                cycler = self.cyclers[psname]
                if ppty == 'parameters':
                    r = cycler.is_prepared(self.mode)
                elif ppty == 'opmode':
                    r = cycler.check_opmode_cycle(self.mode)
                if r:
                    need_check.remove(psname)
                    self._checks_result[psname] = True
            if not need_check:
                break
            _time.sleep(TIMEOUT_SLEEP)
        for psname in need_check:
            self._checks_result[psname] = False

        status = True
        for psname in psnames:
            self._update_log('Checking '+psname+' '+ppty+'...')
            if self._checks_result[psname]:
                self._update_log(done=True)
            else:
                self._update_log(psname+' is not ready.', error=True)
                status &= False
        return status

    def check_timing(self):
        """Check timing preparation."""
        if self._only_linac:
            return True

        self._update_log('Checking Timing...')
        time0 = _time.time()
        while _time.time()-time0 < TIMEOUT_CHECK/2:
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
        """Send sync pulse to power supplies. Not being used."""
        psnames = []
        threads = list()
        for psname in psnames:
            thread = _thread.Thread(
                target=self.cyclers[psname].pulse, daemon=True)
            self._update_log('Pulsing '+psname+'...')
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    def init(self):
        """Trigger timing according to mode to init cycling."""
        # initialize dict to check which ps is cycling
        self._is_cycling_dict = dict()
        for psname in self.psnames:
            self._is_cycling_dict[psname] = True
        self._li_threads = list()
        for psname in self.psnames_li:
            cycler = self.cyclers[psname]
            thread = _thread.Thread(target=cycler.cycle, daemon=True)
            self._li_threads.append(thread)
            thread.start()

        psnames = [ps for ps in self.psnames if 'LI' not in ps]
        if not psnames:
            return
        self._update_log('Triggering timing...')
        self._timing.trigger(self.mode)
        self._update_log(done=True)

    def wait(self):
        """Wait/Sleep while cycling according to mode."""
        self._update_log('Waiting for cycling...')
        time0 = _time.time()
        keep_waiting = True
        while keep_waiting:
            # update remaining time
            _time.sleep(1)
            if self.mode == 'Cycle':
                time = round(self._cycle_duration - (_time.time()-time0))
            else:
                time = round(
                    self._cycle_duration -
                    self._timing.get_cycle_count() *
                    DEFAULT_RAMP_DURATION/1000000)
            self._update_log('Remaining time: {}s...'.format(time))

            # verify if power supplies started to cycle
            if (self.mode == 'Cycle') and (5 < _time.time() - time0 < 6):
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
                keep_waiting = _time.time() - time0 < self._cycle_duration
            else:
                keep_waiting = not self._timing.check_ramp_end()

        self._update_log(done=True)
        return True

    def check_all_pwrsupplies_final_state(self):
        """Check all power supplies final state according to mode."""
        need_check = _dcopy(self.psnames)

        self._checks_final_result = dict()
        time = _time.time()
        while _time.time() - time < TIMEOUT_CHECK:
            for psname in self.psnames:
                if psname not in need_check:
                    continue
                cycler = self.cyclers[psname]
                if cycler.check_final_state(self.mode):
                    need_check.remove(psname)
                    self._checks_final_result[psname] = True
            if not need_check:
                break
            _time.sleep(TIMEOUT_SLEEP)
        for psname in need_check:
            self._checks_final_result[psname] = False

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

    def restore_timing_initial_state(self):
        """Reset all subsystems."""
        if self._only_linac:
            return
        self._update_log('Restoring Timing initial state...')
        self._timing.restore_initial_state()
        self._update_log(done=True)

    # --- main commands ---

    def prepare_timing(self):
        """."""
        self.config_timing()
        if not self.check_timing():
            return
        self._update_log('Timing preparation finished!')

    def prepare_pwrsupplies_parameters(self):
        """Prepare to cycle."""
        self.set_check_si_pwrsupplies_currents_zero()
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
        self.restore_timing_initial_state()

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
