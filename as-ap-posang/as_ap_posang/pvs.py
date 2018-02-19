"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util


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
    global _TL
    return _TL


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
    global _COMMIT_HASH
    pvs_database = {
        'Version-Cte':       {'type': 'string', 'value': _COMMIT_HASH},

        'Log-Mon':           {'type': 'string', 'value': 'Starting...'},

        'DeltaPosX-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm', 'hilim': 5, 'lolim': -5},
        'DeltaPosX-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm'},
        'DeltaAngX-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad', 'hilim': 4, 'lolim': -4},
        'DeltaAngX-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},

        'DeltaPosY-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm', 'hilim': 5, 'lolim': -5},
        'DeltaPosY-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm'},
        'DeltaAngY-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad', 'hilim': 4, 'lolim': -4},
        'DeltaAngY-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},

        'ConfigName-SP':     {'type': 'string', 'value': ''},
        'ConfigName-RB':     {'type': 'string', 'value': ''},
        'RespMatX-Mon':      {'type': 'float', 'value': 4*[0], 'prec': 3,
                              'count': 4},
        'RespMatY-Mon':      {'type': 'float', 'value': 4*[0], 'prec': 3,
                              'count': 4},

        'RefKickCH1-Mon':    {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},
        'RefKickCH2-Mon':    {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},
        'RefKickCV1-Mon':    {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},
        'RefKickCV2-Mon':    {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},
        'SetNewRefKick-Cmd': {'type': 'int', 'value': 0},

        'ConfigMA-Cmd':   {'type': 'int', 'value': 0},

        'Status-Mon':     {'type': 'int', 'value': 0xf},
        'Status-Cte':     {'type': 'string', 'count': 4, 'value':
                           ('MA Connection', 'MA PwrState',
                            'MA OpMode', 'MA CtrlMode')},
    }
    return pvs_database


def print_banner_and_save_pv_list():
    """Print Soft IOC banner."""
    global _TL, _PREFIX, _COMMIT_HASH, _DEVICE, _PREFIX_VACA
    _util.print_ioc_banner(
        ioc_name=_TL + '-AP-PosAng',
        db=get_pvs_database(),
        description=_TL+'-AP-PosAng Soft IOC',
        version=_COMMIT_HASH,
        prefix=_PREFIX)
    _util.save_ioc_pv_list(_TL.lower()+'-ap-posang',
                           (_DEVICE, _PREFIX_VACA),
                           get_pvs_database())
