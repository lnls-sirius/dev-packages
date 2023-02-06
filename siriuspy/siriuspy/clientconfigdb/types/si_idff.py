"""SI Insertion Device Feedforward (IDFF) Configuration.

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


# IDFF corrector table
#
# 1st-level keys:
#   - 'pvnames': its value is a dict with
#       ('kparameter', 'ch1', 'ch2', ... 'qs1', 'qs2') as
#       keys and corresponding pvname values for
#       ID k-variation parameter readout and correctors setpoints.
#   - 'polarizations': its value is a dict with
#       ('horizontal', 'vertical', ...) light polarization configs of the ID
#       as keys and dicts with kparameter and correctors
#       IDFF tables as lists.

_template_dict = {
    'pvnames': {
        'kparameter': 'SI-10SB:ID-EPU50:Gap-Mon',
        'ch1': 'SI-10SB:PS-CH-1:Current-SP',
        'ch2': 'SI-10SB:PS-CH-2:Current-SP',
        'cv1': 'SI-10SB:PS-CV-1:Current-SP',
        'cv2': 'SI-10SB:PS-CV-2:Current-SP',
        'qs1': 'SI-10SB:PS-QS-1:Current-SP',
        'qs2': 'SI-10SB:PS-QS-2:Current-SP',
    },
    'polarizations': {
        'horizontal': {
            'kparameter': [-1, 0, 1],
            'ch1': 3*[0],
            'ch2': 3*[0],
            'cv1': 3*[0],
            'cv2': 3*[0],
            'qs1': 3*[0],
            'qs2': 3*[0],
            },
        'vertical': {
            'kparameter': [-2, -1, 0, 1, 2],
            'ch1': 5*[0],
            'ch2': 5*[0],
            'cv1': 5*[0],
            'cv2': 5*[0],
            'qs1': 5*[0],
            'qs2': 5*[0],
            },
    },
}
