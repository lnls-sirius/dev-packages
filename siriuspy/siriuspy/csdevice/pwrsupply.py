"""Power Supply Control System Devices."""

import copy as _copy

from siriuspy.search import PSSearch as _PSSearch
from siriuspy.search import MASearch as _MASearch
from siriuspy.pwrsupply.siggen import DEFAULT_SIGGEN_CONFIG as _DEF_SIGG_CONF
from siriuspy.csdevice import util as _cutil


# MIN_WFMSIZE = 2001
MAX_WFMSIZE = 4000
DEFAULT_SIGGEN_CONFIG = _DEF_SIGG_CONF
DEFAULT_WFMDATA = (0.0, ) * MAX_WFMSIZE

default_ps_current_precision = 4
default_pu_current_precision = 4
_default_ps_current_unit = None
_default_pu_current_unit = None


# --- Enumeration Types ---

class ETypes(_cutil.ETypes):
    """Local enumerate types."""

    INTERFACE = ('Remote', 'Local', 'PCHost')
    MODELS = ('Empty',
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
    PWRSTATE_SEL = _cutil.ETypes.OFF_ON
    PWRSTATE_STS = ('Off', 'On', 'Initializing')
    STATES = ('Off', 'Interlock', 'Initializing',
              'SlowRef', 'SlowRefSync', 'Cycle', 'RmpWfm', 'MigWfm', 'FastRef')
    OPMODES = ('SlowRef', 'SlowRefSync', 'Cycle',
               'RmpWfm', 'MigWfm', 'FastRef')
    CMD_ACK = ('OK', 'Local', 'PCHost', 'Interlocked', 'UDC_locked',
               'DSP_TimeOut', 'DSP_Busy', 'Invalid',)
    SOFT_INTLCK_FBP = (
        'Sobre-temperatura no módulo', 'Reserved',
        'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',)
    HARD_INTLCK_FBP = (
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
    SOFT_INTLCK_FBP_DCLINK = (
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',)
    HARD_INTLCK_FBP_DCLINK = (
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
    SOFT_INTLCK_FAC = (
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
    HARD_INTLCK_FAC = (
        'Sobre-corrente na carga', 'Sobre-tensão na carga',
        'Sobre-tensão no DC-Link', 'Sub-tensão no DC-Link',
        'Falha nos drivers do módulo', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',)
    SOFT_INTLCK_FAC_ACDC = (
        'Sobre-temperatura no dissipador', 'Sobre-temperatura nos indutores',
        'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',)
    HARD_INTLCK_FAC_ACDC = (
        'Sobre-tensão no banco de capacitores',
        'Sobre-tensão na saída do retificador',
        'Sub-tensão na saída do retificador',
        'Sobre-corrente na saída do retificador',
        'Falha no contator de entrada AC trifásica', 'Falha no driver do IGBT',
        'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',)
    SOFT_INTLCK_FAC_2P4S = (
        'Sobre-temperatura nos indutores',  'Sobre-temperatura nos IGBTs',
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
    HARD_INTLCK_FAC_2P4S = (
        'Sobre-corrente na carga', 'Sobre-tensão na carga',
        'Sobre-tensão no DC-Link do módulo 1',
        'Sobre-tensão no DC-Link do módulo 2',
        'Sobre-tensão no DC-Link do módulo 3',
        'Sobre-tensão no DC-Link do módulo 4',
        'Sobre-tensão no DC-Link do módulo 5',
        'Sobre-tensão no DC-Link do módulo 6',
        'Sobre-tensão no DC-Link do módulo 7',
        'Sobre-tensão no DC-Link do módulo 8',
        'Sub-tensão no DC-Link do módulo 1',
        'Sub-tensão no DC-Link do módulo 2',
        'Sub-tensão no DC-Link do módulo 3',
        'Sub-tensão no DC-Link do módulo 4',
        'Sub-tensão no DC-Link do módulo 5',
        'Sub-tensão no DC-Link do módulo 6',
        'Sub-tensão no DC-Link do módulo 7',
        'Sub-tensão no DC-Link do módulo 8',
        'Sobre-tensão na saída do módulo 1',
        'Sobre-tensão na saída do módulo 2',
        'Sobre-tensão na saída do módulo 3',
        'Sobre-tensão na saída do módulo 4',
        'Sobre-tensão na saída do módulo 5',
        'Sobre-tensão na saída do módulo 6',
        'Sobre-tensão na saída do módulo 7',
        'Sobre-tensão na saída do módulo 8',
        'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved',)
    SOFT_INTLCK_FAC_2P4S_ACDC = (
        'Sobre-temperatura no dissipador', 'Sobre-temperatura nos indutores',
        'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',)
    HARD_INTLCK_FAC_2P4S_ACDC = (
        'Sobre-tensão no banco de capacitores',
        'Sobre-tensão na saída do retificador',
        'Sub-tensão na saída do retificador',
        'Sobre-corrente na saída do retificador',
        'Falha no contator de entrada AC trifásica', 'Falha no driver do IGBT',
        'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',)
    SOFT_INTLCK_FAP = (
        'Falha no DCCT1', 'Falha no DCCT2',
        'Alta diferença entre DCCTs', 'Falha de leitura corrente DCCT1',
        'Falha de leitura corrente DCCT2', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',)
    HARD_INTLCK_FAP = (
        'Sobre-corrente na crga',
        'Sobre-tensão na carga',
        'Sobre-tensão no DCLink',
        'Sub-tensão no DCLink',
        'Sobre-corrente no IGBT1', 'Sobre-corrente no IGBT2',
        'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',
        'Reserved', 'Reserved', 'Reserved', 'Reserved',)
    CYCLE_TYPES = ('Sine', 'DampedSine', 'Trapezoidal')
    SYNC_MODES = ('Off', 'Cycle', 'RmpEnd', 'MigEnd')


_et = ETypes  # syntatic sugar


# --- Const class ---

class Const(_cutil.Const):
    """Const class defining power supply constants."""

    Models = _cutil.Const.register('Models', _et.MODELS)
    Interface = _cutil.Const.register('Interface', _et.INTERFACE)
    OpenLoop = _cutil.Const.register('OpenLoop', _et.CLOSE_OPEN)
    States = _cutil.Const.register('States', _et.STATES)
    PwrStateSel = _cutil.Const.register('PwrStateSel', _et.PWRSTATE_SEL)
    PwrStateSts = _cutil.Const.register('PwrStateSts', _et.PWRSTATE_STS)
    OpMode = _cutil.Const.register('OpMode', _et.OPMODES)
    CmdAck = _cutil.Const.register('CmdAck', _et.CMD_ACK)
    CycleType = _cutil.Const.register('CycleType', _et.CYCLE_TYPES)
    SyncMode = _cutil.Const.register('SyncMode', _et.SYNC_MODES)


# --- Power supply databases ---

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


def get_common_propty_database():
    """Return database entries to all BSMP-like devices."""
    db = {
        'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
        'CtrlMode-Mon': {'type': 'enum', 'enums': _et.INTERFACE,
                         'value': Const.Interface.Remote},
        # Common Variables
        'PwrState-Sel': {'type': 'enum', 'enums': _et.PWRSTATE_SEL,
                         'value': Const.PwrStateSel.Off},
        'PwrState-Sts': {'type': 'enum', 'enums': _et.PWRSTATE_STS,
                         'value': Const.PwrStateSts.Off},
        'CtrlLoop-Sel': {'type': 'enum', 'enums': _et.CLOSE_OPEN,
                         'value': Const.OpenLoop.Open},
        'CtrlLoop-Sts': {'type': 'enum', 'enums': _et.CLOSE_OPEN,
                         'value': Const.OpenLoop.Open},
        'OpMode-Sel': {'type': 'enum', 'enums': _et.OPMODES,
                       'value': Const.OpMode.SlowRef},
        'OpMode-Sts': {'type': 'enum', 'enums': _et.OPMODES,
                       'value': Const.OpMode.SlowRef},
        # PRU
        'PRUSyncMode-Mon': {'type': 'enum', 'enums': _et.SYNC_MODES,
                            'value': Const.SyncMode.Off},
        'PRUBlockIndex-Mon': {'type': 'int', 'value': 0},
        'PRUSyncPulseCount-Mon': {'type': 'int', 'value': 0},
        'PRUCtrlQueueSize-Mon': {'type': 'int', 'value': 0,
                                 'high': 50, 'hihi': 50},
        # BSMPComm
        'BSMPComm-Sel': {'type': 'enum', 'enums': _et.PWRSTATE_SEL,
                         'value': Const.PwrStateSel.On},
        'BSMPComm-Sts': {'type': 'enum', 'enums': _et.PWRSTATE_STS,
                         'value': Const.PwrStateSts.On},
        # Interlocks
        'IntlkSoft-Mon':    {'type': 'int',    'value': 0},
        'IntlkHard-Mon':    {'type': 'int',    'value': 0},

        'Reset-Cmd': {'type': 'int', 'value': 0},

    }
    return db


def get_basic_propty_database():
    """Return database entries to all power-supply-like devices."""
    db = get_common_propty_database()
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
        'CycleType-Sel': {'type': 'enum', 'enums': _et.CYCLE_TYPES,
                          'value': DEFAULT_SIGGEN_CONFIG[0]},
        'CycleType-Sts': {'type': 'enum', 'enums': _et.CYCLE_TYPES,
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
        'CtrlMode-Mon': {'type': 'enum', 'enums': _et.INTERFACE,
                         'value': Const.Interface.Remote},
        'PwrState-Sel': {'type': 'enum', 'enums': _et.PWRSTATE_SEL,
                         'value': Const.PwrStateSel.Off},
        'PwrState-Sts': {'type': 'enum', 'enums': _et.PWRSTATE_STS,
                         'value': Const.PwrStateSts.Off},
        'Reset-Cmd': {'type': 'int', 'value': 0},
        'Pulse-Sel': {'type': 'enum', 'enums': _et.DSBL_ENBL,
                      'value': Const.DsblEnbl.Dsbl},
        # 'Pulse-Sts': {'type': 'enum', 'enums': _et.DSBL_ENBL,
        #               'value': Const.DsbEnbl.Dsbl},
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
    database = _get_model_db(psmodel)
    _set_limits(pstype, database)
    # add pvs list
    database = _cutil.add_pvslist_cte(database)
    return database


def get_pu_propty_database(pstype):
    """Return database definition for a pulsed power supply type."""
    database = get_common_pu_propty_database()
    signals_lims = ('Voltage-SP', 'Voltage-RB', 'Voltage-Mon')
    signals_unit = signals_lims
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
    # add pvs list
    database = _cutil.add_pvslist_cte(database)
    return database


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
    database = get_ps_propty_database(psmodel, pstype)
    db = {}

    for psname, magfunc in magfunc_dict.items():
        db[psname] = _copy.deepcopy(database)
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
            unit = 'urad'

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

        # add pvs list
        db[psname] = _cutil.add_pvslist_cte(db[psname])

    return db


def get_pm_propty_database(maname):
    """Return property database of a pulsed magnet type device."""
    if 'InjNLKckr' in maname or 'InjDipKckr' in maname:
        database = get_common_pu_SI_InjKicker_propty_database()
    else:
        database = get_common_pu_propty_database()

    psnames = _MASearch.conv_psmaname_2_psnames(maname)
    psmodel = _PSSearch.conv_psname_2_psmodel(psnames[0])
    current_alarm = ('Voltage-SP', 'Voltage-RB', 'Voltage-Mon', )
    unit = _MASearch.get_splims_unit(psmodel=psmodel)
    magfunc_dict = _MASearch.conv_maname_2_magfunc(maname)
    db = {}
    for psname, magfunc in magfunc_dict.items():
        db[psname] = _copy.deepcopy(database)
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
            db[psname]['Kick-SP']['unit'] = 'mrad'
            db[psname]['Kick-RB'] = _copy.deepcopy(db[psname]['Voltage-RB'])
            db[psname]['Kick-RB']['unit'] = 'mrad'
            db[psname]['Kick-Mon'] = _copy.deepcopy(db[psname]['Voltage-Mon'])
            db[psname]['Kick-Mon']['unit'] = 'mrad'

            for field in ["-SP", "-RB", "-Mon"]:
                db[psname]['Kick' + field]['lolo'] = 0.0
                db[psname]['Kick' + field]['low'] = 0.0
                db[psname]['Kick' + field]['lolim'] = 0.0
                db[psname]['Kick' + field]['hilim'] = 0.0
                db[psname]['Kick' + field]['high'] = 0.0
                db[psname]['Kick' + field]['hihi'] = 0.0
        else:
            raise ValueError('Invalid pulsed magnet power supply type!')
        # add pvs list
        db[psname] = _cutil.add_pvslist_cte(db[psname])

    return db


# --- Auxiliary functions ---


def _get_ps_FBP_propty_database():
    """Return database with FBP pwrsupply model PVs."""
    propty_db = get_basic_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FBP),
                                 'value': _et.SOFT_INTLCK_FBP},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FBP),
                                 'value': _et.HARD_INTLCK_FBP},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FBP_DCLink_propty_database():
    """Return database with FBP_DCLink pwrsupply model PVs."""
    propty_db = get_common_propty_database()
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
                                 'count': len(_et.SOFT_INTLCK_FBP_DCLINK),
                                 'value': _et.SOFT_INTLCK_FBP_DCLINK},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FBP_DCLINK),
                                 'value': _et.HARD_INTLCK_FBP_DCLINK},
        'ModulesStatus-Mon': {'type': 'int', 'value': 0},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_propty_database():
    """Return database with FAC pwrsupply model PVs."""
    # TODO: implement!!!
    propty_db = get_basic_propty_database()
    db_ps = {
        'Current2-Mon': {'type': 'float',  'value': 0.0,
                         'prec': default_ps_current_precision},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAC),
                                 'value': _et.SOFT_INTLCK_FAC},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAC),
                                 'value': _et.HARD_INTLCK_FAC},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_ACDC_propty_database():
    """Return database with FAC_ACDC pwrsupply model PVs."""
    # TODO: MISSING SETPOINT!!!
    propty_db = get_common_propty_database()
    db_ps = {
        'CapacitorBankVoltage-SP': {'type': 'float', 'value': 0.0,
                                    'prec': default_ps_current_precision},
        'CapacitorBankVoltage-RB': {'type': 'float', 'value': 0.0,
                                    'prec': default_ps_current_precision},
        'CapacitorBankVoltageRef-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': default_ps_current_precision},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAC_ACDC),
                                 'value': _et.SOFT_INTLCK_FAC_ACDC},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAC_ACDC),
                                 'value': _et.HARD_INTLCK_FAC_ACDC},
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
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_2S_propty_database():
    """Return database with FAC_2S pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_FAC_2S_ACDC_propty_database():
    """Return database with FAC_2S pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FAC_ACDC_propty_database()


