"""Define PVs, constants and properties of CurrInfo SoftIOCs."""
import numpy as _np

from .. import csdev as _csdev


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    DCCTSELECTIONTYP = ('Avg', 'DCCT13C4', 'DCCT14C4')
    BUFFAUTORSTTYP = ('Off', 'DCurrCheck')
    FITTYP = ('Exponential', 'Linear')


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_csdev.Const):
    """Const class defining CurrInfo constants and Enum types."""

    DCCT = _csdev.Const.register('DCCT', _et.DCCTSELECTIONTYP)
    DCCTFltCheck = _csdev.Const.register('DCCTFltCheck', _et.OFF_ON)
    BuffAutoRst = _csdev.Const.register('BuffAutoRst', _et.BUFFAUTORSTTYP)
    Fit = _csdev.Const.register('Fit', _et.FITTYP)


_c = Const  # syntactic sugar


# --- Databases ---

def get_currinfo_database(acc):
    """Return CurrentInfo Soft IOC database."""
    pvs_db = {'Version-Cte': {'type': 'string', 'value': 'UNDEF'}}
    if acc == 'SI':
        pvs_db['Current-Mon'] = {'type': 'float', 'value': 0.0,
                                 'prec': 3, 'unit': 'mA'}

        pvs_db['StoredEBeam-Mon'] = {'type': 'int', 'value': 0}

        pvs_db['DCCT-Sel'] = {'type': 'enum', 'value': _c.DCCT.DCCT13C4,
                              'enums': _et.DCCTSELECTIONTYP}
        pvs_db['DCCT-Sts'] = {'type': 'enum', 'value': _c.DCCT.DCCT13C4,
                              'enums': _et.DCCTSELECTIONTYP}

        pvs_db['DCCTFltCheck-Sel'] = {'type': 'enum', 'enums': _et.OFF_ON,
                                      'value': _c.DCCTFltCheck.Off}
        pvs_db['DCCTFltCheck-Sts'] = {'type': 'enum', 'enums': _et.OFF_ON,
                                      'value': _c.DCCTFltCheck.Off}

        pvs_db['Charge-Mon'] = {'type': 'float', 'value': 0.0, 'prec': 12,
                                'unit': 'A.h', 'scan': 60}

        pvs_db['InjEff-Mon'] = {'type': 'float', 'value': 0.0,
                                'prec': 2, 'unit': '%'}
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
                                      'prec': 4, 'unit': 'nC'}
        pvs_db['Charge1GeV-Mon'] = {'type': 'float', 'value': 0.0,
                                    'prec': 4, 'unit': 'nC'}
        pvs_db['Charge2GeV-Mon'] = {'type': 'float', 'value': 0.0,
                                    'prec': 4, 'unit': 'nC'}
        pvs_db['Charge3GeV-Mon'] = {'type': 'float', 'value': 0.0,
                                    'prec': 4, 'unit': 'nC'}

        pvs_db['IntCurrent3GeV-Mon'] = {'type': 'float', 'value': 0.0,
                                        'prec': 9, 'unit': 'mA.h'}

        pvs_db['CurrThold-SP'] = {'type': 'float', 'value': 0.004,
                                  'prec': 4, 'unit': 'mA', 'lolo': 0.0,
                                  'low': 0.0, 'lolim': 0.0, 'hilim': 0.010,
                                  'high': 0.010, 'hihi': 0.010}
        pvs_db['CurrThold-RB'] = {'type': 'float', 'value': 0.004,
                                  'prec': 4, 'unit': 'mA', 'lolo': 0.0,
                                  'low': 0.0, 'lolim': 0.0, 'hilim': 0.010,
                                  'high': 0.010, 'hihi': 0.010}

        pvs_db['RampEff-Mon'] = {'type': 'float', 'value': 0.0,
                                 'prec': 2, 'unit': '%'}
    pvs_db = _csdev.add_pvslist_cte(pvs_db)
    return pvs_db


