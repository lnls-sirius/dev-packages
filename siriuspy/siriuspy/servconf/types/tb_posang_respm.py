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

# Position-Angle Correction Response Matrices for the Booster Injection
# (TB correctors)
#
# Horizontal Matrix:
#
#  | DeltaPosX @ TB-04:PM-InjS |    | h11  h12 |   | Kick TB-03:MA-CH   |
#  |                           | =  |          | * |                    |
#  | DeltaAngX @ TB-04:PM-InjS |    | h21  h22 |   | Kick TB-04:PM-InjS |
#
# Data structure:
#         h11   h12
#         h21   h22
#
# Vertical Matrix:
#
#  | DeltaPosY @ TB-04:PM-InjS |    | v11  v12 |   | Kick TB-04:MA-CV-1 |
#  |                           | =  |          | * |                    |
#  | DeltaAngY @ TB-04:PM-InjS |    | v21  v22 |   | Kick TB-04:MA-CV-2 |
#
# Data structure:
#         v11   v12
#         v21   v22


_value = {'respm-x': [[0.0, 0.0],
                      [0.0, 0.0]],
          'respm-y': [[0.0, 0.0],
                      [0.0, 0.0]]}
