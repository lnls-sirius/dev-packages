"""Module implementing PRU elements."""

import time as _time
from queue import Queue as _Queue
from threading import Thread as _Thread

from siriuspy.csdevice.pwrsupply import max_wfmsize as _max_wfmsize
from siriuspy.pwrsupply.bsmp import Const as _BSMPConst
from siriuspy.pwrsupply.bsmp import get_variables_FBP as _get_variables_FBP
from siriuspy.pwrsupply.bsmp import get_functions as _get_functions
from siriuspy.pwrsupply.controller import PSState as _PSState
from siriuspy.bsmp import Const as _ack
from siriuspy.bsmp import BSMPQuery as _BSMPQuery


try:
    import PRUserial485.PRUserial485 as _PRUserial485
except:
    # in case the PRUserial library is not installed and
    # this module is used only for simulating PRUs.
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

    def curve(self, curve1, curve2, curve3, curve4):
        """Set waveforms for power supplies."""
        return self._curve(curve1, curve2, curve3, curve4)

    # --- pure virtual methods ---

    def _get_sync_pulse_count(self):
        raise NotImplementedError

    def _set_sync_mode(self, value):
        raise NotImplementedError

    def _UART_write(self, stream, timeout):
        raise NotImplementedError

    def _UART_read(self, stream):
        raise NotImplementedError

    def _curve(self, curve1, curve2, curve3, curve4):
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

    def _curve(self, curve1, curve2, curve3, curbe4):
        pass


class PRU(_PRUInterface):
    """Functions for the programmable real-time unit."""

    def __init__(self):
        """Init method."""
        if _PRUserial485 is None:
            raise ValueError('module PRUserial485 is not installed!')
        _PRUInterface.__init__(self)
        # signal use of PRU and shared memory.
        baud_rate = 6
        mode = b"M"  # slave(S)/master(M)
        _PRUserial485.PRUserial485_open(baud_rate, mode)

    def _get_sync_pulse_count(self):
        return _PRUserial485.PRUserial485_read_pulse_count_sync()

    def _get_sync_mode(self):
        return self._sync_mode

    def _set_sync_mode(self, value):
        ID_device = 1  # could it be any number?
        if value:
            _PRUserial485.PRUserial485_sync_start(ID_device, 100)
        else:
            _PRUserial485.PRUserial485_sync_stop()

    def _UART_write(self, stream, timeout):
        # this method send streams through UART to the RS-485 line.
        # print('write: ', stream)
        return _PRUserial485.PRUserial485_write(stream, timeout)

    def _UART_read(self):
        # this method send streams through UART to the RS-485 line.
        stream = _PRUserial485.PRUserial485_read()
        # print('read: ', stream)
        return stream

    def _curve(self, curve1, curve2, curve3, curve4):
        _PRUserial485.PRUserial485_curve(curve1, curve2, curve3, curve4)


