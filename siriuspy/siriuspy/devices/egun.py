"""E-Gun devices."""

import time as _time
from datetime import timedelta as _timedelta
import numpy as _np

from ..pwrsupply.psctrl.pscstatus import PSCStatus as _PSCStatus

from .device import Device as _Device, Devices as _Devices, \
    DeviceNC as _DeviceNC
from .timing import Trigger


class EGBias(_Device):
    """EGun Bias Device."""

    DEF_TIMEOUT = 10  # [s]
    PWRSTATE = _PSCStatus.PWRSTATE

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-BiasPS'
        ALL = (LI, )

    _properties = (
        'voltoutsoft', 'voltinsoft', 'currentinsoft', 'switch', 'swstatus')

    def __init__(self, devname=None):
        """."""
        if devname is None:
            devname = EGBias.DEVICES.LI

        # check if device exists
        if devname not in EGBias.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EGBias._properties)

    @property
    def voltage(self):
        """."""
        return self['voltinsoft']

    @voltage.setter
    def voltage(self, value):
        self['voltoutsoft'] = value

    @property
    def current(self):
        """."""
        return self['currentinsoft']

    def cmd_turn_on(self, timeout=DEF_TIMEOUT):
        """."""
        self['switch'] = self.PWRSTATE.On
        return self._wait('swstatus', self.PWRSTATE.On, timeout)

    def cmd_turn_off(self, timeout=DEF_TIMEOUT):
        """."""
        self['switch'] = self.PWRSTATE.Off
        return self._wait('swstatus', self.PWRSTATE.Off, timeout)

    def is_on(self):
        """."""
        return self['swstatus'] == self.PWRSTATE.On

    def set_voltage(self, value, tol=0.2, timeout=DEF_TIMEOUT):
        """Set voltage and wait readback reach value with a tolerance."""
        self.voltage = value
        nrp = int(timeout / 0.1)
        for _ in range(nrp):
            if abs(self.voltage - value) < tol:
                return True
            _time.sleep(0.1)
        print('timed out waiting for EGBias voltage to reach ',
              value, 'with tolerance ', tol)
        return False


class EGFilament(_Device):
    """EGun Filament Device."""

    DEF_TIMEOUT = 10  # [s]
    PWRSTATE = _PSCStatus.PWRSTATE

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-FilaPS'
        ALL = (LI, )

    _properties = (
        'voltinsoft', 'currentinsoft', 'currentoutsoft', 'switch', 'swstatus')

    def __init__(self, devname=None):
        """."""
        if devname is None:
            devname = EGFilament.DEVICES.LI

        # check if device exists
        if devname not in EGFilament.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EGFilament._properties)

    @property
    def voltage(self):
        """."""
        return self['voltinsoft']

    @property
    def current(self):
        """."""
        return self['currentinsoft']

    @current.setter
    def current(self, value):
        """."""
        self['currentoutsoft'] = value

    def cmd_turn_on(self, timeout=DEF_TIMEOUT):
        """."""
        self['switch'] = self.PWRSTATE.On
        return self._wait('swstatus', self.PWRSTATE.On, timeout)

    def cmd_turn_off(self, timeout=DEF_TIMEOUT):
        """."""
        self['switch'] = self.PWRSTATE.Off
        return self._wait('swstatus', self.PWRSTATE.Off, timeout)

    def is_on(self):
        """."""
        return self['swstatus'] == self.PWRSTATE.On

    def wait_current(self, value, tol=0.20, timeout=DEF_TIMEOUT):
        """Wait current to reach value with tolerance 'tol'."""
        _t0 = _time.time()
        while _time.time() - _t0 < timeout:
            if abs(self.current - value) < tol:
                return True
            _time.sleep(0.1)
        return False


