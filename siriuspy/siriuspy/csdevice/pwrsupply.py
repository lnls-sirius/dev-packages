"""Power Supply Control System Devices."""

import copy as _copy
from collections import namedtuple as _namedtuple
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.search import MASearch as _MASearch
default_wfmsize = 4000
default_wfmlabels = _et.enums('PSWfmLabelsTyp')
# default_intlklabels = _et.enums('PSIntlkLabelsTyp')
default_ps_current_precision = 4
default_pu_current_precision = 4

_default_ps_current_unit = None
_default_pu_current_unit = None

# --- power supply enums ---

ps_models = ('FBP', 'FAP', 'FAP_4P_Master', 'FAP_4P_Slave',
             'FAP_2P2S_Master', 'FAP_2P2S_Slave', 'FAC', 'FAC_2S_ACDC',
             'FAC_2S_DCDC', 'FAC_2P4S_ACDC', 'FAC_2P4S_DCDC',)
ps_dsblenbl = ('Dsbl', 'Enbl')
ps_interface = ('Remote', 'Local', 'PCHost')
ps_openloop = ('Closed', 'Open')
ps_states = ('Off', 'Interlock', 'Initializing',
             'SlowRef', 'SlowRefSync', 'FastRef', 'RmpWfm', 'MigWfm', 'Cycle')
ps_pwrstate_sel = ('Off', 'On', 'Initializing')
ps_pwrstate_sts = ('Off', 'On')
ps_opmode = ('SlowRef', 'SlowRefSync', 'FastRef', 'RmpWfm', 'MigWfm', 'Cycle')
ps_cmdack = ('OK', 'Local', 'PCHost', 'Interlocked', 'UDC_locked',
             'DSP_TimeOut', 'DSP_Busy', 'Invalid',)
ps_soft_interlock = ('Reserved', 'Reserved',
                     'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     )
ps_hard_interlock = ('Falha na fonte 1', 'Falha na fonte 2',
                     'Falha na fonte 3', 'Sensor de fumaça',
                     'Interlock externo', 'Sobre-tensão na fonte 1',
                     'Sobre-tensão na fonte 2', 'Sobre-tensão na fonte 3',
                     'Sub-tensão na fonte 1', 'Sub-tensão na fonte 2',
                     'Sub-tensão na fonte 3', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',
                     'Reserved', 'Reserved', 'Reserved', 'Reserved',)

# --- power supply constants definition class ---


class Const:
    """Const class defining power supply constants."""

    @staticmethod
    def _init():
        """Create class constants."""
        for i in range(len(ps_models)):
            Const._add_const('Models', ps_models[i], i)
        for i in range(len(ps_dsblenbl)):
            Const._add_const('DsblEnbl', ps_dsblenbl[i], i)
        for i in range(len(ps_interface)):
            Const._add_const('Interface', ps_interface[i], i)
        for i in range(len(ps_openloop)):
            Const._add_const('Openloop', ps_openloop[i], i)
        for i in range(len(ps_states)):
            Const._add_const('States', ps_states[i], i)
        for i in range(len(ps_pwrstate_sel)):
            Const._add_const('PwrState', ps_pwrstate_sel[i], i)
        for i in range(len(ps_opmode)):
            Const._add_const('OpMode', ps_opmode[i], i)
        for i in range(len(ps_cmdack)):
            Const._add_const('CmdAck', ps_cmdack[i], i)

    @staticmethod
    def _add_const(group, const, i):
        if not hasattr(Const, group):
            setattr(Const, group, _namedtuple(group, ''))
        obj = getattr(Const, group)
        setattr(obj, const, i)


Const._init()


# --- power supply databases ---
def get_ps_current_unit():
    """Return power supply current unit."""
    global _default_ps_current_unit
    if _default_ps_current_unit is None:
        _default_ps_current_unit = _PSSearch.get_splims_unit(ispulsed=False)
    return _default_ps_current_unit


def get_pu_current_unit():
    """Return pulsed power supply 'current' unit."""
    global _default_pu_current_unit
    if _default_pu_current_unit is None:
        _default_pu_current_unit = _PSSearch.get_splims_unit(ispulsed=True)
    return _default_pu_current_unit


def get_common_propty_database():
    """Return database entries to all power-supply-like devices."""
    db = {
        'Version-Cte':      {'type': 'str', 'value': 'UNDEF'},
        'CtrlMode-Mon':     {'type': 'enum', 'enums': ps_interface,
                             'value': _et.idx.Remote},
        'PwrState-Sel':     {'type': 'enum', 'enums': ps_pwrstate_sel,
                             'value': _et.idx.Off},
        'PwrState-Sts':     {'type': 'enum', 'enums': ps_pwrstate_sts,
                             'value': _et.idx.Off},
        'IntlkSoft-Mon':    {'type': 'int',    'value': 0},
        'IntlkHard-Mon':    {'type': 'int',    'value': 0},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(ps_soft_interlock),
                                 'value': ps_soft_interlock},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(ps_hard_interlock),
                                 'value': ps_hard_interlock},
        'Reset-Cmd': {'type': 'int', 'value': 0},
    }
    return db


