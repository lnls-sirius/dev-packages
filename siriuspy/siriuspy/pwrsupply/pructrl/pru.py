"""Module implementing PRU elements."""
import time as _time

from siriuspy.bsmp import IOInterface as _IOInterface

from ... import csdev as _csdev


class PRUInterface(_IOInterface):
    """Interface class for programmable real-time units."""

    def __init__(self):
        """Init method."""
        self._timestamp_write = _time.time()
        self._timestamp_read = self._timestamp_write
        self._wr_duration = 0.0

    # --- public interface ---

    def open(self):
        """."""

    def close(self):
        """Close PRU session."""
        self._close()
        return None

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

    def UART_request(self, stream, timeout):
        """Write stream to serial port then read."""
        self._timestamp_write = _time.time()
        ret = self._UART_request(stream, timeout=timeout)
        return ret

    # --- pure virtual methods ---

    def _UART_write(self, stream, timeout):
        raise NotImplementedError

    def _UART_read(self):
        raise NotImplementedError

    def _UART_request(self, stream, timeout):
        raise NotImplementedError

    def _close(self):
        raise NotImplementedError


class PRU(PRUInterface):
    """Functions for the programmable real-time unit."""

    def __init__(self, ethbridgeclnt_class, bbbname=None, ip_address=None):
        """Init method."""
        # if ip address was not given, get it from bbbname
        if ip_address is None:
            dev2ips = _csdev.get_device_2_ioc_ip()
            ip_address = dev2ips[bbbname]
        print('BEAGLEBONE: ', bbbname)
        print('IP_ADDRESS: ', ip_address)

        # stores bbbname and ip address
        self._bbbname = bbbname
        self._ip_address = ip_address

        # start communication threads
        self._ethbridge = ethbridgeclnt_class(ip_address=ip_address)

        # init PRUserial485 interface
        PRUInterface.__init__(self)

    @property
    def bbbname(self):
        """Return beaglebone name."""
        return self._bbbname

    @property
    def ip_address(self):
        """Return beaglebone IP address."""
        return self._ip_address

    def _UART_write(self, stream, timeout):
        # this method send streams through UART to the RS-485 line.
        ret = self._ethbridge.write(stream, timeout)
        return ret

    def _UART_read(self):
        # this method send streams through UART to the RS-485 line.
        value = self._ethbridge.read()
        return value

    def _UART_request(self, stream, timeout):
        # this method send streams through UART to the RS-485 line.
        ret = self._ethbridge.request(stream, timeout)
        return ret

    def _close(self):
        # self._ethbridge.close()
        return None
