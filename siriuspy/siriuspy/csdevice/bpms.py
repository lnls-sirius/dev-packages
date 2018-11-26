"""Define the PV database of a single BPM and its enum types."""
from copy import deepcopy as _dcopy
import numpy as _np
from siriuspy.csdevice.util import ETypes as _et
from siriuspy.util import get_namedtuple as _get_namedtuple


# TODO: refactor this code as to make it closer in structure to all other
# modules in csdevice subpackage


TrigDir = _get_namedtuple('TrigDir', ('trn', 'rcv'))
TrigDirPol = _get_namedtuple('TrigDirPol', ('same', 'rev'))
TrigSrc = _get_namedtuple('TrigSrc', ('ext', 'int'))
TrigExtern = _get_namedtuple(
    'TrigExtern', (
        'UserDefined', 'BeamLossIn', 'BeamLossOut', 'OrbitInterlock',
        'StorageRingTbTClk', 'BoosterTbTClk', 'FOFBClk', 'Reserved'))
TrigIntern = _get_namedtuple('TrigIntern', ('FMCTrigIn', 'DSPSWClk'))
LogTrigIntern = _get_namedtuple(
    'LogTrigIntern', (
        'ADC', 'ADCSwap', 'MixerIQ', 'Unconnected', 'TbTIQ',
        'Unconnected2', 'TbTAmp', 'TbTPha', 'TbTPos', 'FOFBIQ',
        'Unconnected3', 'FOFBAmp', 'FOFBPha', 'FOFBPos', 'MonitAmp',
        'MonitPos', 'Monit1Pos', 'FMCTrigOut', 'Unconnected4', 'Unconnected5',
        'Unconnected6', 'Unconnected7', 'Unconnected8', 'Unconnected9'))
SwModes = _get_namedtuple('SwModes', (
    'rffe_switching', 'direct', 'inverted', 'switching'))
SwTagEnbl = _get_namedtuple('SwTagEnbl', ('disabled', 'enabled'))
SwDataMaskEnbl = _get_namedtuple('SwDataMaskEnbl', ('disabled', 'enabled'))
MonitEnbl = _get_namedtuple('MonitEnbl', ('No', 'Yes'))

OpModes = _get_namedtuple('OpModes', ('MultiBunch', 'SinglePass'))
Polarity = _get_namedtuple('Polarity', ('Positive', 'Negative'))
EnblTyp = _get_namedtuple('EnblTyp', ('Disable', 'Enable'))
ConnTyp = _get_namedtuple('ConnTyp', _et.DISCONN_CONN)
AcqRepeat = _get_namedtuple('AcqRepeat', ('Normal', 'Repetitive'))
AcqEvents = _get_namedtuple('AcqEvents', ('Start', 'Stop', 'Abort'))
AcqDataTyp = _get_namedtuple('AcqDataTyp', ('A', 'B', 'C', 'D'))
AcqChan = _get_namedtuple(
            'AcqChan',
            ('ADC', 'ADCSwp', 'TbT', 'FOFB', 'TbTPha', 'FOFBPha', 'Monit1'))
AcqStates = _get_namedtuple(
            'AcqStates',
            ('Idle', 'Waiting', 'External Trig', 'Data Trig', 'Software Trig',
             'Acquiring', 'Error', 'Aborted', 'Too Many Samples',
             'Too Few Samples', 'No Memory'))
AcqTrigTyp = _get_namedtuple(
                        'AcqTrigTyp', ('Now', 'External', 'Data', 'Software'))
FFTWindowTyp = _get_namedtuple(
            'FFTWindowTyp', ('Square', 'Hanning', 'Parzen', 'Welch', 'QuadW'))
FFTConvDirection = _get_namedtuple('FFTConvDirection', ('Forward', 'Backward'))
FFTAvgSubtract = _get_namedtuple(
                    'FFTAvgSubtract', ('No Subtraction', 'Average', 'Linear'))

FFTWritableProps = ['INDX', 'MXIX', 'WIND', 'CDIR', 'ASUB', 'SPAN']


