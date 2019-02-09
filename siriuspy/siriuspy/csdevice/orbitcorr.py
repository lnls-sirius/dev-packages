"""Define PVs, constants and properties of OrbitCorr SoftIOCs."""
import os as _os
from copy import deepcopy as _dcopy
from siriuspy.util import get_namedtuple as _get_namedtuple
import siriuspy.csdevice.bpms as _csbpm
from siriuspy.csdevice import util as _cutil
from siriuspy.csdevice import timesys as _cstiming
from siriuspy.search.ma_search import MASearch as _MASearch
from siriuspy.search.ll_time_search import LLTimeSearch as _TISearch
from siriuspy.search.hl_time_search import HLTimeSearch as _HLTISearch
from siriuspy.search.bpms_search import BPMSearch as _BPMSearch


# --- Enumeration Types ---

class ETypes(_cutil.ETypes):
    """Local enumerate types."""

    ENBL_RF = _cutil.ETypes.OFF_ON
    ORB_MODE_RINGS = ('Offline', 'Online', 'MultiTurn', 'SinglePass')
    ORB_MODE_TLINES = ('Offline', 'SinglePass')
    APPLY_CORR_RINGS = ('CH', 'CV', 'RF', 'All')
    APPLY_CORR_TLINES = ('CH', 'CV', 'All')
    ORB_ACQ_CHAN = ('Monit1', 'FOFB', 'TbT')
    MEAS_RMAT_CMD = ('Start', 'Stop', 'Reset')
    MEAS_RMAT_MON = ('Idle', 'Measuring', 'Completed', 'Aborted')
    TLINES = ('TB', 'TS')
    RINGS = ('BO', 'SI')
    ACCELERATORS = TLINES + RINGS

    STATUS_LABELS_CORRS_TLINES = (
        'CHCVConnected', 'CHCVModeConfigured', 'CHCVPwrStateOn')
    STATUS_LABELS_CORRS_RINGS = (
        'CHCVConnected', 'CHCVModeConfigured', 'CHCVPwrStateOn',
        'TimingConnected', 'TimingConfigured', 'RFConnected',
        'RFPwrStateOn')
    STATUS_LABELS_ORB = (
        'TimingConnected', 'TimingConfigured', 'BPMsConnected',
        'BPMsEnabled', 'BPMsConfigured')
    STATUS_LABELS_GLOB = ('Ok', 'NotOk')


_et = ETypes  # syntactic sugar


# --- Const class ---

class ConstTLines(_cutil.Const):
    """Const class defining transport lines orbitcorr constants."""

    EVG_NAME = _TISearch.get_device_names({'dev': 'EVG'})[0]
    ORBIT_CONVERSION_UNIT = 1/1000  # from nm to um
    MAX_MT_ORBS = 4000

    OrbitAcqCtrl = _csbpm.AcqEvents
    OrbitAcqDataSel = _csbpm.AcqDataTyp
    OrbitAcqDataPol = _csbpm.Polarity
    OrbitAcqTrig = _cutil.Const.register('OrbitAcqTrig', ('External', 'Data'))
    MeasRespMatCmd = _cutil.Const.register('MeasRespMatCmd', _et.MEAS_RMAT_CMD)
    MeasRespMatMon = _cutil.Const.register('MeasRespMatMon', _et.MEAS_RMAT_MON)
    TransportLines = _cutil.Const.register('TransportLines',
                                           _et.TLINES, (0, 1))
    Rings = _cutil.Const.register('Rings', _et.RINGS, (2, 3))
    Accelerators = _cutil.Const.register('Accelerators', _et.ACCELERATORS)

    OrbitMode = _cutil.Const.register('OrbitMode', _et.ORB_MODE_TLINES)
    ApplyCorr = _cutil.Const.register('ApplyCorr', _et.APPLY_CORR_TLINES)
    StatusLabelsCorrs = _cutil.Const.register(
                        'StatusLabelsCorrs', _et.STATUS_LABELS_CORRS_TLINES)
    StatusLabelsOrb = _cutil.Const.register(
                        'StatusLabelsOrb', _et.STATUS_LABELS_ORB)
    StatusLabelsGlob = _cutil.Const.register(
                        'StatusLabelsGlob', _et.STATUS_LABELS_GLOB)


