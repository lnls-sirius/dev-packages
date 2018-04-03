"""Module for definitions of BSMP entities of power supply devices."""


import struct as _struct

from siriuspy.bsmp import __version__ as __bsmp_version__
from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.bsmp import Const as _ack
from siriuspy.bsmp import BSMPResponse as _BSMPResponse
# from siriuspy.csdevice.pwrsupply import ps_models as _ps_models
# from siriuspy.csdevice.pwrsupply import ps_interface as _ps_interface
# from siriuspy.csdevice.pwrsupply import ps_openloop as _ps_openloop
# from siriuspy.csdevice.pwrsupply import ps_states as _ps_states
from siriuspy.csdevice.pwrsupply import ps_pwrstate_sel as _ps_pwrstate_sel
from siriuspy.csdevice.pwrsupply import ps_opmode as _ps_opmode
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.pwrsupply import ps_soft_interlock_FBP as \
    _ps_soft_interlock_FBP
from siriuspy.csdevice.pwrsupply import ps_hard_interlock_FBP as \
    _ps_hard_interlock_FBP


class Const:
    """Namespace for organizing power supply BSMP constants."""

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
    t_char128 = 8
    t_float4 = 9
    t_param = 10
    t_float12 = 11
    t_dspclass = 12
    t_none = 13

    # --- common variables ---
    ps_status = 0
    ps_setpoint = 1  # corresponds to IOC Current-RB
    ps_reference = 2  # corresponds to IOC CurrentRef-Mon
    firmware_version = 3
    counter_set_slowref = 4
    counter_sync_pulse = 5
    siggen_enable = 6
    siggen_type = 7
    siggen_num_cycles = 8
    siggen_n = 9
    siggen_freq = 10
    siggen_amplitude = 11
    siggen_offset = 12
    siggen_aux_param = 13

    # --- FSB variables ---
    ps_soft_interlocks = 25  # BSMP doc says ID numbering should be continous!
    ps_hard_interlocks = 26
    i_load = 27  # corresponds to IOC Current-Mon
    v_load = 28
    v_dclink = 29
    temp_switches = 30

    # --- functions ---
    turn_on = 0
    turn_off = 1
    open_loop = 2
    close_loop = 3
    select_op_mode = 4
    reset_interlocks = 6
    set_serial_termination = 9  # --- NOT IMPLEMENTED YET ---
    sync_pulse = 15  # --- NOT IMPLEMENTED YET ---
    set_slowref = 16
    set_slowref_fbp = 17  # --- NOT IMPLEMENTED YET ---
    reset_counters = 18
    cfg_siggen = 23
    set_siggen = 24  # --- NOT IMPLEMENTED YET ---
    enable_siggen = 25
    disable_siggen = 26
    set_slowref_readback = 27  # --- NOT IMPLEMENTED YET ---
    set_slowref_fbp_readback = 28  # --- NOT IMPLEMENTED YET ---
    set_param = 29  # --- NOT IMPLEMENTED YET ---
    get_param = 30  # --- NOT IMPLEMENTED YET ---
    save_param_eeprom = 31  # --- NOT IMPLEMENTED YET ---
    load_param_eeprom = 32  # --- NOT IMPLEMENTED YET ---
    save_param_bank = 33  # --- NOT IMPLEMENTED YET ---
    load_param_bank = 34  # --- NOT IMPLEMENTED YET ---
    set_dsp_coeffs = 35  # --- NOT IMPLEMENTED YET ---
    get_dsp_coeff = 36  # --- NOT IMPLEMENTED YET ---
    save_dsp_coeffs_eeprom = 37  # --- NOT IMPLEMENTED YET ---
    load_dsp_coeffs_eeprom = 38  # --- NOT IMPLEMENTED YET ---
    save_dsp_modules_eeprom = 39  # --- NOT IMPLEMENTED YET ---
    load_dsp_modules_eeprom = 40  # --- NOT IMPLEMENTED YET ---
    reset_udc = 41  # --- NOT IMPLEMENTED YET ---

    # --- variables groups ---
    group_id = 3  # default variables group ID defined for power supplies


