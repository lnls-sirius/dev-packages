"""Booster ramp configuration definition."""
import copy as _copy


# TODO: delete this configuration!


def get_dict():
    """Return a dict with ramp settings."""
    module_name = __name__.split('.')[-1]

    _dict = {
        'config_type_name': module_name,
        'value': _copy.deepcopy(_value)
    }

    return _dict

_value = {}

# _value = {
#     'SI-Fam:MA-B1B2:WfmData-SP"': _ref_wfm_array,
# }
