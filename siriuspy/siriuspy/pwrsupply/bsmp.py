"""BSMP entities definitions for the power supply devices."""

import time as _time
from Queue import Queue as _Queue
from threading import Thread as _Thread

from siriuspy.bsmp import __version__ as __bsmp_version__
from siriuspy.bsmp import Const as _ack
from siriuspy.bsmp import BSMPDeviceMaster as _BSMPDeviceMaster
from siriuspy.bsmp import BSMPDeviceSlave as _BSMPDeviceSlave
from siriuspy.pwrsupply.status import Status as _Status
from siriuspy.csdevice.pwrsupply import Const as _PSConst

# import PRUserial485 as _PRUserial485
_PRUserial485 = None


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
    def pulse_count_sync(self):
        """Return synchronism pulse count."""
        return self._get_pulse_count_sync()

    def write(self, stream, timeout):
        """Write stream to serial line."""
        raise NotImplementedError

    # --- pure virtual method ---

    def _get_pulse_count_sync(self):
        raise NotImplementedError

    def _set_sync_mode(self, value):
        raise NotImplementedError


class PRUSim(_PRUInterface):
    """Simulated PRU."""

    def __init__(self):
        """Init method."""
        _PRUInterface.__init__(self)
        self._pulse_count_sync = 0

    def process_sync_signal(self):
        """Process synchronization signal."""
        self._pulse_count_sync += 1

    def _get_pulse_count_sync(self):
        return self._pulse_count_sync

    def _set_sync_mode(self, value):
        pass

    def _write(self, stream, timeout):
        # not used!
        raise NotImplementedError


class PRU(_PRUInterface):
    """Programmable real-time unit."""

    def _get_pulse_count_sync(self):
        return _PRUserial485.PRUserial485_read_pulse_count_sync()

    def _get_sync_mode(self):
        return self._sync_mode

    def _set_sync_mode(self, value):
        self._sync_mode = value

    def _write(self, stream, timeout):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this class'))


class PSState:
    """Power supply state."""

    def __init__(self, variables):
        """Init method."""
        self._state = {}
        for ID_variable, variable in variables.items():
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

    def __getitem__(self, key):
        """Return value corresponfing to a certain key (ps_variable)."""
        return self._state[key]

    def __setitem__(self, key, value):
        """Set value for a certain key (ps_variable)."""
        self._state[key] = value
        return value


class SerialComm(_BSMPDeviceMaster):
    """Master BSMP device for FBP power supplies."""

    _SCAN_INTERVAL_SYNC_MODE_OFF = 0.1  # [s]
    _SCAN_INTERVAL_SYNC_MODE_ON = 1.0  # [s]

    def __init__(self, PRU, slaves=None):
        """Init method."""
        variables = get_variables_FBP()
        _BSMPDeviceMaster.__init__(self,
                                   variables=variables,
                                   functions=get_functions(),
                                   slaves=slaves)
        self._PRU = PRU
        self._queue = _Queue()
        self._state = PSState(variables=variables)
        # Cria, configura e inicializa as duas threads auxiliares
        self._process = _Thread(target=self._process_thread, daemon=True)
        self._scan = _Thread(target=self._scan_thread, daemon=True)
        self._process.start()
        self._scan.start()

    @property
    def sync_mode(self):
        """Return sync mode of PRU."""
        return self._PRU.sync_mode

    @sync_mode.setter
    def sync_mode(self, value):
        """Set PRU sync mode."""
        self._PRU.sync_mode = value

    def write(self, stream, timeout):
        """Write stream to controlled serial line."""
        self._PRU.write(stream, timeout)

    def add_slave(self, slave):
        """Add slave to slave pool controlled by master BSMP device."""
        # create group for all variables.
        _BSMPDeviceMaster.add_slave(self, slave)
        slave.serial_comm = self
        IDs_variable = tuple(self.variables.keys())
        ack, *_ = self.cmd_0x30(ID_slave=slave.ID_device,
                                ID_group=3,
                                IDs_variable=IDs_variable)
        if ack != _ack.ok:
            raise Exception('Could not create variables group!')

    def put(self, ID_device, cmd, value):
        """Put a SBMP command request in queue."""
        self._queue.put((ID_device, cmd, value))

    def get_variable(self, ID_slave, ID_variable):
        """Return a BSMP variable."""
        return self._state[ID_variable]

    def _process_thread(self):
        """Process queue."""
        item = self._queue.get()
        id_slave = item[0]
        operation = item[1]
        try:
            kwargs = item[2]
        except KeyError:
            kwargs = {}

        answer = getattr(self.slaves[id_slave], operation)(**kwargs)

    def _scan_thread(self):
        """Add scan puts into queue."""
        while (True):
            self._sync_counter = self._PRU.pulse_count_sync
            for ID_slave in self._slaves:
                self._queue.put((ID_slave, 'cmd_0x10', {'ID_group': 3}))
            if self._PRU.sync_mode:
                # self.event.wait(1)
                _time.sleep(SerialComm._SCAN_INTERVAL_SYNC_MODE_ON)
            else:
                # self.event.wait(0.1)
                _time.sleep(SerialComm._SCAN_INTERVAL_SYNC_MODE_OFF)