class SerialComm(_BSMPQuery):
    """Serial communication Master BSMP device for power supplies."""

    _SCAN_FREQUENCY_SYNC_MODE_OFF = 10.0  # [Hz]
    _SCAN_FREQUENCY_SYNC_MODE_ON = 1.0  # [Hz]
    _default_wfm = [0.0 for _ in range(_max_wfmsize)]

    def __init__(self, simulate=True, slaves=None):
        """Init method."""
        variables = _get_variables_FBP()  # TODO: generalize for other PS types
        self._states = {}
        self._queue = _Queue()
        self._waveforms = {}
        self._simulate = simulate
        self._connected = {}

        _BSMPQuery.__init__(self,
                            variables=variables,
                            functions=_get_functions(),
                            slaves=slaves)

        # self._PRU = PRU
        self._PRU = PRUSim() if self._simulate else PRU()

        # does not start variables scanning just yet.
        self._scanning = False

        # create, configure and start auxilliary threads.
        self._thread_queue = _Thread(target=self._process_queue, daemon=True)
        self._thread_scan = _Thread(target=self._process_scan, daemon=True)
        self._thread_queue.start()
        self._thread_scan.start()

    @property
    def PRU(self):
        """Return PRU object."""
        return self._PRU

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

    def get_connected(self, ID_device):
        """Return connected state of ID_device."""
        return self._connected[ID_device]

    def get_wfmdata(self, ID_device):
        """Return wfmdata of a given ID_device."""
        return self._waveforms[ID_device]

    def set_wfmdata(self, ID_device, wfmdata):
        """Set waveform of a device."""
        sorted_IDs = sorted(self._waveforms.keys())
        if ID_device not in sorted_IDs:
            print('ID_device {} not defined!'.format(ID_device))
            return
        else:
            self._waveforms[ID_device] = wfmdata[:]
            if len(sorted_IDs) == 1:
                self._PRU.curve(self._waveforms[sorted_IDs[0]],
                                SerialComm._default_wfm,
                                SerialComm._default_wfm,
                                SerialComm._default_wfm)
            elif len(sorted_IDs) == 2:
                self._PRU.curve(self._waveforms[sorted_IDs[0]],
                                self._waveforms[sorted_IDs[1]],
                                SerialComm._default_wfm,
                                SerialComm._default_wfm)
            elif len(sorted_IDs) == 3:
                self._PRU.curve(self._waveforms[sorted_IDs[0]],
                                self._waveforms[sorted_IDs[1]],
                                self._waveforms[sorted_IDs[2]],
                                SerialComm._default_wfm)
            elif len(sorted_IDs) > 3:
                self._PRU.curve(self._waveforms[sorted_IDs[0]],
                                self._waveforms[sorted_IDs[1]],
                                self._waveforms[sorted_IDs[2]],
                                self._waveforms[sorted_IDs[3]])

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
        # add entry in waveform dictionary
        # TODO: should we load it from permanent memory?
        self._waveforms[slave.ID_device] = SerialComm._default_wfm

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

            # print(_time.time(), end='')
            # for ID_device in self._connected:
            #     print(self._connected[ID_device], end='')
            # print('')
            item = self._queue.get()
            ID_device, ID_cmd, kwargs = item
            # print('process: ', ID_device, hex(ID_cmd), kwargs)
            cmd = 'cmd_' + str(hex(ID_cmd))
            method = getattr(self, cmd)

            # ack, load = method(ID_receiver=ID_device, **kwargs)
            # self._connected[ID_device] = True

            try:
                ack, load = method(ID_receiver=ID_device, **kwargs)
                self._connected[ID_device] = True
            except Exception:
                # TODO: This try-catch code is very awkward for debugging!
                # try to improve it!
                self._connected[ID_device] = False
                # print('Exception raised while executing {}'.format(cmd))
                continue

            if ack != _ack.ok:
                # needs implementation
                self._connected[ID_device] = False
                print(
                    'Error returned in BSMP command: {}!'.format(hex(ack)))
            elif load is not None:
                ret = self._process_load(ID_device, ID_cmd, load)
                if ret is None:
                    self._connected[ID_device] = False

    def _process_load(self, ID_device, ID_cmd, load):
        if ID_cmd == 0x12:
            for variable, value in load.items():
                # if variable == 27:
                #     print(value)
                self._states[ID_device][variable] = value
            return 0
        else:
            # err_str = 'BSMP cmd {} not implemented in process_thread!'
            # print(err_str)
            return None

    def _process_scan(self):
        """Scan power supply variables, adding puts into queue."""
        interval_sync_off = 1.0/SerialComm._SCAN_FREQUENCY_SYNC_MODE_OFF
        interval_sync_on = 1.0/SerialComm._SCAN_FREQUENCY_SYNC_MODE_ON
        while True:
            time_start = _time.time()
            if self._scanning:
                # init disconnected controllers
                for ID_device in self._connected:
                    if not self._connected[ID_device]:
                        self._init_controller(self.slaves[ID_device])
                self._sync_counter = self._PRU.sync_pulse_count
                self._insert_variables_group_read()
            time_end = _time.time()
            interval = interval_sync_on if self._PRU.sync_mode else \
                interval_sync_off
            sleep_time = max(0, interval - (time_end - time_start))
            _time.sleep(sleep_time)

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
