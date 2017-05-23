import siriuspy as _siriuspy

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

pvs_database = {}

pvs_database['TEST-'] = {

    'Version-Cte': {'type':'string', 'value':__version__},
}
