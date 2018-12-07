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

__version__ = 'V0.16b2018-08-22V0.16b2018-08-22'

# FAP dipole version
# __version__ = 'V0.18 2018-10-22V0.18 2018-10-22'


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

    # --- power supply parameters ---
    P_PS_NAME = 0
    P_PS_MODEL = 1
    P_PS_NR_PSMODELS = 2
    P_COMM_CMD_INTERFACE = 3
    P_COMM_RS485_BAUDRATE = 4
    P_COMM_RS485_ADDRESS = 5
    P_COMM_RS485_TERMINATOR_RESISTOR = 6
    P_COMM_UDC_NETWORK_ADDRESS = 7
    P_COMM_ETHERNET_IP = 8
    P_COMM_ETHERNET_SUBNET_MASK = 9
    P_CTRL_FREQ_CONTROL_ISR = 10
    P_CTRL_FREQ_TIME_SLICER = 11
    P_CTRL_MAX_REF = 12
    P_CTRL_MIN_REF = 13
    P_CTRL_MAX_REF_OPEN_LOOP = 14
    P_CTRL_MIN_REF_OPEN_LOOP = 15
    P_CTRL_SLEW_RATE_SLOWREF = 16
    P_CTRL_SLEW_RATE_SIGGEN_AMP = 17
    P_CTRL_SLEW_RATE_SIGGEN_OFFSET = 18
    P_CTRL_SLEW_RATE_WFMREF = 19
    P_PWM_FREQ = 20
    P_PWM_DEAD_TIME = 21
    P_PWM_MAX_DUTY = 22
    P_PWM_MIN_DUTY = 23
    P_PWM_MAX_DUTY_OPEN_LOOP = 24
    P_PWM_MIN_DUTY_OPEN_LOOP = 25
    P_PWM_LIM_DUTY_SHARE = 26
    P_HRADC_NR_BORARDS = 27
    P_HRADC_SPI_CLK = 28
    P_HRADC_FREQ_SAMPLING = 29
    P_HRADC_ENABLE_HEATER = 30
    P_HRADC_ENABLE_HAILS_MON = 31
    P_HRADC_TRANSDUCER_OUTPUT = 32
    P_HRADC_TRANSDUCER_GAIN = 33
    P_HRADC_TRANSDUCER_OFFSET = 34
    P_SIGGEN_TYPE = 35
    P_SIGGEN_NUM_CYCLES = 36
    P_SIGGEN_FREQ = 37
    P_SIGGEN_AMPLITUDE = 38
    P_SIGGEN_OFFSET = 39
    P_SIGGEN_AUX_PARAM = 40
    P_WFMREF_ID = 41
    P_WFMREF_SYNC_MODE = 42
    P_WFMREF_GAIN = 43
    P_WFMREF_OFFSET = 44
    P_ANALOG_MAX = 45
    P_ANALOG_MIN = 46


class ConstFBP(ConstBSMP):
    """Namespace for organizing power supply FBP BSMP constants."""

    # --- implemented protocol version ---
    # version = __bsmp_version__

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


class ConstFBP_DCLink(ConstBSMP):
    """Namespace for organizing power supply FBP_DCLink BSMP constants."""

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

    # --- FBP_DCLink variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_DIGITAL_INPUTS = 27
    V_V_OUT = 28
    V_V_OUT_1 = 29
    V_V_OUT_2 = 30
    V_V_OUT_3 = 31
    V_DIG_POT_TAP = 32


class ConstFAC_DCDC(ConstBSMP):
    """Namespace for organizing power supply FAC BSMP constants."""

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
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_I_LOAD1 = 27
    V_I_LOAD2 = 28
    V_V_LOAD = 29
    V_V_CAPACITOR_BANK = 30
    V_TEMP_INDUCTORS = 31
    V_TEMP_IGBTS = 32
    V_DUTY_CYCLE = 33


