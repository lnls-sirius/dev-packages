"""."""

from .device import Device as _Device


class BeamlineScreen(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        MANACA = 'SI-09SABL:AP-Manaca-MVS2:'
        ALL = (MANACA, )

    _properties = (
        'BeamCenterX-Mon', 'BeamCentermmX-Mon',
        'BeamCenterY-Mon', 'BeamCentermmY-Mon',
        'BeamSizeX-Mon', 'BeamSizemmX-Mon',
        'BeamSizeY-Mon', 'BeamSizemmY-Mon',
    )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in BeamLineScreen.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=BeamLineScreen._properties)


    @property
    def centerx(self):
        """."""
        return self['BeamCenterX-Mon']

    @property
    def centermmx(self):
        """."""
        return self['BeamCentermmX-Mon']

    @property
    def centery(self):
        """."""
        return self['BeamCenterY-Mon']

    @property
    def centermmy(self):
        """."""
        return self['BeamCentermmY-Mon']

    @property
    def sizex(self):
        """."""
        return self['BeamSizeX-Mon']

    @property
    def sizemmx(self):
        """."""
        return self['BeamSizemmX-Mon']

    @property
    def centery(self):
        """."""
        return self['BeamSizeY-Mon']

    @property
    def centermmy(self):
        """."""
        return self['BeamSizemmY-Mon']
