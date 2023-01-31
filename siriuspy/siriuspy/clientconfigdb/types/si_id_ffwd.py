"""SI Insertion device feedforward configuration.

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


# Insertion Device Feedforward tables for correctors
#
# 1st-level keys: polarization type strings
# 1st-level values: dictionaries with
#    a) 'k-parameter' key with values (list) of the knob for k-parameter
#       variation.
#    b) more (key, value) pairs:
#       key: corrector devname
#       value: list with setpoint values (either in harware or physics units)
#       associated with each k-parameter variation knob value.

_template_dict = {
    'polarization-horizontal': {
        'k-parameter': [-1, 0, 1],
        'ch1-devname': 3*[0],
        'cv1-devname': 3*[0],
        'qs1-devname': 3*[0],
        'ch2-devname': 3*[0],
        'cv2-devname': 3*[0],
        'qs2-devname': 3*[0],
        },
    'polarization-vertical': {
        'k-parameter': [-2, -1, 0, 1, 2],
        'ch1-devname': 5*[0],
        'cv1-devname': 5*[0],
        'qs1-devname': 5*[0],
        'ch2-devname': 5*[0],
        'cv2-devname': 5*[0],
        'qs2-devname': 5*[0],
        },
}