class ConstFAC_ACDC(ConstBSMP):
    """Namespace for organizing power supply FAC ACDC BSMP constants."""

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

    # --- FAC_ACDC variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_CAPACITOR_BANK = 27
    V_OUT_RECTIFIER = 28
    I_OUT_RECTIFIER = 29
    TEMP_HEATSINK = 30
    TEMP_INDUCTORS = 31
    DUTY_CYCLE = 32


class ConstFAC_2P4S_DCDC(ConstBSMP):
    """Namespace for organizing power supply FAC BSMP constants."""

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

    # --- FAC_2P4S variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_I_LOAD1 = 27
    V_I_LOAD2 = 28
    V_V_LOAD = 29
    V_V_CAPACITOR_BANK1 = 30
    V_V_CAPACITOR_BANK2 = 31
    V_V_CAPACITOR_BANK3 = 32
    V_V_CAPACITOR_BANK4 = 33
    V_V_CAPACITOR_BANK5 = 34
    V_V_CAPACITOR_BANK6 = 35
    V_V_CAPACITOR_BANK7 = 36
    V_V_CAPACITOR_BANK8 = 37
    V_V_OUT1 = 38
    V_V_OUT2 = 39
    V_V_OUT3 = 40
    V_V_OUT4 = 41
    V_V_OUT5 = 42
    V_V_OUT6 = 43
    V_V_OUT7 = 44
    V_V_OUT8 = 45
    V_DUTY_CYCLE1 = 46
    V_DUTY_CYCLE2 = 47
    V_DUTY_CYCLE3 = 48
    V_DUTY_CYCLE4 = 49
    V_DUTY_CYCLE5 = 50
    V_DUTY_CYCLE6 = 51
    V_DUTY_CYCLE7 = 52
    V_DUTY_CYCLE8 = 53
    V_I_ARM1 = 54
    V_I_ARM2 = 55


class ConstFAC_2P4S_ACDC(ConstBSMP):
    """Namespace for organizing power supply FAC ACDC BSMP constants."""

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

    # --- FAC_2P4S_ACDC variables ---
    V_PS_SOFT_INTERLOCKS = 25
    V_PS_HARD_INTERLOCKS = 26
    V_CAPACITOR_BANK = 27
    V_OUT_RECTIFIER = 28
    I_OUT_RECTIFIER = 29
    TEMP_HEATSINK = 30
    TEMP_INDUCTORS = 31
    DUTY_CYCLE = 32


