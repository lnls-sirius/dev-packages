"""SI ID configuration."""
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


# When using this type of configuration to set the machine,
# the list of PVs should be processed in the same order they are stored
# in the configuration. The second numeric parameter in the pair is the
# delay [s] the client should wait before setting the next PV.

_pvs_ids = [
    ['SI-06SB:ID-APU22:MaxPhaseSpeed-SP', 0.0, 0.0],  # [mm/s]
    ['SI-07SP:ID-APU22:MaxPhaseSpeed-SP', 0.0, 0.0],  # [mm/s]
    ['SI-08SB:ID-APU22:MaxPhaseSpeed-SP', 0.0, 0.0],  # [mm/s]
    ['SI-09SA:ID-APU22:MaxPhaseSpeed-SP', 0.0, 0.0],  # [mm/s]
    ['SI-11SP:ID-APU58:MaxPhaseSpeed-SP', 0.0, 0.0],  # [mm/s]
]

_template_dict = {
    'pvs': _pvs_ids,
}
