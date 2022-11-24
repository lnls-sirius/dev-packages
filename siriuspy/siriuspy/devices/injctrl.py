"""Injection control IOC device."""

from .device import Device as _Device

from ..clientarch import Time


class InjCtrl(_Device):
    """Injection Control IOC device."""

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
        'TopUpNextInj-Mon',
        'TopUpNrPulses-SP', 'TopUpNrPulses-RB',
        'AutoStop-Sel', 'AutoStop-Sts',
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

    @property
    def injmode(self):
        """Injection mode (Decay or TopUp)."""
        return self['Mode-Sts']

    @injmode.setter
    def injmode(self, value):
        self['Mode-Sel'] = value

    @property
    def injtype(self):
        """Injection mode (SingleBunch or MultiBunch)."""
        return self['Type-Sts']

    @injtype.setter
    def injtype(self, value):
        self['Type-Sel'] = value

    @property
    def injtype_mon(self):
        """Injection mode (SingleBunch, MultiBunch or Undefined)."""
        return self['Type-Mon']

    @property
    def pumode(self):
        """PU mode (Accumulation, Optimization or OnAxis)."""
        return self['PUMode-Sts']

    @pumode.setter
    def pumode(self, value):
        self['PUMode-Sel'] = value

    @property
    def pumode_mon(self):
        """PU mode (Accumulation, Optimization, OnAxis or Undefined)."""
        return self['PUMode-Mon']

    @property
    def topup_nextinj_timestamp(self):
        """Next topup scheduled injection [s]."""
        return self['TopUpNextInj-Mon']

    @property
    def topup_nextinj_time(self):
        """Next topup scheduled injection Time object."""
        return Time.fromtimestamp(self['TopUpNextInj-Mon'])