def get_common_ps_propty_database():
    """Return database of commun to all pwrsupply PVs."""
    db = get_common_propty_database()
    db_ps = {
        'OpMode-Sel': {'type': 'enum', 'enums': ps_opmode,
                       'value': _et.idx.SlowRef},
        'OpMode-Sts': {'type': 'enum', 'enums': ps_opmode,
                       'value': _et.idx.SlowRef},
        'Abort-Cmd': {'type': 'int', 'value': 0},
        'WfmIndex-Mon': {'type': 'int', 'value': 0},
        # 'WfmLabels-Mon': {'type': 'string', 'count': len(default_wfmlabels),
        #                   'value': default_wfmlabels},
        # 'WfmLabel-SP': {'type': 'string', 'value': default_wfmlabels[0]},
        # 'WfmLabel-RB': {'type': 'string', 'value': default_wfmlabels[0]},
        # 'WfmLoad-Sel': {'type': 'enum', 'enums': default_wfmlabels,
        #                 'value': 0},
        # 'WfmLoad-Sts': {'type': 'enum', 'enums': default_wfmlabels,
        #                 'value': 0},
        'WfmData-SP': {'type': 'float', 'count': default_wfmsize,
                       'prec': default_ps_current_precision,
                       'value': [0.0 for datum in range(default_wfmsize)]},
        'WfmData-RB': {'type': 'float', 'count': default_wfmsize,
                       'prec': default_ps_current_precision,
                       'value': [0.0 for datum in range(default_wfmsize)]},
        # 'WfmSave-Cmd': {'type': 'int', 'value': 0},
        'Current-SP': {'type': 'float', 'value': 0.0,
                       'prec': default_ps_current_precision},
        'Current-RB': {'type': 'float', 'value': 0.0,
                       'prec': default_ps_current_precision},
        'CurrentRef-Mon': {'type': 'float', 'value': 0.0,
                           'prec': default_ps_current_precision},
        'Current-Mon': {'type': 'float',  'value': 0.0,
                        'prec': default_ps_current_precision},
    }
    db.update(db_ps)
    return db


def get_common_pu_propty_database():
    """Return database of commun to all pulsed pwrsupply PVs."""
    db = get_common_propty_database()
    db_p = {'type': 'enum', 'enums': _et.enums('DsblEnblTyp'),
            'value': _et.idx.Dsbl}
    db_v = {'type': 'float', 'value': 0.0,
            'prec': default_pu_current_precision}
    db_pu = {
        'Pulsed-Sel': _copy.deepcopy(db_p),
        'Pulsed-Sts': _copy.deepcopy(db_p),
        'Voltage-SP': _copy.deepcopy(db_v),
        'Voltage-RB': _copy.deepcopy(db_v),
        'Voltage-Mon': _copy.deepcopy(db_v),
    }
    db.update(db_pu)
    return db


