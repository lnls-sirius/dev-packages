"""Define PVs, constants and properties of OrbitCorr SoftIOCs."""
import numpy as _np

from .. import csdev as _csdev


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    MEASURESTATE = ('Stopped', 'Measuring')
    READINGORDER = ('CLike', 'FortranLike')
    METHOD = ('GaussFit', 'Moments')
    MEAS_STATE = _csdev.ETypes.OFF_ON
    AUTO_CENTER = ('Manual', 'Auto')
    BG_CTRL = ('Acquire', 'Reset')
    BG_USAGE = ('NotUsing', 'Using')
    CROPIDX = ('Low', 'High')
    FITPARAMS = ('Amp', 'Cen', 'Sig', 'Off')
    PLANE = ('Y', 'X')
    FLIP = ('Off', 'On')


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_csdev.Const):
    """Const class defining constants."""

    DEFAULT_DISP = 1087  # in mm
    DEFAULT_B_ANG = _np.pi/4
    DEFAULT_SPECT = 'LI-01:PS-Spect'
    DEFAULT_PROFILE = 'LA-BI:PRF4'
    DEFAULT_WIDTH = 1024
    DEFAULT_HEIGHT = 1090
    DEFAULT_ROI_SIZE = 500
    MAX_WIDTH = 3000

    MeasureState = _csdev.Const.register('MeasureState', _et.MEASURESTATE)
    ReadingOrder = _csdev.Const.register('ReadingOrder', _et.READINGORDER)
    Method = _csdev.Const.register('Method', _et.METHOD)
    AutoCenter = _csdev.Const.register('AutoCenter', _et.AUTO_CENTER)
    BgCtrl = _csdev.Const.register('BgCtrl', _et.BG_CTRL)
    BgUsage = _csdev.Const.register('BgUsage', _et.BG_USAGE)
    CropIdx = _csdev.Const.register('CropIdx', _et.CROPIDX)
    FitParams = _csdev.Const.register('FitParams', _et.FITPARAMS)
    Plane = _csdev.Const.register('Plane', _et.PLANE)
    ImgFlip = _csdev.Const.register('ImgFlip', _et.FLIP)


# --- Database classes ---

