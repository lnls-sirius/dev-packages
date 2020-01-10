"""SI tune correction configuration.

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


#  Tune Correction Parameters for Storage Ring
#
#  | DeltaTuneX |    | m00  m01...m07 |   | KL SI QFA  |
#  |            | =  |                | * |      .     |
#  | DeltaTuneY |    | m10  m11...m17 |   |      .     |
#                                         |      .     |
#                                         | KL SI QDP2 |
# Where (1+f)KL = KL + DeltaKL.
#
# Correction Matrix of Svd and Additional Method
# (obtained by matlab lnls_calc_tunecorr_params routine)
#   m(0,0)   m(0,1)...m(0,7)
#   m(1,0)   m(1,1)...m(1,7)
#
# Nominals KLs
# [quadrupole_order   QFA  QFB  QFP  QDA  QDB1  QDB2  QDP1  QDP2]

_template_dict = {
    'matrix': [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
    'nominal KLs': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
}
