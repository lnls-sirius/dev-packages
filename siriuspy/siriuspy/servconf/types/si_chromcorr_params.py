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

# Chromaticity Correction Parameters for Storage Ring
#
# | ChromX |   | NominalChromX |   | m00  m01...m014 |   | SL SI-Fam:MA-SFA1 |
# |        | = |               | + |                 | * |         .         |
# | ChromY |   | NominalChromY |   | m10  m11...m114 |   |         .         |
#                                                        |         .         |
#                                                        | SL SI-Fam:MA-SDP3 |
# Data ordering:
#
# Nominal Chromaticity
#    NominalChromX    NominalChromY
#
# Correction Matrix of Additional Method
#   m(0,0)   m(0,1) ... m(0,14)
#   m(1,0)   m(1,1) ... m(1,14)
#
# Nominals SLs
# [sextupole_order  SFA1  SFA2  SDA1  SDA2  SDA3  SFB1  SFB2  SDB1  SDB2  SDB3  SFP1  SFP2  SDP1  SDP2  SDP3]


_value = {'nominal chrom': [0.0, 0.0],
          'matrix':        [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
          'nominal SLs':   [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
