"""Define PVs, contants and properties of all OpticsCorr SoftIOCs."""
from copy import deepcopy as _dcopy
from siriuspy.util import get_namedtuple as _get_namedtuple
import siriuspy.csdevice.bpms as _csbpm
from siriuspy.search.ma_search import MASearch as _MASearch
from siriuspy.search.ll_time_search import LLTimeSearch as _TISearch
from siriuspy.search.hl_time_search import HLTimeSearch as _HLTISearch
from siriuspy.search.bpms_search import BPMSearch as _BPMSearch


def get_consts(acc):
    acc = acc.upper()
    bpm_names = _BPMSearch.get_names({'sec': acc})
    ch_names = _MASearch.get_manames({'sec': acc, 'dis': 'MA', 'dev': 'CH'})
    cv_names = _MASearch.get_manames({'sec': acc, 'dis': 'MA', 'dev': 'CV'})
    bpm_nicknames = _BPMSearch.get_nicknames(bpm_names)
    ch_nicknames = _MASearch.get_manicknames(ch_names)
    cv_nicknames = _MASearch.get_manicknames(cv_names)
    bpm_pos = _BPMSearch.get_positions(bpm_names)
    ch_pos = _MASearch.get_mapositions(ch_names)
    cv_pos = _MASearch.get_mapositions(cv_names)
    nr_ch = len(ch_names)
    nr_cv = len(cv_names)
    nr_bpms = len(bpm_names)
    nr_corrs = nr_ch + nr_cv + 1
    mtx_sz = nr_corrs * (2*nr_bpms)
    nr_sing_vals = min(nr_corrs, 2*nr_bpms)

    field_names = (
        'NR_BPMS', 'NR_CH', 'NR_CV', 'NR_CORRS', 'MTX_SZ', 'NR_SING_VALS',
        'CH_NAMES', 'CV_NAMES', 'BPM_NAMES',
        'BPM_NICKNAMES', 'CH_NICKNAMES', 'CV_NICKNAMES',
        'BPM_POS', 'CH_POS', 'CV_POS')
    values = (
        nr_bpms, nr_ch, nr_cv, nr_corrs, mtx_sz, nr_sing_vals,
        ch_names, cv_names, bpm_names,
        bpm_nicknames, ch_nicknames, cv_nicknames,
        bpm_pos, ch_pos, cv_pos)
    return _get_namedtuple('Const', field_names, values)


EVG_NAME = _TISearch.get_device_names({'dev': 'EVG'})[0]
TRIGGER_NAME = 'AS-Glob:TI-BPM-SIBO:'
RF_GEN_NAME = 'AS-Glob:RF-Gen'  # TODO: use correct name for this device
ORBIT_CONVERSION_UNIT = 1/1000  # from nm to um
MAX_MT_ORBS = 10000
RF_NOM_FREQ = 499458000.0
EnblRF = _get_namedtuple('EnblRF', ('Off', 'On'))
AutoCorr = _get_namedtuple('AutoCorr', ('Off', 'On'))
SyncKicks = _get_namedtuple('SyncKicks', ('Off', 'On'))
OrbitMode = _get_namedtuple(
    'OrbitMode', ('Offline', 'Online', 'MultiTurn', 'SinglePass'))
OrbitAcqCtrl = _csbpm.AcqEvents
OrbitAcqChan = _get_namedtuple('OrbitAcqChan', ('Monit1', 'FOFB', 'TbT'))
OrbitAcqTrig = _get_namedtuple('OrbitAcqTrig', ('External', 'Data'))
OrbitAcqDataChan = _csbpm.AcqChan
OrbitAcqDataSel = _csbpm.AcqDataTyp
OrbitAcqDataPol = _csbpm.Polarity
OrbitAcqExtEvtSrc = _get_namedtuple(
    'OrbitAcqExtEvtSrc', _HLTISearch.get_hl_trigger_sources(TRIGGER_NAME))
ApplyCorr = _get_namedtuple('ApplyCorr', ('CH', 'CV', 'RF', 'All'))
MeasRespMatCmd = _get_namedtuple('MeasRespMatCmd', ('Start', 'Stop', 'Reset'))
MeasRespMatMon = _get_namedtuple(
    'MeasRespMatMon', ('Idle', 'Measuring', 'Completed', 'Aborted'))
