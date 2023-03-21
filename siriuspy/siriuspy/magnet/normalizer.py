"""This module contains classes for current normalization."""

import re as _re
import numpy as _np

import mathphys as _mp

from .. import util as _util
from ..namesys import SiriusPVName as _SiriusPVName
from ..search import PSSearch as _PSSearch
from ..search import MASearch as _MASearch
from ..pwrsupply.csdev import get_ps_propty_database as _get_ps_propty_database

from . import util as _mutil


# beta(energy) ~ 1 approximation is more computationally efficient.
_BETA_APPROXIMATION = True
if not _BETA_APPROXIMATION:
    _GAMMA_2_GEV = _mp.constants.electron_rest_energy * _mp.units.joule_2_GeV

_MAGFUNCS = _mutil.get_magfunc_2_multipole_dict()
_KCOEFF = _mp.constants.elementary_charge / \
          _mp.constants.light_speed / \
          _mp.constants.electron_mass / \
          2 / _np.pi  # [1/(T.m)]


class _MagnetNormalizer:
    """Base class for converting magnet properties: current and strength."""

    def __init__(
            self, maname, magnet_conv_sign=-1, default_strengths_dipole=None):
        """Class constructor."""
        self._default_strengths_dipole = None
        self._brho = None
        self.default_strengths_dipole = default_strengths_dipole  # [GeV]
        self._maname = _SiriusPVName(maname) if type(maname) == str else maname
        self._psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self._psmodel = _PSSearch.conv_psname_2_psmodel(self._psnames[0])
        self._pstype = _PSSearch.conv_psname_2_pstype(self._psnames[0])
        self._magfunc = _PSSearch.conv_pstype_2_magfunc(self._pstype)
        self._excdata = _PSSearch.conv_psname_2_excdata(self._psnames[0])
        self._magnet_conv_sign = magnet_conv_sign
        self._mfmult = _MAGFUNCS[self._magfunc]
        self._psname = self._power_supplies()[0]
        self._calc_conv_coef()

    @property
    def default_strengths_dipole(self):
        return self._default_strengths_dipole

    @default_strengths_dipole.setter
    def default_strengths_dipole(self, value):
        self._default_strengths_dipole = value
        if value is not None:
            self._brho = self._get_brho(value)

    @property
    def magfunc(self):
        """Return magnet function string."""
        return self._magfunc

    @property
    def maname(self):
        """Return magnet name."""
        return self._maname

    # --- normalizer interface ---

    def conv_current_2_strength(self, currents, **kwargs):
        """Convert current to strength."""
        if currents is None:
            return None
        intfields = self._conv_current_2_intfield(currents)
        # NOTE: really necessary? ---
        if intfields is None:
            if isinstance(currents, (int, float)):
                return 0.0
            else:
                return [0.0, ] * len(currents)
        # ---
        strengths = self._conv_intfield_2_strength(intfields, **kwargs)
        strengths = self._conv_default_2_epicsdb(strengths)
        return strengths

    def conv_strength_2_current(self, strengths, **kwargs):
        """Convert strength to current."""
        strengths = self._conv_epicsdb_2_default(strengths)
        intfields = self._conv_strength_2_intfield(strengths, **kwargs)
        mft = self._mfmult
        currents = self._excdata.interp_mult2curr(
            intfields, mft['harmonic'], mft['type'])
        return currents

    # --- normalizer aux. methods ---

    def _get_brho(self, strengths_dipole=None, **kwargs):
        """Calculate appropriate brho."""
        _ = kwargs
        if strengths_dipole is None and self._brho is not None:
            return self._brho
        elif strengths_dipole is None:
            raise ValueError(
                "Missing input 'strengths_dipole' and no default value is "
                "set in attribute 'default_strengths_dipole'.")

        brho, *_ = _util.beam_rigidity(strengths_dipole)
        return brho

    def _conv_current_2_intfield(self, currents):
        mpoles = self._conv_current_2_multipoles(
            currents, only_main_harmonic=True)
        if mpoles is None:
            return None
        mfm = self._mfmult
        intfield = mpoles[mfm['type']][mfm['harmonic']]
        return intfield

    def _conv_current_2_multipoles(self, currents, only_main_harmonic=False):
        # NOTE: think about implementation of this function for magnets with
        # multiple functions...
        if currents is None:
            return None
        msum = {}
        if self._magfunc != 'dipole':
            mpoles = \
                self._excdata.interp_curr2mult(currents, only_main_harmonic)
            msum = _mutil.sum_magnetic_multipoles(msum, mpoles)
        else:
            mpoles = \
                self._excdata.interp_curr2mult(currents, only_main_harmonic)
            msum = _mutil.sum_magnetic_multipoles(msum, mpoles)
        return msum

    def _power_supplies(self):
        psname = self._maname.replace(":MA", ":PS").replace(':PM', ':PU')
        return [psname]

    # --- conversion default [rad] to epicsdb [(m|u)rad] values ---

    def _conv_values(self, values, coef):
        if isinstance(values, (int, float)):
            return coef * values
        elif isinstance(values, tuple):
            return (coef*v for v in values)
        elif isinstance(values, list):
            return [coef*v for v in values]
        elif isinstance(values, _np.ndarray):
            return coef*values
        else:
            raise ValueError()

    def _conv_default_2_epicsdb(self, values):
        return self._conv_values(values, self._coef_def2edb)

    def _conv_epicsdb_2_default(self, values):
        return self._conv_values(values, 1.0/self._coef_def2edb)

    def _calc_conv_coef(self):
        dbase = _get_ps_propty_database(self._psmodel, self._pstype)
        if 'Energy-SP' in dbase:
            dbase = dbase['Energy-SP']
        elif 'KL-SP' in dbase:
            dbase = dbase['KL-SP']
        elif 'SL-SP' in dbase:
            dbase = dbase['SL-SP']
        elif 'Kick-SP' in dbase:
            dbase = dbase['Kick-SP']
        if 'unit' in dbase:
            unit = dbase['unit'].lower()
            if unit == 'mrad':
                self._coef_def2edb = 1e3
                return
            if unit == 'urad':
                self._coef_def2edb = 1e6
                return
            if unit == 'rad':
                self._coef_def2edb = 1
                return
            if unit == 'deg':
                self._coef_def2edb = 180.0 / _np.pi
                return
        self._coef_def2edb = 1.0

    def _conv_intfield_2_strength(self, intfields, **kwargs):
        raise NotImplementedError


