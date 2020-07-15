"""."""
from .device import Device as _Device
from .device import Devices as _Devices


class CurrInfoLinear(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        LI = 'LI-Glob:AP-CurrInfo'
        TB = 'TB-Glob:AP-CurrInfo'
        TS = 'TS-Glob:AP-CurrInfo'
        ALL = (LI, TB, TS, )

    _properties = ('TranspEff-Mon', )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in CurrInfoLinear.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=CurrInfoLinear._properties)

    @property
    def transpeff(self):
        """."""
        return self['TranspEff-Mon']


class CurrInfoBO(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        BO = 'BO-Glob:AP-CurrInfo'
        ALL = (BO, )

    _properties = (
        'Charge150MeV-Mon', 'Current150MeV-Mon',
        'Charge1GeV-Mon', 'Current1GeV-Mon',
        'Charge2GeV-Mon', 'Current2GeV-Mon',
        'Charge3GeV-Mon', 'Current3GeV-Mon',
        'IntCurrent3GeV-Mon', 'RampEff-Mon',
    )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in CurrInfoBO.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=CurrInfoBO._properties)

    @property
    def charge150mev(self):
        """."""
        return self['Charge150MeV-Mon']

    @property
    def current150mev(self):
        """."""
        return self['Current150MeV-Mon']

    @property
    def charge1gev(self):
        """."""
        return self['Charge1GeV-Mon']

    @property
    def current1gev(self):
        """."""
        return self['Current1GeV-Mon']

    @property
    def charge2gev(self):
        """."""
        return self['Charge2GeV-Mon']

    @property
    def current2gev(self):
        """."""
        return self['Current2GeV-Mon']

    @property
    def charge3gev(self):
        """."""
        return self['Charge3GeV-Mon']

    @property
    def current3gev(self):
        """."""
        return self['Current3GeV-Mon']

    @property
    def intcurrent3gev(self):
        """."""
        return self['IntCurrent3GeV-Mon']

    @property
    def rampeff(self):
        """."""
        return self['RampEff-Mon']


class CurrInfoSI(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        SI = 'SI-Glob:AP-CurrInfo'
        ALL = (SI, )

    _properties = (
        'Charge-Mon', 'Current-Mon',
        'InjEff-Mon', 'Lifetime-Mon', 'LifetimeBPM-Mon',
        'StoredEBeam-Mon',
    )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in CurrInfoSI.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=CurrInfoSI._properties)

    @property
    def charge(self):
        """."""
        return self['Charge-Mon']

    @property
    def current(self):
        """."""
        return self['Current-Mon']

    @property
    def injeff(self):
        """."""
        return self['InjEff-Mon']

    @property
    def lifetime(self):
        """."""
        return self['Lifetime-Mon']

    @property
    def lifetimebpm(self):
        """."""
        return self['LifetimeBPM-Mon']

    @property
    def storedbeam(self):
        """."""
        return self['StoredEBeam-Mon']


class CurrInfo(_Devices):
    """."""

    class DEVICES:
        """Devices names."""

        LI = CurrInfoLinear.DEVICES.LI
        TB = CurrInfoLinear.DEVICES.TB
        BO = CurrInfoBO.DEVICES.BO
        TS = CurrInfoLinear.DEVICES.TS
        SI = CurrInfoSI.DEVICES.SI
        ALL = (LI, TB, BO, TS, SI, )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in CurrInfo.DEVICES.ALL:
            raise NotImplementedError(devname)

        currinfo_li = CurrInfoLinear(CurrInfo.DEVICES.LI)
        currinfo_tb = CurrInfoLinear(CurrInfo.DEVICES.TB)
        currinfo_bo = CurrInfoBO(CurrInfo.DEVICES.BO)
        currinfo_ts = CurrInfoLinear(CurrInfo.DEVICES.TS)
        currinfo_si = CurrInfoSI(CurrInfo.DEVICES.SI)

        devices = (
            currinfo_li, currinfo_tb, currinfo_bo,
            currinfo_ts, currinfo_si
        )

        # call base class constructor
        super().__init__(devname, devices)

    @property
    def li(self):
        """Return LI CurrInfo device."""
        return self.devices[0]

    @property
    def tb(self):
        """Return TB CurrInfo device."""
        return self.devices[1]

    @property
    def bo(self):
        """Return BO CurrInfo device."""
        return self.devices[2]

    @property
    def ts(self):
        """Return TS CurrInfo device."""
        return self.devices[3]

    @property
    def si(self):
        """Return SI CurrInfo device."""
        return self.devices[4]