def get_variables_common():
    """Return common power supply BSMP variables."""
    variables = {
        # key (variable index): (variable name, variable type, writeable?)
        Const.ps_status:
            ('ps_status', Const.t_status, False),
        Const.ps_setpoint:
            ('ps_setpoint', Const.t_float, False),
        Const.ps_reference:
            ('ps_reference', Const.t_float, False),
        Const.firmware_version:
            ('firmware_version', Const.t_char128, False),
        Const.counter_set_slowref:
            ('counter_set_slowref', Const.t_uint32, False),
        Const.counter_sync_pulse:
            ('counter_sync_pulse', Const.t_uint32, False),
        Const.siggen_enable:
            ('siggen_enable', Const.t_uint16, False),
        Const.siggen_type:
            ('siggen_type', Const.t_uint16, False),
        Const.siggen_num_cycles:
            ('siggen_num_cycles', Const.t_uint16, False),
        Const.siggen_n:
            ('siggen_n', Const.t_float, False),
        Const.siggen_freq:
            ('siggen_freq', Const.t_float, False),
        Const.siggen_amplitude:
            ('siggen_amplitude', Const.t_float, False),
        Const.siggen_offset:
            ('siggen_offset', Const.t_float, False),
        Const.siggen_aux_param:
            ('siggen_aux_param', Const.t_float4, False),
    }
    return variables


