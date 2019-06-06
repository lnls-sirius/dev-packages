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
        # --- dipole ---
        ['BO-Fam:MA-B:Energy-SP', _util.DEFAULT_PS_RAMP_START_ENERGY, 0.0],  # [GeV] (just a reference)
        # --- quadrupoles ---
        ['BO-Fam:MA-QD:KL-SP', +0.0011197961538728, 0.0],  # [1/m]
        ['BO-Fam:MA-QF:KL-SP', +0.3770999232791374, 0.0],  # [1/m]
        ['BO-02D:MA-QS:KL-SP', +0.0, 0.0],  # [1/m] (skew quadrupole)
        # --- sextupoles ---
        ['BO-Fam:MA-SD:SL-SP', +1.1649714449989350, 0.0],  # [1/m^2]
        ['BO-Fam:MA-SF:SL-SP', +1.1816645548211360, 0.0],  # [1/m^2]
        # --- horizontal correctors ---
        ['BO-01U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-03U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-05U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-07U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-09U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-11U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-13U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-15U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-17U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-19U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-21U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-23U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-25U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-27U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-29U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-31U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-33U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-35U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-37U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-39U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-41U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-43U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-45U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-47U:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-49D:MA-CH:Kick-SP', +0.0, 0.0],  # [urad]
        # --- vertical correctors ---
        ['BO-01U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-03U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-05U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-07U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-09U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-11U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-13U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-15U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-17U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-19U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-21U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-23U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-25U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-27U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-29U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-31U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-33U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-35U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-37U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-39U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-41U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-43U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-45U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-47U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
        ['BO-49U:MA-CV:Kick-SP', +0.0, 0.0],  # [urad]
    ]
}
