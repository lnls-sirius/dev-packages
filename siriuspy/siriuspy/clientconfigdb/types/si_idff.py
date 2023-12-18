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
#       ('pparameter', 'kparameter', 'ch1', 'ch2', ... 'qs1', 'qs2') as
#       keys and corresponding pvname values for
#       ID k-variation parameter readout and correctors setpoints.
#   - 'polarizations': its value is a dict with
#       ('none', 'horizontal', 'vertical', ...) light polarization configs of
#       the ID as keys and dicts with kparameter and correctors
#       IDFF tables as lists.
#
#   obs:
#   1) pparameter: pvname that varies polarization configurations
#   2) kparameter: pvname that varies k (photon energy) configurations
#   3) 'none' polarization configuration should always be in the config.
#       it is a transition configuration between polarization configs.

_template_dict = {
    'description': 'description of the IDFF particularities.',
    'pvnames': {
        'pparameter': 'SI-10SB:ID-EPU50:Phase-Mon',
        'kparameter': 'SI-10SB:ID-EPU50:Gap-Mon',
        'ch1': 'SI-10SB:PS-CH-1:Current-SP',
        'ch2': 'SI-10SB:PS-CH-2:Current-SP',
        'cv1': 'SI-10SB:PS-CV-1:Current-SP',
        'cv2': 'SI-10SB:PS-CV-2:Current-SP',
        'qs1': 'SI-10SB:PS-QS-1:Current-SP',
        'qs2': 'SI-10SB:PS-QS-2:Current-SP',
        'qd1_1': 'SI-10M1:PS-QDB1:Current-SP',
        'qd2_1': 'SI-10M2:PS-QDB1:Current-SP',
        'qf1': 'SI-10M1:PS-QFB:Current-SP',
        'qf2': 'SI-10M2:PS-QFB:Current-SP',
        'qd1_2': 'SI-10M1:PS-QDB2:Current-SP',
        'qd2_2': 'SI-10M2:PS-QDB2:Current-SP',
    },
    'polarizations': {
        'none': {
            'pparameter': [-16.39, 0.0, 16.39, 25.0],
            'kparameter': 300,
            'ch1': 4*[0],
            'ch2': 4*[0],
            'cv1': 4*[0],
            'cv2': 4*[0],
            'qs1': 4*[0],
            'qs2': 4*[0],
            'qd1_1': 4*[0],
            'qd2_1': 4*[0],
            'qf1': 4*[0],
            'qf2': 4*[0],
            'qd1_2': 4*[0],
            'qd2_2': 4*[0],
            },
        'circularn': {
            'pparameter': -16.39,
            'kparameter': [22.0, 300.0],
            'ch1': 2*[0],
            'ch2': 2*[0],
            'cv1': 2*[0],
            'cv2': 2*[0],
            'qs1': 2*[0],
            'qs2': 2*[0],
            'qd1_1': 2*[0],
            'qd2_1': 2*[0],
            'qf1': 2*[0],
            'qf2': 2*[0],
            'qd1_2': 2*[0],
            'qd2_2': 2*[0],
            },
        'horizontal': {
            'pparameter': 0,
            'kparameter': [22.0, 100.0, 300.0],
            'ch1': 3*[0],
            'ch2': 3*[0],
            'cv1': 3*[0],
            'cv2': 3*[0],
            'qs1': 3*[0],
            'qs2': 3*[0],
            'qd1_1': 3*[0],
            'qd2_1': 3*[0],
            'qf1': 3*[0],
            'qf2': 3*[0],
            'qd1_2': 3*[0],
            'qd2_2': 3*[0],
            },
        'circularp': {
            'pparameter': 16.39,
            'kparameter': [22.0, 300.0],
            'ch1': 2*[0],
            'ch2': 2*[0],
            'cv1': 2*[0],
            'cv2': 2*[0],
            'qs1': 2*[0],
            'qs2': 2*[0],
            'qd1_1': 2*[0],
            'qd2_1': 2*[0],
            'qf1': 2*[0],
            'qf2': 2*[0],
            'qd1_2': 2*[0],
            'qd2_2': 2*[0],
            },
        'vertical': {
            'pparameter': 25,
            'kparameter': [22.0, 60, 100.0, 200, 300.0],
            'ch1': 5*[0],
            'ch2': 5*[0],
            'cv1': 5*[0],
            'cv2': 5*[0],
            'qs1': 5*[0],
            'qs2': 5*[0],
            'qd1_1': 5*[0],
            'qd2_1': 5*[0],
            'qf1': 5*[0],
            'qf2': 5*[0],
            'qd1_2': 5*[0],
            'qd2_2': 5*[0],
            },
    },
}
