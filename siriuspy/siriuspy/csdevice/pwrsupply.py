"""Power Supply Control System Devices."""

import copy as _copy

from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.search import MASearch as _MASearch
from siriuspy.pwrsupply.siggen import DEFAULT_SIGGEN_CONFIG as _DEF_SIGG_CONF
from siriuspy.csdevice.const import Const

MAX_WFMSIZE = 4000
DEFAULT_SIGGEN_CONFIG = _DEF_SIGG_CONF
DEFAULT_WFMDATA = (0.0, ) * MAX_WFMSIZE

default_ps_current_precision = 4
default_pu_current_precision = 4
_default_ps_current_unit = None
_default_pu_current_unit = None

# TODO: cleanup this module !!!!
# TODO: Add properties to power EPICS supply devices:
# DSPLoop-Mon: 'Off', 'On'

# --- power supply enums ---

ps_models = ('Empty',
             'FBP', 'FBP_DCLink',
             'FAC_ACDC', 'FAC_DCDC',
             'FAC_2S_ACDC', 'FAC_2S_DCDC',
             'FAC_2P4S_ACDC', 'FAC_2P4S_DCDC',
             'FAP',
             'FAP_4P_Master', 'FAP_4P_Slave',
             'FAP_2P2S_MASTER', 'FAP_2P2S_SLAVE',
             'FBP_SOFB',
             'Commercial',
             'FP')
ps_dsblenbl = ('Dsbl', 'Enbl')
ps_interface = ('Remote', 'Local', 'PCHost')
ps_openloop = ('Close', 'Open')
ps_pwrstate_sel = ('Off', 'On')
ps_pwrstate_sts = ('Off', 'On', 'Initializing')
ps_states = ('Off', 'Interlock', 'Initializing',
             'SlowRef', 'SlowRefSync', 'Cycle', 'RmpWfm', 'MigWfm', 'FastRef')
ps_opmode = ('SlowRef', 'SlowRefSync', 'Cycle', 'RmpWfm', 'MigWfm', 'FastRef')
ps_cmdack = ('OK', 'Local', 'PCHost', 'Interlocked', 'UDC_locked',
             'DSP_TimeOut', 'DSP_Busy', 'Invalid',)
ps_soft_interlock_FBP = (
    'Sobre-temperatura no módulo', 'Reserved',
    'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',)
