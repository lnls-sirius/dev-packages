"""Module implementing PRU elements."""
try:
    import PRUserial485 as _PRUserial485
except:
    # in case the PRUserial library is not installed and
    # this module is used only for simulated PRUs.
    _PRUserial485 = None


class _PRUInterface:
    """Interface class for programmable real-time units."""

    _SYNC_OFF = 0
    _SYNC_ON = 1

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

    def sync_stop(self):
        """Stop sync mode."""
        return self._sync_stop()

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

    def _sync_stop(self):
        raise NotImplementedError


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

    def _sync_stop(self):
        _PRUserial485.PRUserial485_sync_stop()


class PRUSim(_PRUInterface):
    """Functions for simulated programmable real-time unit."""

    def __init__(self):
        """Init method."""
        _PRUInterface.__init__(self)
        self._sync_status = _PRUInterface._SYNC_OFF
        self._sync_mode = None
        self._sync_pulse_count = 0

    def _get_sync_status(self):
        return self._sync_status

    def _sync_start(self, sync_mode, delay):
        self._sync_mode = sync_mode
        self._sync_status = _PRUInterface._SYNC_ON

    def _get_sync_pulse_count(self):
        return self._sync_pulse_count

    def _UART_write(self, stream, timeout):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this subclass'))

    def _UART_read(self):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this subclass'))

    def _curve(self, curve1, curve2, curve3, curbe4):
        pass

    def _sync_stop(self):
        self._sync_status = _PRUInterface._SYNC_OFF

    def process_sync_signal(self):
        """Process synchronization signal."""
        self._sync_pulse_count += 1

    # def set_wfmdata(self, ID_device, wfmdata):
    #     """Set waveform of a device."""
    #     sorted_IDs = sorted(self._waveforms.keys())
    #     if ID_device not in sorted_IDs:
    #         print('ID_device {} not defined!'.format(ID_device))
    #         return
    #     else:
    #         self._waveforms[ID_device] = wfmdata[:]
    #         if len(sorted_IDs) == 1:
    #             self._PRU.curve(self._waveforms[sorted_IDs[0]],
    #                             SerialComm._default_wfm,
    #                             SerialComm._default_wfm,
    #                             SerialComm._default_wfm)
    #         elif len(sorted_IDs) == 2:
    #             self._PRU.curve(self._waveforms[sorted_IDs[0]],
    #                             self._waveforms[sorted_IDs[1]],
    #                             SerialComm._default_wfm,
    #                             SerialComm._default_wfm)
    #         elif len(sorted_IDs) == 3:
    #             self._PRU.curve(self._waveforms[sorted_IDs[0]],
    #                             self._waveforms[sorted_IDs[1]],
    #                             self._waveforms[sorted_IDs[2]],
    #                             SerialComm._default_wfm)
    #         elif len(sorted_IDs) > 3:
    #             self._PRU.curve(self._waveforms[sorted_IDs[0]],
    #                             self._waveforms[sorted_IDs[1]],
    #                             self._waveforms[sorted_IDs[2]],
    #                             self._waveforms[sorted_IDs[3]])
