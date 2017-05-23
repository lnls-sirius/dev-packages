
import numpy as _np
import bib_status as _bib_status

#enums are limited to 25 characters

pvdb = {
    'SI-GLOB:AP-SOFB.OpMode': {'type': 'enum', 'enums': ['Off', 'AutoCorr', 'MeasRespMat']},
    'SI-GLOB:AP-SOFB.RespMatType': {'type': 'enum', 'enums': ['H', 'V', 'HV', 'HVCoup']},
    'SI-GLOB:AP-SOFB.RFreqEnbl': {'type': 'enum', 'enums': ['Off', 'On']},
    'SI-GLOB:AP-SOFB.ManCorrTrig': {'type': 'enum', 'enums': ['Off', 'On']},
    'SI-GLOB:AP-SOFB.AvgMeasOrbX': {'type': 'float', 'count': _bib_status.nBPM},
    'SI-GLOB:AP-SOFB.AvgMeasOrbY': {'type': 'float', 'count': _bib_status.nBPM},
    'SI-GLOB:AP-SOFB.NrSpl': {'type': 'int', 'value': 1},
    'SI-GLOB:AP-SOFB.Err': {'type': 'enum', 'enums': ['None', 'MeasRespmError', 'SetNumSamplesError', 'ReadOrbitError', 'SetRespmError', 'SetRefOrbitError', 'CorrOrbitError', 'SetRespmSlotError', 'SetRefOrbitSlotError', 'UpdateRespmError', 'UpdateRefOrbitError', 'DeviceSelError', 'KickThresholdError', 'WeightOutRangeError', 'SetModeParameter', 'StartManualCorrError', 'LockedRegisterError']}, #0-16
    'SI-GLOB:AP-SOFB.RespMatSlot': {'type': 'enum', 'enums': ['user_shift', 'slot1', 'slot2']},
    'SI-GLOB:AP-SOFB.RespMat': {'type': 'float', 'count': (_bib_status.nBPM*2)*(_bib_status.nCH+_bib_status.nCV+1)},
    'SI-GLOB:AP-SOFB.RefOrbXSlot': {'type': 'enum', 'enums': ['null', 'slot1', 'slot2']},
    'SI-GLOB:AP-SOFB.RefOrbYSlot': {'type': 'enum', 'enums': ['null', 'slot1', 'slot2']},
    'SI-GLOB:AP-SOFB.RefOrbX': {'type': 'float', 'count': _bib_status.nBPM},
    'SI-GLOB:AP-SOFB.RefOrbY': {'type': 'float', 'count': _bib_status.nBPM},
    'SI-GLOB:AP-SOFB.EnblListBPM': {'type': 'int', 'count': _bib_status.nBPM},
    'SI-GLOB:AP-SOFB.EnblListCH': {'type': 'int', 'count': _bib_status.nCH},
    'SI-GLOB:AP-SOFB.EnblListCV': {'type': 'int', 'count': _bib_status.nCV},
    'SI-GLOB:AP-SOFB.RmvBPM': {'type': 'string'},
    'SI-GLOB:AP-SOFB.AddBPM': {'type': 'string'},
    'SI-GLOB:AP-SOFB.RmvCH': {'type': 'string'},
    'SI-GLOB:AP-SOFB.AddCH': {'type': 'string'},
    'SI-GLOB:AP-SOFB.RmvCV': {'type': 'string'},
    'SI-GLOB:AP-SOFB.AddCV': {'type': 'string'},
    'SICO-BPM-DEVICENAMES': {'type': 'string', 'count': _bib_status.nBPM, 'value': _bib_status.devicenames_bpm},
    'SICO-CH-DEVICENAMES': {'type': 'string', 'count': _bib_status.nCH, 'value': _bib_status.devicenames_ch},
    'SICO-CV-DEVICENAMES': {'type': 'string', 'count': _bib_status.nCV, 'value': _bib_status.devicenames_cv},
    'SI-GLOB:AP-SOFB.StrthCH': {'type': 'float', 'value': 100, 'unit': '%', 'prec': 0},
    'SI-GLOB:AP-SOFB.StrthCV': {'type': 'float', 'value': 100, 'unit': '%', 'prec': 0},
}