class DevSlaveSim(_BSMPDeviceSlave):
    """Transport BSMP layer interacting with simulated slave device."""

    def __init__(self, ID_device):
        """Init method."""
        _BSMPDeviceSlave.__init__(self,
                                  variables=get_variables_FBP(),
                                  functions=get_functions(),
                                  ID_device=ID_device)
        self._state = PSState(variables=self.variables)

    def _create_group(self, ID_group, IDs_variable):
        ID_group = len(self._groups)
        self._groups[ID_group] = IDs_variable[:]
        return _ack.ok, None

    def _delete_groups(self):
        self._groups = {}
        return _ack.ok, None

    def cmd_0x01(self):
        """Respond BSMP protocol version."""
        return _ack.ok, __bsmp_version__

    def cmd_0x11(self, ID_variable):
        """Respond BSMP variable."""
        if ID_variable not in self._variables.keys():
            return _ack.invalid_id, None
        return _ack.ok, self._state[ID_variable]

    def cmd_0x13(self, ID_group):
        """Respond SBMP variable group."""
        IDs_variable = self._groups[ID_group]
        data = {}
        for ID_variable in IDs_variable:
            data[ID_variable] = self._state[ID_variable]
        return _ack.ok, data

    def cmd_0x51(self, ID_function, **kwargs):
        """Respond execute BSMP function."""
        if ID_function == Const.turn_on:
            status = self._state[Const.ps_status]
            status = _Status.set_state(status, _PSConst.States.SlowRef)
            self._state[Const.ps_status] = status
            self._state[Const.i_load] = self._state[Const.ps_reference]
            return _ack.ok, None
        elif ID_function == Const.turn_off:
            status = self._state[Const.ps_status]
            status = _Status.set_state(status, _PSConst.States.Off)
            self._state[Const.ps_status] = status
            self._state[Const.i_load] = 0.0
            return _ack.ok, None
        elif ID_function == Const.set_slowref:
            return self._func_set_slowref(**kwargs)
        elif ID_function == Const.cfg_op_mode:
            return self._func_cfg_op_mode(**kwargs)
        else:
            raise NotImplementedError

    def _func_set_slowref(self, **kwargs):
        self._state[Const.ps_setpoint] = kwargs['setpoint']
        self._state[Const.ps_reference] = self._state[Const.ps_setpoint]
        status = self._state[Const.ps_status]
        if _Status.pwrstate(status) == _PSConst.PwrState.On:
            self._state[Const.i_load] = self._state[Const.ps_reference]
        return _ack.ok, None

    def _func_cfg_op_mode(self, **kwargs):
        status = self._state[Const.ps_status]
        status = _Status.set_state(status, kwargs['op_mode'])
        self._state[Const.ps_status] = status
        return _ack.ok, None


class DevSlave(_BSMPDeviceSlave):
    """Transport BSMP layer interacting with real slave device."""

    def __init__(self, ID_device):
        """Init method."""
        _BSMPDeviceSlave.__init__(self,
                                  variables=get_variables_FBP(),
                                  functions=get_functions(),
                                  ID_device=ID_device)

        self._serial_comm = None

    @property
    def serial_comm(self):
        """Return associated SerialComm object."""
        return self._serial_comm

    @serial_comm.setter
    def serial_comm(self, value):
        """Set associated SerialComm object."""
        self._serial_comm = value

    def cmd_0x01(self):
        """Respond BSMP protocol version."""
        ID_receiver = chr(self.ID_device)
        stream = [ID_receiver, "\x00", "\x00", "\x00"]
        stream = DevSlaveSim.includeChecksum(stream)
        answer = self._serial_comm.write(stream, timeout=10)
        if len(answer) != 8:
            return _ack.invalid_message, None
        version_str = '.'.join([str(ord(c)) for c in answer[4:7]])
        return _ack.ok, version_str

    @staticmethod
    def includeChecksum(string):
        """Return string checksum."""
        counter = 0
        i = 0
        while (i < len(string)):
            counter += ord(string[i])
            i += 1
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        return(string + [chr(counter)])