ps_hard_interlock_FBP = (
    'Sobre-corrente na carga', 'Sobre-tensão na carga',
    'Sobre-tensão no DC-Link', 'Sub-tensão no DC-Link',
    'Falha no relé de entrada do DC-Link',
    'Falha no fusível de entrada do DC-Link',
    'Falha nos drivers do módulo', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',)
ps_soft_interlock_FBP_DCLink = (
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',)
ps_hard_interlock_FBP_DCLink = (
    'Falha na fonte 1', 'Falha na fonte 2',
    'Falha na fonte 3', 'Sobre-tensão da saída do bastidor DC-Link',
    'Sobre-tensão da fonte 1', 'Sobre-tensão na fonte 2',
    'Sobre-tensão na fonte 3', 'Sub-tensão da saída do bastidor DC-Link',
    'Sub-tensão na fonte 1', 'Sub-tensão na fonte 2',
    'Sub-tensão na fonte 3', 'Sensor de fumaça',
    'Interlock externo', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',)
ps_soft_interlock_FAC = (
    'Sobre-temperatura nos indutores',  'Sobre-temperatura nos indutores',
    'Falha no DCCT 1', 'Falha no DCCT 2',
    'Alta diferença entre DCCTs',
    'Falha na leitura da corrente na carga do DCCT 1',
    'Falha na leitura da corrente na carga do DCCT 2', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',)
ps_hard_interlock_FAC = (
    'Sobre-corrente na carga', 'Sobre-corrente na carga',
    'Sobre-tensão no DC-Link', 'Sub-tensão no DC-Link',
    'Falha nos drivers do módulo', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',)
ps_soft_interlock_FAC_ACDC = (
    'Sobre-temperatura no dissipador', 'Sobre-temperatura nos indutores',
    'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',)
ps_hard_interlock_FAC_ACDC = (
    'Sobre-tensão no banco de capacitores',
    'Sobre-tensão na saída do retificador',
    'Sub-tensão na saída do retificador',
    'Sobre-corrente na saída do retificador',
    'Falha no driver do IGBT', 'Falha no contator de entrada AC trifásica',
    'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',
    'Reserved', 'Reserved', 'Reserved', 'Reserved',)
ps_cycle_type = ('Sine', 'DampedSine', 'Trapezoidal')
ps_sync_mode = ('Off', 'Cycle', 'RmpEnd', 'MigEnd')


# --- power supply constants definition class ---

Const.add_field('Models', ps_models)
Const.add_field('DsblEnbl', ps_dsblenbl)
Const.add_field('Interface', ps_interface)
Const.add_field('OpenLoop', ps_openloop)
Const.add_field('States', ps_states)
Const.add_field('PwrState', ps_pwrstate_sel)
Const.add_field('OpMode', ps_opmode)
Const.add_field('CmdAck', ps_cmdack)
Const.add_field('CycleType', ps_cycle_type)
Const.add_field('SyncMode', ps_sync_mode)

# --- power supply databases ---


def get_ps_current_unit():
    """Return power supply current unit."""
    global _default_ps_current_unit
    if _default_ps_current_unit is None:
        _default_ps_current_unit = _PSSearch.get_splims_unit('FBP')
    return _default_ps_current_unit


def get_pu_current_unit():
    """Return pulsed power supply 'current' unit."""
    global _default_pu_current_unit
    if _default_pu_current_unit is None:
        _default_pu_current_unit = _PSSearch.get_splims_unit('')
    return _default_pu_current_unit


def get_basic_propty_database():
    """Return database entries to all BSMP-like devices."""
    db = {
        'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
        'CtrlMode-Mon': {'type': 'enum', 'enums': ps_interface,
                         'value': _et.idx.Remote},
        # Common Variables
        'PwrState-Sel': {'type': 'enum', 'enums': ps_pwrstate_sel,
                         'value': _et.idx.Off},
        'PwrState-Sts': {'type': 'enum', 'enums': ps_pwrstate_sts,
                         'value': _et.idx.Off},
        'CtrlLoop-Sel': {'type': 'enum', 'enums': ps_openloop,
                         'value': Const.OpenLoop.Open},
        'CtrlLoop-Sts': {'type': 'enum', 'enums': ps_openloop,
                         'value': Const.OpenLoop.Open},
        'OpMode-Sel': {'type': 'enum', 'enums': ps_opmode,
                       'value': _et.idx.SlowRef},
        'OpMode-Sts': {'type': 'enum', 'enums': ps_opmode,
                       'value': _et.idx.SlowRef},
        # PRU
        'PRUSyncMode-Mon': {'type': 'enum', 'enums': ps_sync_mode,
                            'value': Const.SyncMode.Off},
        'PRUBlockIndex-Mon': {'type': 'int', 'value': 0},
        'PRUSyncPulseCount-Mon': {'type': 'int', 'value': 0},
        'PRUCtrlQueueSize-Mon': {'type': 'int', 'value': 0,
                                 'high': 50, 'hihi': 50},
        # Interlocks
        'IntlkSoft-Mon':    {'type': 'int',    'value': 0},
        'IntlkHard-Mon':    {'type': 'int',    'value': 0},

        'Reset-Cmd': {'type': 'int', 'value': 0},

    }
    return db


def get_common_propty_database():
    """Return database entries to all power-supply-like devices."""
    db = get_basic_propty_database()
    db.update({
        'Current-SP': {'type': 'float', 'value': 0.0,
                       'prec': default_ps_current_precision},
        'Current-RB': {'type': 'float', 'value': 0.0,
                       'prec': default_ps_current_precision},
        'CurrentRef-Mon': {'type': 'float', 'value': 0.0,
                           'prec': default_ps_current_precision},
        'Current-Mon': {'type': 'float',  'value': 0.0,
                        'prec': default_ps_current_precision},
        # Commands
        'Abort-Cmd': {'type': 'int', 'value': 0},
        # Cycle
        'CycleEnbl-Mon': {'type': 'int', 'value': 0},
        'CycleType-Sel': {'type': 'enum', 'enums': ps_cycle_type,
                          'value': DEFAULT_SIGGEN_CONFIG[0]},
        'CycleType-Sts': {'type': 'enum', 'enums': ps_cycle_type,
                          'value': DEFAULT_SIGGEN_CONFIG[0]},
        'CycleNrCycles-SP': {'type': 'int', 'value': DEFAULT_SIGGEN_CONFIG[1]},
        'CycleNrCycles-RB': {'type': 'int', 'value': DEFAULT_SIGGEN_CONFIG[1]},
        'CycleFreq-SP': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[2],
                         'unit': 'Hz', 'prec': 4},
        'CycleFreq-RB': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[2],
                         'unit': 'Hz', 'prec': 4},
        'CycleAmpl-SP': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[3]},
        'CycleAmpl-RB': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[3]},
        'CycleOffset-SP': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[4]},
        'CycleOffset-RB': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[4]},
        'CycleAuxParam-SP': {'type': 'float', 'count': 4,
                             'value': DEFAULT_SIGGEN_CONFIG[5:9]},
        'CycleAuxParam-RB': {'type': 'float', 'count': 4,
                             'value': DEFAULT_SIGGEN_CONFIG[5:9]},
        'CycleIndex-Mon': {'type': 'int', 'value': 0},
        # Wfm
        'WfmIndex-Mon': {'type': 'int', 'value': 0},
        'WfmData-SP': {'type': 'float', 'count': MAX_WFMSIZE,
                       'value': list(DEFAULT_WFMDATA),
                       'prec': default_ps_current_precision},
        'WfmData-RB': {'type': 'float', 'count': MAX_WFMSIZE,
                       'value': list(DEFAULT_WFMDATA),
                       'prec': default_ps_current_precision},
    })
    return db


