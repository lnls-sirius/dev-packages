"""."""

from mathphys.functions import get_namedtuple as _get_namedtuple

from ..namesys import SiriusPVName as _PVName
from .device import Device as _Device, DeviceSet as _DeviceSet


class Screen(_DeviceSet):
    """Screen Device."""

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
        LI_1 = 'LA-BI:PRF1'
        LI_2 = 'LA-BI:PRF2'
        LI_3 = 'LA-BI:PRF3'
        LI_4 = 'LA-BI:PRF4'
        LI_5 = 'LA-BI:PRF5'
        LI = (LI_1, LI_2, LI_3, LI_4, LI_5)
        TB = (TB_1, TB_2, TB_3, TB_4, TB_5, TB_6)
        BO = (BO_1, BO_2, BO_3)
        TS = (TS_1, TS_2, TS_3, TS_4, TS_5, TS_6)
        ALL = TB + BO + TS + LI

    def __new__(cls, devname):
        """."""
        # check if device exists
        if devname not in Screen.DEVICES.ALL:
            raise NotImplementedError(devname)

        if devname.lower().startswith('la'):
            return LIScreen(devname)
        else:
            return TBBOTSScreen(devname)


class LIScreen(_Device):
    """."""

    PROPERTIES_DEFAULT = (
        'RAW:ArrayData',
        'IMG:ArrayData',
        'ROI:MaxSizeX_RBV',
        'ROI:MaxSizeY_RBV',
        'ROI:SizeX',
        'ROI:SizeY',
        'ROI:SizeX_RBV',
        'ROI:SizeY_RBV',
        'ROI:MinX_',
        'ROI:MinY_',
        'ROI:MinX_RBV',
        'ROI:MinY_RBV',
        'X:Gauss:Peak',
        'Y:Gauss:Peak',
        'X:Gauss:Sigma',
        'Y:Gauss:Sigma',
        'X:Gauss:Coef',
        'Y:Gauss:Coef',
        'CAM:Gain',
        'CAM:Gain_RBV',
        'CAM:AcquireTime',
        'CAM:AcquireTime_RBV',
    )

    def __init__(self, devname, props2init='all'):
        """."""
        if devname not in Screen.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def image_width(self):
        """."""
        return self['ROI:MaxSizeX_RBV']

    @property
    def image_height(self):
        """."""
        return self['ROI:MaxSizeY_RBV']

    @property
    def image(self):
        """."""
        row_image = self['RAW:ArrayData']
        h = self.image_height
        w = self.image_width
        return row_image.reshape([h, w])

    @property
    def centerx(self):
        """."""
        return self['X:Gauss:Peak']

    @property
    def centery(self):
        """."""
        return self['Y:Gauss:Peak']

    @property
    def sigmax(self):
        """."""
        return self['X:Gauss:Sigma']

    @property
    def sigmay(self):
        """."""
        return self['Y:Gauss:Sigma']

    @property
    def scale_factor_x(self):
        """Pixel to mm."""
        return self['X:Gauss:Coef']

    @property
    def scale_factor_y(self):
        """Pixel to mm."""
        return self['Y:Gauss:Coef']

    @property
    def roix_size(self):
        """."""
        return self['ROI:SizeX_RBV']

    @property
    def roiy_size(self):
        """."""
        return self['ROI:SizeY_RBV']

    @property
    def roix_start(self):
        """."""
        return self['ROI:MinX_RBV']

    @property
    def roiy_start(self):
        """."""
        return self['ROI:MinY_RBV']

    @property
    def image_roi(self):
        """."""
        img = self['IMG:ArrayData']
        return img.reshape((self.roix_size, self.roiy_size))

    @property
    def cam_exposure(self):
        """."""
        return self['CAM:AcquireTime_RBV']

    @property
    def cam_gain(self):
        """."""
        return self['CAM:Gain_RBV']


