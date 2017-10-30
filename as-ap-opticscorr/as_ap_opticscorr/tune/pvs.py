"""Create IOC Database."""

from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy import util as _util


_COMMIT_HASH = _util.get_last_commit_hash()
_PREFIX_VACA = _vaca_prefix
_ACC = None
_PREFIX = None
_QFAMS = None
_DEVICE = None


def select_ioc(acc):
    """Select IOC to build database for."""
    global _ACC, _PREFIX, _QFAMS, _DEVICE
    _ACC = acc.upper()
    _DEVICE = _ACC + '-Glob:AP-TuneCorr:'
    _PREFIX = _PREFIX_VACA + _DEVICE
    if _ACC == 'BO':
        _QFAMS = ['QF', 'QD']
    elif _ACC == 'SI':
        _QFAMS = ['QFA', 'QFB', 'QFP',
                  'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2']


def get_pvs_database():
    """Return IOC database."""
    global _QFAMS
    corrmat_size = len(_QFAMS)*2

    pvs_database = {
        'Version-Cte':          {'type': 'string', 'value': _COMMIT_HASH},

        'Log-Mon':              {'type': 'string', 'value': 'Starting...'},

        'DeltaTuneX-SP':        {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 1, 'lolim': -1},
        'DeltaTuneX-RB':        {'type': 'float', 'value': 0, 'prec': 6},
        'DeltaTuneY-SP':        {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 1, 'lolim': -1},
        'DeltaTuneY-RB':        {'type': 'float', 'value': 0, 'prec': 6},

        'ApplyDeltaKL-Cmd':     {'type': 'int', 'value': 0},

        'CorrMat-SP':           {'type': 'float', 'count': corrmat_size,
                                 'value': corrmat_size*[0], 'prec': 6, 'unit':
                                 'Tune x KFams (Matrix of add method)'},
        'CorrMat-RB':           {'type': 'float', 'count': corrmat_size,
                                 'value': corrmat_size*[0], 'prec': 6, 'unit':
                                 'Tune x KFams (Matrix of add method)'},

        'CorrFactor-SP':        {'type': 'float', 'value': 0, 'unit': '%',
                                 'prec': 1, 'lolim': -1000, 'hilim': 1000},
        'CorrFactor-RB':        {'type': 'float', 'value': 0, 'unit': '%',
                                 'prec': 1},

        'SyncCorr-Sel':         {'type': 'enum', 'value': 0,
                                 'enums': ['Off', 'On']},
        'SyncCorr-Sts':         {'type': 'enum', 'value': 0,
                                 'enums': ['Off', 'On']},

        'ConfigPS-Cmd':         {'type': 'int', 'value': 0},
        'ConfigTiming-Cmd':     {'type': 'int', 'value': 0},

        'SetNewRefKL-Cmd':      {'type': 'int', 'value': 0},

        'Status-Mon':           {'type': 'int', 'value': 0},
        'Status-Cte':           {'type': 'string', 'count': 5, 'value':
                                 ('PS Connection', 'PS PwrState', 'PS OpMode',
                                  'PS CtrlMode', 'Timing Config')},
    }

    for fam in _QFAMS:
        pvs_database[fam + 'RefKL-Mon'] = {'type': 'float', 'value': 0,
                                           'prec': 6, 'unit': '1/m'}
        pvs_database['LastCalcd' + fam + 'DeltaKL-Mon'] = {'type': 'float',
                                                           'value': 0,
                                                           'prec': 6}
    if _ACC == 'SI':
        pvs_database['CorrMeth-Sel'] = {'type': 'enum', 'value': 0, 'enums':
                                        ['Proportional', 'Additional']}
        pvs_database['CorrMeth-Sts'] = {'type': 'enum', 'value': 0, 'enums':
                                        ['Proportional', 'Additional']}
        pvs_database['NominalKL-SP'] = {'type': 'float', 'count': len(_QFAMS),
                                        'value': len(_QFAMS)*[0], 'prec': 6}
        pvs_database['NominalKL-RB'] = {'type': 'float', 'count': len(_QFAMS),
                                        'value': len(_QFAMS)*[0], 'prec': 6}
    return pvs_database
