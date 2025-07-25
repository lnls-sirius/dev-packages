"""Power Supply Control System Devices epics database functions."""

import numpy as _np

# from pcaspy import Severity as _Severity
from .. import csdev as _csdev
from ..search import PSSearch as _PSSearch
from .bsmp.constants import ConstPSBSMP as _ConstPSBSMP, \
    UDC_MAX_NR_DEV as _UDC_MAX_NR_DEV
from .siggen import DEFAULT_SIGGEN_CONFIG as _DEF_SIGG_CONF

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
DEFAULT_WFM_SELECTED = 0
DEFAULT_WFM_FREQUENCY = 2000.0  # [Hz]
DEFAULT_WFM_GAIN = 1.0
DEFAULT_WFM_OFFSET = 0.0  # [A/V]

DEFAULT_WFM = _np.zeros(DEF_WFMSIZE_OTHERS)

# --- SOFBCurrent ---
PSSOFB_MAX_NR_UDC = 2

# --- SigGen ---
DEFAULT_SIGGEN_CONFIG = _DEF_SIGG_CONF

# --- PS currents/voltage precision and unit ---
PS_CURRENT_PRECISION = 4
PU_VOLTAGE_PRECISION = 4
PS_CURRENT_UNIT = 'A'
PU_VOLTAGE_UNIT = 'V'


# --- Alarms ---
# _SEVERITY_NO_ALARM = _Severity.NO_ALARM
# _SEVERITY_MAJOR_ALARM = _Severity.MAJOR_ALARM
_SEVERITY_NO_ALARM = 0
_SEVERITY_MAJOR_ALARM = 2


# --- Linac PS interlock ---
PS_LI_INTLK_THRS = 55


# --- Enumeration Types ---


