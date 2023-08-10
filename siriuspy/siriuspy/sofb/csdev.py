"""Define PVs, constants and properties of OrbitCorr SoftIOCs."""
import os as _os
from copy import deepcopy as _dcopy

from .. import csdev as _csdev
from ..namesys import SiriusPVName as _PVName
from ..search import MASearch as _MASearch, BPMSearch as _BPMSearch, \
    LLTimeSearch as _TISearch, PSSearch as _PSSearch
from ..diagbeam.bpm.csdev import Const as _csbpm
from ..timesys import csdev as _cstiming


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    ENBL_RF = _csdev.ETypes.OFF_ON
    OPEN_CLOSED = ('Open', 'Closed')
    ORB_MODE_SI = ('SlowOrb', 'MultiTurn', 'SinglePass')
    ORB_MODE_RINGS = ('MultiTurn', 'SinglePass')
    ORB_MODE_TLINES = ('SinglePass', )
    SMOOTH_METH = ('Average', 'Median')
    RESPMAT_MODE = ('Mxx', 'Myy', 'NoCoup', 'Full')
    SPASS_METHOD = ('FromBPMs', 'Calculated')
    MTURN_ACQUIRE = ('Idle', 'Acquire')
    APPLY_CORR_TLINES = ('CH', 'CV', 'All')
    APPLY_CORR_RINGS = ('CH', 'CV', 'RF', 'All')
    APPLY_DELTA_MON = ('Idle', 'Applying', 'Done', 'Error')
    SI_CORR_SYNC = ('Off', 'Event', 'Clock')
    ORB_ACQ_CHAN = ('FAcq', 'FOFB', 'TbT', 'ADC', 'ADCSwp')
    MEAS_RMAT_CMD = ('Start', 'Stop', 'Reset')
    MEAS_RMAT_MON = ('Idle', 'Measuring', 'Completed', 'Aborted')
    DRIVE_TYPE = ('Sine', 'Square', 'Impulse')
    TLINES = ('TB', 'TS')
    RINGS = ('BO', 'SI')
    ACCELERATORS = TLINES + RINGS

    STS_LBLS_CORR_TLINES = (
        'CHCVConnected', 'CHCVModeConfigured', 'CHCVPwrStateOn')
    STS_LBLS_CORR_RINGS = STS_LBLS_CORR_TLINES + (
        'TimingConnected', 'TimingConfigured', 'RFConnected', 'RFPwrStateOn')
    STS_LBLS_ORB = (
        'TimingConnected', 'TimingConfigured', 'BPMsConnected',
        'BPMsEnabled', 'BPMsConfigured', 'BPMsTestDsbld', 'BPMsSwSyncEnbld',
        'OrbRawConnected')
    STS_LBLS_GLOB = ('Ok', 'NotOk')


_et = ETypes  # syntactic sugar


# --- Const class ---

class ConstTLines(_csdev.Const):
    """Const class defining transport lines orbitcorr constants."""

    ORBIT_CONVERSION_UNIT = 1/1000  # from nm to um
    MAX_MT_ORBS = 4000
    MAX_DRIVE_DATA = 3 * 5000
    MIN_SING_VAL = 0.2
    TIKHONOV_REG_CONST = 0
    TINY_KICK = 1e-3  # [urad]
    DEF_MAX_ORB_DISTORTION = 50  # [um]
    ACQRATE_TRIGMODE = 2  # [Hz]
    ACQRATE_SLOWORB = 60  # [Hz]
    BPMsFreq = 10.48  # [Hz]

    TrigAcqCtrl = _csbpm.AcqEvents
    TrigAcqChan = _csdev.Const.register('TrigAcqChan', _et.ORB_ACQ_CHAN)
    TrigAcqRepeat = _csbpm.AcqRepeat
    SmoothMeth = _csdev.Const.register('SmoothMeth', _et.SMOOTH_METH)
    RespMatMode = _csdev.Const.register('RespMatMode', _et.RESPMAT_MODE)
    MeasRespMatCmd = _csdev.Const.register('MeasRespMatCmd', _et.MEAS_RMAT_CMD)
    MeasRespMatMon = _csdev.Const.register('MeasRespMatMon', _et.MEAS_RMAT_MON)
    TransportLines = _csdev.Const.register(
        'TransportLines', _et.TLINES, (0, 1))
    Rings = _csdev.Const.register('Rings', _et.RINGS, (2, 3))
    Accelerators = _csdev.Const.register('Accelerators', _et.ACCELERATORS)

    SOFBMode = _csdev.Const.register('SOFBMode', _et.ORB_MODE_TLINES)
    SyncWithInj = _csdev.Const.register('SyncWithInj', _et.OFF_ON)
    ApplyDelta = _csdev.Const.register('ApplyDelta', _et.APPLY_CORR_TLINES)
    ApplyDeltaMon = _csdev.Const.register(
        'ApplyDeltaMon', _et.APPLY_DELTA_MON)
    StsLblsCorr = _csdev.Const.register(
        'StsLblsCorr', _et.STS_LBLS_CORR_TLINES)
    StsLblsOrb = _csdev.Const.register('StsLblsOrb', _et.STS_LBLS_ORB)
    StsLblsGlob = _csdev.Const.register('StsLblsGlob', _et.STS_LBLS_GLOB)

    LoopState = _csdev.Const.register('LoopState', _et.OPEN_CLOSED)


class ConstRings(ConstTLines):
    """Const class defining rings orbitcorr constants."""

    SOFBMode = _csdev.Const.register('SOFBMode', _et.ORB_MODE_RINGS)
    StsLblsCorr = _csdev.Const.register('StsLblsCorr', _et.STS_LBLS_CORR_RINGS)
    MTurnAcquire = _csdev.Const.register('MTurnAcquire', _et.MTURN_ACQUIRE)
    ApplyDelta = _csdev.Const.register('ApplyDelta', _et.APPLY_CORR_RINGS)
    EnblRF = _csdev.Const.register('EnblRF', _et.ENBL_RF)
    RF_GEN_NAME = 'RF-Gen'