def get_bpm_database(prefix=''):
    """Get the PV database of a single BPM."""
    data_db = {'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
    db = {
        'INFOFOFBRate-SP': {
            'type': 'int', 'value': 1910, 'low': 0, 'high': 2**31-1},
        'INFOFOFBRate-RB': {
            'type': 'int', 'value': 1910, 'low': 0, 'high': 2**31-1},
        'INFOHarmonicNumber-SP': {
            'type': 'int', 'value': 864, 'low': 0, 'high': 2**31-1},
        'INFOHarmonicNumber-RB': {
            'type': 'int', 'value': 864, 'low': 0, 'high': 2**31-1},
        'INFOMONITRate-SP': {
            'type': 'int', 'value': 21965000, 'low': 0, 'high': 2**31-1},
        'INFOMONITRate-RB': {
            'type': 'int', 'value': 21965000, 'low': 0, 'high': 2**31-1},
        'INFOTBTRate-SP': {
            'type': 'int', 'value': 382, 'low': 0, 'high': 2**31-1},
        'INFOTBTRate-RB': {
            'type': 'int', 'value': 382, 'low': 0, 'high': 2**31-1},
        }

    # PHYSICAL TRIGGERS
    for i in range(8):
        trig = 'TRIGGER{0:d}'.format(i)
        db.update(get_physical_trigger_database(trig))

    # LOGICAL TRIGGERS
    for trig_tp in ('', '_PM'):
        for i in range(24):
            trig = 'TRIGGER' + trig_tp + '{0:d}'.format(i)
            db.update(get_logical_trigger_database(trig))

    # AMPLITUDES AND POSITION CHANNELS
    for amp_tp in ('', 'SP'):
        db.update(get_amplitudes_database(amp_tp))

    # SETTINGS AND STATUS
    db.update(get_offsets_database())
    db.update(get_gain_database())
    db.update(get_rffe_database())
    db.update(get_asyn_database())
    db.update(get_switch_database())
    db.update(get_monit_database())

    data_names = {
        'GEN': ['A', 'B', 'C', 'D', 'Q', 'Sum', 'X', 'Y'],
        'PM': ['A', 'B', 'C', 'D', 'Q', 'Sum', 'X', 'Y'],
        'SP': ['A', 'B', 'C', 'D'],
        }
    data_db = {
        'type': 'float', 'value': _np.array(100000*[0.0]), 'count': 100000}

    # ARRAY DATA FROM TRIGGERED ACQUISITIONS
    for acq_tp in ['GEN', 'SP', 'PM']:
        for prop in data_names[acq_tp]:
            nm = acq_tp + '_' + prop
            db[nm + 'ArrayData'] = _dcopy(data_db)
            db.update(get_statistic_database(nm))
            if acq_tp == 'GEN':
                db.update(get_fft_database(nm))

    # TRIGGERED ACQUISITIONS CONFIGURATION
    for acq_md in ['ACQ', 'ACQ_PM']:
        db.update(get_config_database(acq_md))

    for k, v in db.items():
        if 'low' in v:
            v['lolo'] = v['low']
            v['lolim'] = v['low']
        if 'high' in v:
            v['hihi'] = v['high']
            v['hilim'] = v['high']

    return {prefix + k: v for k, v in db.items()}


def get_asyn_database(prefix=''):
    db = {
        'asyn.ENBL': {
            'type': 'enum', 'enums': EnblTyp._fields, 'value': 0},
        'asyn.CNCT': {
            'type': 'enum', 'enums': ConnTyp._fields, 'value': 0},
        }
    return {prefix + k: v for k, v in db.items()}


def get_rffe_database(prefix=''):
    prefix = prefix + 'RFFE'
    db = {
        'Att-SP': {
            'type': 'float', 'value': 0, 'unit': 'dB',
            'low': 0, 'high': 100},
        'Att-RB': {
            'type': 'float', 'value': 0, 'unit': 'dB',
            'low': 0, 'high': 100},
        'PidSpAC-SP': {
            'type': 'float', 'value': 0, 'unit': 'oC',
            'low': 0, 'high': 100},
        'PidSpAC-RB': {
            'type': 'float', 'value': 0, 'unit': 'oC',
            'low': 0, 'high': 100},
        'PidSpBD-SP': {
            'type': 'float', 'value': 0, 'unit': 'oC',
            'low': 0, 'high': 100},
        'PidSpBD-RB': {
            'type': 'float', 'value': 0, 'unit': 'oC',
            'low': 0, 'high': 100},
        'HeaterAC-SP': {
            'type': 'float', 'value': 0, 'unit': 'V',
            'low': 0, 'high': 100},
        'HeaterAC-RB': {
            'type': 'float', 'value': 0, 'unit': 'V',
            'low': 0, 'high': 100},
        'HeaterBD-SP': {
            'type': 'float', 'value': 0, 'unit': 'V',
            'low': 0, 'high': 100},
        'HeaterBD-RB': {
            'type': 'float', 'value': 0, 'unit': 'V',
            'low': 0, 'high': 100},
        'PidACKp-SP': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidACKp-RB': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidBDKp-SP': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidBDKp-RB': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidACTi-SP': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidACTi-RB': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidBDTi-SP': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidBDTi-RB': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidACTd-SP': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidACTd-RB': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidBDTd-SP': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        'PidBDTd-RB': {
            'type': 'float', 'value': 0, 'low': 0, 'high': 100},
        }
    db.update(get_asyn_database())
    return {prefix + k: v for k, v in db.items()}


def get_switch_database(prefix=''):
    db = {
        'SwMode-Sel': {
            'type': 'enum', 'enums': SwModes._fields, 'value': 3},
        'SwMode-Sts': {
            'type': 'enum', 'enums': SwModes._fields, 'value': 3},
        'SwTagEn-Sel': {
            'type': 'enum', 'enums': SwTagEnbl._fields, 'value': 0},
        'SwTagEn-Sts': {
            'type': 'enum', 'enums': SwTagEnbl._fields, 'value': 0},
        'SwDataMaskEn-Sel': {
            'type': 'enum', 'enums': SwDataMaskEnbl._fields, 'value': 0},
        'SwDataMaskEn-Sts': {
            'type': 'enum', 'enums': SwDataMaskEnbl._fields, 'value': 0},
        'SwDly-SP': {
            'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
        'SwDly-RB': {
            'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
        'SwDivClk-SP': {
            'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
        'SwDivClk-RB': {
            'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
        'SwDataMaskSamples-SP': {
            'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
        'SwDataMaskSamples-RB': {
            'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
        }
    return {prefix + k: v for k, v in db.items()}


def get_monit_database(prefix=''):
    db = {
        'MonitEnable-Sel': {
            'type': 'enum', 'enums': MonitEnbl._fields, 'value': 3},
        'MonitEnable-Sts': {
            'type': 'enum', 'enums': MonitEnbl._fields, 'value': 3},
        'MONITUpdtTime-SP': {
            'type': 'float', 'value': 0, 'low': 0.05, 'high': 1.0,
            'unit': 's'},
        'MONITUpdtTime-RB': {
            'type': 'float', 'value': 0, 'low': 0.05, 'high': 1.0,
            'unit': 's'},
        }
    return {prefix + k: v for k, v in db.items()}


def get_offsets_database(prefix=''):
    data_db = {'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
    db = {
        'PosQOffset-SP': _dcopy(data_db), 'PosQOffset-RB': _dcopy(data_db),
        'PosXOffset-SP': _dcopy(data_db), 'PosXOffset-RB': _dcopy(data_db),
        'PosYOffset-SP': _dcopy(data_db), 'PosYOffset-RB': _dcopy(data_db),
        }
    return {prefix + k: v for k, v in db.items()}


def get_gain_database(prefix=''):
    data_db = {'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
    db = {
        'PosKq-SP': _dcopy(data_db), 'PosKq-RB': _dcopy(data_db),
        'PosKsum-SP': _dcopy(data_db), 'PosKsum-RB': _dcopy(data_db),
        'PosKx-SP': _dcopy(data_db), 'PosKx-RB': _dcopy(data_db),
        'PosKy-SP': _dcopy(data_db), 'PosKy-RB': _dcopy(data_db),
        }
    return {prefix + k: v for k, v in db.items()}


def get_amplitudes_database(prefix=''):
    data_db = {'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
    db = {
        'PosX-Mon': _dcopy(data_db), 'PosY-Mon': _dcopy(data_db),
        'Sum-Mon': _dcopy(data_db), 'PosQ-Mon': _dcopy(data_db),
        'AmplA-Mon': _dcopy(data_db), 'AmplB-Mon': _dcopy(data_db),
        'AmplC-Mon': _dcopy(data_db), 'AmplD-Mon': _dcopy(data_db),
        }
    return {prefix + k: v for k, v in db.items()}


def get_physical_trigger_database(prefix=''):
    db = {
        'Dir-Sel': {
            'type': 'enum', 'enums': TrigDir._fields, 'value': 1},
        'Dir-Sts': {
            'type': 'enum', 'enums': TrigDir._fields, 'value': 1},
        'DirPol-Sel': {
            'type': 'enum', 'enums': TrigDirPol._fields, 'value': 1},
        'DirPol-Sts': {
            'type': 'enum', 'enums': TrigDirPol._fields, 'value': 1},
        'RcvCntRst-SP': {
            'type': 'short', 'value': 0},
        'TrnCntRst-SP': {
            'type': 'short', 'value': 0},
        'RcvCnt-Mon': {
            'type': 'int', 'value': 0},
        'TrnCnt-Mon': {
            'type': 'int', 'value': 0},
        'RcvLen-SP': {
            'type': 'short', 'value': 1, 'low': 0, 'high': 2**15-1},
        'RcvLen-RB': {
            'type': 'short', 'value': 1, 'low': 0, 'high': 2**15-1},
        'TrnLen-SP': {
            'type': 'short', 'value': 1, 'low': 0, 'high': 2**15-1},
        'TrnLen-RB': {
            'type': 'short', 'value': 1, 'low': 0, 'high': 2**15-1},
        }
    return {prefix + k: v for k, v in db.items()}


def get_logical_trigger_database(prefix=''):
    db = {
        'RcvSrc-Sel': {
            'type': 'enum', 'enums': TrigSrc._fields, 'value': 0},
        'RcvSrc-Sts': {
            'type': 'enum', 'enums': TrigSrc._fields, 'value': 0},
        'TrnSrc-Sel': {
            'type': 'enum', 'enums': TrigSrc._fields, 'value': 0},
        'TrnSrc-Sts': {
            'type': 'enum', 'enums': TrigSrc._fields, 'value': 0},
        'RcvInSel-SP': {
            'type': 'short', 'value': 1, 'low': 0, 'high': 2**15-1},
        'RcvInSel-RB': {
            'type': 'short', 'value': 1, 'low': 0, 'high': 2**15-1},
        'TrnOutSel-SP': {
            'type': 'short', 'value': 1, 'low': 0, 'high': 2**15-1},
        'TrnOutSel-RB': {
            'type': 'short', 'value': 1, 'low': 0, 'high': 2**15-1},
        }
    return {prefix + k: v for k, v in db.items()}


def get_config_database(prefix=''):
    """Get the configuration PVs database."""
    db = {
        'BPMMode-Sel': {
            'type': 'enum', 'enums': OpModes._fields, 'value': 0},
        'BPMMode-Sts': {
            'type': 'enum', 'enums': OpModes._fields, 'value': 0},
        'Channel-Sel': {
            'type': 'enum', 'enums': AcqChan._fields, 'value': 0},
        'Channel-Sts': {
            'type': 'enum', 'enums': AcqChan._fields, 'value': 0},
        # 'NrShots-SP': {
        'Shots-SP': {
            'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
        # 'NrShots-RB': {
        'Shots-RB': {
            'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
        'TriggerHwDly-SP': {
            'type': 'float', 'value': 0.0, 'low': 0.0, 'high': 1e9},
        'TriggerHwDly-RB': {
            'type': 'float', 'value': 0.0, 'low': 0.0, 'high': 1e9},
        'UpdateTime-SP': {
            'type': 'float', 'value': 1.0, 'low': 0.0, 'high': 1e9},
        'UpdateTime-RB': {
            'type': 'float', 'value': 1.0, 'low': 0.0, 'high': 1e9},
        # 'NrSamplesPre-SP': {
        'SamplesPre-SP': {
            'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
        # 'NrSamplesPre-RB': {
        'SamplesPre-RB': {
            'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
        # 'NrSamplesPost-SP': {
        'SamplesPost-SP': {
            'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
        # 'NrSamplesPost-RB': {
        'SamplesPost-RB': {
            'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
        # 'Ctrl-Sel': {
        'TriggerEvent-Sel': {
            'type': 'enum', 'enums': AcqEvents._fields,
            'value': AcqEvents.Stop},
        # 'Ctrl-Sts': {
        'TriggerEvent-Sts': {
            'type': 'enum', 'enums': AcqEvents._fields,
            'value': AcqEvents.Stop},
        # 'Status-Mon': {
        'Status-Sel': {
            'type': 'enum', 'enums': AcqStates._fields, 'value': 0},
        # 'TriggerType-Sel': {
        'Trigger-Sel': {
            'type': 'enum', 'enums': AcqTrigTyp._fields, 'value': 1},
        # 'TriggerType-Sts': {
        'Trigger-Sts': {
            'type': 'enum', 'enums': AcqTrigTyp._fields, 'value': 1},
        'TriggerRep-Sel': {
            'type': 'enum', 'enums': AcqRepeat._fields, 'value': 0},
        'TriggerRep-Sts': {
            'type': 'enum', 'enums': AcqRepeat._fields, 'value': 0},
        # 'TriggerDataChan-Sel': {
        'DataTrigChan-Sel': {
            'type': 'enum', 'enums': AcqChan._fields, 'value': 0},
        # 'TriggerDataChan-Sts': {
        'DataTrigChan-Sts': {
            'type': 'enum', 'enums': AcqChan._fields, 'value': 0},
        # 'TriggerDataSel-Sel': {
        #     'type': 'enum', 'enums': AcqDataTyp._fields, 'value': 0},
        # 'TriggerDataSel-Sts': {
        #     'type': 'enum', 'enums': AcqDataTyp._fields, 'value': 0},
        'TriggerDataSel-SP': {
            'type': 'short', 'value': 0, 'low': 0, 'high': 4},
        'TriggerDataSel-RB': {
            'type': 'short', 'value': 0, 'low': 0, 'high': 4},
        'TriggerDataThres-SP': {
            'type': 'int', 'value': 1, 'low': 0, 'high': 2**31 - 1},
        'TriggerDataThres-RB': {
            'type': 'int', 'value': 1, 'low': 0, 'high': 2**31 - 1},
        'TriggerDataPol-Sel': {
            'type': 'enum', 'enums': Polarity._fields, 'value': 0},
        'TriggerDataPol-Sts': {
            'type': 'enum', 'enums': Polarity._fields, 'value': 0},
        'TriggerDataHyst-SP': {
            'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
        'TriggerDataHyst-RB': {
            'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
        }
    return {prefix + k: v for k, v in db.items()}


def get_fft_database(prefix=''):
    """Get the PV database of the FFT plugin."""
    data_db = {
        'type': 'float', 'value': _np.array(100000*[0.0]), 'count': 100000}
    acq_int_db = {'type': 'int', 'value': 1, 'low': 0, 'high': 100000}
    db = dict()
    db['FFTFreq-Mon'] = _dcopy(data_db)
    db['FFTData.SPAN'] = _dcopy(acq_int_db)
    db['FFTData.AMP'] = _dcopy(data_db)
    db['FFTData.PHA'] = _dcopy(data_db)
    db['FFTData.SIN'] = _dcopy(data_db)
    db['FFTData.COS'] = _dcopy(data_db)
    db['FFTData.WAVN'] = _dcopy(data_db)
    db['FFTData.INDX'] = _dcopy(acq_int_db)
    db['FFTData.MXIX'] = _dcopy(acq_int_db)
    db['FFTData.WIND'] = {
        'type': 'enum', 'enums': FFTWindowTyp._fields, 'value': 0}
    db['FFTData.CDIR'] = {
        'type': 'enum', 'enums': FFTConvDirection._fields, 'value': 0}
    db['FFTData.ASUB'] = {
        'type': 'enum', 'enums': FFTAvgSubtract._fields, 'value': 0}
    return {prefix + k: v for k, v in db.items()}


def get_statistic_database(prefix=''):
    """Get the PV database of the STAT plugin."""
    acq_data_stat_db = {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
    db = dict()
    db['_STATSMaxValue_RBV'] = _dcopy(acq_data_stat_db)
    db['_STATSMeanValue_RBV'] = _dcopy(acq_data_stat_db)
    db['_STATSMinValue_RBV'] = _dcopy(acq_data_stat_db)
    db['_STATSSigma_RBV'] = _dcopy(acq_data_stat_db)
    return {prefix + k: v for k, v in db.items()}