class EnergyMeas(Const):
    """class for energy measurement."""

    @classmethod
    def get_database(cls, prefix=''):
        """Return IOC database."""
        db = {
            'Log-Mon': {'type': 'char', 'value': '', 'count': 200},
            'Image-SP': {
                'type': 'int',
                'value': _np.zeros(
                    cls.DEFAULT_WIDTH*cls.DEFAULT_WIDTH, dtype=int),
                'count': cls.MAX_WIDTH*cls.MAX_WIDTH},
            'Image-RB': {
                'type': 'int',
                'value': _np.zeros(
                    cls.DEFAULT_WIDTH*cls.DEFAULT_WIDTH, dtype=int),
                'count': cls.MAX_WIDTH*cls.MAX_WIDTH},
            'Width-SP': {
                'type': 'int', 'value': cls.DEFAULT_WIDTH, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'Width-RB': {
                'type': 'int', 'value': cls.DEFAULT_WIDTH, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            # 'ReadingOrder-Sel': {
            #     'type': 'enum', 'value': cls.ReadingOrder.CLike,
            #     'enums': cls.ReadingOrder._fields},
            # 'ReadingOrder-Sel': {
            #     'type': 'enum', 'value': cls.ReadingOrder.CLike,
            #     'enums': cls.ReadingOrder._fields},
            'ImgCropLow-SP': {
                'type': 'int', 'value': 0, 'unit': '',
                'lolim': 0, 'hilim': 255},
            'ImgCropLow-RB': {
                'type': 'int', 'value': 0, 'unit': '',
                'lolim': 0, 'hilim': 255},
            'ImgCropHigh-SP': {
                'type': 'int', 'value': 255, 'unit': '',
                'lolim': 0, 'hilim': 255},
            'ImgCropHigh-RB': {
                'type': 'int', 'value': 255, 'unit': '',
                'lolim': 0, 'hilim': 255},
            'ImgCropUse-Sel': {
                'type': 'enum', 'value': cls.BgUsage.NotUsing,
                'enums': cls.BgUsage._fields},
            'ImgCropUse-Sts': {
                'type': 'enum', 'value': cls.BgUsage.NotUsing,
                'enums': cls.BgUsage._fields},
            # 'ImgFlipX-Sel': {
            #     'type': 'enum', 'value': cls.ImgFlip.Off,
            #     'enums': cls.ImgFlip._fields},
            # 'ImgFlipX-Sts': {
            #     'type': 'enum', 'value': cls.ImgFlip.Off,
            #     'enums': cls.ImgFlip._fields},
            # 'ImgFlipY-Sel': {
            #     'type': 'enum', 'value': cls.ImgFlip.Off,
            #     'enums': cls.ImgFlip._fields},
            # 'ImgFlipY-Sts': {
            #     'type': 'enum', 'value': cls.ImgFlip.Off,
            #     'enums': cls.ImgFlip._fields},
            'CalcMethod-Sel': {
                'type': 'enum', 'value': cls.Method.GaussFit,
                'enums': cls.Method._fields},
            'CalcMethod-Sts': {
                'type': 'enum', 'value': cls.Method.GaussFit,
                'enums': cls.Method._fields},
            'ROIAutoCenter-Sel': {
                'type': 'enum', 'value': cls.AutoCenter.Auto,
                'enums': cls.AutoCenter._fields},
            'ROIAutoCenter-Sts': {
                'type': 'enum', 'value': cls.AutoCenter.Auto,
                'enums': cls.AutoCenter._fields},
            'ROICenterX-SP': {
                'type': 'int', 'value': 0, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROICenterX-RB': {
                'type': 'int', 'value': 0, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROICenterY-SP': {
                'type': 'int', 'value': 0, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROICenterY-RB': {
                'type': 'int', 'value': 0, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROISizeX-SP': {
                'type': 'int', 'value': cls.DEFAULT_ROI_SIZE, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROISizeX-RB': {
                'type': 'int', 'value': cls.DEFAULT_ROI_SIZE, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROISizeY-SP': {
                'type': 'int', 'value': cls.DEFAULT_ROI_SIZE, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROISizeY-RB': {
                'type': 'int', 'value': cls.DEFAULT_ROI_SIZE, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            # 'Background-SP': {
            #     'type': 'int',
            #     'value': _np.zeros(cls.DEFAULT_WIDTH*cls.DEFAULT_WIDTH),
            #     'count': cls.MAX_WIDTH*cls.MAX_WIDTH},
            # 'Background-RB': {
            #     'type': 'int',
            #     'value': _np.zeros(cls.DEFAULT_WIDTH*cls.DEFAULT_WIDTH),
            #     'count': cls.MAX_WIDTH*cls.MAX_WIDTH},
            # 'BgUse-Sel': {
            #     'type': 'enum', 'value': cls.BgUsage.NotUsing,
            #     'enums': cls.BgUsage._fields},
            # 'BgUse-Sts': {
            #     'type': 'enum', 'value': cls.BgUsage.NotUsing,
            #     'enums': cls.BgUsage._fields},
            'Px2mmScaleX-SP': {
                'type': 'float', 'value': 1, 'prec': 3,
                'unit': 'mm/px', 'lolim': 0, 'hilim': 10},
            'Px2mmScaleX-RB': {
                'type': 'float', 'value': 1, 'prec': 3,
                'unit': 'mm/px', 'lolim': 0, 'hilim': 10},
            'Px2mmScaleY-SP': {
                'type': 'float', 'value': 1, 'prec': 3,
                'unit': 'mm/px', 'lolim': 0, 'hilim': 10},
            'Px2mmScaleY-RB': {
                'type': 'float', 'value': 1, 'prec': 3,
                'unit': 'mm/px', 'lolim': 0, 'hilim': 10},
            'Px2mmAutoCenter-Sel': {
                'type': 'enum', 'value': cls.AutoCenter.Auto,
                'enums': cls.AutoCenter._fields},
            'Px2mmAutoCenter-Sts': {
                'type': 'enum', 'value': cls.AutoCenter.Auto,
                'enums': cls.AutoCenter._fields},
            'Px2mmCenterX-SP': {
                'type': 'int', 'value': 0,
                'unit': 'px', 'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'Px2mmCenterX-RB': {
                'type': 'int', 'value': 0,
                'unit': 'px', 'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'Px2mmCenterY-SP': {
                'type': 'int', 'value': 0,
                'unit': 'px', 'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'Px2mmCenterY-RB': {
                'type': 'int', 'value': 0,
                'unit': 'px', 'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROIStartX-Mon': {
                'type': 'int', 'value': 0, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROIStartY-Mon': {
                'type': 'int', 'value': 0, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROIEndX-Mon': {
                'type': 'int', 'value': cls.DEFAULT_ROI_SIZE, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROIEndY-Mon': {
                'type': 'int', 'value': cls.DEFAULT_ROI_SIZE, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'ROIProjX-Mon': {
                'type': 'int', 'value': _np.zeros(cls.DEFAULT_ROI_SIZE),
                'count': cls.MAX_WIDTH},
            'ROIProjY-Mon': {
                'type': 'int', 'value': _np.zeros(cls.DEFAULT_ROI_SIZE),
                'count': cls.MAX_WIDTH},
            'ROIAxisX-Mon': {
                'type': 'int', 'value': _np.arange(cls.DEFAULT_ROI_SIZE),
                'count': cls.MAX_WIDTH},
            'ROIAxisY-Mon': {
                'type': 'int', 'value': _np.arange(cls.DEFAULT_ROI_SIZE),
                'count': cls.MAX_WIDTH},
            'ROIGaussFitX-Mon': {
                'type': 'float', 'value': 0.0*_np.zeros(cls.DEFAULT_ROI_SIZE),
                'count': cls.MAX_WIDTH},
            'ROIGaussFitY-Mon': {
                'type': 'float', 'value': 0.0*_np.zeros(cls.DEFAULT_ROI_SIZE),
                'count': cls.MAX_WIDTH},
            'BeamCenterX-Mon': {
                'type': 'int', 'value': 1, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'BeamCenterY-Mon': {
                'type': 'int', 'value': 1, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'BeamSizeX-Mon': {
                'type': 'int', 'value': 1, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'BeamSizeY-Mon': {
                'type': 'int', 'value': 1, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'BeamCentermmX-Mon': {
                'type': 'float', 'value': 1, 'prec': 3,
                'unit': 'mm', 'lolim': -20, 'hilim': 20},
            'BeamCentermmY-Mon': {
                'type': 'float', 'value': 1, 'prec': 3,
                'unit': 'mm', 'lolim': -20, 'hilim': 20},
            'BeamSizemmX-Mon': {
                'type': 'float', 'value': 1, 'prec': 3,
                'unit': 'mm', 'lolim': -20, 'hilim': 20},
            'BeamSizemmY-Mon': {
                'type': 'float', 'value': 1, 'prec': 3,
                'unit': 'mm', 'lolim': -20, 'hilim': 20},
            'BeamAmplX-Mon': {
                'type': 'float', 'value': 0, 'prec': 3,
                'unit': 'mm', 'lolim': -20, 'hilim': 20},
            'BeamAmplY-Mon': {
                'type': 'float', 'value': 0, 'prec': 3,
                'unit': 'mm', 'lolim': -20, 'hilim': 20},
            'BeamOffsetX-Mon': {
                'type': 'float', 'value': 0, 'prec': 3,
                'unit': 'mm', 'lolim': -20, 'hilim': 20},
            'BeamOffsetY-Mon': {
                'type': 'float', 'value': 0, 'prec': 3,
                'unit': 'mm', 'lolim': -20, 'hilim': 20},

            'Dispersion-SP': {
                'type': 'float', 'prec': 4, 'unit': 'mm',
                'value': cls.DEFAULT_DISP},
            'Dispersion-RB': {
                'type': 'float', 'prec': 4, 'unit': 'mm',
                'value': cls.DEFAULT_DISP},
            # 'Angle-SP': {
            #     'type': 'float', 'prec': 4, 'unit': 'deg',
            #     'value': cls.DEFAULT_B_ANG},
            # 'Angle-RB': {
            #     'type': 'float', 'prec': 4, 'unit': 'deg',
            #     'value': cls.DEFAULT_B_ANG},
            # 'Spectrometer-SP': {
            #     'type': 'string', 'value': cls.DEFAULT_SPECT},
            # 'Spectrometer-RB': {
            #     'type': 'string', 'value': cls.DEFAULT_SPECT},
            'IntDipole-Mon': {
                'type': 'float', 'prec': 4, 'unit': 'T.m', 'value': 0},
            'Energy-Mon': {
                'type': 'float', 'prec': 2, 'unit': 'MeV', 'value': 0},
            'Spread-Mon': {
                'type': 'float', 'prec': 4, 'unit': '%', 'value': 0},

            'MeasureCtrl-Sel': {
                'type': 'enum', 'value': cls.MeasureState.Stopped,
                'enums': cls.MeasureState._fields},
            'MeasureCtrl-Sts': {
                'type': 'enum', 'value': cls.MeasureState.Stopped,
                'enums': cls.MeasureState._fields},
            }
        for val in db.values():
            low = val.get('lolim', None)
            hig = val.get('hilim', None)
            if low is not None:
                val['lolo'] = low
                val['low'] = low
            if hig is not None:
                val['hihi'] = hig
                val['high'] = hig
        if prefix:
            return {prefix + k: v for k, v in db.items()}
        return db