class ConstSI(ConstRings):
    """Const class defining rings orbitcorr constants."""

    SOFBMode = _csdev.Const.register('SOFBMode', _et.ORB_MODE_SI)
    CorrSync = _csdev.Const.register('CorrSync', _et.SI_CORR_SYNC)
    CorrPSSOFBEnbl = _csdev.Const.register('CorrPSSOFBEnbl', _et.DSBL_ENBL)
    DriveType = _csdev.Const.register('DriveType', _et.DRIVE_TYPE)
    DriveState = _csdev.Const.register('DriveState', _et.OPEN_CLOSED)

    CORR_DEF_DELAY = 12  # [ms]


# --- Database classes ---

class SOFBTLines(ConstTLines):
    """SOFB class for TLines."""

    def __init__(self, acc):
        """Init1 method."""
        self.acc = acc.upper()
        self.evg_name = _TISearch.get_evg_name()
        self.acc_idx = self.Accelerators._fields.index(self.acc)

        # Define the BPMs:
        self.bpm_names = _BPMSearch.get_names({'sec': acc, 'dev': 'BPM'})

        # Define correctors:
        filter_ch = dict(sec=acc, dis='PS', dev='CH')
        filter_cv = dict(sec=acc, dis='PS', dev='CV')
        if self.acc == 'SI':
            filter_ch.update({'sub': '..(M|C).'})
            filter_cv.update({'sub': '..(M|C).'})
        self.ch_names = _PSSearch.get_psnames(filter_ch)
        self.cv_names = _PSSearch.get_psnames(filter_cv)
        if self.acc == 'TS':
            self.ch_names = [_PVName('TS-01:PU-EjeSeptG'), ] + self.ch_names
            self.cv_names = [
                cvn for cvn in self.cv_names
                if not ('E' in cvn.idx or '0' in cvn.idx)]

        # Give them a nickname:
        self.bpm_nicknames = _BPMSearch.get_nicknames(self.bpm_names)
        self.ch_nicknames = _PSSearch.get_psnicknames(self.ch_names)
        self.cv_nicknames = _PSSearch.get_psnicknames(self.cv_names)
        if self.acc == 'TS':
            self.ch_nicknames[0] = 'EjeseptG'

        # Find their position along the ring:
        self.bpm_pos = _BPMSearch.get_positions(self.bpm_names)
        self.ch_pos = _MASearch.get_mapositions(map(
            lambda x: x.substitute(dis='MA' if x.dis == 'PS' else 'PM'),
            self.ch_names))
        self.cv_pos = _MASearch.get_mapositions(map(
            lambda x: x.substitute(dis='MA' if x.dis == 'PS' else 'PM'),
            self.cv_names))

        # Find the total number of BPMs and correctors:
        self.nr_bpms = len(self.bpm_names)
        self.nr_ch = len(self.ch_names)
        self.nr_cv = len(self.cv_names)
        self.nr_chcv = self.nr_ch + self.nr_cv
        self.nr_corrs = self.nr_chcv + 1 if self.isring else self.nr_chcv

        ext = acc.lower() + 'orb'
        ioc_fol = acc.lower() + '-ap-sofb'
        ioc_fol = _os.path.join('/home', 'sirius', 'iocs-log', ioc_fol, 'data')
        self.ref_orb_fname = _os.path.join(ioc_fol, 'ref_orbit.'+ext)
        ext = acc.lower() + 'respmat'
        self.respmat_fname = _os.path.join(ioc_fol, 'respmat.'+ext)

        self.trigger_acq_name = self.acc + '-Fam:TI-BPM'
        if self.acc == 'SI':
            self.trigger_cor_name = self.acc + '-Glob:TI-Mags-Corrs'
            self.evt_cor_name = 'Orb' + self.acc
            self.clk_cor_name = 'Clock3'

        self.evt_acq_name = 'Linac'
        self.matrix_size = self.nr_corrs * (2 * self.nr_bpms)
        self.nr_svals = min(self.nr_corrs, 2 * self.nr_bpms)
        self.circum = 21.2477 if self.acc == 'TB' else 26.8933  # in meters
        self.rev_per = self.circum / 299792458  # in seconds

    @property
    def isring(self):
        """."""
        return self.acc in self.Rings._fields

    def get_ioc_database(self, prefix=''):
        """Return IOC database."""
        dbase = self.get_sofb_database(prefix)
        dbase.update(self.get_corrs_database(prefix))
        dbase.update(self.get_respmat_database(prefix))
        dbase.update(self.get_orbit_database(prefix))
        dbase = _csdev.add_pvslist_cte(dbase)
        return dbase

    def get_sofb_database(self, prefix=''):
        """Return SOFB database."""
        dbase = {
            'Log-Mon': {'type': 'char', 'value': '', 'count': 200},
            'MeasRespMat-Cmd': {
                'type': 'enum', 'value': 0,
                'enums': self.MeasRespMatCmd._fields},
            'MeasRespMat-Mon': {
                'type': 'enum', 'value': 0,
                'enums': self.MeasRespMatMon._fields},
            'MeasRespMatKickCH-SP': {
                'type': 'float', 'value': 15, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatKickCH-RB': {
                'type': 'float', 'value': 15, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatKickCV-SP': {
                'type': 'float', 'value': 22.5, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatKickCV-RB': {
                'type': 'float', 'value': 22.5, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatWait-SP': {
                'type': 'float', 'value': 1, 'unit': 's', 'prec': 3,
                'lolim': 0.005, 'hilim': 100},
            'MeasRespMatWait-RB': {
                'type': 'float', 'value': 1, 'unit': 's', 'prec': 3,
                'lolim': 0.005, 'hilim': 100},
            'CalcDelta-Cmd': {
                'type': 'int', 'value': 0, 'unit': 'Calculate kicks'},
            'ManCorrGainCH-SP': {
                'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
                'lolim': -10000, 'hilim': 10000},
            'ManCorrGainCH-RB': {
                'type': 'float', 'value': 100, 'prec': 2, 'unit': '%'},
            'ManCorrGainCV-SP': {
                'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
                'lolim': -10000, 'hilim': 10000},
            'ManCorrGainCV-RB': {
                'type': 'float', 'value': 100, 'prec': 2, 'unit': '%'},
            'MaxKickCH-SP': {
                'type': 'float', 'value': 300, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 500000},
            'MaxKickCH-RB': {
                'type': 'float', 'value': 300, 'prec': 3, 'unit': 'urad',
                'lolim': 0, 'hilim': 500000},
            'MaxKickCV-SP': {
                'type': 'float', 'value': 300, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxKickCV-RB': {
                'type': 'float', 'value': 300, 'prec': 3, 'unit': 'urad',
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickCH-SP': {
                'type': 'float', 'value': 5, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickCH-RB': {
                'type': 'float', 'value': 5, 'prec': 3, 'unit': 'urad',
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickCV-SP': {
                'type': 'float', 'value': 5, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickCV-RB': {
                'type': 'float', 'value': 5, 'prec': 3, 'unit': 'urad',
                'lolim': 0, 'hilim': 10000},
            'DeltaKickCH-SP': {
                'type': 'float', 'count': self.nr_ch, 'value': self.nr_ch*[0],
                'unit': 'urad'},
            'DeltaKickCH-RB': {
                'type': 'float', 'count': self.nr_ch, 'value': self.nr_ch*[0],
                'unit': 'urad'},
            'DeltaKickCV-SP': {
                'type': 'float', 'count': self.nr_cv, 'value': self.nr_cv*[0],
                'unit': 'urad'},
            'DeltaKickCV-RB': {
                'type': 'float', 'count': self.nr_cv, 'value': self.nr_cv*[0],
                'unit': 'urad'},
            'ApplyDelta-Cmd': {
                'type': 'enum', 'enums': self.ApplyDelta._fields, 'value': 0,
                'unit': 'Apply last calculated kicks.'},
            'ApplyDelta-Mon': {
                'type': 'enum', 'enums': self.ApplyDeltaMon._fields,
                'value': 0, 'unit': 'Status of Kicks implementation.'},
            'Status-Mon': {
                'type': 'enum', 'value': 1,
                'enums': self.StsLblsGlob._fields}
            }
        return self._add_prefix(dbase, prefix)

    def get_corrs_database(self, prefix=''):
        """Return SOFB Correctors database."""
        dbase = {
            'KickCH-Mon': {
                'type': 'float', 'count': self.nr_ch, 'value': self.nr_ch*[0],
                'unit': 'urad'},
            'KickCV-Mon': {
                'type': 'float', 'count': self.nr_cv, 'value': self.nr_cv*[0],
                'unit': 'urad'},
            'CorrConfig-Cmd': {'type': 'int', 'value': 0},
            'CHPosS-Cte': {
                'type': 'float', 'unit': 'm', 'count': self.nr_ch,
                'value': self.ch_pos},
            'CVPosS-Cte': {
                'type': 'float', 'unit': 'm', 'count': self.nr_cv,
                'value': self.cv_pos},
            'CHNickName-Cte': {
                'type': 'string', 'unit': 'shortname for the chs.',
                'count': self.nr_ch, 'value': self.ch_nicknames},
            'CVNickName-Cte': {
                'type': 'string', 'unit': 'shortname for the cvs.',
                'count': self.nr_cv, 'value': self.cv_nicknames},
            'CorrStatus-Mon': {'type': 'int', 'value': 0b1111111},
            'CorrStatusLabels-Cte': {
                'type': 'string', 'count': len(self.StsLblsCorr._fields),
                'value': self.StsLblsCorr._fields}
            }
        return self._add_prefix(dbase, prefix)

    def get_orbit_database(self, prefix=''):
        """Return Orbit database."""
        nbpm = self.nr_bpms
        pvs = [
            'RefOrbX-SP', 'RefOrbX-RB',
            'RefOrbY-SP', 'RefOrbY-RB',
            'SPassOrbX-Mon', 'SPassOrbY-Mon',
            'SPassSum-Mon',
            'BPMOffsetX-Mon', 'BPMOffsetY-Mon',
            ]
        dbase = dict()
        prop = {
            'type': 'float', 'unit': 'um', 'count': nbpm, 'value': nbpm*[0]}
        for k in pvs:
            dbase[k] = _dcopy(prop)

        # Orbit statistics
        pvs = [
            'DeltaOrbXAvg-Mon', 'DeltaOrbYAvg-Mon',
            'DeltaOrbXStd-Mon', 'DeltaOrbYStd-Mon',
            'DeltaOrbXMin-Mon', 'DeltaOrbYMin-Mon',
            'DeltaOrbXMax-Mon', 'DeltaOrbYMax-Mon']
        prop = {'type': 'float', 'value': 0, 'prec': 3, 'unit': 'um'}
        for k in pvs:
            dbase[k] = _dcopy(prop)

        dbase.update({
            'SyncWithInjection-Sel': {
                'type': 'enum', 'unit': 'Off_On',
                'value': self.SyncWithInj.Off,
                'enums': self.SyncWithInj._fields},
            'SyncWithInjection-Sts': {
                'type': 'enum', 'unit': 'Off_On',
                'value': self.SyncWithInj.Off,
                'enums': self.SyncWithInj._fields},
            'TestDataEnbl-Sel': {
                'type': 'enum', 'unit': 'Dsbl_Enbl',
                'value': self.DsblEnbl.Dsbl, 'enums': self.DsblEnbl._fields},
            'TestDataEnbl-Sts': {
                'type': 'enum', 'unit': 'Dsbl_Enbl',
                'value': self.DsblEnbl.Dsbl, 'enums': self.DsblEnbl._fields},
            'TrigAcqConfig-Cmd': {'type': 'int', 'value': 0},
            'TrigAcqCtrl-Sel': {
                'type': 'enum', 'unit': 'Start_Stop_Abort',
                'value': self.TrigAcqCtrl.Stop,
                'enums': self.TrigAcqCtrl._fields},
            'TrigAcqCtrl-Sts': {
                'type': 'enum', 'unit': 'Start_Stop_Abort.',
                'value': self.TrigAcqCtrl.Stop,
                'enums': self.TrigAcqCtrl._fields},
            'TrigAcqChan-Sel': {
                'type': 'enum', 'unit': 'FAcq_FOFB_TbT_ADC_ADCSwp',
                'value': self.TrigAcqChan.ADC,
                'enums': self.TrigAcqChan._fields},
            'TrigAcqChan-Sts': {
                'type': 'enum', 'unit': 'FAcq_FOFB_TbT_ADC_ADCSwp',
                'value': self.TrigAcqChan.ADC,
                'enums': self.TrigAcqChan._fields},
            'TrigAcqRepeat-Sel': {
                'type': 'enum', 'unit': 'Normal_Repetitive',
                'value': self.TrigAcqRepeat.Repetitive,
                'enums': self.TrigAcqRepeat._fields},
            'TrigAcqRepeat-Sts': {
                'type': 'enum', 'unit': 'Normal_Repetitive',
                'value': self.TrigAcqRepeat.Repetitive,
                'enums': self.TrigAcqRepeat._fields},
            'TrigNrShots-SP': {
                'type': 'int', 'unit': '', 'value': 1,
                'hilim': 1000, 'lolim': 1},
            'TrigNrShots-RB': {
                'type': 'int', 'unit': '', 'value': 1,
                'hilim': 1000, 'lolim': 1},
            'TrigNrSamplesPre-SP': {
                'type': 'int', 'unit': '', 'value': 0,
                'hilim': 20000, 'lolim': -1},
            'TrigNrSamplesPre-RB': {
                'type': 'int', 'unit': '', 'value': 0,
                'hilim': 20000, 'lolim': -1},
            'TrigNrSamplesPost-SP': {
                'type': 'int', 'unit': '', 'value': 382,
                'hilim': 20000, 'lolim': 0},
            'TrigNrSamplesPost-RB': {
                'type': 'int', 'unit': '', 'value': 382,
                'hilim': 20000, 'lolim': 0},
            'PolyCalibration-Sel': {
                'type': 'enum', 'unit': 'Dsbl_Enbl',
                'value': self.DsblEnbl.Enbl, 'enums': self.DsblEnbl._fields},
            'PolyCalibration-Sts': {
                'type': 'enum', 'unit': 'Dsbl_Enbl',
                'value': self.DsblEnbl.Enbl, 'enums': self.DsblEnbl._fields},
            'SmoothNrPts-SP': {
                'type': 'int', 'value': 1, 'unit': '#',
                'lolim': 1, 'hilim': 500},
            'SmoothNrPts-RB': {
                'type': 'int', 'value': 1, 'unit': '#',
                'lolim': 1, 'hilim': 500},
            'SmoothMethod-Sel': {
                'type': 'enum', 'unit': 'Average_Median',
                'value': self.SmoothMeth.Average, 'enums': _et.SMOOTH_METH},
            'SmoothMethod-Sts': {
                'type': 'enum', 'unit': 'Average_Median',
                'value': self.SmoothMeth.Average, 'enums': _et.SMOOTH_METH},
            'SmoothReset-Cmd': {'type': 'int', 'value': 0, 'unit': '#'},
            'BufferCount-Mon': {'type': 'int', 'value': 0, 'unit': '#'},
            'SPassMaskSplBeg-SP': {
                'type': 'int', 'value': 0, 'lolim': -1, 'hilim': 1000},
            'SPassMaskSplBeg-RB': {
                'type': 'int', 'value': 0, 'lolim': -1, 'hilim': 1000},
            'SPassMaskSplEnd-SP': {
                'type': 'int', 'value': 0, 'lolim': -1, 'hilim': 1000},
            'SPassMaskSplEnd-RB': {
                'type': 'int', 'value': 0, 'lolim': -1, 'hilim': 1000},
            'SPassAvgNrTurns-SP': {
                'type': 'int', 'value': 1, 'lolim': 1, 'hilim': 1000},
            'SPassAvgNrTurns-RB': {
                'type': 'int', 'value': 1, 'lolim': 1, 'hilim': 1000},
            'BPMPosS-Mon': {
                'type': 'float', 'unit': 'm', 'count': nbpm,
                'value': self.bpm_pos, 'prec': 2},
            'BPMNickName-Cte': {
                'type': 'string', 'unit': 'shortname for the bpms.',
                'count': nbpm, 'value': self.bpm_nicknames},
            'OrbStatus-Mon': {'type': 'int', 'value': 0b00000000},
            'OrbStatusLabels-Cte': {
                'type': 'string', 'count': len(self.StsLblsOrb._fields),
                'value': self.StsLblsOrb._fields},
            'SlowOrbTimeout-Mon': {
                'type': 'int', 'value': 0, 'lolim': -1, 'hilim': 1001},
            'SyncBPMs-Cmd': {'type': 'int', 'value': 0},
            })
        return self._add_prefix(dbase, prefix)

    def get_respmat_database(self, prefix=''):
        """Return SOFB respmat database."""
        dbase = {
            'RespMat-SP': {
                'type': 'float', 'count': self.matrix_size,
                'value': self.matrix_size*[0],
                'unit': '(BH, BV)(um) x (CH, CV, RF)(urad, Hz)'},
            'RespMat-RB': {
                'type': 'float', 'count': self.matrix_size,
                'value': self.matrix_size*[0],
                'unit': '(BH, BV)(um) x (CH, CV, RF)(urad, Hz)'},
            'RespMat-Mon': {
                'type': 'float', 'count': self.matrix_size,
                'value': self.matrix_size*[0],
                'unit': '(BH, BV)(um) x (CH, CV, RF)(urad, Hz)'},
            'InvRespMat-Mon': {
                'type': 'float', 'count': self.matrix_size,
                'value': self.matrix_size*[0],
                'unit': '(CH, CV, RF)(urad, Hz) x (BH, BV)(um)'},
            'RespMatMode-Sel': {
                'type': 'enum', 'value': self.RespMatMode.Full,
                'enums': self.RespMatMode._fields},
            'RespMatMode-Sts': {
                'type': 'enum', 'value': self.RespMatMode.Full,
                'enums': self.RespMatMode._fields},
            'SingValuesRaw-Mon': {
                'type': 'float', 'count': self.nr_svals,
                'value': self.nr_svals*[0],
                'unit': 'Singular values of the matrix'},
            'SingValues-Mon': {
                'type': 'float', 'count': self.nr_svals,
                'value': self.nr_svals*[0],
                'unit': 'Singular values of the matrix in use'},
            'CHEnblList-SP': {
                'type': 'int', 'count': self.nr_ch, 'value': self.nr_ch*[1],
                'unit': 'CHs used in correction'},
            'CHEnblList-RB': {
                'type': 'int', 'count': self.nr_ch, 'value': self.nr_ch*[1],
                'unit': 'CHs used in correction'},
            'CVEnblList-SP': {
                'type': 'int', 'count': self.nr_cv, 'value': self.nr_cv*[1],
                'unit': 'CVs used in correction'},
            'CVEnblList-RB': {
                'type': 'int', 'count': self.nr_cv, 'value': self.nr_cv*[1],
                'unit': 'CVs used in correction'},
            'BPMXEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPMX used in correction'},
            'BPMXEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPMX used in correction'},
            'BPMYEnblList-SP': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPMY used in correction'},
            'BPMYEnblList-RB': {
                'type': 'int', 'count': self.nr_bpms,
                'value': self.nr_bpms*[1],
                'unit': 'BPMY used in correction'},
            'MinSingValue-SP': {
                'type': 'float', 'value': self.MIN_SING_VAL, 'prec': 5,
                'lolim': 0, 'hilim': 1e9, 'unit': 'SingVal'},
            'MinSingValue-RB': {
                'type': 'float', 'value': self.MIN_SING_VAL, 'prec': 5,
                'lolim': 0, 'hilim': 1e9, 'unit': 'SingVal'},
            'TikhonovRegConst-SP': {
                'type': 'float', 'value': self.TIKHONOV_REG_CONST, 'prec': 5,
                'lolim': 0, 'hilim': 1e9, 'unit': 'SingVal'},
            'TikhonovRegConst-RB': {
                'type': 'float', 'value': self.TIKHONOV_REG_CONST, 'prec': 5,
                'lolim': 0, 'hilim': 1e9, 'unit': 'SingVal'},
            'NrSingValues-Mon': {
                'type': 'int', 'value': self.nr_svals, 'unit': '#SingVals',
                'lolim': 1, 'hilim': self.nr_svals},
            'DeltaKickCH-Mon': {
                'type': 'float', 'count': self.nr_ch, 'value': self.nr_ch*[0],
                'unit': 'urad'},
            'DeltaKickCV-Mon': {
                'type': 'float', 'count': self.nr_cv, 'value': self.nr_cv*[0],
                'unit': 'urad'},
            }
        return self._add_prefix(dbase, prefix)

    def _add_prefix(self, dbase, prefix):
        if prefix:
            return {prefix + k: v for k, v in dbase.items()}
        return dbase


