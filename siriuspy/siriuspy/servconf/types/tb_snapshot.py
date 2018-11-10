"""TB Snapshot configuration."""
from copy import deepcopy as _dcopy


def get_dict():
    """Return configuration type dictionary."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict)
    }
    return _dict


# TS Orbit:
#   -First bpm in the list is the first seen by the beam during injection
#   -Units: um (micrometer)
#
_template_dict = {
    'pvs': [
        ['TB-01:PS-CH-1:PwrState-Sel', 0],
        ['TB-01:PS-CH-2:PwrState-Sel', 0],
        ['TB-01:PS-CV-1:PwrState-Sel', 0],
        ['TB-01:PS-CV-2:PwrState-Sel', 0],
        ['TB-01:PS-QD1:PwrState-Sel', 0],
        ['TB-01:PS-QF1:PwrState-Sel', 0],
        ['TB-02:PS-CH-1:PwrState-Sel', 0],
        ['TB-02:PS-CH-2:PwrState-Sel', 0],
        ['TB-02:PS-CV-1:PwrState-Sel', 0],
        ['TB-02:PS-CV-2:PwrState-Sel', 0],
        ['TB-02:PS-QD2A:PwrState-Sel', 0],
        ['TB-02:PS-QD2B:PwrState-Sel', 0],
        ['TB-03:PS-QD3:PwrState-Sel', 0],
        ['TB-03:PS-QF3:PwrState-Sel', 0],
        ['TB-04:PS-CH:PwrState-Sel', 0],
        ['TB-04:PS-CV-1:PwrState-Sel', 0],
        ['TB-04:PS-CV-2:PwrState-Sel', 0],
        ['TB-04:PS-QD4:PwrState-Sel', 0],
        ['TB-04:PS-QF4:PwrState-Sel', 0],
        ['TB-Fam:PS-B:PwrState-Sel', 0],
        ['TB-01:PS-CH-1:Current-SP', 0.0],
        ['TB-01:PS-CH-2:Current-SP', 0.0],
        ['TB-01:PS-CV-1:Current-SP', 0.0],
        ['TB-01:PS-CV-2:Current-SP', 0.0],
        ['TB-01:PS-QD1:Current-SP', 0.0],
        ['TB-01:PS-QF1:Current-SP', 0.0],
        ['TB-02:PS-CH-1:Current-SP', 0.0],
        ['TB-02:PS-CH-2:Current-SP', 0.0],
        ['TB-02:PS-CV-1:Current-SP', 0.0],
        ['TB-02:PS-CV-2:Current-SP', 0.0],
        ['TB-02:PS-QD2A:Current-SP', 0.0],
        ['TB-02:PS-QD2B:Current-SP', 0.0],
        ['TB-02:PS-QF2A:PwrState-Sel', 0],
        ['TB-02:PS-QF2A:Current-SP', 0.0],
        ['TB-02:PS-QF2B:PwrState-Sel', 0],
        ['TB-02:PS-QF2B:Current-SP', 0.0],
        ['TB-03:PS-QD3:Current-SP', 0.0],
        ['TB-03:PS-QF3:Current-SP', 0.0],
        ['TB-04:PS-CH:Current-SP', 0.0],
        ['TB-04:PS-CV-1:Current-SP', 0.0],
        ['TB-04:PS-CV-2:Current-SP', 0.0],
        ['TB-04:PS-QD4:Current-SP', 0.0],
        ['TB-04:PS-QF4:Current-SP', 0.0],
        ['TB-Fam:PS-B:Current-SP', 0.0],
    ]
}
