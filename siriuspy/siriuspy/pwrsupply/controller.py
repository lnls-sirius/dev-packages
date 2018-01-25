"""Power supply controller classes."""

import time as _time
import struct as _struct
from queue import Queue as _Queue
from threading import Thread as _Thread
import random as _random

from siriuspy import __version__
from siriuspy.csdevice.pwrsupply import ps_opmode as _ps_opmode
from siriuspy.csdevice.pwrsupply import get_common_ps_propty_database as \
    _get_common_ps_propty_database

from siriuspy.bsmp import Const as _ack
from siriuspy.bsmp import BSMPQuery as _BSMPQuery
from siriuspy.bsmp import BSMPResponse as _BSMPResponse
from siriuspy.pwrsupply.status import Status as _Status
from siriuspy.pwrsupply.bsmp import Const as _BSMPConst
from siriuspy.pwrsupply.bsmp import StreamChecksum as _StreamChecksum
from siriuspy.pwrsupply.bsmp import get_variables_FBP as _get_variables_FBP
from siriuspy.pwrsupply.bsmp import get_functions as _get_functions
from siriuspy.pwrsupply.bsmp import get_value_from_load as \
    _get_value_from_load
from siriuspy.csdevice.pwrsupply import Const as _PSConst

# Needs loading PRUserial485 package:
import PRUserial485.PRUserial485 as _PRUserial485
#_PRUserial485 = None

# loads power supply database with default initial values
_db_ps = _get_common_ps_propty_database()


class _PRUInterface:
    """Interface class for programmable real-time units."""

    def __init__(self):
        """Init method."""
        self._sync_mode = False

    # --- interface ---

    @property
    def sync_mode(self):
        """Return sync mode."""
        return self._sync_mode

    @sync_mode.setter
    def sync_mode(self, value):
        """Set sync mode."""
        self._set_sync_mode(value)
        self._sync_mode = value

    @property
    def sync_pulse_count(self):
        """Return synchronism pulse count."""
        return self._get_sync_pulse_count()

    def UART_write(self, stream, timeout):
        """Write stream to serial port."""
        return self._UART_write(stream, timeout=timeout)

    def UART_read(self):
        """Return read from UART."""
        return self._UART_read()

    # --- pure virtual method ---

    def _get_sync_pulse_count(self):
        raise NotImplementedError

    def _set_sync_mode(self, value):
        raise NotImplementedError

    def _UART_write(stream, timeout):
        raise NotImplementedError

    def _UART_read(stream):
        raise NotImplementedError


class PRUSim(_PRUInterface):
    """Functions for simulated programmable real-time unit."""

    def __init__(self):
        """Init method."""
        _PRUInterface.__init__(self)
        self._sync_pulse_count = 0

    def process_sync_signal(self):
        """Process synchronization signal."""
        self._sync_pulse_count += 1

    def _get_sync_pulse_count(self):
        return self._sync_pulse_count

    def _set_sync_mode(self, value):
        pass

    def _UART_write(self, stream, timeout):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this subclass'))

    def _UART_read(self):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this subclass'))


class PRU(_PRUInterface):
    """Functions for the programmable real-time unit."""

    def _get_sync_pulse_count(self):
        return _PRUserial485.PRUserial485_read_pulse_count_sync()

    def _get_sync_mode(self):
        return self._sync_mode

    def _set_sync_mode(self, value):
        self._sync_mode = value

    def _UART_write(self, stream, timeout):
        # this method send streams through UART to the RS-485 line.
        return _PRUserial485.PRUserial485_write(stream, timeout)

    def _UART_read(self, stream, timeout):
        # this method send streams through UART to the RS-485 line.
        return _PRUserial485.PRUserial485_read()