class EGHVPS(_Device):
    """Egun High-Voltage Power Supply Device."""

    DEF_TIMEOUT = 10  # [s]
    PWRSTATE = _PSCStatus.PWRSTATE

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-HVPS'
        ALL = (LI, )

    _properties = (
        'currentinsoft', 'currentoutsoft',
        'voltinsoft', 'voltoutsoft',
        'enable', 'enstatus',
        'switch', 'swstatus')

    def __init__(self, devname=None):
        """."""
        if devname is None:
            devname = EGHVPS.DEVICES.LI

        # check if device exists
        if devname not in EGHVPS.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EGHVPS._properties)

    @property
    def current(self):
        """."""
        return self['currentinsoft']

    @current.setter
    def current(self, value):
        """."""
        self['currentoutsoft'] = value

    @property
    def voltage(self):
        """."""
        return self['voltinsoft']

    @voltage.setter
    def voltage(self, value):
        self['voltoutsoft'] = value

    def cmd_turn_on(self, timeout=DEF_TIMEOUT):
        """."""
        self['enable'] = self.PWRSTATE.On
        if not self._wait('enstatus', self.PWRSTATE.On, timeout=timeout/2):
            return False
        self['switch'] = self.PWRSTATE.On
        return self._wait('swstatus', self.PWRSTATE.On, timeout=timeout/2)

    def cmd_turn_off(self, timeout=DEF_TIMEOUT):
        """."""
        self['enable'] = self.PWRSTATE.Off
        if not self._wait('enstatus', self.PWRSTATE.Off, timeout=timeout/2):
            return False
        self['switch'] = self.PWRSTATE.Off
        return self._wait('swstatus', self.PWRSTATE.Off, timeout=timeout/2)

    def is_on(self):
        """."""
        ison = self['enstatus'] == self.PWRSTATE.On
        ison &= self['swstatus'] == self.PWRSTATE.On
        return ison

    def wait_voltage(self, value, tol=1, timeout=DEF_TIMEOUT):
        """Wait voltage to reach value with tolerance 'tol'."""
        _t0 = _time.time()
        while _time.time() - _t0 < timeout:
            if abs(self.voltage - value) < tol:
                return True
            _time.sleep(0.1)
        return False


class EGTriggerPS(_Device):
    """Egun Trigger Power Supply Device."""

    DEF_TIMEOUT = 10  # [s]

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-TriggerPS'
        ALL = (LI, )

    _properties = (
        'status', 'allow', 'enable', 'enablereal')

    def __init__(self, devname=DEVICES.LI):
        """."""
        # check if device exists
        if devname not in EGTriggerPS.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EGTriggerPS._properties)

    @property
    def status(self):
        """."""
        return self['status']

    @property
    def allow(self):
        """."""
        return self['allow']

    @property
    def enable(self):
        """."""
        return self['enablereal']

    @enable.setter
    def enable(self, value):
        self['enable'] = bool(value)

    def cmd_enable_trigger(self, timeout=DEF_TIMEOUT):
        """."""
        self['enable'] = 1
        return self._wait('enablereal', value=1, timeout=timeout)

    def cmd_disable_trigger(self, timeout=DEF_TIMEOUT):
        """."""
        self['enable'] = 0
        return self._wait('enablereal', value=0, timeout=timeout)

    def is_on(self):
        """."""
        return self['enablereal'] == 1


