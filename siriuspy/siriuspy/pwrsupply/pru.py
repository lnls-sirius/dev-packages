"""Module implementing PRU elements."""
import time as _time

from siriuspy.csdevice.pwrsupply import DEFAULT_WFMDATA as _DEFAULT_WFMDATA

# load PRUserial485 if available and checks version

# version of PRUserial485 library compatible with current implementation of
# PRU classes.
__version__ = '1.3.1'

try:
    import PRUserial485 as _PRUserial485
    ver, *_ = _PRUserial485.__version__.split(':')
    if ver != __version__:
        # loaded library has an incompatible version!
        err_msg = 'Invalid PRUserial485 library version! {} != {}'.format(
            _PRUserial485.__version__, __version__)
        raise ValueError(err_msg)
    # if not _PRUserial485.libraries_loaded:
    #     # could not import libray, which is interpreted as not installed.
    #     _PRUserial485 = None
except ImportError:
    # in case PRUserial485 library is not installed and
    # this module is used only for simulated PRUs.
    _PRUserial485 = None
finally:
    del(ver)


class Const:
    """Namespace for constants."""

    RETURN = _PRUserial485.ConstReturn
    SYNC_MODE = _PRUserial485.ConstSyncMode

    class SYNC_STATE:
        """Namespace for sync state constants."""

        OFF = False
        ON = True


class PRUInterface:
    """Interface class for programmable real-time units."""

    # TODO: replace 'write' and 'read' methods by 'request' and 'read' methods

    VERSION = __version__  # Version of the compatible PRUserial485 library

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
        if sync_mode in Const.SYNC_MODE.ALL:
            self._sync_mode = sync_mode
            self._sync_start(sync_mode, sync_address, delay)
            return None
        else:
            # TODO: should this be changed to an exception?
            print('Invalid sync_mode for PRU!')
            return None

    def sync_stop(self):
        """Stop sync mode."""
        self._sync_stop()
        return None

    def sync_abort(self):
        """Force stop sync mode."""
        self._sync_abort()
        return None

    @property
    def sync_pulse_count(self):
        """Return synchronism pulse count."""
        return self._get_sync_pulse_count()

    def clear_pulse_count_sync(self):
        """Clear pulse count sync."""
        return self._clear_pulse_count_sync()

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
        return None

    def read_curve_block(self):
        """Read selected block of curves."""
        return self._read_curve_block()

    def set_curve_block(self, block):
        """Set the block of curves."""
        self._set_curve_block(block)
        return None

    def close(self):
        """Close PRU session."""
        self._close()
        return None

    # --- pure virtual methods ---

    def _get_sync_status(self):
        raise NotImplementedError

    def _sync_start(sync_mode, sync_address, delay):
        raise NotImplementedError

    def _sync_stop(self):
        raise NotImplementedError

    def _sync_abort(self):
        raise NotImplementedError

    def _get_sync_pulse_count(self):
        raise NotImplementedError

    def _UART_write(self, stream, timeout):
        raise NotImplementedError

    def _UART_read(self, stream):
        raise NotImplementedError

    def _curve(self, curve1, curve2, curve3, curve4, block):
        raise NotImplementedError

    def _read_curve_pointer(self):
        raise NotImplementedError

    # def _set_curve_pointer(self, index):
    #     raise NotImplementedError

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
        ret = _PRUserial485.PRUserial485_open(baud_rate, mode)
        if ret != Const.RETURN.OK:
            raise ValueError(('Error {} returned in '
                              'PRUserial485_open').format(ret))

    def _get_sync_status(self):
        value = _PRUserial485.PRUserial485_sync_status()
        return value

    def _sync_start(self, sync_mode, sync_address, delay):
        _PRUserial485.PRUserial485_sync_start(
            sync_mode, delay, sync_address)  # delay-sync_addres order is ok.
        return True

    def _sync_stop(self):
        # TODO: ask CON to implement sync_stop
        return self._sync_abort()

    def _sync_abort(self):
        _PRUserial485.PRUserial485_sync_stop()  # None returned
        return None

    def _get_sync_pulse_count(self):
        value = _PRUserial485.PRUserial485_read_pulse_count_sync()
        return value

    def _clear_pulse_count_sync(self):
        value = _PRUserial485.PRUserial485_clear_pulse_count_sync()
        return value

    def _UART_write(self, stream, timeout):
        # this method send streams through UART to the RS-485 line.
        # print('write: ', stream)
        ret = _PRUserial485.PRUserial485_write(stream, timeout)
        return ret

    def _UART_read(self):
        # this method send streams through UART to the RS-485 line.
        value = _PRUserial485.PRUserial485_read()
        # print('read: ', value)
        return value

    def _curve(self, curve1, curve2, curve3, curve4, block):
        ret = _PRUserial485.PRUserial485_curve(curve1, curve2,
                                               curve3, curve4, block)
        return ret

    def _read_curve_pointer(self):
        value = _PRUserial485.PRUserial485_read_curve_pointer()
        return value

    def _set_curve_pointer(self, index):
        _PRUserial485.PRUserial485_set_curve_pointer(index)
        return None

    def _read_curve_block(self):
        value = _PRUserial485.PRUserial485_read_curve_block()
        return value

    def _set_curve_block(self, block):
        _PRUserial485.PRUserial485_set_curve_block(block)
        return None

    def _close(self):
        _PRUserial485.PRUserial485_close()
        return None


