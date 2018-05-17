"""Configuration Type Definition."""

import copy as _copy

# TODO: delete this configuration!

def get_dict():
    """Return configuration type dictionar."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _copy.deepcopy(_value)
    }
    return _dict


_value = {'tunex': 0.0, 'tuney': 0.0, }
