"""E-Gun devices."""

import time as _time
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

    def cmd_enable(self, timeout=DEF_TIMEOUT):
        """Enable."""
        if self['enstatus'] == self.PWRSTATE.Off:
            self['enable'] = self.PWRSTATE.Off
            _time.sleep(1)

        self['enable'] = self.PWRSTATE.On
        if not self._wait('enstatus', self.PWRSTATE.On, timeout=timeout):
            return False
        return True

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

    def wait_current(self, value, tol=1e-3, timeout=DEF_TIMEOUT):
        """Wait current setpoint to reach value with tolerance 'tol'."""
        _t0 = _time.time()
        while _time.time() - _t0 < timeout:
            if abs(self['currentoutsoft'] - value) < tol:
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
    HV_OPVALUE = 90.0  # [kV]
    HV_TOLERANCE = 1.0  # [kV]
    HV_LEAKCURR_OPVALUE = 0.015  # [mA]
    HV_MAXVALUE = 90.0  # [kV]
    HV_RAMPUP_NRPTS = 15
    HV_RAMPDN_NRPTS = 6
    HV_RAMP_DURATION = 70  # [s]
    FILACURR_OPVALUE = 1.38  # [A]
    FILACURR_TOLERANCE = 0.20  # [A]
    FILACURR_MAXVALUE = 1.42  # [A]
    FILACURR_RAMP_NRPTS = 10
    FILACURR_RAMP_DURATION = 7*60  # [s]

    def __init__(self, print_log=True):
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
        self._hv_leakcurr = EGun.HV_LEAKCURR_OPVALUE
        self._filacurr_opval = EGun.FILACURR_OPVALUE
        self._filacurr_tol = EGun.FILACURR_TOLERANCE
        self._last_status = ''
        self._print_log = print_log

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
        self._update_last_status('Switching EGun mode to SingleBunch...')
        _time.sleep(0.1)  # needed for InjCtrl IOC to get logs

        if not self.connected:
            self._update_last_status('ERR:EGun device not connected. Aborted.')
            return False

        if not self.trigps.cmd_disable_trigger():
            self._update_last_status('ERR:Could not disable EGun Trigger.')
            return False

        if not self.pulse.cmd_turn_off_multi_bunch():
            self._update_last_status('ERR:Could not turn off MultiBunch.')
            return False

        if not self.bias.set_voltage(self._bias_sb, tol=self._bias_tol):
            self._update_last_status(
                'ERR:Could not set EGun Bias voltage to SB operation value.')
            return False

        if not self.trigmultipre.cmd_disable():
            self._update_last_status('ERR:Could not disable MB pre trigger.')
            return False
        if not self.trigmulti.cmd_disable():
            self._update_last_status('ERR: Could not disable MB trigger.')
            return False
        if not self.trigsingle.cmd_enable():
            self._update_last_status('ERR: Could not enable SB trigger.')
            return False

        if not self.pulse.cmd_turn_on_single_bunch():
            self._update_last_status('ERR: Could not turn on SingleBunch.')
            return False
        self._update_last_status('EGun switched to SingleBunch!')
        return True

    def cmd_switch_to_multi_bunch(self):
        """Switch to multi bunch mode."""
        self._update_last_status('Switching EGun mode to MultiBunch...')
        _time.sleep(0.1)  # needed for InjCtrl IOC to get logs

        if not self.connected:
            self._update_last_status('ERR:EGun device not connected. Aborted.')
            return False

        if not self.trigps.cmd_disable_trigger():
            self._update_last_status('ERR:Could not disable EGun Trigger.')
            return False

        if not self.pulse.cmd_turn_off_single_bunch():
            self._update_last_status('ERR:Could not turn off SingleBunch.')
            return False

        if not self.bias.set_voltage(self._bias_mb, tol=self._bias_tol):
            self._update_last_status(
                'ERR:Could not set EGun Bias voltage to MB operation value.')
            return False

        if not self.trigsingle.cmd_disable():
            self._update_last_status('ERR:Could not disable SB trigger.')
            return False
        if not self.trigmultipre.cmd_enable():
            self._update_last_status('ERR: Could not disable SB pre trigger.')
            return False
        if not self.trigmulti.cmd_enable():
            self._update_last_status('ERR: Could not enable MB trigger.')
            return False

        if not self.pulse.cmd_turn_on_multi_bunch():
            self._update_last_status('ERR: Could not turn on MultiBunch.')
            return False
        self._update_last_status('EGun configured to MultiBunch!')
        return True

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
    def high_voltage_leakcurr(self):
        """High voltage leakage current value."""
        return self._hv_leakcurr

    @high_voltage_leakcurr.setter
    def high_voltage_leakcurr(self, value):
        self._hv_leakcurr = value
        self.hvps.current = value

    @property
    def is_hv_on(self):
        """Indicate whether high voltage is on and in operational value."""
        is_on = self.hvps.is_on()
        is_op = abs(self.hvps.voltage - self._hv_opval) < self._hv_tol
        return is_on and is_op

    def set_hv_voltage(self, value=None, duration=None, timeout=DEF_TIMEOUT):
        """Set HVPS voltage."""
        self._update_last_status('Setpoint received for HVPS voltage...')
        if not self._check_status_ok():
            self._update_last_status('ERR:MPS or LI Status not ok. Aborted.')
            return False
        if not self.hvps['swstatus'] == self.hvps.PWRSTATE.On:
            self._update_last_status('ERR:HVPS switch is not on.')
            return False
        if value is None:
            value = self._hv_opval

        # if voltage already satisfies value
        cond = abs(self.hvps['voltinsoft'] - value) < self._hv_tol
        cond &= abs(self.hvps['voltoutsoft'] - value) < 1e-4
        if cond:
            self._update_last_status(
                f'HVPS Voltage is already at {value:.3f}kV.')
            self.hvps.voltage = value
            return True

        # if needed, enable HVPS
        if not self.hvps['enstatus'] == self.hvps.PWRSTATE.On:
            self._update_last_status('Sending enable command to HVPS...')
            _time.sleep(0.1)  # needed for InjCtrl IOC to get logs
            if not self.hvps.cmd_enable(5):
                self._update_last_status('ERR:Could not enable HVPS.')
                return False
            self._update_last_status('HVPS enabled.')
        _time.sleep(0.1)  # needed for InjCtrl IOC to get logs

        # before voltage setpoints, set leakage current to suitable value
        self._update_last_status(
            f'Setting max. leak current to {self._hv_leakcurr:.3f}mA.')
        _time.sleep(0.1)  # needed for InjCtrl IOC to get logs
        self.hvps.current = self._hv_leakcurr
        if not self.hvps.wait_current(self._hv_leakcurr):
            self._update_last_status(
                'ERR:Timed out waiting for HVPS leak current.')
            return False
        _time.sleep(0.1)  # needed for InjCtrl IOC to get logs

        # if value is lower, do a ramp down
        if value < self.hvps.voltage:
            nrpts = EGun.HV_RAMPDN_NRPTS
            power = 1
        else:  # else, do a ramp up
            nrpts = EGun.HV_RAMPUP_NRPTS
            power = 2
        duration = duration if duration is not None else EGun.HV_RAMP_DURATION
        max_value = EGun.HV_MAXVALUE
        ydata = self._get_ramp(
            self.hvps.voltage, value, nrpts, max_value, power)
        t_inter = duration / (nrpts-1)

        self._update_last_status(f'Starting HVPS ramp to {value:.3f}kV.')
        _time.sleep(0.1)  # needed for InjCtrl IOC to get logs
        self._update_last_status(
            f'This process will take about {ydata.size*t_inter:.1f}s.')
        _time.sleep(0.1)  # needed for InjCtrl IOC to get logs
        for i, volt in enumerate(ydata[1:]):
            self.hvps.voltage = volt
            self._update_last_status(
                f'{i+1:02d}/{len(ydata[1:]):02d} -> HV = {volt:.3f}kV')
            _time.sleep(t_inter)
            _t0 = _time.time()
            while _time.time() - _t0 < timeout:
                if not self._check_status_ok():
                    self._update_last_status(
                        'ERR:MPS or LI Status not ok. Aborted.')
                    return False
                if abs(self.hvps.voltage - volt) < self._hv_tol:
                    break
                _time.sleep(0.1)
            else:
                self._update_last_status(
                    'ERR:HVPS Voltage is taking too'
                    ' long to reach setpoint. Aborted.')
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
        is_op_sp = abs(self.fila['currentoutsoft']-self._filacurr_opval) < 1e-4
        is_op_rb = abs(self.fila['currentinsoft']-self._filacurr_opval) < \
            self._filacurr_tol
        return is_on and is_op_sp and is_op_rb

    def set_fila_current(self, value=None):
        """Set filament current."""
        self._update_last_status('Setpoint received for FilaPS current...')
        if not self._check_status_ok():
            self._update_last_status('ERR:MPS or LI Status not ok. Aborted.')
            return False
        if not self.fila.is_on():
            self._update_last_status('ERR:FilaPS is not on.')
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
            self._update_last_status(f'Setting current to {value:.3f}A...')
            self.fila.current = value
            if self.fila.wait_current(value, self._filacurr_tol):
                self._update_last_status('FilaPS Ready!')
                return True
            self._update_last_status(
                'ERR:Timed out waiting for FilaPS current.')
            return False

        # else, do a ramp up
        duration = EGun.FILACURR_RAMP_DURATION
        nrpts = EGun.FILACURR_RAMP_NRPTS
        max_value = EGun.FILACURR_MAXVALUE
        ydata = self._get_ramp(self.fila.current, value, nrpts, max_value)
        t_inter = duration / (nrpts-1)
        total_steps_duration = (len(ydata)-1)*t_inter

        self._update_last_status(
            f'Starting filament ramp to {value:.3f} A.')
        _time.sleep(0.1)  # needed for InjCtrl IOC to get logs
        for i, cur in enumerate(ydata[1:]):
            self.fila.current = cur
            dur = total_steps_duration - i*t_inter
            self._update_last_status(
                f'{i+1:02d}/{len(ydata[1:]):02d} -> '
                f'Rem. Time: {dur:03.0f}s  Curr: {cur:.3f} A')
            _time.sleep(t_inter)

            if not self._check_status_ok():
                self._update_last_status(
                    'ERR:MPS or LI Status not ok. Aborted.')
                return False
        self._update_last_status('FilaPS Ready!')
        return True

    def _get_ramp(self, curr_val, goal, nrpts, max_val, power=2):
        xdata = _np.linspace(0, 1, nrpts)
        if curr_val > goal:
            xdata = _np.flip(xdata)

        ydata = 1 - (1-xdata)**power
        # ydata = _np.sqrt(1 - (1-xdata)**2)
        # ydata = _np.sin(2*np.pi * xdata/4)

        ydata *= max_val
        mini = min(curr_val, goal)
        maxi = max(curr_val, goal)
        ydata = ydata[ydata > mini]
        ydata = ydata[ydata < maxi]
        ydata = _np.r_[curr_val, ydata, goal]
        return ydata

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
        if self._print_log:
            print(status)
