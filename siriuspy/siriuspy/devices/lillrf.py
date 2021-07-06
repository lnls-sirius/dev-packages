"""LI LLRF device."""

import time as _time
import numpy as _np

from .device import DeviceNC as _DeviceNC
from ..csdev import Const as _Const


class LILLRF(_DeviceNC):
    """LI LLRF."""

    class DEVICES:
        """Devices names."""

        LI_SHB = 'LA-RF:LLRF:BUN1'
        LI_KLY1 = 'LA-RF:LLRF:KLY1'
        LI_KLY2 = 'LA-RF:LLRF:KLY2'
        ALL = (LI_SHB, LI_KLY1, LI_KLY2)

    _properties = (
        'SET_AMP', 'GET_AMP',
        'SET_PHASE', 'GET_PHASE',
        'SET_INTEGRAL_ENABLE', 'GET_INTEGRAL_ENABLE',
        'SET_FB_MODE', 'GET_FB_MODE',
        'GET_CH1_SETTING_I', 'GET_CH1_SETTING_Q',
        'GET_CH1_I', 'GET_CH1_Q')

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in LILLRF.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=LILLRF._properties)

    @property
    def amplitude(self):
        """Amplitude."""
        return self['GET_AMP']

    @amplitude.setter
    def amplitude(self, value):
        self['SET_AMP'] = value

    @property
    def phase(self):
        """Phase."""
        return self['GET_PHASE']

    @phase.setter
    def phase(self, value):
        self['SET_PHASE'] = value

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
        self._wait_rb_sp(timeout, 'phase')

    def set_amplitude(self, value, timeout=30):
        """Set and wait for amplitude property to reach value."""
        self.amplitude = value
        self._wait_rb_sp(timeout, 'amplitude')

    def cmd_turn_on_integral_enable(self):
        """Set and wait for integral enable property to reach 'on' state."""
        self.integral_enable = _Const.DsblEnbl.Enbl
        self._wait('GET_INTEGRAL_ENABLE', _Const.DsblEnbl.Enbl, timeout=3)

    def cmd_turn_off_integral_enable(self):
        """Set and wait for integral enable property to reach 'off' state."""
        self.integral_enable = _Const.DsblEnbl.Dsbl
        self._wait('GET_INTEGRAL_ENABLE', _Const.DsblEnbl.Dsbl, timeout=3)

    def cmd_turn_on_feedback_state(self):
        """Set and wait for feedback state property to reach 'on' state."""
        self.feedback_state = _Const.DsblEnbl.Enbl
        self._wait('GET_FB_MODE', _Const.DsblEnbl.Enbl, timeout=3)

    def cmd_turn_off_feedback_state(self):
        """Set and wait for feedback state property to reach 'off' state."""
        self.feedback_state = _Const.DsblEnbl.Dsbl
        self._wait('GET_FB_MODE', _Const.DsblEnbl.Dsbl, timeout=3)

    def cmd_turn_on_feedback_loop(self):
        """Turn on feedback loop."""
        self.cmd_turn_on_integral_enable()
        self.cmd_turn_on_feedback_state()

    def cmd_turn_off_feedback_loop(self):
        """Turn off feedback loop."""
        self.cmd_turn_off_feedback_state()
        self.cmd_turn_off_integral_enable()

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
                    break
            elif propty == 'amplitude':
                if abs(self.amplitude - self['SET_AMP']) < 0.1:
                    break
            else:
                raise Exception(
                    'Set LLRF property (phase or amplitude)')
        else:
            print('timed out waiting LLRF.')
