"""Ramp Convertion Classes."""


import siriuspy.util as _util
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.magnet_orig import util as _mutil
from siriuspy.magnet_orig import model as _model

# import siriuspy.magnet.model as _model
# from siriuspy import util as _util
# from siriuspy import envars as _envars
# from siriuspy.csdevice.enumtypes import EnumTypes as _et


_magfuncs = _mutil.get_magfunc_2_multipole_dict()


class Magnet(object):
    """Base class for handling magnets."""

    def __init__(self, maname):
        """Init method."""
        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(maname=self._maname)
        self._dipole_name = _mutil.get_section_dipole_name(self._maname)
        self._family_name = _mutil.get_magnet_family_name(self._maname)
        self._magfunc = self._madata.magfunc(self._madata.psnames[0])
        self._mfmult = _magfuncs[self.magfunc]
        self._strength_obj = _model.create_magnet_normalizer(self)
        self._strength_label = _util.get_strength_label(self._magfunc)
        self._strength_units = _util.get_strength_units(self._magfunc,
                                                        self._maname.sec)

    @property
    def maname(self):
        """Return magnet device name."""
        return self._maname

    @property
    def section(self):
        """Section the magnet belongs to."""
        return self._maname.sec

    @property
    def dipole_name(self):
        """Return section dipole device name."""
        return self._dipole_name

    @property
    def family_name(self):
        """Return section dipole device name."""
        return self._family_name

    @property
    def magfunc(self):
        """Return magnet function."""
        return self._magfunc

    @property
    def strength_label(self):
        """Return strength label of magnet."""
        return self._strength_label

    @property
    def strength_units(self):
        """Strength units of magnet."""
        return self._strength_units

    @property
    def current_min(self):
        """Mininum current for magnet power supply."""
        return self._madata._splims['DRVL']

    @property
    def current_max(self):
        """Maximum current for magnet power supply."""
        return self._madata._splims['DRVH']

    @property
    def splims(self):
        """Magnet SP limits."""
        return self._madata.splims

    def conv_current_2_strength(self, currents, **kwargs):
        """Return strength value from current(s)."""
        strength = self._strength_obj.conv_current_2_strength(currents,
                                                              **kwargs)
        return strength

    def conv_strength_2_current(self, strengths, **kwargs):
        """Return current value from strengths(s)."""
        current = self._strength_obj.conv_strength_2_current(strengths,
                                                             **kwargs)
        return current

    def __str__(self):
        """__str__ method."""
        s = ''
        s += '\nmaname         : {}'.format(self.maname)
        s += '\nsection        : {}'.format(self.section)
        s += '\ndipole_name    : {}'.format(self.dipole_name)
        s += '\nfamily_name    : {}'.format(self.family_name)
        s += '\nmagfunc        : {}'.format(self.magfunc)
        s += '\nstrength_label : {}'.format(self.strength_label)
        s += '\nstrength_units : {}'.format(self.strength_units)
        s += '\ncurrent_min    : {}'.format(self.current_min)
        s += '\ncurrent_max    : {}'.format(self.current_max)
        return s
