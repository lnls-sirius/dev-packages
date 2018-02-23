"""This module contain classes for normalizing currents."""
import re as _re

from siriuspy import util as _util
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.magnet import util as _mutil
from siriuspy.magnet.data import MAData as _MAData
import numpy as _np
from siriuspy.computer import Computer as _Computer


_magfuncs = _mutil.get_magfunc_2_multipole_dict()
_electron_rest_energy = _util.get_electron_rest_energy()

_is_dipole = _re.compile(".*:[A-Z]{2}-B.*:.+$")
_is_fam = _re.compile(".*[A-Z]{2}-Fam:[A-Z]{2}-.+$")


class _MagnetNormalizer(_Computer):
    """Base class for converting magnet properties: current and strength."""

    def __init__(self, maname, magnet_conv_sign=-1):
        """Class constructor."""
        self._maname = _SiriusPVName(maname) if type(maname) == str else maname
        self._madata = _MAData(maname=maname)
        self._magfunc = self._madata.magfunc(self._madata.psnames[0])
        self._magnet_conv_sign = magnet_conv_sign
        self._mfmult = _magfuncs[self._magfunc]
        self._psname = self._power_supplies()[0]

    # --- computer interface ---

    def compute_put(self, computed_pv, value):
        """Put strength value."""
        # convert strength to current
        kwargs = self._get_params(computed_pv)
        current = self.conv_strength_2_current(value, **kwargs)
        # first PV must be actual magnet current
        computed_pv.pvs[0].put(current)

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Convert current to strength."""
        kwret = {}
        # convert current to strength
        kwret["value"] = self._compute_new_value(computed_pv,
                                                 updated_pv_name, value)

        lims = self._compute_limits(computed_pv, updated_pv_name)
        if lims is not None:
            kwret["hihi"] = lims[0]
            kwret["high"] = lims[1]
            kwret["hilim"] = lims[2]
            kwret["lolim"] = lims[3]
            kwret["low"] = lims[4]
            kwret["lolo"] = lims[5]

        return kwret

    def compute_limits(self, computed_pv):
        """Compute limits to normalized strength."""
        kwargs = self._get_params(computed_pv)
        high = self.conv_current_2_strength(
            self._madata.splims['HIGH'], **kwargs)
        low = self.conv_current_2_strength(
            self._madata.splims['LOW'], **kwargs)
        if high < low:
            high, low = low, high

        hihi = self.conv_current_2_strength(
            self._madata.splims["HIHI"], **kwargs)
        lolo = self.conv_current_2_strength(
            self._madata.splims["LOLO"], **kwargs)
        if hihi < lolo:
            hihi, lolo = lolo, hihi

        hilim = self.conv_current_2_strength(
            self._madata.splims["HOPR"], **kwargs)
        lolim = self.conv_current_2_strength(
            self._madata.splims["LOPR"], **kwargs)
        if hilim < lolim:
            hilim, lolim = lolim, hilim

        return hihi, high, hilim, lolim, low, lolo

    # --- normalizer interface ---

    def conv_current_2_strength(self, currents, **kwargs):
        intfields = self._conv_current_2_intfield(currents)
        if intfields is None:
            return 0.0
        strengths = self._conv_intfield_2_strength(intfields, **kwargs)
        return strengths

    def conv_strength_2_current(self, strengths, **kwargs):
        intfields = self._conv_strength_2_intfield(strengths, **kwargs)
        mf = self._mfmult
        # excdata = self._get_main_excdata()
        excdata = self._madata.excdata(self._psname)
        currents = excdata.interp_mult2curr(
            intfields, mf['harmonic'], mf['type'])
        return currents

    # --- computer aux. methods ---

    def _compute_limits(self, computed_pv):
        raise NotImplementedError

    def _get_params(self, computed_pv):
        if len(computed_pv.pvs) == 1:
            return {}
        elif len(computed_pv.pvs) == 2:
            return {"strengths_dipole": computed_pv.pvs[1].get()}
        elif len(computed_pv.pvs) == 3:
            return {"strengths_dipole": computed_pv.pvs[1].get(),
                    "strengths_family": computed_pv.pvs[2].get()}

    def _compute_new_value(self, computed_pv, updated_pv_name, value):
        # return new computed value
        if len(computed_pv.pvs) == 1:  # Dipole
            return self.conv_current_2_strength(value)
        elif len(computed_pv.pvs) == 2:  # Standard Magnet
            if _is_dipole.match(updated_pv_name):  # Use regexp?
                current = computed_pv.pvs[0].get()
                strength_dipole = value
            else:
                current = value
                strength_dipole = computed_pv.pvs[1].get()
            return self.conv_current_2_strength(
                currents=current, strengths_dipole=strength_dipole)
        elif len(computed_pv.pvs) == 3:  # Trim Magnet
            if not _is_fam.match(updated_pv_name):  # Use Regexp?
                current = value
                strength_dipole = computed_pv.pvs[1].get()
                strength_family = computed_pv.pvs[2].get()
            elif _is_dipole.match(updated_pv_name):
                current = computed_pv.pvs[0].get()
                strength_dipole = value
                strength_family = computed_pv.pvs[2].get()
            else:
                current = computed_pv.pvs[0].get()
                strength_dipole = computed_pv.pvs[1].get()
                strength_family = value
            return self.conv_current_2_strength(
                currents=current,
                strengths_dipole=strength_dipole,
                strengths_family=strength_family)

    # --- normalizer aux. methods ---

    def _conv_current_2_intfield(self, currents):
        m = self._conv_current_2_multipoles(currents)
        if m is None:
            return None
        mf = self._mfmult
        intfield = m[mf['type']][mf['harmonic']]
        return intfield

    def _conv_current_2_multipoles(self, currents):
        # TODO: think about implementation of this function: magnets with
        # multiple functions...
        if currents is None:
            return None
        msum = {}
        if self._magfunc != 'dipole':
            # for psname in self._madata.psnames:
            excdata = self._madata.excdata(self._psname)
            m = excdata.interp_curr2mult(currents)
            msum = _mutil.sum_magnetic_multipoles(msum, m)
        else:
            excdata = self._madata.excdata(self._psname)
            m = excdata.interp_curr2mult(currents)
            msum = _mutil.sum_magnetic_multipoles(msum, m)
        return msum

    def _get_energy(self, current_dipole):
        return self._dipole.conv_current_2_strength(currents=current_dipole)

    def _get_brho(self, currents_dipole):
        """Get Magnetic Rigidity."""
        if currents_dipole is None:
            return 0  # TODO: is this really necessary?! in what case?
        energies = self._get_energy(currents_dipole)
        brho, *_ = _util.beam_rigidity(energies)
        return brho

    def _power_supplies(self):
        psname = self._maname.replace(":MA", ":PS").replace(':PM', ':PU')
        return [psname]


class DipoleNormalizer(_MagnetNormalizer):
    """Convert magnet current to strength and vice versa."""

    _ref_angles = _mutil.get_nominal_dipole_angles()

    def __init__(self, maname, **kwargs):
        """Class constructor."""
        super(DipoleNormalizer, self).__init__(maname, **kwargs)
        self._set_reference_dipole_data()

    # --- computer interface ---

    def _compute_limits(self, computed_pv, updated_pv_name):
        """Compute limits to normalized strength."""
        if computed_pv.upper_alarm_limit is None:
            # initialization of limits
            # return _MagnetNormalizer.compute_limits(self, computed_pv)
            return self.compute_limits(computed_pv)
        else:
            # limits have already been calculated.
            return None

    # --- normalizer aux. methods ---

    def _set_reference_dipole_data(self):
        ang = DipoleNormalizer._ref_angles
        if self._maname.sec == 'SI':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho, *_ = _util.beam_rigidity(self._ref_energy)
            self._ref_BL_BC = - self._ref_brho * ang['SI_BC']
            self._ref_angle = ang['SI_B1'] + ang['SI_B2'] + ang['SI_BC']
            self._ref_BL = - self._ref_brho * self._ref_angle - self._ref_BL_BC
        elif self._maname.sec == 'BO':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho, *_ = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['BO']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif self._maname.sec == 'TS':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho, *_ = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TS']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif self._maname.sec == 'TB':
            self._ref_energy = 0.150  # [GeV]
            self._ref_brho, *_ = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TB']
            self._ref_BL = - self._ref_brho * self._ref_angle
        else:
            raise NotImplementedError

    def _get_energy(self, currents_dipole):
        return self.conv_current_2_strength(currents=currents_dipole)

    def _conv_strength_2_intfield(self, strengths, **kwargs):
        if isinstance(strengths, list):
            strengths = _np.array(strengths)
        if self._maname.sec == 'SI':
            intfields = (- self._ref_angle *
                         (self._ref_brho / self._ref_energy)
                         * strengths - self._ref_BL_BC)
        else:
            intfields = (- self._ref_angle *
                         (self._ref_brho / self._ref_energy)
                         * strengths)
        return intfields

    def _conv_intfield_2_strength(self, intfields, **kwargs):
        if isinstance(intfields, list):
            intfields = _np.array(intfields)
        if self._maname.sec == 'SI':
            strengths = -self._magnet_conv_sign * \
                        ((self._ref_energy / self._ref_brho) *
                         (- intfields - self._ref_BL_BC) / self._ref_angle)
        else:
            strengths = -self._magnet_conv_sign * \
                        ((self._ref_energy / self._ref_brho) *
                         (-intfields) / self._ref_angle)
        # if isinstance(strengths, _np.ndarray):
        #     sel = strengths < _electron_rest_energy
        #     strengths[sel] = _electron_rest_energy
        # else:
        #     if strengths < _electron_rest_energy:
        #         strengths = _electron_rest_energy
        return strengths

    def _power_supplies(self):
        return self._madata.psnames


class MagnetNormalizer(_MagnetNormalizer):
    """Convert magnet current to strength and vice versa.

    Since we decided to match signs of Kick-Mon and direction
    of the beam kick, as we do in beam dynamic models, we have
    to treat horizontal and vertical correctors differently in the
    conversion from current to strength and vice-versa.
    """

    def __init__(self, maname, dipole_name, magnet_conv_sign=-1.0, **kwargs):
        """Call super and initializes a dipole."""
        super(MagnetNormalizer, self).__init__(maname, **kwargs)
        self._dipole = DipoleNormalizer(dipole_name, **kwargs)
        # self._magnet_conv_sign = magnet_conv_sign

    # --- computer interface ---

    def _compute_limits(self, computed_pv, updated_pv_name):
        """Compute limits to normalized strength."""
        # print('here: ', self._maname, computed_pv.pvname, computed_pv.upper_alarm_limit)
        if computed_pv.upper_alarm_limit is None:
            # initialization of limits
            return self.compute_limits(computed_pv)
        else:
            # check if limits ready need calculation
            if updated_pv_name is not None and 'Energy' in updated_pv_name:
                return self.compute_limits(computed_pv)
            else:
                return None

    def _conv_strength_2_intfield(self, strengths, **kwargs):
        if isinstance(strengths, list):
            strengths = _np.array(strengths)
        brhos, *_ = _util.beam_rigidity(kwargs['strengths_dipole'])
        # brhos = _np.array(brhos)  # TODO: necessary?
        intfields = self._magnet_conv_sign * brhos * strengths
        return intfields

    def _conv_intfield_2_strength(self, intfields, **kwargs):
        if isinstance(intfields, list):
            intfields = _np.array(intfields)
        brhos, *_ = _util.beam_rigidity(kwargs['strengths_dipole'])
        if isinstance(brhos, _np.ndarray):
            strengths = self._magnet_conv_sign * intfields / brhos
            strengths[brhos == 0] = 0.0
        else:
            if brhos == 0:
                strengths = 0.0
            else:
                strengths = self._magnet_conv_sign * intfields / brhos
        return strengths


class TrimNormalizer(_MagnetNormalizer):
    """Convert trim magnet current to strength and vice versa."""

    def __init__(self, maname, dipole_name, family_name, magnet_conv_sign=-1.0,
                 **kwargs):
        """Call super and initializes a dipole and the family magnet."""
        super(TrimNormalizer, self).__init__(maname, **kwargs)
        self._dipole = DipoleNormalizer(dipole_name, **kwargs)
        self._fam = MagnetNormalizer(family_name, dipole_name, **kwargs)

    # --- computer interface ---

    def _compute_limits(self, computed_pv, updated_pv_name):
        """Compute limits to normalized strength."""
        if computed_pv.upper_alarm_limit is None:
            # initialization of limits
            return self.compute_limits(computed_pv)
        else:
            # check if limits ready need calculation
            if 'Energy' in updated_pv_name or 'KL' in updated_pv_name:
                return self.compute_limits(computed_pv)
            else:
                return None

    def _conv_strength_2_intfield(self, strengths, **kwargs):
        if isinstance(strengths, list):
            strengths = _np.array(strengths)
        # strengths_fam = self._fam.conv_current_2_strength(
        #     currents=kwargs["strengths_family"],
        #     currents_dipole=kwargs["strengths_dipole"])
        strengths_fam = kwargs['strengths_family']
        brhos, *_ = _util.beam_rigidity(kwargs['strengths_dipole'])
        intfields = - brhos * (strengths - strengths_fam)
        return intfields

    def _conv_intfield_2_strength(self, intfields, **kwargs):
        if isinstance(intfields, list):
            intfields = _np.array(intfields)
        brhos, *_ = _util.beam_rigidity(kwargs['strengths_dipole'])
        if brhos == 0:
            return 0
        strengths_trim = - intfields / brhos
        # strengths_fam = self._fam.conv_current_2_strength(
        #     currents=kwargs["currents_family"],
        #     currents_dipole=kwargs["currents_dipole"])
        strengths_fam = _np.array(kwargs['strengths_family'])
        return strengths_trim + strengths_fam
