"""BO ramp configuration.

Values in _template_dict are arbitrary. They are used just to compare with
corresponding values when a new configuration is tried to be inserted in the
servconf database.
"""
from copy import deepcopy as _dcopy


def get_dict():
    """Return a dict with ramp settings."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict)
    }

    return _dict


_eje_current = 981.7835215242153  # [A] - BO dipole current @ 3 GeV
_i07 = (1, 104, 2480, 2576, 2640, 2736, 3840, 3999)
_v07 = (0.01, 0.026250000000000006, 1.0339285714285713,
        1.05, 1.05, 1.0, 0.07, 0.01)
_ramp_duration = 0.490  # [s]
_wfm_nrpoints = 4000
_interval = _ramp_duration / (_wfm_nrpoints - 1.0)


_dipole_ramp_parameters = {
    # ramp duration
    'duration': _ramp_duration,  # [s]
    # start indices of regions
    'time': [_interval * i for i in _i07],
    # current values [A]
    'current': [_eje_current * v for v in _v07],
}
_normalized_configurations = [
    (0.000, 'configname1'),
    (0.100, 'configname2'),
    (0.400, 'configname3'),
]
_rf_parameters = {
    'delay': 0.0,  # [us]
}


_template_dict = {
    'power_supplies_delay': 0.0,  # [us]
    'dipole_ramp_parameters': _dipole_ramp_parameters,
    'normalized_configurations*': _normalized_configurations,
    'rf_parameters': _rf_parameters,
}
