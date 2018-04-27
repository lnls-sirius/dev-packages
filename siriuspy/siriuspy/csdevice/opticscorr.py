"""Define PVs, contants and properties of all OpticsCorr SoftIOCs."""
import collections as _collections


OFFONTYP = ('Off', 'On')
PROPADDTYP = ('Proportional', 'Additional')


class Const:
    """Const class defining OpticsCorr constants and Enum types."""

    BO_SFAMS_CHROMCORR = ('SF', 'SD')
    SI_SFAMS_CHROMCORR = ('SFA1', 'SFA2', 'SDA1', 'SDA2', 'SDA3',
                          'SFB1', 'SFB2', 'SDB1', 'SDB2', 'SDB3',
                          'SFP1', 'SFP2', 'SDP1', 'SDP2', 'SDP3')
    BO_QFAMS_TUNECORR = ('QF', 'QD')
    SI_QFAMS_TUNECORR = ('QFA', 'QFB', 'QFP',
                         'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2')
    STATUSLABELS = ('MA Connection', 'MA PwrState', 'MA OpMode',
                    'MA CtrlMode', 'Timing Config')

    @staticmethod
    def _init():
        """Create class constants."""
        for i in range(len(PROPADDTYP)):
            Const._add_const('CorrMeth', PROPADDTYP[i], i)
        for i in range(len(OFFONTYP)):
            Const._add_const('SyncCorr', OFFONTYP[i], i)

    @staticmethod
    def _add_const(group, const, i):
        if not hasattr(Const, group):
            setattr(Const, group, _collections.namedtuple(group, ''))
        obj = getattr(Const, group)
        setattr(obj, const, i)


Const._init()  # create class constants


def get_chrom_database(acc):
    """Return OpticsCorr-Chrom Soft IOC database."""
    if acc == 'BO':
        sfams = Const.BO_SFAMS_CHROMCORR
    elif acc == 'SI':
        sfams = Const.SI_SFAMS_CHROMCORR

    corrmat_size = len(sfams)*2

    pvs_database = {
        'Version-Cte':      {'type': 'string', 'value': 'UNDEF', 'scan': 0.25},

        'Log-Mon':          {'type': 'string', 'value': 'Starting...'},

        'ChromX-SP':        {'type': 'float', 'value': 0, 'prec': 6,
                             'hilim': 10, 'lolim': -10, 'high': 10,
                             'low': -10, 'hihi': 10, 'lolo': -10},
        'ChromX-RB':        {'type': 'float', 'value': 0, 'prec': 6},
        'ChromY-SP':        {'type': 'float', 'value': 0, 'prec': 6,
                             'hilim': 10, 'lolim': -10, 'high': 10,
                             'low': -10, 'hihi': 10, 'lolo': -10},
        'ChromY-RB':        {'type': 'float', 'value': 0, 'prec': 6},

        'ApplyCorr-Cmd':    {'type': 'int', 'value': 0},

        'ConfigName-SP':    {'type': 'string', 'value': ''},
        'ConfigName-RB':    {'type': 'string', 'value': ''},
        'RespMat-Mon':      {'type': 'float', 'count': corrmat_size,
                             'value': corrmat_size*[0], 'prec': 6, 'unit':
                             'Chrom x SFams (Matrix of add method)'},
        'NominalChrom-Mon': {'type': 'float', 'count': 2, 'value': 2*[0],
                             'prec': 6},
        'NominalSL-Mon':    {'type': 'float', 'count': len(sfams),
                             'value': len(sfams)*[0], 'prec': 6},

        'ConfigMA-Cmd':     {'type': 'int', 'value': 0},

        'Status-Mon':       {'type': 'int', 'value': 0b11111},
        'StatusLabels-Cte': {'type': 'string', 'count': 5,
                             'value': Const.STATUSLABELS},
    }

    for fam in sfams:
        pvs_database['SL' + fam + '-Mon'] = {
            'type': 'float', 'value': 0, 'prec': 4, 'unit': '1/m^2',
            'lolim': 0, 'hilim': 0, 'low': 0, 'high': 0, 'lolo': 0, 'hihi': 0}

    if acc == 'SI':
        pvs_database['CorrMeth-Sel'] = {'type': 'enum', 'enums': PROPADDTYP,
                                        'value': Const.CorrMeth.Proportional}
        pvs_database['CorrMeth-Sts'] = {'type': 'enum', 'enums': PROPADDTYP,
                                        'value': Const.CorrMeth.Proportional}
        pvs_database['SyncCorr-Sel'] = {'type': 'enum', 'enums': OFFONTYP,
                                        'value': Const.SyncCorr.Off}
        pvs_database['SyncCorr-Sts'] = {'type': 'enum', 'enums': OFFONTYP,
                                        'value': Const.SyncCorr.Off}
        pvs_database['ConfigTiming-Cmd'] = {'type': 'int', 'value': 0}

    return pvs_database


