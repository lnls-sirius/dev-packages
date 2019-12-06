"""Power Supply Control System Devices."""

import copy as _copy
import numpy as _np

# from pcaspy import Severity as _Severity
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.search import MASearch as _MASearch
from siriuspy.pwrsupply.siggen import DEFAULT_SIGGEN_CONFIG as _DEF_SIGG_CONF
from siriuspy.csdevice import util as _cutil

# --- WfmData ---
# TODO: delete these deprecated parameters from packages
MAX_WFMSIZE = 4000
DEF_WFMSIZE = 3920

# --- Wfm ---
# NOTE: _SIZE has to be consistent with
# pwrsupply.bsmp.EntitiesFBP.Curve: _SIZE = _curve['count']*_curve['nblocks']
# _SIZE = 4096
MAX_WFMSIZE_FBP = 1024
DEF_WFMSIZE_FBP = 980
DEFAULT_WFM_FBP = _np.zeros(DEF_WFMSIZE_FBP, dtype=float)
MAX_WFMSIZE_OTHERS = 4096
DEF_WFMSIZE_OTHERS = 3920
DEFAULT_WFM_OTHERS = _np.zeros(DEF_WFMSIZE_OTHERS, dtype=float)

DEFAULT_WFM = _np.zeros(DEF_WFMSIZE_OTHERS)

# --- SigGen ---
DEFAULT_SIGGEN_CONFIG = _DEF_SIGG_CONF

# --- PS currents/voltage precision and unit ---
DEFAULT_PS_CURRENT_PRECISION = 4
DEFAULT_PU_CURRENT_PRECISION = 4
_DEFAULT_PS_CURRENT_UNIT = None
_DEFAULT_PU_CURRENT_UNIT = None


# --- Alarms ---
# _SEVERITY_NO_ALARM = _Severity.NO_ALARM
# _SEVERITY_MAJOR_ALARM = _Severity.MAJOR_ALARM
_SEVERITY_NO_ALARM = 0
_SEVERITY_MAJOR_ALARM = 2


# --- Enumeration Types ---


