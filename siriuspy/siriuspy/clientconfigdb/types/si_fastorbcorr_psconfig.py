"""SI fast orbit correction power supply matrix configuration.

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


#  Fast Orbit Correction Power Supply Matrix for Sirius:
#    Each row refers to a fast corrector
#   -First column is the Kp for each power supply
#   -Second column is the Ti for each power supply
#   -Third column is the Acc filter gain for each power supply
#   -From the fourth to the last nth column,
#    we have the acc filter coefficients
#   -By standard, we consider 4 biquads for each corrector.
#    One biquad has 5 coefficients
#
# | KPi  TIi  GAINi  COEFFi        COEFFn |
# |  ................................... |
# | KPj  TIj  GAINj  COEFFj       COEFFn |

_template = 160*[23*[0.0]]
