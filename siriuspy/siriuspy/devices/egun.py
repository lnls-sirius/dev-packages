"""E-Gun devices."""

import time as _time
from threading import Event as _Flag
from functools import partial as _part

import numpy as _np

from ..pwrsupply.psctrl.pscstatus import PSCStatus as _PSCStatus
from ..injctrl.csdev import Const as _InjConst
from ..callbacks import Callback as _Callback

from .device import Device as _Device, DeviceSet as _DeviceSet
from .timing import Trigger


class EGBias(_Device):
    """EGun Bias Device."""

    DEF_TIMEOUT = 10  # [s]
    PWRSTATE = _PSCStatus.PWRSTATE

    class DEVICES:
        """Devices names."""

        LI = 'LI-01:EG-BiasPS'
        ALL = (LI, )

    PROPERTIES_DEFAULT = (
        'voltoutsoft', 'voltinsoft', 'currentinsoft', 'switch', 'swstatus')

    def __init__(self, devname=None, props2init='all'):
        """."""
        if devname is None:
            devname = EGBias.DEVICES.LI

        # check if device exists
        if devname not in EGBias.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def voltage_mon(self):
        """."""
        return self['voltinsoft']

    @property
    def voltage(self):
        """."""
        return self['voltoutsoft']

    @voltage.setter
    def voltage(self, value):
        self['voltoutsoft'] = value

    @property
    def current_mon(self):
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
            if abs(self.voltage_mon - value) < tol:
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

    PROPERTIES_DEFAULT = (
        'voltinsoft', 'currentinsoft', 'currentoutsoft', 'switch', 'swstatus')

    def __init__(self, devname=None, props2init='all'):
        """."""
        if devname is None:
            devname = EGFilament.DEVICES.LI

        # check if device exists
        if devname not in EGFilament.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def voltage_mon(self):
        """."""
        return self['voltinsoft']

    @property
    def current_mon(self):
        """."""
        return self['currentinsoft']

    @property
    def current(self):
        """."""
        return self['currentoutsoft']

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
            if abs(self.current_mon - value) < tol:
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

    PROPERTIES_DEFAULT = (
        'currentinsoft', 'currentoutsoft',
        'voltinsoft', 'voltoutsoft',
        'enable', 'enstatus',
        'switch', 'swstatus')

    def __init__(self, devname=None, props2init='all'):
        """."""
        if devname is None:
            devname = EGHVPS.DEVICES.LI

        # check if device exists
        if devname not in EGHVPS.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def current_mon(self):
        """."""
        return self['currentinsoft']

    @property
    def current(self):
        """."""
        return self['currentoutsoft']

    @current.setter
    def current(self, value):
        """."""
        self['currentoutsoft'] = value

    @property
    def voltage_mon(self):
        """."""
        return self['voltinsoft']

    @property
    def voltage(self):
        """."""
        return self['voltoutsoft']

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
            if abs(self.voltage_mon - value) < tol:
                return True
            _time.sleep(0.1)
        return False

    def wait_current(self, value, tol=1e-3, timeout=DEF_TIMEOUT):
        """Wait current setpoint to reach value with tolerance 'tol'."""
        _t0 = _time.time()
        while _time.time() - _t0 < timeout:
            if abs(self.current - value) < tol:
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

    PROPERTIES_DEFAULT = (
        'status', 'allow', 'enable', 'enablereal')

    def __init__(self, devname=DEVICES.LI, props2init='all'):
        """."""
        # check if device exists
        if devname not in EGTriggerPS.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

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

    PROPERTIES_DEFAULT = (
        'singleselect', 'singleselstatus', 'singleswitch', 'singleswstatus',
        'multiselect', 'multiselstatus', 'multiswitch', 'multiswstatus',
        'poweroutsoft', 'powerinsoft')

    def __init__(self, devname=DEVICES.LI, props2init='all'):
        """Init."""
        # check if device exists
        if devname not in EGPulsePS.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

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
    def power_mon(self):
        """Power monitor."""
        return self['powerinsoft']

    @property
    def power(self):
        """Power readback."""
        return self['poweroutsoft']

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


