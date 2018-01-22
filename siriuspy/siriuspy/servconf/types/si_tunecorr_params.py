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
# (obtained by matlab lnls_correct_tunes routine)
#   m(0,0)   m(0,1)...m(0,7)
#   m(1,0)   m(1,1)...m(1,7)
#
# Nominals KLs
# [quadrupole_order   QFA  QFB  QFP  QDA  QDB1  QDB2  QDP1  QDP2]


_value = {'matrix':        [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]],
          'nominal KLs':   [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
