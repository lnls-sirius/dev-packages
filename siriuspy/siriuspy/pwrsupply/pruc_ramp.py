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

        factors = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

        # Get curves
        pruc = self._controller.pru_controller
        self._original_curves = dict()
        for dev_id in self._dev_ids:
            self._original_curves[dev_id] = pruc.pru_curve_read(dev_id)

        self._curves = list()
        for factor in factors:
            curves = dict()
            for dev_id in self._dev_ids:
                curves[dev_id] = \
                    [factor * value for value in self._original_curves[dev_id]]
            self._curves.append(curves)

        self._size = len(self._curves[0][self._dev_ids[0]])

        self._set_waveform(0)
        self._exit = False

    def stop(self):
        """Stop thread."""
        self._exit = True

    def run(self):
        """Thread execution."""
        print(self._size)
        begin = 0
        next_idx = 1
        while True:
            if self._exit:
                print('leaving thread')
                break
            elif self._state == Ramp.WAIT_RAMP_MODE:
                print('wait ramp mode')
                count = self._controller.pru_controller.pru_sync_pulse_count
                if self._achieved_op_mode() and count == 0:
                    print('going to ramp begin')
                    self._state = Ramp.WAIT_RAMP_BEGIN
            elif self._state == Ramp.WAIT_RAMP_BEGIN:
                count = self._controller.pru_controller.pru_sync_pulse_count
                if count > begin:
                    self._set_waveform(next_idx)
                    begin += self._size
                    next_idx += 1
                    if next_idx == 10 or not self._achieved_op_mode():
                        self.stop()
            _time.sleep(1e-6)

    def _current_op_mode(self):
        return self._controller.read(self._dev_names[0], 'OpMode-Sts')

    def _achieved_op_mode(self):
        return _PSConst.OpMode.RmpWfm == self._current_op_mode()

    def _set_waveform(self, idx):
        pruc = self._controller.pru_controller
        for dev_id in self._dev_ids:
            new_curve = self._curves[idx][dev_id]
            pruc.pru_curve_write(dev_id, new_curve)