class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    INTERFACE = ['', ] * 3
    INTERFACE[_ConstPSBSMP.E_INTERFACE_REMOTE] = 'Remote'
    INTERFACE[_ConstPSBSMP.E_INTERFACE_LOCAL] = 'Local'
    INTERFACE[_ConstPSBSMP.E_INTERFACE_PCHOST] = 'PCHost'
    INTERFACE = tuple(INTERFACE)

    MODELS = ['Field' + str(i) for i in range(32)]
    MODELS[_ConstPSBSMP.E_PS_MODEL_EMPTY] = 'Empty'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FBP] = 'FBP'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FBP_DCLink] = 'FBP_DCLink'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAC_ACDC] = 'FAC_ACDC'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAC_DCDC] = 'FAC_DCDC'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAC_2S_ACDC] = 'FAC_2S_ACDC'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAC_2S_DCDC] = 'FAC_2S_DCDC'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAC_2P4S_ACDC] = 'FAC_2P4S_ACDC'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAC_2P4S_DCDC] = 'FAC_2P4S_DCDC'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAP] = 'FAP'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAP_4P] = 'FAP_4P'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAC_DCDC_EMA] = 'FAC_DCDC_EMA'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAP_2P2S] = 'FAP_2P2S'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAP_IMAS] = 'FAP_IMAS'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAC_2P_ACDC_IMAS] = 'FAC_2P_ACDC_IMAS'
    MODELS[_ConstPSBSMP.E_PS_MODEL_FAC_2P_DCDC_IMAS] = 'FAC_2P_DCDC_IMAS'
    MODELS[_ConstPSBSMP.E_PS_MODEL_UNINITIALIZED] = 'Uninitialized'
    MODELS = tuple(MODELS)

    PWRSTATE_SEL = _csdev.ETypes.OFF_ON
    PWRSTATE_STS = ('Off', 'On', 'Initializing')
    STATES = ('Off', 'Interlock', 'Initializing',
              'SlowRef', 'SlowRefSync', 'Cycle', 'RmpWfm', 'MigWfm', 'FastRef')
    OPMODES = ('SlowRef', 'SlowRefSync', 'Cycle',
               'RmpWfm', 'MigWfm', 'FastRef')
    CMD_ACK = ('OK', 'Local', 'PCHost', 'Interlocked', 'UDC_locked',
               'DSP_TimeOut', 'DSP_Busy', 'Invalid',)
    _UNDEF_INTLCK = (
        'Bit0', 'Bit1', 'Bit2', 'Bit3',
        'Bit4', 'Bit5', 'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
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
        'Falha nos drivers do modulo',
        'Contato do rele de entrada do DC-Link colado',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    ALARMS_FBP = (
        'Alta frequencia de pulsos de sincronismo',
        'Bit1', 'Bit2', 'Bit3',
        'Bit4', 'Bit5', 'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FBP_DCLINK = _UNDEF_INTLCK
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
        'Falha no DCCT 1', 'Falha no DCCT 2',
        'Alta diferenca entre DCCTs',
        'Falha na leitura da corrente na carga do DCCT 1',
        'Falha na leitura da corrente na carga do DCCT 2',
        'Bit5', 'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FAC_DCDC = (
        'Sobre-corrente na carga',
        'Sobre-tensao no DC-Link', 'Sub-tensao no DC-Link',
        'Interlock da placa IIB',
        'Interlock externo', 'Interlock do rack',
        'Alta corrente de fuga', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    ALARMS_FAC_DCDC = ALARMS_FBP
    IIB_INTLCK_FAC_DCDC = (
        'Sobre-tensao de entrada',
        'Sobre-corrente de entrada',
        'Sobre-corrente de saida',
        'Sobre-temperatura no IGBT 1',
        'Sobre-temperatura no IGBT 1 (HW)',
        'Sobre-temperatura no IGBT 2',
        'Sobre-temperatura no IGBT 2 (HW)',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Erro no driver do IGBT Top 1',
        'Erro no driver do IGBT Bottom 1',
        'Erro no driver do IGBT Top 2',
        'Erro no driver do IGBT Bottom 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_ALARMS_FAC_DCDC = (
        'Sobre-tensao de entrada',
        'Sobre-corrente de entrada',
        'Sobre-corrente de saida',
        'Sobre-temperatura no IGBT 1',
        'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAC_2S_DCDC = (
        'Falha no DCCT1', 'Falha no DCCT2',
        'Alta diferenca entre DCCTs',
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
        'Sobre-corrente na carga',
        'Sobre-tensao no DC-Link do modulo 1',
        'Sobre-tensao no DC-Link do modulo 2',
        'Sub-tensao no DC-Link do modulo 1',
        'Sub-tensao no DC-Link do modulo 2',
        'Interlock da placa IIB do modulo 1',
        'Interlock da placa IIB do modulo 2',
        'Interlock externo', 'Interlock dos racks',
        'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    ALARMS_FAC_2S_DCDC = ALARMS_FBP
    IIB_INTLCK_FAC_2S_DCDC = (
        'Sobre-tensao de entrada',
        'Sobre-corrente de entrada',
        'Sobre-corrente de saida',
        'Sobre-temperatura no IGBT 1',
        'Sobre-temperatura no IGBT 1 (HW)',
        'Sobre-temperatura no IGBT 2',
        'Sobre-temperatura no IGBT 2 (HW)',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Erro no driver do IGBT Top 1',
        'Erro no driver do IGBT Bottom 1',
        'Erro no driver do IGBT Top 2',
        'Erro no driver do IGBT Bottom 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_ALARMS_FAC_2S_DCDC = (
        'Sobre-tensao de entrada',
        'Sobre-corrente de entrada',
        'Sobre-corrente de saida',
        'Sobre-temperatura no IGBT 1',
        'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAC_2S_ACDC = _UNDEF_INTLCK
    HARD_INTLCK_FAC_2S_ACDC = (
        'Sobre-tensao no banco de capacitores',
        'Sobre-tensao na saida do retificador',
        'Sub-tensao na saida do retificador',
        'Sobre-corrente na saida do retificador',
        'Contator de entrada AC trifasica colado',
        'Abertura do contator de entrada AC trifasica',
        'Interlock da placa IIB do estagio de entrada',
        'Interlock da placa IIB da gaveta de comando',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIBIS_INTLCK_FAC_2S_ACDC = (
        'Sobre-tensao de entrada',
        'Sobre-corrente de entrada',
        'Sobre-temperatura no IGBT',
        'Sobre-temperatura no IGBT(HW)',
        'Sobre-tensao do driver do IGBT',
        'Sobre-corrente no driver do IGBT',
        'Erro no driver do IGBT Top',
        'Erro no driver do IGBT Bottom',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIBIS_ALARMS_FAC_2S_ACDC = (
        'Sobre-tensao de entrada',
        'Sobre-corrente de entrada',
        'Sobre-temperatura no IGBT',
        'Sobre-tensao do driver do IGBT',
        'Sobre-corrente no driver do IGBT',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIBCMD_INTLCK_FAC_2S_ACDC = (
        'Sobre-tensao do banco de capacitores',
        'Sobre-tensao do modulo de saida',
        'Sobre-tensao das placas externas',
        'Sobre-corrente da placa auxiliar',
        'Sobre-corrente da placa IDB',
        'Sobre-temperatura no indutor do retificador',
        'Sobre-temperatura no dissipador de calor do retificador',
        'Sobre-corrente da entrada AC trifasica',
        'Botao de emergencia',
        'Sobre-tensao da entrada AC trifasica',
        'Sub-tensao da entrada AC trifasica',
        'Alta corrente de fuga',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIBCMD_ALARMS_FAC_2S_ACDC = (
        'Sobre-tensao do banco de capacitores',
        'Sobre-tensao do modulo de saida',
        'Sobre-tensao das placas externas',
        'Sobre-corrente da placa auxiliar',
        'Sobre-corrente da placa IDB',
        'Sobre-temperatura no indutor do retificador',
        'Sobre-temperatura no dissipador de calor do retificador',
        'Alta corrente de fuga',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAC_2P4S_DCDC = (
        'Falha no DCCT 1', 'Falha no DCCT 2',
        'Alta diferenca entre DCCTs',
        'Falha na leitura da corrente na carga do DCCT 1',
        'Falha na leitura da corrente na carga do DCCT 2',
        'Sobre-corrente no braco 1', 'Sobre-corrente no braco 2',
        'Alta diferenca entre a corrente dos bracos',
        'Interlock da fonte complementar', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    HARD_INTLCK_FAC_2P4S_DCDC = (
        'Sobre-corrente na carga',
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
        'Interlock da placa IIB do modulo 1',
        'Interlock da placa IIB do modulo 2',
        'Interlock da placa IIB do modulo 3',
        'Interlock da placa IIB do modulo 4',
        'Interlock da placa IIB do modulo 5',
        'Interlock da placa IIB do modulo 6',
        'Interlock da placa IIB do modulo 7',
        'Interlock da placa IIB do modulo 8',
        'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    ALARMS_FAC_2P4S_DCDC = ALARMS_FBP
    IIB_INTLCK_FAC_2P4S_DCDC = (
        'Sobre-tensao de entrada', 'Sobre-corrente de entrada',
        'Sobre-corrente de saida',
        'Sobre-temperatura no IGBT 1', 'Sobre-temperatura no IGBT 1 (HW)',
        'Sobre-temperatura no IGBT 2', 'Sobre-temperatura no IGBT 2 (HW)',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Erro no driver do IGBT Top 1',
        'Erro no driver do IGBT Bottom 1',
        'Erro no driver do IGBT Top 2',
        'Erro no driver do IGBT Bottom 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_ALARMS_FAC_2P4S_DCDC = (
        'Sobre-tensao de entrada', 'Sobre-corrente de entrada',
        'Sobre-corrente de saida',
        'Sobre-temperatura no IGBT 1', 'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAC_2P4S_ACDC = _UNDEF_INTLCK
    HARD_INTLCK_FAC_2P4S_ACDC = (
        'Sobre-tensao no banco de capacitores',
        'Sobre-tensao na saida do retificador',
        'Sub-tensao na saida do retificador',
        'Sobre-corrente na saida do retificador',
        'Contator de entrada AC trifasica colado',
        'Abertura do contator de entrada AC trifasica ',
        'Interlock da placa IIB do estagio de entrada',
        'Interlock da placa IIB da gaveta de comando',
        'Bit8', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIBIS_INTLCK_FAC_2P4S_ACDC = (
        'Sobre-tensao de entrada', 'Sobre-corrente de entrada',
        'Sobre-temperatura no IGBT', 'Sobre-temperatura no IGBT (HW)',
        'Sobre-tensao do driver do IGBT', 'Sobre-corrente no driver do IGBT',
        'Erro no driver do IGBT Top', 'Erro no driver do IGBT Bottom',
        'Sobre-temperatura nos indutores', 'Sobre-temperatura no dissipador',
        'Sobre-temperatura da placa IIB', 'Alta umidade relativa',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIBIS_ALARMS_FAC_2P4S_ACDC = (
        'Sobre-tensao de entrada', 'Sobre-corrente de entrada',
        'Sobre-temperatura no IGBT', 'Sobre-tensao do driver do IGBT',
        'Sobre-corrente no driver do IGBT', 'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador', 'Sobre-temperatura da placa IIB',
        'Alta umidade relativa', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIBCMD_INTLCK_FAC_2P4S_ACDC = (
        'Sobre-tensao do banco de capacitores',
        'Sobre-tensao do modulo de saida',
        'Sobre-tensao das placas externas',
        'Sobre-corrente da placa auxiliar',
        'Sobre-corrente da placa IDB',
        'Sobre-temperatura no indutor do retificador',
        'Sobre-temperatura no dissipador de calor do retificador',
        'Sobre-corrente da entrada AC trifasica',
        'Botao de emergencia',
        'Sobre-tensao da entrada AC trifasica',
        'Sub-tensao da entrada AC trifasica',
        'Alta corrente de fuga',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIBCMD_ALARMS_FAC_2P4S_ACDC = (
        'Sobre-tensao do banco de capacitores',
        'Sobre-tensao do modulo de saida',
        'Sobre-tensao das placas externas',
        'Sobre-corrente da placa auxiliar',
        'Sobre-corrente da placa IDB',
        'Sobre-temperatura no indutor do retificador',
        'Sobre-temperatura no dissipador de calor do retificador',
        'Alta corrente de fuga',
        'Sobre-temperatura da placa IIB', 'Alta umidade relativa',
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
        'Alta diferenca entre a corrente dos IGBTs',
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
        'Contator de entrada do DC-Link colado',
        'Abertura do contator de entrada do DC-Link',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Interlock da placa IIB', 'Bit9', 'Bit10', 'Bit11',
        'Bit12', 'Bit13', 'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    ALARMS_FAP = ALARMS_FBP
    IIB_INTLCK_FAP = (
        'Sobre-tensao de entrada', 'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1', 'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente do driver do IGBT 1',
        'Sobre-corrente do driver do IGBT 2', 'Erro no driver do IGBT 1',
        'Erro no driver do IGBT 2', 'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Falha no contator de entrada do DC-Link',
        'Contator de entrada do DC-Link colado', 'Interlock externo',
        'Interlock do rack', 'Alta corrente de fuga',
        'Sobre-temperatura da placa IIB', 'Alta umidade relativa',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_ALARMS_FAP = (
        'Sobre-tensao de entrada', 'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1', 'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador', 'Alta corrente de fuga',
        'Sobre-temperatura da placa IIB', 'Alta umidade relativa',
        'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAP_4P = SOFT_INTLCK_FAP
    HARD_INTLCK_FAP_4P = (
        'Sobre-corrente na carga',
        'Sobre-tensao na carga',
        'Sobre-corrente no IGBT 1 do modulo 1',
        'Sobre-corrente no IGBT 2 do modulo 1',
        'Sobre-corrente no IGBT 1 do modulo 2',
        'Sobre-corrente no IGBT 2 do modulo 2',
        'Sobre-corrente no IGBT 1 do modulo 3',
        'Sobre-corrente no IGBT 2 do modulo 3',
        'Sobre-corrente no IGBT 1 do modulo 4',
        'Sobre-corrente no IGBT 2 do modulo 4',
        'Contator de entrada do DC-Link colado do modulo 1',
        'Contator de entrada do DC-Link colado do modulo 2',
        'Contator de entrada do DC-Link colado do modulo 3',
        'Contator de entrada do DC-Link colado do modulo 4',
        'Abertura do contato de entrada do DC-Link do modulo 1',
        'Abertura do contato de entrada do DC-Link do modulo 2',
        'Abertura do contato de entrada do DC-Link do modulo 3',
        'Abertura do contato de entrada do DC-Link do modulo 4',
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
        'Bit30', 'Bit31')
    ALARMS_FAP_4P = ALARMS_FBP
    IIB_INTLCK_FAP_4P_MOD1 = IIB_INTLCK_FAP
    IIB_ALARMS_FAP_4P_MOD1 = (
        'Sobre-tensao de entrada', 'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1', 'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador', 'Alta corrente de fuga',
        'Sobre-temperatura da placa IIB', 'Alta umidade relativa',
        'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_INTLCK_FAP_4P_MOD234 = (
        'Sobre-tensao de entrada', 'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1', 'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente do driver do IGBT 1',
        'Sobre-corrente do driver do IGBT 2', 'Erro no driver do IGBT 1',
        'Erro no driver do IGBT 2', 'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Falha no contator de entrada do DC-Link',
        'Contator de entrada do DC-Link colado', 'Interlock externo',
        'Interlock do rack', 'Bit17',
        'Sobre-temperatura da placa IIB', 'Alta umidade relativa',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_ALARMS_FAP_4P_MOD234 = (
        'Sobre-tensao de entrada', 'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1', 'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1', 'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador', 'Bit11',
        'Sobre-temperatura da placa IIB', 'Alta umidade relativa',
        'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    SOFT_INTLCK_FAP_2P2S = (
        'Falha no DCCT 1', 'Falha no DCCT 2',
        'Alta diferenca entre DCCTs',
        'Falha de leitura da corrente na carga do DCCT 1',
        'Falha de leitura da corrente na carga do DCCT 2',
        'Alta diferenca entre a corrente dos bracos',
        'Alta diferenca entre a corrente dos IGBTs',
        'Interlock da fonte complementar',
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
        'Contator de entrada do DC-Link colado do modulo 1',
        'Contator de entrada do DC-Link colado do modulo 2',
        'Contator de entrada do DC-Link colado do modulo 3',
        'Contator de entrada do DC-Link colado do modulo 4',
        'Abertura do contator de entrada do DC-Link do modulo 1',
        'Abertura do contator de entrada do DC-Link do modulo 2',
        'Abertura do contator de entrada do DC-Link do modulo 3',
        'Abertura do contator de entrada do DC-Link do modulo 4',
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
        'Sobre-corrente no braco 1',
        'Sobre-corrente no braco 2',
        'Bit31')
    ALARMS_FAP_2P2S = ALARMS_FBP
    IIB_INTLCK_FAP_2P2S_MOD1 = (
        'Sobre-tensao de entrada',
        'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1',
        'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1',
        'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Erro no driver do IGBT 1',
        'Erro no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Falha no contator de entrada do DC-Link',
        'Contator de entrada do DC-Link colado',
        'Interlock Externo',
        'Interlock do Rack',
        'Alta corrente de fuga',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_ALARMS_FAP_2P2S_MOD1 = (
        'Sobre-tensao de entrada',
        'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1',
        'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1',
        'Sobre-temperatura no IGBT 2',
        'Sobre-tensao nos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Alta corrente de fuga',
        'Sobre-temperatura na placa IIB',
        'Alta umidade relativa',
        'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_INTLCK_FAP_2P2S_MOD234 = (
        'Sobre-tensao de entrada',
        'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1',
        'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1',
        'Sobre-temperatura no IGBT 2',
        'Sobre-tensao dos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Erro no driver do IGBT 1',
        'Erro no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Falha no contator de entrada do DC-Link',
        'Contator de entrada do DC-Link colado',
        'Interlock Externo',
        'Interlock do Rack',
        'Bit17',
        'Sobre-temperatura da placa IIB',
        'Alta umidade relativa',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')
    IIB_ALARMS_FAP_2P2S_MOD234 = (
        'Sobre-tensao de entrada',
        'Sobre-tensao de saida',
        'Sobre-corrente no IGBT 1',
        'Sobre-corrente no IGBT 2',
        'Sobre-temperatura no IGBT 1',
        'Sobre-temperatura no IGBT 2',
        'Sobre-tensao nos drivers dos IGBTs',
        'Sobre-corrente no driver do IGBT 1',
        'Sobre-corrente no driver do IGBT 2',
        'Sobre-temperatura nos indutores',
        'Sobre-temperatura no dissipador',
        'Bit11',
        'Sobre-temperatura na placa IIB',
        'Alta umidade relativa',
        'Bit14', 'Bit15',
        'Bit16', 'Bit17', 'Bit18', 'Bit19',
        'Bit20', 'Bit21', 'Bit22', 'Bit23',
        'Bit24', 'Bit25', 'Bit26', 'Bit27',
        'Bit28', 'Bit29', 'Bit30', 'Bit31')

    CYCLE_TYPES = ['', ] * 5
    CYCLE_TYPES[_ConstPSBSMP.E_SIGGENTYPE_SINE] = 'Sine'
    CYCLE_TYPES[_ConstPSBSMP.E_SIGGENTYPE_DAMPEDSINE] = 'DampedSine'
    CYCLE_TYPES[_ConstPSBSMP.E_SIGGENTYPE_TRAPEZOIDAL] = 'Trapezoidal'
    CYCLE_TYPES[_ConstPSBSMP.E_SIGGENTYPE_DAMPEDSQUAREDSINE] = \
        'DampedSquaredSine'
    CYCLE_TYPES[_ConstPSBSMP.E_SIGGENTYPE_SQUARE] = 'Square'
    CYCLE_TYPES = tuple(CYCLE_TYPES)

    WFMREF_SYNCMODE = ['', ] * 3
    WFMREF_SYNCMODE[_ConstPSBSMP.E_WFMREFSYNC_SAMPLEBYSAMPLE] = \
        'SampleBySample'
    WFMREF_SYNCMODE[_ConstPSBSMP.E_WFMREFSYNC_SAMPLEBYSAMPLE_ONECYCLE] = \
        'SampleBySample_OneCycle'
    WFMREF_SYNCMODE[_ConstPSBSMP.E_WFMREFSYNC_ONESHOT] = 'OneShot'
    WFMREF_SYNCMODE = tuple(WFMREF_SYNCMODE)

    LINAC_INTLCK_WARN = (
        'LoadI 0C Shutdown', 'LoadI 0C Interlock',
        'LoadV 0V Shutdown', 'LoadV 0V Interlock',
        'Ext Interlock Fault', 'LoadI Over Thrs', 'TestPoint', 'ADC Cali')
    LINAC_INTLCK_SGIN = (
        'Fan state', 'Unused', 'Unused', 'DC-Link Delay Feedback',
        'Unused', 'Unused', 'Unused', 'Unused', 'Unused',
        'External interlock 1', 'External interlock 2',
        'Power Module OverTemp', 'DCCT Status', 'Output OverCurrent',
        'Output OverVoltage', 'DC-Link UnderVoltage')
    LINAC_INTLCK_RDSGIN_MASK = (
        'Bit0', 'Bit1', 'Bit2', 'Bit3', 'Bit4', 'Bit5', 'Bit6', 'Bit7',
        'Bit8', 'Bit9', 'Bit10', 'Bit11', 'Bit12', 'Bit13', 'Bit14', 'Bit15')
    LINAC_INTLCK_SGOUT = (
        'DC-Link ON', 'Unused', 'Unused', 'Unused', 'Unused', 'Unused',
        'Threshold Warning', 'Overcurr./overvolt./ext. interlock')
    LINAC_INTLCK_RDSGOUT_MASK = (
        'Bit0', 'Bit1', 'Bit2', 'Bit3', 'Bit4', 'Bit5', 'Bit6', 'Bit7')

    FOFB_OPMODES_SEL = ('manual', 'fofb')
    FOFB_OPMODES_STS = ('manual', 'fofb', 'unknown')
    FOFB_CURRLOOPMODES = (
        'open_loop_manual',
        'open_loop_test_sqr',
        'closed_loop_manual',
        'closed_loop_test_sqr',
        'closed_loop_fofb')
    FOFB_ALARMS_AMP = (
        'Amplifier left over current flag',
        'Amplifier left over temperature flag',
        'Amplifier right over current flag',
        'Amplifier right over temperature flag',
    )


_et = ETypes  # syntactic sugar


# --- Const class ---

class Const(_csdev.Const):
    """Const class defining power supply constants."""

    Models = _csdev.Const.register('Models', _et.MODELS)
    Interface = _csdev.Const.register('Interface', _et.INTERFACE)
    OpenLoop = _csdev.Const.register('OpenLoop', _et.CLOSE_OPEN)
    States = _csdev.Const.register('States', _et.STATES)
    PwrStateSel = _csdev.Const.register('PwrStateSel', _et.PWRSTATE_SEL)
    PwrStateSts = _csdev.Const.register('PwrStateSts', _et.PWRSTATE_STS)
    OpMode = _csdev.Const.register('OpMode', _et.OPMODES)
    CmdAck = _csdev.Const.register('CmdAck', _et.CMD_ACK)
    CycleType = _csdev.Const.register('CycleType', _et.CYCLE_TYPES)
    WfmRefSyncMode = _csdev.Const.register(
        'WfmRefSyncMode', _et.WFMREF_SYNCMODE)
    DsblEnbl = _csdev.Const.register('DsblEnbl', _et.DSBL_ENBL)
    OpModeFOFBSel = _csdev.Const.register(
        'OpModeFOFBSel', _et.FOFB_OPMODES_SEL)
    OpModeFOFBSts = _csdev.Const.register(
        'OpModeFOFBSts', _et.FOFB_OPMODES_STS)
    CurrLoopModeFOFB = _csdev.Const.register(
        'CurrLoopModeFOFB', _et.FOFB_CURRLOOPMODES)

# --- Main power supply database functions ---


def get_ps_propty_database(psmodel=None, pstype=None, psname=None):
    """Return epics properties database for a power supply model and type."""
    # in case psname is given
    if psname is not None:
        psmodel = _PSSearch.conv_psname_2_psmodel(psname)
        pstype = _PSSearch.conv_psname_2_pstype(psname)

    # get dbase for a specific psmodel
    dbase = _get_model_db(psmodel)

    # insert corresponding strengths
    dbase = _insert_strengths(dbase, pstype)

    # update limits
    _set_limits(pstype, dbase)

    # add pvs list as Properties-Cte
    if not psmodel.startswith('FP_'):
        dbase = _csdev.add_pvslist_cte(dbase)

    # return database
    return dbase


def get_conv_propty_database(pstype=None, psname=None):
    """Return strength database definition for a power supply type."""
    # in case psname is given
    if psname is not None:
        pstype = _PSSearch.conv_psname_2_pstype(psname)

    # update with strengths
    dbase = _insert_strengths(dict(), pstype)

    # return database
    return dbase


def get_ps_interlocks(psmodel=None, psname=None):
    """Return interlock PVs for a power supply model."""
    # in case psname is given
    if psname is not None:
        psmodel = _PSSearch.conv_psname_2_psmodel(psname)

    dbase = _get_model_db(psmodel)
    intlks = [k for k in dbase.keys() if 'Mon' in k and
              ('Intlk' in k or 'Alarm' in k)]
    return intlks


def get_ps_modules(psmodel=None, psname=None):
    """Return PS modules for a power supply model."""
    # in case psname is given
    if psname is not None:
        psmodel = _PSSearch.conv_psname_2_psmodel(psname)

    dbase = _get_model_db(psmodel)
    modules = set()
    for k in dbase:
        if ('Mod' in k) and ('Labels-Cte' in k):
            aux = k.split('Mod')
            aux = aux[1].split('Labels-Cte')
            mod = aux[0]
            modules.add(mod)
    return sorted(modules)


def get_ps_scopesourcemap(psname):
    """Return PS modules for a power supply model."""
    psmodel = _PSSearch.conv_psname_2_psmodel(psname)
    psudcindex = _PSSearch.conv_psname_2_udcindex(psname)
    if psmodel == 'FBP':
        return {
            'Output current [A]': 0xD000 + 2*psudcindex,
            'Output voltage [V]': 0xC008 + 2*psudcindex,
            'Tracking error [A or V]': 0xD008 + 2*psudcindex,
            'DCLink voltage [V]': 0xC000 + 2*psudcindex,
            'PWM duty cycle [p.u.]': 0xD040 + 2*psudcindex,
        }
    if psmodel == 'FAC_DCDC':
        return {
            'Output current [A]': 0xD006,
            'Output voltage [V]': 0xC000,
            'Tracking error [A or V]': 0xD008,
            'DCLink voltage [V]': 0xD004,
            'PWM duty cycle [p.u.]': 0xD040,
        }
    if psmodel == 'FAC_2S_DCDC':
        return {
            'Output current [A]': 0xD008,
            'Tracking error [A or V]': 0xD00A,
            'PWM duty cycle [p.u.]': 0xD040,
        }
    if psmodel == 'FAC_2S_ACDC':
        return {
            'Output voltage [V]': 0xD000 + 2*psudcindex,
            'Tracking error [A or V]': 0xD00C + 14*psudcindex,
            'PWM duty cycle [p.u.]': 0xD040 + 2*psudcindex,
        }
    if psmodel == 'FAC_2P4S_DCDC':
        return {
            'Output current [A]': 0xD008,
            'Tracking error [A or V]': 0xD00A,
            'PWM duty cycle [p.u.]': 0xD040,
        }
    if psmodel == 'FAC_2P4S_ACDC':
        return {
            'Output voltage [V]': 0xD000 + 2*psudcindex,
            'Tracking error [A or V]': 0xD00C + 14*psudcindex,
            'DCLink voltage [V]': 0xC000 + 2*psudcindex,
            'PWM duty cycle [p.u.]': 0xD040 + 2*psudcindex,
        }
    if psmodel == 'FAP':
        return {
            'Output current [A]': 0xD006,
            'Output voltage [V]': 0xC004,
            'Tracking error [A or V]': 0xD008,
            'DCLink voltage [V]': 0xD004,
            'PWM duty cycle [p.u.]': 0xD040,
        }
    if psmodel == 'FAP_2P2S':
        return {
            'Output current [A]': 0xD008,
            'Tracking error [A or V]': 0xD00A,
            'PWM duty cycle [p.u.]': 0xD040,
        }
    if psmodel == 'FAP_4P':
        return {
            'Output current [A]': 0xD006,
            'Tracking error [A or V]': 0xD008,
            'PWM duty cycle [p.u.]': 0xD040,
        }
    return dict()


# --- Auxiliary functions ---


def _get_ps_common_propty_database():
    """Return database entries to all BSMP-like devices."""
    dbase = {
        'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
        'TimestampBoot-Cte': {'type': 'float', 'value': 0,
                              'prec': 7, 'unit': 'timestamp'},
        'TimestampUpdate-Mon': {'type': 'float', 'value': 0,
                                'prec': 7, 'unit': 'timestamp'},
        'CtrlMode-Mon': {'type': 'enum', 'enums': _et.INTERFACE,
                         'value': Const.Interface.Remote,
                         'unit': 'ctrlmode'},
        # Common Variables
        'PwrState-Sel': {'type': 'enum', 'enums': _et.PWRSTATE_SEL,
                         'value': Const.PwrStateSel.Off,
                         'unit': 'pwrstate'},
        'PwrState-Sts': {'type': 'enum', 'enums': _et.PWRSTATE_STS,
                         'value': Const.PwrStateSts.Off,
                         'unit': 'pwrstate'},
        'CtrlLoop-Sel': {'type': 'enum', 'enums': _et.CLOSE_OPEN,
                         'value': Const.OpenLoop.Open,
                         'unit': 'ctrlloop'},
        'CtrlLoop-Sts': {'type': 'enum', 'enums': _et.CLOSE_OPEN,
                         'value': Const.OpenLoop.Open,
                         'unit': 'ctrlloop'},
        'OpMode-Sel': {'type': 'enum', 'enums': _et.OPMODES,
                       'value': Const.OpMode.SlowRef,
                       'unit': 'opmode_sel'},
        'OpMode-Sts': {'type': 'enum', 'enums': _et.STATES,
                       'value': Const.OpMode.SlowRef,
                       'unit': 'opmode_sts'},
        # PRU
        'PRUCtrlQueueSize-Mon': {'type': 'int', 'value': 0,
                                 'unit': 'count',
                                 'low': -1, 'lolo': -1,
                                 'high': 50, 'hihi': 50},
        # Interlocks
        'IntlkSoft-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkHard-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'Reset-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
        # Wfm
        'WfmSelected-Mon': {
            'type': 'int', 'value': DEFAULT_WFM_SELECTED ,
             'unit': 'wfmselected'},
        'WfmSyncMode-Sel': {
            'type': 'enum', 'enums': _et.WFMREF_SYNCMODE,
            'value': _ConstPSBSMP.E_WFMREFSYNC_ONESHOT},
        'WfmSyncMode-Sts': {
            'type': 'enum', 'enums': _et.WFMREF_SYNCMODE,
            'value': _ConstPSBSMP.E_WFMREFSYNC_ONESHOT},
        'WfmFreq-SP': {
            'type': 'float',
            'value': DEFAULT_WFM_FREQUENCY, 'prec': 4, 'unit': 'Hz',
            'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 1e5, 'high': 1e5, 'hihi': 1e5},
        'WfmFreq-RB': {
            'type': 'float',
            'value': DEFAULT_WFM_FREQUENCY, 'prec': 4, 'unit': 'Hz',
            'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 1e5, 'high': 1e5, 'hihi': 1e5},
        'WfmGain-SP': {
            'type': 'float', 'value': DEFAULT_WFM_GAIN,
            'prec': 4, 'unit': 'wfmgain',
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 1000, 'high': 1000, 'hihi': 1000},
        'WfmGain-RB': {
            'type': 'float', 'value': DEFAULT_WFM_GAIN,
            'prec': 4, 'unit': 'wfmgain',
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 1000, 'high': 1000, 'hihi': 1000},
        'WfmOffset-SP': {
            'type': 'float', 'value': DEFAULT_WFM_OFFSET,
            'prec': PS_CURRENT_PRECISION, 'unit': 'A'},
        'WfmOffset-RB': {
            'type': 'float', 'value': DEFAULT_WFM_OFFSET,
            'prec': PS_CURRENT_PRECISION, 'unit': 'A'},
        # Scope
        'ScopeSrcAddr-SP': {
            'type': 'int', 'value': 0x0000C000, 'unit': 'scope_srcaddr',
            'lolo': 0x0000C000, 'low': 0x0000C000, 'lolim': 0x0000C000,
            'hilim': 0x00013FFE, 'high': 0x00013FFE, 'hihi': 0x00013FFE},
        'ScopeSrcAddr-RB': {
            'type': 'int', 'value': 0x0000C000, 'unit': 'scope_srcaddr',
            'lolo': 0x0000C000, 'low': 0x0000C000, 'lolim': 0x0000C000,
            'hilim': 0x00013FFE, 'high': 0x00013FFE, 'hihi': 0x00013FFE},
        'ScopeFreq-SP': {
            'type': 'float', 'value': 1.0, 'prec': 4, 'unit': 'Hz',
            'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 1e5, 'high': 1e5, 'hihi': 1e5},
        'ScopeFreq-RB': {
            'type': 'float', 'value': 1.0, 'prec': 4, 'unit': 'Hz',
            'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 1e5, 'high': 1e5, 'hihi': 1e5},
        'ScopeDuration-SP': {
            'type': 'float', 'value': 1.0, 'prec': 4, 'unit': 's',
            'lolo': 1e-2, 'low': 1e-2, 'lolim': 1e-2,
            'hilim': 4096, 'high': 4096, 'hihi': 4096},
        'ScopeDuration-RB': {
            'type': 'float', 'value': 1.0, 'prec': 4, 'unit': 's',
            'lolo': 1e-2, 'low': 1e-2, 'lolim': 1e-2,
            'hilim': 4096, 'high': 4096, 'hihi': 4096},
        # Trigger pulse diagnostics
        'NrCtrlCycBtwLastTrigs-Mon': {
            'type': 'int', 'value': 0, 'unit': 'count'},
        # Power Supply Parameters
        # --- PS ---
        'ParamPSName-Cte': {'type': 'char', 'count': 64, 'value': ''},
        'ParamPSModel-Cte': {'type': 'float', 'value': 0.0, 'unit': 'psmodel'},
        'ParamNrModules-Cte': {'type': 'float', 'value': 0.0, 'unit': 'count'},
        # --- COMM ---
        'ParamCommCmdInferface-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'cmdinterface'},
        'ParamCommRS485BaudRate-Cte': {
            'type': 'float', 'value': 0.0, 'units': 'bps'},
        'ParamCommRS485Addr-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        'ParamCommRS485TermRes-Cte': {'type': 'float', 'value': 0.0},
        'ParamCommUDCNetAddr-Cte': {'type': 'float', 'value': 0.0},
        'ParamCommEthIP-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        'ParamCommEthSubnetMask-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        'ParamCommBuzVol-Cte': {
            'type': 'float', 'value': 0.0, 'unit': '%'},
        # --- Control ---
        'ParamCtrlFreqCtrlISR-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'Hz'},
        'ParamCtrlFreqTimeSlicer-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4), 'unit': 'Hz'},
        'ParamCtrlLoopState-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'ctrlloop'},
        'ParamCtrlMaxRef-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4), 'unit': 'A/V'},
        'ParamCtrlMinRef-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4), 'unit': 'A/V'},
        'ParamCtrlMaxRefOpenLoop-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4), 'unit': '%'},
        'ParamCtrlMinRefOpenLoop-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4), 'unit': '%'},
        # --- PWM ---
        'ParamPWMFreq-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'Hz'},
        'ParamPWMDeadTime-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'ns'},
        'ParamPWMMaxDuty-Cte': {
            'type': 'float', 'value': 0.0, 'unit': '%', 'prec': 3},
        'ParamPWMMinDuty-Cte': {
            'type': 'float', 'value': 0.0, 'unit': '%', 'prec': 3},
        'ParamPWMMaxDutyOpenLoop-Cte': {
            'type': 'float', 'value': 0.0, 'unit': '%', 'prec': 3},
        'ParamPWMMinDutyOpenLoop-Cte': {
            'type': 'float', 'value': 0.0, 'unit': '%', 'prec': 3},
        'ParamPWMLimDutyShare-Cte': {
            'type': 'float', 'value': 0.0, 'unit': '%', 'prec': 3},
        # ----- HRADC -----
        'ParamHRADCNrBoards-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'count'},
        'ParamHRADCSpiClk-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'MHz'},
        'ParamHRADCFreqSampling-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'Hz'},
        'ParamHRADCEnableHeater-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        'ParamHRADCEnableRails-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        'ParamHRADCTransducerOutput-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        'ParamHRADCTransducerGain-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        'ParamHRADCTransducerOffset-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        # ----- SigGen -----
        'ParamSigGenType-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'siggentype'},
        'ParamSigGenNumCycles-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'siggennumcycles'},
        'ParamSigGenFreq-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'Hz'},
        'ParamSigGenAmplitude-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'A/V/%'},
        'ParamSigGenOffset-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'A/V/%'},
        'ParamSigGenAuxParam-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        # ----- WfmRef -----
        'ParamWfmRefId-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        'ParamWfmRefSyncMode-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4)},
        'ParamWfmRefFreq-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4), 'unit': 'Hz'},
        'ParamWfmRefGain-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4), 'unit': 'A/V/%'},
        'ParamWfmRefOffset-Cte': {
            'type': 'float', 'count': 4,
            'value': _np.array([0.0, ] * 4), 'unit': 'A/V/%'},
        # --- Analog Variables ---
        'ParamAnalogMax-Cte': {
            'type': 'float', 'count': 64,
            'value': _np.array([0.0, ] * 64)},
        'ParamAnalogMin-Cte': {
            'type': 'float', 'count': 64,
            'value': _np.array([0.0, ] * 64)},
        # --- Debounce Manager ---
        'ParamHardIntlkDebounceTime-Cte': {
            'type': 'float', 'count': 32,
            'value': _np.array([0.0, ] * 32), 'unit': 'us'},
        'ParamHardIntlkResetTime-Cte': {
            'type': 'float', 'count': 32,
            'value': _np.array([0.0, ] * 32), 'unit': 'us'},
        'ParamSoftIntlkDebounceTime-Cte': {
            'type': 'float', 'count': 32,
            'value': _np.array([0.0, ] * 32), 'unit': 'us'},
        'ParamSoftIntlkResetTime-Cte': {
            'type': 'float', 'count': 32,
            'value': _np.array([0.0, ] * 32), 'unit': 'us'},
        'ParamScopeSamplingFreq-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'Hz'},
        'ParamScopeDataSource-Cte': {'type': 'float', 'value': 0.0},
        # --- Update Parameters ---
        'ParamUpdate-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
    }
    return dbase


def _get_ps_basic_propty_database():
    """Return database entries to all power-supply-like devices."""
    dbase = _get_ps_common_propty_database()
    dbase.update({
        'Current-SP': {'type': 'float', 'value': 0.0,
                       'prec': PS_CURRENT_PRECISION},
        'Current-RB': {'type': 'float', 'value': 0.0,
                       'prec': PS_CURRENT_PRECISION},
        'CurrentRef-Mon': {'type': 'float', 'value': 0.0,
                           'prec': PS_CURRENT_PRECISION},
        'Current-Mon': {'type': 'float', 'value': 0.0,
                        'prec': PS_CURRENT_PRECISION},
        # Commands
        'Abort-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
        'SyncPulse-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
        # Cycle
        'CycleEnbl-Mon': {'type': 'int', 'value': 0, 'unit': 'cycleenbl'},
        'CycleType-Sel': {
            'type': 'enum', 'enums': _et.CYCLE_TYPES, 'unit': 'cycletype',
            'value': DEFAULT_SIGGEN_CONFIG[0]},
        'CycleType-Sts': {
            'type': 'enum', 'enums': _et.CYCLE_TYPES, 'unit': 'cycletype',
            'value': DEFAULT_SIGGEN_CONFIG[0]},
        'CycleNrCycles-SP': {
            'type': 'int', 'value': DEFAULT_SIGGEN_CONFIG[1], 'unit': 'count'},
        'CycleNrCycles-RB': {
            'type': 'int', 'value': DEFAULT_SIGGEN_CONFIG[1], 'unit': 'count'},
        'CycleFreq-SP': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[2],
                         'unit': 'Hz', 'prec': 4},
        'CycleFreq-RB': {'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[2],
                         'unit': 'Hz', 'prec': 4},
        'CycleAmpl-SP': {
            'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[3],
            'prec': PS_CURRENT_PRECISION, 'unit': 'A'},
        'CycleAmpl-RB': {
            'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[3],
            'prec': PS_CURRENT_PRECISION, 'unit': 'A'},
        'CycleOffset-SP': {
            'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[4],
            'prec': PS_CURRENT_PRECISION, 'unit': 'A'},
        'CycleOffset-RB': {
            'type': 'float', 'value': DEFAULT_SIGGEN_CONFIG[4],
            'prec': PS_CURRENT_PRECISION, 'unit': 'A'},
        'CycleAuxParam-SP': {
            'type': 'float', 'count': 4,
            'value': DEFAULT_SIGGEN_CONFIG[5:9]},
        'CycleAuxParam-RB': {
            'type': 'float', 'count': 4,
            'value': DEFAULT_SIGGEN_CONFIG[5:9]},
        'CycleIndex-Mon': {'type': 'int', 'value': 0, 'unit': 'count'},
        # Wfm - UDC
        'Wfm-SP': {'type': 'float', 'count': len(DEFAULT_WFM),
                   'value': list(DEFAULT_WFM), 'unit': 'A',
                   'prec': PS_CURRENT_PRECISION},
        'Wfm-RB': {'type': 'float', 'count': len(DEFAULT_WFM),
                   'value': list(DEFAULT_WFM), 'unit': 'A',
                   'prec': PS_CURRENT_PRECISION},
        'WfmRef-Mon': {'type': 'float', 'count': len(DEFAULT_WFM),
                       'value': list(DEFAULT_WFM), 'unit': 'A',
                       'prec': PS_CURRENT_PRECISION},
        'Wfm-Mon': {'type': 'float', 'count': len(DEFAULT_WFM),
                    'value': list(DEFAULT_WFM), 'unit': 'A/V/p.u.',
                    'prec': PS_CURRENT_PRECISION},
        # 'WfmMonAcq-Sel': {'type': 'enum', 'enums': _et.DSBL_ENBL,
        #                   'value': Const.DsblEnbl.Dsbl},
        'WfmIndex-Mon': {'type': 'int', 'value': 0, 'unit': 'count'},
        'WfmSyncPulseCount-Mon': {'type': 'int', 'value': 0, 'unit': 'count'},
        'WfmUpdate-Cmd': {'type': 'int', 'value': 0, 'unit': 'count'},
        'WfmUpdateAuto-Sel': {
            'type': 'enum', 'enums': _et.DSBL_ENBL,
            'value': Const.DsblEnbl.Dsbl, 'unit': 'wfmupdateauto'},
        'WfmUpdateAuto-Sts': {
            'type': 'enum', 'enums': _et.DSBL_ENBL,
            'value': Const.DsblEnbl.Dsbl, 'unit': 'wfmupdateauto'},
    })

    return dbase


def _get_ps_idff_propty_database():
    """Return PSIDFF properties."""
    dbase = {
        'IDFFMode-Sel': {
            'type': 'enum', 'enums': _et.DSBL_ENBL,
            'value': Const.DsblEnbl.Dsbl, 'unit': 'iocmode'},
        'IDFFMode-Sts': {
            'type': 'enum', 'enums': _et.DSBL_ENBL,
            'value': Const.DsblEnbl.Dsbl, 'unit': 'iocmode'},
        }
    return dbase


def _get_id_apu_propty_database():
    """Return database of APU ID."""
    dbase = {
        'Phase-SP': {'type': 'float', 'value': 0.0,
                     'prec': 4, 'unit': 'mm'},
        'Phase-Mon': {'type': 'float', 'value': 0.0,
                      'prec': 4, 'unit': 'mm'},
    }
    return dbase


def _get_pu_septum_propty_database():
    """Return database of common to all septa pulsed pwrsupply PVs."""
    # S TB-04:PU-InjSept
    # S TS-01:PU-EjeSeptF
    # S TS-01:PU-EjeSeptG
    # S TS-04:PU-InjSeptG-1
    # S TS-04:PU-InjSeptG-2
    # S TS-04:PU-InjSeptF
    dbase = {
        # 'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
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
                       'prec': PU_VOLTAGE_PRECISION},
        'Voltage-RB': {'type': 'float', 'value': 0.0,
                       'prec': PU_VOLTAGE_PRECISION},
        'Voltage-Mon': {'type': 'float', 'value': 0.0,
                        'prec': PU_VOLTAGE_PRECISION},
        'Intlk1-Mon': {'type': 'int', 'value': 0},
        'Intlk2-Mon': {'type': 'int', 'value': 0},
        'Intlk3-Mon': {'type': 'int', 'value': 0},
        'Intlk4-Mon': {'type': 'int', 'value': 0},
        'Intlk5-Mon': {'type': 'int', 'value': 0},
        'Intlk6-Mon': {'type': 'int', 'value': 0},
        'Intlk7-Mon': {'type': 'int', 'value': 0},
        'Intlk1Label-Cte': {'type': 'str', 'value': 'Switch module'},
        'Intlk2Label-Cte': {'type': 'str', 'value': 'AC CPFL OFF'},
        'Intlk3Label-Cte': {'type': 'str', 'value': 'Temperature'},
        'Intlk4Label-Cte': {'type': 'str', 'value': 'Personnel protection'},
        'Intlk5Label-Cte': {'type': 'str', 'value': 'HVPS Overcurrent'},
        'Intlk6Label-Cte': {'type': 'str', 'value': 'HVPS Overvoltage'},
        'Intlk7Label-Cte': {'type': 'str', 'value': 'External'},
    }
    return dbase


def _get_pu_common_propty_database():
    """Return database of common to all pulsed pwrsupply PVs."""
    # K BO-01D:PU-InjKckr
    # K BO-48D:PU-EjeKckr
    # K SI-01SA:PU-InjDpKckr
    # P SI-19C4:PU-PingV
    dbase = _get_pu_septum_propty_database()
    dbase.update({
        'Intlk8-Mon': {'type': 'int', 'value': 0},
        'Intlk8Label-Cte': {'type': 'str', 'value': 'Switch Overcurrent'},
    })
    return dbase


def _get_pu_FP_SEPT_propty_database():  # noqa: N802
    """."""
    return _get_pu_septum_propty_database()


def _get_pu_FP_KCKR_propty_database():  # noqa: N802
    """."""
    return _get_pu_common_propty_database()


def _get_pu_FP_KCKRCCOIL_propty_database():  # noqa: N802
    """."""
    dbase = {
        'Voltage-SP': {'type': 'float', 'value': 0.0,
                       'prec': PU_VOLTAGE_PRECISION},
        'Voltage-RB': {'type': 'float', 'value': 0.0,
                       'prec': PU_VOLTAGE_PRECISION},
        'Voltage-Mon': {'type': 'float', 'value': 0.0,
                        'prec': PU_VOLTAGE_PRECISION},
    }
    return dbase


def _get_pu_FP_PINGER_propty_database():  # noqa: N802
    """."""
    return _get_pu_common_propty_database()


def _get_ps_LINAC_propty_database():  # noqa: N802
    """Return LINAC pwrsupply props."""
    # NOTE: This is a mirror of the PS IOC database in linac-ioc-ps repo.
    version = '2021-11-23'
    propty_db = {
        # --- ioc metapvs
        'Version-Cte': {'type': 'string', 'value': version},
        'TimestampBoot-Cte': {
            'type': 'float', 'value': 0.0, 'unit': 'timestamp'},
        'TimestampUpdate-Mon': {
            'type': 'float', 'value': 0.0, 'unit': 'timestamp'},
        'Connected-Mon': {
            'type': 'enum', 'enums': ['Connected', 'Broken'],
            'states': [_SEVERITY_NO_ALARM, _SEVERITY_MAJOR_ALARM],
            'value': 0, 'unit': 'connected'},
        # --- ps state
        'PwrState-Sel': {
            'type': 'enum', 'enums': ['Pwm_Off', 'Pwm_On'],
            'value': 0, 'unit': 'pwrstate'},  # 40
        'PwrState-Sts': {
            'type': 'enum', 'enums': ['Pwm_Off', 'Pwm_On'],
            'value': 0, 'unit': 'pwrstate'},  # 40
        # --- current
        'Current-SP': {
            'type': 'float', 'prec': PS_CURRENT_PRECISION, 'value': 0.0,
            'unit': 'A', 'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 0.0, 'high': 0.0, 'hihi': 0.0},  # 90
        'Current-RB': {
            'type': 'float', 'prec': PS_CURRENT_PRECISION, 'value': 0.0,
            'unit': 'A', 'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 0.0, 'high': 0.0, 'hihi': 0.0},  # 90
        'Current-Mon': {
            'type': 'float', 'prec': PS_CURRENT_PRECISION, 'value': 0.0,
            'unit': 'A', 'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 0.0, 'high': 0.0, 'hihi': 0.0,
            'mdel': 0.000099, 'adel': 0.000099},  # f1
        'CurrentMax-Mon': {
            'type': 'float', 'prec': PS_CURRENT_PRECISION, 'value': 0.0,
            'unit': 'A'},  # 91
        'CurrentMin-Mon': {
            'type': 'float', 'prec': PS_CURRENT_PRECISION, 'value': 0.0,
            'unit': 'A'},  # 92
        'CurrentFit-Mon': {
            'type': 'float', 'prec': PS_CURRENT_PRECISION,
            'value': 0.0},  # f0
        # --- interlocks
        'StatusIntlk-Mon': {
            'type': 'int', 'value': 0, 'hihi': 55, 'unit': 'interlock'},
        'IntlkWarn-Mon': {
            'type': 'int', 'value': 0, 'unit': 'interlock'},  # 23
        'IntlkSignalIn-Mon': {
            'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkSignalOut-Mon': {
            'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkRdSignalIn-Mon': {
            'type': 'int', 'value': 0, 'unit': 'interlock'},  # 70
        'IntlkRdSignalInMask-Mon': {
            'type': 'int', 'value': 0, 'unit': 'interlock'},  # 71
        'IntlkRdSignalOut-Mon': {
            'type': 'int', 'value': 0, 'unit': 'interlock'},  # 72
        'IntlkRdSignalOutMask-Mon': {
            'type': 'int', 'value': 0, 'unit': 'interlock'},  # 73
        # --- interlock labels
        'IntlkWarnLabels-Cte':  {
            'type': 'string',
            'count': len(_et.LINAC_INTLCK_WARN),
            'value': _et.LINAC_INTLCK_WARN,
            'unit': 'interlock'},
        'IntlkSignalInLabels-Cte':  {
            'type': 'string',
            'count': len(_et.LINAC_INTLCK_WARN),
            'value': _et.LINAC_INTLCK_WARN,
            'unit': 'interlock'},
        'IntlkRdSignalInMaskLabels-Cte':  {
            'type': 'string',
            'count': len(_et.LINAC_INTLCK_RDSGIN_MASK),
            'value': _et.LINAC_INTLCK_RDSGIN_MASK,
            'unit': 'interlock'},
        'IntlkSignalOutLabels-Cte':  {
            'type': 'string',
            'count': len(_et.LINAC_INTLCK_SGOUT),
            'value': _et.LINAC_INTLCK_SGOUT,
            'unit': 'interlock'},
        'IntlkRdSignalOutMaskLabels-Cte':  {
            'type': 'string',
            'count': len(_et.LINAC_INTLCK_RDSGOUT_MASK),
            'value': _et.LINAC_INTLCK_RDSGOUT_MASK,
            'unit': 'interlock'},
        # --- misc
        'Temperature-Mon': {
            'type': 'float', 'prec': 4, 'value': 0.0, 'unit': 'C'},  # 74
        'LoadVoltage-Mon': {
            'type': 'float', 'prec': 4, 'value': 0.0, 'unit': 'V'},  # f2
        'BusVoltage-Mon': {
            'type': 'float', 'prec': 4, 'value': 0.0, 'unit': 'V'}  # f3
    }
    propty_db = _csdev.add_pvslist_cte(propty_db)
    return propty_db


def _get_ps_FOFB_propty_database():  # noqa: N802
    """This is not a primary source database.

    Primary sources can be found in Fast Orbit Feedback EPICS Support:
    https://github.com/lnls-dig/fofb-epics-ioc/.
    """
    dbase = {
        # PwsState
        'PwrState-Sel': {
            'type': 'enum', 'enums': _et.OFF_ON,
            'value': Const.OffOn.Off, 'unit': 'pwrstate'},
        'PwrState-Sts': {
            'type': 'enum', 'enums': _et.OFF_ON,
            'value': Const.OffOn.Off, 'unit': 'pwrstate'},
        # OpMode
        'OpMode-Sel': {
            'type': 'enum', 'enums': _et.FOFB_OPMODES_SEL,
            'value': Const.OpModeFOFBSel.manual,
            'unit': 'opmodefofb'},
        'OpMode-Sts': {
            'type': 'enum', 'enums': _et.FOFB_OPMODES_STS,
            'value': Const.OpModeFOFBSts.manual,
            'unit': 'opmodefofb'},
        # Test mode configurations
        'TestLimA-SP': {
            'type': 'int', 'value': 0,
            'lolo': -32768, 'low': -32768, 'lolim': -32768,
            'hilim': 32767, 'high': 32767, 'hihi': 32767},
        'TestLimA-RB': {
            'type': 'int', 'value': 0,
            'lolo': -32768, 'low': -32768, 'lolim': -32768,
            'hilim': 32767, 'high': 32767, 'hihi': 32767},
        'TestLimB-SP': {
            'type': 'int', 'value': 0,
            'lolo': -32768, 'low': -32768, 'lolim': -32768,
            'hilim': 32767, 'high': 32767, 'hihi': 32767},
        'TestLimB-RB': {
            'type': 'int', 'value': 0,
            'lolo': -32768, 'low': -32768, 'lolim': -32768,
            'hilim': 32767, 'high': 32767, 'hihi': 32767},
        'TestWavePeriod-SP': {
            'type': 'int', 'value': 0,
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 4194303, 'high': 4194303, 'hihi': 4194303},
        'TestWavePeriod-RB': {
            'type': 'int', 'value': 0,
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 4194303, 'high': 4194303, 'hihi': 4194303},
        # Status and Alarms
        'AlarmsAmp-Mon': {'type': 'int', 'value': 0},
        'AlarmsAmpLabels-Cte': {
            'type': 'string', 'count': len(_et.FOFB_ALARMS_AMP),
            'value': _et.FOFB_ALARMS_AMP},
        'AlarmsAmpLtc-Mon': {'type': 'int', 'value': 0},
        'AlarmsAmpLtcLabels-Cte': {
            'type': 'string', 'count': len(_et.FOFB_ALARMS_AMP),
            'value': _et.FOFB_ALARMS_AMP},
        'AlarmsAmpLtcRst-Cmd': {'type': 'int', 'value': 0},
        # PI control
        'CurrLoopKp-SP': {'type': 'int', 'value': 0},
        'CurrLoopKp-RB': {'type': 'int', 'value': 0},
        'CurrLoopKi-SP': {'type': 'int', 'value': 0},
        'CurrLoopKi-RB': {'type': 'int', 'value': 0},
        'CurrLoopMode-Sel': {
            'type': 'enum', 'enums': _et.FOFB_CURRLOOPMODES,
            'value': Const.CurrLoopModeFOFB.open_loop_manual,
            'unit': 'currloopmode'},
        'CurrLoopMode-Sts': {
            'type': 'enum', 'enums': _et.FOFB_CURRLOOPMODES,
            'value': Const.CurrLoopModeFOFB.open_loop_manual,
            'unit': 'currloopmode'},
        # Calibration params
        'CurrGain-SP': {'type': 'float', 'prec': 12, 'value': 0.0},
        'CurrGain-RB': {'type': 'float', 'prec': 12, 'value': 0.0},
        'CurrOffset-SP': {'type': 'int', 'value': 0},
        'CurrOffset-RB': {'type': 'int', 'value': 0},
        'VoltGain-SP': {'type': 'float', 'prec': 12, 'value': 0.0},
        'VoltGain-RB': {'type': 'float', 'prec': 12, 'value': 0.0},
        'VoltOffset-SP': {'type': 'int', 'value': 0},
        'VoltOffset-RB': {'type': 'int', 'value': 0},
        # Current
        'CurrentRaw-SP': {
            'type': 'int', 'value': 0.0, 'unit': 'count'},
        'CurrentRaw-RB': {
            'type': 'int', 'value': 0.0, 'unit': 'count'},
        'CurrentRawRef-Mon': {
            'type': 'int', 'value': 0.0, 'unit': 'count'},
        'CurrentRaw-Mon': {
            'type': 'int', 'value': 0.0, 'unit': 'count'},
        'Current-SP': {
            'type': 'float', 'prec': 12, 'value': 0.0, 'unit': 'A',
            'lolo': -0.95, 'low': -0.95, 'lolim': -0.95,
            'hilim': 0.95, 'high': 0.95, 'hihi': 0.95},
        'Current-RB': {
            'type': 'float', 'prec': 12, 'value': 0.0, 'unit': 'A',
            'lolo': -0.95, 'low': -0.95, 'lolim': -0.95,
            'hilim': 0.95, 'high': 0.95, 'hihi': 0.95},
        'CurrentRef-Mon': {
            'type': 'float', 'prec': 12, 'value': 0.0, 'unit': 'A',
            'lolo': -0.95, 'low': -0.95, 'lolim': -0.95,
            'hilim': 0.95, 'high': 0.95, 'hihi': 0.95},
        'Current-Mon': {
            'type': 'float', 'prec': 12, 'value': 0.0, 'unit': 'A',
            'lolo': -0.95, 'low': -0.95, 'lolim': -0.95,
            'hilim': 0.95, 'high': 0.95, 'hihi': 0.95},
        # Voltage
        'VoltageRaw-SP': {
            'type': 'int', 'value': 0.0, 'unit': 'count',
            'lolo': -32768, 'low': -32768, 'lolim': -32768,
            'hilim': 32767, 'high': 32767, 'hihi': 32767},
        'VoltageRaw-RB': {
            'type': 'int', 'value': 0.0, 'unit': 'count',
            'lolo': -32768, 'low': -32768, 'lolim': -32768,
            'hilim': 32767, 'high': 32767, 'hihi': 32767},
        'VoltageRaw-Mon': {
            'type': 'int', 'value': 0.0, 'unit': 'count'},
        'Voltage-SP': {
            'type': 'float', 'prec': 12, 'value': 0.0, 'unit': 'V'},
        'Voltage-RB': {
            'type': 'float', 'prec': 12, 'value': 0.0, 'unit': 'V'},
        'Voltage-Mon': {
            'type': 'float', 'prec': 12, 'value': 0.0, 'unit': 'V'},
    }
    dbase = _csdev.add_pvslist_cte(dbase)
    return dbase


# --- FBP ---


def _get_ps_FBP_propty_database():  # noqa: N802
    """Return database with FBP pwrsupply model PVs."""
    propty_db = _get_ps_basic_propty_database()
    dbase = {
        'IntlkSoftLabels-Cte':  {
            'type': 'string',
            'count': len(_et.SOFT_INTLCK_FBP),
            'value': _et.SOFT_INTLCK_FBP,
            'unit': 'interlock'},
        'IntlkHardLabels-Cte':  {
            'type': 'string',
            'count': len(_et.HARD_INTLCK_FBP),
            'value': _et.HARD_INTLCK_FBP,
            'unit': 'interlock'},
        'Alarms-Mon': {'type': 'int', 'value': 0},
        'AlarmsLabels-Cte': {
            'type': 'string',
            'count': len(_et.ALARMS_FBP),
            'value': _et.ALARMS_FBP},
        'LoadVoltage-Mon': {
            'type': 'float', 'value': 0.0,
            'prec': PS_CURRENT_PRECISION,
            'unit': 'V'},
        'DCLinkVoltage-Mon': {
            'type': 'float', 'value': 0.0,
            'prec': PS_CURRENT_PRECISION,
            'unit': 'V'},
        'SwitchesTemperature-Mon': {
            'type': 'float', 'value': 0.0,
            'prec': 2,
            'unit': 'C'},
        'PWMDutyCycle-Mon': {
            'type': 'float', 'value': 0.0, 'unit': 'p.u.',
            'prec': PS_CURRENT_PRECISION},
        }
    propty_db.update(dbase)

    dbase = _get_ps_idff_propty_database()
    propty_db.update(dbase)

    return propty_db


def _get_ps_FBP_DCLink_propty_database():  # noqa: N802
    """Return database with FBP_DCLink pwrsupply model PVs."""
    propty_db = _get_ps_common_propty_database()
    # FBP DCLinks have different units for Voltage-* PVs
    db_ps = {
        'Voltage-SP': {
            'type': 'float', 'value': 0.0,
            'lolim': 0.0, 'hilim': 100.0, 'prec': 4, 'unit': '%'},
        'Voltage-RB': {
            'type': 'float', 'value': 0.0,
            'lolim': 0.0, 'hilim': 100.0, 'prec': 4, 'unit': '%'},
        'VoltageRef-Mon': {
            'type': 'float', 'value': 0.0,
            'lolim': 0.0, 'hilim': 100.0, 'prec': 4, 'unit': '%'},
        'Voltage-Mon': {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'V'},
        'Voltage1-Mon': {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'V'},
        'Voltage2-Mon': {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'V'},
        'Voltage3-Mon': {
            'type': 'float', 'value': 0.0, 'prec': 4, 'unit': 'V'},
        'VoltageDig-Mon': {
            'type': 'int', 'value': 0,
            'lolim': 0, 'hilim': 255, 'unit': '%'},
        'IntlkSoftLabels-Cte':  {
            'type': 'string',
            'count': len(_et.SOFT_INTLCK_FBP_DCLINK),
            'value': _et.SOFT_INTLCK_FBP_DCLINK,
            'unit': 'interlock'},
        'IntlkHardLabels-Cte':  {
            'type': 'string',
            'count': len(_et.HARD_INTLCK_FBP_DCLINK),
            'value': _et.HARD_INTLCK_FBP_DCLINK,
            'unit': 'interlock'},
        'ModulesStatus-Mon': {
            'type': 'int', 'value': 0, 'unit': 'count'},
    }
    propty_db.update(db_ps)
    return propty_db


# --- FAC DCDC ---


def _get_ps_FAC_DCDC_propty_database():  # noqa: N802
    """Return database with FAC_DCDC pwrsupply model PVs."""
    propty_db = _get_ps_basic_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {
            'type': 'string',
            'count': len(_et.SOFT_INTLCK_FAC_DCDC),
            'value': _et.SOFT_INTLCK_FAC_DCDC,
            'unit': 'interlock'},
        'IntlkHardLabels-Cte':  {
            'type': 'string',
            'count': len(_et.HARD_INTLCK_FAC_DCDC),
            'value': _et.HARD_INTLCK_FAC_DCDC,
            'unit': 'interlock'},
        'Alarms-Mon': {'type': 'int', 'value': 0},
        'AlarmsLabels-Cte': {
            'type': 'string',
            'count': len(_et.ALARMS_FAC_DCDC),
            'value': _et.ALARMS_FAC_DCDC},
        'Current1-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'CapacitorBankVoltage-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'lolim': 0.0, 'hilim': 1.0,
                                     'unit': 'V'},
        'PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0,
                             'prec': PS_CURRENT_PRECISION,
                             'unit': 'p.u.'},
        'LeakCurrent-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'VoltageInputIIB-Mon': {'type': 'float', 'value': 0.0,
                                'prec': PS_CURRENT_PRECISION,
                                'unit': 'V'},
        'CurrentInputIIB-Mon': {'type': 'float', 'value': 0.0,
                                'prec': PS_CURRENT_PRECISION,
                                'unit': 'A'},
        'CurrentOutputIIB-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT1TemperatureIIB-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIB-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': 2, 'unit': 'C'},
        'InductorsTemperatureIIB-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIB-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIB-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBT1DriverCurrentIIB-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'A'},
        'IGBT2DriverCurrentIIB-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'A'},
        'BoardTemperatureIIB-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIB-Mon': {'type': 'float', 'value': 0.0,
                                    'unit': '%'},
        'IntlkIIB-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBLabels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAC_DCDC),
            'value': _et.IIB_INTLCK_FAC_DCDC,
            'unit': 'interlock'},
        'AlarmsIIB-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBLabels-Cte': {'type': 'string',
                                'count': len(_et.IIB_ALARMS_FAC_DCDC),
                                'value': _et.IIB_ALARMS_FAC_DCDC},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_2S_DCDC_propty_database():  # noqa: N802
    """Return database with FAC_2S_DCDC pwrsupply model PVs."""
    propty_db = _get_ps_basic_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {
            'type': 'string',
            'count': len(_et.SOFT_INTLCK_FAC_2S_DCDC),
            'value': _et.SOFT_INTLCK_FAC_2S_DCDC,
            'unit': 'interlock'},
        'IntlkHardLabels-Cte':  {
            'type': 'string',
            'count': len(_et.HARD_INTLCK_FAC_2S_DCDC),
            'value': _et.HARD_INTLCK_FAC_2S_DCDC,
            'unit': 'interlock'},
        'Alarms-Mon': {'type': 'int', 'value': 0},
        'AlarmsLabels-Cte': {
            'type': 'string',
            'count': len(_et.ALARMS_FAC_2S_DCDC),
            'value': _et.ALARMS_FAC_2S_DCDC},
        'Current1-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'CapacitorBankVoltageMod1-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'CapacitorBankVoltageMod2-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'PWMDutyCycleMod1-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                 'prec': PS_CURRENT_PRECISION},
        'PWMDutyCycleMod2-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                 'prec': PS_CURRENT_PRECISION},
        'VoltageInputIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'CurrentInputIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'CurrentOutputIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'A'},
        'IGBT1TemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'InductorsTemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                            'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'BoardTemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                        'unit': '%'},
        'IntlkIIBMod1-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBMod1Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAC_2S_DCDC),
            'value': _et.IIB_INTLCK_FAC_2S_DCDC,
            'unit': 'interlock'},
        'AlarmsIIBMod1-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBMod1Labels-Cte': {'type': 'string',
                                    'count': len(_et.IIB_ALARMS_FAC_2S_DCDC),
                                    'value': _et.IIB_ALARMS_FAC_2S_DCDC},
        'VoltageInputIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'CurrentInputIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'CurrentOutputIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'A'},
        'IGBT1TemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'InductorsTemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                            'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'BoardTemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                        'unit': '%'},
        'IntlkIIBMod2-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBMod2Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAC_2S_DCDC),
            'value': _et.IIB_INTLCK_FAC_2S_DCDC,
            'unit': 'interlock'},
        'AlarmsIIBMod2-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBMod2Labels-Cte': {'type': 'string',
                                    'count': len(_et.IIB_ALARMS_FAC_2S_DCDC),
                                    'value': _et.IIB_ALARMS_FAC_2S_DCDC},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_2P4S_DCDC_propty_database():  # noqa: N802
    """Return database with FAC_2P4S_DCDC pwrsupply model PVs."""
    propty_db = _get_ps_basic_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {
            'type': 'string',
            'count': len(_et.SOFT_INTLCK_FAC_2P4S_DCDC),
            'value': _et.SOFT_INTLCK_FAC_2P4S_DCDC,
            'unit': 'interlock'},
        'IntlkHardLabels-Cte':  {
            'type': 'string',
            'count': len(_et.HARD_INTLCK_FAC_2P4S_DCDC),
            'value': _et.HARD_INTLCK_FAC_2P4S_DCDC,
            'unit': 'interlock'},
        'Alarms-Mon': {'type': 'int', 'value': 0},
        'AlarmsLabels-Cte': {
            'type': 'string',
            'count': len(_et.ALARMS_FAC_2P4S_DCDC),
            'value': _et.ALARMS_FAC_2P4S_DCDC},
        'Current1-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Arm1Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'Arm2Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'CapacitorBankVoltageMod1-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'CapacitorBankVoltageMod2-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'CapacitorBankVoltageMod3-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'CapacitorBankVoltageMod4-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'CapacitorBankVoltageMod5-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'CapacitorBankVoltageMod6-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'CapacitorBankVoltageMod7-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'CapacitorBankVoltageMod8-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'PWMDutyCycleMod1-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                 'prec': PS_CURRENT_PRECISION},
        'PWMDutyCycleMod2-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                 'prec': PS_CURRENT_PRECISION},
        'PWMDutyCycleMod3-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                 'prec': PS_CURRENT_PRECISION},
        'PWMDutyCycleMod4-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                 'prec': PS_CURRENT_PRECISION},
        'PWMDutyCycleMod5-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                 'prec': PS_CURRENT_PRECISION},
        'PWMDutyCycleMod6-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                 'prec': PS_CURRENT_PRECISION},
        'PWMDutyCycleMod7-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                 'prec': PS_CURRENT_PRECISION},
        'PWMDutyCycleMod8-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                                 'prec': PS_CURRENT_PRECISION},
        'VoltageInputIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'CurrentInputIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'CurrentOutputIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'A'},
        'IGBT1TemperatureIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'InductorTemperatureIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'BoardTemperatureIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBModA-Mon': {'type': 'float', 'value': 0.0,
                                        'unit': '%'},
        'IntlkIIBModA-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBModALabels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAC_2P4S_DCDC),
            'value': _et.IIB_INTLCK_FAC_2P4S_DCDC,
            'unit': 'interlock'},
        'AlarmsIIBModA-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBModALabels-Cte': {
            'type': 'string', 'count': len(_et.IIB_ALARMS_FAC_2P4S_DCDC),
            'value': _et.IIB_ALARMS_FAC_2P4S_DCDC},
        'VoltageInputIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'CurrentInputIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'CurrentOutputIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'A'},
        'IGBT1TemperatureIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'InductorTemperatureIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'BoardTemperatureIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBModB-Mon': {'type': 'float', 'value': 0.0,
                                        'unit': '%'},
        'IntlkIIBModB-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBModBLabels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAC_2P4S_DCDC),
            'value': _et.IIB_INTLCK_FAC_2P4S_DCDC,
            'unit': 'interlock'},
        'AlarmsIIBModB-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBModBLabels-Cte': {
            'type': 'string', 'count': len(_et.IIB_ALARMS_FAC_2P4S_DCDC),
            'value': _et.IIB_ALARMS_FAC_2P4S_DCDC},
        }
    propty_db.update(db_ps)
    return propty_db


# --- FAC ACDC ---


def _get_ps_FAC_2S_ACDC_propty_database():  # noqa: N802
    """Return database with FAC_2S_ACDC pwrsupply model PVs."""
    propty_db = _get_ps_common_propty_database()
    db_ps = {
        'CapacitorBankVoltage-SP': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'lolim': 0.0, 'hilim': 1.0,
                                    'unit': 'V'},
        'CapacitorBankVoltage-RB': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'CapacitorBankVoltageRef-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': PS_CURRENT_PRECISION,
                                        'unit': 'V'},
        'CapacitorBankVoltage-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IntlkSoftLabels-Cte':  {
            'type': 'string',
            'count': len(_et.SOFT_INTLCK_FAC_2S_ACDC),
            'value': _et.SOFT_INTLCK_FAC_2S_ACDC,
            'unit': 'interlock'},
        'IntlkHardLabels-Cte':  {
            'type': 'string',
            'count': len(_et.HARD_INTLCK_FAC_2S_ACDC),
            'value': _et.HARD_INTLCK_FAC_2S_ACDC,
            'unit': 'interlock'},
        'RectifierCurrent-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                             'prec': PS_CURRENT_PRECISION},
        'CurrentInputIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'A'},
        'VoltageInputIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBTTemperatureIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'V'},
        'IGBTDriverCurrentIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'InductorTemperatureIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                            'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                            'prec': 2, 'unit': 'C'},
        'BoardTemperatureIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                         'unit': '%'},
        'IntlkIIBModIS-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBModISLabels-Cte':  {
            'type': 'string', 'count': len(_et.IIBIS_INTLCK_FAC_2S_ACDC),
            'value': _et.IIBIS_INTLCK_FAC_2S_ACDC,
            'unit': 'interlock'},
        'AlarmsIIBModIS-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBModISLabels-Cte': {
            'type': 'string', 'count': len(_et.IIBIS_ALARMS_FAC_2S_ACDC),
            'value': _et.IIBIS_ALARMS_FAC_2S_ACDC},
        'VoltageOutputIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': PS_CURRENT_PRECISION,
                                       'unit': 'V'},
        'CapacitorBankVoltageIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                              'prec': PS_CURRENT_PRECISION,
                                              'unit': 'V'},
        'RectInductorTempIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': 2, 'unit': 'C'},
        'RectHeatSinkTempIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': 2, 'unit': 'C'},
        'ExtBoardsVoltageIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'V'},
        'AuxBoardCurrentIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'A'},
        'IDBBoardCurrentIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'A'},
        'LeakCurrentIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'A'},
        'BoardTemperatureIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                          'unit': '%'},
        'IntlkIIBModCmd-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBModCmdLabels-Cte':  {
            'type': 'string', 'count': len(_et.IIBCMD_INTLCK_FAC_2S_ACDC),
            'value': _et.IIBCMD_INTLCK_FAC_2S_ACDC,
            'unit': 'interlock'},
        'AlarmsIIBModCmd-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBModCmdLabels-Cte': {
            'type': 'string', 'count': len(_et.IIBCMD_ALARMS_FAC_2S_ACDC),
            'value': _et.IIBCMD_ALARMS_FAC_2S_ACDC},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAC_2P4S_ACDC_propty_database():  # noqa: N802
    """Return database with FAC_2P4S_ACDC pwrsupply model PVs."""
    propty_db = _get_ps_common_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {
            'type': 'string',
            'count': len(_et.SOFT_INTLCK_FAC_2P4S_ACDC),
            'value': _et.SOFT_INTLCK_FAC_2P4S_ACDC,
            'unit': 'interlock'},
        'IntlkHardLabels-Cte':  {
            'type': 'string',
            'count': len(_et.HARD_INTLCK_FAC_2P4S_ACDC),
            'value': _et.HARD_INTLCK_FAC_2P4S_ACDC,
            'unit': 'interlock'},
        'CapacitorBankVoltage-SP': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'lolim': 0.0, 'hilim': 1.0,
                                    'unit': 'V'},
        'CapacitorBankVoltage-RB': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'CapacitorBankVoltageRef-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': PS_CURRENT_PRECISION,
                                        'unit': 'V'},
        'CapacitorBankVoltage-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'RectifierCurrent-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'V'},
        'PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                             'prec': PS_CURRENT_PRECISION},
        'CurrentInputIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'A'},
        'VoltageInputIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBTTemperatureIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'V'},
        'IGBTDriverCurrentIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'InductorTemperatureIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                            'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                            'prec': 2, 'unit': 'C'},
        'BoardTemperatureIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBModIS-Mon': {'type': 'float', 'value': 0.0,
                                         'unit': '%'},
        'IntlkIIBModIS-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBModISLabels-Cte':  {
            'type': 'string', 'count': len(_et.IIBIS_INTLCK_FAC_2P4S_ACDC),
            'value': _et.IIBIS_INTLCK_FAC_2P4S_ACDC,
            'unit': 'interlock'},
        'AlarmsIIBModIS-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBModISLabels-Cte': {
            'type': 'string', 'count': len(_et.IIBIS_ALARMS_FAC_2P4S_ACDC),
            'value': _et.IIBIS_ALARMS_FAC_2P4S_ACDC},
        'VoltageOutputIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': PS_CURRENT_PRECISION,
                                       'unit': 'V'},
        'CapacitorBankVoltageIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                              'prec': PS_CURRENT_PRECISION,
                                              'unit': 'V'},
        'InductorTemperatureIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                             'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                             'prec': 2, 'unit': 'C'},
        'ExtBoardsVoltageIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'V'},
        'AuxBoardCurrentIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'A'},
        'IDBBoardCurrentIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'A'},
        'LeakCurrentIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'A'},
        'BoardTemperatureIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBModCmd-Mon': {'type': 'float', 'value': 0.0,
                                          'unit': '%'},
        'IntlkIIBModCmd-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBModCmdLabels-Cte':  {
            'type': 'string', 'count': len(_et.IIBCMD_INTLCK_FAC_2P4S_ACDC),
            'value': _et.IIBCMD_INTLCK_FAC_2P4S_ACDC,
            'unit': 'interlock'},
        'AlarmsIIBModCmd-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBModCmdLabels-Cte': {
            'type': 'string', 'count': len(_et.IIBCMD_ALARMS_FAC_2P4S_ACDC),
            'value': _et.IIBCMD_ALARMS_FAC_2P4S_ACDC},
    }
    propty_db.update(db_ps)
    return propty_db


# --- FAP ---


def _get_ps_FAP_propty_database():  # noqa: N802
    """Return database with FAP pwrsupply model PVs."""
    propty_db = _get_ps_basic_propty_database()
    db_ps = {
        'Current1-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'IntlkSoftLabels-Cte': {
            'type': 'string',
            'count': len(_et.SOFT_INTLCK_FAP),
            'value': _et.SOFT_INTLCK_FAP,
            'unit': 'interlock'},
        'IntlkHardLabels-Cte': {
            'type': 'string',
            'count': len(_et.HARD_INTLCK_FAP),
            'value': _et.HARD_INTLCK_FAP,
            'unit': 'interlock'},
        'Alarms-Mon': {'type': 'int', 'value': 0},
        'AlarmsLabels-Cte': {
            'type': 'string',
            'count': len(_et.ALARMS_FAP),
            'value': _et.ALARMS_FAP},
        'DCLinkVoltage-Mon': {'type': 'float', 'value': 0.0,
                              'prec': PS_CURRENT_PRECISION,
                              'unit': 'V'},
        'IGBT1Current-Mon': {'type': 'float', 'value': 0.0,
                             'prec': PS_CURRENT_PRECISION,
                             'unit': 'A'},
        'IGBT2Current-Mon': {'type': 'float', 'value': 0.0,
                             'prec': PS_CURRENT_PRECISION,
                             'unit': 'A'},
        'IGBT1PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0,
                                  'prec': PS_CURRENT_PRECISION,
                                  'unit': 'p.u.'},
        'IGBT2PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0,
                                  'prec': PS_CURRENT_PRECISION,
                                  'unit': 'p.u.'},
        'PWMDutyDiff-Mon': {'type': 'float', 'value': 0.0, 'unit': 'p.u.',
                            'prec': PS_CURRENT_PRECISION},
        'VoltageInputIIB-Mon': {'type': 'float', 'value': 0.0,
                                'prec': PS_CURRENT_PRECISION,
                                'unit': 'V'},
        'VoltageOutputIIB-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'V'},
        'IGBT1CurrentIIB-Mon': {'type': 'float', 'value': 0.0,
                                'prec': PS_CURRENT_PRECISION,
                                'unit': 'A'},
        'IGBT2CurrentIIB-Mon': {'type': 'float', 'value': 0.0,
                                'prec': PS_CURRENT_PRECISION,
                                'unit': 'A'},
        'IGBT1TemperatureIIB-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIB-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIB-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBT1DriverCurrentIIB-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'A'},
        'IGBT2DriverCurrentIIB-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'A'},
        'InductorTemperatureIIB-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2,
                                       'unit': 'C'},
        'HeatSinkTemperatureIIB-Mon': {'type': 'float', 'value': 0.0,
                                       'prec': 2,
                                       'unit': 'C'},
        'LeakCurrentIIB-Mon': {'type': 'float', 'value': 0.0,
                               'prec': PS_CURRENT_PRECISION,
                               'unit': 'A'},
        'BoardTemperatureIIB-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIB-Mon': {'type': 'float', 'value': 0.0,
                                    'unit': '%'},
        'IntlkIIB-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBLabels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAP),
            'value': _et.IIB_INTLCK_FAP,
            'unit': 'interlock'},
        'AlarmsIIB-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBLabels-Cte': {'type': 'string',
                                'count': len(_et.IIB_ALARMS_FAP),
                                'value': _et.IIB_ALARMS_FAP},
    }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAP_4P_propty_database():  # noqa: N802
    """Return database with FAP_4P pwrsupply model PVs."""
    propty_db = _get_ps_basic_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {
            'type': 'string',
            'count': len(_et.SOFT_INTLCK_FAP_4P),
            'value': _et.SOFT_INTLCK_FAP_4P,
            'unit': 'interlock'},
        'IntlkHardLabels-Cte':  {
            'type': 'string',
            'count': len(_et.HARD_INTLCK_FAP_4P),
            'value': _et.HARD_INTLCK_FAP_4P,
            'unit': 'interlock'},
        'Alarms-Mon': {'type': 'int', 'value': 0},
        'AlarmsLabels-Cte': {
            'type': 'string',
            'count': len(_et.ALARMS_FAP_4P),
            'value': _et.ALARMS_FAP_4P},
        'Current1-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'LoadVoltage-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'V'},
        'IGBT1CurrentMod1-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT2CurrentMod1-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT1CurrentMod2-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT2CurrentMod2-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT1CurrentMod3-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT2CurrentMod3-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT1CurrentMod4-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT2CurrentMod4-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'DCLinkVoltageMod1-Mon': {'type': 'float', 'value': 0.0,
                                  'prec': PS_CURRENT_PRECISION,
                                  'unit': 'V'},
        'DCLinkVoltageMod2-Mon': {'type': 'float', 'value': 0.0,
                                  'prec': PS_CURRENT_PRECISION,
                                  'unit': 'V'},
        'DCLinkVoltageMod3-Mon': {'type': 'float', 'value': 0.0,
                                  'prec': PS_CURRENT_PRECISION,
                                  'unit': 'V'},
        'DCLinkVoltageMod4-Mon': {'type': 'float', 'value': 0.0,
                                  'prec': PS_CURRENT_PRECISION,
                                  'unit': 'V'},
        'PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0,
                             'prec': PS_CURRENT_PRECISION,
                             'unit': 'p.u.'},
        'IGBT1PWMDutyCycleMod1-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT2PWMDutyCycleMod1-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT1PWMDutyCycleMod2-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT2PWMDutyCycleMod2-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT1PWMDutyCycleMod3-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT2PWMDutyCycleMod3-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT1PWMDutyCycleMod4-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT2PWMDutyCycleMod4-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'LeakCurrent-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'VoltageInputIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'VoltageOutputIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBT1CurrentIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT2CurrentIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT1TemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'InductorTemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'TemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                   'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBMod1-Mon': {
            'type': 'float', 'value': 0.0,
            'prec': 2,
            'unit': '%'},
        'IntlkIIBMod1-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBMod1Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAP_4P_MOD1),
            'value': _et.IIB_INTLCK_FAP_4P_MOD1,
            'unit': 'interlock'},
        'AlarmsIIBMod1-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBMod1Labels-Cte': {'type': 'string',
                                    'count': len(_et.IIB_ALARMS_FAP_4P_MOD1),
                                    'value': _et.IIB_ALARMS_FAP_4P_MOD1},
        'VoltageInputIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'VoltageOutputIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBT1CurrentIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT2CurrentIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT1TemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'InductorTemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'TemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                   'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBMod2-Mon': {
            'type': 'float', 'value': 0.0,
            'prec': 2,
            'unit': '%'},
        'IntlkIIBMod2-Mon': {
            'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBMod2Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAP_4P_MOD234),
            'value': _et.IIB_INTLCK_FAP_4P_MOD234,
            'unit': 'interlock'},
        'AlarmsIIBMod2-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBMod2Labels-Cte': {'type': 'string',
                                    'count': len(_et.IIB_ALARMS_FAP_4P_MOD234),
                                    'value': _et.IIB_ALARMS_FAP_4P_MOD234},
        'VoltageInputIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'VoltageOutputIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBT1CurrentIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT2CurrentIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT1TemperatureIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'InductorTemperatureIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'TemperatureIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                   'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBMod3-Mon': {
            'type': 'float', 'value': 0.0,
            'prec': 2,
            'unit': '%'},
        'IntlkIIBMod3-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBMod3Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAP_4P_MOD234),
            'value': _et.IIB_INTLCK_FAP_4P_MOD234,
            'unit': 'interlock'},
        'AlarmsIIBMod3-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBMod3Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_ALARMS_FAP_4P_MOD234),
            'value': _et.IIB_ALARMS_FAP_4P_MOD234},
        'VoltageInputIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'VoltageOutputIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBT1CurrentIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT2CurrentIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT1TemperatureIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'InductorTemperatureIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'TemperatureIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                   'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBMod4-Mon': {
            'type': 'float', 'value': 0.0,
            'prec': 2,
            'unit': '%'},
        'IntlkIIBMod4-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBMod4Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAP_4P_MOD234),
            'value': _et.IIB_INTLCK_FAP_4P_MOD234,
            'unit': 'interlock'},
        'AlarmsIIBMod4-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBMod4Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_ALARMS_FAP_4P_MOD234),
            'value': _et.IIB_ALARMS_FAP_4P_MOD234},
        }
    propty_db.update(db_ps)
    return propty_db


