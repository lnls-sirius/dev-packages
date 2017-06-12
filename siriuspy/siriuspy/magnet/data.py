
import math as _math
from abc import abstractmethod as _abstractmethod
from abc import ABCMeta as _ABCMeta
import siriuspy.util as _util
from siriuspy.search import MASearch as _MASearch
import siriuspy.servweb as _web
from siriuspy.namesys import Filter as _Filter
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.csdevice.pwrsupply import get_ma_propty_database as _get_ma_propty_database

class MAData:

    def __init__(self, maname):
        self._maname = maname
        self._splims_unit = _MASearch.get_splims_unit()
        psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self._propty_databases = _get_ma_propty_database(self._maname)
        self._psdata = {}
        for psname in psnames:
            self._psdata[psname] = _PSData(psname=psname)

    @property
    def maname(self):
        return self._maname

    @property
    def splims_unit(self):
        return self.splims_unit

    @property
    def psnames(self):
        return list(self._psdata.keys())

    def magfunc(self, psname):
        return self._psdata[psname].magfunc

    def excdata(self, psname):
        return self._psdata[psname].excdata

    def __getitem__(self, psname):
        return self._psdata[psname]

    def get_database(self, psname):
        return self._propty_databases[psname]


class MAStrengthBase(metaclass=_ABCMeta):

    _dipoles_maname = {
        'SI':'SI-Fam:MA-B1B2',
        'TS':'TS-Fam:MA-B',
        'BO':'BO-Fam:MA-B',
        'TB':'TB-Fam:MA-B',
    }

    def __init__(self, maname=None):
        self._maname = maname
        self._madata = MAData(maname=self._maname)
        self._psnames = self._madata.psnames
        self._excdata = self._madata.excdata(self._psnames[0])

    @staticmethod
    def get_dipole_sector_maname(section=None, maname=None):
        if section is None:
            pvname = _SiriusPVName(maname)
            section = pvname.section
        return section, MAStrengthBase._dipoles_maname[section]

    @_abstractmethod
    def conv_current_2_strength(self, current, **kwargs):
        pass

    @_abstractmethod
    def conv_strength_2_current(self, strength, **kwargs):
        pass


class MAStrengthDip(MAStrengthBase):

    _ref_angles = {
        'SI_BC': _math.radians(4.2966),
        'SI_B1': _math.radians(2.7553),
        'SI_B2': _math.radians(4.0964),
        'TS'   : _math.radians(5.3333),
        'BO'   : _math.radians(7.2000),
        'TB'   : _math.radians(15.000),
    }

    def __init__(self, section=None, **kwargs):
        section, maname = self.get_dipole_sector_maname(section=section, maname=kwargs.get('maname',None))
        self._section = section
        super().__init__(maname=maname)
        self._set_reference_dipole_data(self._section)

    def _set_reference_dipole_data(self, section):
        ang = MAStrengthDip._ref_angles
        if section == 'SI':
            self._ref_energy = 3.0 #[GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_BL_BC =  - self._ref_brho * ang['SI_BC']
            self._ref_angle = ang['SI_B1'] + ang['SI_B2'] + ang['SI_BC']
            self._ref_BL = - self._ref_brho * self._ref_angle - self._ref_BL_BC
        elif section == 'BO':
            self._ref_energy = 3.0 #[GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['BO']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif section == 'TS':
            self._ref_energy = 3.0 #[GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TS']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif section == 'TB':
            self._ref_energy = 0.150 #[GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TB']
            self._ref_BL = - self._ref_brho * self._ref_angle
        else:
            raise NotImplementedError

    def conv_current_2_strength(self, current, **kwargs):
        """Return dipole strength [Energy in GeV]."""
        multipoles = self._excdata.interp_curr2mult(current)
        m_type = self._excdata.main_multipole_type
        m_harm = self._excdata.main_multipole_harmonic
        intfield = multipoles[m_type][m_harm]
        if self._section == 'SI':
            strength = (self._ref_energy / self._ref_brho) * (- intfield - self._ref_BL_BC) / self._ref_angle
        else:
            strength = (self._ref_energy / self._ref_brho) * (-intfield) / self._ref_angle
        return strength

    def conv_strength_2_current(self, strength, **kwargs):
        """Return dipole power supply current."""
        if self._section == 'SI':
            intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * strength - self._ref_BL_BC
        else:
            intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * strength
        m_type = self._excdata.main_multipole_type
        m_harm = self._excdata.main_multipole_harmonic
        current = self._excdata.interp_mult2curr(intfield, harmonic=m_harm, multipole_type=m_type)
        return current

    def conv_current_2_brho(self, current):
        """Return beam rigidity as defined by the dipole field."""
        energy = self.conv_current_2_strength(current)
        brho = _util.beam_rigidity(energy)
        return brho
