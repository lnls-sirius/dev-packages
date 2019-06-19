"""BO orbit correction response matrix configuration.

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
        'value': _dcopy(_template),
        'check': False,
    }
    return _dict


# Orbit Correction Response Matrix for Booster
#   -First bpm in the list is the first seen by the beam during injection
#   -First ch in the list is the first seen by the beam during injection
#   -First cv in the list is the first seen by the beam during injection
#   -RF is the last component;
#   -Units: bpm --> um; (ch, cv) --> urad; RF --> Hz
#
# | BPMXi |   | Mik ... Mil ... Min |   | CHk |
# |  ...  | = | ... ... ... ... ... | * | ... |
# | BPMYj |   | Mjk ... Mjl ... Mjn |   | CVl |
#                                       | ... |
#                                       | RFn |

_template = 100*[51*[0.0]]
