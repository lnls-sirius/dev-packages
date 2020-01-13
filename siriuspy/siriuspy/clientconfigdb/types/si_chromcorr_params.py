"""SI chromaticity correction configuration.

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


# Chromaticity Correction Parameters for Storage Ring
#
# | ChromX |   | NominalChromX |   | m00  m01...m014 |   | SL SI-Fam:PS-SFA1 |
# |        | = |               | + |                 | * |         .         |
# | ChromY |   | NominalChromY |   | m10  m11...m114 |   |         .         |
#                                                        |         .         |
#                                                        | SL SI-Fam:PS-SDP3 |
# Data ordering:
#
# Nominal Chromaticity
#    NominalChromX    NominalChromY
#
# Correction Matrix of Additional Method
# (obtained from matlab lnls_calc_chromcorr_params routine)
#   m(0,0)   m(0,1) ... m(0,14)
#   m(1,0)   m(1,1) ... m(1,14)
#
# Nominals SLs
# [sextupole_order  SFA1  SFA2  SDA1  SDA2  SDA3  SFB1  SFB2  SDB1  SDB2  SDB3  SFP1  SFP2  SDP1  SDP2  SDP3]


_template_dict = {
    'nominal chrom': [0.0, 0.0],
    'matrix': [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    'nominal SLs': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
}
