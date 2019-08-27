"""Power Supply BSMP.

Module for definitions of BSMP entities of power supply devices.

Documentation:

https://wiki-sirius.lnls.br/mediawiki/index.php/Machine:Power_Supplies
"""

from siriuspy.bsmp import BSMP as _BSMP
from siriuspy.bsmp import Entities as _Entities
from siriuspy.bsmp import Types as _Types
from siriuspy.pwrsupply.pru import PRU as _PRU


# version of the BSMP implementation of power supplies that is compatible
# with the current implemenation of this module.

# firmware: modified for group FAC
# __version__ = 'V0.11b2018-05-08V0.11b2018-05-08'
# firmware: original, before V0.11b2018-05-08 (FBP works!)
# __version__ = 'V0.11 2018-04-26V0.11 2018-04-25'
# firmware: latest, created when module DCLink was installed in bench test.
# __version__ = 'V0.13 2018-06-07V0.13 2018-06-07'
# firmware: FBP DCLink variable id 32 changed from float to uint8
# __version__ = 'V0.15 2018-07-11V0.15 2018-07-11'
# FAP dipole version
# __version__ = 'V0.18 2018-10-22V0.18 2018-10-22'

__version__ = 'V0.32 2019-04-10V0.32 2019-04-10'


# --- DCDC ---

class ConstBSMP:
    """Namespace for organizing power supply BSMP constants."""

    # --- implemented protocol version ---
    # version = __bsmp_version__

    # --- types ---
    T_STATUS = 0
    T_STATE = 1
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
    T_ENUM = 14

    # --- enums ---
    E_STATE_OFF = 0
    E_STATE_INTERLOCK = 1
    E_STATE_INITIALIZING = 2
    E_STATE_SLOWREF = 3
    E_STATE_SLOWREFSYNC = 4
    E_STATE_CYCLE = 5
    E_STATE_RMPWFM = 6
    E_STATE_MIGWFM = 7
    E_STATE_FASTREF = 8

    E_REMOTE_REMOTE = 0
    E_REMOTE_LOCAL = 1
    E_REMOTE_PCHOST = 2

    E_SIGGENTYPE_SINE = 0
    E_SIGGENTYPE_DAMPEDSINE = 1
    E_SIGGENTYPE_TRAPEZOIDAL = 2

    # --- functions ---
    F_TURN_ON = 0
    F_TURN_OFF = 1
    F_OPEN_LOOP = 2
    F_CLOSE_LOOP = 3
    F_SELECT_OP_MODE = 4
    F_SELECT_PS_MODEL = 5
    F_RESET_INTERLOCKS = 6
    F_REMOTE_INTERFACE = 7
    F_SET_SERIAL_ADDRESS = 8
    F_SET_SERIAL_TERMINATION = 9
    F_UNLOCK_UDC = 10
    F_LOCK_UDC = 11
    F_CFG_BUF_SAMPLES = 12
    F_ENABLE_BUF_SAMPLES = 13
    F_DISABLE_BUF_SAMPLES = 14
    F_SYNC_PULSE = 15
    F_SET_SLOWREF = 16
    F_SET_SLOWREF_FBP = 17
    F_RESET_COUNTERS = 18
    F_SCALE_WFMREF = 19
    F_SELECT_WFMREF = 20
    F_SAVE_WFMREF = 21
    F_RESET_WFMREF = 22
    F_CFG_SIGGEN = 23
    F_SET_SIGGEN = 24
    F_ENABLE_SIGGEN = 25
    F_DISABLE_SIGGEN = 26
    F_SET_SLOWREF_READBACK = 27
    F_SET_SLOWREF_FBP_READBACK = 28
    F_SET_PARAM = 29
    F_GET_PARAM = 30
    F_SAVE_PARAM_EEPROM = 31
    F_LOAD_PARAM_EEPROM = 32
    F_SAVE_PARAM_BANK = 33
    F_LOAD_PARAM_BANK = 34
    F_SET_DSP_COEFFS = 35
    F_GET_DSP_COEFF = 36
    F_SAVE_DSP_COEFFS_EEPROM = 37
    F_LOAD_DSP_COEFFS_EEPROM = 38
    F_SAVE_DSP_MODULES_EEPROM = 39
    F_LOAD_DSP_MODULES_EEPROM = 40
    F_RESET_UDC = 41

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
    V_WFMREF_SELECTED = 14
    V_WFMREF_SYNC_MODE = 15
    V_WFMREF_GAIN = 16
    V_WFMREF_OFFSET = 17
    V_WFMREF_START = 18
    V_WFMREF_END = 19
    V_WFMREF_IDX = 20
    # --- undefined variables
    V_UNDEF21 = 21
    V_UNDEF22 = 22
    V_UNDEF23 = 23
    V_UNDEF24 = 24

    # --- power supply parameters ---
    # ----- class PS -----
    P_PS_NAME = 0
    P_PS_MODEL = 1
    P_PS_NR_PSMODELS = 2
    # ----- class Communication -----
    P_COMM_CMD_INTERFACE = 3
    P_COMM_RS485_BAUDRATE = 4
    P_COMM_RS485_ADDRESS = 5
    P_COMM_RS485_TERMINATOR_RESISTOR = 6
    P_COMM_UDC_NETWORK_ADDRESS = 7
    P_COMM_ETHERNET_IP = 8
    P_COMM_ETHERNET_SUBNET_MASK = 9
    P_COMM_BUZZER_VOLUME = 10
    # ----- class Control -----
    P_CTRL_FREQ_CONTROL_ISR = 11
    P_CTRL_FREQ_TIME_SLICER = 12
    P_CTRL_MAX_REF = 13
    P_CTRL_MIN_REF = 14
    P_CTRL_MAX_REF_OPEN_LOOP = 15
    P_CTRL_MIN_REF_OPEN_LOOP = 16
    P_CTRL_SLEW_RATE_SLOWREF = 17
    P_CTRL_SLEW_RATE_SIGGEN_AMP = 18
    P_CTRL_SLEW_RATE_SIGGEN_OFFSET = 19
    P_CTRL_SLEW_RATE_WFMREF = 20
    # ----- class PWM -----
    P_PWM_FREQ = 21
    P_PWM_DEAD_TIME = 22
    P_PWM_MAX_DUTY = 23
    P_PWM_MIN_DUTY = 24
    P_PWM_MAX_DUTY_OPEN_LOOP = 25
    P_PWM_MIN_DUTY_OPEN_LOOP = 26
    P_PWM_LIM_DUTY_SHARE = 27
    # ----- class HRADC -----
    P_HRADC_NR_BOARDS = 28
    P_HRADC_SPI_CLK = 29
    P_HRADC_FREQ_SAMPLING = 30
    P_HRADC_ENABLE_HEATER = 31
    P_HRADC_ENABLE_RAILS_MON = 32
    P_HRADC_TRANSDUCER_OUTPUT = 33
    P_HRADC_TRANSDUCER_GAIN = 34
    P_HRADC_TRANSDUCER_OFFSET = 35
    # ----- class SigGen -----
    P_SIGGEN_TYPE = 36
    P_SIGGEN_NUM_CYCLES = 37
    P_SIGGEN_FREQ = 38
    P_SIGGEN_AMPLITUDE = 39
    P_SIGGEN_OFFSET = 40
    P_SIGGEN_AUX_PARAM = 41
    # ----- class WfmRef -----
    P_WFMREF_ID = 42
    P_WFMREF_SYNC_MODE = 43
    P_WFMREF_GAIN = 44
    P_WFMREF_OFFSET = 45
    # ----- class Analog Variables -----
    P_ANALOG_MAX = 46
    P_ANALOG_MIN = 47


