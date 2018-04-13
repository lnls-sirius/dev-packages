"""Module implementing PRU elements."""
try:
    import PRUserial485 as _PRUserial485
except:
    # in case the PRUserial library is not installed and
    # this module is used only for simulated PRUs.
    _PRUserial485 = None


class PRUInterface:
    """Interface class for programmable real-time units."""

    _SYNC_OFF = 0
    _SYNC_ON = 1

    SYNC_MODES = {
        'MigInt': 0x51,  # Single curve sequence & Intercalated read messages
        'MigEnd': 0x5E,  # Single curve sequence & Read msgs at End of curve
        'RmpInt': 0xC1,  # Contin. curve sequence & Intercalated read messages
        'RmpEnd': 0xCE,  # Contin. curve sequence & Read msgs at End of curve
        'Cycle':  0x5C,  # Single Sequence - Single CYCLING COMMAND
    }

    def __init__(self):
        """Init method."""
        self._sync_mode = None

    # --- interface ---

    @property
    def sync_mode(self):
        """Return sync mode."""
        return self._sync_mode

    @property
    def sync_status(self):
        """Return sync status."""
        return self._get_sync_status()

    def sync_start(self, sync_mode, delay, sync_address):
        """Start sync mode in PRU."""
        if sync_mode in PRUInterface.SYNC_MODES:
            self._sync_mode = sync_mode
            self._sync_start(sync_mode, delay, sync_address)
        else:
            print('Invalid sync_mode for PRU!')

    def sync_stop(self):
        """Stop sync mode."""
        return self._sync_stop()

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

    def _get_sync_status(self):
        raise NotImplementedError

    def _sync_start(sync_mode, delay, sync_address):
        raise NotImplementedError

    def _sync_stop(self):
        raise NotImplementedError

    def _get_sync_pulse_count(self):
        raise NotImplementedError

    def _UART_write(self, stream, timeout):
        raise NotImplementedError

    def _UART_read(self, stream):
        raise NotImplementedError

    def _curve(self, curve1, curve2, curve3, curve4):
        raise NotImplementedError


class PRU(PRUInterface):
    """Functions for the programmable real-time unit."""

    def __init__(self):
        """Init method."""
        if _PRUserial485 is None:
            raise ValueError('module PRUserial485 is not installed!')
        PRUInterface.__init__(self)
        # signal use of PRU and shared memory.
        baud_rate = 6
        mode = b"M"  # slave(S)/master(M)
        _PRUserial485.PRUserial485_open(baud_rate, mode)

    def _get_sync_status(self):
        return _PRUserial485.PRUserial485_sync_status()

    def _sync_start(self, sync_mode, delay, sync_address):
        return _PRUserial485.PRUserial485_sync_start(
            sync_mode, delay, sync_address)

    def _sync_stop(self):
        return _PRUserial485.PRUserial485_sync_stop()

    def _get_sync_pulse_count(self):
        return _PRUserial485.PRUserial485_read_pulse_count_sync()

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
        return _PRUserial485.PRUserial485_curve(curve1, curve2, curve3, curve4)


class PRUSim(PRUInterface):
    """Functions for simulated programmable real-time unit."""

    def __init__(self):
        """Init method."""
        PRUInterface.__init__(self)
        self._sync_status = PRUInterface._SYNC_OFF
        self._sync_pulse_count = 0

    def _get_sync_status(self):
        return self._sync_status

    def _sync_start(self, sync_mode, delay):
        self._sync_status = PRUInterface._SYNC_ON

    def _sync_stop(self):
        self._sync_status = PRUInterface._SYNC_OFF

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
