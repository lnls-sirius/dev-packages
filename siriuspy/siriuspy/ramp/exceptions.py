"""Module with ramp exceptions."""


class RampError(Exception):
    """Gerenarl exception in Ramp."""

    pass


class RampCouldNotConnect(RampError):
    """Could not connect with server."""

    pass


class RampConfigError(RampError):
    """General exception for config manipulations."""

    pass


class RampConfigNameNotDefined(RampConfigError):
    """Configuration name not defined."""

    pass


class RampConfigFormatError(RampConfigError):
    """Configuration value with inconsistent format."""

    pass


class RampConfigNotFound(RampConfigError):
    """Configuration not found in server."""

    pass


class RampMetadataInvalid(RampError):
    """Invalid metadata."""

    pass
