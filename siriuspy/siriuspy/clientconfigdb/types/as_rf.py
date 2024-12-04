"""AS RF configuration."""
from copy import deepcopy as _dcopy
import numpy as _np

az = _np.zeros(5)

# NOTE: absolute imports are necessary here due to how
# CONFIG_TYPES in __init__.py is built.
from siriuspy.clientconfigdb.types.global_config import _pvs_as_rf, \
    _pvs_li_llrf


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

_pvs_bo_llrf = [
    # Interlock disable
    ['RA-RaBO01:RF-LLRF:FIMRevSSA1-Sel', 0.0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRevSSA2-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRevSSA3-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRevSSA4-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRevCav-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMManual-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMPLC-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMLLRF1-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMLLRF2-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMLLRF3-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMPLG1Up-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMPLG1Down-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMPLG2Up-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMPLG2Down-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMCav-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMFwdCav-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMFwdSSA1-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRFIn7-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRFIn8-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRFIn9-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRFIn10-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRFIn11-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRFIn12-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRFIn13-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRFIn14-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMRFIn15-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMOrbitIntlk-Sel', 0, 0.0],
    # End switches logic
    ['RA-RaBO01:RF-LLRF:EndSwLogicInv-Sel', 0, 0.0],
    # Beam trip logic
    ['RA-RaBO01:RF-LLRF:OrbitIntlkLogicInv-Sel', 0, 0.0],
    # Vacuum sensor logic
    ['RA-RaBO01:RF-LLRF:VacLogicInv-Sel', 0, 0.0],
    # Pwr interlock threshold
    ['RA-RaBO01:RF-LLRF:LimRevSSA1-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRevSSA2-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRevSSA3-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRevSSA4-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRevCav-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimCav-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimFwdCav-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimFwdSSA1-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRFIn7-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRFIn8-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRFIn9-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRFIn10-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRFIn11-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRFIn12-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRFIn13-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRFIn14-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:LimRFIn15-SP', 0, 0.0],
    # Interlock delay
    ['RA-RaBO01:RF-LLRF:IntlkDly-SP', 0, 0.0],
    # Settings PVs values lims
    ### Are we still saving this?
    ['RA-RaBO01:RF-LLRF:ALRef-SP.DRVH', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:ALRef-SP.DRVL', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpAmpTop-SP.DRVH', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpAmpTop-SP.DRVL', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpAmpBot-SP.DRVH', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpAmpBot-SP.DRVL', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:OLGain-SP.DRVH', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:OLGain-SP.DRVL', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:SLKP-SP.DRVH', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:SLKP-SP.DRVL', 0, 0.0],
    # Pressure threshold
    ['BO-05D:VA-CCG-RFC:FastRelay-SP', 0, 0.0],
    # Pressure Lock power increase
    ['RA-RaBO01:RF-LLRF:CondAuto-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:EPSEnbl-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FIMEnbl-Sel', 0, 0.0],
    # ADC Phase and Gain
    ['RA-RaBO01:RF-LLRF:PhShCav-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PhShFwdCav-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PhShFwdSSA1-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PhShFwdSSA2-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PhShFwdSSA3-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PhShFwdSSA4-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:GainFwdCav-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:GainFwdSSA1-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:GainFwdSSA2-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:GainFwdSSA3-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:GainFwdSSA4-SP', 0, 0.0],
    # DAC Phse and Gain
    ['RA-RaBO01:RF-LLRF:PhShSSA1-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PhShSSA2-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PhShSSA3-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PhShSSA4-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:GainSSA1-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:GainSSA2-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:GainSSA3-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:GainSSA4-SP', 0, 0.0],
    # Loops parameters
    ['RA-RaBO01:RF-LLRF:SLKP-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:SLKI-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:SLPILim-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:SLInp-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FLKP-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FLKI-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FLPILim-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FLInp-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:ALKP-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:ALKI-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:ALInp-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PLKP-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PLKI-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:PLInp-Sel', 0, 0.0],
    # Loop mode
    ['RA-RaBO01:RF-LLRF:LoopMode-Sel', 0, 0.0],
    # Min forward power
    ['RA-RaBO01:RF-LLRF:LoopFwdMin-SP', 0, 0.0],
    # Min amplitude ref
    ['RA-RaBO01:RF-LLRF:AmpRefMin-SP', 0, 0.0],
    # Min phase ref
    ['RA-RaBO01:RF-LLRF:PhsRefMin-SP', 0, 0.0],
    # Open loop gain
    ['RA-RaBO01:RF-LLRF:OLGain-SP', 0, 0.0],
    # Tuning loop config
    ['RA-RaBO01:RF-LLRF:Tune-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:TuneDir-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:TuneFwdMin-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:TuneMarginHI-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:TuneMarginLO-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Detune-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:TuneDly-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:TuneFreq-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:TuneFilt-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:TuneTrig-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpTuneTop-Sel', 0, 0.0],
    # Field Flatness loop config
    ['RA-RaBO01:RF-LLRF:FFEnbl-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FFDir-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FFDeadBand-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FFGainCell2-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FFGainCell4-SP', 0, 0.0],
    # Pulsed mode config
    ['RA-RaBO01:RF-LLRF:CondFreq-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:CondDuty2-SP', 0, 0.0],
    # Rmp mode config
    ['RA-RaBO01:RF-LLRF:RmpTs1-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpTs2-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpTs3-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpTs4-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpAmpBot-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpPhsBot-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpAmpTop-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpPhsTop-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpIncTime-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RmpDownDsbl-Sel', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FDLFrame-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FDLRearm-Sel', 0, 0.0],
    # Enable plungers step motor drivers
    ['RA-RaBO01:RF-CavPlDrivers:DrEnbl-Sel', 0, 0.0],
    # Enable ADC phase and gain
    ['RA-RaBO01:RF-LLRF:PhShADC-Sel', 0, 0.0],
    # Enable DAC phase and gain
    ['RA-RaBO01:RF-LLRF:PhShDAC-Sel', 0, 0.0]
    ]

_pvs_bo_rfssa = [
    # SSA tower offsets
    ['RA-ToBO:OffsetConfig:UpperIncidentPower', 0, 0.0],  # [dB]
    ['RA-ToBO:OffsetConfig:UpperReflectedPower', 0, 0.0],  # [dB]
    ['RA-ToBO:OffsetConfig:LowerIncidentPower', 0, 0.0],  # [dB]
    ['RA-ToBO:OffsetConfig:LowerReflectedPower', 0, 0.0],  # [dB]
    ['RA-ToBO:OffsetConfig:InputIncidentPower', 0, 0.0],  # [dB]
    ['RA-ToBO:OffsetConfig:InputReflectedPower', 0, 0.0],  # [dB]
    ['RA-ToBO:OffsetConfig:OutputIncidentPower', 0, 0.0],  # [dB]
    ['RA-ToBO:OffsetConfig:OutputReflectedPower', 0, 0.0],  # [dB]
    # SSA tower pwr alarm limits
    ['RA-ToBO:AlarmConfig:GeneralPowerLimHiHi', 0, 0.0],  # [dBm]
    ['RA-ToBO:AlarmConfig:GeneralPowerLimHigh', 0, 0.0],  # [dBm]
    ['RA-ToBO:AlarmConfig:GeneralPowerLimLow', 0, 0.0],  # [dBm]
    ['RA-ToBO:AlarmConfig:GeneralPowerLimLoLo', 0, 0.0],  # [dBm]
    ['RA-ToBO:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],  # [dBm]
    ['RA-ToBO:AlarmConfig:InnerPowerLimHigh', 0, 0.0],  # [dBm]
    ['RA-ToBO:AlarmConfig:InnerPowerLimLow', 0, 0.0],  # [dBm]
    ['RA-ToBO:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],  # [dBm]
    # SSA tower current alarm limits
    ['RA-ToBO:AlarmConfig:CurrentLimHiHi', 0, 0.0],  # [A]
    ['RA-ToBO:AlarmConfig:CurrentLimHigh', 0, 0.0],  # [A]
    ['RA-ToBO:AlarmConfig:CurrentLimLow', 0, 0.0],  # [A]
    ['RA-ToBO:AlarmConfig:CurrentLimLoLo', 0, 0.0],  # [A]
    ]

_pvs_bo_rfcal = [
    ['RA-RaBO01:RF-LLRF:CavOffset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:CavSysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:CavSysCalInv-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:FwdCavOffset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FwdCavSysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:FwdCavSysCalInv-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:RevCavOffset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RevCavSysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:MOOffset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:MOSysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:FwdSSA1Offset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FwdSSA1SysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:FwdSSA1SysCalInv-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:RevSSA1Offset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RevSSA1SysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:Cell2Offset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Cell2SysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:Cell4Offset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Cell4SysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:Cell1Offset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Cell1SysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:Cell5Offset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Cell5SysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:InPre1AmpOffset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:InPre1AmpSysCal-SP', az, 0.0],


    ['RA-RaBO01:RF-LLRF:RevPreAmpOffset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RevPreAmpSysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:FwdCircOffset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:FwdCircSysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:RevCircOffset-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:RevCircSysCal-SP', az, 0.0],
    ['RA-RaBO01:RF-LLRF:AmpVCav2HwCoeff-SP', az, 0.0],
    ['BO-05D:RF-P5Cav:Rsh-Cte', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Hw2AmpVCavCoeff-SP', az, 0.0],
    # CalSys Offsets
    ['RA-RaBO01:RF-RFCalSys:OFSdB1-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB2-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB3-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB4-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB5-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB6-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB7-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB8-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB9-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB10-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB11-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB12-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB13-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB14-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB15-Mon', 0, 0.0],
    ['RA-RaBO01:RF-RFCalSys:OFSdB16-Mon', 0, 0.0]
]

_pvs_bo_pow_sensor = [
    #Keysight U2021xa Power Sensor config
    ['RA-RF:PowerSensor1:GainOffsetStat-Sel', 0, 0.0],
    ['RA-RF:PowerSensor1:GainOffset-SP', 0, 0.0],
    ['RA-RF:PowerSensor1:Egu-SP', 0, 0.0],
    ['RA-RF:PowerSensor1:TracTime-SP', 0, 0.0],
    ['RA-RF:PowerSensor1:Freq-SP', 0, 0.0],
    ]

##SIA PVs

_pvs_sia_llrf = [
    # Interlock disable
    ['RA-RaSIA01:RF-LLRF:FIMRevSSA1-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRevSSA2-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRevSSA3-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRevSSA4-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRevCav-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMManual-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMPLC-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMLLRF1-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMLLRF2-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMLLRF3-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMTunerHigh-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMTunerLow-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMPLG2Up-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMPLG2Down-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMCav-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMFwdCav-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMFwdSSA1-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRFIn7-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRFIn8-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRFIn9-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRFIn10-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRFIn11-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRFIn12-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRFIn13-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRFIn14-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMRFIn15-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMOrbitIntlk-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMQuenchCond1-Sts', 0, 0.0],
    # End switches logic
    ['RA-RaSIA01:RF-LLRF:EndSwLogicInv-Sel', 0, 0.0],
    # Beam trip logic
    ['RA-RaSIA01:RF-LLRF:OrbitIntlkLogicInv-Sel', 0, 0.0],
    # Vacuum sensor logic
    ['RA-RaSIA01:RF-LLRF:VacLogicInv-Sel', 0, 0.0],
    # Pwr interlock threshold
    ['RA-RaSIA01:RF-LLRF:LimRevSSA1-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRevSSA2-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRevSSA3-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRevSSA4-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRevCav-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimCav-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimFwdCav-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimFwdSSA1-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRFIn7-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRFIn8-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRFIn9-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRFIn10-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRFIn11-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRFIn12-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRFIn13-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRFIn14-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:LimRFIn15-SP', 0, 0.0],
    # Interlock delay
    ['RA-RaSIA01:RF-LLRF:IntlkDly-SP', 0, 0.0],
    # Set PVs value lims
    ['RA-RaSIA01:RF-LLRF:ALRef-SP.DRVH', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:ALRef-SP.DRVL', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:OLGain-SP.DRVH', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:OLGain-SP.DRVL', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:SLKP-SP.DRVH', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:SLKP-SP.DRVL', 0, 0.0],
    # Pressure Lock power increase
    ['RA-RaSIA01:RF-LLRF:CondAuto-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:EPSEnbl-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FIMEnbl-Sel', 0, 0.0],
    # ADC Phase and Gain
    ['RA-RaSIA01:RF-LLRF:PhShCav-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PhShFwdCav-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PhShFwdSSA1-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PhShFwdSSA2-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PhShFwdSSA3-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PhShFwdSSA4-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:GainFwdCav-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:GainFwdSSA1-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:GainFwdSSA2-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:GainFwdSSA3-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:GainFwdSSA4-SP', 0, 0.0],
    # DAC Phse and Gain
    ['RA-RaSIA01:RF-LLRF:PhShSSA1-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PhShSSA2-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PhShSSA3-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PhShSSA4-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:GainSSA1-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:GainSSA2-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:GainSSA3-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:GainSSA4-SP', 0, 0.0],
    # Loops parameters
    ['RA-RaSIA01:RF-LLRF:SLKP-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:SLKI-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:SLPILim-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:SLInp-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FLKP-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FLKI-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FLPILim-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FLInp-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:ALKP-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:ALKI-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:ALInp-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PLKP-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PLKI-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:PLInp-Sel', 0, 0.0],
    # Loop mode
    ['RA-RaSIA01:RF-LLRF:LoopMode-Sel', 0, 0.0],
    # Min forward power
    ['RA-RaSIA01:RF-LLRF:LoopFwdMin-SP', 0, 0.0],
    # Min amplitude reference
    ['RA-RaSIA01:RF-LLRF:AmpRefMin-SP', 0, 0.0],
    # Min phase reference
    ['RA-RaSIA01:RF-LLRF:PhsRefMin-SP', 0, 0.0],
    # Open loop gain
    ['RA-RaSIA01:RF-LLRF:OLGain-SP', 0, 0.0],
    # Phase ref
    ['RA-RaSIA01:RF-LLRF:PLRef-SP', 0, 0.0],
    # Tuning loop config
    ['RA-RaSIA01:RF-LLRF:Tune-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:TuneDir-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:TuneFwdMin-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:TuneMarginHI-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:TuneMarginLO-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:Detune-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:TuneDly-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:TuneFreq-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:TuneFilt-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:TuneTrig-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RmpTuneTop-Sel', 0, 0.0],
    # Rmp mode config
    ['RA-RaSIA01:RF-LLRF:RmpTs1-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RmpTs2-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RmpTs3-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RmpTs4-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RmpAmpTop-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RmpPhsTop-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RmpAmpBot-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RmpPhsBot-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RmpIncTime-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RmpDownDsbl-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FDLFrame-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FDLRearm-Sel', 0, 0.0],
    # Enable ADC phase and gain
    ['RA-RaSIA01:RF-LLRF:PhShADC-Sel', 0, 0.0],
    # Enable DAC phase and gain
    ['RA-RaSIA01:RF-LLRF:PhShDAC-Sel', 0, 0.0],
    # Dac5 outputs
    ['RA-RaSIA01:RF-LLRF:CavMonGain-Sel', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:CavMonCh-Sel', 0, 0.0],
    # Quench Condition
    ['RA-RaSIA01:RF-LLRF:QuenchCond1RvRatio-SP',0, 0.0],
    ['RA-RaSIA01:RF-LLRF:QuenchCond1Dly-SP',0, 0.0],
    # Dynamic Interlock setpoints
    ['RA-RaSIA01:RF-LLRF:CurrentDelta-SP', 0, 0.0],
    ["RA-RaSIA01:RF-LLRF:LimRevCavCoeff-SP", 0, 0.0],
    ["RA-RaSIA01:RF-LLRF:LimFwdCavCoeff-SP", 0, 0.0],
    ["RA-RaSIA01:RF-LLRF:QuenchCond1RvRatioCoeff-SP", 0, 0.0],
    ["RA-RaSIA01:RF-LLRF:LimRevCavOffset-SP", 0, 0.0],
    ["RA-RaSIA01:RF-LLRF:LimFwdCavOffset-SP", 0, 0.0],
    ["RA-RaSIA01:RF-LLRF:QuenchCond1RvRatioOffset-SP", 0, 0.0],
    ["RA-RaSIA01:RF-LLRF:LimRevCavEn-Sel", 0, 0.0],
    ["RA-RaSIA01:RF-LLRF:LimFwdCavEn-Sel", 0, 0.0],
    ["RA-RaSIA01:RF-LLRF:QuenchCond1RvRatioEn-Sel", 0, 0.0],
]

_pvs_sia_rfssa = [
    # NOTE: Alarms and offset of SSA towers 3 & 4 temporaly removed
    # SSA tower 1 offsets
    ['RA-ToSIA01:OffsetConfig:UpperIncidentPower', 0, 0.0],
    ['RA-ToSIA01:OffsetConfig:UpperReflectedPower', 0, 0.0],
    ['RA-ToSIA01:OffsetConfig:LowerIncidentPower', 0, 0.0],
    ['RA-ToSIA01:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # SSA tower 1 pwr alarm limits
    ['RA-ToSIA01:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    ['RA-ToSIA01:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    ['RA-ToSIA01:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    ['RA-ToSIA01:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # SSA tower 1 current alarm limits
    ['RA-ToSIA01:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    ['RA-ToSIA01:AlarmConfig:CurrentLimHigh', 0, 0.0],
    ['RA-ToSIA01:AlarmConfig:CurrentLimLow', 0, 0.0],
    ['RA-ToSIA01:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # SSA tower 2 offsets
    ['RA-ToSIA02:OffsetConfig:UpperIncidentPower', 0, 0.0],
    ['RA-ToSIA02:OffsetConfig:UpperReflectedPower', 0, 0.0],
    ['RA-ToSIA02:OffsetConfig:LowerIncidentPower', 0, 0.0],
    ['RA-ToSIA02:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # SSA tower 2 pwr alarm limits
    ['RA-ToSIA02:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    ['RA-ToSIA02:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    ['RA-ToSIA02:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    ['RA-ToSIA02:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # SSA tower 2 current alarm limits
    ['RA-ToSIA02:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    ['RA-ToSIA02:AlarmConfig:CurrentLimHigh', 0, 0.0],
    ['RA-ToSIA02:AlarmConfig:CurrentLimLow', 0, 0.0],
    ['RA-ToSIA02:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # # SSA tower 3 offsets
    # ['RA-ToSIA03:OffsetConfig:UpperIncidentPower', 0, 0.0],
    # ['RA-ToSIA03:OffsetConfig:UpperReflectedPower', 0, 0.0],
    # ['RA-ToSIA03:OffsetConfig:LowerIncidentPower', 0, 0.0],
    # ['RA-ToSIA03:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # # SSA tower 3 pwr alarm limits
    # ['RA-ToSIA03:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    # ['RA-ToSIA03:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    # ['RA-ToSIA03:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    # ['RA-ToSIA03:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # # SSA tower 3 current alarm limits
    # ['RA-ToSIA03:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    # ['RA-ToSIA03:AlarmConfig:CurrentLimHigh', 0, 0.0],
    # ['RA-ToSIA03:AlarmConfig:CurrentLimLow', 0, 0.0],
    # ['RA-ToSIA03:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # # SSA tower 4 offsets
    # ['RA-ToSIA04:OffsetConfig:UpperIncidentPower', 0, 0.0],
    # ['RA-ToSIA04:OffsetConfig:UpperReflectedPower', 0, 0.0],
    # ['RA-ToSIA04:OffsetConfig:LowerIncidentPower', 0, 0.0],
    # ['RA-ToSIA04:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # # SSA tower 4 pwr alarm limits
    # ['RA-ToSIA04:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    # ['RA-ToSIA04:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    # ['RA-ToSIA04:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    # ['RA-ToSIA04:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # # SSA tower 4 current alarm limits
    # ['RA-ToSIA04:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    # ['RA-ToSIA04:AlarmConfig:CurrentLimHigh', 0, 0.0],
    # ['RA-ToSIA04:AlarmConfig:CurrentLimLow', 0, 0.0],
    # ['RA-ToSIA04:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    #SSA1 Pwr Cal Coeff
    ['RA-ToSIA01:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    ['RA-ToSIA01:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    ['RA-ToSIA01:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    ['RA-ToSIA01:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    #SSA2 Pwr Cal Coeff
    ['RA-ToSIA02:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    ['RA-ToSIA02:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    ['RA-ToSIA02:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    ['RA-ToSIA02:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    # # SSA3 Pwr Cal Coeff
    # ['RA-ToSIA03:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    # ['RA-ToSIA03:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    # ['RA-ToSIA03:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    # ['RA-ToSIA03:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    # # SSA4 Pwr Cal Coeff
    # ['RA-ToSIA04:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    # ['RA-ToSIA04:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    # ['RA-ToSIA04:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    # ['RA-ToSIA04:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    ]

## Commented out temporarily in case we need to switch back to the Petra 7 cavity.
_pvs_sia_rfcav = [
#     # CavP7 water flow rate
#     ['SI-02SB:RF-P7Cav:Disc1FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Cell1FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Disc2FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Cell2FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Disc3FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Cell3FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Disc4FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Cell4FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Disc5FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Cell5FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Disc6FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Cell6FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Disc7FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Cell7FlwRt-Mon', 0, 0.0],  # [L/h]
#     ['SI-02SB:RF-P7Cav:Disc8FlwRt-Mon', 0, 0.0],  # [L/h]
    ]

_pvs_sia_rfcal = [
    ['RA-RaSIA01:RF-LLRF:CavOffset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:CavSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:CavSysCalInv-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdCavOffset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdCavSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdCavSysCalInv-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdLoadOffset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdLoadSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FBTntOffset-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FBTntSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdInCircOffset-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdInCircSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:RevInCircOffset-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:RevInCircSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdSSA1Offset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdSSA1SysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdSSA1SysCalInv-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdSSA2Offset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdSSA2SysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:FwdSSA2SysCalInv-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:In1PreAmpOffset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:In1PreAmpSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:In2PreAmpOffset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:In2PreAmpSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:MOOffset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:MOSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:RevCavOffset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RevCavSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:RevLoadOffset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RevLoadSysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:RevSSA1Offset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RevSSA1SysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:RevSSA2Offset-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:RevSSA2SysCal-SP', az, 0.0],
    ['RA-RaSIA01:RF-LLRF:AmpVCav2HwCoeff-SP', az, 0.0],
    ['SI-03SP:RF-SRFCav-A:Rsh-Cte', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB1-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB2-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB3-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB4-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB5-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB6-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB7-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB8-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB9-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB10-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB11-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB12-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB13-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB14-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB15-Mon', 0, 0.0],
    ['RA-RaSIA01:RF-RFCalSys:OFSdB16-Mon', 0, 0.0]
]

##SIB PVs

_pvs_sib_llrf = [
    # Interlock disable
    ['RA-RaSIB01:RF-LLRF:FIMRevSSA1-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRevSSA2-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRevSSA3-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRevSSA4-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRevCav-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMManual-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMPLC-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMLLRF1-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMLLRF2-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMLLRF3-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMTunerHigh-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMTunerLow-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMPLG2Up-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMPLG2Down-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMCav-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMFwdCav-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMFwdSSA1-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRFIn7-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRFIn8-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRFIn9-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRFIn10-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRFIn11-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRFIn12-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRFIn13-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRFIn14-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMRFIn15-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMOrbitIntlk-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMQuenchCond1-Sts', 0, 0.0],
    # End switches logic
    ['RA-RaSIB01:RF-LLRF:EndSwLogicInv-Sel', 0, 0.0],
    # Beam trip logic
    ['RA-RaSIB01:RF-LLRF:OrbitIntlkLogicInv-Sel', 0, 0.0],
    # Vacuum sensor logic
    ['RA-RaSIB01:RF-LLRF:VacLogicInv-Sel', 0, 0.0],
    # Pwr interlock threshold
    ['RA-RaSIB01:RF-LLRF:LimRevSSA1-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRevSSA2-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRevSSA3-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRevSSA4-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRevCav-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimCav-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimFwdCav-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimFwdSSA1-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRFIn7-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRFIn8-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRFIn9-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRFIn10-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRFIn11-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRFIn12-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRFIn13-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRFIn14-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:LimRFIn15-SP', 0, 0.0],
    # Interlock delay
    ['RA-RaSIB01:RF-LLRF:IntlkDly-SP', 0, 0.0],
    # Set PVs value lims
    ###Are we still saving this?
    ['RA-RaSIB01:RF-LLRF:ALRef-SP.DRVL', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:ALRef-SP.DRVH', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:OLGain-SP.DRVH', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:OLGain-SP.DRVL', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:SLKP-SP.DRVH', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:SLKP-SP.DRVL', 0, 0.0],
    # Pressure Lock power increase
    ['RA-RaSIB01:RF-LLRF:CondAuto-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:EPSEnbl-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FIMEnbl-Sel', 0, 0.0],
    # ADC Phase and Gain
    ['RA-RaSIB01:RF-LLRF:PhShCav-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PhShFwdCav-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PhShFwdSSA1-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PhShFwdSSA2-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PhShFwdSSA3-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PhShFwdSSA4-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:GainFwdCav-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:GainFwdSSA1-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:GainFwdSSA2-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:GainFwdSSA3-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:GainFwdSSA4-SP', 0, 0.0],
    # DAC Phse and Gain
    ['RA-RaSIB01:RF-LLRF:PhShSSA1-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PhShSSA2-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PhShSSA3-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PhShSSA4-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:GainSSA1-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:GainSSA2-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:GainSSA3-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:GainSSA4-SP', 0, 0.0],
    # Loops parameters
    ['RA-RaSIB01:RF-LLRF:SLKP-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:SLKI-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:SLPILim-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:SLInp-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FLKP-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FLKI-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FLPILim-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FLInp-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:ALKP-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:ALKI-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:ALInp-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PLKP-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PLKI-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:PLInp-Sel', 0, 0.0],
    # Loop mode
    ['RA-RaSIB01:RF-LLRF:LoopMode-Sel', 0, 0.0],
    # Min forward power
    ['RA-RaSIB01:RF-LLRF:LoopFwdMin-SP', 0, 0.0],
    # Min amplitude reference
    ['RA-RaSIB01:RF-LLRF:AmpRefMin-SP', 0, 0.0],
    # Min phase reference
    ['RA-RaSIB01:RF-LLRF:PhsRefMin-SP', 0, 0.0],
    # Open loop gain
    ['RA-RaSIB01:RF-LLRF:OLGain-SP', 0, 0.0],
    # Phase ref
    ['RA-RaSIB01:RF-LLRF:PLRef-SP', 0, 0.0],
    # Tuning loop config
    ['RA-RaSIB01:RF-LLRF:Tune-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:TuneDir-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:TuneFwdMin-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:TuneMarginHI-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:TuneMarginLO-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:Detune-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:TuneDly-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:TuneFreq-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:TuneFilt-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:TuneTrig-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RmpTuneTop-Sel', 0, 0.0],
    # Rmp mode config
    ['RA-RaSIB01:RF-LLRF:RmpTs1-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RmpTs2-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RmpTs3-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RmpTs4-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RmpAmpTop-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RmpPhsTop-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RmpAmpBot-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RmpPhsBot-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RmpIncTime-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RmpDownDsbl-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FDLFrame-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FDLRearm-Sel', 0, 0.0],
    # Enable ADC phase and gain
    ['RA-RaSIB01:RF-LLRF:PhShADC-Sel', 0, 0.0],
    # Enable DAC phase and gain
    ['RA-RaSIB01:RF-LLRF:PhShDAC-Sel', 0, 0.0],
    # DAC5 Output
    ['RA-RaSIB01:RF-LLRF:CavMonGain-Sel', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:CavMonCh-Sel', 0, 0.0],
    # Quench Condition
    ['RA-RaSIB01:RF-LLRF:QuenchCond1RvRatio-SP',0, 0.0],
    ['RA-RaSIB01:RF-LLRF:QuenchCond1Dly-SP',0, 0.0],
    # Dynamic Interlock setpoints
    ['RA-RaSIB01:RF-LLRF:CurrentDelta-SP', 0, 0.0],
    ["RA-RaSIB01:RF-LLRF:LimRevCavCoeff-SP", 0, 0.0],
    ["RA-RaSIB01:RF-LLRF:LimFwdCavCoeff-SP", 0, 0.0],
    ["RA-RaSIB01:RF-LLRF:QuenchCond1RvRatioCoeff-SP", 0, 0.0],
    ["RA-RaSIB01:RF-LLRF:LimRevCavOffset-SP", 0, 0.0],
    ["RA-RaSIB01:RF-LLRF:LimFwdCavOffset-SP", 0, 0.0],
    ["RA-RaSIB01:RF-LLRF:QuenchCond1RvRatioOffset-SP", 0, 0.0],
    ["RA-RaSIB01:RF-LLRF:LimRevCavEn-Sel", 0, 0.0],
    ["RA-RaSIB01:RF-LLRF:LimFwdCavEn-Sel", 0, 0.0],
    ["RA-RaSIB01:RF-LLRF:QuenchCond1RvRatioEn-Sel", 0, 0.0],
]

_pvs_sib_rfssa = [
    # SSA tower 1 offsets
    # ['RA-ToSIB01:OffsetConfig:UpperIncidentPower', 0, 0.0],
    # ['RA-ToSIB01:OffsetConfig:UpperReflectedPower', 0, 0.0],
    # ['RA-ToSIB01:OffsetConfig:LowerIncidentPower', 0, 0.0],
    # ['RA-ToSIB01:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # # SSA tower 1 pwr alarm limits
    # ['RA-ToSIB01:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    # ['RA-ToSIB01:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    # ['RA-ToSIB01:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    # ['RA-ToSIB01:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # # SSA tower 1 current alarm limits
    # ['RA-ToSIB01:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    # ['RA-ToSIB01:AlarmConfig:CurrentLimHigh', 0, 0.0],
    # ['RA-ToSIB01:AlarmConfig:CurrentLimLow', 0, 0.0],
    # ['RA-ToSIB01:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # # SSA tower 2 offsets
    # ['RA-ToSIB02:OffsetConfig:UpperIncidentPower', 0, 0.0],
    # ['RA-ToSIB02:OffsetConfig:UpperReflectedPower', 0, 0.0],
    # ['RA-ToSIB02:OffsetConfig:LowerIncidentPower', 0, 0.0],
    # ['RA-ToSIB02:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # # SSA tower 2 pwr alarm limits
    # ['RA-ToSIB02:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    # ['RA-ToSIB02:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    # ['RA-ToSIB02:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    # ['RA-ToSIB02:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # # SSA tower 2 current alarm limits
    # ['RA-ToSIB02:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    # ['RA-ToSIB02:AlarmConfig:CurrentLimHigh', 0, 0.0],
    # ['RA-ToSIB02:AlarmConfig:CurrentLimLow', 0, 0.0],
    # ['RA-ToSIB02:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # SSA tower 3 offsets
    ['RA-ToSIB03:OffsetConfig:UpperIncidentPower', 0, 0.0],
    ['RA-ToSIB03:OffsetConfig:UpperReflectedPower', 0, 0.0],
    ['RA-ToSIB03:OffsetConfig:LowerIncidentPower', 0, 0.0],
    ['RA-ToSIB03:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # SSA tower 3 pwr alarm limits
    ['RA-ToSIB03:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    ['RA-ToSIB03:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    ['RA-ToSIB03:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    ['RA-ToSIB03:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # SSA tower 3 current alarm limits
    ['RA-ToSIB03:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    ['RA-ToSIB03:AlarmConfig:CurrentLimHigh', 0, 0.0],
    ['RA-ToSIB03:AlarmConfig:CurrentLimLow', 0, 0.0],
    ['RA-ToSIB03:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # SSA tower 4 offsets
    ['RA-ToSIB04:OffsetConfig:UpperIncidentPower', 0, 0.0],
    ['RA-ToSIB04:OffsetConfig:UpperReflectedPower', 0, 0.0],
    ['RA-ToSIB04:OffsetConfig:LowerIncidentPower', 0, 0.0],
    ['RA-ToSIB04:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # SSA tower 4 pwr alarm limits
    ['RA-ToSIB04:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    ['RA-ToSIB04:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    ['RA-ToSIB04:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    ['RA-ToSIB04:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # SSA tower 4 current alarm limits
    ['RA-ToSIB04:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    ['RA-ToSIB04:AlarmConfig:CurrentLimHigh', 0, 0.0],
    ['RA-ToSIB04:AlarmConfig:CurrentLimLow', 0, 0.0],
    ['RA-ToSIB04:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # #SSA1 Pwr Cal Coeff
    # ['RA-ToSIB01:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    # ['RA-ToSIB01:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    # ['RA-ToSIB01:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    # ['RA-ToSIB01:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    # #SSA2 Pwr Cal Coeff
    # ['RA-ToSIB02:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    # ['RA-ToSIB02:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    # ['RA-ToSIB02:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    # ['RA-ToSIB02:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    # SSA3 Pwr Cal Coeff
    ['RA-ToSIB03:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    ['RA-ToSIB03:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    ['RA-ToSIB03:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    ['RA-ToSIB03:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    # SSA4 Pwr Cal Coeff
    ['RA-ToSIB04:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    ['RA-ToSIB04:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    ['RA-ToSIB04:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    ['RA-ToSIB04:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    ]

_pvs_sib_rfcav = []

_pvs_sib_rfcal = [
    ['RA-RaSIB01:RF-LLRF:CavOffset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:CavSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:CavSysCalInv-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdCavOffset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdCavSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdCavSysCalInv-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdLoadOffset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdLoadSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FBTntOffset-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FBTntSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdInCircOffset-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdInCircSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:RevInCircOffset-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:RevInCircSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdSSA1Offset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdSSA1SysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdSSA1SysCalInv-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdSSA2Offset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdSSA2SysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:FwdSSA2SysCalInv-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:In1PreAmpOffset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:In1PreAmpSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:In2PreAmpOffset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:In2PreAmpSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:MOOffset-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:MOSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:RevCavOffset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RevCavSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:RevLoadOffset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RevLoadSysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:RevSSA1Offset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RevSSA1SysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:RevSSA2Offset-SP', 0, 0.0],
    ['RA-RaSIB01:RF-LLRF:RevSSA2SysCal-SP', az, 0.0],
    ['RA-RaSIB01:RF-LLRF:AmpVCav2HwCoeff-SP', az, 0.0],
    ['SI-03SP:RF-SRFCav-B:Rsh-Cte', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB1-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB2-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB3-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB4-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB5-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB6-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB7-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB8-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB9-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB10-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB11-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB12-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB13-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB14-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB15-Mon', 0, 0.0],
    ['RA-RaSIB01:RF-RFCalSys:OFSdB16-Mon', 0, 0.0]
]

##
_template_dict = {
    'pvs':
    _pvs_as_rf + _pvs_li_llrf +
    _pvs_bo_pow_sensor + _pvs_bo_llrf + _pvs_bo_rfssa + _pvs_bo_rfcal +
    _pvs_sia_llrf + _pvs_sia_rfssa + _pvs_sia_rfcav + _pvs_sia_rfcal +
    _pvs_sib_llrf + _pvs_sib_rfssa + _pvs_sib_rfcav + _pvs_sib_rfcal
    }
