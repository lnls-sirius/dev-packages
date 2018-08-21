"""Define PVs, contants and properties of all OpticsCorr SoftIOCs."""
from copy import deepcopy as _dcopy
from siriuspy.csdevice.const import get_namedtuple as _get_namedtuple
from siriuspy.search.ma_search import MASearch as _MASearch
from siriuspy.search.ll_time_search import LLTimeSearch as _TISearch
from siriuspy.search.bpms_search import BPMSearch as _BPMSearch


def get_consts(acc):
    acc = acc.upper()
    ch_names = _MASearch.get_manames({'sec': acc, 'dis': 'MA', 'dev': 'CH'})
    cv_names = _MASearch.get_manames({'sec': acc, 'dis': 'MA', 'dev': 'CV'})
    bpm_names = _BPMSearch.get_names({'sec': acc})
    bpm_nicknames = _BPMSearch.get_nicknames(bpm_names)
    bpm_pos = _BPMSearch.get_positions(bpm_names)
    nr_ch = len(ch_names)
    nr_cv = len(cv_names)
    nr_bpms = len(bpm_names)
    nr_corrs = nr_ch + nr_cv + 1
    mtx_sz = nr_corrs * (2*nr_bpms)
    nr_sing_vals = min(nr_corrs, 2*nr_bpms)

    field_names = (
        'NR_BPMS', 'NR_CH', 'NR_CV', 'NR_CORRS', 'MTX_SZ', 'NR_SING_VALS',
        'CH_NAMES', 'CV_NAMES', 'BPM_NAMES', 'BPM_NICKNAMES', 'BPM_POS')
    values = (
        nr_bpms, nr_ch, nr_cv, nr_corrs, mtx_sz, nr_sing_vals,
        ch_names, cv_names, bpm_names, bpm_nicknames, bpm_pos)
    return _get_namedtuple('Const', field_names, values)


EVG_NAME = _TISearch.get_device_names({'dev': 'EVG'})[0]
RF_GEN_NAME = 'AS-Glob:RF-Gen'  # TODO: use correct name for this device
EnblRF = _get_namedtuple('EnblRF', ('Off', 'On'))
AutoCorr = _get_namedtuple('AutoCorr', ('Off', 'On'))
SyncKicks = _get_namedtuple('SyncKicks', ('Off', 'On'))
CorrMode = _get_namedtuple('CorrMode', ('Offline', 'Online'))
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
     ('BPMs X Connected', 'BPMs Y Connected'),
     ('Ok', 'Not Ok'),
     ))


def get_ioc_database(acc, prefix=''):
    db = get_sofb_database(acc, prefix)
    db.update(get_corrs_database(acc, prefix))
    db.update(get_respmat_database(acc, prefix))
    db.update(get_orbit_database(acc, prefix))
    return db


