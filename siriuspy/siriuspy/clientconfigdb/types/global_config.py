"""AS Global configuration."""
from copy import deepcopy as _dcopy

from siriuspy.csdevice.pwrsupply import DEFAULT_WFM_FBP as \
    _DEFAULT_WFM_FBP
from siriuspy.csdevice.pwrsupply import DEFAULT_WFM_OTHERS as \
    _DEFAULT_WFM_OTHERS


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
    ['LI-01:EG-BiasPS:voltoutsoft', -60.0, 0.0],   # Volt
    ['LI-01:EG-FilaPS:switch', 0, 0],
    ['LI-01:EG-HVPS:currentoutsoft', 0.003, 0.0],  # mA
    ['LI-01:EG-HVPS:enable', 0, 0.0],
    ['LI-01:EG-PulsePS:multiselect', 0, 0.0],
    ['LI-01:EG-PulsePS:multiswitch', 0, 0.0],
    ['LI-01:EG-PulsePS:singleselect', 0, 0.0],
    ['LI-01:EG-PulsePS:singleswitch', 0, 0.0],
    ['LI-01:EG-PulsePS:poweroutsoft', 0.0, 0.0],  # Volt
    ['LI-01:PU-Modltr-1:WRITE_I', 100.0, 0.0],        # mA
    ['LI-01:PU-Modltr-2:WRITE_I', 100.0, 0.0],     # mA
    ['LI-01:PU-Modltr-1:WRITE_V', 0.0, 0.0],          # kV
    ['LI-01:PU-Modltr-2:WRITE_V', 0.0, 0.0],       # kV
    ]

