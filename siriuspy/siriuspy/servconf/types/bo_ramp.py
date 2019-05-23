"""BO ramp configuration.

Values in _template_dict are arbitrary. They are used just to compare with
corresponding values when a new configuration is tried to be inserted in the
servconf database.
"""
from copy import deepcopy as _dcopy

import numpy as _np
from siriuspy.csdevice.pwrsupply import \
    DEFAULT_WFMDATA as _DEFAULT_WFMDATA, Const as _PSConst
from siriuspy.csdevice.util import Const as _Const


_RmpWfm = _PSConst.OpMode.RmpWfm
_Enbl = _Const.DsblEnbl.Enbl


def get_dict():
    """Return a dict with ramp settings."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict),
        'checklength': False
    }

    return _dict


_ps_pvs = [  # magnets opmode and wfmdata pvs
    ['BO-Fam:MA-B:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-Fam:MA-QD:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-Fam:MA-QF:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-02D:MA-QS:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-Fam:MA-SD:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-Fam:MA-SF:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-01U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-03U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-05U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-07U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-09U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-11U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-13U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-15U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-17U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-19U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-21U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-23U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-25U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-27U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-29U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-31U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-33U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-35U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-37U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-39U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-41U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-43U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-45U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-47U:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-49D:MA-CH:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-01U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-03U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-05U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-07U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-09U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-11U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-13U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-15U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-17U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-19U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-21U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-23U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-25U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-27U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-29U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-31U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-33U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-35U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-37U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-39U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-41U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-43U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-45U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-47U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-49U:MA-CV:OpMode-Sel', _RmpWfm, 0.0],
    ['BO-Fam:MA-B:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-Fam:MA-QD:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-Fam:MA-QF:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-02D:MA-QS:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-Fam:MA-SD:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-Fam:MA-SF:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-01U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-03U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-05U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-07U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-09U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-11U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-13U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-15U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-17U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-19U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-21U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-23U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-25U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-27U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-29U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-31U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-33U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-35U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-37U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-39U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-41U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-43U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-45U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-47U:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-49D:MA-CH:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-01U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-03U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-05U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-07U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-09U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-11U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-13U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-15U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-17U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-19U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-21U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-23U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-25U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-27U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-29U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-31U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-33U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-35U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-37U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-39U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-41U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-43U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-45U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-47U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
    ['BO-49U:MA-CV:WfmData-SP', _np.array(_DEFAULT_WFMDATA), 0.0],
]

_ti_pvs = [  # timing pvs
    # events
    ['RA-RaMO:TI-EVG:LinacMode-Sel', 0, 0.0],
    ['RA-RaMO:TI-EVG:LinacDelayType-Sel', 0, 0.0],
    ['RA-RaMO:TI-EVG:LinacDelay-SP', 0.0, 0.0],  # linac_dly [us]

    ['RA-RaMO:TI-EVG:InjBOMode-Sel', 0, 0.0],
    ['RA-RaMO:TI-EVG:InjBODelayType-Sel', 0, 0.0],
    ['RA-RaMO:TI-EVG:InjBODelay-SP', 0.0, 0.0],  # injbo_dly [us]

    ['RA-RaMO:TI-EVG:RmpBOMode-Sel', 0, 0.0],
    ['RA-RaMO:TI-EVG:RmpBODelayType-Sel', 0, 0.0],
    ['RA-RaMO:TI-EVG:RmpBODelay-SP', 0.0, 0.0],

    ['RA-RaMO:TI-EVG:InjSIMode-Sel', 0, 0.0],
    ['RA-RaMO:TI-EVG:InjSIDelayType-Sel', 0, 0.0],
    ['RA-RaMO:TI-EVG:InjSIDelay-SP', 0.0, 0.0],  # injbo_dly+eje_time*1000 [us]

    # triggers
    ['BO-Glob:TI-Mags:ByPassIntlk-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags:Duration-SP', 0.0, 0.0],  # [us]
    ['BO-Glob:TI-Mags:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-Mags:Delay-SP', 0.0, 0.0],  # [us]
    ['BO-Glob:TI-Mags:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags:State-Sel', _Enbl, 0.0],

    ['BO-Glob:TI-Corrs:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-Corrs:Duration-SP', 0.0, 0.0],  # [us]
    ['BO-Glob:TI-Corrs:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-Corrs:Delay-SP', 0.0, 0.0],  # [us]
    ['BO-Glob:TI-Corrs:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-Corrs:State-Sel', _Enbl, 0.0],

    ['BO-Glob:TI-LLRF-Rmp:ByPassIntlk-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:Duration-SP', 0.0, 0.0],  # [us]
    ['BO-Glob:TI-LLRF-Rmp:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:Delay-SP', 0.0, 0.0],  # [us]
    ['BO-Glob:TI-LLRF-Rmp:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:State-Sel', _Enbl, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:RFDelayType-Sel', 0.0, 0.0],

    ['LI-01:TI-EGun-SglBun:ByPassIntlk-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:Src-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:Duration-SP', 0.0, 0.0],  # [us]
    ['LI-01:TI-EGun-SglBun:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:Delay-SP', 0.0, 0.0],  # [us]
    ['LI-01:TI-EGun-SglBun:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:State-Sel', _Enbl, 0.0],

    ['LI-01:TI-EGun-MultBun:ByPassIntlk-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:Src-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:Duration-SP', 0.0, 0.0],  # [us]
    ['LI-01:TI-EGun-MultBun:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:Delay-SP', 0.0, 0.0],  # [us]
    ['LI-01:TI-EGun-MultBun:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:State-Sel', _Enbl, 0.0],

    ['BO-48D:TI-EjeKckr:ByPassIntlk-Sel', 0, 0.0],
    ['BO-48D:TI-EjeKckr:Src-Sel', 0, 0.0],
    ['BO-48D:TI-EjeKckr:Duration-SP', 0.0, 0.0],  # [us]
    ['BO-48D:TI-EjeKckr:NrPulses-SP', 0, 0.0],
    ['BO-48D:TI-EjeKckr:Delay-SP', 0.0, 0.0],  # [us]
    ['BO-48D:TI-EjeKckr:Polarity-Sel', 0.0, 0],
    ['BO-48D:TI-EjeKckr:State-Sel', _Enbl, 0.0],
]

_rf_pvs = [  # rf pvs
    ['BO-05D:RF-LLRF:RmpEnbl-Sel', _Enbl, 0.0],
    ['BO-05D:RF-LLRF:RmpTs1-SP', 0.0, 0.0],
    ['BO-05D:RF-LLRF:RmpTs2-SP', 0.0, 0.0],
    ['BO-05D:RF-LLRF:RmpTs3-SP', 0.0, 0.0],
    ['BO-05D:RF-LLRF:RmpTs4-SP', 0.0, 0.0],
    ['BO-05D:RF-LLRF:RmpIncTs-SP', 0.0, 0.0],
    ['BO-05D:RF-LLRF:RmpVoltBot-SP', 0.0, 0.0],
    ['BO-05D:RF-LLRF:RmpVoltTop-SP', 0.0, 0.0],
    ['BO-05D:RF-LLRF:RmpPhsBot-SP', 0.0, 0.0],
    ['BO-05D:RF-LLRF:RmpPhsTop-SP', 0.0, 0.0],
]

_template_dict = {
    'pvs': _ps_pvs + _ti_pvs + _rf_pvs,
}
