"""Accelerator lattice and optics constants."""


class Accelerator:
    """Accelerator."""

class Ring(Accelerator):
    """Ring."""


class SI(Ring):
    """SI."""

    sector = 'SI'
    length = 518.396  # [m]
    circumference = length
    harmonic_number = 864


class BO(Ring):
    """BO."""

    sector = 'BO'
    length = 496.396  # [m]
    circumference = length
    harmonic_number = 828
