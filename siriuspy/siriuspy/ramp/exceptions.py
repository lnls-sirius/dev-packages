"""Module with Ramp exceptions."""


class RampError(ValueError):
    """General Ramp Error."""


class RampInvalidDipoleWfmParms(RampError):
    """Invalid Dipole waveform parameters."""


class RampInvalidNormConfig(RampError):
    """Invalid normalized configuration."""


class RampInvalidRFParms(RampError):
    """Invalid RF parameters."""
