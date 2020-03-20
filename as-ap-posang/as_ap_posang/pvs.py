"""Create IOC Database."""

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy import util as _util
from siriuspy.csdevice.posang import get_posang_database as _get_database


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_TL = None
_DEVICE = None
_PREFIX = None
_CORRSTYPE = None


def select_ioc(transport_line, corrs_type):
    """Select IOC to build database for."""
    global _TL, _PREFIX, _DEVICE, _PREFIX_VACA, _CORRSTYPE
    _TL = transport_line.upper()
    _DEVICE = _TL + '-Glob:AP-PosAng:'
    _PREFIX = _PREFIX_VACA + _DEVICE
    _CORRSTYPE = corrs_type


def get_corrs_type():
    """Return type of horizontal correctors."""
    return _CORRSTYPE


def get_pvs_section():
    """Return Soft IOC transport line."""
    return _TL


def get_pvs_vaca_prefix():
    """Return Soft IOC vaca prefix."""
    return _PREFIX_VACA


def get_pvs_prefix():
    """Return Soft IOC prefix."""
    return _PREFIX


def get_pvs_database():
    """Return Soft IOC database."""
    pvs_database = _get_database(_TL, corrs_type=_CORRSTYPE)
    pvs_database['Version-Cte']['value'] = _COMMIT_HASH
    return pvs_database


def print_banner():
    """Print Soft IOC banner."""
    _util.print_ioc_banner(
        ioc_name=_TL + '-AP-PosAng',
        db=get_pvs_database(),
        description=_TL+'-AP-PosAng Soft IOC',
        version=_COMMIT_HASH,
        prefix=_PREFIX)
