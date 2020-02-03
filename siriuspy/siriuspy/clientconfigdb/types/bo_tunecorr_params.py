"""BO tune correction configuration.

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


# Tune Correction Response Matrix for Booster
#
# | DeltaTuneX |   | m00  m01 |   | KL BO-Fam:PS-QF |
# |            | = |          | * |                 |
# | DeltaTuneY |   | m10  m11 |   | KL BO-Fam:PS-QD |
#
# Correction Matrix of Additional Method
# (obtained from lnls_calc_tunecorr_params routine)
#   m(0,0)   m(0,1)
#   m(1,0)   m(1,1)
#
# Nominal KLs
# [quadrupole_order  QF  QD]

_template_dict = {
    'matrix': [[0.0, 0.0],
               [0.0, 0.0]],
    'nominal KLs': [0.0, 0.0],
}
