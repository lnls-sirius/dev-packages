"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util
from siriuspy.csdevice.currinfo import get_lifetime_database as _get_database


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
    return _ACC


def get_pvs_vaca_prefix():
    """Return Soft IOC vaca prefix."""
    return _PREFIX_VACA


def get_pvs_prefix():
    """Return Soft IOC prefix."""
    return _PREFIX


def get_pvs_database():
    """Return IOC database."""
    pvs_database = _get_database()
    pvs_database['Version-Cte']['value'] = _COMMIT_HASH
    return pvs_database


def print_banner():
    """Print Soft IOC banner."""
    _util.print_ioc_banner(
        ioc_name=_ACC.lower()+'-ap-currinfo-lifetime',
        db=get_pvs_database(),
        description=_ACC.upper()+'-AP-CurrInfo-Lifetime Soft IOC',
        version=_COMMIT_HASH,
        prefix=_PREFIX)