class EGPulsePS(_Device):
    """Egun Pulse Power Supply Device."""

    DEF_TIMEOUT = 10  # [s]

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-PulsePS'
        ALL = (LI, )

    _properties = (
        'singleselect', 'singleselstatus', 'singleswitch', 'singleswstatus',
        'multiselect', 'multiselstatus', 'multiswitch', 'multiswstatus',
        'poweroutsoft', 'powerinsoft')

    def __init__(self, devname=DEVICES.LI):
        """Init."""
        # check if device exists
        if devname not in EGPulsePS.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EGPulsePS._properties)

    @property
    def single_bunch_mode(self):
        """Single bunch mode."""
        return self['singleselstatus']

    @single_bunch_mode.setter
    def single_bunch_mode(self, value):
        self['singleselect'] = value

    @property
    def single_bunch_switch(self):
        """Single bunch switch."""
        return self['singleswstatus']

    @single_bunch_switch.setter
    def single_bunch_switch(self, value):
        self['singleswitch'] = value

    @property
    def multi_bunch_mode(self):
        """Multi bunch mode."""
        return self['multiselstatus']

    @multi_bunch_mode.setter
    def multi_bunch_mode(self, value):
        self['multiselect'] = value

    @property
    def multi_bunch_switch(self):
        """Multi bunch switch."""
        return self['multiswstatus']

    @multi_bunch_switch.setter
    def multi_bunch_switch(self, value):
        self['multiswitch'] = value

    @property
    def power(self):
        """Power."""
        return self['powerinsoft']

    @power.setter
    def power(self, value):
        self['poweroutsoft'] = value

    def cmd_turn_off_single_bunch_switch(self, timeout=DEF_TIMEOUT):
        """Turn off single bunch switch."""
        self.single_bunch_switch = 0
        return self._wait('singleswstatus', 0, timeout=timeout)

    def cmd_turn_off_single_bunch_mode(self, timeout=DEF_TIMEOUT):
        """Turn off single bunch mode."""
        self.single_bunch_mode = 0
        return self._wait('singleselstatus', 0, timeout=timeout)

    def cmd_turn_off_single_bunch(self, timeout=DEF_TIMEOUT):
        """Turn off single bunch."""
        if not self.cmd_turn_off_single_bunch_switch():
            return False
        return self.cmd_turn_off_single_bunch_mode()

    def cmd_turn_on_single_bunch_switch(self, timeout=DEF_TIMEOUT):
        """Turn on single bunch switch."""
        self.single_bunch_switch = 1
        return self._wait('singleswstatus', 1, timeout=timeout)

    def cmd_turn_on_single_bunch_mode(self, timeout=DEF_TIMEOUT):
        """Turn on single bunch mode."""
        self.single_bunch_mode = 1
        return self._wait('singleselstatus', 1, timeout=timeout)

    def cmd_turn_on_single_bunch(self, timeout=DEF_TIMEOUT):
        """Turn on single bunch."""
        if not self.cmd_turn_on_single_bunch_mode():
            return False
        return self.cmd_turn_on_single_bunch_switch()

    def cmd_turn_off_multi_bunch_switch(self, timeout=DEF_TIMEOUT):
        """Turn off multi bunch switch."""
        self.multi_bunch_switch = 0
        return self._wait('multiswstatus', 0, timeout=timeout)

    def cmd_turn_off_multi_bunch_mode(self, timeout=DEF_TIMEOUT):
        """Turn off multi bunch mode."""
        self.multi_bunch_mode = 0
        return self._wait('multiselstatus', 0, timeout=timeout)

    def cmd_turn_off_multi_bunch(self, timeout=DEF_TIMEOUT):
        """Turn off multi bunch."""
        if not self.cmd_turn_off_multi_bunch_switch():
            return False
        return self.cmd_turn_off_multi_bunch_mode()

    def cmd_turn_on_multi_bunch_switch(self, timeout=DEF_TIMEOUT):
        """Turn on multi bunch switch."""
        self.multi_bunch_switch = 1
        return self._wait('multiswstatus', 1, timeout=timeout)

    def cmd_turn_on_multi_bunch_mode(self, timeout=DEF_TIMEOUT):
        """Turn on multi bunch mode."""
        self.multi_bunch_mode = 1
        return self._wait('multiselstatus', 1, timeout=timeout)

    def cmd_turn_on_multi_bunch(self, timeout=DEF_TIMEOUT):
        """Turn on multi bunch."""
        if not self.cmd_turn_on_multi_bunch_mode():
            return False
        return self.cmd_turn_on_multi_bunch_switch()