class EGun(_DeviceSet, _Callback):
    """EGun device."""

    DEF_TIMEOUT = 10  # [s]
    BIAS_MULTI_BUNCH = _InjConst.BIAS_MULTI_BUNCH
    BIAS_SINGLE_BUNCH = _InjConst.BIAS_SINGLE_BUNCH
    BIAS_TOLERANCE = 1.0  # [V]
    HV_OPVALUE = _InjConst.HV_OPVALUE
    HV_TOLERANCE = 1.0  # [kV]
    HV_LEAKCURR_OPVALUE = 0.015  # [mA]
    HV_MAXVALUE = 90.0  # [kV]
    HV_RAMPUP_NRPTS = 15
    HV_RAMPDN_NRPTS = 6
    HV_RAMP_DURATION = 70  # [s]
    FILACURR_OPVALUE = _InjConst.FILACURR_OPVALUE
    FILACURR_TOLERANCE = 0.20  # [A]
    FILACURR_MAXVALUE = 1.42  # [A]
    FILACURR_RAMP_NRPTS = 10
    FILACURR_RAMP_DURATION = 7*60  # [s]

    def __init__(self, print_log=True, callback=None):
        """Init."""
        self.bias = EGBias()
        self.fila = EGFilament()
        self.hvps = EGHVPS()
        self.trigps = EGTriggerPS()
        self.pulse = EGPulsePS()
        self.trigsingle = Trigger('LI-01:TI-EGun-SglBun')
        self.trigmulti = Trigger('LI-01:TI-EGun-MultBun')
        self.trigmultipre = Trigger('LI-01:TI-EGun-MultBunPre')

        self.sys_ext = _Device('LI-01:EG-External', props2init=('status', ))
        self.sys_vlv = _Device('LI-01:EG-Valve', props2init=('status', ))
        self.sys_gat = _Device('LI-01:EG-Gate', props2init=('status', ))
        self.sys_vac = _Device('LI-01:EG-Vacuum', props2init=('status', ))
        self.mps_ccg = _Device(
            'LA-CN:H1MPS-1', props2init=('CCG1Warn_L', 'CCG2Warn_L'))
        self.mps_gun = _Device('LA-CN:H1MPS-1', props2init=('GunPermit', ))

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
        self._print_log = print_log
        self._abort_chg_type = _Flag()
        self._abort_rmp_hvps = _Flag()
        self._abort_rmp_fila = _Flag()

        _DeviceSet.__init__(self, devices)
        _Callback.__init__(self, callback=callback)

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
        self._abort_chg_type.clear()
        self._update_status('Switching EGun mode to SingleBunch...')

        if not self.wait_for_connection(1):
            self._update_status('ERR:EGun device not connected. Aborted.')
            return False

        # fun, msg
        proced = (
            (_part(self.trigps.cmd_disable_trigger), 'disable EGun Trigger.'),
            (_part(self.pulse.cmd_turn_off_multi_bunch),
             'turn off MultiBunch.'),
            (_part(
                self.bias.set_voltage, self._bias_sb, tol=self._bias_tol),
             'set EGun Bias voltage to SB operation value.'),
            (_part(self.trigmultipre.cmd_disable), 'disable MB pre trigger.'),
            (_part(self.trigmulti.cmd_disable), 'disable MB trigger.'),
            (_part(self.trigsingle.cmd_enable), 'enable SB trigger.'),
            (_part(self.pulse.cmd_turn_on_single_bunch),
             'turn on SingleBunch.'),
            )

        for fun, msg in proced:
            if self._abort_chg_type.is_set():
                self._clr_flag_abort_chg_type()
                return False
            if not fun():
                self._update_status('ERR:Could not ' + msg)
                return False
        self._update_status('EGun switched to SingleBunch!')
        return True

    def cmd_switch_to_multi_bunch(self):
        """Switch to multi bunch mode."""
        self._abort_chg_type.clear()
        self._update_status('Switching EGun mode to MultiBunch...')

        if not self.wait_for_connection(1):
            self._update_status('ERR:EGun device not connected. Aborted.')
            return False

        # fun, msg
        proced = (
            (_part(self.trigps.cmd_disable_trigger), 'disable EGun Trigger.'),
            (_part(self.pulse.cmd_turn_off_single_bunch),
             'turn off SingleBunch.'),
            (_part(self.bias.set_voltage, self._bias_mb, tol=self._bias_tol),
             'set EGun Bias voltage to MB operation value.'),
            (_part(self.trigsingle.cmd_disable), 'disable SB trigger.'),
            (_part(self.trigmultipre.cmd_enable), 'disable SB pre trigger.'),
            (_part(self.trigmulti.cmd_enable), 'enable MB trigger.'),
            (_part(self.pulse.cmd_turn_on_multi_bunch), 'turn on MultiBunch.'),
        )

        for fun, msg in proced:
            if self._abort_chg_type.is_set():
                self._clr_flag_abort_chg_type()
                return False
            if not fun():
                self._update_status('ERR:Could not ' + msg)
                return False
        self._update_status('EGun configured to MultiBunch!')
        return True

    @property
    def is_single_bunch(self):
        """Is configured to single bunch mode."""
        if not self.wait_for_connection(1):
            return False
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
        if not self.wait_for_connection(1):
            return False
        sts = not self.pulse.single_bunch_switch
        sts &= not self.pulse.single_bunch_mode
        sts &= not self.trigsingle.state
        sts &= self.trigmultipre.state
        sts &= self.trigmulti.state
        sts &= self.pulse.multi_bunch_mode
        sts &= self.pulse.multi_bunch_switch
        return sts

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
        if not self.hvps.wait_for_connection(1):
            return False
        is_on = self.hvps.is_on()
        is_op = abs(self.hvps.voltage_mon - self._hv_opval) < self._hv_tol
        return is_on and is_op

    def set_hv_voltage(self, value=None, duration=None, timeout=DEF_TIMEOUT):
        """Set HVPS voltage."""
        self._abort_rmp_hvps.clear()
        self._update_status('Setpoint received for HVPS voltage...')
        if not self._check_status_ok():
            self._update_status('ERR:MPS or LI Status not ok. Aborted.')
            return False
        if not self.hvps['swstatus'] == self.hvps.PWRSTATE.On:
            self._update_status('ERR:HVPS switch is not on.')
            return False
        if self._abort_rmp_hvps.is_set():
            self._clr_flag_abort_rmp_hvps()
            return False
        if value is None:
            value = self._hv_opval

        # if voltage already satisfies value
        cond = abs(self.hvps['voltinsoft'] - value) < self._hv_tol
        cond &= abs(self.hvps['voltoutsoft'] - value) < 1e-4
        if cond:
            self._update_status(
                f'HVPS Voltage is already at {value:.3f}kV.')
            self.hvps.voltage = value
            return True

        if self._abort_rmp_hvps.is_set():
            self._clr_flag_abort_rmp_hvps()
            return False

        # if needed, enable HVPS
        if not self.hvps['enstatus'] == self.hvps.PWRSTATE.On:
            self._update_status('Sending enable command to HVPS...')
            if not self.hvps.cmd_enable(5):
                self._update_status('ERR:Could not enable HVPS.')
                return False
            self._update_status('HVPS enabled.')

        if self._abort_rmp_hvps.is_set():
            self._clr_flag_abort_rmp_hvps()
            return False

        # before voltage setpoints, set leakage current to suitable value
        self._update_status(
            f'Setting max. leak current to {self._hv_leakcurr:.3f}mA.')
        self.hvps.current = self._hv_leakcurr
        if not self.hvps.wait_current(self._hv_leakcurr):
            self._update_status(
                'ERR:Timed out waiting for HVPS leak current.')
            return False

        if self._abort_rmp_hvps.is_set():
            self._clr_flag_abort_rmp_hvps()
            return False

        # if value is lower, do a ramp down
        if value < self.hvps.voltage_mon:
            nrpts = EGun.HV_RAMPDN_NRPTS
            power = 1
        else:  # else, do a ramp up
            nrpts = EGun.HV_RAMPUP_NRPTS
            power = 2
        duration = duration if duration is not None else EGun.HV_RAMP_DURATION
        max_value = EGun.HV_MAXVALUE
        ydata = self._get_ramp(
            self.hvps.voltage_mon, value, nrpts, max_value, power)
        t_inter = duration / (nrpts-1)

        self._update_status(f'Starting HVPS ramp to {value:.3f}kV.')
        self._update_status(
            f'This process will take about {ydata.size*t_inter:.1f}s.')
        for i, volt in enumerate(ydata[1:]):
            if self._abort_rmp_hvps.is_set():
                self._clr_flag_abort_rmp_hvps()
                return False
            self.hvps.voltage = volt
            self._update_status(
                f'{i+1:02d}/{len(ydata[1:]):02d} -> HV = {volt:.3f}kV')
            _time.sleep(t_inter)
            _t0 = _time.time()
            while _time.time() - _t0 < timeout:
                if self._abort_rmp_hvps.is_set():
                    self._clr_flag_abort_rmp_hvps()
                    return False
                if not self._check_status_ok():
                    self._update_status(
                        'ERR:MPS or LI Status not ok. Aborted.')
                    return False
                if abs(self.hvps.voltage_mon - volt) < self._hv_tol:
                    break
                _time.sleep(0.1)
            else:
                self._update_status(
                    'ERR:HVPS Voltage is taking too '
                    'long to reach setpoint. Aborted.')
                return False
        self._update_status('HVPS Ready!')
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
        if not self.fila.wait_for_connection(1):
            return False
        is_on = self.fila.is_on()
        is_op_sp = abs(self.fila['currentoutsoft']-self._filacurr_opval) < 1e-4
        is_op_rb = abs(self.fila['currentinsoft']-self._filacurr_opval) < \
            self._filacurr_tol
        return is_on and is_op_sp and is_op_rb

    def set_fila_current(self, value=None):
        """Set filament current."""
        self._abort_rmp_fila.clear()
        self._update_status('Setpoint received for FilaPS current...')
        if not self._check_status_ok():
            self._update_status('ERR:MPS or LI Status not ok. Aborted.')
            return False
        if not self.fila.is_on():
            self._update_status('ERR:FilaPS is not on.')
            return False
        if self._abort_rmp_fila.is_set():
            self._clr_flag_abort_rmp_fila()
            return False
        if value is None:
            value = self._filacurr_opval

        # if current already satisfies value
        cond = abs(self.fila['currentinsoft'] - value) < self._filacurr_tol
        cond &= abs(self.fila['currentoutsoft'] - value) < 1e-4
        if cond:
            self._update_status(
                'FilaPS current is already at {0:.3f}A.'.format(value))
            self.fila.current = value
            return True

        if self._abort_rmp_fila.is_set():
            self._clr_flag_abort_rmp_fila()
            return False

        # elif value is lower, do only one setpoint
        if value < self.fila.current_mon:
            self._update_status(f'Setting current to {value:.3f}A...')
            self.fila.current = value
            if self.fila.wait_current(value, self._filacurr_tol):
                self._update_status('FilaPS Ready!')
                return True
            self._update_status(
                'ERR:Timed out waiting for FilaPS current.')
            return False

        if self._abort_rmp_fila.is_set():
            self._clr_flag_abort_rmp_fila()
            return False

        # else, do a ramp up
        duration = EGun.FILACURR_RAMP_DURATION
        nrpts = EGun.FILACURR_RAMP_NRPTS
        max_value = EGun.FILACURR_MAXVALUE
        ydata = self._get_ramp(self.fila.current_mon, value, nrpts, max_value)
        t_inter = duration / (nrpts-1)
        total_steps_duration = (len(ydata)-1)*t_inter

        self._update_status(
            f'Starting filament ramp to {value:.3f} A.')
        for i, cur in enumerate(ydata[1:]):
            if self._abort_rmp_fila.is_set():
                self._clr_flag_abort_rmp_fila()
                return False
            self.fila.current = cur
            dur = total_steps_duration - i*t_inter
            self._update_status(
                f'{i+1:02d}/{len(ydata[1:]):02d} -> '
                f'Rem. Time: {dur:03.0f}s  Curr: {cur:.3f} A')
            _time.sleep(t_inter)

            if not self._check_status_ok():
                self._update_status(
                    'ERR:MPS or LI Status not ok. Aborted.')
                return False
        self._update_status('FilaPS Ready!')
        return True

    # -------- thread help methods --------

    def cmd_abort_chg_type(self):
        """Abort injection type change."""
        self._abort_chg_type.set()
        self._update_status('WARN:Abort received for Type change.')
        return True

    def _clr_flag_abort_chg_type(self):
        """Clear abort flag for injection type change."""
        self._abort_chg_type.clear()
        self._update_status('ERR:Aborted Type change.')
        return True

    def cmd_abort_rmp_hvps(self):
        """Abort set HVPS voltage ramp."""
        self._abort_rmp_hvps.set()
        self._update_status('WARN:Abort received for HVPS ramp.')
        return True

    def _clr_flag_abort_rmp_hvps(self):
        """Clear abort flag for HVPS voltage ramp."""
        self._abort_rmp_hvps.clear()
        self._update_status('ERR:Aborted HVPS voltage ramp.')
        return True

    def cmd_abort_rmp_fila(self):
        """Abort FilaPS current ramp."""
        self._abort_rmp_fila.set()
        self._update_status('WARN:Abort received for FilaPS ramp.')
        return True

    def _clr_flag_abort_rmp_fila(self):
        """Clear abort flag for FilaPS current ramp."""
        self._abort_rmp_fila.clear()
        self._update_status('ERR:Aborted FilaPS current ramp.')
        return True

    # ---------- private methods ----------

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
        if not self.wait_for_connection(1):
            return False
        isok = [
            self.mps_ccg[ppty] == 0
            for ppty in self.mps_ccg.properties_in_use]
        allok = all(isok)
        allok &= self.mps_gun['GunPermit'] == 1
        allok &= self.sys_ext['status'] == 1
        allok &= self.sys_vlv['status'] == 1
        allok &= self.sys_gat['status'] == 1
        allok &= self.sys_vac['status'] == 1
        return allok

    # ---------- logging -----------

    def _update_status(self, status):
        if self._print_log:
            print(status)
        self.run_callbacks(status)
