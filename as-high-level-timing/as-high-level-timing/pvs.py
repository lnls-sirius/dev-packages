import siriuspy as _siriuspy

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

pvs_database = {}

pvs_database['TEST-'] = {

    'Version-Cte': {'type':'string', 'value':__version__},

    'PV1': {'type':'float', 'value': 1.200, 'prec': 3, 'unit': 'm'},
    'PV2': {'type':'string', 'value': 'test'},
}