class ConstRings(ConstTLines):
    """Const class defining rings orbitcorr constants."""

    OrbitMode = _cutil.Const.register('OrbitMode', _et.ORB_MODE_RINGS)
    ApplyCorr = _cutil.Const.register('ApplyCorr', _et.APPLY_CORR_RINGS)
    StatusLabelsCorrs = _cutil.Const.register(
                        'StatusLabelsCorrs', _et.STATUS_LABELS_CORRS_RINGS)

    # TODO: use correct name for the RF generator
    RF_GEN_NAME = 'AS-Glob:RF-Gen'
    RF_NOM_FREQ = 499458000.0
    EnblRF = _cutil.Const.register('EnblRF', _et.ENBL_RF)
    AutoCorr = _cutil.Const.register('AutoCorr', _et.OFF_ON)
    SyncKicks = _cutil.Const.register('SyncKicks', _et.OFF_ON)
    OrbitAcqChan = _cutil.Const.register('OrbitAcqChan', _et.ORB_ACQ_CHAN)
    OrbitAcqDataChan = _csbpm.AcqChan


# --- Database classes ---

class OrbitCorrDevTLines(ConstTLines):
    """OrbitCorrDev class for TLines."""

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
        self.REFORBFNAME = _os.path.join('data', 'ref_orbit.'+ext)
        ext = acc.lower() + 'respmat'
        self.RESPMAT_FILENAME = _os.path.join('data', 'respmat.'+ext)

        self.NR_CORRS = self.NR_CHCV + 1 if acc in _et.RINGS else self.NR_CHCV

        if self.acc in ('TB', 'TS'):
            self.TRIGGER_ACQ_NAME = 'AS-Glob:TI-BPM-TBTS'
            if self.isring():
                self.TRIGGER_COR_NAME = self.acc + '-Glob:TI-Mags'
                self.EVT_COR_NAME = 'Cycle'
        else:
            self.TRIGGER_ACQ_NAME = 'AS-Glob:TI-BPM-SIBO'
            self.TRIGGER_COR_NAME = self.acc + '-Glob:TI-Corrs'
            self.EVT_COR_NAME = 'Orb' + self.acc

        self.EVT_ACQ_NAME = 'Dig' + self.acc
        evts = _HLTISearch.get_hl_trigger_allowed_evts(self.TRIGGER_ACQ_NAME)
        vals = _cstiming.get_hl_trigger_database(self.TRIGGER_ACQ_NAME)
        vals = tuple([vals['Src-Sel']['enums'].index(evt) for evt in evts])
        self.OrbitAcqExtEvtSrc = _get_namedtuple(
                                    'OrbitAcqExtEvtSrc', evts, vals)
        self.MTX_SZ = self.NR_CORRS * (2 * self.NR_BPMS)
        self.NR_SING_VALS = min(self.NR_CORRS, 2 * self.NR_BPMS)

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
            'MeasRespMat-Cmd': {
                'type': 'enum', 'value': 0,
                'enums': self.MeasRespMatCmd._fields},
            'MeasRespMat-Mon': {
                'type': 'enum', 'value': 0,
                'enums': self.MeasRespMatMon._fields},
            'MeasRespMatKickCH-SP': {
                'type': 'float', 'value': 0.2, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 50},
            'MeasRespMatKickCH-RB': {
                'type': 'float', 'value': 0.2, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 50},
            'MeasRespMatKickCV-SP': {
                'type': 'float', 'value': 0.2, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 50},
            'MeasRespMatKickCV-RB': {
                'type': 'float', 'value': 0.2, 'unit': 'urad', 'prec': 3,
                'lolim': 0.002, 'hilim': 50},
            'MeasRespMatWait-SP': {
                'type': 'float', 'value': 0.5, 'unit': 's', 'prec': 3,
                'lolim': 0.05, 'hilim': 100},
            'MeasRespMatWait-RB': {
                'type': 'float', 'value': 0.5, 'unit': 's', 'prec': 3,
                'lolim': 0.05, 'hilim': 100},
            'CalcCorr-Cmd': {
                'type': 'short', 'value': 0, 'unit': 'Calculate kicks'},
            'CorrFactorCH-SP': {
                'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
                'lolim': -1000, 'hilim': 1000},
            'CorrFactorCH-RB': {
                'type': 'float', 'value': 100, 'prec': 2, 'unit': '%'},
            'CorrFactorCV-SP': {
                'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
                'lolim': -1000, 'hilim': 1000},
            'CorrFactorCV-RB': {
                'type': 'float', 'value': 100, 'prec': 2, 'unit': '%'},
            'MaxKickCH-SP': {
                'type': 'float', 'value': 300, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 1000},
            'MaxKickCH-RB': {
                'type': 'float', 'value': 300, 'prec': 2, 'unit': 'urad'},
            'MaxKickCV-SP': {
                'type': 'float', 'value': 300, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 1000},
            'MaxKickCV-RB': {
                'type': 'float', 'value': 300, 'prec': 2, 'unit': 'urad'},
            'MaxDeltaKickCH-SP': {
                'type': 'float', 'value': 50, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 1000},
            'MaxDeltaKickCH-RB': {
                'type': 'float', 'value': 50, 'prec': 2, 'unit': 'urad',
                'lolim': 0, 'hilim': 1000},
            'MaxDeltaKickCV-SP': {
                'type': 'float', 'value': 50, 'unit': 'urad', 'prec': 3,
                'lolim': 0, 'hilim': 1000},
            'MaxDeltaKickCV-RB': {
                'type': 'float', 'value': 50, 'prec': 2, 'unit': 'urad',
                'lolim': 0, 'hilim': 1000},
            'ApplyCorr-Cmd': {
                'type': 'enum', 'enums': self.ApplyCorr._fields, 'value': 0,
                'unit': 'Apply last calculated kicks.'},
            'Status-Mon': {
                'type': 'enum', 'value': 1,
                'enums': self.StatusLabelsGlob._fields}
            }
        return self._add_prefix(db, prefix)

    def get_corrs_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        db = {
            'KickAcqRate-SP': {
                'type': 'float', 'unit': 'Hz', 'value': 10,
                'hilim': 20, 'lolim': 0.5},
            'KickAcqRate-RB': {
                'type': 'float', 'unit': 'Hz', 'value': 10,
                'hilim': 20, 'lolim': 0.5},
            'KicksCH-Mon': {
                'type': 'float', 'count': self.NR_CH, 'value': self.NR_CH*[0],
                'unit': 'urad'},
            'KicksCV-Mon': {
                'type': 'float', 'count': self.NR_CV, 'value': self.NR_CV*[0],
                'unit': 'urad'},
            'ConfigCorrs-Cmd': {'type': 'short', 'value': 0},
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
            'CorrStatus-Mon': {'type': 'short', 'value': 0b1111111},
            'CorrStatusLabels-Cte': {
                'type': 'string', 'count': len(self.StatusLabelsCorrs._fields),
                'value': self.StatusLabelsCorrs._fields}
            }
        return self._add_prefix(db, prefix)

    def get_orbit_database(self, prefix=''):
        """Return Orbit database."""
        nbpm = self.NR_BPMS
        evt = self.EVT_ACQ_NAME
        pvs = [
            'OrbitRefX-SP', 'OrbitRefX-RB',
            'OrbitRefY-SP', 'OrbitRefY-RB',
            'OrbitRawSinglePassX-Mon', 'OrbitRawSinglePassY-Mon',
            'OrbitRawSinglePassSum-Mon',
            'OrbitSmoothSinglePassX-Mon', 'OrbitSmoothSinglePassY-Mon',
            'OrbitSmoothSinglePassSum-Mon',
            'OrbitOfflineX-SP', 'OrbitOfflineX-RB',
            'OrbitOfflineY-SP', 'OrbitOfflineY-RB',
            'BPMOffsetsX-Mon', 'BPMOffsetsY-Mon',
            ]
        db = dict()
        prop = {
            'type': 'float', 'unit': 'um', 'count': nbpm, 'value': nbpm*[0]}
        for k in pvs:
            db[k] = _dcopy(prop)
        db.update({
            'OrbitMode-Sel': {
                'type': 'enum', 'unit': 'Change orbit acquisition mode.',
                'value': self.OrbitMode.Offline,
                'enums': self.OrbitMode._fields},
            'OrbitMode-Sts': {
                'type': 'enum', 'unit': 'Change orbit acquisition mode.',
                'value': self.OrbitMode.Offline,
                'enums': self.OrbitMode._fields},
            'OrbitTrigAcqConfig-Cmd': {'type': 'short', 'value': 0},
            'OrbitTrigAcqCtrl-Sel': {
                'type': 'enum', 'unit': 'Start/Stop/Abort acquistion.',
                'value': self.OrbitAcqCtrl.Stop,
                'enums': self.OrbitAcqCtrl._fields},
            'OrbitTrigAcqCtrl-Sts': {
                'type': 'enum', 'unit': 'Start/Stop/Reset acquistion.',
                'value': self.OrbitAcqCtrl.Stop,
                'enums': self.OrbitAcqCtrl._fields},
            'OrbitTrigAcqTrigger-Sel': {
                'type': 'enum', 'unit': 'If trigger is external or by data.',
                'value': self.OrbitAcqTrig.External,
                'enums': self.OrbitAcqTrig._fields},
            'OrbitTrigAcqTrigger-Sts': {
                'type': 'enum', 'unit': 'If trigger is external or by data.',
                'value': self.OrbitAcqTrig.External,
                'enums': self.OrbitAcqTrig._fields},
            'OrbitTrigNrSamplesPre-SP': {
                'type': 'short', 'unit': '', 'value': 0,
                'hilim': 2**15-1, 'lolim': 0},
            'OrbitTrigNrSamplesPre-RB': {
                'type': 'short', 'unit': '', 'value': 0,
                'hilim': 2**15-1, 'lolim': 0},
            'OrbitTrigNrSamplesPost-SP': {
                'type': 'short', 'unit': '', 'value': 200,
                'hilim': 2**15-1, 'lolim': 1},
            'OrbitTrigNrSamplesPost-RB': {
                'type': 'short', 'unit': '', 'value': 200,
                'hilim': 2**15-1, 'lolim': 1},
            'OrbitTrigDataSel-Sel': {
                'type': 'enum', 'unit': 'Set Data trigger Selection.',
                'value': self.OrbitAcqDataSel.A,
                'enums': self.OrbitAcqDataSel._fields},
            'OrbitTrigDataSel-Sts': {
                'type': 'enum', 'unit': 'Set Data trigger Selection.',
                'value': self.OrbitAcqDataSel.A,
                'enums': self.OrbitAcqDataSel._fields},
            'OrbitTrigDataThres-SP': {
                'type': 'int', 'value': 1,
                'unit': 'set data trigger threshold',
                'lolim': 1, 'hilim': 2**31-1},
            'OrbitTrigDataThres-RB': {
                'type': 'int', 'value': 1,
                'unit': 'set data trigger threshold',
                'lolim': 1, 'hilim': 2**31-1},
            'OrbitTrigDataHyst-SP': {
                'type': 'int', 'value': 1,
                'unit': 'set data trigger hysteresis',
                'lolim': 1, 'hilim': 2**31-1},
            'OrbitTrigDataHyst-RB': {
                'type': 'int', 'value': 1,
                'unit': 'set data trigger hysteresis',
                'lolim': 1, 'hilim': 2**31-1},
            'OrbitTrigDataPol-Sel': {
                'type': 'enum', 'unit': 'Set Data trigger Polarity.',
                'value': self.OrbitAcqDataPol.Positive,
                'enums': self.OrbitAcqDataPol._fields},
            'OrbitTrigDataPol-Sts': {
                'type': 'enum', 'unit': 'Set Data trigger Polarity.',
                'value': self.OrbitAcqDataPol.Positive,
                'enums': self.OrbitAcqDataPol._fields},
            'OrbitTrigExtDuration-SP': {
                'type': 'float', 'value': 1e-3,
                'unit': 'set external trigger duration [ms]',
                'lolim': 8e-6, 'hilim': 500},
            'OrbitTrigExtDuration-RB': {
                'type': 'float', 'value': 1e-3,
                'unit': 'set external trigger duration [ms]',
                'lolim': 8e-6, 'hilim': 500},
            'OrbitTrigExtDelay-SP': {
                'type': 'float', 'value': 0.0,
                'unit': 'set external trigger delay [us]',
                'lolim': 0.0, 'hilim': 5e5},
            'OrbitTrigExtDelay-RB': {
                'type': 'float', 'value': 0.0,
                'unit': 'set external trigger delay [us]',
                'lolim': 0.0, 'hilim': 5e5},
            'OrbitTrigExtEvtSrc-Sel': {
                'type': 'enum', 'unit': 'Set ext trigger timing event.',
                'value': self.OrbitAcqExtEvtSrc._fields.index(evt),
                'enums': self.OrbitAcqExtEvtSrc._fields},
            'OrbitTrigExtEvtSrc-Sts': {
                'type': 'enum', 'unit': 'Set ext trigger timing event.',
                'value': self.OrbitAcqExtEvtSrc._fields.index(evt),
                'enums': self.OrbitAcqExtEvtSrc._fields},
            'OrbitAcqRate-SP': {
                'type': 'float', 'unit': 'Hz', 'value': 10,
                'hilim': 20, 'lolim': 0.5},
            'OrbitAcqRate-RB': {
                'type': 'float', 'unit': 'Hz', 'value': 10,
                'hilim': 20, 'lolim': 0.5},
            'OrbitSmoothNPnts-SP': {
                'type': 'short', 'value': 1,
                'unit': 'number of points for average',
                'lolim': 1, 'hilim': 200},
            'OrbitSmoothNPnts-RB': {
                'type': 'short', 'value': 1,
                'unit': 'number of points for average',
                'lolim': 1, 'hilim': 200},
            'OrbitSmoothReset-Cmd': {
                'type': 'short', 'value': 0, 'unit': 'Reset orbit buffer'},
            'BPMPosS-Cte': {
                'type': 'float', 'unit': 'm', 'count': nbpm,
                'value': self.BPM_POS},
            'BPMNickName-Cte': {
                'type': 'string', 'unit': 'shortname for the bpms.',
                'count': nbpm, 'value': self.BPM_NICKNAMES},
            'OrbitStatus-Mon': {'type': 'short', 'value': 0b00000},
            'OrbitStatusLabels-Cte': {
                'type': 'string', 'count': len(self.StatusLabelsOrb._fields),
                'value': self.StatusLabelsOrb._fields},
            })
        return self._add_prefix(db, prefix)

    def get_respmat_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        db = {
            'RespMat-SP': {
                'type': 'float', 'count': self.MTX_SZ,
                'value': self.MTX_SZ*[0],
                'unit': '(BH, BV)(um) x (CH, CV, RF)(urad, Hz)'},
            'RespMat-RB': {
                'type': 'float', 'count': self.MTX_SZ,
                'value': self.MTX_SZ*[0],
                'unit': '(BH, BV)(um) x (CH, CV, RF)(urad, Hz)'},
            'SingValues-Mon': {
                'type': 'float', 'count': self.NR_SING_VALS,
                'value': self.NR_SING_VALS*[0],
                'unit': 'Singular values of the matrix in use'},
            'InvRespMat-Mon': {
                'type': 'float', 'count': self.MTX_SZ,
                'value': self.MTX_SZ*[0],
                'unit': '(CH, CV, RF)(urad, Hz) x (BH, BV)(um)'},
            'CHEnblList-SP': {
                'type': 'short', 'count': self.NR_CH, 'value': self.NR_CH*[1],
                'unit': 'CHs used in correction'},
            'CHEnblList-RB': {
                'type': 'short', 'count': self.NR_CH, 'value': self.NR_CH*[1],
                'unit': 'CHs used in correction'},
            'CVEnblList-SP': {
                'type': 'short', 'count': self.NR_CV, 'value': self.NR_CV*[1],
                'unit': 'CVs used in correction'},
            'CVEnblList-RB': {
                'type': 'short', 'count': self.NR_CV, 'value': self.NR_CV*[1],
                'unit': 'CVs used in correction'},
            'BPMXEnblList-SP': {
                'type': 'short', 'count': self.NR_BPMS,
                'value': self.NR_BPMS*[1],
                'unit': 'BPMX used in correction'},
            'BPMXEnblList-RB': {
                'type': 'short', 'count': self.NR_BPMS,
                'value': self.NR_BPMS*[1],
                'unit': 'BPMX used in correction'},
            'BPMYEnblList-SP': {
                'type': 'short', 'count': self.NR_BPMS,
                'value': self.NR_BPMS*[1],
                'unit': 'BPMY used in correction'},
            'BPMYEnblList-RB': {
                'type': 'short', 'count': self.NR_BPMS,
                'value': self.NR_BPMS*[1],
                'unit': 'BPMY used in correction'},
            'NumSingValues-SP': {
                'type': 'short', 'value': self.NR_SING_VALS,
                'lolim': 1, 'hilim': self.NR_SING_VALS,
                'unit': 'Maximum number of SV to use'},
            'NumSingValues-RB': {
                'type': 'short', 'value': self.NR_SING_VALS,
                'lolim': 1, 'hilim': self.NR_SING_VALS,
                'unit': 'Maximum number of SV to use'},
            'DeltaKicksCH-Mon': {
                'type': 'float', 'count': self.NR_CH, 'value': self.NR_CH*[0],
                'unit': 'Last CH kicks calculated.'},
            'DeltaKicksCV-Mon': {
                'type': 'float', 'count': self.NR_CV, 'value': self.NR_CV*[0],
                'unit': 'Last CV kicks calculated.'},
            }
        return self._add_prefix(db, prefix)

    def _add_prefix(self, db, prefix):
        if prefix:
            return {prefix + k: v for k, v in db.items()}
        return db


