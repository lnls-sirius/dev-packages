"""SI Bunch-by-bunch feedback system configuration."""
from copy import deepcopy as _dcopy
import numpy as _np

_ZERO_INT = 0
_ZERO_FLOAT = 0.0
_EMPTY_NDARRAY_INT = _np.zeros(32)
_EMPTY_STR = ''


def get_dict():
    """Return configuration type dictionary."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict),
        'check': False,
    }
    return _dict


# When using this type of configuration to set the machine,
# the list of PVs should be processed in the same order they are stored
# in the configuration. The second numeric parameter in the pair is the
# delay [s] the client should wait before setting the next PV.

_pvs_bbb_proc_l = [
    ['SI-Glob:DI-BbBProc-L:GDEN', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBCTRL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SETSEL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DELAY', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLKRST', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SHIFTGAIN', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PROC_DS', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:COEFF', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CSET0', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CSET1', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CSET2', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CSET3', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:LDSET', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DESC_COEFF', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:DESC_CSET0', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:DESC_CSET1', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:DESC_CSET2', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:DESC_CSET3', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:FID_DELAY', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FLT_GAIN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FLT_PHASE', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FLT_FREQ', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FLT_TAPS', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FTF_TUNE', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA31', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA30', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA29', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA28', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA27', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA26', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA25', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA24', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA23', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA22', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA21', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA20', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA19', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA18', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA17', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA16', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA15', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA14', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA13', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA12', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA11', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA10', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA9', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA8', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA7', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA6', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA5', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA4', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA3', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA2', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA1', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DATA0', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR31', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR30', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR29', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR28', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR27', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR26', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR25', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR24', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR23', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR22', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR21', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR20', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR19', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR18', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR17', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR16', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR15', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR14', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR13', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR12', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR11', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR10', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR9', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR8', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR7', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR6', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR5', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR4', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR3', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR2', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR1', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_DIR0', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE0_FREQ', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE0_AMPL', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE0_SPAN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE0_PERIOD', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE0_WAVEFORM', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE0_PATTERN', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE0_MASK', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE0_MOD', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE1_FREQ', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE1_AMPL', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE1_SPAN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE1_PERIOD', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE1_WAVEFORM', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE1_PATTERN', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE1_MASK', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE1_MOD', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE2_FREQ', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE2_AMPL', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE2_SPAN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE2_PERIOD', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE2_WAVEFORM', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE2_PATTERN', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE2_MASK', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE2_MOD', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DRIVE2_TRACK', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FE_PHASE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FE_ATTEN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BE_PHASE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BE_ATTEN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:TADC', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:TDAC', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:OFF_FIDS', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:DEL_CAL', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHASE_SERVO_OFFSET', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHASE_SERVO_SETPT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHASE_SERVO_MAXDELTA', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHASE_SERVO_GAIN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHASE_SERVO_MODE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHASE_SERVO_SIGN', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:GPIO_SEL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SAT_THRESHOLD', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FB_PATTERN', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:FB_MASK', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CF_PATTERN', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:CF_MASK', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_TUNE', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_AMPL', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_SPAN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_PERIOD', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_PATTERN', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_ENABLE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_SAVE_FREQ', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_SAVE_AMPL', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_SAVE_SPAN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_SAVE_PERIOD', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_SAVE_DRV_PATTERN', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_SAVE_FB_PATTERN', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:CLEAN_SAVE_MODE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:MMGRAW_0_SLOPE', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:MMGRAW_1_SLOPE', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:MMGRAW_0_OFFSET', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:MMGRAW_1_OFFSET', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:MCLRAW_0_FWDLOSS', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:MCLRAW_1_FWDLOSS', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:MCLRAW_0_REVLOSS', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:MCLRAW_1_REVLOSS', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:LEVEL_FID_ENABLE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:LEVEL_TRIG1_ENABLE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:LEVEL_TRIG2_ENABLE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH0', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH1', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH2', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH3', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH4', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH5', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH6', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH7', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH8', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH9', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH10', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644_V_CH11', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644REF0_BO', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644REF1_BO', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:AD5644REF2_BO', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:LEVEL_FID', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:LEVEL_TRIG1', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:LEVEL_TRIG2', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:LEVEL_VTRIG1', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:LEVEL_VTRIG2', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_SERVO_SETPT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_X_PHASE_SETPT', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_Y_PHASE_SETPT', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_SERVO_X_TRACK', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_SERVO_Y_TRACK', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBE_BE_PHASE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBE_Z_ATT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBE_X_ATT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBE_Y_ATT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBE_BE_ATT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_SERVO_MODE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_SERVO_SIGN', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_SERVO_GAIN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_SERVO_OFFSET', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_SERVO_MAXDELTA', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_FAN_SETPT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_FAN_MODE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_FAN_GAIN_P', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBELT_FAN_GAIN_I', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SHAPE_C0', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SHAPE_C2', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:TUNE_MODE', _ZERO_INT, 0.0],  # TODO: meaning?
    ['SI-Glob:DI-BbBProc-L:SRAM_REC_DS', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_DACQ', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_ACQTIME', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_GDTIME', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_HOLDTIME', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_POSTTIME', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_ARM', _ZERO_INT, 0.0],  # NOTE: Dmitry absent
    ['SI-Glob:DI-BbBProc-L:SRAM_HWTEN', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_BR_ARM', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_ACQ_SINGLE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_ACQ_EN', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_ACQ_PATTERN', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_ACQ_MASK', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_SP_LOW1', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_SP_HIGH1', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_SP_SEARCH1', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_SP_LOW2', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_SP_HIGH2', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_SP_SEARCH2', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_SP_AVG', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_TRIG_IN_SEL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_POSTSEL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_MD_FTUNE', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_MD_FSPAN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_MD_ENABLE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_MD_MSEL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_MD_SMODE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_MD_AVG', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_MD_SP_LOW', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_MD_SP_HIGH', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SRAM_MD_SP_SEARCH', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_REC_DS', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_DACQ', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_ACQTIME', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_GDTIME', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_HOLDTIME', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_POSTTIME', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_ARM', _ZERO_INT, 0.0],  # NOTE: Dmitry absent
    ['SI-Glob:DI-BbBProc-L:BRAM_HWTEN', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_BR_ARM', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_ACQ_SINGLE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_ACQ_EN', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_ACQ_PATTERN', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_ACQ_MASK', _EMPTY_NDARRAY_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_SP_LOW1', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_SP_HIGH1', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_SP_SEARCH1', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_SP_LOW2', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_SP_HIGH2', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_SP_SEARCH2', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_SP_AVG', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_TRIG_IN_SEL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_POSTSEL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_MD_FTUNE', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_MD_FSPAN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_MD_ENABLE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_MD_MSEL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_MD_SMODE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_MD_AVG', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_MD_SP_LOW', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_MD_SP_HIGH', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:BRAM_MD_SP_SEARCH', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_ACQTIME', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_BUNCH_ID', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_EXTEN', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_ARM', _ZERO_INT, 0.0],  # NOTE: Dmitry absent
    ['SI-Glob:DI-BbBProc-L:SB_BR_ARM', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_ACQ_SINGLE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_ACQ_EN', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_TRIG_IN_SEL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_TF_ENABLE', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_NFFT', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_NOVERLAP', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_DEL_CAL', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_SP_AVG', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_SP_LOW1', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:SB_SP_HIGH1', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:FBE_DEV_ID', _EMPTY_STR, 0.0],
    ['SI-Glob:DI-BbBProc-L:TRIG1INV', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:TRIG2INV', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHTRK_DECIM', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHTRK_SETPT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHTRK_GAIN', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHTRK_RANGE', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHTRK_LOOPCTRL', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PHTRK_MOD', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:PANEL_BG', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:ILOCK_TSAT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:ILOCK_TOUT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:ILOCK_TAPS', _ZERO_INT, 0.0],
    ['SI-Glob:DI-BbBProc-L:ILOCK_TUNE', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:ILOCK_FE_CAL', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:ILOCK_CURRENT', _ZERO_FLOAT, 0.0],
    ['SI-Glob:DI-BbBProc-L:ILOCK_THRESH', _ZERO_FLOAT, 0.0],
    ]

_pvs_bbb_proc_h, _pvs_bbb_proc_v = [], []
for p, v, d in _pvs_bbb_proc_l:
    _pvs_bbb_proc_h.append([p.replace('oc-L:', 'oc-H:'), v, d])
    _pvs_bbb_proc_v.append([p.replace('oc-L:', 'oc-V:'), v, d])


_template_dict = {
    'pvs':
        _pvs_bbb_proc_h + _pvs_bbb_proc_v + _pvs_bbb_proc_l
    }