class ConstFBP(ConstBSMP):
    """Namespace for organizing power supply FBP BSMP constants."""

    # --- implemented protocol version ---
    # version = __bsmp_version__

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


class ConstFAC_DCDC(ConstBSMP):
    """Namespace for organizing power supply FAC_DCDC BSMP constants."""

    # --- FAC_DCDC variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_I_LOAD_MEAN = 27
    V_I_LOAD1 = 28
    V_I_LOAD2 = 29
    V_V_LOAD = 30
    V_V_CAPBANK = 31
    V_TEMP_INDUCTORS = 32
    V_TEMP_IGBTS = 33
    V_DUTY_CYCLE = 34
    V_I_INPUT_IIB = 35
    V_I_OUTPUT_IIB = 36
    V_V_INPUT_IIB = 37
    V_TEMP_IGBTS_1_IIB = 38
    V_TEMP_IGBTS_2_IIB = 39
    V_TEMP_INDUCTOR_IIB = 40
    V_TEMP_HEATSINK_IIB = 41
    V_DRIVER_ERROR_1_IIB = 42
    V_DRIVER_ERROR_2_IIB = 43
    V_IIB_INTERLOCKS = 44


class ConstFAC_2P4S_DCDC(ConstBSMP):
    """Namespace for organizing power supply FAC_2P4S_DCDC BSMP constants."""

    # --- FAC_2P4S_DCDC variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_I_LOAD_MEAN = 27
    V_I_LOAD1 = 28
    V_I_LOAD2 = 29
    V_I_ARM_1 = 30
    V_I_ARM_2 = 31
    V_V_LOAD = 32
    V_V_CAPBANK_1 = 33
    V_V_CAPBANK_2 = 34
    V_V_CAPBANK_3 = 35
    V_V_CAPBANK_4 = 36
    V_V_CAPBANK_5 = 37
    V_V_CAPBANK_6 = 38
    V_V_CAPBANK_7 = 39
    V_V_CAPBANK_8 = 40
    V_V_OUT_1 = 41
    V_V_OUT_2 = 42
    V_V_OUT_3 = 43
    V_V_OUT_4 = 44
    V_V_OUT_5 = 45
    V_V_OUT_6 = 46
    V_V_OUT_7 = 47
    V_V_OUT_8 = 48
    V_DUTY_CYCLE_1 = 49
    V_DUTY_CYCLE_2 = 50
    V_DUTY_CYCLE_3 = 51
    V_DUTY_CYCLE_4 = 52
    V_DUTY_CYCLE_5 = 53
    V_DUTY_CYCLE_6 = 54
    V_DUTY_CYCLE_7 = 55
    V_DUTY_CYCLE_8 = 56


