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


# _eje_current = 981.7835215242153  # [A] - BO dipole current @ 3 GeV
# _eje_energy = 3.0  # [GeV]
# _i07 = (1, 104, 2480, 2576, 2640, 2736, 3840, 3999)
# _v07 = (0.01, 0.026250000000000006, 1.0339285714285713,
#         1.05, 1.05, 1.0, 0.07, 0.01)
# _ramp_duration = _util.DEFAULT_RAMP_DURATION  # [s]
# _wfm_nrpoints = _MAX_WFMSIZE
# _interval = _ramp_duration / (_wfm_nrpoints - 1.0)


_ramp_dipole = {
    # dipole delay [us]
    'delay': 0.0,
    # number of points in power supply waveforms
    'wfm_nrpoints': _MAX_WFMSIZE,
    # ramp time parameters [ms]
    'duration': _util.DEFAULT_RAMP_DURATION,
    'rampup_start_time': _util.DEFAULT_RAMP_RAMPUP_START_TIME,
    'rampup_stop_time': _util.DEFAULT_RAMP_RAMPUP_STOP_TIME,
    'rampdown_start_time': _util.DEFAULT_RAMP_RAMPDOWN_START_TIME,
    'rampdown_stop_time': _util.DEFAULT_RAMP_RAMPDOWN_STOP_TIME,
    # ramp energy parameters [GeV]
    'start_energy': _util.DEFAULT_RAMP_START_ENERGY,
    'rampup_start_energy': _util.DEFAULT_RAMP_RAMPUP_START_ENERGY,
    'rampup_stop_energy': _util.DEFAULT_RAMP_RAMPUP_STOP_ENERGY,
    'plateau_energy': _util.DEFAULT_RAMP_PLATEAU_ENERGY,
    'rampdown_start_energy': _util.DEFAULT_RAMP_RAMPDOWN_START_ENERGY,
    'rampdown_stop_energy': _util.DEFAULT_RAMP_RAMPDOWN_STOP_ENERGY,
}

_normalized_configs = [
    # time [ms]            normalized configuration name
    [_util.DEFAULT_RAMP_RAMPUP_START_TIME, 'rampup-start'],
    [_util.DEFAULT_RAMP_RAMPUP_STOP_TIME, 'rampup-stop'],
]

_rf_parameters = {
    # global RF delay [us]
    'delay': 0.0,
}


_template_dict = {
    'injection_time': _util.DEFAULT_RAMP_INJECTION_TIME,  # [ms]
    'ejection_time': _util.DEFAULT_RAMP_EJECTION_TIME,  # [ms]
    'rf_parameters': _rf_parameters,
    'normalized_configs*': _normalized_configs,
    'ramp_dipole': _ramp_dipole,
}
