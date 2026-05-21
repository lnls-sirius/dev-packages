"""Definition of factories.

NormalizerFactory
    used to create magnet normalizers
"""

from ..search import MASearch as _MASearch, PSSearch as _PSSearch
from . import normalizer as _norm, util as _mutil


class NormalizerFactory:
    """Factory class for normalizer objects."""

    @staticmethod
    def create(maname, **kwargs):
        """Return appropriate normalizer."""
        ma_class = _mutil.magnet_class(maname)
        if ma_class == 'ids':
            return _norm.IDNormalizer(
                idname=maname,
                polarization=kwargs['polarization'],
            )
        # not an ID normalizer
        if ma_class == 'dipole':
            kwargs['magnet_conv_sign'] = -1.0
            return _norm.DipoleNormalizer(maname, **kwargs)
        if ma_class == 'trim':
            kwargs['magnet_conv_sign'] = -1.0
            return _norm.TrimNormalizer(maname, **kwargs)
        if 'TB' in maname and 'QD' in maname:
            kwargs['magnet_conv_sign'] = +1.0
            return _norm.MagnetNormalizer(maname, **kwargs)
        psname = _MASearch.conv_maname_2_psnames(maname)[0]
        magfunc = _PSSearch.conv_psname_2_magfunc(psname)
        if magfunc == 'corrector-horizontal':
            kwargs['magnet_conv_sign'] = +1.0
            return _norm.MagnetNormalizer(maname, **kwargs)
        # all other cases
        kwargs['magnet_conv_sign'] = -1.0
        return _norm.MagnetNormalizer(maname, **kwargs)
