"""Define PVs, constants and properties of Meas IOCs."""
import numpy as _np

from .. import csdev as _csdev


# --- Enumeration Types ---
class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    READINGORDER = ('CLike', 'FortranLike')
    METHOD = ('GaussFit', 'Moments')
    AUTO_CENTER = ('Manual', 'Auto')
    BG_CTRL = ('Acquire', 'Reset')
    BG_USAGE = ('NotUsing', 'Using')
    CROPIDX = ('Low', 'High')
    FLIP = ('Off', 'On')
    FITPARAMS = ('Amp', 'Cen', 'Sig', 'Off')
    PLANES = ('Y', 'X')


_et = ETypes  # syntactic sugar


# --- Const class ---
class Const(_csdev.Const):
    """Const class defining constants."""

    DEFAULT_WIDTH = 1024
    DEFAULT_HEIGHT = 1090
    DEFAULT_ROI_SIZE = 500
    MAX_WIDTH = 3000

    ReadingOrder = _csdev.Const.register('ReadingOrder', _et.READINGORDER)
    Method = _csdev.Const.register('Method', _et.METHOD)
    AutoCenter = _csdev.Const.register('AutoCenter', _et.AUTO_CENTER)
    BgCtrl = _csdev.Const.register('BgCtrl', _et.BG_CTRL)
    BgUsage = _csdev.Const.register('BgUsage', _et.BG_USAGE)
    CropIdx = _csdev.Const.register('CropIdx', _et.CROPIDX)
    ImgFlip = _csdev.Const.register('ImgFlip', _et.FLIP)
    FitParams = _csdev.Const.register('FitParams', _et.FITPARAMS)
    Plane = _csdev.Const.register('Plane', _et.PLANES)

    @classmethod
    def get_database(cls, prefix=''):
        """Return IOC database."""
        dbase = {
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
            'ReadingOrder-Sel': {
                'type': 'enum', 'value': cls.ReadingOrder.CLike,
                'enums': cls.ReadingOrder._fields},
            'ReadingOrder-Sts': {
                'type': 'enum', 'value': cls.ReadingOrder.CLike,
                'enums': cls.ReadingOrder._fields},
            'NrAverages-SP': {
                'type': 'int', 'unit': '#', 'value': 1,
                'lolim': 1, 'hilim': 999},
            'NrAverages-RB': {
                'type': 'int', 'unit': '#', 'value': 1,
                'lolim': 1, 'hilim': 999},
            'ResetBuffer-Cmd': {'type': 'int', 'value': 0},
            'BufferSize-Mon': {'type': 'int', 'value': 0},
            'ImgCropLow-SP': {
                'type': 'int', 'value': 0, 'unit': '',
                'lolim': 0, 'hilim': 2**16},
            'ImgCropLow-RB': {
                'type': 'int', 'value': 0, 'unit': '',
                'lolim': 0, 'hilim': 2**16},
            'ImgCropHigh-SP': {
                'type': 'int', 'value': 2**16, 'unit': '',
                'lolim': 0, 'hilim': 2**16},
            'ImgCropHigh-RB': {
                'type': 'int', 'value': 2**16, 'unit': '',
                'lolim': 0, 'hilim': 2**16},
            'ImgCropUse-Sel': {
                'type': 'enum', 'value': cls.BgUsage.NotUsing,
                'enums': cls.BgUsage._fields},
            'ImgCropUse-Sts': {
                'type': 'enum', 'value': cls.BgUsage.NotUsing,
                'enums': cls.BgUsage._fields},
            'ImgFlipX-Sel': {
                'type': 'enum', 'value': cls.ImgFlip.Off,
                'enums': cls.ImgFlip._fields},
            'ImgFlipX-Sts': {
                'type': 'enum', 'value': cls.ImgFlip.Off,
                'enums': cls.ImgFlip._fields},
            'ImgFlipY-Sel': {
                'type': 'enum', 'value': cls.ImgFlip.Off,
                'enums': cls.ImgFlip._fields},
            'ImgFlipY-Sts': {
                'type': 'enum', 'value': cls.ImgFlip.Off,
                'enums': cls.ImgFlip._fields},
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
            }
        for val in dbase.values():
            low = val.get('lolim', None)
            hig = val.get('hilim', None)
            if low is not None:
                val['lolo'] = low
                val['low'] = low
            if hig is not None:
                val['hihi'] = hig
                val['high'] = hig
        if prefix:
            return {prefix + k: v for k, v in dbase.items()}
        return dbase
