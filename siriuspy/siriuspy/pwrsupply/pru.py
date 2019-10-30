"""Module implementing PRU elements."""
import os as _os
import sys as _sys
import threading as _threading

import time as _time

import epics as _epics

import PRUserial485 as _PRUserial485


# check PRUserial485 package version
__version1__ = '1.3.3'  # PRUserial485
__version2__ = '2.3.3'  # eth-PRUserial485
__prulib_ver__ = _PRUserial485.__version__
if not(__version1__ in __prulib_ver__ or __version2__ in __prulib_ver__):
    # loaded library has an incompatible version!
    _ERR_MSG = 'Invalid PRUserial485 library version! {} != {} or {}'.format(
        _PRUserial485.__version__, __version1__, __version2__)
    raise ValueError(_ERR_MSG)


class PRUInterface:
    """Interface class for programmable real-time units."""

    OK = 0

    def __init__(self):
        """Init method."""
        self._timestamp_write = _time.time()
        self._timestamp_read = self._timestamp_write
        self._wr_duration = 0.0

    # --- public interface ---

    @property
    def simulated(self):
        """Simulate flag."""
        return self._get_simulated()

    @property
    def wr_duration(self):
        """Return write-read accumulated duration."""
        return self._wr_duration

    def wr_duration_reset(self):
        """Reset write/read accumulated duration."""
        self._wr_duration = 0.0

    def UART_write(self, stream, timeout):
        """Write stream to serial port."""
        self._timestamp_write = _time.time()
        ret = self._UART_write(stream, timeout=timeout)
        return ret

    def UART_read(self):
        """Return read from UART."""
        value = self._UART_read()
        self._timestamp_read = _time.time()
        self._wr_duration += self._timestamp_read - self._timestamp_write
        return value

    def close(self):
        """Close PRU session."""
        self._close()
        return None

    # --- pure virtual methods ---

    def _UART_write(self, stream, timeout):
        raise NotImplementedError

    def _UART_read(self):
        raise NotImplementedError

    def _close(self):
        raise NotImplementedError


class PRU(PRUInterface):
    """Functions for the programmable real-time unit."""

    def __init__(self, bbbname=None):
        """Init method."""
        # check if appropriate conditions are met
        if _PRUserial485 is None:
            raise ValueError('module PRUserial485 is not installed!')
        if bbbname is None:
            self.version = __version1__
            self.version_server = None
            # check if process is running as root
            if _os.geteuid() != 0:
                _sys.exit('You need to have root privileges to use PRU')
        else:
            if _PRUserial485.__version__ != __version2__:
                _sys.exit('PRUserial485 library if not ethernet client-server')
            # tell PRUserial485_eth what BBB it should connect to
            _PRUserial485.set_beaglebone_ip(bbbname)
            self.version = __version2__
            self.version_server = _PRUserial485.PRUserial485_version()

        # print prulib version
        fmtstr = 'PRUserial485 lib version_{}: {}'
        print(fmtstr.format('client', self.version))
        print(fmtstr.format('server', self.version_server))
        print()

        # init PRUserial485 interface
        PRUInterface.__init__(self)

        # start PRU library and set PRU to sync off
        baud_rate = 6
        mode = b"M"  # "S": slave | "M": master
        ret = _PRUserial485.PRUserial485_open(baud_rate, mode)
        if ret != PRUInterface.OK:
            raise ValueError(('Error {} returned in '
                              'PRUserial485_open').format(ret))

    def _get_simulated(self):
        return False

    def _UART_write(self, stream, timeout):
        # this method send streams through UART to the RS-485 line.
        ret = _PRUserial485.PRUserial485_write(stream, timeout)
        return ret

    def _UART_read(self):
        # this method send streams through UART to the RS-485 line.
        value = _PRUserial485.PRUserial485_read()
        return value

    def _close(self):
        _PRUserial485.PRUserial485_close()
        return None


class PRUSim(PRUInterface):
    """Functions for simulated programmable real-time unit."""

    TIMING_PV = 'FAKE-AS-Glob:PS-Timing:Trigger-Cmd'

    def __init__(self):
        """Init method."""
        PRUInterface.__init__(self)
        self.version = 'Simulation'
        self._callbacks = list()
        self._index = 0
        self._t = None
        self._timing = _epics.PV(PRUSim.TIMING_PV)
        self._timing.add_callback(self.timing_trigger_callback)

        self.sync_block = False

    def _get_simulated(self):
        return True

    def issue_callbacks(self):
        """Execute all callbacks."""
        for cb in self._callbacks:
            cb()

    def timing_trigger_callback(self, pvname, value, **kwargs):
        """Define callback to issue a timing to simulated PS."""

    def _UART_write(self, stream, timeout):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this subclass'))

    def _UART_read(self):
        raise NotImplementedError(('This method should not be called '
                                  'for objects of this subclass'))

    def _close(self):
        return None

    # --- simulation auxilliary methods ---

    def add_callback(self, func):
        """Add callback."""
        self._callbacks.append(func)
