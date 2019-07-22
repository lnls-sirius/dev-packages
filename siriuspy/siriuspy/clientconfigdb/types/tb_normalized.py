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
        ['TB-Fam:MA-B:Energy-SP', 0.0, 0.0],  # [GeV]
        ['TB-01:MA-QD1:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-01:MA-QF1:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-02:MA-QD2A:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-02:MA-QF2A:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-02:MA-QD2B:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-02:MA-QF2B:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-03:MA-QD3:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-03:MA-QF3:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-04:MA-QD4:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-04:MA-QF4:KL-SP', 0.0, 0.0],  # [1/m]
        ['TB-01:MA-CH-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-01:MA-CV-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-01:MA-CH-2:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-01:MA-CV-2:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-02:MA-CH-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-02:MA-CV-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-02:MA-CH-2:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-02:MA-CV-2:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-04:MA-CH-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-04:MA-CH-2:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-04:MA-CV-1:Kick-SP', 0.0, 0.0],  # [urad]
        ['TB-04:MA-CV-2:Kick-SP', 0.0, 0.0],  # [urad]
    ]
}