class ETypes(_cutil.ETypes):
    """Local enumerate types."""

    INTERFACE = ('Remote', 'Local', 'PCHost')
    MODELS = ('Empty',
              'FBP', 'FBP_DCLink', 'FAC_DCDC',
              'FAC_2S_ACDC', 'FAC_2S_DCDC',
              'FAC_2P4S_ACDC', 'FAC_2P4S_DCDC',
              'FAP', 'FAP_4P', 'FAP_2P2S',
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
        'Sobre-temperatura no modulo', 'Bit1', 'Bit2', 'Bit3',
        'Bit4', 'Bit5', 'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FBP = (
        'Sobre-corrente na carga', 'Sobre-tensao na carga',
        'Sobre-tensao no DC-Link', 'Sub-tensao no DC-Link',
        'Falha no rele de entrada do DC-Link',
        'Falha no fusivel de entrada do DC-Link',
        'Falha nos drivers do modulo', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FBP_DCLINK = (
        'Bit0', 'Bit1', 'Bit2', 'Bit3',
        'Bit4', 'Bit5', 'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FBP_DCLINK = (
        'Falha na fonte 1', 'Falha na fonte 2', 'Falha na fonte 3',
        'Sobre-tensao da saida do bastidor DC-Link',
        'Sobre-tensao da fonte 1', 'Sobre-tensao na fonte 2',
        'Sobre-tensao na fonte 3', 'Sub-tensao da saida do bastidor DC-Link',
        'Sub-tensao na fonte 1', 'Sub-tensao na fonte 2',
        'Sub-tensao na fonte 3', 'Sensor de fumaca', 'Interlock externo',
        'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAC_DCDC = (
        'Sobre-temperatura nos indutores', 'Sobre-temperatura nos IGBTs',
        'Falha no DCCT 1', 'Falha no DCCT 2',
        'Alta diferenca entre DCCTs',
        'Falha na leitura da corrente na carga do DCCT 1',
        'Falha na leitura da corrente na carga do DCCT 2', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FAC_DCDC = (
        'Sobre-corrente na carga', 'Sobre-tensao na carga',
        'Sobre-tensao no DC-Link', 'Sub-tensao no DC-Link',
        'Falha nos drivers do modulo',
        'Interlock da placa IIB',
        'Interlock externo', 'Interlock do rack',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAC_2S_DCDC = (
        'Falha no DCCT1', 'Falha no DCCT2',
        'Alta diferenca entre DCCT\'s',
        'Falha na leitura da corrente na carga do DCCT1',
        'Falha na leitura da corrente na carga do DCCT2',
        'Bit5', 'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FAC_2S_DCDC = (
        'Sobre-corrente na carga', 'Sobre-tensao na carga',
        'Sobre-tensao no DC-Link do modulo 1',
        'Sobre-tensao no DC-Link do modulo 2',
        'Sub-tensao no DC-Link do modulo 1',
        'Sub-tensao no DC-Link do modulo 2',
        'Sobre-tensao na saida do modulo 1',
        'Sobre-tensao na saida do modulo 2',
        'Interlock da placa IIB do modulo 1',
        'Interlock da placa IIB do modulo 2',
        'Interlock externo', 'Interlock dos racks',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAC_2S_ACDC = (
        'Sobre-temperatura no dissipador', 'Sobre-temperatura nos indutores',
        'Bit2', 'Bit3',
        'Bit4', 'Bit5', 'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FAC_2S_ACDC = (
        'Sobre-tensao no banco de capacitores',
        'Sobre-corrente na saida do retificador',
        'Falha no contator de entrada AC trifasica',
        'Interlock da placa IIB 1', 'Interlock da placa IIB 2',
        'Interlock da placa IIB 3', 'Interlock da placa IIB 4', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAC_2P4S_DCDC = (
        'Sobre-temperatura nos indutores', 'Sobre-temperatura nos IGBTs',
        'Falha no DCCT 1', 'Falha no DCCT 2',
        'Alta diferenca entre DCCTs',
        'Falha na leitura da corrente na carga do DCCT 1',
        'Falha na leitura da corrente na carga do DCCT 2',
        'Sobre-corrente no braço 1', 'Sobre-corrente no braço 2',
        'Alta diferença entre a corrente dos braços', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FAC_2P4S_DCDC = (
        'Sobre-corrente na carga', 'Sobre-tensao na carga',
        'Sobre-tensao no DC-Link do modulo 1',
        'Sobre-tensao no DC-Link do modulo 2',
        'Sobre-tensao no DC-Link do modulo 3',
        'Sobre-tensao no DC-Link do modulo 4',
        'Sobre-tensao no DC-Link do modulo 5',
        'Sobre-tensao no DC-Link do modulo 6',
        'Sobre-tensao no DC-Link do modulo 7',
        'Sobre-tensao no DC-Link do modulo 8',
        'Sub-tensao no DC-Link do modulo 1',
        'Sub-tensao no DC-Link do modulo 2',
        'Sub-tensao no DC-Link do modulo 3',
        'Sub-tensao no DC-Link do modulo 4',
        'Sub-tensao no DC-Link do modulo 5',
        'Sub-tensao no DC-Link do modulo 6',
        'Sub-tensao no DC-Link do modulo 7',
        'Sub-tensao no DC-Link do modulo 8',
        'Sobre-tensao na saida do modulo 1',
        'Sobre-tensao na saida do modulo 2',
        'Sobre-tensao na saida do modulo 3',
        'Sobre-tensao na saida do modulo 4',
        'Sobre-tensao na saida do modulo 5',
        'Sobre-tensao na saida do modulo 6',
        'Sobre-tensao na saida do modulo 7',
        'Sobre-tensao na saida do modulo 8',
        'Interlock da placa IIB do módulo 1',
        'Interlock da placa IIB do módulo 2',
        'Interlock da placa IIB do módulo 3',
        'Interlock da placa IIB do módulo 4',
        'Interlock da placa IIB do módulo 5',
        'Interlock da placa IIB do módulo 6')
    SOFT_INTLCK_FAC_2P4S_ACDC = (
        'Sobre-temperatura no dissipador', 'Sobre-temperatura nos indutores',
        'Bit2', 'Bit3',
        'Bit4', 'Bit5', 'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FAC_2P4S_ACDC = (
        'Sobre-tensao no banco de capacitores',
        'Sobre-tensao na saida do retificador',
        'Sub-tensao na saida do retificador',
        'Sobre-corrente na saida do retificador',
        'Falha no contator de entrada AC trifasica', 'Falha no driver do IGBT',
        'Interlock da placa IIB 1', 'Interlock da placa IIB 2',
        'Interlock da placa IIB 3', 'Interlock da placa IIB 4',
        'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAP = (
        'Falha no DCCT 1', 'Falha no DCCT 2',
        'Alta diferenca entre DCCTs',
        'Falha de leitura da corrente na carga do DCCT 1',
        'Falha de leitura da corrente na carga do DCCT 2',
        'Alta diferença entre a corrente dos IGBTs',
        'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FAP = (
        'Sobre-corrente na carga',
        'Sobre-tensao na carga',
        'Sobre-tensao no DC-Link',
        'Sub-tensao no DC-Link',
        'Falha no contator de entrada do DC-Link',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Interlock da placa IIB',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_INTLCK_FAP = (
        'Sobre-tensao de entrada', 'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1', 'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente do driver do IGBT 1',
        'Sobre-corrente do driver do IGBT 2',
        'Erro no driver do IGBT 1', 'Erro no driver do IGBT 2',
        'Sobre-temperatura nos indutores', 'Sobre-temperatura no dissipador',
        'Falha no contator de entrada do DC-Link', 'Interlock externo',
        'Alta corrente de fuga', 'Interlock do rack',
        'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAP_4P = SOFT_INTLCK_FAP
    HARD_INTLCK_FAP_4P = (
        'Sobre-corrente na carga',
        'Sobre-tensão na carga',
        'Sobre-corrente no IGBT 1 do modulo 1',
        'Sobre-corrente no IGBT 2 do modulo 1',
        'Sobre-corrente no IGBT 1 do modulo 2',
        'Sobre-corrente no IGBT 2 do modulo 2',
        'Sobre-corrente no IGBT 1 do modulo 3',
        'Sobre-corrente no IGBT 2 do modulo 3',
        'Sobre-corrente no IGBT 1 do modulo 4',
        'Sobre-corrente no IGBT 2 do modulo 4',
        'Falha no contator de entrada do DC-Link do modulo 1',
        'Falha no contator de entrada do DC-Link do modulo 2',
        'Falha no contator de entrada do DC-Link do modulo 3',
        'Falha no contator de entrada do DC-Link do modulo 4',
        'Sobre-tensao do DC-Link do modulo 1',
        'Sobre-tensao do DC-Link do modulo 2',
        'Sobre-tensao do DC-Link do modulo 3',
        'Sobre-tensao do DC-Link do modulo 4',
        'Sub-tensao do DC-Link do modulo 1',
        'Sub-tensao do DC-Link do modulo 2',
        'Sub-tensao do DC-Link do modulo 3',
        'Sub-tensao do DC-Link do modulo 4',
        'Interlock da placa IIB do modulo 1',
        'Interlock da placa IIB do modulo 2',
        'Interlock da placa IIB do modulo 3',
        'Interlock da placa IIB do modulo 4',
        'Bit26', 'Bit27', 'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_INTLCK_FAP_4P = IIB_INTLCK_FAP
    SOFT_INTLCK_FAP_2P2S = (
        'Falha no DCCT 1', 'Falha no DCCT 2',
        'Alta diferenca entre DCCTs',
        'Falha de leitura da corrente na carga do DCCT 1',
        'Falha de leitura da corrente na carga do DCCT 2',
        'Alta diferença entre a corrente dos braços',
        'Alta diferença entre a corrente dos IGBTs', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FAP_2P2S = (
        'Sobre-corrente na carga',
        'Sobre-corrente no IGBT 1 do modulo 1',
        'Sobre-corrente no IGBT 2 do modulo 1',
        'Sobre-corrente no IGBT 1 do modulo 2',
        'Sobre-corrente no IGBT 2 do modulo 2',
        'Sobre-corrente no IGBT 1 do modulo 3',
        'Sobre-corrente no IGBT 2 do modulo 3',
        'Sobre-corrente no IGBT 1 do modulo 4',
        'Sobre-corrente no IGBT 2 do modulo 4',
        'Falha no contator de entrada do DC-Link do modulo 1',
        'Falha no contator de entrada do DC-Link do modulo 2',
        'Falha no contator de entrada do DC-Link do modulo 3',
        'Falha no contator de entrada do DC-Link do modulo 4',
        'Sobre-tensao no DC-Link do modulo 1',
        'Sobre-tensao no DC-Link do modulo 2',
        'Sobre-tensao no DC-Link do modulo 3',
        'Sobre-tensao no DC-Link do modulo 4',
        'Sub-tensao no DC-Link do modulo 1',
        'Sub-tensao no DC-Link do modulo 2',
        'Sub-tensao no DC-Link do modulo 3',
        'Sub-tensao no DC-Link do modulo 4',
        'Interlock da placa IIB do modulo 1',
        'Interlock da placa IIB do modulo 2',
        'Interlock da placa IIB do modulo 3',
        'Interlock da placa IIB do modulo 4',
        'Sobre-corrente no braço 1',
        'Sobre-corrente no braço 2',
        'Bit27', 'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_INTLCK_FAP_2P2S = IIB_INTLCK_FAP
    IIB_INTLCK_FAC_2P4S_DCDC = IIB_INTLCK_FAP
    CYCLE_TYPES = ('Sine', 'DampedSine', 'Trapezoidal', 'DampedSquaredSine')
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
    global _DEFAULT_PS_CURRENT_UNIT
    if _DEFAULT_PS_CURRENT_UNIT is None:
        _DEFAULT_PS_CURRENT_UNIT = _PSSearch.get_splims_unit('FBP')
    return _DEFAULT_PS_CURRENT_UNIT


def get_pu_current_unit():
    """Return pulsed power supply 'current' unit."""
    global _DEFAULT_PU_CURRENT_UNIT
    if _DEFAULT_PU_CURRENT_UNIT is None:
        _DEFAULT_PU_CURRENT_UNIT = _PSSearch.get_splims_unit('')
    return _DEFAULT_PU_CURRENT_UNIT


def get_common_propty_database():
    """Return database entries to all BSMP-like devices."""
    dbase = {
        'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
        'TimestampBoot-Cte': {'type': 'float', 'value': 0,
                              'prec': 7, 'unit': 'timestamp'},
        'TimestampUpdate-Mon': {'type': 'float', 'value': 0,
                                'prec': 7, 'unit': 'timestamp'},
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
        'OpMode-Sts': {'type': 'enum', 'enums': _et.STATES,
                       'value': Const.OpMode.SlowRef},
        # PRU
        'PRUCtrlQueueSize-Mon': {'type': 'int', 'value': 0,
                                 'unit': 'count',
                                 'low': -1, 'lolo': -1,
                                 'high': 50, 'hihi': 50},
        # Interlocks
        'IntlkSoft-Mon': {'type': 'int', 'value': 0},
        'IntlkHard-Mon': {'type': 'int', 'value': 0},

        'Reset-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},

    }
    return dbase


def get_basic_propty_database():
    """Return database entries to all power-supply-like devices."""
    dbase = get_common_propty_database()
    dbase.update({
        'Current-SP': {'type': 'float', 'value': 0.0,
                       'prec': DEFAULT_PS_CURRENT_PRECISION},
        'Current-RB': {'type': 'float', 'value': 0.0,
                       'prec': DEFAULT_PS_CURRENT_PRECISION},
        'CurrentRef-Mon': {'type': 'float', 'value': 0.0,
                           'prec': DEFAULT_PS_CURRENT_PRECISION},
        'Current-Mon': {'type': 'float', 'value': 0.0,
                        'prec': DEFAULT_PS_CURRENT_PRECISION},
        # Commands
        'Abort-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
        'SyncPulse-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
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
        'CycleAmpl-SP': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[3],
                         'prec': DEFAULT_PS_CURRENT_PRECISION},
        'CycleAmpl-RB': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[3],
                         'prec': DEFAULT_PS_CURRENT_PRECISION},
        'CycleOffset-SP': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[4],
                           'prec': DEFAULT_PS_CURRENT_PRECISION},
        'CycleOffset-RB': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[4],
                           'prec': DEFAULT_PS_CURRENT_PRECISION},
        'CycleAuxParam-SP': {'type': 'float', 'count': 4,
                             'value': DEFAULT_SIGGEN_CONFIG[5:9]},
        'CycleAuxParam-RB': {'type': 'float', 'count': 4,
                             'value': DEFAULT_SIGGEN_CONFIG[5:9]},
        'CycleIndex-Mon': {'type': 'int', 'value': 0},
        # Wfm - UDC
        'Wfm-SP': {'type': 'float', 'count': len(DEFAULT_WFM),
                   'value': list(DEFAULT_WFM),
                   'prec': DEFAULT_PS_CURRENT_PRECISION},
        'Wfm-RB': {'type': 'float', 'count': len(DEFAULT_WFM),
                   'value': list(DEFAULT_WFM),
                   'prec': DEFAULT_PS_CURRENT_PRECISION},
        'WfmRef-Mon': {'type': 'float', 'count': len(DEFAULT_WFM),
                       'value': list(DEFAULT_WFM),
                       'prec': DEFAULT_PS_CURRENT_PRECISION},
        'Wfm-Mon': {'type': 'float', 'count': len(DEFAULT_WFM),
                    'value': list(DEFAULT_WFM),
                    'prec': DEFAULT_PS_CURRENT_PRECISION},
        # 'WfmMonAcq-Sel': {'type': 'enum', 'enums': _et.DSBL_ENBL,
        #                   'value': Const.DsblEnbl.Dsbl},
        'WfmIndex-Mon': {'type': 'int', 'value': 0},
        'WfmSyncPulseCount-Mon': {'type': 'int', 'value': 0, 'unit': 'count'},
        'WfmUpdate-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
        'WfmUpdateAuto-Sel': {'type': 'enum', 'enums': _et.DSBL_ENBL,
                              'value': Const.DsblEnbl.Dsbl},
        'WfmUpdateAuto-Sts': {'type': 'enum', 'enums': _et.DSBL_ENBL,
                              'value': Const.DsblEnbl.Dsbl},
        # Power Supply Parameters
        'ParamPSName-Cte': {'type': 'char', 'count': 64, 'value': ''},
        'ParamPSModel-Cte': {'type': 'float', 'value': float('NaN')},
        'ParamNrModules-Cte': {'type': 'float', 'value': float('NaN')},
        'ParamCommCmdInferface-Cte': {'type': 'float', 'value': float('NaN')},
        'ParamCommRS485BaudRate-Cte': {'type': 'float', 'value': float('NaN')},
        'ParamCommRS485Addr-Cte': {'type': 'float', 'count': 4,
                                   'value': _np.array([float('NaN'), ] * 4)},
        'ParamCommRS485TermRes-Cte': {'type': 'float', 'value': float('NaN')},
        'ParamCommUDCNetAddr-Cte': {'type': 'float', 'value': float('NaN')},
        'ParamCommEthIP-Cte':
            {'type': 'float', 'count': 4,
             'value': _np.array([float('NaN'), ] * 4)},
        'ParamCommEthSubnetMask-Cte':
            {'type': 'float', 'count': 4,
             'value': _np.array([float('NaN'), ] * 4)},
        'ParamCommBuzVol-Cte': {'type': 'float', 'value': float('NaN')},
        'ParamCtrlFreqCtrlISR-Cte': {'type': 'float', 'value': float('NaN')},
        'ParamCtrlFreqTimeSlicer-Cte':
            {'type': 'float', 'count': 4,
             'value': _np.array([float('NaN'), ] * 4)},
        'ParamCtrlMaxRef-Cte': {'type': 'float', 'value': float('NaN')},
        'ParamCtrlMinRef-Cte': {'type': 'float', 'value': float('NaN')},
        'ParamCtrlMaxRefOpenLoop-Cte':
            {'type': 'float', 'value': float('NaN')},
        'ParamCtrlMinRefOpenLoop-Cte':
            {'type': 'float', 'value': float('NaN')},
        'ParamCtrlSlewRateSlowRef-Cte':
            {'type': 'float', 'value': float('NaN')},
        'ParamCtrlSlewRateSigGenAmp-Cte':
            {'type': 'float', 'value': float('NaN')},
        'ParamCtrlSlewRateSigGenOffset-Cte':
            {'type': 'float', 'value': float('NaN')},
        'ParamCtrlSlewRateWfmRef-Cte':
            {'type': 'float', 'value': float('NaN')}})
    return dbase


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
    dbase = {
        'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
        'CtrlMode-Mon': {'type': 'enum', 'enums': _et.INTERFACE,
                         'value': Const.Interface.Remote},
        'PwrState-Sel': {'type': 'enum', 'enums': _et.PWRSTATE_SEL,
                         'value': Const.PwrStateSel.Off},
        'PwrState-Sts': {'type': 'enum', 'enums': _et.PWRSTATE_STS,
                         'value': Const.PwrStateSts.Off},
        'Reset-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
        'Pulse-Sel': {'type': 'enum', 'enums': _et.DSBL_ENBL,
                      'value': Const.DsblEnbl.Dsbl},
        'Pulse-Sts': {'type': 'enum', 'enums': _et.DSBL_ENBL,
                      'value': Const.DsblEnbl.Dsbl},
        'Voltage-SP': {'type': 'float', 'value': 0.0,
                       'prec': DEFAULT_PU_CURRENT_PRECISION},
        'Voltage-RB': {'type': 'float', 'value': 0.0,
                       'prec': DEFAULT_PU_CURRENT_PRECISION},
        'Voltage-Mon': {'type': 'float', 'value': 0.0,
                        'prec': DEFAULT_PU_CURRENT_PRECISION},
        'Intlk1-Mon': {'type': 'int', 'value': 0},
        'Intlk2-Mon': {'type': 'int', 'value': 0},
        'Intlk3-Mon': {'type': 'int', 'value': 0},
        'Intlk4-Mon': {'type': 'int', 'value': 0},
        'Intlk5-Mon': {'type': 'int', 'value': 0},
        'Intlk6-Mon': {'type': 'int', 'value': 0},
        'Intlk7-Mon': {'type': 'int', 'value': 0},
        'Intlk8-Mon': {'type': 'int', 'value': 0},
        'Intlk1Label-Cte': {'type': 'str', 'value': 'Switch module'},
        'Intlk2Label-Cte': {'type': 'str', 'value': 'AC CPFL OFF'},
        'Intlk3Label-Cte': {'type': 'str', 'value': 'Temperature'},
        'Intlk4Label-Cte': {'type': 'str', 'value': 'Personnel protection'},
        'Intlk5Label-Cte': {'type': 'str', 'value': 'HVPS Overcurrent'},
        'Intlk6Label-Cte': {'type': 'str', 'value': 'HVPS Overvoltage'},
        'Intlk7Label-Cte': {'type': 'str', 'value': 'External'},
        'Intlk8Label-Cte': {'type': 'str', 'value': 'Switch Overcurrent'},
    }
    return dbase


def get_common_pu_SI_InjKicker_propty_database():
    """Return database of SI injection kicker."""
    # K SI-01SA:PU-InjNLKckr
    dbase = get_common_pu_propty_database()
    # 'Comissioning': On-Axis magnet
    # 'Accumulation': Non-linear kicker
    dbase.update({
        'OpMode-Sel': {'type': 'enum',
                       'enums': ['Comissioning', 'Accumulation'],
                       'value': 0},
        'OpMode-Sts': {'type': 'enum',
                       'enums': ['Comissioning', 'Accumulation'],
                       'value': 0},
    })
    return dbase


def get_ps_propty_database(psmodel, pstype):
    """Return property database of a LNLS power supply type device."""
    database = _get_model_db(psmodel)
    database = _insert_strengths(database, pstype)
    _set_limits(pstype, database)
    # add pvs list
    database = _cutil.add_pvslist_cte(database)
    return database


def get_pu_propty_database(pstype):
    """Return database definition for a pulsed power supply type."""
    database = get_common_pu_propty_database()
    signals_lims = ('Voltage-SP', 'Voltage-RB', 'Voltage-Mon')
    signals_unit = signals_lims
    for propty, dbase in database.items():
        # set setpoint limits in database
        if propty in signals_lims:
            dbase['lolo'] = _PSSearch.get_splims(pstype, 'lolo')
            dbase['low'] = _PSSearch.get_splims(pstype, 'low')
            dbase['lolim'] = _PSSearch.get_splims(pstype, 'lolim')
            dbase['hilim'] = _PSSearch.get_splims(pstype, 'hilim')
            dbase['high'] = _PSSearch.get_splims(pstype, 'high')
            dbase['hihi'] = _PSSearch.get_splims(pstype, 'hihi')
        # define unit of current
        if propty in signals_unit:
            dbase['unit'] = get_ps_current_unit()
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
    dbase = {}

    for psname, magfunc in magfunc_dict.items():
        dbase[psname] = _copy.deepcopy(database)
        # set appropriate PS limits and unit
        for field in {'-SP', '-RB', 'Ref-Mon', '-Mon'}:
            dbase[psname]['Current' + field]['lolo'] = \
                _MASearch.get_splims(maname, 'lolo')
            dbase[psname]['Current' + field]['low'] = \
                _MASearch.get_splims(maname, 'low')
            dbase[psname]['Current' + field]['lolim'] = \
                _MASearch.get_splims(maname, 'lolim')
            dbase[psname]['Current' + field]['hilim'] = \
                _MASearch.get_splims(maname, 'hilim')
            dbase[psname]['Current' + field]['high'] = \
                _MASearch.get_splims(maname, 'high')
            dbase[psname]['Current' + field]['hihi'] = \
                _MASearch.get_splims(maname, 'hihi')
        for propty in current_pvs:
            dbase[psname][propty]['unit'] = unit[0]
        # set approriate MA limits and unit
        if magfunc in {'quadrupole', 'quadrupole-skew'}:
            strength_name = 'KL'
            unit = '1/m'
        elif magfunc == 'sextupole':
            strength_name = 'SL'
            unit = '1/m^2'
        elif magfunc == 'dipole':
            strength_name = 'Energy'
            unit = 'GeV'
        elif magfunc in {'corrector-vertical', 'corrector-horizontal'}:
            strength_name = 'Kick'
            unit = 'urad'

        dbase[psname][strength_name + '-SP'] = \
            _copy.deepcopy(dbase[psname]['Current-SP'])
        dbase[psname][strength_name + '-SP']['unit'] = unit
        dbase[psname][strength_name + '-RB'] = \
            _copy.deepcopy(dbase[psname]['Current-RB'])
        dbase[psname][strength_name + '-RB']['unit'] = unit
        dbase[psname][strength_name + 'Ref-Mon'] = \
            _copy.deepcopy(dbase[psname]['CurrentRef-Mon'])
        dbase[psname][strength_name + 'Ref-Mon']['unit'] = unit
        dbase[psname][strength_name + '-Mon'] = \
            _copy.deepcopy(dbase[psname]['Current-Mon'])
        dbase[psname][strength_name + '-Mon']['unit'] = unit

        for field in {'-SP', '-RB', 'Ref-Mon', '-Mon'}:
            dbase[psname][strength_name + field]['lolo'] = 0.0
            dbase[psname][strength_name + field]['low'] = 0.0
            dbase[psname][strength_name + field]['lolim'] = 0.0
            dbase[psname][strength_name + field]['hilim'] = 0.0
            dbase[psname][strength_name + field]['high'] = 0.0
            dbase[psname][strength_name + field]['hihi'] = 0.0

        # add PSConnStatus
        dbase[psname]['PSConnStatus-Mon'] = {
            'type': 'enum', 'enums': _et.DISCONN_CONN,
                            'value': Const.DisconnConn.Disconnected}

        # add pvs list
        dbase[psname] = _cutil.add_pvslist_cte(dbase[psname])

    return dbase


def get_li_ma_propty_database(maname):
    """Return property database of a magnet type device."""
    psnames = _MASearch.conv_psmaname_2_psnames(maname)
    database = _get_ps_LINAC_propty_database()
    dbase = {}
    dbase[psnames[0]] = database
    return dbase


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
    dbase = {}
    for psname, magfunc in magfunc_dict.items():
        dbase[psname] = _copy.deepcopy(database)
        # set appropriate PS limits and unit
        for field in ('-SP', '-RB', '-Mon'):
            dbase[psname]['Voltage' + field]['lolo'] = \
                _MASearch.get_splims(maname, 'lolo')
            dbase[psname]['Voltage' + field]['low'] = \
                _MASearch.get_splims(maname, 'low')
            dbase[psname]['Voltage' + field]['lolim'] = \
                _MASearch.get_splims(maname, 'lolim')
            dbase[psname]['Voltage' + field]['hilim'] = \
                _MASearch.get_splims(maname, 'hilim')
            dbase[psname]['Voltage' + field]['high'] = \
                _MASearch.get_splims(maname, 'high')
            dbase[psname]['Voltage' + field]['hihi'] = \
                _MASearch.get_splims(maname, 'hihi')
        for propty in current_alarm:
            dbase[psname][propty]['unit'] = unit[0]
        # set approriate MA limits and unit
        if magfunc in ('corrector-vertical', 'corrector-horizontal'):
            dbase[psname]['Kick-SP'] = _copy.deepcopy(dbase[psname]['Voltage-SP'])
            dbase[psname]['Kick-SP']['unit'] = 'mrad'
            dbase[psname]['Kick-RB'] = _copy.deepcopy(dbase[psname]['Voltage-RB'])
            dbase[psname]['Kick-RB']['unit'] = 'mrad'
            dbase[psname]['Kick-Mon'] = _copy.deepcopy(dbase[psname]['Voltage-Mon'])
            dbase[psname]['Kick-Mon']['unit'] = 'mrad'

            for field in ('-SP', '-RB', '-Mon'):
                dbase[psname]['Kick' + field]['lolo'] = 0.0
                dbase[psname]['Kick' + field]['low'] = 0.0
                dbase[psname]['Kick' + field]['lolim'] = 0.0
                dbase[psname]['Kick' + field]['hilim'] = 0.0
                dbase[psname]['Kick' + field]['high'] = 0.0
                dbase[psname]['Kick' + field]['hihi'] = 0.0
        else:
            raise ValueError('Invalid pulsed magnet power supply type!')

        # add PSConnStatus
        dbase[psname]['PSConnStatus-Mon'] = {
            'type': 'enum', 'enums': _et.DISCONN_CONN,
                            'value': Const.DisconnConn.Disconnected}
        # add pvs list
        dbase[psname] = _cutil.add_pvslist_cte(dbase[psname])

    return dbase


# --- Auxiliary functions ---


def _get_pu_FP_SEPT_propty_database():
    """."""
    return get_common_pu_propty_database()


def _get_pu_FP_KCKR_propty_database():
    """."""
    return get_common_pu_propty_database()


def _get_pu_FP_PINGER_propty_database():
    """."""
    return get_common_pu_propty_database()


def _get_ps_LINAC_propty_database():
    """Return LINAC pwrsupply props."""
    propty_db = {
        'rdnets': {'type': 'enum', 'enums': ['Connected', 'Broken'],
                   # 'states': [_Severity.NO_ALARM, _Severity.MAJOR_ALARM]},
                   'states': [_SEVERITY_NO_ALARM, _SEVERITY_MAJOR_ALARM]},
        'setpwm': {'type': 'enum', 'enums': ['Pwm_Off', 'Pwm_On']},  # 40
        'rdpwm': {'type': 'enum', 'enums': ['Pwm_Off', 'Pwm_On']},   # 40
        'seti': {'type': 'float', 'prec': 4, 'unit': 'A',
                 'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
                 'hilim': 0.0, 'high': 0.0, 'hihi': 0.0},            # 90
        'rdseti': {'type': 'float', 'prec': 4, 'unit': 'A',
                   'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
                   'hilim': 0.0, 'high': 0.0, 'hihi': 0.0},          # 90
        'rdmaxti': {'type': 'float', 'prec': 4, 'unit': 'A'},        # 91
        'rdminti': {'type': 'float', 'prec': 4, 'unit': 'A'},        # 92
        'rdseti_fit': {'type': 'float', 'prec': 4},                  # f0
        'rdi': {'type': 'float', 'prec': 4, 'unit': 'A',
                'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
                'hilim': 0.0, 'high': 0.0, 'hihi': 0.0,
                'mdel': 0.000099, 'adel': 0.000099},                 # f1
        'rdldv': {'type': 'float', 'prec': 4},                       # f2
        'rdbusv': {'type': 'float', 'prec': 4},                      # f3
        'rdwarn': {'type': 'int'},                                   # 23
        'rdsgin': {'type': 'int'},                                   # 70
        'rdsgin_msk': {'type': 'int'},                               # 71
        'sgin': {'type': 'int'},
        'rdsgout': {'type': 'int'},                                  # 72
        'rdsgout_msk': {'type': 'int'},                              # 73
        'sgout': {'type': 'int'},
        'rdtp': {'type': 'float', 'prec': 4},                        # 74
        'boottime': {'type': 'string'},
        'interlock': {'type': 'int', 'hihi': 55},
        'Cycle-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
        'Abort-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
        'Version-Cte': {'type': 'string', 'value': 'UNDEF'}
    }
    return propty_db


# --- FBP ---

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
        'SwitchesTemperature-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': 2,
                                    'unit': 'C'},
        'PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                             'prec': DEFAULT_PS_CURRENT_PRECISION},
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


# --- FAC DCDC ---


def _get_ps_FAC_DCDC_propty_database():
    """Return database with FAC_DCDC pwrsupply model PVs."""
    propty_db = get_basic_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAC_DCDC),
                                 'value': _et.SOFT_INTLCK_FAC_DCDC},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAC_DCDC),
                                 'value': _et.HARD_INTLCK_FAC_DCDC},
        'Current1-Mon': {'type': 'float',  'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float',  'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'LoadVoltage-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'V'},
        'InductorsTemperature-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': 2,
                                     'unit': 'C'},
        'IGBTSTemperature-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': 2,
                                 'unit': 'C'},
        'PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                             'prec': DEFAULT_PS_CURRENT_PRECISION},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_2S_DCDC_propty_database():
    """Return database with FAC_2S_DCDC pwrsupply model PVs."""
    propty_db = get_basic_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAC_2S_DCDC),
                                 'value': _et.SOFT_INTLCK_FAC_2S_DCDC},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAC_2S_DCDC),
                                 'value': _et.HARD_INTLCK_FAC_2S_DCDC},
        'Current1-Mon': {'type': 'float', 'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float', 'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'LoadVoltage-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'V'},
        'Module1Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'Module2Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'CapacitorBank1Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': DEFAULT_PS_CURRENT_PRECISION,
                                      'unit': 'V'},
        'CapacitorBank2Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': DEFAULT_PS_CURRENT_PRECISION,
                                      'unit': 'V'},
        'PWMDutyCycle1-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                              'prec': DEFAULT_PS_CURRENT_PRECISION},
        'PWMDutyCycle2-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                              'prec': DEFAULT_PS_CURRENT_PRECISION},
        'PWMDutyDiff-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                            'prec': DEFAULT_PS_CURRENT_PRECISION},
        'IIB1InductorsTemperature-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': 2,
                                         'unit': 'C'},
        'IIB1HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IIB2InductorsTemperature-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': 2,
                                         'unit': 'C'},
        'IIB2HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IntlkIIB1-Mon': {'type': 'int', 'value': 0},
        'IntlkIIB2-Mon': {'type': 'int', 'value': 0},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_2P4S_DCDC_propty_database():
    """Return database with FAC_2P4S pwrsupply model PVs."""
    propty_db = get_basic_propty_database()
    db_ps = {
        'Current1-Mon': {'type': 'float',  'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float',  'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAC_2P4S_DCDC),
                                 'value': _et.SOFT_INTLCK_FAC_2P4S_DCDC},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAC_2P4S_DCDC),
                                 'value': _et.HARD_INTLCK_FAC_2P4S_DCDC},
        'LoadVoltage-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'V'},
        'CapacitorBank1Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': DEFAULT_PS_CURRENT_PRECISION,
                                      'unit': 'V'},
        'CapacitorBank2Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': DEFAULT_PS_CURRENT_PRECISION,
                                      'unit': 'V'},
        'CapacitorBank3Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': DEFAULT_PS_CURRENT_PRECISION,
                                      'unit': 'V'},
        'CapacitorBank4Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': DEFAULT_PS_CURRENT_PRECISION,
                                      'unit': 'V'},
        'CapacitorBank5Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': DEFAULT_PS_CURRENT_PRECISION,
                                      'unit': 'V'},
        'CapacitorBank6Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': DEFAULT_PS_CURRENT_PRECISION,
                                      'unit': 'V'},
        'CapacitorBank7Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': DEFAULT_PS_CURRENT_PRECISION,
                                      'unit': 'V'},
        'CapacitorBank8Voltage-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': DEFAULT_PS_CURRENT_PRECISION,
                                      'unit': 'V'},
        'Module1Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'Module2Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'Module3Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'Module4Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'Module5Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'Module6Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'Module7Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'Module8Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'PWMDutyCycle1-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                              'prec': DEFAULT_PS_CURRENT_PRECISION},
        'PWMDutyCycle2-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                              'prec': DEFAULT_PS_CURRENT_PRECISION},
        'PWMDutyCycle3-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                              'prec': DEFAULT_PS_CURRENT_PRECISION},
        'PWMDutyCycle4-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                              'prec': DEFAULT_PS_CURRENT_PRECISION},
        'PWMDutyCycle5-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                              'prec': DEFAULT_PS_CURRENT_PRECISION},
        'PWMDutyCycle6-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                              'prec': DEFAULT_PS_CURRENT_PRECISION},
        'PWMDutyCycle7-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                              'prec': DEFAULT_PS_CURRENT_PRECISION},
        'PWMDutyCycle8-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                              'prec': DEFAULT_PS_CURRENT_PRECISION},
        'Arm1Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'Arm2Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'IIB1InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IIB1HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB2InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB2HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB3InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB3HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB4InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB4HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB5InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB5HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB6InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB6HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB7InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB7HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB8InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IIB8HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IntlkIIB1-Mon': {'type': 'int', 'value': 0},
        'IntlkIIB2-Mon': {'type': 'int', 'value': 0},
        'IntlkIIB3-Mon': {'type': 'int', 'value': 0},
        'IntlkIIB4-Mon': {'type': 'int', 'value': 0},
        'IntlkIIB5-Mon': {'type': 'int', 'value': 0},
        'IntlkIIB6-Mon': {'type': 'int', 'value': 0},
        'IntlkIIB7-Mon': {'type': 'int', 'value': 0},
        'IntlkIIB8-Mon': {'type': 'int', 'value': 0},
        'IntlkIIB1Labels-Cte': {'type': 'string',
                                'count': len(_et.IIB_INTLCK_FAC_2P4S_DCDC),
                                'value': _et.IIB_INTLCK_FAC_2P4S_DCDC},
        'IntlkIIB2Labels-Cte': {'type': 'string',
                                'count': len(_et.IIB_INTLCK_FAC_2P4S_DCDC),
                                'value': _et.IIB_INTLCK_FAC_2P4S_DCDC},
        'IntlkIIB3Labels-Cte': {'type': 'string',
                                'count': len(_et.IIB_INTLCK_FAC_2P4S_DCDC),
                                'value': _et.IIB_INTLCK_FAC_2P4S_DCDC},
        'IntlkIIB4Labels-Cte': {'type': 'string',
                                'count': len(_et.IIB_INTLCK_FAC_2P4S_DCDC),
                                'value': _et.IIB_INTLCK_FAC_2P4S_DCDC},
        'IntlkIIB5Labels-Cte': {'type': 'string',
                                'count': len(_et.IIB_INTLCK_FAC_2P4S_DCDC),
                                'value': _et.IIB_INTLCK_FAC_2P4S_DCDC},
        'IntlkIIB6Labels-Cte': {'type': 'string',
                                'count': len(_et.IIB_INTLCK_FAC_2P4S_DCDC),
                                'value': _et.IIB_INTLCK_FAC_2P4S_DCDC},
        'IntlkIIB7Labels-Cte': {'type': 'string',
                                'count': len(_et.IIB_INTLCK_FAC_2P4S_DCDC),
                                'value': _et.IIB_INTLCK_FAC_2P4S_DCDC},
        'IntlkIIB8Labels-Cte': {'type': 'string',
                                'count': len(_et.IIB_INTLCK_FAC_2P4S_DCDC),
                                'value': _et.IIB_INTLCK_FAC_2P4S_DCDC},
    }
    propty_db.update(db_ps)
    return propty_db


