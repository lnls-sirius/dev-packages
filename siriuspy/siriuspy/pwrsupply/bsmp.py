"""Module for definitions of BSMP entities of power supply devices."""
# from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.bsmp import Entities as _Entities
from siriuspy.bsmp import Types as _Types


class Const:
    """Namespace for organizing power supply BSMP constants."""

    # --- implemented protocol version ---
    # version = __bsmp_version__

    # --- types ---
    t_status = 0
    t_state = 1
    t_remote = 2
    t_model = 3
    t_float = 4
    t_uint8 = 5
    t_uint16 = 6
    t_uint32 = 7
    t_char128 = 8
    t_float4 = 9
    t_param = 10
    t_float12 = 11
    t_dspclass = 12
    t_none = 13

    # --- common variables ---
    PS_STATUS = 0
    PS_SETPOINT = 1  # corresponds to IOC Current-RB
    PS_REFERENCE = 2  # corresponds to IOC CurrentRef-Mon
    FIRMWARE_VERSION = 3
    COUNTER_SET_SLOWREF = 4
    COUNTER_SYNC_PULSE = 5
    SIGGEN_ENABLE = 6
    SIGGEN_TYPE = 7
    SIGGEN_NUM_CYCLES = 8
    SIGGEN_N = 9
    SIGGEN_FREQ = 10
    SIGGEN_AMPLITUDE = 11
    SIGGEN_OFFSET = 12
    SIGGEN_AUX_PARAM = 13

    # --- FSB variables ---
    PS_SOFT_INTERLOCKS = 25  # BSMP doc says ID numbering should be continous!
    PS_HARD_INTERLOCKS = 26
    I_LOAD = 27  # corresponds to IOC Current-Mon
    V_LOAD = 28
    V_DCLINK = 29
    TEMP_SWITCHES = 30

    # --- functions ---
    TURN_ON = 0
    TURN_OFF = 1
    OPEN_LOOP = 2
    CLOSE_LOOP = 3
    SELECT_OP_MODE = 4
    RESET_INTERLOCKS = 6
    SET_SERIAL_TERMINATION = 9  # --- NOT IMPLEMENTED YET ---
    SYNC_PULSE = 15  # --- NOT IMPLEMENTED YET ---
    SET_SLOWREF = 16
    SET_SLOWREF_FBP = 17  # --- NOT IMPLEMENTED YET ---
    RESET_COUNTERS = 18
    CFG_SIGGEN = 23
    SET_SIGGEN = 24  # --- NOT IMPLEMENTED YET ---
    ENABLE_SIGGEN = 25
    DISABLE_SIGGEN = 26
    SET_SLOWREF_READBACK = 27  # --- NOT IMPLEMENTED YET ---
    SET_SLOWREF_FBP_READBACK = 28  # --- NOT IMPLEMENTED YET ---
    SET_PARAM = 29  # --- NOT IMPLEMENTED YET ---
    GET_PARAM = 30  # --- NOT IMPLEMENTED YET ---
    SAVE_PARAM_EEPROM = 31  # --- NOT IMPLEMENTED YET ---
    LOAD_PARAM_EEPROM = 32  # --- NOT IMPLEMENTED YET ---
    SAVE_PARAM_BANK = 33  # --- NOT IMPLEMENTED YET ---
    LOAD_PARAM_BANK = 34  # --- NOT IMPLEMENTED YET ---
    SET_DSP_COEFFS = 35  # --- NOT IMPLEMENTED YET ---
    GET_DSP_COEFF = 36  # --- NOT IMPLEMENTED YET ---
    SAVE_DSP_COEFFS_EEPROM = 37  # --- NOT IMPLEMENTED YET ---
    LOAD_DSP_COEFFS_EEPROM = 38  # --- NOT IMPLEMENTED YET ---
    SAVE_DSP_MODULES_EEPROM = 39  # --- NOT IMPLEMENTED YET ---
    LOAD_DSP_MODULES_EEPROM = 40  # --- NOT IMPLEMENTED YET ---
    RESET_UDC = 41  # --- NOT IMPLEMENTED YET ---

    # --- variables groups ---


group_id = 3  # default variables group ID defined for power supplies


class FBPEntities(_Entities):
    """PS FBP Entities."""

    Variables = (
        {'eid': 0, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint16},
        {'eid': 1, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 2, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 3, 'waccess': False, 'count': 128, 'var_type': _Types.t_char},
        {'eid': 4, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint32},
        {'eid': 5, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint32},
        {'eid': 6, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint16},
        {'eid': 7, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint16},
        {'eid': 8, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint16},
        {'eid': 9, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 10, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 11, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 12, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 13, 'waccess': False, 'count': 4, 'var_type': _Types.t_float},
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint32},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint32},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint16},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint16},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint16},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint16},
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.t_uint32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.t_float},
    )
    Curves = tuple()
    Functions = (
        {'eid': 0, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 1, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 2, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 3, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 4, 'i_type': [_Types.t_uint16], 'o_type': [_Types.t_uint8]},
        {'eid': 5, 'i_type': [_Types.t_uint16], 'o_type': [_Types.t_uint8]},
        {'eid': 6, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 7, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 8, 'i_type': [_Types.t_uint16], 'o_type': [_Types.t_uint8]},
        {'eid': 9, 'i_type': [_Types.t_uint16], 'o_type': [_Types.t_uint8]},
        {'eid': 10, 'i_type': [_Types.t_uint16], 'o_type': [_Types.t_uint8]},
        {'eid': 11, 'i_type': [_Types.t_uint16], 'o_type': [_Types.t_uint8]},
        {'eid': 12, 'i_type': [_Types.t_uint32], 'o_type': [_Types.t_uint8]},
        {'eid': 13, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 14, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 15, 'i_type': [_Types.t_none], 'o_type': [_Types.t_none]},
        {'eid': 16, 'i_type': [_Types.t_float], 'o_type': [_Types.t_uint8]},
        {'eid': 17,
         'i_type': [_Types.t_float, _Types.t_float, _Types.t_float,
                    _Types.t_float],
         'o_type': [_Types.t_uint8]},
        {'eid': 18, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 19,
         'i_type': [_Types.t_float, _Types.t_float],
         'o_type': [_Types.t_uint8]},
        {'eid': 20, 'i_type': [_Types.t_uint16], 'o_type': [_Types.t_uint8]},
        {'eid': 21, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 22, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 23,
         'i_type': [_Types.t_uint16, _Types.t_uint16, _Types.t_float,
                    _Types.t_float, _Types.t_float, _Types.t_float,
                    _Types.t_float,
                    _Types.t_float, _Types.t_float],
         'o_type': [_Types.t_uint8]},
        {'eid': 24,
         'i_type': [_Types.t_float, _Types.t_float, _Types.t_float],
         'o_type': [_Types.t_uint8]},
        {'eid': 25, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
        {'eid': 26, 'i_type': [_Types.t_none], 'o_type': [_Types.t_uint8]},
    )

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)
