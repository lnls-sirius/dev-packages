"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util
from siriuspy.csdevice.posang import get_posang_database as _get_database


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_TL = None
_DEVICE = None
_PREFIX = None


def select_ioc(transport_line):
    """Select IOC to build database for."""
    global _TL, _PREFIX, _DEVICE, _PREFIX_VACA
    _TL = transport_line.upper()
    _DEVICE = _TL + '-Glob:AP-PosAng:'
    _PREFIX = _PREFIX_VACA + _DEVICE


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
    pvs_database = _get_database()
    pvs_database['Version-Cte']['value'] = _COMMIT_HASH
    return pvs_database


def print_banner_and_save_pv_list():
    """Print Soft IOC banner."""
    _util.print_ioc_banner(
        ioc_name=_TL + '-AP-PosAng',
        db=get_pvs_database(),
        description=_TL+'-AP-PosAng Soft IOC',
        version=_COMMIT_HASH,
        prefix=_PREFIX)
    _util.save_ioc_pv_list(_TL.lower()+'-ap-posang',
                           (_DEVICE, _PREFIX_VACA),
                           get_pvs_database())
