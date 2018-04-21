"""Power Supply BSMP.

Module for definitions of BSMP entities of power supply devices.

Documentation:

https://wiki-sirius.lnls.br/mediawiki/index.php/Machine:Power_Supplies
"""

# from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.bsmp import Entities as _Entities
from siriuspy.bsmp import Types as _Types


__version__ = ''


# Mirror power supply variables
# =============================
#
# The current version of Beaglebone's PRU library is able to send only one
# BSMP command to the serial line at the end of each ramp cycle. Within BSMP
# there is no way a read command to multiple power supplies can be sent.
# At each ramp cycle a single power supply attached to the Beaglebone can be
# selected for its state to be read. With a ramp running at 2 Hz, the update
# of each power supply in a create with 4 powet supplies would be slowed to
# 0.5 Hz = 2 Hz / 4 power supploes.
#
# In order to keep a refresh rate of 2 Hz, a modification of the specification
# for the BSMP power supply was done. Each power supply will register a
# selected set of BSMP variables corresponding to variables of the other
# power supplies. This is simple to implement in the firmware of the
# ARM controller.
#
# Power supply variables with IDs in the range [40,63] serve this purpose.
# The dictionary MAP_MIRROR_2_ORIG maps the so-called mirror variable ids
# onto the original variable IDs.

MAP_MIRROR_2_ORIG = {
    # This dictionary maps variable ids of mirror variables to the
    # corresponding original power supply and variable ids, organized as a
    # tuple (device_id, variable_id).
    40: (1, 0),  41: (2, 0),  42: (3, 0),  43: (4, 0),   # V_PS_STATUS
    44: (1, 1),  45: (2, 1),  46: (3, 1),  47: (4, 1),   # V_PS_SETPOINT
    48: (1, 2),  49: (2, 2),  50: (3, 2),  51: (4, 2),   # V_PS_REFERENCE
    52: (1, 25), 53: (2, 25), 54: (3, 25), 55: (4, 25),  # V_PS_SOFT_INTERLOCK
    56: (1, 26), 57: (2, 26), 58: (3, 26), 59: (4, 26),  # V_PS_HARD_INTERLOCK
    60: (1, 27), 61: (2, 27), 62: (3, 27), 63: (4, 27)}  # V_PS_HARD_INTERLOCK


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

    # --- undefined variables
    V_UNDEF14 = 14
    V_UNDEF15 = 15
    V_UNDEF16 = 16
    V_UNDEF17 = 17
    V_UNDEF18 = 18
    V_UNDEF19 = 19
    V_UNDEF20 = 20
    V_UNDEF21 = 21
    V_UNDEF22 = 22
    V_UNDEF23 = 23
    V_UNDEF24 = 24

    # --- FSB variables ---
    V_PS_SOFT_INTERLOCKS = 25  # BSMP doc says ID numb. should be continous!
    V_PS_HARD_INTERLOCKS = 26
    V_I_LOAD = 27  # corresponds to IOC Current-Mon
    V_V_LOAD = 28
    V_V_DCLINK = 29
    V_TEMP_SWITCHES = 30
    V_DUTY_CYCLE = 31  # (float)

    # --- undefined variables

    V_UNDEF32 = 32
    V_UNDEF33 = 33
    V_UNDEF34 = 34
    V_UNDEF35 = 35
    V_UNDEF36 = 36
    V_UNDEF37 = 37
    V_UNDEF38 = 38
    V_UNDEF39 = 39

    # --- mirror variables ---

    V_PS_STATUS_1 = 40
    V_PS_STATUS_2 = 41
    V_PS_STATUS_3 = 42
    V_PS_STATUS_4 = 43

    V_PS_SETPOINT_1 = 44  # corresponds to IOC Current-RB
    V_PS_SETPOINT_2 = 45  # corresponds to IOC Current-RB
    V_PS_SETPOINT_3 = 46  # corresponds to IOC Current-RB
    V_PS_SETPOINT_4 = 47  # corresponds to IOC Current-RB

    V_PS_REFERENCE_1 = 48  # corresponds to IOC CurrentRef-Mon
    V_PS_REFERENCE_2 = 49  # corresponds to IOC CurrentRef-Mon
    V_PS_REFERENCE_3 = 50  # corresponds to IOC CurrentRef-Mon
    V_PS_REFERENCE_4 = 51  # corresponds to IOC CurrentRef-Mon

    V_PS_SOFT_INTERLOCKS_1 = 52  # BSMP doc says ID numb. should be continous!
    V_PS_SOFT_INTERLOCKS_2 = 53  # BSMP doc says ID numb. should be continous!
    V_PS_SOFT_INTERLOCKS_3 = 54  # BSMP doc says ID numb. should be continous!
    V_PS_SOFT_INTERLOCKS_4 = 55  # BSMP doc says ID numb. should be continous!

    V_PS_HARD_INTERLOCKS_1 = 56
    V_PS_HARD_INTERLOCKS_2 = 57
    V_PS_HARD_INTERLOCKS_3 = 58
    V_PS_HARD_INTERLOCKS_4 = 59

    V_I_LOAD_1 = 60  # corresponds to IOC Current-Mon
    V_I_LOAD_2 = 61  # corresponds to IOC Current-Mon
    V_I_LOAD_3 = 62  # corresponds to IOC Current-Mon
    V_I_LOAD_4 = 63  # corresponds to IOC Current-Mon

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


class FBPEntities(_Entities):
    """FBP-type power supply entities."""

    Variables = (
        # --- common variables
        {'eid': 0, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 1, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 2, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 3, 'waccess': False, 'count': 128, 'var_type': _Types.T_CHAR},
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
        # --- undefined variables
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        # --- FBP-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        # --- undefined Variables
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 33, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 34, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 35, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 36, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 37, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 38, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        {'eid': 39, 'waccess': False, 'count': 1, 'var_type': _Types.T_NONE},
        # --- mirror variables
        # ------ PS_STATUS
        {'eid': 40, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 41, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 42, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 43, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        # ------ PS_SETPOINT
        {'eid': 44, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 45, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 46, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 47, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        # ------ PS_REFERENCE
        {'eid': 48, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 49, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 50, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 51, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        # ------ PS_SOFT_INTERLOCK
        {'eid': 52, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 53, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 54, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 55, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        # ------ PS_HARD_INTERLOCK
        {'eid': 56, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 57, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 58, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 59, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        # ------ PS_I_LOAD
        {'eid': 60, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 61, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 62, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 63, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
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
