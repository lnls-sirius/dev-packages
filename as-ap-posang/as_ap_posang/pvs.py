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
    """Return IOC dagtabase."""
    if _TL is None:
        return {}
    pvs_database = {
        'Version-Cte': {'type': 'string', 'value': _COMMIT_HASH},
        'OrbXDeltaPos-SP': {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mm', 'hilim': 5, 'lolim': -5},
        'OrbXDeltaPos-RB': {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mm'},
        'OrbXDeltaAng-SP': {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mrad', 'hilim': 4, 'lolim': -4},
        'OrbXDeltaAng-RB': {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mrad'},
        'OrbXRespMat':     {'type': 'float', 'count': 4, 'value': 4*[0],
                            'prec': 3},
        'OrbYDeltaPos-SP': {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mm', 'hilim': 5, 'lolim': -5},
        'OrbYDeltaPos-RB': {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mm'},
        'OrbYDeltaAng-SP': {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mrad', 'hilim': 4, 'lolim': -4},
        'OrbYDeltaAng-RB': {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mrad'},
        'OrbYRespMat':     {'type': 'float', 'count': 4, 'value': 4*[0],
                            'prec': 3},
        'CH1KickRef-Mon':  {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mrad'},
        'CH2KickRef-Mon':  {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mrad'},
        'CV1KickRef-Mon':  {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mrad'},
        'CV2KickRef-Mon':  {'type': 'float', 'count': 1, 'value': 0, 'prec': 3,
                            'unit': 'mrad'},
        'SetNewRef':       {'type': 'int',   'count': 1, 'value': 0},
    }
    return pvs_database
