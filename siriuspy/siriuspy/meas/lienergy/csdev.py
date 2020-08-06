"""Define PVs, constants and properties of LIEnergyMeas IOC."""
import numpy as _np

from .. import csdev as _csdev


# --- Enumeration Types ---
class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    MEASURESTATE = ('Stopped', 'Measuring')


_et = ETypes  # syntactic sugar


# --- Const class ---
class Const(_csdev.Const):
    """Const class defining constants."""

    DEFAULT_DISP = 1087  # in mm
    DEFAULT_B_ANG = _np.pi/4
    DEFAULT_SPECT = 'LI-01:PS-Spect'
    DEFAULT_PROFILE = 'LA-BI:PRF4'

    MeasureState = _csdev.Const.register('MeasureState', _et.MEASURESTATE)

    @classmethod
    def get_database(cls, prefix=''):
        """Return IOC database."""
        dbase = {
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
        dbase2 = _csdev.Const.get_database(prefix=prefix)
        dbase2[prefix+'ImgFlipY-Sel']['value'] = cls.ImgFlip.Off
        dbase2[prefix+'ImgFlipY-Sts']['value'] = cls.ImgFlip.Off
        dbase2[prefix+'ImgFlipX-Sel']['value'] = cls.ImgFlip.On
        dbase2[prefix+'ImgFlipX-Sts']['value'] = cls.ImgFlip.On
        dbase.update(dbase2)
        return dbase
