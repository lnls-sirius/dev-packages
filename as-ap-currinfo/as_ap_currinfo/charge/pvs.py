"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_DEVICE = 'SI-Glob:AP-CurrInfo:'
_PREFIX = _PREFIX_VACA + _DEVICE


def get_pvs_vaca_prefix():
    """Return Soft IOC vaca prefix."""
    global _PREFIX_VACA
    return _PREFIX_VACA


def get_pvs_prefix():
    """Return Soft IOC prefix."""
    global _PREFIX
    return _PREFIX


def get_pvs_database():
    """Return Soft IOC database."""
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


def print_banner_and_save_pv_list():
    """Print Soft IOC banner."""
    global _COMMIT_HASH, _PREFIX_VACA, _DEVICE, _PREFIX
    _util.print_ioc_banner(
        ioc_name='si-ap-currinfo-charge',
        db=get_pvs_database(),
        description='SI-AP-CurrInfo-Charge Soft IOC',
        version=_COMMIT_HASH,
        prefix=_PREFIX)
    _util.save_ioc_pv_list('si-ap-currinfo-charge',
                           (_DEVICE, _PREFIX_VACA),
                           get_pvs_database())
