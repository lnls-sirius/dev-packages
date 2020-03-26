"""Define PVs, constants and properties of OpticsCorr SoftIOCs."""
from siriuspy import csdev as _csdev


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    PROP_ADD = ('Proportional', 'Additional')
    INDIV_2KNOBS = ('Individual', 'TwoKnobs')


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_csdev.Const):
    """Const class defining OpticsCorr constants and Enum types."""

    CorrMeth = _csdev.Const.register('CorrMeth', _et.PROP_ADD)
    CorrGroup = _csdev.Const.register('CorrGroup', _et.INDIV_2KNOBS)
    SyncCorr = _csdev.Const.register('SyncCorr', _et.OFF_ON)
    BO_SFAMS_CHROMCORR = ('SF', 'SD')
    SI_SFAMS_CHROMCORR = ('SFA1', 'SFA2', 'SDA1', 'SDA2', 'SDA3',
                          'SFB1', 'SFB2', 'SDB1', 'SDB2', 'SDB3',
                          'SFP1', 'SFP2', 'SDP1', 'SDP2', 'SDP3')
    BO_QFAMS_TUNECORR = ('QF', 'QD')
    SI_QFAMS_TUNECORR = ('QFA', 'QFB', 'QFP',
                         'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2')
    STATUS_LABELS = ('PS Connection', 'PS PwrState', 'PS OpMode',
                     'PS CtrlMode', 'Timing Config')


_c = Const  # syntactic sugar


# --- Databases ---


def get_chrom_database(acc):
    """Return OpticsCorr-Chrom Soft IOC database."""
    if acc == 'BO':
        sfams = _c.BO_SFAMS_CHROMCORR
    elif acc == 'SI':
        sfams = _c.SI_SFAMS_CHROMCORR

    corrmat_size = len(sfams)*2

    pvs_database = {
        'Version-Cte':      {'type': 'string', 'value': 'UNDEF'},

        'Log-Mon':          {'type': 'string', 'value': 'Starting...'},

        'ChromX-SP':        {'type': 'float', 'value': 0, 'prec': 6,
                             'hilim': 10, 'lolim': -10, 'high': 10,
                             'low': -10, 'hihi': 10, 'lolo': -10},
        'ChromX-RB':        {'type': 'float', 'value': 0, 'prec': 6},
        'ChromY-SP':        {'type': 'float', 'value': 0, 'prec': 6,
                             'hilim': 10, 'lolim': -10, 'high': 10,
                             'low': -10, 'hihi': 10, 'lolo': -10},
        'ChromY-RB':        {'type': 'float', 'value': 0, 'prec': 6},

        'ApplyDelta-Cmd':    {'type': 'int', 'value': 0},

        'ConfigName-SP':    {'type': 'string', 'value': ''},
        'ConfigName-RB':    {'type': 'string', 'value': ''},
        'RespMat-Mon':      {'type': 'float', 'count': corrmat_size,
                             'value': corrmat_size*[0], 'prec': 6, 'unit':
                             'Chrom x SFams (Matrix of add method)'},
        'NominalChrom-Mon': {'type': 'float', 'count': 2, 'value': 2*[0],
                             'prec': 6},
        'NominalSL-Mon':    {'type': 'float', 'count': len(sfams),
                             'value': len(sfams)*[0], 'prec': 6},

        'ConfigPS-Cmd':     {'type': 'int', 'value': 0},

        'Status-Mon':       {'type': 'int', 'value': 0b11111},
        'StatusLabels-Cte': {'type': 'char', 'count': 1000,
                             'value': '\n'.join(_c.STATUS_LABELS)},
    }

    for fam in sfams:
        pvs_database['SL' + fam + '-Mon'] = {
            'type': 'float', 'value': 0, 'prec': 4, 'unit': '1/m^2',
            'lolim': 0, 'hilim': 0, 'low': 0, 'high': 0, 'lolo': 0, 'hihi': 0}

    if acc == 'SI':
        pvs_database['CorrMeth-Sel'] = {'type': 'enum',
                                        'enums': _et.PROP_ADD,
                                        'value': _c.CorrMeth.Proportional}
        pvs_database['CorrMeth-Sts'] = {'type': 'enum',
                                        'enums': _et.PROP_ADD,
                                        'value': _c.CorrMeth.Proportional}
        pvs_database['CorrGroup-Sel'] = {'type': 'enum',
                                         'enums': _et.INDIV_2KNOBS,
                                         'value': _c.CorrGroup.TwoKnobs}
        pvs_database['CorrGroup-Sts'] = {'type': 'enum',
                                         'enums': _et.INDIV_2KNOBS,
                                         'value': _c.CorrGroup.TwoKnobs}
        # pvs_database['SyncCorr-Sel'] = {'type': 'enum', 'enums': _et.OFF_ON,
        #                                 'value': _c.SyncCorr.Off}
        # pvs_database['SyncCorr-Sts'] = {'type': 'enum', 'enums': _et.OFF_ON,
        #                                 'value': _c.SyncCorr.Off}
        # pvs_database['ConfigTiming-Cmd'] = {'type': 'int', 'value': 0}

    pvs_database = _csdev.add_pvslist_cte(pvs_database)
    return pvs_database


