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

    Variables = (
        {'eid': 0, 'waccess': False, 'count': 1, 'var_type': Types.t_uint16},
        {'eid': 1, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 2, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 3, 'waccess': False, 'count': 128, 'var_type': Types.t_char},
        {'eid': 4, 'waccess': False, 'count': 1, 'var_type': Types.t_uint32},
        {'eid': 5, 'waccess': False, 'count': 1, 'var_type': Types.t_uint32},
        {'eid': 6, 'waccess': False, 'count': 1, 'var_type': Types.t_uint16},
        {'eid': 7, 'waccess': False, 'count': 1, 'var_type': Types.t_uint16},
        {'eid': 8, 'waccess': False, 'count': 1, 'var_type': Types.t_uint16},
        {'eid': 9, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 10, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 11, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 12, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 13, 'waccess': False, 'count': 4, 'var_type': Types.t_float},
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': Types.t_uint32},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': Types.t_uint32},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': Types.t_uint16},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': Types.t_uint16},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': Types.t_uint16},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': Types.t_uint16},
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': Types.t_uint32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': Types.t_uint32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': Types.t_float},
    )
    Curves = tuple()
    Functions = (
        {'eid': 0, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 1, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 2, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 3, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 4, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'eid': 5, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'eid': 6, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 7, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 8, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'eid': 9, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'eid': 10, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'eid': 11, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'eid': 12, 'i_type': [Types.t_uint32], 'o_type': [Types.t_uint8]},
        {'eid': 13, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 14, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 15, 'i_type': [Types.t_none], 'o_type': [Types.t_none]},
        {'eid': 16, 'i_type': [Types.t_float], 'o_type': [Types.t_uint8]},
        {'eid': 17,
         'i_type': [Types.t_float, Types.t_float, Types.t_float,
                    Types.t_float],
         'o_type': [Types.t_uint8]},
        {'eid': 18, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 19,
         'i_type': [Types.t_float, Types.t_float],
         'o_type': [Types.t_uint8]},
        {'eid': 20, 'i_type': [Types.t_uint16], 'o_type': [Types.t_uint8]},
        {'eid': 21, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 22, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 23,
         'i_type': [Types.t_uint16, Types.t_uint16, Types.t_float,
                    Types.t_float, Types.t_float, Types.t_float, Types.t_float,
                    Types.t_float, Types.t_float],
         'o_type': [Types.t_uint8]},
        {'eid': 24,
         'i_type': [Types.t_float, Types.t_float, Types.t_float],
         'o_type': [Types.t_uint8]},
        {'eid': 25, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
        {'eid': 26, 'i_type': [Types.t_none], 'o_type': [Types.t_uint8]},
    )

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)
