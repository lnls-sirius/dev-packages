"""Define the PV database of a single BPM and its enum types."""
from copy import deepcopy as _dcopy
import numpy as _np

from ... import csdev as _csdev


# --- Enumeration Types ---
class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    TRIGDIR = ('trn', 'rcv')
    TRIGDIRPOL = ('same', 'rev')
    TRIGSRC = ('ext', 'int')
    TRIGEXTERN = (
        'UserDefined', 'BeamLossIn', 'BeamLossOut', 'OrbitInterlock',
        'StorageRingTbTClk', 'BoosterTbTClk', 'FOFBClk', 'Reserved')
    TRIGINTERN = ('FMCTrigIn', 'DSPSWClk')
    LOGTRIGINTERN = (
        'ADC', 'ADCSwap', 'MixerIQ', 'Unconnected', 'TbTIQ',
        'Unconnected2', 'TbTAmp', 'TbTPha', 'TbTPos', 'FOFBIQ',
        'Unconnected3', 'FOFBAmp', 'FOFBPha', 'FOFBPos', 'MonitAmp',
        'MonitPos', 'FAcqPos', 'FMCTrigOut', 'Unconnected4', 'Unconnected5',
        'Unconnected6', 'Unconnected7', 'Unconnected8', 'Unconnected9')
    SWMODES = ('rffe_switching', 'direct', 'inverted', 'switching')
    SWTAGENBL = ('disabled', 'enabled')
    FOFBDATAMASKENBL = ('disabled', 'enabled')

    POLARITY = ('Positive', 'Negative')
    ENBLTYP = ('Disable', 'Enable')
    DSBLDENBLD = ('disabled', 'enabled')
    CONNTYP = _csdev.ETypes.DISCONN_CONN
    ACQREPEAT = ('Normal', 'Repetitive')
    ACQEVENTS = ('Start', 'Stop')
    ACQDATATYP = ('A', 'B', 'C', 'D')
    ACQCHAN = ('ADC', 'ADCSwp', 'TbT', 'TbTPha', 'FOFB', 'FOFBPha', 'FAcq')
    ACQSTATES = (
        'Idle', 'Waiting', 'External Trig', 'Data Trig', 'Software Trig',
        'Acquiring', 'Error', 'Bad Post Samples', 'Too Many Samples',
        'No Samples', 'No Memory', 'Overflow')
    ACQTRIGTYP = ('Now', 'External', 'Data', 'Software')


_et = ETypes  # syntactic sugar