class ConstFAC_2S_DCDC(ConstBSMP):
    """Namespace for organizing power supply FAC_2S_DCDC BSMP constants."""

    # --- FAC_2S_DCDC variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_I_LOAD_MEAN = 27
    V_I_LOAD1 = 28
    V_I_LOAD2 = 29
    V_V_LOAD = 30
    V_V_OUT_1 = 31
    V_V_OUT_2 = 32
    V_V_CAPBANK_1 = 33
    V_V_CAPBANK_2 = 34
    V_DUTY_CYCLE_1 = 35
    V_DUTY_CYCLE_2 = 36
    V_DUTY_DIFF = 37
    V_I_INPUT_IIB_1 = 38
    V_I_OUTPUT_IIB_1 = 39
    V_V_INPUT_IIB_1 = 40
    V_TEMP_INDUCTOR_IIB_1 = 41
    V_TEMP_HEATSINK_IIB_1 = 42
    V_DRIVER_ERROR_1_IIB_1 = 43
    V_DRIVER_ERROR_2_IIB_1 = 44
    V_I_INPUT_IIB_2 = 45
    V_I_OUTPUT_IIB_2 = 46
    V_V_INPUT_IIB_2 = 47
    V_TEMP_INDUCTOR_IIB_2 = 48
    V_TEMP_HEATSINK_IIB_2 = 49
    V_DRIVER_ERROR_1_IIB_2 = 50
    V_DRIVER_ERROR_2_IIB_2 = 51
    V_IIB_INTERLOCKS_1 = 52
    V_IIB_INTERLOCKS_2 = 53


class ConstFAP(ConstBSMP):
    """Namespace for organizing power supply FAP BSMP constants."""

    # --- implemented protocol version ---
    # version = __bsmp_version__

    # --- FAP variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_I_LOAD_MEAN = 27  # corresponds to IOC Current-Mon
    V_I_LOAD1 = 28  # corresponds to IOC Current1-Mon
    V_I_LOAD2 = 29  # corresponds to IOC Current2-Mon
    V_V_DCLINK = 30
    V_I_IGBT_1 = 31
    V_I_IGBT_2 = 32
    V_DUTY_CYCLE_1 = 33
    V_DUTY_CYCLE_2 = 34
    V_DUTY_DIFF = 35
    V_V_INPUT_IIB = 36
    V_V_OUTPUT_IIB = 37
    V_I_IGBT_1_IIB = 38
    V_I_IGBT_2_IIB = 39
    V_TEMP_IGBT_1_IIB = 40
    V_TEMP_IGBT_2_IIB = 41
    V_V_DRIVER_IIB = 42
    V_I_DRIVER_1_IIB = 43
    V_I_DRIVER_2_IIB = 44
    V_TEMP_INDUCTOR_IIB = 45
    V_TEMP_HEATSINK_IIB = 46
    V_IIB_INTERLOCKS = 47


class ConstFAP_4P(ConstBSMP):
    """Namespace for organizing power supply FAP_4P BSMP constants."""

    # --- implemented protocol version ---
    # version = __bsmp_version__

    # --- FAP variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_I_LOAD_MEAN = 27  # corresponds to IOC Current-Mon
    V_I_LOAD1 = 28  # corresponds to IOC Current1-Mon
    V_I_LOAD2 = 29  # corresponds to IOC Current2-Mon
    V_V_LOAD = 30
    V_I_IGBT_1_1 = 31
    V_I_IGBT_2_1 = 32
    V_I_IGBT_1_2 = 33
    V_I_IGBT_2_2 = 34
    V_I_IGBT_1_3 = 35
    V_I_IGBT_2_3 = 36
    V_I_IGBT_1_4 = 37
    V_I_IGBT_2_4 = 38
    V_V_DCLINK_1 = 39
    V_V_DCLINK_2 = 40
    V_V_DCLINK_3 = 41
    V_V_DCLINK_4 = 42
    V_DUTY_MEAN = 43
    V_DUTY_CYCLE_1_1 = 44
    V_DUTY_CYCLE_2_1 = 45
    V_DUTY_CYCLE_1_2 = 46
    V_DUTY_CYCLE_2_2 = 47
    V_DUTY_CYCLE_1_3 = 48
    V_DUTY_CYCLE_2_3 = 49
    V_DUTY_CYCLE_1_4 = 50
    V_DUTY_CYCLE_2_4 = 51
    V_V_INPUT_IIB_1 = 52
    V_V_OUTPUT_IIB_1 = 53
    V_I_IGBT_1_IIB_1 = 54
    V_I_IGBT_2_IIB_1 = 55
    V_TEMP_IGBT_1_IIB_1 = 56
    V_TEMP_IGBT_2_IIB_1 = 57
    V_V_DRIVER_IIB_1 = 58
    V_I_DRIVER_1_IIB_1 = 59
    V_I_DRIVER_2_IIB_1 = 60
    V_TEMP_INDUCTOR_IIB_1 = 61
    V_TEMP_HEATSINK_IIB_1 = 62
    V_I_LEAKAGE_IIB_1 = 63
    V_V_INPUT_IIB_1 = 64
    V_V_OUTPUT_IIB_1 = 65
    V_I_IGBT_1_IIB_1 = 66
    V_I_IGBT_2_IIB_1 = 67
    V_TEMP_IGBT_1_IIB_1 = 68
    V_TEMP_IGBT_2_IIB_1 = 69
    V_V_DRIVER_IIB_1 = 70
    V_I_DRIVER_1_IIB_1 = 71
    V_I_DRIVER_2_IIB_1 = 72
    V_TEMP_INDUCTOR_IIB_1 = 73
    V_TEMP_HEATSINK_IIB_1 = 74
    V_I_LEAKAGE_IIB_1 = 75
    V_V_INPUT_IIB_1 = 76
    V_V_OUTPUT_IIB_1 = 77
    V_I_IGBT_1_IIB_1 = 78
    V_I_IGBT_2_IIB_1 = 79
    V_TEMP_IGBT_1_IIB_1 = 80
    V_TEMP_IGBT_2_IIB_1 = 81
    V_V_DRIVER_IIB_1 = 82
    V_I_DRIVER_1_IIB_1 = 83
    V_I_DRIVER_2_IIB_1 = 84
    V_TEMP_INDUCTOR_IIB_1 = 85
    V_TEMP_HEATSINK_IIB_1 = 86
    V_I_LEAKAGE_IIB_1 = 87
    V_V_INPUT_IIB_1 = 88
    V_V_OUTPUT_IIB_1 = 89
    V_I_IGBT_1_IIB_1 = 90
    V_I_IGBT_2_IIB_1 = 91
    V_TEMP_IGBT_1_IIB_1 = 92
    V_TEMP_IGBT_2_IIB_1 = 93
    V_V_DRIVER_IIB_1 = 94
    V_I_DRIVER_1_IIB_1 = 95
    V_I_DRIVER_2_IIB_1 = 96
    V_TEMP_INDUCTOR_IIB_1 = 97
    V_TEMP_HEATSINK_IIB_1 = 98
    V_I_LEAKAGE_IIB_1 = 99
    V_IIB_INTERLOCKS_1 = 100
    V_IIB_INTERLOCKS_2 = 101
    V_IIB_INTERLOCKS_3 = 102
    V_IIB_INTERLOCKS_4 = 103
    V_I_MOD_1 = 104
    V_I_MOD_2 = 105
    V_I_MOD_3 = 106
    V_I_MOD_4 = 107


