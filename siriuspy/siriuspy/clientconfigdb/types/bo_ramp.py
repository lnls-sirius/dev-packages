"""BO ramp configuration.

Values in _template_dict are arbitrary. They are used just to compare with
corresponding values when a new configuration is tried to be inserted in the
servconf database.
"""
from copy import deepcopy as _dcopy
from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE as _MAX_WFMSIZE
from siriuspy.ramp import util as _util


def get_dict():
    """Return a dict with ramp settings."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict)
    }

    return _dict


_ps_ramp = {
    # ramp total duration [ms]
    'duration':             _util.DEFAULT_PS_RAMP_DURATION,
    # number of points in power supply waveforms
    'wfm_nrpoints':         _MAX_WFMSIZE,
    # ramp time parameters [ms]
    'rampup_start_time':    _util.DEFAULT_PS_RAMP_RAMPUP_START_TIME,
    'rampup_stop_time':     _util.DEFAULT_PS_RAMP_RAMPUP_STOP_TIME,
    'rampdown_start_time':  _util.DEFAULT_PS_RAMP_RAMPDOWN_START_TIME,
    'rampdown_stop_time':   _util.DEFAULT_PS_RAMP_RAMPDOWN_STOP_TIME,
    # ramp energy parameters [GeV]
    'start_energy':         _util.DEFAULT_PS_RAMP_START_ENERGY,
    'rampup_start_energy':  _util.DEFAULT_PS_RAMP_RAMPUP_START_ENERGY,
    'rampup_stop_energy':   _util.DEFAULT_PS_RAMP_RAMPUP_STOP_ENERGY,
    'plateau_energy':       _util.DEFAULT_PS_RAMP_PLATEAU_ENERGY,
    'rampdown_start_energy': _util.DEFAULT_PS_RAMP_RAMPDOWN_START_ENERGY,
    'rampdown_stop_energy': _util.DEFAULT_PS_RAMP_RAMPDOWN_STOP_ENERGY,
}

_ps_normalized_configs = [
    # time [ms]            normalized configuration name
    [0,                              'ramp-start'],
    [_util.DEFAULT_PS_RAMP_DURATION, 'ramp-stop'],
]

_rf_ramp = {
    # ramp increase duration [min]
    'rampinc_duration': _util.DEFAULT_RF_RAMP_RAMPINC_DURATION,
    # ramp intervals durations [ms]
    'bottom_duration':      _util.DEFAULT_RF_RAMP_BOTTOM_DURATION,
    'rampup_duration':      _util.DEFAULT_RF_RAMP_RAMPUP_DURATION,
    'top_duration':         _util.DEFAULT_RF_RAMP_TOP_DURATION,
    'rampdown_duration':    _util.DEFAULT_RF_RAMP_RAMPDOWN_DURATION,
    # ramp voltage parameters [kV]
    'bottom_voltage':       _util.DEFAULT_RF_RAMP_BOTTOM_VOLTAGE,
    'top_voltage':          _util.DEFAULT_RF_RAMP_TOP_VOLTAGE,
    # ramp phase parameters [°]
    'bottom_phase':         _util.DEFAULT_RF_RAMP_BOTTOM_PHASE,
    'top_phase':            _util.DEFAULT_RF_RAMP_TOP_PHASE,
}

_ti_params = {
    'injection_time':       _util.DEFAULT_TI_PARAMS_INJECTION_TIME,  # [ms]
    'ejection_time':        _util.DEFAULT_TI_PARAMS_EJECTION_TIME,  # [ms]
    'rf_ramp_delay':        _util.DEFAULT_TI_PARAMS_RF_RAMP_DELAY,  # [us]
    'ps_ramp_delay':        _util.DEFAULT_TI_PARAMS_PS_RAMP_DELAY,  # [us]
}


_template_dict = {
    'ps_ramp': _ps_ramp,
    'ps_normalized_configs*': _ps_normalized_configs,
    'rf_ramp': _rf_ramp,
    'ti_params': _ti_params,
}
