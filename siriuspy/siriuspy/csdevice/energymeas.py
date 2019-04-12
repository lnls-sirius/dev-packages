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

    METHOD = ('GaussFit', 'Moments')
    MEAS_STATE = _cutil.ETypes.OFF_ON
    AUTO_CENTER = ('Manual', 'Auto')
    BG_CTRL = ('Acquire', 'Reset')
    BG_USAGE = ('NotUsing', 'Using')


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_cutil.Const):
    """Const class defining constants."""

    AutoCenter = _cutil.Const.register('AutoCenter', _et.AUTO_CENTER)
    BgCtrl = _cutil.Const.register('BgCtrl', _et.BG_CTRL)
    BgUsage = _cutil.Const.register('BgUsage', _et.BG_USAGE)


# --- Database classes ---

class EnergyMeas(Const):
    """class for energy measurement."""

    def __init__(self):
        """Init method."""

    def get_database(self, prefix=''):
        """Return IOC database."""
        db = {
            'Log-Mon': {'type': 'char', 'value': '', 'count': 200},
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
                'type': 'enum', 'value': self.AutoCenter.Auto,
                'enums': self.AutoCenter._fields},
            'AutoCenter-Sts': {
                'type': 'enum', 'value': self.AutoCenter.Auto,
                'enums': self.AutoCenter._fields},
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
                'type': 'enum', 'value': self.AutoCenter.Auto,
                'enums': self.AutoCenter._fields},
            'BgUsage-Sel': {
                'type': 'enum', 'value': self.BgUsage.NotUsing,
                'enums': self.BgUsage._fields},
            'BgUsage-Sts': {
                'type': 'enum', 'value': self.BgUsage.NotUsing,
                'enums': self.BgUsage._fields},
            'Energy-Mon': {
                'type': 'float', 'prec': 2, 'unit': 'MeV', 'value': 0},
            'Spread-Mon': {
                'type': 'float', 'prec': 4, 'unit': '%', 'value': 0},
            }
        return self._add_prefix(db, prefix)

    def _add_prefix(self, db, prefix):
        if prefix:
            return {prefix + k: v for k, v in db.items()}
        return db