class ConstFAP_2P2S(ConstBSMP):
    """Namespace for organizing power supply FAP_2P2S BSMP constants."""

    # --- FAP_2P2S variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_I_LOAD_MEAN = 27
    V_I_LOAD1 = 28
    V_I_LOAD2 = 29
    V_I_ARM_1 = 30
    V_I_ARM_2 = 31
    V_I_IGBT_1_1 = 32
    V_I_IGBT_2_1 = 33
    V_I_IGBT_1_2 = 34
    V_I_IGBT_2_2 = 35
    V_I_IGBT_1_3 = 36
    V_I_IGBT_2_3 = 37
    V_I_IGBT_1_4 = 38
    V_I_IGBT_2_4 = 39
    V_V_DCLINK_1 = 40
    V_V_DCLINK_2 = 41
    V_V_DCLINK_3 = 42
    V_V_DCLINK_4 = 43
    V_DUTY_MEAN = 44
    V_DUTY_ARMS_DIFF = 45
    V_DUTY_CYCLE_1_1 = 46
    V_DUTY_CYCLE_2_1 = 47
    V_DUTY_CYCLE_1_2 = 48
    V_DUTY_CYCLE_2_2 = 49
    V_DUTY_CYCLE_1_3 = 50
    V_DUTY_CYCLE_2_3 = 51
    V_DUTY_CYCLE_1_4 = 52
    V_DUTY_CYCLE_2_4 = 53
    V_V_INPUT_IIB_1 = 54
    V_V_OUTPUT_IIB_1 = 55
    V_I_IGBT_1_IIB_1 = 56
    V_I_IGBT_2_IIB_1 = 57
    V_TEMP_IGBT_1_IIB_1 = 58
    V_TEMP_IGBT_2_IIB_1 = 59
    V_V_DRIVER_IIB_1 = 60
    V_I_DRIVER_1_IIB_1 = 61
    V_I_DRIVER_2_IIB_1 = 62
    V_TEMP_INDUCTOR_IIB_1 = 63
    V_TEMP_HEATSINK_IIB_1 = 64
    V_V_INPUT_IIB_2 = 65
    V_V_OUTPUT_IIB_2 = 66
    V_I_IGBT_1_IIB_2 = 67
    V_I_IGBT_2_IIB_2 = 68
    V_TEMP_IGBT_1_IIB_2 = 69
    V_TEMP_IGBT_2_IIB_2 = 70
    V_V_DRIVER_IIB_2 = 71
    V_I_DRIVER_1_IIB_2 = 72
    V_I_DRIVER_2_IIB_2 = 73
    V_TEMP_INDUCTOR_IIB_2 = 74
    V_TEMP_HEATSINK_IIB_2 = 75
    V_V_INPUT_IIB_3 = 76
    V_V_OUTPUT_IIB_3 = 77
    V_I_IGBT_1_IIB_3 = 78
    V_I_IGBT_2_IIB_3 = 79
    V_TEMP_IGBT_1_IIB_3 = 80
    V_TEMP_IGBT_2_IIB_3 = 81
    V_V_DRIVER_IIB_3 = 82
    V_I_DRIVER_1_IIB_3 = 83
    V_I_DRIVER_2_IIB_3 = 84
    V_TEMP_INDUCTOR_IIB_3 = 85
    V_TEMP_HEATSINK_IIB_3 = 86
    V_V_INPUT_IIB_4 = 87
    V_V_OUTPUT_IIB_4 = 88
    V_I_IGBT_1_IIB_4 = 89
    V_I_IGBT_2_IIB_4 = 90
    V_TEMP_IGBT_1_IIB_4 = 91
    V_TEMP_IGBT_2_IIB_4 = 92
    V_V_DRIVER_IIB_4 = 93
    V_I_DRIVER_1_IIB_4 = 94
    V_I_DRIVER_2_IIB_4 = 95
    V_TEMP_INDUCTOR_IIB_4 = 96
    V_TEMP_HEATSINK_IIB_4 = 97
    V_IIB_INTERLOCKS_1 = 98
    V_IIB_INTERLOCKS_2 = 99
    V_IIB_INTERLOCKS_3 = 100
    V_IIB_INTERLOCKS_4 = 101
    V_I_MOD_1 = 102
    V_I_MOD_2 = 103
    V_I_MOD_3 = 104
    V_I_MOD_4 = 105


