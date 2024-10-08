"""AS Global configuration."""
from copy import deepcopy as _dcopy

from siriuspy.pwrsupply.csdev import \
    DEFAULT_WFM_FBP as _DEFAULT_WFM_FBP, \
    MAX_WFMSIZE_FBP as _MAX_WFMSIZE_FBP, \
    DEFAULT_WFM_OTHERS as _DEFAULT_WFM_OTHERS

from siriuspy.clientconfigdb.types.as_diagnostics import _bpms


_OFF = 0
_ON = 1
_SLOWREF = 0


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


_pvs_li_egunmod = [
    ['LI-01:EG-BiasPS:switch', 0, 0],
    ['LI-01:EG-BiasPS:voltoutsoft', -60.0, 0.0],  # [V]
    ['LI-01:EG-FilaPS:switch', 0, 0],
    ['LI-01:EG-HVPS:currentoutsoft', 0.003, 0.0],  # [mA]
    ['LI-01:EG-HVPS:enable', 0, 0.0],
    ['LI-01:EG-PulsePS:multiselect', 0, 0.0],
    ['LI-01:EG-PulsePS:multiswitch', 0, 0.0],
    ['LI-01:EG-PulsePS:singleselect', 0, 0.0],
    ['LI-01:EG-PulsePS:singleswitch', 0, 0.0],
    ['LI-01:EG-PulsePS:poweroutsoft', 0.0, 0.0],  # [V]
    ['LI-01:PU-Modltr-1:WRITE_I', 100.0, 0.0],  # [mA]
    ['LI-01:PU-Modltr-2:WRITE_I', 100.0, 0.0],  # [mA]
    ['LI-01:PU-Modltr-1:WRITE_V', 0.0, 0.0],  # [kV]
    ['LI-01:PU-Modltr-2:WRITE_V', 0.0, 0.0],  # [kV]
    ]