StatusLabels = _get_namedtuple(
    'StatusLabels', ('Corrs', 'Matrix', 'Orbit', 'Global'),
    (('Timing Connected', 'Timing Configured',
      'RF Connected', 'RF PwrState On',
      'CHCV Connected', 'CHCV Mode Configured', 'CHCV PwrState On'),
     ('', ),
     ('Timing Connected', 'Timing Configured',
      'BPMs Connected', 'BPMs Enabled', 'BPMs Configured'),
     ('Ok', 'Not Ok'),
     ))


def get_ioc_database(acc, prefix=''):
    db = get_sofb_database(prefix)
    db.update(get_corrs_database(acc, prefix))
    db.update(get_respmat_database(acc, prefix))
    db.update(get_orbit_database(acc, prefix))
    return db


def get_sofb_database(prefix=''):
    """Return OpticsCorr-Chrom Soft IOC database."""
    db = {
        'Log-Mon': {'type': 'char', 'value': '', 'count': 200},
        'AutoCorr-Sel': {
            'type': 'enum', 'enums': AutoCorr._fields, 'value': 0},
        'AutoCorr-Sts': {
            'type': 'enum', 'enums': AutoCorr._fields, 'value': 0},
        'AutoCorrFreq-SP': {
            'type': 'float', 'value': 1, 'unit': 'Hz', 'prec': 3,
            'lolim': 1e-3, 'hilim': 20},
        'AutoCorrFreq-RB': {
            'type': 'float', 'value': 1, 'prec': 2, 'unit': 'Hz'},
        'MeasRespMat-Cmd': {
            'type': 'enum', 'value': 0, 'enums': MeasRespMatCmd._fields},
        'MeasRespMat-Mon': {
            'type': 'enum', 'value': 0, 'enums': MeasRespMatMon._fields},
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
        'MeasRespMatKickRF-SP': {
            'type': 'float', 'value': 50, 'unit': 'Hz', 'prec': 3,
            'lolim': 1, 'hilim': 400},
        'MeasRespMatKickRF-RB': {
            'type': 'float', 'value': 200, 'unit': 'Hz', 'prec': 3,
            'lolim': 1, 'hilim': 400},
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
        'CorrFactorRF-SP': {
            'type': 'float', 'value': 100, 'unit': '%', 'prec': 2,
            'lolim': -1000, 'hilim': 1000},
        'CorrFactorRF-RB': {
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
        'MaxKickRF-SP': {
            'type': 'float', 'value': 3000, 'unit': 'Hz', 'prec': 3,
            'lolim': 0, 'hilim': 10000},
        'MaxKickRF-RB': {
            'type': 'float', 'value': 3000, 'prec': 2, 'unit': 'Hz',
            'lolim': 0, 'hilim': 10000},
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
        'MaxDeltaKickRF-SP': {
            'type': 'float', 'value': 500, 'unit': 'Hz', 'prec': 3,
            'lolim': 0, 'hilim': 10000},
        'MaxDeltaKickRF-RB': {
            'type': 'float', 'value': 500, 'prec': 2, 'unit': 'Hz',
            'lolim': 0, 'hilim': 10000},
        'ApplyCorr-Cmd': {
            'type': 'enum', 'enums': ApplyCorr._fields, 'value': 0,
            'unit': 'Apply last calculated kicks.'},
        'Status-Mon': {
                'type': 'enum', 'value': 1, 'enums': StatusLabels.Global}
    }
    if prefix:
        return {prefix + k: v for k, v in db.items()}
    return db


def get_corrs_database(acc, prefix=''):
    """Return OpticsCorr-Chrom Soft IOC database."""
    const = get_consts(acc)
    db = {
        'KickAcqRate-SP': {
            'type': 'float', 'unit': 'Hz', 'value': 10,
            'hilim': 20, 'lolim': 0.5},
        'KickAcqRate-RB': {
            'type': 'float', 'unit': 'Hz', 'value': 10,
            'hilim': 20, 'lolim': 0.5},
        'KicksCH-Mon': {
            'type': 'float', 'count': const.NR_CH, 'value': const.NR_CH*[0],
            'unit': 'urad'},
        'KicksCV-Mon': {
            'type': 'float', 'count': const.NR_CV, 'value': const.NR_CV*[0],
            'unit': 'urad'},
        'KicksRF-Mon': {
            'type': 'float', 'value': 1, 'unit': 'Hz', 'prec': 3},
        'NominalFreqRF-SP': {
            'type': 'float', 'value': RF_NOM_FREQ, 'unit': 'Hz', 'prec': 3},
        'NominalFreqRF-RB': {
            'type': 'float', 'value': RF_NOM_FREQ, 'unit': 'Hz', 'prec': 3},
        'SyncKicks-Sel': {
            'type': 'enum', 'enums': SyncKicks._fields, 'value': SyncKicks.On},
        'SyncKicks-Sts': {
            'type': 'enum', 'enums': SyncKicks._fields, 'value': SyncKicks.On},
        'ConfigCorrs-Cmd': {'type': 'short', 'value': 0},
        'CHPosS-Cte': {
            'type': 'float', 'unit': 'm', 'count': const.NR_CH,
            'value': const.CH_POS},
        'CVPosS-Cte': {
            'type': 'float', 'unit': 'm', 'count': const.NR_CV,
            'value': const.CV_POS},
        'CHNickName-Cte': {
            'type': 'string', 'unit': 'shortname for the chs.',
            'count': const.NR_CH, 'value': const.CH_NICKNAMES},
        'CVNickName-Cte': {
            'type': 'string', 'unit': 'shortname for the cvs.',
            'count': const.NR_CV, 'value': const.CV_NICKNAMES},
        'CorrStatus-Mon': {'type': 'short', 'value': 0b1111111},
        'CorrStatusLabels-Cte': {
            'type': 'string', 'count': len(StatusLabels.Corrs),
            'value': StatusLabels.Corrs}
        }
    if prefix:
        return {prefix + k: v for k, v in db.items()}
    return db


def get_orbit_database(acc, prefix=''):
    const = get_consts(acc)
    nbpm = const.NR_BPMS
    evt = 'Dig' + acc
    pvs = [
        'OrbitRefX-SP', 'OrbitRefX-RB',
        'OrbitRefY-SP', 'OrbitRefY-RB',
        'OrbitRawX-Mon', 'OrbitRawY-Mon',
        'OrbitSmoothX-Mon', 'OrbitSmoothY-Mon',
        'OrbitRawSinglePassX-Mon', 'OrbitRawSinglePassY-Mon',
        'OrbitRawSinglePassSum-Mon',
        'OrbitMultiTurnX-Mon', 'OrbitMultiTurnY-Mon',
        'OrbitSmoothSinglePassX-Mon', 'OrbitSmoothSinglePassY-Mon',
        'OrbitSmoothSinglePassSum-Mon',
        'OrbitOfflineX-SP', 'OrbitOfflineX-RB',
        'OrbitOfflineY-SP', 'OrbitOfflineY-RB',
        ]
    db = dict()
    prop = {'type': 'float', 'unit': 'um', 'count': nbpm, 'value': nbpm*[0]}
    for k in pvs:
        db[k] = _dcopy(prop)
    db.update({
        'OrbitsMultiTurnX-Mon': {
            'type': 'float', 'unit': 'um', 'count': MAX_MT_ORBS*nbpm,
            'value': MAX_MT_ORBS*nbpm*[0]},
        'OrbitsMultiTurnY-Mon': {
            'type': 'float', 'unit': 'um', 'count': MAX_MT_ORBS*nbpm,
            'value': MAX_MT_ORBS*nbpm*[0]},
        'OrbitsMultiTurnSum-Mon': {
            'type': 'float', 'unit': 'um', 'count': MAX_MT_ORBS*nbpm,
            'value': MAX_MT_ORBS*nbpm*[0]},
        'OrbitMultiTurnTime-Mon': {
            'type': 'float', 'unit': 'ms', 'count': MAX_MT_ORBS,
            'value': MAX_MT_ORBS*[0]},
        'OrbitMultiTurnIdx-SP': {
            'type': 'int', 'unit': '', 'value': 0,
            'hilim': MAX_MT_ORBS, 'lolim': 0},
        'OrbitMultiTurnIdx-RB': {
            'type': 'int', 'unit': '', 'value': 0,
            'hilim': MAX_MT_ORBS, 'lolim': 0},
        'OrbitMultiTurnIdxTime-Mon': {
            'type': 'float', 'unit': 'ms', 'value': 0.0,
            'hilim': 500, 'lolim': 0},
        'OrbitMode-Sel': {
            'type': 'enum', 'unit': 'Change orbit acquisition mode.',
            'value': OrbitMode.Online, 'enums': OrbitMode._fields},
        'OrbitMode-Sts': {
            'type': 'enum', 'unit': 'Change orbit acquisition mode.',
            'value': OrbitMode.Online, 'enums': OrbitMode._fields},
        'OrbitTrigAcqConfig-Cmd': {'type': 'short', 'value': 0},
        'OrbitTrigAcqCtrl-Sel': {
            'type': 'enum', 'unit': 'Start/Stop/Abort acquistion.',
            'value': OrbitAcqCtrl.Stop, 'enums': OrbitAcqCtrl._fields},
        'OrbitTrigAcqCtrl-Sts': {
            'type': 'enum', 'unit': 'Start/Stop/Reset acquistion.',
            'value': OrbitAcqCtrl.Stop, 'enums': OrbitAcqCtrl._fields},
        'OrbitTrigAcqChan-Sel': {
            'type': 'enum', 'unit': 'Change orbit acquisition Channel.',
            'value': OrbitAcqChan.Monit1, 'enums': OrbitAcqChan._fields},
        'OrbitTrigAcqChan-Sts': {
            'type': 'enum', 'unit': 'Change orbit acquisition Channel.',
            'value': OrbitAcqChan.Monit1, 'enums': OrbitAcqChan._fields},
        'OrbitTrigAcqTrigger-Sel': {
            'type': 'enum', 'unit': 'If trigger is external or by data.',
            'value': OrbitAcqTrig.External, 'enums': OrbitAcqTrig._fields},
        'OrbitTrigAcqTrigger-Sts': {
            'type': 'enum', 'unit': 'If trigger is external or by data.',
            'value': OrbitAcqTrig.External, 'enums': OrbitAcqTrig._fields},
        'OrbitTrigNrShots-SP': {
            'type': 'short', 'unit': '', 'value': 1,
            'hilim': 1000, 'lolim': 1},
        'OrbitTrigNrShots-RB': {
            'type': 'short', 'unit': '', 'value': 1,
            'hilim': 1000, 'lolim': 1},
        'OrbitTrigNrSamples-SP': {
            'type': 'short', 'unit': '', 'value': 200,
            'hilim': MAX_MT_ORBS, 'lolim': 1},
        'OrbitTrigNrSamples-RB': {
            'type': 'short', 'unit': '', 'value': 200,
            'hilim': MAX_MT_ORBS, 'lolim': 1},
        'OrbitTrigDownSample-SP': {
            'type': 'short', 'unit': '', 'value': 1,
            'hilim': MAX_MT_ORBS, 'lolim': 1},
        'OrbitTrigDownSample-RB': {
            'type': 'short', 'unit': '', 'value': 1,
            'hilim': MAX_MT_ORBS, 'lolim': 1},
        'OrbitTrigDataChan-Sel': {
            'type': 'enum', 'unit': 'Set Data-driven trigger Channel.',
            'value': OrbitAcqDataChan.Monit1,
            'enums': OrbitAcqDataChan._fields},
        'OrbitTrigDataChan-Sts': {
            'type': 'enum', 'unit': 'Set Data-driven trigger Channel.',
            'value': OrbitAcqDataChan.Monit1,
            'enums': OrbitAcqDataChan._fields},
        'OrbitTrigDataSel-Sel': {
            'type': 'enum', 'unit': 'Set Data trigger Selection.',
            'value': OrbitAcqDataSel.Sum,
            'enums': OrbitAcqDataSel._fields},
        'OrbitTrigDataSel-Sts': {
            'type': 'enum', 'unit': 'Set Data trigger Selection.',
            'value': OrbitAcqDataSel.Sum,
            'enums': OrbitAcqDataSel._fields},
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
            'value': OrbitAcqDataPol.Positive,
            'enums': OrbitAcqDataPol._fields},
        'OrbitTrigDataPol-Sts': {
            'type': 'enum', 'unit': 'Set Data trigger Polarity.',
            'value': OrbitAcqDataPol.Positive,
            'enums': OrbitAcqDataPol._fields},
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
            'value': OrbitAcqExtEvtSrc._fields.index(evt),
            'enums': OrbitAcqExtEvtSrc._fields},
        'OrbitTrigExtEvtSrc-Sts': {
            'type': 'enum', 'unit': 'Set ext trigger timing event.',
            'value': OrbitAcqExtEvtSrc._fields.index(evt),
            'enums': OrbitAcqExtEvtSrc._fields},
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
        'BPMPosS-Cte': {
            'type': 'float', 'unit': 'm', 'count': nbpm,
            'value': const.BPM_POS},
        'BPMNickName-Cte': {
            'type': 'string', 'unit': 'shortname for the bpms.',
            'count': nbpm, 'value': const.BPM_NICKNAMES},
        'OrbitStatus-Mon': {'type': 'short', 'value': 0b00000},
        'OrbitStatusLabels-Cte': {
            'type': 'string', 'count': len(StatusLabels.Orbit),
            'value': StatusLabels.Orbit},
        })
    if prefix:
        return {prefix + k: v for k, v in db.items()}
    return db


