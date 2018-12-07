"""TB power supplies snapshot configuration."""
from copy import deepcopy as _dcopy


def get_dict():
    """Return configuration type dictionary."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict)
    }
    return _dict


# TB power supply snapshot
#
# When using this type of configuration to set the machine,
# the list of PVs should be processed in the same order they are stored
# in the configuration. The second numeric parameter in the pair is the
# delay [s] the client should wait before setting the next PV.
#
#   a) First all power supplies should be turned on,
#   b) a small delay should be introduced.
#   c) and then all currents setpoint values should be set.

_Off = 0

_template_dict = {
    'pvs': [
        ['TB-Fam:PS-B:PwrState-Sel', _Off, 0.0],
        ['TB-01:PS-QD1:PwrState-Sel', _Off, 0.0],
        ['TB-01:PS-QF1:PwrState-Sel', _Off, 0.0],
        ['TB-02:PS-QD2A:PwrState-Sel', _Off, 0.0],
        ['TB-02:PS-QF2A:PwrState-Sel', _Off, 0.0],
        ['TB-02:PS-QF2B:PwrState-Sel', _Off, 0.0],
        ['TB-02:PS-QD2B:PwrState-Sel', _Off, 0.0],
        ['TB-03:PS-QF3:PwrState-Sel', _Off, 0.0],
        ['TB-03:PS-QD3:PwrState-Sel', _Off, 0.0],
        ['TB-04:PS-QF4:PwrState-Sel', _Off, 0.0],
        ['TB-04:PS-QD4:PwrState-Sel', _Off, 0.0],
        ['TB-01:PS-CH-1:PwrState-Sel', _Off, 0.0],
        ['TB-01:PS-CV-1:PwrState-Sel', _Off, 0.0],
        ['TB-01:PS-CH-2:PwrState-Sel', _Off, 0.0],
        ['TB-01:PS-CV-2:PwrState-Sel', _Off, 0.0],
        ['TB-02:PS-CH-1:PwrState-Sel', _Off, 0.0],
        ['TB-02:PS-CV-1:PwrState-Sel', _Off, 0.0],
        ['TB-02:PS-CH-2:PwrState-Sel', _Off, 0.0],
        ['TB-02:PS-CV-2:PwrState-Sel', _Off, 0.0],
        ['TB-04:PS-CH:PwrState-Sel', _Off, 0.0],
        ['TB-04:PS-CV-1:PwrState-Sel', _Off, 0.0],
        ['TB-04:PS-CV-2:PwrState-Sel', _Off, 0.4],
        ['TB-Fam:PS-B:Current-SP', 0.0, 0.0],
        ['TB-01:PS-QD1:Current-SP', 0.0, 0.0],
        ['TB-01:PS-QF1:Current-SP', 0.0, 0.0],
        ['TB-02:PS-QD2A:Current-SP', 0.0, 0.0],
        ['TB-02:PS-QF2A:Current-SP', 0.0, 0.0],
        ['TB-02:PS-QF2B:Current-SP', 0.0, 0.0],
        ['TB-02:PS-QD2B:Current-SP', 0.0, 0.0],
        ['TB-03:PS-QF3:Current-SP', 0.0, 0.0],
        ['TB-03:PS-QD3:Current-SP', 0.0, 0.0],
        ['TB-04:PS-QF4:Current-SP', 0.0, 0.0],
        ['TB-04:PS-QD4:Current-SP', 0.0, 0.0],
        ['TB-01:PS-CH-1:Current-SP', 0.0, 0.0],
        ['TB-01:PS-CV-1:Current-SP', 0.0, 0.0],
        ['TB-01:PS-CH-2:Current-SP', 0.0, 0.0],
        ['TB-01:PS-CV-2:Current-SP', 0.0, 0.0],
        ['TB-02:PS-CH-1:Current-SP', 0.0, 0.0],
        ['TB-02:PS-CV-1:Current-SP', 0.0, 0.0],
        ['TB-02:PS-CH-2:Current-SP', 0.0, 0.0],
        ['TB-02:PS-CV-2:Current-SP', 0.0, 0.0],
        ['TB-04:PS-CH:Current-SP', 0.0, 0.0],
        ['TB-04:PS-CV-1:Current-SP', 0.0, 0.0],
        ['TB-04:PS-CV-2:Current-SP', 0.0, 0.0],
    ]
}
