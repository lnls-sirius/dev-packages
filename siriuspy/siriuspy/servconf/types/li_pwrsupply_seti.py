"""LI power supply current setpoint configuration."""
from copy import deepcopy as _dcopy


def get_dict():
    """Return configuration type dictionary."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict)
    }
    return _dict


# When using this type of configuration to set the machine,
# the list of PVs should be processed in the same order they are stored
# in the configuration. The second numeric parameter in the pair is the
# delay [s] the client should wait before setting the next PV.


_template_dict = {
    'pvs': [
        ['LA-CN:H1MLPS-1:seti', 0.0, 0.0],
        ['LA-CN:H1MLPS-2:seti', 0.0, 0.0],
        ['LA-CN:H1MLPS-3:seti', 0.0, 0.0],
        ['LA-CN:H1MLPS-4:seti', 0.0, 0.0],
        ['LA-CN:H1SCPS-1:seti', 0.0, 0.0],
        ['LA-CN:H1SCPS-2:seti', 0.0, 0.0],
        ['LA-CN:H1SCPS-3:seti', 0.0, 0.0],
        ['LA-CN:H1SCPS-4:seti', 0.0, 0.0],
        ['LA-CN:H1LCPS-1:seti', 0.0, 0.0],
        ['LA-CN:H1LCPS-2:seti', 0.0, 0.0],
        ['LA-CN:H1LCPS-3:seti', 0.0, 0.0],
        ['LA-CN:H1LCPS-4:seti', 0.0, 0.0],
        ['LA-CN:H1LCPS-5:seti', 0.0, 0.0],
        ['LA-CN:H1LCPS-6:seti', 0.0, 0.0],
        ['LA-CN:H1LCPS-7:seti', 0.0, 0.0],
        ['LA-CN:H1LCPS-8:seti', 0.0, 0.0],
        ['LA-CN:H1LCPS-9:seti', 0.0, 0.0],
        ['LA-CN:H1LCPS-10:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-1:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-2:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-3:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-4:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-5:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-6:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-7:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-8:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-9:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-10:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-11:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-12:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-13:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-14:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-15:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-16:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-17:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-18:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-19:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-20:seti', 0.0, 0.0],
        ['LA-CN:H1SLPS-21:seti', 0.0, 0.0],
        ['LA-CN:H1FQPS-1:seti', 0.0, 0.0],
        ['LA-CN:H1FQPS-2:seti', 0.0, 0.0],
        ['LA-CN:H1FQPS-3:seti', 0.0, 0.0],
        ['LA-CN:H1DQPS-1:seti', 0.0, 0.0],
        ['LA-CN:H1DQPS-2:seti', 0.0, 0.0],
        ['LA-CN:H1RCPS-1:seti', 0.0, 0.0],
        ['LA-CN:H1DPPS-1:seti', 0.0, 0.0],
    ]
}
