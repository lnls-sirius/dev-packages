"""BSMP serial communications classes."""

import struct as _struct
from threading import Lock as _Lock
from .exceptions import SerialErrEmpty as _SerialErrEmpty
from .exceptions import SerialErrCheckSum as _SerialErrCheckSum
from .exceptions import SerialErrPckgLen as _SerialErrPckgLen
from .exceptions import SerialErrMsgShort as _SerialErrMsgShort


class Message:
    """BSMP Message.

    Command: command id; 1 byte;
    Load Size: payload size in bytes; 2 bytes (big endian);
    Load: 0..65535 bytes.
    """

    # TODO: indicate somehow that stream is a char stream.

    # Constructors
    def __init__(self, stream):
        """Build a BSMP message."""
        if len(stream) < 3:
            raise _SerialErrMsgShort("BSMP Message too short.")
        self._stream = stream
        self._cmd = ord(stream[0])

    def __eq__(self, other):
        """Compare messages."""
        return self._stream == other.stream

    @classmethod
    def message(cls, cmd, payload=None):
        """Build a Message object from a byte stream."""
        if payload and not isinstance(payload, list):
            # TODO: should be create serial exceptions here too?
            raise TypeError("Load must be a list.")
        if payload and len(payload) > 65535:
            # TODO: should be create serial exceptions here too?
            raise ValueError("Load must be smaller than 65535.")

        stream = []

        if not payload:
            payload = []
        # Append cmd
        stream.append(chr(cmd))
        # Append size
        stream.extend(list(map(chr, (_struct.pack('>H', len(payload))))))
        # Append payload
        stream.extend(payload)
        return cls(stream)

    # API
    @property
    def stream(self):
        """Return stream."""
        return self._stream

    @property
    def cmd(self):
        """Command ID."""
        return self._cmd

    @property
    def size(self):
        """Load size."""
        return _struct.unpack('>H', bytes(map(ord, self._stream[1:3])))[0]

    @property
    def payload(self):
        """Message payload."""
        return self._stream[3:]


class Package:
    """BSMP Package.

    Address: 1 byte, 0..31
    Message: no limit
    Checksum: package checksum
    """

    def __init__(self, stream):
        """Build a BSMP package."""
        if len(stream) < 5:
            raise _SerialErrPckgLen("BSMP Package too short.")
        if not Package.verify_checksum(stream):
            # print('resp: ', [hex(ord(c)) for c in stream])
            raise _SerialErrCheckSum(
                "Inconsistent message. Checksum does not check.")
        self._stream = stream
        self._address = ord(stream[0])  # 0 to 31
        self._message = Message(stream[1:-1])
        self._checksum = ord(stream[-1])

    @classmethod
    def package(cls, address, message):
        """Build a Package object from a byte stream."""
        # Return new package
        stream = []
        stream.append(chr(address))
        stream.extend(message.stream)
        chksum = cls.calc_checksum(stream)
        stream.append(chr(chksum))
        return cls(stream)

    # API
    @property
    def stream(self):
        """Stream."""
        return self._stream

    @property
    def address(self):
        """Receiver node serial address."""
        return self._address

    @property
    def message(self):
        """Return package message."""
        return self._message

    @property
    def checksum(self):
        """Return package checksum."""
        return self._checksum

    @staticmethod
    def calc_checksum(stream):
        """Return stream checksum."""
        streambytes = [ord(s) for s in stream]
        counter = sum(streambytes)
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        return counter

    @staticmethod
    def verify_checksum(stream):
        """Verify stream checksum."""
        streambytes = [ord(s) for s in stream[:-1]]
        counter = sum(streambytes)
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        if stream[len(stream) - 1] == chr(counter):
            return True
        else:
            return False


class Channel:
    """BSMP Channel.

    The channel is defined by a sender pru controller and recipient
    address.
    """

    # TODO: should we remove use of default timeout values. It is dangerous!

    _lock = _Lock()

    def __init__(self, pru, address):
        """Set channel."""
        self._pru = pru  # PRU object to communicate with bsmp device
        self._address = address  # address of recipient device.

    @property
    def pru(self):
        """Reurn PRU serial communication object."""
        return self._pru

    @property
    def address(self):
        """Return attached bsmp device id."""
        return self._address

    def read(self):
        """Read from serial."""
        resp = self.pru.UART_read()
        # print('read resp ({}): '.format(
        #     len(resp)), [hex(ord(c)) for c in resp])
        if not resp:
            raise _SerialErrEmpty("Serial read returned empty!")
        package = Package(resp)
        return package.message

    def write(self, message, timeout=100):
        """Write to serial."""
        stream = Package.package(self._address, message).stream
        # print('write query : ', [hex(ord(c)) for c in stream])
        response = self.pru.UART_write(stream, timeout=timeout)
        return response

    def request(self, message, timeout=100, read_flag=True):
        """Write and wait for response."""
        # This lock is important in order to avoid threads in the same process
        # space to read each other's responses.
        #
        # Channel._lock.acquire(blocking=True)
        # try:
        #     self.write(message, timeout)
        #     if read_flag:
        #         response = self.read()
        #     else:
        #         package = Package([])
        #         response = package.message
        # except _SerialError:
        #     Channel._lock.release()
        #     raise
        # Channel._lock.release()
        # return response
        with Channel._lock:
            self.write(message, timeout)
            if read_flag:
                response = self.read()
            else:
                response = Message([chr(0xE0), chr(0), chr(0)])  # arbitrary 0xE0 (OK) response
            return response
