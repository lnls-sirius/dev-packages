"""Module implementing PRU elements."""

import time as _time
from queue import Queue as _Queue
from threading import Thread as _Thread

from siriuspy.pwrsupply.bsmp import Const as _BSMPConst
from siriuspy.pwrsupply.bsmp import get_variables_FBP as _get_variables_FBP
from siriuspy.pwrsupply.bsmp import get_functions as _get_functions
from siriuspy.pwrsupply.bsmp import PSState as _PSState
from siriuspy.bsmp import Const as _ack
from siriuspy.bsmp import BSMPQuery as _BSMPQuery


try:
    import PRUserial485.PRUserial485 as _PRUserial485
except ModuleNotFoundError:
    _PRUserial485 = None


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

    def __init__(self):
        """Init method."""
        if _PRUserial485 is None:
            raise ModuleNotFoundError('module PRUserial485 is not installed!')
        _PRUInterface.__init__(self)
        # signal use of PRU and shared memory.
        _PRUserial485.PRUserial485_open(6, b"M")

    def _get_sync_pulse_count(self):
        return _PRUserial485.PRUserial485_read_pulse_count_sync()

    def _get_sync_mode(self):
        return self._sync_mode

    def _set_sync_mode(self, value):
        self._sync_mode = value

    def _UART_write(self, stream, timeout):
        # this method send streams through UART to the RS-485 line.
        return _PRUserial485.PRUserial485_write(stream, timeout)

    def _UART_read(self):
        # this method send streams through UART to the RS-485 line.
        return _PRUserial485.PRUserial485_read()


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
        self._states[slave.ID_device] = _PSState(variables=self._variables)
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
            # print('get :', ID_device, hex(ID_cmd), kwargs)
            cmd = 'cmd_' + str(hex(ID_cmd))
            method = getattr(self, cmd)
            ack, load = method(ID_receiver=ID_device, **kwargs)
            # print('cmd: ', cmd)
            # print('ack: ', hex(ack))
            # print('load: ', load)
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
