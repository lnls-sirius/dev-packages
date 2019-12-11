"""BO normalized configurations.

Values in _template_dict are arbitrary. They are used just to compare with
corresponding values when a new configuration is tried to be inserted in the
servconf database.
"""
from copy import deepcopy as _dcopy
from siriuspy.ramp import util as _util


def get_dict():
    """Return a dict with ramp settings."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict)
    }

    return _dict


_template_dict = {
    'pvs': [
        # --- dipole [GeV] (just a reference)---
        ['BO-Fam:PS-B-1:Energy-SP', _util.DEFAULT_PS_RAMP_START_ENERGY, 0.0],
        ['BO-Fam:PS-B-2:Energy-SP', _util.DEFAULT_PS_RAMP_START_ENERGY, 0.0],
        # --- quadrupoles ---
        ['BO-Fam:PS-QD:KL-SP', +0.0011197961538728, 0.0],  # [1/m]
        ['BO-Fam:PS-QF:KL-SP', +0.3770999232791374, 0.0],  # [1/m]
        ['BO-02D:PS-QS:KL-SP', +0.0, 0.0],  # [1/m] (skew quadrupole)
        # --- sextupoles ---
        ['BO-Fam:PS-SD:SL-SP', +1.1649714449989350, 0.0],  # [1/m^2]
        ['BO-Fam:PS-SF:SL-SP', +1.1816645548211360, 0.0],  # [1/m^2]
        # --- horizontal correctors ---
        ['BO-01U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-03U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-05U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-07U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-09U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-11U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-13U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-15U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-17U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-19U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-21U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-23U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-25U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-27U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-29U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-31U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-33U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-35U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-37U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-39U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-41U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-43U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-45U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-47U:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-49D:PS-CH:Kick-SP', +0.0, 0.0],  # [urad]
        # --- vertical correctors ---
        ['BO-01U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-03U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-05U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-07U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-09U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-11U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-13U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-15U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-17U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-19U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-21U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-23U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-25U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-27U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-29U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-31U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-33U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-35U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-37U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-39U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-41U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-43U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-45U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-47U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-49U:PS-CV:Kick-SP', +0.0, 0.0],  # [urad]
    ]
}
