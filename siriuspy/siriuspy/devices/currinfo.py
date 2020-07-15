"""."""
from .device import Device as _Device


class CurrInfo(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        LI = 'LI-Glob:AP-CurrInfo'
        TB = 'TB-Glob:AP-CurrInfo'
        BO = 'BO-Glob:AP-CurrInfo'
        TS = 'TS-Glob:AP-CurrInfo'
        SI = 'SI-Glob:AP-CurrInfo'
        ALL = (LI, TB, BO, TS, SI, )

    _properties = (
        # linac and transport lines
        'TranspEff-Mon',
        # booster
        'Charge150MeV-Mon', 'Current150MeV-Mon',
        'Charge1GeV-Mon', 'Current1GeV-Mon',
        'Charge2GeV-Mon', 'Current2GeV-Mon',
        'Charge3GeV-Mon', 'Current3GeV-Mon',
        'IntCurrent3GeV-Mon', 'RampEff-Mon'
        # storage ring
        'Charge-Mon', 'Current-Mon',
        'InjEff-Mon', 'Lifetime-Mon', 'LifetimeBPM-Mon'
        'StoredEBeam-Mon'
    )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in CurrInfo.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=CurrInfo._properties)

    @property
    def transpeff(self):
        """."""
        if 'BO' in self.devname or 'SI' in self.devname:
            return None
        return self['TranspEff-Mon']

    @property
    def charge150mev(self):
        """."""
        if 'BO' not in self.devname:
            return None
        return self['Charge150MeV-Mon']

    @property
    def current150mev(self):
        """."""
        if 'BO' not in self.devname:
            return None
        return self['Current150MeV-Mon']

    @property
    def charge1gev(self):
        """."""
        if 'BO' not in self.devname:
            return None
        return self['Charge1GeV-Mon']

    @property
    def current1gev(self):
        """."""
        if 'BO' not in self.devname:
            return None
        return self['Current1GeV-Mon']

    @property
    def charge2gev(self):
        """."""
        if 'BO' not in self.devname:
            return None
        return self['Charge2GeV-Mon']

    @property
    def current2gev(self):
        """."""
        if 'BO' not in self.devname:
            return None
        return self['Current2GeV-Mon']

    @property
    def charge3gev(self):
        """."""
        if 'BO' not in self.devname:
            return None
        return self['Charge3GeV-Mon']

    @property
    def current3gev(self):
        """."""
        if 'BO' not in self.devname:
            return None
        return self['Current3GeV-Mon']

    @property
    def intcurrent3gev(self):
        """."""
        if 'BO' not in self.devname:
            return None
        return self['IntCurrent3GeV-Mon']

    @property
    def rampeff(self):
        """."""
        if 'BO' not in self.devname:
            return None
        return self['RampEff-Mon']

    @property
    def charge(self):
        """."""
        if 'SI' not in self.devname:
            return None
        return self['Charge-Mon']

    @property
    def current(self):
        """."""
        if 'SI' not in self.devname:
            return None
        return self['Current-Mon']

    @property
    def injeff(self):
        """."""
        if 'SI' not in self.devname:
            return None
        return self['InjEff-Mon']

    @property
    def lifetime(self):
        """."""
        if 'SI' not in self.devname:
            return None
        return self['Lifetime-Mon']

    @property
    def lifetimebpm(self):
        """."""
        if 'SI' not in self.devname:
            return None
        return self['LifetimeBPM-Mon']

    @property
    def storedbeam(self):
        """."""
        if 'SI' not in self.devname:
            return None
        return self['StoredEBeam-Mon']
