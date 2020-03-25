"""Define PVs, constants and properties of OrbitCorr SoftIOCs."""
import os as _os
from copy import deepcopy as _dcopy

from ..namesys import SiriusPVName as _PVName
from ..util import get_namedtuple as _get_namedtuple
from ..search import MASearch as _MASearch, BPMSearch as _BPMSearch, \
    LLTimeSearch as _TISearch, HLTimeSearch as _HLTISearch, \
    PSSearch as _PSSearch

from . import bpms as _csbpm
from . import util as _cutil
from . import timesys as _cstiming


# --- Enumeration Types ---

class ETypes(_cutil.ETypes):
    """Local enumerate types."""

    ENBL_RF = _cutil.ETypes.OFF_ON
    ORB_MODE_RINGS = ('Offline', 'SlowOrb', 'MultiTurn', 'SinglePass')
    ORB_MODE_TLINES = ('Offline', 'SinglePass')
    SMOOTH_METH = ('Average', 'Median')
    SPASS_METHOD = ('FromBPMs', 'Calculated')
    SPASS_BG_CTRL = ('Acquire', 'Reset')
    SPASS_BG_STS = ('Empty', 'Acquiring', 'Acquired')
    SPASS_USE_BG = ('NotUsing', 'Using')
    APPLY_CORR_TLINES = ('CH', 'CV', 'All')
    APPLY_CORR_SI = ('CH', 'CV', 'RF', 'All')
    ORB_ACQ_CHAN = ('Monit1', 'FOFB', 'TbT', 'ADC', 'ADCSwp')
    MEAS_RMAT_CMD = ('Start', 'Stop', 'Reset')
    MEAS_RMAT_MON = ('Idle', 'Measuring', 'Completed', 'Aborted')
    TLINES = ('TB', 'TS')
    RINGS = ('BO', 'SI')
    ACCELERATORS = TLINES + RINGS

    STS_LBLS_CORR_TLINES = (
        'CHCVConnected', 'CHCVModeConfigured', 'CHCVPwrStateOn')
    STS_LBLS_CORR_RINGS = STS_LBLS_CORR_TLINES + (
        'TimingConnected', 'TimingConfigured')
    STS_LBLS_CORR_SI = STS_LBLS_CORR_RINGS + ('RFConnected', 'RFPwrStateOn')
    STS_LBLS_ORB = (
        'TimingConnected', 'TimingConfigured', 'BPMsConnected',
        'BPMsEnabled', 'BPMsConfigured')
    STS_LBLS_GLOB = ('Ok', 'NotOk')


_et = ETypes  # syntactic sugar


# --- Const class ---