class DipoleNormalizer(_MagnetNormalizer):
    """Convert magnet current to strength and vice versa."""

    TYPE = 'DipoleNormalizer'

    _ref_angles = _mutil.get_nominal_dipole_angles()

    def __init__(self, maname, **kwargs):
        """Class constructor."""
        super(DipoleNormalizer, self).__init__(maname, **kwargs)
        self._set_reference_dipole_data()

    # --- normalizer aux. methods ---

    def _set_reference_dipole_data(self):
        ang = DipoleNormalizer._ref_angles
        if self._maname.sec == 'SI':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho, self._ref_beta, self._ref_gamma, *_ = \
                _util.beam_rigidity(self._ref_energy)
            # self._ref_bl_bc = - self._ref_brho * ang['SI_BC']
            # self._ref_angle = ang['SI_B1'] + ang['SI_B2']  + ang['SI_BC']
            # self._ref_bl = - self._ref_brho * self._ref_angle \
            #     - self._ref_bl_bc
            self._ref_angle = ang['SI_B1'] + ang['SI_B2']
            self._ref_bl = - self._ref_brho * self._ref_angle
        elif self._maname.sec == 'BO':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho, self._ref_beta, self._ref_gamma, *_ = \
                _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['BO']
            self._ref_bl = - self._ref_brho * self._ref_angle
        elif self._maname.sec == 'TS':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho, *_ = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TS']
            self._ref_bl = - self._ref_brho * self._ref_angle
        elif self._maname.sec == 'TB':
            self._ref_energy = 0.150  # [GeV]
            self._ref_brho, *_ = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TB']
            self._ref_bl = - self._ref_brho * self._ref_angle
        elif self._maname.sec == 'LI':
            self._ref_energy = 0.150  # [GeV]
            self._ref_brho, *_ = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['LI']
            self._ref_bl = - self._ref_brho * self._ref_angle
        else:
            raise NotImplementedError

    def _conv_strength_2_intfield(self, strengths, **kwargs):
        _ = kwargs  # throwaway arguments
        if isinstance(strengths, list):
            strengths = _np.array(strengths)
        if self._maname.sec == 'SI':
            if _BETA_APPROXIMATION:
                # 1. approximation beta(energy) ~ 1.0
                intfields = (- self._ref_angle *
                             (self._ref_brho / self._ref_energy) *
                             strengths)  # - self._ref_bl_bc)
            else:
                # 2. without approximation
                brho, *_ = _util.beam_rigidity(strengths)
                intfields = brho * (- self._ref_angle)  # - self._ref_bl_bc
        else:
            if _BETA_APPROXIMATION:
                # 1. approximation beta(energy) ~ 1.0
                intfields = (- self._ref_angle *
                             (self._ref_brho / self._ref_energy) * strengths)
            else:
                # 2. without approximation
                brho, *_ = _util.beam_rigidity(strengths)
                intfields = brho * (- self._ref_angle)

        return intfields

    def _conv_intfield_2_strength(self, intfields, **kwargs):
        if isinstance(intfields, list):
            intfields = _np.array(intfields)
        if self._maname.sec == 'SI':
            if _BETA_APPROXIMATION:
                # 1. approximation beta(energy) ~ 1.0
                total_bl = intfields  # + self._ref_bl_bc
                strengths = -self._magnet_conv_sign * \
                    ((self._ref_energy / self._ref_brho) *
                     (-total_bl) / self._ref_angle)
            else:
                # 2. without approximation
                total_bl = intfields  # + self._ref_bl_bc
                beam_rigidity = -total_bl / self._ref_angle
                alpha = (beam_rigidity / self._ref_brho) * \
                    (self._ref_gamma**2 - 1.0)/(self._ref_gamma)
                gamma = (alpha/2) + _np.sqrt(1.0 + (alpha/2)**2)
                strengths = gamma * _GAMMA_2_GEV
        else:
            if _BETA_APPROXIMATION:
                # 1. approximation beta(energy) ~ 1.0
                strengths = -self._magnet_conv_sign * \
                    ((self._ref_energy / self._ref_brho) *
                     (- intfields) / self._ref_angle)
            else:
                # 2. without approximation
                total_bl = intfields
                beam_rigidity = -total_bl / self._ref_angle
                alpha = (beam_rigidity / self._ref_brho) * \
                    (self._ref_gamma**2 - 1.0)/(self._ref_gamma)
                gamma = (alpha/2) + _np.sqrt(1.0 + (alpha/2)**2)
                strengths = gamma * _GAMMA_2_GEV

        return strengths

    def _power_supplies(self):
        return self._psnames


