"""."""

from ..namesys import SiriusPVName as _PVName
from .device import Device as _Device, Devices as _Devices


class Screen(_Devices):
    """."""

    class DEVICES:
        """Devices names."""

        TB_1 = 'TB-01:DI-Scrn-1'
        TB_2 = 'TB-01:DI-Scrn-2'
        TB_3 = 'TB-02:DI-Scrn-1'
        TB_4 = 'TB-02:DI-Scrn-2'
        TB_5 = 'TB-03:DI-Scrn'
        TB_6 = 'TB-04:DI-Scrn'
        BO_1 = 'BO-01D:DI-Scrn-1'
        BO_2 = 'BO-01D:DI-Scrn-2'
        BO_3 = 'BO-02U:DI-Scrn'
        TS_1 = 'TS-01:DI-Scrn'
        TS_2 = 'TS-02:DI-Scrn'
        TS_3 = 'TS-03:DI-Scrn'
        TS_4 = 'TS-04:DI-Scrn-1'
        TS_5 = 'TS-04:DI-Scrn-2'
        TS_6 = 'TS-04:DI-Scrn-3'
        TB = (TB_1, TB_2, TB_3, TB_4, TB_5, TB_6)
        TS = (TS_1, TS_2, TS_3, TS_4, TS_5, TS_6)
        BO = (BO_1, BO_2, BO_3)
        ALL = (
            TB_1, TB_2, TB_3, TB_4, TB_5, TB_6,
            BO_1, BO_2, BO_3,
            TS_1, TS_2, TS_3, TS_4, TS_5, TS_6)

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in Screen.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        self.screen = _Screen(devname)
        self.screencam = _ScreenCam(devname)
        devs = [self.screen, self.screencam]
        super().__init__(devname, devices=devs)

    @property
    def image_width(self):
        """."""
        return self.screen['ImgROIWidth-RB']

    @property
    def image_height(self):
        """."""
        return self.screen['ImgROIHeight-RB']

    @property
    def image(self):
        """."""
        row_image = self.screen['ImgData-Mon']
        h = self.image_height
        w = self.image_width
        return row_image.reshape([h, w])

    @property
    def centerx(self):
        """."""
        return self.screen['CenterXDimFei-Mon']

    @property
    def centery(self):
        """."""
        return self.screen['CenterYDimFei-Mon']

    @property
    def sigmax(self):
        """."""
        return self.screen['SigmaXDimFei-Mon']

    @property
    def sigmay(self):
        """."""
        return self.screen['SigmaYDimFei-Mon']

    @property
    def angle(self):
        """."""
        return self.screen['ThetaDimFei-Mon']

    @property
    def scale_factor_x(self):
        """Pixel to mm"""
        return self.screencam['ScaleFactorX-RB']

    @property
    def scale_factor_y(self):
        """Pixel to mm"""
        return self.screencam['ScaleFactorY-RB']

    @property
    def center_offset_x(self):
        """."""
        return self.screencam['CenterOffsetX-RB']

    @property
    def center_offset_y(self):
        """."""
        return self.screencam['CenterOffsetY-RB']


class _Screen(_Device):
    """."""

    DEVICES = Screen.DEVICES

    _properties = (
        'ImgData-Mon',
        'CenterXDimFei-Mon', 'CenterYDimFei-Mon',
        'SigmaXDimFei-Mon', 'SigmaYDimFei-Mon',
        'ThetaDimFei-Mon', 'ImgROIHeight-RB',
        'ImgROIWidth-RB'
    )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in Screen.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=_Screen._properties)


class _ScreenCam(_Device):
    """."""

    DEVICES = Screen.DEVICES

    _properties = (
        'ScaleFactorX-RB', 'ScaleFactorY-RB',
        'CenterOffsetX-RB', 'CenterOffsetY-RB',
        )

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in Screen.DEVICES.ALL:
            raise NotImplementedError(devname)

        devname = _PVName(devname).substitute(dev='ScrnCam')
        # call base class constructor
        super().__init__(devname, properties=_ScreenCam._properties)
