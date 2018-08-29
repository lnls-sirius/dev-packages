"""Class resposible for implementing a ramp of the pru controller curves."""
import threading as _threading
import time as _time

from siriuspy.csdevice.pwrsupply import Const as _PSConst


class Ramp(_threading.Thread):
    """Do the ramp."""

    RAMP_COUNT = 3

    WAIT_RAMP_MODE = 0
    WAIT_RAMP_BEGIN = 1

    def __init__(self, devices, controller):
        """Constructor."""
        super().__init__(daemon=True)
        self._devices = devices
        self._dev_names = list(self._devices.keys())
        self._dev_ids = list(self._devices.values())
        self._controller = controller
        self._state = Ramp.WAIT_RAMP_MODE
        self._factors = [0.25, 0.5, 0.75, 1]

        pruc = self._controller.pru_controller
        self._original_curves = dict()
        for dev_id in self._dev_ids:
            self._original_curves[dev_id] = pruc.pru_curve_read(dev_id)

        self._size = len(self._original_curves[self._dev_ids[0]])
        self._set_waveform(0)
        self._exit = False

    def stop(self):
        """Stop thread."""
        self._exit = True

    def run(self):
        """Thread execution."""
        while True:
            if self._exit:
                break
            elif self._state == Ramp.WAIT_RAMP_MODE:
                if self._achieved_op_mode():
                    self._state = Ramp.WAIT_RAMP_BEGIN
            elif self._state == Ramp.WAIT_RAMP_BEGIN:
                count = self._controller.pru_controller.pru_sync_pulse_count
                if count > 0 and count < self._size:
                    self._set_waveform(1)
                elif count > self._size and count < 2 * self._size:
                    self._set_waveform(2)
                elif count > 2 * self._size:
                    self._set_waveform(-1)
                    self.stop()
                if not self._achieved_op_mode():
                    self.stop()
            _time.sleep(1e-2)

    def _current_op_mode(self):
        return self.controller.read(self._dev_names[0], 'OpMode-Sts')

    def _achieved_op_mode(self):
        return _PSConst.OpMode.RmpWfm == self._current_op_mode()

    def _set_waveform(self, factor_idx):
        pruc = self._controller.pru_controller
        factor = self._factors[factor_idx]
        for dev_id in self._dev_ids:
            curve = self._original_curves[dev_id]
            new_curve = [factor * value for value in curve]
            pruc.pru_curve_write(dev_id, new_curve)
