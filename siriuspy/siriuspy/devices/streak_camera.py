"""Streak Camera control"""

from .device import Device as _Device
from .device import _PVNames

class StreakCamera(_Device):
    """Wrap the basic features of the Streak Camera used in Sirius
    
    The Streak Camera is the model C5680, installed in the IMBUIA beamline.
    For more information about the functionalities of this equipment and IOC
    information, please refer to:
        https://github.com/lnls-ids/c5680-streak-camera-ioc
    """
    PVS = _PVNames()

    class DEVICES:
        SC = "SC"
        ALL = (SC,)

    def __init__(self, devname=None, props2init="all", **kwargs):
        """Init."""
        if devname is None:
            devname = self.DEVICES.SC
        if devname not in self.DEVICES.ALL:
            raise ValueError("Wrong value for devname")

        super().__init__(devname=devname, props2init=props2init, **kwargs)

        # Streak Camera IOC Prefix
        pvprefix = 'SC:IMB:'

        # General Parameters
        self.PVS.TIME_RANGE_SP   = pvprefix + 'GenParams:TimeRange-SP'
        self.PVS.TIME_RANGE_RB   = pvprefix + 'GenParams:TimeRange-RB'
        self.PVS.MCP_GAIN_SP     = pvprefix + 'GenParams:MCPGain-SP'
        self.PVS.MCP_GAIN_RB     = pvprefix + 'GenParams:MCPGain-RB'
        self.PVS.HTRIG_LEV_SP    = pvprefix + 'GenParams:HTrigLevel-SP'
        self.PVS.HTRIG_LEV_RB    = pvprefix + 'GenParams:HTrigLevel-RB'
        self.PVS.DELAY_SP        = pvprefix + 'GenParams:Delay-SP'
        self.PVS.DELAY_RB        = pvprefix + 'GenParams:Delay-RB'
        self.PVS.FOC_TIMEOVER_SP = pvprefix + 'GenParams:FocusTimeOver-SP'
        self.PVS.FOC_TIMEOVER_RB = pvprefix + 'GenParams:FocusTimeOver-RB'
        self.PVS.MODE_SEL        = pvprefix + 'GenParams:Mode-Sel'
        self.PVS.MODE_STS        = pvprefix + 'GenParams:Mode-Sts'
        self.PVS.GATE_MODE_SEL   = pvprefix + 'GenParams:GateMode-Sel'
        self.PVS.GATE_MODE_STS   = pvprefix + 'GenParams:GateMode-Sts'
        self.PVS.SHUTTER_SEL     = pvprefix + 'GenParams:Shutter-Sel'
        self.PVS.SHUTTER_STS     = pvprefix + 'GenParams:Shutter-Sts' 
        self.PVS.BLANK_AMP_SEL   = pvprefix + 'GenParams:BlankingAmp-Sel'
        self.PVS.BLANK_AMP_STS   = pvprefix + 'GenParams:BlankingAmp-Sts'
        self.PVS.HTRIG_STS_SEL   = pvprefix + 'GenParams:HTrigStatus-Sel'
        self.PVS.HTRIG_STS_STS   = pvprefix + 'GenParams:HTrigStatus-Sts'
        self.PVS.HTRIG_MODE_SEL  = pvprefix + 'GenParams:HTrigMode-Sel'
        self.PVS.HTRIG_MODE_STS  = pvprefix + 'GenParams:HTrigMode-Sts'

        # Acquisition Commands
        self.PVS.ACQ_START_SEL = pvprefix + 'AcqParams:Start-Sel'
        self.PVS.ACQ_START_STS = pvprefix + 'AcqParams:Start-Sts'

        # LUT Control
        self.PVS.LUT_LOW_LIMIT_MON = pvprefix + 'LUT:LowerLimit-RB' #  Get LUT lower limits -> Change suffix to -Mon
        self.PVS.LUT_UPP_LIMIT_MON = pvprefix + 'LUT:UpperLimit-RB' #  Get LUT upper limits -> Change suffix to -Mon
        self.PVS.LUT_AUTOSET_CMD   = pvprefix + 'LUT:SetAuto-Cmd'

        # Image Parameters
        self.PVS.ROI_INI_X_SP   = pvprefix + 'ImgParams:RoiIniX-SP'
        self.PVS.ROI_INI_X_RB   = pvprefix + 'ImgParams:RoiIniX-RB'
        self.PVS.ROI_INI_Y_SP   = pvprefix + 'ImgParams:RoiIniY-SP'
        self.PVS.ROI_INI_Y_RB   = pvprefix + 'ImgParams:RoiIniY-RB'
        self.PVS.ROI_WID_X_SP   = pvprefix + 'ImgParams:RoiWidthX-SP'
        self.PVS.ROI_WID_X_RB   = pvprefix + 'ImgParams:RoiWidthX-RB'
        self.PVS.ROI_WID_Y_SP   = pvprefix + 'ImgParams:RoiWidthY-SP'
        self.PVS.ROI_WID_Y_RB   = pvprefix + 'ImgParams:RoiWidthY-RB'
        self.PVS.IMG_WIDTH_MON  = pvprefix + 'ImgParams:ImageWidth-Mon'
        self.PVS.IMG_HEIGHT_MON = pvprefix + 'ImgParams:ImageHeight-Mon'
        self.PVS.IMG_OPENED_MON = pvprefix + 'ImgParams:ImageOpened-Mon'
        self.PVS.FWHM_MON       = pvprefix + 'ImgProfile:FWHM-Mon'

        # Camera Parameters
        self.PVS.EXPOSURE_SP     = pvprefix + 'CamParams:Exposure-SP'
        self.PVS.EXPOSURE_RB     = pvprefix + 'CamParams:Exposure-RB'
        self.PVS.VER_REC_ROI_CMD = pvprefix + 'ImgParams:CreateVerRectRoi-Cmd' # Creates vertical rectagular ROI

        # App Commands
        self.PVS.APP_START_CMD = pvprefix + 'App:Start-Cmd'
        self.PVS.APP_END_CMD   = pvprefix + 'App:End-Cmd'       

        self.PROPERTIES_DEFAULT = tuple(
            set(value for key, value in vars(self.PVS).items())
        )

    @property
    def time_range(self):
        """Returns the acquisition time range from 1-4
        Where:
        1 -  150 ps
        2 -  400 ps
        3 -  800 ps
        4 - 1600 ps
        """
        return self[self.PVS.TIME_RANGE_RB]

    @time_range.setter
    def time_range(self, value):
        """Sets acquisition time range from 1-4"""
        self[self.PVS.TIME_RANGE_SP] = value

    @property
    def mcp_gain(self):
        """Returns the MCP Gain value"""
        return self[self.PVS.MCP_GAIN_RB]

    @mcp_gain.setter
    def mcp_gain(self, value):
        """Sets MCP gain value from 0-63"""
        self[self.PVS.MCP_GAIN_SP] = value

    @property
    def htrig_level(self):
        """Returns HTrig level value"""
        return self[self.PVS.HTRIG_LEV_RB]

    @htrig_level.setter
    def htrig_level(self, value):
        """Sets HTrig level value"""
        self[self.PVS.HTRIG_LEV_SP] = value

    @property
    def delay(self):
        """Returns delay value"""
        return self[self.PVS.DELAY_RB]
    
    @delay.setter
    def delay(self, value):
        """Sets delay value"""
        self[self.PVS.DELAY_SP] = value

    @property
    def focus_timeover(self):
        """Returns focus timeover in minutes"""
        return self[self.PVS.FOC_TIMEOVER_RB]
    
    @focus_timeover.setter
    def focus_timeover(self, value):
        """Sets focus timeover in minutes"""
        self[self.PVS.FOC_TIMEOVER_SP] = value
    
    @property
    def mode(self):
        """Returns the operation mode
        Where:
        0 - Focus
        1 - Operate
        """
        return self[self.PVS.MODE_STS]
    
    @mode.setter
    def mode(self, value):
        """Sets the operation mode"""
        self[self.PVS.MODE_SEL] = value

    @property
    def gate_mode(self):
        """Returns the gate mode
        Where:
        0 - Normal
        1 - External
        """
        return self[self.PVS.GATE_MODE_STS]
    
    @gate_mode.setter
    def gate_mode(self, value):
        """Sets the gate mode"""
        self[self.PVS.GATE_MODE_SEL] = value
    
    @property
    def shutter(self):
        """Returns the SC shutter state
        Where:
        0 - Closed
        1 - Opened
        """
        return self[self.PVS.SHUTTER_STS]
    
    @shutter.setter
    def shutter(self, value):
        """Sets the SC shutter state"""
        self[self.PVS.SHUTTER_SEL] = value

    @property
    def blanking_amp(self):
        """Returns the blanking amp time from 0-15
        Where:
         0 - Off
         1 - 100 ns
         2 - 200 ns
         3 - 500 ns
         4 -   1 us
         5 -   2 us
         6 -   5 us
         7 -  10 us
         8 -  20 us
         9 -  50 us
        10 - 100 us
        11 - 200 us
        12 - 500 us
        13 -   1 ms
        14 -   2 ms
        15 -   5 ms
        """
        return self[self.PVS.BLANK_AMP_STS]
    
    @blanking_amp.setter
    def blanking_amp(self, value):
        """Sets the blanking amp time from 0-15"""
        self[self.PVS.BLANK_AMP_SEL] = value

    @property
    def htrig_status(self):
        """Returns HTrig status
        Where:
        0 - Ready
        1 - Fired
        2 - Do Reset
        """
        return self[self.PVS.HTRIG_STS_STS]
    
    @htrig_status.setter
    def htrig_status(self, value):
        """Sets HTrig status"""
        self[self.PVS.HTRIG_STS_SEL] = value

    @property
    def htrig_mode(self):
        """Returns HTrig mode
        Where:
        0 - Cont
        1 - Single
        """
        return self[self.PVS.HTRIG_MODE_STS]
    
    @htrig_mode.setter
    def htrig_mode(self, value):
        """Sets HTrig mode"""
        self[self.PVS.HTRIG_MODE_SEL] = value

    @property
    def acquisition(self):
        """Returns the current acquisiton mode
        Where:
        0 - Live
        1 - Acquire
        2 - AI
        3 - PC
        """
        return self[self.PVS.ACQ_START_STS]
    
    @acquisition.setter
    def acquisition(self, value):
        """Sets the acquisition mode"""
        self[self.PVS.ACQ_START_SEL] = value

    @property
    def lut_lower_limits(self):
        """Returns LUT lower limit value"""
        return self[self.PVS.LUT_LOW_LIMIT_MON]
    
    @property
    def lut_upper_limits(self):
        """Returns LUT upper limit value"""
        return self[self.PVS.LUT_UPP_LIMIT_MON]

    def lut_autoset(self):
        """Autoset the LUT values"""
        self[self.PVS.LUT_AUTOSET_CMD] = 1

    @property
    def roi_initial_x(self):
        """Returns the ROI initial X value"""
        return self[self.PVS.ROI_INI_X_RB]
    
    @roi_initial_x.setter
    def roi_initial_x(self, value):
        """Sets the ROI initial X value"""
        self[self.PVS.ROI_INI_X_SP] = value

    @property
    def roi_initial_y(self):
        """Returns the ROI initial Y value"""
        return self[self.PVS.ROI_INI_Y_RB]
    
    @roi_initial_y.setter
    def roi_initial_y(self, value):
        """Sets the ROI initial Y value"""
        self[self.PVS.ROI_INI_Y_SP] = value

    @property
    def roi_width_x(self):
        """Returns the ROI width X value"""
        return self[self.PVS.ROI_WID_X_RB]
    
    @roi_width_x.setter
    def roi_width_x(self, value):
        """Sets the ROI width X value"""
        self[self.PVS.ROI_WID_X_SP] = value

    @property
    def roi_width_y(self):
        """Returns the ROI initial Y value"""
        return self[self.PVS.ROI_WID_Y_RB]
    
    @roi_width_y.setter
    def roi_width_y(self, value):
        """Sets the ROI initial Y value"""
        self[self.PVS.ROI_WID_Y_SP] = value

    @property
    def image_width(self):
        """Returns the image width value"""
        return self[self.PVS.IMG_WIDTH_MON]
    
    @property
    def image_height(self):
        """returns the image height value"""
        return self[self.PVS.IMG_HEIGHT_MON]
    
    @property
    def image_opened(self):
        """Returns whether the image is opened"""
        return self[self.PVS.IMG_OPENED_MON]
    
    @property
    def image_fwhm(self):
        """Returns the current image FWHM"""
        return self[self.PVS.FWHM_MON]
    
    @property
    def exposure(self):
        """Returns the exposure time in us or ms"""
        return self[self.PVS.EXPOSURE_RB]
    
    @exposure.setter
    def exposure(self, value):
        """Sets the exposure time in ms"""
        self[self.PVS.EXPOSURE_SP] = value

    def create_vertical_rect_roi(self):
        """Creates a vertical rectangular ROI"""
        self[self.PVS.VER_REC_ROI_CMD] = 1

    def start_app(self):
        """Starts the HPD-TA Software"""
        self[self.PVS.APP_START_CMD] = 1

    def end_app(self):
        self[self.PVS.APP_END_CMD] = 1
