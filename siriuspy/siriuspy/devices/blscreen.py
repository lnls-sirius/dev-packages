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
        if devname not in BeamlineScreen.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=BeamlineScreen._properties)

    @property
    def centerx_pxl(self):
        """."""
        return self['BeamCenterX-Mon']

    @property
    def centerx_mm(self):
        """."""
        return self['BeamCentermmX-Mon']

    @property
    def centery_pxl(self):
        """."""
        return self['BeamCenterY-Mon']

    @property
    def centery_mm(self):
        """."""
        return self['BeamCentermmY-Mon']

    @property
    def sizex_pxl(self):
        """."""
        return self['BeamSizeX-Mon']

    @property
    def sizex_mm(self):
        """."""
        return self['BeamSizemmX-Mon']

    @property
    def sizey_pxl(self):
        """."""
        return self['BeamSizeY-Mon']

    @property
    def sizey_mm(self):
        """."""
        return self['BeamSizemmY-Mon']