def _get_ps_FAP_2P2S_propty_database():  # noqa: N802
    """Return database with FAP_2P2S pwrsupply model PVs."""
    propty_db = _get_ps_basic_propty_database()
    db_ps = {
        'IntlkSoftLabels-Cte':  {
            'type': 'string',
            'count': len(_et.SOFT_INTLCK_FAP_2P2S),
            'value': _et.SOFT_INTLCK_FAP_2P2S,
            'unit': 'interlock'},
        'IntlkHardLabels-Cte':  {
            'type': 'string',
            'count': len(_et.HARD_INTLCK_FAP_2P2S),
            'value': _et.HARD_INTLCK_FAP_2P2S,
            'unit': 'interlock'},
        'Alarms-Mon': {'type': 'int', 'value': 0},
        'AlarmsLabels-Cte': {
            'type': 'string',
            'count': len(_et.ALARMS_FAP_2P2S),
            'value': _et.ALARMS_FAP_2P2S},
        'Current1-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Current2-Mon': {'type': 'float', 'value': 0.0,
                         'prec': PS_CURRENT_PRECISION,
                         'unit': 'A'},
        'Arm1Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'Arm2Current-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'IGBT1CurrentMod1-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT2CurrentMod1-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT1CurrentMod2-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT2CurrentMod2-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT1CurrentMod3-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT2CurrentMod3-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT1CurrentMod4-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'IGBT2CurrentMod4-Mon': {'type': 'float', 'value': 0.0,
                                 'prec': PS_CURRENT_PRECISION,
                                 'unit': 'A'},
        'CurrentMod1-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'CurrentMod2-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'CurrentMod3-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'CurrentMod4-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'DCLinkVoltageMod1-Mon': {'type': 'float', 'value': 0.0,
                                  'prec': PS_CURRENT_PRECISION,
                                  'unit': 'V'},
        'DCLinkVoltageMod2-Mon': {'type': 'float', 'value': 0.0,
                                  'prec': PS_CURRENT_PRECISION,
                                  'unit': 'V'},
        'DCLinkVoltageMod3-Mon': {'type': 'float', 'value': 0.0,
                                  'prec': PS_CURRENT_PRECISION,
                                  'unit': 'V'},
        'DCLinkVoltageMod4-Mon': {'type': 'float', 'value': 0.0,
                                  'prec': PS_CURRENT_PRECISION,
                                  'unit': 'V'},
        'PWMDutyCycle-Mon': {'type': 'float', 'value': 0.0,
                             'prec': PS_CURRENT_PRECISION,
                             'unit': 'p.u.'},
        'PWMDutyCycleArmsDiff-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'p.u.'},
        'IGBT1PWMDutyCycleMod1-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT2PWMDutyCycleMod1-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT1PWMDutyCycleMod2-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT2PWMDutyCycleMod2-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT1PWMDutyCycleMod3-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT2PWMDutyCycleMod3-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT1PWMDutyCycleMod4-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'IGBT2PWMDutyCycleMod4-Mon': {'type': 'float', 'value': 0.0,
                                      'prec': PS_CURRENT_PRECISION,
                                      'unit': 'p.u.'},
        'LeakCurrent-Mon': {'type': 'float', 'value': 0.0,
                            'prec': PS_CURRENT_PRECISION,
                            'unit': 'A'},
        'VoltageInputIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'VoltageOutputIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBT1CurrentIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT2CurrentIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT1TemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'InductorTemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'TemperatureIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                   'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBMod1-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': '%'},
        'IntlkIIBMod1-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBMod1Labels-Cte':  {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAP_2P2S_MOD1),
            'value': _et.IIB_INTLCK_FAP_2P2S_MOD1,
            'unit': 'interlock'},
        'AlarmsIIBMod1-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBMod1Labels-Cte': {'type': 'string',
                                    'count': len(_et.IIB_ALARMS_FAP_2P2S_MOD1),
                                    'value': _et.IIB_ALARMS_FAP_2P2S_MOD1},
        'VoltageInputIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'VoltageOutputIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBT1CurrentIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT2CurrentIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT1TemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IGBT2TemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IGBTDriverVoltageIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'InductorTemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'TemperatureIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                   'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBMod2-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': '%'},
        'IntlkIIBMod2-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBMod2Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAP_2P2S_MOD234),
            'value': _et.IIB_INTLCK_FAP_2P2S_MOD234,
            'unit': 'interlock'},
        'AlarmsIIBMod2-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBMod2Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_ALARMS_FAP_2P2S_MOD234),
            'value': _et.IIB_ALARMS_FAP_2P2S_MOD234},
        'VoltageInputIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'VoltageOutputIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBT1CurrentIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT2CurrentIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT1TemperatureIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBT2TemperatureIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': 'C'},
        'IGBTDriverVoltageIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'InductorTemperatureIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'TemperatureIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                   'prec': 2, 'unit': 'C'},
        'RelativeHumidityIIBMod3-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': '%'},
        'IntlkIIBMod3-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBMod3Labels-Cte':  {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAP_2P2S_MOD234),
            'value': _et.IIB_INTLCK_FAP_2P2S_MOD234,
            'unit': 'interlock'},
        'AlarmsIIBMod3-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBMod3Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_ALARMS_FAP_2P2S_MOD234),
            'value': _et.IIB_ALARMS_FAP_2P2S_MOD234},
        'VoltageInputIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'V'},
        'VoltageOutputIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                     'prec': PS_CURRENT_PRECISION,
                                     'unit': 'V'},
        'IGBT1CurrentIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT2CurrentIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                    'prec': PS_CURRENT_PRECISION,
                                    'unit': 'A'},
        'IGBT1TemperatureIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IGBT2TemperatureIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2,
                                        'unit': 'C'},
        'IGBTDriverVoltageIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                         'prec': PS_CURRENT_PRECISION,
                                         'unit': 'V'},
        'IGBT1DriverCurrentIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'IGBT2DriverCurrentIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                          'prec': PS_CURRENT_PRECISION,
                                          'unit': 'A'},
        'InductorTemperatureIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'HeatSinkTemperatureIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                           'prec': 2, 'unit': 'C'},
        'TemperatureIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                   'prec': 2,
                                   'unit': 'C'},
        'RelativeHumidityIIBMod4-Mon': {'type': 'float', 'value': 0.0,
                                        'prec': 2, 'unit': '%'},
        'IntlkIIBMod4-Mon': {'type': 'int', 'value': 0, 'unit': 'interlock'},
        'IntlkIIBMod4Labels-Cte':  {
            'type': 'string',
            'count': len(_et.IIB_INTLCK_FAP_2P2S_MOD234),
            'value': _et.IIB_INTLCK_FAP_2P2S_MOD234,
            'unit': 'interlock'},
        'AlarmsIIBMod4-Mon': {'type': 'int', 'value': 0},
        'AlarmsIIBMod4Labels-Cte': {
            'type': 'string',
            'count': len(_et.IIB_ALARMS_FAP_2P2S_MOD234),
            'value': _et.IIB_ALARMS_FAP_2P2S_MOD234},
    }
    propty_db.update(db_ps)
    return propty_db