# --- FAC ACDC ---


def _get_ps_FAC_2S_ACDC_propty_database():
    """Return database with FAC_2S_ACDC pwrsupply model PVs."""
    propty_db = get_common_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAC_2S_ACDC),
                                 'value': _et.SOFT_INTLCK_FAC_2S_ACDC},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAC_2S_ACDC),
                                 'value': _et.HARD_INTLCK_FAC_2S_ACDC},
        'CapacitorBankVoltage-SP': {'type': 'float', 'value': 0.0,
                                    'prec': DEFAULT_PS_CURRENT_PRECISION,
                                    'lolim': 0.0, 'hilim': 1.0,
                                    'unit': 'V'},
        'CapacitorBankVoltage-RB': {'type': 'float', 'value': 0.0,
                                    'prec': DEFAULT_PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'CapacitorBankVoltageRef-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': DEFAULT_PS_CURRENT_PRECISION,
                                        'unit': 'V'},
        'CapacitorBankVoltage-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': DEFAULT_PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'RectifierVoltage-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': DEFAULT_PS_CURRENT_PRECISION,
                                 'unit': 'V'},
        'RectifierCurrent-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': DEFAULT_PS_CURRENT_PRECISION,
                                 'unit': 'V'},
        'HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': 2,
                                    'unit': 'C'},
        'InductorsTemperature-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': 2,
                                     'unit': 'C'},
        'PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                     'prec': DEFAULT_PS_CURRENT_PRECISION},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_2P4S_ACDC_propty_database():
    """Return database with FAC_2P4S_ACDC pwrsupply model PVs."""
    propty_db = get_common_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAC_2P4S_ACDC),
                                 'value': _et.SOFT_INTLCK_FAC_2P4S_ACDC},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAC_2P4S_ACDC),
                                 'value': _et.HARD_INTLCK_FAC_2P4S_ACDC},
        'CapacitorBankVoltage-SP': {'type': 'float', 'value': 0.0,
                                    'prec': DEFAULT_PS_CURRENT_PRECISION,
                                    'lolim': 0.0, 'hilim': 1.0,
                                    'unit': 'V'},
        'CapacitorBankVoltage-RB': {'type': 'float', 'value': 0.0,
                                    'prec': DEFAULT_PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'CapacitorBankVoltageRef-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': DEFAULT_PS_CURRENT_PRECISION,
                                        'unit': 'V'},
        'CapacitorBankVoltage-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': DEFAULT_PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'RectifierVoltage-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': DEFAULT_PS_CURRENT_PRECISION,
                                 'unit': 'V'},
        'RectifierCurrent-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': DEFAULT_PS_CURRENT_PRECISION,
                                 'unit': 'V'},
        'HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': 2,
                                    'unit': 'C'},
        'InductorsTemperature-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': 2,
                                     'unit': 'C'},
        'PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                     'prec': DEFAULT_PS_CURRENT_PRECISION},
        'IIBISInductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': 2,
                                         'unit': 'C'},
        'IIBISHeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': 2,
                                         'unit': 'C'},
        'IIBCmdInductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': 2,
                                          'unit': 'C'},
        'IIBCmdHeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': 2,
                                          'unit': 'C'},
        'IntlkIIBIS-Mon': {'type': 'int', 'value': 0},
        'IntlkIIBCmd-Mon': {'type': 'int', 'value': 0},
        'IntlkIIBIS-Cte':  {'type': 'string',
                            'count': len(_et.SOFT_INTLCK_FAC_2P4S_ACDC),
                            'value': _et.SOFT_INTLCK_FAC_2P4S_ACDC},
        'IntlkIIBCmd-Cte':  {'type': 'string',
                             'count': len(_et.HARD_INTLCK_FAC_2P4S_ACDC),
                             'value': _et.HARD_INTLCK_FAC_2S_ACDC}, }
    propty_db.update(db_ps)
    return propty_db


