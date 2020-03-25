"""Accelerator lattice and optics constants."""


class Accelerator:
    """Accelerator."""


class Ring(Accelerator):
    """Ring."""


class SI(Ring):
    """SI."""

    length = 518.396  # [m]
    circumference = length
    harmonic_number = 864


class BO(Ring):
    """BO."""

    length = 496.396  # [m]
    circumference = length
    harmonic_number = 828
