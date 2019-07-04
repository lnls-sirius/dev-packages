"""Main cycle module."""

import sys as _sys
import time as _time
import logging as _log
import threading as _thread
from siriuspy.namesys import Filter as _Filter
from siriuspy.search import MASearch as _MASearch
from .conn import MagnetCycler, Timing

TIMEOUT_SLEEP = 0.1
TIMEOUT_CHECK = 20


class CycleController:
    """Class to perform automated cycle procedure."""

    def __init__(self, cyclers=None, timing=None,
                 is_bo=False, ramp_config=None, logger=None):
        """Initialize."""
        if cyclers:
            self.cyclers = cyclers
        else:
            if is_bo:
                manames = _MASearch.get_manames({'sec': 'BO', 'dis': 'MA'})
            else:
                manames = _MASearch.get_manames({'sec': 'TB', 'dis': 'MA'})
                # manames = _MASearch.get_manames(
                #     {'sec': '(TB|TS|SI)', 'dis': 'MA'})
            self.cyclers = dict()
            for maname in manames:
                self.cyclers[maname] = MagnetCycler(maname, ramp_config)
        self._timing = timing if timing is not None else Timing()

        self._logger = logger
        self._logger_message = ''
        if not logger:
            _log.basicConfig(
                format='%(asctime)s | %(message)s',
                datefmt='%F %T', level=_log.INFO, stream=_sys.stdout)

        ma2cycle = self._manames_2_cycle()
        ma2ramp = self._manames_2_ramp()
        if ma2cycle and ma2ramp:
            raise Exception('Can not cycle Booster with other accelerators!')
        elif ma2cycle:
            self._mode = 'Cycle'
        else:
            self._mode = 'Ramp'

        self._cycle_duration = 0
        for ma in self.manames:
            self._cycle_duration = max(
                self._cycle_duration,
                self.cyclers[ma].cycle_duration(self._mode))

        self.aborted = False
        self._prepare_size = None
        self._cycle_size = None

    @property
    def manames(self):
        """Magnets to cycle."""
        return self.cyclers.keys()

    @property
    def mode(self):
        """Mode."""
        return self._mode

    @property
    def prepare_size(self):
        """Prepare size."""
        if not self._prepare_size:
            s_check = len(self.manames) + 3
            s_prep = len(self.manames) + 3
            self._prepare_size = s_check + s_prep
        return self._prepare_size

    @property
    def cycle_size(self):
        """Cycle size."""
        if not self._cycle_size:
            s_check = len(self.manames)+3
            s_cycle = round(self._cycle_duration)+3*len(self.manames)+4
            self._cycle_size = s_check + s_cycle
        return self._cycle_size

    def prepare_all_magnets(self, ppty):
        """Prepare magnets to cycle according to mode."""
        threads = list()
        for maname in self.manames:
            t = _thread.Thread(
                target=self.prepare_magnet, args=(maname, ppty), daemon=True)
            self._update_log('Preparing '+maname+' '+ppty+'...')
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return

    def prepare_magnet(self, maname, ppty):
        """Prepare magnet parameters."""
        if ppty == 'parameters':
            self.cyclers[maname].prepare(self.mode)
        elif ppty == 'opmode':
            self.cyclers[maname].set_opmode_cycle(self.mode)

    def prepare_timing(self):
        """Prepare timing to cycle according to mode."""
        self._timing.turnoff()
        sections = ['TB', ] if self.mode == 'Cycle' else ['BO', ]
        # TODO: uncomment when using TS and SI
        # sections = ['TB', 'TS', 'SI'] if mode == 'Cycle' else ['BO', ]
        self._update_log('Preparing Timing...')
        self._timing.prepare(self.mode, sections)
        self._update_log(done=True)

    def check_all_magnets(self, ppty):
        """Check all magnets according to mode."""
        threads = list()
        self._checks_result = dict()
        for maname in self.manames:
            t = _thread.Thread(
                target=self.check_magnet,
                args=(maname, ppty), daemon=True)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return False

        for maname in self.manames:
            self._update_log('Checking '+maname+' '+ppty+'...')
            if self._checks_result[maname]:
                self._update_log(done=True)
            else:
                self._update_log(maname+' is not ready.', error=True)
                return False
        return True

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
        sections = ['TB', ] if self.mode == 'Cycle' else ['BO', ]
        # TODO: uncomment when using TS and SI
        # sections = ['TB', 'TS', 'SI'] if mode == 'Cycle' else ['BO', ]
        self._update_log('Checking Timing...')
        t0 = _time.time()
        while _time.time()-t0 < TIMEOUT_CHECK:
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

    def init(self):
        """Trigger timing according to mode to init cycling."""
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
                          self._timing.DEFAULT_RAMP_DURATION/1000000)
            self._update_log('Remaining time: {}s...'.format(t))

            # verify if magnets started to cycle
            if (self.mode == 'Cycle') and (5 < _time.time() - t0 < 8):
                for maname in self.manames:
                    if not self.cyclers[maname].get_cycle_enable():
                        self._update_log(
                            'Magnets are not cycling! Verify triggers!',
                            error=True)
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
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return False

        for maname in self.manames:
            self._update_log('Checking '+maname+' final state...')
            has_prob = self._checks_final_result[maname]
            if not has_prob:
                self._update_log(done=True)
            elif has_prob == 1:
                self._update_log(
                    'Verify the number of pulses '+maname+' received!',
                    warning=True)
            elif has_prob == 2:
                self._update_log(maname+' is finishing cycling...',
                                 warning=True)
            else:
                self._update_log(maname+' has interlock problems.',
                                 error=True)
        return True

    def check_magnet_final_state(self, maname):
        """Check magnet final state."""
        self._checks_final_result[maname] = \
            self.cyclers[maname].check_final_state(self.mode)

    def reset_all_subsystems(self):
        """Reset all subsystems."""
        self._update_log('Setting magnets to SlowRef...')
        threads = list()
        for ma in self.manames:
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

    def prepare(self):
        """Prepare to cycle."""
        self.prepare_all_magnets('parameters')
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return
        self.prepare_timing()
        if not self.check():
            return
        self._update_log('Preparation finished!')

    def check(self):
        """Check cycle preparation."""
        if not self.check_all_magnets('parameters'):
            self._update_log(
                'There are magnets not configured to cycle. Stopping.',
                error=True)
            return False
        if not self.check_timing():
            return False
        return True

    def cycle(self):
        """Cycle."""
        if not self.check():
            return
        if self.aborted:
            self._update_log('Aborted.', error=True)
            return

        self.prepare_all_magnets('opmode')
        if not self.check_all_magnets('opmode'):
            self._update_log(
                'There are magnets with wrong opmode. Stopping.',
                error=True)
            return
        if self.aborted:
            self._update_log('Aborted.', error=True)
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
        return _Filter.process_filters(
            self.cyclers.keys(), filters={'sec': 'TB', 'dis': 'MA'})
        # TODO: uncomment when using TS and SI
        #    self.cyclers.keys(), filters={'sec': '(TB|TS|SI)', 'dis': 'MA'})

    def _manames_2_ramp(self):
        """Return manames to ramp."""
        return _Filter.process_filters(
            self.cyclers.keys(), filters={'sec': 'BO', 'dis': 'MA'})

    def _update_log(self, message='', done=False, warning=False, error=False):
        self._logger_message = message
        if self._logger:
            self._logger.update(message, done, warning, error)
        else:
            if done and not message:
                message = 'Done.'
            _log.info(message)