def get_tune_database(acc):
    """Return OpticsCorr-Tune Soft IOC database."""
    if acc == 'BO':
        qfams = Const.BO_QFAMS_TUNECORR
    elif acc == 'SI':
        qfams = Const.SI_QFAMS_TUNECORR

    corrmat_size = len(qfams)*2

    pvs_database = {
        'Version-Cte':     {'type': 'string', 'value': 'UNDEF'},

        'Log-Mon':         {'type': 'string', 'value': 'Starting...'},

        'DeltaTuneX-SP':   {'type': 'float', 'value': 0, 'prec': 6,
                            'hilim': 1, 'lolim': -1, 'high': 1, 'low': -1,
                            'hihi': 1, 'lolo': -1},
        'DeltaTuneX-RB':   {'type': 'float', 'value': 0, 'prec': 6,
                            'hilim': 1, 'lolim': -1, 'high': 1, 'low': -1,
                            'hihi': 1, 'lolo': -1},
        'DeltaTuneY-SP':   {'type': 'float', 'value': 0, 'prec': 6,
                            'hilim': 1, 'lolim': -1, 'high': 1, 'low': -1,
                            'hihi': 1, 'lolo': -1},
        'DeltaTuneY-RB':   {'type': 'float', 'value': 0, 'prec': 6,
                            'hilim': 1, 'lolim': -1, 'high': 1, 'low': -1,
                            'hihi': 1, 'lolo': -1},

        'ApplyCorr-Cmd':   {'type': 'int', 'value': 0},

        'ConfigName-SP':   {'type': 'string', 'value': ''},
        'ConfigName-RB':   {'type': 'string', 'value': ''},
        'RespMat-Mon':     {'type': 'float', 'count': corrmat_size,
                            'value': corrmat_size*[0], 'prec': 6, 'unit':
                            'Tune x QFams (Nominal Response Matrix)'},
        'NominalKL-Mon':   {'type': 'float', 'count': len(qfams),
                            'value': len(qfams)*[0], 'prec': 6},

        'CorrFactor-SP':   {'type': 'float', 'value': 0, 'unit': '%',
                            'prec': 1, 'hilim': 1000, 'lolim': -1000,
                            'high': 1000, 'low': -1000, 'hihi': 1000,
                            'lolo': -1000},
        'CorrFactor-RB':   {'type': 'float', 'value': 0, 'unit': '%',
                            'prec': 1, 'hilim': 1000, 'lolim': -1000,
                            'high': 1000, 'low': -1000, 'hihi': 1000,
                            'lolo': -1000},

        'ConfigMA-Cmd':    {'type': 'int', 'value': 0},

        'SetNewRefKL-Cmd': {'type': 'int', 'value': 0},

        'Status-Mon':      {'type': 'int', 'value': 0b11111},
        'StatusLabels-Cte': {'type': 'string', 'count': 5,
                             'value': Const.STATUSLABELS},
    }

    for fam in qfams:
        pvs_database['RefKL' + fam + '-Mon'] = {'type': 'float', 'value': 0,
                                                'prec': 6, 'unit': '1/m'}

        pvs_database['DeltaKL' + fam + '-Mon'] = {
            'type': 'float', 'value': 0, 'prec': 6, 'unit': '1/m',
            'lolim': 0, 'hilim': 0, 'low': 0, 'high': 0, 'lolo': 0, 'hihi': 0}

    if acc == 'SI':
        pvs_database['CorrMeth-Sel'] = {'type': 'enum', 'enums': PROPADDTYP,
                                        'value': Const.CorrMeth.Proportional}
        pvs_database['CorrMeth-Sts'] = {'type': 'enum', 'enums': PROPADDTYP,
                                        'value': Const.CorrMeth.Proportional}
        pvs_database['SyncCorr-Sel'] = {'type': 'enum', 'enums': OFFONTYP,
                                        'value': Const.SyncCorr.Off}
        pvs_database['SyncCorr-Sts'] = {'type': 'enum', 'enums': OFFONTYP,
                                        'value': Const.SyncCorr.Off}
        pvs_database['ConfigTiming-Cmd'] = {'type': 'int', 'value': 0}

    return pvs_database
