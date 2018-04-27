"""Module implementing PRU elements."""
import time as _time
import threading as _threading

from siriuspy.csdevice.pwrsupply import DEFAULT_WFMDATA as _DEFAULT_WFMDATA

# load PRUserial485 if available and checks version

# version of PRUserial485 library compatible with current implementation of
# PRU classes.
__version__ = '1.2.0'

try:
    import PRUserial485 as _PRUserial485
    ver, *_ = _PRUserial485.__version__.split(':')
    if ver != __version__:
        # loaded library has an incompatible version!
        err_msg = 'Invalid PRUserial485 library version! {} != {}'.format(
            _PRUserial485.__version__, __version__)
        raise ValueError(err_msg)
    if not _PRUserial485.libraries_loaded:
        # could not import libray, which is interpreted as not installed.
        _PRUserial485 = None
except ImportError:
    # in case PRUserial485 library is not installed and
    # this module is used only for simulated PRUs.
    _PRUserial485 = None


class PRUInterface:
    """Interface class for programmable real-time units."""

    # TODO: replace 'write' and 'read' methods by 'request' and 'read' methods

    _SYNC_OFF = False
    _SYNC_ON = True
    _SYNC_DELAY = 20  # [us] TODO: better understand this parameter!

    VERSION = __version__  # Version of the compatible PRUserial485 library

    SYNC_MIGINT = 0x51  # Single curve sequence & Read msgs at End of curve
    SYNC_MIGEND = 0x5E  # Single curve sequence & Read msgs at End of curve
    SYNC_RMPINT = 0xC1  # Contin. curve sequence & Intercalated read messages
    SYNC_RMPEND = 0xCE  # Contin. curve sequence & Read msgs at End of curve
    SYNC_CYCLE = 0x5C   # Single Sequence - Single CYCLING COMMAND
    SYNC_MODES = (
        SYNC_MIGINT, SYNC_MIGEND,
        SYNC_RMPINT, SYNC_RMPEND,
        SYNC_CYCLE
    )

    def __init__(self):
        """Init method."""
        self._sync_mode = None

    # --- public interface ---

    @property
    def sync_mode(self):
        """Return sync mode."""
        return self._sync_mode

    @property
    def sync_status(self):
        """Return sync status."""
        return self._get_sync_status()

    def sync_start(self, sync_mode, sync_address, delay):
        """Start sync mode in PRU."""
        if sync_mode in PRUInterface.SYNC_MODES:
            self._sync_mode = sync_mode
            return self._sync_start(sync_mode, sync_address, delay)
        else:
            # TODO: should this be changed to an exception?
            print('Invalid sync_mode for PRU!')
            return None

    def sync_stop(self):
        """Stop sync mode."""
        return self._sync_stop()

    @property
    def sync_pulse_count(self):
        """Return synchronism pulse count."""
        return self._get_sync_pulse_count()

    def UART_write(self, stream, timeout):
        """Write stream to serial port."""
        ret = self._UART_write(stream, timeout=timeout)
        return ret

    def UART_read(self):
        """Return read from UART."""
        value = self._UART_read()
        return value

    def curve(self, curve1, curve2, curve3, curve4, block):
        """Set waveforms for power supplies."""
        return self._curve(curve1, curve2, curve3, curve4, block)

    def read_curve_pointer(self):
        """Index of next curve point to be processed."""
        return self._read_curve_pointer()

    def set_curve_pointer(self, index):
        """Set index of next curve point to be processed."""
        self._set_curve_pointer(index)

    def read_curve_block(self):
        """Read selected block of curves."""
        self._read_curve_block()

    def set_curve_block(self, block):
        """Set the block of curves."""
        self._set_curve_block(block)

    def close(self):
        """Close PRU session."""
        return self._close()

    # --- pure virtual methods ---

    def _get_sync_status(self):
        raise NotImplementedError

    def _sync_start(sync_mode, sync_address, delay):
        raise NotImplementedError

    def _sync_stop(self):
        raise NotImplementedError

    def _get_sync_pulse_count(self):
        raise NotImplementedError

    def _UART_write(self, stream, timeout):
        raise NotImplementedError

    def _UART_read(self, stream):
        raise NotImplementedError

    def _curve(self, curve1, curve2, curve3, curve4, block):
        raise NotImplementedError

    def _set_curve_block(self, block):
        raise NotImplementedError

    def _read_curve_block(self):
        raise NotImplementedError

    def _close(self):
        raise NotImplementedError