class ConstFAP(ConstBSMP):
    """Namespace for organizing power supply FAP BSMP constants."""

    # --- implemented protocol version ---
    # version = __bsmp_version__

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
    V_I_LOAD1 = 27  # corresponds to IOC Current-Mon
    V_I_LOAD2 = 28  # corresponds to IOC Current2-Mon
    V_V_DCLINK = 29
    V_I_IGBT_1 = 30
    V_I_IGBT_2 = 31
    V_DUTY_CYCLE_1 = 32
    V_DUTY_CYCLE_2 = 33
    V_DUTY_DIFF = 34

    # --- undefined variables

    V_UNDEF35 = 35
    V_UNDEF36 = 36
    V_UNDEF37 = 37
    V_UNDEF38 = 38
    V_UNDEF39 = 39


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
         'init': False, 'config': False, 'Op': True},
        {'eid': 1, 'count': 1, 'type': str, 'unit': '',
         'init': True, 'config': False, 'Op': False},
        {'eid': 2, 'count': 1, 'type': int, 'unit': '',
         'init': True, 'config': False, 'Op': False},
        {'eid': 3, 'count': 1, 'type': int, 'unit': '',
         'init': False, 'config': False, 'Op': True},
        {'eid': 4, 'count': 1, 'type': int, 'unit': 'bps',
         'init': True, 'config': False, 'Op': True},
        {'eid': 5, 'count': 4, 'type': str, 'unit': '',
         'init': False, 'config': False, 'Op': True},
        {'eid': 6, 'count': 1, 'type': float, 'unit': '',
         'init': True, 'config': False, 'Op': False},
        {'eid': 7, 'count': 1, 'type': str, 'unit': '',
         'init': False, 'config': False, 'Op': True},
        {'eid': 8, 'count': 4, 'type': str, 'unit': '',
         'init': False, 'config': False, 'Op': True},
        {'eid': 9, 'count': 4, 'type': str, 'unit': '',
         'init': False, 'config': False, 'Op': True},
        {'eid': 10, 'count': 1, 'type': float, 'unit': 'Hz',
         'init': True, 'config': False, 'Op': False},
        {'eid': 11, 'count': 4, 'type': float, 'unit': 'Hz',
         'init': False, 'config': True, 'Op': False},
        {'eid': 12, 'count': 1, 'type': float, 'unit': 'A/V',
         'init': False, 'config': False, 'Op': True},
        {'eid': 13, 'count': 1, 'type': float, 'unit': 'A/V',
         'init': False, 'config': False, 'Op': True},
        {'eid': 14, 'count': 1, 'type': float, 'unit': '',
         'init': False, 'config': False, 'Op': True},
        {'eid': 15, 'count': 1, 'type': float, 'unit': '',
         'init': False, 'config': False, 'Op': True},
        {'eid': 16, 'count': 1, 'type': float, 'unit': 'Ref/s',
         'init': False, 'config': True, 'Op': False},
        {'eid': 17, 'count': 1, 'type': float, 'unit': 'Ref/s',
         'init': False, 'config': True, 'Op': False},
        {'eid': 18, 'count': 1, 'type': float, 'unit': 'Ref/s',
         'init': False, 'config': True, 'Op': False},
        {'eid': 19, 'count': 1, 'type': float, 'unit': 'Ref/s',
         'init': False, 'config': True, 'Op': False},
        {'eid': 20, 'count': 1, 'type': float, 'unit': 'Hz',
         'init': True, 'config': False, 'Op': False},
        {'eid': 21, 'count': 1, 'type': float, 'unit': 'ns',
         'init': False, 'config': True, 'Op': False},
        {'eid': 22, 'count': 1, 'type': float, 'unit': '%',
         'init': False, 'config': False, 'Op': True},
        {'eid': 23, 'count': 1, 'type': float, 'unit': '%',
         'init': False, 'config': False, 'Op': True},
        {'eid': 24, 'count': 1, 'type': float, 'unit': '%',
         'init': False, 'config': False, 'Op': True},
        {'eid': 25, 'count': 1, 'type': float, 'unit': '%',
         'init': False, 'config': False, 'Op': True},
        {'eid': 26, 'count': 1, 'type': float, 'unit': '%',
         'init': False, 'config': False, 'Op': True},
        {'eid': 27, 'count': 1, 'type': int, 'unit': '',
         'init': True, 'config': False, 'Op': False},
        {'eid': 28, 'count': 1, 'type': float, 'unit': 'MHz',
         'init': True, 'config': False, 'Op': False},
        {'eid': 29, 'count': 1, 'type': float, 'unit': 'Hz',
         'init': True, 'config': False, 'Op': False},
        {'eid': 30, 'count': 4, 'type': int, 'unit': '',
         'init': True, 'config': False, 'Op': False},
        {'eid': 31, 'count': 4, 'type': int, 'unit': '',
         'init': True, 'config': False, 'Op': False},
        {'eid': 32, 'count': 4, 'type': float, 'unit': '',
         'init': True, 'config': False, 'Op': False},
        {'eid': 33, 'count': 4, 'type': float, 'unit': '',
         'init': False, 'config': False, 'Op': True},
        {'eid': 34, 'count': 4, 'type': float, 'unit': '',
         'init': False, 'config': False, 'Op': True},
        {'eid': 35, 'count': 1, 'type': int, 'unit': '',
         'init': False, 'config': True, 'Op': False},
        {'eid': 36, 'count': 1, 'type': float, 'unit': '',
         'init': False, 'config': True, 'Op': False},
        {'eid': 37, 'count': 1, 'type': float, 'unit': 'Hz',
         'init': False, 'config': False, 'Op': True},
        {'eid': 38, 'count': 1, 'type': float, 'unit': 'A/V/%',
         'init': False, 'config': False, 'Op': True},
        {'eid': 39, 'count': 1, 'type': float, 'unit': 'A/V/%',
         'init': False, 'config': False, 'Op': True},
        {'eid': 40, 'count': 4, 'type': float, 'unit': '',
         'init': False, 'config': True, 'Op': False},
        {'eid': 41, 'count': 1, 'type': int, 'unit': '',
         'init': False, 'config': True, 'Op': False},
        {'eid': 42, 'count': 1, 'type': int, 'unit': '',
         'init': False, 'config': True, 'Op': False},
        {'eid': 43, 'count': 1, 'type': float, 'unit': 'A/V/%',
         'init': False, 'config': False, 'Op': True},
        {'eid': 44, 'count': 1, 'type': float, 'unit': 'A/V/%',
         'init': False, 'config': False, 'Op': True},
        {'eid': 45, 'count': 64, 'type': float, 'unit': '',
         'init': False, 'config': False, 'Op': True},
        {'eid': 46, 'count': 64, 'type': float, 'unit': '',
         'init': False, 'config': False, 'Op': True},
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
        # --- undefined variables
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
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

    Curves = tuple()

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


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
        # --- undefined variables
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
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
    )

    Curves = tuple()

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


