"""TB High Level Timing configuration."""
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
        ['RA-RaMO:TI-EVG:InjBOMode-Sel', 0, 0.0],
        ['RA-RaMO:TI-EVG:DigTBMode-Sel', 0, 0.0],
        ['RA-RaMO:TI-EVG:LinacMode-Sel', 0, 0.0],
        ['RA-RaMO:TI-EVG:DigLIMode-Sel', 0, 0.0],

        ['RA-RaMO:TI-EVG:InjBODelayType-Sel', 0, 0.0],
        ['RA-RaMO:TI-EVG:DigTBDelayType-Sel', 0, 0.0],
        ['RA-RaMO:TI-EVG:LinacDelayType-Sel', 0, 0.0],
        ['RA-RaMO:TI-EVG:DigLIDelayType-Sel', 0, 0.0],

        ['RA-RaMO:TI-EVG:InjBODelay-SP', 0.0, 0.0],
        ['RA-RaMO:TI-EVG:DigTBDelay-SP', 0.0, 0.0],
        ['RA-RaMO:TI-EVG:LinacDelay-SP', 0.0, 0.0],
        ['RA-RaMO:TI-EVG:DigLIDelay-SP', 0.0, 0.0],

        ['TB-Glob:TI-Mags:State-Sel', 0, 0.0],
        ['TB-04:TI-InjSept:State-Sel', 0, 0.0],
        ['AS-Fam:TI-Scrn-TBBO:State-Sel', 0, 0.0],
        ['AS-Glob:TI-BPM-TBTS:State-Sel', 0, 0.0],
        ['AS-Glob:TI-Osc-InjBO:State-Sel', 0, 0.0],
        ['TB-Fam:TI-ICT-Digit:State-Sel', 0, 0.0],
        ['TB-Fam:TI-ICT-Integ:State-Sel', 0, 0.0],
        ['BO-01D:TI-InjKckr:State-Sel', 0, 0.0],
        ['AS-Glob:TI-FCT:State-Sel', 0, 0.0],

        ['TB-Glob:TI-Mags:Polarity-Sel', 0, 0.0],
        ['TB-04:TI-InjSept:Polarity-Sel', 0, 0.0],
        ['AS-Fam:TI-Scrn-TBBO:Polarity-Sel', 0, 0.0],
        ['AS-Glob:TI-BPM-TBTS:Polarity-Sel', 0, 0.0],
        ['AS-Glob:TI-Osc-InjBO:Polarity-Sel', 0, 0.0],
        ['TB-Fam:TI-ICT-Digit:Polarity-Sel', 0, 0.0],
        ['TB-Fam:TI-ICT-Integ:Polarity-Sel', 0, 0.0],
        ['BO-01D:TI-InjKckr:Polarity-Sel', 0, 0.0],
        ['AS-Glob:TI-FCT:Polarity-Sel', 0, 0.0],

        ['TB-Glob:TI-Mags:Src-Sel', 0, 0.0],
        ['TB-04:TI-InjSept:Src-Sel', 0, 0.0],
        ['AS-Fam:TI-Scrn-TBBO:Src-Sel', 0, 0.0],
        ['AS-Glob:TI-BPM-TBTS:Src-Sel', 0, 0.0],
        ['AS-Glob:TI-Osc-InjBO:Src-Sel', 0, 0.0],
        ['TB-Fam:TI-ICT-Digit:Src-Sel', 0, 0.0],
        ['TB-Fam:TI-ICT-Integ:Src-Sel', 0, 0.0],
        ['BO-01D:TI-InjKckr:Src-Sel', 0, 0.0],
        ['AS-Glob:TI-FCT:Src-Sel', 0, 0.0],

        ['TB-Glob:TI-Mags:NrPulses-SP', 0, 0.0],
        ['TB-04:TI-InjSept:NrPulses-SP', 0, 0.0],
        ['AS-Fam:TI-Scrn-TBBO:NrPulses-SP', 0, 0.0],
        ['AS-Glob:TI-BPM-TBTS:NrPulses-SP', 0, 0.0],
        ['AS-Glob:TI-Osc-InjBO:NrPulses-SP', 0, 0.0],
        ['TB-Fam:TI-ICT-Digit:NrPulses-SP', 0, 0.0],
        ['TB-Fam:TI-ICT-Integ:NrPulses-SP', 0, 0.0],
        ['BO-01D:TI-InjKckr:NrPulses-SP', 0, 0.0],
        ['AS-Glob:TI-FCT:NrPulses-SP', 0, 0.0],

        ['TB-Glob:TI-Mags:Duration-SP', 0.0, 0.0],
        ['TB-04:TI-InjSept:Duration-SP', 0.0, 0.0],
        ['AS-Fam:TI-Scrn-TBBO:Duration-SP', 0.0, 0.0],
        ['AS-Glob:TI-BPM-TBTS:Duration-SP', 0.0, 0.0],
        ['AS-Glob:TI-Osc-InjBO:Duration-SP', 0.0, 0.0],
        ['TB-Fam:TI-ICT-Digit:Duration-SP', 0.0, 0.0],
        ['TB-Fam:TI-ICT-Integ:Duration-SP', 0.0, 0.0],
        ['BO-01D:TI-InjKckr:Duration-SP', 0.0, 0.0],
        ['AS-Glob:TI-FCT:Duration-SP', 0.0, 0.0],

        ['TB-Glob:TI-Mags:Delay-SP', 0.0, 0.0],
        ['TB-04:TI-InjSept:Delay-SP', 0.0, 0.0],
        ['AS-Fam:TI-Scrn-TBBO:Delay-SP', 0.0, 0.0],
        ['AS-Glob:TI-BPM-TBTS:Delay-SP', 0.0, 0.0],
        ['AS-Glob:TI-Osc-InjBO:Delay-SP', 0.0, 0.0],
        ['TB-Fam:TI-ICT-Digit:Delay-SP', 0.0, 0.0],
        ['TB-Fam:TI-ICT-Integ:Delay-SP', 0.0, 0.0],
        ['BO-01D:TI-InjKckr:Delay-SP', 0.0, 0.0],
        ['AS-Glob:TI-FCT:Delay-SP', 0.0, 0.0],

        # ['TB-Glob:TI-Mags:ByPassIntlk-Sel', 0, 0.0],
        ['TB-04:TI-InjSept:ByPassIntlk-Sel', 0, 0.0],
        ['AS-Fam:TI-Scrn-TBBO:ByPassIntlk-Sel', 0, 0.0],
        # ['AS-Glob:TI-BPM-TBTS:ByPassIntlk-Sel', 0, 0.0],
        ['AS-Glob:TI-Osc-InjBO:ByPassIntlk-Sel', 0, 0.0],
        ['TB-Fam:TI-ICT-Digit:ByPassIntlk-Sel', 0, 0.0],
        ['TB-Fam:TI-ICT-Integ:ByPassIntlk-Sel', 0, 0.0],
        ['BO-01D:TI-InjKckr:ByPassIntlk-Sel', 0, 0.0],
        ['AS-Glob:TI-FCT:ByPassIntlk-Sel', 0, 0.0],

        # ['TB-Glob:TI-Mags:RFDelayType-Sel', 0, 0.0],
        # ['TB-04:TI-InjSept:RFDelayType-Sel', 0, 0.0],
        ['AS-Fam:TI-Scrn-TBBO:RFDelayType-Sel', 0, 0.0],
        # ['AS-Glob:TI-BPM-TBTS:RFDelayType-Sel', 0, 0.0],
        # ['AS-Glob:TI-Osc-InjBO:RFDelayType-Sel', 0, 0.0],
        # ['TB-Fam:TI-ICT-Digit:RFDelayType-Sel', 0, 0.0],
        # ['TB-Fam:TI-ICT-Integ:RFDelayType-Sel', 0, 0.0],
        # ['BO-01D:TI-InjKckr:RFDelayType-Sel', 0, 0.0],
        ['AS-Glob:TI-FCT:RFDelayType-Sel', 0, 0.0],
    ]
}
