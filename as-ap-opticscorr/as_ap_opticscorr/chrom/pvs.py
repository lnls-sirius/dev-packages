"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_ACC = None
_PREFIX = None
_SFAMS = None
_DEVICE = None


def select_ioc(acc):
    """Select IOC to build database for."""
    global _ACC, _PREFIX, _SFAMS, _DEVICE
    _ACC = acc.upper()
    _DEVICE = _ACC + '-Glob:AP-ChromCorr:'
    _PREFIX = _PREFIX_VACA + _DEVICE
    if _ACC == 'BO':
        _SFAMS = ['SF', 'SD']
    elif _ACC == 'SI':
        _SFAMS = ['SFA1', 'SFA2', 'SDA1', 'SDA2', 'SDA3',
                  'SFB1', 'SFB2', 'SDB1', 'SDB2', 'SDB3',
                  'SFP1', 'SFP2', 'SDP1', 'SDP2', 'SDP3']


def get_pvs_database():
    """Return IOC database."""
    global _SFAMS
    corrmat_size = len(_SFAMS)*2

    pvs_database = {
        'Version-Cte':          {'type': 'string', 'value': _COMMIT_HASH},

        'Log-Mon':              {'type': 'string', 'value': 'Starting...'},

        'ChromX-SP':            {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 10, 'lolim': -10},
        'ChromX-RB':            {'type': 'float', 'value': 0, 'prec': 6},
        'ChromY-SP':            {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 10, 'lolim': -10},
        'ChromY-RB':            {'type': 'float', 'value': 0, 'prec': 6},

        'ApplySL-Cmd':          {'type': 'int', 'value': 0},

        'CorrMat-SP':           {'type': 'float', 'count': corrmat_size,
                                 'value': corrmat_size*[0], 'prec': 6, 'unit':
                                 'Chrom x SFams (Matrix of add method)'},
        'CorrMat-RB':           {'type': 'float', 'count': corrmat_size,
                                 'value': corrmat_size*[0], 'prec': 6, 'unit':
                                 'Chrom x SFams (Matrix of add method)'},
        'NominalChrom-SP':      {'type': 'float', 'count': 2, 'value': 2*[0],
                                 'prec': 6},
        'NominalChrom-RB':      {'type': 'float', 'count': 2, 'value': 2*[0],
                                 'prec': 6},
        'NominalSL-SP':         {'type': 'float', 'count': len(_SFAMS),
                                 'value': len(_SFAMS)*[0], 'prec': 6},
        'NominalSL-RB':         {'type': 'float', 'count': len(_SFAMS),
                                 'value': len(_SFAMS)*[0], 'prec': 6},

        'SyncCorr-Sel':         {'type': 'enum', 'value': 0,
                                 'enums': ['Off', 'On']},
        'SyncCorr-Sts':         {'type': 'enum', 'value': 0,
                                 'enums': ['Off', 'On']},

        'ConfigPS-Cmd':         {'type': 'int', 'value': 0},
        'ConfigTiming-Cmd':     {'type': 'int', 'value': 0},

        'Status-Mon':           {'type': 'int', 'value': 0},
        'Status-Cte':           {'type': 'string', 'count': 5, 'value':
                                 ('PS Connection', 'PS PwrState', 'PS OpMode',
                                  'PS CtrlMode', 'Timing Config')},
    }

    for fam in _SFAMS:
        pvs_database['LastCalcd' + fam + 'SL-Mon'] = {'type': 'float',
                                                      'value': 0, 'prec': 4,
                                                      'unit': '1/m^2'}
    if _ACC == 'SI':
        pvs_database['CorrMeth-Sel'] = {'type': 'enum', 'value': 0, 'enums':
                                        ['Proportional', 'Additional']}
        pvs_database['CorrMeth-Sts'] = {'type': 'enum', 'value': 0, 'enums':
                                        ['Proportional', 'Additional']}
    return pvs_database
