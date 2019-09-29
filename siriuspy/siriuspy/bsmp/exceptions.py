"""BSMP exceptions."""


class SerialError(Exception):
    """Exception raised when there's a problem with serial."""


class SerialErrEmpty(SerialError):
    """Exception raised when empty message."""


class SerialErrCheckSum(SerialError):
    """Exception raised when there'a problem with checksum."""


class SerialErrPckgLen(SerialError):
    """Exception raised when there'a problem with package length."""


class SerialErrMsgShort(SerialError):
    """Exception raised when message is too short."""


class SerialAnomResp(SerialError):
    """Exception raised when response is not the expected one."""
