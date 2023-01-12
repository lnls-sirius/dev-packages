"""Injection control IOC device."""

from .device import Device as _Device

from ..clientarch import Time
from ..injctrl.csdev import Const as _Const


class InjCtrl(_Device):
    """Injection Control IOC device."""

    OffOn = _Const.OffOn
    InjMode = _Const.InjMode
    InjType = _Const.InjType
    InjTypeMon = _Const.InjTypeMon
    PUMode = _Const.PUMode
    PUModeMon = _Const.PUModeMon
    TopUpSts = _Const.TopUpSts

    _properties = (
        'Mode-Sel', 'Mode-Sts',
        'Type-Sel', 'Type-Sts', 'Type-Mon', 'TypeCmdSts-Mon',
        'SglBunBiasVolt-SP', 'SglBunBiasVolt-RB',
        'MultBunBiasVolt-SP', 'MultBunBiasVolt-RB',
        'BiasVoltCmdSts-Mon',
        'FilaOpCurr-SP', 'FilaOpCurr-RB', 'FilaOpCurrCmdSts-Mon',
        'HVOpVolt-SP', 'HVOpVolt-RB', 'HVOpVoltCmdSts-Mon',
        'PUMode-Sel', 'PUMode-Sts', 'PUMode-Mon', 'PUModeCmdSts-Mon',
        'TargetCurrent-SP', 'TargetCurrent-RB',
        'BucketListStart-SP', 'BucketListStart-RB',
        'BucketListStop-SP', 'BucketListStop-RB',
        'BucketListStep-SP', 'BucketListStep-RB',
        'TopUpState-Sel', 'TopUpState-Sts',
        'TopUpPeriod-SP', 'TopUpPeriod-RB',
        'TopUpHeadStartTime-SP', 'TopUpHeadStartTime-RB',
        'TopUpNextInj-Mon',
        'TopUpNrPulses-SP', 'TopUpNrPulses-RB',
        'InjSysTurnOn-Cmd', 'InjSysTurnOff-Cmd', 'InjSysCmdSts-Mon',
        'InjSysTurnOnOrder-SP', 'InjSysTurnOnOrder-RB',
        'InjSysTurnOffOrder-SP', 'InjSysTurnOffOrder-RB',
        'RFKillBeam-Cmd', 'RFKillBeam-Mon',
        'DiagStatus-Mon', 'InjStatus-Mon',
    )

    class DEVICES:
        """Devices names."""

        AS = 'AS-Glob:AP-InjCtrl'
        ALL = (AS, )

    def __init__(self, devname=None):
        """Init."""
        if devname is None:
            devname = InjCtrl.DEVICES.AS
        if devname not in InjCtrl.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=InjCtrl._properties)

    # ----- general injection properties -----

    @property
    def injmode(self):
        """Injection mode (Decay or TopUp)."""
        return self['Mode-Sts']

    @injmode.setter
    def injmode(self, value):
        self._enum_setter('Mode-Sel', value, self.InjMode)

    @property
    def injmode_str(self):
        """Injection mode string (Decay or TopUp)."""
        return self.InjMode._fields[self['Mode-Sts']]

    @property
    def injtype(self):
        """Injection type (SingleBunch or MultiBunch)."""
        return self['Type-Sts']

    @injtype.setter
    def injtype(self, value):
        self._enum_setter('Type-Sel', value, self.InjType)

    @property
    def injtype_str(self):
        """Injection type string (SingleBunch or MultiBunch)."""
        return self.InjType._fields[self['Type-Sts']]

    @property
    def injtype_mon(self):
        """Injection type (SingleBunch, MultiBunch or Undefined)."""
        return self['Type-Mon']

    @property
    def injtype_cmdsts(self):
        """Injection type command status (Idle or Running)."""
        return self['TypeCmdSts-Mon']

    @property
    def bias_volt_sglbun(self):
        """Bias voltage for single bunch injection type."""
        return self['SglBunBiasVolt-RB']

    @bias_volt_sglbun.setter
    def bias_volt_sglbun(self, value):
        self['SglBunBiasVolt-SP'] = value

    @property
    def bias_volt_multbun(self):
        """Bias voltage for multi bunch injection type."""
        return self['MultBunBiasVolt-RB']

    @bias_volt_multbun.setter
    def bias_volt_multbun(self, value):
        self['MultBunBiasVolt-SP'] = value

    @property
    def bias_volt_cmdsts(self):
        """Bias voltage command status (Idle or Running)."""
        return self['BiasVoltCmdSts-Mon']

    @property
    def filacurr_opvalue(self):
        """EGun filament operation current value."""
        return self['FilaOpCurr-RB']

    @filacurr_opvalue.setter
    def filacurr_opvalue(self, value):
        self['FilaOpCurr-SP'] = value

    @property
    def filacurr_cmdsts(self):
        """EGun filament current setpoint command status (Idle or Running)."""
        return self['FilaOpCurrCmdSts-Mon']

    @property
    def hvolt_opvalue(self):
        """EGun high voltage operation value."""
        return self['HVOpVolt-RB']

    @hvolt_opvalue.setter
    def hvolt_opvalue(self, value):
        self['HVOpVolt-SP'] = value

    @property
    def hvolt_cmdsts(self):
        """EGun high voltage setpoint command status (Idle or Running)."""
        return self['HVOpVoltCmdSts-Mon']

    @property
    def pumode(self):
        """PU mode (Accumulation, Optimization or OnAxis)."""
        return self['PUMode-Sts']

    @pumode.setter
    def pumode(self, value):
        self._enum_setter('PUMode-Sel', value, self.PUMode)

    @property
    def pumode_str(self):
        """PU mode string (Accumulation, Optimization or OnAxis)."""
        return self.PUMode._fields[self['PUMode-Sts']]

    @property
    def pumode_mon(self):
        """PU mode (Accumulation, Optimization, OnAxis or Undefined)."""
        return self['PUMode-Mon']

    @property
    def pumode_cmdsts(self):
        """PU mode command status (Idle or Running)."""
        return self['PUModeCmdSts-Mon']

    @property
    def target_current(self):
        """Target current value."""
        return self['TargetCurrent-RB']

    @target_current.setter
    def target_current(self, value):
        self['TargetCurrent-SP'] = value

    @property
    def bucketlist_start(self):
        """Bucket list start value."""
        return self['BucketListStart-RB']

    @bucketlist_start.setter
    def bucketlist_start(self, value):
        self['BucketListStart-SP'] = value

    @property
    def bucketlist_step(self):
        """Bucket list step value."""
        return self['BucketListStep-RB']

    @bucketlist_step.setter
    def bucketlist_step(self, value):
        self['BucketListStep-SP'] = value

    @property
    def bucketlist_stop(self):
        """Bucket list stop value."""
        return self['BucketListStop-RB']

    @bucketlist_stop.setter
    def bucketlist_stop(self, value):
        self['BucketListStop-SP'] = value

    # ----- injection mode properties -----

    @property
    def topup_state(self):
        """Top-up state (Off, Waiting, TurningOn, Injecting or TurningOff)."""
        return self['TopUpState-Sts']

    @topup_state.setter
    def topup_state(self, value):
        self._enum_setter('TopUpState-Sel', value, self.OffOn)

    @property
    def topup_state_str(self):
        """Top-up state (Off, Waiting, TurningOn, Injecting or TurningOff)."""
        return self.TopUpSts._fields[self['TopUpState-Sts']]

    @property
    def topup_period(self):
        """Top-up period [min]."""
        return self['TopUpPeriod-RB']

    @topup_period.setter
    def topup_period(self, value):
        self['TopUpPeriod-SP'] = value

    @property
    def topup_headstarttime(self):
        """Top-up head start time [s]."""
        return self['TopUpHeadStartTime-RB']

    @topup_headstarttime.setter
    def topup_headstarttime(self, value):
        self['TopUpHeadStartTime-SP'] = value

    @property
    def topup_nrpulses(self):
        """Top-up number of pulses [s]."""
        return self['TopUpNrPulses-RB']

    @topup_nrpulses.setter
    def topup_nrpulses(self, value):
        self['TopUpNrPulses-SP'] = value

    @property
    def topup_nextinj_timestamp(self):
        """Next topup scheduled injection [s]."""
        return self['TopUpNextInj-Mon']

    @property
    def topup_nextinj_time(self):
        """Next topup scheduled injection Time object."""
        return Time.fromtimestamp(self['TopUpNextInj-Mon'])

    # ----- injection system properties -----

    def cmd_injsys_turn_on(self):
        """Injection system turn on command."""
        self['InjSysTurnOn-Cmd'] = 1

    @property
    def injsys_turn_on_order(self):
        """Injection system turn on command order.

        Return
        ------
        str
            A string of a list with the reference of the handlers,
            in the order that they are executed in turn on command.
            Default value: 'bo_rf,as_pu,bo_ps,injbo,li_rf'.
        """
        return self['InjSysTurnOnOrder-RB']

    @injsys_turn_on_order.setter
    def injsys_turn_on_order(self, value):
        self['InjSysTurnOnOrder-SP'] = value

    def cmd_injsys_turn_off(self):
        """Injection system turn off command."""
        self['InjSysTurnOff-Cmd'] = 1

    @property
    def injsys_turn_off_order(self):
        """Injection system turn on command order.

        Return
        ------
        str
            A string of a list with the reference of the handlers,
            in the order that they are executed in turn off command.
            Default value: 'bo_rf,li_rf,injbo,as_pu,bo_ps'.
        """
        return self['InjSysTurnOffOrder-RB']

    @injsys_turn_off_order.setter
    def injsys_turn_off_order(self, value):
        self['InjSysTurnOffOrder-SP'] = value

    @property
    def injsys_cmdsts(self):
        """Injection system command status (Idle or Running)."""
        return self['InjSysCmdSts-Mon']

    # ----- kill beam properties -----

    def cmd_rfkillbeam(self):
        """RF Kill Beam command."""
        self['RFKillBeam-Cmd'] = 1

    @property
    def rfkillbeam_cmdsts(self):
        """Kill beam command status (Idle or Kill)."""
        return self['RFKillBeam-Mon']

    # ----- diagnostics properties -----

    @property
    def diag_status(self):
        """Diagnostics status."""
        return self['DiagStatus-Mon']

    @property
    def inj_status(self):
        """Injection status."""
        return self['InjStatus-Mon']
