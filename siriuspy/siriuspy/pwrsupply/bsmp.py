"""Module for definitions of BSMP entities of power supply devices."""
# from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.bsmp import Entities as _Entities
from siriuspy.bsmp import Types as _Types


class Const:
    """Namespace for organizing power supply BSMP constants."""

    # --- implemented protocol version ---
    # version = __bsmp_version__

    # --- types ---
    T_STATUS = 0
    T_STATUS = 1
    T_REMOTE = 2
    T_MODEL = 3
    T_FLOAT = 4
    T_UINT8 = 5
    T_UINT16 = 6
    T_UINT32 = 7
    T_CHAR128 = 8
    T_FLOAT4 = 9
    T_PARAM = 10
    T_FLOAT12 = 11
    T_DSPCLASS = 12
    T_NONE = 13

    # --- common variables ---
    V_PS_STATUS = 0
    V_PS_SETPOINT = 1  # corresponds to IOC Current-RB
    V_PS_REFERENCE = 2  # corresponds to IOC CurrentRef-Mon
    V_FIRMWARE_VERSION = 3
    V_COUNTER_SET_SLOWREF = 4
    V_COUNTER_SYNC_PULSE = 5
    V_SIGGEN_ENABLE = 6
    V_SIGGEN_TYPE = 7
    V_SIGGEN_NUM_CYCLES = 8
    V_SIGGEN_N = 9
    V_SIGGEN_FREQ = 10
    V_SIGGEN_AMPLITUDE = 11
    V_SIGGEN_OFFSET = 12
    V_SIGGEN_AUX_PARAM = 13

    # --- FSB variables ---
    V_PS_SOFT_INTERLOCKS = 25  # BSMP doc says ID numb. should be continous!
    V_PS_HARD_INTERLOCKS = 26
    V_I_LOAD = 27  # corresponds to IOC Current-Mon
    V_V_LOAD = 28
    V_V_DCLINK = 29
    V_TEMP_SWITCHES = 30

    # --- functions ---
    F_TURN_ON = 0
    F_TURN_OFF = 1
    F_OPEN_LOOP = 2
    F_CLOSE_LOOP = 3
    F_SELECT_OP_MODE = 4
    F_RESET_INTERLOCKS = 6
    F_SET_SERIAL_TERMINATION = 9  # --- NOT IMPLEMENTED YET ---
    F_SYNC_PULSE = 15  # --- NOT IMPLEMENTED YET ---
    F_SET_SLOWREF = 16
    F_SET_SLOWREF_FBP = 17  # --- NOT IMPLEMENTED YET ---
    F_RESET_COUNTERS = 18
    F_CFG_SIGGEN = 23
    F_SET_SIGGEN = 24  # --- NOT IMPLEMENTED YET ---
    F_ENABLE_SIGGEN = 25
    F_DISABLE_SIGGEN = 26
    F_SET_SLOWREF_READBACK = 27  # --- NOT IMPLEMENTED YET ---
    F_SET_SLOWREF_FBP_READBACK = 28  # --- NOT IMPLEMENTED YET ---
    F_SET_PARAM = 29  # --- NOT IMPLEMENTED YET ---
    F_GET_PARAM = 30  # --- NOT IMPLEMENTED YET ---
    F_SAVE_PARAM_EEPROM = 31  # --- NOT IMPLEMENTED YET ---
    F_LOAD_PARAM_EEPROM = 32  # --- NOT IMPLEMENTED YET ---
    F_SAVE_PARAM_BANK = 33  # --- NOT IMPLEMENTED YET ---
    F_LOAD_PARAM_BANK = 34  # --- NOT IMPLEMENTED YET ---
    F_SET_DSP_COEFFS = 35  # --- NOT IMPLEMENTED YET ---
    F_GET_DSP_COEFF = 36  # --- NOT IMPLEMENTED YET ---
    F_SAVE_DSP_COEFFS_EEPROM = 37  # --- NOT IMPLEMENTED YET ---
    F_LOAD_DSP_COEFFS_EEPROM = 38  # --- NOT IMPLEMENTED YET ---
    F_SAVE_DSP_MODULES_EEPROM = 39  # --- NOT IMPLEMENTED YET ---
    F_LOAD_DSP_MODULES_EEPROM = 40  # --- NOT IMPLEMENTED YET ---
    F_RESET_UDC = 41  # --- NOT IMPLEMENTED YET ---

    # --- variables groups ---


group_id = 3  # default variables group ID defined for power supplies


class FBPEntities(_Entities):
    """PS FBP Entities."""

    Variables = (
        {'eid': 0, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 1, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 2, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 3, 'waccess': False, 'count': 128, 'var_type': _Types.t_char},
        {'eid': 4, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 5, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 6, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 7, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 8, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 9, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 10, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 11, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 12, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 13, 'waccess': False, 'count': 4, 'var_type': _Types.T_FLOAT},
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
    )
    Curves = tuple()
    Functions = (
        {'eid': 0, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 1, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 2, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 3, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 4, 'i_type': [_Types.T_UINT16], 'o_type': [_Types.T_UINT8]},
        {'eid': 5, 'i_type': [_Types.T_UINT16], 'o_type': [_Types.T_UINT8]},
        {'eid': 6, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 7, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 8, 'i_type': [_Types.T_UINT16], 'o_type': [_Types.T_UINT8]},
        {'eid': 9, 'i_type': [_Types.T_UINT16], 'o_type': [_Types.T_UINT8]},
        {'eid': 10, 'i_type': [_Types.T_UINT16], 'o_type': [_Types.T_UINT8]},
        {'eid': 11, 'i_type': [_Types.T_UINT16], 'o_type': [_Types.T_UINT8]},
        {'eid': 12, 'i_type': [_Types.T_UINT32], 'o_type': [_Types.T_UINT8]},
        {'eid': 13, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 14, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 15, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_NONE]},
        {'eid': 16, 'i_type': [_Types.T_FLOAT], 'o_type': [_Types.T_UINT8]},
        {'eid': 17,
         'i_type': [_Types.T_FLOAT, _Types.T_FLOAT, _Types.T_FLOAT,
                    _Types.T_FLOAT],
         'o_type': [_Types.T_UINT8]},
        {'eid': 18, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 19,
         'i_type': [_Types.T_FLOAT, _Types.T_FLOAT],
         'o_type': [_Types.T_UINT8]},
        {'eid': 20, 'i_type': [_Types.T_UINT16], 'o_type': [_Types.T_UINT8]},
        {'eid': 21, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 22, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 23,
         'i_type': [_Types.T_UINT16, _Types.T_UINT16, _Types.T_FLOAT,
                    _Types.T_FLOAT, _Types.T_FLOAT, _Types.T_FLOAT,
                    _Types.T_FLOAT,
                    _Types.T_FLOAT, _Types.T_FLOAT],
         'o_type': [_Types.T_UINT8]},
        {'eid': 24,
         'i_type': [_Types.T_FLOAT, _Types.T_FLOAT, _Types.T_FLOAT],
         'o_type': [_Types.T_UINT8]},
        {'eid': 25, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
        {'eid': 26, 'i_type': [_Types.T_NONE], 'o_type': [_Types.T_UINT8]},
    )

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)
