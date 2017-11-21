"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_TL = None
_PREFIX = None


def select_ioc(transport_line):
    """Select IOC to build database for."""
    global _TL, _PREFIX
    _TL = transport_line.upper()
    _PREFIX = _PREFIX_VACA + _TL + '-Glob:AP-PosAng:'


def get_pvs_database():
    """Return IOC database."""
    if _TL is None:
        return {}
    pvs_database = {
        'Version-Cte':          {'type': 'string', 'value': _COMMIT_HASH},

        'Log-Mon':              {'type': 'string', 'value': 'Starting...'},

        'DeltaPosX-SP':         {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mm', 'hilim': 5, 'lolim': -5},
        'DeltaPosX-RB':         {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mm'},
        'DeltaAngX-SP':         {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mrad', 'hilim': 4, 'lolim': -4},
        'DeltaAngX-RB':         {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mrad'},

        'DeltaPosY-SP':         {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mm', 'hilim': 5, 'lolim': -5},
        'DeltaPosY-RB':         {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mm'},
        'DeltaAngY-SP':         {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mrad', 'hilim': 4, 'lolim': -4},
        'DeltaAngY-RB':         {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mrad'},

        'RespMatConfigName-SP': {'type': 'string', 'value': ''},
        'RespMatConfigName-RB': {'type': 'string', 'value': ''},
        'RespMatX-Mon':         {'type': 'float', 'value': 4*[0], 'prec': 3,
                                 'count': 4},
        'RespMatY-Mon':         {'type': 'float', 'value': 4*[0], 'prec': 3,
                                 'count': 4},

        'CH1RefKick-Mon':       {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mrad'},
        'CH2RefKick-Mon':       {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mrad'},
        'CV1RefKick-Mon':       {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mrad'},
        'CV2RefKick-Mon':       {'type': 'float', 'value': 0, 'prec': 6,
                                 'unit': 'mrad'},
        'SetNewRef-Cmd':        {'type': 'int', 'value': 0},

        'ConfigPS-Cmd':         {'type': 'int', 'value': 0},

        'Status-Mon':           {'type': 'int', 'value': 0},
        'Status-Cte':           {'type': 'string', 'count': 4, 'value':
                                 ('PS Connection', 'PS PwrState',
                                  'PS OpMode', 'PS CtrlMode')},
    }
    return pvs_database