_pvs_li_llrf = [
    ['LA-RF:LLRF:BUN1:SET_STREAM', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH1_DELAY', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH2_DELAY', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH7_DELAY', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH8_DELAY', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_TRIGGER_DELAY', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_AMP', 0.0, 0.0],  # [%]
    ['LA-RF:LLRF:BUN1:SET_PHASE', 0.0, 0.0],  # [deg]
    ['LA-RF:LLRF:BUN1:SET_KP', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_KI', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH1_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH2_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH7_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH8_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_FBLOOP_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_FBLOOP_AMP_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH1_ADT', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH2_ADT', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH7_ADT', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH8_ADT', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_VM_ADT', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH1_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH2_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH7_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH8_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_PID_KP', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_PID_KI', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_STREAM', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH1_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH2_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH3_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH4_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH5_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH6_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH7_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH8_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH9_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_TRIGGER_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_AMP', 0.0, 0.0],  # [%]
    ['LA-RF:LLRF:KLY1:SET_PHASE', 0.0, 0.0],  # [deg]
    ['LA-RF:LLRF:KLY1:SET_REFL_POWER_LIMIT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_KP', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_KI', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_FBLOOP_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_FBLOOP_AMP_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH1_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH2_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH3_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH4_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH5_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH6_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH7_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH8_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH9_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH1_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH2_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH3_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH4_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH5_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH6_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH7_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH8_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_VM_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH1_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH2_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH3_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH4_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH5_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH6_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH7_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH8_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_CH9_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY1:SET_SHIF_MOTOR_ANGLE', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_STREAM', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH1_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH2_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH3_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH4_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH5_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH6_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH7_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH8_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH9_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_TRIGGER_DELAY', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_AMP', 0.0, 0.0],  # [%]
    ['LA-RF:LLRF:KLY2:SET_PHASE', 0.0, 0.0],  # [deg]
    ['LA-RF:LLRF:KLY2:SET_REFL_POWER_LIMIT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_KP', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_KI', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_FBLOOP_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_FBLOOP_AMP_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH1_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH2_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH3_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH4_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH5_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH6_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH7_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH8_PHASE_CORR', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH1_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH2_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH3_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH4_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH5_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH6_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH7_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH8_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_VM_ADT', 0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH1_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH2_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH3_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH4_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH5_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH6_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH7_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH8_ATT', 0.0, 0.0],
    ['LA-RF:LLRF:KLY2:SET_CH9_ATT', 0.0, 0.0],
    ]


_pvs_as_ti = [
    # Clocks
    ['AS-RaMO:TI-EVG:Clk0MuxDiv-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk0MuxEnbl-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk1MuxDiv-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk1MuxEnbl-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk2MuxDiv-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk2MuxEnbl-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk3MuxDiv-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk3MuxEnbl-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk4MuxDiv-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk4MuxEnbl-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk5MuxDiv-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk5MuxEnbl-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk6MuxDiv-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk6MuxEnbl-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk7MuxDiv-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:Clk7MuxEnbl-Sel', 0, 0.0],

    # Events
    ['AS-RaMO:TI-EVG:CplSIDelayRaw-SP', 0, 0],
    ['AS-RaMO:TI-EVG:CplSIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:CplSIMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:CycleDelayRaw-SP', 0, 0],
    ['AS-RaMO:TI-EVG:CycleDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:CycleMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:InjBODelayRaw-SP', 0, 0],
    ['AS-RaMO:TI-EVG:InjBODelayType-Sel', 0, 0.0],
    # ['AS-RaMO:TI-EVG:InjBOMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:InjSIDelayRaw-SP', 0, 0],
    ['AS-RaMO:TI-EVG:InjSIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:InjSIMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:LinacDelayRaw-SP', 0, 0],
    ['AS-RaMO:TI-EVG:LinacDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:LinacMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:OrbSIDelayRaw-SP', 0, 0],
    ['AS-RaMO:TI-EVG:OrbSIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:OrbSIMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:RmpBODelayRaw-SP', 0, 0],
    ['AS-RaMO:TI-EVG:RmpBODelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:RmpBOMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:StudyDelayRaw-SP', 0, 0],
    ['AS-RaMO:TI-EVG:StudyDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:StudyMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:TunSIDelayRaw-SP', 0, 0],
    ['AS-RaMO:TI-EVG:TunSIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:TunSIMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:FOFBSDelayRaw-SP', 0, 0],
    ['AS-RaMO:TI-EVG:FOFBSDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:FOFBSMode-Sel', 0, 0.0],

    # Triggers
    ['AS-Fam:TI-Scrn-TBBO:DelayRaw-SP', 0, 0],
    ['AS-Fam:TI-Scrn-TBBO:WidthRaw-SP', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:NrPulses-SP', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:Polarity-Sel', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:RFDelayType-Sel', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:Src-Sel', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:State-Sel', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['AS-Fam:TI-Scrn-TBBO:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-FCT:DelayRaw-SP', 0, 0],
    ['AS-Glob:TI-FCT:WidthRaw-SP', 0, 0.0],
    ['AS-Glob:TI-FCT:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-FCT:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-FCT:RFDelayType-Sel', 0, 0.0],
    ['AS-Glob:TI-FCT:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-FCT:State-Sel', 0, 0.0],
    ['AS-Glob:TI-FCT:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['AS-Glob:TI-FCT:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-FillPtrnMon:DelayRaw-SP', 0, 0],
    ['AS-Glob:TI-FillPtrnMon:WidthRaw-SP', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:RFDelayType-Sel', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:State-Sel', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['AS-Glob:TI-FillPtrnMon:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-Osc-EjeBO:DelayRaw-SP', 0, 0],
    ['AS-Glob:TI-Osc-EjeBO:WidthRaw-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:RFDelayType-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:State-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['AS-Glob:TI-Osc-EjeBO:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-Osc-InjBO:DelayRaw-SP', 0, 0],
    ['AS-Glob:TI-Osc-InjBO:WidthRaw-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-InjBO:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-InjBO:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjBO:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjBO:State-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjBO:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['AS-Glob:TI-Osc-InjBO:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-Osc-InjSI:DelayRaw-SP', 0, 0],
    ['AS-Glob:TI-Osc-InjSI:WidthRaw-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI:State-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['AS-Glob:TI-Osc-InjSI:LowLvlLock-Sel', 0, 0.0],

    ['BO-01D:TI-InjKckr:DelayRaw-SP', 0, 0],
    ['BO-01D:TI-InjKckr:WidthRaw-SP', 0, 0.0],
    ['BO-01D:TI-InjKckr:NrPulses-SP', 0, 0.0],
    ['BO-01D:TI-InjKckr:Polarity-Sel', 0, 0.0],
    ['BO-01D:TI-InjKckr:Src-Sel', 0, 0.0],
    ['BO-01D:TI-InjKckr:State-Sel', 0, 0.0],
    ['BO-01D:TI-InjKckr:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-01D:TI-InjKckr:LowLvlLock-Sel', 0, 0.0],

    ['BO-35D:TI-DCCT:DelayRaw-SP', 0, 0],
    ['BO-35D:TI-DCCT:WidthRaw-SP', 0, 0.0],
    ['BO-35D:TI-DCCT:NrPulses-SP', 0, 0.0],
    ['BO-35D:TI-DCCT:Polarity-Sel', 0, 0.0],
    ['BO-35D:TI-DCCT:RFDelayType-Sel', 0, 0.0],
    ['BO-35D:TI-DCCT:Src-Sel', 0, 0.0],
    ['BO-35D:TI-DCCT:State-Sel', 0, 0.0],
    ['BO-35D:TI-DCCT:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-35D:TI-DCCT:LowLvlLock-Sel', 0, 0.0],

    ['BO-48D:TI-EjeKckr:DelayRaw-SP', 0, 0],
    ['BO-48D:TI-EjeKckr:WidthRaw-SP', 0, 0.0],
    ['BO-48D:TI-EjeKckr:NrPulses-SP', 0, 0.0],
    ['BO-48D:TI-EjeKckr:Polarity-Sel', 0, 0.0],
    ['BO-48D:TI-EjeKckr:RFDelayType-Sel', 0, 0.0],
    ['BO-48D:TI-EjeKckr:Src-Sel', 0, 0.0],
    ['BO-48D:TI-EjeKckr:State-Sel', 0, 0.0],
    ['BO-48D:TI-EjeKckr:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-48D:TI-EjeKckr:LowLvlLock-Sel', 0, 0.0],

    ['BO-50U:TI-VLightCam:DelayRaw-SP', 0, 0],
    ['BO-50U:TI-VLightCam:WidthRaw-SP', 0, 0.0],
    ['BO-50U:TI-VLightCam:NrPulses-SP', 0, 0.0],
    ['BO-50U:TI-VLightCam:Polarity-Sel', 0, 0.0],
    ['BO-50U:TI-VLightCam:RFDelayType-Sel', 0, 0.0],
    ['BO-50U:TI-VLightCam:Src-Sel', 0, 0.0],
    ['BO-50U:TI-VLightCam:State-Sel', 0, 0.0],
    ['BO-50U:TI-VLightCam:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-50U:TI-VLightCam:LowLvlLock-Sel', 0, 0.0],

    ['BO-Fam:TI-BPM:DelayRaw-SP', 0, 0],
    ['BO-Fam:TI-BPM:WidthRaw-SP', 0, 0.0],
    ['BO-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
    ['BO-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
    ['BO-Fam:TI-BPM:Src-Sel', 0, 0.0],
    ['BO-Fam:TI-BPM:State-Sel', 0, 0.0],
    ['BO-Fam:TI-BPM:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-Fam:TI-BPM:LowLvlLock-Sel', 0, 0.0],
    ['BO-Fam:TI-BPM:Direction-Sel', 0, 0.0],

    ['BO-Glob:TI-LLRF-Gen:DelayRaw-SP', 0, 0],
    ['BO-Glob:TI-LLRF-Gen:WidthRaw-SP', 0, 0.0],
    ['BO-Glob:TI-LLRF-Gen:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-LLRF-Gen:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Gen:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Gen:State-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Gen:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-Glob:TI-LLRF-Gen:LowLvlLock-Sel', 0, 0.0],

    ['BO-Glob:TI-LLRF-PsMtm:DelayRaw-SP', 0, 0],
    ['BO-Glob:TI-LLRF-PsMtm:WidthRaw-SP', 0, 0.0],
    ['BO-Glob:TI-LLRF-PsMtm:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-LLRF-PsMtm:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-PsMtm:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-PsMtm:State-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-PsMtm:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-Glob:TI-LLRF-PsMtm:LowLvlLock-Sel', 0, 0.0],

    ['BO-Glob:TI-LLRF-Rmp:DelayRaw-SP', 0, 0],
    ['BO-Glob:TI-LLRF-Rmp:WidthRaw-SP', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:State-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-Glob:TI-LLRF-Rmp:LowLvlLock-Sel', 0, 0.0],

    ['BO-Glob:TI-Mags-Corrs:DelayRaw-SP', 0, 0],
    ['BO-Glob:TI-Mags-Corrs:WidthRaw-SP', 0, 0.0],
    ['BO-Glob:TI-Mags-Corrs:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-Mags-Corrs:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Corrs:Src-Sel', 0, 0.0],
    # ['BO-Glob:TI-Mags-Corrs:State-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Corrs:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-Glob:TI-Mags-Corrs:LowLvlLock-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Corrs:Direction-Sel', 0, 0.0],

    ['BO-Glob:TI-Mags-Fams:DelayRaw-SP', 0, 0],
    ['BO-Glob:TI-Mags-Fams:WidthRaw-SP', 0, 0.0],
    ['BO-Glob:TI-Mags-Fams:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-Mags-Fams:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Fams:Src-Sel', 0, 0.0],
    # ['BO-Glob:TI-Mags-Fams:State-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Fams:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-Glob:TI-Mags-Fams:LowLvlLock-Sel', 0, 0.0],

    ['BO-Glob:TI-TuneProc:DelayRaw-SP', 0, 0],
    ['BO-Glob:TI-TuneProc:WidthRaw-SP', 0, 0.0],
    ['BO-Glob:TI-TuneProc:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-TuneProc:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-TuneProc:RFDelayType-Sel', 0, 0.0],
    ['BO-Glob:TI-TuneProc:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-TuneProc:State-Sel', 0, 0.0],
    ['BO-Glob:TI-TuneProc:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['BO-Glob:TI-TuneProc:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-Osc-Modltr:DelayRaw-SP', 0, 0],
    ['LI-01:TI-Osc-Modltr:WidthRaw-SP', 0, 0.0],
    ['LI-01:TI-Osc-Modltr:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-Osc-Modltr:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-Osc-Modltr:Src-Sel', 0, 0.0],
    ['LI-01:TI-Osc-Modltr:State-Sel', 0, 0.0],
    ['LI-01:TI-Osc-Modltr:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-01:TI-Osc-Modltr:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-EGun-MultBun:DelayRaw-SP', 0, 0],
    ['LI-01:TI-EGun-MultBun:WidthRaw-SP', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:RFDelayType-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:Src-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:State-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-01:TI-EGun-MultBun:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-EGun-MultBunPre:DelayRaw-SP', 0, 0],
    ['LI-01:TI-EGun-MultBunPre:WidthRaw-SP', 0, 0.0],
    ['LI-01:TI-EGun-MultBunPre:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-EGun-MultBunPre:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBunPre:RFDelayType-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBunPre:Src-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBunPre:State-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBunPre:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-01:TI-EGun-MultBunPre:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-EGun-SglBun:DelayRaw-SP', 0, 0],
    ['LI-01:TI-EGun-SglBun:WidthRaw-SP', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:RFDelayType-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:Src-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:State-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-01:TI-EGun-SglBun:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-Modltr-1:DelayRaw-SP', 0, 0],
    ['LI-01:TI-Modltr-1:WidthRaw-SP', 0, 0.0],
    ['LI-01:TI-Modltr-1:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-Modltr-1:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-1:Src-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-1:State-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-1:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-01:TI-Modltr-1:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-Modltr-2:DelayRaw-SP', 0, 0],
    ['LI-01:TI-Modltr-2:WidthRaw-SP', 0, 0.0],
    ['LI-01:TI-Modltr-2:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-Modltr-2:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-2:Src-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-2:State-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-2:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-01:TI-Modltr-2:LowLvlLock-Sel', 0, 0.0],

    ['LI-Fam:TI-BPM:DelayRaw-SP', 0, 0],
    ['LI-Fam:TI-BPM:WidthRaw-SP', 0, 0.0],
    ['LI-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
    ['LI-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
    ['LI-Fam:TI-BPM:RFDelayType-Sel', 0, 0.0],
    ['LI-Fam:TI-BPM:Src-Sel', 0, 0.0],
    ['LI-Fam:TI-BPM:State-Sel', 0, 0.0],
    ['LI-Fam:TI-BPM:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-Fam:TI-BPM:LowLvlLock-Sel', 0, 0.0],

    ['LI-Fam:TI-ICT:DelayRaw-SP', 0, 0],
    ['LI-Fam:TI-ICT:WidthRaw-SP', 0, 0.0],
    ['LI-Fam:TI-ICT:NrPulses-SP', 0, 0.0],
    ['LI-Fam:TI-ICT:Polarity-Sel', 0, 0.0],
    ['LI-Fam:TI-ICT:RFDelayType-Sel', 0, 0.0],
    ['LI-Fam:TI-ICT:Src-Sel', 0, 0.0],
    ['LI-Fam:TI-ICT:State-Sel', 0, 0.0],
    ['LI-Fam:TI-ICT:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-Fam:TI-ICT:LowLvlLock-Sel', 0, 0.0],

    ['LI-Fam:TI-Scrn:DelayRaw-SP', 0, 0],
    ['LI-Fam:TI-Scrn:WidthRaw-SP', 0, 0.0],
    ['LI-Fam:TI-Scrn:NrPulses-SP', 0, 0.0],
    ['LI-Fam:TI-Scrn:Polarity-Sel', 0, 0.0],
    ['LI-Fam:TI-Scrn:RFDelayType-Sel', 0, 0.0],
    ['LI-Fam:TI-Scrn:Src-Sel', 0, 0.0],
    ['LI-Fam:TI-Scrn:State-Sel', 0, 0.0],
    ['LI-Fam:TI-Scrn:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-Fam:TI-Scrn:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-LLRF-Kly1:DelayRaw-SP', 0, 0],
    ['LI-Glob:TI-LLRF-Kly1:WidthRaw-SP', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly1:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly1:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly1:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly1:State-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly1:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-Glob:TI-LLRF-Kly1:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-LLRF-Kly2:DelayRaw-SP', 0, 0],
    ['LI-Glob:TI-LLRF-Kly2:WidthRaw-SP', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly2:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly2:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly2:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly2:State-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly2:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-Glob:TI-LLRF-Kly2:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-LLRF-SHB:DelayRaw-SP', 0, 0],
    ['LI-Glob:TI-LLRF-SHB:WidthRaw-SP', 0, 0.0],
    ['LI-Glob:TI-LLRF-SHB:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-LLRF-SHB:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-SHB:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-SHB:State-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-SHB:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-Glob:TI-LLRF-SHB:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-SSAmp-Kly1:DelayRaw-SP', 0, 0],
    ['LI-Glob:TI-SSAmp-Kly1:WidthRaw-SP', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly1:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly1:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly1:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly1:State-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly1:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-Glob:TI-SSAmp-Kly1:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-SSAmp-Kly2:DelayRaw-SP', 0, 0],
    ['LI-Glob:TI-SSAmp-Kly2:WidthRaw-SP', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly2:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly2:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly2:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly2:State-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly2:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-Glob:TI-SSAmp-Kly2:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-SSAmp-SHB:DelayRaw-SP', 0, 0],
    ['LI-Glob:TI-SSAmp-SHB:WidthRaw-SP', 0, 0.0],
    ['LI-Glob:TI-SSAmp-SHB:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-SSAmp-SHB:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-SHB:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-SHB:State-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-SHB:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['LI-Glob:TI-SSAmp-SHB:LowLvlLock-Sel', 0, 0.0],

    ['SI-01SA:TI-InjDpKckr:DelayRaw-SP', 0, 0],
    ['SI-01SA:TI-InjDpKckr:WidthRaw-SP', 0, 0.0],
    ['SI-01SA:TI-InjDpKckr:NrPulses-SP', 0, 0.0],
    ['SI-01SA:TI-InjDpKckr:Polarity-Sel', 0, 0.0],
    ['SI-01SA:TI-InjDpKckr:Src-Sel', 0, 0.0],
    ['SI-01SA:TI-InjDpKckr:State-Sel', 0, 0.0],
    ['SI-01SA:TI-InjDpKckr:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-01SA:TI-InjDpKckr:LowLvlLock-Sel', 0, 0.0],

    ['SI-01SA:TI-InjNLKckr:DelayRaw-SP', 0, 0],
    ['SI-01SA:TI-InjNLKckr:WidthRaw-SP', 0, 0.0],
    ['SI-01SA:TI-InjNLKckr:NrPulses-SP', 0, 0.0],
    ['SI-01SA:TI-InjNLKckr:Polarity-Sel', 0, 0.0],
    ['SI-01SA:TI-InjNLKckr:Src-Sel', 0, 0.0],
    ['SI-01SA:TI-InjNLKckr:State-Sel', 0, 0.0],
    ['SI-01SA:TI-InjNLKckr:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-01SA:TI-InjNLKckr:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-Osc-InjSI2:DelayRaw-SP', 0, 0],
    ['AS-Glob:TI-Osc-InjSI2:WidthRaw-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI2:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI2:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI2:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI2:State-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI2:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['AS-Glob:TI-Osc-InjSI2:LowLvlLock-Sel', 0, 0.0],

    ['SI-13C4:TI-DCCT:DelayRaw-SP', 0, 0],
    ['SI-13C4:TI-DCCT:WidthRaw-SP', 0, 0.0],
    ['SI-13C4:TI-DCCT:NrPulses-SP', 0, 0.0],
    ['SI-13C4:TI-DCCT:Polarity-Sel', 0, 0.0],
    ['SI-13C4:TI-DCCT:RFDelayType-Sel', 0, 0.0],
    ['SI-13C4:TI-DCCT:Src-Sel', 0, 0.0],
    ['SI-13C4:TI-DCCT:State-Sel', 0, 0.0],
    ['SI-13C4:TI-DCCT:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-13C4:TI-DCCT:LowLvlLock-Sel', 0, 0.0],

    ['SI-14C4:TI-DCCT:DelayRaw-SP', 0, 0],
    ['SI-14C4:TI-DCCT:WidthRaw-SP', 0, 0.0],
    ['SI-14C4:TI-DCCT:NrPulses-SP', 0, 0.0],
    ['SI-14C4:TI-DCCT:Polarity-Sel', 0, 0.0],
    ['SI-14C4:TI-DCCT:RFDelayType-Sel', 0, 0.0],
    ['SI-14C4:TI-DCCT:Src-Sel', 0, 0.0],
    ['SI-14C4:TI-DCCT:State-Sel', 0, 0.0],
    ['SI-14C4:TI-DCCT:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-14C4:TI-DCCT:LowLvlLock-Sel', 0, 0.0],

    ['SI-19C4:TI-PingV:DelayRaw-SP', 0, 0],
    ['SI-19C4:TI-PingV:WidthRaw-SP', 0, 0.0],
    ['SI-19C4:TI-PingV:NrPulses-SP', 0, 0.0],
    ['SI-19C4:TI-PingV:Polarity-Sel', 0, 0.0],
    ['SI-19C4:TI-PingV:RFDelayType-Sel', 0, 0.0],
    ['SI-19C4:TI-PingV:Src-Sel', 0, 0.0],
    ['SI-19C4:TI-PingV:State-Sel', 0, 0.0],
    ['SI-19C4:TI-PingV:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-19C4:TI-PingV:LowLvlLock-Sel', 0, 0.0],

    ['SI-Fam:TI-BPM:DelayRaw-SP', 0, 0],
    ['SI-Fam:TI-BPM:WidthRaw-SP', 0, 0.0],
    ['SI-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
    ['SI-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM:Src-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM:State-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Fam:TI-BPM:LowLvlLock-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM:Direction-Sel', 0, 0.0],

    ['SI-Fam:TI-BPM-PsMtm:DelayRaw-SP', 0, 0],
    ['SI-Fam:TI-BPM-PsMtm:WidthRaw-SP', 0, 0.0],
    ['SI-Fam:TI-BPM-PsMtm:NrPulses-SP', 0, 0.0],
    ['SI-Fam:TI-BPM-PsMtm:Polarity-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM-PsMtm:Src-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM-PsMtm:State-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM-PsMtm:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Fam:TI-BPM-PsMtm:LowLvlLock-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM-PsMtm:Direction-Sel', 0, 0.0],

    ['AS-Fam:TI-BPM-MonitClk:DelayRaw-SP', 0, 0],
    ['AS-Fam:TI-BPM-MonitClk:WidthRaw-SP', 0, 0.0],
    ['AS-Fam:TI-BPM-MonitClk:NrPulses-SP', 0, 0.0],
    ['AS-Fam:TI-BPM-MonitClk:Polarity-Sel', 0, 0.0],
    ['AS-Fam:TI-BPM-MonitClk:Src-Sel', 0, 0.0],
    ['AS-Fam:TI-BPM-MonitClk:State-Sel', 0, 0.0],
    ['AS-Fam:TI-BPM-MonitClk:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['AS-Fam:TI-BPM-MonitClk:LowLvlLock-Sel', 0, 0.0],
    ['AS-Fam:TI-BPM-MonitClk:Direction-Sel', 0, 0.0],

    ['SI-Fam:TI-BPM-OrbIntlk:DelayRaw-SP', 0, 0],
    ['SI-Fam:TI-BPM-OrbIntlk:WidthRaw-SP', 0, 0.0],
    ['SI-Fam:TI-BPM-OrbIntlk:NrPulses-SP', 0, 0.0],
    ['SI-Fam:TI-BPM-OrbIntlk:Polarity-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM-OrbIntlk:Src-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM-OrbIntlk:State-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM-OrbIntlk:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Fam:TI-BPM-OrbIntlk:LowLvlLock-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM-OrbIntlk:Direction-Sel', 1, 0.0],

    ['SI-Fam:TI-FOFB:DelayRaw-SP', 0, 0],
    ['SI-Fam:TI-FOFB:WidthRaw-SP', 0, 0.0],
    ['SI-Fam:TI-FOFB:NrPulses-SP', 0, 0.0],
    ['SI-Fam:TI-FOFB:Polarity-Sel', 0, 0.0],
    ['SI-Fam:TI-FOFB:Src-Sel', 0, 0.0],
    ['SI-Fam:TI-FOFB:State-Sel', 0, 0.0],
    ['SI-Fam:TI-FOFB:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Fam:TI-FOFB:LowLvlLock-Sel', 0, 0.0],
    ['SI-Fam:TI-FOFB:Direction-Sel', 0, 0.0],

    ['SI-01:TI-Mags-FFCorrs:DelayRaw-SP', 0, 0],
    ['SI-01:TI-Mags-FFCorrs:WidthRaw-SP', 0, 0.0],
    ['SI-01:TI-Mags-FFCorrs:NrPulses-SP', 0, 0.0],
    ['SI-01:TI-Mags-FFCorrs:Polarity-Sel', 0, 0.0],
    ['SI-01:TI-Mags-FFCorrs:Src-Sel', 0, 0.0],
    ['SI-01:TI-Mags-FFCorrs:State-Sel', 0, 0.0],
    ['SI-01:TI-Mags-FFCorrs:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-01:TI-Mags-FFCorrs:LowLvlLock-Sel', 0, 0.0],
    ['SI-01:TI-Mags-FFCorrs:Direction-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcH-Fid:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-BbBProcH-Fid:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:RFDelayType-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-BbBProcH-Fid:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcH-Trig1:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-BbBProcH-Trig1:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig1:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig1:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig1:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig1:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig1:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-BbBProcH-Trig1:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcH-Trig2:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-BbBProcH-Trig2:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig2:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig2:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig2:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig2:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig2:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-BbBProcH-Trig2:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcL-Fid:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-BbBProcL-Fid:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:RFDelayType-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-BbBProcL-Fid:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcL-Trig1:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-BbBProcL-Trig1:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig1:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig1:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig1:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig1:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig1:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-BbBProcL-Trig1:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcL-Trig2:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-BbBProcL-Trig2:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig2:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig2:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig2:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig2:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig2:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-BbBProcL-Trig2:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcV-Fid:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-BbBProcV-Fid:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:RFDelayType-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-BbBProcV-Fid:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcV-Trig1:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-BbBProcV-Trig1:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig1:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig1:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig1:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig1:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig1:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-BbBProcV-Trig1:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcV-Trig2:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-BbBProcV-Trig2:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig2:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig2:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig2:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig2:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig2:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-BbBProcV-Trig2:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-LLRF-Gen:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-LLRF-Gen:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-LLRF-Gen:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-LLRF-Gen:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-Gen:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-Gen:State-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-Gen:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-LLRF-Gen:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-LLRF-PsMtm:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-LLRF-PsMtm:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-LLRF-PsMtm:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-LLRF-PsMtm:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-PsMtm:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-PsMtm:State-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-PsMtm:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-LLRF-PsMtm:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-LLRF-Rmp:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-LLRF-Rmp:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-LLRF-Rmp:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-LLRF-Rmp:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-Rmp:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-Rmp:State-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-Rmp:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-LLRF-Rmp:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-Bends:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-Mags-Bends:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Bends:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Bends:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Bends:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Bends:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Bends:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-Mags-Bends:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-Corrs:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-Mags-Corrs:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Corrs:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Corrs:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Corrs:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Corrs:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Corrs:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-Mags-Corrs:LowLvlLock-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Corrs:Direction-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-Quads:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-Mags-Quads:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Quads:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Quads:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Quads:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Quads:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Quads:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-Mags-Quads:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-QTrims:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-Mags-QTrims:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-QTrims:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-QTrims:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-QTrims:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-QTrims:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-QTrims:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-Mags-QTrims:LowLvlLock-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-QTrims:Direction-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-Sexts:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-Mags-Sexts:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Sexts:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Sexts:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Sexts:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Sexts:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Sexts:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-Mags-Sexts:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-Skews:DelayRaw-SP', 0, 0],
    ['SI-Glob:TI-Mags-Skews:WidthRaw-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Skews:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Skews:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Skews:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Skews:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Skews:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['SI-Glob:TI-Mags-Skews:LowLvlLock-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Skews:Direction-Sel', 0, 0.0],

    # NOTE: This trigger is not present yet in timing IOC:
    # ['SI-Glob:TI-StrkCam-Trig1:DelayRaw-SP', 0, 0],
    # ['SI-Glob:TI-StrkCam-Trig1:WidthRaw-SP', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig1:NrPulses-SP', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig1:Polarity-Sel', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig1:RFDelayType-Sel', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig1:Src-Sel', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig1:State-Sel', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig1:DeltaDelayRaw-SP', 30*[0, ], 0],
    # ['SI-Glob:TI-StrkCam-Trig1:LowLvlLock-Sel', 0, 0.0],

    # ['SI-Glob:TI-StrkCam-Trig2:DelayRaw-SP', 0, 0],
    # ['SI-Glob:TI-StrkCam-Trig2:WidthRaw-SP', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig2:NrPulses-SP', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig2:Polarity-Sel', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig2:RFDelayType-Sel', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig2:Src-Sel', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig2:State-Sel', 0, 0.0],
    # ['SI-Glob:TI-StrkCam-Trig2:DeltaDelayRaw-SP', 30*[0, ], 0],
    # ['SI-Glob:TI-StrkCam-Trig2:LowLvlLock-Sel', 0, 0.0],

    ['TB-04:TI-InjSept:DelayRaw-SP', 0, 0],
    ['TB-04:TI-InjSept:WidthRaw-SP', 0, 0.0],
    ['TB-04:TI-InjSept:NrPulses-SP', 0, 0.0],
    ['TB-04:TI-InjSept:Polarity-Sel', 0, 0.0],
    ['TB-04:TI-InjSept:Src-Sel', 0, 0.0],
    ['TB-04:TI-InjSept:State-Sel', 0, 0.0],
    ['TB-04:TI-InjSept:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TB-04:TI-InjSept:LowLvlLock-Sel', 0, 0.0],

    ['TB-Fam:TI-BPM:DelayRaw-SP', 0, 0],
    ['TB-Fam:TI-BPM:WidthRaw-SP', 0, 0.0],
    ['TB-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
    ['TB-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
    ['TB-Fam:TI-BPM:Src-Sel', 0, 0.0],
    ['TB-Fam:TI-BPM:State-Sel', 0, 0.0],
    ['TB-Fam:TI-BPM:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TB-Fam:TI-BPM:LowLvlLock-Sel', 0, 0.0],
    ['TB-Fam:TI-BPM:Direction-Sel', 0, 0.0],

    ['TB-Fam:TI-ICT-Digit:DelayRaw-SP', 0, 0],
    ['TB-Fam:TI-ICT-Digit:WidthRaw-SP', 0, 0.0],
    ['TB-Fam:TI-ICT-Digit:NrPulses-SP', 0, 0.0],
    ['TB-Fam:TI-ICT-Digit:Polarity-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Digit:Src-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Digit:State-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Digit:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TB-Fam:TI-ICT-Digit:LowLvlLock-Sel', 0, 0.0],

    ['TB-Fam:TI-ICT-Integ:DelayRaw-SP', 0, 0],
    ['TB-Fam:TI-ICT-Integ:WidthRaw-SP', 0, 0.0],
    ['TB-Fam:TI-ICT-Integ:NrPulses-SP', 0, 0.0],
    ['TB-Fam:TI-ICT-Integ:Polarity-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Integ:Src-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Integ:State-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Integ:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TB-Fam:TI-ICT-Integ:LowLvlLock-Sel', 0, 0.0],

    ['TB-Glob:TI-Mags:DelayRaw-SP', 0, 0],
    ['TB-Glob:TI-Mags:WidthRaw-SP', 0, 0.0],
    ['TB-Glob:TI-Mags:NrPulses-SP', 0, 0.0],
    ['TB-Glob:TI-Mags:Polarity-Sel', 0, 0.0],
    ['TB-Glob:TI-Mags:Src-Sel', 0, 0.0],
    ['TB-Glob:TI-Mags:State-Sel', 0, 0.0],
    ['TB-Glob:TI-Mags:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TB-Glob:TI-Mags:LowLvlLock-Sel', 0, 0.0],

    ['TS-01:TI-EjeSeptF:DelayRaw-SP', 0, 0],
    ['TS-01:TI-EjeSeptF:WidthRaw-SP', 0, 0.0],
    ['TS-01:TI-EjeSeptF:NrPulses-SP', 0, 0.0],
    ['TS-01:TI-EjeSeptF:Polarity-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptF:RFDelayType-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptF:Src-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptF:State-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptF:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TS-01:TI-EjeSeptF:LowLvlLock-Sel', 0, 0.0],

    ['TS-01:TI-EjeSeptG:DelayRaw-SP', 0, 0],
    ['TS-01:TI-EjeSeptG:WidthRaw-SP', 0, 0.0],
    ['TS-01:TI-EjeSeptG:NrPulses-SP', 0, 0.0],
    ['TS-01:TI-EjeSeptG:Polarity-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptG:RFDelayType-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptG:Src-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptG:State-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptG:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TS-01:TI-EjeSeptG:LowLvlLock-Sel', 0, 0.0],

    ['TS-04:TI-InjSeptF:DelayRaw-SP', 0, 0],
    ['TS-04:TI-InjSeptF:WidthRaw-SP', 0, 0.0],
    ['TS-04:TI-InjSeptF:NrPulses-SP', 0, 0.0],
    ['TS-04:TI-InjSeptF:Polarity-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptF:Src-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptF:State-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptF:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TS-04:TI-InjSeptF:LowLvlLock-Sel', 0, 0.0],

    ['TS-04:TI-InjSeptG-1:DelayRaw-SP', 0, 0],
    ['TS-04:TI-InjSeptG-1:WidthRaw-SP', 0, 0.0],
    ['TS-04:TI-InjSeptG-1:NrPulses-SP', 0, 0.0],
    ['TS-04:TI-InjSeptG-1:Polarity-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-1:Src-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-1:State-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-1:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TS-04:TI-InjSeptG-1:LowLvlLock-Sel', 0, 0.0],

    ['TS-04:TI-InjSeptG-2:DelayRaw-SP', 0, 0],
    ['TS-04:TI-InjSeptG-2:WidthRaw-SP', 0, 0.0],
    ['TS-04:TI-InjSeptG-2:NrPulses-SP', 0, 0.0],
    ['TS-04:TI-InjSeptG-2:Polarity-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-2:Src-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-2:State-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-2:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TS-04:TI-InjSeptG-2:LowLvlLock-Sel', 0, 0.0],

    ['TS-Fam:TI-BPM:DelayRaw-SP', 0, 0],
    ['TS-Fam:TI-BPM:WidthRaw-SP', 0, 0.0],
    ['TS-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
    ['TS-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
    ['TS-Fam:TI-BPM:Src-Sel', 0, 0.0],
    ['TS-Fam:TI-BPM:State-Sel', 0, 0.0],
    ['TS-Fam:TI-BPM:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TS-Fam:TI-BPM:LowLvlLock-Sel', 0, 0.0],
    ['TS-Fam:TI-BPM:Direction-Sel', 0, 0.0],

    ['TS-Fam:TI-ICT-Digit:DelayRaw-SP', 0, 0],
    ['TS-Fam:TI-ICT-Digit:WidthRaw-SP', 0, 0.0],
    ['TS-Fam:TI-ICT-Digit:NrPulses-SP', 0, 0.0],
    ['TS-Fam:TI-ICT-Digit:Polarity-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Digit:Src-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Digit:State-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Digit:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TS-Fam:TI-ICT-Digit:LowLvlLock-Sel', 0, 0.0],

    ['TS-Fam:TI-ICT-Integ:DelayRaw-SP', 0, 0],
    ['TS-Fam:TI-ICT-Integ:WidthRaw-SP', 0, 0.0],
    ['TS-Fam:TI-ICT-Integ:NrPulses-SP', 0, 0.0],
    ['TS-Fam:TI-ICT-Integ:Polarity-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Integ:Src-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Integ:State-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Integ:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TS-Fam:TI-ICT-Integ:LowLvlLock-Sel', 0, 0.0],

    ['TS-Fam:TI-Scrn:DelayRaw-SP', 0, 0],
    ['TS-Fam:TI-Scrn:WidthRaw-SP', 0, 0.0],
    ['TS-Fam:TI-Scrn:NrPulses-SP', 0, 0.0],
    ['TS-Fam:TI-Scrn:Polarity-Sel', 0, 0.0],
    ['TS-Fam:TI-Scrn:RFDelayType-Sel', 0, 0.0],
    ['TS-Fam:TI-Scrn:Src-Sel', 0, 0.0],
    ['TS-Fam:TI-Scrn:State-Sel', 0, 0.0],
    ['TS-Fam:TI-Scrn:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TS-Fam:TI-Scrn:LowLvlLock-Sel', 0, 0.0],

    ['TS-Glob:TI-Mags:DelayRaw-SP', 0, 0],
    ['TS-Glob:TI-Mags:WidthRaw-SP', 0, 0.0],
    ['TS-Glob:TI-Mags:NrPulses-SP', 0, 0.0],
    ['TS-Glob:TI-Mags:Polarity-Sel', 0, 0.0],
    ['TS-Glob:TI-Mags:Src-Sel', 0, 0.0],
    ['TS-Glob:TI-Mags:State-Sel', 0, 0.0],
    ['TS-Glob:TI-Mags:DeltaDelayRaw-SP', 30*[0, ], 0],
    ['TS-Glob:TI-Mags:LowLvlLock-Sel', 0, 0.0],

    ]


_pvs_li_ps = [
    ['LI-01:PS-LensRev:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Lens-1:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Lens-2:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Lens-3:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Lens-4:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-1:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-2:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-3:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-4:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-5:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-6:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-7:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-8:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-9:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-10:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-11:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-12:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Slnd-13:Current-SP', 0.0, 0.0],  # [A]
    ['LI-Fam:PS-Slnd-14:Current-SP', 0.0, 0.0],  # [A]
    ['LI-Fam:PS-Slnd-15:Current-SP', 0.0, 0.0],  # [A]
    ['LI-Fam:PS-Slnd-16:Current-SP', 0.0, 0.0],  # [A]
    ['LI-Fam:PS-Slnd-17:Current-SP', 0.0, 0.0],  # [A]
    ['LI-Fam:PS-Slnd-18:Current-SP', 0.0, 0.0],  # [A]
    ['LI-Fam:PS-Slnd-19:Current-SP', 0.0, 0.0],  # [A]
    ['LI-Fam:PS-Slnd-20:Current-SP', 0.0, 0.0],  # [A]
    ['LI-Fam:PS-Slnd-21:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CH-1:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CH-2:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CV-3:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CH-3:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CV-4:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CH-4:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CV-5:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CH-5:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CV-6:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CH-6:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CV-7:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-CH-7:Current-SP', 0.0, 0.0],  # [A]
    ['LI-Fam:PS-QF1:Current-SP', 0.0, 0.0],  # [A]
    ['LI-Fam:PS-QF2:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-QF3:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-QD1:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-QD2:Current-SP', 0.0, 0.0],  # [A]
    ['LI-01:PS-Spect:Current-SP', 0.0, 0.0],  # [A]
    ]


_pvs_as_pu = [
    ['TB-04:PU-InjSept:Voltage-SP', 0.0, 0.0],   # [V]
    ['BO-01D:PU-InjKckr:Voltage-SP', 0.0, 0.0],  # [V]
    ['BO-48D:PU-EjeKckr:Voltage-SP', 0.0, 0.0],  # [V]
    ['SI-01SA:PU-InjDpKckr:Voltage-SP', 0.0, 0.0],  # [V]
    ['SI-01SA:PU-InjNLKckr:Voltage-SP', 0.0, 0.0],  # [V]
    ['SI-01SA:PU-InjNLKckr:CCoilHVoltage-SP', 0.0, 0.0],  # [V]
    ['SI-01SA:PU-InjNLKckr:CCoilVVoltage-SP', 0.0, 0.0],  # [V]
    ['TS-04:PU-InjSeptG-1:Voltage-SP', 0.0, 0.0],  # [V]
    ['TS-04:PU-InjSeptG-2:Voltage-SP', 0.0, 0.0],  # [V]
    ['TS-04:PU-InjSeptF:Voltage-SP', 0.0, 0.0],  # [V]
    ['TS-01:PU-EjeSeptG:Voltage-SP', 0.0, 0.0],  # [V]
    ['TS-01:PU-EjeSeptF:Voltage-SP', 0.0, 0.1],  # [V]
    ]


_pvs_as_rf = [
    ['RF-Gen:FreqPhsCont-Sel', 0, 0.0],
    ['RF-Gen:GeneralFreq-SP', 0.0, 0.0],  # [Hz]
    ]


_pvs_bo_llrf = [
    ['RA-RaBO01:RF-LLRF:SLKI-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:SLKP-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:AmpIncRate-SP', 0, 0.0],  # mV
    ['RA-RaBO01:RF-LLRF:PhsIncRate-SP', 0, 0.0],  # Deg
    ['RA-RaBO01:RF-LLRF:ALRef-SP', 0, 0.0],  # mV
    ['RA-RaBO01:RF-LLRF:PLRef-SP', 0, 0.0],  # Deg
    ['RA-RaBO01:RF-LLRF:TuneMarginHI-SP', 0, 0.0],  # Deg
    ['RA-RaBO01:RF-LLRF:TuneMarginLO-SP', 0, 0.0],  # Deg
    ['RA-RaBO01:RF-LLRF:Detune-SP', 0, 0.0],  # Deg
    ['RA-RaBO01:RF-LLRF:FFGainCell2-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FFGainCell4-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FFDeadBand-SP', 0, 0.0],  # %
    ['RA-RaBO01:RF-LLRF:RmpTs1-SP', 0, 0.0],  # ms
    ['RA-RaBO01:RF-LLRF:RmpTs2-SP', 0, 0.0],  # ms
    ['RA-RaBO01:RF-LLRF:RmpTs3-SP', 0, 0.0],  # ms
    ['RA-RaBO01:RF-LLRF:RmpTs4-SP', 0, 0.0],  # ms
    ['RA-RaBO01:RF-LLRF:RmpPhsTop-SP', 0, 0.0],  # Deg
    ['RA-RaBO01:RF-LLRF:RmpPhsBot-SP', 0, 0.0],  # Deg
    ['RA-RaBO01:RF-LLRF:RmpAmpTop-SP', 0, 0.0],  # mV
    ['RA-RaBO01:RF-LLRF:RmpAmpBot-SP', 0, 0.0],  # mV
    ]


_pvs_si_llrf_a = [
    ['RA-RaSIA01:RF-LLRF:SLKI-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:SLKP-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:AmpIncRate-SP', 0, 0.0],  # mV
    ['RA-RaSIA01:RF-LLRF:PhsIncRate-SP', 0, 0.0],  # Deg
    ['RA-RaSIA01:RF-LLRF:ALRef-SP', 0, 0.0],  # mV
    ['RA-RaSIA01:RF-LLRF:PLRef-SP', 0, 0.0],  # Deg
    ['RA-RaSIA01:RF-LLRF:TuneMarginHI-SP', 0, 0.0],  # Deg
    ['RA-RaSIA01:RF-LLRF:TuneMarginLO-SP', 0, 0.0],  # Deg
    ['RA-RaSIA01:RF-LLRF:Detune-SP', 0, 0.0],  # Deg
    ]

_pvs_si_llrf_b = [
    ['RA-RaSIB01:RF-LLRF:SLKI-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:SLKP-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:AmpIncRate-SP', 0, 0.0],  # mV
    ['RA-RaSIB01:RF-LLRF:PhsIncRate-SP', 0, 0.0],  # Deg
    ['RA-RaSIB01:RF-LLRF:ALRef-SP', 0, 0.0],  # mV
    ['RA-RaSIB01:RF-LLRF:PLRef-SP', 0, 0.0],  # Deg
    ['RA-RaSIB01:RF-LLRF:TuneMarginHI-SP', 0, 0.0],  # Deg
    ['RA-RaSIB01:RF-LLRF:TuneMarginLO-SP', 0, 0.0],  # Deg
    ['RA-RaSIB01:RF-LLRF:Detune-SP', 0, 0.0],  # Deg
    ]

_bpm_propts = [
    [':RFFEAtt-SP', 0.0, 0.0],
    ]

_bpm_pvs = list()
for dev in _bpms:
    for ppt, val, dly in _bpm_propts:
        _bpm_pvs.append([dev+ppt, val, dly])

_pvs_tb_ps = [
    ['TB-Fam:PS-B:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-01:PS-QD1:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-01:PS-QF1:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-02:PS-QD2A:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-02:PS-QF2A:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-02:PS-QF2B:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-02:PS-QD2B:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-03:PS-QF3:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-03:PS-QD3:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-04:PS-QF4:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-04:PS-QD4:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-01:PS-CH-1:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-01:PS-CV-1:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-01:PS-CH-2:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-01:PS-CV-2:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-02:PS-CH-1:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-02:PS-CV-1:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-02:PS-CH-2:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-02:PS-CV-2:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-04:PS-CH-1:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-04:PS-CH-2:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-04:PS-CV-1:OpMode-Sel', _SLOWREF, 0.0],
    ['TB-04:PS-CV-2:OpMode-Sel', _SLOWREF, 0.05],

    ['TB-Fam:PS-B:Current-SP', 0.0, 0.0],    # [A]
    ['TB-01:PS-QD1:Current-SP', 0.0, 0.0],   # [A]
    ['TB-01:PS-QF1:Current-SP', 0.0, 0.0],   # [A]
    ['TB-02:PS-QD2A:Current-SP', 0.0, 0.0],  # [A]
    ['TB-02:PS-QF2A:Current-SP', 0.0, 0.0],  # [A]
    ['TB-02:PS-QF2B:Current-SP', 0.0, 0.0],  # [A]
    ['TB-02:PS-QD2B:Current-SP', 0.0, 0.0],  # [A]
    ['TB-03:PS-QF3:Current-SP', 0.0, 0.0],   # [A]
    ['TB-03:PS-QD3:Current-SP', 0.0, 0.0],   # [A]
    ['TB-04:PS-QF4:Current-SP', 0.0, 0.0],   # [A]
    ['TB-04:PS-QD4:Current-SP', 0.0, 0.0],   # [A]
    ['TB-01:PS-CH-1:Current-SP', 0.0, 0.0],  # [A]
    ['TB-01:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['TB-01:PS-CH-2:Current-SP', 0.0, 0.0],  # [A]
    ['TB-01:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['TB-02:PS-CH-1:Current-SP', 0.0, 0.0],  # [A]
    ['TB-02:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['TB-02:PS-CH-2:Current-SP', 0.0, 0.0],  # [A]
    ['TB-02:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['TB-04:PS-CH-1:Current-SP', 0.0, 0.0],  # [A]
    ['TB-04:PS-CH-2:Current-SP', 0.0, 0.0],  # [A]
    ['TB-04:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['TB-04:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ]


_pvs_bo_ps = [
    ['BO-Fam:PS-B-1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],  # [A]
    ['BO-Fam:PS-B-2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],  # [A]
    ['BO-Fam:PS-QD:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],  # [A]
    ['BO-Fam:PS-QF:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],  # [A]
    ['BO-Fam:PS-SD:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],  # [A]
    ['BO-Fam:PS-SF:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],  # [A]
    ['BO-02D:PS-QS:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-01U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-03U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-05U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-07U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-09U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-11U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-13U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-15U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-17U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-19U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-21U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-23U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-25U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-27U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-29U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-31U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-33U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-35U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-37U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-39U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-41U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-43U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-45U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-47U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-49D:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-01U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-03U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-05U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-07U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-09U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-11U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-13U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-15U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-17U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-19U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-21U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-23U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-25U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-27U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-29U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-31U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-33U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-35U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-37U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-39U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-41U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-43U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-45U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-47U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['BO-49U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ]


_pvs_ts_ps = [
    ['TS-Fam:PS-B:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-01:PS-QF1A:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-01:PS-QF1B:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-02:PS-QF2:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-03:PS-QF3:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-04:PS-QF4:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-02:PS-QD2:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-04:PS-QD4A:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-04:PS-QD4B:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-01:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-02:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-03:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-04:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-01:PS-CV-1:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-01:PS-CV-1E2:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-01:PS-CV-2:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-02:PS-CV-0:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-02:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-03:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-04:PS-CV-0:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-04:PS-CV-1:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-04:PS-CV-1E2:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-04:PS-CV-2:OpMode-Sel', _SLOWREF, 0.05],

    ['TS-Fam:PS-B:Current-SP', 0.0, 0.0],    # [A]
    ['TS-01:PS-QF1A:Current-SP', 0.0, 0.0],   # [A]
    ['TS-01:PS-QF1B:Current-SP', 0.0, 0.0],   # [A]
    ['TS-02:PS-QF2:Current-SP', 0.0, 0.0],  # [A]
    ['TS-03:PS-QF3:Current-SP', 0.0, 0.0],  # [A]
    ['TS-04:PS-QF4:Current-SP', 0.0, 0.0],  # [A]
    ['TS-02:PS-QD2:Current-SP', 0.0, 0.0],  # [A]
    ['TS-04:PS-QD4A:Current-SP', 0.0, 0.0],   # [A]
    ['TS-04:PS-QD4B:Current-SP', 0.0, 0.0],   # [A]
    ['TS-01:PS-CH:Current-SP', 0.0, 0.0],   # [A]
    ['TS-02:PS-CH:Current-SP', 0.0, 0.0],   # [A]
    ['TS-03:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['TS-04:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['TS-01:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['TS-01:PS-CV-1E2:Current-SP', 0.0, 0.0],  # [A]
    ['TS-01:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['TS-02:PS-CV-0:Current-SP', 0.0, 0.0],  # [A]
    ['TS-02:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['TS-03:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['TS-04:PS-CV-0:Current-SP', 0.0, 0.0],  # [A]
    ['TS-04:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['TS-04:PS-CV-1E2:Current-SP', 0.0, 0.0],  # [A]
    ['TS-04:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ]


_pvs_si_ps_fam = [
    ['SI-Fam:PS-B1B2-1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-B1B2-2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-QFA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SFA0:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SFA1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SFA2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SFB0:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SFB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SFB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SFP0:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SFP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SFP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDA0:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDA1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDA2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDA3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDB0:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDB3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDP0:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-Fam:PS-SDP3:OpMode-Sel', _SLOWREF, 0.05],

    ['SI-Fam:PS-B1B2-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-B1B2-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SFA0:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SFA1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SFA2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SFB0:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SFB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SFB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SFP0:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SFP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SFP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDA0:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDA1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDA2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDA3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDB0:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDB3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDP0:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-Fam:PS-SDP3:Current-SP', 0.0, 0.0],  # [A]
    ]


_pvs_si_ps_ch = [
    # NOTE: these are SOFB correctors usually used in SlowRefSync/Wfm mode.
    ['SI-01M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C1:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C2:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C3:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C4:PS-CH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01M1:PS-CH:Current-SP', 0.0, 0.0],  # [A]

    ['SI-01M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20M2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20C1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20C2:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20C3:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20C4:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01M1:PS-CH:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ]


_pvs_si_ps_cv = [
    # NOTE: these are SOFB correctors usually used in SlowRefSync/Wfm mode.
    ['SI-01M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M2:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C1:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C2:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C2:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C3:PS-CV-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C3:PS-CV-2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C4:PS-CV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01M1:PS-CV:Current-SP', 0.0, 0.0],  # [A]

    ['SI-01M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-02C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-03C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-04C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-05C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-06C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-07C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-08C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-09C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-10C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-11C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-12C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-13C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-14C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-15C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-16C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-17C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-18C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-19C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20M2:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20C1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20C2:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20C2:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20C3:PS-CV-1:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20C3:PS-CV-2:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-20C4:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ['SI-01M1:PS-CV:Wfm-SP', _MAX_WFMSIZE_FBP, 0.0],  # [A]
    ]


_pvs_si_ps_qs = [
    ['SI-01M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20M1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20M2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C1:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C2:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C3:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01M1:PS-QS:OpMode-Sel', _SLOWREF, 0.05],

    ['SI-01M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C2:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C3:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01M1:PS-QS:Current-SP', 0.0, 0.0],  # [A]
    ]


_pvs_si_ps_qn = [
    ['SI-01M2:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01M2:PS-QFA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02M1:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02M1:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02M1:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02M2:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02M2:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02M2:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-02C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03M1:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03M1:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03M1:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03M2:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03M2:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03M2:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-03C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04M1:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04M1:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04M1:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04M2:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04M2:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04M2:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-04C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05M1:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05M1:PS-QFA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05M2:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05M2:PS-QFA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-05C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06M1:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06M1:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06M1:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06M2:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06M2:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06M2:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-06C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07M1:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07M1:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07M1:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07M2:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07M2:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07M2:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-07C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08M1:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08M1:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08M1:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08M2:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08M2:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08M2:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-08C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09M1:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09M1:PS-QFA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09M2:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09M2:PS-QFA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-09C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10M1:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10M1:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10M1:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10M2:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10M2:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10M2:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-10C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11M1:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11M1:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11M1:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11M2:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11M2:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11M2:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-11C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12M1:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12M1:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12M1:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12M2:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12M2:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12M2:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-12C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13M1:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13M1:PS-QFA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13M2:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13M2:PS-QFA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-13C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14M1:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14M1:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14M1:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14M2:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14M2:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14M2:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15M1:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15M1:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15M1:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15M2:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15M2:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15M2:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-15C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16M1:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16M1:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16M1:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16M2:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16M2:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16M2:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-16C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17M1:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17M1:PS-QFA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17M2:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17M2:PS-QFA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-17C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18M1:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18M1:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18M1:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18M2:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18M2:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18M2:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-18C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19M1:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19M1:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19M1:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19M2:PS-QDP1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19M2:PS-QDP2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19M2:PS-QFP:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-19C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20M1:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20M1:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20M1:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20M2:PS-QDB1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20M2:PS-QDB2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20M2:PS-QFB:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C1:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C1:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C2:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C2:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C3:PS-Q3:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C3:PS-Q4:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C4:PS-Q1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-20C4:PS-Q2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01M1:PS-QDA:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01M1:PS-QFA:OpMode-Sel', _SLOWREF, 0.05],

    ['SI-01M2:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01M2:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M1:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M1:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M1:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M2:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M2:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02M2:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-02C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M1:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M1:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M1:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M2:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M2:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03M2:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-03C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M1:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M1:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M1:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M2:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M2:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04M2:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-04C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05M1:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05M1:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05M2:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05M2:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-05C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M1:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M1:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M1:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M2:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M2:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06M2:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-06C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M1:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M1:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M1:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M2:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M2:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07M2:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-07C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M1:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M1:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M1:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M2:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M2:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08M2:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-08C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09M1:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09M1:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09M2:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09M2:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-09C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M1:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M1:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M1:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M2:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M2:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10M2:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-10C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M1:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M1:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M1:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M2:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M2:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11M2:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-11C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M1:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M1:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M1:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M2:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M2:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12M2:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-12C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13M1:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13M1:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13M2:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13M2:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-13C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M1:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M1:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M1:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M2:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M2:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14M2:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M1:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M1:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M1:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M2:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M2:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15M2:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-15C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M1:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M1:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M1:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M2:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M2:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16M2:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-16C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17M1:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17M1:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17M2:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17M2:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-17C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M1:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M1:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M1:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M2:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M2:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18M2:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-18C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M1:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M1:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M1:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M2:PS-QDP1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M2:PS-QDP2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19M2:PS-QFP:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-19C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M1:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M1:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M1:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M2:PS-QDB1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M2:PS-QDB2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20M2:PS-QFB:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C1:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C1:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C2:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C2:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C3:PS-Q3:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C3:PS-Q4:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C4:PS-Q1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-20C4:PS-Q2:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01M1:PS-QDA:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01M1:PS-QFA:Current-SP', 0.0, 0.0],  # [A]
    ]


_pvs_si_ps_ids = [
    ['SI-14SB:PS-CH-1:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14SB:PS-CH-2:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-14SB:PS-CH-1:Current-SP', 0.0, 0.0],  # [A]
    ['SI-14SB:PS-CH-2:Current-SP', 0.0, 0.0],  # [A]
    ]


_pvs_si_septff = [
    ['SI-01M1:PS-FFCH:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01M1:PS-FFCV:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01M2:PS-FFCH:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01M2:PS-FFCV:OpMode-Sel', _SLOWREF, 0.0],
    ['SI-01M1:PS-FFCH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['SI-01M1:PS-FFCV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['SI-01M2:PS-FFCH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['SI-01M2:PS-FFCV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],  # [A]
    ['SI-01M1:PS-FFCH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01M1:PS-FFCV:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01M2:PS-FFCH:Current-SP', 0.0, 0.0],  # [A]
    ['SI-01M2:PS-FFCV:Current-SP', 0.0, 0.0],  # [A]
]


_template_dict = {
    'pvs':
    _pvs_as_ti +
    _pvs_li_egunmod + _pvs_li_llrf + _pvs_li_ps +
    _pvs_as_pu +
    _pvs_as_rf + _pvs_bo_llrf + _pvs_si_llrf_a + _pvs_si_llrf_b +
    _bpm_pvs +
    _pvs_tb_ps + _pvs_bo_ps + _pvs_ts_ps +
    _pvs_si_ps_fam +
    _pvs_si_ps_ch + _pvs_si_ps_cv +
    _pvs_si_ps_qs + _pvs_si_ps_qn +
    _pvs_si_ps_ids + _pvs_si_septff
    }