# --- ACDC ---

class ConstFBP_DCLink(ConstBSMP):
    """Namespace for organizing power supply FBP_DCLink BSMP constants."""

    # --- FBP_DCLink variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_MODULES_STATUS = 27
    V_V_OUT = 28
    V_V_OUT_1 = 29
    V_V_OUT_2 = 30
    V_V_OUT_3 = 31
    V_DIG_POT_TAP = 32


class ConstFAC_2S_ACDC(ConstBSMP):
    """Namespace for organizing power supply FAC_2S_ACDC BSMP constants."""

    # --- FAC_2S_ACDC variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_V_CAPBANK = 27
    V_V_OUT_RECTIFIER = 28
    V_I_OUT_RECTIFIER = 29
    V_TEMP_HEATSINK = 30
    V_TEMP_INDUCTORS = 31
    V_DUTY_CYCLE = 32
    V_I_INPUT_IS_IIB = 33
    V_V_INPUT_IS_IIB = 34
    V_TEMP_INDUCTOR_IS_IIB = 35
    V_TEMP_HEATSINK_IS_IIB = 36
    V_OUTPUT_CMD_IIB = 37
    V_CAPBANK_CMD_IIB = 38
    V_TEMP_INDUCTOR_CMD_IIB = 39
    V_TEMP_HEATSINK_CMD_IIB = 40
    V_I_LEAKAGE_CMD_IIB = 41
    V_IIB_INTERLOCKS_IS = 42
    V_IIB_INTERLOCKS_CMD = 43


class ConstFAC_2P4S_ACDC(ConstFAC_2S_ACDC):
    """Namespace for organizing power supply FAC_2P4S_ACDC BSMP constants."""

    pass


# Mirror power supply variables (FBP)
# ===================================
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

MAP_MIRROR_2_ORIG_FBP = {
    # This dictionary maps variable ids of mirror variables to the
    # corresponding original power supply crate index and variable ids,
    # organized as a tuple (device_idx, variable_id).
    ConstFBP.V_PS_STATUS_1: (1, 0),
    ConstFBP.V_PS_STATUS_2: (2, 0),
    ConstFBP.V_PS_STATUS_3: (3, 0),
    ConstFBP.V_PS_STATUS_4: (4, 0),
    ConstFBP.V_PS_SETPOINT_1: (1, 1),
    ConstFBP.V_PS_SETPOINT_2: (2, 1),
    ConstFBP.V_PS_SETPOINT_3: (3, 1),
    ConstFBP.V_PS_SETPOINT_4: (4, 1),
    ConstFBP.V_PS_REFERENCE_1: (1, 2),
    ConstFBP.V_PS_REFERENCE_2: (2, 2),
    ConstFBP.V_PS_REFERENCE_3: (3, 2),
    ConstFBP.V_PS_REFERENCE_4: (4, 2),
    ConstFBP.V_PS_SOFT_INTERLOCKS_1: (1, 25),
    ConstFBP.V_PS_SOFT_INTERLOCKS_2: (2, 25),
    ConstFBP.V_PS_SOFT_INTERLOCKS_3: (3, 25),
    ConstFBP.V_PS_SOFT_INTERLOCKS_4: (4, 25),
    ConstFBP.V_PS_HARD_INTERLOCKS_1: (1, 26),
    ConstFBP.V_PS_HARD_INTERLOCKS_2: (2, 26),
    ConstFBP.V_PS_HARD_INTERLOCKS_3: (3, 26),
    ConstFBP.V_PS_HARD_INTERLOCKS_4: (4, 26),
    ConstFBP.V_I_LOAD_1: (1, 27),
    ConstFBP.V_I_LOAD_2: (2, 27),
    ConstFBP.V_I_LOAD_3: (3, 27),
    ConstFBP.V_I_LOAD_4: (4, 27)}


# TODO: delete functions and parameters which do not make sense for Entities
#       which are specialized.