class PSState:
    """Power supply state.

    Objects of this class have a dictionary that stores the state of
    power supplies, as defined by its list of BSMP variables.
    """

    def __init__(self, variables):
        """Init method."""
        self._state = {}
        for ID_variable, variable in variables.items():
            name, type_t, writable = variable
            if type_t == _BSMPConst.t_float:
                value = 0.0
            elif type_t in (_BSMPConst.t_status,
                            _BSMPConst.t_state,
                            _BSMPConst.t_remote,
                            _BSMPConst.t_model,
                            _BSMPConst.t_uint8,
                            _BSMPConst.t_uint16,
                            _BSMPConst.t_uint32):
                value = 0
            else:
                raise ValueError('Invalid BSMP variable type!')
            self._state[ID_variable] = value

    def __getitem__(self, key):
        """Return value corresponfing to a certain key (ps_variable)."""
        return self._state[key]

    def __setitem__(self, key, value):
        """Set value for a certain key (ps_variable)."""
        self._state[key] = value
        return value


class SerialComm(_BSMPQuery):
    """Serial communiationMaster BSMP device for power supplies."""

    _SCAN_INTERVAL_SYNC_MODE_OFF = 0.1  # [s]
    _SCAN_INTERVAL_SYNC_MODE_ON = 1.0  # [s]

    def __init__(self, PRU, slaves=None):
        """Init method."""
        variables = _get_variables_FBP()
        _BSMPQuery.__init__(self,
                            variables=variables,
                            functions=_get_functions(),
                            slaves=slaves)
        self._PRU = PRU
        self._queue = _Queue()
        self._states = {}
        # does not start variables scanning just yet.
        self._scanning = False
        # create, configure and start auxilliary threads.
        self._thread_queue = _Thread(target=self._process_queue, daemon=True)
        self._thread_scan = _Thread(target=self._process_scan, daemon=True)
        self._thread_queue.start()
        self._thread_scan.start()

    @property
    def sync_mode(self):
        """Return sync mode of PRU."""
        return self._PRU.sync_mode

    @sync_mode.setter
    def sync_mode(self, value):
        """Set PRU sync mode."""
        self._PRU.sync_mode = value

    @property
    def sync_pulse_count(self):
        """Return synchronism pulse count."""
        return self._PRU.sync_pulse_count

    @property
    def scanning(self):
        """Return scanning state."""
        return self._scanning

    @scanning.setter
    def scanning(self, value):
        """Set scanning state."""
        self._scanning = value

    def write(self, stream, timeout):
        """Return response to a BSMP stream command through UART."""
        self._PRU.UART_write(stream, timeout)
        answer = self._PRU.UART_read()
        return answer

    def add_slave(self, slave):
        """Add slave to slave pool controlled by master BSMP device."""
        # insert slave into pool
        _BSMPQuery.add_slave(self, slave)
        # create mirrored state for slave
        self._states[slave.ID_device] = PSState(variables=self._variables)
        # init pwrsupply slave
        self._init_controller(slave)

    def put(self, ID_device, ID_cmd, kwargs):
        """Put a SBMP command request in queue."""
        # print('put :', ID_device, hex(ID_cmd), kwargs)
        self._queue.put((ID_device, ID_cmd, kwargs))

    def get_variable(self, ID_device, ID_variable):
        """Return a BSMP variable."""
        return self._states[ID_device][ID_variable]

    def _process_queue(self):
        """Process queue."""
        while True:
            item = self._queue.get()
            ID_device, ID_cmd, kwargs = item
            # print('get :', ID_device, hex(id_cmd), kwargs)
            cmd = 'cmd_' + str(hex(ID_cmd))
            method = getattr(self, cmd)
            ack, load = method(ID_receiver=ID_device, **kwargs)
            if ack != _ack.ok:
                # needs implementation
                raise NotImplementedError(
                    'Error returned in BSMP command!')
            elif load is not None:
                self._process_load(ID_device, ID_cmd, load)

    def _process_load(self, ID_device, ID_cmd, load):
        if ID_cmd == 0x12:
            for variable, value in load.items():
                self._states[ID_device][variable] = value
        else:
            err_str = 'BSMP cmd {} not implemented in process_thread!'
            raise NotImplementedError(err_str.format(hex(ID_cmd)))

    def _process_scan(self):
        """Scan power supply variables, adding puts into queue."""
        while True:
            if self._scanning:
                self._sync_counter = self._PRU.sync_pulse_count
                self._insert_variables_group_read()
            if self._PRU.sync_mode:
                # self.event.wait(1)
                _time.sleep(SerialComm._SCAN_INTERVAL_SYNC_MODE_ON)
            else:
                # self.event.wait(0.1)
                _time.sleep(SerialComm._SCAN_INTERVAL_SYNC_MODE_OFF)

    def _insert_variables_group_read(self):
        kwargs = {'ID_group': _BSMPConst.group_id}
        for ID_receiver in self._slaves:
            self.put(ID_device=ID_receiver, ID_cmd=0x12, kwargs=kwargs)

    def _init_controller(self, slave):
        # clean variable groups in slave
        kwargs = {}
        self.put(ID_device=slave.ID_device, ID_cmd=0x32, kwargs=kwargs)

        # create group of all variables in slave.
        IDs_variable = tuple(self.variables.keys())
        kwargs = {'ID_group': _BSMPConst.group_id,
                  'IDs_variable': IDs_variable}
        self.put(ID_device=slave.ID_device, ID_cmd=0x30, kwargs=kwargs)

        # these have been moved to PowerSupply:
        # ------------------------------------
        # # reset ps interlocks
        # # turn ps on
        # # close ps control loop.
        # # set slowref to zero


