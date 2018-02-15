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


def get_pvs_section():
    """Return Soft IOC section/accelerator."""
    global _ACC
    return _ACC


def get_pvs_vaca_prefix():
    """Return Soft IOC vaca prefix."""
    global _PREFIX_VACA
    return _PREFIX_VACA


def get_pvs_prefix():
    """Return Soft IOC prefix."""
    global _PREFIX
    return _PREFIX


def get_corr_fams():
    """Return list of magnet families used on correction."""
    global _SFAMS
    return _SFAMS


def get_pvs_database():
    """Return IOC database."""
    global _SFAMS, _COMMIT_HASH
    corrmat_size = len(_SFAMS)*2

    pvs_database = {
        'Version-Cte':          {'type': 'string', 'value': _COMMIT_HASH,
                                 'scan': 0.25},

        'Log-Mon':              {'type': 'string', 'value': 'Starting...'},

        'ChromX-SP':            {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 10, 'lolim': -10, 'high': 10,
                                 'low': -10, 'hihi': 10, 'lolo': -10},
        'ChromX-RB':            {'type': 'float', 'value': 0, 'prec': 6},
        'ChromY-SP':            {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 10, 'lolim': -10, 'high': 10,
                                 'low': -10, 'hihi': 10, 'lolo': -10},
        'ChromY-RB':            {'type': 'float', 'value': 0, 'prec': 6},

        'ApplyCorr-Cmd':        {'type': 'int', 'value': 0},

        'ConfigName-SP':        {'type': 'string', 'value': ''},
        'ConfigName-RB':        {'type': 'string', 'value': ''},
        'RespMat-Mon':          {'type': 'float', 'count': corrmat_size,
                                 'value': corrmat_size*[0], 'prec': 6, 'unit':
                                 'Chrom x SFams (Matrix of add method)'},
        'NominalChrom-Mon':     {'type': 'float', 'count': 2, 'value': 2*[0],
                                 'prec': 6},
        'NominalSL-Mon':        {'type': 'float', 'count': len(_SFAMS),
                                 'value': len(_SFAMS)*[0], 'prec': 6},

        'SyncCorr-Sel':         {'type': 'enum', 'value': 0,
                                 'enums': ['Off', 'On']},
        'SyncCorr-Sts':         {'type': 'enum', 'value': 0,
                                 'enums': ['Off', 'On']},

        'ConfigMA-Cmd':         {'type': 'int', 'value': 0},
        'ConfigTiming-Cmd':     {'type': 'int', 'value': 0},

        'Status-Mon':           {'type': 'int', 'value': 0x1f},
        'Status-Cte':           {'type': 'string', 'count': 5, 'value':
                                 ('MA Connection', 'MA PwrState', 'MA OpMode',
                                  'MA CtrlMode', 'Timing Config')},
    }

    for fam in _SFAMS:
        pvs_database['SL' + fam + '-Mon'] = {
            'type': 'float', 'value': 0, 'prec': 4, 'unit': '1/m^2',
            'lolim': 0, 'hilim': 0, 'low': 0, 'high': 0, 'lolo': 0, 'hihi': 0}

    if _ACC == 'SI':
        pvs_database['CorrMeth-Sel'] = {'type': 'enum', 'value': 0, 'enums':
                                        ['Proportional', 'Additional']}
        pvs_database['CorrMeth-Sts'] = {'type': 'enum', 'value': 0, 'enums':
                                        ['Proportional', 'Additional']}
    return pvs_database


def print_banner_and_save_pv_list():
    """Print Soft IOC banner."""
    global _COMMIT_HASH, _PREFIX_VACA, _ACC, _DEVICE, _PREFIX
    _util.print_ioc_banner(
        ioc_name=_ACC+'-AP-ChromCorr',
        db=get_pvs_database(),
        description=_ACC+'-AP-ChromCorr Soft IOC',
        version=_COMMIT_HASH,
        prefix=_PREFIX)
    _util.save_ioc_pv_list(
        _ACC.lower()+'-ap-chromcorr',
        (_DEVICE, _PREFIX_VACA),
        get_pvs_database())