class Parameters:
    """power supply parameters."""

    _parameters = (
        {'eid': 0, 'count': 1, 'type': str, 'unit': '',
         'init': False, 'Op': True},
        {'eid': 1, 'count': 1, 'type': str, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 2, 'count': 1, 'type': int, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 3, 'count': 1, 'type': int, 'unit': '',
         'init': False, 'Op': True},
        {'eid': 4, 'count': 1, 'type': int, 'unit': 'bps',
         'init': True, 'Op': False},
        {'eid': 5, 'count': 4, 'type': str, 'unit': '',
         'init': False, 'Op': True},
        {'eid': 6, 'count': 1, 'type': float, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 7, 'count': 1, 'type': str, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 8, 'count': 4, 'type': str, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 9, 'count': 4, 'type': str, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 10, 'count': 1, 'type': float, 'unit': '%',
         'init': True, 'Op': False},
        {'eid': 11, 'count': 1, 'type': float, 'unit': 'Hz',
         'init': True, 'Op': False},
        {'eid': 12, 'count': 4, 'type': float, 'unit': 'Hz',
         'init': True, 'Op': False},
        {'eid': 13, 'count': 1, 'type': float, 'unit': 'A/V',
         'init': False, 'Op': True},
        {'eid': 14, 'count': 1, 'type': float, 'unit': 'A/V',
         'init': False, 'Op': True},
        {'eid': 15, 'count': 1, 'type': float, 'unit': '',
         'init': False, 'Op': True},
        {'eid': 16, 'count': 1, 'type': float, 'unit': '',
         'init': False, 'Op': True},
        {'eid': 17, 'count': 1, 'type': float, 'unit': 'Ref/s',
         'init': True, 'Op': False},
        {'eid': 18, 'count': 1, 'type': float, 'unit': 'Ref/s',
         'init': True, 'Op': False},
        {'eid': 19, 'count': 1, 'type': float, 'unit': 'Ref/s',
         'init': True, 'Op': False},
        {'eid': 20, 'count': 1, 'type': float, 'unit': 'Ref/s',
         'init': True, 'Op': False},
        {'eid': 21, 'count': 1, 'type': float, 'unit': 'Hz',
         'init': True, 'Op': False},
        {'eid': 22, 'count': 1, 'type': float, 'unit': 'ns',
         'init': True, 'Op': False},
        {'eid': 23, 'count': 1, 'type': float, 'unit': '%',
         'init': False, 'Op': True},
        {'eid': 24, 'count': 1, 'type': float, 'unit': '%',
         'init': False, 'Op': True},
        {'eid': 25, 'count': 1, 'type': float, 'unit': '%',
         'init': False, 'Op': True},
        {'eid': 26, 'count': 1, 'type': float, 'unit': '%',
         'init': False, 'Op': True},
        {'eid': 27, 'count': 1, 'type': float, 'unit': '%',
         'init': False, 'Op': True},
        {'eid': 28, 'count': 1, 'type': int, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 29, 'count': 1, 'type': float, 'unit': 'MHz',
         'init': True, 'Op': False},
        {'eid': 30, 'count': 1, 'type': float, 'unit': 'Hz',
         'init': True, 'Op': False},
        {'eid': 31, 'count': 4, 'type': int, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 32, 'count': 4, 'type': int, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 33, 'count': 4, 'type': float, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 34, 'count': 4, 'type': float, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 35, 'count': 4, 'type': float, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 36, 'count': 1, 'type': int, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 37, 'count': 1, 'type': float, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 38, 'count': 1, 'type': float, 'unit': 'Hz',
         'init': False, 'Op': True},
        {'eid': 39, 'count': 1, 'type': float, 'unit': 'A/V/%',
         'init': False, 'Op': True},
        {'eid': 40, 'count': 1, 'type': float, 'unit': 'A/V/%',
         'init': False, 'Op': True},
        {'eid': 41, 'count': 4, 'type': float, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 42, 'count': 1, 'type': int, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 43, 'count': 1, 'type': int, 'unit': '',
         'init': True, 'Op': False},
        {'eid': 44, 'count': 1, 'type': float, 'unit': 'A/V/%',
         'init': False, 'Op': True},
        {'eid': 45, 'count': 1, 'type': float, 'unit': 'A/V/%',
         'init': False, 'Op': True},
        {'eid': 46, 'count': 64, 'type': float, 'unit': '',
         'init': False, 'Op': True},
        {'eid': 47, 'count': 64, 'type': float, 'unit': '',
         'init': False, 'Op': True},
    )

    @staticmethod
    def conv(eid, value):
        """Convert from float to parameter type."""
        type_cast = Parameters._parameters[eid]['type']
        cast_value = type_cast(value)
        return cast_value

    @staticmethod
    def get_eids():
        """Return parameters eids."""
        return list(Parameters._parameters.keys())


