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


def get_pvs_section():
    """Return Soft IOC transport line."""
    global _ACC
    return _ACC


def get_pvs_vaca_prefix():
    """Return Soft IOC vaca prefix."""
    global _PREFIX_VACA
    return _PREFIX_VACA


def get_pvs_prefix():
    """Return Soft IOC prefix."""
    global _PREFIX
    return _PREFIX


def get_pvs_database():
    """Return IOC database."""
    global _ACC, _COMMIT_HASH

    pvs_database = {
        'Version-Cte':     {'type': 'string', 'value': _COMMIT_HASH},
        'Current-Mon':     {'type': 'float', 'value': 0.0, 'prec': 3,
                            'unit': 'mA'},
        'StoredEBeam-Mon': {'type': 'enum', 'value': 0,
                            'enums': ['False', 'True']},
    }

    if _ACC == 'SI':
        pvs_database['DCCT-Sel'] = {'type': 'enum', 'value': 0,
                                    'enums': ['Avg', '13C4', '14C4']}
        pvs_database['DCCT-Sts'] = {'type': 'enum', 'value': 0,
                                    'enums': ['Avg', '13C4', '14C4']}
        pvs_database['DCCTFltCheck-Sel'] = {'type': 'enum', 'value': 1,
                                            'enums': ['Off', 'On']}
        pvs_database['DCCTFltCheck-Sts'] = {'type': 'enum', 'value': 1,
                                            'enums': ['Off', 'On']}
    return pvs_database


def print_banner_and_save_pv_list():
    """Print Soft IOC banner."""
    global _COMMIT_HASH, _PREFIX_VACA, _ACC, _DEVICE, _PREFIX
    _util.print_ioc_banner(
        ioc_name=_ACC.lower()+'-ap-currinfo-current',
        db=get_pvs_database(),
        description=_ACC.upper()+'-AP-CurrInfo-Current Soft IOC',
        version=_COMMIT_HASH,
        prefix=_PREFIX)
    _util.save_ioc_pv_list(
        _ACC.lower()+'-ap-currinfo-current',
        (_DEVICE, _PREFIX_VACA),
        get_pvs_database())
