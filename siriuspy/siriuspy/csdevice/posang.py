"""Define PVs, contants and properties of PosAng SoftIOCs."""

from siriuspy.csdevice import util as _cutil


class Const:
    """Const class defining PosAng constants."""

    TB_CORRH_POSANG_CHSEPT = ('TB-04:MA-CH-1', 'TB-04:PM-InjSept')
    TB_CORRH_POSANG_CHCH = ('TB-04:MA-CH-1', 'TB-04:MA-CH-2')
    TB_CORRV_POSANG = ('TB-04:MA-CV-1', 'TB-04:MA-CV-2')

    TS_CORRH_POSANG = ('TS-04:MA-CH', 'TS-04:PM-InjSeptF')
    TS_CORRV_POSANG = ('TS-04:MA-CV-1', 'TS-04:MA-CV-2')

    STATUSLABELS = ('MA Connection', 'MA PwrState', 'MA OpMode', 'MA CtrlMode')


def get_posang_database(tl, correctors_type):
    """Return Soft IOC database."""
    if tl.upper() == 'TS':
        CORRV = Const.TS_CORRV_POSANG
        CORRH = Const.TS_CORRH_POSANG
        ch2_unit = 'mrad'
    elif tl.upper() == 'TB':
        CORRV = Const.TB_CORRV_POSANG
        CORRH = Const.TB_CORRH_POSANG_CHSEPT if correctors_type == 'ch-sept' \
            else Const.TB_CORRH_POSANG_CHCH
        ch2_unit = 'mrad' if correctors_type == 'ch-sept' else 'urad'

    pvs_database = {
        'Version-Cte':       {'type': 'string', 'value': 'UNDEF'},
        'CorrType-Cte':      {'type': 'string', 'value': correctors_type},

        'Log-Mon':           {'type': 'string', 'value': 'Starting...'},

        'DeltaPosX-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm', 'hilim': 10, 'lolim': -10},
        'DeltaPosX-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm'},
        'DeltaAngX-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad', 'hilim': 10, 'lolim': -10},
        'DeltaAngX-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},

        'DeltaPosY-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm', 'hilim': 10, 'lolim': -10},
        'DeltaPosY-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm'},
        'DeltaAngY-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad', 'hilim': 10, 'lolim': -10},
        'DeltaAngY-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},

        'ConfigName-SP':     {'type': 'string', 'value': ''},
        'ConfigName-RB':     {'type': 'string', 'value': ''},
        'RespMatX-Mon':      {'type': 'float', 'value': 4*[0], 'prec': 6,
                              'count': 4},
        'RespMatY-Mon':      {'type': 'float', 'value': 4*[0], 'prec': 6,
                              'count': 4},

        'CH1-Cte':           {'type': 'string', 'value': CORRH[0]},
        'RefKickCH1-Mon':    {'type': 'float', 'value': 0, 'prec': 4,
                              'unit': 'urad'},
        'CH2-Cte':           {'type': 'string', 'value': CORRH[1]},
        'RefKickCH2-Mon':    {'type': 'float', 'value': 0, 'prec': 4,
                              'unit': ch2_unit},
        'CV1-Cte':           {'type': 'string', 'value':  CORRV[0]},
        'RefKickCV1-Mon':    {'type': 'float', 'value': 0, 'prec': 4,
                              'unit': 'urad'},
        'CV2-Cte':           {'type': 'string', 'value':  CORRV[1]},
        'RefKickCV2-Mon':    {'type': 'float', 'value': 0, 'prec': 4,
                              'unit': 'urad'},
        'SetNewRefKick-Cmd': {'type': 'int', 'value': 0},

        'ConfigMA-Cmd':      {'type': 'int', 'value': 0},

        'Status-Mon':        {'type': 'int', 'value': 0b1111},
        'StatusLabels-Cte':  {'type': 'char', 'count': 1000,
                              'value': '\n'.join(Const.STATUSLABELS)},
    }
    pvs_database = _cutil.add_pvslist_cte(pvs_database)
    return pvs_database
