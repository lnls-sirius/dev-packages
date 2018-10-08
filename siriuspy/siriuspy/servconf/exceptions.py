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


class SrvConfigAlreadyExists(SrvConfigError):
    """A configuration with the given name already exists in server."""

    pass
