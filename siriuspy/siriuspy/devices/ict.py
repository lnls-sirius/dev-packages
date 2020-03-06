"""."""

from .device import Device as _Device


class ICT(_Device):
    """ICT Device."""

    DEVICE_LI_1 = 'LI-01:DI-ICT-1'
    DEVICE_LI_2 = 'LI-01:DI-ICT-2'

    DEVICES = (DEVICE_LI_1, DEVICE_LI_2)

    _properties_li = (
        'Charge-Mon', 'ChargeAvg-Mon', 'ChargeMax-Mon',
        'ChargeMin-Mon', 'ChargeStd-Mon', 'PulseCount-Mon')

    _properties = {
        DEVICE_LI_1: _properties_li,
        DEVICE_LI_2: _properties_li}

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in (ICT.DEVICE_LI_1, ICT.DEVICE_LI_2):
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=ICT._properties[devname])

    @property
    def charge(self):
        """."""
        return self['Charge-Mon']

    @property
    def charge_avg(self):
        """."""
        return self['ChargeAvg-Mon']

    @property
    def charge_max(self):
        """."""
        return self['ChargeMax-Mon']

    @property
    def charge_min(self):
        """."""
        return self['ChargeMin-Mon']

    @property
    def charge_std(self):
        """."""
        return self['ChargeStd-Mon']

    @property
    def pulse_count(self):
        """."""
        return self['PulseCount-Mon']


class TranspEff(_Device):
    """Transport Efficiency Device."""

    DEVICE_LI = 'LI-Glob:AP-TranspEff'

    _properties_li = ('Eff-Mon', )

    _properties = {
        DEVICE_LI: _properties_li}

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in (TranspEff.DEVICE_LI, ):
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=TranspEff._properties[devname])

    @property
    def efficiency(self):
        """."""
        return self['Eff-Mon']
