"""."""

from .device import Device as _Device


class Screen(_Device):
    """."""

    DEVICE_TB_1 = 'TB-01:DI-Scrn-1'
    DEVICE_TB_2 = 'TB-01:DI-Scrn-2'
    DEVICE_TB_3 = 'TB-02:DI-Scrn-1'
    DEVICE_TB_4 = 'TB-02:DI-Scrn-2'
    DEVICE_TB_5 = 'TB-03:DI-Scrn'
    DEVICE_TB_6 = 'TB-04:DI-Scrn'
    DEVICE_BO_1 = 'BO-01D:DI-Scrn-1'
    DEVICE_BO_2 = 'BO-01D:DI-Scrn-2'
    DEVICE_BO_3 = 'BO-02U:DI-Scrn'
    DEVICE_TS_1 = 'TS-01:DI-Scrn'
    DEVICE_TS_2 = 'TS-02:DI-Scrn'
    DEVICE_TS_3 = 'TS-03:DI-Scrn'
    DEVICE_TS_4 = 'TS-04:DI-Scrn-1'
    DEVICE_TS_5 = 'TS-04:DI-Scrn-2'
    DEVICE_TS_6 = 'TS-04:DI-Scrn-3'

    DEVICES = (
        DEVICE_TB_1,
        DEVICE_TB_2,
        DEVICE_TB_3,
        DEVICE_TB_4,
        DEVICE_TB_5,
        DEVICE_TB_6,
        DEVICE_BO_1,
        DEVICE_BO_2,
        DEVICE_BO_3,
        DEVICE_TS_1,
        DEVICE_TS_2,
        DEVICE_TS_3,
        DEVICE_TS_4,
        DEVICE_TS_5,
        DEVICE_TS_6)

    _properties = (
        'ImgData-Mon',
        'CenterXDimFei-Mon', 'CenterYDimFei-Mon',
        'SigmaXDimFei-Mon', 'SigmaYDimFei-Mon',
    )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in Screen.DEVICES:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=Screen._properties)

    @property
    def image(self):
        """."""
        return self['ImgData-Mon']

    @property
    def centerx(self):
        """."""
        return self['CenterXDimFei-Mon']

    @property
    def centery(self):
        """."""
        return self['CenterYDimFei-Mon']

    @property
    def sigmax(self):
        """."""
        return self['SigmaXDimFei-Mon']

    @property
    def sigmay(self):
        """."""
        return self['SigmaYDimFei-Mon']
