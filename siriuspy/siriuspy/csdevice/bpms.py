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

acq_datasel_types = ['A', 'B', 'C', 'D', 'X', 'Y', 'Sum', 'Q']
acq_types = ['adc', 'adcswp', 'tbt', 'sofb', 'tbtpha', 'fofbpha']
acq_states = ['Idle', 'Waiting', 'Acquiring', 'Error', 'Aborted']
acq_trig_types = ['now', 'external', 'data', 'software']
acq_trig_exter = ['Trig1', 'Trig2', 'Trig3', 'Trig4', 'Trig5']

config_pvs = {
    'Channel-Sel': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'Channel-Sts': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'Shots-SP': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
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
    'SamplesPre-SP': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'SamplesPre-RB': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'SamplesPost-SP': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'SamplesPost-RB': {
        'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
    'TriggerEvent-Sel': {
        'type': 'enum', 'enums': acq_events, 'value': 0},
    'TriggerEvent-Sts': {
        'type': 'enum', 'enums': acq_events, 'value': 0},
    'Status-Sts': {
        'type': 'enum', 'enums': acq_states, 'value': 0},
    'Trigger-Sel': {
        'type': 'enum', 'enums': acq_trig_types, 'value': 1},
    'Trigger-Sts': {
        'type': 'enum', 'enums': acq_trig_types, 'value': 1},
    'TriggerRep-Sel': {
        'type': 'enum', 'enums': acq_repeat, 'value': 0},
    'TriggerRep-Sts': {
        'type': 'enum', 'enums': acq_repeat, 'value': 0},
    'TriggerExternalChan-Sel': {
        'type': 'enum', 'enums': acq_trig_exter, 'value': 0},
    'TriggerExternalChan-Sts': {
        'type': 'enum', 'enums': acq_trig_exter, 'value': 0},
    'TriggerDataChan-Sel': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'TriggerDataChan-Sts': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'TriggerDataSel-Sel': {
        'type': 'enum', 'enums': acq_datasel_types, 'value': 0},
    'TriggerDataSel-Sts': {
        'type': 'enum', 'enums': acq_datasel_types, 'value': 0},
    'TriggerDataThres-SP': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 2**16 - 1},
    'TriggerDataThres-RB': {
        'type': 'int', 'value': 1, 'low': 0, 'high': 2**16 - 1},
    'TriggerDataPol-Sel': {
        'type': 'enum', 'enums': polarity, 'value': 0},
    'TriggerDataPol-Sts': {
        'type': 'enum', 'enums': polarity, 'value': 0},
    'TriggerDataHyst-SP': {
        'type': 'int', 'value': 0, 'low': 0, 'high': 2**16 - 1},
    'TriggerDataHyst-RB': {
        'type': 'int', 'value': 0, 'low': 0, 'high': 2**16 - 1},
    }

pvs_definitions = {
    'ACQBPMMode-Sel': {
        'type': 'enum', 'enums': op_modes, 'value': 0},
    'ACQBPMMode-Sts': {
        'type': 'enum', 'enums': op_modes, 'value': 0},

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
        pvs_loc[nm + 'FFTData.SPAN'] = _copy(acq_int_db)
        pvs_loc[nm + 'FFTData.AMP'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.PHA'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.SIN'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.COS'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.WAVN'] = _copy(acq_data_prop_db)
        pvs_loc[nm + 'FFTData.INDX'] = _copy(acq_int_db)
        pvs_loc[nm + 'FFTData.MXIX'] = _copy(acq_int_db)
        pvs_loc[nm + 'FFTData.WIND'] = {
                'type': 'enum', 'enums': fft_window_types, 'value': 0}
        pvs_loc[nm + 'FFTData.CDIR'] = {
                'type': 'enum', 'enums': fft_conv_direction, 'value': 0}
        pvs_loc[nm + 'FFTData.ASUB'] = {
                'type': 'enum', 'enums': fft_average_subtraction, 'value': 0}
        pvs_definitions.update(pvs_loc)

for acq_md in ['ACQ', 'ACQ_PM']:
    for key, value in config_pvs.items():
        pvs_definitions[acq_md+key] = _copy(value)

for k, v in pvs_definitions.items():
    if 'low' in v:
        v['lolo'] = v['low']
        v['lolim'] = v['low']
    if 'high' in v:
        v['hihi'] = v['high']
        v['hilim'] = v['high']
