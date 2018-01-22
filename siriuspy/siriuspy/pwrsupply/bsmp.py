"""BSMP entities definitions for the power supply devices."""


from siriuspy.bsmp import __version__ as __bsmp_version__


class Const:
    """Power supply BSMP constants."""

    # --- implemented protocol version ---
    version = __bsmp_version__

    # --- types ---
    t_status = 0
    t_state = 1
    t_remote = 2
    t_model = 3
    t_float = 4
    t_uint8 = 5
    t_uint16 = 6
    t_uint32 = 7

    # --- common variables ---
    ps_status = 0
    ps_setpoint = 1
    ps_reference = 2
    frmware_version = 3  # a new PS definition will eventually implement this.

    # --- FSB variables ---
    ps_soft_interlocks = 25  # BSMP def says ID numbering should be continous!
    ps_hard_interlocks = 26
    i_load = 27
    v_load = 28
    v_dclink = 29
    temp_switches = 30

    # --- functions ---
    turn_on = 0
    turn_off = 1
    open_loop = 2
    close_loop = 3
    reset_interlocks = 6
    cfg_op_mode = 12
    set_slowref = 16


def get_variables_common():
    """Return common power supply BSMP variables."""
    variables = {
        Const.frmware_version: ('frmware_version',
                                Const.t_uint16, False),
        Const.ps_status: ('ps_status', Const.t_status, False),
        Const.ps_setpoint: ('ps_setpoint', Const.t_float, False),
        Const.ps_reference: ('ps_reference', Const.t_float, False),
    }
    return variables


def get_variables_FBP():
    """Return FBP power supply BSMP variables."""
    variables = get_variables_common()
    variables.update({
        Const.ps_soft_interlocks:
            ('ps_soft_interlocks', Const.t_uint16, False),
        Const.ps_hard_interlocks:
            ('ps_hard_interlocks', Const.t_uint16, False),
        Const.i_load:
            ('i_load', Const.t_float, False),
        Const.v_load:
            ('v_load', Const.t_float, False),
        Const.v_dclink:
            ('v_dclink', Const.t_float, False),
        Const.temp_switches:
            ('temp_switches', Const.t_float, False),
    })
    return variables


def get_functions():
    """Return power supply BSMP functions."""
    functions = {
        Const.turn_on: ('turn_on', Const.t_uint8, []),
        Const.turn_off: ('turn_off', Const.t_uint8, []),
        Const.open_loop: ('open_loop', Const.t_uint8, []),
        Const.close_loop: ('close_loop', Const.t_uint8, []),
        Const.cfg_op_mode:
            ('cfg_op_mode', Const.t_uint8, [Const.t_state]),
        Const.reset_interlocks:
            ('reset_interlocks', Const.t_uint8, []),
        Const.set_slowref:
            ('set_slowref', Const.t_uint8, [Const.t_float]),
    }
    return functions


def get_value_from_load(variables, ID_variable, load):
    """Build variable value from message load."""
    var_name, var_typ, var_writable = variables[ID_variable]
    if var_typ == Const.t_uint16:
        value = load[0] + (load[1] << 8)
    else:
        raise NotImplementedError
    return value