# --- FAP ---

def _get_ps_FAP_propty_database():
    """Return database with FAP pwrsupply model PVs."""
    propty_db = get_basic_propty_database()
    db_ps = {
        'Current1-Mon': {'type': 'float', 'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float', 'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'IntlkIIB-Mon': {'type': 'int', 'value': 0},
        'IntlkSoftLabels-Cte': {'type': 'string',
                                'count': len(_et.SOFT_INTLCK_FAP),
                                'value': _et.SOFT_INTLCK_FAP},
        'IntlkHardLabels-Cte': {'type': 'string',
                                'count': len(_et.HARD_INTLCK_FAP),
                                'value': _et.HARD_INTLCK_FAP},
        'IntlkIIB-Cte': {'type': 'string',
                         'count': len(_et.IIB_INTLCK_FAP),
                         'value': _et.IIB_INTLCK_FAP},
        'IIBLeakCurrent-Mon': {'type': 'float',  'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'A'},
        'IIBInductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2,
                                       'unit': 'C'},
        'IIBHeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2,
                                       'unit': 'C'},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAP_4P_propty_database():
    """Return database with FAP_4P pwrsupply model PVs."""
    propty_db = get_basic_propty_database()
    db_ps = {
        'Current1-Mon': {'type': 'float', 'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float', 'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'DCLink1Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'DCLink2Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'DCLink3Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'DCLink4Voltage-Mon': {'type': 'float', 'value': 0.0,
                               'prec': DEFAULT_PS_CURRENT_PRECISION,
                               'unit': 'V'},
        'Mod1Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'Mod2Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'Mod3Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'Mod4Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'Intlk1IIB-Mon': {'type': 'int', 'value': 0},
        'Intlk2IIB-Mon': {'type': 'int', 'value': 0},
        'Intlk3IIB-Mon': {'type': 'int', 'value': 0},
        'Intlk4IIB-Mon': {'type': 'int', 'value': 0},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAP_4P),
                                 'value': _et.SOFT_INTLCK_FAP_4P},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAP_4P),
                                 'value': _et.HARD_INTLCK_FAP_4P},
        'Intlk1IIBLabels-Cte':  {'type': 'string',
                                 'count': len(_et.IIB_INTLCK_FAP_4P),
                                 'value': _et.IIB_INTLCK_FAP_4P},
        'Intlk2IIBLabels-Cte':  {'type': 'string',
                                 'count': len(_et.IIB_INTLCK_FAP_4P),
                                 'value': _et.IIB_INTLCK_FAP_4P},
        'Intlk3IIBLabels-Cte':  {'type': 'string',
                                 'count': len(_et.IIB_INTLCK_FAP_4P),
                                 'value': _et.IIB_INTLCK_FAP_4P},
        'Intlk4IIBLabels-Cte':  {'type': 'string',
                                 'count': len(_et.IIB_INTLCK_FAP_4P),
                                 'value': _et.IIB_INTLCK_FAP_4P},

    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAP_2P2S_propty_database():
    """Return database with FAP_2P2S pwrsupply model PVs."""
    propty_db = get_basic_propty_database()
    db_ps = {
        'Current1-Mon': {'type': 'float',  'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float',  'value': 0.0,
                         'prec': DEFAULT_PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Intlk1IIB-Mon': {'type': 'int', 'value': 0},
        'Intlk2IIB-Mon': {'type': 'int', 'value': 0},
        'Intlk3IIB-Mon': {'type': 'int', 'value': 0},
        'Intlk4IIB-Mon': {'type': 'int', 'value': 0},
        'IntlkSoftLabels-Cte':  {'type': 'string',
                                 'count': len(_et.SOFT_INTLCK_FAP_2P2S),
                                 'value': _et.SOFT_INTLCK_FAP},
        'IntlkHardLabels-Cte':  {'type': 'string',
                                 'count': len(_et.HARD_INTLCK_FAP_2P2S),
                                 'value': _et.HARD_INTLCK_FAP},
        'Intlk1IIBLabels-Cte':  {'type': 'string',
                                 'count': len(_et.IIB_INTLCK_FAP_2P2S),
                                 'value': _et.IIB_INTLCK_FAP},
        'Intlk2IIBLabels-Cte':  {'type': 'string',
                                 'count': len(_et.IIB_INTLCK_FAP_2P2S),
                                 'value': _et.IIB_INTLCK_FAP},
        'Intlk3IIBLabels-Cte':  {'type': 'string',
                                 'count': len(_et.IIB_INTLCK_FAP_2P2S),
                                 'value': _et.IIB_INTLCK_FAP},
        'Intlk4IIBLabels-Cte':  {'type': 'string',
                                 'count': len(_et.IIB_INTLCK_FAP_2P2S),
                                 'value': _et.IIB_INTLCK_FAP},
        'Mod1Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'Mod2Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'Mod3Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'Mod4Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': DEFAULT_PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'IIB1InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IIB1HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': 2,
                                         'unit': 'C'},
        'IIB2InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IIB2HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IIB3InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IIB3HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IIB4InductorTemperature-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IIB4HeatSinkTemperature-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
    }
    propty_db.update(db_ps)
    return propty_db


