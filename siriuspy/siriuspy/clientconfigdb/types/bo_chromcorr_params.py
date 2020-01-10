"""BO chromaticity correction configuration.

Values in _template_dict are arbitrary. They are used just to compare with
corresponding values when a new configuration is tried to be inserted in the
servconf database.
"""
from copy import deepcopy as _dcopy


def get_dict():
    """Return configuration type dictionary."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict)
    }
    return _dict


# Chromaticity Correction Parameters for Booster
#
# | ChromX |   | NominalChromX |   | m00  m01 |   | SL BO-Fam:PS-SF |
# |        | = |               | + |          | * |                 |
# | ChromY |   | NominalChromY |   | m10  m11 |   | SL BO-Fam:PS-SD |
#
# Nominal Chromaticity
#   NominalChromX   NominalChromY
#
# Correction Matrix of Additional Method
# (obtained from matlab lnls_calc_chromcorr_params routine)
#   m(0,0)   m(0,1)
#   m(1,0)   m(1,1)
#
# Nominals SLs
# [sextupole_order  SF  SD]

_template_dict = {
    'nominal chrom': [0.0, 0.0],
    'matrix': [[0.0, 0.0],
               [0.0, 0.0]],
    'nominal SLs':  [0.0, 0.0],
}
