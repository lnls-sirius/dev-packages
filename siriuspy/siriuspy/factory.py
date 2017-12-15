"""Definition of factories.

MagnetFacoty
    used to create magnets
"""
# import re as _re

from siriuspy.magnet import util as _mutil
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.magnet import normalizer as _norm


class NormalizerFactory:
    """Creates normalizer objects."""

    @staticmethod
    def factory(maname):
        """Return appropriate normalizer."""
        madata = _MAData(maname)
        magfunc = madata.magfunc(madata.psnames[0])
        ma_class = _mutil.magnet_class(maname)
        if 'dipole' == ma_class:
            return _norm.DipoleNormalizer(maname, magnet_conv_sign=-1.0)
        elif 'trim' == ma_class:
            return _norm.TrimNormalizer(
                maname, magnet_conv_sign=-1.0,
                dipole_name=_mutil.get_section_dipole_name(maname),
                family_name=_mutil.get_magnet_family_name(maname))
        else:
            if magfunc in ('corrector-horizontal', 'quadrupole-skew'):
                return _norm.MagnetNormalizer(
                    maname, magnet_conv_sign=+1.0,
                    dipole_name=_mutil.get_section_dipole_name(maname))
            else:
                return _norm.MagnetNormalizer(
                    maname, magnet_conv_sign=-1.0,
                    dipole_name=_mutil.get_section_dipole_name(maname))
