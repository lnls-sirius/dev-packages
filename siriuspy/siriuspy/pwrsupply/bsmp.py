"""Module for definitions of BSMP entities of power supply devices."""


import struct as _struct
import random as _random

from siriuspy.bsmp import __version__ as __bsmp_version__
from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.bsmp import Const as _ack
from siriuspy.bsmp import BSMPResponse as _BSMPResponse
from siriuspy.csdevice.pwrsupply import ps_models as _ps_models
from siriuspy.csdevice.pwrsupply import ps_interface as _ps_interface
from siriuspy.csdevice.pwrsupply import ps_openloop as _ps_openloop
from siriuspy.csdevice.pwrsupply import ps_states as _ps_states
from siriuspy.csdevice.pwrsupply import ps_pwrstate_sel as _ps_pwrstate_sel
from siriuspy.csdevice.pwrsupply import ps_opmode as _ps_opmode
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.pwrsupply import ps_soft_interlock as _ps_soft_interlock
from siriuspy.csdevice.pwrsupply import ps_hard_interlock as _ps_hard_interlock


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

    # --- common variables ---
    ps_status = 0
    ps_setpoint = 1  # corresponds to IOC Current-RB
    ps_reference = 2  # corresponds to IOC CurrentRef-Mon
    firmware_version = 3  # not implemented yet
    counter_set_slowref = 4  # not implemented yet
    counter_sync_pulse = 5  # not implemented yet
    siggen_enable = 6  # not implemented yet
    siggen_type = 7  # not implemented yet
    siggen_num_cycles = 8  # not implemented yet
    siggen_n = 9  # not implemented yet
    siggen_freq = 10  # not implemented yet
    siggen_amplitude = 11  # not implemented yet
    siggen_offset = 12  # not implemented yet
    siggen_aux_param = 13  # not implemented yet

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
    set_serial_termination = 9  # not implemented yet
    sync_pulse = 15  # not implemented yet
    set_slowref = 16
    set_slowref_fbp = 17  # not implemented yet
    reset_counters = 18  # not implemented yet
    cfg_siggen = 23  # not implemented yet
    set_siggen = 24  # not implemented yet
    enable_siggen = 25  # not implemented yet
    disable_siggen = 26  # not implemented yet
    set_slowref_readback = 27  # not implemented yet
    set_slowref_fbp_readback = 28  # not implemented yet

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
        # Const.firmware_version:
        #     ('firmaware_version', Const.t_char128, False),
        # Const.counter_set_slowref:
        #     ('counter_set_slowref', Const.t_uint32, False),
        # Const.counter_sync_pulse:
        #     ('counter_sync_pulse', Const.t_uint32, False),
        # Const.siggen_enable:
        #     ('siggen_enable', Const.t_uint16, False),
        # Const.siggen_type:
        #     ('siggen_type', Const.t_uint16, False),
        # Const.siggen_num_cycles:
        #     ('siggen_num_cycles', Const.t_uint16, False),
        # Const.siggen_n:
        #     ('siggen_n', Const.t_float, False),
        # Const.siggen_freq:
        #     ('siggen_freq', Const.t_float, False),
        # Const.siggen_amplitude:
        #     ('siggen_amplitude', Const.t_float, False),
        # Const.siggen_offset:
        #     ('siggen_offset', Const.t_float, False),
        # Const.siggen_aux_param:
        #     ('siggen_aux_param', Const.t_float4, False),
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
        self._labels = _ps_soft_interlock
        self._init()


class _InterlockHard(_Interlock):
    """Power supply hard iterlocks."""

    def __init__(self):
        self._labels = _ps_hard_interlock
        self._init()


# the following variables can be used to manipulate interlock bits.
InterlockSoft = _InterlockSoft()
InterlockHard = _InterlockHard()


