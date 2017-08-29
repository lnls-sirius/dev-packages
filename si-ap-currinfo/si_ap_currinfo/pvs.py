"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_DEVICE = 'SI-Glob:AP-CurrInfo:'
_PREFIX = _PREFIX_VACA + _DEVICE
_INFO = None


def select_ioc(info):
    """Select IOC to build database for."""
    global _INFO
    _INFO = info.lower()


def get_pvs_database():
    """Return IOC database."""
    if _INFO == 'current':
        pvs_database = {
            'Version-Cte':        {'type': 'string', 'value': _COMMIT_HASH},
            'Current-Mon':        {'type': 'float', 'value': 0.0, 'prec': 2,
                                   'unit': 'mA'},
            'StoredEBeam-Mon':    {'type': 'enum', 'value': 0,
                                   'enums': ['False', 'True']},
            'DCCT-Sel':           {'type': 'enum', 'value': 0,
                                   'enums': ['Avg', '13C4', '14C4']},
            'DCCT-Sts':           {'type': 'enum', 'value': 0,
                                   'enums': ['Avg', '13C4', '14C4']},
            'DCCTFltCheck-Sel':   {'type': 'enum', 'value': 0,
                                   'enums': ['On', 'Off']},
            'DCCTFltCheck-Sts':   {'type': 'enum', 'value': 0,
                                   'enums': ['On', 'Off']},
        }
    elif _INFO == 'lifetime':
        pvs_database = {
            'Version-Cte':        {'type': 'string', 'value': _COMMIT_HASH},
            'Lifetime-Mon':       {'type': 'float', 'value': 0.0, 'prec': 0,
                                   'unit': 's'},
            'BuffSizeMax-SP':	  {'type': 'int', 'value': 0},
            'BuffSizeMax-RB':	  {'type': 'int', 'value': 0},
            'BuffSize-Mon':	      {'type': 'int', 'value': 0},
            'SplIntvl-SP':	      {'type': 'int', 'value': 10, 'unit': 's'},
            'SplIntvl-RB':	      {'type': 'int', 'value': 10, 'unit': 's'},
            'BuffRst-Cmd':        {'type': 'int', 'value': 0},
            'BuffAutoRst-Sel':    {'type': 'enum', 'value': 0,
                                   'enums': ['PVsTrig', 'DCurrCheck', 'Off']},
            'BuffAutoRst-Sts':    {'type': 'enum', 'value': 0,
                                   'enums': ['PVsTrig', 'DCurrCheck', 'Off']},
            'DCurrFactor-Cte':    {'type': 'float', 'value': 0.003, 'prec': 2,
                                   'unit': 'mA'}
        }
    elif _INFO == 'charge':
        pvs_database = {
            'Version-Cte':        {'type': 'string', 'value': _COMMIT_HASH},
            'Charge-Mon':         {'type': 'float', 'value': 0.0, 'prec': 10,
                                   'unit': 'A.h'},
            'ChargeCalcIntvl-SP': {'type': 'float', 'value': 100.0, 'prec': 1,
                                   'unit': 's'},
            'ChargeCalcIntvl-RB': {'type': 'float', 'value': 100.0, 'prec': 1,
                                   'unit': 's'},
        }
    return pvs_database
