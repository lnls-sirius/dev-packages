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
        'MonitPos', 'Monit1Pos', 'FMCTrigOut', 'Unconnected4', 'Unconnected5',
        'Unconnected6', 'Unconnected7', 'Unconnected8', 'Unconnected9')
    SWMODES = ('rffe_switching', 'direct', 'inverted', 'switching')
    SWTAGENBL = ('disabled', 'enabled')
    SWDATAMASKENBL = ('disabled', 'enabled')
    MONITENBL = ('No', 'Yes')

    OPMODES = ('MultiBunch', 'SinglePass')
    POLARITY = ('Positive', 'Negative')
    ENBLTYP = ('Disable', 'Enable')
    ENBLDDSBLD = ('disabled', 'enabled')
    CONNTYP = _csdev.ETypes.DISCONN_CONN
    ACQREPEAT = ('Normal', 'Repetitive')
    ACQEVENTS = ('Start', 'Stop', 'Abort')
    ACQDATATYP = ('A', 'B', 'C', 'D')
    ACQCHAN = ('ADC', 'ADCSwp', 'TbT', 'FOFB', 'TbTPha', 'FOFBPha', 'Monit1')
    ACQSTATES = (
        'Idle', 'Waiting', 'External Trig', 'Data Trig', 'Software Trig',
        'Acquiring', 'Error', 'Aborted', 'Too Many Samples',
        'Too Few Samples', 'No Memory', 'Acq Overflow')
    ACQTRIGTYP = ('Now', 'External', 'Data', 'Software')
    FFTWINDOWTYP = ('Square', 'Hanning', 'Parzen', 'Welch', 'QuadW')
    FFTCONVDIRECTION = ('Forward', 'Backward')
    FFTAVGSUBTRACT = ('No Subtraction', 'Average', 'Linear')
    FFTWRITABLEPROPS = ('INDX', 'MXIX', 'WIND', 'CDIR', 'ASUB', 'SPAN')


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
    SwTagEnbl = _csdev.Const.register('SwTagEnbl', _et.SWTAGENBL)
    SwDataMaskEnbl = _csdev.Const.register(
        'SwDataMaskEnbl', _et.SWDATAMASKENBL)
    MonitEnbl = _csdev.Const.register('MonitEnbl', _et.MONITENBL)
    OpModes = _csdev.Const.register('OpModes', _et.OPMODES)
    Polarity = _csdev.Const.register('Polarity', _et.POLARITY)
    EnblTyp = _csdev.Const.register('EnblTyp', _et.ENBLTYP)
    EnbldDsbld = _csdev.Const.register('EnbldDsbld', _et.ENBLDDSBLD)
    ConnTyp = _csdev.Const.register('ConnTyp', _et.CONNTYP)
    AcqRepeat = _csdev.Const.register('AcqRepeat', _et.ACQREPEAT)
    AcqEvents = _csdev.Const.register('AcqEvents', _et.ACQEVENTS)
    AcqDataTyp = _csdev.Const.register('AcqDataTyp', _et.ACQDATATYP)
    AcqChan = _csdev.Const.register('AcqChan', _et.ACQCHAN)
    AcqStates = _csdev.Const.register('AcqStates', _et.ACQSTATES)
    AcqTrigTyp = _csdev.Const.register('AcqTrigTyp', _et.ACQTRIGTYP)
    FFTWindowTyp = _csdev.Const.register('FFTWindowTyp', _et.FFTWINDOWTYP)
    FFTConvDirection = _csdev.Const.register(
        'FFTConvDirection', _et.FFTCONVDIRECTION)
    FFTAvgSubtract = _csdev.Const.register(
        'FFTAvgSubtract', _et.FFTAVGSUBTRACT)
    FFTWritableProps = _csdev.Const.register(
        'FFTWritableProps', _et.FFTWRITABLEPROPS)

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
            'INFOMONIT1Rate-SP': {
                'type': 'int', 'value': 21965000, 'low': 0, 'high': 2**31-1},
            'INFOMONIT1Rate-RB': {
                'type': 'int', 'value': 21965000, 'low': 0, 'high': 2**31-1},
            'INFOTBTRate-SP': {
                'type': 'int', 'value': 382, 'low': 0, 'high': 2**31-1},
            'INFOTBTRate-RB': {
                'type': 'int', 'value': 382, 'low': 0, 'high': 2**31-1},
            }

        # PHYSICAL TRIGGERS
        for i in range(8):
            trig = 'TRIGGER{0:d}'.format(i)
            dbase.update(Const.get_physical_trigger_database(trig))

        # LOGICAL TRIGGERS
        for trig_tp in ('', '_PM'):
            for i in range(24):
                trig = 'TRIGGER' + trig_tp + '{0:d}'.format(i)
                dbase.update(Const.get_logical_trigger_database(trig))

        # AMPLITUDES AND POSITION CHANNELS
        for amp_tp in ('', 'SP'):
            dbase.update(Const.get_amplitudes_database(amp_tp))

        # SETTINGS AND STATUS
        dbase.update(Const.get_offsets_database())
        dbase.update(Const.get_gain_database())
        dbase.update(Const.get_rffe_database())
        dbase.update(Const.get_asyn_database())
        dbase.update(Const.get_switch_database())
        dbase.update(Const.get_monit_database())

        data_names = {
            'GEN': ['A', 'B', 'C', 'D', 'Q', 'SUM', 'X', 'Y'],
            'PM': ['A', 'B', 'C', 'D', 'Q', 'SUM', 'X', 'Y'],
            'SP': ['A', 'B', 'C', 'D'],
            }
        data_db = {
            'type': 'float', 'value': _np.array(100000*[0.0]), 'count': 100000}

        # ARRAY DATA FROM TRIGGERED ACQUISITIONS
        for acq_tp in ('GEN', 'SP', 'PM'):
            for prop in data_names[acq_tp]:
                nm = acq_tp + '_' + prop
                dbase[nm + 'ArrayData'] = _dcopy(data_db)
                dbase.update(Const.get_statistic_database(nm))
                if acq_tp == 'GEN':
                    dbase.update(Const.get_fft_database(nm))

        # TRIGGERED ACQUISITIONS CONFIGURATION
        for acq_md in ('ACQ', 'ACQ_PM'):
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
            'SwTagEn-Sel': {
                'type': 'enum', 'enums': Const.SwTagEnbl._fields, 'value': 0},
            'SwTagEn-Sts': {
                'type': 'enum', 'enums': Const.SwTagEnbl._fields, 'value': 0},
            'SwDataMaskEn-Sel': {
                'type': 'enum', 'enums': Const.SwDataMaskEnbl._fields,
                'value': 0},
            'SwDataMaskEn-Sts': {
                'type': 'enum', 'enums': Const.SwDataMaskEnbl._fields,
                'value': 0},
            'SwDly-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
            'SwDly-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
            'SwDivClk-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
            'SwDivClk-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
            'SwDataMaskSamples-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
            'SwDataMaskSamples-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31-1},
            }
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_monit_database(prefix=''):
        """."""
        dbase = {
            'MonitEnable-Sel': {
                'type': 'enum', 'enums': Const.MonitEnbl._fields, 'value': 3},
            'MonitEnable-Sts': {
                'type': 'enum', 'enums': Const.MonitEnbl._fields, 'value': 3},
            'MONITUpdtTime-SP': {
                'type': 'float', 'value': 0, 'low': 0.05, 'high': 1.0,
                'unit': 's'},
            'MONITUpdtTime-RB': {
                'type': 'float', 'value': 0, 'low': 0.05, 'high': 1.0,
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
    def get_amplitudes_database(prefix=''):
        """."""
        data_db = {'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
        dbase = {
            'PosX-Mon': _dcopy(data_db), 'PosY-Mon': _dcopy(data_db),
            'Sum-Mon': _dcopy(data_db), 'PosQ-Mon': _dcopy(data_db),
            'AmplA-Mon': _dcopy(data_db), 'AmplB-Mon': _dcopy(data_db),
            'AmplC-Mon': _dcopy(data_db), 'AmplD-Mon': _dcopy(data_db),
            }
        return {prefix + k: v for k, v in dbase.items()}

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
            'RcvCntRst-SP': {
                'type': 'int', 'value': 0},
            'TrnCntRst-SP': {
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
            'BPMMode-Sel': {
                'type': 'enum', 'enums': Const.OpModes._fields, 'value': 0},
            'BPMMode-Sts': {
                'type': 'enum', 'enums': Const.OpModes._fields, 'value': 0},
            'Channel-Sel': {
                'type': 'enum', 'enums': Const.AcqChan._fields, 'value': 0},
            'Channel-Sts': {
                'type': 'enum', 'enums': Const.AcqChan._fields, 'value': 0},
            # 'NrShots-SP': {
            'Shots-SP': {
                'type': 'int', 'value': 1, 'low': 0, 'high': 65536},
            # 'NrShots-RB': {
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
            # 'NrSamplesPre-SP': {
            'SamplesPre-SP': {
                'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
            # 'NrSamplesPre-RB': {
            'SamplesPre-RB': {
                'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
            # 'NrSamplesPost-SP': {
            'SamplesPost-SP': {
                'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
            # 'NrSamplesPost-RB': {
            'SamplesPost-RB': {
                'type': 'int', 'value': 1000, 'low': 0, 'high': 100000},
            # 'Ctrl-Sel': {
            'TriggerEvent-Sel': {
                'type': 'enum', 'enums': Const.AcqEvents._fields,
                'value': Const.AcqEvents.Stop},
            # 'Ctrl-Sts': {
            'TriggerEvent-Sts': {
                'type': 'enum', 'enums': Const.AcqEvents._fields,
                'value': Const.AcqEvents.Stop},
            # 'Status-Mon': {
            'Status-Sel': {
                'type': 'enum', 'enums': Const.AcqStates._fields, 'value': 0},
            # 'TriggerType-Sel': {
            'Trigger-Sel': {
                'type': 'enum', 'enums': Const.AcqTrigTyp._fields, 'value': 1},
            # 'TriggerType-Sts': {
            'Trigger-Sts': {
                'type': 'enum', 'enums': Const.AcqTrigTyp._fields, 'value': 1},
            'TriggerRep-Sel': {
                'type': 'enum', 'enums': Const.AcqRepeat._fields, 'value': 0},
            'TriggerRep-Sts': {
                'type': 'enum', 'enums': Const.AcqRepeat._fields, 'value': 0},
            # 'TriggerDataChan-Sel': {
            'DataTrigChan-Sel': {
                'type': 'enum', 'enums': Const.AcqChan._fields, 'value': 0},
            # 'TriggerDataChan-Sts': {
            'DataTrigChan-Sts': {
                'type': 'enum', 'enums': Const.AcqChan._fields, 'value': 0},
            # 'TriggerDataSel-Sel': {
            #     'type': 'enum', 'enums': AcqDataTyp._fields, 'value': 0},
            # 'TriggerDataSel-Sts': {
            #     'type': 'enum', 'enums': AcqDataTyp._fields, 'value': 0},
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
            'TbtTagEn-Sel': {
                'type': 'enum', 'enums': Const.EnbldDsbld._fields, 'value': 0},
            'TbtTagEn-Sts': {
                'type': 'enum', 'enums': Const.EnbldDsbld._fields, 'value': 0},
            'TbtTagDly-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbtTagDly-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbtDataMaskEn-Sel': {
                'type': 'enum', 'enums': Const.EnbldDsbld._fields, 'value': 0},
            'TbtDataMaskEn-Sts': {
                'type': 'enum', 'enums': Const.EnbldDsbld._fields, 'value': 0},
            'TbtDataMaskSamplesBeg-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbtDataMaskSamplesBeg-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbtDataMaskSamplesEnd-SP': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            'TbtDataMaskSamplesEnd-RB': {
                'type': 'int', 'value': 0, 'low': 0, 'high': 2**31 - 1},
            }
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_fft_database(prefix=''):
        """Get the PV database of the FFT plugin."""
        data_db = {
            'type': 'float', 'value': _np.array(100000*[0.0]), 'count': 100000}
        acq_int_db = {'type': 'int', 'value': 1, 'low': 0, 'high': 100000}
        dbase = dict()
        dbase['FFTFreq-Mon'] = _dcopy(data_db)
        dbase['FFTData.SPAN'] = _dcopy(acq_int_db)
        dbase['FFTData.AMP'] = _dcopy(data_db)
        dbase['FFTData.PHA'] = _dcopy(data_db)
        dbase['FFTData.SIN'] = _dcopy(data_db)
        dbase['FFTData.COS'] = _dcopy(data_db)
        dbase['FFTData.WAVN'] = _dcopy(data_db)
        dbase['FFTData.INDX'] = _dcopy(acq_int_db)
        dbase['FFTData.MXIX'] = _dcopy(acq_int_db)
        dbase['FFTData.WIND'] = {
            'type': 'enum', 'enums': Const.FFTWindowTyp._fields, 'value': 0}
        dbase['FFTData.CDIR'] = {
            'type': 'enum', 'enums': Const.FFTConvDirection._fields,
            'value': 0}
        dbase['FFTData.ASUB'] = {
            'type': 'enum', 'enums': Const.FFTAvgSubtract._fields, 'value': 0}
        return {prefix + k: v for k, v in dbase.items()}

    @staticmethod
    def get_statistic_database(prefix=''):
        """Get the PV database of the STAT plugin."""
        acq_data_stat_db = {
            'type': 'float', 'value': 0.0, 'low': -1e12, 'high': 1e12}
        dbase = dict()
        dbase['_STATSMaxValue_RBV'] = _dcopy(acq_data_stat_db)
        dbase['_STATSMeanValue_RBV'] = _dcopy(acq_data_stat_db)
        dbase['_STATSMinValue_RBV'] = _dcopy(acq_data_stat_db)
        dbase['_STATSSigma_RBV'] = _dcopy(acq_data_stat_db)
        return {prefix + k: v for k, v in dbase.items()}