def get_lifetime_database():
    """Return CurrentInfo-Lifetime Soft IOC database."""
    pvs_db = {
        'VersionLifetime-Cte': {'type': 'string', 'value': 'UNDEF'},

        'LtFitMode-Sel': {'type': 'enum', 'enums': _et.FITTYP,
                          'value': _c.Fit.Linear},
        'LtFitMode-Sts': {'type': 'enum', 'enums': _et.FITTYP,
                          'value': _c.Fit.Linear},
        'MaxSplIntvl-SP': {'type': 'float', 'unit': 's', 'lolim': -1,
                           'hilim': 360000, 'prec': 2, 'value': 500},
        'MaxSplIntvl-RB': {'type': 'float', 'unit': 's', 'lolim': 10,
                           'hilim': 360000, 'prec': 2, 'value': 500},
        'SplIntvl-Mon': {'type': 'float', 'unit': 's', 'prec': 2,
                         'value': 0.0},
        'SplIntvlBPM-Mon': {'type': 'float', 'unit': 's', 'prec': 2,
                            'value': 0.0},
        'MinIntvlBtwSpl-SP': {'type': 'float', 'unit': 's', 'lolim': 0,
                              'hilim': 1200, 'low': 0, 'high': 1200,
                              'lolo': 0, 'hihi': 1200, 'prec': 2,
                              'value': 0},
        'MinIntvlBtwSpl-RB': {'type': 'float', 'value': 0, 'prec': 2,
                              'unit': 's'},
        'CurrOffset-SP': {'type': 'float', 'value': 0.0, 'prec': 3,
                          'unit': 'mA', 'lolim': -10.0, 'hilim': 10.0,
                          'low': -10.0, 'high': 10.0, 'lolo': -10.0,
                          'hihi': 10.0},
        'CurrOffset-RB': {'type': 'float', 'value': 0.0, 'prec': 3,
                          'unit': 'mA', 'lolim': -10.0, 'hilim': 10.0,
                          'low': -10.0, 'high': 10.0, 'lolo': -10.0,
                          'hihi': 10.0},

        'BuffRst-Cmd': {'type': 'int', 'value': 0},
        'BuffAutoRst-Sel': {'type': 'enum', 'enums': _et.BUFFAUTORSTTYP,
                            'value': _c.BuffAutoRst.Off},
        'BuffAutoRst-Sts': {'type': 'enum', 'enums': _et.BUFFAUTORSTTYP,
                            'value': _c.BuffAutoRst.Off},
        'BuffAutoRstDCurr-SP': {'type': 'float', 'value': 0.1, 'prec': 2,
                                'unit': 'mA', 'lolim': -300.0, 'hilim': 300.0,
                                'low': -300.0, 'high': 300.0, 'lolo': -300.0,
                                'hihi': 300.0},
        'BuffAutoRstDCurr-RB': {'type': 'float', 'value': 0.1, 'prec': 2,
                                'unit': 'mA', 'lolim': -300.0, 'hilim': 300.0,
                                'low': -300.0, 'high': 300.0, 'lolo': -300.0,
                                'hihi': 300.0},

        'FrstSplTime-SP': {'type': 'float', 'value': 0.0, 'prec': 2,
                           'unit': 's', 'lolim': -1.0, 'hilim': 2e10},
        'FrstSplTime-RB': {'type': 'float', 'value': 0.0, 'prec': 2,
                           'unit': 's', 'lolim': -1.0, 'hilim': 2e10},
        'LastSplTime-SP': {'type': 'float', 'value': 0.0, 'prec': 2,
                           'unit': 's', 'lolim': -1.0, 'hilim': 2e10},
        'LastSplTime-RB': {'type': 'float', 'value': 0.0, 'prec': 2,
                           'unit': 's', 'lolim': -1.0, 'hilim': 2e10},
        'FrstSplTimeBPM-RB': {'type': 'float', 'value': 0.0, 'prec': 2,
                              'unit': 's', 'lolim': -1.0, 'hilim': 2e10},
        'LastSplTimeBPM-RB': {'type': 'float', 'value': 0.0, 'prec': 2,
                              'unit': 's', 'lolim': -1.0, 'hilim': 2e10},

        'Lifetime-Mon': {'type': 'float', 'value': 0.0, 'prec': 2,
                         'unit': 's', 'scan': 0.2},
        'BuffSize-Mon': {'type': 'int', 'value': 0},
        'BuffSizeTot-Mon': {'type': 'int', 'value': 0},
        'BufferValue-Mon': {'type': 'float', 'prec': 3, 'count': 100000,
                            'value': [0.0, ] * 100000},
        'BufferTimestamp-Mon': {'type': 'float', 'prec': 3, 'count': 100000,
                                'value': [0.0, ] * 100000},

        'LifetimeBPM-Mon': {'type': 'float', 'value': 0.0, 'prec': 2,
                            'unit': 's', 'scan': 0.2},
        'BuffSizeBPM-Mon': {'type': 'int', 'value': 0},
        'BuffSizeTotBPM-Mon': {'type': 'int', 'value': 0},
        'BufferValueBPM-Mon': {'type': 'float', 'prec': 3, 'count': 100000,
                               'value': [0.0, ] * 100000},
        'BufferTimestampBPM-Mon': {'type': 'float', 'count': 100000,
                                   'value': [0.0, ] * 100000, 'prec': 3},
        }
    pvs_db = _csdev.add_pvslist_cte(pvs_db)
    return pvs_db
