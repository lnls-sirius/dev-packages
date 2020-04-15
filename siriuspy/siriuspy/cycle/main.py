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
        self._aux_cyclers = dict()

        # cyclers
        self.cyclers = cyclers
        ps2cycle = self._filter_psnames({'sec': '(LI|TB|TS|SI)', 'dis': 'PS'})
        ps2ramp = self._filter_psnames({'sec': 'BO', 'dis': 'PS'})
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
        self._only_linac = self._sections == ['LI', ]
        if not self._only_linac:
            self._timing = timing if timing is not None else Timing()
            self._triggers = _get_trigger_by_psname(self.psnames)

        # egun pv
        if 'LI-01:PS-Spect' in self.psnames:
            self._pv_egun = _PV('LI-01:EG-TriggerPS:enablereal',
                                connection_timeout=0.05)

        # cycle duration
        duration = 0
        for psname in self.psnames:
            duration = max(
                duration, self.cyclers[psname].cycle_duration(self._mode))
        self._cycle_duration = duration

        # task sizes
        self.prepare_timing_size = 3
        self.prepare_timing_max_duration = 10

        self.prepare_ps_size = 2*len(self.psnames)+1
        self.prepare_ps_max_duration = 20
        if 'SI' in self._sections:
            # set and check currents to zero
            self.prepare_ps_size += 3*len(self.psnames)
            self.prepare_ps_max_duration += \
                TIMEOUT_CHECK + TIMEOUT_CHECK_SI_CURRENTS

        self.cycle_size = (
            2 +  # check timing
            len(self.psnames)+3 +  # check params
            len(self.psnames) +    # check opmode
            2 +  # set and check triggers enable
            3+round(self._cycle_duration) +  # cycle
            len(self.psnames) +  # check final
            len(self.psnames)+2)  # reset subsystems
        self.cycle_max_duration = (
            5 +  # check timing
            TIMEOUT_CHECK +  # check params
            TIMEOUT_CHECK +  # check opmode
            6 +  # set and check triggers enable
            60 +  # wait for timing trigger
            round(self._cycle_duration) +  # cycle
            12 +  # check final
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

    def create_aux_cyclers(self):
        """Create auxiliar cyclers."""
        # create cyclers, if needed
        for psn in self.trims_psnames:
            self._update_log('Connecting to '+psn+'...')
            self._aux_cyclers[psn] = PSCycler(psn)

        # wait for connections
        for cycler in self._aux_cyclers.values():
            cycler.wait_for_connection()

    def set_pwrsupplies_currents_zero(self):
        """Zero currents of all SI power supplies."""
        psnames = _PSSearch.get_psnames(
            {'sec': 'SI', 'dis': 'PS', 'dev': '(B|Q|S|CH|CV)'})

        # set currents to zero
        for psn in psnames:
            cycler = self._get_cycler(psn)
            self._update_log('Setting '+psn+' current to zero...')
            cycler.set_current_zero()

        # check currents zero
        self._update_log('Waiting power supplies...')
        need_check = _dcopy(psnames)
        self._checks_result = dict()
        time = _time.time()
        while _time.time() - time < TIMEOUT_CHECK_SI_CURRENTS:
            for psname in psnames:
                if psname not in need_check:
                    continue
                cycler = self._get_cycler(psname)
                if cycler.check_current_zero():
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

    def config_pwrsupplies(self, ppty, psnames):
        """Prepare power supplies to cycle according to mode."""
        threads = list()
        for psname in psnames:
            cycler = self._get_cycler(psname)
            if ppty == 'parameters':
                target = cycler.prepare
            elif ppty == 'opmode':
                target = cycler.set_opmode_cycle
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

    def check_pwrsupplies(self, ppty, psnames):
        """Check all power supplies according to mode."""
        need_check = _dcopy(psnames)

        self._checks_result = dict()
        time = _time.time()
        while _time.time() - time < TIMEOUT_CHECK:
            for psname in psnames:
                if psname not in need_check:
                    continue
                cycler = self._get_cycler(psname)
                if ppty == 'parameters':
                    ret = cycler.is_prepared(self.mode)
                elif ppty == 'opmode':
                    ret = cycler.check_opmode_cycle(self.mode)
                if ret:
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
        while _time.time() - time0 < 5:
            status = self._timing.check(self.mode, self._triggers)
            if status:
                self._update_log(done=True)
                return True
            _time.sleep(TIMEOUT_SLEEP)
        self._update_log('Timing is not configured.', error=True)
        return False

    def check_egun_off(self):
        """Check egun off."""
        if 'LI-01:PS-Spect' in self.psnames:
            status = (self._pv_egun.value == 0)
            if not status:
                self._update_log(
                    'Linac EGun pulse is enabled! '
                    'Please disable it.', error=True)
            return status
        return True

    def pulse_si_pwrsupplies(self):
        """Send sync pulse to power supplies. Not being used."""
        psnames = []
        threads = list()
        for psname in psnames:
            cycler = self._get_cycler(psname)
            thread = _thread.Thread(target=cycler.pulse, daemon=True)
            self._update_log('Pulsing '+psname+'...')
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    def enable_triggers(self, triggers):
        """Enable triggers."""
        if self._only_linac:
            return True
        self._update_log('Enabling triggers...')
        if self._timing.enable_triggers(triggers):
            self._update_log(done=True)
            return True
        self._update_log('Could not enable triggers!', error=True)
        return False

    def disable_triggers(self, triggers):
        """Disable triggers."""
        self._update_log('Disabling triggers...')
        if self._timing.disable_triggers(triggers):
            self._update_log(done=True)
            return True
        self._update_log('Could not disable triggers!', error=True)
        return False

    def trigger_timing(self):
        """Trigger timing according to mode."""
        if self._only_linac:
            return
        self._update_log('Triggering timing...')
        self._timing.trigger(self.mode)
        self._update_log(done=True)

    def init(self):
        """Initialize cycling process."""
        # initialize dict to check which ps is cycling
        self._is_cycling_dict = {ps: True for ps in self.psnames}

        self._li_threads = list()
        psnames_li = [psn for psn in self.psnames if 'LI' in psn]
        for psname in psnames_li:
            cycler = self._get_cycler(psname)
            thread = _thread.Thread(target=cycler.cycle, daemon=True)
            self._li_threads.append(thread)
            thread.start()

        # trigger
        self.trigger_timing()

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
                    cycler = self._get_cycler(psname)
                    if not cycler.get_cycle_enable():
                        self._update_log(
                            psname + ' is not cycling!', warning=True)
                        self._is_cycling_dict[psname] = False
                if sum(self._is_cycling_dict.values()) == 0:
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

    def check_pwrsupplies_finalsts(self, psnames):
        """Check all power supplies final state according to mode."""
        need_check = _dcopy(psnames)

        self._checks_final_result = dict()
        time = _time.time()
        while _time.time() - time < 10:
            for psname in psnames:
                if psname not in need_check:
                    continue
                cycler = self._get_cycler(psname)
                if cycler.check_final_state(self.mode):
                    need_check.remove(psname)
                    self._checks_final_result[psname] = True
            if not need_check:
                break
            _time.sleep(TIMEOUT_SLEEP)
        for psname in need_check:
            self._checks_final_result[psname] = False

        all_ok = True
        for psname in psnames:
            self._update_log('Checking '+psname+' state...')
            has_prob = self._checks_final_result[psname]
            if has_prob == 0:
                self._update_log(done=True)
            elif has_prob == 1:
                self._update_log(
                    'Verify the number of pulses '+psname+' received!',
                    error=True)
                all_ok = False
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
                all_ok = False
        return all_ok

    def restore_timing_initial_state(self):
        """Reset all subsystems."""
        if self._only_linac:
            return
        self._update_log('Restoring Timing initial state...')
        self._timing.restore_initial_state()
        self._update_log(done=True)

    # --- main commands ---

    def prepare_timing(self):
        """Prepare Timing."""
        self.config_timing()
        if not self.check_timing():
            return
        self._update_log('Timing preparation finished!')

    def prepare_pwrsupplies_parameters(self):
        """Prepare parameters to cycle."""
        psnames = self.psnames
        if 'SI' in self._sections:
            self.create_aux_cyclers()
            self.set_pwrsupplies_currents_zero()

        self.config_pwrsupplies('parameters', psnames)
        if not self.check_pwrsupplies('parameters', psnames):
            self._update_log(
                'There are power supplies not configured to cycle.',
                error=True)
            return
        self._update_log('Power supplies parameters preparation finished!')

    def prepare_pwrsupplies_opmode(self):
        """Prepare OpMode to cycle."""
        psnames = [ps for ps in self.psnames if 'LI' not in ps]
        self.config_pwrsupplies('opmode', psnames)
        if not self.check_pwrsupplies('opmode', psnames):
            self._update_log(
                'There are power supplies with wrong opmode.', error=True)
            return
        self._update_log('Power supplies OpMode preparation finished!')

    def cycle(self):
        """Cycle."""
        # check
        if not self.check_egun_off():
            return
        if not self.check_timing():
            return
        if not self.check_pwrsupplies('parameters', self.psnames):
            self._update_log(
                'There are power supplies not configured to cycle. Stopping.',
                error=True)
            return
        psnames_wo_li = [ps for ps in self.psnames if 'LI' not in ps]
        if not self.check_pwrsupplies('opmode', psnames_wo_li):
            self._update_log(
                'There are power supplies with wrong opmode. Stopping.',
                error=True)
            return

        if not self.enable_triggers(self._triggers):
            return
        self.init()
        if not self.wait():
            return

        self.check_pwrsupplies_finalsts(self.psnames)
        self.restore_timing_initial_state()

        # Indicate cycle end
        self._update_log('Cycle finished!')

    # --- private methods ---

    def _filter_psnames(self, filt):
        if self.cyclers:
            psnames = _Filter.process_filters(
                self.cyclers.keys(), filters=filt)
        else:
            psnames = _PSSearch.get_psnames(filt)
        return psnames

    def _get_cycler(self, psname):
        if psname in self.cyclers:
            return self.cyclers[psname]
        if psname in self._aux_cyclers:
            return self._aux_cyclers[psname]
        raise ValueError('There is no cycler defined to '+psname+'!')

    def _update_log(self, message='', done=False, warning=False, error=False):
        self._logger_message = message
        if self._logger:
            self._logger.update(message, done, warning, error)
        else:
            if done and not message:
                message = 'Done.'
            _log.info(message)