class BSMPResponseSim(_BSMPResponse):
    """Transport BSMP layer interacting with simulated slave device."""

    def __init__(self, ID_device, i_load_fluctuation_rms=0.0):
        """Init method."""
        _BSMPResponse.__init__(self,
                               variables=_get_variables_FBP(),
                               functions=_get_functions(),
                               ID_device=ID_device)
        self._state = PSState(variables=self.variables)
        self._i_load_fluctuaton_rms = i_load_fluctuation_rms
        self._i_load_fluctuation = 0.0

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
        return _ack.ok, _BSMPConst.version

    def cmd_0x11(self, ID_receiver, ID_variable):
        """Respond BSMP variable."""
        self._update_state()
        if ID_variable not in self._variables.keys():
            return _ack.invalid_id, None
        return _ack.ok, self._state[ID_variable]

    def cmd_0x13(self, ID_receiver, ID_group):
        """Respond SBMP variable group."""
        self._update_state()
        if ID_group not in self._groups:
            return _ack.invalid_id, None
        IDs_variable = self._groups[ID_group]
        load = {}
        for ID_variable in IDs_variable:
            # check if variable value copying is needed!
            load[ID_variable] = self._state[ID_variable]
        load[_BSMPConst.i_load] += self._i_load_fluctuation
        return _ack.ok, load

    def cmd_0x51(self, ID_receiver, ID_function, **kwargs):
        """Respond to execute BSMP function."""
        self._update_state()
        if ID_function == _BSMPConst.set_slowref:
            return self._func_set_slowref(**kwargs)
        elif ID_function == _BSMPConst.cfg_op_mode:
            return self._func_cfg_op_mode(**kwargs)
        elif ID_function == _BSMPConst.turn_on:
            status = self._state[_BSMPConst.ps_status]
            status = _Status.set_state(status, _PSConst.States.SlowRef)
            self._state[_BSMPConst.ps_status] = status
            self._state[_BSMPConst.i_load] = \
                self._state[_BSMPConst.ps_reference] + \
                self._i_load_fluctuation
            return _ack.ok, None
        elif ID_function == _BSMPConst.turn_off:
            status = self._state[_BSMPConst.ps_status]
            status = _Status.set_state(status, _PSConst.States.Off)
            self._state[_BSMPConst.ps_status] = status
            self._state[_BSMPConst.i_load] = 0.0 + self._i_load_fluctuation
            return _ack.ok, None
        elif ID_function == _BSMPConst.reset_interlocks:
            self._state[_BSMPConst.ps_soft_interlocks] = 0
            self._state[_BSMPConst.ps_hard_interlocks] = 0
            return _ack.ok, None
        elif ID_function == _BSMPConst.close_loop:
            return self._func_close_loop()
        else:
            raise NotImplementedError(
                'Run of {} function not implemented!'.format(hex(ID_function)))

    def _func_set_slowref(self, **kwargs):
        self._state[_BSMPConst.ps_setpoint] = kwargs['setpoint']
        self._state[_BSMPConst.ps_reference] = \
            self._state[_BSMPConst.ps_setpoint]
        status = self._state[_BSMPConst.ps_status]
        if _Status.pwrstate(status) == _PSConst.PwrState.On:
            # i_load <= ps_reference
            self._state[_BSMPConst.i_load] = \
                self._state[_BSMPConst.ps_reference] + self._i_load_fluctuation
        return _ack.ok, None

    def _func_cfg_op_mode(self, **kwargs):
        status = self._state[_BSMPConst.ps_status]
        status = _Status.set_state(status, kwargs['op_mode'])
        self._state[_BSMPConst.ps_status] = status
        return _ack.ok, None

    def _func_close_loop(self):
        status = self._state[_BSMPConst.ps_status]
        status = _Status.set_openloop(status, 0)
        return _ack.ok, None

    def _update_state(self):
        if self._i_load_fluctuaton_rms != 0.0:
            self._i_load_fluctuation = \
                _random.gauss(0.0, self._i_load_fluctuaton_rms)



