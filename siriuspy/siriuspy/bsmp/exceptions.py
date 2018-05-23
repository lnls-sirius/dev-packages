"""BSMP exceptions."""


class SerialError(Exception):
    """Exception raised when there's a problem with serial."""

    pass


class SerialErrEmpty(SerialError):
    """Exception raised when empty message."""

    pass


class SerialErrCheckSum(SerialError):
    """Exception raised when there'a problem with checksum."""

    pass


class SerialErrPckgLen(SerialError):
    """Exception raised when there'a problem with package length."""

    pass


class SerialErrMsgShort(SerialError):
    """Exception raised when message is too short."""

    pass
