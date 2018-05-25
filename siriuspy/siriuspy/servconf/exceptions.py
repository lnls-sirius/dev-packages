"""Module with ConfigServer exceptions."""


class SrvError(Exception):
    """General exception in ConfigSrv."""

    pass


class SrvCouldNotConnect(SrvError):
    """Could not connect with ConfigServer."""

    pass


class SrvConfigError(SrvError):
    """General exception for config manipulations."""

    pass


class SrvConfigInvalidName(SrvConfigError):
    """Configuration name not defined."""

    pass


class SrvConfigFormatError(SrvConfigError):
    """Configuration value with inconsistent format."""

    pass


class SrvConfigNotFound(SrvConfigError):
    """Configuration not found in server."""

    pass


class SrvConfigConflict(SrvConfigError):
    """Configuration conflict."""

    pass


class SrvMetadataInvalid(SrvError):
    """Invalid metadata."""

    pass
