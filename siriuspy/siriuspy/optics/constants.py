"""Accelerator lattice and optics constants."""

from mathphys import beam_optics as _bopts

from ..util import ClassProperty as _ClassProperty


class Accelerator:
    """Accelerator."""

    sector = ''
    length = 0.0  # [m]

    @_ClassProperty
    def velocity(cls):
        """Beam velocity [m/s]."""
        _, velocity, *_ = _bopts.beam_rigidity(energy=cls.beam_energy)
        return velocity


class TLine(Accelerator):
    """Transport line."""


class Ring(Accelerator):
    """Ring."""

    @_ClassProperty
    def circumference(cls):
        """Ring circumference [m]."""
        return cls.length

    @_ClassProperty
    def rev_period(cls):
        """Return revolution period [s]."""
        velocity = cls.velocity
        return cls.circumference / velocity

    @_ClassProperty
    def rev_frequency(cls):
        """Return revolution frequency [Hz]."""
        velocity = cls.velocity
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


class TB(TLine):
    """TB."""

    sector = 'TB'
    beam_energy = 0.150  # [GeV]
    length = 21.2477  # [m]


class TS(TLine):
    """TS."""

    sector = 'TS'
    beam_energy = 3  # [GeV]
    length = 26.8933  # [m]
