"""BSMP entities definitions for the power supply devices."""


from siriuspy.bsmp import __version__ as __bsmp_version__
from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.csdevice.pwrsupply import ps_soft_interlock as _ps_soft_interlock
from siriuspy.csdevice.pwrsupply import ps_hard_interlock as _ps_hard_interlock


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

    # --- variables groups ---
    group_id = 3


class StreamChecksum:
    """Methods to include and verify stream checksum."""

    @staticmethod
    def includeChecksum(stream):
        """Return stream with checksum byte at end of message."""
        counter = 0
        i = 0
        while (i < len(stream)):
            counter += ord(stream[i])
            i += 1
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        return(stream + [chr(counter)])

    @staticmethod
    def _verifyChecksum(stream):
        """Verify stream checksum."""
        counter = 0
        i = 0
        while (i < len(stream) - 1):
            counter += ord(stream[i])
            i += 1
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        if (stream[len(stream) - 1] == chr(counter)):
            return(True)
        else:
            return(False)


class _Interlock:
    """Interlock class."""

    @property
    def labels(self):
        """Return list of all interlock labels."""
        return [interlock for interlock in self._labels]

    def label(self, i):
        """Convert bit index to its interlock label."""
        return self._labels[i]

    def interlock_set(self, interlock):
        """Return a list of active interlocks."""
        interlock_list = []
        for i in range(len(self.labels)):
            label = self.label(i)
            if interlock & (1 << i):
                interlock_list.append(label)
        return interlock_list

    def _init(self):
        # set properties corresponding to interlock bit labels.
        for i in range(len(self.labels)):
            label = self.label(i)
            setattr(_Interlock, 'bit_' + label, 1 << i)


class _InterlockSoft(_Interlock):
    """Power supply soft iterlocks."""

    def __init__(self):
        self._labels = _ps_soft_interlock
        self._init()


class _InterlockHard(_Interlock):
    """Power supply hard iterlocks."""

    def __init__(self):
        self._labels = _ps_hard_interlock
        self._init()


class BSMPStream():
    """Class to process BSMP streams."""

    @staticmethod
    def process(stream):
        """Process BSMP stream."""
        ID_receiver, ID_cmd, load_size, load = _BSMP.parse_stream(stream)


# the following variables can be used to manipulate interlock bits.
InterlockSoft = _InterlockSoft()
InterlockHard = _InterlockHard()


def get_variables_common():
    """Return common power supply BSMP variables."""
    variables = {
        # Const.frmware_version: ('frmware_version',
        #                         Const.t_uint16, False),
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