class EGun(_Devices):
    """EGun device."""

    DEF_TIMEOUT = 10  # [s]
    BIAS_MULTI_BUNCH = -46.0  # [V]
    BIAS_SINGLE_BUNCH = -80.0  # [V]
    BIAS_TOLERANCE = 1.0  # [V]
    HV_OPVALUE = 90.0  # [V]
    HV_TOLERANCE = 1.0  # [V]
    FILACURR_OPVALUE = 1.34  # [A]
    FILACURR_TOLERANCE = 0.20  # [A]

    def __init__(self):
        """Init."""
        self.bias = EGBias()
        self.fila = EGFilament()
        self.hvps = EGHVPS()
        self.trigps = EGTriggerPS()
        self.pulse = EGPulsePS()
        self.trigsingle = Trigger('LI-01:TI-EGun-SglBun')
        self.trigmulti = Trigger('LI-01:TI-EGun-MultBun')
        self.trigmultipre = Trigger('LI-01:TI-EGun-MultBunPre')

        self.sys_ext = _DeviceNC('LI-01:EG-External', ('status', ))
        self.sys_vlv = _DeviceNC('LI-01:EG-Valve', ('status', ))
        self.sys_gat = _DeviceNC('LI-01:EG-Gate', ('status', ))
        self.sys_vac = _DeviceNC('LI-01:EG-Vacuum', ('status', ))
        self.mps_ccg = _DeviceNC(
            'LA-CN:H1MPS-1', ('CCG1Warn_L', 'CCG2Warn_L'))
        self.mps_gun = _DeviceNC('LA-CN:H1MPS-1', ('GunPermit', ))

        devices = (
            self.bias, self.fila, self.hvps, self.trigps, self.pulse,
            self.trigsingle, self.trigmulti, self.trigmultipre,
            self.sys_ext, self.sys_vlv, self.sys_gat, self.sys_vac,
            self.mps_ccg, self.mps_gun)

        self._bias_mb = EGun.BIAS_MULTI_BUNCH
        self._bias_sb = EGun.BIAS_SINGLE_BUNCH
        self._bias_tol = EGun.BIAS_TOLERANCE
        self._hv_opval = EGun.HV_OPVALUE
        self._hv_tol = EGun.HV_TOLERANCE
        self._filacurr_opval = EGun.FILACURR_OPVALUE
        self._filacurr_tol = EGun.FILACURR_TOLERANCE
        self._last_status = ''

        super().__init__('', devices)

    @property
    def multi_bunch_bias_voltage(self):
        """Multi bunch bias voltage to be used in mode setup."""
        return self._bias_mb

    @multi_bunch_bias_voltage.setter
    def multi_bunch_bias_voltage(self, value):
        self._bias_mb = value

    @property
    def single_bunch_bias_voltage(self):
        """Single bunch bias voltage to be used in mode setup."""
        return self._bias_sb

    @single_bunch_bias_voltage.setter
    def single_bunch_bias_voltage(self, value):
        self._bias_sb = value

    @property
    def bias_voltage_tol(self):
        """Bias voltage tolerance."""
        return self._bias_tol

    @bias_voltage_tol.setter
    def bias_voltage_tol(self, value):
        self._bias_tol = value

    def cmd_switch_to_single_bunch(self):
        """Switch to single bunch mode."""
        if not self.connected:
            return False

        if not self.trigps.cmd_disable_trigger():
            return False

        if not self.pulse.cmd_turn_off_multi_bunch():
            return False

        if not self.bias.set_voltage(self._bias_sb, tol=self._bias_tol):
            return False

        if not self.trigmultipre.cmd_disable():
            return False
        if not self.trigmulti.cmd_disable():
            return False
        if not self.trigsingle.cmd_enable():
            return False

        return self.pulse.cmd_turn_on_single_bunch()

    def cmd_switch_to_multi_bunch(self):
        """Switch to multi bunch mode."""
        if not self.connected:
            return False

        if not self.trigps.cmd_disable_trigger():
            return False

        if not self.pulse.cmd_turn_off_single_bunch():
            return False

        if not self.bias.set_voltage(self._bias_mb, tol=self._bias_tol):
            return False

        if not self.trigsingle.cmd_disable():
            return False
        if not self.trigmultipre.cmd_enable():
            return False
        if not self.trigmulti.cmd_enable():
            return False

        return self.pulse.cmd_turn_on_multi_bunch()

    @property
    def is_single_bunch(self):
        """Is configured to single bunch mode."""
        sts = not self.pulse.multi_bunch_switch
        sts &= not self.pulse.multi_bunch_mode
        sts &= not self.trigmultipre.state
        sts &= not self.trigmulti.state
        sts &= self.trigsingle.state
        sts &= self.pulse.single_bunch_mode
        sts &= self.pulse.single_bunch_switch
        return sts

    @property
    def is_multi_bunch(self):
        """Is configured to multi bunch mode."""
        sts = not self.pulse.single_bunch_switch
        sts &= not self.pulse.single_bunch_mode
        sts &= not self.trigsingle.state
        sts &= self.trigmultipre.state
        sts &= self.trigmulti.state
        sts &= self.pulse.multi_bunch_mode
        sts &= self.pulse.multi_bunch_switch
        return sts

    @property
    def last_status(self):
        """Return last status log."""
        return self._last_status

    @property
    def high_voltage_opvalue(self):
        """High voltage operation value."""
        return self._hv_opval

    @high_voltage_opvalue.setter
    def high_voltage_opvalue(self, value):
        self._hv_opval = value

    @property
    def is_hv_on(self):
        """Indicate whether high voltage is on and in operational value."""
        is_on = self.hvps.is_on()
        is_op = abs(self.hvps.voltage - self._hv_opval) < self._hv_tol
        return is_on and is_op

    def set_hv_voltage(self, value=None, nrpts=15, timeout=DEF_TIMEOUT):
        """Set HVPS voltage."""
        if not self._check_status_ok():
            self._update_last_status('ERR:MPS or LI Status not ok. Aborted.')
            return False
        if not self.hvps.is_on():
            self._update_last_status('HVPS voltage is not on.')
            return False
        if value is None:
            value = self._hv_opval

        # if voltage already satisfies value
        cond = abs(self.hvps['voltinsoft'] - value) < self._hv_tol
        cond &= abs(self.hvps['voltoutsoft'] - value) < 1e-4
        if cond:
            self._update_last_status(
                'HVPS Voltage is already at {0:.3f}kV.'.format(value))
            self.hvps.voltage = value
            return True

        # elif value is lower, do only one setpoint
        if value < self.hvps.voltage:
            self.hvps.voltage = value
            return self.hvps.wait_voltage(value, self._hv_tol)

        # else, do a ramp up
        xdata = _np.linspace(self.hvps.voltage/value, 1, nrpts)
        ydata = self._get_ramp(xdata, value, False)

        self._update_last_status(
            'Starting HVPS ramp to {0:.3f} kV.'.format(value))
        self.hvps.voltage = ydata[0]
        for volt in ydata[1:]:
            self.hvps.voltage = volt
            self._update_last_status('HV: {:.3f}kV'.format(volt))
            _t0 = _time.time()
            while _time.time() - _t0 < timeout:
                if not self._check_status_ok():
                    self._update_last_status(
                        'ERR:MPS or LI Status not ok. Aborted.')
                    return False
                if self.hvps.voltage - volt < self._hv_tol and \
                        self.hvps.current < volt * 1e-4:
                    break
                _time.sleep(0.1)
            else:
                if self.hvps.voltage - volt > self._hv_tol:
                    self._update_last_status(
                        'ERR:HVPS Voltage is taking too'
                        ' long to increase. Aborted.')
                else:
                    self._update_last_status(
                        'ERR:HVPS Current is taking too'
                        ' long to decrease. Aborted.')
                return False
        self._update_last_status('HVPS Ready!')
        return True

    @property
    def fila_current_opvalue(self):
        """Filament current operation value."""
        return self._filacurr_opval

    @fila_current_opvalue.setter
    def fila_current_opvalue(self, value):
        self._filacurr_opval = value

    @property
    def is_fila_on(self):
        """Indicate whether filament is on and in operational current."""
        is_on = self.fila.is_on()
        is_op = abs(self.fila.current - self._filacurr_opval) < \
            self._filacurr_tol
        return is_on and is_op

    def set_fila_current(self, value=None, nrpts=10, duration=5*60):
        """Set filament current."""
        if not self.fila.is_on():
            self._update_last_status('FilaPS is not on.')
            return False
        if value is None:
            value = self._filacurr_opval

        # if current already satisfies value
        cond = abs(self.fila['currentinsoft'] - value) < self._filacurr_tol
        cond &= abs(self.fila['currentoutsoft'] - value) < 1e-4
        if cond:
            self._update_last_status(
                'FilaPS current is already at {0:.3f}A.'.format(value))
            self.fila.current = value
            return True

        # elif value is lower, do only one setpoint
        if value < self.fila.current:
            self.fila.current = value
            return self.fila.wait_current(value, self._filacurr_tol)

        # else, do a ramp up
        isfast = value < 0.7
        if isfast:
            duration = 5
            nrpts = 10
        xdata = _np.linspace(0, 1, nrpts)
        ydata = self._get_ramp(xdata, value, isfast)

        t_inter = duration / (nrpts-1)

        strg = 'fast' if isfast else 'slow'
        self._update_last_status(
            'Starting {0:s} filament ramp to {1:.3f}.'.format(strg, value))
        self.fila.current = ydata[0]
        for i, cur in enumerate(ydata[1:]):
            dur = str(_timedelta(seconds=duration - i*t_inter)).split('.')[0]
            self._update_last_status(
                'Remaining Time: {0:s}  Curr: {1:.3f} A'.format(dur, cur))
            _time.sleep(t_inter)
            self.fila.current = cur
        self._update_last_status('FilaPS Ready!')

    def _get_ramp(self, xdata, value, isfast):
        if isfast:
            ydata = xdata.copy()
        else:
            ydata = 1 - (1-xdata)**3
            # ydata = 1 - (1-xdata)**2
            # ydata = _np.sqrt(1 - (1-xdata)**2)
            # ydata = _np.sin(2*np.pi * xdata/4)
        return ydata*value

    def _check_status_ok(self):
        """Check if interlock signals are ok."""
        isok = [self.mps_ccg[ppty] == 0 for ppty in self.mps_ccg.properties]
        allok = all(isok)
        allok &= self.mps_gun['GunPermit'] == 1
        allok &= self.sys_ext['status'] == 1
        allok &= self.sys_vlv['status'] == 1
        allok &= self.sys_gat['status'] == 1
        allok &= self.sys_vac['status'] == 1
        return allok

    def _update_last_status(self, status):
        self._last_status = status
        print(status)