class OrbitCorrDevRings(OrbitCorrDevTLines, ConstRings):
    """OrbitCorrDev class."""

    def __init__(self, acc):
        """Init method."""
        OrbitCorrDevTLines.__init__(self, acc)
        evts = _HLTISearch.get_hl_trigger_allowed_evts(self.TRIGGER_COR_NAME)
        vals = _cstiming.get_hl_trigger_database(self.TRIGGER_COR_NAME)
        vals = tuple([vals['Src-Sel']['enums'].index(evt) for evt in evts])
        self.OrbitCorExtEvtSrc = _get_namedtuple(
                                        'OrbitCorExtEvtSrc', evts, vals)
        self.C0 = (496.8 if self.acc == 'BO' else 518.396)  # in meter
        self.T0 = self.C0 / 299792458 * 1000  # in milliseconds

    def get_sofb_database(self, prefix=''):
        """Return OpticsCorr-Chrom Soft IOC database."""
        db_ring = {
            'AutoCorr-Sel': {
                'type': 'enum', 'enums': self.AutoCorr._fields, 'value': 0},
            'AutoCorr-Sts': {
                'type': 'enum', 'enums': self.AutoCorr._fields, 'value': 0},
            'AutoCorrFreq-SP': {
                'type': 'float', 'value': 1, 'unit': 'Hz', 'prec': 3,
                'lolim': 1e-3, 'hilim': 20},
            'AutoCorrFreq-RB': {
                'type': 'float', 'value': 1, 'prec': 2, 'unit': 'Hz'},
            'MeasRespMatKickRF-SP': {
                'type': 'float', 'value': 50, 'unit': 'Hz', 'prec': 3,
                'lolim': 1, 'hilim': 400},
            'MeasRespMatKickRF-RB': {
                'type': 'float', 'value': 200, 'unit': 'Hz', 'prec': 3,
                'lolim': 1, 'hilim': 400},
            'CorrFactorRF-SP': {
                'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
                'lolim': -1000, 'hilim': 1000},
            'CorrFactorRF-RB': {
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
            'KicksRF-Mon': {
                'type': 'float', 'value': 1, 'unit': 'Hz', 'prec': 3},
            'NominalFreqRF-SP': {
                'type': 'float', 'value': self.RF_NOM_FREQ, 'unit': 'Hz',
                'prec': 3},
            'NominalFreqRF-RB': {
                'type': 'float', 'value': self.RF_NOM_FREQ, 'unit': 'Hz',
                'prec': 3},
            'SyncKicks-Sel': {
                'type': 'enum', 'enums': self.SyncKicks._fields,
                'value': self.SyncKicks.On},
            'SyncKicks-Sts': {
                'type': 'enum', 'enums': self.SyncKicks._fields,
                'value': self.SyncKicks.On},
            }
        db = super().get_corrs_database(prefix=prefix)
        db.update(self._add_prefix(db_ring, prefix))
        return db

    def get_orbit_database(self, prefix=''):
        """Return Orbit database."""
        nbpm = self.NR_BPMS
        pvs_ring = [
            'OrbitRawX-Mon', 'OrbitRawY-Mon',
            'OrbitSmoothX-Mon', 'OrbitSmoothY-Mon',
            'OrbitMultiTurnX-Mon', 'OrbitMultiTurnY-Mon',
            'OrbitMultiTurnSum-Mon',
            ]
        db_ring = dict()
        prop = {
            'type': 'float', 'unit': 'um', 'count': nbpm, 'value': nbpm*[0]}
        for k in pvs_ring:
            db_ring[k] = _dcopy(prop)
        db_ring.update({
            'OrbitsMultiTurnX-Mon': {
                'type': 'float', 'unit': 'um', 'count': self.MAX_MT_ORBS*nbpm,
                'value': 50*nbpm*[0]},
            'OrbitsMultiTurnY-Mon': {
                'type': 'float', 'unit': 'um', 'count': self.MAX_MT_ORBS*nbpm,
                'value': 50*nbpm*[0]},
            'OrbitsMultiTurnSum-Mon': {
                'type': 'float', 'unit': 'um', 'count': self.MAX_MT_ORBS*nbpm,
                'value': 50*nbpm*[0]},
            'OrbitMultiTurnTime-Mon': {
                'type': 'float', 'unit': 'ms', 'count': self.MAX_MT_ORBS,
                'value': 50*[0]},
            'OrbitMultiTurnIdx-SP': {
                'type': 'int', 'unit': '', 'value': 0,
                'hilim': 50, 'lolim': 0},
            'OrbitMultiTurnIdx-RB': {
                'type': 'int', 'unit': '', 'value': 0,
                'hilim': self.MAX_MT_ORBS, 'lolim': 0},
            'OrbitMultiTurnIdxTime-Mon': {
                'type': 'float', 'unit': 'ms', 'value': 0.0, 'prec': 5,
                'hilim': 500, 'lolim': 0},
            'OrbitTrigAcqChan-Sel': {
                'type': 'enum', 'unit': 'Change orbit acquisition Channel.',
                'value': self.OrbitAcqChan.Monit1,
                'enums': self.OrbitAcqChan._fields},
            'OrbitTrigAcqChan-Sts': {
                'type': 'enum', 'unit': 'Change orbit acquisition Channel.',
                'value': self.OrbitAcqChan.Monit1,
                'enums': self.OrbitAcqChan._fields},
            'OrbitTrigNrShots-SP': {
                'type': 'short', 'unit': '', 'value': 1,
                'hilim': 1000, 'lolim': 1},
            'OrbitTrigNrShots-RB': {
                'type': 'short', 'unit': '', 'value': 1,
                'hilim': 1000, 'lolim': 1},
            'OrbitTrigDownSample-SP': {
                'type': 'short', 'unit': '', 'value': 1,
                'hilim': 2**15-1, 'lolim': 1},
            'OrbitTrigDownSample-RB': {
                'type': 'short', 'unit': '', 'value': 1,
                'hilim': 2**15-1, 'lolim': 1},
            'OrbitTrigDataChan-Sel': {
                'type': 'enum', 'unit': 'Set Data-driven trigger Channel.',
                'value': self.OrbitAcqDataChan.Monit1,
                'enums': self.OrbitAcqDataChan._fields},
            'OrbitTrigDataChan-Sts': {
                'type': 'enum', 'unit': 'Set Data-driven trigger Channel.',
                'value': self.OrbitAcqDataChan.Monit1,
                'enums': self.OrbitAcqDataChan._fields},
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
            'DeltaKicksRF-Mon': {
                'type': 'float', 'value': 0,
                'unit': 'Last RF kick calculated.'},
            }
        db = super().get_respmat_database(prefix=prefix)
        db.update(self._add_prefix(db_ring, prefix))
        return db


class OrbitCorrDevFactory:
    """Factory class for OrbitCorrDev objects."""

    @staticmethod
    def create(acc):
        """Return appropriate OrbitCorrDev object."""
        acc = acc.upper()
        if acc in _et.RINGS:
            return OrbitCorrDevRings(acc)
        elif acc in _et.TLINES:
            return OrbitCorrDevTLines(acc)
        else:
            raise ValueError('Invalid accelerator name "{}"'.format(acc))
