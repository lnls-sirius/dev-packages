"""."""

from .device import Device as _Device


class LIEnergy(_Device):
    """Linac Energy Measurement Device."""

    class DEVICES:
        """Devices names."""

        LI = 'LI-Glob:AP-MeasEnergy'
        ALL = (LI, )

    PROPERTIES_DEFAULT = (
        'Dispersion-SP', 'Dispersion-RB',
        'IntDipole-Mon', 'Energy-Mon', 'Spread-Mon',
        'MeasureCtrl-Sel', 'MeasureCtrl-Sts')

    def __init__(self, devname=None, props2init='all'):
        """."""
        # check if device exists
        devname = devname if devname else self.DEVICES.LI
        if devname not in LIEnergy.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def dispersion(self):
        """."""
        return self['Dispersion-RB']

    @dispersion.setter
    def dispersion(self, val):
        self['Dispersion-SP'] = val

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

    def cmd_turn_on_measurement(self, timeout=10):
        """."""
        self['MeasureCtrl-Sel'] = 1
        return self._wait('MeasureCtrl-Sts', 1, timeout=timeout)

    def cmd_turn_off_measurement(self, timeout=10):
        """."""
        self['MeasureCtrl-Sel'] = 0
        return self._wait('MeasureCtrl-Sts', 0, timeout=timeout)
