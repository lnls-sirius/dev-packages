from copy import deepcopy as _copy
import numpy as _np

op_modes = ['MultiBunch', 'SinglePass']
data_names = {
    'GEN': ['A', 'B', 'C', 'D', 'Q', 'Sum', 'X', 'Y'],
    'PM': ['A', 'B', 'C', 'D', 'Q', 'Sum', 'X', 'Y'],
    'SP': ['A', 'B', 'C', 'D'],
}

polarity = ['positive', 'negative']
acq_repeat = ['normal', 'repetitive']
acq_events = ['start', 'stop', 'abort', 'reset']

acq_types = ['adc', 'adcswp', 'tbt', 'sofb', 'tbtpha', 'fofbpha']
acq_states = ['Idle', 'Waiting', 'Acquiring', 'Error', 'Aborted']
acq_trig_types = ['now', 'external', 'data', 'software']
acq_trig_exter = ['Trig1', 'Trig2', 'Trig3', 'Trig4', 'Trig5']

pvs_definitions = {
    'asyn.ENBL': {
        'type': 'enum', 'enums': ['Disable', 'Enable'], 'value': 0},
    'asyn.CNCT': {
        'type': 'enum', 'enums': ['Disconnect', 'Connect'], 'value': 0},
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
    'ACQBPMMode-Sel': {
        'type': 'enum', 'enums': op_modes, 'value': 0},
    'ACQBPMMode-Sts': {
        'type': 'enum', 'enums': op_modes, 'value': 0},
    'PosQOffset-SP': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosQOffset-RB': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosXOffset-SP': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosXOffset-RB': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosYOffset-SP': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosYOffset-RB': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosKq-SP': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosKq-RB': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosKsum-SP': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosKsum-RB': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosKx-SP': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosKx-RB': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosKy-SP': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosKy-RB': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosX-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosY-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'Sum-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'PosQ-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'AmplA-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'AmplB-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'AmplC-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'AmplD-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'ACQChannel-Sel': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'ACQChannel-Sts': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'ACQShots-SP': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
    'ACQShots-RB': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
    'ACQTriggerHwDly-SP': {
        'type': 'float', 'value': 0.0, 'low': 0.0, 'high': 1e9},
    'ACQTriggerHwDly-RB': {
        'type': 'float', 'value': 0.0, 'low': 0.0, 'high': 1e9},
    'ACQUpdateTime-SP': {
        'type': 'float', 'value': 1.0, 'low': 0.0, 'high': 1e9},
    'ACQUpdateTime-RB': {
        'type': 'float', 'value': 1.0, 'low': 0.0, 'high': 1e9},
    'ACQSamplesPre-SP': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'ACQSamplesPre-RB': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'ACQSamplesPost-SP': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'ACQSamplesPost-RB': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'ACQTriggerEvent-Sel': {
        'type': 'enum', 'enums': acq_events, 'value': 0},
    'ACQTriggerEvent-Sts': {
        'type': 'enum', 'enums': acq_events, 'value': 0},
    'ACQStatus-Sts': {
        'type': 'enum', 'enums': acq_states, 'value': 0},
    'ACQTrigger-Sel': {
        'type': 'enum', 'enums': acq_trig_types, 'value': 1},
    'ACQTrigger-Sts': {
        'type': 'enum', 'enums': acq_trig_types, 'value': 1},
    'ACQTriggerRep-Sel': {
        'type': 'enum', 'enums': acq_repeat, 'value': 0},
    'ACQTriggerRep-Sts': {
        'type': 'enum', 'enums': acq_repeat, 'value': 0},
    'ACQExtTrigChan-Sel': {
        'type': 'enum', 'enums': acq_trig_exter, 'value': 0},
    'ACQExtTrigChan-Sts': {
        'type': 'enum', 'enums': acq_trig_exter, 'value': 0},
    'ACQDataTrigChan-Sel': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'ACQDataTrigChan-Sts': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'ACQTriggerDataSel-SP': {
        'type': 'int', 'value': 0, 'low': 0, 'high': 7},
    'ACQTriggerDataSel-RB': {
        'type': 'int', 'value': 0, 'low': 0, 'high': 7},
    'ACQTriggerDataThres-SP': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 2**16 - 1},
    'ACQTriggerDataThres-RB': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 2**16 - 1},
    'ACQTriggerDataPol-Sel': {
        'type': 'enum', 'enums': polarity, 'value': 0},
    'ACQTriggerDataPol-Sts': {
        'type': 'enum', 'enums': polarity, 'value': 0},
    'ACQTriggerDataHyst-SP': {
        'type': 'int', 'value': 0, 'low': 0, 'high': 2**16 - 1},
    'ACQTriggerDataHyst-RB': {
        'type': 'int', 'value': 0, 'low': 0, 'high': 2**16 - 1},

    'ACQ_PMChannel-Sel': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'ACQ_PMChannel-Sts': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'ACQ_PMShots-SP': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
    'ACQ_PMShots-RB': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
    'ACQ_PMTriggerHwDly-SP': {
        'type': 'float', 'value': 0.0, 'low': 0.0, 'high': 1e9},
    'ACQ_PMTriggerHwDly-RB': {
        'type': 'float', 'value': 0.0, 'low': 0.0, 'high': 1e9},
    'ACQ_PMUpdateTime-SP': {
        'type': 'float', 'value': 1.0, 'low': 0.0, 'high': 1e9},
    'ACQ_PMUpdateTime-RB': {
        'type': 'float', 'value': 1.0, 'low': 0.0, 'high': 1e9},
    'ACQ_PMSamplesPre-SP': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'ACQ_PMSamplesPre-RB': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'ACQ_PMSamplesPost-SP': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'ACQ_PMSamplesPost-RB': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'ACQ_PMTriggerEvent-Sel': {
        'type': 'enum', 'enums': acq_events, 'value': 0},
    'ACQ_PMTriggerEvent-Sts': {
        'type': 'enum', 'enums': acq_events, 'value': 0},
    'ACQ_PMStatus-Sts': {
        'type': 'enum', 'enums': acq_states, 'value': 0},
    'ACQ_PMTrigger-Sel': {
        'type': 'enum', 'enums': acq_trig_types, 'value': 1},
    'ACQ_PMTrigger-Sts': {
        'type': 'enum', 'enums': acq_trig_types, 'value': 1},
    'ACQ_PMTriggerRep-Sel': {
        'type': 'enum', 'enums': acq_repeat, 'value': 0},
    'ACQ_PMTriggerRep-Sts': {
        'type': 'enum', 'enums': acq_repeat, 'value': 0},
    'ACQ_PMExtTrigChan-Sel': {
        'type': 'enum', 'enums': acq_trig_exter, 'value': 0},
    'ACQ_PMExtTrigChan-Sts': {
        'type': 'enum', 'enums': acq_trig_exter, 'value': 0},
    'ACQ_PMDataTrigChan-Sel': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'ACQ_PMDataTrigChan-Sts': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'ACQ_PMTriggerDataSel-SP': {
        'type': 'int', 'value': 0, 'low': 0, 'high': 7},
    'ACQ_PMTriggerDataSel-RB': {
        'type': 'int', 'value': 0, 'low': 0, 'high': 7},
    'ACQ_PMTriggerDataThres-SP': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 2**16 - 1},
    'ACQ_PMTriggerDataThres-RB': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 2**16 - 1},
    'ACQ_PMTriggerDataPol-Sel': {
        'type': 'enum', 'enums': polarity, 'value': 0},
    'ACQ_PMTriggerDataPol-Sts': {
        'type': 'enum', 'enums': polarity, 'value': 0},
    'ACQ_PMTriggerDataHyst-SP': {
        'type': 'int', 'value': 0, 'low': 0, 'high': 2**16 - 1},
    'ACQ_PMTriggerDataHyst-RB': {
        'type': 'int', 'value': 0, 'low': 0, 'high': 2**16 - 1},

    'SPPosX-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'SPPosY-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'SPSum-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'SPPosQ-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'SPAmplA-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'SPAmplB-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'SPAmplC-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    'SPAmplD-Mon': {
        'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12},
    }

