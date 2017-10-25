import copy as _copy
import numpy as _np

op_modes = ['Continuous', 'SinglePass']
processed_data = ['PosX', 'PosY', 'PosQ', 'PosS',
                  'AmpA', 'AmpB', 'AmpC', 'AmpD']
raw_data = ['AntA', 'AntB', 'AntC', 'AntD']
slopes = ['Positive', 'Negative']
acq_repeat = ['Dsbl', 'Enbl']

acq_types = ['TbT', 'ADC', 'SOFB']
acq_states = ['Idle', 'Waiting', 'Acquiring', 'Error', 'Aborted']
acq_trig_types = ['Manual', 'External', 'Auto', 'SoftTrig']
acq_trig_exter = ['Trig1', 'Trig2', 'Trig3', 'Trig4', 'Trig5']

sgl_states = ['Idle', 'Waiting', 'Acquiring', 'Error', 'Aborted']
sgl_trig_types = ['External', 'Auto']
sgl_trig_exter = ['Trig1', 'Trig2', 'Trig3', 'Trig4', 'Trig5']

pvs_definitions = {
    'OpMode-Sel': {
        'type': 'enum', 'enums': op_modes, 'value': 0},
    'OpMode-Sts': {
        'type': 'enum', 'enums': op_modes, 'value': 0},
    'PosX-Mon': {
        'type': 'float', 'value': 0.0},
    'PosY-Mon': {
        'type': 'float', 'value': 0.0},
    'PosS-Mon': {
        'type': 'float', 'value': 0.0},
    'PosQ-Mon': {
        'type': 'float', 'value': 0.0},
    'AmpA-Mon': {
        'type': 'float', 'value': 0.0},
    'AmpB-Mon': {
        'type': 'float', 'value': 0.0},
    'AmpC-Mon': {
        'type': 'float', 'value': 0.0},
    'AmpD-Mon': {
        'type': 'float', 'value': 0.0},
    'AcqRate-Sel': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'AcqRate-Sts': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'AcqNrShots-SP': {
        'type': 'int', 'value': 1},
    'AcqNrShots-RB': {
        'type': 'int', 'value': 1},
    'AcqDelay-SP': {
        'type': 'float', 'value': 0.0},
    'AcqDelay-RB': {
        'type': 'float', 'value': 0.0},
    'AcqNrSmplsPre-SP': {
        'type': 'int', 'value': 1000},
    'AcqNrSmplsPre-RB': {
        'type': 'int', 'value': 1000},
    'AcqNrSmplsPos-SP': {
        'type': 'int', 'value': 1000},
    'AcqNrSmplsPos-RB': {
        'type': 'int', 'value': 1000},
    'AcqStart-Cmd': {
        'type': 'int', 'value': 0},
    'AcqStop-Cmd': {
        'type': 'int', 'value': 0},
    'AcqState-Sts': {
        'type': 'enum', 'enums': acq_states, 'value': 0},
    'AcqTrigType-Sel': {
        'type': 'enum', 'enums': acq_trig_types, 'value': 1},
    'AcqTrigType-Sts': {
        'type': 'enum', 'enums': acq_trig_types, 'value': 1},
    'AcqTrigRep-Sel': {
        'type': 'enum', 'enums': acq_repeat, 'value': 0},
    'AcqTrigRep-Sts': {
        'type': 'enum', 'enums': acq_repeat, 'value': 0},
    'AcqTrigExt-Sel': {
        'type': 'enum', 'enums': acq_trig_exter, 'value': 0},
    'AcqTrigExt-Sts': {
        'type': 'enum', 'enums': acq_trig_exter, 'value': 0},
    'AcqTrigAuto-Sel': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'AcqTrigAuto-Sts': {
        'type': 'enum', 'enums': acq_types, 'value': 0},
    'AcqTrigAutoCh-Sel': {
        'type': 'enum', 'enums': processed_data, 'value': 3},
    'AcqTrigAutoCh-Sts': {
        'type': 'enum', 'enums': processed_data, 'value': 3},
    'AcqTrigAutoThres-SP': {
        'type': 'int', 'value': 1},
    'AcqTrigAutoThres-RB': {
        'type': 'int', 'value': 1},
    'AcqTrigAutoSlope-Sel': {
        'type': 'enum', 'enums': slopes, 'value': 0},
    'AcqTrigAutoSlope-Sts': {
        'type': 'enum', 'enums': slopes, 'value': 0},
    'AcqTrigAutoHyst-SP': {
        'type': 'int', 'value': 1},
    'AcqTrigAutoHyst-RB': {
        'type': 'int', 'value': 1},

    'SglPosX-Mon': {
        'type': 'float', 'value': 0.0},
    'SglPosY-Mon': {
        'type': 'float', 'value': 0.0},
    'SglPosS-Mon': {
        'type': 'float', 'value': 0.0},
    'SglPosQ-Mon': {
        'type': 'float', 'value': 0.0},
    'SglAmpA-Mon': {
        'type': 'float', 'value': 0.0},
    'SglAmpB-Mon': {
        'type': 'float', 'value': 0.0},
    'SglAmpC-Mon': {
        'type': 'float', 'value': 0.0},
    'SglAmpD-Mon': {
        'type': 'float', 'value': 0.0},
    'SglAntA-Mon': {
        'type': 'float', 'value': _np.array(1000*[0.0]), 'count': 1000},
    'SglAntB-Mon': {
        'type': 'float', 'value': _np.array(1000*[0.0]), 'count': 1000},
    'SglAntC-Mon': {
        'type': 'float', 'value': _np.array(1000*[0.0]), 'count': 1000},
    'SglAntD-Mon': {
        'type': 'float', 'value': _np.array(1000*[0.0]), 'count': 1000},
    'SglStart-Cmd': {
        'type': 'int', 'value': 0},
    'SglStop-Cmd': {
        'type': 'int', 'value': 0},
    'SglTrigType-Sel': {
        'type': 'enum', 'enums': acq_trig_types, 'value': 1},
    'SglTrigType-Sts': {
        'type': 'enum', 'enums': acq_trig_types, 'value': 1},
    'SglDelay-SP': {
        'type': 'float', 'value': 0.0},
    'SglDelay-RB': {
        'type': 'float', 'value': 0.0},
    'SglTrigExt-Sel': {
        'type': 'enum', 'enums': acq_trig_exter, 'value': 0},
    'SglTrigExt-Sts': {
        'type': 'enum', 'enums': acq_trig_exter, 'value': 0},
    'SglTrigAutoCh-Sel': {
        'type': 'enum', 'enums': processed_data, 'value': 3},
    'SglTrigAutoCh-Sts': {
        'type': 'enum', 'enums': processed_data, 'value': 3},
    'SglTrigAutoThres-SP': {
        'type': 'int', 'value': 1},
    'SglTrigAutoThres-RB': {
        'type': 'int', 'value': 1},
    'SglTrigAutoSlope-Sel': {
        'type': 'enum', 'enums': slopes, 'value': 0},
    'SglTrigAutoSlope-Sts': {
        'type': 'enum', 'enums': slopes, 'value': 0},
    'SglTrigAutoHyst-SP': {
        'type': 'int', 'value': 1},
    'SglTrigAutoHyst-RB': {
        'type': 'int', 'value': 1},
    }