# --- Const class ---
class Const(_csdev.Const):
    """Const class defining BPM constants."""

    TrigDir = _csdev.Const.register('TrigDir', _et.TRIGDIR)
    TrigDirPol = _csdev.Const.register('TrigDirPol', _et.TRIGDIRPOL)
    TrigSrc = _csdev.Const.register('TrigSrc', _et.TRIGSRC)
    TrigExtern = _csdev.Const.register('TrigExtern', _et.TRIGEXTERN)
    TrigIntern = _csdev.Const.register('TrigIntern', _et.TRIGINTERN)
    LogTrigIntern = _csdev.Const.register('LogTrigIntern', _et.LOGTRIGINTERN)
    SwModes = _csdev.Const.register('SwModes', _et.SWMODES)
    SwPhaseSyncEnbl = _csdev.Const.register('SwPhaseSyncEnbl', _et.SWTAGENBL)
    FOFBDataMaskEnbl = _csdev.Const.register(
        'FOFBDataMaskEnbl', _et.FOFBDATAMASKENBL)
    Polarity = _csdev.Const.register('Polarity', _et.POLARITY)
    EnblTyp = _csdev.Const.register('EnblTyp', _et.ENBLTYP)
    DsblEnbl = _csdev.Const.register('DsblEnbl', _et.DSBLDENBLD)
    ConnTyp = _csdev.Const.register('ConnTyp', _et.CONNTYP)
    AcqRepeat = _csdev.Const.register('AcqRepeat', _et.ACQREPEAT)
    AcqEvents = _csdev.Const.register('AcqEvents', _et.ACQEVENTS)
    AcqDataTyp = _csdev.Const.register('AcqDataTyp', _et.ACQDATATYP)
    AcqChan = _csdev.Const.register('AcqChan', _et.ACQCHAN)
    AcqStates = _csdev.Const.register('AcqStates', _et.ACQSTATES)
    AcqTrigTyp = _csdev.Const.register('AcqTrigTyp', _et.ACQTRIGTYP)

    @staticmethod
    def get_bpm_database(prefix=''):
        """Get the PV database of a single BPM."""
        data_db = {'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
        dbase = {
            'INFOFOFBRate-SP': {
                'type': 'int', 'value': 1910, 'low': 0, 'high': 2**31-1},
            'INFOFOFBRate-RB': {
                'type': 'int', 'value': 1910, 'low': 0, 'high': 2**31-1},
            'INFOHarmonicNumber-SP': {
                'type': 'int', 'value': 864, 'low': 0, 'high': 2**31-1},
            'INFOHarmonicNumber-RB': {
                'type': 'int', 'value': 864, 'low': 0, 'high': 2**31-1},
            'INFOMONITRate-SP': {
                'type': 'int', 'value': 21965000, 'low': 0, 'high': 2**31-1},
            'INFOMONITRate-RB': {
                'type': 'int', 'value': 21965000, 'low': 0, 'high': 2**31-1},
            'INFOFAcqRate-SP': {
                'type': 'int', 'value': 21965000, 'low': 0, 'high': 2**31-1},
            'INFOFAcqRate-RB': {
                'type': 'int', 'value': 21965000, 'low': 0, 'high': 2**31-1},
            'INFOTbTRate-SP': {
                'type': 'int', 'value': 382, 'low': 0, 'high': 2**31-1},
            'INFOTbTRate-RB': {
                'type': 'int', 'value': 382, 'low': 0, 'high': 2**31-1},
            }

        # PHYSICAL TRIGGERS
        for i in range(8):
            trig = 'TRIGGER{0:d}'.format(i)
            dbase.update(Const.get_physical_trigger_database(trig))

        # LOGICAL TRIGGERS
        for trig_tp in ('_GEN', '_PM'):
            for i in range(24):
                trig = 'TRIGGER' + trig_tp + '{0:d}'.format(i)
                dbase.update(Const.get_logical_trigger_database(trig))

        # AMPLITUDES AND POSITION CHANNELS
        dbase.update(Const.get_amplitudes_database())

        # SETTINGS AND STATUS
        dbase.update(Const.get_offsets_database())
        dbase.update(Const.get_gain_database())
        dbase.update(Const.get_rffe_database())
        dbase.update(Const.get_switch_database())
        dbase.update(Const.get_monit_database())

        data_names = {
            'GEN': [
                'AmplA', 'AmplB', 'AmplC', 'AmplD',
                'PosQ', 'Sum', 'PosX', 'PosY'
            ],
            'PM': [
                'AmplA', 'AmplB', 'AmplC', 'AmplD',
                'PosQ', 'Sum', 'PosX', 'PosY'
            ],
            }
        data_db = {
            'type': 'float', 'value': _np.array(100000*[0.0]), 'count': 100000}

        # ARRAY DATA FROM TRIGGERED ACQUISITIONS
        for acq_tp in ('GEN', 'PM'):
            for prop in data_names[acq_tp]:
                nm = acq_tp + prop
                dbase[nm + 'Data'] = _dcopy(data_db)

        # TRIGGERED ACQUISITIONS CONFIGURATION
        for acq_md in ('GEN', 'PM'):
            dbase.update(Const.get_config_database(acq_md))

        for _, v in dbase.items():
            if 'low' in v:
                v['lolo'] = v['low']
                v['lolim'] = v['low']
            if 'high' in v:
                v['hihi'] = v['high']
                v['hilim'] = v['high']

        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_asyn_database(prefix=''):
        """."""
        dbase = {
            'asyn.ENBL': {
                'type': 'enum', 'enums': Const.EnblTyp._fields, 'value': 0},
            'asyn.CNCT': {
                'type': 'enum', 'enums': Const.ConnTyp._fields, 'value': 0},
            }
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_rffe_database(prefix=''):
        """."""
        prefix = prefix + 'RFFE'
        dbase = {
            'Att-SP': {
                'type': 'float', 'value': 0, 'unit': 'dB',
                'low': 0, 'high': 100},
            'Att-RB': {
                'type': 'float', 'value': 0, 'unit': 'dB',
                'low': 0, 'high': 100},
            'PidSpAC-SP': {
                'type': 'float', 'value': 0, 'unit': 'oC',
                'low': 0, 'high': 100},
            'PidSpAC-RB': {
                'type': 'float', 'value': 0, 'unit': 'oC',
                'low': 0, 'high': 100},
            'PidSpBD-SP': {
                'type': 'float', 'value': 0, 'unit': 'oC',
                'low': 0, 'high': 100},
            'PidSpBD-RB': {
                'type': 'float', 'value': 0, 'unit': 'oC',
                'low': 0, 'high': 100},
            'HeaterAC-SP': {
                'type': 'float', 'value': 0, 'unit': 'V',
                'low': 0, 'high': 100},
            'HeaterAC-RB': {
                'type': 'float', 'value': 0, 'unit': 'V',
                'low': 0, 'high': 100},
            'HeaterBD-SP': {
                'type': 'float', 'value': 0, 'unit': 'V',
                'low': 0, 'high': 100},
            'HeaterBD-RB': {
                'type': 'float', 'value': 0, 'unit': 'V',
                'low': 0, 'high': 100},
            'PidACKp-SP': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidACKp-RB': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidBDKp-SP': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidBDKp-RB': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidACTi-SP': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidACTi-RB': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidBDTi-SP': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidBDTi-RB': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidACTd-SP': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidACTd-RB': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidBDTd-SP': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            'PidBDTd-RB': {
                'type': 'float', 'value': 0, 'low': 0, 'high': 100},
            }
        dbase.update(Const.get_asyn_database())
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_switch_database(prefix=''):
        """."""
        dbase = {
            'SwMode-Sel': {
                'type': 'enum', 'enums': Const.SwModes._fields, 'value': 3},
            'SwMode-Sts': {
                'type': 'enum', 'enums': Const.SwModes._fields, 'value': 3},
            'SwPhaseSyncEn-Sel': {
                'type': 'enum', 'enums': Const.SwPhaseSyncEnbl._fields,
                'value': 0},
            'SwPhaseSyncEn-Sts': {
                'type': 'enum', 'enums': Const.SwPhaseSyncEnbl._fields,
                'value': 0},
            'SwDeswapDly-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
            'SwDeswapDly-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
            'SwDivClk-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
            'SwDivClk-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
            'SwDirGainA-SP': {
                'type': 'float', 'value': 0, 'low': 0.0, 'high': 1.0},
            'SwDirGainB-SP': {
                'type': 'float', 'value': 0, 'low': 0.0, 'high': 1.0},
            'SwDirGainC-SP': {
                'type': 'float', 'value': 0, 'low': 0.0, 'high': 1.0},
            'SwDirGainD-SP': {
                'type': 'float', 'value': 0, 'low': 0.0, 'high': 1.0},
            'SwInvGainA-SP': {
                'type': 'float', 'value': 0, 'low': 0.0, 'high': 1.0},
            'SwInvGainB-SP': {
                'type': 'float', 'value': 0, 'low': 0.0, 'high': 1.0},
            'SwInvGainC-SP': {
                'type': 'float', 'value': 0, 'low': 0.0, 'high': 1.0},
            'SwInvGainD-SP': {
                'type': 'float', 'value': 0, 'low': 0.0, 'high': 1.0},
            }
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_monit_database(prefix=''):
        """."""
        dbase = {
            'MONITUpdtTime-SP': {
                'type': 'float', 'value': 0, 'low': 0.001, 'high': 1.0,
                'unit': 's'},
            'MONITUpdtTime-RB': {
                'type': 'float', 'value': 0, 'low': 0.001, 'high': 1.0,
                'unit': 's'},
            }
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_offsets_database(prefix=''):
        """."""
        data_db = {'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
        dbase = {
            'PosQOffset-SP': _dcopy(data_db), 'PosQOffset-RB': _dcopy(data_db),
            'PosXOffset-SP': _dcopy(data_db), 'PosXOffset-RB': _dcopy(data_db),
            'PosYOffset-SP': _dcopy(data_db), 'PosYOffset-RB': _dcopy(data_db),
            }
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_gain_database(prefix=''):
        """."""
        data_db = {'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
        dbase = {
            'PosKq-SP': _dcopy(data_db), 'PosKq-RB': _dcopy(data_db),
            'PosKsum-SP': _dcopy(data_db), 'PosKsum-RB': _dcopy(data_db),
            'PosKx-SP': _dcopy(data_db), 'PosKx-RB': _dcopy(data_db),
            'PosKy-SP': _dcopy(data_db), 'PosKy-RB': _dcopy(data_db),
            }
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_amplitudes_database():
        """."""
        data_db = {'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
        dbase = {
            'PosX-Mon': _dcopy(data_db), 'PosY-Mon': _dcopy(data_db),
            'Sum-Mon': _dcopy(data_db), 'PosQ-Mon': _dcopy(data_db),
            'AmplA-Mon': _dcopy(data_db), 'AmplB-Mon': _dcopy(data_db),
            'AmplC-Mon': _dcopy(data_db), 'AmplD-Mon': _dcopy(data_db),
            }
        return {k: v for k, v in dbase.items()}

    @staticmethod
    def get_physical_trigger_database(prefix=''):
        """."""
        dbase = {
            'Dir-Sel': {
                'type': 'enum', 'enums': Const.TrigDir._fields, 'value': 1},
            'Dir-Sts': {
                'type': 'enum', 'enums': Const.TrigDir._fields, 'value': 1},
            'DirPol-Sel': {
                'type': 'enum', 'enums': Const.TrigDirPol._fields, 'value': 1},
            'DirPol-Sts': {
                'type': 'enum', 'enums': Const.TrigDirPol._fields, 'value': 1},
            'RcvCntRst-Cmd': {
                'type': 'int', 'value': 0},
            'TrnCntRst-Cmd': {
                'type': 'int', 'value': 0},
            'RcvCnt-Mon': {
                'type': 'int', 'value': 0},
            'TrnCnt-Mon': {
                'type': 'int', 'value': 0},
            'RcvLen-SP': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 2**15-1},
            'RcvLen-RB': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 2**15-1},
            'TrnLen-SP': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 2**15-1},
            'TrnLen-RB': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 2**15-1},
            }
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_logical_trigger_database(prefix=''):
        """."""
        dbase = {
            'RcvSrc-Sel': {
                'type': 'enum', 'enums': Const.TrigSrc._fields, 'value': 0},
            'RcvSrc-Sts': {
                'type': 'enum', 'enums': Const.TrigSrc._fields, 'value': 0},
            'TrnSrc-Sel': {
                'type': 'enum', 'enums': Const.TrigSrc._fields, 'value': 0},
            'TrnSrc-Sts': {
                'type': 'enum', 'enums': Const.TrigSrc._fields, 'value': 0},
            'RcvInSel-SP': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 2**15-1},
            'RcvInSel-RB': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 2**15-1},
            'TrnOutSel-SP': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 2**15-1},
            'TrnOutSel-RB': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 2**15-1},
            }
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_config_database(prefix=''):
        """Get the configuration PVs database."""
        dbase = {
            'Channel-Sel': {
                'type': 'enum', 'enums': Const.AcqChan._fields, 'value': 0},
            'Channel-Sts': {
                'type': 'enum', 'enums': Const.AcqChan._fields, 'value': 0},
            'Shots-SP': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
            'Shots-RB': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
            'TriggerHwDly-SP': {
                'type': 'float', 'value': 0.0, 'low': 0.0, 'high': 1e9},
            'TriggerHwDly-RB': {
                'type': 'float', 'value': 0.0, 'low': 0.0, 'high': 1e9},
            'UpdateTime-SP': {
                'type': 'float', 'value': 1.0, 'low': 0.001, 'high': 1e9},
            'UpdateTime-RB': {
                'type': 'float', 'value': 1.0, 'low': 0.001, 'high': 1e9},
            'SamplesPre-SP': {
                'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
            'SamplesPre-RB': {
                'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
            'SamplesPost-SP': {
                'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
            'SamplesPost-RB': {
                'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
            'TriggerEvent-Cmd': {
                'type': 'enum', 'enums': Const.AcqEvents._fields,
                'value': Const.AcqEvents.Stop},
            'Status-Mon': {
                'type': 'enum', 'enums': Const.AcqStates._fields, 'value': 0},
            'Trigger-Sel': {
                'type': 'enum', 'enums': Const.AcqTrigTyp._fields, 'value': 1},
            'Trigger-Sts': {
                'type': 'enum', 'enums': Const.AcqTrigTyp._fields, 'value': 1},
            'TriggerRep-Sel': {
                'type': 'enum', 'enums': Const.AcqRepeat._fields, 'value': 0},
            'TriggerRep-Sts': {
                'type': 'enum', 'enums': Const.AcqRepeat._fields, 'value': 0},
            'DataTrigChan-Sel': {
                'type': 'enum', 'enums': Const.AcqChan._fields, 'value': 0},
            'DataTrigChan-Sts': {
                'type': 'enum', 'enums': Const.AcqChan._fields, 'value': 0},
            'TriggerDataSel-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 4},
            'TriggerDataSel-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 4},
            'TriggerDataThres-SP': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 2**31 - 1},
            'TriggerDataThres-RB': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 2**31 - 1},
            'TriggerDataPol-Sel': {
                'type': 'enum', 'enums': Const.Polarity._fields, 'value': 0},
            'TriggerDataPol-Sts': {
                'type': 'enum', 'enums': Const.Polarity._fields, 'value': 0},
            'TriggerDataHyst-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TriggerDataHyst-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbTPhaseSyncEn-Sel': {
                'type': 'enum', 'enums': Const.DsblEnbl._fields, 'value': 0},
            'TbTPhaseSyncEn-Sts': {
                'type': 'enum', 'enums': Const.DsblEnbl._fields, 'value': 0},
            'TbTPhaseSyncDly-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbTPhaseSyncDly-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbTDataMaskEn-Sel': {
                'type': 'enum', 'enums': Const.DsblEnbl._fields, 'value': 0},
            'TbTDataMaskEn-Sts': {
                'type': 'enum', 'enums': Const.DsblEnbl._fields, 'value': 0},
            'TbTDataMaskSamplesBeg-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbTDataMaskSamplesBeg-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbTDataMaskSamplesEnd-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbTDataMaskSamplesEnd-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            }
        return {prefix + k: v for k, v in dbase.items()}
