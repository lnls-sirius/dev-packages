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
#       ('pparameter', 'kparameter', 'ch_1', 'ch_2', ... 'qs_1', 'qs_2') as
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
#
# See siriuspy.search.IDSearch for more details

_template_dict = {
    'description': 'description of the IDFF particularities.',
    'pvnames': {
        'pparameter': 'SI-10SB:ID-EPU50:Phase-Mon',
        'kparameter': 'SI-10SB:ID-EPU50:Gap-Mon',
        'ch_1': 'SI-10SB:PS-CH-1:Current-SP',
        'ch_2': 'SI-10SB:PS-CH-2:Current-SP',
        'cv_1': 'SI-10SB:PS-CV-1:Current-SP',
        'cv_2': 'SI-10SB:PS-CV-2:Current-SP',
        'qs_1': 'SI-10SB:PS-QS-1:Current-SP',
        'qs_2': 'SI-10SB:PS-QS-2:Current-SP',
    },
    'offsets': {
        'qs_1': 0.0,
        'qs_2': 0.0,
    },
    'polarizations': {
        'none': {
            'pparameter': [-16.39, 0.0, 16.39, 25.0],
            'kparameter': 300,
            'ch_1': 4*[0],
            'ch_2': 4*[0],
            'cv_1': 4*[0],
            'cv_2': 4*[0],
            'qs_1': 4*[0],
            'qs_2': 4*[0],
            },
        'circularn': {
            'pparameter': -16.39,
            'kparameter': [22.0, 300.0],
            'ch_1': 2*[0],
            'ch_2': 2*[0],
            'cv_1': 2*[0],
            'cv_2': 2*[0],
            'qs_1': 2*[0],
            'qs_2': 2*[0],
            },
        'horizontal': {
            'pparameter': 0,
            'kparameter': [22.0, 100.0, 300.0],
            'ch_1': 3*[0],
            'ch_2': 3*[0],
            'cv_1': 3*[0],
            'cv_2': 3*[0],
            'qs_1': 3*[0],
            'qs_2': 3*[0],
            },
        'circularp': {
            'pparameter': 16.39,
            'kparameter': [22.0, 300.0],
            'ch_1': 2*[0],
            'ch_2': 2*[0],
            'cv_1': 2*[0],
            'cv_2': 2*[0],
            'qs_1': 2*[0],
            'qs_2': 2*[0],
            },
        'vertical': {
            'pparameter': 25,
            'kparameter': [22.0, 60, 100.0, 200, 300.0],
            'ch_1': 5*[0],
            'ch_2': 5*[0],
            'cv_1': 5*[0],
            'cv_2': 5*[0],
            'qs_1': 5*[0],
            'qs_2': 5*[0],
            },
    },
}
