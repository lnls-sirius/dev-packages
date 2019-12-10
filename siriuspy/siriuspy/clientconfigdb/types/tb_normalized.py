"""TB normalized configurations.

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
    'pvs': [
        ['TB-Fam:PS-B:Energy-SP', 0.0, 0.0],  # [GeV]
        ['TB-01:PS-QD1:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-01:PS-QF1:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-02:PS-QD2A:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-02:PS-QF2A:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-02:PS-QD2B:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-02:PS-QF2B:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-03:PS-QD3:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-03:PS-QF3:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-04:PS-QD4:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-04:PS-QF4:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-01:PS-CH-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-01:PS-CV-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-01:PS-CH-2:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-01:PS-CV-2:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-02:PS-CH-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-02:PS-CV-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-02:PS-CH-2:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-02:PS-CV-2:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-04:PS-CH-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-04:PS-CH-2:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-04:PS-CV-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-04:PS-CV-2:Kick-SP', 0.0, 0.0],  # [urad]
    ]
}
