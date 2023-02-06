"""."""

from .device import Device as _Device


class LIEnergy(_Device):
    """Linac Energy Measurement Device."""

    class DEVICES:
        """Devices names."""

        LI = 'LI-Glob:AP-MeasEnergy'
        ALL = (LI, )

    _properties = (
        'Dispersion-SP', 'Angle-SP', 'Spectrometer-SP',
        'Dispersion-RB', 'Angle-RB', 'Spectrometer-RB',
        'IntDipole-Mon', 'Energy-Mon', 'Spread-Mon',
        'MeasureCtrl-Sel', 'MeasureCtrl-Sts')

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in LIEnergy.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=LIEnergy._properties)

    @property
    def dispersion(self):
        """."""
        return self['Dispersion-RB']

    @dispersion.setter
    def dispersion(self, val):
        self['Dispersion-SP'] = val

    @property
    def angle(self):
        """."""
        return self['Angle-RB']

    @angle.setter
    def angle(self, val):
        self['Angle-SP'] = val

    @property
    def spectrometer(self):
        """."""
        return self['Spectrometer-RB']

    @spectrometer.setter
    def spectrometer(self, val):
        self['Spectrometer-SP'] = val

    @property
    def intdipole(self):
        """."""
        return self['IntDipole-Mon']

    @property
    def energy(self):
        """."""
        return self['Energy-Mon']

    @property
    def energy_spread(self):
        """."""
        return self['Spread-Mon']

    @property
    def is_measuring(self):
        """."""
        return self['MeasureCtrl-Sts']

    def cmd_turn_on_measurement(self):
        """."""
        self['MeasureCtrl-Sel'] = 1

    def cmd_turn_off_measurement(self):
        """."""
        self['MeasureCtrl-Sel'] = 0
