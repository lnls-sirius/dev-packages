"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util
from siriuspy.csdevice.opticscorr import (
    Const as _Const,
    get_chrom_database as _get_database)


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_ACC = None
_PREFIX = None
_SFAMS = None
_DEVICE = None


def select_ioc(acc):
    """Select IOC to build database for."""
    global _ACC, _PREFIX, _SFAMS, _DEVICE
    _ACC = acc.upper()
    _DEVICE = _ACC + '-Glob:AP-ChromCorr:'
    _PREFIX = _PREFIX_VACA + _DEVICE
    if _ACC == 'BO':
        _SFAMS = _Const.BO_SFAMS_CHROMCORR
    elif _ACC == 'SI':
        _SFAMS = _Const.SI_SFAMS_CHROMCORR


def get_pvs_section():
    """Return Soft IOC section/accelerator."""
    return _ACC


def get_pvs_vaca_prefix():
    """Return Soft IOC vaca prefix."""
    return _PREFIX_VACA


def get_pvs_prefix():
    """Return Soft IOC prefix."""
    return _PREFIX


def get_corr_fams():
    """Return list of magnet families used on correction."""
    return _SFAMS


def get_pvs_database():
    """Return IOC database."""
    pvs_database = _get_database(_ACC)
    pvs_database['Version-Cte']['value'] = _COMMIT_HASH
    return pvs_database


def print_banner():
    """Print Soft IOC banner."""
    _util.print_ioc_banner(
        ioc_name=_ACC+'-AP-ChromCorr',
        db=get_pvs_database(),
        description=_ACC+'-AP-ChromCorr Soft IOC',
        version=_COMMIT_HASH,
        prefix=_PREFIX)
