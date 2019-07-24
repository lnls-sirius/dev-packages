"""Main cycle module."""

import sys as _sys
import time as _time
import logging as _log
import threading as _thread
from epics import PV as _PV
from siriuspy.namesys import Filter as _Filter, SiriusPVName as _PVName
from siriuspy.search import MASearch as _MASearch, PSSearch as _PSSearch
from .conn import Timing, MagnetCycler, LinacMagnetCycler
from .bo_cycle_data import DEFAULT_RAMP_DURATION
from .util import get_sections as _get_sections

TIMEOUT_SLEEP = 0.1
TIMEOUT_CHECK = 20


class CycleController:
    """Class to perform automated cycle procedure."""

    def __init__(self, cyclers=dict(), timing=None,
                 is_bo=False, ramp_config=None, logger=None):
        """Initialize."""
        # cyclers
        self.cyclers = cyclers
        ma2cycle = self._manames_2_cycle()
        ma2ramp = self._manames_2_ramp()
        if cyclers and (ma2cycle and ma2ramp):
            raise Exception('Can not cycle Booster with other accelerators!')
        self._mode = 'Ramp' if ma2ramp else 'Cycle'

        if not cyclers:
            manames = ma2ramp if is_bo else ma2cycle
            for name in manames:
                if 'LI' in name:
                    self.cyclers[name] = LinacMagnetCycler(name)
                else:
                    self.cyclers[name] = MagnetCycler(name, ramp_config)

        # timing connector
        sections = _get_sections(self.manames)
        self._only_linac = (len(sections) == 1) and (sections[0] == 'LI')
        if not self._only_linac:
            self._timing = timing if timing is not None else Timing()

        # egun pv
        if 'LI-01:PS-Spect' in self.manames:
            self._pv_egun = _PV('LI-01:EG-TriggerPS:enablereal',
                                connection_timeout=0.05)

        # duration
        d = 0
        for ma in self.manames:
            d = max(d, self.cyclers[ma].cycle_duration(self._mode))
        self._cycle_duration = d

        # task sizes
        self.prepare_timing_size = 3
        self.prepare_magnets_size = 2*len(self.manames)+1
        self.cycle_size = (len(self.manames)+3 +  # check params
                           2*len(self.manames) +  # opmode
                           1+round(self._cycle_duration) +  # cycle
                           len(self.manames)+2)  # check final

        # logger
        self._logger = logger
        self._logger_message = ''
        if not logger:
            _log.basicConfig(format='%(asctime)s | %(message)s',
                             datefmt='%F %T', level=_log.INFO,
                             stream=_sys.stdout)

    @property
    def manames(self):
        """Magnets to cycle."""
        return self.cyclers.keys()

    @property
    def mode(self):
        """Mode."""
        return self._mode

    def config_all_magnets(self, ppty):
        """Prepare magnets to cycle according to mode."""
        if ppty == 'opmode':
            manames = [ma for ma in self.manames if 'LI' not in ma]
        else:
            manames = self.manames
        threads = list()
        for maname in manames:
            t = _thread.Thread(
                target=self.config_magnet, args=(maname, ppty), daemon=True)
            self._update_log('Preparing '+maname+' '+ppty+'...')
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def config_magnet(self, maname, ppty):
        """Prepare magnet parameters."""
        if ppty == 'parameters':
            self.cyclers[maname].prepare(self.mode)
        elif ppty == 'opmode' and 'LI' not in maname:
            self.cyclers[maname].set_opmode_cycle(self.mode)

    def config_timing(self):
        """Prepare timing to cycle according to mode."""
        if self._only_linac:
            return
        self._timing.turnoff()
        sections = ['TB', ] if self.mode == 'Cycle' else ['BO', ]
        # TODO: uncomment when using TS and SI
        # sections = ['TB', 'TS', 'SI'] if mode == 'Cycle' else ['BO', ]
        self._update_log('Preparing Timing...')
        self._timing.prepare(self.mode, sections)
        self._update_log(done=True)

    def check_all_magnets(self, ppty):
        """Check all magnets according to mode."""
        if ppty == 'opmode':
            manames = [ma for ma in self.manames if 'LI' not in ma]
        else:
            manames = self.manames
        threads = list()
        self._checks_result = dict()
        for maname in manames:
            t = _thread.Thread(
                target=self.check_magnet,
                args=(maname, ppty), daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        status = True
        for maname in manames:
            self._update_log('Checking '+maname+' '+ppty+'...')
            if self._checks_result[maname]:
                self._update_log(done=True)
            else:
                self._update_log(maname+' is not ready.', error=True)
                status &= False
        return status

    def check_magnet(self, maname, ppty):
        """Check magnet."""
        t0 = _time.time()
        cycler = self.cyclers[maname]
        r = False
        while _time.time()-t0 < TIMEOUT_CHECK:
            if ppty == 'parameters':
                r = cycler.is_prepared(self.mode)
            elif ppty == 'opmode':
                r = cycler.check_opmode_cycle(self.mode)
            if r:
                break
            _time.sleep(TIMEOUT_SLEEP)
        self._checks_result[maname] = r

    def check_timing(self):
        """Check timing preparation."""
        if self._only_linac:
            return True

        sections = ['TB', ] if self.mode == 'Cycle' else ['BO', ]
        # TODO: uncomment when using TS and SI
        # sections = ['TB', 'TS', 'SI'] if self.mode == 'Cycle' else ['BO', ]
        self._update_log('Checking Timing...')
        t0 = _time.time()
        while _time.time()-t0 < TIMEOUT_CHECK/2:
            status = self._timing.check(self.mode, sections)
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
        if 'LI-01:PS-Spect' in self.manames:
            status = (self._pv_egun.value == 0)
            if not status:
                self._update_log(
                    'Linac EGun pulse is enabled! '
                    'Please disable it.', error=True)
            return status
        else:
            return True

    def init(self):
        """Trigger timing according to mode to init cycling."""
        # initialize dict to check which ps is cycling
        self._is_cycling_dict = dict()
        for maname in self.manames:
            self._is_cycling_dict[maname] = True
        self._li_threads = list()
        for psname in self.psnames_li:
            cycler = self.cyclers[psname]
            t = _thread.Thread(target=cycler.cycle, daemon=True)
            self._li_threads.append(t)
            t.start()

        manames = [ma for ma in self.manames if 'LI' not in ma]
        if not manames:
            return
        self._update_log('Triggering timing...')
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

            # verify if magnets started to cycle
            if (self.mode == 'Cycle') and (5 < _time.time() - t0 < 6):
                for maname in self.manames:
                    if _PVName(maname).sec == 'LI':
                        continue
                    if not self.cyclers[maname].get_cycle_enable():
                        self._update_log(maname + ' is not cycling!',
                                         warning=True)
                        self._is_cycling_dict[maname] = False
            if all([v is False for v in self._is_cycling_dict.values()]):
                self._update_log('All magnets failed. Stopping.', error=True)
                return False

            # update keep_waiting
            if self.mode == 'Cycle':
                keep_waiting = _time.time() - t0 < self._cycle_duration
            else:
                keep_waiting = not self._timing.check_ramp_end()

        self._update_log(done=True)
        return True

    def check_all_magnets_final_state(self):
        """Check all magnets final state according to mode."""
        threads = list()
        self._checks_final_result = dict()
        for maname in self.manames:
            t = _thread.Thread(
                target=self.check_magnet_final_state,
                args=(maname, ), daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        for maname in self.manames:
            self._update_log('Checking '+maname+' state...')
            has_prob = self._checks_final_result[maname]
            if has_prob == 0:
                self._update_log(done=True)
            elif has_prob == 1:
                self._update_log(
                    'Verify the number of pulses '+maname+' received!',
                    error=True)
            elif has_prob == 2 and self._is_cycling_dict[maname]:
                self._update_log(maname+' is finishing cycling...',
                                 warning=True)
            elif has_prob == 3:
                self._update_log(maname+' has interlock problems.',
                                 error=True)
        return True

    def check_magnet_final_state(self, maname):
        """Check magnet final state."""
        self._checks_final_result[maname] = \
            self.cyclers[maname].check_final_state(self.mode)

    def reset_all_subsystems(self):
        """Reset all subsystems."""
        if self._only_linac:
            return
        self._update_log('Setting magnets to SlowRef...')
        threads = list()
        for ma in self.manames:
            if 'LI' in ma:
                continue
            t = _thread.Thread(
                target=self.cyclers[ma].set_opmode_slowref, daemon=True)
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

    def prepare_magnets_parameters(self):
        """Prepare to cycle."""
        self.config_all_magnets('parameters')
        if not self.check_all_magnets('parameters'):
            self._update_log(
                'There are magnets not configured to cycle.',
                error=True)
            return
        self._update_log('Magnets parameters preparation finished!')

    def prepare_magnets_opmode(self):
        """Prepare to cycle."""
        self.config_all_magnets('opmode')
        if not self.check_all_magnets('opmode'):
            self._update_log(
                'There are magnets with wrong opmode.',
                error=True)
            return
        self._update_log('Magnets OpMode preparation finished!')

    def cycle(self):
        """Cycle."""
        # check
        if not self.check_egun_off():
            return
        if not self.check_timing():
            return
        if not self.check_all_magnets('parameters'):
            self._update_log(
                'There are magnets not configured to cycle. Stopping.',
                error=True)
            return
        if not self.check_all_magnets('opmode'):
            self._update_log(
                'There are magnets with wrong opmode. Stopping.',
                error=True)
            return

        self.init()
        if not self.wait():
            return
        self.check_all_magnets_final_state()
        _time.sleep(4)  # TODO: replace by checks
        self.reset_all_subsystems()

        # Indicate cycle end
        self._update_log('Cycle finished!')

    # --- private methods ---

    def _manames_2_cycle(self):
        """Return manames to cycle."""
        if self.cyclers:
            manames = _Filter.process_filters(
                self.cyclers.keys(), filters={'sec': 'TB', 'dis': 'MA'})
        # TODO: uncomment when using TS and SI
        #    self.cyclers.keys(), filters={'sec':'(TB|TS|SI)', 'dis':'MA'})
            lipsnames = _Filter.process_filters(
                self.cyclers.keys(), filters={'sec': 'LI', 'dis': 'PS'})
        else:
            manames = _MASearch.get_manames({'sec': 'TB', 'dis': 'MA'})
            lipsnames = _PSSearch.get_psnames({'sec': 'LI', 'dis': 'PS'})
        manames.extend(lipsnames)
        self.psnames_li = lipsnames
        return manames

    def _manames_2_ramp(self):
        """Return manames to ramp."""
        if self.cyclers:
            manames = _Filter.process_filters(
                self.cyclers.keys(), filters={'sec': 'BO', 'dis': 'MA'})
        else:
            manames = _MASearch.get_manames({'sec': 'BO', 'dis': 'MA'})
        return manames

    def _update_log(self, message='', done=False, warning=False, error=False):
        self._logger_message = message
        if self._logger:
            self._logger.update(message, done, warning, error)
        else:
            if done and not message:
                message = 'Done.'
            _log.info(message)
