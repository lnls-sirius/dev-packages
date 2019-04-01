"""TB orbit configuration.

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


# TB Orbit:
#   -First bpm in the list is the first seen by the beam during injection
#   -Units: um (micrometer)
#
_template_dict = {
    'x': 6*[0.0],  # unit: um
    'y': 6*[0.0]   # unit: um
    }