def get_ps_propty_database(pstype):
    """Return property database of a LNLS power supply type device."""
    propty_db = get_common_ps_propty_database()
    signals_lims = ('Current-SP', 'Current-RB',
                    'CurrentRef-Mon', 'Current-Mon', )
    signals_unit = signals_lims + ('WfmData-SP', 'WfmData-RB')
    for propty, db in propty_db.items():
        # set setpoint limits in database
        if propty in signals_lims:
            db['lolo'] = _PSSearch.get_splims(pstype, 'lolo')
            db['low'] = _PSSearch.get_splims(pstype, 'low')
            db['lolim'] = _PSSearch.get_splims(pstype, 'lolim')
            db['hilim'] = _PSSearch.get_splims(pstype, 'hilim')
            db['high'] = _PSSearch.get_splims(pstype, 'high')
            db['hihi'] = _PSSearch.get_splims(pstype, 'hihi')
        # define unit of current
        if propty in signals_unit:
            db['unit'] = get_ps_current_unit()
    return propty_db


def get_pu_propty_database(pstype):
    """Return database definition for a pulsed power supply type."""
    propty_db = get_common_pu_propty_database()
    signals_lims = ('Voltage-SP', 'Voltage-RB', 'Voltage-Mon')
    signals_unit = signals_lims
    for propty, db in propty_db.items():
        # set setpoint limits in database
        if propty in signals_lims:
            db['lolo'] = _PSSearch.get_splims(pstype, 'lolo')
            db['low'] = _PSSearch.get_splims(pstype, 'low')
            db['lolim'] = _PSSearch.get_splims(pstype, 'lolim')
            db['hilim'] = _PSSearch.get_splims(pstype, 'hilim')
            db['high'] = _PSSearch.get_splims(pstype, 'high')
            db['hihi'] = _PSSearch.get_splims(pstype, 'hihi')
        # define unit of current
        if propty in signals_unit:
            db['unit'] = get_ps_current_unit()
    return propty_db


def get_ma_propty_database(maname):
    """Return property database of a magnet type device."""
    current_alarm = ('Current-SP', 'Current-RB',
                     'CurrentRef-Mon', 'Current-Mon', )
    current_pvs = current_alarm  # + ('WfmData-SP', 'WfmData-RB')
    propty_db = get_common_ps_propty_database()
    unit = _MASearch.get_splims_unit(ispulsed=False)
    magfunc_dict = _MASearch.conv_maname_2_magfunc(maname)
    db = {}

    for psname, magfunc in magfunc_dict.items():
        db[psname] = _copy.deepcopy(propty_db)
        # set appropriate PS limits and unit
        for field in ["-SP", "-RB", "Ref-Mon", "-Mon"]:
            db[psname]['Current' + field]['lolo'] = \
                _MASearch.get_splims(maname, 'lolo')
            db[psname]['Current' + field]['low'] = \
                _MASearch.get_splims(maname, 'low')
            db[psname]['Current' + field]['lolim'] = \
                _MASearch.get_splims(maname, 'lolim')
            db[psname]['Current' + field]['hilim'] = \
                _MASearch.get_splims(maname, 'hilim')
            db[psname]['Current' + field]['high'] = \
                _MASearch.get_splims(maname, 'high')
            db[psname]['Current' + field]['hihi'] = \
                _MASearch.get_splims(maname, 'hihi')
        for propty in current_pvs:
            db[psname][propty]['unit'] = unit[0]
        # set approriate MA limits and unit
        if magfunc in ('quadrupole', 'quadrupole-skew'):
            strength_name = 'KL'
            unit = '1/m'
        elif magfunc == 'sextupole':
            strength_name = 'SL'
            unit = '1/m^2'
        elif magfunc == 'dipole':
            strength_name = 'Energy'
            unit = 'Gev'
        elif magfunc in ('corrector-vertical', 'corrector-horizontal'):
            strength_name = 'Kick'
            unit = 'rad'

        db[psname][strength_name + '-SP'] = \
            _copy.deepcopy(db[psname]['Current-SP'])
        db[psname][strength_name + '-SP']['unit'] = unit
        db[psname][strength_name + '-RB'] = \
            _copy.deepcopy(db[psname]['Current-RB'])
        db[psname][strength_name + '-RB']['unit'] = unit
        db[psname][strength_name + 'Ref-Mon'] = \
            _copy.deepcopy(db[psname]['CurrentRef-Mon'])
        db[psname][strength_name + 'Ref-Mon']['unit'] = unit
        db[psname][strength_name + '-Mon'] = \
            _copy.deepcopy(db[psname]['Current-Mon'])
        db[psname][strength_name + '-Mon']['unit'] = unit

        for field in ["-SP", "-RB", "Ref-Mon", "-Mon"]:
            db[psname][strength_name + field]['lolo'] = 0.0
            db[psname][strength_name + field]['low'] = 0.0
            db[psname][strength_name + field]['lolim'] = 0.0
            db[psname][strength_name + field]['hilim'] = 0.0
            db[psname][strength_name + field]['high'] = 0.0
            db[psname][strength_name + field]['hihi'] = 0.0

    return db