class BSMPResponse(_BSMPResponse, _StreamChecksum):
    """Transport BSMP layer interacting with real slave device."""

    _FAKE_FRMWARE_VERSION = ['\x00', '\x00']

    def __init__(self, ID_device, PRU):
        """Init method."""
        _BSMPResponse.__init__(self,
                               variables=_get_variables_FBP(),
                               functions=_get_functions(),
                               ID_device=ID_device)

        self._pru = PRU

    def create_group(self, ID_receiver, ID_group, IDs_variable):
        """Create group of BSMP variables."""
        n = len(IDs_variable)
        hb, lb = (n & 0xFF00) >> 8, n & 0xFF
        query = [chr(ID_receiver), "\x30", chr(hb), chr(lb)] + \
            [chr(ID_variable) for ID_variable in IDs_variable]
        query = BSMPResponse.includeChecksum(query)
        self._pru.UART_write(query, timeout=100)
        response = self._pru.UART_read()
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        return ID_cmd, None

    def delete_groups(self, ID_receiver):
        """Delete all groups of BSMP variables."""
        query = [chr(ID_receiver), "\x32", '\x00', '\x00']
        query = BSMPResponse.includeChecksum(query)
        self._pru.UART_write(query, timeout=100)
        response = self._pru.UART_read()
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        return ID_cmd, None

    def cmd_0x01(self, ID_receiver):
        """Respond BSMP protocol version."""
        query = [chr(ID_receiver), "\x00", "\x00", "\x00"]
        query = BSMPResponse.includeChecksum(query)
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
        if ID_variable == _BSMPConst.frmware_version:
            # simulate response to firmware version
            ID_master = 0
            response = [chr(ID_master), '\x11', '\x00', '\x02'] + \
                BSMPResponse._FAKE_FRMWARE_VERSION
            response = BSMPResponse.includeChecksum(response)
        else:
            query = [chr(ID_receiver),
                     '\x10', '\x00', '\x01', chr(ID_variable)]
            query = BSMPResponse.includeChecksum(query)
            self._pru.UART_write(query, timeout=10)  # 10 or 100 for timeout?
            response = self._pru.UART_read()
        # process response
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        if ID_variable == _BSMPConst.frmware_version:
            if len(load) != 2:
                return _ack.invalid_message, None
            value = _get_value_from_load(self._variables, ID_variable, load)
        else:
            raise NotImplementedError(
                'This power supply cmd is not defined for this variable ID!')
        return ID_cmd, value

    def cmd_0x13(self, ID_receiver, ID_group):
        """Respond SBMP variable group."""
        # query power supply
        query = [chr(ID_receiver), '\x12', '\x00', '\x01', chr(ID_group)]
        query = BSMPResponse.includeChecksum(query)
        self._pru.UART_write(query, timeout=10)
        response = self._pru.UART_read()
        # process response
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        if ID_group == _BSMPConst.group_id:
            value = dict()
            value['ps_status'] = ord(response[4]) + (ord(response[5]) << 8)
            value['ps_setpoint'] = \
                _struct.unpack("<f", "".join(response[6:10]))
            value['ps_soft_interlocks'] = \
                ord(response[14]) + (ord(response[15]) << 8)
            value['ps_hard_interlocks'] = \
                ord(response[16]) + (ord(response[17]) << 8)
            value['i_load'] = \
                _struct.unpack("<f", "".join(response[18:22]))
        else:
            raise ValueError('Invalid group ID!')
        return ID_cmd, value

    def cmd_0x51(self, ID_receiver, ID_function, **kwargs):
        """Respond to execute BSMP function."""
        # execute function in power supply
        if ID_function in (_BSMPConst.turn_on,
                           _BSMPConst.turn_off,
                           _BSMPConst.open_loop,
                           _BSMPConst.close_loop,
                           _BSMPConst.reset_interlocks):
            load = []
        elif ID_function == _BSMPConst.set_slowref:
            load = list(_struct.pack("<f", kwargs['setpoint']))
        else:
            raise NotImplementedError
        n = len(load)
        hb, lb = (n & 0xFF00) >> 8, n & 0xFF
        query = [chr(ID_receiver), '\x50', chr(hb), chr(lb),
                 chr(ID_function)] + load
        self._pru.UART_write(query, timeout=100)
        response = self._pru.UART_read()
        # process response
        ID_receiver, ID_cmd, load_size, load = self.parse_stream(response)
        return ID_cmd, None