_BSMP_Functions = (
    {'eid': ConstBSMP.F_TURN_ON,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_TURN_OFF,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_OPEN_LOOP,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_CLOSE_LOOP,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_SELECT_OP_MODE,
     'i_type': (_Types.T_ENUM, ), 'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_SELECT_PS_MODEL,
     'i_type': (_Types.T_UINT16, ), 'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_RESET_INTERLOCKS,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_REMOTE_INTERFACE,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_SET_SERIAL_ADDRESS,
     'i_type': (_Types.T_UINT16, ), 'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_SET_SERIAL_TERMINATION,
     'i_type': (_Types.T_UINT16, ), 'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_UNLOCK_UDC,
     'i_type': (_Types.T_UINT16,), 'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_LOCK_UDC,
     'i_type': (_Types.T_UINT16,), 'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_CFG_BUF_SAMPLES,
     'i_type': (_Types.T_UINT32,), 'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_ENABLE_BUF_SAMPLES,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_DISABLE_BUF_SAMPLES,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_SYNC_PULSE,
     'i_type': (), 'o_type': ()},
    {'eid': ConstBSMP.F_SET_SLOWREF,
     'i_type': (_Types.T_FLOAT,), 'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_SET_SLOWREF_FBP,
     'i_type': (_Types.T_FLOAT, _Types.T_FLOAT, _Types.T_FLOAT,
                _Types.T_FLOAT),
     'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_RESET_COUNTERS,
     'i_type': (), 'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_SCALE_WFMREF,
     'i_type': (_Types.T_FLOAT, _Types.T_FLOAT),
     'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_SELECT_WFMREF,
     'i_type': (_Types.T_UINT16,), 'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_SAVE_WFMREF,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_RESET_WFMREF,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_CFG_SIGGEN,
     'i_type': (_Types.T_ENUM, _Types.T_UINT16,
                _Types.T_FLOAT, _Types.T_FLOAT, _Types.T_FLOAT,
                _Types.T_FLOAT, _Types.T_FLOAT,
                _Types.T_FLOAT, _Types.T_FLOAT),
     'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_SET_SIGGEN,
     'i_type': (_Types.T_FLOAT, _Types.T_FLOAT, _Types.T_FLOAT),
     'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_ENABLE_SIGGEN,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_DISABLE_SIGGEN,
     'i_type': (), 'o_type': (_Types.T_UINT8, )},
    {'eid': ConstBSMP.F_SET_SLOWREF_READBACK,
     'i_type': (_Types.T_FLOAT,), 'o_type': (_Types.T_FLOAT,)},
    {'eid': ConstBSMP.F_SET_SLOWREF_FBP_READBACK,
     'i_type': (_Types.T_FLOAT, _Types.T_FLOAT,
                _Types.T_FLOAT, _Types.T_FLOAT,),
     'o_type': (_Types.T_FLOAT, _Types.T_FLOAT,
                _Types.T_FLOAT, _Types.T_FLOAT,)},
    {'eid': ConstBSMP.F_SET_PARAM,
     'i_type': (_Types.T_PARAM, _Types.T_UINT16, _Types.T_FLOAT,),
     'o_type': (_Types.T_UINT8,)},
    {'eid': ConstBSMP.F_GET_PARAM,
     'i_type': (_Types.T_PARAM, _Types.T_UINT16,),
     'o_type': (_Types.T_FLOAT,)},
)


# --- DCDC ---


class EntitiesFBP(_Entities):
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
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        # --- undefined variables
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- FBP-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        # --- undefined Variables
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 33, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 34, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 35, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 36, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 37, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 38, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 39, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
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

    Curves = (
        {'eid': 0, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 1, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 2, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
    )

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


class EntitiesFAC_DCDC(_Entities):
    """FAC-type power supply entities."""

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
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- undefined variables
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- FAC-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 33, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 34, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 35, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 36, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 37, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 38, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 39, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 40, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 41, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 42, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 43, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 44, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
    )

    Curves = (
        {'eid': 0, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 1, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 2, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
    )

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


class EntitiesFAC_2P4S_DCDC(_Entities):
    """FAC-2P4S-type power supply entities."""

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
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- undefined variables
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- FAC-2P4S-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 33, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 34, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 35, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 36, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 37, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 38, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 39, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 40, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 41, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 42, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 43, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 44, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 45, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 46, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 47, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 48, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 49, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 50, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 51, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 52, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 53, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 54, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 55, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 56, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
    )

    Curves = (
        {'eid': 0, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 1, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 2, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
    )

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


class EntitiesFAC_2S_DCDC(_Entities):
    """FAC-2S-type power supply entities."""

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
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- undefined variables
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- FAC-2S-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 33, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 34, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 35, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 36, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 37, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 38, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 39, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 40, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 41, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 42, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 43, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 44, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 45, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 46, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 47, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 48, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 49, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 50, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 51, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 52, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 53, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
    )

    Curves = (
        {'eid': 0, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 1, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 2, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
    )

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


class EntitiesFAP(_Entities):
    """FAP-type power supply entities."""

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
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        # --- undefined variables
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- FBP-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 33, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 34, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 35, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 36, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 37, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 38, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 39, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 40, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 41, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 42, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 43, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 44, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 45, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 46, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 47, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32}, )

    Curves = (
        {'eid': 0, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 1, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 2, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT}, )

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


