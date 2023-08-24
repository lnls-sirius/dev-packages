"""LI LLRF device."""

import time as _time
import numpy as _np

from .device import Device as _Device, DeviceSet as _DeviceSet
from ..csdev import Const as _Const


class DevLILLRF(_Device):
    """Linac-LLRF single device (SHB, Klystron1 or Klystron2)."""

    DEF_TIMEOUT = 10  # [s]

    class DEVICES:
        """Devices names."""

        LI_SHB = 'LA-RF:LLRF:BUN1'
        LI_KLY1 = 'LA-RF:LLRF:KLY1'
        LI_KLY2 = 'LA-RF:LLRF:KLY2'
        ALL = (LI_SHB, LI_KLY1, LI_KLY2)

    PROPERTIES_DEFAULT = (
        'SET_AMP', 'GET_AMP',
        'SET_PHASE', 'GET_PHASE',
        'SET_INTEGRAL_ENABLE', 'GET_INTEGRAL_ENABLE',
        'SET_FB_MODE', 'GET_FB_MODE',
        'GET_CH1_SETTING_I', 'GET_CH1_SETTING_Q',
        'GET_CH1_I', 'GET_CH1_Q')

    def __init__(self, devname, props2init='all'):
        """."""
        # check if device exists
        if devname not in DevLILLRF.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, props2init=props2init)

    @property
    def amplitude(self):
        """Amplitude."""
        return self['GET_AMP']

    @amplitude.setter
    def amplitude(self, value):
        self['SET_AMP'] = value

    @property
    def phase(self):
        """Phase in [deg]."""
        return self['GET_PHASE']

    @phase.setter
    def phase(self, value):
        self['SET_PHASE'] = self._wrap_phase(value)

    @property
    def integral_enable(self):
        """Integral Enable."""
        return self['GET_INTEGRAL_ENABLE']

    @integral_enable.setter
    def integral_enable(self, value):
        self['SET_INTEGRAL_ENABLE'] = value

    @property
    def feedback_state(self):
        """Feedback State."""
        return self['GET_FB_MODE']

    @feedback_state.setter
    def feedback_state(self, value):
        self['SET_FB_MODE'] = value

    @property
    def i_ref(self):
        """I reference."""
        return self['GET_CH1_SETTING_I']

    @property
    def q_ref(self):
        """Q reference."""
        return self['GET_CH1_SETTING_Q']

    @property
    def i_mon(self):
        """I monitor."""
        return self['GET_CH1_I']

    @property
    def q_mon(self):
        """Q monitor."""
        return self['GET_CH1_Q']

    def set_phase(self, value, timeout=10):
        """Set and wait for phase property to reach value."""
        self.phase = value
        return self._wait_rb_sp(timeout, 'phase')

    def set_amplitude(self, value, timeout=30):
        """Set and wait for amplitude property to reach value."""
        self.amplitude = value
        return self._wait_rb_sp(timeout, 'amplitude')

    def cmd_turn_on_integral_enable(self, timeout=DEF_TIMEOUT):
        """Set and wait for integral enable property to reach 'on' state."""
        self.integral_enable = _Const.DsblEnbl.Enbl
        return self._wait(
            'GET_INTEGRAL_ENABLE', _Const.DsblEnbl.Enbl, timeout=timeout)

    def cmd_turn_off_integral_enable(self, timeout=DEF_TIMEOUT):
        """Set and wait for integral enable property to reach 'off' state."""
        self.integral_enable = _Const.DsblEnbl.Dsbl
        return self._wait(
            'GET_INTEGRAL_ENABLE', _Const.DsblEnbl.Dsbl, timeout=timeout)

    def cmd_turn_on_feedback_state(self, timeout=DEF_TIMEOUT):
        """Set and wait for feedback state property to reach 'on' state."""
        self.feedback_state = _Const.DsblEnbl.Enbl
        return self._wait(
            'GET_FB_MODE', _Const.DsblEnbl.Enbl, timeout=timeout)

    def cmd_turn_off_feedback_state(self, timeout=DEF_TIMEOUT):
        """Set and wait for feedback state property to reach 'off' state."""
        self.feedback_state = _Const.DsblEnbl.Dsbl
        return self._wait(
            'GET_FB_MODE', _Const.DsblEnbl.Dsbl, timeout=timeout)

    def cmd_turn_on_feedback_loop(self, timeout=DEF_TIMEOUT):
        """Turn on feedback loop."""
        if not self.cmd_turn_on_integral_enable(timeout=timeout/2):
            return False
        return self.cmd_turn_on_feedback_state(timeout=timeout/2)

    def cmd_turn_off_feedback_loop(self, timeout=DEF_TIMEOUT):
        """Turn off feedback loop."""
        if not self.cmd_turn_off_feedback_state(timeout=timeout/2):
            return False
        return self.cmd_turn_off_integral_enable(timeout=timeout/2)

    def check_feeedback_loop(self, tol=5e-3):
        """Check if feedback loop is closed within a tolerance."""
        sp_vec = _np.array([self.i_ref, self.q_ref])
        rb_vec = _np.array([self.i_mon, self.q_mon])
        diff = _np.linalg.norm(rb_vec - sp_vec)
        return diff < tol

    def wait_feedback_loop(self, tol=5e-3, timeout=10):
        """Wait for feedback loop to be closed."""
        ntrials = int(timeout/0.1)
        _time.sleep(4*0.1)
        for _ in range(ntrials):
            if self.check_feeedback_loop(tol):
                return True
            _time.sleep(0.1)
        return False

    def _wait_rb_sp(self, timeout=10, propty=None):
        """Wait for property readback to reach setpoint."""
        nrp = int(timeout / 0.1)
        for _ in range(nrp):
            _time.sleep(0.1)
            if propty == 'phase':
                if abs(self.phase - self['SET_PHASE']) < 0.1:
                    return True
            elif propty == 'amplitude':
                if abs(self.amplitude - self['SET_AMP']) < 0.1:
                    return True
            else:
                raise Exception(
                    'Set LLRF property (phase or amplitude)')
        print('timed out waiting LLRF.')
        return False

    @staticmethod
    def _wrap_phase(phase):
        """Phase must be in [-180, +180] interval."""
        return (phase + 180) % 360 - 180


class LILLRF(_DeviceSet):
    """Linac Low-Level-RF devices."""

    def __init__(self):
        """."""
        shb = DevLILLRF(DevLILLRF.DEVICES.LI_SHB)
        klystron1 = DevLILLRF(DevLILLRF.DEVICES.LI_KLY1)
        klystron2 = DevLILLRF(DevLILLRF.DEVICES.LI_KLY2)
        devices = (shb, klystron1, klystron2)

        # call base class constructor
        super().__init__(devices)

    @property
    def dev_shb(self):
        """Sub-Harmonic Buncher (SHB) device."""
        return self.devices[0]

    @property
    def dev_klystron1(self):
        """Klystron 1 device."""
        return self.devices[1]

    @property
    def dev_klystron2(self):
        """Klystron 2 device."""
        return self.devices[2]

    def shift_phase(self, delta_phase):
        """Shift LILLRF using SHB phase variation as reference."""
        shb_phase0 = self.dev_shb.phase
        kly1_phase0 = self.dev_klystron1.phase
        kly2_phase0 = self.dev_klystron2.phase

        self.dev_shb.set_phase(shb_phase0 + delta_phase)
        # Klystrons frequencies are 6 times larger than SHB's
        self.dev_klystron1.set_phase(kly1_phase0 + 6*delta_phase)
        self.dev_klystron2.set_phase(kly2_phase0 + 6*delta_phase)