class SOFBRings(SOFBTLines, ConstRings):
    """SOFB class."""

    def __init__(self, acc):
        """Init method."""
        SOFBTLines.__init__(self, acc)
        self.circum = 496.8  # in meter
        self.harm_number = 828
        self.rev_per = self.circum / 299792458  # in seconds

    def get_sofb_database(self, prefix=''):
        """Return SOFB database."""
        db_ring = {
            'MeasRespMatKickRF-SP': {
                'type': 'float', 'value': 75, 'unit': 'Hz', 'prec': 2,
                'lolim': 1, 'hilim': 1000},
            'MeasRespMatKickRF-RB': {
                'type': 'float', 'value': 75, 'unit': 'Hz', 'prec': 2,
                'lolim': 1, 'hilim': 1000},
            'ManCorrGainRF-SP': {
                'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
                'lolim': -1000, 'hilim': 1000},
            'ManCorrGainRF-RB': {
                'type': 'float', 'value': 100, 'prec': 2, 'unit': '%'},
            'MaxDeltaKickRF-SP': {
                'type': 'float', 'value': 10, 'unit': 'Hz', 'prec': 2,
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickRF-RB': {
                'type': 'float', 'value': 10, 'prec': 2, 'unit': 'Hz',
                'lolim': 0, 'hilim': 10000},
            'DeltaKickRF-SP': {
                'type': 'float', 'value': 0, 'prec': 2, 'unit': 'Hz'},
            'DeltaKickRF-RB': {
                'type': 'float', 'value': 0, 'prec': 2, 'unit': 'Hz'},
            }
        dbase = super().get_sofb_database(prefix=prefix)
        dbase.update(self._add_prefix(db_ring, prefix))
        return dbase

    def get_corrs_database(self, prefix=''):
        """Return SOFB correctors database."""
        db_ring = {
            'KickRF-Mon': {
                'type': 'float', 'value': 1, 'unit': 'Hz', 'prec': 2},
            'OrbLength-Mon': {
                'type': 'float', 'value': 1, 'unit': 'm', 'prec': 6},
            }
        dbase = super().get_corrs_database(prefix=prefix)
        dbase.update(self._add_prefix(db_ring, prefix))
        return dbase

    def get_respmat_database(self, prefix=''):
        """Return SOFB respmat database."""
        db_ring = {
            'RFEnbl-Sel': {
                'type': 'enum', 'enums': self.EnblRF._fields, 'value': 0,
                'unit': 'Off_On'},
            'RFEnbl-Sts': {
                'type': 'enum', 'enums': self.EnblRF._fields, 'value': 0,
                'unit': 'Off_On'},
            'DeltaKickRF-Mon': {
                'type': 'float', 'value': 0, 'prec': 2, 'unit': 'Hz'},
            }
        dbase = super().get_respmat_database(prefix=prefix)
        dbase.update(self._add_prefix(db_ring, prefix))
        return dbase

    def get_orbit_database(self, prefix=''):
        """Return Orbit database."""
        nbpm = self.nr_bpms
        pvs_ring = [
            'MTurnIdxOrbX-Mon', 'MTurnIdxOrbY-Mon',
            'MTurnIdxSum-Mon',
            ]
        db_ring = dict()
        prop = {
            'type': 'float', 'unit': 'um', 'count': nbpm, 'value': nbpm*[0]}
        for k in pvs_ring:
            db_ring[k] = _dcopy(prop)
        db_ring.update({
            'MTurnAcquire-Cmd': {
                'type': 'enum', 'value': 0,
                'enums': self.MTurnAcquire._fields},
            'MTurnUseMask-Sel': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'MTurnUseMask-Sts': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'MTurnMaskSplBeg-SP': {
                'type': 'int', 'value': 0, 'lolim': -1, 'hilim': 1000},
            'MTurnMaskSplBeg-RB': {
                'type': 'int', 'value': 0, 'lolim': -1, 'hilim': 1000},
            'MTurnMaskSplEnd-SP': {
                'type': 'int', 'value': 0, 'lolim': -1, 'hilim': 1000},
            'MTurnMaskSplEnd-RB': {
                'type': 'int', 'value': 0, 'lolim': -1, 'hilim': 1000},
            'MTurnDownSample-SP': {
                'type': 'int', 'unit': '', 'value': 1,
                'hilim': 20000, 'lolim': 1},
            'MTurnDownSample-RB': {
                'type': 'int', 'unit': '', 'value': 1,
                'hilim': 20000, 'lolim': 1},
            'MTurnOrbX-Mon': {
                'type': 'float', 'unit': 'um', 'count': self.MAX_MT_ORBS*nbpm,
                'value': 50*nbpm*[0]},
            'MTurnOrbY-Mon': {
                'type': 'float', 'unit': 'um', 'count': self.MAX_MT_ORBS*nbpm,
                'value': 50*nbpm*[0]},
            'MTurnSum-Mon': {
                'type': 'float', 'unit': 'count',
                'count': self.MAX_MT_ORBS*nbpm,
                'value': 50*nbpm*[0]},
            'MTurnTime-Mon': {
                'type': 'float', 'unit': 's', 'count': self.MAX_MT_ORBS,
                'value': 50*[0]},
            'MTurnIdx-SP': {
                'type': 'int', 'unit': '', 'value': 0,
                'hilim': self.MAX_MT_ORBS, 'lolim': 0},
            'MTurnIdx-RB': {
                'type': 'int', 'unit': '', 'value': 0,
                'hilim': self.MAX_MT_ORBS, 'lolim': 0},
            'MTurnIdxTime-Mon': {
                'type': 'float', 'unit': 's', 'value': 0.0, 'prec': 5,
                'hilim': 500, 'lolim': 0},
            })
        dbase = super().get_orbit_database(prefix=prefix)
        dbase.update(self._add_prefix(db_ring, prefix))
        return dbase


