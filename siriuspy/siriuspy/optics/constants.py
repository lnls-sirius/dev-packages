"""Accelerator lattice and optics constants."""

from mathphys import beam_optics as _bopts


class _ClassProperty:
    """."""

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        return self.func(cls)


class Accelerator:
    """Accelerator."""

    sector = ''
    length = 0.0  # [m]


class Ring(Accelerator):
    """Ring."""

    @_ClassProperty
    def circumference(cls):
        """Ring circumference [m]."""
        return cls.length

    @_ClassProperty
    def beam_rigidity(cls):
        """Beam ridigity."""
        brho = _bopts.beam_rigidity(energy=cls.beam_energy)
        return brho

    @_ClassProperty
    def rev_period(cls):
        """Return revolution period [s]."""
        _, velocity, *_ = cls.beam_rigidity
        return cls.circumference / velocity

    @_ClassProperty
    def rev_frequency(cls):
        """Return revolution frequency [Hz]."""
        _, velocity, *_ = cls.beam_rigidity
        return velocity / cls.circumference  # [Hz]


class SI(Ring):
    """SI."""

    sector = 'SI'
    beam_energy = 3.0  # [GeV]
    length = 518.396  # [m]
    harmonic_number = 864


class BO(Ring):
    """BO."""

    sector = 'BO'
    beam_energy = 0.150  # [GeV] - Low Energy
    length = 496.396  # [m]
    harmonic_number = 828
