"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_ACC = None
_DEVICE = None
_PREFIX = None


def select_ioc(acc):
    """Select IOC to build database for."""
    global _ACC, _PREFIX, _DEVICE
    _ACC = acc.upper()
    _DEVICE = _ACC + '-Glob:AP-CurrInfo:'
    _PREFIX = _PREFIX_VACA + _DEVICE


def get_pvs_database():
    """Return IOC database."""
    global _ACC

    pvs_database = {
        'Version-Cte':        {'type': 'string', 'value': _COMMIT_HASH},
        'Current-Mon':        {'type': 'float', 'value': 0.0, 'prec': 3,
                               'unit': 'mA'},
        'StoredEBeam-Mon':    {'type': 'enum', 'value': 0,
                               'enums': ['False', 'True']},
    }

    if _ACC == 'SI':
        pvs_database['DCCT-Sel'] = {'type': 'enum', 'value': 0,
                                    'enums': ['Avg', '13C4', '14C4']}
        pvs_database['DCCT-Sts'] = {'type': 'enum', 'value': 0,
                                    'enums': ['Avg', '13C4', '14C4']}
        pvs_database['DCCTFltCheck-Sel'] = {'type': 'enum', 'value': 0,
                                            'enums': ['On', 'Off']}
        pvs_database['DCCTFltCheck-Sts'] = {'type': 'enum', 'value': 0,
                                            'enums': ['On', 'Off']}
    return pvs_database
