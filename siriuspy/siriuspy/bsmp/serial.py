"""BSMP serial communications classes."""
import struct as _struct
from .exceptions import SerialError as _SerialError

# TODO: rename module to 'channel.py' ?


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
            raise ValueError("BSMP Message too short.")
        self._stream = stream
        self._cmd = ord(stream[0])

    def __eq__(self, other):
        """Compare messages."""
        return self._stream == other.stream

    @classmethod
    def message(cls, cmd, payload=None):
        """Build a Message object from a byte stream."""
        if payload and not isinstance(payload, list):
            raise TypeError("Load must be a list.")
        if payload and len(payload) > 65535:
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
    """BSMP package.

    Address: 1 byte, 0..31
    Message: no limit
    Checksum: package checksum
    """

    # TODO: think about the name "address"...

    # Constructors
    def __init__(self, stream):
        """Build a BSMP package."""
        # if address < 0 or address > 31:
        #     raise ValueError("Address {} out of range.".format(address))
        if len(stream) < 5:
            raise ValueError("BSMP Package too short.")
        if not Package.verify_checksum(stream):
            raise ValueError("Inconsistent message. Checksum does not check.")
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
        """Package message."""
        return self._message

    @property
    def checksum(self):
        """Package checksum."""
        return self._checksum

    @staticmethod
    def calc_checksum(stream):
        """Return stream checksum."""
        counter = 0
        i = 0
        while (i < len(stream)):
            counter += ord(stream[i])
            i += 1
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        return counter

    @staticmethod
    def verify_checksum(stream):
        """Verify stream checksum."""
        counter = 0
        i = 0
        while (i < len(stream) - 1):
            counter += ord(stream[i])
            i += 1
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        if (stream[len(stream) - 1] == chr(counter)):
            return(True)
        else:
            return(False)


class Channel:
    """Serial comm with address."""

    # TODO: think about the name "address"...

    def __init__(self, serial, address):
        """Set channel."""
        self.serial = serial
        self.address = address

    def read(self):
        """Read from serial."""
        resp = self.serial.UART_read()
        if not resp:
            raise _SerialError("Serial read returned empty!")
        package = Package(resp)
        return package.message

    def write(self, message, timeout=100):
        """Write to serial."""
        # TODO: should we use a default timeout?
        stream = Package.package(self.address, message).stream
        return self.serial.UART_write(stream, timeout=timeout)

    def request(self, message, timeout=100):
        """Write and wait for response."""
        # TODO: should we use a default timeout?
        self.write(message, timeout)
        return self.read()