class MagnetNormalizer(_MagnetNormalizer):
    """Convert magnet current to strength and vice versa.

    Since we decided to match signs of Kick-Mon and direction
    of the beam kick, as we do in beam dynamic models, we have
    to treat horizontal and vertical correctors differently in the
    conversion from current to strength and vice-versa.
    """

    TYPE = 'MagnetNormalizer'

    def __init__(self, maname, **kwargs):
        """Call superclass init and initializes a dipole."""
        super(MagnetNormalizer, self).__init__(maname, **kwargs)

    def _conv_strength_2_intfield(self, strengths, **kwargs):
        if isinstance(strengths, list):
            strengths = _np.array(strengths)

        brho = self._get_brho(**kwargs)
        intfields = self._magnet_conv_sign * brho * strengths
        return intfields

    def _conv_intfield_2_strength(self, intfields, **kwargs):
        if isinstance(intfields, list):
            intfields = _np.array(intfields)

        brho = self._get_brho(**kwargs)
        if isinstance(brho, _np.ndarray):
            with _np.errstate(divide='ignore', invalid='ignore'):
                strengths = self._magnet_conv_sign * intfields / brho
                strengths[brho == 0] = 0.0
        else:
            if brho == 0:
                strengths = 0.0
            else:
                strengths = self._magnet_conv_sign * intfields / brho
        if not isinstance(intfields, (int, float)):
            if isinstance(strengths, (int, float)):
                strengths = [strengths, ] * len(intfields)
        return strengths


class APUNormalizer(_MagnetNormalizer):
    """."""

    def _conv_strength_2_intfield(self, strengths, **kwargs):
        """Convert K parameter to field amplitude.

        For APU, integrated field is just the field amplitude B * lamba [T.m].
        The strength is the K parameter:
            K ~ 93.3729/(T.m) * (lambda * B)
        """
        _ = kwargs  # throwaway arguments
        if isinstance(strengths, list):
            strengths = _np.array(strengths)

        intfields = strengths / _KCOEFF
        return intfields

    def _conv_intfield_2_strength(self, intfields, **kwargs):
        """Convert field amplitude to K parameter.

        For APU, integrated field is just the field amplitude B * lamba [T.m].
        The strength is the K parameter:
            K ~ 93.3729/(T.m) * (lambda * B)
        """
        _ = kwargs  # throwaway arguments
        if isinstance(intfields, list):
            intfields = _np.array(intfields)

        strengths = _KCOEFF * intfields
        return strengths


class TrimNormalizer(_MagnetNormalizer):
    """Convert trim magnet current to strength and vice versa."""

    TYPE = 'TrimNormalizer'

    def __init__(self, maname, **kwargs):
        """Call super and initializes a dipole and the family magnet."""
        super(TrimNormalizer, self).__init__(maname, **kwargs)

    def _conv_strength_2_intfield(self, strengths, **kwargs):
        if isinstance(strengths, list):
            strengths = _np.array(strengths)
        strengths_fam = kwargs['strengths_family']

        brho = self._get_brho(**kwargs)
        intfields = self._magnet_conv_sign * brho * (strengths - strengths_fam)
        return intfields

    def _conv_intfield_2_strength(self, intfields, **kwargs):
        if isinstance(intfields, (list, tuple)):
            intfields = _np.array(intfields)

        brho = self._get_brho(**kwargs)
        if brho == 0:
            return 0 * intfields
        strengths_trim = self._magnet_conv_sign * intfields / brho
        # integrated field in excitation data for trims is just
        # its contribution.
        strengths_fam = _np.array(kwargs['strengths_family'])
        return strengths_trim + strengths_fam