# --- Others ---

def _get_ps_FBP_FOFB_propty_database():
    """Return database with FBP_FOFB pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


def _get_ps_Commercial_propty_database():
    """Return database with Commercial pwrsupply model PVs."""
    # TODO: implement!!!
    return _get_ps_FBP_propty_database()


# --- Aux. ---


def _set_limits(pstype, database):
    signals_lims = ('Current-SP', 'Current-RB',
                    'CurrentRef-Mon', 'Current-Mon', 'Current2-Mon'
                    'CycleAmpl-SP', 'CycleAmpl-RB',
                    'CycleOffset-SP', 'CycleOffset-RB',
                    'Voltage-SP', 'Voltage-RB',
                    'VoltageRef-Mon', 'Voltage-Mon',
                    )
    # TODO: define limits to WfmData as well!
    signals_unit = signals_lims + (
        'WfmData-SP', 'WfmData-RB',
    )
    signals_prec = signals_unit

    for propty, dbase in database.items():
        # set setpoint limits in database
        if propty in signals_lims:
            if propty == 'Voltage-Mon' and pstype == 'as-dclink-fbp':
                # for FBP DCLinks Voltage-Mon has different units than
                # Voltage-SP!
                continue
            dbase['lolo'] = _PSSearch.get_splims(pstype, 'lolo')
            dbase['low'] = _PSSearch.get_splims(pstype, 'low')
            dbase['lolim'] = _PSSearch.get_splims(pstype, 'lolim')
            dbase['hilim'] = _PSSearch.get_splims(pstype, 'hilim')
            dbase['high'] = _PSSearch.get_splims(pstype, 'high')
            dbase['hihi'] = _PSSearch.get_splims(pstype, 'hihi')
        # define unit of current
        if propty in signals_unit:
            dbase['unit'] = get_ps_current_unit()
        # define prec of current
        if propty in signals_prec:
            dbase['prec'] = DEFAULT_PS_CURRENT_PRECISION


def _get_model_db(psmodel):
    psmodel_2_dbfunc = {
        'FBP': _get_ps_FBP_propty_database,
        'FBP_DCLink': _get_ps_FBP_DCLink_propty_database,
        'FBP_FOFB': _get_ps_FBP_FOFB_propty_database,
        'FAC_DCDC': _get_ps_FAC_DCDC_propty_database,
        'FAC_2S_DCDC': _get_ps_FAC_2S_DCDC_propty_database,
        'FAC_2S_ACDC': _get_ps_FAC_2S_ACDC_propty_database,
        'FAC_2P4S_DCDC': _get_ps_FAC_2P4S_DCDC_propty_database,
        'FAC_2P4S_ACDC': _get_ps_FAC_2P4S_ACDC_propty_database,
        'FAP': _get_ps_FAP_propty_database,
        'FAP_2P2S': _get_ps_FAP_2P2S_propty_database,
        'FAP_4P': _get_ps_FAP_4P_propty_database,
        'Commercial': _get_ps_Commercial_propty_database,
        'FP_SEPT': _get_pu_FP_SEPT_propty_database,
        'FP_KCKR': _get_pu_FP_KCKR_propty_database,
        'FP_PINGER': _get_pu_FP_PINGER_propty_database,
        'LINAC_PS': _get_ps_LINAC_propty_database,
    }
    if psmodel in psmodel_2_dbfunc:
        func = psmodel_2_dbfunc[psmodel]
        return func()
    else:
        raise ValueError(
            'DB for psmodel "{}" not implemented!'.format(psmodel))


def _insert_strengths(database, pstype):
    magfunc = _PSSearch.conv_pstype_2_magfunc(pstype)
    if magfunc in {'quadrupole', 'quadrupole-skew'}:
        database['KL-SP'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': '1/m'}
        database['KL-RB'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': '1/m'}
        database['KLRef-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': '1/m'}
        database['KL-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': '1/m'}
    elif magfunc == 'sextupole':
        database['SL-SP'] = {
            'type': 'float', 'value': 0.0, 'unit': '1/m^2'}
        database['SL-RB'] = {
            'type': 'float', 'value': 0.0, 'unit': '1/m^2'}
        database['SLRef-Mon'] = {
            'type': 'float', 'value': 0.0, 'unit': '1/m^2'}
        database['SL-Mon'] = {
            'type': 'float', 'value': 0.0, 'unit': '1/m^2'}
    elif magfunc == 'dipole':
        database['Energy-SP'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'GeV'}
        database['Energy-RB'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'GeV'}
        database['EnergyRef-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'GeV'}
        database['Energy-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'GeV'}
    elif magfunc in {'corrector-horizontal', 'corrector-vertical'}:
        database['Kick-SP'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'urad'}
        database['Kick-RB'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'urad'}
        database['KickRef-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'urad'}
        database['Kick-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'urad'}
    else:
        raise NotImplementedError('Missing {} implementation'.format(magfunc))
    return database
