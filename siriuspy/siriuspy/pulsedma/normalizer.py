"""Definition of a class that normalizes pulsed magnet tensions."""

from siriuspy.magnet import util as _mutil
from siriuspy.pulsedma.data import PMData as _PMData
from siriuspy.magnet.model import DipoleNormalizer


class PulsedMagnetNormalizer:
    """Calculate normalized tensions for pulsed magnets."""

    def __init__(self, maname, dipole_name):
        """Class constructor."""
        self._maname = maname
        self._data = _PMData(self._maname)
        self.dipole_name = dipole_name
        self._dipole = DipoleNormalizer(dipole_name)
        self._magfunc = self._data.magfunc(self._data.psnames[0])
        self._mfmult = _mutil.get_magfunc_2_multipole_dict()[self._magfunc]

    # ComputedPV interface
    def compute_get(self, computed_pv, updated_pv, *pvs):
        """Convert tension to strength.

        Compute strength value and compute new limits if the dipole value
        changed.
        """
        kwret = {}
        # Convert tension to strength
        value = self.conv_tension_2_strength(
            tension=pvs[0].get(), current_dipole=pvs[1].get())
        kwret["value"] = value
        # Compute new limits if the dipole current is being updated
        if self.dipole_name in updated_pv \
                or computed_pv.upper_disp_limit is None:
            low, high, lolo, hihi, lolim, hilim = self.compute_limits(*pvs)
            # print("Calculating limtis", updated_pv, lolim)
            kwret["low"] = low
            kwret["high"] = high
            kwret["lolo"] = lolo
            kwret["hihi"] = hihi
            kwret["lolim"] = lolim
            kwret["hilim"] = hilim

        return kwret

    def compute_put(self, value, *pvs):
        """Convert strength to tension."""
        tension = self.conv_strength_2_tension(
            strength=value, current_dipole=pvs[1].get())
        pvs[0].put(tension)

    def compute_limits(self, *pvs):
        """Compute limits to normalized strength."""
        high = self.conv_tension_2_strength(
            pvs[0].upper_warning_limit, pvs[1].get())
        low = self.conv_tension_2_strength(
            pvs[0].lower_warning_limit, pvs[1].get())
        if high < low:
            high, low = low, high

        hihi = self.conv_tension_2_strength(
            pvs[0].upper_alarm_limit, pvs[1].get())
        lolo = self.conv_tension_2_strength(
            pvs[0].lower_alarm_limit, pvs[1].get())
        if hihi < lolo:
            hihi, lolo = lolo, hihi

        hilim = self.conv_tension_2_strength(
            pvs[0].upper_disp_limit, pvs[1].get())
        lolim = self.conv_tension_2_strength(
            pvs[0].lower_disp_limit, pvs[1].get())
        if hilim < lolim:
            hilim, lolim = lolim, hilim

        return (low, high, lolo, hihi, lolim, hilim)

    # Public interface
    def conv_tension_2_strength(self, tension, current_dipole):
        """Normalize tension into kick."""
        # Get integrated field
        if tension is None:
            return 0
        intfield = self._conv_tension_2_intfield(tension)
        # Get magnetic rigidity
        brho = self._dipole._get_brho(current_dipole)
        try:
            return intfield/brho
        except ZeroDivisionError:
            return 0

    def conv_strength_2_tension(self, strength, current_dipole):
        """Denormalize the strength returning the tension."""
        intfield = self._conv_strength_2_intfield(strength, current_dipole)
        mf = self._mfmult
        excdata = self._data.excdata(self._data.psnames[0])
        tension = excdata.interp_mult2curr(intfield, mf["harmonic"],
                                           mf["type"])
        return tension

    # Private methods
    def _conv_tension_2_multipoles(self, tension):
        msum = {}
        excdata = self._data.excdata(self._data.psnames[0])
        m = excdata.interp_curr2mult(tension)
        msum = _mutil.sum_magnetic_multipoles(msum, m)
        return msum

    def _conv_tension_2_intfield(self, tension):
        m = self._conv_tension_2_multipoles(tension)
        mf = self._mfmult
        intfield = m[mf["type"]][mf["harmonic"]]
        return intfield

    def _conv_strength_2_intfield(self, strength, current_dipole):
        brho = self._dipole._get_brho(current_dipole)
        return strength*brho
