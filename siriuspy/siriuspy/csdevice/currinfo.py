"""Define PVs, constants and properties of CurrInfo SoftIOCs."""
import numpy as _np
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

def get_currinfo_database(acc):
    """Return CurrentInfo Soft IOC database."""
    pvs_db = {'Version-Cte': {'type': 'string', 'value': 'UNDEF'}}
    if acc == 'SI':
        pvs_db['Current-Mon'] = {'type': 'float', 'value': 0.0,
                                 'prec': 3, 'unit': 'mA'}

        pvs_db['StoredEBeam-Mon'] = {'type': 'int', 'value': 0}

        pvs_db['DCCT-Sel'] = {'type': 'enum', 'value': _c.DCCT.Avg,
                              'enums': _et.DCCTSELECTIONTYP}
        pvs_db['DCCT-Sts'] = {'type': 'enum', 'value': _c.DCCT.Avg,
                              'enums': _et.DCCTSELECTIONTYP}

        pvs_db['DCCTFltCheck-Sel'] = {'type': 'enum', 'enums': _et.OFF_ON,
                                      'value': _c.DCCTFltCheck.On}
        pvs_db['DCCTFltCheck-Sts'] = {'type': 'enum', 'enums': _et.OFF_ON,
                                      'value': _c.DCCTFltCheck.On}

        pvs_db['Charge-Mon'] = {'type': 'float', 'value': 0.0,
                                'prec': 12, 'unit': 'A.h'}

        pvs_db['ChargeCalcIntvl-SP'] = {'type': 'float', 'value': 100.0,
                                        'prec': 1, 'unit': 's'}
        pvs_db['ChargeCalcIntvl-RB'] = {'type': 'float', 'value': 100.0,
                                        'prec': 1, 'unit': 's'}
    elif acc == 'BO':
        pvs_db['RawReadings-Mon'] = {'type': 'float', 'count': 100000,
                                     'value': _np.array(100000*[0.0]),
                                     'unit': 'mA'}

        pvs_db['Current150MeV-Mon'] = {'type': 'float', 'value': 0.0,
                                       'prec': 3, 'unit': 'mA'}
        pvs_db['Current1GeV-Mon'] = {'type': 'float', 'value': 0.0,
                                     'prec': 3, 'unit': 'mA'}
        pvs_db['Current2GeV-Mon'] = {'type': 'float', 'value': 0.0,
                                     'prec': 3, 'unit': 'mA'}
        pvs_db['Current3GeV-Mon'] = {'type': 'float', 'value': 0.0,
                                     'prec': 3, 'unit': 'mA'}

        pvs_db['Charge150MeV-Mon'] = {'type': 'float', 'value': 0.0,
                                      'prec': 12, 'unit': 'A.h'}
        pvs_db['Charge1GeV-Mon'] = {'type': 'float', 'value': 0.0,
                                    'prec': 12, 'unit': 'A.h'}
        pvs_db['Charge2GeV-Mon'] = {'type': 'float', 'value': 0.0,
                                    'prec': 12, 'unit': 'A.h'}
        pvs_db['Charge3GeV-Mon'] = {'type': 'float', 'value': 0.0,
                                    'prec': 12, 'unit': 'A.h'}

        pvs_db['RampEff-Mon'] = {'type': 'float', 'value': 0.0,
                                 'prec': 2, 'unit': '%'}
    pvs_db = _cutil.add_pvslist_cte(pvs_db)
    return pvs_db


def get_lifetime_database():
    """Return CurrentInfo-Lifetime Soft IOC database."""
    pvs_db = {
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
    pvs_db = _cutil.add_pvslist_cte(pvs_db)
    return pvs_db
