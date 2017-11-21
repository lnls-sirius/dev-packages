"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_DEVICE = 'SI-Glob:AP-CurrInfo:'
_PREFIX = _PREFIX_VACA + _DEVICE


def get_pvs_database():
    """Return IOC database."""
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
    return pvs_database
