"""Module with Ramp exceptions."""

from siriuspy.servconf.exceptions import SrvConfigError as _SrvConfigError


class RampError(_SrvConfigError):
    """General Ramp Error."""

    pass


class RampInvalidDipoleWfmParms(RampError):
    """Invalid Dipole waveform parameters."""

    pass


class RampInvalidNormConfig(RampError):
    """Invalid normalized configuration."""

    pass


class RampInvalidRFParms(RampError):
    """Invalid RF parameters."""

    pass
