"""Define PVs, constants and properties of OrbitCorr SoftIOCs."""
import os as _os
from copy import deepcopy as _dcopy
from siriuspy.util import get_namedtuple as _get_namedtuple
import siriuspy.csdevice.bpms as _csbpm
from siriuspy.csdevice import util as _cutil
from siriuspy.csdevice import timesys as _cstiming
from siriuspy.search import MASearch as _MASearch, BPMSearch as _BPMSearch, \
    LLTimeSearch as _TISearch, HLTimeSearch as _HLTISearch


# --- Enumeration Types ---

class ETypes(_cutil.ETypes):
    """Local enumerate types."""

    READINGORDER = ('CLike', 'FortranLike')
    METHOD = ('GaussFit', 'Moments')
    MEAS_STATE = _cutil.ETypes.OFF_ON
    AUTO_CENTER = ('Manual', 'Auto')
    BG_CTRL = ('Acquire', 'Reset')
    BG_USAGE = ('NotUsing', 'Using')
    CROPIDX = ('Low', 'High')
    FITPARAMS = ('Amp', 'Cen', 'Sig', 'Off')
    PLANE = ('X', 'Y')


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_cutil.Const):
    """Const class defining constants."""

    ReadingOrder = _cutil.Const.register('ReadingOrder', _et.READINGORDER)
    Method = _cutil.Const.register('Method', _et.METHOD)
    AutoCenter = _cutil.Const.register('AutoCenter', _et.AUTO_CENTER)
    BgCtrl = _cutil.Const.register('BgCtrl', _et.BG_CTRL)
    BgUsage = _cutil.Const.register('BgUsage', _et.BG_USAGE)
    CropIdx = _cutil.Const.register('CropIdx', _et.CROPIDX)
    FitParams = _cutil.Const.register('FitParams', _et.FITPARAMS)
    Plane = _cutil.Const.register('Plane', _et.PLANE)


# --- Database classes ---

class EnergyMeas(Const):
    """class for energy measurement."""

    @classmethod
    def get_database(cls, prefix=''):
        """Return IOC database."""
        db = {
            'Log-Mon': {'type': 'char', 'value': '', 'count': 200},
            'Width-SP': {
                'type': 'int', 'value': 1024, 'unit': 'px',
                'lolim': 0, 'hilim': 4000},
            'Width-RB': {
                'type': 'int', 'value': 1024, 'unit': 'px',
                'lolim': 0, 'hilim': 4000},
            'ReadingOrder-Sel': {
                'type': 'enum', 'value': cls.ReadingOrder.Auto,
                'enums': cls.ReadingOrder._fields},
            'ReadingOrder-Sel': {
                'type': 'enum', 'value': cls.ReadingOrder.Auto,
                'enums': cls.ReadingOrder._fields},
            'ImgCropLow-SP': {
                'type': 'int', 'value': 0, 'unit': '',
                'lolim': 0, 'hilim': 255},
            'ImgCropLow-RB': {
                'type': 'int', 'value': 0, 'unit': '',
                'lolim': 0, 'hilim': 255},
            'ImgCropHigh-SP': {
                'type': 'int', 'value': 0, 'unit': '',
                'lolim': 0, 'hilim': 255},
            'ImgCropHigh-RB': {
                'type': 'int', 'value': 0, 'unit': '',
                'lolim': 0, 'hilim': 255},
            'ImgCropUse-Sel': {'type': , 'value' , },
            'CalcMethod-Sel': {'type': , 'value' , },
            'ROIAutoCenter-Sel': {'type': , 'value' , },
            'ROICenterX-SP': {'type': , 'value' , },
            'ROICenterY-SP': {'type': , 'value' , },
            'ROISizeX-SP': {'type': , 'value' , },
            'ROISizeY-SP': {'type': , 'value' , },
            'Background-SP': {'type': , 'value' , },
            'BgUse-Sel': {'type': , 'value' , },
            'Px2mmScaleX-SP': {'type': , 'value' , },
            'Px2mmScaleY-SP': {'type': , 'value' , },
            'Px2mmAutoCenter-Sel': {'type': , 'value' , },
            'Px2mmCenterX-SP': {'type': , 'value' , },
            'Px2mmCenterY-SP': {'type': , 'value' , },


            'ROISizeX-SP': {
                'type': 'int', 'value': 0.2, 'unit': 'px',
                'lolim': 0, 'hilim': 4000},
            'ROISizeX-RB': {
                'type': 'int', 'value': 0.2, 'unit': 'px',
                'lolim': 0, 'hilim': 4000},
            'ROISizeY-SP': {
                'type': 'int', 'value': 0.2, 'unit': 'px',
                'lolim': 0, 'hilim': 4000},
            'ROISizeY-RB': {
                'type': 'int', 'value': 0.2, 'unit': 'px',
                'lolim': 0, 'hilim': 4000},
            'AutoCenter-Sel': {
                'type': 'enum', 'value': cls.AutoCenter.Auto,
                'enums': cls.AutoCenter._fields},
            'AutoCenter-Sts': {
                'type': 'enum', 'value': cls.AutoCenter.Auto,
                'enums': cls.AutoCenter._fields},
            'ROICenterX-SP': {
                'type': 'int', 'value': 0.2, 'unit': 'px',
                'lolim': 0, 'hilim': 4000},
            'ROICenterX-RB': {
                'type': 'int', 'value': 0.2, 'unit': 'px',
                'lolim': 0, 'hilim': 4000},
            'ROICenterY-SP': {
                'type': 'int', 'value': 0.2, 'unit': 'px',
                'lolim': 0, 'hilim': 4000},
            'ROICenterY-RB': {
                'type': 'int', 'value': 0.2, 'unit': 'px',
                'lolim': 0, 'hilim': 4000},
            'BgCtrl-Cmd': {
                'type': 'enum', 'value': cls.AutoCenter.Auto,
                'enums': cls.AutoCenter._fields},
            'BgUsage-Sel': {
                'type': 'enum', 'value': cls.BgUsage.NotUsing,
                'enums': cls.BgUsage._fields},
            'BgUsage-Sts': {
                'type': 'enum', 'value': cls.BgUsage.NotUsing,
                'enums': cls.BgUsage._fields},
            'Energy-Mon': {
                'type': 'float', 'prec': 2, 'unit': 'MeV', 'value': 0},
            'Spread-Mon': {
                'type': 'float', 'prec': 4, 'unit': '%', 'value': 0},
            }
        return cls._add_prefix(db, prefix)

    def _add_prefix(cls, db, prefix):
        if prefix:
            return {prefix + k: v for k, v in db.items()}
        return db
