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

# Position-Angle Correction Response Matrices for the Storage Ring Injection
# (TS correctors)
#
# Horizontal Matrix:
#
#  | DeltaPosX @ TS-04:DI-Scrn-3 |    | h11  h12 |   | Kick TS-04:MA-CH    |
#  |                             | =  |          | * |                     |
#  | DeltaAngX @ TS-04:DI-Scrn-3 |    | h21  h22 |   | Kick TS-04:PM-InjSF |
#
# Data structure:
#         h11   h12
#         h21   h22
#
# Vertical Matrix:
#
#  | DeltaPosY @ TS-04:DI-Scrn-3 |    | v11  v12 |   | Kick TS-04:MA-CV-1 |
#  |                             | =  |          | * |                    |
#  | DeltaAngY @ TS-04:DI-Scrn-3 |    | v21  v22 |   | Kick TS-04:MA-CV-2 |
#
# Data structure:
#         v11   v12
#         v21   v22


_value = {'respm-x': [[0.0, 0.0],
                      [0.0, 0.0]],
          'respm-y': [[0.0, 0.0],
                      [0.0, 0.0]]}
