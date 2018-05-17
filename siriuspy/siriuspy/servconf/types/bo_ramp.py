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


_current = 981.7835215242153  # [A] - BO dipole current @ 3 GeV
_norm_v07 = (0.01, 0.026250000000000006, 1.0339285714285713,
             1.05, 1.05, 1.0, 0.07, 0.01)
_bo_dipole_ramp_parameters = {
    # start indices of regions
    'i07*': [1, 104, 2480, 2576, 2640, 2736, 3840, 3999],
    # current values [A]
    'v07*': [_current * v for v in _norm_v07],}
_normalized_configurations = [
    'normalized_config_name_1',
    'normalized_config_name_2',]
_rf_parameters = {
    'delay': 0.0,}  # TODO: int or float?


_template_dict = {
    'power_supplies_delay': 0.0,  # TODO: int or float?
    'bo_dipole_ramp_parameters': _bo_dipole_ramp_parameters,
    'normalized_configurations*': _normalized_configurations,
    'rf_parameters': _rf_parameters,
}