class PRUSim(PRUInterface):
    """Functions for simulated programmable real-time unit."""

    # TODO: maybe create a thread to simulate timing triggers.

    def emulate_trigger(self):
        """Simulate trigger signal from the timing system."""
        if self._sync_status == Const.SYNC_STATE.ON:
            self._sync_pulse_count += 1
            if self.sync_mode == Const.SYNC_MODE.CYCLE:
                self._sync_status = Const.SYNC_STATE.OFF
            elif self.sync_mode in (Const.SYNC_MODE.MIGINT,
                                    Const.SYNC_MODE.MIGEND):
                self._index = (self._index + 1) % len(self._curves[0])
                if self._index == 0:
                    self._sync_status = Const.SYNC_STATE.OFF
            elif self.sync_mode in (Const.SYNC_MODE.RMPINT,
                                    Const.SYNC_MODE.RMPEND):
                self._index = (self._index + 1) % len(self._curves[0])

    def __init__(self):
        """Init method."""
        PRUInterface.__init__(self)
        self._sync_status = Const.SYNC_STATE.OFF
        self._sync_pulse_count = 0
        self._curves = self._create_curves()
        self._block = 0  # TODO: check if this is the default PRU value
        self._index = 0

    def _get_sync_status(self):
        return self._sync_status

    def _sync_start(self, sync_mode, sync_address, delay):
        self._sync_status = Const.SYNC_STATE.ON
        # TODO: implement while loop as thread (for RMP and MIG modes to work)
        while self._sync_status == Const.SYNC_STATE.ON:
            self.emulate_trigger()
            _time.sleep(0.1)
        return None

    def _sync_stop(self):
        self._sync_abort()
        return None

    def _sync_abort(self):
        self._sync_status = Const.SYNC_STATE.OFF
        return None

    def _get_sync_pulse_count(self):
        return self._sync_pulse_count

    def _clear_pulse_count_sync(self):
        if self._sync_status == Const.SYNC_STATE.OFF:
            self._sync_pulse_count = 0
            return Const.RETURN.OK
        else:
            return Const.RETURN.ERR_CLEAR_PULSE

    def _UART_write(self, stream, timeout):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this subclass'))

    def _UART_read(self):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this subclass'))

    def _curve(self, curve1, curve2, curve3, curve4, block):
        if len(curve1) == len(curve2) == len(curve3) == len(curve4):
            self._curves[block][0] = curve1.copy()
            self._curves[block][1] = curve2.copy()
            self._curves[block][2] = curve3.copy()
            self._curves[block][3] = curve4.copy()
            return Const.RETURN.OK
        else:
            raise ValueError("Erro: Curvas nao tem o mesmo tamanho!")

    def _read_curve_pointer(self):
        return self._index

    def _set_curve_pointer(self, index):
        self._index = index
        return None

    def _read_curve_block(self):
        return self._block

    def _set_curve_block(self, block):
        # TODO: have to simulate change when previous curve is processed!
        self._block = block
        return None

    def _close(self):
        return None

    # --- simulation auxilliary methods ---

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
