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
    pvs_database = {
        'Version-Cte':     {'type': 'string', 'value': _COMMIT_HASH},
        'Lifetime-Mon':    {'type': 'float', 'value': 0.0, 'prec': 0,
                            'unit': 's'},
        'BuffSizeMax-SP':  {'type': 'int', 'lolim': 0, 'hilim': 360000,
                            'value': 0},
        'BuffSizeMax-RB':  {'type': 'int', 'value': 0},
        'BuffSize-Mon':	   {'type': 'int', 'value': 0},
        'SplIntvl-SP':     {'type': 'int', 'unit': 's',  'lolim': 0,
                            'hilim': 360000, 'low': 0, 'high': 3600,
                            'lolo': 0, 'hihi': 3600, 'value': 10},
        'SplIntvl-RB':	   {'type': 'int', 'value': 10, 'unit': 's'},
        'BuffRst-Cmd':     {'type': 'int', 'value': 0},
        'BuffAutoRst-Sel': {'type': 'enum', 'value': 1,
                            'enums': ['PVsTrig', 'DCurrCheck', 'Off']},
        'BuffAutoRst-Sts': {'type': 'enum', 'value': 1,
                            'enums': ['PVsTrig', 'DCurrCheck', 'Off']},
        'DCurrFactor-Cte': {'type': 'float', 'value': 0.003, 'prec': 2,
                            'unit': 'mA'}
    }
    return pvs_database


def print_banner_and_save_pv_list():
    """Print Soft IOC banner."""
    global _COMMIT_HASH, _PREFIX_VACA, _ACC, _DEVICE, _PREFIX
    _util.print_ioc_banner(
        ioc_name=_ACC.lower()+'-ap-currinfo-lifetime',
        db=get_pvs_database(),
        description=_ACC.upper()+'-AP-CurrInfo-Lifetime Soft IOC',
        version=_COMMIT_HASH,
        prefix=_PREFIX)
    _util.save_ioc_pv_list(
        _ACC.lower()+'-ap-currinfo-lifetime',
        (_DEVICE, _PREFIX_VACA),
        get_pvs_database())