class PRU(PRUInterface):
    """Functions for the programmable real-time unit."""

    def __init__(self):
        """Init method."""
        if _PRUserial485 is None:
            raise ValueError('module PRUserial485 is not installed!')
        PRUInterface.__init__(self)

        # start PRU library and set PRU to sync off
        baud_rate = 6
        mode = b"M"  # "S": slave | "M": master
        _PRUserial485.PRUserial485_open(baud_rate, mode)

    def _get_sync_status(self):
        value = _PRUserial485.PRUserial485_sync_status()
        return value

    def _sync_start(self, sync_mode, sync_address, delay):
        _PRUserial485.PRUserial485_sync_start(
            sync_mode, delay, sync_address)  # delay-sync_addres order is ok.
        return True

    def _sync_stop(self):
        _PRUserial485.PRUserial485_sync_stop()  # None returned
        return True

    def _get_sync_pulse_count(self):
        value = _PRUserial485.PRUserial485_read_pulse_count_sync()
        return value

    def _UART_write(self, stream, timeout):
        # this method send streams through UART to the RS-485 line.
        # print('write: ', stream)
        _PRUserial485.PRUserial485_write(stream, timeout)  # None returned
        return True

    def _UART_read(self):
        # this method send streams through UART to the RS-485 line.
        value = _PRUserial485.PRUserial485_read()
        # print('read: ', value)
        return value

    def _curve(self, curve1, curve2, curve3, curve4, block):
        _PRUserial485.PRUserial485_curve(curve1, curve2, curve3, curve4, block)
        return True

    def _read_curve_pointer(self):
        value = _PRUserial485.PRUserial485_read_curve_pointer()
        return value

    def _set_curve_pointer(self, index):
        _PRUserial485.PRUserial485_set_curve_pointer(index)
        return True

    def _read_curve_block(self):
        value = _PRUserial485.PRUserial485_read_curve_block()
        return value

    def _set_curve_block(self, block):
        _PRUserial485.PRUserial485_set_curve_block(block)  # None returned
        return True

    def _close(self):
        _PRUserial485.PRUserial485_close()
        return True


class PRUSim(PRUInterface):
    """Functions for simulated programmable real-time unit."""

    def __init__(self):
        """Init method."""
        PRUInterface.__init__(self)
        self._sync_status = PRUInterface._SYNC_OFF
        self._sync_pulse_count = 0
        self._trigger_thread = _threading.Thread(
            target=self._listen_timing_trigger, daemon=True)
        self._curves = self._create_curves()
        self._block = 0  # TODO: check if this is the default PRU value
        self._index = 0

    def _get_sync_status(self):
        return self._sync_status

    def _sync_start(self, sync_mode, sync_address, delay):
        self._sync_status = PRUInterface._SYNC_ON
        if not self._trigger_thread.is_alive():
            self._trigger_thread = _threading.Thread(
                target=self._listen_timing_trigger, daemon=True)
            self._trigger_thread.start()
        return True

    def _sync_stop(self):
        self._sync_status = PRUInterface._SYNC_OFF
        return True

    def _get_sync_pulse_count(self):
        return self._sync_pulse_count

    def _UART_write(self, stream, timeout):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this subclass'))

    def _UART_read(self):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this subclass'))

    def _curve(self, curve1, curve2, curve3, curve4, block):
        self._curves[block][0] = curve1.copy()
        self._curves[block][1] = curve2.copy()
        self._curves[block][2] = curve3.copy()
        self._curves[block][3] = curve4.copy()
        return True

    def _read_curve_pointer(self):
        return self._index

    def _set_curve_pointer(self, index):
        self._index = index
        return True

    def _read_curve_block(self):
        return self._block

    def _set_curve_block(self, block):
        # TODO: have to simulate change when previous curve is processed!
        self._block = block
        return True

    def _close(self):
        return True

    # --- simulation auxilliary methods ---

    def _listen_timing_trigger(self):
        # this tries to simulate trigger signal from the timing system
        while self._sync_status == PRUInterface._SYNC_ON:
            if self.sync_mode == PRUSim.SYNC_CYCLE:
                self._sync_pulse_count += 1
                self._sync_status = PRUInterface._SYNC_OFF
            elif self.sync_mode in (PRUSim.SYNC_MIGINT, PRUSim.SYNC_MIGEND):
                self._sync_pulse_count += 1
            elif self.sync_mode in (PRUSim.SYNC_RMPINT, PRUSim.SYNC_RMPEND):
                self._sync_pulse_count += 1
            _time.sleep(0.001)  # TODO: solve this arbitrary value.

    def _create_curves(self):
        curves = [
            # block 0
            [list(_DEFAULT_WFMDATA),  # 1st power suply
             list(_DEFAULT_WFMDATA),  # 2nd power suply
             list(_DEFAULT_WFMDATA),  # 3rd power suply
             list(_DEFAULT_WFMDATA),  # 4th power suply
             ],
            # block 1
            [list(_DEFAULT_WFMDATA),  # 1st power suply
             list(_DEFAULT_WFMDATA),  # 2nd power suply
             list(_DEFAULT_WFMDATA),  # 3rd power suply
             list(_DEFAULT_WFMDATA),  # 4th power suply
             ],
            # block 2
            [list(_DEFAULT_WFMDATA),  # 1st power suply
             list(_DEFAULT_WFMDATA),  # 2nd power suply
             list(_DEFAULT_WFMDATA),  # 3rd power suply
             list(_DEFAULT_WFMDATA),  # 4th power suply
             ],
            # block 3
            [list(_DEFAULT_WFMDATA),  # 1st power suply
             list(_DEFAULT_WFMDATA),  # 2nd power suply
             list(_DEFAULT_WFMDATA),  # 3rd power suply
             list(_DEFAULT_WFMDATA),  # 4th power suply
             ],
        ]
        return curves

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