class ConstTLines(_cutil.Const):
    """Const class defining transport lines orbitcorr constants."""

    EVG_NAME = _TISearch.get_evg_name()
    ORBIT_CONVERSION_UNIT = 1/1000  # from nm to um
    MAX_MT_ORBS = 4000
    MAX_RINGSZ = 5
    TINY_KICK = 1e-3  # urad

    EnbldDsbld = _cutil.Const.register('EnbldDsbld', _et.DSBLD_ENBLD)
    TrigAcqCtrl = _csbpm.AcqEvents
    TrigAcqChan = _cutil.Const.register('TrigAcqChan', _et.ORB_ACQ_CHAN)
    TrigAcqDataChan = _csbpm.AcqChan
    TrigAcqDataSel = _csbpm.AcqDataTyp
    TrigAcqDataPol = _csbpm.Polarity
    TrigAcqRepeat = _csbpm.AcqRepeat
    TrigAcqTrig = _cutil.Const.register('TrigAcqTrig', ('External', 'Data'))
    SmoothMeth = _cutil.Const.register('SmoothMeth', _et.SMOOTH_METH)
    SPassBgCtrl = _cutil.Const.register('SPassBgCtrl', _et.SPASS_BG_CTRL)
    SPassBgSts = _cutil.Const.register('SPassBgSts', _et.SPASS_BG_STS)
    SPassUseBg = _cutil.Const.register('SPassUseBg', _et.SPASS_USE_BG)
    MeasRespMatCmd = _cutil.Const.register('MeasRespMatCmd', _et.MEAS_RMAT_CMD)
    MeasRespMatMon = _cutil.Const.register('MeasRespMatMon', _et.MEAS_RMAT_MON)
    TransportLines = _cutil.Const.register(
        'TransportLines', _et.TLINES, (0, 1))
    Rings = _cutil.Const.register('Rings', _et.RINGS, (2, 3))
    Accelerators = _cutil.Const.register('Accelerators', _et.ACCELERATORS)

    SOFBMode = _cutil.Const.register('SOFBMode', _et.ORB_MODE_TLINES)
    SyncWithInj = _cutil.Const.register('SyncWithInj', _et.OFF_ON)
    ApplyDelta = _cutil.Const.register('ApplyDelta', _et.APPLY_CORR_TLINES)
    StsLblsCorr = _cutil.Const.register(
        'StsLblsCorr', _et.STS_LBLS_CORR_TLINES)
    StsLblsOrb = _cutil.Const.register('StsLblsOrb', _et.STS_LBLS_ORB)
    StsLblsGlob = _cutil.Const.register('StsLblsGlob', _et.STS_LBLS_GLOB)

    ClosedLoop = _cutil.Const.register('ClosedLoop', _et.OFF_ON)


class ConstRings(ConstTLines):
    """Const class defining rings orbitcorr constants."""

    SOFBMode = _cutil.Const.register('SOFBMode', _et.ORB_MODE_RINGS)
    StsLblsCorr = _cutil.Const.register('StsLblsCorr', _et.STS_LBLS_CORR_RINGS)


class ConstSI(ConstRings):
    """Const class defining rings orbitcorr constants."""

    ApplyDelta = _cutil.Const.register('ApplyDelta', _et.APPLY_CORR_SI)
    StsLblsCorr = _cutil.Const.register('StsLblsCorr', _et.STS_LBLS_CORR_SI)
    CorrSync = _cutil.Const.register('CorrSync', _et.OFF_ON)

    # TODO: use correct name for the RF generator
    RF_GEN_NAME = 'AS-Glob:RF-Gen'
    EnblRF = _cutil.Const.register('EnblRF', _et.ENBL_RF)


# --- Database classes ---