fft_window_types = ["Square", "Hanning", "Parzen", "Welch", "QuadW"]
fft_conv_direction = ['Forward', 'Backward']
fft_average_subtraction = ["No Subtraction", "Average", "Linear"]

fft_writable_props = ['INDX', 'MXIX', 'WIND', 'CDIR', 'ASUB', 'SPAN']

acq_data_prop_db = {
    'type': 'float', 'value': _np.array(100000*[0.0]), 'count': 100000}
acq_data_stat_db = {'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
acq_int_db = {'type': 'int', 'value': 1, 'low': 0, 'high': 100000}
for acq_tp in ['GEN', 'SP', 'PM']:
    for prop in data_names[acq_tp]:
        nm = acq_tp + '_' + prop
        pvs_loc = dict()
        pvs_loc[nm+'ArrayData-Mon'] = _copy(acq_data_prop_db)
        pvs_loc[nm + '_STATSMaxValue_RBV'] = _copy(acq_data_stat_db)
        pvs_loc[nm + '_STATSMeanValue_RBV'] = _copy(acq_data_stat_db)
        pvs_loc[nm + '_STATSMinValue_RBV'] = _copy(acq_data_stat_db)
        pvs_loc[nm + '_STATSSigma_RBV'] = _copy(acq_data_stat_db)
        pvs_loc[nm + 'FFTFreq-Mon'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.SPAN'] = {
                'type': 'int', 'value': 0, 'low': 0, 'high': 100000}
        pvs_loc[nm + 'FFTData.AMP'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.PHA'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.SIN'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.COS'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.INDX'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.MXIX'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.WIND'] = {
                'type': 'enum', 'enums': fft_window_types, 'value': 0}
        pvs_loc[nm + 'FFTData.CDIR'] = {
                'type': 'enum', 'enums': fft_conv_direction, 'value': 0}
        pvs_loc[nm + 'FFTData.ASUB'] = {
                'type': 'enum', 'enums': fft_average_subtraction, 'value': 0}
        pvs_definitions.update(pvs_loc)
