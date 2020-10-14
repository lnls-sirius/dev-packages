"""Define Screen device high level PVs database.

This is not a primary source database. Primary sources can be found in:
 - Screen IOC: https://github.com/lnls-dig/screen-epics-ioc
 - Camera IOC: https://github.com/lnls-dig/basler-acA1300-75gm-epics-ioc
 - Motor IOC: https://github.com/lnls-dig/galil-dmc30017-epics-ioc
"""

from ... import csdev as _csdev


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    SCRNTYPESEL = ('None', 'Calibration', 'Fluorescent')
    SCRNTYPESTS = ('None', 'Calibration', 'Fluorescent', 'Unknown')
    CAMACQMODE = ('AUTO', 'TRIG')
    CAMEXPOSUREMODE = ('TIMED', 'TRIGWIDTH')
    CAMLASTERR = ('NoError', 'Overtrigger', 'Userset', 'InvalidParameter',
                  'OverTemperature', 'PowerFailure', 'InsufficientTrig',
                  'UserDefPixFailur')
    CAMTEMPSTATE = ('Ok', 'Critical', 'Error')


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_csdev.Const):
    """Const class defining Screens constants and Enum types."""

    CamAcqMode = _csdev.Const.register('CamAcqMode', _et.CAMACQMODE)
    CamExposureMode = _csdev.Const.register('CamExposureMode',
                                            _et.CAMEXPOSUREMODE)
    CamLastErr = _csdev.Const.register('CamLastErr', _et.CAMLASTERR)
    CamTempState = _csdev.Const.register('CamTempState', _et.CAMTEMPSTATE)


_c = Const  # syntactic sugar


# --- Database ---

