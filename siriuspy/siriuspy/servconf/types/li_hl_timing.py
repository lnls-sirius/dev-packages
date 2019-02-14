"""LI power supply current setpoint configuration."""
from copy import deepcopy as _dcopy


def get_dict():
    """Return configuration type dictionary."""
    module_name = __name__.split('.')[-1]
    _dict = {
        'config_type_name': module_name,
        'value': _dcopy(_template_dict)
    }
    return _dict


# When using this type of configuration to set the machine,
# the list of PVs should be processed in the same order they are stored
# in the configuration. The second numeric parameter in the pair is the
# delay [s] the client should wait before setting the next PV.


_template_dict = {
    'pvs': [
        ['RA-RaMO:TI-EVG:LinacMode-Sel', 0, 0.0],
        ['RA-RaMO:TI-EVG:DigLIMode-Sel', 0, 0.0],

        ['RA-RaMO:TI-EVG:LinacDelayType-Sel', 0, 0.0],
        ['RA-RaMO:TI-EVG:DigLIDelayType-Sel', 0, 0.0],

        ['RA-RaMO:TI-EVG:LinacDelay-SP', 0.0, 0.0],
        ['RA-RaMO:TI-EVG:DigLIDelay-SP', 0.0, 0.0],

        ['LI-01:TI-EGun-MultBun:State-Sel', 0, 0.0],
        ['LI-01:TI-EGun-SglBun:State-Sel', 0, 0.0],
        ['LI-01:TI-Modltr-1:State-Sel', 0, 0.0],
        ['LI-01:TI-Modltr-2:State-Sel', 0, 0.0],
        ['LI-Fam:TI-BPM:State-Sel', 0, 0.0],
        ['LI-Fam:TI-ICT:State-Sel', 0, 0.0],
        ['LI-Fam:TI-Scrn:State-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-Kly1:State-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-Kly2:State-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-SHB:State-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly1:State-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly2:State-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-SHB:State-Sel', 0, 0.0],

        ['LI-01:TI-EGun-MultBun:Polarity-Sel', 0, 0.0],
        ['LI-01:TI-EGun-SglBun:Polarity-Sel', 0, 0.0],
        ['LI-01:TI-Modltr-1:Polarity-Sel', 0, 0.0],
        ['LI-01:TI-Modltr-2:Polarity-Sel', 0, 0.0],
        ['LI-Fam:TI-BPM:Polarity-Sel', 0, 0.0],
        ['LI-Fam:TI-ICT:Polarity-Sel', 0, 0.0],
        ['LI-Fam:TI-Scrn:Polarity-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-Kly1:Polarity-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-Kly2:Polarity-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-SHB:Polarity-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly1:Polarity-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly2:Polarity-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-SHB:Polarity-Sel', 0, 0.0],

        ['LI-01:TI-EGun-MultBun:Src-Sel', 0, 0.0],
        ['LI-01:TI-EGun-SglBun:Src-Sel', 0, 0.0],
        ['LI-01:TI-Modltr-1:Src-Sel', 0, 0.0],
        ['LI-01:TI-Modltr-2:Src-Sel', 0, 0.0],
        ['LI-Fam:TI-BPM:Src-Sel', 0, 0.0],
        ['LI-Fam:TI-ICT:Src-Sel', 0, 0.0],
        ['LI-Fam:TI-Scrn:Src-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-Kly1:Src-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-Kly2:Src-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-SHB:Src-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly1:Src-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly2:Src-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-SHB:Src-Sel', 0, 0.0],

        ['LI-01:TI-EGun-MultBun:NrPulses-SP', 0, 0.0],
        ['LI-01:TI-EGun-SglBun:NrPulses-SP', 0, 0.0],
        ['LI-01:TI-Modltr-1:NrPulses-SP', 0, 0.0],
        ['LI-01:TI-Modltr-2:NrPulses-SP', 0, 0.0],
        ['LI-Fam:TI-BPM:NrPulses-SP', 0, 0.0],
        ['LI-Fam:TI-ICT:NrPulses-SP', 0, 0.0],
        ['LI-Fam:TI-Scrn:NrPulses-SP', 0, 0.0],
        ['LI-Glob:TI-LLRF-Kly1:NrPulses-SP', 0, 0.0],
        ['LI-Glob:TI-LLRF-Kly2:NrPulses-SP', 0, 0.0],
        ['LI-Glob:TI-LLRF-SHB:NrPulses-SP', 0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly1:NrPulses-SP', 0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly2:NrPulses-SP', 0, 0.0],
        ['LI-Glob:TI-SSAmp-SHB:NrPulses-SP', 0, 0.0],

        ['LI-01:TI-EGun-MultBun:Duration-SP', 0.0, 0.0],
        ['LI-01:TI-EGun-SglBun:Duration-SP', 0.0, 0.0],
        ['LI-01:TI-Modltr-1:Duration-SP', 0.0, 0.0],
        ['LI-01:TI-Modltr-2:Duration-SP', 0.0, 0.0],
        ['LI-Fam:TI-BPM:Duration-SP', 0.0, 0.0],
        ['LI-Fam:TI-ICT:Duration-SP', 0.0, 0.0],
        ['LI-Fam:TI-Scrn:Duration-SP', 0.0, 0.0],
        ['LI-Glob:TI-LLRF-Kly1:Duration-SP', 0.0, 0.0],
        ['LI-Glob:TI-LLRF-Kly2:Duration-SP', 0.0, 0.0],
        ['LI-Glob:TI-LLRF-SHB:Duration-SP', 0.0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly1:Duration-SP', 0.0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly2:Duration-SP', 0.0, 0.0],
        ['LI-Glob:TI-SSAmp-SHB:Duration-SP', 0.0, 0.0],

        ['LI-01:TI-EGun-MultBun:Delay-SP', 0.0, 0.0],
        ['LI-01:TI-EGun-SglBun:Delay-SP', 0.0, 0.0],
        ['LI-01:TI-Modltr-1:Delay-SP', 0.0, 0.0],
        ['LI-01:TI-Modltr-2:Delay-SP', 0.0, 0.0],
        ['LI-Fam:TI-BPM:Delay-SP', 0.0, 0.0],
        ['LI-Fam:TI-ICT:Delay-SP', 0.0, 0.0],
        ['LI-Fam:TI-Scrn:Delay-SP', 0.0, 0.0],
        ['LI-Glob:TI-LLRF-Kly1:Delay-SP', 0.0, 0.0],
        ['LI-Glob:TI-LLRF-Kly2:Delay-SP', 0.0, 0.0],
        ['LI-Glob:TI-LLRF-SHB:Delay-SP', 0.0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly1:Delay-SP', 0.0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly2:Delay-SP', 0.0, 0.0],
        ['LI-Glob:TI-SSAmp-SHB:Delay-SP', 0.0, 0.0],

        ['LI-01:TI-EGun-MultBun:ByPassIntlk-Sel', 0, 0.0],
        ['LI-01:TI-EGun-SglBun:ByPassIntlk-Sel', 0, 0.0],
        ['LI-01:TI-Modltr-1:ByPassIntlk-Sel', 0, 0.0],
        ['LI-01:TI-Modltr-2:ByPassIntlk-Sel', 0, 0.0],
        ['LI-Fam:TI-BPM:ByPassIntlk-Sel', 0, 0.0],
        ['LI-Fam:TI-ICT:ByPassIntlk-Sel', 0, 0.0],
        ['LI-Fam:TI-Scrn:ByPassIntlk-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-Kly1:ByPassIntlk-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-Kly2:ByPassIntlk-Sel', 0, 0.0],
        ['LI-Glob:TI-LLRF-SHB:ByPassIntlk-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly1:ByPassIntlk-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-Kly2:ByPassIntlk-Sel', 0, 0.0],
        ['LI-Glob:TI-SSAmp-SHB:ByPassIntlk-Sel', 0, 0.0],

        ['LI-01:TI-EGun-MultBun:RFDelayType-Sel', 0, 0.0],
        ['LI-01:TI-EGun-SglBun:RFDelayType-Sel', 0, 0.0],
        # ['LI-01:TI-Modltr-1:RFDelayType-Sel', 0, 0.0],
        # ['LI-01:TI-Modltr-2:RFDelayType-Sel', 0, 0.0],
        ['LI-Fam:TI-BPM:RFDelayType-Sel', 0, 0.0],
        ['LI-Fam:TI-ICT:RFDelayType-Sel', 0, 0.0],
        ['LI-Fam:TI-Scrn:RFDelayType-Sel', 0, 0.0],
        # ['LI-Glob:TI-LLRF-Kly1:RFDelayType-Sel', 0, 0.0],
        # ['LI-Glob:TI-LLRF-Kly2:RFDelayType-Sel', 0, 0.0],
        # ['LI-Glob:TI-LLRF-SHB:RFDelayType-Sel', 0, 0.0],
        # ['LI-Glob:TI-SSAmp-Kly1:RFDelayType-Sel', 0, 0.0],
        # ['LI-Glob:TI-SSAmp-Kly2:RFDelayType-Sel', 0, 0.0],
        # ['LI-Glob:TI-SSAmp-SHB:RFDelayType-Sel', 0, 0.0],

    ]
}
