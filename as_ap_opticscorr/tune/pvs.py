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
    _DEVICE = _ACC + '-Glob:AP-OpticsCorr:'
    _PREFIX = _PREFIX_VACA + _DEVICE
    if _ACC == 'BO':
        _QFAMS = ['QF', 'QD']
    elif _ACC == 'SI':
        _QFAMS = ['QFA', 'QDA',
                  'QFB', 'QDB1', 'QDB2',
                  'QFP', 'QDP1', 'QDP2']


def get_pvs_database():
    """Return IOC database."""
    # global _QFAMS
    # corrmat_size = len(_QFAMS)*2

    pvs_database = {
        'Version-Cte':          {'type': 'string', 'value': _COMMIT_HASH},

        'DeltaTuneX-SP':        {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 1, 'lolim': -1},
        'DeltaTuneX-RB':        {'type': 'float', 'value': 0, 'prec': 6},
        'DeltaTuneY-SP':        {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 1, 'lolim': -1},
        'DeltaTuneY-RB':        {'type': 'float', 'value': 0, 'prec': 6},

        'CalcDeltaKL-Cmd':      {'type': 'int', 'value': 0},
        'ApplyDeltaKL-Cmd':     {'type': 'int', 'value': 0},

        # 'TuneCorrMat-SP':      {'type': 'float', 'count': corrmat_size,
        #                         'value': corrmat_size*[0], 'prec': 6, 'unit':
        #                         '(dTuneX/dKLQFam0,...,dTuneY/dKLQFam0,...)'},
        # 'TuneCorrMat-RB':      {'type': 'float', 'count': corrmat_size,
        #                         'value': corrmat_size*[0], 'prec': 6, 'unit':
        #                         '(dTuneX/dKLQFam0,...,dTuneY/dKLQFam0,...)'},
        # 'TuneCorrInvMat-Mon':  {'type': 'float', 'count': corrmat_size,
        #                         'value': corrmat_size*[0], 'prec': 6},
        'TuneCorrFactor-SP':    {'type': 'float', 'value': 0, 'unit': '%',
                                 'prec': 1, 'lolim': -1000, 'hilim': 1000},
        'TuneCorrFactor-RB':    {'type': 'float', 'value': 0, 'unit': '%',
                                 'prec': 1},

        'SetNewKLRef-Cmd':      {'type': 'int', 'value': 0},
    }

    for fam in _QFAMS:
        pvs_database[fam + 'KLRef-Mon'] = {'type': 'float', 'value': 0,
                                           'prec': 6, 'unit': '1/m'}
        pvs_database['LastCalcd' + fam + 'DeltaKL-Mon'] = {'type': 'float',
                                                           'value': 0,
                                                           'prec': 6}
    return pvs_database