class SOFBSI(SOFBRings, ConstSI):
    """SOFB class."""

    def __init__(self, acc):
        """Init method."""
        SOFBRings.__init__(self, acc)
        vals = _cstiming.get_hl_trigger_database(self.trigger_cor_name)
        evts = vals['Src-Sel']['enums']
        self.CorrExtEvtSrc = self.register('CorrExtEvtSrc', evts)
        self.circum = 518.396  # in meter
        self.harm_number = 864
        self.rev_per = self.circum / 299792458  # in seconds

    def get_sofb_database(self, prefix=''):
        """Return SOFB database."""
        db_ring = {
            'LoopState-Sel': {
                'type': 'enum', 'enums': self.LoopState._fields, 'value': 0},
            'LoopState-Sts': {
                'type': 'enum', 'enums': self.LoopState._fields, 'value': 0},
            'LoopFreq-SP': {
                'type': 'float', 'value': self.BPMsFreq, 'unit': 'Hz',
                'prec': 3, 'lolim': 1e-3, 'hilim': 60},
            'LoopFreq-RB': {
                'type': 'float', 'value': self.BPMsFreq, 'unit': 'Hz',
                'prec': 3, 'lolim': 1e-3, 'hilim': 60},
            'LoopPIDKpCH-SP': {
                'type': 'float', 'value': 0.0, 'unit': 'frac', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKpCH-RB': {
                'type': 'float', 'value': 0.0, 'unit': 'frac', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKpCV-SP': {
                'type': 'float', 'value': 0.0, 'unit': 'frac', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKpCV-RB': {
                'type': 'float', 'value': 0.0, 'unit': 'frac', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKiCH-SP': {
                'type': 'float', 'value': 0.2, 'unit': 'frac.Hz', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKiCH-RB': {
                'type': 'float', 'value': 0.2, 'unit': 'frac.Hz', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKiCV-SP': {
                'type': 'float', 'value': 0.2, 'unit': 'frac.Hz', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKiCV-RB': {
                'type': 'float', 'value': 0.2, 'unit': 'frac.Hz', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKdCH-SP': {
                'type': 'float', 'value': 0, 'unit': 'frac.s', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKdCH-RB': {
                'type': 'float', 'value': 0, 'unit': 'frac.s', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKdCV-SP': {
                'type': 'float', 'value': 0, 'unit': 'frac.s', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKdCV-RB': {
                'type': 'float', 'value': 0, 'unit': 'frac.s', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKpRF-SP': {
                'type': 'float', 'value': 0.0, 'unit': 'frac', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKpRF-RB': {
                'type': 'float', 'value': 0.0, 'unit': 'frac', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKiRF-SP': {
                'type': 'float', 'value': 0.2, 'unit': 'frac.Hz', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKiRF-RB': {
                'type': 'float', 'value': 0.2, 'unit': 'frac.Hz', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKdRF-SP': {
                'type': 'float', 'value': 0, 'unit': 'frac.s', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPIDKdRF-RB': {
                'type': 'float', 'value': 0, 'unit': 'frac.s', 'prec': 3,
                'lolim': -1000, 'hilim': 1000},
            'LoopPerfItersOk-Mon': {
                'type': 'float', 'value': 0, 'unit': '%', 'prec': 3,
                'lolim': -1, 'hilim': 100},
            'LoopEffectiveRate-Mon': {
                'type': 'float', 'value': 0, 'unit': 'Hz', 'prec': 3,
                'lolim': 0, 'hilim': 100},
            'LoopNumIters-Mon': {
                'type': 'float', 'value': 0, 'unit': '#', 'prec': 0,
                'lolim': 0, 'hilim': 100000},
            'LoopPrintEveryNumIters-SP': {
                'type': 'float', 'value': 200, 'unit': '#', 'prec': 0,
                'lolim': 1, 'hilim': 100000},
            'LoopPrintEveryNumIters-RB': {
                'type': 'float', 'value': 200, 'unit': '#', 'prec': 0,
                'lolim': 1, 'hilim': 100000},
            'LoopPerfItersTOut-Mon': {
                'type': 'float', 'value': 0, 'unit': '%', 'prec': 3,
                'lolim': -1, 'hilim': 100},
            'LoopPerfItersDiff-Mon': {
                'type': 'float', 'value': 0, 'unit': '%', 'prec': 3,
                'lolim': -1, 'hilim': 100},
            'LoopPerfDiffNrPSMax-Mon': {
                'type': 'float', 'value': 0, 'unit': '#', 'prec': 3,
                'lolim': -1, 'hilim': 400},
            'LoopPerfDiffNrPSAvg-Mon': {
                'type': 'float', 'value': 0, 'unit': '#', 'prec': 3,
                'lolim': -1, 'hilim': 400},
            'LoopPerfDiffNrPSStd-Mon': {
                'type': 'float', 'value': 0, 'unit': '#', 'prec': 3,
                'lolim': -1, 'hilim': 400},
            'LoopPerfTimGetOMax-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimGetOMin-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimGetOAvg-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimGetOStd-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimGetKMax-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimGetKMin-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimGetKAvg-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimGetKStd-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimCalcMax-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimCalcMin-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimCalcAvg-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimCalcStd-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimProcMax-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimProcMin-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimProcAvg-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimProcStd-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimAppMax-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimAppMin-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimAppAvg-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimAppStd-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimTotMax-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimTotMin-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimTotAvg-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopPerfTimTotStd-Mon': {
                'type': 'float', 'value': 0, 'unit': 'ms', 'prec': 1,
                'lolim': -1, 'hilim': 100},
            'LoopMaxOrbDistortion-SP': {
                'type': 'float', 'value': self.DEF_MAX_ORB_DISTORTION,
                'prec': 3, 'unit': 'um',
                'lolim': 0, 'hilim': 10000},
            'LoopMaxOrbDistortion-RB': {
                'type': 'float', 'value': self.DEF_MAX_ORB_DISTORTION,
                'prec': 3, 'unit': 'um',
                'lolim': 0, 'hilim': 10000},
            'CorrPSSOFBEnbl-Sel': {
                'type': 'enum', 'enums': self.CorrPSSOFBEnbl._fields,
                'value': self.CorrPSSOFBEnbl.Dsbl},
            'CorrPSSOFBEnbl-Sts': {
                'type': 'enum', 'enums': self.CorrPSSOFBEnbl._fields,
                'value': self.CorrPSSOFBEnbl.Dsbl},
            'CorrPSSOFBEnbl-Mon': {
                'type': 'enum', 'enums': self.CorrPSSOFBEnbl._fields,
                'value': self.CorrPSSOFBEnbl.Dsbl},
            'FOFBDownloadKicksPerc-SP': {
                'type': 'float', 'value': 4.0, 'prec': 2, 'unit': '%',
                'lolim': 0.0, 'hilim': 100.1},
            'FOFBDownloadKicksPerc-RB': {
                'type': 'float', 'value': 4.0, 'prec': 2, 'unit': '%',
                'lolim': 0.0, 'hilim': 100.1},
            'FOFBDownloadKicks-Sel': {
                'type': 'enum', 'value': self.DsblEnbl.Enbl,
                'enums': self.DsblEnbl._fields},
            'FOFBDownloadKicks-Sts': {
                'type': 'enum', 'value': self.DsblEnbl.Enbl,
                'enums': self.DsblEnbl._fields},
            'FOFBDownloadKicks-Mon': {
                'type': 'enum', 'value': self.DsblEnbl.Enbl,
                'enums': self.DsblEnbl._fields},
            'FOFBUpdateRefOrbPerc-SP': {
                'type': 'float', 'value': 0.0, 'prec': 2, 'unit': '%',
                'lolim': -100.1, 'hilim': 100.1},
            'FOFBUpdateRefOrbPerc-RB': {
                'type': 'float', 'value': 0.0, 'prec': 2, 'unit': '%',
                'lolim': -100.1, 'hilim': 100.1},
            'FOFBUpdateRefOrb-Sel': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'FOFBUpdateRefOrb-Sts': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'FOFBUpdateRefOrb-Mon': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'FOFBNullSpaceProj-Sel': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'FOFBNullSpaceProj-Sts': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'FOFBNullSpaceProj-Mon': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'FOFBZeroDistortionAtBPMs-Sel': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'FOFBZeroDistortionAtBPMs-Sts': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'FOFBZeroDistortionAtBPMs-Mon': {
                'type': 'enum', 'value': self.DsblEnbl.Dsbl,
                'enums': self.DsblEnbl._fields},
            'DriveFreqDivisor-SP': {
                'type': 'int', 'value': 12, 'unit': 'Div',
                'lolim': 0, 'hilim': 1000},
            'DriveFreqDivisor-RB': {
                'type': 'int', 'value': 12, 'unit': 'Div',
                'lolim': 0, 'hilim': 1000},
            'DriveFrequency-Mon': {
                'type': 'float', 'value': self.BPMsFreq/12, 'prec': 3,
                'unit': 'Hz', 'lolim': 0, 'hilim': 1000},
            'DriveNrCycles-SP': {
                'type': 'int', 'value': 10, 'unit': 'number',
                'lolim': 0, 'hilim': 1000},
            'DriveNrCycles-RB': {
                'type': 'int', 'value': 10, 'unit': 'number',
                'lolim': 0, 'hilim': 1000},
            'DriveDuration-Mon': {
                'type': 'float', 'value': 12/self.BPMsFreq*10, 'prec': 1,
                'unit': 's', 'lolim': 0, 'hilim': 1000},
            'DriveAmplitude-SP': {
                'type': 'float', 'value': 5, 'prec': 2, 'unit': 'urad or Hz',
                'lolim': -100, 'hilim': 100},
            'DriveAmplitude-RB': {
                'type': 'float', 'value': 5, 'prec': 2, 'unit': 'urad or Hz',
                'lolim': -100, 'hilim': 100},
            'DrivePhase-SP': {
                'type': 'float', 'value': 0, 'prec': 3, 'unit': 'deg',
                'lolim': -360, 'hilim': 360},
            'DrivePhase-RB': {
                'type': 'float', 'value': 0, 'prec': 3, 'unit': 'deg',
                'lolim': -360, 'hilim': 360},
            'DriveCorrIndex-SP': {
                'type': 'int', 'value': 0, 'unit': '#',
                'lolim': -self.nr_corrs, 'hilim': self.nr_corrs},
            'DriveCorrIndex-RB': {
                'type': 'int', 'value': 0, 'unit': '#',
                'lolim': -self.nr_corrs, 'hilim': self.nr_corrs},
            'DriveBPMIndex-SP': {
                'type': 'int', 'value': 0, 'unit': '#',
                'lolim': -self.nr_bpms*2, 'hilim': self.nr_bpms*2},
            'DriveBPMIndex-RB': {
                'type': 'int', 'value': 0, 'unit': '#',
                'lolim': -self.nr_bpms*2, 'hilim': self.nr_bpms*2},
            'DriveType-Sel': {
                'type': 'enum', 'enums': self.DriveType._fields,
                'unit': 'Sine_Square_Impulse', 'value': 0},
            'DriveType-Sts': {
                'type': 'enum', 'enums': self.DriveType._fields,
                'unit': 'Sine_Square_Impulse', 'value': 0},
            'DriveState-Sel': {
                'type': 'enum', 'enums': self.DriveState._fields,
                'unit': 'Open_Closed', 'value': 0},
            'DriveState-Sts': {
                'type': 'enum', 'enums': self.DriveState._fields,
                'unit': 'Open_Closed', 'value': 0},
            'DriveData-Mon': {
                'type': 'float', 'unit': '(s, urad, um)',
                'count': self.MAX_DRIVE_DATA, 'value': self.MAX_DRIVE_DATA*[0]}
            }
        dbase = super().get_sofb_database(prefix=prefix)
        dbase.update(self._add_prefix(db_ring, prefix))
        return dbase

    def get_corrs_database(self, prefix=''):
        """Return SOFB correctors database."""
        db_ring = {
            'CorrSync-Sel': {
                'type': 'enum', 'enums': self.CorrSync._fields,
                'unit': 'Off_Event_Clock', 'value': self.CorrSync.Off},
            'CorrSync-Sts': {
                'type': 'enum', 'enums': self.CorrSync._fields,
                'unit': 'Off_Event_Clock', 'value': self.CorrSync.Off},
            }
        dbase = super().get_corrs_database(prefix=prefix)
        dbase.update(self._add_prefix(db_ring, prefix))
        return dbase

    def get_orbit_database(self, prefix=''):
        """Return Orbit database."""
        nbpm = self.nr_bpms
        pvs_ring = ['SlowOrbX-Mon', 'SlowOrbY-Mon']
        db_ring = dict()
        prop = {
            'type': 'float', 'unit': 'um', 'count': nbpm, 'value': nbpm*[0]}
        for k in pvs_ring:
            db_ring[k] = _dcopy(prop)
        db_ring.update({
            'SOFBMode-Sel': {
                'type': 'enum', 'unit': 'SlowOrb_MultiTurn_SinglePass',
                'value': 0, 'enums': self.SOFBMode._fields},
            'SOFBMode-Sts': {
                'type': 'enum', 'unit': 'SlowOrb_MultiTurn_SinglePass',
                'value': 0, 'enums': self.SOFBMode._fields},
            })
        dbase = super().get_orbit_database(prefix=prefix)
        dbase.update(self._add_prefix(db_ring, prefix))
        return dbase


class SOFBFactory:
    """Factory class for SOFB objects."""

    @staticmethod
    def create(acc):
        """Return appropriate SOFB object."""
        acc = acc.upper()
        if acc == 'SI':
            return SOFBSI(acc)
        elif acc in _et.RINGS:
            return SOFBRings(acc)
        elif acc in _et.TLINES:
            return SOFBTLines(acc)
        else:
            raise ValueError('Invalid accelerator name "{}"'.format(acc))