def get_sofb_database(acc, prefix=''):
    """Return OpticsCorr-Chrom Soft IOC database."""
    db = {
        'Log-Mon': {'type': 'string', 'value': ''},
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
            'type': 'float', 'value': 0.2, 'unit': 'urad', 'prec': 3},
        'MeasRespMatKickCH-RB': {
            'type': 'float', 'value': 0.2, 'unit': 'urad', 'prec': 3},
        'MeasRespMatKickCV-SP': {
            'type': 'float', 'value': 0.2, 'unit': 'urad', 'prec': 3},
        'MeasRespMatKickCV-RB': {
            'type': 'float', 'value': 0.2, 'unit': 'urad', 'prec': 3},
        'MeasRespMatKickRF-SP': {
            'type': 'float', 'value': 200, 'unit': 'Hz', 'prec': 3},
        'MeasRespMatKickRF-RB': {
            'type': 'float', 'value': 200, 'unit': 'Hz', 'prec': 3},
        'CalcCorr-Cmd': {
            'type': 'char', 'value': 0, 'unit': 'Calculate kicks'},
        'CorrFactorCH-SP': {
            'type': 'float', 'value': 0, 'unit': '%', 'prec': 2,
            'lolim': -1000, 'hilim': 1000},
        'CorrFactorCH-RB': {
            'type': 'float', 'value': 0, 'prec': 2, 'unit': '%'},
        'CorrFactorCV-SP': {
            'type': 'float', 'value': 0, 'unit': '%', 'prec': 2,
            'lolim': -1000, 'hilim': 1000},
        'CorrFactorCV-RB': {
            'type': 'float', 'value': 0, 'prec': 2, 'unit': '%'},
        'CorrFactorRF-SP': {
            'type': 'float', 'value': 0, 'unit': '%', 'prec': 2,
            'lolim': -1000, 'hilim': 1000},
        'CorrFactorRF-RB': {
            'type': 'float', 'value': 0, 'prec': 2, 'unit': '%'},
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
            'type': 'float', 'value': 3000, 'prec': 2, 'unit': 'Hz'},
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
        'SyncKicks-Sel': {
            'type': 'enum', 'enums': SyncKicks._fields, 'value': 1},
        'SyncKicks-Sts': {
            'type': 'enum', 'enums': SyncKicks._fields, 'value': 1},
        'ConfigTiming-Cmd': {'type': 'char', 'value': 0},
        'CorrStatus-Mon': {'type': 'char', 'value': 0b1111111},
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
    pvs = [
        'OrbitRefX-SP',     'OrbitRefX-RB',
        'OrbitRefY-SP',     'OrbitRefY-RB',
        'OrbitRawX-Mon',    'OrbitRawY-Mon',
        'OrbitSmoothX-Mon', 'OrbitSmoothY-Mon',
        'OrbitOfflineX-SP', 'OrbitOfflineX-RB',
        'OrbitOfflineY-SP', 'OrbitOfflineY-RB',
        ]
    db = dict()
    prop = {'type': 'float', 'unit': 'nm', 'count': nbpm, 'value': nbpm*[0]}
    for k in pvs:
        db[k] = _dcopy(prop)
    db.update({
        'OrbitAcqRate-SP': {
            'type': 'float', 'unit': 'Hz', 'value': 10,
            'hilim': 20, 'lolim': 0.5},
        'OrbitAcqRate-RB': {
            'type': 'float', 'unit': 'Hz', 'value': 10,
            'hilim': 20, 'lolim': 0.5},
        'CorrMode-Sel': {
            'type': 'enum', 'enums': CorrMode._fields, 'value': 1,
            'unit': 'Defines is correction is offline or online'},
        'CorrMode-Sts': {
            'type': 'enum', 'enums': CorrMode._fields, 'value': 1,
            'unit': 'Defines is correction is offline or online'},
        'OrbitSmoothNPnts-SP': {
            'type': 'char', 'value': 1,
            'unit': 'number of points for average',
            'lolim': 1, 'hilim': 200},
        'OrbitSmoothNPnts-RB': {
            'type': 'char', 'value': 1,
            'unit': 'number of points for average',
            'lolim': 1, 'hilim': 200},
        'PosS-Cte': {
            'type': 'float', 'unit': 'm', 'count': nbpm,
            'value': const.BPM_POS},
        'BPMNickName-Cte': {
            'type': 'string', 'unit': 'shotname for the bpms.',
            'count': nbpm, 'value': const.BPM_NICKNAMES},
        'OrbitStatus-Mon': {'type': 'char', 'value': 0},
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
            'unit': '(BH, BV)(nm) x (CH, CV, RF)(urad, Hz)'},
        'RespMat-RB': {
            'type': 'float', 'count': const.MTX_SZ, 'value': const.MTX_SZ*[0],
            'unit': '(BH, BV)(nm) x (CH, CV, RF)(urad, Hz)'},
        'SingValues-Mon': {
            'type': 'float', 'count': const.NR_SING_VALS,
            'value': const.NR_SING_VALS*[0],
            'unit': 'Singular values of the matrix in use'},
        'InvRespMat-Mon': {
            'type': 'float', 'count': const.MTX_SZ, 'value': const.MTX_SZ*[0],
            'unit': '(CH, CV, RF)(urad, Hz) x (BH, BV)(nm)'},
        'CHEnblList-SP': {
            'type': 'char', 'count': const.NR_CH, 'value': const.NR_CH*[1],
            'unit': 'CHs used in correction'},
        'CHEnblList-RB': {
            'type': 'char', 'count': const.NR_CH, 'value': const.NR_CH*[1],
            'unit': 'CHs used in correction'},
        'CVEnblList-SP': {
            'type': 'char', 'count': const.NR_CV, 'value': const.NR_CV*[1],
            'unit': 'CVs used in correction'},
        'CVEnblList-RB': {
            'type': 'char', 'count': const.NR_CV, 'value': const.NR_CV*[1],
            'unit': 'CVs used in correction'},
        'BPMXEnblList-SP': {
            'type': 'char', 'count': const.NR_BPMS, 'value': const.NR_BPMS*[1],
            'unit': 'BPMX used in correction'},
        'BPMXEnblList-RB': {
            'type': 'char', 'count': const.NR_BPMS, 'value': const.NR_BPMS*[1],
            'unit': 'BPMX used in correction'},
        'BPMYEnblList-SP': {
            'type': 'char', 'count': const.NR_BPMS, 'value': const.NR_BPMS*[1],
            'unit': 'BPMY used in correction'},
        'BPMYEnblList-RB': {
            'type': 'char', 'count': const.NR_BPMS, 'value': const.NR_BPMS*[1],
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
            'type': 'float', 'value': 1, 'unit': 'Last RF kick calculated.'},
        }
    if prefix:
        return {prefix + k: v for k, v in db.items()}
    return db
