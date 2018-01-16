"""Power Supply BSMP implementation."""

# from siriuspy.bsmp import BSMPVariable as _BSMPVariable
# from siriuspy.bsmp import BSMPFunction as _BSMPFunction
from siriuspy.bsmp import BSMPDevice as _BSMPDevice
from siriuspy.pwrsupply.status import Status as _Status
from siriuspy.csdevice.pwrsupply import Const as _PSConst


class Const:
    """Power supply BSMP constants."""

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
    # --- FSB variables ---
    ps_soft_interlocks = 25
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


class SerialComm(_BSMPDevice):
    """Master BSMP device for FBP power supplies."""

    def __init__(self, slaves=None):
        """Init method."""
        _BSMPDevice.__init__(self,
                             variables=get_variables_FBP(),
                             functions=get_functions(),
                             ID_device=None,
                             slaves=slaves)

        # serial line mode
        self._sync_mode = False

        # create group for all variables.
        IDs_variable = tuple(self.variables.keys())
        self.cmd_0x30(IDs_variable=IDs_variable)

        # Implement threaded queue as in IOC.py


class SlaveSim(_BSMPDevice):
    """Simulated BSMP slave device for power supplies."""

    def __init__(self, ID_device):
        """Init method."""
        _BSMPDevice.__init__(self,
                             variables=get_variables_FBP(),
                             functions=get_functions(),
                             ID_device=ID_device)

        self._init_state()

    def _init_state(self):
        self._state = {}
        for ID_variable, variable in self.variables.items():
            name, type_t, writable = variable
            if type_t == Const.t_float:
                value = 0.0
            elif type_t in (Const.t_status,
                            Const.t_state,
                            Const.t_remote,
                            Const.t_model,
                            Const.t_uint8,
                            Const.t_uint16,
                            Const.t_uint32):
                value = 0
            else:
                raise ValueError('Invalid BSMP variable type!')
            self._state[ID_variable] = value

    def ack_0x10(self, ID_variable):
        """Read variable identified by its ID."""
        return self._state[ID_variable]

    def ack_0x12(self, ID_group):
        """Read group variables identified by its ID (slave)."""
        IDs_variable = self._groups[ID_group]
        data = {}
        for ID_variable in IDs_variable:
            data[ID_variable] = self._state[ID_variable]
        return data

    def ack_0x50(self, ID_function, **kwargs):
        """Slave response to function execution."""
        if ID_function == Const.turn_on:
            status = self._state[Const.ps_status]
            status = _Status.set_state(status, _PSConst.States.SlowRef)
            self._state[Const.ps_status] = status
        elif ID_function == Const.turn_off:
            status = self._state[Const.ps_status]
            status = _Status.set_state(status, _PSConst.States.Off)
            self._state[Const.ps_status] = status
        else:
            raise NotImplementedError


class SlaveRS485(_BSMPDevice):
    """Transport layer to interact with BSMP slave device through RS485."""

    def __init__(ID_device):
        """Init method."""
        _BSMPDevice.__init__(variables=get_variables_FBP(),
                             functions=get_functions(),
                             ID_device=ID_device)