def get_variables_FBP():
    """Return FBP power supply BSMP variables."""
    variables = get_variables_common()
    variables.update({
        Const.ps_soft_interlocks:
            ('ps_soft_interlocks', Const.t_uint32, False),
        Const.ps_hard_interlocks:
            ('ps_hard_interlocks', Const.t_uint32, False),
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
        Const.turn_on:
            ('turn_on', Const.t_uint8, []),
        Const.turn_off:
            ('turn_off', Const.t_uint8, []),
        Const.open_loop:
            ('open_loop', Const.t_uint8, []),
        Const.close_loop:
            ('close_loop', Const.t_uint8, []),
        Const.select_op_mode:
            ('select_op_mode', Const.t_uint8, [Const.t_state]),
        Const.reset_interlocks:
            ('reset_interlocks', Const.t_uint8, []),
        Const.set_serial_termination:
            ('set_serial_termination', Const.t_uint8, [Const.t_uint16]),
        Const.sync_pulse:
            ('sync_pulse', Const.t_uint8, []),
        Const.set_slowref:
            ('set_slowref', Const.t_uint8, [Const.t_float]),
        Const.set_slowref_fbp:
            ('set_slowref_fbp', Const.t_uint8,
             [Const.t_float, Const.t_float, Const.t_float, Const.t_float, ]),
        Const.reset_counters:
            ('reset_counters', Const.t_uint8, []),
        Const.cfg_siggen:
            ('cfg_siggen', Const.t_uint8,
             [Const.t_uint8, Const.t_uint16,
              Const.t_float, Const.t_float, Const.t_float, Const.t_float,
              Const.t_float, Const.t_float, Const.t_float]),
        Const.set_siggen:
            ('set_siggen', Const.t_uint8,
             [Const.t_float, Const.t_float, Const.t_float]),
        Const.enable_siggen:
            ('enable_siggen', Const.t_uint8, []),
        Const.disable_siggen:
            ('disble_siggen', Const.t_uint8, []),
        Const.set_slowref_readback:
            ('set_slowref_readback', Const.t_uint8, [Const.t_float]),
        Const.set_slowref_fbp_readback:
            ('set_slowref_fbp_readback', Const.t_uint8,
             [Const.t_float, Const.t_float, Const.t_float, Const.t_float]),
        Const.set_param:
            ('set_param', Const.t_uint8,
             [Const.t_param, Const.t_uint16, Const.t_float]),
        Const.get_param:
            ('get_param', Const.t_float, [Const.t_param, Const.t_uint16]),
        Const.save_param_eeprom:
            ('save_param_eeprom', Const.t_uint8,
             [Const.t_param, Const.t_uint16]),
        Const.load_param_eeprom:
            ('load_param_eeprom', Const.t_uint8,
             [Const.t_param, Const.t_uint16]),
        Const.save_param_bank:
            ('save_param_bank', Const.t_uint8, []),
        Const.load_param_bank:
            ('load_param_bank', Const.t_uint8, []),
        Const.set_dsp_coeffs:
            ('set_dsp_coeffs', Const.t_uint8,
             [Const.t_dspclass, Const.t_uint16, Const.t_float12]),
        Const.get_dsp_coeff:
            ('get_dsp_coeff', Const.t_uint8,
             [Const.t_dspclass, Const.t_uint16, Const.t_float]),
        Const.get_dsp_coeff:
            ('get_dsp_coeff', Const.t_uint8,
             [Const.t_dspclass, Const.t_uint16, Const.t_float]),
        Const.save_dsp_coeffs_eeprom:
            ('save_dsp_coeffs_eeprom', Const.t_uint8,
             [Const.t_dspclass, Const.t_uint16]),
        Const.load_dsp_coeffs_eeprom:
            ('load_dsp_coeffs_eeprom', Const.t_uint8,
             [Const.t_dspclass, Const.t_uint16]),
        Const.save_dsp_modules_eeprom:
            ('save_dsp_modules_eeprom', Const.t_uint8, []),
        Const.load_dsp_modules_eeprom:
            ('load_dsp_modules_eeprom', Const.t_uint8, []),
        Const.reset_udc:
            ('reset_udc', Const.t_none, []),

    }
    return functions


# def get_value_from_load(variables, ID_variable, load):
#     """Build variable value from message load."""
#     var_name, var_typ, var_writable = variables[ID_variable]
#     if var_typ == Const.t_uint16:
#         value = load[0] + (load[1] << 8)
#     else:
#         raise NotImplementedError
#     return value


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


class BSMPStream():
    """Class to process BSMP streams."""

    # --- not used yet! ---
    @staticmethod
    def process(stream):
        """Process BSMP stream."""
        ID_receiver, ID_cmd, load_size, load = _BSMP.parse_stream(stream)


# --- not used yet! ---

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
        self._labels = _ps_soft_interlock_FBP
        self._init()


class _InterlockHard(_Interlock):
    """Power supply hard iterlocks."""

    def __init__(self):
        self._labels = _ps_hard_interlock_FBP
        self._init()


# the following variables can be used to manipulate interlock bits.
InterlockSoft = _InterlockSoft()
InterlockHard = _InterlockHard()


class PSCStatus:
    """PS controller ps_status."""

    _mask_state = 0b0000000000001111
    _mask_oloop = 0b0000000000010000
    _mask_intfc = 0b0000000001100000
    _mask_activ = 0b0000000010000000
    _mask_model = 0b0001111100000000
    _mask_unlck = 0b0010000000000000
    _mask_rsrvd = 0b1100000000000000
    _mask_stats = 0b1111111111111111

    _psc2ioc_state = {
        _PSConst.States.Off: _PSConst.OpMode.SlowRef,
        _PSConst.States.Interlock: _PSConst.OpMode.SlowRef,
        _PSConst.States.Initializing: _PSConst.OpMode.SlowRef,
        _PSConst.States.SlowRef: _PSConst.OpMode.SlowRef,
        _PSConst.States.SlowRefSync: _PSConst.OpMode.SlowRefSync,
        _PSConst.States.Cycle: _PSConst.OpMode.Cycle,
        _PSConst.States.RmpWfm: _PSConst.OpMode.RmpWfm,
        _PSConst.States.MigWfm: _PSConst.OpMode.MigWfm,
        _PSConst.States.FastRef: _PSConst.OpMode.FastRef,
    }

    _ioc2psc_state = {
        # TODO: controller firmware still defines only a subset of opmodes
        _PSConst.OpMode.SlowRef: _PSConst.States.SlowRef,
        _PSConst.OpMode.SlowRefSync: _PSConst.States.SlowRefSync,
        _PSConst.OpMode.Cycle: _PSConst.States.Cycle,
        _PSConst.OpMode.RmpWfm: _PSConst.States.SlowRef,
        _PSConst.OpMode.MigWfm: _PSConst.States.SlowRef,
        _PSConst.OpMode.FastRef: _PSConst.States.SlowRef,
    }

    def __init__(self, ps_status=0):
        """Constructor."""
        self._ps_status = ps_status

    # --- public interface ---

    @property
    def ps_status(self):
        """Return ps-controller ps_status."""
        return self._ps_status

    @ps_status.setter
    def ps_status(self, value):
        """Set ps-controller ps_status."""
        self._ps_status = value & PSCStatus._mask_stats

    @property
    def state(self):
        """Return ps-controller state."""
        return (self._ps_status & PSCStatus._mask_state) >> 0

    @state.setter
    def state(self, value):
        """Set ps-controller state."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_state
        self._ps_status += (value & 0b1111) << 0

    @property
    def open_loop(self):
        """Return ps-controller open_loop."""
        return (self._ps_status & PSCStatus._mask_oloop) >> 4

    @open_loop.setter
    def open_loop(self, value):
        """Set ps-controller open_loop."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_oloop
        self._ps_status += (value & 0b1) << 4

    @property
    def interface(self):
        """Return ps-controller interface."""
        return (self._ps_status & PSCStatus._mask_intfc) >> 5

    @interface.setter
    def interface(self, value):
        """Set ps-controller interface."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_intfc
        self._ps_status += (value & 0b11) << 5

    @property
    def active(self):
        """Return ps-controller active."""
        return (self._ps_status & PSCStatus._mask_activ) >> 7

    @active.setter
    def active(self, value):
        """Set ps-controller active."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_activ
        self._ps_status += (value & 0b1) << 7

    @property
    def model(self):
        """Return ps-controller model."""
        return (self._ps_status & PSCStatus._mask_model) >> 8

    @model.setter
    def model(self, value):
        """Set ps-controller interface."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_model
        self._ps_status += (value & 0b11111) << 8

    @property
    def unlocked(self):
        """Return ps-controller unlocked."""
        return (self._ps_status & PSCStatus._mask_unlck) >> 13

    @unlocked.setter
    def unlocked(self, value):
        """Set ps-controller unlocked."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_unlck
        self._ps_status += (value & 0b1) << 13

    @property
    def reserved(self):
        """Return ps-controller reserved."""
        return (self._ps_status & PSCStatus._mask_rsrvd) >> 14

    @reserved.setter
    def reserved(self, value):
        """Set ps-controller reserved."""
        self._ps_status = self._ps_status & ~PSCStatus._mask_rsrvd
        self._ps_status += (value & 0b11) << 14

    @property
    def ioc_pwrstate(self):
        """Return ioc-controller power state."""
        state = self.state
        if state in (_PSConst.States.Off,
                     _PSConst.States.Interlock):
            pwrstate = _PSConst.PwrState.Off
        else:
            pwrstate = _PSConst.PwrState.On
        return pwrstate

    @ioc_pwrstate.setter
    def ioc_pwrstate(self, value):
        """Set ps_status with a given ioc-controller power state."""
        if not (0 <= value < len(_ps_pwrstate_sel)):
            raise ValueError('Invalid pwrstate value!')
        # TurnOn sets Opmode to SlowRef by default.
        state = _PSConst.States.Off if value == _PSConst.PwrState.Off else \
            _PSConst.States.SlowRef
        self.state = state

    @property
    def ioc_opmode(self):
        """Return ioc-controller opmode."""
        state = self.state
        opmode = PSCStatus._psc2ioc_state[state]
        return opmode

    @ioc_opmode.setter
    def ioc_opmode(self, value):
        """Set ps_status with a given ioc-controller opmode."""
        if not (0 <= value < len(_ps_opmode)):
            raise ValueError('Invalid opmode value!')
        state = PSCStatus._ioc2psc_state[value]
        self.state = state


class BSMPMasterSlaveSim(_BSMPResponse):
    """Class used to perform BSMP comm between a master and simulated slave."""

    def __init__(self, ID_device, pscontroller):
        """Init method."""
        _BSMPResponse.__init__(self,
                               variables=get_variables_FBP(),
                               functions=get_functions(),
                               ID_device=ID_device)
        self._pscontroller = pscontroller

    def create_group(self, ID_receiver, ID_group, IDs_variable):
        """Create group of BSMP variables."""
        self._groups[ID_group] = IDs_variable[:]
        return _ack.ok, None

    def remove_groups(self, ID_receiver):
        """Delete all groups of BSMP variables."""
        self._groups = {}
        return _ack.ok, None

    def cmd_0x01(self, ID_receiver):
        """Respond BSMP protocol version."""
        return _ack.ok, Const.version

    def cmd_0x11(self, ID_receiver, ID_variable):
        """Respond BSMP variable."""
        if ID_variable not in self._variables.keys():
            return _ack.invalid_id, None
        return _ack.ok, self._pscontroller[ID_variable]

    def cmd_0x13(self, ID_receiver, ID_group):
        """Respond SBMP variable group."""
        if ID_group not in self._groups:
            return _ack.invalid_id, None
        IDs_variable = self._groups[ID_group]
        load = {}
        for ID_variable in IDs_variable:
            # check if variable value copying is needed!
            load[ID_variable] = self._pscontroller[ID_variable]
        return _ack.ok, load

    def cmd_0x51(self, ID_receiver, **kwargs):
        """Respond to execute BSMP function."""
        # ID_function = kwargs['ID_function']
        return self._pscontroller.exec_function(**kwargs)


class BSMPMasterSlave(_BSMPResponse, StreamChecksum):
    """Class used to perform BSMP comm between a master and slave."""

    ver_labels = ('udc_arm', 'udc_c28', 'hradc0_cpld', 'hradc1_cpld',
                  'hradc2_cpld', 'hradc3_cpld', 'iib_arm', 'ihm_pic')

    def __init__(self, ID_device, PRU):
        """Init method."""
        _BSMPResponse.__init__(self,
                               variables=get_variables_FBP(),
                               functions=get_functions(),
                               ID_device=ID_device)

        self._pru = PRU

    def create_group(self, ID_receiver, ID_group, IDs_variable):
        """Create group of BSMP variables."""
        n = len(IDs_variable)
        hb, lb = (n & 0xFF00) >> 8, n & 0xFF
        query = [chr(ID_receiver), "\x30", chr(hb), chr(lb)] + \
            [chr(ID_variable) for ID_variable in IDs_variable]
        # print('ID_receiver: ', ID_receiver)
        # print('ID_group: ', ID_group)
        # print('IDs_variable:', IDs_variable)
        # print('query: ', query)
        query = BSMPMasterSlave.includeChecksum(query)
        self._pru.UART_write(query, timeout=100)
        response = self._pru.UART_read()
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        return ID_cmd, None

    def remove_groups(self, ID_receiver):
        """Delete all groups of BSMP variables."""
        query = [chr(ID_receiver), "\x32", '\x00', '\x00']
        query = BSMPMasterSlave.includeChecksum(query)
        self._pru.UART_write(query, timeout=100)
        response = self._pru.UART_read()
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        return ID_cmd, None

    def cmd_0x01(self, ID_receiver):
        """Respond BSMP protocol version."""
        query = [chr(ID_receiver), "\x00", "\x00", "\x00"]
        query = BSMPMasterSlave.includeChecksum(query)
        self._pru.UART_write(query, timeout=100)
        response = self._pru.UART_read()
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        if len(load) != 3:
            return _ack.invalid_message, None
        version_str = '.'.join([str(ord(c)) for c in load])
        return ID_cmd, version_str

    def cmd_0x11(self, ID_receiver, ID_variable):
        """Respond BSMP variable readout."""
        # query power supply
        query = [chr(ID_receiver),
                 '\x10', '\x00', '\x01', chr(ID_variable)]
        query = BSMPMasterSlave.includeChecksum(query)
        # TODO: move timeout value for a more visible location
        self._pru.UART_write(query, timeout=10)  # 10 or 100 for timeout?
        response = self._pru.UART_read()
        # process response
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        # TODO: implement response to variable readout
        raise NotImplementedError('cmd_0x11 not implemented!')
        # return ID_cmd, value

    def cmd_0x13(self, ID_receiver, ID_group):
        """Respond SBMP variable group read command."""
        # query power supply
        query = [chr(ID_receiver), '\x12', '\x00', '\x01', chr(ID_group)]
        query = BSMPMasterSlave.includeChecksum(query)
        # TODO: move timeout value for a more visible location
        self._pru.UART_write(query, timeout=10)
        response = self._pru.UART_read()
        # print('ID_receiver: ', ID_receiver)
        # print('ID_group: ', ID_group)
        # print('response: ', response)
        # process response
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        # print(ID_receiver, ID_cmd, load_size, load)
        if ID_cmd != 0x13:
            return ID_cmd, None
        if ID_group == Const.group_id:
            data = [ord(element) for element in load]
            value = dict()
            i = 0
            # ID:00 - ps_status
            datum = _struct.unpack("<H", bytes(data[i:i+2]))[0]
            value[Const.ps_status] = datum
            i += 2
            # ID:01 - ps_setpoint
            datum = _struct.unpack("<f", bytes(data[i:i+4]))[0]
            value[Const.ps_setpoint] = datum
            i += 4
            # ID:02 - ps_reference
            datum = _struct.unpack("<f", bytes(data[i:i+4]))[0]
            value[Const.ps_reference] = datum
            i += 4
            # ID:03 - firmware_version
            version, di = BSMPMasterSlave._process_firmware_stream(data, i)
            value[Const.firmware_version] = version
            i += di
            # ID:04 - counter_set_slowref
            datum = _struct.unpack("<I", bytes(data[i:i+4]))[0]
            value[Const.counter_set_slowref] = datum
            i += 4
            # ID:05 - counter_sync_pulse
            datum = _struct.unpack("<I", bytes(data[i:i+4]))[0]
            value[Const.counter_sync_pulse] = datum
            i += 4
            # print('05:', datum)
            # ID:06 - siggen_enable
            datum = _struct.unpack("<H", bytes(data[i:i+2]))[0]
            value[Const.siggen_enable] = datum
            # print('06:', datum)
            i += 2
            # ID:07 - siggen_type
            datum = _struct.unpack("<H", bytes(data[i:i+2]))[0]
            value[Const.siggen_type] = datum
            # print('07:', datum)
            i += 2
            # ID:08 - siggen_num_cycles
            datum = _struct.unpack("<H", bytes(data[i:i+2]))[0]
            value[Const.siggen_num_cycles] = datum
            # print('08:', datum)
            i += 2
            # ID:09 - siggen_n
            datum = _struct.unpack("<f", bytes(data[i:i+4]))[0]
            value[Const.siggen_n] = datum
            i += 4
            # ID:10 - siggen_freq
            datum = _struct.unpack("<f", bytes(data[i:i+4]))[0]
            value[Const.siggen_freq] = datum
            i += 4
            # ID:11 - siggen_amplitue
            datum = _struct.unpack("<f", bytes(data[i:i+4]))[0]
            value[Const.siggen_amplitude] = datum
            i += 4
            # ID:12 - siggen_offset
            datum = _struct.unpack("<f", bytes(data[i:i+4]))[0]
            value[Const.siggen_offset] = datum
            i += 4
            # ID:13 - siggen_aux_param
            param0 = _struct.unpack("<f", bytes(data[i+0:i+0+4]))[0]
            param1 = _struct.unpack("<f", bytes(data[i+4:i+4+4]))[0]
            param2 = _struct.unpack("<f", bytes(data[i+8:i+8+4]))[0]
            param3 = _struct.unpack("<f", bytes(data[i+12:i+12+4]))[0]
            value[Const.siggen_aux_param] = [param0, param1, param2, param3]
            i += 4*4
            # ID:25 - ps_soft_interlocks
            datum = data[i] + (data[i+1] << 8) + \
                (data[i+2] << 16) + (data[i+3] << 24)
            value[Const.ps_soft_interlocks] = datum
            i += 4
            # ID:26 - ps_hard_interlocks
            datum = data[i] + (data[i+1] << 8) + \
                (data[i+2] << 16) + (data[i+3] << 24)
            value[Const.ps_hard_interlocks] = datum
            i += 4
            # ID:27 - i_load
            datum = _struct.unpack("<f", bytes(data[i:i+4]))[0]
            value[Const.i_load] = datum
            i += 4
            # ID:28 - v_load
            datum = _struct.unpack("<f", bytes(data[i:i+4]))[0]
            value[Const.v_load] = datum
            i += 4
            # ID:29 - v_dclink
            datum = _struct.unpack("<f", bytes(data[i:i+4]))[0]
            value[Const.v_dclink] = datum
            i += 4
            # ID:30 - temp_switches
            datum = _struct.unpack("<f", bytes(data[i:i+4]))[0]
            value[Const.temp_switches] = datum
            i += 4
        else:
            raise ValueError('Invalid group ID!')
        return _ack.ok, value

    def cmd_0x51(self, ID_receiver, ID_function, **kwargs):
        """Respond to execute BSMP function."""
        # execute function in power supply
        if ID_function in (Const.turn_on,
                           Const.turn_off,
                           Const.open_loop,
                           Const.close_loop,
                           Const.reset_interlocks,
                           Const.reset_counters,
                           Const.enable_siggen,
                           Const.disable_siggen):
            load = []
        elif ID_function == Const.set_slowref:
            load = [chr(b) for b in _struct.pack("<f", kwargs['setpoint'])]
        elif ID_function == Const.select_op_mode:
            load = [chr(b) for b in _struct.pack("<H", kwargs['op_mode'])]
        elif ID_function == Const.cfg_siggen:
            load = [chr(b) for b in _struct.pack("<H", kwargs['type'])]
            load += [chr(b) for b in _struct.pack("<H", kwargs['num_cycles'])]
            load += [chr(b) for b in _struct.pack("<f", kwargs['freq'])]
            load += [chr(b) for b in _struct.pack("<f", kwargs['amplitude'])]
            load += [chr(b) for b in _struct.pack("<f", kwargs['offset'])]
            load += [chr(b) for b in _struct.pack("<f", kwargs['aux_param0'])]
            load += [chr(b) for b in _struct.pack("<f", kwargs['aux_param1'])]
            load += [chr(b) for b in _struct.pack("<f", kwargs['aux_param2'])]
            load += [chr(b) for b in _struct.pack("<f", kwargs['aux_param3'])]
        else:
            raise NotImplementedError
        n = 1 + len(load)  # one additional byte for checksum.
        hb, lb = (n & 0xFF00) >> 8, n & 0xFF
        query = [chr(ID_receiver), '\x50', chr(hb), chr(lb),
                 chr(ID_function)] + load
        # if ID_function == Const.select_op_mode:
        #     print([hex(ord(c)) for c in query])
        query = BSMPMasterSlave.includeChecksum(query)
        # print('cmd_0x51: ', n, query)
        # TODO: check this timeout. eventually will be part of the BSMP PS spec
        self._pru.UART_write(query, timeout=100)
        response = self._pru.UART_read()
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        if ID_cmd != 0x51:
            # currently ps slaves are returning 0x53 sometimes !!!
            # print('anomalous response!')
            # print('query    : ', [hex(ord(c)) for c in query])
            # print('response : ', [hex(ord(c)) for c in response])
            pass
        return _ack.ok, None

    # --- private aux. methods ---

    @staticmethod
    def _process_firmware_stream(data, i):

        version = ''
        first_ok = False

        # udc_arm
        version, i, first_ok = \
            BSMPMasterSlave._process_firmware_stream_substring(
                data, version, i, first_ok, 0)
        # TODO: uncomment the rest of this method once Version-Cte has been
        # modifed to an array of chars (epics strings PVs are limited to
        # 40 chars in length!)

        # # udc_c28
        # version, i, first_ok = \
        #     BSMPMasterSlave._process_firmware_stream_substring(
        #         data, version, i, first_ok, 1)
        # # hradc0_cpld
        # version, i, first_ok = \
        #     BSMPMasterSlave._process_firmware_stream_substring(
        #         data, version, i, first_ok, 2)
        # # hradc1_cpld
        # version, i, first_ok = \
        #     BSMPMasterSlave._process_firmware_stream_substring(
        #         data, version, i, first_ok, 3)
        # # hradc2_cpld
        # version, i, first_ok = \
        #     BSMPMasterSlave._process_firmware_stream_substring(
        #         data, version, i, first_ok, 4)
        # # hradc3_cpld
        # version, i, first_ok = \
        #     BSMPMasterSlave._process_firmware_stream_substring(
        #         data, version, i, first_ok, 5)
        # # iib_arm
        # version, i, first_ok = \
        #     BSMPMasterSlave._process_firmware_stream_substring(
        #         data, version, i, first_ok, 6)
        # # ihm_pic
        # version, i, first_ok = \
        #     BSMPMasterSlave._process_firmware_stream_substring(
        #         data, version, i, first_ok, 7)

        return version, 128

    @staticmethod
    def _process_firmware_stream_substring(data, version,
                                           i, first_ok, label_idx):
        if data[i] != 0:
            ver = ''.join([chr(v) for v in data[i:i+16]])
            ver = ver.replace(' ', '_')
            if first_ok:
                version += ' '
            version += BSMPMasterSlave.ver_labels[label_idx] + ':' + ver
            first_ok = True
        i += 16
        return version, i, first_ok
