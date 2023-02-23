"""Window position and size configuration.

Values in _template_dict are arbitrary. They are used just to compare with
corresponding values when a new configuration is tried to be inserted in the
servconf database.
"""
from copy import deepcopy as _dcopy


def get_dict():
    """Return configuration type dictionary."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict),
        'check': False,
    }
    return _dict

# This configuration contains the positions and size of windows, that were open at the configuration save.

_template_dict = {
    'computer': 'computername',
    'config': [
        {'window': 'windowname',
         'size': [0, 0],
         'position': [0, 0]},
         ],
    }
