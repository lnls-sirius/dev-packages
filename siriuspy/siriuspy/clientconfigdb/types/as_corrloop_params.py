"""Parameters of the IOCs of the AP discipline."""
from copy import deepcopy as _dcopy

_off = 0
_on = 1


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

_si_sofb = [
    ['SI-Glob:AP-SOFB:BPMXEnblList-SP', [0, ]*800, 0.0],
    ['SI-Glob:AP-SOFB:BPMYEnblList-SP', [0, ]*800, 0.0],
    ['SI-Glob:AP-SOFB:CHEnblList-SP', [0, ]*120, 0.0],
    ['SI-Glob:AP-SOFB:CVEnblList-SP', [0, ]*160, 0.0],
    ['SI-Glob:AP-SOFB:LoopFreq-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:CorrSync-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:ManCorrGainCH-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:ManCorrGainCV-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:ManCorrGainRF-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:KickAcqRate-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MTurnDownSample-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:MTurnIdx-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:MTurnMaskSplBeg-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:MTurnMaskSplEnd-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:MTurnSyncTim-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:MTurnUseMask-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:MaxDeltaKickCH-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MaxDeltaKickCV-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MaxDeltaKickRF-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MaxKickCH-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MaxKickCV-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MeasRespMatKickCH-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MeasRespMatKickCV-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MeasRespMatKickRF-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MeasRespMatWait-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:OfflineOrbX-SP', [0.0, ]*800, 0.0],
    ['SI-Glob:AP-SOFB:OfflineOrbY-SP', [0.0, ]*800, 0.0],
    ['SI-Glob:AP-SOFB:OrbAcqRate-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:RFEnbl-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:RefOrbX-SP', [0.0, ]*800, 0.0],
    ['SI-Glob:AP-SOFB:RefOrbY-SP', [0.0, ]*800, 0.0],
    ['SI-Glob:AP-SOFB:RespMat-SP', [0.0, ]*449600, 0.0],
    ['SI-Glob:AP-SOFB:RespMatMode-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:RingSize-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:SOFBMode-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:SPassAvgNrTurns-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:SPassMaskSplBeg-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:SPassMaskSplEnd-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:SPassMethod-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:SPassUseBg-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:SmoothMethod-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:SmoothNrPts-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigAcqChan-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigAcqCtrl-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigAcqRepeat-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigAcqTrigger-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigDataChan-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigDataHyst-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigDataPol-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigDataSel-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigDataThres-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigNrSamplesPost-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigNrSamplesPre-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:TrigNrShots-SP', 0, 0.0],
]


_si_fofb = [
    ['SI-Glob:AP-FOFB:LoopGainH-SP', 0.0, 0.0],
    ['SI-Glob:AP-FOFB:LoopGainV-SP', 0.0, 0.0],
    ['SI-Glob:AP-FOFB:CHAccSatMax-SP', 0.0, 0.0],
    ['SI-Glob:AP-FOFB:CVAccSatMax-SP', 0.0, 0.0],
    ['SI-Glob:AP-FOFB:TimeFrameLen-SP', 0.0, 0.0],
    ['SI-Glob:AP-FOFB:FOFBCtrlSyncUseEnblList-Sel', 0, 0.0],
    ['SI-Glob:AP-FOFB:KickBufferSize-SP', 0, 0.0],
    ['SI-Glob:AP-FOFB:RefOrbX-SP', [0.0, ]*160, 0.0],
    ['SI-Glob:AP-FOFB:RefOrbY-SP', [0.0, ]*160, 0.0],
    ['SI-Glob:AP-FOFB:BPMXEnblList-SP', [0, ]*160, 0.0],
    ['SI-Glob:AP-FOFB:BPMYEnblList-SP', [0, ]*160, 0.0],
    ['SI-Glob:AP-FOFB:CHEnblList-SP', [0, ]*80, 0.0],
    ['SI-Glob:AP-FOFB:CVEnblList-SP', [0, ]*80, 0.0],
    ['SI-Glob:AP-FOFB:UseRF-Sel', 0, 0.0],
    ['SI-Glob:AP-FOFB:RespMat-SP', [0.0, ]*51520, 0.0],
    ['SI-Glob:AP-FOFB:MinSingValue-SP', 0.0, 0.0],
    ['SI-Glob:AP-FOFB:TikhonovRegConst-SP', 0.0, 0.0],
    ['SI-Glob:AP-FOFB:InvRespMatNormMode-Sel', 0, 0.0],
]


_template_dict = {'pvs': _si_sofb + _si_fofb}