def get_common_pu_propty_database():
    """Return database of common to all pulsed pwrsupply PVs."""
    # S TB-04:PU-InjSept
    # S TS-01:PU-EjeSeptF
    # S TS-01:PU-EjeSeptG
    # S TS-04:PU-InjSeptG-1
    # S TS-04:PU-InjSeptG-2
    # S TS-04:PU-InjSeptF
    # K BO-01D:PU-InjKckr
    # K BO-48D:PU-EjeKckr
    # K SI-01SA:PU-InjDpKckr
    # P SI-19C4:PU-PingV
    db = {
        'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
        'CtrlMode-Mon': {'type': 'enum', 'enums': ps_interface,
                         'value': _et.idx.Remote},
        'PwrState-Sel': {'type': 'enum', 'enums': ps_pwrstate_sel,
                         'value': _et.idx.Off},
        'PwrState-Sts': {'type': 'enum', 'enums': ps_pwrstate_sts,
                         'value': _et.idx.Off},
        'Reset-Cmd': {'type': 'int', 'value': 0},
        'Pulse-Sel': {'type': 'enum', 'enums': _et.enums('DsblEnblTyp'),
                      'value': _et.idx.Dsbl},
        # 'Pulse-Sts': {'type': 'enum', 'enums': _et.enums('DsblEnblTyp'),
        #               'value': _et.idx.Dsbl},
        'Voltage-SP': {'type': 'float', 'value': 0.0,
                       'prec': default_pu_current_precision},
        'Voltage-RB': {'type': 'float', 'value': 0.0,
                       'prec': default_pu_current_precision},
        'Voltage-Mon': {'type': 'float', 'value': 0.0,
                        'prec': default_pu_current_precision},
        'Intlk1-Mon': {'type': 'int', 'value': 0},
        'Intlk2-Mon': {'type': 'int', 'value': 0},
        'Intlk3-Mon': {'type': 'int', 'value': 0},
        'Intlk4-Mon': {'type': 'int', 'value': 0},
        'Intlk5-Mon': {'type': 'int', 'value': 0},
        'Intlk6-Mon': {'type': 'int', 'value': 0},
        'Intlk1Label-Cte': {'type': 'str', 'value': 'Intlk1'},
        'Intlk2Label-Cte': {'type': 'str', 'value': 'Intlk2'},
        'Intlk3Label-Cte': {'type': 'str', 'value': 'Intlk3'},
        'Intlk4Label-Cte': {'type': 'str', 'value': 'Intlk4'},
        'Intlk5Label-Cte': {'type': 'str', 'value': 'Intlk5'},
        'Intlk6Label-Cte': {'type': 'str', 'value': 'Intlk6'},
    }
    return db