class TBBOTSScreen(_DeviceSet):
    """."""

    DsblEnbl = _get_namedtuple('DsblEnbl', ['OFF', 'ON'])
    ScrnPosition = _get_namedtuple(
        'ScrnPosition', ['None_', 'Calibration', 'Fluorescent', 'Unknown']
    )
    Homing = _get_namedtuple('Homing', ['In Progress', 'Finished', 'Error'])

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in Screen.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        self.screen = _Screen(devname)
        self.screencam = _ScreenCam(devname)
        devs = [self.screen, self.screencam]
        super().__init__(devs, devname=devname)

    @property
    def homing_status_str(self):
        """."""
        return self.Homing._fields[self.screen['HomeDone-Mon']]

    @property
    def homing_status(self):
        """."""
        return self.screen['HomeDone-Mon']

    def cmd_do_homing(self, timeout=60):
        """."""
        self.screen['Home-Cmd'] = 1
        return self._wait(
            'HomeDone-Mon', self.Homing.Finished, timeout=timeout
        )

    @property
    def screen_position_str(self):
        """."""
        return self.ScrnPosition._fields[self.screen['ScrnType-Sts']]

    @property
    def screen_position(self):
        """."""
        return self.screen['ScrnType-Sts']

    @screen_position.setter
    def screen_position(self, value):
        """."""
        self.screen._enum_setter('ScrnType-Sel', value, self.ScrnPosition)

    def change_screen_position(self, screen_type, timeout=20):
        """."""
        screen_type = self.screen._enum_selector(
            screen_type, self.ScrnPosition
        )
        self.screen_position = screen_type
        return self._wait('ScrnType-Sts', screen_type, timeout=timeout)

    def move_to_calibration(self, timeout=20):
        """."""
        return self.change_screen_position(
            self.ScrnPosition.Calibration, timeout=timeout
        )

    def move_to_fluorescent(self, timeout=20):
        """."""
        return self.change_screen_position(
            self.ScrnPosition.Fluorescent, timeout=timeout
        )

    def move_to_none(self, timeout=20):
        """."""
        return self.change_screen_position(
            self.ScrnPosition.None_, timeout=timeout
        )

    @property
    def enabled_str(self):
        """."""
        return self.DsblEnbl._fields[self.screencam['Enbl-Sts']]

    @property
    def enabled(self):
        """."""
        return self.screencam['Enbl-Sts']

    @enabled.setter
    def enabled(self, value):
        """."""
        self.screencam._enum_setter('Enbl-Sel', value, self.DsblEnbl)

    def cmd_enable(self, timeout=1):
        """."""
        self.enabled = self.DsblEnbl.ON
        return self.wait('Enbl-Sts', self.DsblEnbl.ON, timeout=timeout)

    def cmd_disable(self, timeout=1):
        """."""
        self.enabled = self.DsblEnbl.OFF
        return self._wait('Enbl-Sts', self.DsblEnbl.OFF, timeout=timeout)

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
    def exposure_time(self):
        """."""
        return self.screencam['ExposureTime-RB']

    @exposure_time.setter
    def exposure_time(self, value):
        """."""
        self.screencam['ExposureTime-SP'] = value

    @property
    def gain(self):
        """."""
        return self.screencam['Gain-RB']

    @gain.setter
    def gain(self, value):
        """."""
        self.screencam['Gain-SP'] = value

    @property
    def frame_count(self):
        """."""
        return self.screencam['FrameCnt-Mon']

    @property
    def scale_factor_x(self):
        """Pixel to mm."""
        return self.screencam['ScaleFactorX-RB']

    @property
    def scale_factor_y(self):
        """Pixel to mm."""
        return self.screencam['ScaleFactorY-RB']

    @property
    def center_offset_x(self):
        """."""
        return self.screencam['CenterOffsetX-RB']

    @property
    def center_offset_y(self):
        """."""
        return self.screencam['CenterOffsetY-RB']


""" TODO: _Screen and _ScreenCam class could be merged into DVF class, since
    they seem to implement the same functionalities and originally had the same
    base IOC code.
"""


class _Screen(_Device):
    """."""

    DEVICES = Screen.DEVICES

    PROPERTIES_DEFAULT = (
        'Home-Cmd',
        'HomeDone-Mon',
        'ScrnType-Sel',
        'ScrnType-Sts',
        'ImgData-Mon',
        'CenterXDimFei-Mon',
        'CenterYDimFei-Mon',
        'SigmaXDimFei-Mon',
        'SigmaYDimFei-Mon',
        'ThetaDimFei-Mon',
        'ImgROIHeight-RB',
        'ImgROIWidth-RB',
    )

    def __init__(self, devname, props2init='all'):
        """."""
        if devname not in Screen.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)


class _ScreenCam(_Device):
    """."""

    DEVICES = Screen.DEVICES

    PROPERTIES_DEFAULT = (
        'Enbl-Sel',
        'Enbl-Sts',
        'ScaleFactorX-RB',
        'ScaleFactorY-RB',
        'CenterOffsetX-RB',
        'CenterOffsetY-RB',
        'ExposureTime-SP',
        'ExposureTime-RB',
        'Gain-SP',
        'Gain-RB',
        'FrameCnt-Mon',
    )

    def __init__(self, devname, props2init='all'):
        """."""
        if devname not in Screen.DEVICES.ALL:
            raise NotImplementedError(devname)
        devname = _PVName(devname).substitute(dev='ScrnCam')
        super().__init__(devname, props2init=props2init)
