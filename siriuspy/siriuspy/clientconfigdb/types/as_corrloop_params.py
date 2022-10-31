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
    ['SI-Glob:AP-SOFB:SOFBMode-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:RefOrbX-SP', [0.0, ]*800, 0.0],
    ['SI-Glob:AP-SOFB:RefOrbY-SP', [0.0, ]*800, 0.0],
    ['SI-Glob:AP-SOFB:SmoothNrPts-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:OrbAcqRate-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:SmoothMethod-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:LoopFreq-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:LoopMaxOrbDistortion-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:LoopPIDKpCH-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:LoopPIDKpCV-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:LoopPIDKpRF-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:LoopPIDKiCH-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:LoopPIDKiCV-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:LoopPIDKiRF-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:LoopPIDKdCH-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:LoopPIDKdCV-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:LoopPIDKdRF-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MaxKickCH-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MaxKickCV-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MaxDeltaKickCH-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MaxDeltaKickCV-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:MaxDeltaKickRF-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:CorrSync-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:CorrPSSOFBWait-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:CorrPSSOFBEnbl-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:FOFBDownloadKicks-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:FOFBUpdateRefOrb-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:FOFBNullSpaceProj-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:FOFBZeroDistortionAtBPMs-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:FOFBDownloadKicksPerc-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:FOFBUpdateRefOrbPerc-SP', 0, 0.0],
    ['SI-Glob:AP-SOFB:RespMat-SP', [0.0, ]*449600, 0.0],
    ['SI-Glob:AP-SOFB:RespMatMode-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:BPMXEnblList-SP', [0, ]*800, 0.0],
    ['SI-Glob:AP-SOFB:BPMYEnblList-SP', [0, ]*800, 0.0],
    ['SI-Glob:AP-SOFB:CHEnblList-SP', [0, ]*120, 0.0],
    ['SI-Glob:AP-SOFB:CVEnblList-SP', [0, ]*160, 0.0],
    ['SI-Glob:AP-SOFB:RFEnbl-Sel', 0, 0.0],
    ['SI-Glob:AP-SOFB:MinSingValue-SP', 0.0, 0.0],
    ['SI-Glob:AP-SOFB:TikhonovRegConst-SP', 0.0, 0.0],
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
