"""Define PVs, constants and properties of OrbitCorr SoftIOCs."""
import os as _os
from copy import deepcopy as _dcopy
from siriuspy.util import get_namedtuple as _get_namedtuple
import siriuspy.csdevice.bpms as _csbpm
from siriuspy.csdevice import util as _cutil
from siriuspy.csdevice import timesys as _cstiming
from siriuspy.search import MASearch as _MASearch, BPMSearch as _BPMSearch, \
    LLTimeSearch as _TISearch, HLTimeSearch as _HLTISearch


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
    APPLY_CORR_RINGS = ('CH', 'CV', 'RF', 'All')
    APPLY_CORR_TLINES = ('CH', 'CV', 'All')
    ORB_ACQ_CHAN = ('Monit1', 'FOFB', 'TbT', 'ADC')
    MEAS_RMAT_CMD = ('Start', 'Stop', 'Reset')
    MEAS_RMAT_MON = ('Idle', 'Measuring', 'Completed', 'Aborted')
    TLINES = ('TB', 'TS')
    RINGS = ('BO', 'SI')
    ACCELERATORS = TLINES + RINGS

    STS_LBLS_CORR_TLINES = (
        'CHCVConnected', 'CHCVModeConfigured', 'CHCVPwrStateOn')
    STS_LBLS_CORR_RINGS = (
        'CHCVConnected', 'CHCVModeConfigured', 'CHCVPwrStateOn',
        'TimingConnected', 'TimingConfigured', 'RFConnected',
        'RFPwrStateOn')
    STS_LBLS_ORB = (
        'TimingConnected', 'TimingConfigured', 'BPMsConnected',
        'BPMsEnabled', 'BPMsConfigured')
    STS_LBLS_GLOB = ('Ok', 'NotOk')


_et = ETypes  # syntactic sugar


# --- Const class ---

class ConstTLines(_cutil.Const):
    """Const class defining transport lines orbitcorr constants."""

    EVG_NAME = _TISearch.get_device_names({'dev': 'EVG'})[0]
    ORBIT_CONVERSION_UNIT = 1/1000  # from nm to um
    MAX_MT_ORBS = 4000
    MAX_RINGSZ = 5

    EnbldDsbld = _cutil.Const.register('EnbldDsbld', _et.DSBLD_ENBLD)
    TrigAcqCtrl = _csbpm.AcqEvents
    TrigAcqChan = _cutil.Const.register('TrigAcqChan', _et.ORB_ACQ_CHAN)
    TrigAcqDataChan = _csbpm.AcqChan
    TrigAcqDataSel = _csbpm.AcqDataTyp
    TrigAcqDataPol = _csbpm.Polarity
    TrigAcqRepeat = _csbpm.AcqRepeat
    TrigAcqTrig = _cutil.Const.register('TrigAcqTrig', ('External', 'Data'))
    SmoothMeth = _cutil.Const.register('SmoothMeth', _et.SMOOTH_METH)
    SPassMethod = _cutil.Const.register('SPassMethod', _et.SPASS_METHOD)
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
    ApplyDelta = _cutil.Const.register('ApplyDelta', _et.APPLY_CORR_TLINES)
    StsLblsCorr = _cutil.Const.register(
        'StsLblsCorr', _et.STS_LBLS_CORR_TLINES)
    StsLblsOrb = _cutil.Const.register('StsLblsOrb', _et.STS_LBLS_ORB)
    StsLblsGlob = _cutil.Const.register('StsLblsGlob', _et.STS_LBLS_GLOB)

    ClosedLoop = _cutil.Const.register('ClosedLoop', _et.OFF_ON)


class ConstRings(ConstTLines):
    """Const class defining rings orbitcorr constants."""

    SOFBMode = _cutil.Const.register('SOFBMode', _et.ORB_MODE_RINGS)
    ApplyDelta = _cutil.Const.register('ApplyDelta', _et.APPLY_CORR_RINGS)
    StsLblsCorr = _cutil.Const.register('StsLblsCorr', _et.STS_LBLS_CORR_RINGS)

    # TODO: use correct name for the RF generator
    RF_GEN_NAME = 'AS-Glob:RF-Gen'
    EnblRF = _cutil.Const.register('EnblRF', _et.ENBL_RF)
    CorrSync = _cutil.Const.register('CorrSync', _et.OFF_ON)


# --- Database classes ---

