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
    _DEVICE = _ACC + '-Glob:AP-OpticsCorr:'
    _PREFIX = _PREFIX_VACA + _DEVICE
    if _ACC == 'BO':
        _SFAMS = ['SF', 'SD']
    elif _ACC == 'SI':
        _SFAMS = ['SFA1', 'SFA2', 'SDA1', 'SDA2', 'SDA3',
                  'SFB1', 'SFB2', 'SDB1', 'SDB2', 'SDB3',
                  'SFP1', 'SFP2', 'SDP1', 'SDP2', 'SDP3']


def get_pvs_database():
    """Return IOC dagtabase."""
    # global _SFAMS
    # corrmat_size = len(_SFAMS)*2

    pvs_database = {
        'Version-Cte':          {'type': 'string', 'value': _COMMIT_HASH},

        'ChromX-SP':            {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 40, 'lolim': -40},
        'ChromX-RB':            {'type': 'float', 'value': 0, 'prec': 6},
        'ChromY-SP':            {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 40, 'lolim': -40},
        'ChromY-RB':            {'type': 'float', 'value': 0, 'prec': 6},

        'CalcSL-Cmd':           {'type': 'int', 'value': 0},
        'ApplySL-Cmd':          {'type': 'int', 'value': 0},

        # 'ChromCorrMat-SP':    {'type': 'float', 'count': corrmat_size,
        #                        'value': corrmat_size*[0], 'prec': 6, 'unit':
        #                        '(dChromX/dSLSFam0,..,dChromY/dSLSFam0,..)'},
        # 'ChromCorrMat-RB':    {'type': 'float', 'count': corrmat_size,
        #                        'value': corrmat_size*[0], 'prec': 6, 'unit':
        #                        '(dChromX/dSLSFam0,..,dChromY/dSLSFam0,..)'},
        # 'ChromCorrInvMat-Mon':{'type': 'float', 'count': corrmat_size,
        #                        'value': corrmat_size*[0], 'prec': 6},
        # 'InitialChromX-SP':   {'type': 'float', 'count': 1,
        #                        'value': 0, 'prec': 6, 'unit':
        #                        'Considers Quadrupoles + Dipoles Multipoles'},
        # 'InitialChromX-RB':   {'type': 'float', 'count': 1,
        #                        'value': 0, 'prec': 6, 'unit':
        #                        'Considers Quadrupoles + Dipoles Multipoles'},
        # 'InitialChromY-SP':   {'type': 'float', 'count': 1,
        #                        'value': 0, 'prec': 6, 'unit':
        #                        'Considers Quadrupoles + Dipoles Multipoles'},
        # 'InitialChromY-RB':   {'type': 'float', 'count': 1,
        #                        'value': 0, 'prec': 6, 'unit':
        #                        'Considers Quadrupoles + Dipoles Multipoles'},

        # Delete these pvs if access to chrom0 is enable to control system
        'InitialChromX-Mon':  {'type': 'float', 'count': 1,
                               'value': 0, 'prec': 6, 'unit':
                               'Considers Quadrupoles + Dipoles Multipoles'},
        'InitialChromY-Mon':  {'type': 'float', 'count': 1,
                               'value': 0, 'prec': 6, 'unit':
                               'Considers Quadrupoles + Dipoles Multipoles'},
    }

    for fam in _SFAMS:
        pvs_database['LastCalcd' + fam + 'SL-Mon'] = {'type': 'float',
                                                      'value': 0, 'prec': 6,
                                                      'unit': '1/m^2'}
    return pvs_database
