"""Injection Control App."""

from .. import csdev as _csdev
from ..devices import InjSysStandbyHandler as _InjSysHandler, \
    EGun as _EGun


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    INJMODE = ('Decay', 'TopUp')
    INJTYPE = ('SingleBunch', 'MultiBunch')
    INJTYPE_MON = INJTYPE + ('Undefined', )
    PUMODE = ('Accumulation', 'Optimization', 'OnAxis')
    PUMODE_MON = PUMODE + ('Undefined', )
    TOPUPSTS = (
        'Off', 'Waiting', 'TurningOn', 'Injecting', 'TurningOff')
    INJSYSCMDSTS = ('Idle', 'On', 'Off')
    RFKILLBEAMMON = ('Idle', 'Kill')
    IDLERUNNING = ('Idle', 'Running')


_et = ETypes


# --- Const class ---

class Const(_csdev.Const):
    """Const class."""

    InjMode = _csdev.Const.register('InjMode', _et.INJMODE)
    InjType = _csdev.Const.register('InjType', _et.INJTYPE)
    InjTypeMon = _csdev.Const.register('InjTypeMon', _et.INJTYPE_MON)
    PUMode = _csdev.Const.register('PUMode', _et.PUMODE)
    PUModeMon = _csdev.Const.register('PUModeMon', _et.PUMODE_MON)
    TopUpSts = _csdev.Const.register('TopUpSts', _et.TOPUPSTS)
    InjSysCmdSts = _csdev.Const.register('InjSysCmdSts', _et.INJSYSCMDSTS)
    RFKillBeamMon = _csdev.Const.register('RFKillBeamMon', _et.RFKILLBEAMMON)
    IdleRunning = _csdev.Const.register('IdleRunning', _et.IDLERUNNING)

    GEN_STATUS_LABELS = ('LI', 'TB', 'BO', 'TS', 'SI', 'AS')
    LI_STATUS_LABELS = ('Egun', 'PS', 'PU', 'RF', 'TI')
    TL_STATUS_LABELS = ('PS', 'PU', 'TI')
    SR_STATUS_LABELS = ('PS', 'PU', 'RF', 'TI')
    AS_STATUS_LABELS = ('TI', )
    INJ_STATUS_LABELS = (
        'TI ContinuousEvt is off',
        'BucketList not synced',
        'EGBiasPS voltage diff. from desired',
        'EGFilaPS current diff. from op.value',
        'EGHVPS voltage diff. from op.value',
        'EGPulsePS setup is diff. from desired',
        'EGTriggerPS is off',
        'Inj.System is not on',
    )

    MIN_BKT = 1
    MAX_BKT = 864

    RF_RMP_TIMEOUT = 3*60  # [s]
    TI_INJ_TIMEOUT = 3*60  # [s]


_ct = Const


def get_status_labels(sec=''):
    """Return Status Labels enum."""
    if sec == 'LI':
        return _ct.LI_STATUS_LABELS
    if sec in ['TB', 'TS']:
        return _ct.TL_STATUS_LABELS
    if sec in ['BO', 'SI']:
        return _ct.SR_STATUS_LABELS
    if sec == 'AS':
        return _ct.AS_STATUS_LABELS
    if sec == 'Inj':
        return _ct.INJ_STATUS_LABELS
    return _ct.GEN_STATUS_LABELS


# --- Databases ---