class SOFBTLines(ConstTLines):
    """SOFB class for TLines."""

    def __init__(self, acc):
        """Init1 method."""
        self.acc = acc.upper()
        self.acc_idx = self.Accelerators._fields.index(self.acc)
        self.BPM_NAMES = _BPMSearch.get_names({'sec': acc})
        self.CH_NAMES = _MASearch.get_manames(
                            {'sec': acc, 'dis': 'MA', 'dev': 'CH'})
        self.CV_NAMES = _MASearch.get_manames(
                            {'sec': acc, 'dis': 'MA', 'dev': 'CV'})
        self.BPM_NICKNAMES = _BPMSearch.get_nicknames(self.BPM_NAMES)
        self.CH_NICKNAMES = _MASearch.get_manicknames(self.CH_NAMES)
        self.CV_NICKNAMES = _MASearch.get_manicknames(self.CV_NAMES)
        self.BPM_POS = _BPMSearch.get_positions(self.BPM_NAMES)
        self.CH_POS = _MASearch.get_mapositions(self.CH_NAMES)
        self.CV_POS = _MASearch.get_mapositions(self.CV_NAMES)
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

        self.NR_CORRS = self.NR_CHCV + 1 if acc in _et.RINGS else self.NR_CHCV

        if not self.isring():
            self.TRIGGER_ACQ_NAME = 'AS-Glob:TI-BPM-TBTS'
        else:
            self.TRIGGER_ACQ_NAME = 'AS-Glob:TI-BPM-SIBO'
            self.TRIGGER_COR_NAME = self.acc + '-Glob:TI-Corrs'
            self.EVT_COR_NAME = 'Orb' + self.acc

        self.EVT_ACQ_NAME = 'Dig' + self.acc
        self.MTX_SZ = self.NR_CORRS * (2 * self.NR_BPMS)
        self.NR_SING_VALS = min(self.NR_CORRS, 2 * self.NR_BPMS)
        self.C0 = 22 if self.acc == 'TB' else 30  # in meters
        self.T0 = self.C0 / 299792458  # in seconds

    def isring(self):
        return self.acc in self.Rings._fields

    def get_ioc_database(self, prefix=''):
        """Return IOC database."""
        db = self.get_sofb_database(prefix)
        db.update(self.get_corrs_database(prefix))
        db.update(self.get_respmat_database(prefix))
        db.update(self.get_orbit_database(prefix))
        db = _cutil.add_pvslist_cte(db)
        return db

    def get_sofb_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        db = {
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
                'type': 'float', 'value': 300, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatKickCH-RB': {
                'type': 'float', 'value': 300, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatKickCV-SP': {
                'type': 'float', 'value': 150, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatKickCV-RB': {
                'type': 'float', 'value': 150, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 500},
            'MeasRespMatWait-SP': {
                'type': 'float', 'value': 5, 'unit': 's', 'prec': 3,
                'lolim': 0.05, 'hilim': 100},
            'MeasRespMatWait-RB': {
                'type': 'float', 'value': 5, 'unit': 's', 'prec': 3,
                'lolim': 0.05, 'hilim': 100},
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
                'type': 'float', 'value': 3000, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxKickCH-RB': {
                'type': 'float', 'value': 3000, 'prec': 2, 'unit': 'urad'},
            'MaxKickCV-SP': {
                'type': 'float', 'value': 3000, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxKickCV-RB': {
                'type': 'float', 'value': 3000, 'prec': 2, 'unit': 'urad'},
            'MaxDeltaKickCH-SP': {
                'type': 'float', 'value': 3000, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickCH-RB': {
                'type': 'float', 'value': 3000, 'prec': 2, 'unit': 'urad',
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickCV-SP': {
                'type': 'float', 'value': 3000, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickCV-RB': {
                'type': 'float', 'value': 3000, 'prec': 2, 'unit': 'urad',
                'lolim': 0, 'hilim': 10000},
            'ApplyDelta-Cmd': {
                'type': 'enum', 'enums': self.ApplyDelta._fields, 'value': 0,
                'unit': 'Apply last calculated kicks.'},
            'Status-Mon': {
                'type': 'enum', 'value': 1,
                'enums': self.StsLblsGlob._fields}
            }
        return self._add_prefix(db, prefix)

    def get_corrs_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        db = {
            'KickAcqRate-SP': {
                'type': 'float', 'unit': 'Hz', 'value': 2,
                'hilim': 20, 'lolim': 0.5},
            'KickAcqRate-RB': {
                'type': 'float', 'unit': 'Hz', 'value': 2,
                'hilim': 20, 'lolim': 0.5},
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
        return self._add_prefix(db, prefix)

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
        db = dict()
        prop = {
            'type': 'float', 'unit': 'um', 'count': self.MAX_RINGSZ*nbpm,
            'value': nbpm*[0]}
        for k in pvs:
            db[k] = _dcopy(prop)
        db.update({
            'SOFBMode-Sel': {
                'type': 'enum', 'unit': 'Change orbit acquisition mode.',
                'value': self.SOFBMode.Offline,
                'enums': self.SOFBMode._fields},
            'SOFBMode-Sts': {
                'type': 'enum', 'unit': 'Change orbit acquisition mode.',
                'value': self.SOFBMode.Offline,
                'enums': self.SOFBMode._fields},
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
                'hilim': 20, 'lolim': 0.5},
            'OrbAcqRate-RB': {
                'type': 'float', 'unit': 'Hz', 'value': 10,
                'hilim': 20, 'lolim': 0.5},
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
            'SPassMethod-Sel': {
                'type': 'enum', 'value': self.SPassMethod.FromBPMs,
                'enums': self.SPassMethod._fields},
            'SPassMethod-Sts': {
                'type': 'enum', 'value': self.SPassMethod.FromBPMs,
                'enums': self.SPassMethod._fields},
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
        return self._add_prefix(db, prefix)

    def get_respmat_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        db = {
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
                'unit': 'Last CH kicks calculated.'},
            'DeltaKickCV-Mon': {
                'type': 'float', 'count': self.NR_CV, 'value': self.NR_CV*[0],
                'unit': 'Last CV kicks calculated.'},
            }
        return self._add_prefix(db, prefix)

    def _add_prefix(self, db, prefix):
        if prefix:
            return {prefix + k: v for k, v in db.items()}
        return db


class SOFBRings(SOFBTLines, ConstRings):
    """SOFB class."""

    def __init__(self, acc):
        """Init method."""
        SOFBTLines.__init__(self, acc)
        evts = _HLTISearch.get_hl_trigger_allowed_evts(self.TRIGGER_COR_NAME)
        vals = _cstiming.get_hl_trigger_database(self.TRIGGER_COR_NAME)
        vals = tuple([vals['Src-Sel']['enums'].index(evt) for evt in evts])
        self.CorrExtEvtSrc = _get_namedtuple('CorrExtEvtSrc', evts, vals)
        self.C0 = (496.8 if self.acc == 'BO' else 518.396)  # in meter
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
            'MeasRespMatKickRF-SP': {
                'type': 'float', 'value': 50, 'unit': 'Hz', 'prec': 3,
                'lolim': 1, 'hilim': 400},
            'MeasRespMatKickRF-RB': {
                'type': 'float', 'value': 200, 'unit': 'Hz', 'prec': 3,
                'lolim': 1, 'hilim': 400},
            'DeltaFactorRF-SP': {
                'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
                'lolim': -1000, 'hilim': 1000},
            'DeltaFactorRF-RB': {
                'type': 'float', 'value': 100, 'prec': 2, 'unit': '%'},
            'MaxKickRF-SP': {
                'type': 'float', 'value': 3000, 'unit': 'Hz', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxKickRF-RB': {
                'type': 'float', 'value': 3000, 'prec': 2, 'unit': 'Hz',
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickRF-SP': {
                'type': 'float', 'value': 500, 'unit': 'Hz', 'prec': 3,
                'lolim': 0, 'hilim': 10000},
            'MaxDeltaKickRF-RB': {
                'type': 'float', 'value': 500, 'prec': 2, 'unit': 'Hz',
                'lolim': 0, 'hilim': 10000},
            }
        db = super().get_sofb_database(prefix=prefix)
        db.update(self._add_prefix(db_ring, prefix))
        return db

    def get_corrs_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        db_ring = {
            'KickRF-Mon': {
                'type': 'float', 'value': 1, 'unit': 'Hz', 'prec': 3},
            'CorrSync-Sel': {
                'type': 'enum', 'enums': self.CorrSync._fields,
                'value': self.CorrSync.Off},
            'CorrSync-Sts': {
                'type': 'enum', 'enums': self.CorrSync._fields,
                'value': self.CorrSync.Off},
            }
        db = super().get_corrs_database(prefix=prefix)
        db.update(self._add_prefix(db_ring, prefix))
        return db

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
        db = super().get_orbit_database(prefix=prefix)
        db.update(self._add_prefix(db_ring, prefix))
        return db

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
                'type': 'float', 'value': 0,
                'unit': 'Last RF kick calculated.'},
            }
        db = super().get_respmat_database(prefix=prefix)
        db.update(self._add_prefix(db_ring, prefix))
        return db


class SOFBFactory:
    """Factory class for SOFB objects."""

    @staticmethod
    def create(acc):
        """Return appropriate SOFB object."""
        acc = acc.upper()
        if acc in _et.RINGS:
            return SOFBRings(acc)
        elif acc in _et.TLINES:
            return SOFBTLines(acc)
        else:
            raise ValueError('Invalid accelerator name "{}"'.format(acc))
