"""Define PVs, constants and properties of SI AP Manaca IOC."""
from .. import csdev as _csdev


# --- Enumeration Types ---
class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    MEASURESTATE = ('Stopped', 'Measuring')


_et = ETypes  # syntactic sugar


# --- Const class ---
class Const(_csdev.Const):
    """Const class defining constants."""

    DEF_COEFX = 10.00 * 1e-3  # [mm/px] (source: Sergio Lordano from OPT)
    DEF_COEFY = 10.04 * 1e-3  # [mm/px] (source: Sergio Lordano from OPT)
    DEF_ROISIZE = 150
    DEF_ROICENTERX = 850
    DEF_ROICENTERY = 750
    TARGETX = 372  # [px] source: Lucas Sanfelici via email
    TARGETY = 720  # [px] source: Lucas Sanfelici via email
    DIST_FROM_SRC = 30.160  # [m] source: Sergio Lordano from OPT
    DEF_PROFILE = 'MNC:A:BASLER02:'
    DEF_RATE = 2  # [Hz]
    IP_IOC = '10.31.74.45'
    PREFIX_IOC = 'SI-09SABL:AP-Manaca-MVS2:'

    MeasureState = _csdev.Const.register('MeasureState', _et.MEASURESTATE)

    @classmethod
    def get_database(cls, prefix=''):
        """Return IOC database."""
        dbase = {
            'MeasureCtrl-Sel': {
                'type': 'enum', 'value': cls.MeasureState.Stopped,
                'enums': cls.MeasureState._fields},
            'MeasureCtrl-Sts': {
                'type': 'enum', 'value': cls.MeasureState.Stopped,
                'enums': cls.MeasureState._fields},
            'MeasureRate-SP': {
                'type': 'float', 'prec': 4, 'unit': 'Hz',
                'value': cls.DEF_RATE, 'lolim': 0.1, 'hilim': 30},
            'MeasureRate-RB': {
                'type': 'float', 'prec': 4, 'unit': 'Hz',
                'value': cls.DEF_RATE, 'lolim': 0.1, 'hilim': 30},
            'TargetPosX-SP': {
                'type': 'int', 'value': cls.TARGETX, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'TargetPosX-RB': {
                'type': 'int', 'value': cls.TARGETX, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'TargetPosY-SP': {
                'type': 'int', 'value': cls.TARGETY, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'TargetPosY-RB': {
                'type': 'int', 'value': cls.TARGETY, 'unit': 'px',
                'lolim': 0, 'hilim': cls.MAX_WIDTH},
            'SOFBBumpX-Mon': {
                'type': 'float', 'prec': 3, 'unit': 'urad',
                'value': 0.0, 'lolim': -100, 'hilim': 100},
            'SOFBBumpY-Mon': {
                'type': 'float', 'prec': 3, 'unit': 'urad',
                'value': 0.0, 'lolim': -100, 'hilim': 100},
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
            dbase = {prefix + k: v for k, v in dbase.items()}
        dbase.update(_csdev.Const.get_database(prefix=prefix))

        dbase[prefix+'ImgFlipY-Sel']['value'] = cls.ImgFlip.Off
        dbase[prefix+'ImgFlipY-Sts']['value'] = cls.ImgFlip.Off
        dbase[prefix+'ImgFlipX-Sel']['value'] = cls.ImgFlip.On
        dbase[prefix+'ImgFlipX-Sts']['value'] = cls.ImgFlip.On
        dbase[prefix+'ROISizeX-SP']['value'] = cls.DEF_ROISIZE
        dbase[prefix+'ROISizeX-RB']['value'] = cls.DEF_ROISIZE
        dbase[prefix+'ROISizeY-SP']['value'] = cls.DEF_ROISIZE
        dbase[prefix+'ROISizeY-RB']['value'] = cls.DEF_ROISIZE
        dbase[prefix+'ROICenterX-SP']['value'] = cls.DEF_ROICENTERX
        dbase[prefix+'ROICenterX-RB']['value'] = cls.DEF_ROICENTERX
        dbase[prefix+'ROICenterY-SP']['value'] = cls.DEF_ROICENTERY
        dbase[prefix+'ROICenterY-RB']['value'] = cls.DEF_ROICENTERY
        dbase[prefix+'ROIAutoCenter-Sel']['value'] = cls.AutoCenter.Manual
        dbase[prefix+'ROIAutoCenter-Sts']['value'] = cls.AutoCenter.Manual
        dbase[prefix+'CalcMethod-Sel']['value'] = cls.Method.Moments
        dbase[prefix+'CalcMethod-Sts']['value'] = cls.Method.Moments

        dbase.pop(prefix + 'Px2mmScaleX-SP')
        info = dbase.pop(prefix + 'Px2mmScaleX-RB')
        info['value'] = cls.DEF_COEFX
        dbase[prefix + 'Px2mmScaleX-Cte'] = info

        dbase.pop(prefix + 'Px2mmScaleY-SP')
        info = dbase.pop(prefix + 'Px2mmScaleY-RB')
        info['value'] = cls.DEF_COEFY
        dbase[prefix + 'Px2mmScaleY-Cte'] = info
        return dbase
