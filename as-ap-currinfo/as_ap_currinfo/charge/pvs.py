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
        'Charge-Mon':         {'type': 'float', 'value': 0.0, 'prec': 10,
                               'unit': 'A.h'},
        'ChargeCalcIntvl-SP': {'type': 'float', 'value': 100.0, 'prec': 1,
                               'unit': 's'},
        'ChargeCalcIntvl-RB': {'type': 'float', 'value': 100.0, 'prec': 1,
                               'unit': 's'},
    }
    return pvs_database
