import siriuspy as _siriuspy

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

pvs_database = {}

pvs_database['TS-Glob:AP-PosAng:'] = {

    'Version-Cte': {'type':'string', 'value':__version__},

    'DeltaPosX-SP':   {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mm', 'hilim': 5, 'lolim': -5},
    'DeltaPosX-RB':   {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mm'},
    'DeltaAngX-SP':   {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad', 'hilim': 4, 'lolim': -4},
    'DeltaAngX-RB':   {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'RespMatX-Cte':   {'type':'float', 'count': 4, 'value': 4*[0], 'prec': 3},
    'DeltaPosY-SP':   {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mm', 'hilim': 5, 'lolim': -5},
    'DeltaPosY-RB':   {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mm'},
    'DeltaAngY-SP':   {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad', 'hilim': 4, 'lolim': -4},
    'DeltaAngY-RB':   {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'RespMatY-Cte':   {'type':'float', 'count': 4, 'value': 4*[0], 'prec': 3},
    'CH1KickRef-Mon': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'CH2KickRef-Mon': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'CV1KickRef-Mon': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'CV2KickRef-Mon': {'type':'float', 'count': 1, 'value': 0, 'prec': 3, 'unit': 'mrad'},
    'SetNewRef-Cmd' : {'type':'int',   'count': 1, 'value': 0},
}