_pvs_li_llrf = [
    ['LA-RF:LLRF:BUN1:SET_STREAM', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH1_DELAY', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH2_DELAY', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH7_DELAY', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_CH8_DELAY', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_TRIGGER_DELAY', 0, 0.0],
    ['LA-RF:LLRF:BUN1:SET_AMP', 0.0, 0.0],  # %
    ['LA-RF:LLRF:BUN1:SET_PHASE', 0.0, 0.0],  # Degree
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
    ['LA-RF:LLRF:KLY1:SET_AMP', 0.0, 0.0],  # %
    ['LA-RF:LLRF:KLY1:SET_PHASE', 0.0, 0.0],  # Degree
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
    ['LA-RF:LLRF:KLY2:SET_AMP', 0.0, 0.0],  # %
    ['LA-RF:LLRF:KLY2:SET_PHASE', 0.0, 0.0],  # Degree
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

_pvs_timing = [
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
    ['AS-RaMO:TI-EVG:CplSIDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:CplSIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:CplSIMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:CycleDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:CycleDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:CycleMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:DigBODelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:DigBODelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:DigBOMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:DigLIDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:DigLIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:DigLIMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:DigSIDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:DigSIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:DigSIMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:DigTBDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:DigTBDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:DigTBMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:DigTSDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:DigTSDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:DigTSMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:InjBODelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:InjBODelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:InjBOMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:InjSIDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:InjSIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:InjSIMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:LinacDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:LinacDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:LinacMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:MigSIDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:MigSIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:MigSIMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:OrbBODelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:OrbBODelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:OrbBOMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:OrbSIDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:OrbSIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:OrbSIMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:RmpBODelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:RmpBODelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:RmpBOMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:StudyDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:StudyDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:StudyMode-Sel', 0, 0.0],

    ['AS-RaMO:TI-EVG:TunSIDelay-SP', 0, 0.0],
    ['AS-RaMO:TI-EVG:TunSIDelayType-Sel', 0, 0.0],
    ['AS-RaMO:TI-EVG:TunSIMode-Sel', 0, 0.0],

    # Triggers
    ['AS-Fam:TI-Scrn-TBBO:Delay-SP', 0, 0.0],  # us
    ['AS-Fam:TI-Scrn-TBBO:Duration-SP', 0, 0.0],  # us
    ['AS-Fam:TI-Scrn-TBBO:NrPulses-SP', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:Polarity-Sel', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:RFDelayType-Sel', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:Src-Sel', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:State-Sel', 0, 0.0],
    ['AS-Fam:TI-Scrn-TBBO:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['AS-Fam:TI-Scrn-TBBO:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-FCT:Delay-SP', 0, 0.0],  # us
    ['AS-Glob:TI-FCT:Duration-SP', 0, 0.0],  # us
    ['AS-Glob:TI-FCT:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-FCT:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-FCT:RFDelayType-Sel', 0, 0.0],
    ['AS-Glob:TI-FCT:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-FCT:State-Sel', 0, 0.0],
    ['AS-Glob:TI-FCT:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['AS-Glob:TI-FCT:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-FillPtrnMon:Delay-SP', 0, 0.0],  # us
    ['AS-Glob:TI-FillPtrnMon:Duration-SP', 0, 0.0],  # us
    ['AS-Glob:TI-FillPtrnMon:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:RFDelayType-Sel', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:State-Sel', 0, 0.0],
    ['AS-Glob:TI-FillPtrnMon:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['AS-Glob:TI-FillPtrnMon:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-Osc-EjeBO:Delay-SP', 0, 0.0],  # us
    ['AS-Glob:TI-Osc-EjeBO:Duration-SP', 0, 0.0],  # us
    ['AS-Glob:TI-Osc-EjeBO:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:RFDelayType-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:State-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-EjeBO:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['AS-Glob:TI-Osc-EjeBO:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-Osc-InjBO:Delay-SP', 0, 0.0],  # us
    ['AS-Glob:TI-Osc-InjBO:Duration-SP', 0, 0.0],  # us
    ['AS-Glob:TI-Osc-InjBO:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-InjBO:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjBO:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjBO:State-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjBO:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['AS-Glob:TI-Osc-InjBO:LowLvlLock-Sel', 0, 0.0],

    ['AS-Glob:TI-Osc-InjSI:Delay-SP', 0, 0.0],  # us
    ['AS-Glob:TI-Osc-InjSI:Duration-SP', 0, 0.0],  # us
    ['AS-Glob:TI-Osc-InjSI:NrPulses-SP', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI:Polarity-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI:Src-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI:State-Sel', 0, 0.0],
    ['AS-Glob:TI-Osc-InjSI:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['AS-Glob:TI-Osc-InjSI:LowLvlLock-Sel', 0, 0.0],

    ['BO-01D:TI-InjKckr:Delay-SP', 0, 0.0],  # us
    ['BO-01D:TI-InjKckr:Duration-SP', 0, 0.0],  # us
    ['BO-01D:TI-InjKckr:NrPulses-SP', 0, 0.0],
    ['BO-01D:TI-InjKckr:Polarity-Sel', 0, 0.0],
    ['BO-01D:TI-InjKckr:Src-Sel', 0, 0.0],
    ['BO-01D:TI-InjKckr:State-Sel', 0, 0.0],
    ['BO-01D:TI-InjKckr:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['BO-01D:TI-InjKckr:LowLvlLock-Sel', 0, 0.0],

    ['BO-35D:TI-DCCT:Delay-SP', 0, 0.0],  # us
    ['BO-35D:TI-DCCT:Duration-SP', 0, 0.0],  # us
    ['BO-35D:TI-DCCT:NrPulses-SP', 0, 0.0],
    ['BO-35D:TI-DCCT:Polarity-Sel', 0, 0.0],
    ['BO-35D:TI-DCCT:RFDelayType-Sel', 0, 0.0],
    ['BO-35D:TI-DCCT:Src-Sel', 0, 0.0],
    ['BO-35D:TI-DCCT:State-Sel', 0, 0.0],
    ['BO-35D:TI-DCCT:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['BO-35D:TI-DCCT:LowLvlLock-Sel', 0, 0.0],

    ['BO-48D:TI-EjeKckr:Delay-SP', 0, 0.0],  # us
    ['BO-48D:TI-EjeKckr:Duration-SP', 0, 0.0],  # us
    ['BO-48D:TI-EjeKckr:NrPulses-SP', 0, 0.0],
    ['BO-48D:TI-EjeKckr:Polarity-Sel', 0, 0.0],
    ['BO-48D:TI-EjeKckr:RFDelayType-Sel', 0, 0.0],
    ['BO-48D:TI-EjeKckr:Src-Sel', 0, 0.0],
    ['BO-48D:TI-EjeKckr:State-Sel', 0, 0.0],
    ['BO-48D:TI-EjeKckr:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['BO-48D:TI-EjeKckr:LowLvlLock-Sel', 0, 0.0],

    ['BO-50U:TI-VLightCam:Delay-SP', 0, 0.0],  # us
    ['BO-50U:TI-VLightCam:Duration-SP', 0, 0.0],  # us
    ['BO-50U:TI-VLightCam:NrPulses-SP', 0, 0.0],
    ['BO-50U:TI-VLightCam:Polarity-Sel', 0, 0.0],
    ['BO-50U:TI-VLightCam:RFDelayType-Sel', 0, 0.0],
    ['BO-50U:TI-VLightCam:Src-Sel', 0, 0.0],
    ['BO-50U:TI-VLightCam:State-Sel', 0, 0.0],
    ['BO-50U:TI-VLightCam:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['BO-50U:TI-VLightCam:LowLvlLock-Sel', 0, 0.0],

    ['BO-Fam:TI-BPM:Delay-SP', 0, 0.0],  # us
    ['BO-Fam:TI-BPM:Duration-SP', 0, 0.0],  # us
    ['BO-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
    ['BO-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
    ['BO-Fam:TI-BPM:Src-Sel', 0, 0.0],
    ['BO-Fam:TI-BPM:State-Sel', 0, 0.0],
    ['BO-Fam:TI-BPM:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['BO-Fam:TI-BPM:LowLvlLock-Sel', 0, 0.0],

    ['BO-Glob:TI-LLRF-PsMtn:Delay-SP', 0, 0.0],  # us
    ['BO-Glob:TI-LLRF-PsMtn:Duration-SP', 0, 0.0],  # us
    ['BO-Glob:TI-LLRF-PsMtn:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-LLRF-PsMtn:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-PsMtn:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-PsMtn:State-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-PsMtn:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['BO-Glob:TI-LLRF-PsMtn:LowLvlLock-Sel', 0, 0.0],

    ['BO-Glob:TI-LLRF-Rmp:Delay-SP', 0, 0.0],  # us
    ['BO-Glob:TI-LLRF-Rmp:Duration-SP', 0, 0.0],  # us
    ['BO-Glob:TI-LLRF-Rmp:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:State-Sel', 0, 0.0],
    ['BO-Glob:TI-LLRF-Rmp:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['BO-Glob:TI-LLRF-Rmp:LowLvlLock-Sel', 0, 0.0],

    ['BO-Glob:TI-Mags-Corrs:Delay-SP', 0, 0.0],  # us
    ['BO-Glob:TI-Mags-Corrs:Duration-SP', 0, 0.0],  # us
    ['BO-Glob:TI-Mags-Corrs:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-Mags-Corrs:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Corrs:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Corrs:State-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Corrs:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['BO-Glob:TI-Mags-Corrs:LowLvlLock-Sel', 0, 0.0],

    ['BO-Glob:TI-Mags-Fams:Delay-SP', 0, 0.0],  # us
    ['BO-Glob:TI-Mags-Fams:Duration-SP', 0, 0.0],  # us
    ['BO-Glob:TI-Mags-Fams:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-Mags-Fams:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Fams:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Fams:State-Sel', 0, 0.0],
    ['BO-Glob:TI-Mags-Fams:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['BO-Glob:TI-Mags-Fams:LowLvlLock-Sel', 0, 0.0],

    ['BO-Glob:TI-TuneProc:Delay-SP', 0, 0.0],  # us
    ['BO-Glob:TI-TuneProc:Duration-SP', 0, 0.0],  # us
    ['BO-Glob:TI-TuneProc:NrPulses-SP', 0, 0.0],
    ['BO-Glob:TI-TuneProc:Polarity-Sel', 0, 0.0],
    ['BO-Glob:TI-TuneProc:RFDelayType-Sel', 0, 0.0],
    ['BO-Glob:TI-TuneProc:Src-Sel', 0, 0.0],
    ['BO-Glob:TI-TuneProc:State-Sel', 0, 0.0],
    ['BO-Glob:TI-TuneProc:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['BO-Glob:TI-TuneProc:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-Osc-Modltr:Delay-SP', 0, 0.0],  # us
    ['LI-01:TI-Osc-Modltr:Duration-SP', 0, 0.0],  # us
    ['LI-01:TI-Osc-Modltr:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-Osc-Modltr:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-Osc-Modltr:Src-Sel', 0, 0.0],
    ['LI-01:TI-Osc-Modltr:State-Sel', 0, 0.0],
    ['LI-01:TI-Osc-Modltr:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-01:TI-Osc-Modltr:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-EGun-MultBun:Delay-SP', 0, 0.0],  # us
    ['LI-01:TI-EGun-MultBun:Duration-SP', 0, 0.0],  # us
    ['LI-01:TI-EGun-MultBun:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:RFDelayType-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:Src-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:State-Sel', 0, 0.0],
    ['LI-01:TI-EGun-MultBun:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-01:TI-EGun-MultBun:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-EGun-SglBun:Delay-SP', 0, 0.0],  # us
    ['LI-01:TI-EGun-SglBun:Duration-SP', 0, 0.0],  # us
    ['LI-01:TI-EGun-SglBun:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:RFDelayType-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:Src-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:State-Sel', 0, 0.0],
    ['LI-01:TI-EGun-SglBun:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-01:TI-EGun-SglBun:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-Modltr-1:Delay-SP', 0, 0.0],  # us
    ['LI-01:TI-Modltr-1:Duration-SP', 0, 0.0],  # us
    ['LI-01:TI-Modltr-1:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-Modltr-1:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-1:Src-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-1:State-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-1:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-01:TI-Modltr-1:LowLvlLock-Sel', 0, 0.0],

    ['LI-01:TI-Modltr-2:Delay-SP', 0, 0.0],  # us
    ['LI-01:TI-Modltr-2:Duration-SP', 0, 0.0],  # us
    ['LI-01:TI-Modltr-2:NrPulses-SP', 0, 0.0],
    ['LI-01:TI-Modltr-2:Polarity-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-2:Src-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-2:State-Sel', 0, 0.0],
    ['LI-01:TI-Modltr-2:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-01:TI-Modltr-2:LowLvlLock-Sel', 0, 0.0],

    ['LI-Fam:TI-BPM:Delay-SP', 0, 0.0],  # us
    ['LI-Fam:TI-BPM:Duration-SP', 0, 0.0],  # us
    ['LI-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
    ['LI-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
    ['LI-Fam:TI-BPM:RFDelayType-Sel', 0, 0.0],
    ['LI-Fam:TI-BPM:Src-Sel', 0, 0.0],
    ['LI-Fam:TI-BPM:State-Sel', 0, 0.0],
    ['LI-Fam:TI-BPM:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-Fam:TI-BPM:LowLvlLock-Sel', 0, 0.0],

    ['LI-Fam:TI-ICT:Delay-SP', 0, 0.0],  # us
    ['LI-Fam:TI-ICT:Duration-SP', 0, 0.0],  # us
    ['LI-Fam:TI-ICT:NrPulses-SP', 0, 0.0],
    ['LI-Fam:TI-ICT:Polarity-Sel', 0, 0.0],
    ['LI-Fam:TI-ICT:RFDelayType-Sel', 0, 0.0],
    ['LI-Fam:TI-ICT:Src-Sel', 0, 0.0],
    ['LI-Fam:TI-ICT:State-Sel', 0, 0.0],
    ['LI-Fam:TI-ICT:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-Fam:TI-ICT:LowLvlLock-Sel', 0, 0.0],

    ['LI-Fam:TI-Scrn:Delay-SP', 0, 0.0],  # us
    ['LI-Fam:TI-Scrn:Duration-SP', 0, 0.0],  # us
    ['LI-Fam:TI-Scrn:NrPulses-SP', 0, 0.0],
    ['LI-Fam:TI-Scrn:Polarity-Sel', 0, 0.0],
    ['LI-Fam:TI-Scrn:RFDelayType-Sel', 0, 0.0],
    ['LI-Fam:TI-Scrn:Src-Sel', 0, 0.0],
    ['LI-Fam:TI-Scrn:State-Sel', 0, 0.0],
    ['LI-Fam:TI-Scrn:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-Fam:TI-Scrn:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-LLRF-Kly1:Delay-SP', 0, 0.0],  # us
    ['LI-Glob:TI-LLRF-Kly1:Duration-SP', 0, 0.0],  # us
    ['LI-Glob:TI-LLRF-Kly1:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly1:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly1:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly1:State-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly1:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-Glob:TI-LLRF-Kly1:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-LLRF-Kly2:Delay-SP', 0, 0.0],  # us
    ['LI-Glob:TI-LLRF-Kly2:Duration-SP', 0, 0.0],  # us
    ['LI-Glob:TI-LLRF-Kly2:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly2:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly2:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly2:State-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-Kly2:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-Glob:TI-LLRF-Kly2:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-LLRF-SHB:Delay-SP', 0, 0.0],  # us
    ['LI-Glob:TI-LLRF-SHB:Duration-SP', 0, 0.0],  # us
    ['LI-Glob:TI-LLRF-SHB:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-LLRF-SHB:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-SHB:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-SHB:State-Sel', 0, 0.0],
    ['LI-Glob:TI-LLRF-SHB:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-Glob:TI-LLRF-SHB:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-SSAmp-Kly1:Delay-SP', 0, 0.0],  # us
    ['LI-Glob:TI-SSAmp-Kly1:Duration-SP', 0, 0.0],  # us
    ['LI-Glob:TI-SSAmp-Kly1:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly1:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly1:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly1:State-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly1:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-Glob:TI-SSAmp-Kly1:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-SSAmp-Kly2:Delay-SP', 0, 0.0],  # us
    ['LI-Glob:TI-SSAmp-Kly2:Duration-SP', 0, 0.0],  # us
    ['LI-Glob:TI-SSAmp-Kly2:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly2:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly2:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly2:State-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-Kly2:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-Glob:TI-SSAmp-Kly2:LowLvlLock-Sel', 0, 0.0],

    ['LI-Glob:TI-SSAmp-SHB:Delay-SP', 0, 0.0],  # us
    ['LI-Glob:TI-SSAmp-SHB:Duration-SP', 0, 0.0],  # us
    ['LI-Glob:TI-SSAmp-SHB:NrPulses-SP', 0, 0.0],
    ['LI-Glob:TI-SSAmp-SHB:Polarity-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-SHB:Src-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-SHB:State-Sel', 0, 0.0],
    ['LI-Glob:TI-SSAmp-SHB:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['LI-Glob:TI-SSAmp-SHB:LowLvlLock-Sel', 0, 0.0],

    ['SI-01SA:TI-InjDpKckr:Delay-SP', 0, 0.0],  # us
    ['SI-01SA:TI-InjDpKckr:Duration-SP', 0, 0.0],  # us
    ['SI-01SA:TI-InjDpKckr:NrPulses-SP', 0, 0.0],
    ['SI-01SA:TI-InjDpKckr:Polarity-Sel', 0, 0.0],
    ['SI-01SA:TI-InjDpKckr:Src-Sel', 0, 0.0],
    ['SI-01SA:TI-InjDpKckr:State-Sel', 0, 0.0],
    ['SI-01SA:TI-InjDpKckr:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-01SA:TI-InjDpKckr:LowLvlLock-Sel', 0, 0.0],

    ['SI-01SA:TI-InjNLKckr:Delay-SP', 0, 0.0],  # us
    ['SI-01SA:TI-InjNLKckr:Duration-SP', 0, 0.0],  # us
    ['SI-01SA:TI-InjNLKckr:NrPulses-SP', 0, 0.0],
    ['SI-01SA:TI-InjNLKckr:Polarity-Sel', 0, 0.0],
    ['SI-01SA:TI-InjNLKckr:Src-Sel', 0, 0.0],
    ['SI-01SA:TI-InjNLKckr:State-Sel', 0, 0.0],
    ['SI-01SA:TI-InjNLKckr:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-01SA:TI-InjNLKckr:LowLvlLock-Sel', 0, 0.0],

    ['SI-01SA:TI-PingH:Delay-SP', 0, 0.0],  # us
    ['SI-01SA:TI-PingH:Duration-SP', 0, 0.0],  # us
    ['SI-01SA:TI-PingH:NrPulses-SP', 0, 0.0],
    ['SI-01SA:TI-PingH:Polarity-Sel', 0, 0.0],
    ['SI-01SA:TI-PingH:Src-Sel', 0, 0.0],
    ['SI-01SA:TI-PingH:State-Sel', 0, 0.0],
    ['SI-01SA:TI-PingH:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-01SA:TI-PingH:LowLvlLock-Sel', 0, 0.0],

    ['SI-13C4:TI-DCCT:Delay-SP', 0, 0.0],  # us
    ['SI-13C4:TI-DCCT:Duration-SP', 0, 0.0],  # us
    ['SI-13C4:TI-DCCT:NrPulses-SP', 0, 0.0],
    ['SI-13C4:TI-DCCT:Polarity-Sel', 0, 0.0],
    ['SI-13C4:TI-DCCT:RFDelayType-Sel', 0, 0.0],
    ['SI-13C4:TI-DCCT:Src-Sel', 0, 0.0],
    ['SI-13C4:TI-DCCT:State-Sel', 0, 0.0],
    ['SI-13C4:TI-DCCT:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-13C4:TI-DCCT:LowLvlLock-Sel', 0, 0.0],

    ['SI-14C4:TI-DCCT:Delay-SP', 0, 0.0],  # us
    ['SI-14C4:TI-DCCT:Duration-SP', 0, 0.0],  # us
    ['SI-14C4:TI-DCCT:NrPulses-SP', 0, 0.0],
    ['SI-14C4:TI-DCCT:Polarity-Sel', 0, 0.0],
    ['SI-14C4:TI-DCCT:RFDelayType-Sel', 0, 0.0],
    ['SI-14C4:TI-DCCT:Src-Sel', 0, 0.0],
    ['SI-14C4:TI-DCCT:State-Sel', 0, 0.0],
    ['SI-14C4:TI-DCCT:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-14C4:TI-DCCT:LowLvlLock-Sel', 0, 0.0],

    ['SI-19C4:TI-PingV:Delay-SP', 0, 0.0],  # us
    ['SI-19C4:TI-PingV:Duration-SP', 0, 0.0],  # us
    ['SI-19C4:TI-PingV:NrPulses-SP', 0, 0.0],
    ['SI-19C4:TI-PingV:Polarity-Sel', 0, 0.0],
    ['SI-19C4:TI-PingV:RFDelayType-Sel', 0, 0.0],
    ['SI-19C4:TI-PingV:Src-Sel', 0, 0.0],
    ['SI-19C4:TI-PingV:State-Sel', 0, 0.0],
    ['SI-19C4:TI-PingV:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-19C4:TI-PingV:LowLvlLock-Sel', 0, 0.0],

    ['SI-Fam:TI-BPM:Delay-SP', 0, 0.0],  # us
    ['SI-Fam:TI-BPM:Duration-SP', 0, 0.0],  # us
    ['SI-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
    ['SI-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM:Src-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM:State-Sel', 0, 0.0],
    ['SI-Fam:TI-BPM:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Fam:TI-BPM:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcH-Fid:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcH-Fid:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcH-Fid:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:RFDelayType-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-BbBProcH-Fid:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcH-Trig1:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcH-Trig1:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcH-Trig1:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig1:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig1:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig1:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig1:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-BbBProcH-Trig1:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcH-Trig2:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcH-Trig2:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcH-Trig2:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig2:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig2:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig2:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcH-Trig2:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-BbBProcH-Trig2:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcL-Fid:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcL-Fid:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcL-Fid:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:RFDelayType-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-BbBProcL-Fid:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcL-Trig1:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcL-Trig1:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcL-Trig1:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig1:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig1:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig1:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig1:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-BbBProcL-Trig1:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcL-Trig2:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcL-Trig2:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcL-Trig2:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig2:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig2:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig2:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcL-Trig2:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-BbBProcL-Trig2:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcV-Fid:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcV-Fid:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcV-Fid:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:RFDelayType-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-BbBProcV-Fid:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcV-Trig1:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcV-Trig1:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcV-Trig1:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig1:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig1:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig1:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig1:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-BbBProcV-Trig1:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-BbBProcV-Trig2:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcV-Trig2:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-BbBProcV-Trig2:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig2:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig2:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig2:State-Sel', 0, 0.0],
    ['SI-Glob:TI-BbBProcV-Trig2:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-BbBProcV-Trig2:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-LLRF-PsMtn:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-LLRF-PsMtn:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-LLRF-PsMtn:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-LLRF-PsMtn:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-PsMtn:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-PsMtn:State-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-PsMtn:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-LLRF-PsMtn:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-LLRF-Rmp:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-LLRF-Rmp:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-LLRF-Rmp:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-LLRF-Rmp:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-Rmp:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-Rmp:State-Sel', 0, 0.0],
    ['SI-Glob:TI-LLRF-Rmp:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-LLRF-Rmp:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-Bends:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-Mags-Bends:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-Mags-Bends:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Bends:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Bends:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Bends:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Bends:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-Mags-Bends:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-Corrs:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-Mags-Corrs:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-Mags-Corrs:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Corrs:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Corrs:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Corrs:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Corrs:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-Mags-Corrs:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-Quads:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-Mags-Quads:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-Mags-Quads:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Quads:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Quads:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Quads:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Quads:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-Mags-Quads:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-Sexts:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-Mags-Sexts:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-Mags-Sexts:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Sexts:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Sexts:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Sexts:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Sexts:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-Mags-Sexts:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-Mags-Skews:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-Mags-Skews:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-Mags-Skews:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-Mags-Skews:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Skews:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Skews:State-Sel', 0, 0.0],
    ['SI-Glob:TI-Mags-Skews:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-Mags-Skews:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-StrkCam-Trig1:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-StrkCam-Trig1:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-StrkCam-Trig1:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-StrkCam-Trig1:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-StrkCam-Trig1:RFDelayType-Sel', 0, 0.0],
    ['SI-Glob:TI-StrkCam-Trig1:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-StrkCam-Trig1:State-Sel', 0, 0.0],
    ['SI-Glob:TI-StrkCam-Trig1:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-StrkCam-Trig1:LowLvlLock-Sel', 0, 0.0],

    ['SI-Glob:TI-StrkCam-Trig2:Delay-SP', 0, 0.0],  # us
    ['SI-Glob:TI-StrkCam-Trig2:Duration-SP', 0, 0.0],  # us
    ['SI-Glob:TI-StrkCam-Trig2:NrPulses-SP', 0, 0.0],
    ['SI-Glob:TI-StrkCam-Trig2:Polarity-Sel', 0, 0.0],
    ['SI-Glob:TI-StrkCam-Trig2:RFDelayType-Sel', 0, 0.0],
    ['SI-Glob:TI-StrkCam-Trig2:Src-Sel', 0, 0.0],
    ['SI-Glob:TI-StrkCam-Trig2:State-Sel', 0, 0.0],
    ['SI-Glob:TI-StrkCam-Trig2:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['SI-Glob:TI-StrkCam-Trig2:LowLvlLock-Sel', 0, 0.0],

    ['TB-04:TI-InjSept:Delay-SP', 0, 0.0],  # us
    ['TB-04:TI-InjSept:Duration-SP', 0, 0.0],  # us
    ['TB-04:TI-InjSept:NrPulses-SP', 0, 0.0],
    ['TB-04:TI-InjSept:Polarity-Sel', 0, 0.0],
    ['TB-04:TI-InjSept:Src-Sel', 0, 0.0],
    ['TB-04:TI-InjSept:State-Sel', 0, 0.0],
    ['TB-04:TI-InjSept:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TB-04:TI-InjSept:LowLvlLock-Sel', 0, 0.0],

    ['TB-Fam:TI-BPM:Delay-SP', 0, 0.0],  # us
    ['TB-Fam:TI-BPM:Duration-SP', 0, 0.0],  # us
    ['TB-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
    ['TB-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
    ['TB-Fam:TI-BPM:Src-Sel', 0, 0.0],
    ['TB-Fam:TI-BPM:State-Sel', 0, 0.0],
    ['TB-Fam:TI-BPM:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TB-Fam:TI-BPM:LowLvlLock-Sel', 0, 0.0],

    ['TB-Fam:TI-ICT-Digit:Delay-SP', 0, 0.0],  # us
    ['TB-Fam:TI-ICT-Digit:Duration-SP', 0, 0.0],  # us
    ['TB-Fam:TI-ICT-Digit:NrPulses-SP', 0, 0.0],
    ['TB-Fam:TI-ICT-Digit:Polarity-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Digit:Src-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Digit:State-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Digit:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TB-Fam:TI-ICT-Digit:LowLvlLock-Sel', 0, 0.0],

    ['TB-Fam:TI-ICT-Integ:Delay-SP', 0, 0.0],  # us
    ['TB-Fam:TI-ICT-Integ:Duration-SP', 0, 0.0],  # us
    ['TB-Fam:TI-ICT-Integ:NrPulses-SP', 0, 0.0],
    ['TB-Fam:TI-ICT-Integ:Polarity-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Integ:Src-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Integ:State-Sel', 0, 0.0],
    ['TB-Fam:TI-ICT-Integ:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TB-Fam:TI-ICT-Integ:LowLvlLock-Sel', 0, 0.0],

    ['TB-Glob:TI-Mags:Delay-SP', 0, 0.0],  # us
    ['TB-Glob:TI-Mags:Duration-SP', 0, 0.0],  # us
    ['TB-Glob:TI-Mags:NrPulses-SP', 0, 0.0],
    ['TB-Glob:TI-Mags:Polarity-Sel', 0, 0.0],
    ['TB-Glob:TI-Mags:Src-Sel', 0, 0.0],
    ['TB-Glob:TI-Mags:State-Sel', 0, 0.0],
    ['TB-Glob:TI-Mags:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TB-Glob:TI-Mags:LowLvlLock-Sel', 0, 0.0],

    ['TS-01:TI-EjeSeptF:Delay-SP', 0, 0.0],  # us
    ['TS-01:TI-EjeSeptF:Duration-SP', 0, 0.0],  # us
    ['TS-01:TI-EjeSeptF:NrPulses-SP', 0, 0.0],
    ['TS-01:TI-EjeSeptF:Polarity-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptF:RFDelayType-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptF:Src-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptF:State-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptF:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TS-01:TI-EjeSeptF:LowLvlLock-Sel', 0, 0.0],

    ['TS-01:TI-EjeSeptG:Delay-SP', 0, 0.0],  # us
    ['TS-01:TI-EjeSeptG:Duration-SP', 0, 0.0],  # us
    ['TS-01:TI-EjeSeptG:NrPulses-SP', 0, 0.0],
    ['TS-01:TI-EjeSeptG:Polarity-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptG:RFDelayType-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptG:Src-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptG:State-Sel', 0, 0.0],
    ['TS-01:TI-EjeSeptG:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TS-01:TI-EjeSeptG:LowLvlLock-Sel', 0, 0.0],

    ['TS-04:TI-InjSeptF:Delay-SP', 0, 0.0],  # us
    ['TS-04:TI-InjSeptF:Duration-SP', 0, 0.0],  # us
    ['TS-04:TI-InjSeptF:NrPulses-SP', 0, 0.0],
    ['TS-04:TI-InjSeptF:Polarity-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptF:Src-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptF:State-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptF:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TS-04:TI-InjSeptF:LowLvlLock-Sel', 0, 0.0],

    ['TS-04:TI-InjSeptG-1:Delay-SP', 0, 0.0],  # us
    ['TS-04:TI-InjSeptG-1:Duration-SP', 0, 0.0],  # us
    ['TS-04:TI-InjSeptG-1:NrPulses-SP', 0, 0.0],
    ['TS-04:TI-InjSeptG-1:Polarity-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-1:Src-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-1:State-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-1:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TS-04:TI-InjSeptG-1:LowLvlLock-Sel', 0, 0.0],

    ['TS-04:TI-InjSeptG-2:Delay-SP', 0, 0.0],  # us
    ['TS-04:TI-InjSeptG-2:Duration-SP', 0, 0.0],  # us
    ['TS-04:TI-InjSeptG-2:NrPulses-SP', 0, 0.0],
    ['TS-04:TI-InjSeptG-2:Polarity-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-2:Src-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-2:State-Sel', 0, 0.0],
    ['TS-04:TI-InjSeptG-2:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TS-04:TI-InjSeptG-2:LowLvlLock-Sel', 0, 0.0],

    ['TS-Fam:TI-BPM:Delay-SP', 0, 0.0],  # us
    ['TS-Fam:TI-BPM:Duration-SP', 0, 0.0],  # us
    ['TS-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
    ['TS-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
    ['TS-Fam:TI-BPM:Src-Sel', 0, 0.0],
    ['TS-Fam:TI-BPM:State-Sel', 0, 0.0],
    ['TS-Fam:TI-BPM:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TS-Fam:TI-BPM:LowLvlLock-Sel', 0, 0.0],

    ['TS-Fam:TI-ICT-Digit:Delay-SP', 0, 0.0],  # us
    ['TS-Fam:TI-ICT-Digit:Duration-SP', 0, 0.0],  # us
    ['TS-Fam:TI-ICT-Digit:NrPulses-SP', 0, 0.0],
    ['TS-Fam:TI-ICT-Digit:Polarity-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Digit:Src-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Digit:State-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Digit:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TS-Fam:TI-ICT-Digit:LowLvlLock-Sel', 0, 0.0],

    ['TS-Fam:TI-ICT-Integ:Delay-SP', 0, 0.0],  # us
    ['TS-Fam:TI-ICT-Integ:Duration-SP', 0, 0.0],  # us
    ['TS-Fam:TI-ICT-Integ:NrPulses-SP', 0, 0.0],
    ['TS-Fam:TI-ICT-Integ:Polarity-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Integ:Src-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Integ:State-Sel', 0, 0.0],
    ['TS-Fam:TI-ICT-Integ:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TS-Fam:TI-ICT-Integ:LowLvlLock-Sel', 0, 0.0],

    ['TS-Fam:TI-Scrn:Delay-SP', 0, 0.0],  # us
    ['TS-Fam:TI-Scrn:Duration-SP', 0, 0.0],  # us
    ['TS-Fam:TI-Scrn:NrPulses-SP', 0, 0.0],
    ['TS-Fam:TI-Scrn:Polarity-Sel', 0, 0.0],
    ['TS-Fam:TI-Scrn:RFDelayType-Sel', 0, 0.0],
    ['TS-Fam:TI-Scrn:Src-Sel', 0, 0.0],
    ['TS-Fam:TI-Scrn:State-Sel', 0, 0.0],
    ['TS-Fam:TI-Scrn:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TS-Fam:TI-Scrn:LowLvlLock-Sel', 0, 0.0],

    ['TS-Glob:TI-Mags:Delay-SP', 0, 0.0],  # us
    ['TS-Glob:TI-Mags:Duration-SP', 0, 0.0],  # us
    ['TS-Glob:TI-Mags:NrPulses-SP', 0, 0.0],
    ['TS-Glob:TI-Mags:Polarity-Sel', 0, 0.0],
    ['TS-Glob:TI-Mags:Src-Sel', 0, 0.0],
    ['TS-Glob:TI-Mags:State-Sel', 0, 0.0],
    ['TS-Glob:TI-Mags:DeltaDelay-SP', 30*[0.0, ], 0.0],
    ['TS-Glob:TI-Mags:LowLvlLock-Sel', 0, 0.0],

    ]

_pvs_li_ps = [
    ['LI-01:PS-LensRev:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Lens-1:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Lens-2:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Lens-3:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Lens-4:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-1:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-2:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-3:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-4:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-5:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-6:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-7:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-8:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-9:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-10:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-11:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-12:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Slnd-13:seti', 0.0, 0.0],  # unit: A
    ['LI-Fam:PS-Slnd-14:seti', 0.0, 0.0],  # unit: A
    ['LI-Fam:PS-Slnd-15:seti', 0.0, 0.0],  # unit: A
    ['LI-Fam:PS-Slnd-16:seti', 0.0, 0.0],  # unit: A
    ['LI-Fam:PS-Slnd-17:seti', 0.0, 0.0],  # unit: A
    ['LI-Fam:PS-Slnd-18:seti', 0.0, 0.0],  # unit: A
    ['LI-Fam:PS-Slnd-19:seti', 0.0, 0.0],  # unit: A
    ['LI-Fam:PS-Slnd-20:seti', 0.0, 0.0],  # unit: A
    ['LI-Fam:PS-Slnd-21:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CV-1:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CH-1:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CV-2:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CH-2:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CV-3:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CH-3:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CV-4:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CH-4:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CV-5:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CH-5:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CV-6:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CH-6:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CV-7:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-CH-7:seti', 0.0, 0.0],  # unit: A
    ['LI-Fam:PS-QF1:seti', 0.0, 0.0],  # unit: A
    ['LI-Fam:PS-QF2:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-QF3:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-QD1:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-QD2:seti', 0.0, 0.0],  # unit: A
    ['LI-01:PS-Spect:seti', 0.0, 0.0],  # unit: A
    ]

_pvs_pu = [
    ['TB-04:PU-InjSept:PwrState-Sel', _OFF, 0.0],
    ['BO-01D:PU-InjKckr:PwrState-Sel', _OFF, 0.0],
    ['BO-48D:PU-EjeKckr:PwrState-Sel', _OFF, 0.0],
    ['TS-04:PU-InjSeptG-1:PwrState-Sel', _OFF, 0.0],
    ['TS-04:PU-InjSeptG-2:PwrState-Sel', _OFF, 0.0],
    ['TS-04:PU-InjSeptF:PwrState-Sel', _OFF, 0.0],
    ['TS-01:PU-EjeSeptG:PwrState-Sel', _OFF, 0.0],
    ['TS-01:PU-EjeSeptF:PwrState-Sel', _OFF, 0.0],
    ['TB-04:PU-InjSept:Pulse-Sel', 0, 0.0],
    ['BO-01D:PU-InjKckr:Pulse-Sel', 0, 0.0],
    ['BO-48D:PU-EjeKckr:Pulse-Sel', 0, 0.0],
    ['TS-04:PU-InjSeptG-1:Pulse-Sel', 0, 0.0],
    ['TS-04:PU-InjSeptG-2:Pulse-Sel', 0, 0.0],
    ['TS-04:PU-InjSeptF:Pulse-Sel', 0, 0.0],
    ['TS-01:PU-EjeSeptG:Pulse-Sel', 0, 0.0],
    ['TS-01:PU-EjeSeptF:Pulse-Sel', 0, 0.0],
    ['TB-04:PU-InjSept:Voltage-SP', 0.0, 0.0],   # [Volt]
    ['BO-01D:PU-InjKckr:Voltage-SP', 0.0, 0.0],  # [Volt]
    ['BO-48D:PU-EjeKckr:Voltage-SP', 0.0, 0.0],  # [Volt]
    ['TS-04:PU-InjSeptG-1:Voltage-SP', 0.0, 0.0],  # [Volt]
    ['TS-04:PU-InjSeptG-2:Voltage-SP', 0.0, 0.0],  # [Volt]
    ['TS-04:PU-InjSeptF:Voltage-SP', 0.0, 0.0],  # [Volt]
    ['TS-01:PU-EjeSeptG:Voltage-SP', 0.0, 0.0],  # [Volt]
    ['TS-01:PU-EjeSeptF:Voltage-SP', 0.0, 0.0],  # [Volt]
    ]

_rf_pvs = [
    ['BR-RF-DLLRF-01:LIMIT:REVSSA1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:REVSSA2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:REVSSA3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:REVSSA4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:REVCAV:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:VCAV:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:FWCAV:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:FWSSA1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:RFIN7:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:RFIN8:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:RFIN9:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:RFIN10:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:RFIN11:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:RFIN12:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:RFIN13:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:RFIN14:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:LIMIT:RFIN15:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:SWITCHES:S', 0, 0.0],
    ['BR-RF-DLLRF-01:TRIPINVERT:S', 0, 0.0],
    ['BR-RF-DLLRF-01:VACINVERT:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:REVSSA1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:REVSSA2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:REVSSA3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:REVSSA4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:REVCAV:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:MAN:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:PLC:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:LLRF1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:LLRF2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:LLRF3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:PLG1:UP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:PLG1:DN:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:PLG2:UP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:PLG2:DN:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:VCAV:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:FWCAV:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:FWSSA1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:RFIN7:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:RFIN8:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:RFIN9:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:RFIN10:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:RFIN11:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:RFIN12:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:RFIN13:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:RFIN14:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:RFIN15:S', 0, 0.0],
    ['BR-RF-DLLRF-01:ILK:BEAM:TRIP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:mV:AMPREF:MIN:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:PHSREF:MIN:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLGAIN:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:SL:PILIMIT:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:SL:KI:S', 0, 0.0],
    ['BR-RF-DLLRF-01:SL:KP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FL:PILIMIT:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FL:KI:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FL:KP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:AL:KI:S', 0, 0.0],
    ['BR-RF-DLLRF-01:AL:KP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:PL:KI:S', 0, 0.0],
    ['BR-RF-DLLRF-01:PL:KP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:MODE:S', 0, 0.0],
    ['BR-RF-DLLRF-01:PHSCORR:S', 0, 0.0],
    ['BR-RF-DLLRF-01:QUAD:SEL:S', 0, 0.0],
    ['BR-RF-DLLRF-01:LOOKREF:S', 0, 0.0],
    ['BR-RF-DLLRF-01:AMPREF:INCRATE:S', 0, 0.0],
    ['BR-RF-DLLRF-01:PHSREF:INCRATE:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWMIN:AMPPHS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:PHSH:CAV:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:PHSH:FWDCAV:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:GAIN:FWDCAV:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:PHSH:FWDSSA1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:GAIN:FWDSSA1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:PHSH:ADC:S', 0, 0.0],
    ['BR-RF-DLLRF-01:RmpTs1-SP', 0.0, 0.0],
    ['BR-RF-DLLRF-01:RmpTs2-SP', 0.0, 0.0],
    ['BR-RF-DLLRF-01:RmpTs3-SP', 0.0, 0.0],
    ['BR-RF-DLLRF-01:RmpTs4-SP', 0.0, 0.0],
    ['BR-RF-DLLRF-01:RmpIncTs-SP', 0.0, 0.0],
    ['BR-RF-DLLRF-01:RmpPhsTop-SP', 0.0, 0.0],
    ['BR-RF-DLLRF-01:RmpPhsBot-SP', 0.0, 0.0],
    ['BR-RF-DLLRF-01:RAMP:AMP:TOP:W-SP', 0.0, 0.0],
    ['BR-RF-DLLRF-01:RAMP:AMP:BOT:W-SP', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:MARGIN:HI:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:MARGIN:LO:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:FWMIN:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DTune-SP', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:DELAY:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:POS:S', 0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:FILT:S', 0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:TOPRAMP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:TRIG:S', 0, 0.0],
    ['BR-RF-DLLRF-01:mV:AL:REF:S.DRVH', 0.0, 0.0],
    ['BR-RF-DLLRF-01:mV:AL:REF:S.DRVL', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLGAIN:S.DRVH', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLGAIN:S.DRVL', 0.0, 0.0],
    ['BR-RF-DLLRF-01:SL:KP:S.DRVH', 0, 0.0],
    ['BR-RF-DLLRF-01:SL:KP:S.DRVL', 0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:U-Raw:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:U-Raw:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:U-Raw:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:U-Raw:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:U-Raw:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:U-Raw:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:U-Raw:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:U-Raw:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:U-Raw:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA2:Const:U-Raw:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPCAV:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPCAV:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPCAV:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPCAV:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPCAV:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPCAV:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPFWD:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPFWD:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPFWD:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPFWD:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPFWD:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:AMPFWD:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:OUT:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:OUT:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:OUT:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:OUT:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:OUT:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:DACIF:OUT:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL3:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL3:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL3:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL3:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL3:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL3:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL2:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL2:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL2:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVSSA1:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVSSA1:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVSSA1:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVSSA1:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVSSA1:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVCAV:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVCAV:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVCAV:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVCAV:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVCAV:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVCAV:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL3:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL3:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL3:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL3:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL3:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL3:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL2:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL2:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL2:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL2:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL2:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL2:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL4:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL4:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL4:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL4:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL4:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:CELL4:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDSSA1:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDSSA1:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDSSA1:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDSSA1:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDSSA1:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDSSA1:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVSSA1:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVSSA1:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVSSA1:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVSSA1:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVSSA1:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVSSA1:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVCAV:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVCAV:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVCAV:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVCAV:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVCAV:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:REVCAV:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDCAV:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDCAV:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDCAV:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDCAV:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDCAV:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDCAV:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDCAV:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDCAV:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDCAV:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDCAV:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDCAV:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:BOT:FWDCAV:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL2:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL2:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL2:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL2:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL2:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL2:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL4:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL4:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL4:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL4:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL4:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:FF:CELL4:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:CAV:Const:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDCAV:Const:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA1:Const:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA2:Const:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:CAV:Const:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDCAV:Const:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA1:Const:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA2:Const:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:CAV:Const:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDCAV:Const:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA1:Const:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA2:Const:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:CAV:Const:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDCAV:Const:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA1:Const:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA2:Const:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:CAV:Const:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDCAV:Const:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA1:Const:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA2:Const:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL2:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL2:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL2:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL4:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL4:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL4:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL4:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL4:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:CELL4:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDSSA1:Const:Raw-U:C4:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDSSA1:Const:Raw-U:C3:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDSSA1:Const:Raw-U:C2:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDSSA1:Const:Raw-U:C1:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDSSA1:Const:Raw-U:C0:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:FWDSSA1:Const:OFS:S', 0.0, 0.0],
    ['BR-RF-DLLRF-01:TOP:REVSSA1:Const:Raw-U:C4:S', 0.0, 0.0],
    ]

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
    ['TB-04:PS-CV-2:OpMode-Sel', _SLOWREF, 0.0],

    ['TB-Fam:PS-B:Current-SP', 0.0, 0.0],    # unit: A
    ['TB-01:PS-QD1:Current-SP', 0.0, 0.0],   # unit: A
    ['TB-01:PS-QF1:Current-SP', 0.0, 0.0],   # unit: A
    ['TB-02:PS-QD2A:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-02:PS-QF2A:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-02:PS-QF2B:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-02:PS-QD2B:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-03:PS-QF3:Current-SP', 0.0, 0.0],   # unit: A
    ['TB-03:PS-QD3:Current-SP', 0.0, 0.0],   # unit: A
    ['TB-04:PS-QF4:Current-SP', 0.0, 0.0],   # unit: A
    ['TB-04:PS-QD4:Current-SP', 0.0, 0.0],   # unit: A
    ['TB-01:PS-CH-1:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-01:PS-CV-1:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-01:PS-CH-2:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-01:PS-CV-2:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-02:PS-CH-1:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-02:PS-CV-1:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-02:PS-CH-2:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-02:PS-CV-2:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-04:PS-CH-1:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-04:PS-CH-2:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-04:PS-CV-1:Current-SP', 0.0, 0.0],  # unit: A
    ['TB-04:PS-CV-2:Current-SP', 0.0, 0.0],  # unit: A
    ]

_pvs_bo_ps = [
    ['BO-Fam:PS-B-1:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-Fam:PS-B-2:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-Fam:PS-QD:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-Fam:PS-QF:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-02D:PS-QS:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-Fam:PS-SD:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-Fam:PS-SF:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-01U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-03U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-05U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-07U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-09U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-11U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-13U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-15U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-17U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-19U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-21U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-23U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-25U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-27U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-29U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-31U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-33U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-35U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-37U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-39U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-41U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-43U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-45U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-47U:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-49D:PS-CH:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-01U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-03U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-05U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-07U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-09U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-11U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-13U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-15U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-17U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-19U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-21U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-23U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-25U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-27U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-29U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-31U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-33U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-35U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-37U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-39U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-41U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-43U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-45U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-47U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['BO-49U:PS-CV:OpMode-Sel', _SLOWREF, 0.0],

    ['BO-Fam:PS-B-1:Current-SP', 0.0, 0.0],  # unit: A
    ['BO-Fam:PS-B-2:Current-SP', 0.0, 0.0],  # unit: A
    ['BO-Fam:PS-QD:Current-SP', 0.0, 0.0],   # unit: A
    ['BO-Fam:PS-QF:Current-SP', 0.0, 0.0],   # unit: A
    ['BO-02D:PS-QS:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-Fam:PS-SD:Current-SP', 0.0, 0.0],   # unit: A
    ['BO-Fam:PS-SF:Current-SP', 0.0, 0.0],   # unit: A
    ['BO-01U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-03U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-05U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-07U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-09U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-11U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-13U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-15U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-17U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-19U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-21U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-23U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-25U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-27U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-29U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-31U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-33U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-35U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-37U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-39U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-41U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-43U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-45U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-47U:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-49D:PS-CH:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-01U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-03U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-05U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-07U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-09U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-11U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-13U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-15U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-17U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-19U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-21U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-23U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-25U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-27U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-29U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-31U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-33U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-35U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-37U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-39U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-41U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-43U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-45U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-47U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A
    ['BO-49U:PS-CV:Current-SP', +0.0, 0.0],  # unit: A

    ['BO-Fam:PS-B-1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['BO-Fam:PS-B-2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['BO-Fam:PS-QD:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['BO-Fam:PS-QF:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['BO-Fam:PS-SD:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['BO-Fam:PS-SF:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['BO-02D:PS-QS:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-01U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-03U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-05U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-07U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-09U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-11U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-13U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-15U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-17U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-19U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-21U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-23U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-25U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-27U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-29U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-31U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-33U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-35U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-37U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-39U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-41U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-43U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-45U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-47U:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-49D:PS-CH:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-01U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-03U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-05U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-07U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-09U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-11U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-13U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-15U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-17U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-19U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-21U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-23U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-25U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-27U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-29U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-31U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-33U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-35U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-37U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-39U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-41U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-43U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-45U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-47U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0],
    ['BO-49U:PS-CV:Wfm-SP', _DEFAULT_WFM_FBP, 0.0]]

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
    ['TS-01:PS-CV-2:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-02:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-03:PS-CV:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-04:PS-CV-1:OpMode-Sel', _SLOWREF, 0.0],
    ['TS-04:PS-CV-2:OpMode-Sel', _SLOWREF, 0.0],

    ['TS-Fam:PS-B:Current-SP', 0.0, 0.0],    # unit: A
    ['TS-01:PS-QF1A:Current-SP', 0.0, 0.0],   # unit: A
    ['TS-01:PS-QF1B:Current-SP', 0.0, 0.0],   # unit: A
    ['TS-02:PS-QF2:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-03:PS-QF3:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-04:PS-QF4:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-02:PS-QD2:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-04:PS-QD4A:Current-SP', 0.0, 0.0],   # unit: A
    ['TS-04:PS-QD4B:Current-SP', 0.0, 0.0],   # unit: A
    ['TS-01:PS-CH:Current-SP', 0.0, 0.0],   # unit: A
    ['TS-02:PS-CH:Current-SP', 0.0, 0.0],   # unit: A
    ['TS-03:PS-CH:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-04:PS-CH:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-01:PS-CV-1:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-01:PS-CV-2:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-02:PS-CV:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-03:PS-CV:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-04:PS-CV-1:Current-SP', 0.0, 0.0],  # unit: A
    ['TS-04:PS-CV-2:Current-SP', 0.0, 0.0],  # unit: A
    ]

_pvs_si_ps = [
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
    ['SI-Fam:PS-SDP3:OpMode-Sel', _SLOWREF, 0.0],

    ['SI-Fam:PS-B1B2-1:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-B1B2-2:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-QFA:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-QFB:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-QFP:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-QDA:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-QDB1:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-QDB2:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-QDP1:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-QDP2:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-Q1:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-Q2:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-Q3:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-Q4:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SFA0:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SFA1:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SFA2:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SFB0:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SFB1:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SFB2:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SFP0:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SFP1:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SFP2:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDA0:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDA1:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDA2:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDA3:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDB0:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDB1:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDB2:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDB3:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDP0:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDP1:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDP2:Current-SP', 0.0, 0.0],  # unit: A
    ['SI-Fam:PS-SDP3:Current-SP', 0.0, 0.0],  # unit: A

    ['SI-Fam:PS-B1B2-1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-B1B2-2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-QFA:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-QFB:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-QFP:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-QDA:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-QDB1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-QDB2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-QDP1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-QDP2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-Q1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-Q2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-Q3:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-Q4:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SFA0:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SFA1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SFA2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SFB0:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SFB1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SFB2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SFP0:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SFP1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SFP2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDA0:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDA1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDA2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDA3:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDB0:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDB1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDB2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDB3:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDP0:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDP1:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDP2:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ['SI-Fam:PS-SDP3:Wfm-SP', _DEFAULT_WFM_OTHERS, 0.0],
    ]

_template_dict = {
    'pvs':
        _pvs_li_egunmod + _pvs_li_llrf + _pvs_timing +
        _pvs_li_ps + _pvs_pu + _rf_pvs +
        _pvs_tb_ps + _pvs_bo_ps + _pvs_ts_ps + _pvs_si_ps
    }
