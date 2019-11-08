"""Module implementing PRU elements."""
import time as _time

import epics as _epics
import PRUserial485 as _PRUserial485
from PRUserial485 import EthBrigdeClient as _EthBrigdeClient

from siriuspy.csdevice import util as _util


# check PRUserial485 package version
__version_eth_required__ = '2.4.0'  # eth-PRUserial485
__version_eth_implmntd__ = _PRUserial485.__version__
if __version_eth_implmntd__ != __version_eth_required__:
    _ERR_MSG = 'Incompatible PRUserial485 library versions: {} != {}'.format(
        __version_eth_implmntd__, __version_eth_required__)
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

    def __init__(self, bbbname=None, ip_address=None):
        """Init method."""
        # check if appropriate conditions are met
        if _PRUserial485 is None:
            raise ValueError('module PRUserial485 is not installed!')

        # if ip address was not given, get it from bbbname
        if ip_address is None:
            dev2ips = _util.get_device_2_ioc_ip()
            ip_address = dev2ips[bbbname]
        print('BEAGLEBONE: ', bbbname)
        print('IP_ADDRESS: ', ip_address)

        # start communication threads
        self._ethbrigde = _EthBrigdeClient(ip_address=ip_address)
        self._ethbrigde.threads_start()

        # print prulib version
        # fmtstr = 'PRUserial485 lib version_{}: {}'
        # print(fmtstr.format('client', self.version))
        # print(fmtstr.format('server', self.version_server))
        # print()

        # init PRUserial485 interface
        PRUInterface.__init__(self)

        # start PRU library and set PRU to sync off
        baud_rate = 6
        mode = b"M"  # "S": slave | "M": master
        ret = self._ethbrigde.open(baud_rate, mode)
        if ret != PRUInterface.OK:
            raise ValueError(('Error {} returned in '
                              'PRUserial485_open').format(ret))

    def _get_simulated(self):
        return False

    def _UART_write(self, stream, timeout):
        # this method send streams through UART to the RS-485 line.
        ret = self._ethbrigde.write(stream, timeout)
        return ret

    def _UART_read(self):
        # this method send streams through UART to the RS-485 line.
        value = self._ethbrigde.read()
        return value

    def _close(self):
        self._ethbrigde.close()
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
