"""Define the PV database of a single BPM and its enum types."""
from copy import deepcopy as _dcopy
import numpy as _np
from siriuspy.csdevice.const import get_namedtuple as _get_namedtuple

OpModes = _get_namedtuple('OpModes', ('MultiBunch', 'SinglePass'))
Polarity = _get_namedtuple('Polarity', ('Positive', 'Negative'))
EnblTyp = _get_namedtuple('EnblTyp', ('Disable', 'Enable'))
ConnTyp = _get_namedtuple('ConnTyp', ('Disconnect', 'Connect'))
AcqRepeat = _get_namedtuple('AcqRepeat', ('Normal', 'Repetitive'))
AcqEvents = _get_namedtuple('AcqEvents', ('Start', 'Stop', 'Abort'))
AcqDataTyp = _get_namedtuple(
                    'AcqDataTyp', ('A', 'B', 'C', 'D', 'X', 'Y', 'Sum', 'Q'))
AcqChan = _get_namedtuple(
            'AcqChan',
            ('ADC', 'ADCSwp', 'TbT', 'FOFB', 'TbTPha', 'FOFBPha', 'Monit1'))
AcqStates = _get_namedtuple(
            'AcqStates',
            ('Idle', 'Waiting', 'ExternalTrig', 'DataTrig', 'SoftwareTrig',
             'Acquiring', 'Error', 'Aborted', 'TooManySamples',
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
        'ACQBPMMode-Sel': {
            'type': 'enum', 'enums': OpModes._fields, 'value': 0},
        'ACQBPMMode-Sts': {
            'type': 'enum', 'enums': OpModes._fields, 'value': 0},

        'asyn.ENBL': {
            'type': 'enum', 'enums': EnblTyp._fields, 'value': 0},
        'asyn.CNCT': {
            'type': 'enum', 'enums': ConnTyp._fields, 'value': 0},
        'INFOFOFBRate-SP': {
            'type': 'int', 'value': 1910, 'low': 0, 'high': 2**32-1},
        'INFOFOFBRate-RB': {
            'type': 'int', 'value': 1910, 'low': 0, 'high': 2**32-1},
        'INFOHarmonicNumber-SP': {
            'type': 'int', 'value': 864, 'low': 0, 'high': 2**32-1},
        'INFOHarmonicNumber-RB': {
            'type': 'int', 'value': 864, 'low': 0, 'high': 2**32-1},
        'INFOMONITRate-SP': {
            'type': 'int', 'value': 21965000, 'low': 0, 'high': 2**32-1},
        'INFOMONITRate-RB': {
            'type': 'int', 'value': 21965000, 'low': 0, 'high': 2**32-1},
        'INFOTBTRate-SP': {
            'type': 'int', 'value': 382, 'low': 0, 'high': 2**32-1},
        'INFOTBTRate-RB': {
            'type': 'int', 'value': 382, 'low': 0, 'high': 2**32-1},

        'PosQOffset-SP': _dcopy(data_db), 'PosQOffset-RB': _dcopy(data_db),
        'PosXOffset-SP': _dcopy(data_db), 'PosXOffset-RB': _dcopy(data_db),
        'PosYOffset-SP': _dcopy(data_db), 'PosYOffset-RB': _dcopy(data_db),
        'PosKq-SP': _dcopy(data_db), 'PosKq-RB': _dcopy(data_db),
        'PosKsum-SP': _dcopy(data_db), 'PosKsum-RB': _dcopy(data_db),
        'PosKx-SP': _dcopy(data_db), 'PosKx-RB': _dcopy(data_db),
        'PosKy-SP': _dcopy(data_db), 'PosKy-RB': _dcopy(data_db),
        'PosX-Mon': _dcopy(data_db), 'PosY-Mon': _dcopy(data_db),
        'Sum-Mon': _dcopy(data_db), 'PosQ-Mon': _dcopy(data_db),
        'AmplA-Mon': _dcopy(data_db), 'AmplB-Mon': _dcopy(data_db),
        'AmplC-Mon': _dcopy(data_db), 'AmplD-Mon': _dcopy(data_db),

        'SPPosX-Mon': _dcopy(data_db), 'SPPosY-Mon': _dcopy(data_db),
        'SPSum-Mon': _dcopy(data_db), 'SPPosQ-Mon': _dcopy(data_db),
        'SPAmplA-Mon': _dcopy(data_db), 'SPAmplB-Mon': _dcopy(data_db),
        'SPAmplC-Mon': _dcopy(data_db), 'SPAmplD-Mon': _dcopy(data_db),
        }

    data_names = {
        'GEN': ['A', 'B', 'C', 'D', 'Q', 'Sum', 'X', 'Y'],
        'PM': ['A', 'B', 'C', 'D', 'Q', 'Sum', 'X', 'Y'],
        'SP': ['A', 'B', 'C', 'D'],
        }
    data_db = {
        'type': 'float', 'value': _np.array(100000*[0.0]), 'count': 100000}

    for acq_tp in ['GEN', 'SP', 'PM']:
        for prop in data_names[acq_tp]:
            nm = acq_tp + '_' + prop
            db[nm + 'ArrayData-Mon'] = _dcopy(data_db)
            db.update(get_statistic_database(nm))
            db.update(get_fft_database(nm))

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


def get_config_database(prefix=''):
    """Get the configuration PVs database."""
    db = {
        'Channel-Sel': {
            'type': 'enum', 'enums': AcqChan._fields, 'value': 0},
        'Channel-Sts': {
            'type': 'enum', 'enums': AcqChan._fields, 'value': 0},
        'NrShots-SP': {
            'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
        'NrShots-RB': {
            'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
        'TriggerHwDly-SP': {
            'type': 'float', 'value': 0.0, 'low': 0.0, 'high': 1e9},
        'TriggerHwDly-RB': {
            'type': 'float', 'value': 0.0, 'low': 0.0, 'high': 1e9},
        'UpdateTime-SP': {
            'type': 'float', 'value': 1.0, 'low': 0.0, 'high': 1e9},
        'UpdateTime-RB': {
            'type': 'float', 'value': 1.0, 'low': 0.0, 'high': 1e9},
        'NrSamplesPre-SP': {
            'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
        'NrSamplesPre-RB': {
            'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
        'NrSamplesPost-SP': {
            'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
        'NrSamplesPost-RB': {
            'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
        'Ctrl-Sel': {
            'type': 'enum', 'enums': AcqEvents._fields,
            'value': AcqEvents.Stop},
        'Ctrl-Sts': {
            'type': 'enum', 'enums': AcqEvents._fields,
            'value': AcqEvents.Stop},
        'Status-Mon': {
            'type': 'enum', 'enums': AcqStates._fields, 'value': 0},
        'TriggerType-Sel': {
            'type': 'enum', 'enums': AcqTrigTyp._fields, 'value': 1},
        'TriggerType-Sts': {
            'type': 'enum', 'enums': AcqTrigTyp._fields, 'value': 1},
        'TriggerRep-Sel': {
            'type': 'enum', 'enums': AcqRepeat._fields, 'value': 0},
        'TriggerRep-Sts': {
            'type': 'enum', 'enums': AcqRepeat._fields, 'value': 0},
        'TriggerDataChan-Sel': {
            'type': 'enum', 'enums': AcqChan._fields, 'value': 0},
        'TriggerDataChan-Sts': {
            'type': 'enum', 'enums': AcqChan._fields, 'value': 0},
        'TriggerDataSel-Sel': {
            'type': 'enum', 'enums': AcqDataTyp._fields, 'value': 0},
        'TriggerDataSel-Sts': {
            'type': 'enum', 'enums': AcqDataTyp._fields, 'value': 0},
        'TriggerDataThres-SP': {
            'type': 'int', 'value': 1, 'low': 0, 'high': 2**16 - 1},
        'TriggerDataThres-RB': {
            'type': 'int', 'value': 1, 'low': 0, 'high': 2**16 - 1},
        'TriggerDataPol-Sel': {
            'type': 'enum', 'enums': Polarity._fields, 'value': 0},
        'TriggerDataPol-Sts': {
            'type': 'enum', 'enums': Polarity._fields, 'value': 0},
        'TriggerDataHyst-SP': {
            'type': 'int', 'value': 0, 'low': 0, 'high': 2**16 - 1},
        'TriggerDataHyst-RB': {
            'type': 'int', 'value': 0, 'low': 0, 'high': 2**16 - 1},
        }
    return {prefix + k: v for k, v in db.items()}


def get_fft_database(prefix=''):
    """Get the PV database of the FFT plugin."""
    data_db = {
        'type': 'float', 'value': _np.array(100000*[0.0]), 'count': 100000}
    acq_int_db = {'type': 'int', 'value': 1, 'low': 0, 'high': 100000}
    db = dict()
    db[prefix + 'FFTFreq-Mon'] = _dcopy(data_db)
    db[prefix + 'FFTData.SPAN'] = _dcopy(acq_int_db)
    db[prefix + 'FFTData.AMP'] = _dcopy(data_db)
    db[prefix + 'FFTData.PHA'] = _dcopy(data_db)
    db[prefix + 'FFTData.SIN'] = _dcopy(data_db)
    db[prefix + 'FFTData.COS'] = _dcopy(data_db)
    db[prefix + 'FFTData.WAVN'] = _dcopy(data_db)
    db[prefix + 'FFTData.INDX'] = _dcopy(acq_int_db)
    db[prefix + 'FFTData.MXIX'] = _dcopy(acq_int_db)
    db[prefix + 'FFTData.WIND'] = {
            'type': 'enum', 'enums': FFTWindowTyp._fields, 'value': 0}
    db[prefix + 'FFTData.CDIR'] = {
            'type': 'enum', 'enums': FFTConvDirection._fields, 'value': 0}
    db[prefix + 'FFTData.ASUB'] = {
            'type': 'enum', 'enums': FFTAvgSubtract._fields, 'value': 0}

    return db


def get_statistic_database(prefix=''):
    """Get the PV database of the STAT plugin."""
    acq_data_stat_db = {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
    db = dict()
    db[prefix + '_STATSMaxValue_RBV'] = _dcopy(acq_data_stat_db)
    db[prefix + '_STATSMeanValue_RBV'] = _dcopy(acq_data_stat_db)
    db[prefix + '_STATSMinValue_RBV'] = _dcopy(acq_data_stat_db)
    db[prefix + '_STATSSigma_RBV'] = _dcopy(acq_data_stat_db)
    return db
