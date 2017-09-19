
import copy as _copy
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.search import MASearch as _MASearch


default_wfmsize   = 2000
default_wfmlabels =_et.enums('PSWfmLabelsTyp')
default_intlklabels = _et.enums('PSIntlkLabelsTyp')


def create_commun_propty_database():
    db = {
        'CtrlMode-Mon':     {'type': 'enum', 'enums': _et.enums('RmtLocTyp'),
                             'value': _et.idx.Remote},
        'PwrState-Sel':     {'type': 'enum', 'enums': _et.enums('OffOnTyp'),
                             'value': _et.idx.Off},
        'PwrState-Sts':     {'type': 'enum', 'enums': _et.enums('OffOnTyp'),
                             'value': _et.idx.Off},
        'OpMode-Sel':       {'type': 'enum', 'enums': _et.enums('PSOpModeTyp'),
                             'value': _et.idx.SlowRef},
        'OpMode-Sts':       {'type': 'enum', 'enums': _et.enums('PSOpModeTyp'),
                             'value': _et.idx.SlowRef},
        'Reset-Cmd':        {'type': 'int', 'value': 0},
        'Abort-Cmd':        {'type': 'int', 'value': 0},
        'WfmIndex-Mon':     {'type': 'int', 'value': 0},
        'WfmLabels-Mon':    {'type': 'string', 'count': len(default_wfmlabels),
                             'value': default_wfmlabels},
        'WfmLabel-SP':      {'type': 'string', 'value': default_wfmlabels[0]},
        'WfmLabel-RB':      {'type': 'string', 'value': default_wfmlabels[0]},
        'WfmLoad-Sel':      {'type': 'enum',   'enums': default_wfmlabels,
                             'value': 0},
        'WfmLoad-Sts':      {'type': 'enum',   'enums': default_wfmlabels,
                             'value': 0},
        'WfmData-SP':       {'type': 'float',  'count': default_wfmsize, 'value': [0.0 for datum in range(default_wfmsize)]},
        'WfmData-RB':       {'type': 'float',  'count': default_wfmsize, 'value': [0.0 for datum in range(default_wfmsize)]},
        'WfmSave-Cmd':      {'type': 'int',    'value': 0},
        'Intlk-Mon':        {'type': 'int',    'value': 0},
        'IntlkLabels-Cte':  {'type': 'string', 'count': 8, 'value': default_intlklabels},
        'Current-SP':       {'type': 'float',  'value': 0.0, 'prec': 4},
        'Current-RB':       {'type': 'float',  'value': 0.0, 'prec': 4},
        'CurrentRef-Mon':   {'type': 'float',  'value': 0.0, 'prec': 4},
        'Current-Mon':      {'type': 'float',  'value': 0.0, 'prec': 4},
    }
    return db

def get_ps_propty_database(pstype):
    """Returns property database of a power supply type device."""
    propty_db = create_commun_propty_database()
    units = _PSSearch.get_splims_unit()
    for propty, db in propty_db.items():
        # set setpoint limits in database
        if propty in ('Current-SP',):
            label='lolo';  db[label] = _PSSearch.get_splim(pstype,label)
            label='low';   db[label] = _PSSearch.get_splim(pstype,label)
            label='lolim'; db[label] = _PSSearch.get_splim(pstype,label)
            label='hilim'; db[label] = _PSSearch.get_splim(pstype,label)
            label='high';  db[label] = _PSSearch.get_splim(pstype,label)
            label='hihi';  db[label] = _PSSearch.get_splim(pstype,label)
        # define unit of current
        if propty in \
                ('Current-SP', 'Current-RB', 'CurrentRef-Mon', 'Current-Mon',
                 'WfmData-SP', 'WfmData-RB'):
            db['unit'] = units

    return propty_db