def get_injctrl_propty_database():
    """Return property database of injection control IOC."""
    # injsys properties
    injsys_onorder = ','.join(_InjSysHandler.DEF_ON_ORDER)
    injsys_offorder = ','.join(_InjSysHandler.DEF_OFF_ORDER)
    # egun properties
    egsbbias = _EGun.BIAS_SINGLE_BUNCH
    egmbbias = _EGun.BIAS_MULTI_BUNCH
    egfilacurr = _EGun.FILACURR_OPVALUE
    eghvolt = _EGun.HV_OPVALUE

    dbase = {
        'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
        'Log-Mon': {'type': 'str', 'value': 'Starting...'},

        'Mode-Sel': {
            'type': 'enum', 'value': _ct.InjMode.Decay,
            'enums': _et.INJMODE},
        'Mode-Sts': {
            'type': 'enum', 'value': _ct.InjMode.Decay,
            'enums': _et.INJMODE},
        'Type-Sel': {
            'type': 'enum', 'value': _ct.InjType.MultiBunch,
            'enums': _et.INJTYPE},
        'Type-Sts': {
            'type': 'enum', 'value': _ct.InjType.MultiBunch,
            'enums': _et.INJTYPE},
        'Type-Mon': {
            'type': 'enum', 'value': _ct.InjTypeMon.Undefined,
            'enums': _et.INJTYPE_MON},
        'TypeCmdSts-Mon': {
            'type': 'enum', 'value': _ct.IdleRunning.Idle,
            'enums': _et.IDLERUNNING},
        'SglBunBiasVolt-SP': {
            'type': 'float', 'value': egsbbias, 'prec': 1,
            'unit': 'V', 'lolim': -150.0, 'hilim': 0.0},
        'SglBunBiasVolt-RB': {
            'type': 'float', 'value': egsbbias, 'prec': 1,
            'unit': 'V', 'lolim': -150.0, 'hilim': 0.0},
        'MultBunBiasVolt-SP': {
            'type': 'float', 'value': egmbbias, 'prec': 1,
            'unit': 'V', 'lolim': -150.0, 'hilim': 0.0},
        'MultBunBiasVolt-RB': {
            'type': 'float', 'value': egmbbias, 'prec': 1,
            'unit': 'V', 'lolim': -150.0, 'hilim': 0.0},
        'BiasVoltCmdSts-Mon': {
            'type': 'enum', 'value': _ct.IdleRunning.Idle,
            'enums': _et.IDLERUNNING},
        'FilaOpCurr-SP': {
            'type': 'float', 'value': egfilacurr, 'prec': 3,
            'unit': 'A', 'lolim': 0.0, 'hilim': 1.5},
        'FilaOpCurr-RB': {
            'type': 'float', 'value': egfilacurr, 'prec': 3,
            'unit': 'A', 'lolim': 0.0, 'hilim': 1.5},
        'FilaOpCurrCmdSts-Mon': {
            'type': 'enum', 'value': _ct.IdleRunning.Idle,
            'enums': _et.IDLERUNNING},
        'HVOpVolt-SP': {
            'type': 'float', 'value': eghvolt, 'prec': 3,
            'unit': 'kV', 'lolim': 0.0, 'hilim': 95.0},
        'HVOpVolt-RB': {
            'type': 'float', 'value': eghvolt, 'prec': 3,
            'unit': 'kV', 'lolim': 0.0, 'hilim': 95.0},
        'HVOpVoltCmdSts-Mon': {
            'type': 'enum', 'value': _ct.IdleRunning.Idle,
            'enums': _et.IDLERUNNING},
        'PUMode-Sel': {
            'type': 'enum', 'value': _ct.PUMode.Accumulation,
            'enums': _et.PUMODE},
        'PUMode-Sts': {
            'type': 'enum', 'value': _ct.PUMode.Accumulation,
            'enums': _et.PUMODE},
        'PUMode-Mon': {
            'type': 'enum', 'value': _ct.PUModeMon.Undefined,
            'enums': _et.PUMODE_MON},
        'PUModeCmdSts-Mon': {
            'type': 'enum', 'value': _ct.IdleRunning.Idle,
            'enums': _et.IDLERUNNING},
        'TargetCurrent-SP': {
            'type': 'float', 'value': 100.0, 'unit': 'mA',
            'prec': 2, 'lolim': 0.0, 'low': 0.0, 'lolo': 0.0,
            'hilim': 500.0, 'high': 500.0, 'hihi': 500.0},
        'TargetCurrent-RB': {
            'type': 'float', 'value': 100.0, 'unit': 'mA',
            'prec': 2, 'lolim': 0.0, 'low': 0.0, 'lolo': 0.0,
            'hilim': 500.0, 'high': 500.0, 'hihi': 500.0},
        'BucketListStart-SP': {
            'type': 'int', 'value': 1, 'unit': 'bucket index',
            'lolim': _ct.MIN_BKT, 'hilim': _ct.MAX_BKT},
        'BucketListStart-RB': {
            'type': 'int', 'value': 1, 'unit': 'bucket index',
            'lolim': _ct.MIN_BKT, 'hilim': _ct.MAX_BKT},
        'BucketListStop-SP': {
            'type': 'int', 'value': 864, 'unit': 'bucket index',
            'lolim': _ct.MIN_BKT, 'hilim': _ct.MAX_BKT, },
        'BucketListStop-RB': {
            'type': 'int', 'value': 864, 'unit': 'bucket index',
            'lolim': _ct.MIN_BKT, 'hilim': _ct.MAX_BKT},
        'BucketListStep-SP': {
            'type': 'int', 'value': 15, 'unit': 'buckets',
            'lolim': -_ct.MAX_BKT+1, 'hilim': _ct.MAX_BKT-1},
        'BucketListStep-RB': {
            'type': 'int', 'value': 15, 'unit': 'buckets',
            'lolim': -_ct.MAX_BKT+1, 'hilim': _ct.MAX_BKT-1},

        'TopUpState-Sel': {
            'type': 'enum', 'value': _ct.OffOn.Off, 'enums': _et.OFF_ON},
        'TopUpState-Sts': {
            'type': 'enum', 'value': _ct.TopUpSts.Off, 'enums': _et.TOPUPSTS},
        'TopUpPeriod-SP': {
            'type': 'int', 'value': 15*60, 'unit': 's',
            'lolim': 30, 'hilim': 6*60*60},
        'TopUpPeriod-RB': {
            'type': 'int', 'value': 15*60, 'unit': 's',
            'lolim': 30, 'hilim': 6*60*60},
        'TopUpNextInj-Mon': {
            'type': 'float', 'value': 0.0, 'unit': 's'},
        'TopUpNextInjRound-Cmd': {'type': 'int', 'value': 0},
        'TopUpNrPulses-SP': {
            'type': 'int', 'value': 1, 'unit': 'pulses',
            'lolim': _ct.MIN_BKT, 'hilim': _ct.MAX_BKT},
        'TopUpNrPulses-RB': {
            'type': 'int', 'value': 1, 'unit': 'pulses',
            'lolim': _ct.MIN_BKT, 'hilim': _ct.MAX_BKT},
        'AutoStop-Sel': {
            'type': 'enum', 'value': _ct.OffOn.Off, 'enums': _et.OFF_ON},
        'AutoStop-Sts': {
            'type': 'enum', 'value': _ct.OffOn.Off, 'enums': _et.OFF_ON},

        'InjSysTurnOn-Cmd': {'type': 'int', 'value': 0},
        'InjSysTurnOff-Cmd': {'type': 'int', 'value': 0},
        'InjSysCmdDone-Mon': {
            'type': 'string', 'value': ''},
        'InjSysCmdSts-Mon': {
            'type': 'enum', 'value': _ct.InjSysCmdSts.Idle,
            'enums': _et.INJSYSCMDSTS},
        'InjSysTurnOnOrder-SP': {'type': 'string', 'value': injsys_onorder},
        'InjSysTurnOnOrder-RB': {'type': 'string', 'value': injsys_onorder},
        'InjSysTurnOffOrder-SP': {'type': 'string', 'value': injsys_offorder},
        'InjSysTurnOffOrder-RB': {'type': 'string', 'value': injsys_offorder},

        'RFKillBeam-Cmd': {'type': 'int', 'value': 0},
        'RFKillBeam-Mon': {
            'type': 'enum', 'value': _ct.RFKillBeamMon.Idle,
            'enums': _et.RFKILLBEAMMON},

        'DiagStatusLI-Mon': {
            'type': 'int', 'value': 2**len(_ct.LI_STATUS_LABELS)-1},
        'DiagStatusLILabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.LI_STATUS_LABELS)},
        'DiagStatusTB-Mon': {
            'type': 'int', 'value': 2**len(_ct.TL_STATUS_LABELS)-1},
        'DiagStatusTBLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.TL_STATUS_LABELS)},
        'DiagStatusBO-Mon': {
            'type': 'int', 'value': 2**len(_ct.SR_STATUS_LABELS)-1},
        'DiagStatusBOLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.SR_STATUS_LABELS)},
        'DiagStatusTS-Mon': {
            'type': 'int', 'value': 2**len(_ct.TL_STATUS_LABELS)-1},
        'DiagStatusTSLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.TL_STATUS_LABELS)},
        'DiagStatusSI-Mon': {
            'type': 'int', 'value': 2**len(_ct.SR_STATUS_LABELS)-1},
        'DiagStatusSILabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.SR_STATUS_LABELS)},
        'DiagStatusAS-Mon': {
            'type': 'int', 'value': 2**len(_ct.AS_STATUS_LABELS)-1},
        'DiagStatusASLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.AS_STATUS_LABELS)},
        'DiagStatus-Mon': {
            'type': 'int', 'value': 2**len(_ct.GEN_STATUS_LABELS)-1},
        'DiagStatusLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.GEN_STATUS_LABELS)},
        'InjStatus-Mon': {
            'type': 'int', 'value': 2**len(_ct.INJ_STATUS_LABELS)-1},
        'InjStatusLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.INJ_STATUS_LABELS)},
    }
    dbase = _csdev.add_pvslist_cte(dbase)
    return dbase