def get_common_pu_SI_InjKicker_propty_database():
    """Return database of SI injection kicker."""
    # K SI-01SA:PU-InjNLKckr
    db = get_common_pu_propty_database()
    # 'Comissioning': On-Axis magnet
    # 'Accumulation': Non-linear kicker
    db.update({
        'OpMode-Sel': {'type': 'enum',
                       'enums': ['Comissioning', 'Accumulation'],
                       'value': 0},
        'OpMode-Sts': {'type': 'enum',
                       'enums': ['Comissioning', 'Accumulation'],
                       'value': 0},
    })


def get_ps_propty_database(psmodel, pstype):
    """Return property database of a LNLS power supply type device."""
    propty_db = _get_model_db(psmodel)
    _set_limits(pstype, propty_db)
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
    psnames = _MASearch.conv_psmaname_2_psnames(maname)
    psmodel = _PSSearch.conv_psname_2_psmodel(psnames[0])
    unit = _MASearch.get_splims_unit(psmodel=psmodel)
    magfunc_dict = _MASearch.conv_maname_2_magfunc(maname)
    pstype = _PSSearch.conv_psname_2_pstype(psnames[0])
    propty_db = get_ps_propty_database(psmodel, pstype)
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
    if 'InjNLKckr' in maname or 'InjDipKckr' in maname:
        propty_db = get_common_pu_SI_InjKicker_propty_database()
    else:
        propty_db = get_common_pu_propty_database()

    psnames = _MASearch.conv_psmaname_2_psnames(maname)
    psmodel = _PSSearch.conv_psname_2_psmodel(psnames[0])
    current_alarm = ('Voltage-SP', 'Voltage-RB', 'Voltage-Mon', )
    unit = _MASearch.get_splims_unit(psmodel=psmodel)
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


