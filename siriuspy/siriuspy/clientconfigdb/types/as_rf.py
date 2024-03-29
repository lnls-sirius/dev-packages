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
    ['BR-RF-DLLRF-01:ILK:REVSSA1:S', 0.0, 0.0],
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
    # End switches logic
    ['BR-RF-DLLRF-01:SWITCHES:S', 0, 0.0],
    # Beam trip logic
    ['BR-RF-DLLRF-01:TRIPINVERT:S', 0, 0.0],
    # Vacuum sensor logic
    ['BR-RF-DLLRF-01:VACINVERT:S', 0, 0.0],
    # Pwr interlock threshold
    ['BR-RF-DLLRF-01:LIMIT:REVSSA1:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:REVSSA2:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:REVSSA3:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:REVSSA4:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:REVCAV:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:VCAV:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:FWCAV:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:FWSSA1:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:RFIN7:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:RFIN8:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:RFIN9:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:RFIN10:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:RFIN11:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:RFIN12:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:RFIN13:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:RFIN14:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:LIMIT:RFIN15:S', 0, 0.0],  # [mV]
    # Interlock delay
    ['BR-RF-DLLRF-01:ILK:DELAY:S', 0, 0.0],  # [μs]
    # Settings PVs values lims
    ['BR-RF-DLLRF-01:mV:AL:REF-SP.DRVH', 0, 0.0],
    ['BR-RF-DLLRF-01:mV:AL:REF-SP.DRVL', 0, 0.0],
    ['BR-RF-DLLRF-01:mV:RAMP:AMP:TOP-SP.DRVH', 0, 0.0],
    ['BR-RF-DLLRF-01:mV:RAMP:AMP:TOP-SP.DRVL', 0, 0.0],
    ['BR-RF-DLLRF-01:mV:RAMP:AMP:BOT-SP.DRVH', 0, 0.0],
    ['BR-RF-DLLRF-01:mV:RAMP:AMP:BOT-SP.DRVL', 0, 0.0],
    ['BR-RF-DLLRF-01:OLGAIN:S.DRVH', 0, 0.0],
    ['BR-RF-DLLRF-01:OLGAIN:S.DRVL', 0, 0.0],
    # kp limit high
    ['BR-RF-DLLRF-01:SL:KP:S.DRVH', 0, 0.0],
    # kp limit low
    ['BR-RF-DLLRF-01:SL:KP:S.DRVL', 0, 0.0],
    # Pressure threshold
    ['BO-05D:VA-CCG-RFC:FastRelay-SP', 0, 0.0],
    # Pressure Lock power increase
    ['BR-RF-DLLRF-01:AUTOCOND:S', 0, 0.0], 
    ['BR-RF-DLLRF-01:EPS:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FIM:S', 0, 0.0],
    # ADC Phase and Gain
    ['BR-RF-DLLRF-01:PHSH:CAV:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:PHSH:FWDCAV:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:PHSH:FWDSSA1:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:PHSH:FWDSSA2:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:PHSH:FWDSSA3:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:PHSH:FWDSSA4:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:GAIN:FWDCAV:S', 0, 0.0],
    ['BR-RF-DLLRF-01:GAIN:FWDSSA1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:GAIN:FWDSSA2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:GAIN:FWDSSA3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:GAIN:FWDSSA4:S', 0, 0.0],
    # DAC Phse and Gain
    ['BR-RF-DLLRF-01:PHSH:SSA1:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:PHSH:SSA2:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:PHSH:SSA3:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:PHSH:SSA4:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:GAIN:SSA1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:GAIN:SSA2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:GAIN:SSA3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:GAIN:SSA4:S', 0, 0.0],
    # Loops parameters
    ['BR-RF-DLLRF-01:SL:KP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:SL:KI:S', 0, 0.0],
    ['BR-RF-DLLRF-01:SL:PILIMIT:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:SL:SEL:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FL:KP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FL:KI:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FL:PILIMIT:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:FL:SEL:S', 0, 0.0],
    ['BR-RF-DLLRF-01:AL:KP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:AL:KI:S', 0, 0.0],
    ['BR-RF-DLLRF-01:AL:SEL:S', 0, 0.0],
    ['BR-RF-DLLRF-01:PL:KP:S', 0, 0.0],
    ['BR-RF-DLLRF-01:PL:KI:S', 0, 0.0],
    ['BR-RF-DLLRF-01:PL:SEL:S', 0, 0.0],
    # Loop mode
    ['BR-RF-DLLRF-01:MODE:S', 0, 0.0],
    # Min forward power
    ['BR-RF-DLLRF-01:FWMIN:AMPPHS:S', 0, 0.0],  # [mV]
    # Min amplitude ref
    ['BR-RF-DLLRF-01:mV:AMPREF:MIN:S', 0, 0.0],  # [mV]
    # Min phase ref
    ['BR-RF-DLLRF-01:PHSREF:MIN:S', 0, 0.0],  # [°]
    # Open loop gain
    ['BR-RF-DLLRF-01:OLGAIN:S', 0, 0.0],
    # Tuning loop config
    ['BR-RF-DLLRF-01:TUNE:POS:S', 0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:FWMIN:S', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:TUNE:MARGIN:HI:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:TUNE:MARGIN:LO:S', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:DTune-SP', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:TUNE:DELAY:S', 0, 0.0],  # [s]
    ['BR-RF-DLLRF-01:TUNE:PULSE:FREQ:S', 0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:FILT:S', 0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:TRIG:S', 0, 0.0],
    ['BR-RF-DLLRF-01:TUNE:TOPRAMP:S', 0, 0.0],
    # Field Flatness loop config
    ['BR-RF-DLLRF-01:FF:POS:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FF:DEADBAND:S', 0, 0.0],  # [%]
    ['BR-RF-DLLRF-01:FF:GAIN:CELL2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FF:GAIN:CELL4:S', 0, 0.0],
    # Pulsed mode config
    ['BR-RF-DLLRF-01:freq:cond:S', 0, 0.0],  # [Hz]
    ['BR-RF-DLLRF-01:freq:duty:S', 0, 0.0],  # [%]
    # Ramp mode config
    ['BR-RF-DLLRF-01:RmpTs1-SP', 0, 0.0],  # [ms]
    ['BR-RF-DLLRF-01:RmpTs2-SP', 0, 0.0],  # [ms]
    ['BR-RF-DLLRF-01:RmpTs3-SP', 0, 0.0],  # [ms]
    ['BR-RF-DLLRF-01:RmpTs4-SP', 0, 0.0],  # [ms]
    ['BR-RF-DLLRF-01:mV:RAMP:AMP:BOT-SP', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:RmpPhsBot-SP', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:mV:RAMP:AMP:TOP-SP', 0, 0.0],  # [mV]
    ['BR-RF-DLLRF-01:RmpPhsTop-SP', 0, 0.0],  # [°]
    ['BR-RF-DLLRF-01:RmpIncTs-SP', 0, 0.0],  # [min]
    ['BR-RF-DLLRF-01:DisableRampDown:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FDL:FrameQty-SP', 0, 0.0],
    ['BR-RF-DLLRF-01:FDL:REARM', 0, 0.0],
    # Enable plungers step motor drivers
    ['RA-RaBO01:RF-CavPlDrivers:DrEnbl-Sel', 0, 0.0],
    # Enable ADC phase and gain
    ['BR-RF-DLLRF-01:PHSH:ADC:S', 0, 0.0],
    # Enable DAC phase and gain
    ['BR-RF-DLLRF-01:PHSH:DAC:S', 0, 0.0],
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
    # Offsets and conv coeffs
    ['BR-RF-DLLRF-01:CAV:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:CAV:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:U-Raw:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:U-Raw:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:U-Raw:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:U-Raw:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CAV:Const:U-Raw:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:REVCAV:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVCAV:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:MO:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:MO:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:CELL2:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL2:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:CELL4:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL4:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:CELL1:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL1:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:CELL5:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:CELL5:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:INPRE:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:INPRE:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:FWDPRE:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDPRE:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:REVPRE:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVPRE:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:OFS:S', 0, 0.0], # [dB]
    ['BR-RF-DLLRF-01:REVCIRC:Const:Raw-U:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:Raw-U:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:Raw-U:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:Raw-U:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:REVCIRC:Const:Raw-U:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:CAV:Const:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:CAV:Const:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:CAV:Const:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:CAV:Const:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:CAV:Const:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDCAV:Const:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDCAV:Const:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDCAV:Const:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDCAV:Const:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDCAV:Const:C4:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA1:Const:C0:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA1:Const:C1:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA1:Const:C2:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA1:Const:C3:S', 0, 0.0],
    ['BR-RF-DLLRF-01:OLG:FWDSSA1:Const:C4:S', 0, 0.0],
    # Conv coeffs for gap voltage calc
    ['RA-RaBO01:RF-LLRF:AmpVCav2HwCoeff0-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:AmpVCav2HwCoeff1-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:AmpVCav2HwCoeff2-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:AmpVCav2HwCoeff3-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:AmpVCav2HwCoeff4-SP', 0, 0.0],
    # Cavity Shunt impedance
    ['BO-05D:RF-P5Cav:Rsh-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Hw2AmpVCavCoeff0-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Hw2AmpVCavCoeff1-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Hw2AmpVCavCoeff2-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Hw2AmpVCavCoeff3-SP', 0, 0.0],
    ['RA-RaBO01:RF-LLRF:Hw2AmpVCavCoeff4-SP', 0, 0.0],
    # CalSys Offsets
    ['RA-RaBO01:RF-RFCalSys:OFSdB1-Mon', 0, 0.0], # [dB]
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
    ['RA-RaBO01:RF-RFCalSys:OFSdB16-Mon', 0, 0.0],
    ]


