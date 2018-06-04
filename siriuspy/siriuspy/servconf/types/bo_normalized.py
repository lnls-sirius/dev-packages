"""BO normalized configurations.

Values in _template_dict are arbitrary. They are used just to compare with
corresponding values when a new configuration is tried to be inserted in the
servconf database.
"""
from copy import deepcopy as _dcopy


def get_dict():
    """Return a dict with ramp settings."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict)
    }

    return _dict


_template_dict = {
    # --- dipole ---
    'BO-Fam:MA-B': 0.0,  # [Energy: GeV]  (just a reference)
    # --- quadrupoles ---
    'BO-Fam:MA-QF': 0.0,  # [KL: 1/m]
    'BO-Fam:MA-QD': 0.0,  # [KL: 1/m]
    'BO-02D:MA-QS': 0.0,  # [KL: 1/m] (skew quadrupole)
    # --- sextupoles ---
    'BO-Fam:MA-SF': 0.0,  # [SL: 1/m^2]
    'BO-Fam:MA-SD': 0.0,  # [SL: 1/m^2]
    # --- horizontal correctors ---
    'BO-01U:MA-CH': 0.0,  # [Kick: rad]
    'BO-03U:MA-CH': 0.0,  # [Kick: rad]
    'BO-05U:MA-CH': 0.0,  # [Kick: rad]
    'BO-07U:MA-CH': 0.0,  # [Kick: rad]
    'BO-09U:MA-CH': 0.0,  # [Kick: rad]
    'BO-11U:MA-CH': 0.0,  # [Kick: rad]
    'BO-13U:MA-CH': 0.0,  # [Kick: rad]
    'BO-15U:MA-CH': 0.0,  # [Kick: rad]
    'BO-17U:MA-CH': 0.0,  # [Kick: rad]
    'BO-19U:MA-CH': 0.0,  # [Kick: rad]
    'BO-21U:MA-CH': 0.0,  # [Kick: rad]
    'BO-23U:MA-CH': 0.0,  # [Kick: rad]
    'BO-25U:MA-CH': 0.0,  # [Kick: rad]
    'BO-27U:MA-CH': 0.0,  # [Kick: rad]
    'BO-29U:MA-CH': 0.0,  # [Kick: rad]
    'BO-31U:MA-CH': 0.0,  # [Kick: rad]
    'BO-33U:MA-CH': 0.0,  # [Kick: rad]
    'BO-35U:MA-CH': 0.0,  # [Kick: rad]
    'BO-37U:MA-CH': 0.0,  # [Kick: rad]
    'BO-39U:MA-CH': 0.0,  # [Kick: rad]
    'BO-41U:MA-CH': 0.0,  # [Kick: rad]
    'BO-43U:MA-CH': 0.0,  # [Kick: rad]
    'BO-45U:MA-CH': 0.0,  # [Kick: rad]
    'BO-47U:MA-CH': 0.0,  # [Kick: rad]
    'BO-49D:MA-CH': 0.0,  # [Kick: rad]
    # --- vertical correctors ---
    'BO-01U:MA-CV': 0.0,  # [Kick: rad]
    'BO-03U:MA-CV': 0.0,  # [Kick: rad]
    'BO-05U:MA-CV': 0.0,  # [Kick: rad]
    'BO-07U:MA-CV': 0.0,  # [Kick: rad]
    'BO-09U:MA-CV': 0.0,  # [Kick: rad]
    'BO-11U:MA-CV': 0.0,  # [Kick: rad]
    'BO-13U:MA-CV': 0.0,  # [Kick: rad]
    'BO-15U:MA-CV': 0.0,  # [Kick: rad]
    'BO-17U:MA-CV': 0.0,  # [Kick: rad]
    'BO-19U:MA-CV': 0.0,  # [Kick: rad]
    'BO-21U:MA-CV': 0.0,  # [Kick: rad]
    'BO-23U:MA-CV': 0.0,  # [Kick: rad]
    'BO-25U:MA-CV': 0.0,  # [Kick: rad]
    'BO-27U:MA-CV': 0.0,  # [Kick: rad]
    'BO-29U:MA-CV': 0.0,  # [Kick: rad]
    'BO-31U:MA-CV': 0.0,  # [Kick: rad]
    'BO-33U:MA-CV': 0.0,  # [Kick: rad]
    'BO-35U:MA-CV': 0.0,  # [Kick: rad]
    'BO-37U:MA-CV': 0.0,  # [Kick: rad]
    'BO-39U:MA-CV': 0.0,  # [Kick: rad]
    'BO-41U:MA-CV': 0.0,  # [Kick: rad]
    'BO-43U:MA-CV': 0.0,  # [Kick: rad]
    'BO-45U:MA-CV': 0.0,  # [Kick: rad]
    'BO-47U:MA-CV': 0.0,  # [Kick: rad]
    'BO-49U:MA-CV': 0.0,  # [Kick: rad]
}