def get_tune_database(acc):
    """Return OpticsCorr-Tune Soft IOC database."""
    if acc == 'BO':
        qfams = _c.BO_QFAMS_TUNECORR
    elif acc == 'SI':
        qfams = _c.SI_QFAMS_TUNECORR

    corrmat_size = len(qfams)*2

    pvs_database = {
        'Version-Cte':     {'type': 'string', 'value': 'UNDEF'},

        'Log-Mon':         {'type': 'string', 'value': 'Starting...'},

        'DeltaTuneX-SP':   {'type': 'float', 'value': 0, 'prec': 6,
                            'hilim': 5, 'lolim': -5, 'high': 5, 'low': -5,
                            'hihi': 5, 'lolo': -5},
        'DeltaTuneX-RB':   {'type': 'float', 'value': 0, 'prec': 6,
                            'hilim': 5, 'lolim': -5, 'high': 5, 'low': -5,
                            'hihi': 5, 'lolo': -5},
        'DeltaTuneY-SP':   {'type': 'float', 'value': 0, 'prec': 6,
                            'hilim': 5, 'lolim': -5, 'high': 5, 'low': -5,
                            'hihi': 5, 'lolo': -5},
        'DeltaTuneY-RB':   {'type': 'float', 'value': 0, 'prec': 6,
                            'hilim': 5, 'lolim': -5, 'high': 5, 'low': -5,
                            'hihi': 5, 'lolo': -5},

        'ApplyDelta-Cmd':   {'type': 'int', 'value': 0},

        'ConfigName-SP':   {'type': 'string', 'value': ''},
        'ConfigName-RB':   {'type': 'string', 'value': ''},
        'RespMat-Mon':     {'type': 'float', 'count': corrmat_size,
                            'value': corrmat_size*[0], 'prec': 6, 'unit':
                            'Tune x QFams (Nominal Response Matrix)'},
        'NominalKL-Mon':   {'type': 'float', 'count': len(qfams),
                            'value': len(qfams)*[0], 'prec': 6},

        'ConfigPS-Cmd':    {'type': 'int', 'value': 0},

        'SetNewRefKL-Cmd': {'type': 'int', 'value': 0},

        'Status-Mon':      {'type': 'int', 'value': 0b11111},
        'StatusLabels-Cte': {'type': 'char', 'count': 1000,
                             'value': '\n'.join(_c.STATUS_LABELS)},
    }

    for fam in qfams:
        pvs_database['RefKL' + fam + '-Mon'] = {'type': 'float', 'value': 0,
                                                'prec': 6, 'unit': '1/m'}

        pvs_database['DeltaKL' + fam + '-Mon'] = {
            'type': 'float', 'value': 0, 'prec': 6, 'unit': '1/m',
            'lolim': 0, 'hilim': 0, 'low': 0, 'high': 0, 'lolo': 0, 'hihi': 0}

    if acc == 'SI':
        pvs_database['CorrMeth-Sel'] = {'type': 'enum',
                                        'enums': _et.PROP_ADD,
                                        'value': _c.CorrMeth.Proportional}
        pvs_database['CorrMeth-Sts'] = {'type': 'enum',
                                        'enums': _et.PROP_ADD,
                                        'value': _c.CorrMeth.Proportional}
        pvs_database['CorrGroup-Sel'] = {'type': 'enum',
                                         'enums': _et.INDIV_2KNOBS,
                                         'value': _c.CorrGroup.TwoKnobs}
        pvs_database['CorrGroup-Sts'] = {'type': 'enum',
                                         'enums': _et.INDIV_2KNOBS,
                                         'value': _c.CorrGroup.TwoKnobs}
        pvs_database['SyncCorr-Sel'] = {'type': 'enum', 'enums': _et.OFF_ON,
                                        'value': _c.SyncCorr.Off}
        pvs_database['SyncCorr-Sts'] = {'type': 'enum', 'enums': _et.OFF_ON,
                                        'value': _c.SyncCorr.Off}
        pvs_database['ConfigTiming-Cmd'] = {'type': 'int', 'value': 0}

    pvs_database = _csdev.add_pvslist_cte(pvs_database)
    return pvs_database