def _get_ps_FAC_2P4S_propty_database():
    """Return database with FAC_2P4S pwrsupply model PVs."""
    propty_db = get_basic_propty_database()
    db_ps = {
        'Current2-Mon': {'type': 'float',  'value': 0.0,
                         'prec': default_ps_current_precision},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAC_2P4S),
                                 'value': _et.SOFT_INTLCK_FAC_2P4S},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAC_2P4S),
                                 'value': _et.HARD_INTLCK_FAC_2P4S},
        'LoadVoltage-Mon': {'type': 'float', 'value': 0.0,
                            'prec': default_ps_current_precision,
                            'unit': 'V'},
        'CapacitorBank1Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': default_ps_current_precision,
                                      'unit': 'V'},
        'CapacitorBank2Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': default_ps_current_precision,
                                      'unit': 'V'},
        'CapacitorBank3Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': default_ps_current_precision,
                                      'unit': 'V'},
        'CapacitorBank4Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': default_ps_current_precision,
                                      'unit': 'V'},
        'CapacitorBank5Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': default_ps_current_precision,
                                      'unit': 'V'},
        'CapacitorBank6Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': default_ps_current_precision,
                                      'unit': 'V'},
        'CapacitorBank7Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': default_ps_current_precision,
                                      'unit': 'V'},
        'CapacitorBank8Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': default_ps_current_precision,
                                      'unit': 'V'},
        'Module1Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': default_ps_current_precision,
                               'unit': 'V'},
        'Module2Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': default_ps_current_precision,
                               'unit': 'V'},
        'Module3Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': default_ps_current_precision,
                               'unit': 'V'},
        'Module4Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': default_ps_current_precision,
                               'unit': 'V'},
        'Module5Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': default_ps_current_precision,
                               'unit': 'V'},
        'Module6Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': default_ps_current_precision,
                               'unit': 'V'},
        'Module7Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': default_ps_current_precision,
                               'unit': 'V'},
        'Module8Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': default_ps_current_precision,
                               'unit': 'V'},
        'PWMDutyCycle1-Mon': {'type': 'float', 'value': 0.0,
                              'prec': default_ps_current_precision},
        'PWMDutyCycle2-Mon': {'type': 'float', 'value': 0.0,
                              'prec': default_ps_current_precision},
        'PWMDutyCycle3-Mon': {'type': 'float', 'value': 0.0,
                              'prec': default_ps_current_precision},
        'PWMDutyCycle4-Mon': {'type': 'float', 'value': 0.0,
                              'prec': default_ps_current_precision},
        'PWMDutyCycle5-Mon': {'type': 'float', 'value': 0.0,
                              'prec': default_ps_current_precision},
        'PWMDutyCycle6-Mon': {'type': 'float', 'value': 0.0,
                              'prec': default_ps_current_precision},
        'PWMDutyCycle7-Mon': {'type': 'float', 'value': 0.0,
                              'prec': default_ps_current_precision},
        'PWMDutyCycle8-Mon': {'type': 'float', 'value': 0.0,
                              'prec': default_ps_current_precision},
        'Arm1Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': default_ps_current_precision,
                            'unit': 'A'},
        'Arm2Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': default_ps_current_precision,
                            'unit': 'A'}
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_2P4S_ACDC_propty_database():
    """Return database with FAC_2P4S pwrsupply model PVs."""
    propty_db = get_common_propty_database()
    db_ps = {
        'CapacitorBankVoltage-SP': {'type': 'float', 'value': 0.0,
                                    'prec': default_ps_current_precision,
                                    'lolim': 0.0, 'hilim': 1.0},
        'CapacitorBankVoltage-RB': {'type': 'float', 'value': 0.0,
                                    'prec': default_ps_current_precision},
        'CapacitorBankVoltageRef-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': default_ps_current_precision},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAC_2P4S_ACDC),
                                 'value': _et.SOFT_INTLCK_FAC_2P4S_ACDC},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAC_2P4S_ACDC),
                                 'value': _et.HARD_INTLCK_FAC_2P4S_ACDC},
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
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAP_propty_database():
    """Return database with FAP pwrsupply model PVs."""
    propty_db = get_basic_propty_database()
    db_ps = {
        'Current2-Mon': {'type': 'float',  'value': 0.0,
                         'prec': default_ps_current_precision},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAP),
                                 'value': _et.SOFT_INTLCK_FAP},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAP),
                                 'value': _et.HARD_INTLCK_FAP},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAP_4P_propty_database():
    """Return database with FAP_4P pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_FAP_2P2S_propty_database():
    """Return database with FAP_2P2S pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_FAP_4P_Master_propty_database():
    """Return database with FAP_2P2S pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_FAP_4P_Slave_propty_database():
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
    psmodel_2_dbfunc = {
        'FBP': _get_ps_FBP_propty_database,
        'FBP_DCLink': _get_ps_FBP_DCLink_propty_database,
        'FBP_FOFB': _get_ps_FBP_FOFB_propty_database,
        'FAC_DCDC': _get_ps_FAC_propty_database,
        'FAC_ACDC': _get_ps_FAC_ACDC_propty_database,
        'FAC_2S_DCDC': _get_ps_FAC_2S_propty_database,
        'FAC_2S_ACDC': _get_ps_FAC_2S_ACDC_propty_database,
        'FAC_2P4S_DCDC': _get_ps_FAC_2P4S_propty_database,
        'FAC_2P4S_ACDC': _get_ps_FAC_2P4S_ACDC_propty_database,
        'FAP': _get_ps_FAP_propty_database,
        'FAP_2P2S_MASTER': _get_ps_FAP_2P2S_propty_database,
        'FAP_4P_Master': _get_ps_FAP_4P_Master_propty_database,
        'FAP_4P_Slave': _get_ps_FAP_4P_Slave_propty_database,
        'Commercial': _get_ps_Commercial_propty_database,
    }
    if psmodel in psmodel_2_dbfunc:
        func = psmodel_2_dbfunc[psmodel]
        return func()
    else:
        raise ValueError(
            'DB for psmodel "{}" not implemented!'.format(psmodel))