# --- Others ---


def _get_ps_REGATRON_DCLink_database():  # noqa: N802
    """Return database with REGATRON DCLink model PVs."""
    # TODO: implement!!!
    return dict()


# --- Aux. ---


def _set_limits(pstype, database):
    signals_unit = (
        'Current-SP', 'Current-RB',
        'CurrentRef-Mon', 'Current-Mon', 'Current2-Mon'
        'CycleAmpl-SP', 'CycleAmpl-RB',
        'CycleOffset-SP', 'CycleOffset-RB',
        'WfmOffset-SP', 'WfmOffset-RB',
    )
    signals_lims = signals_unit + (
        'Voltage-SP', 'Voltage-RB',
        'VoltageRef-Mon', 'Voltage-Mon',
        )
    signals_prec = signals_lims

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
            dbase['unit'] = PS_CURRENT_UNIT
        # define prec of current
        if propty in signals_prec:
            dbase['prec'] = PS_CURRENT_PRECISION


def _get_model_db(psmodel):
    psmodel_2_dbfunc = {
        'FBP': _get_ps_FBP_propty_database,
        'FBP_DCLink': _get_ps_FBP_DCLink_propty_database,
        'FAC_DCDC': _get_ps_FAC_DCDC_propty_database,
        'FAC_2S_DCDC': _get_ps_FAC_2S_DCDC_propty_database,
        'FAC_2S_ACDC': _get_ps_FAC_2S_ACDC_propty_database,
        'FAC_2P4S_DCDC': _get_ps_FAC_2P4S_DCDC_propty_database,
        'FAC_2P4S_ACDC': _get_ps_FAC_2P4S_ACDC_propty_database,
        'FAP': _get_ps_FAP_propty_database,
        'FAP_2P2S': _get_ps_FAP_2P2S_propty_database,
        'FAP_4P': _get_ps_FAP_4P_propty_database,
        'FP_SEPT': _get_pu_FP_SEPT_propty_database,
        'FP_KCKR': _get_pu_FP_KCKR_propty_database,
        'FP_KCKRCCOIL': _get_pu_FP_KCKRCCOIL_propty_database,
        'FP_PINGER': _get_pu_FP_PINGER_propty_database,
        'LINAC_PS': _get_ps_LINAC_propty_database,
        'FOFB_PS': _get_ps_FOFB_propty_database,
        'APU': _get_id_apu_propty_database,
        'REGATRON_DCLink': _get_ps_REGATRON_DCLink_database,
    }
    if psmodel in psmodel_2_dbfunc:
        func = psmodel_2_dbfunc[psmodel]
        return func()
    else:
        raise ValueError(
            'DB for psmodel "{}" not implemented!'.format(psmodel))


