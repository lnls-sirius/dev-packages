"""Define PVs, contants and properties of PosAng SoftIOCs."""

from siriuspy.csdevice import util as _cutil


class Const:
    """Const class defining PosAng constants."""

    TB_CORRH_POSANG = ('TB-04:MA-CH', 'TB-04:PM-InjSept')
    TB_CORRV_POSANG = ('TB-04:MA-CV-1', 'TB-04:MA-CV-2')
    TS_CORRH_POSANG = ('TS-04:MA-CH', 'TS-04:PM-InjSeptF')
    TS_CORRV_POSANG = ('TS-04:MA-CV-1', 'TS-04:MA-CV-2')

    STATUSLABELS = ('MA Connection', 'MA PwrState', 'MA OpMode', 'MA CtrlMode')


def get_posang_database():
    """Return Soft IOC database."""
    pvs_database = {
        'Version-Cte':       {'type': 'string', 'value': 'UNDEF'},

        'Log-Mon':           {'type': 'string', 'value': 'Starting...'},

        'DeltaPosX-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm', 'hilim': 5, 'lolim': -5},
        'DeltaPosX-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm'},
        'DeltaAngX-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad', 'hilim': 4, 'lolim': -4},
        'DeltaAngX-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},

        'DeltaPosY-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm', 'hilim': 5, 'lolim': -5},
        'DeltaPosY-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mm'},
        'DeltaAngY-SP':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad', 'hilim': 4, 'lolim': -4},
        'DeltaAngY-RB':      {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},

        'ConfigName-SP':     {'type': 'string', 'value': ''},
        'ConfigName-RB':     {'type': 'string', 'value': ''},
        'RespMatX-Mon':      {'type': 'float', 'value': 4*[0], 'prec': 3,
                              'count': 4},
        'RespMatY-Mon':      {'type': 'float', 'value': 4*[0], 'prec': 3,
                              'count': 4},

        'RefKickCH1-Mon':    {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'urad'},
        'RefKickCH2-Mon':    {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'mrad'},
        'RefKickCV1-Mon':    {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'urad'},
        'RefKickCV2-Mon':    {'type': 'float', 'value': 0, 'prec': 6,
                              'unit': 'urad'},
        'SetNewRefKick-Cmd': {'type': 'int', 'value': 0},

        'ConfigMA-Cmd':      {'type': 'int', 'value': 0},

        'Status-Mon':        {'type': 'int', 'value': 0b1111},
        'StatusLabels-Cte':  {'type': 'string', 'count': 4,
                              'value': Const.STATUSLABELS},
    }
    pvs_database = _cutil.add_pvslist_cte(pvs_database)
    return pvs_database