class Controller():
    """Controller class."""

    # conversion dict from PS fields to DSP properties for read method.
    _read_field2func = {
        'CtrlMode-Mon': '_get_ctrlmode',
        'PwrState-Sts': '_get_pwrstate',
        'OpMode-Sts': '_get_opmode',
        'Current-RB': '_get_ps_setpoint',
        'CurrentRef-Mon': '_get_ps_reference',
        'Current-Mon': '_get_i_load',
        'IntlkSoft-Mon': '_get_ps_soft_interlocks',
        'IntlkHard-Mon': '_get_ps_hard_interlocks',
        'Version-Cte': '_get_frmware_version',
    }

    _write_field2func = {
        'PwrState-Sel': '_set_pwrstate',
        'OpMode-Sel': '_set_opmode',
        'Current-SP': 'cmd_set_slowref',
    }

    # --- API: general power supply 'variables' ---

    def __init__(self, serial_comm, ID_device):
        """Init method."""
        self._ID_device = ID_device
        self._serial_comm = serial_comm
        self._opmode = _PSConst.OpMode.SlowRef

        # reset interlocks
        self.cmd_reset_interlocks()

        # turn ps on and implicitly close control loop
        self.pwrstate = _PSConst.PwrState.On

        # set opmode do SlowRef
        self.opmode = _PSConst.OpMode.SlowRef

        # set reference current to zero
        self.cmd_set_slowref(0.0)

    @property
    def scanning(self):
        """Return scanning state of serial comm."""
        return self._serial_comm.scanning

    @property
    def pwrstate(self):
        """Return PS power state."""
        return self._pwrstate

    @pwrstate.setter
    def pwrstate(self, value):
        """Set PS power state."""
        if value == _PSConst.PwrState.Off:
            self._pwrstate = value
            self.cmd_turn_off()
        elif value == _PSConst.PwrState.On:
            # turn ps on
            self._pwrstate = value
            self.cmd_turn_on()
            # close control loop
            self.cmd_close_loop()
            # set ps opmode to stored value
            self.opmode = self._opmode
        else:
            raise ValueError

    @property
    def opmode(self):
        """Return PS opmode."""
        return self._opmode

    @opmode.setter
    def opmode(self, value):
        """Set PS opmode."""
        if not(0 <= value < len(_ps_opmode)):
            raise ValueError
        # set opmode state
        self._opmode = value
        if self.pwrstate == _PSConst.PwrState.On:
            ps_status = self._get_ps_status()
            op_mode = _Status.set_opmode(ps_status, value)
            self._cmd_cfg_op_mode(op_mode=op_mode)

    # --- API: power supply 'functions' ---

    def cmd_turn_on(self):
        """Turn power supply on."""
        return self._bsmp_run_function(ID_function=_BSMPConst.turn_on)

    def cmd_turn_off(self):
        """Turn power supply off."""
        return self._bsmp_run_function(ID_function=_BSMPConst.turn_off)

    def cmd_open_loop(self):
        """Open DSP control loop."""
        return self._bsmp_run_function(ID_function=_BSMPConst.open_loop)

    def cmd_close_loop(self):
        """Open DSP control loop."""
        return self._bsmp_run_function(_BSMPConst.close_loop)

    def cmd_reset_interlocks(self):
        """Reset interlocks."""
        return self._bsmp_run_function(_BSMPConst.reset_interlocks)

    def cmd_set_slowref(self, setpoint):
        """Set SlowRef reference value."""
        return self._bsmp_run_function(ID_function=_BSMPConst.set_slowref,
                                       setpoint=setpoint)

    # --- API: public properties and methods ---

    def read(self, field):
        """Return value of a field."""
        if field in Controller._read_field2func:
            func = getattr(self, Controller._read_field2func[field])
            value = func()
            return value
        else:
            raise ValueError('Field "{}"" not valid!'.format(field))

    def write(self, field, value):
        """Write value to a field."""
        if field in Controller._write_field2func:
            func = getattr(self, Controller._write_field2func[field])
            ret = func(value)
            return ret
        else:
            raise ValueError('Field "{}"" not valid!'.format(field))

    # --- private methods ---
    #     These are the functions that all subclass have to implement!

    def _get_frmware_version(self):
        value = self._bsmp_get_variable(_BSMPConst.frmware_version)
        vmajor = str((value & 0xFF00) >> 8)
        vminor = str(value & 0xFF)
        frmware_ver = '.'.join([vmajor, vminor])
        return __version__ + '-' + frmware_ver

    def _get_ps_status(self):
        return self._bsmp_get_variable(_BSMPConst.ps_status)

    def _get_ps_setpoint(self):
        return self._bsmp_get_variable(_BSMPConst.ps_setpoint)

    def _get_ps_reference(self):
        return self._bsmp_get_variable(_BSMPConst.ps_reference)

    def _get_ps_soft_interlocks(self):
        return self._bsmp_get_variable(_BSMPConst.ps_soft_interlocks)

    def _get_ps_hard_interlocks(self):
        return self._bsmp_get_variable(_BSMPConst.ps_hard_interlocks)

    def _get_i_load(self):
        return self._bsmp_get_variable(_BSMPConst.i_load)

    def _get_v_load(self):
        return self._bsmp_get_variable(_BSMPConst.v_load)

    def _get_v_dclink(self):
        return self._bsmp_get_variable(_BSMPConst.v_dclink)

    def _bsmp_get_variable(self, ID_variable):
        # read ps_variable as mirrored in the serial_comm object.
        value = self._serial_comm.get_variable(
            ID_device=self._ID_device,
            ID_variable=ID_variable)
        return value

    def _bsmp_run_function(self, ID_function, **kwargs):
        # check if ps is in remote ctrlmode
        if not self._ps_interface_in_remote():
            return
        kwargs.update({'ID_function': ID_function})
        self._serial_comm.put(ID_device=self._ID_device,
                              ID_cmd=0x50,
                              kwargs=kwargs)

    def _get_ctrlmode(self):
        ps_status = self._get_ps_status()
        value = _Status.interface(ps_status)
        return value

    def _get_pwrstate(self):
        return self.pwrstate

    def _get_opmode(self):
        return self.opmode

    def _set_pwrstate(self, value):
        """Set pwrstate state."""
        self.pwrstate = value

    def _set_opmode(self, value):
        """Set pwrstate state."""
        self.opmode = value

    def _cmd_cfg_op_mode(self, op_mode):
        """Set controller operation mode."""
        return self._bsmp_run_function(_BSMPConst.cfg_op_mode, op_mode=op_mode)

    def _ps_interface_in_remote(self):
        ps_status = self._get_ps_status()
        interface = _Status.interface(ps_status)
        return interface == _PSConst.Interface.Remote