def get_respmat_database(acc, prefix=''):
    """Return OpticsCorr-Chrom Soft IOC database."""
    const = get_consts(acc)

    db = {
        'RespMat-SP': {
            'type': 'float', 'count': const.MTX_SZ, 'value': const.MTX_SZ*[0],
            'unit': '(BH, BV)(um) x (CH, CV, RF)(urad, Hz)'},
        'RespMat-RB': {
            'type': 'float', 'count': const.MTX_SZ, 'value': const.MTX_SZ*[0],
            'unit': '(BH, BV)(um) x (CH, CV, RF)(urad, Hz)'},
        'SingValues-Mon': {
            'type': 'float', 'count': const.NR_SING_VALS,
            'value': const.NR_SING_VALS*[0],
            'unit': 'Singular values of the matrix in use'},
        'InvRespMat-Mon': {
            'type': 'float', 'count': const.MTX_SZ, 'value': const.MTX_SZ*[0],
            'unit': '(CH, CV, RF)(urad, Hz) x (BH, BV)(um)'},
        'CHEnblList-SP': {
            'type': 'short', 'count': const.NR_CH, 'value': const.NR_CH*[1],
            'unit': 'CHs used in correction'},
        'CHEnblList-RB': {
            'type': 'short', 'count': const.NR_CH, 'value': const.NR_CH*[1],
            'unit': 'CHs used in correction'},
        'CVEnblList-SP': {
            'type': 'short', 'count': const.NR_CV, 'value': const.NR_CV*[1],
            'unit': 'CVs used in correction'},
        'CVEnblList-RB': {
            'type': 'short', 'count': const.NR_CV, 'value': const.NR_CV*[1],
            'unit': 'CVs used in correction'},
        'BPMXEnblList-SP': {
            'type': 'short', 'count': const.NR_BPMS,
            'value': const.NR_BPMS*[1],
            'unit': 'BPMX used in correction'},
        'BPMXEnblList-RB': {
            'type': 'short', 'count': const.NR_BPMS,
            'value': const.NR_BPMS*[1],
            'unit': 'BPMX used in correction'},
        'BPMYEnblList-SP': {
            'type': 'short', 'count': const.NR_BPMS,
            'value': const.NR_BPMS*[1],
            'unit': 'BPMY used in correction'},
        'BPMYEnblList-RB': {
            'type': 'short', 'count': const.NR_BPMS,
            'value': const.NR_BPMS*[1],
            'unit': 'BPMY used in correction'},
        'RFEnbl-Sel': {
            'type': 'enum', 'enums': EnblRF._fields, 'value': 0,
            'unit': 'If RF is used in correction'},
        'RFEnbl-Sts': {
            'type': 'enum', 'enums': EnblRF._fields, 'value': 0,
            'unit': 'If RF is used in correction'},
        'NumSingValues-SP': {
            'type': 'short', 'value': const.NR_SING_VALS,
            'lolim': 1, 'hilim': const.NR_SING_VALS,
            'unit': 'Maximum number of SV to use'},
        'NumSingValues-RB': {
            'type': 'short', 'value': const.NR_SING_VALS,
            'lolim': 1, 'hilim': const.NR_SING_VALS,
            'unit': 'Maximum number of SV to use'},
        'DeltaKicksCH-Mon': {
            'type': 'float', 'count': const.NR_CH, 'value': const.NR_CH*[0],
            'unit': 'Last CH kicks calculated.'},
        'DeltaKicksCV-Mon': {
            'type': 'float', 'count': const.NR_CV, 'value': const.NR_CV*[0],
            'unit': 'Last CV kicks calculated.'},
        'DeltaKicksRF-Mon': {
            'type': 'float', 'value': 0, 'unit': 'Last RF kick calculated.'},
        }
    if prefix:
        return {prefix + k: v for k, v in db.items()}
    return db