additional_acq_data_props = set()
existent_acq_data_props = set()
max_number_of_shots = 9

acq_data_prop_db = {
    'type': 'float', 'value': _np.array(100000*[0.0]), 'count': 100000}
acq_data_stat_db = {'type': 'float', 'value': 0.0}
for acq in acq_types:
    var = raw_data if acq == 'ADC' else processed_data
    for prop in var:
        for i in range(max_number_of_shots+1):
            nm = acq + prop
            pvs_loc = dict()
            if i:
                nm += 'Shot{0}'.format(i)
            pvs_loc[nm+'-Mon'] = _copy.deepcopy(acq_data_prop_db)
            pvs_loc[nm + 'Max'] = _copy.deepcopy(acq_data_stat_db)
            pvs_loc[nm + 'Min'] = _copy.deepcopy(acq_data_stat_db)
            pvs_loc[nm + 'Ave'] = _copy.deepcopy(acq_data_stat_db)
            pvs_loc[nm + 'Std'] = _copy.deepcopy(acq_data_stat_db)
            pvs_loc[nm + 'FFT.SPAN'] = {'type': 'int', 'value': 0}
            pvs_loc[nm + 'FFT.FREQ'] = _copy.deepcopy(acq_data_prop_db)
            pvs_loc[nm + 'FFT.AMP'] = _copy.deepcopy(acq_data_prop_db)
            pvs_loc[nm + 'FFT.PHA'] = _copy.deepcopy(acq_data_prop_db)
            pvs_loc[nm + 'FFT.SIN'] = _copy.deepcopy(acq_data_prop_db)
            pvs_loc[nm + 'FFT.COS'] = _copy.deepcopy(acq_data_prop_db)
            pvs_definitions.update(pvs_loc)
            if i:
                additional_acq_data_props.update(pvs_loc.keys())
            else:
                existent_acq_data_props.update(pvs_loc.keys())
