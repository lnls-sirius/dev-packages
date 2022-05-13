"""Main cycle module."""

import sys as _sys
import time as _time
import logging as _log
import threading as _thread
from concurrent.futures import ThreadPoolExecutor
from epics import PV as _PV

from ..namesys import Filter as _Filter, SiriusPVName as _PVName
from ..search import PSSearch as _PSSearch

from .conn import Timing, PSCycler, PSCyclerFBP, LinacPSCycler, FOFBPSCycler
from .bo_cycle_data import DEFAULT_RAMP_DURATION
from .util import get_sections as _get_sections, Const as _Const, \
    get_trigger_by_psname as _get_trigger_by_psname

TIMEOUT_SLEEP = 0.1
TIMEOUT_CHECK = 20
TIMEOUT_CONN = 0.5


class CycleController:
    """Class to perform automated cycle procedure."""

    def __init__(self, cyclers=None, timing=None,
                 is_bo=False, ramp_config=None, logger=None,
                 isadv=False):
        """Initialize."""
        # initialize auxiliar variables
        self._mode = None
        self._sections = list()
        self._not_ctrl_ti = None
        self._cycle_duration = 0
        self._aux_cyclers = dict()
        self._cycle_trims_duration = 0
        self._checks_result = dict()
        self._si_aux_triggers = list()

        # in case user wants to cycle SI power supplies individually,
        # not following the standard procedure
        self._isadv = isadv

        # in case cyclers are not set and user wants to cycle bo
        self._is_bo = is_bo
        self._ramp_config = ramp_config

        # cyclers
        self.cyclers = cyclers

        # timing connector
        self.timing = timing

        # logger
        self._logger_message = ''
        self.logger = logger

    # --- main parameter setters ---

    @property
    def cyclers(self):
        """Return current cyclers."""
        return self._cyclers

    @cyclers.setter
    def cyclers(self, new_cyclers):
        if new_cyclers:
            if not isinstance(new_cyclers, dict):
                raise TypeError("Input 'new_cyclers' has to be a dict!")
            psnames2filt = list(new_cyclers.keys())
            ps2cycle = self._filter_psnames(
                psnames2filt, {'sec': '(LI|TB|TS|SI)', 'dis': 'PS'})
            ps2ramp = self._filter_psnames(
                psnames2filt, {'sec': 'BO', 'dis': 'PS'})
            if ps2cycle and ps2ramp:
                raise Exception('Can not cycle Booster with other sectors!')
            self._mode = 'Ramp' if ps2ramp else 'Cycle'
        else:
            # create cyclers, if needed
            if self._is_bo:
                psnames = _PSSearch.get_psnames({'sec': 'BO', 'dis': 'PS'})
                self._mode = 'Ramp'
            else:
                psnames = _PSSearch.get_psnames(
                    {'sec': '(LI|TB|TS|SI)', 'dis': 'PS'})
                self._mode = 'Cycle'
            new_cyclers = dict()
            for name in psnames:
                if 'LI' in name:
                    new_cyclers[name] = LinacPSCycler(name)
                elif _PSSearch.conv_psname_2_psmodel(name) == 'FOFB_PS':
                    new_cyclers[name] = FOFBPSCycler(name)
                elif _PSSearch.conv_psname_2_psmodel(name) == 'FBP':
                    new_cyclers[name] = PSCyclerFBP(name, self._ramp_config)
                else:
                    new_cyclers[name] = PSCycler(name, self._ramp_config)
        self._cyclers = new_cyclers

        # define section
        self._sections = _get_sections(self._cyclers.keys())

        # define not_ctrl_ti variable
        ps_no_ti = _PSSearch.get_psnames({'sec': 'LI', 'dis': 'PS'})
        ps_no_ti.extend(
            _PSSearch.get_psnames({'sec': 'SI', 'dis': 'PS', 'dev': 'FC.*'}))
        self._not_ctrl_ti = not bool(set(self._cyclers.keys()) - set(ps_no_ti))

        # define triggers
        self._triggers = _get_trigger_by_psname(self._cyclers.keys())

        if 'SI' in self._sections and not self._isadv:
            # trims psnames
            self.trimnames = _PSSearch.get_psnames(
                {'sec': 'SI', 'sub': '[0-2][0-9](M|C).*', 'dis': 'PS',
                 'dev': '(CH|CV|QS|QD.*|QF.*|Q[1-4])'})

            # trims triggers
            self._si_aux_triggers = [
                'SI-Glob:TI-Mags-Skews', 'SI-Glob:TI-Mags-Corrs',
                'SI-Glob:TI-Mags-QTrims']
            self._triggers.update(self._si_aux_triggers)

            # move CV-2 and QS of C2 to trims group, if they are in cyclers
            qs_c2 = _PSSearch.get_psnames(
                {'sec': 'SI', 'sub': '[0-2][0-9]C2', 'dis': 'PS',
                 'dev': 'QS'})
            cv2_c2 = _PSSearch.get_psnames(
                {'sec': 'SI', 'sub': '[0-2][0-9]C2', 'dis': 'PS',
                 'dev': 'CV', 'idx': '2'})
            for psn in qs_c2 + cv2_c2:
                if psn in self._cyclers.keys():
                    self._aux_cyclers[psn] = self._cyclers.pop(psn)
        else:
            self.trimnames = list()

        # define cycle duration
        duration = 0
        for psname in self._cyclers.keys():
            duration = max(
                duration, self._cyclers[psname].cycle_duration(self._mode))
        self._cycle_duration = duration

        # egun pv
        if 'LI-01:PS-Spect' in self._cyclers.keys():
            self._pv_egun = _PV('LI-01:EG-TriggerPS:enablereal',
                                connection_timeout=0.05)

    def create_trims_cyclers(self):
        """Create trims cyclers."""
        self._update_log('Creating trims connections...')
        for idx, psn in enumerate(self.trimnames):
            if idx % 5 == 4 or idx == len(self.trimnames)-1:
                self._update_log(
                    'Created connections of {0}/{1} trims'.format(
                        str(idx+1), str(len(self.trimnames))))
            if psn in self._aux_cyclers.keys():
                continue
            if _PSSearch.conv_psname_2_psmodel(psn) == 'FBP':
                self._aux_cyclers[psn] = PSCyclerFBP(psn, self._ramp_config)
            else:
                self._aux_cyclers[psn] = PSCycler(psn, self._ramp_config)

        # wait for connections
        self._update_log('Waiting for connections...')
        for cycler in self._aux_cyclers.values():
            cycler.wait_for_connection(0.1)

        # calculate trims cycle duration
        duration = 0
        for psname in self.trimnames:
            duration = max(
                duration, self._aux_cyclers[psname].cycle_duration(self._mode))
        self._cycle_trims_duration = duration

    @property
    def timing(self):
        """Return timing connector."""
        return self._timing

    @timing.setter
    def timing(self, new_timing):
        self._timing = new_timing if new_timing is not None else Timing()

    @property
    def logger(self):
        """Return current logger."""
        return self._logger

    @logger.setter
    def logger(self, new_log):
        self._logger = new_log
        if not new_log:
            _log.basicConfig(format='%(asctime)s | %(message)s',
                             datefmt='%F %T', level=_log.INFO,
                             stream=_sys.stdout)

    # --- properties ---

    @property
    def psnames(self):
        """Power supplies to cycle."""
        return list(self._cyclers.keys())

    @property
    def mode(self):
        """Mode."""
        return self._mode

    @property
    def sections(self):
        """Mode."""
        return self._sections

    @property
    def save_timing_size(self):
        """Save timing initial state task size."""
        return 2

    @property
    def prepare_timing_size(self):
        """Prepare timing task size."""
        return 3

    @property
    def prepare_ps_sofbmode_size(self):
        """Prepare PS SOFBMode task size."""
        prepare_ps_size = 2*(len(self.psnames)+1)
        if 'SI' in self._sections and not self._isadv:
            prepare_ps_size += 2*len(self.trimnames)
        return prepare_ps_size

    @property
    def prepare_ps_opmode_slowref_size(self):
        """Prepare PS OpMode SlowRef task size."""
        prepare_ps_size = 2*(len(self.psnames)+1)
        if 'SI' in self._sections and not self._isadv:
            prepare_ps_size += 3*len(self.trimnames)
        return prepare_ps_size

    @property
    def prepare_ps_current_zero_size(self):
        """Prepare PS current zero task size."""
        prepare_ps_size = 2*(len(self.psnames)+1)
        if 'SI' in self._sections and not self._isadv:
            prepare_ps_size += 3*len(self.trimnames)
        return prepare_ps_size

    @property
    def prepare_ps_params_size(self):
        """Prepare PS parameters task size."""
        prepare_ps_size = 2*(len(self.psnames)+1)
        if 'SI' in self._sections and not self._isadv:
            prepare_ps_size += 3*len(self.trimnames)
        return prepare_ps_size

    @property
    def prepare_ps_opmode_cycle_size(self):
        """Prepare PS task size."""
        prepare_ps_size = 2*(len(self.psnames)+1)
        return prepare_ps_size

    @property
    def cycle_size(self):
        """Cycle task size."""
        cycle_size = (
            2 +  # check timing
            len(self.psnames)+3 +  # check params
            len(self.psnames) +    # check opmode
            2 +  # set and check triggers enable
            3+round(self._cycle_duration) +  # cycle
            len(self.psnames) +  # check final
            len(self.psnames)+2)  # reset subsystems
        return cycle_size

    @property
    def cycle_trims_size(self):
        """Cycle trims task size."""
        cycle_trims_size = (
            2*2 +  # check timing
            2*2*len(self.trimnames) +  # set and check params
            2*2*len(self.trimnames) +  # set and check opmode
            2*2 +  # set and check triggers enable
            2*(3+round(self._cycle_trims_duration)) +  # cycle
            2*len(self.trimnames))  # check final
        return cycle_trims_size

    @property
    def restore_timing_size(self):
        """Restore timing initial state task size."""
        return 2

    @property
    def save_timing_max_duration(self):
        """Save timing initial state task maximum duration."""
        return 10

    @property
    def prepare_timing_max_duration(self):
        """Prepare timing task maximum duration."""
        return 10

    @property
    def prepare_ps_sofbmode_max_duration(self):
        """Prepare PS SOFBMode task maximum duration."""
        prepare_ps_max_duration = 5 + TIMEOUT_CHECK
        if 'SI' in self._sections and not self._isadv:
            prepare_ps_max_duration += TIMEOUT_CHECK
        return prepare_ps_max_duration

    @property
    def prepare_ps_opmode_slowref_max_duration(self):
        """Prepare PS OpMode SlowRef task maximum duration."""
        prepare_ps_max_duration = 10 + TIMEOUT_CHECK
        if 'SI' in self._sections and not self._isadv:
            prepare_ps_max_duration += 3*TIMEOUT_CHECK
        return prepare_ps_max_duration

    @property
    def prepare_ps_current_zero_max_duration(self):
        """Prepare PS current zero task maximum duration."""
        prepare_ps_max_duration = 10 + TIMEOUT_CHECK
        if 'SI' in self._sections and not self._isadv:
            prepare_ps_max_duration += 3*TIMEOUT_CHECK
        return prepare_ps_max_duration

    @property
    def prepare_ps_params_max_duration(self):
        """Prepare PS parameters task maximum duration."""
        prepare_ps_max_duration = 10 + TIMEOUT_CHECK
        if 'SI' in self._sections and not self._isadv:
            prepare_ps_max_duration += 3*TIMEOUT_CHECK
        return prepare_ps_max_duration

    @property
    def prepare_ps_opmode_cycle_max_duration(self):
        """Prepare PS task maximum duration."""
        prepare_ps_max_duration = 10 + TIMEOUT_CHECK
        if 'SI' in self._sections and not self._isadv:
            prepare_ps_max_duration += 3*TIMEOUT_CHECK
        return prepare_ps_max_duration

    @property
    def cycle_max_duration(self):
        """Cycle task maximum duration."""
        cycle_max_duration = (
            8 +  # check timing
            TIMEOUT_CHECK +  # check params
            TIMEOUT_CHECK +  # check opmode
            TIMEOUT_CHECK +  # set and check triggers enable
            60 +  # wait for timing trigger
            round(self._cycle_duration) +  # cycle
            TIMEOUT_CHECK +  # check final
            TIMEOUT_CHECK)  # set and check ps slowref
        return cycle_max_duration

    @property
    def cycle_trims_max_duration(self):
        """Cycle trims task maximum duration."""
        cycle_trims_max_duration = (
            8 +  # check timing
            2*50 +  # check params
            2*50 +  # set and check opmode
            2*TIMEOUT_CHECK +  # set and check triggers enable
            2*10 +  # wait for timing trigger
            2*round(self._cycle_trims_duration) +  # cycle
            2*TIMEOUT_CHECK +  # check final
            2*50)  # set and check ps slowref
        return cycle_trims_max_duration

    @property
    def restore_timing_max_duration(self):
        """Restore timing initial state task maximum duration."""
        return 10

    # --- auxiliary commands ---

    def config_pwrsupplies(self, ppty, psnames):
        """Prepare power supplies to cycle according to mode."""
        if ppty == 'opmode':
            psnames = {
                p for p in psnames if 'LI' not in p and
                not _PSSearch.conv_psname_2_psmodel(p) == 'FOFB_PS'}
        if not psnames:
            return True

        self._update_log('Preparing power supplies '+ppty+'...')
        with ThreadPoolExecutor(max_workers=100) as executor:
            for idx, psname in enumerate(psnames):
                cycler = self._get_cycler(psname)
                if ppty == 'parameters':
                    target = cycler.prepare
                elif ppty == 'opmode':
                    target = cycler.set_opmode_cycle
                executor.submit(target, self.mode)
                if idx % 5 == 4 or idx == len(psnames)-1:
                    self._update_log(
                        'Sent '+ppty+' preparation to {0}/{1}'.format(
                            str(idx+1), str(len(psnames))))

    def config_timing(self):
        """Prepare timing to cycle according to mode."""
        if self._not_ctrl_ti:
            return
        self._timing.turnoff(self._triggers)
        self._update_log('Preparing Timing...')
        self._timing.prepare(self.mode, self._triggers)
        self._update_log(done=True)

    def check_pwrsupplies(self, ppty, psnames, timeout=TIMEOUT_CHECK):
        """Check all power supplies according to mode."""
        if ppty == 'opmode':
            psnames = {
                p for p in psnames if 'LI' not in p and
                not _PSSearch.conv_psname_2_psmodel(p) == 'FOFB_PS'}
        if not psnames:
            return True

        self._update_log('Checking power supplies '+ppty+'...')
        self._checks_result = {psn: False for psn in psnames}
        msg = 'Successfully checked '+ppty+' preparation for {}/' + \
            str(len(psnames))
        checked = 0
        time = _time.time()
        while _time.time() - time < timeout:
            for psname in psnames:
                if self._checks_result[psname]:
                    continue
                cycler = self._get_cycler(psname)
                if ppty == 'parameters':
                    ret = cycler.is_prepared(self.mode, 0.05)
                elif ppty == 'opmode':
                    ret = cycler.check_opmode_cycle(self.mode, 0.05)
                if ret:
                    self._checks_result[psname] = True
                    checked = sum(self._checks_result.values())
                    if not checked % 5:
                        self._update_log(msg.format(str(checked)))
                if _time.time() - time > timeout:
                    break
            if all(self._checks_result.values()):
                break
            _time.sleep(TIMEOUT_SLEEP)
        self._update_log(msg.format(str(checked)))

        status = True
        for psname, sts in self._checks_result.items():
            if sts:
                continue
            self._update_log(psname+' is not ready.', error=True)
            status &= False
        return status

    def check_timing(self):
        """Check timing preparation."""
        if self._not_ctrl_ti:
            return True

        self._update_log('Checking Timing...')
        time0 = _time.time()
        while _time.time() - time0 < 5:
            status = self._timing.check(self.mode, self._triggers)
            if status:
                self._update_log(done=True)
                return True
            _time.sleep(TIMEOUT_SLEEP)
        self._update_log(
            'Timing is not configured or has problems. Please verify.',
            error=True)
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

    def set_triggers_state(self, triggers, state):
        """Set triggers state."""
        if self._not_ctrl_ti:
            return True

        label = 'enabl' if state == 'enbl' else 'disabl'
        self._update_log(label.capitalize()+'ing triggers...')
        if self._timing.set_triggers_state(state, triggers):
            self._update_log(done=True)
            return True
        self._update_log('Could not '+label+'e triggers!', error=True)
        return False

    def trigger_timing(self):
        """Trigger timing according to mode."""
        if self._not_ctrl_ti:
            return
        self._update_log('Triggering timing...')
        self._timing.trigger(self.mode)
        self._update_log(done=True)

    def init_trims(self, trims):
        """Initialize trims cycling process."""
        # initialize dict to check which trim is cycling
        self._is_cycling_dict = {ps: True for ps in trims}

        # trigger
        self.trigger_timing()

    def wait_trims(self):
        """Wait Trims to cycle."""
        self._update_log('Waiting for trims to cycle...')
        time0 = _time.time()
        keep_waiting = True
        while keep_waiting:
            # update remaining time
            _time.sleep(1)
            time = round(self._cycle_trims_duration - (_time.time()-time0))
            self._update_log('Remaining time: {}s...'.format(time))

            # verify if trims started to cycle
            if 14 < _time.time() - time0 < 15:
                for psname in self._is_cycling_dict:
                    cycler = self._get_cycler(psname)
                    if not cycler.get_cycle_enable():
                        self._update_log(
                            psname + ' is not cycling!', warning=True)
                        self._is_cycling_dict[psname] = False
                if sum(self._is_cycling_dict.values()) == 0:
                    self._update_log(
                        'All trims failed. Stopping.', error=True)
                    return False

            # update keep_waiting
            keep_waiting = _time.time() - time0 < self._cycle_trims_duration

        self._update_log(done=True)
        return True

    def cycle_trims_subset(self, trims, timeout=TIMEOUT_CHECK):
        """Cycle trims."""
        if not self.check_pwrsupplies('parameters', trims, timeout):
            return False

        self.config_pwrsupplies('opmode', trims)
        if not self.check_pwrsupplies('opmode', trims, timeout):
            return False

        triggers = _get_trigger_by_psname(trims)
        if not self.set_triggers_state(triggers, 'enbl'):
            return False
        self.init_trims(trims)
        if not self.wait_trims():
            self.set_pwrsupplies_slowref(trims)
            return False
        if not self.set_triggers_state(triggers, 'dsbl'):
            self.set_pwrsupplies_slowref(trims)
            return False

        if not self.check_pwrsupplies_finalsts(trims):
            self.set_pwrsupplies_slowref(trims)
            return False

        self.set_pwrsupplies_slowref(trims)
        if not self.check_pwrsupplies_slowref(trims, timeout):
            return False
        return True

    def init(self):
        """Initialize cycling process."""
        # initialize dict to check which ps is cycling
        self._is_cycling_dict = {ps: True for ps in self.psnames}

        self._aux_threads = list()
        psn2thr = [
            p for p in self.psnames if _PVName(p).sec == 'LI' or
            _PVName(p).dev in ['FCH', 'FCV']]
        for psname in psn2thr:
            cycler = self._get_cycler(psname)
            thread = _thread.Thread(target=cycler.cycle, daemon=True)
            self._aux_threads.append(thread)
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
                    if _PVName(psname).dev in ['FCH', 'FCV']:
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
        self._update_log('Checking power supplies final state...')
        self._checks_final_result = dict()
        sucess_cnt = 0
        msg = 'Successfully checked final state for {}/'+str(len(psnames))
        for psname in psnames:
            cycler = self._get_cycler(psname)
            status = cycler.check_final_state(self.mode)
            if status == _Const.CycleEndStatus.Ok:
                sucess_cnt += 1
                if sucess_cnt % 5 == 0:
                    self._update_log(msg.format(str(sucess_cnt)))
            self._checks_final_result[psname] = status
        self._update_log(msg.format(str(sucess_cnt)))

        all_ok = True
        for psname, has_prob in self._checks_final_result.items():
            if has_prob == _Const.CycleEndStatus.LackTriggers:
                self._update_log(
                    'Verify the number of pulses '+psname+' received!',
                    error=True)
                all_ok = False
            elif has_prob == _Const.CycleEndStatus.NotFinished \
                    and self._is_cycling_dict[psname]:
                self._update_log(
                    psname+' is finishing cycling...', warning=True)
            elif has_prob == _Const.CycleEndStatus.Interlock:
                self._update_log(
                    psname+' has interlock problems.', error=True)
                all_ok = False
        return all_ok

    def set_pwrsupplies_sofbmode(self, psnames):
        """Set power supplies SOFBMode."""
        psnames = {
            p for p in psnames if _PSSearch.conv_psname_2_psmodel(p) == 'FBP'}
        if not psnames:
            return True

        self._update_log('Turning off power supplies SOFBMode...')
        for idx, psname in enumerate(psnames):
            cycler = self._get_cycler(psname)
            cycler.set_sofbmode('off')
            if idx % 5 == 4 or idx == len(psnames)-1:
                self._update_log(
                    'Sent SOFBMode preparation to {0}/{1}'.format(
                        str(idx+1), str(len(psnames))))

    def check_pwrsupplies_sofbmode(self, psnames, timeout=TIMEOUT_CHECK):
        """Check power supplies SOFBMode."""
        psnames = {
            p for p in psnames if _PSSearch.conv_psname_2_psmodel(p) == 'FBP'}
        if not psnames:
            return True

        self._update_log('Checking power supplies SOFBMode...')
        self._checks_result = {psn: False for psn in psnames}
        msg = 'Successfully checked SOFBMode preparation for {}/' + \
            str(len(psnames))
        checked = 0
        time = _time.time()
        while _time.time() - time < timeout:
            for psname in psnames:
                if self._checks_result[psname]:
                    continue
                cycler = self._get_cycler(psname)
                if cycler.check_sofbmode('off', 0.05):
                    self._checks_result[psname] = True
                    checked = sum(self._checks_result.values())
                    if not checked % 5:
                        self._update_log(msg.format(str(checked)))
                if _time.time() - time > timeout:
                    break
            if all(self._checks_result.values()):
                break
            _time.sleep(TIMEOUT_SLEEP)
        self._update_log(msg.format(str(checked)))

        status = True
        for psname, sts in self._checks_result.items():
            if sts:
                continue
            self._update_log(psname+' is in SOFBMode.', error=True)
            status &= False
        return status

    def set_pwrsupplies_slowref(self, psnames):
        """Set power supplies OpMode to SlowRef."""
        psnames = {p for p in psnames if 'LI' not in p}
        if not psnames:
            return True

        self._update_log('Setting power supplies to SlowRef...')
        with ThreadPoolExecutor(max_workers=100) as executor:
            for idx, psname in enumerate(psnames):
                cycler = self._get_cycler(psname)
                target = cycler.set_opmode_slowref
                executor.submit(target)
                if idx % 5 == 4 or idx == len(psnames)-1:
                    self._update_log(
                        'Sent opmode preparation to {0}/{1}'.format(
                            str(idx+1), str(len(psnames))))

    def check_pwrsupplies_slowref(self, psnames, timeout=TIMEOUT_CHECK):
        """Check power supplies OpMode."""
        psnames = {p for p in psnames if 'LI' not in p}
        if not psnames:
            return True

        self._update_log('Checking power supplies opmode...')
        self._checks_result = {psn: False for psn in psnames}
        msg = 'Successfully checked opmode preparation for {}/' + \
            str(len(psnames))
        checked = 0
        time = _time.time()
        while _time.time() - time < timeout:
            for psname in psnames:
                if self._checks_result[psname]:
                    continue
                cycler = self._get_cycler(psname)
                if cycler.check_opmode_slowref(0.05):
                    self._checks_result[psname] = True
                    checked = sum(self._checks_result.values())
                    if not checked % 5:
                        self._update_log(msg.format(str(checked)))
                if _time.time() - time > timeout:
                    break
            if all(self._checks_result.values()):
                break
            _time.sleep(TIMEOUT_SLEEP)
        self._update_log(msg.format(str(checked)))

        status = True
        for psname, sts in self._checks_result.items():
            if sts:
                continue
            self._update_log(psname+' is not in SlowRef.', error=True)
            status &= False
        return status

    def set_pwrsupplies_current_zero(self, psnames):
        """Set power supplies current to zero."""
        self._update_log('Setting power supplies current to zero...')
        for idx, psname in enumerate(psnames):
            cycler = self._get_cycler(psname)
            cycler.set_current_zero()
            if idx % 5 == 4 or idx == len(psnames)-1:
                self._update_log(
                    'Sent current preparation to {0}/{1}'.format(
                        str(idx+1), str(len(psnames))))

    def check_pwrsupplies_current_zero(self, psnames, timeout=TIMEOUT_CHECK):
        """Check power supplies current."""
        self._update_log('Checking power supplies current...')
        self._checks_result = {psn: False for psn in psnames}
        msg = 'Successfully checked current preparation for {}/' + \
            str(len(psnames))
        checked = 0
        time = _time.time()
        while _time.time() - time < timeout:
            for psname in psnames:
                if self._checks_result[psname]:
                    continue
                cycler = self._get_cycler(psname)
                if cycler.check_current_zero(0.05):
                    self._checks_result[psname] = True
                    checked = sum(self._checks_result.values())
                    if not checked % 5:
                        self._update_log(msg.format(str(checked)))
                if _time.time() - time > timeout:
                    break
            if all(self._checks_result.values()):
                break
            _time.sleep(TIMEOUT_SLEEP)
        self._update_log(msg.format(str(checked)))

        status = True
        for psname, sts in self._checks_result.items():
            if sts:
                continue
            self._update_log(psname+' current is not zero.', error=True)
            status &= False
        return status

    # --- main commands ---

    def save_timing_initial_state(self):
        """Save timing initial state."""
        self._update_log('Saving Timing initial state...')
        self._timing.save_initial_state()
        self._update_log('...finished!')

    def prepare_timing(self):
        """Prepare Timing."""
        self.config_timing()
        if not self.check_timing():
            return
        self._update_log('Timing preparation finished!')

    def prepare_pwrsupplies_sofbmode(self):
        """Prepare SOFBMode."""
        psnames = self.psnames
        timeout = TIMEOUT_CHECK
        if 'SI' in self._sections and not self._isadv:
            self.create_trims_cyclers()
            psnames.extend(self.trimnames)
            timeout += TIMEOUT_CHECK

        self.set_pwrsupplies_sofbmode(psnames)
        if not self.check_pwrsupplies_sofbmode(psnames, timeout):
            self._update_log(
                'There are power supplies in SOFBMode.', error=True)
            return
        self._update_log('Power supplies SOFBMode preparation finished!')

    def prepare_pwrsupplies_opmode_slowref(self):
        """Prepare OpMode to slowref."""
        psnames = self.psnames
        timeout = TIMEOUT_CHECK
        if 'SI' in self._sections and not self._isadv:
            self.create_trims_cyclers()
            psnames.extend(self.trimnames)
            timeout += 3*TIMEOUT_CHECK

        self.set_pwrsupplies_slowref(psnames)
        if not self.check_pwrsupplies_slowref(psnames, timeout):
            self._update_log(
                'There are power supplies not in OpMode SlowRef.', error=True)
            return
        self._update_log('Power supplies OpMode preparation finished!')

    def prepare_pwrsupplies_current_zero(self):
        """Prepare current to cycle."""
        psnames = self.psnames
        timeout = TIMEOUT_CHECK
        if 'SI' in self._sections and not self._isadv:
            self.create_trims_cyclers()
            psnames.extend(self.trimnames)
            timeout += 3*TIMEOUT_CHECK

        self.set_pwrsupplies_current_zero(psnames)
        if not self.check_pwrsupplies_current_zero(psnames, timeout):
            self._update_log(
                'There are power supplies with current not zero.', error=True)
            return
        self._update_log('Power supplies current preparation finished!')

    def prepare_pwrsupplies_parameters(self):
        """Prepare parameters to cycle."""
        psnames = self.psnames
        timeout = TIMEOUT_CHECK
        if 'SI' in self._sections and not self._isadv:
            self.create_trims_cyclers()
            psnames.extend(self.trimnames)
            timeout += 3*TIMEOUT_CHECK

        self.config_pwrsupplies('parameters', psnames)
        if not self.check_pwrsupplies('parameters', psnames, timeout):
            self._update_log(
                'There are power supplies not configured to cycle.',
                error=True)
            return
        self._update_log('Power supplies parameters preparation finished!')

    def prepare_pwrsupplies_opmode_cycle(self):
        """Prepare OpMode to cycle."""
        psnames = self.psnames
        self.config_pwrsupplies('opmode', psnames)
        if not self.check_pwrsupplies('opmode', psnames):
            self._update_log(
                'There are power supplies with wrong opmode.', error=True)
            return
        self._update_log('Power supplies OpMode preparation finished!')

    def cycle_trims(self):
        """Cycle all trims."""
        if 'SI' not in self._sections or self._isadv:
            return

        if not self.check_timing():
            return

        self.create_trims_cyclers()

        self._update_log('Preparing to cycle CHs, QSs and QTrims...')
        trims = _PSSearch.get_psnames({
            'sec': 'SI', 'sub': '[0-2][0-9](M|C).*', 'dis': 'PS',
            'dev': '(CH|QS|QD.*|QF.*|Q[1-4])'})
        if not self.cycle_trims_subset(trims, timeout=50):
            self._update_log(
                'There was problems in trims cycling. Stoping.', error=True)
            return

        self._update_log('Preparing to cycle CVs...')
        trims = _PSSearch.get_psnames({
            'sec': 'SI', 'sub': '[0-2][0-9](M|C).*', 'dis': 'PS',
            'dev': 'CV'})
        if not self.cycle_trims_subset(trims, timeout=50):
            self._update_log(
                'There was problems in trims cycling. Stoping.', error=True)
            return

        self._update_log('Trims cycle finished!')

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
        if not self.check_pwrsupplies('opmode', self.psnames):
            self._update_log(
                'There are power supplies with wrong opmode. Stopping.',
                error=True)
            return

        triggers = self._triggers.copy()
        if 'SI' in self._sections and not self._isadv:
            triggers.difference_update(self._si_aux_triggers)
        if not self.set_triggers_state(triggers, 'enbl'):
            return
        self.init()
        if not self.wait():
            return

        self.check_pwrsupplies_finalsts(self.psnames)
        self.set_pwrsupplies_slowref(self.psnames)
        if not self.check_pwrsupplies_slowref(self.psnames):
            return False

        # Indicate cycle end
        self._update_log('Cycle finished!')

    def restore_timing_initial_state(self):
        """Restore timing initial state."""
        self._update_log('Restoring Timing initial state...')
        self._timing.restore_initial_state()
        self._update_log('...finished!')

    # --- private methods ---

    def _filter_psnames(self, psnames2filt, filt):
        if psnames2filt:
            psnames = _Filter.process_filters(
                psnames2filt, filters=filt)
        else:
            psnames = _PSSearch.get_psnames(filt)
        return psnames

    def _get_cycler(self, psname):
        if psname in self._cyclers:
            return self._cyclers[psname]
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