MAStrengthBase.register(MAStrengthDip)


class MAStrength(MAStrengthBase):

    def __init__(self, maname, **kwargs):
        section,dipole_maname = self.get_dipole_sector_maname(maname=maname)
        if maname == dipole_maname:
            raise Exception('MAStrength cannot be used for dipoles!')
        super().__init__(maname=maname)
        self._dipole = MAStrengthDip(section=section)

    @property
    def dipole(self):
        return self._dipole

    def conv_current_2_strength(self, current, current_dipole, **kwargs):
        brho = self.dipole.conv_current_2_brho(current_dipole)
        multipoles = self._excdata.interp_curr2mult(current)
        m_type = self._excdata.main_multipole_type
        m_harm = self._excdata.main_multipole_harmonic
        intfield = multipoles[m_type][m_harm]
        strength = - intfield / brho
        return strength

    def conv_strength_2_current(self, strength, current_dipole, **kwargs):
        brho = self.dipole.conv_current_2_brho(current_dipole)
        intfield = - brho * strength
        m_type = self._excdata.main_multipole_type
        m_harm = self._excdata.main_multipole_harmonic
        current = self._excdata.interp_mult2curr(intfield, harmonic=m_harm, multipole_type=m_type)
        return current
MAStrengthBase.register(MAStrength)


class MAStrengthTrim(MAStrengthBase):

    def __init__(self, maname, **kwargs):
        super().__init__(maname=maname)
        pvname = _SiriusPVName(maname)
        self._family = MAStrength(maname=maname.replace(pvname.subsection, 'Fam'))

    @property
    def dipole(self):
        return self._family.dipole

    @property
    def family(self):
        return self._family

    def conv_current_2_strength(self, current, current_dipole, current_family, **kwargs):
        brho = self.dipole.conv_current_2_brho(current_dipole)
        multipoles = self._excdata.interp_curr2mult(current)
        m_type = self._excdata.main_multipole_type
        m_harm = self._excdata.main_multipole_harmonic
        intfield = multipoles[m_type][m_harm]
        strength_trim = - intfield / brho
        strength_family = self.family.conv_current_2_strength(current_family, current_dipole)
        return strength_family + strength_trim

    def conv_strength_2_current(self, strength, current_dipole, current_family, **kwargs):
        strength_family = self.family.conv_current_2_strength(current_family, current_dipole)
        brho = self.dipole.conv_current_2_brho(current_dipole)
        intfield = - brho * (strength - strength_family)
        m_type = self._excdata.main_multipole_type
        m_harm = self._excdata.main_multipole_harmonic
        current = self._excdata.interp_mult2curr(intfield, harmonic=m_harm, multipole_type=m_type)
        return current
MAStrengthBase.register(MAStrengthTrim)



#
# import siriuspy.servweb as _web
# import siriuspy.util as _util
# from siriuspy.csdevice.pwrsupply import MASetPointLims as _SPLims
#
# _timeout = None
#
# class _MagData:
#
#     def __init__(self, timeout=_timeout):
#
#         self._splims = _SPLims(timeout=_timeout)
#
#     def conv_mag2ps(self, magname):
#         return self._splims.conv_mag2ps(magname)
#
#     def conv_ps2mag(self, psname):
#         return self._splims.conv_ps2mag(magname)
#
#
#
# _magdata = None
# def _get_magdata():
#     # encapsulating _psdata within a function avoid creating the global object
#     # (which is time consuming) at module load time.
#     global _magdata
#     if _magdata is None:
#         _magdata = _MagData()
#     return _magdata
#
#
# # PSDATA API
# # ==========
#
# def server_online():
#     """Return True/False if Sirius web server is online."""
#     return _web.server_online()
#
# def get_ma_names():
#     """Return a name list of magnets"""
#     magdata = _get_magdata()
#     return tuple(magdata._splims.mag2ps_dict.keys())
#
# def get_ps_names():
#     """Return a name list of power supplies"""
#     magdata = _get_magdata()
#     return tuple(magdata._splims.magps_sp_limits_dict.keys())
#
# def get_ma_unit():
#     """Return the power supplies' unit for the currents."""
#     magdata = _get_magdata()
#     return magdata._splims.setpoint_unit
#
# def get_ma_setpoint_limits(magps=None):
#     """Return a dictionary with setpoint limits of a given power supply name of
#     type."""
#     magdata = _get_magdata()
#     return magdata._splims.magps_sp_limits_dict[magps]
#
# def conv_maname_2_psname(magname):
#     magdata = _get_magdata()
#     return magdata.conv_mag2ps(magname)
#
# def conv_psname_2_maname(psname):
#     magdata = _get_magdata()
#     return magdata.conv_ps2mag2(psname)
