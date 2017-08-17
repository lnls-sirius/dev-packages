"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_PREFIX = 'SI-Glob:AP-CurrInfo:'


def get_pvs_database():
    """Return IOC database."""
    pvs_database = {
        'Version':        {'type': 'string', 'value': _COMMIT_HASH,
                           'scan': 0.02},
        'Current-Mon':    {'type': 'float', 'count': 1, 'value': 0.0,
                           'prec': 3, 'unit': 'mA'},
        'CurrLT-Mon':     {'type': 'float', 'count': 1, 'value': 0.0,
                           'prec': 0, 'unit': 's'},
        'SplNr-Sel':	  {'type': 'int',	'count': 1, 'value': 100},
        'SplNr-Sts':	  {'type': 'int',	'count': 1, 'value': 100},
        'TotTs':		  {'type': 'int',   'count': 1, 'value': 10.0, 'unit': 's'},
        'DCCT-Sel':		  {'type': 'enum',  'count': 1, 'value': 0, 'enums': [
                           '13C4', '14C4', 'Avg']},
        'DCCT-Sts':		  {'type': 'enum',  'count': 1, 'value': 0, 'enums': [
                           '13C4', '14C4', 'Avg']},
        'DeltaCurrMinLT': {'type': 'float', 'count': 1, 'value': 100.0,
                           'prec': 1, 'unit': 's'},
        'RstBuffLT':      {'type': 'int',   'count': 1, 'value': 0}
    }
    return pvs_database
