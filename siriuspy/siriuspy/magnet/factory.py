"""Definition of factories.

NormalizerFactory
    used to create magnet normalizers
"""

from ..search import PSSearch as _PSSearch
from ..search import MASearch as _MASearch

from . import util as _mutil
from . import normalizer as _norm


class NormalizerFactory:
    """Factory class for normalizer objects."""

    @staticmethod
    def create(maname, **kwargs):
        """Return appropriate normalizer."""
        psname = _MASearch.conv_maname_2_psnames(maname)[0]
        magfunc = _PSSearch.conv_psname_2_magfunc(psname)
        ma_class = _mutil.magnet_class(maname)
        if ma_class == 'dipole':
            kwargs['magnet_conv_sign'] = -1.0
            return _norm.DipoleNormalizer(maname, **kwargs)
        if ma_class == 'trim':
            kwargs['magnet_conv_sign'] = -1.0
            return _norm.TrimNormalizer(maname, **kwargs)
        if ma_class == 'id-apu':
            kwargs['magnet_conv_sign'] = +1.0
            return _norm.APUNormalizer(maname, **kwargs)
        if magfunc == 'corrector-horizontal':
            kwargs['magnet_conv_sign'] = +1.0
            return _norm.MagnetNormalizer(maname, **kwargs)
        if 'TB' in maname and 'QD' in maname:
            kwargs['magnet_conv_sign'] = +1.0
            return _norm.MagnetNormalizer(maname, **kwargs)
        kwargs['magnet_conv_sign'] = -1.0
        return _norm.MagnetNormalizer(maname, **kwargs)