def get_ma_propty_database(maname):
    propty_db = create_commun_propty_database()
    units = _MASearch.get_splims_unit()
    magfunc_dict = _MASearch.conv_maname_2_magfunc(maname)
    db = {}
    for psname, magfunc in magfunc_dict.items():
        # psnames = _MASearch.conv_maname_2_psnames(maname)
        db[psname] = _copy.deepcopy(propty_db)
        # for propty,pdb in propty_db.items():
        #     # set setpoint limits in database
        #     if propty in ('Current-SP',):
        #         label='lolo';  pdb[label] = _MASearch.get_splim(maname,label)
        #         label='low';   pdb[label] = _MASearch.get_splim(maname,label)
        #         label='lolim'; pdb[label] = _MASearch.get_splim(maname,label)
        #         label='hilim'; pdb[label] = _MASearch.get_splim(maname,label)
        #         label='high';  pdb[label] = _MASearch.get_splim(maname,label)
        #         label='hihi';  pdb[label] = _MASearch.get_splim(maname,label)
        #     # define unit of current
        #     if propty in \
        #           ('Current-SP', 'Current-RB', 'CurrentRef-Mon',
        #            'Current-Mon'):
        #         #db[psname]['unit'] = units[0]
        #         pdb['unit'] = units[0]
        db[psname]["Current-SP"]['lolo'] = _MASearch.get_splim(maname, 'lolo')
        db[psname]["Current-SP"]['low'] = _MASearch.get_splim(maname, 'low')
        db[psname]["Current-SP"]['lolim'] = \
            _MASearch.get_splim(maname, 'lolim')
        db[psname]["Current-SP"]['hilim'] = \
            _MASearch.get_splim(maname, 'hilim')
        db[psname]["Current-SP"]['high'] = _MASearch.get_splim(maname, 'high')
        db[psname]["Current-SP"]['hihi'] = _MASearch.get_splim(maname, 'hihi')
        db[psname]["Current-SP"]['unit'] = units[0]
        db[psname]["Current-RB"]['unit'] = units[0]
        db[psname]["CurrentRef-Mon"]['unit'] = units[0]
        db[psname]["Current-Mon"]['unit'] = units[0]
        # db[psname]["Current-SP"]['prec'] = 6
        # db[psname]["Current-RB"]['prec'] = 6
        # db[psname]["CurrentRef-Mon"]['prec'] = 6
        # db[psname]["Current-Mon"]['prec'] = 6
        if magfunc in ('quadrupole', 'quadrupole-skew'):
            db[psname]['KL-SP'] = _copy.deepcopy(db[psname]['Current-SP']); db[psname]['KL-SP']['unit'] = '1/m'
            db[psname]['KL-RB'] = _copy.deepcopy(db[psname]['Current-RB']); db[psname]['KL-RB']['unit'] = '1/m'
            db[psname]['KLRef-Mon'] = _copy.deepcopy(db[psname]['CurrentRef-Mon']); db[psname]['KLRef-Mon']['unit'] = '1/m'
            db[psname]['KL-Mon'] = _copy.deepcopy(db[psname]['Current-Mon']); db[psname]['KL-Mon']['unit'] = '1/m'
        elif magfunc == 'sextupole':
            db[psname]['SL-SP']     = _copy.deepcopy(db[psname]['Current-SP']); db[psname]['SL-SP']['unit'] = '1/m^2'
            db[psname]['SL-RB']     = _copy.deepcopy(db[psname]['Current-RB']); db[psname]['SL-RB']['unit'] = '1/m^2'
            db[psname]['SLRef-Mon'] = _copy.deepcopy(db[psname]['CurrentRef-Mon']); db[psname]['SLRef-Mon']['unit'] = '1/m^2'
            db[psname]['SL-Mon']    = _copy.deepcopy(db[psname]['Current-Mon']); db[psname]['SL-Mon']['unit'] = '1/m^2'
        elif magfunc == 'dipole':
            db[psname]['Energy-SP']     = _copy.deepcopy(db[psname]['Current-SP']); db[psname]['Energy-SP']['unit'] = 'GeV'
            db[psname]['Energy-RB']     = _copy.deepcopy(db[psname]['Current-RB']); db[psname]['Energy-RB']['unit'] = 'GeV'
            db[psname]['EnergyRef-Mon'] = _copy.deepcopy(db[psname]['CurrentRef-Mon']); db[psname]['EnergyRef-Mon']['unit'] = 'GeV'
            db[psname]['Energy-Mon']    = _copy.deepcopy(db[psname]['Current-Mon']); db[psname]['Energy-Mon']['unit'] = 'GeV'
            db[psname]['Energy-SP']['prec'] = 6
        elif magfunc in ('corrector-vertical', 'corrector-horizontal'):
            db[psname]['Kick-SP'] = _copy.deepcopy(db[psname]['Current-SP'])
            db[psname]['Kick-SP']['prec'] = 6
            db[psname]['Kick-SP']['unit'] = 'rad'
            db[psname]['Kick-RB']     = _copy.deepcopy(db[psname]['Current-RB']); db[psname]['Kick-RB']['unit'] = 'rad'
            db[psname]['KickRef-Mon'] = _copy.deepcopy(db[psname]['CurrentRef-Mon']); db[psname]['KickRef-Mon']['unit'] = 'rad'
            db[psname]['Kick-Mon']    = _copy.deepcopy(db[psname]['Current-Mon']); db[psname]['Kick-Mon']['unit'] = 'rad'
    return db
