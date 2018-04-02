"""Module for definitions of BSMP entities of power supply devices."""
from siriuspy.bsmp import Entities, Types
bsmp_2_epics = {
    0: None,
    1: 'Current-RB',
    2: 'CurrentRef-Mon',
    3: 'Version-Cte',
    7: 'CycleType-Sts',
    25: 'IntlkSoft-Mon',
    26: 'IntlkHard-Mon',
    27: 'Current-Mon',
}

epics_2_bsmp = {
    'PwrState-Sts': 0,
    'OpMode-Sts': 0,
    'Current-RB': 1,
    'CurrentRef-Mon': 2,
    'Version-Cte': 3,
    'CycleType-Sts': 7,
    'IntlkSoft-Mon': 25,
    'IntlkHard-Mon': 26,
    'Current-Mon': 27,
}

# class Mapping:
#     """Maps Power Supply epics fields to BSMP entities and vice-versa."""
#
#
#
#     @staticmethod
#     def get_field_id(field):
#         """Return BSMP variable id."""
#         return Mapping._epics_2_bsmp[field]
#
#     def get_id_fieldname(var_id):
#         """Return epics field name."""
#         return Mapping._bsmp_2_epics[var_id]
#


class FBPEntities(Entities):
    """PS FBP Entities."""

    Variables = [
        {'id': 0, 'access': False, 'length': 1, 'type': Types.t_uint16},
        {'id': 1, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 2, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 3, 'access': False, 'length': 128, 'type': Types.t_char},
        {'id': 4, 'access': False, 'length': 1, 'type': Types.t_uint32},
        {'id': 5, 'access': False, 'length': 1, 'type': Types.t_uint32},
        {'id': 6, 'access': False, 'length': 1, 'type': Types.t_uint16},
        {'id': 7, 'access': False, 'length': 1, 'type': Types.t_uint16},
        {'id': 8, 'access': False, 'length': 1, 'type': Types.t_uint16},
        {'id': 9, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 10, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 11, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 12, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 13, 'access': False, 'length': 4, 'type': Types.t_float},
        {'id': 14, 'access': False, 'length': 1, 'type': Types.t_uint32},
        {'id': 15, 'access': False, 'length': 1, 'type': Types.t_uint32},
        {'id': 16, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 17, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 18, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 19, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 20, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 21, 'access': False, 'length': 1, 'type': Types.t_uint16},
        {'id': 22, 'access': False, 'length': 1, 'type': Types.t_uint16},
        {'id': 23, 'access': False, 'length': 1, 'type': Types.t_uint16},
        {'id': 24, 'access': False, 'length': 1, 'type': Types.t_uint16},
        {'id': 25, 'access': False, 'length': 1, 'type': Types.t_uint32},
        {'id': 26, 'access': False, 'length': 1, 'type': Types.t_uint32},
        {'id': 27, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 28, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 29, 'access': False, 'length': 1, 'type': Types.t_float},
        {'id': 30, 'access': False, 'length': 1, 'type': Types.t_float},
    ]
    Curves = []
    Functions = [
        {'id': 0, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'id': 1, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'id': 2, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'id': 3, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'id': 4, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'id': 5, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'id': 6, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'id': 7, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'id': 8, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'id': 9, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'id': 10, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'id': 11, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'id': 12, 'i_type': [Types.t_uint32], 'o_type': [Types.t_uint8]},
        {'id': 13, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'id': 14, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'id': 15, 'i_type': [Types.t_none], 'o_type': [Types.t_none]},
        {'id': 16, 'i_type': [Types.t_float], 'o_type': [Types.t_uint8]},
        # {'id': 17, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 18, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 19, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 20, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 21, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 22, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 23, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 24, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 25, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 26, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 27, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 28, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 29, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 30, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 31, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 32, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 33, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 34, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 35, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 36, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 37, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 38, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 39, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 40, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
        # {'id': 41, 'i_size':, 'i_type':, 'o_size':, 'o_type':},
    ]

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)