# Hidden
def _get_ps_FBP_propty_database():
    """Return database with FBP pwrsupply model PVs."""
    propty_db = get_common_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(ps_soft_interlock_FBP),
                                 'value': ps_soft_interlock_FBP},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(ps_hard_interlock_FBP),
                                 'value': ps_hard_interlock_FBP},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FBP_DCLink_propty_database():
    """Return database with FBP_DCLink pwrsupply model PVs."""
    propty_db = get_basic_propty_database()
    db_ps = {
        'Voltage-SP': {'type': 'float', 'value': 0.0,
                       'lolim': 0.0, 'hilim': 100.0, 'prec': 4},
        'Voltage-RB': {'type': 'float', 'value': 0.0,
                       'lolim': 0.0, 'hilim': 100.0, 'prec': 4},
        'VoltageRef-Mon': {'type': 'float', 'value': 0.0,
                           'lolim': 0.0, 'hilim': 100.0, 'prec': 4},
        'Voltage-Mon': {'type': 'float', 'value': 0.0, 'prec': 4},
        'Voltage1-Mon': {'type': 'float', 'value': 0.0, 'prec': 4},
        'Voltage2-Mon': {'type': 'float', 'value': 0.0, 'prec': 4},
        'Voltage3-Mon': {'type': 'float', 'value': 0.0, 'prec': 4},
        'VoltageDig-Mon': {'type': 'int', 'value': 0,
                           'lolim': 0, 'hilim': 255},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(ps_soft_interlock_FBP_DCLink),
                                 'value': ps_soft_interlock_FBP_DCLink},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(ps_hard_interlock_FBP_DCLink),
                                 'value': ps_hard_interlock_FBP_DCLink},
        'ModulesStatus-Mon': {'type': 'int', 'value': 0},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_propty_database():
    """Return database with FAC pwrsupply model PVs."""
    # TODO: implement!!!
    propty_db = get_common_propty_database()
    db_ps = {
        'Current2-Mon': {'type': 'float',  'value': 0.0,
                         'prec': default_ps_current_precision},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(ps_soft_interlock_FAC),
                                 'value': ps_soft_interlock_FAC},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(ps_hard_interlock_FAC),
                                 'value': ps_hard_interlock_FAC},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_ACDC_propty_database():
    """Return database with FAC_ACDC pwrsupply model PVs."""
    # TODO: MISSING SETPOINT!!!
    db = {
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(ps_soft_interlock_FAC_ACDC),
                                 'value': ps_soft_interlock_FAC_ACDC},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(ps_hard_interlock_FAC_ACDC),
                                 'value': ps_hard_interlock_FAC_ACDC},
        'CapacitorBankVoltage-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': default_ps_current_precision},
        'RectifierVoltage-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': default_ps_current_precision},
        'RectifierCurrent-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': default_ps_current_precision},
        'HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': default_ps_current_precision},
        'InductorsTemperature-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': default_ps_current_precision},
        'PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': default_ps_current_precision},
    }
    return db


def _get_ps_FAC_2S_propty_database():
    """Return database with FAC_2S pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_FAC_2P4S_propty_database():
    """Return database with FAC_2P4S pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_FAP_propty_database():
    """Return database with FAP pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_FAP_4P_propty_database():
    """Return database with FAP_4P pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_FAP_2P2S_propty_database():
    """Return database with FAP_2P2S pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_FBP_FOFB_propty_database():
    """Return database with FBP_FOFB pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_Commercial_propty_database():
    """Return database with Commercial pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _set_limits(pstype, database):
    signals_lims = ('Current-SP', 'Current-RB',
                    'CurrentRef-Mon', 'Current-Mon', 'Current2-Mon'
                    'CycleAmpl-SP', 'CycleAmpl-RB',
                    'CycleOffset-SP', 'CycleOffset-RB',
                    )
    # TODO: define limits to WfmData as well!
    signals_unit = signals_lims + (
        'WfmData-SP', 'WfmData-RB',
    )
    signals_prec = signals_unit

    for propty, db in database.items():
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
        # define prec of current
        if propty in signals_prec:
            db['prec'] = default_ps_current_precision,


def _get_model_db(psmodel):
    if psmodel == 'FBP':
        database = _get_ps_FBP_propty_database()
    elif psmodel in ('FBP_DCLink'):
        database = _get_ps_FBP_DCLink_propty_database()
    elif psmodel in ('FAC'):
        database = _get_ps_FAC_propty_database()
    elif psmodel in ('FAC_2S_DCDC'):
        database = _get_ps_FAC_2S_propty_database()
    elif psmodel in ('FAC_2P4S_DCDC'):
        database = _get_ps_FAC_2P4S_propty_database()
    elif psmodel in ('FAP'):
        database = _get_ps_FAP_propty_database()
    elif psmodel in ('FAP_4P'):
        database = _get_ps_FAP_4P_propty_database()
    elif psmodel in ('FAP_2P2S'):
        database = _get_ps_FAP_2P2S_propty_database()
    elif psmodel in ('FBP_FOFB'):
        database = _get_ps_FBP_FOFB_propty_database()
    elif psmodel in ('Commercial'):
        database = _get_ps_Commercial_propty_database()
    elif psmodel in ('FAC_ACDC'):
        database = _get_ps_FAC_ACDC_propty_database()
    else:
        raise ValueError(
            'DB for psmodel {} not implemented!'.format(psmodel))
    return database
