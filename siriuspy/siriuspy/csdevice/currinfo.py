"""Define PVs, contants and properties of CurrInfo SoftIOCs."""
from siriuspy.csdevice import util as _cutil


# --- Enumeration Types ---

class ETypes(_cutil.ETypes):
    """Local enumerate types."""

    DCCTSELECTIONTYP = ('Avg', 'DCCT13C4', 'DCCT14C4')
    BUFFAUTORSTTYP = ('PVsTrig', 'DCurrCheck', 'Off')


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_cutil.Const):
    """Const class defining CurrInfo constants and Enum types."""

    DCCT = _cutil.Const.register('DCCT', _et.DCCTSELECTIONTYP)
    DCCTFltCheck = _cutil.Const.register('DCCTFltCheck', _et.OFF_ON)
    BuffAutoRst = _cutil.Const.register('BuffAutoRst', _et.BUFFAUTORSTTYP)


_c = Const  # syntactic sugar


# --- Databases ---

def get_charge_database():
    """Return CurrentInfo-Charge Soft IOC database."""
    pvs_database = {
        'Version-Cte':        {'type': 'string', 'value': 'UNDEF'},
        'Charge-Mon':         {'type': 'float', 'value': 0.0, 'prec': 10,
                               'unit': 'A.h'},
        'ChargeCalcIntvl-SP': {'type': 'float', 'value': 100.0, 'prec': 1,
                               'unit': 's'},
        'ChargeCalcIntvl-RB': {'type': 'float', 'value': 100.0, 'prec': 1,
                               'unit': 's'},
        }
    pvs_database = _cutil.add_pvslist_cte(pvs_database)
    return pvs_database


def get_current_database(acc):
    """Return CurrentInfo-Current Soft IOC database."""
    pvs_database = {
        'Version-Cte':     {'type': 'string', 'value': 'UNDEF'},
        'Current-Mon':     {'type': 'float', 'value': 0.0, 'prec': 3,
                            'unit': 'mA'},
        'StoredEBeam-Mon': {'type': 'int', 'value': 0},
    }

    if acc == 'SI':
        pvs_database['DCCT-Sel'] = {'type': 'enum', 'value': _c.DCCT.Avg,
                                    'enums': _et.DCCTSELECTIONTYP}
        pvs_database['DCCT-Sts'] = {'type': 'enum', 'value': _c.DCCT.Avg,
                                    'enums': _et.DCCTSELECTIONTYP}
        pvs_database['DCCTFltCheck-Sel'] = {'type': 'enum',
                                            'enums': _et.OFF_ON,
                                            'value': _c.DCCTFltCheck.On}
        pvs_database['DCCTFltCheck-Sts'] = {'type': 'enum',
                                            'enums': _et.OFF_ON,
                                            'value': _c.DCCTFltCheck.On}
    pvs_database = _cutil.add_pvslist_cte(pvs_database)
    return pvs_database


def get_lifetime_database():
    """Return CurrentInfo-Lifetime Soft IOC database."""
    pvs_database = {
        'Version-Cte':     {'type': 'string', 'value': 'UNDEF'},
        'Lifetime-Mon':    {'type': 'float', 'value': 0.0, 'prec': 0,
                            'unit': 's'},
        'BuffSizeMax-SP':  {'type': 'int', 'lolim': 0, 'hilim': 360000,
                            'value': 0},
        'BuffSizeMax-RB':  {'type': 'int', 'value': 0},
        'BuffSize-Mon':	   {'type': 'int', 'value': 0},
        'SplIntvl-SP':     {'type': 'int', 'unit': 's',  'lolim': 0,
                            'hilim': 360000, 'low': 0, 'high': 3600,
                            'lolo': 0, 'hihi': 3600, 'value': 10},
        'SplIntvl-RB':	   {'type': 'int', 'value': 10, 'unit': 's'},
        'BuffRst-Cmd':     {'type': 'int', 'value': 0},
        'BuffAutoRst-Sel': {'type': 'enum', 'enums': _et.BUFFAUTORSTTYP,
                            'value': _c.BuffAutoRst.DCurrCheck},
        'BuffAutoRst-Sts': {'type': 'enum', 'enums': _et.BUFFAUTORSTTYP,
                            'value': _c.BuffAutoRst.DCurrCheck},
        'DCurrFactor-Cte': {'type': 'float', 'value': 0.003, 'prec': 2,
                            'unit': 'mA'}
        }
    pvs_database = _cutil.add_pvslist_cte(pvs_database)
    return pvs_database
