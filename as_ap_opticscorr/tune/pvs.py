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
    global _ACC, _PREFIX, _PREFIX_VACA, _QFAMS, _DEVICE
    _ACC = acc.upper()
    _DEVICE = _ACC + '-Glob:AP-TuneCorr:'
    _PREFIX = _PREFIX_VACA + _DEVICE
    if _ACC == 'BO':
        _QFAMS = ['QF', 'QD']
    elif _ACC == 'SI':
        _QFAMS = ['QFA', 'QFB', 'QFP',
                  'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2']


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
    global _QFAMS
    return _QFAMS


def get_pvs_database():
    """Return IOC database."""
    global _COMMIT_HASH, _ACC, _QFAMS
    corrmat_size = len(_QFAMS)*2

    pvs_database = {
        'Version-Cte':          {'type': 'string', 'value': _COMMIT_HASH},

        'Log-Mon':              {'type': 'string', 'value': 'Starting...'},

        'DeltaTuneX-SP':        {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 1, 'lolim': -1, 'high': 1, 'low': -1,
                                 'hihi': 1, 'lolo': -1},
        'DeltaTuneX-RB':        {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 1, 'lolim': -1, 'high': 1, 'low': -1,
                                 'hihi': 1, 'lolo': -1},
        'DeltaTuneY-SP':        {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 1, 'lolim': -1, 'high': 1, 'low': -1,
                                 'hihi': 1, 'lolo': -1},
        'DeltaTuneY-RB':        {'type': 'float', 'value': 0, 'prec': 6,
                                 'hilim': 1, 'lolim': -1, 'high': 1, 'low': -1,
                                 'hihi': 1, 'lolo': -1},

        'ApplyCorr-Cmd':        {'type': 'int', 'value': 0},

        'ConfigName-SP':        {'type': 'string', 'value': ''},
        'ConfigName-RB':        {'type': 'string', 'value': ''},
        'RespMat-Mon':          {'type': 'float', 'count': corrmat_size,
                                 'value': corrmat_size*[0], 'prec': 6, 'unit':
                                 'Tune x QFams (Nominal Response Matrix)'},
        'NominalKL-Mon':        {'type': 'float', 'count': len(_QFAMS),
                                 'value': len(_QFAMS)*[0], 'prec': 6},

        'CorrFactor-SP':        {'type': 'float', 'value': 0, 'unit': '%',
                                 'prec': 1, 'hilim': 1000, 'lolim': -1000,
                                 'high': 1000, 'low': -1000, 'hihi': 1000,
                                 'lolo': -1000},
        'CorrFactor-RB':        {'type': 'float', 'value': 0, 'unit': '%',
                                 'prec': 1, 'hilim': 1000, 'lolim': -1000,
                                 'high': 1000, 'low': -1000, 'hihi': 1000,
                                 'lolo': -1000},

        'ConfigMA-Cmd':         {'type': 'int', 'value': 0},

        'SetNewRefKL-Cmd':      {'type': 'int', 'value': 0},

        'Status-Mon':           {'type': 'int', 'value': 0x1f},
        'Status-Cte':           {'type': 'string', 'count': 5, 'value':
                                 ('MA Connection', 'MA PwrState', 'MA OpMode',
                                  'MA CtrlMode', 'Timing Config')},
    }

    for fam in _QFAMS:
        pvs_database['RefKL' + fam + '-Mon'] = {'type': 'float', 'value': 0,
                                                'prec': 6, 'unit': '1/m'}

        pvs_database['DeltaKL' + fam + '-Mon'] = {
            'type': 'float', 'value': 0, 'prec': 6, 'unit': '1/m',
            'lolim': 0, 'hilim': 0, 'low': 0, 'high': 0, 'lolo': 0, 'hihi': 0}

    if _ACC == 'SI':
        pvs_database['CorrMeth-Sel'] = {'type': 'enum', 'value': 0, 'enums':
                                        ['Proportional', 'Additional']}
        pvs_database['CorrMeth-Sts'] = {'type': 'enum', 'value': 0, 'enums':
                                        ['Proportional', 'Additional']}
        pvs_database['SyncCorr-Sel'] = {'type': 'enum', 'value': 0,
                                        'enums': ['Off', 'On']}
        pvs_database['SyncCorr-Sts'] = {'type': 'enum', 'value': 0,
                                        'enums': ['Off', 'On']}
        pvs_database['ConfigTiming-Cmd'] = {'type': 'int', 'value': 0}
    return pvs_database


def print_banner_and_save_pv_list():
    """Print Soft IOC banner."""
    global _COMMIT_HASH, _PREFIX_VACA, _ACC, _PREFIX, _DEVICE
    _util.print_ioc_banner(
        ioc_name=_ACC+'-AP-TuneCorr',
        db=get_pvs_database(),
        description=_ACC+'-AP-TuneCorr Soft IOC',
        version=_COMMIT_HASH,
        prefix=_PREFIX)
    _util.save_ioc_pv_list(
        _ACC.lower()+'-ap-tunecorr',
        (_DEVICE, _PREFIX_VACA),
        get_pvs_database())
