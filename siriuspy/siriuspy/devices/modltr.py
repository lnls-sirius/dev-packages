"""LI PU device."""

import time as _time

from .device import Device as _Device
from ..csdev import Const as _Const


class LIModltr(_Device):
    """LI LLRF."""

    DEF_TIMEOUT = 10  # [s]

    class DEVICES:
        """Devices names."""

        LI_MOD1 = 'LI-01:PU-Modltr-1'
        LI_MOD2 = 'LI-01:PU-Modltr-2'
        ALL = (LI_MOD1, LI_MOD2)

    PROPERTIES_DEFAULT = (
        'Remote', 'OutPut_Status', 'RESET',
        'Run/Stop', 'PreHeat', 'Charge_Allowed', 'TrigOut_Allowed',
        'Emer_Stop', 'CPS_ALL', 'Thy_Heat', 'Kly_Heat', 'LV_Rdy_OK',
        'HV_Rdy_OK', 'TRIG_Rdy_OK', 'MOD_Self_Fault', 'MOD_Sys_Ready',
        'TRIG_Norm', 'Pulse_Current',
        'RUN_STOP', 'PREHEAT', 'CHARGE', 'TRIGOUT',
        'WRITE_I', 'READI', 'WRITE_V', 'READV')

    def __init__(self, devname, props2init='all'):
        """."""
        # check if device exists
        if devname not in LIModltr.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def run_stop(self):
        """RUN_STOP."""
        return self['RUN_STOP']

    @property
    def preheat(self):
        """PREHEAT."""
        return self['PREHEAT']

    @property
    def charge(self):
        """CHARGE."""
        return self['CHARGE']

    @charge.setter
    def charge(self, value):
        self._enum_setter('CHARGE', value, _Const.OffOn)

    @property
    def trigout(self):
        """TRIGOUT."""
        return self['TRIGOUT']

    @trigout.setter
    def trigout(self, value):
        self._enum_setter('TRIGOUT', value, _Const.OffOn)

    @property
    def voltage(self):
        """READV."""
        return self['READV']

    @voltage.setter
    def voltage(self, value):
        """WRITE_V."""
        self['WRITE_V'] = value

    @property
    def current(self):
        """READI."""
        return self['READI']

    @current.setter
    def current(self, value):
        """WRITE_I."""
        self['WRITE_I'] = value

    def cmd_reset(self, timeout=DEF_TIMEOUT):
        """Reset."""
        self['RESET'] = 1
        if not self._wait('RESET', 1, timeout/2):
            return False
        _time.sleep(1)
        self['RESET'] = 0
        return self._wait('RESET', 0, timeout/2)
