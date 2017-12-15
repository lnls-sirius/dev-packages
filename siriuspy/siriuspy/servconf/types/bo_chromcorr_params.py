"""Configuration Type Definition."""

import copy as _copy


def get_dict():
    """Return configuration type dictionary."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _copy.deepcopy(_value)
    }
    return _dict

# Chromaticity Correction Parameters for Booster
#
# | ChromX |   | NominalChromX |   | m00  m01 |   | SL BO-Fam:MA-SF |
# |        | = |               | + |          | * |                 |
# | ChromY |   | NominalChromY |   | m10  m11 |   | SL BO-Fam:MA-SD |
#
# Nominal Chromaticity
#   NominalChromX   NominalChromY
#
# Correction Matrix of Additional Method
#   m(0,0)   m(0,1)
#   m(1,0)   m(1,1)
#
# Nominals SLs
# [sextupole_order  SF  SD]


_value = {'nominal chrom': [0.0, 0.0],
          'matrix':        [[0.0, 0.0],
                            [0.0, 0.0]],
          'nominal SLs':   [0.0, 0.0]}
