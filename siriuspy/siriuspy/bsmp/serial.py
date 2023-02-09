"""BSMP serial communications classes."""
import abc
import struct as _struct
import typing
from threading import Lock as _Lock

from .exceptions import SerialErrCheckSum as _SerialErrCheckSum
from .exceptions import SerialErrEmpty as _SerialErrEmpty
from .exceptions import SerialErrMsgShort as _SerialErrMsgShort
from .exceptions import SerialErrPckgLen as _SerialErrPckgLen


class IOInterface(metaclass=abc.ABCMeta):
    """Base class for I/O"""

    @abc.abstractmethod
    def open(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def UART_read(self) -> typing.List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def UART_write(self, stream, timeout: float) -> typing.Optional[typing.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def UART_request(self, stream, timeout: float) -> typing.Optional[typing.List[str]]:
        raise NotImplementedError


class Message:
    """BSMP Message.

    Command: command id; 1 byte;
    Load Size: payload size in bytes; 2 bytes (big endian);
    Load: 0..65535 bytes.
    """

    # TODO: indicate somehow that stream is a char stream.

    # Constructors
    def __init__(self, stream: typing.List[str]):
        """Build a BSMP message."""
        if len(stream) < 3:
            raise _SerialErrMsgShort(
                f"BSMP Message too short (stream: {stream}).")
        self._stream: typing.List[str] = stream
        self._cmd: int = ord(stream[0])

    def __eq__(self, other) -> bool:
        """Compare messages."""
        return self._stream == other.stream

    @classmethod
    def message(
        cls,
        cmd: int,
        payload: typing.Optional[typing.List[str]] = None
    ):
        """Build a Message object from a byte stream."""
        if payload and not isinstance(payload, list):
            # TODO: should be create serial exceptions here too?
            raise TypeError("Load must be a list.")
        if payload and len(payload) > 65535:
            # TODO: should be create serial exceptions here too?
            raise ValueError("Load must be smaller than 65535.")

        stream: typing.List[str] = []

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
    def stream(self) -> typing.List[str]:
        """Return stream."""
        return self._stream

    @property
    def cmd(self) -> int:
        """Command ID."""
        return self._cmd

    @property
    def size(self) -> int:
        """Load size."""
        return _struct.unpack('>H', bytes(map(ord, self._stream[1:3])))[0]

    @property
    def payload(self) -> typing.List[str]:
        """Message payload."""
        return self._stream[3:]


class Package:
    """BSMP Package.

    Address: 1 byte, 0..31
    Message: no limit
    Checksum: package checksum
    """

    def __init__(
        self,
        stream: typing.List[str]
    ):
        """Build a BSMP package."""
        if len(stream) < 5:
            raise _SerialErrPckgLen(
                f"BSMP Package too short (stream: {stream}).")
        if not Package.verify_checksum(stream):
            raise _SerialErrCheckSum(
                f"Inconsistent message. Checksum does not check (stream: {stream}).")

        self._stream: typing.List[str] = stream
        self._address: int = ord(stream[0])  # 0 to 31
        self._message: Message = Message(stream[1:-1])
        self._checksum: int = ord(stream[-1])

    @classmethod
    def package(cls, address: int, message: Message):
        """Build a Package object from a byte stream."""
        # Return new package
        stream: typing.List[str] = []
        stream.append(chr(address))
        stream.extend(message.stream)
        chksum = cls.calc_checksum(stream)
        stream.append(chr(chksum))
        return cls(stream)

    # API
    @property
    def stream(self) -> typing.List[str]:
        """Stream."""
        return self._stream

    @property
    def address(self) -> int:
        """Receiver node serial address."""
        return self._address

    @property
    def message(self) -> Message:
        """Return package message."""
        return self._message

    @property
    def checksum(self) -> int:
        """Return package checksum."""
        return self._checksum

    @staticmethod
    def calc_checksum(stream) -> int:
        """Return stream checksum."""
        streambytes = [ord(s) for s in stream]
        counter = sum(streambytes)
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        return counter

    @staticmethod
    def verify_checksum(stream: typing.List[str]) -> bool:
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

    The channel is defined by an IOInterface object and recipient
    address.
    """

    # TODO: should we remove use of default timeout values. It is dangerous!
    LOCK: typing.Optional[_Lock] = None

    def __init__(self, iointerf: IOInterface, address: int):
        """Set channel."""
        self._iointerf: IOInterface = iointerf  # IOInterface object to communicate with bsmp device
        self._address: int = address  # address of recipient device.
        self._size_counter: int = 0  # stream size counter [bytes]

    @property
    def iointerf(self) -> IOInterface:
        """Return IOInterface serial communication object."""
        return self._iointerf

    @property
    def address(self) -> int:
        """Return attached bsmp device id."""
        return self._address

    @property
    def size_counter(self) -> int:
        """Return stream size of last request."""
        return self._size_counter

    def size_counter_reset(self) -> None:
        """Reset stream size counter."""
        self._size_counter = 0

    def read(self) -> Message:
        """Read from serial."""
        resp = self.iointerf.UART_read()
        if not resp:
            raise _SerialErrEmpty("Serial read returned empty!")
        package = Package(resp)
        self._size_counter += len(package.stream)
        return package.message

    def write(self, message: Message, timeout: float = 100):
        """Write to serial. :param timeout [ms]"""
        stream = Package.package(self._address, message).stream
        response = self.iointerf.UART_write(stream, timeout=timeout)
        self._size_counter += len(stream)
        return response

    def request_(self, message: Message, timeout: float = 100) -> Message:
        """:param timeout [ms]"""
        stream = Package.package(self._address, message).stream

        if Channel.LOCK is None:
            response = self.iointerf.UART_request(stream, timeout=timeout)
        else:
            with Channel.LOCK:
                response = self.iointerf.UART_request(stream, timeout=timeout)

        self._size_counter += len(stream)

        if not response:
            raise _SerialErrEmpty("Serial read returned empty!")

        package = Package(response)
        self._size_counter += len(package.stream)
        return package.message

    def request(self, message: Message, timeout: float = 100, read_flag: bool = True) -> typing.Optional[Message]:
        """Write and wait for response. :param timeout [ms]"""
        response: typing.Optional[Message] = None

        if read_flag:
            response = self.request_(message, timeout)
        else:
            self.write(message, timeout)

        return response

    @staticmethod
    def create_lock() -> None:
        """."""
        Channel.LOCK = _Lock()