class SOFBTLines(ConstTLines):
    """SOFB class for TLines."""

    def __init__(self, acc):
        """Init1 method."""
        self.acc = acc.upper()
        self.acc_idx = self.Accelerators._fields.index(self.acc)
        self.BPM_NAMES = _BPMSearch.get_names({'sec': acc})
        self.CH_NAMES = _PSSearch.get_psnames(
            {'sec': acc, 'dis': 'PS', 'dev': 'CH'})
        if self.acc == 'TS':
            self.CH_NAMES = [_PVName('TS-01:PU-EjeSeptG'), ] + self.CH_NAMES
        self.CV_NAMES = _PSSearch.get_psnames(
            {'sec': acc, 'dis': 'PS', 'dev': 'CV'})
        self.BPM_NICKNAMES = _BPMSearch.get_nicknames(self.BPM_NAMES)
        self.CH_NICKNAMES = _PSSearch.get_psnicknames(self.CH_NAMES)
        if self.acc == 'TS':
            self.CH_NICKNAMES[0] = 'EjeseptG'
        self.CV_NICKNAMES = _PSSearch.get_psnicknames(self.CV_NAMES)
        self.BPM_POS = _BPMSearch.get_positions(self.BPM_NAMES)

        func = lambda x: x.substitute(dis='MA' if x.dis=='PS' else 'PM')
        self.CH_POS = _MASearch.get_mapositions(map(func, self.CH_NAMES))
        self.CV_POS = _MASearch.get_mapositions(map(func, self.CV_NAMES))
        self.NR_CH = len(self.CH_NAMES)
        self.NR_CV = len(self.CV_NAMES)
        self.NR_CHCV = self.NR_CH + self.NR_CV
        self.NR_BPMS = len(self.BPM_NAMES)
        ext = acc.lower() + 'orb'
        ioc_fol = acc.lower() + '-ap-sofb'
        ioc_fol = _os.path.join('/home', 'sirius', 'iocs-log', ioc_fol, 'data')
        self.REFORBFNAME = _os.path.join(ioc_fol, 'ref_orbit.'+ext)
        ext = acc.lower() + 'respmat'
        self.RESPMAT_FILENAME = _os.path.join(ioc_fol, 'respmat.'+ext)

        self.NR_CORRS = self.NR_CHCV + 1 if acc == 'SI' else self.NR_CHCV

        self.TRIGGER_ACQ_NAME = self.acc + '-Fam:TI-BPM'
        if self.acc == 'SI':
            self.TRIGGER_COR_NAME = self.acc + '-Glob:TI-Mags-Corrs'
            self.EVT_COR_NAME = 'Orb' + self.acc

        self.EVT_ACQ_NAME = 'Dig' + self.acc
        self.MTX_SZ = self.NR_CORRS * (2 * self.NR_BPMS)
        self.NR_SING_VALS = min(self.NR_CORRS, 2 * self.NR_BPMS)
        self.C0 = 21.2477 if self.acc == 'TB' else 26.8933  # in meters
        self.T0 = self.C0 / 299792458  # in seconds

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
        dbase = _cutil.add_pvslist_cte(dbase)
        return dbase

    def get_sofb_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        dbase = {
            'Log-Mon': {'type': 'char', 'value': '', 'count': 200},
            'ClosedLoop-Sel': {
                'type': 'enum', 'enums': self.ClosedLoop._fields, 'value': 0},
            'ClosedLoop-Sts': {
                'type': 'enum', 'enums': self.ClosedLoop._fields, 'value': 0},
            'ClosedLoopFreq-SP': {
                'type': 'float', 'value': 1, 'unit': 'Hz', 'prec': 3,
                'lolim': 1e-3, 'hilim': 20},
            'ClosedLoopFreq-RB': {
                'type': 'float', 'value': 1, 'prec': 2, 'unit': 'Hz'},
            'MeasRespMat-Cmd': {
                'type': 'enum', 'value': 0,
                'enums': self.MeasRespMatCmd._fields},
            'MeasRespMat-Mon': {
                'type': 'enum', 'value': 0,
                'enums': self.MeasRespMatMon._fields},
            'MeasRespMatKickCH-SP': {
                'type': 'float', 'value': 80, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatKickCH-RB': {
                'type': 'float', 'value': 80, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatKickCV-SP': {
                'type': 'float', 'value': 80, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatKickCV-RB': {
                'type': 'float', 'value': 80, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatWait-SP': {
                'type': 'float', 'value': 1, 'unit': 's', 'prec': 3,
                'lolim': 0.005, 'hilim': 100},
            'MeasRespMatWait-RB': {
                'type': 'float', 'value': 1, 'unit': 's', 'prec': 3,
                'lolim': 0.005, 'hilim': 100},
            'CalcDelta-Cmd': {
                'type': 'int', 'value': 0, 'unit': 'Calculate kicks'},
            'DeltaFactorCH-SP': {
                'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
                'lolim': -10000, 'hilim': 10000},
            'DeltaFactorCH-RB': {
                'type': 'float', 'value': 100, 'prec': 2, 'unit': '%'},
            'DeltaFactorCV-SP': {
                'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
                'lolim': -10000, 'hilim': 10000},
            'DeltaFactorCV-RB': {
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
                'type': 'float', 'value': 300, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickCH-RB': {
                'type': 'float', 'value': 300, 'prec': 3, 'unit': 'urad',
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickCV-SP': {
                'type': 'float', 'value': 300, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickCV-RB': {
                'type': 'float', 'value': 300, 'prec': 3, 'unit': 'urad',
                'lolim': 0, 'hilim': 10000},
            'DeltaKickCH-SP': {
                'type': 'float', 'count': self.NR_CH, 'value': self.NR_CH*[0],
                'unit': 'urad'},
            'DeltaKickCH-RB': {
                'type': 'float', 'count': self.NR_CH, 'value': self.NR_CH*[0],
                'unit': 'urad'},
            'DeltaKickCV-SP': {
                'type': 'float', 'count': self.NR_CV, 'value': self.NR_CV*[0],
                'unit': 'urad'},
            'DeltaKickCV-RB': {
                'type': 'float', 'count': self.NR_CV, 'value': self.NR_CV*[0],
                'unit': 'urad'},
            'ApplyDelta-Cmd': {
                'type': 'enum', 'enums': self.ApplyDelta._fields, 'value': 0,
                'unit': 'Apply last calculated kicks.'},
            'Status-Mon': {
                'type': 'enum', 'value': 1,
                'enums': self.StsLblsGlob._fields}
            }
        return self._add_prefix(dbase, prefix)

    def get_corrs_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        dbase = {
            'KickAcqRate-SP': {
                'type': 'float', 'unit': 'Hz', 'value': 2,
                'hilim': 20, 'lolim': 0.01, 'prec': 2},
            'KickAcqRate-RB': {
                'type': 'float', 'unit': 'Hz', 'value': 2,
                'hilim': 20, 'lolim': 0.01, 'prec': 2},
            'KickCH-Mon': {
                'type': 'float', 'count': self.NR_CH, 'value': self.NR_CH*[0],
                'unit': 'urad'},
            'KickCV-Mon': {
                'type': 'float', 'count': self.NR_CV, 'value': self.NR_CV*[0],
                'unit': 'urad'},
            'CorrConfig-Cmd': {'type': 'int', 'value': 0},
            'CHPosS-Cte': {
                'type': 'float', 'unit': 'm', 'count': self.NR_CH,
                'value': self.CH_POS},
            'CVPosS-Cte': {
                'type': 'float', 'unit': 'm', 'count': self.NR_CV,
                'value': self.CV_POS},
            'CHNickName-Cte': {
                'type': 'string', 'unit': 'shortname for the chs.',
                'count': self.NR_CH, 'value': self.CH_NICKNAMES},
            'CVNickName-Cte': {
                'type': 'string', 'unit': 'shortname for the cvs.',
                'count': self.NR_CV, 'value': self.CV_NICKNAMES},
            'CorrStatus-Mon': {'type': 'int', 'value': 0b1111111},
            'CorrStatusLabels-Cte': {
                'type': 'string', 'count': len(self.StsLblsCorr._fields),
                'value': self.StsLblsCorr._fields}
            }
        return self._add_prefix(dbase, prefix)

    def get_orbit_database(self, prefix=''):
        """Return Orbit database."""
        nbpm = self.NR_BPMS
        evt = self.EVT_ACQ_NAME
        pvs = [
            'RefOrbX-SP', 'RefOrbX-RB',
            'RefOrbY-SP', 'RefOrbY-RB',
            'SPassOrbX-Mon', 'SPassOrbY-Mon',
            'SPassSum-Mon',
            'OfflineOrbX-SP', 'OfflineOrbX-RB',
            'OfflineOrbY-SP', 'OfflineOrbY-RB',
            'BPMOffsetX-Mon', 'BPMOffsetY-Mon',
            ]
        dbase = dict()
        prop = {
            'type': 'float', 'unit': 'um', 'count': self.MAX_RINGSZ*nbpm,
            'value': nbpm*[0]}
        for k in pvs:
            dbase[k] = _dcopy(prop)
        dbase.update({
            'SOFBMode-Sel': {
                'type': 'enum', 'unit': 'Change orbit acquisition mode.',
                'value': self.SOFBMode.Offline,
                'enums': self.SOFBMode._fields},
            'SOFBMode-Sts': {
                'type': 'enum', 'unit': 'Change orbit acquisition mode.',
                'value': self.SOFBMode.Offline,
                'enums': self.SOFBMode._fields},
            'SyncWithInjection-Sel': {
                'type': 'enum', 'unit': 'Sync orbit acq. with injection',
                'value': self.SyncWithInj.On,
                'enums': self.SyncWithInj._fields},
            'SyncWithInjection-Sts': {
                'type': 'enum', 'unit': 'Sync orbit acq. with injection',
                'value': self.SyncWithInj.On,
                'enums': self.SyncWithInj._fields},
            'TrigAcqConfig-Cmd': {'type': 'int', 'value': 0},
            'TrigAcqCtrl-Sel': {
                'type': 'enum', 'unit': 'Start/Stop/Abort acquistion.',
                'value': self.TrigAcqCtrl.Stop,
                'enums': self.TrigAcqCtrl._fields},
            'TrigAcqCtrl-Sts': {
                'type': 'enum', 'unit': 'Start/Stop/Reset acquistion.',
                'value': self.TrigAcqCtrl.Stop,
                'enums': self.TrigAcqCtrl._fields},
            'TrigAcqChan-Sel': {
                'type': 'enum', 'unit': 'Change orbit acquisition Channel.',
                'value': self.TrigAcqChan.ADC,
                'enums': self.TrigAcqChan._fields},
            'TrigAcqChan-Sts': {
                'type': 'enum', 'unit': 'Change orbit acquisition Channel.',
                'value': self.TrigAcqChan.ADC,
                'enums': self.TrigAcqChan._fields},
            'TrigDataChan-Sel': {
                'type': 'enum', 'unit': 'Set Data-driven trigger Channel.',
                'value': self.TrigAcqDataChan.ADC,
                'enums': self.TrigAcqDataChan._fields},
            'TrigDataChan-Sts': {
                'type': 'enum', 'unit': 'Set Data-driven trigger Channel.',
                'value': self.TrigAcqDataChan.ADC,
                'enums': self.TrigAcqDataChan._fields},
            'TrigAcqTrigger-Sel': {
                'type': 'enum', 'unit': 'If trigger is external or by data.',
                'value': self.TrigAcqTrig.External,
                'enums': self.TrigAcqTrig._fields},
            'TrigAcqTrigger-Sts': {
                'type': 'enum', 'unit': 'If trigger is external or by data.',
                'value': self.TrigAcqTrig.External,
                'enums': self.TrigAcqTrig._fields},
            'TrigAcqRepeat-Sel': {
                'type': 'enum', 'unit': 'Auto arm to repeat acquisition.',
                'value': self.TrigAcqRepeat.Normal,
                'enums': self.TrigAcqRepeat._fields},
            'TrigAcqRepeat-Sts': {
                'type': 'enum', 'unit': 'Auto arm to repeat acquisition.',
                'value': self.TrigAcqRepeat.Normal,
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
                'type': 'int', 'unit': '', 'value': 360,
                'hilim': 20000, 'lolim': 0},
            'TrigNrSamplesPost-RB': {
                'type': 'int', 'unit': '', 'value': 360,
                'hilim': 20000, 'lolim': 0},
            'TrigDataSel-Sel': {
                'type': 'enum', 'unit': 'Set Data trigger Selection.',
                'value': self.TrigAcqDataSel.A,
                'enums': self.TrigAcqDataSel._fields},
            'TrigDataSel-Sts': {
                'type': 'enum', 'unit': 'Set Data trigger Selection.',
                'value': self.TrigAcqDataSel.A,
                'enums': self.TrigAcqDataSel._fields},
            'TrigDataThres-SP': {
                'type': 'int', 'value': 1,
                'unit': 'set data trigger threshold',
                'lolim': -1000, 'hilim': 2**31-1},
            'TrigDataThres-RB': {
                'type': 'int', 'value': 1,
                'unit': 'set data trigger threshold',
                'lolim': -1000, 'hilim': 2**31-1},
            'TrigDataHyst-SP': {
                'type': 'int', 'value': 0,
                'unit': 'set data trigger hysteresis',
                'lolim': 0, 'hilim': 2**31-1},
            'TrigDataHyst-RB': {
                'type': 'int', 'value': 0,
                'unit': 'set data trigger hysteresis',
                'lolim': 0, 'hilim': 2**31-1},
            'TrigDataPol-Sel': {
                'type': 'enum', 'unit': 'Set Data trigger Polarity.',
                'value': self.TrigAcqDataPol.Positive,
                'enums': self.TrigAcqDataPol._fields},
            'TrigDataPol-Sts': {
                'type': 'enum', 'unit': 'Set Data trigger Polarity.',
                'value': self.TrigAcqDataPol.Positive,
                'enums': self.TrigAcqDataPol._fields},
            'OrbAcqRate-SP': {
                'type': 'float', 'unit': 'Hz', 'value': 10,
                'hilim': 20, 'lolim': 0.01, 'prec': 2},
            'OrbAcqRate-RB': {
                'type': 'float', 'unit': 'Hz', 'value': 10,
                'hilim': 20, 'lolim': 0.01, 'prec': 2},
            'SmoothNrPts-SP': {
                'type': 'int', 'value': 1,
                'unit': 'number of points for smoothing',
                'lolim': 1, 'hilim': 500},
            'SmoothNrPts-RB': {
                'type': 'int', 'value': 1,
                'unit': 'number of points for smoothing',
                'lolim': 1, 'hilim': 500},
            'SmoothMethod-Sel': {
                'type': 'enum', 'value': self.SmoothMeth.Average,
                'enums': _et.SMOOTH_METH},
            'SmoothMethod-Sts': {
                'type': 'enum', 'value': self.SmoothMeth.Average,
                'enums': _et.SMOOTH_METH},
            'SmoothReset-Cmd': {
                'type': 'int', 'value': 0, 'unit': 'Reset orbit buffer'},
            'BufferCount-Mon': {
                'type': 'int', 'value': 0, 'unit': 'Current buffer size'},
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
            'SPassBgCtrl-Cmd': {
                'type': 'enum', 'value': self.SPassBgCtrl.Acquire,
                'enums': self.SPassBgCtrl._fields},
            'SPassBgSts-Mon': {
                'type': 'enum', 'value': self.SPassBgSts.Empty,
                'enums': self.SPassBgSts._fields},
            'SPassUseBg-Sel': {
                'type': 'enum', 'value': self.SPassUseBg.NotUsing,
                'enums': self.SPassUseBg._fields},
            'SPassUseBg-Sts': {
                'type': 'enum', 'value': self.SPassUseBg.NotUsing,
                'enums': self.SPassUseBg._fields},
            'BPMPosS-Mon': {
                'type': 'float', 'unit': 'm', 'count': self.MAX_RINGSZ*nbpm,
                'value': self.BPM_POS, 'prec': 2},
            'BPMNickName-Cte': {
                'type': 'string', 'unit': 'shortname for the bpms.',
                'count': self.MAX_RINGSZ*nbpm, 'value': self.BPM_NICKNAMES},
            'OrbStatus-Mon': {'type': 'int', 'value': 0b00000},
            'OrbStatusLabels-Cte': {
                'type': 'string', 'count': len(self.StsLblsOrb._fields),
                'value': self.StsLblsOrb._fields},
            })
        return self._add_prefix(dbase, prefix)

    def get_respmat_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        dbase = {
            'RespMat-SP': {
                'type': 'float', 'count': self.MAX_RINGSZ*self.MTX_SZ,
                'value': self.MTX_SZ*[0],
                'unit': '(BH, BV)(um) x (CH, CV, RF)(urad, Hz)'},
            'RespMat-RB': {
                'type': 'float', 'count': self.MAX_RINGSZ*self.MTX_SZ,
                'value': self.MTX_SZ*[0],
                'unit': '(BH, BV)(um) x (CH, CV, RF)(urad, Hz)'},
            'SingValues-Mon': {
                'type': 'float', 'count': self.NR_SING_VALS,
                'value': self.NR_SING_VALS*[0],
                'unit': 'Singular values of the matrix in use'},
            'InvRespMat-Mon': {
                'type': 'float', 'count': self.MAX_RINGSZ*self.MTX_SZ,
                'value': self.MTX_SZ*[0],
                'unit': '(CH, CV, RF)(urad, Hz) x (BH, BV)(um)'},
            'CHEnblList-SP': {
                'type': 'int', 'count': self.NR_CH, 'value': self.NR_CH*[1],
                'unit': 'CHs used in correction'},
            'CHEnblList-RB': {
                'type': 'int', 'count': self.NR_CH, 'value': self.NR_CH*[1],
                'unit': 'CHs used in correction'},
            'CVEnblList-SP': {
                'type': 'int', 'count': self.NR_CV, 'value': self.NR_CV*[1],
                'unit': 'CVs used in correction'},
            'CVEnblList-RB': {
                'type': 'int', 'count': self.NR_CV, 'value': self.NR_CV*[1],
                'unit': 'CVs used in correction'},
            'BPMXEnblList-SP': {
                'type': 'int', 'count': self.MAX_RINGSZ*self.NR_BPMS,
                'value': self.NR_BPMS*[1],
                'unit': 'BPMX used in correction'},
            'BPMXEnblList-RB': {
                'type': 'int', 'count': self.MAX_RINGSZ*self.NR_BPMS,
                'value': self.NR_BPMS*[1],
                'unit': 'BPMX used in correction'},
            'BPMYEnblList-SP': {
                'type': 'int', 'count': self.MAX_RINGSZ*self.NR_BPMS,
                'value': self.NR_BPMS*[1],
                'unit': 'BPMY used in correction'},
            'BPMYEnblList-RB': {
                'type': 'int', 'count': self.MAX_RINGSZ*self.NR_BPMS,
                'value': self.NR_BPMS*[1],
                'unit': 'BPMY used in correction'},
            'NrSingValues-SP': {
                'type': 'int', 'value': self.NR_SING_VALS,
                'lolim': 1, 'hilim': self.NR_SING_VALS,
                'unit': 'Maximum number of SV to use'},
            'NrSingValues-RB': {
                'type': 'int', 'value': self.NR_SING_VALS,
                'lolim': 1, 'hilim': self.NR_SING_VALS,
                'unit': 'Maximum number of SV to use'},
            'DeltaKickCH-Mon': {
                'type': 'float', 'count': self.NR_CH, 'value': self.NR_CH*[0],
                'unit': 'urad'},
            'DeltaKickCV-Mon': {
                'type': 'float', 'count': self.NR_CV, 'value': self.NR_CV*[0],
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
        self.C0 = 496.8  # in meter
        self.T0 = self.C0 / 299792458  # in seconds

    def get_sofb_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        db_ring = {
            'RingSize-SP': {
                'type': 'int', 'value': 1, 'lolim': 0,
                'hilim': self.MAX_RINGSZ+1,
                'unit': 'Nr Times to extend the ring'},
            'RingSize-RB': {
                'type': 'int', 'value': 1, 'lolim': 0,
                'hilim': self.MAX_RINGSZ+1,
                'unit': 'Nr Times to extend the ring'},
            }
        dbase = super().get_sofb_database(prefix=prefix)
        dbase.update(self._add_prefix(db_ring, prefix))
        return dbase

    def get_orbit_database(self, prefix=''):
        """Return Orbit database."""
        nbpm = self.NR_BPMS
        pvs_ring = [
            'SlowOrbX-Mon', 'SlowOrbY-Mon',
            'MTurnIdxOrbX-Mon', 'MTurnIdxOrbY-Mon',
            'MTurnIdxSum-Mon',
            ]
        db_ring = dict()
        prop = {
            'type': 'float', 'unit': 'um', 'count': self.MAX_RINGSZ*nbpm,
            'value': nbpm*[0]}
        for k in pvs_ring:
            db_ring[k] = _dcopy(prop)
        db_ring.update({
            'MTurnSyncTim-Sel': {
                'type': 'enum', 'value': self.EnbldDsbld.Enbld,
                'enums': self.EnbldDsbld._fields},
            'MTurnSyncTim-Sts': {
                'type': 'enum', 'value': self.EnbldDsbld.Enbld,
                'enums': self.EnbldDsbld._fields},
            'MTurnUseMask-Sel': {
                'type': 'enum', 'value': self.EnbldDsbld.Dsbld,
                'enums': self.EnbldDsbld._fields},
            'MTurnUseMask-Sts': {
                'type': 'enum', 'value': self.EnbldDsbld.Dsbld,
                'enums': self.EnbldDsbld._fields},
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
        evts = _HLTISearch.get_hl_trigger_allowed_evts(self.TRIGGER_COR_NAME)
        vals = _cstiming.get_hl_trigger_database(self.TRIGGER_COR_NAME)
        vals = tuple([vals['Src-Sel']['enums'].index(evt) for evt in evts])
        self.CorrExtEvtSrc = _get_namedtuple('CorrExtEvtSrc', evts, vals)
        self.C0 = 518.396  # in meter
        self.T0 = self.C0 / 299792458  # in seconds

    def get_sofb_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        db_ring = {
            'MeasRespMatKickRF-SP': {
                'type': 'float', 'value': 50, 'unit': 'Hz', 'prec': 2,
                'lolim': 1, 'hilim': 1000},
            'MeasRespMatKickRF-RB': {
                'type': 'float', 'value': 50, 'unit': 'Hz', 'prec': 2,
                'lolim': 1, 'hilim': 1000},
            'DeltaFactorRF-SP': {
                'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
                'lolim': -1000, 'hilim': 1000},
            'DeltaFactorRF-RB': {
                'type': 'float', 'value': 100, 'prec': 2, 'unit': '%'},
            'MaxKickRF-SP': {
                'type': 'float', 'value': 499663000, 'unit': 'Hz', 'prec': 2,
                'lolim': 499660000, 'hilim': 499665000},
            'MaxKickRF-RB': {
                'type': 'float', 'value': 499663000, 'unit': 'Hz', 'prec': 2,
                'lolim': 499660000, 'hilim': 499665000},
            'MaxDeltaKickRF-SP': {
                'type': 'float', 'value': 500, 'unit': 'Hz', 'prec': 2,
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickRF-RB': {
                'type': 'float', 'value': 500, 'prec': 2, 'unit': 'Hz',
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
        """Return OpticsCorr-Chrom Soft IOC database."""
        db_ring = {
            'CorrSync-Sel': {
                'type': 'enum', 'enums': self.CorrSync._fields,
                'value': self.CorrSync.Off},
            'CorrSync-Sts': {
                'type': 'enum', 'enums': self.CorrSync._fields,
                'value': self.CorrSync.Off},
            'KickRF-Mon': {
                'type': 'float', 'value': 1, 'unit': 'Hz', 'prec': 2},
            }
        dbase = super().get_corrs_database(prefix=prefix)
        dbase.update(self._add_prefix(db_ring, prefix))
        return dbase

    def get_respmat_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        db_ring = {
            'RFEnbl-Sel': {
                'type': 'enum', 'enums': self.EnblRF._fields, 'value': 0,
                'unit': 'If RF is used in correction'},
            'RFEnbl-Sts': {
                'type': 'enum', 'enums': self.EnblRF._fields, 'value': 0,
                'unit': 'If RF is used in correction'},
            'DeltaKickRF-Mon': {
                'type': 'float', 'value': 0, 'prec': 2, 'unit': 'Hz'},
            }
        dbase = super().get_respmat_database(prefix=prefix)
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
