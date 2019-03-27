"""Thread used to watcher power supply operation mode."""
import time as _time
import threading as _threading

from siriuspy.csdevice.pwrsupply import Const as _PSConst


class Watcher(_threading.Thread):
    """Watcher PS on given operation mode."""

    INSTANCE_COUNT = 0

    WAIT_OPMODE = 0
    WAIT_TRIGGER = 1
    WAIT_CYCLE = 2
    WAIT_MIG = 3
    WAIT_RMP = 4

    def __init__(self, writers, controller, dev_name, op_mode):
        """Init thread."""
        super().__init__(daemon=True)
        self.writers = writers
        self.controller = controller
        self.dev_name = dev_name
        self.op_mode = op_mode
        self.wait = 1.0/controller.pru_controller.params.FREQ_SCAN
        self.state = Watcher.WAIT_OPMODE
        self.exit = False

    def run(self):
        """Thread execution."""
        Watcher.INSTANCE_COUNT += 1
        if self.op_mode == _PSConst.OpMode.Cycle:
            self._watch_cycle()
        elif self.op_mode == _PSConst.OpMode.MigWfm:
            self._watch_mig()
        elif self.op_mode == _PSConst.OpMode.RmpWfm:
            self._watch_rmp()
        Watcher.INSTANCE_COUNT -= 1

    def stop(self):
        """Stop thread."""
        self.exit = True

    def _watch_cycle(self):
        while True:
            if self.exit:
                break
            elif self.state == Watcher.WAIT_OPMODE:
                if self._achieved_op_mode() and self._sync_started():
                    self.state = Watcher.WAIT_TRIGGER
                elif self._cycle_started() and self._sync_pulsed():
                    self.state = Watcher.WAIT_CYCLE
            elif self.state == Watcher.WAIT_TRIGGER:
                if self._changed_op_mode():
                    break
                elif self._sync_stopped():
                    if self._cycle_started() or self._sync_pulsed():
                        self.state = Watcher.WAIT_CYCLE
                    else:
                        break
            elif self.state == Watcher.WAIT_CYCLE:
                if self._changed_op_mode():
                    break
                elif self._cycle_stopped():
                    # self._set_current()
                    self._set_slow_ref()
                    break
            _time.sleep(self.wait)

    def _watch_mig(self):
        while True:
            if self.exit:
                break
            elif self.state == Watcher.WAIT_OPMODE:
                if self._achieved_op_mode() and self._sync_started():
                    self.state = Watcher.WAIT_MIG
            elif self.state == Watcher.WAIT_MIG:
                if self._sync_stopped() or self._changed_op_mode():
                    if self._sync_pulsed():
                        self._set_current()
                        self._set_slow_ref()
                    break
            _time.sleep(self.wait)

    def _watch_rmp(self):
        while True:
            if self.exit:
                break
            elif self.state == Watcher.WAIT_OPMODE:
                if self._achieved_op_mode() and self._sync_started():
                    self.state = Watcher.WAIT_RMP
            elif self.state == Watcher.WAIT_RMP:
                if self._sync_stopped() or self._changed_op_mode():
                    if self._sync_pulsed():
                        self._set_current()
                    break
            _time.sleep(self.wait)

    def _current_op_mode(self):
        return self.controller.read(self.dev_name, 'OpMode-Sts') - 3

    def _achieved_op_mode(self):
        return self.op_mode == self._current_op_mode()

    def _changed_op_mode(self):
        return self.op_mode != self._current_op_mode()

    def _cycle_started(self):
        return self.controller.read(self.dev_name, 'CycleEnbl-Mon') == 1

    def _cycle_stopped(self):
        return self.controller.read(self.dev_name, 'CycleEnbl-Mon') == 0

    def _sync_started(self):
        return self.controller.pru_controller.pru_sync_status == 1

    def _sync_stopped(self):
        return self.controller.pru_controller.pru_sync_status == 0

    def _sync_pulsed(self):
        return self.controller.pru_controller.pru_sync_pulse_count > 0

    def _set_current(self):
        dev_name = self.dev_name
        if self.op_mode == _PSConst.OpMode.Cycle:
            val = self.controller.read(dev_name, 'CycleOffset-RB')
        else:
            val = self.controller.read(dev_name, 'WfmData-RB')[-1]
        self.writers['Current-SP'].execute(val)

    def _set_slow_ref(self):
        self.writers['OpMode-Sel'].execute(_PSConst.OpMode.SlowRef)