def get_scrn_database():
    """Return Scrn device database."""
    pvs_database = {
        # Low level devides prefixes
        'MtrCtrlPrefix-Cte': {'type': 'string'},
        'CamPrefix-Cte':     {'type': 'string'},

        # PV to select screen type
        'ScrnType-Sel': {'type': 'enum', 'enums': _et.SCRNTYPESEL, 'value': 0},
        'ScrnType-Sts': {'type': 'enum', 'enums': _et.SCRNTYPESTS, 'value': 0},

        # Camera settings PVs
        'CamEnbl-Sel':         {'type': 'enum', 'enums': _et.OFF_ON,
                                'value': 0},
        'CamEnbl-Sts':         {'type': 'enum', 'enums': _et.OFF_ON,
                                'value': 0},
        'CamAcqMode-Sel':      {'type': 'enum', 'enums': _et.CAMACQMODE,
                                'value': 0},
        'CamAcqMode-Sts':      {'type': 'enum', 'enums': _et.CAMACQMODE,
                                'value': 0},
        'CamAcqPeriod-SP':     {'type': 'float', 'unit': 's', 'prec': 6,
                                'value': 0.2, 'hihi': 10, 'high': 10,
                                'hilim': 10, 'lolim': 0.0124, 'low': 0.0124,
                                'lolo': 0.0124},
        'CamAcqPeriod-RB':     {'type': 'float', 'unit': 's', 'prec': 6,
                                'value': 0.2, 'hihi': 10, 'high': 10,
                                'hilim': 10, 'lolim': 0.0124, 'low': 0.0124,
                                'lolo': 0.0124},
        'CamExposureMode-Sel': {'type': 'enum', 'enums': _et.CAMEXPOSUREMODE,
                                'value': 0},
        'CamExposureMode-Sts': {'type': 'enum', 'enums': _et.CAMEXPOSUREMODE,
                                'value': 0},
        'CamExposureTime-SP':  {'type': 'int', 'unit': 'us', 'value': 5000,
                                'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': 1, 'low': 1,
                                'lolo': 1},
        'CamExposureTime-RB':  {'type': 'int', 'unit': 'us', 'value': 5000,
                                'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': 1, 'low': 1,
                                'lolo': 1},
        'CamGain-SP':          {'type': 'float', 'unit': 'dB', 'prec': 6,
                                'hihi': 20, 'high': 20, 'hilim': 20,
                                'lolim': 0, 'low': 0, 'lolo': 0},
        'CamGain-RB':          {'type': 'float', 'unit': 'dB', 'prec': 6,
                                'hihi': 20, 'high': 20, 'hilim': 20,
                                'lolim': 0, 'low': 0, 'lolo': 0},
        'CamAutoGain-Cmd':     {'type': 'int', 'value': 0},
        'CamBlackLevel-SP':    {'type': 'int', 'unit': 'gray value',
                                'hihi': 64, 'high': 64, 'hilim': 64,
                                'lolim': 0, 'low': 0, 'lolo': 0},
        'CamBlackLevel-RB':    {'type': 'int', 'unit': 'gray value',
                                'hihi': 64, 'high': 64, 'hilim': 64,
                                'lolim': 0, 'low': 0, 'lolo': 0},
        'CamLastErr-Mon':      {'type': 'enum', 'enums': _et.CAMLASTERR},
        'CamClearLastErr-Cmd': {'type': 'int', 'value': 0},
        'CamTempState-Mon':    {'type': 'enum', 'enums': _et.CAMTEMPSTATE},
        'CamTemp-Mon':         {'type': 'float', 'unit': '°C', 'prec': 3},

        # Camera image PVs
        'ImgData-Mon':      {'type': 'int'},
        'ImgMaxWidth-Cte':  {'type': 'int', 'unit': 'pixels'},
        'ImgMaxHeight-Cte': {'type': 'int', 'unit': 'pixels'},

        # Camera ROI settings PVs
        'ImgROIOffsetX-SP':      {'type': 'int', 'unit': 'pixels'},
        'ImgROIOffsetX-RB':      {'type': 'int', 'unit': 'pixels'},
        'ImgROIOffsetY-SP':      {'type': 'int', 'unit': 'pixels'},
        'ImgROIOffsetY-RB':      {'type': 'int', 'unit': 'pixels'},
        'ImgROIWidth-SP':        {'type': 'int', 'unit': 'pixels'},
        'ImgROIWidth-RB':        {'type': 'int', 'unit': 'pixels'},
        'ImgROIHeight-SP':       {'type': 'int', 'unit': 'pixels'},
        'ImgROIHeight-RB':       {'type': 'int', 'unit': 'pixels'},
        'ImgROIAutoCenterX-Sel': {'type': 'int', 'value': 0},
        'ImgROIAutoCenterX-Sts': {'type': 'int', 'value': 0},
        'ImgROIAutoCenterY-Sel': {'type': 'int', 'value': 0},
        'ImgROIAutoCenterY-Sts': {'type': 'int', 'value': 0},

        # Camera image statistics PVs
        'CenterXNDStatsRaw-Mon': {'type': 'int', 'unit': 'pixels'},
        'CenterYNDStatsRaw-Mon': {'type': 'int', 'unit': 'pixels'},
        'SigmaXNDStatsRaw-Mon':  {'type': 'int', 'unit': 'pixels'},
        'SigmaYNDStatsRaw-Mon':  {'type': 'int', 'unit': 'pixels'},
        'SigmaXYNDStatsRaw-Mon': {'type': 'int', 'unit': 'pixels'},
        'CenterXDimFeiRaw-Mon':  {'type': 'int', 'unit': 'pixels'},
        'CenterYDimFeiRaw-Mon':  {'type': 'int', 'unit': 'pixels'},
        'SigmaXDimFeiRaw-Mon':   {'type': 'int', 'unit': 'pixels'},
        'SigmaYDimFeiRaw-Mon':   {'type': 'int', 'unit': 'pixels'},
        'ThetaNDStats-Mon':      {'type': 'float', 'unit': 'rad', 'prec': 6},
        'ThetaDimFei-Mon':       {'type': 'float', 'unit': 'rad', 'prec': 6},

        # Camera image statistics PVs in mm
        'CenterXNDStats-Mon': {'type': 'float', 'unit': 'mm', 'prec': 6},
        'CenterYNDStats-Mon': {'type': 'float', 'unit': 'mm', 'prec': 6},
        'SigmaXNDStats-Mon':  {'type': 'float', 'unit': 'mm', 'prec': 6},
        'SigmaYNDStats-Mon':  {'type': 'float', 'unit': 'mm', 'prec': 6},
        'SigmaXYNDStats-Mon': {'type': 'float', 'unit': 'mm', 'prec': 6},
        'CenterXDimFei-Mon':  {'type': 'float', 'unit': 'mm', 'prec': 6},
        'CenterYDimFei-Mon':  {'type': 'float', 'unit': 'mm', 'prec': 6},
        'SigmaXDimFei-Mon':   {'type': 'float', 'unit': 'mm', 'prec': 6},
        'SigmaYDimFei-Mon':   {'type': 'float', 'unit': 'mm', 'prec': 6},

        # Screens position calibration PVs
        'FluorScrnPos-SP':     {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'hihi': 1000, 'high': 1000, 'hilim': 1000,
                                'lolim': -1000, 'low': -1000, 'lolo': -1000},
        'FluorScrnPos-RB':     {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'hihi': 1000, 'high': 1000, 'hilim': 1000,
                                'lolim': -1000, 'low': -1000, 'lolo': -1000},
        'GetFluorScrnPos-Cmd': {'type': 'int', 'value': 0},
        'CalScrnPos-SP':       {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'hihi': 1000, 'high': 1000, 'hilim': 1000,
                                'lolim': -1000, 'low': -1000, 'lolo': -1000},
        'CalScrnPos-RB':       {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'hihi': 1000, 'high': 1000, 'hilim': 1000,
                                'lolim': -1000, 'low': -1000, 'lolo': -1000},
        'GetCalScrnPos-Cmd':   {'type': 'int', 'value': 0},
        'NoneScrnPos-SP':      {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'hihi': 1000, 'high': 1000, 'hilim': 1000,
                                'lolim': -1000, 'low': -1000, 'lolo': -1000},
        'NoneScrnPos-RB':      {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'hihi': 1000, 'high': 1000, 'hilim': 1000,
                                'lolim': -1000, 'low': -1000, 'lolo': -1000},
        'GetNoneScrnPos-Cmd':  {'type': 'int', 'value': 0},
        'AcceptedErr-SP':      {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'hihi': 1000, 'high': 1000, 'hilim': 1000,
                                'lolim': -1000, 'low': -1000, 'lolo': -1000},
        'AcceptedErr-RB':      {'type': 'float', 'unit': 'mm', 'prec': 5,
                                'hihi': 1000, 'high': 1000, 'hilim': 1000,
                                'lolim': -1000, 'low': -1000, 'lolo': -1000},

        # LED brightness calibration PVs
        'EnblLED-Sel':          {'type': 'enum', 'enums': _et.OFF_ON,
                                 'value': 0},
        'EnblLED-Sts':          {'type': 'enum', 'enums': _et.OFF_ON,
                                 'value': 0},
        'LEDPwrLvl-SP':         {'type': 'float', 'unit': '%',
                                 'hihi': 100, 'high': 100, 'hilim': 100,
                                 'lolim': 0, 'low': 0, 'lolo': 0},
        'LEDPwrLvl-RB':         {'type': 'float', 'unit': '%',
                                 'hihi': 100, 'high': 100, 'hilim': 100,
                                 'lolim': 0, 'low': 0, 'lolo': 0},
        'LEDPwrScaleFactor-SP': {'type': 'float', 'value': 0.011, 'prec': 6,
                                 'hihi': 0.02, 'high': 0.02, 'hilim': 0.02,
                                 'lolim': 0.000001, 'low': 0.000001,
                                 'lolo': 0.000001},
        'LEDPwrScaleFactor-RB': {'type': 'float', 'value': 0.011, 'prec': 6,
                                 'hihi': 0.02, 'high': 0.02, 'hilim': 0.02,
                                 'lolim': 0.000001, 'low': 0.000001,
                                 'lolo': 0.000001},
        'LEDThold-SP':          {'type': 'float', 'unit': 'V', 'prec': 4,
                                 'hihi': 10, 'high': 10, 'hilim': 10,
                                 'lolim': 0, 'low': 0, 'lolo': 0},
        'LEDThold-RB':          {'type': 'float', 'unit': 'V', 'prec': 4,
                                 'hihi': 10, 'high': 10, 'hilim': 10,
                                 'lolim': 0, 'low': 0, 'lolo': 0},

        # Camera statistics unit conversion PVs (pixels -> mm)
        'ImgScaleFactor-SP':   {'type': 'float', 'value': 1, 'prec': 6,
                                'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': 0, 'low': 0,
                                'lolo': 0},
        'ImgScaleFactor-RB':   {'type': 'float', 'value': 1, 'prec': 6,
                                'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': 0, 'low': 0,
                                'lolo': 0},
        'ImgCenterOffsetX-SP': {'type': 'float', 'value': 0, 'prec': 6,
                                'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': -1000000,
                                'low': -1000000, 'lolo': -1000000},
        'ImgCenterOffsetX-RB': {'type': 'float', 'value': 0, 'prec': 6,
                                'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': -1000000,
                                'low': -1000000, 'lolo': -1000000},
        'ImgCenterOffsetY-SP': {'type': 'float', 'value': 0, 'prec': 6,
                                'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': -1000000,
                                'low': -1000000, 'lolo': -1000000},
        'ImgCenterOffsetY-RB': {'type': 'float', 'value': 0, 'prec': 6,
                                'hihi': 1000000, 'high': 1000000,
                                'hilim': 1000000, 'lolim': -1000000,
                                'low': -1000000, 'lolo': -1000000},
    }
    return pvs_database