def get_pm_propty_database(maname):
    """Return property database of a pulsed magnet type device."""
    propty_db = get_common_pu_propty_database()
    current_alarm = ('Voltage-SP', 'Voltage-RB', 'Voltage-Mon', )
    unit = _MASearch.get_splims_unit(ispulsed=True)
    magfunc_dict = _MASearch.conv_maname_2_magfunc(maname)
    db = {}
    for psname, magfunc in magfunc_dict.items():
        db[psname] = _copy.deepcopy(propty_db)
        # set appropriate PS limits and unit
        for field in ["-SP", "-RB", "-Mon"]:
            db[psname]['Voltage' + field]['lolo'] = \
                _MASearch.get_splims(maname, 'lolo')
            db[psname]['Voltage' + field]['low'] = \
                _MASearch.get_splims(maname, 'low')
            db[psname]['Voltage' + field]['lolim'] = \
                _MASearch.get_splims(maname, 'lolim')
            db[psname]['Voltage' + field]['hilim'] = \
                _MASearch.get_splims(maname, 'hilim')
            db[psname]['Voltage' + field]['high'] = \
                _MASearch.get_splims(maname, 'high')
            db[psname]['Voltage' + field]['hihi'] = \
                _MASearch.get_splims(maname, 'hihi')
        for propty in current_alarm:
            db[psname][propty]['unit'] = unit[0]
        # set approriate MA limits and unit
        if magfunc in ('corrector-vertical', 'corrector-horizontal'):
            db[psname]['Kick-SP'] = _copy.deepcopy(db[psname]['Voltage-SP'])
            db[psname]['Kick-SP']['unit'] = 'rad'
            db[psname]['Kick-RB'] = _copy.deepcopy(db[psname]['Voltage-RB'])
            db[psname]['Kick-RB']['unit'] = 'rad'
            db[psname]['Kick-Mon'] = _copy.deepcopy(db[psname]['Voltage-Mon'])
            db[psname]['Kick-Mon']['unit'] = 'rad'

            for field in ["-SP", "-RB", "-Mon"]:
                db[psname]['Kick' + field]['lolo'] = 0.0
                db[psname]['Kick' + field]['low'] = 0.0
                db[psname]['Kick' + field]['lolim'] = 0.0
                db[psname]['Kick' + field]['hilim'] = 0.0
                db[psname]['Kick' + field]['high'] = 0.0
                db[psname]['Kick' + field]['hihi'] = 0.0
        else:
            raise ValueError('Invalid pulsed magnet power supply type!')
    return db
