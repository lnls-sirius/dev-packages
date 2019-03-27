"""Class resposible for implementing a ramp of the pru controller curves."""
import threading as _threading
import time as _time

from siriuspy.csdevice.pwrsupply import Const as _PSConst


class Ramp(_threading.Thread):
    """Do the ramp."""

    WAIT_RAMP_MODE = 0
    WAIT_RAMP_BEGIN = 1
    WAIT_RAMP_END = 2

    def __init__(self, devices, controller):
        """Constructor."""
        super().__init__(daemon=True)
        self._devices = devices
        self._dev_names = list(self._devices.keys())
        self._dev_ids = list(self._devices.values())
        self._controller = controller
        self._pruc = self._controller.pru_controller
        self._state = Ramp.WAIT_RAMP_MODE

        self._length = self._controller.pru_controller.ramp_offset
        factors = [1/(self._length/(i + 1)) for i in range(self._length)]
        # factors = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

        # Get curves
        pruc = self._controller.pru_controller
        self._original_curves = dict()
        for dev_id in self._dev_ids:
            self._original_curves[dev_id] = pruc.pru_curve_read(dev_id)

        self._curves = list()
        for factor in factors:
            curves = dict()
            for dev_id in self._dev_ids:
                w0 = self._original_curves[dev_id]
                w0_min = min(w0)
                curves[dev_id] = [w0_min + factor * (v - w0_min) for v in w0]
            self._curves.append(curves)

        self._wfm_size = len(self._curves[0][self._dev_ids[0]])

        self._set_waveform(0)
        self._exit = False

    def stop(self):
        """Stop thread."""
        self._exit = True

    def run(self):
        """Thread execution."""
        wfm_set = 0
        self._pruc.ramp_offset_count = -1
        while True:
            if self._exit:
                break
            elif self._state == Ramp.WAIT_RAMP_MODE:
                self._waiting_ramp()
            elif self._state == Ramp.WAIT_RAMP_BEGIN:
                if not self._achieved_op_mode:
                    self.stop()
                elif self._wfm_in_progress(wfm_set):  # Set next wfm
                    wfm_set += 1
                    self._pruc.ramp_offset_count += 1
                    if wfm_set == self._length:
                        self._state = Ramp.WAIT_RAMP_END
                    else:
                        self._set_waveform(wfm_set)
            elif self._state == Ramp.WAIT_RAMP_END:
                if not self._achieved_op_mode:
                    self.stop()
                elif self._ramp_finised():
                    self._pruc.ramp_offset_count += 1
                    self.stop()

            _time.sleep(1e-3)

        if self._pruc.ramp_offset_count < self._length:
            self._set_waveform(self._length - 1)

    def _waiting_ramp(self):
        # Wait ramp operation mode
        count = self._pruc.pru_sync_pulse_count
        if self._achieved_op_mode() and count == 0:
            self._state = Ramp.WAIT_RAMP_BEGIN

    def _wfm_in_progress(self, cur_wfm):
        progress = \
            self._pruc.pru_sync_pulse_count / self._wfm_size
        if progress > cur_wfm:
            return True
        return False

    def _ramp_finised(self):
        progress = \
            self._pruc.pru_sync_pulse_count / self._wfm_size
        if progress > self._length:
            return True
        else:
            return False

    def _current_op_mode(self):
        return self._controller.read(self._dev_names[0], 'OpMode-Sts')

    def _achieved_op_mode(self):
        return _PSConst.States.RmpWfm == self._current_op_mode()

    def _set_waveform(self, idx):
        for dev_id in self._dev_ids:
            new_curve = self._curves[idx][dev_id]
            self._pruc.pru_curve_set(dev_id, new_curve)
        self._pruc.pru_curve_send()
