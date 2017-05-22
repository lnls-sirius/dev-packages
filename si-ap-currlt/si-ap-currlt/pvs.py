import siriuspy

with open('VERSION','r') as _f:
    __version__ = _f.read().strip()

pvs_database = {

    'Version': {'type':'string', 'value':__version__, 'scan': 0.02},

    'Current-Mon':    {'type': 'float', 'count': 1, 'value': 0.0, 'prec': 3, 'unit': 'mA', 'scan': 0.1},
    'Lifetime-Mon':   {'type': 'float', 'count': 1, 'value': 0.0, 'prec': 0, 'unit': 's'},
    'SplNr-Sel':	  {'type': 'int',	'count': 1, 'value': 100 },
    'SplNr-Sts':	  {'type': 'int',	'count': 1, 'value': 100 },
    'TotTs':		  {'type': 'int', 'count': 1, 'value': 10.0, 'unit': 's'  },
    'DCCT-Sel':		  {'type': 'enum',  'count': 1, 'value': 0, 'enums': ['13C4','14C4','Avg'] },
    'DCCT-Sts':		  {'type': 'enum',  'count': 1, 'value': 0, 'enums': ['13C4','14C4','Avg'] },
    'DeltaCurrMinLT': {'type': 'float', 'count': 1, 'value': 60.0, 'prec': 1, 'unit': 's'},
    'RstBuffLT':      {'type': 'int',   'count': 1, 'value': 0}
}
