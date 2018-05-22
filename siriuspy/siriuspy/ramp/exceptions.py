"""Module with ConfigServer exceptions."""


# TODO: this is a general class and could be moved to servconf


class SrvError(Exception):
    """General exception in ConfigSrv."""

    pass


class SrvCouldNotConnect(SrvError):
    """Could not connect with ConfigServer."""

    pass


class SrvConfigError(SrvError):
    """General exception for config manipulations."""

    pass


class SrvConfigNameNotDefined(SrvConfigError):
    """Configuration name not defined."""

    pass


class SrvConfigFormatError(SrvConfigError):
    """Configuration value with inconsistent format."""

    pass


class SrvConfigNotFound(SrvConfigError):
    """Configuration not found in server."""

    pass


class SrvMetadataInvalid(SrvError):
    """Invalid metadata."""

    pass
