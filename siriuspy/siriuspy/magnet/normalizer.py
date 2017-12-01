"""This module contain classes for normalizing currents."""


from siriuspy import util as _util
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.magnet import util as _mutil
from siriuspy.magnet.data import MAData as _MAData
import numpy as _np

_magfuncs = _mutil.get_magfunc_2_multipole_dict()


class _MagnetNormalizer:
    """Base class for converting magnet properties: current and strength."""

    def __init__(self, maname, magnet_conv_sign=-1):
        """Class constructor."""
        self._maname = _SiriusPVName(maname) if type(maname) == str else maname
        self._madata = _MAData(maname=self._maname)
        self._magfunc = self._madata.magfunc(self._madata.psnames[0])
        self._magnet_conv_sign = magnet_conv_sign
        self._mfmult = _magfuncs[self._magfunc]
        self._psname = self._power_supplies()[0]

    def _conv_current_2_multipoles(self, currents):
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

    def _conv_current_2_intfield(self, currents):
        m = self._conv_current_2_multipoles(currents)
        if m is None:
            return None
        mf = self._mfmult
        intfield = m[mf['type']][mf['harmonic']]
        return intfield

    def _get_energy(self, current_dipole):
        return self._dipole.conv_current_2_strength(currents=current_dipole)

    def _get_brho(self, currents_dipole):
        """Get Magnetic Rigidity."""
        if currents_dipole is None:
            return 0
        energies = self._get_energy(currents_dipole)
        brho, *_ = _util.beam_rigidity(energies)
        return brho

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

    def _set_reference_dipole_data(self):
        ang = DipoleNormalizer._ref_angles
        if self._maname.section == 'SI':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho, *_ = _util.beam_rigidity(self._ref_energy)
            self._ref_BL_BC = - self._ref_brho * ang['SI_BC']
            self._ref_angle = ang['SI_B1'] + ang['SI_B2'] + ang['SI_BC']
            self._ref_BL = - self._ref_brho * self._ref_angle - self._ref_BL_BC
        elif self._maname.section == 'BO':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho, *_ = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['BO']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif self._maname.section == 'TS':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho, *_ = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TS']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif self._maname.section == 'TB':
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
        if self._maname.section == 'SI':
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
        if self._maname.section == 'SI':
            strengths = -self._magnet_conv_sign * \
                        ((self._ref_energy / self._ref_brho) *
                         (- intfields - self._ref_BL_BC) / self._ref_angle)
        else:
            strengths = -self._magnet_conv_sign * \
                        ((self._ref_energy / self._ref_brho) *
                         (-intfields) / self._ref_angle)
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

    def _conv_strength_2_intfield(self, strengths, **kwargs):
        if isinstance(strengths, list):
            strengths = _np.array(strengths)
        brhos = self._get_brho(currents_dipole=kwargs['currents_dipole'])
        intfields = self._magnet_conv_sign * brhos * strengths
        return intfields

    def _conv_intfield_2_strength(self, intfields, **kwargs):
        if isinstance(intfields, list):
            intfields = _np.array(intfields)
        brhos = self._get_brho(currents_dipole=kwargs['currents_dipole'])
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

    def _conv_strength_2_intfield(self, strengths, **kwargs):
        if isinstance(strengths, list):
            strengths = _np.array(strengths)
        strengths_fam = self._fam.conv_current_2_strength(
            currents=kwargs["currents_family"],
            currents_dipole=kwargs["currents_dipole"])
        brhos = self._get_brho(currents_dipole=kwargs['currents_dipole'])
        intfields = - brhos * (strengths - strengths_fam)
        return intfields

    def _conv_intfield_2_strength(self, intfields, **kwargs):
        if isinstance(intfields, list):
            intfields = _np.array(intfields)
        brhos = self._get_brho(currents_dipole=kwargs['currents_dipole'])
        if brhos == 0:
            return 0
        strengths_trim = - intfields / brhos
        strengths_fam = self._fam.conv_current_2_strength(
            currents=kwargs["currents_family"],
            currents_dipole=kwargs["currents_dipole"])
        return strengths_trim + strengths_fam