class Status:
    """Power supply status class."""

    _mask_state = 0b0000000000001111
    _mask_oloop = 0b0000000000010000
    _mask_intfc = 0b0000000001100000
    _mask_activ = 0b0000000010000000
    _mask_model = 0b0001111100000000
    _mask_unlck = 0b0010000000000000
    _mask_rsrvd = 0b1100000000000000

    _dsp2ps_state = {
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

    _ps2dsp_state = {
        # current PS version implements only SlowRef!
        _PSConst.OpMode.SlowRef: _PSConst.States.SlowRef,
        _PSConst.OpMode.SlowRefSync: _PSConst.States.SlowRef,
        _PSConst.OpMode.FastRef: _PSConst.States.SlowRef,
        _PSConst.OpMode.RmpWfm: _PSConst.States.SlowRef,
        _PSConst.OpMode.MigWfm: _PSConst.States.SlowRef,
        _PSConst.OpMode.Cycle: _PSConst.States.SlowRef,
    }

    @staticmethod
    def state(status, label=False):
        """Return DSP state of power supply."""
        index = (status & (0b1111 << 0)) >> 0
        return _ps_states[index] if label else index

    @staticmethod
    def set_state(status, value):
        """Set state in power supply status."""
        if not (0 <= value < len(_ps_states)):
            raise ValueError('Invalid state value!')
        status = status & ~Status._mask_state
        status += value << 0
        return status

    @staticmethod
    def pwrstate(status, label=False):
        """Return PS powerstate."""
        state = Status.state(status, label=False)
        index = _PSConst.PwrState.Off if state == _PSConst.States.Off else \
            _PSConst.PwrState.On
        return _ps_pwrstate_sel[index] if label else index

    @staticmethod
    def set_pwrstate(status, value):
        """Set pwrstate in power supply status."""
        if not (0 <= value < len(_ps_pwrstate_sel)):
            raise ValueError('Invalid pwrstate value!')
        status = status & ~Status._mask_state
        value = _PSConst.States.Off if value == _PSConst.PwrState.Off else \
            _PSConst.States.SlowRef
        status += value << 0
        return status

    @staticmethod
    def opmode(status, label=False):
        """Return PS opmode."""
        state = Status.state(status, label=False)
        index = Status._dsp2ps_state[state]
        return _ps_opmode[index] if label else index

    @staticmethod
    def set_opmode(status, value):
        """Set power supply opmode."""
        if not (0 <= value < len(_ps_opmode)):
            raise ValueError('Invalid opmode value!')
        value = Status._ps2dsp_state[value]
        status = Status.set_state(status, value)
        return status

    @staticmethod
    def openloop(status, label=False):
        """Return open-loop state index of power supply."""
        index = (status & (0b1 << 4)) >> 4
        return _ps_openloop[index] if label else index

    @staticmethod
    def set_openloop(status, value):
        """Set openloop in power supply status."""
        if not (0 <= value < len(_ps_openloop)):
            raise ValueError('Invalid openloop value!')
        status = status & ~Status._mask_oloop
        status += value << 4
        return status

    @staticmethod
    def interface(status, label=False):
        """Return interface index of power supply."""
        index = (status & (0b11 << 5)) >> 5
        return _ps_interface[index] if label else index

    @staticmethod
    def set_interface(status, value):
        """Set interface index in power supply status."""
        if not (0 <= value < len(_ps_interface)):
            raise ValueError('Invalid interface number!')
        status = status & ~Status._mask_intfc
        status += value << 5
        return status

    @staticmethod
    def active(status, label=False):
        """Return active index of power supply."""
        return (status & (0b1 << 7)) >> 7

    @staticmethod
    def set_active(status, value):
        """Set active index in power supply status."""
        if not (0 <= value <= 1):
            raise ValueError('Invalid active number!')
        status = status & ~Status._mask_activ
        status += value << 7
        return status

    @staticmethod
    def model(status, label=False):
        """Return model index for power supply."""
        index = (status & Status._mask_model) >> 8
        return _ps_models[index] if label else index

    @staticmethod
    def set_model(status, value):
        """Set model in power supply status."""
        if not (0 <= value < len(_ps_models)):
            raise ValueError('Invalid model number!')
        status = status & ~Status._mask_model
        status += value << 8
        return status

    @staticmethod
    def unlocked(status, label=False):
        """Return unlocked index for power supply."""
        return (status & (0b1 << 13)) >> 13

    @staticmethod
    def set_unlocked(status, value):
        """Set unlocked in power supply status."""
        if not (0 <= value <= 1):
            raise ValueError('Invalid unlocked number!')
        status = status & ~Status._mask_unlck
        status += value << 13
        return status


class BSMPMasterSlaveSim(_BSMPResponse):
    """Class used to perform BSMP comm between a master and simulated slave."""

    def __init__(self, ID_device, pscontroller):
        """Init method."""
        _BSMPResponse.__init__(self,
                               variables=get_variables_FBP(),
                               functions=get_functions(),
                               ID_device=ID_device)
        self._pscontroler = pscontroller

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
        return _ack.ok, self._pscontroler[ID_variable]

    def cmd_0x13(self, ID_receiver, ID_group):
        """Respond SBMP variable group."""
        if ID_group not in self._groups:
            return _ack.invalid_id, None
        IDs_variable = self._groups[ID_group]
        load = {}
        for ID_variable in IDs_variable:
            # check if variable value copying is needed!
            load[ID_variable] = self._pscontroler[ID_variable]
        return _ack.ok, load

    def cmd_0x51(self, ID_receiver, **kwargs):
        """Respond to execute BSMP function."""
        # ID_function = kwargs['ID_function']
        return self._pscontroler.exec_function(**kwargs)


class BSMPMasterSlave(_BSMPResponse, StreamChecksum):
    """Class used to perform BSMP comm between a master and slave."""

    _FAKE_FRMWARE_VERSION = ['\x00', '\x00']

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
        """Respond BSMP variable."""
        # query power supply
        if ID_variable == Const.frmware_version:
            # simulate response to firmware version
            # (This variable currently is not implemented  - see bsmp.py !!!)
            ID_master = 0
            response = [chr(ID_master), '\x11', '\x00', '\x02'] + \
                BSMPMasterSlave._FAKE_FRMWARE_VERSION
            response = BSMPMasterSlave.includeChecksum(response)
        else:
            query = [chr(ID_receiver),
                     '\x10', '\x00', '\x01', chr(ID_variable)]
            query = BSMPMasterSlave.includeChecksum(query)
            self._pru.UART_write(query, timeout=10)  # 10 or 100 for timeout?
            response = self._pru.UART_read()
        # process response
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        if ID_variable == Const.frmware_version:
            if len(load) != 2:
                return _ack.invalid_message, None
            value = get_value_from_load(self._variables, ID_variable, load)
        else:
            raise NotImplementedError(
                'This power supply cmd is not defined for this variable ID!')
        return ID_cmd, value

    def cmd_0x13(self, ID_receiver, ID_group):
        """Respond SBMP variable group."""
        # query power supply
        query = [chr(ID_receiver), '\x12', '\x00', '\x01', chr(ID_group)]
        query = BSMPMasterSlave.includeChecksum(query)
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
            value[Const.ps_status] = data[0] + (data[1] << 8)
            value[Const.ps_setpoint] = \
                _struct.unpack("<f", bytes(data[2:6]))[0]
            value[Const.ps_reference] = \
                _struct.unpack("<f", bytes(data[6:10]))[0]
            value[Const.ps_soft_interlocks] = \
                data[10] + (data[11] << 8) + \
                (data[12] << 16) + (data[13] << 24)
            value[Const.ps_hard_interlocks] = \
                data[14] + (data[15] << 8) + \
                (data[16] << 16) + (data[17] << 24)
            value[Const.i_load] = _struct.unpack("<f", bytes(data[18:22]))[0]
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
                           Const.reset_interlocks):
            load = []
        elif ID_function == Const.set_slowref:
            load = [chr(b) for b in _struct.pack("<f", kwargs['setpoint'])]
        else:
            raise NotImplementedError
        n = 1 + len(load)
        hb, lb = (n & 0xFF00) >> 8, n & 0xFF
        query = [chr(ID_receiver), '\x50', chr(hb), chr(lb),
                 chr(ID_function)] + load
        query = BSMPMasterSlave.includeChecksum(query)
        # print('cmd_0x51: ', n, query)
        self._pru.UART_write(query, timeout=100)
        response = self._pru.UART_read()
        # process response
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        if ID_cmd != 0x51:
            # currently ps slaves are returning 0x53 sometimes !!!
            # print('anomalous response!')
            # print('query    : ', [hex(ord(c)) for c in query])
            # print('response : ', [hex(ord(c)) for c in response])
            # return ID_cmd, load
            return _ack.ok, None
        return _ack.ok, None