def _insert_strengths_pulsed(database, pstype, prec):
    pulsed_pstypes = (
        'tb-injseptum',
        'bo-injkicker', 'bo-ejekicker',
        'ts-ejeseptum-thin', 'ts-ejeseptum-thick',
        'ts-injseptum-thin', 'ts-injseptum-thick',
        'si-injdpk', 'si-injnlk', 'si-injnlk-ccoilh', 'si-injnlk-ccoilv',
        'si-hping', 'si-vping')
    if pstype in pulsed_pstypes:
        database['Kick-SP'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': 'mrad'}
        database['Kick-RB'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': 'mrad'}
        database['Kick-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': 'mrad'}
        return True
    return False


def _insert_strengths_spectrometer(database, pstype, prec):
    if pstype.startswith('li-spect'):
        database['Kick-SP'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': 'deg'}
        database['Kick-RB'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': 'deg'}
        database['Kick-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': 'deg'}
        return True
    return False


def _insert_strengths_id_k(database, pstype, prec):
    if pstype.startswith('si-id-apu'):
        database['Kx-SP'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': 'ID_K'}
        database['Kx-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': 'ID_K'}
        return True
    return False


def _insert_strengths_magtype(database, magfunc, magtypes, prec, mtype, unit):
    if magfunc in magtypes:
        database[mtype + '-SP'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': unit}
        database[mtype + '-RB'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': unit}
        database[mtype + 'Ref-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': unit}
        database[mtype + '-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': unit}
        database['WfmOffset' + mtype + '-SP'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': unit}
        database['WfmOffset' + mtype + '-RB'] = {
            'type': 'float', 'value': 0.0, 'prec': prec, 'unit': unit}
        return True
    return False


def _insert_strengths(database, pstype):
    prec_kick = 3
    prec_kl = 5
    prec_sl = 5
    prec_energy = 5
    prec_id_k = 4

    # pulsed
    if _insert_strengths_pulsed(database, pstype, prec_kick):
        return database
    # linac spectrometer
    if _insert_strengths_spectrometer(database, pstype, prec_kick):
        return database
    # insertion devices
    if _insert_strengths_id_k(database, pstype, prec_id_k):
        return database

    corrs = {'corrector-horizontal', 'corrector-vertical'}
    mcs = (
        ({'quadrupole', 'quadrupole-skew'}, prec_kl, 'KL', '1/m'),
        ({'sextupole', }, prec_sl, 'SL', '1/m^2'),
        ({'dipole', }, prec_energy, 'Energy', 'GeV'),
        (corrs, prec_kick, 'Kick', 'urad'),
    )
    magfunc = _PSSearch.conv_pstype_2_magfunc(pstype)
    _ = _insert_strengths_magtype(database, magfunc, *(mcs[0])) \
        or _insert_strengths_magtype(database, magfunc, *(mcs[1])) \
        or _insert_strengths_magtype(database, magfunc, *(mcs[2])) \
        or _insert_strengths_magtype(database, magfunc, *(mcs[3]))

    if pstype.startswith('li-'):
        if 'KickRef-Mon' in database:
            del database['KickRef-Mon']
        if 'KLRef-Mon' in database:
            del database['KLRef-Mon']
        if 'SLRef-Mon' in database:
            del database['SLRef-Mon']
    elif '-fc' in pstype and 'ffc' not in pstype:
        database['KickAcc-Mon'] = {
            'type': 'float', 'value': 0.0, 'prec': prec_kick, 'unit': 'urad'}

    return database