_pvs_bo_pow_sensor = [
    #Keysight U2021xa Power Sensor config
    ['RA-RF:PowerSensor1:GainOffsetStat-Sel', 0, 0.0],
    ['RA-RF:PowerSensor1:GainOffset-SP', 0, 0.0],
    ['RA-RF:PowerSensor1:Egu-SP', 0, 0.0],
    ['RA-RF:PowerSensor1:TracTime-SP', 0, 0.0],
    ['RA-RF:PowerSensor1:Freq-SP', 0, 0.0],
    ]


_pvs_si_llrf = [
    # Interlock disable
    ['SR-RF-DLLRF-01:ILK:REVSSA1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:REVSSA2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:REVSSA3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:REVSSA4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:REVCAV:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:MAN:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:PLC:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:LLRF1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:LLRF2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:LLRF3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:PLG1:UP:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:PLG1:DN:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:PLG2:UP:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:PLG2:DN:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:VCAV:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:FWCAV:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:FWSSA1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:RFIN7:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:RFIN8:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:RFIN9:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:RFIN10:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:RFIN11:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:RFIN12:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:RFIN13:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:RFIN14:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:RFIN15:S', 0, 0.0],
    ['SR-RF-DLLRF-01:ILK:BEAM:TRIP:S', 0, 0.0],
    # End switches logic
    ['SR-RF-DLLRF-01:SWITCHES:S', 0, 0.0],
    # Beam trip logic
    ['SR-RF-DLLRF-01:TRIPINVERT:S', 0, 0.0],
    # Vacuum sensor logic
    ['SR-RF-DLLRF-01:VACINVERT:S', 0, 0.0],
    # Pwr interlock threshold
    ['SR-RF-DLLRF-01:LIMIT:REVSSA1:S', 0, 0.0],  # [mV] 
    ['SR-RF-DLLRF-01:LIMIT:REVSSA2:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:REVSSA3:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:REVSSA4:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:REVCAV:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:VCAV:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:FWCAV:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:FWSSA1:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:RFIN7:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:RFIN8:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:RFIN9:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:RFIN10:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:RFIN11:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:RFIN12:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:RFIN13:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:RFIN14:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:LIMIT:RFIN15:S', 0, 0.0],  # [mV]
    # Interlock delay
    ['SR-RF-DLLRF-01:ILK:DELAY:S', 0, 0.0],  # [μs] 
    # Set PVs value lims
    ['SR-RF-DLLRF-01:mV:AL:REF-SP.DRVH', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:mV:AL:REF-SP.DRVL', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:OLGAIN:S.DRVH', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:OLGAIN:S.DRVL', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:SL:KP:S.DRVH', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:SL:KP:S.DRVL', 0, 0.0],  # [mV]
    # Pressure Lock power increase
    ['SR-RF-DLLRF-01:AUTOCOND:S', 0, 0.0],
    ['SR-RF-DLLRF-01:EPS:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FIM:S', 0, 0.0],
    # ADC Phase and Gain
    ['SR-RF-DLLRF-01:PHSH:CAV:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:PHSH:FWDCAV:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:PHSH:FWDSSA1:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:PHSH:FWDSSA2:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:PHSH:FWDSSA3:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:PHSH:FWDSSA4:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:GAIN:FWDCAV:S', 0, 0.0],
    ['SR-RF-DLLRF-01:GAIN:FWDSSA1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:GAIN:FWDSSA2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:GAIN:FWDSSA3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:GAIN:FWDSSA4:S', 0, 0.0],
    # DAC Phse and Gain
    ['SR-RF-DLLRF-01:PHSH:SSA1:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:PHSH:SSA2:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:PHSH:SSA3:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:PHSH:SSA4:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:GAIN:SSA1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:GAIN:SSA2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:GAIN:SSA3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:GAIN:SSA4:S', 0, 0.0],
    # Loops parameters
    ['SR-RF-DLLRF-01:SL:KP:S', 0, 0.0],
    ['SR-RF-DLLRF-01:SL:KI:S', 0, 0.0],
    ['SR-RF-DLLRF-01:SL:PILIMIT:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:SL:SEL:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FL:KP:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FL:KI:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FL:PILIMIT:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:FL:SEL:S', 0, 0.0],
    ['SR-RF-DLLRF-01:AL:KP:S', 0, 0.0],
    ['SR-RF-DLLRF-01:AL:KI:S', 0, 0.0],
    ['SR-RF-DLLRF-01:AL:SEL:S', 0, 0.0],
    ['SR-RF-DLLRF-01:PL:KP:S', 0, 0.0],
    ['SR-RF-DLLRF-01:PL:KI:S', 0, 0.0],
    ['SR-RF-DLLRF-01:PL:SEL:S', 0, 0.0],
    # Loop mode
    ['SR-RF-DLLRF-01:MODE:S', 0, 0.0],
    # Min forward power
    ['SR-RF-DLLRF-01:FWMIN:AMPPHS:S', 0, 0.0],  # [mV]
    # Min amplitude reference
    ['SR-RF-DLLRF-01:mV:AMPREF:MIN:S', 0, 0.0],  # [mV]
    # Min phase reference
    ['SR-RF-DLLRF-01:PHSREF:MIN:S', 0, 0.0],  # [°]
    # Open loop gain
    ['SR-RF-DLLRF-01:OLGAIN:S', 0, 0.0],
    # Phase ref
    ['SR-RF-DLLRF-01:PL:REF:S', 0, 0.0],  # [°]
    # Tuning loop config
    ['SR-RF-DLLRF-01:TUNE:POS:S', 0, 0.0],
    ['SR-RF-DLLRF-01:TUNE:FWMIN:S', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:TUNE:MARGIN:HI:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:TUNE:MARGIN:LO:S', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:DTune-SP', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:TUNE:DELAY:S', 0, 0.0],  # [s]
    ['SR-RF-DLLRF-01:TUNE:PULSE:FREQ:S', 0, 0.0],
    ['SR-RF-DLLRF-01:TUNE:FILT:S', 0, 0.0],
    ['SR-RF-DLLRF-01:TUNE:TRIG:S', 0, 0.0],
    ['SR-RF-DLLRF-01:TUNE:TOPRAMP:S', 0, 0.0],
    # Field Flatness loop config
    ['SR-RF-DLLRF-01:FF:POS:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FF:DEADBAND:S', 0, 0.0],  # [%]
    ['SR-RF-DLLRF-01:FF:GAIN:CELL2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FF:GAIN:CELL4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:COND:DC:S', 0, 0.0],  # [%]
    # Ramp mode config
    ['SR-RF-DLLRF-01:RmpTs1-SP', 0, 0.0],  # [ms]
    ['SR-RF-DLLRF-01:RmpTs2-SP', 0, 0.0],  # [ms]
    ['SR-RF-DLLRF-01:RmpTs3-SP', 0, 0.0],  # [ms]
    ['SR-RF-DLLRF-01:RmpTs4-SP', 0, 0.0],  # [ms]
    ['SR-RF-DLLRF-01:mV:RAMP:AMP:TOP-SP', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:RmpPhsTop-SP', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:mV:RAMP:AMP:BOT-SP', 0, 0.0],  # [mV]
    ['SR-RF-DLLRF-01:RmpPhsBot-SP', 0, 0.0],  # [°]
    ['SR-RF-DLLRF-01:RmpIncTs-SP', 0, 0.0],  # [min]
    ['SR-RF-DLLRF-01:DisableRampDown:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FDL:FrameQty-SP', 0, 0.0],
    ['SR-RF-DLLRF-01:FDL:REARM', 0, 0.0],
    # Enable ADC phase and gain
    ['SR-RF-DLLRF-01:PHSH:ADC:S', 0, 0.0],
    # Enable DAC phase and gain
    ['SR-RF-DLLRF-01:PHSH:DAC:S', 0, 0.0],
    ]


_pvs_si_rfssa = [
    # NOTE: Alarms and offset of SSA towers 1 & 2 temporaly removed
    # SSA tower 1 offsets
    # ['RA-ToSIA01:OffsetConfig:UpperIncidentPower', 0, 0.0],
    # ['RA-ToSIA01:OffsetConfig:UpperReflectedPower', 0, 0.0],
    # ['RA-ToSIA01:OffsetConfig:LowerIncidentPower', 0, 0.0],
    # ['RA-ToSIA01:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # SSA tower 1 pwr alarm limits
    # ['RA-ToSIA01:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    # ['RA-ToSIA01:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    # ['RA-ToSIA01:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    # ['RA-ToSIA01:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # SSA tower 1 current alarm limits
    # ['RA-ToSIA01:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    # ['RA-ToSIA01:AlarmConfig:CurrentLimHigh', 0, 0.0],
    # ['RA-ToSIA01:AlarmConfig:CurrentLimLow', 0, 0.0],
    # ['RA-ToSIA01:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # SSA tower 2 offsets
    # ['RA-ToSIA02:OffsetConfig:UpperIncidentPower', 0, 0.0],
    # ['RA-ToSIA02:OffsetConfig:UpperReflectedPower', 0, 0.0],
    # ['RA-ToSIA02:OffsetConfig:LowerIncidentPower', 0, 0.0],
    # ['RA-ToSIA02:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # SSA tower 2 pwr alarm limits
    # ['RA-ToSIA02:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    # ['RA-ToSIA02:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    # ['RA-ToSIA02:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    # ['RA-ToSIA02:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # SSA tower 2 current alarm limits
    # ['RA-ToSIA02:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    # ['RA-ToSIA02:AlarmConfig:CurrentLimHigh', 0, 0.0],
    # ['RA-ToSIA02:AlarmConfig:CurrentLimLow', 0, 0.0],
    # ['RA-ToSIA02:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # SSA tower 3 offsets
    ['RA-ToSIA03:OffsetConfig:UpperIncidentPower', 0, 0.0],
    ['RA-ToSIA03:OffsetConfig:UpperReflectedPower', 0, 0.0],
    ['RA-ToSIA03:OffsetConfig:LowerIncidentPower', 0, 0.0],
    ['RA-ToSIA03:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # SSA tower 3 pwr alarm limits
    ['RA-ToSIA03:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    ['RA-ToSIA03:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    ['RA-ToSIA03:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    ['RA-ToSIA03:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # SSA tower 3 current alarm limits
    ['RA-ToSIA03:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    ['RA-ToSIA03:AlarmConfig:CurrentLimHigh', 0, 0.0],
    ['RA-ToSIA03:AlarmConfig:CurrentLimLow', 0, 0.0],
    ['RA-ToSIA03:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # SSA tower 4 offsets
    ['RA-ToSIA04:OffsetConfig:UpperIncidentPower', 0, 0.0],
    ['RA-ToSIA04:OffsetConfig:UpperReflectedPower', 0, 0.0],
    ['RA-ToSIA04:OffsetConfig:LowerIncidentPower', 0, 0.0],
    ['RA-ToSIA04:OffsetConfig:LowerReflectedPower', 0, 0.0],
    # SSA tower 4 pwr alarm limits
    ['RA-ToSIA04:AlarmConfig:InnerPowerLimHiHi', 0, 0.0],
    ['RA-ToSIA04:AlarmConfig:InnerPowerLimHigh', 0, 0.0],
    ['RA-ToSIA04:AlarmConfig:InnerPowerLimLow', 0, 0.0],
    ['RA-ToSIA04:AlarmConfig:InnerPowerLimLoLo', 0, 0.0],
    # SSA tower 4 current alarm limits
    ['RA-ToSIA04:AlarmConfig:CurrentLimHiHi', 0, 0.0],
    ['RA-ToSIA04:AlarmConfig:CurrentLimHigh', 0, 0.0],
    ['RA-ToSIA04:AlarmConfig:CurrentLimLow', 0, 0.0],
    ['RA-ToSIA04:AlarmConfig:CurrentLimLoLo', 0, 0.0],
    # SSA1 Pwr Cal Coeff
    # ['RA-ToSIA01:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    # ['RA-ToSIA01:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    # ['RA-ToSIA01:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    # ['RA-ToSIA01:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    # SSA2 Pwr Cal Coeff
    # ['RA-ToSIA02:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    # ['RA-ToSIA02:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    # ['RA-ToSIA02:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    # ['RA-ToSIA02:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    # SSA3 Pwr Cal Coeff
    ['RA-ToSIA03:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    ['RA-ToSIA03:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    ['RA-ToSIA03:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    ['RA-ToSIA03:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    # SSA4 Pwr Cal Coeff
    ['RA-ToSIA04:RF-SSAmpTower:Hw2PwrFwdInCoeff-Cte', az, 0.0],
    ['RA-ToSIA04:RF-SSAmpTower:Hw2PwrRevInCoeff-Cte', az, 0.0],
    ['RA-ToSIA04:RF-SSAmpTower:Hw2PwrFwdOutCoeff-Cte', az, 0.0],
    ['RA-ToSIA04:RF-SSAmpTower:Hw2PwrRevOutCoeff-Cte', az, 0.0],
    ]


_pvs_si_rfcav = [
    # CavP7 water flow rate
    ['SI-02SB:RF-P7Cav:Disc1FlwRt-Mon', 0, 0.0],  # [L/h] 
    ['SI-02SB:RF-P7Cav:Cell1FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Disc2FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Cell2FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Disc3FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Cell3FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Disc4FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Cell4FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Disc5FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Cell5FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Disc6FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Cell6FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Disc7FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Cell7FlwRt-Mon', 0, 0.0],  # [L/h]
    ['SI-02SB:RF-P7Cav:Disc8FlwRt-Mon', 0, 0.0],  # [L/h]
    ]


_pvs_si_rfcal = [
    # Offsets and conv coeffs
    ['SR-RF-DLLRF-01:CAV:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:CAV:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CAV:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CAV:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CAV:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CAV:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CAV:Const:U-Raw:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CAV:Const:U-Raw:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CAV:Const:U-Raw:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CAV:Const:U-Raw:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CAV:Const:U-Raw:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCAV:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCAV:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCAV:Const:U-Raw:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVCAV:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:REVCAV:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVCAV:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVCAV:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVCAV:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVCAV:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:MO:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:MO:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:MO:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:MO:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:MO:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:MO:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA1:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA1:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA1:Const:U-Raw:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVSSA1:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVSSA1:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CELL2:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:CELL2:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CELL2:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CELL2:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CELL2:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CELL2:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CELL6:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:CELL6:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CELL6:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CELL6:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CELL6:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:CELL6:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA2:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:FWDSSA2:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA2:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA2:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA2:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDSSA2:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVSSA2:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:REVSSA2:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVSSA2:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVSSA2:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVSSA2:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:REVSSA2:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:INPRE1:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:INPRE1:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:INPRE1:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:INPRE1:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:INPRE1:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:INPRE1:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDPRE1:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:FWDPRE1:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDPRE1:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDPRE1:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDPRE1:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDPRE1:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:INPRE2:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:INPRE2:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:INPRE2:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:INPRE2:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:INPRE2:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:INPRE2:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDPRE2:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:FWDPRE2:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDPRE2:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDPRE2:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDPRE2:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDPRE2:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCIRC:Const:OFS:S', 0, 0.0],  # [dB]
    ['SR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:FWDCIRC:Const:Raw-U:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:CAV:Const:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:CAV:Const:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:CAV:Const:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:CAV:Const:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:CAV:Const:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:FWDCAV:Const:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:FWDCAV:Const:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:FWDCAV:Const:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:FWDCAV:Const:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:FWDCAV:Const:C4:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:FWDSSA1:Const:C0:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:FWDSSA1:Const:C1:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:FWDSSA1:Const:C2:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:FWDSSA1:Const:C3:S', 0, 0.0],
    ['SR-RF-DLLRF-01:OLG:FWDSSA1:Const:C4:S', 0, 0.0],
    # Conv coeffs for gap voltage calc
    ['RA-RaSIA01:RF-LLRF:AmpVCav2HwCoeff0-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:AmpVCav2HwCoeff1-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:AmpVCav2HwCoeff2-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:AmpVCav2HwCoeff3-SP', 0, 0.0],
    ['RA-RaSIA01:RF-LLRF:AmpVCav2HwCoeff4-SP', 0, 0.0],
    # Cavity Shunt impedance
    ['SI-02SB:RF-P7Cav:Rsh-SP', 0, 0.0],  # [Ohm]
    # CalSys Offsets
    ['RA-RaSIA01:RF-RFCalSys:OFSdB1-Mon', 0, 0.0], # [dB]
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
    ['RA-RaSIA01:RF-RFCalSys:OFSdB16-Mon', 0, 0.0],
    ]


_template_dict = {
    'pvs':
    _pvs_as_rf + _pvs_li_llrf + 
    _pvs_bo_pow_sensor + _pvs_bo_llrf + _pvs_bo_rfssa + _pvs_bo_rfcal +
    _pvs_si_llrf + _pvs_si_rfssa + _pvs_si_rfcav + _pvs_si_rfcal
    }
    