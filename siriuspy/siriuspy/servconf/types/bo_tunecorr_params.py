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


# Tune Correction Response Matrix for Booster
#
# | DeltaTuneX |   | m00  m01 |   | KL BO-Fam:MA-QF |
# |            | = |          | * |                 |
# | DeltaTuneY |   | m10  m11 |   | KL BO-Fam:MA-QD |
#
# Correction Matrix
#   m(0,0)   m(0,1)
#   m(1,0)   m(1,1)


_value = {'matrix':      [[0.0, 0.0],
                          [0.0, 0.0]],
          'nominal KLs': [0.0, 0.0]}
