"""Definition of factories.

MagnetFacoty
    used to create magnets
"""
from .search import PSSearch as _PSSearch
from .search import MASearch as _MASearch
from .magnet import util as _mutil
from .magnet import normalizer as _norm


class NormalizerFactory:
    """Factory class for normalizer objects."""

    @staticmethod
    def create(maname):
        """Return appropriate normalizer."""
        psname = _MASearch.conv_maname_2_psnames(maname)[0]
        magfunc = _PSSearch.conv_psname_2_magfunc(psname)
        ma_class = _mutil.magnet_class(maname)
        if ma_class == 'dipole':
            return _norm.DipoleNormalizer(maname, magnet_conv_sign=-1.0)
        elif ma_class == 'trim':
            return _norm.TrimNormalizer(
                maname, magnet_conv_sign=-1.0,
                dipole_name=_mutil.get_section_dipole_name(maname),
                family_name=_mutil.get_magnet_family_name(maname))
        elif magfunc == 'corrector-horizontal':
            return _norm.MagnetNormalizer(
                maname, magnet_conv_sign=+1.0,
                dipole_name=_mutil.get_section_dipole_name(maname))
        elif 'TB' in maname and 'QD' in maname:
            return _norm.MagnetNormalizer(
                maname, magnet_conv_sign=+1.0,
                dipole_name=_mutil.get_section_dipole_name(maname))
        else:
            return _norm.MagnetNormalizer(
                maname, magnet_conv_sign=-1.0,
                dipole_name=_mutil.get_section_dipole_name(maname))