class EntitiesFAP_4P(_Entities):
    """FAP_4P-type power supply entities."""

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
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        # --- undefined variables
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- FBP-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 33, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 34, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 35, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 36, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 37, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 38, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 39, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 40, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 41, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 42, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 43, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 44, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 45, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 46, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 47, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 48, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 49, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 50, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 51, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 52, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 53, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 54, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 55, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 56, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 57, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 58, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 59, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 60, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 61, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 62, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 63, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 64, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 65, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 66, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 67, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 68, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 69, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 70, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 71, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 72, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 73, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 74, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 75, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 76, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 77, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 78, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 79, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 80, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 81, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 82, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 83, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 84, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 85, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 86, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 87, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 88, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 89, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 90, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 91, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 92, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 93, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 94, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 95, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 96, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 97, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 98, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 99, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},

        {'eid': 100, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 101, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 102, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 103, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 104, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 105, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 106, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 107, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},)

    Curves = (
        {'eid': 0, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 1, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 2, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT}, )

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)



class EntitiesFAP_2P2S(_Entities):
    """FAP-type power supply entities."""

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
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        # --- undefined variables
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- FAP_2P2S-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 33, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 34, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 35, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 36, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 37, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 38, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 39, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 40, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 41, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 42, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 43, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 44, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 45, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 46, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 47, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 48, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 49, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 50, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 51, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 52, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 53, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 54, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 55, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 56, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 57, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 58, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 59, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 60, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 61, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 62, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 63, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 64, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 65, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 66, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 67, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 68, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 69, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 70, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 71, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 72, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 73, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 74, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 75, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 76, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 77, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 78, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 79, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 80, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 81, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 82, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 83, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 84, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 85, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 86, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 87, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 88, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 89, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 90, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 91, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 92, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 93, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 94, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 95, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 96, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 97, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 98, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 99, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 100, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 101, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 102, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 103, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 104, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 105, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},)

    Curves = (
        {'eid': 0, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 1, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT},
        {'eid': 2, 'waccess': False, 'count': 256,
         'nblocks': 16, 'var_type': _Types.T_FLOAT}, )

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


# --- ACDC ---


class EntitiesFBP_DCLink(_Entities):
    """FBP DCLink-type power supplies entities."""

    Variables = (
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
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        # --- undefined variables
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- FBP DCLINK-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
    )

    Curves = tuple()

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


class EntitiesFAC_2S_ACDC(_Entities):
    """FAC_2S_ACDC-type power supply entities."""

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
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 21, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 22, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 23, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        {'eid': 24, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT8},
        # --- FAC_2S_ACDC-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 33, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 34, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 35, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 36, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 37, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 38, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 39, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 40, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 41, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 42, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 43, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
    )

    Curves = tuple()

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


class EntitiesFAC_2P4S_ACDC(EntitiesFAC_2S_ACDC):
    """FAC_2P4S_ACDC-type power supply entities."""

    pass


class _PSBSMP(_BSMP):
    """Power supply BSMP."""

    def __init__(self, slave_address, entities, pru=None):
        """Init BSMP."""
        if pru is None:
            self.pru = _PRU()
        else:
            self.pru = pru
        # turn sync mode off
        # self.pru.sync_stop()
        super().__init__(self.pru, slave_address, entities)


# --- DCDC ---


class FBP(_PSBSMP):
    """BSMP with EntitiesFBP."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFBP
        _PSBSMP.__init__(self, slave_address, EntitiesFBP(), pru=pru)


class FAC_DCDC(_PSBSMP):
    """BSMP with EntitiesFAC_DCDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAC_DCDC
        _PSBSMP.__init__(self, slave_address, EntitiesFAC_DCDC(), pru=pru)


class FAC_2P4S_DCDC(_PSBSMP):
    """BSMP with EntitiesFAC_2P4S_DCDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAC_2P4S_DCDC
        _PSBSMP.__init__(self, slave_address, EntitiesFAC_2P4S_DCDC(), pru=pru)


class FAC_2S_DCDC(_PSBSMP):
    """BSMP with EntitiesFAC_2S_DCDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAC_2S_DCDC
        _PSBSMP.__init__(self, slave_address, EntitiesFAC_2S_DCDC(), pru=pru)


class FAP(_PSBSMP):
    """BSMP with EntitiesFAP."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAP
        _PSBSMP.__init__(self, slave_address, EntitiesFAP(), pru=pru)


class FAP_4P(_PSBSMP):
    """BSMP with EntitiesFAP_4P."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAP_4P
        _PSBSMP.__init__(self, slave_address, EntitiesFAP_4P(), pru=pru)


class FAP_2P2S(_PSBSMP):
    """BSMP with EntitiesFAP_2P2S."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAP_2P2S
        _PSBSMP.__init__(self, slave_address, EntitiesFAP_2P2S(), pru=pru)



# --- ACDC ---


class FBP_DCLink(_PSBSMP):
    """BSMP with EntitiesFBP_DCLink."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFBP_DCLink
        _PSBSMP.__init__(self, slave_address, EntitiesFBP_DCLink(), pru=pru)



class FAC_2P4S_ACDC(_PSBSMP):
    """BSMP with EntitiesFAC_2P4S_ACDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAC_2P4S_ACDC
        _PSBSMP.__init__(self, slave_address, EntitiesFAC_2P4S_ACDC(), pru=pru)


class FAC_2S_ACDC(_PSBSMP):
    """BSMP with EntitiesFAC_2S_ACDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAC_2S_ACDC
        _PSBSMP.__init__(self, slave_address, EntitiesFAC_2S_ACDC(), pru=pru)
