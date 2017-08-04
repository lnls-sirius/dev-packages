import siriuspy as _siriuspy

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

pvs_database = {}

pvs_database['TS-Glob:AP-PosAng:'] = {

    'Version-Cte': {'type':'string', 'value':__version__},

    'OrbXDeltaPos-SP': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mm', 'hilim': 5, 'lolim': -5},
    'OrbXDeltaPos-RB': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mm'},
    'OrbXDeltaAng-SP': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad', 'hilim': 4, 'lolim': -4},
    'OrbXDeltaAng-RB': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'OrbXRespMat'    : {'type':'float', 'count': 4, 'value': 4*[0], 'prec': 3},
    'OrbYDeltaPos-SP': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mm', 'hilim': 5, 'lolim': -5},
    'OrbYDeltaPos-RB': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mm'},
    'OrbYDeltaAng-SP': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad', 'hilim': 4, 'lolim': -4},
    'OrbYDeltaAng-RB': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'OrbYRespMat'    : {'type':'float', 'count': 4, 'value': 4*[0], 'prec': 3},
    'CH1KickRef-Mon' : {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'CH2KickRef-Mon' : {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'CV1KickRef-Mon' : {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'CV2KickRef-Mon' : {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'SetNewRef'      : {'type':'int',   'count': 1, 'value': 0},
}