class EntitiesFAC_ACDC(_Entities):
    """FAC_ACDC-type power supply entities."""

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
        # --- FAC_ACDC-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
    )

    Curves = tuple()

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
    )

    Curves = tuple()

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


class EntitiesFAC_2P4S_ACDC(_Entities):
    """FAC_ACDC-type power supply entities."""

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
        # --- FAC_2P4S_ACDC-specific variables
        {'eid': 25, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 26, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 27, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 28, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 29, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 30, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 31, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 32, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
    )

    Curves = tuple()

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
        # --- undefined variables
        {'eid': 14, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 15, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT16},
        {'eid': 16, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 17, 'waccess': False, 'count': 1, 'var_type': _Types.T_FLOAT},
        {'eid': 18, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 19, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
        {'eid': 20, 'waccess': False, 'count': 1, 'var_type': _Types.T_UINT32},
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
    )

    Curves = tuple()

    Functions = _BSMP_Functions

    def __init__(self):
        """Call super."""
        super().__init__(self.Variables, self.Curves, self.Functions)


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


class FBP(_PSBSMP):
    """BSMP with EntitiesFBP."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFBP
        _PSBSMP.__init__(self, slave_address, EntitiesFBP(), pru=pru)


class FBP_DCLink(_PSBSMP):
    """BSMP with EntitiesFBP_DCLink."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFBP_DCLink
        _PSBSMP.__init__(self, slave_address, EntitiesFBP_DCLink(), pru=pru)


class FAC_DCDC(_PSBSMP):
    """BSMP with EntitiesFAC_DCDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAC_DCDC
        _PSBSMP.__init__(self, slave_address, EntitiesFAC_DCDC(), pru=pru)


class FAC_ACDC(_PSBSMP):
    """BSMP with EntitiesFAC_ACDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAC_ACDC
        _PSBSMP.__init__(self, slave_address, EntitiesFAC_ACDC(), pru=pru)


class FAC_2P4S_DCDC(_PSBSMP):
    """BSMP with EntitiesFAC_DCDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAC_2P4S_DCDC
        _PSBSMP.__init__(self, slave_address, EntitiesFAC_2P4S_DCDC(), pru=pru)


class FAC_2P4S_ACDC(_PSBSMP):
    """BSMP with EntitiesFAC_ACDC."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAC_2P4S_ACDC
        _PSBSMP.__init__(self, slave_address, EntitiesFAC_2P4S_ACDC(), pru=pru)


class FAP(_PSBSMP):
    """BSMP with EntitiesFAP."""

    def __init__(self, slave_address, pru=None):
        """Init BSMP."""
        self.ConstBSMP = ConstFAP
        _PSBSMP.__init__(self, slave_address, EntitiesFAP(), pru=pru)
