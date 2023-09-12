"""Injection Control App."""

from .. import csdev as _csdev


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    INJMODE = ('Decay', 'TopUp', 'Accum')
    INJTYPE = ('SingleBunch', 'MultiBunch')
    INJTYPE_MON = INJTYPE + ('Undefined', )
    PUMODE = ('Accumulation', 'Optimization', 'OnAxis')
    PUMODE_MON = PUMODE + ('Undefined', )
    TOPUPSTS = (
        'Off', 'Waiting', 'TurningOn', 'Injecting', 'TurningOff', 'Skipping')
    ACCUMSTS = ('Off', 'Waiting', 'TurningOn', 'Injecting')
    INJSYSCMDSTS = ('Idle', 'On', 'Off')
    RFKILLBEAMMON = ('Idle', 'Kill')
    IDLERUNNING = ('Idle', 'Running')
    IDLEINJECTING = ('Idle', 'Injecting')
    BIASFB_MODEL_TYPES = ('Linear', 'GaussianProcess')
    FIXED_UNFIXED = ('Fixed', 'Unfixed')
    STANDBY_INJECT = ('Standby', 'Inject')


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
    AccumSts = _csdev.Const.register('AccumSts', _et.ACCUMSTS)
    InjSysCmdSts = _csdev.Const.register('InjSysCmdSts', _et.INJSYSCMDSTS)
    RFKillBeamMon = _csdev.Const.register('RFKillBeamMon', _et.RFKILLBEAMMON)
    IdleRunning = _csdev.Const.register('IdleRunning', _et.IDLERUNNING)
    IdleInjecting = _csdev.Const.register('IdleInjecting', _et.IDLEINJECTING)
    BiasFBModelTypes = _csdev.Const.register(
        'ModelTypes', _et.BIASFB_MODEL_TYPES)
    FixedUnfixed = _csdev.Const.register('FixedUnfixed', _et.FIXED_UNFIXED)
    StandbyInject = _csdev.Const.register('StandbyInject', _et.STANDBY_INJECT)

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
    MAX_INJTIMEOUT = 3*60  # [s]

    BIAS_SINGLE_BUNCH = -100.0  # [V]
    BIAS_MULTI_BUNCH = -56.0  # [V]
    FILACURR_OPVALUE = 1.39  # [A]
    HV_OPVALUE = 90.0  # [kV]

    INJSYS_DEF_ON_ORDER = ['bo_rf', 'as_pu', 'bo_ps', 'li_rf']
    INJSYS_DEF_OFF_ORDER = ['bo_rf', 'li_rf', 'as_pu', 'bo_ps']

    BIASFB_AHEADSETIME = 10  # [s]
    BIASFB_MINIMUM_LIFETIME = 1800  # [s]
    BIASFB_PROPTY_PREFIX = 'BiasFB'
    BIASFB_MAX_DATA_SIZE = 1000


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
    injsys_onorder = ','.join(_ct.INJSYS_DEF_ON_ORDER)
    injsys_offorder = ','.join(_ct.INJSYS_DEF_OFF_ORDER)
    # egun properties
    egsbbias = _ct.BIAS_SINGLE_BUNCH
    egmbbias = _ct.BIAS_MULTI_BUNCH
    egfilacurr = _ct.FILACURR_OPVALUE
    eghvolt = _ct.HV_OPVALUE

    dbase = {
        'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
        'Log-Mon': {'type': 'str', 'value': 'Starting...'},

        'Mode-Sel': {
            'type': 'enum', 'value': _ct.InjMode.Decay,
            'enums': _et.INJMODE, 'unit': 'Decay_Topup_Accum'},
        'Mode-Sts': {
            'type': 'enum', 'value': _ct.InjMode.Decay,
            'enums': _et.INJMODE, 'unit': 'Decay_Topup_Accum'},
        'Type-Sel': {
            'type': 'enum', 'value': _ct.InjType.MultiBunch,
            'enums': _et.INJTYPE, 'unit': 'SB_MB'},
        'Type-Sts': {
            'type': 'enum', 'value': _ct.InjType.MultiBunch,
            'enums': _et.INJTYPE, 'unit': 'SB_MB'},
        'Type-Mon': {
            'type': 'enum', 'value': _ct.InjTypeMon.Undefined,
            'enums': _et.INJTYPE_MON, 'unit': 'SB_MB_Und'},
        'TypeCmdSts-Mon': {
            'type': 'enum', 'value': _ct.IdleRunning.Idle,
            'enums': _et.IDLERUNNING, 'unit': 'Idle_Run'},
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
            'enums': _et.IDLERUNNING, 'unit': 'Idle_Run'},
        'FilaOpCurr-SP': {
            'type': 'float', 'value': egfilacurr, 'prec': 3,
            'unit': 'A', 'lolim': 0.0, 'hilim': 1.5},
        'FilaOpCurr-RB': {
            'type': 'float', 'value': egfilacurr, 'prec': 3,
            'unit': 'A', 'lolim': 0.0, 'hilim': 1.5},
        'FilaOpCurrCmdSts-Mon': {
            'type': 'enum', 'value': _ct.IdleRunning.Idle,
            'enums': _et.IDLERUNNING, 'unit': 'Idle_Run'},
        'HVOpVolt-SP': {
            'type': 'float', 'value': eghvolt, 'prec': 3,
            'unit': 'kV', 'lolim': 0.0, 'hilim': 95.0},
        'HVOpVolt-RB': {
            'type': 'float', 'value': eghvolt, 'prec': 3,
            'unit': 'kV', 'lolim': 0.0, 'hilim': 95.0},
        'HVOpVoltCmdSts-Mon': {
            'type': 'enum', 'value': _ct.IdleRunning.Idle,
            'enums': _et.IDLERUNNING, 'unit': 'Idle_Run'},
        'PUMode-Sel': {
            'type': 'enum', 'value': _ct.PUMode.Accumulation,
            'enums': _et.PUMODE, 'unit': 'Acq_Opt_OnA'},
        'PUMode-Sts': {
            'type': 'enum', 'value': _ct.PUMode.Accumulation,
            'enums': _et.PUMODE, 'unit': 'Acq_Opt_OnA'},
        'PUMode-Mon': {
            'type': 'enum', 'value': _ct.PUModeMon.Undefined,
            'enums': _et.PUMODE_MON, 'unit': 'Acq_Opt_OnA_Und'},
        'PUModeCmdSts-Mon': {
            'type': 'enum', 'value': _ct.IdleRunning.Idle,
            'enums': _et.IDLERUNNING, 'unit': 'Idle_Run'},
        'PUModeDeltaPosAng-SP': {
            'type': 'float', 'value': 2.5, 'unit': 'mrad',
            'prec': 3, 'lolim': 0.0, 'low': 0.0, 'lolo': 0.0,
            'hilim': 5.0, 'high': 5.0, 'hihi': 5.0},
        'PUModeDeltaPosAng-RB': {
            'type': 'float', 'value': 2.5, 'unit': 'mrad',
            'prec': 3, 'lolim': 0.0, 'low': 0.0, 'lolo': 0.0,
            'hilim': 5.0, 'high': 5.0, 'hihi': 5.0},
        'PUModeDpKckrDlyRef-SP': {
            'type': 'float', 'value': 36.8e6, 'unit': 'hard',
            'prec': 0, 'lolim': 0.0, 'low': 0.0, 'lolo': 0.0,
            'hilim': 37.0e6, 'high': 37.0e6, 'hihi': 37.0e6},
        'PUModeDpKckrDlyRef-RB': {
            'type': 'float', 'value': 36.8e6, 'unit': 'hard',
            'prec': 0, 'lolim': 0.0, 'low': 0.0, 'lolo': 0.0,
            'hilim': 37.0e6, 'high': 37.0e6, 'hihi': 37.0e6},
        'PUModeDpKckrKick-SP': {
            'type': 'float', 'value': -6.7, 'unit': 'mrad',
            'prec': 3, 'lolim': -8.0, 'low': -8.0, 'lolo': -8.0,
            'hilim': 0.0, 'high': 0.0, 'hihi': 0.0},
        'PUModeDpKckrKick-RB': {
            'type': 'float', 'value': -6.7, 'unit': 'mrad',
            'prec': 3, 'lolim': -8.0, 'low': -8.0, 'lolo': -8.0,
            'hilim': 0.0, 'high': 0.0, 'hihi': 0.0},
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
            'type': 'int', 'value': 29, 'unit': 'buckets',
            'lolim': -_ct.MAX_BKT, 'hilim': _ct.MAX_BKT},
        'BucketListStep-RB': {
            'type': 'int', 'value': 29, 'unit': 'buckets',
            'lolim': -_ct.MAX_BKT, 'hilim': _ct.MAX_BKT},
        'IsInjecting-Mon': {
            'type': 'enum', 'value': _ct.IdleInjecting.Idle,
            'enums': _et.IDLEINJECTING, 'unit': 'Idle_Inj'},
        'IsInjDelay-SP': {
            'type': 'int', 'value': 0, 'unit': 'ms',
            'lolim': 0, 'hilim': 1000},
        'IsInjDelay-RB': {
            'type': 'int', 'value': 0, 'unit': 'ms',
            'lolim': 0, 'hilim': 1000},
        'IsInjDuration-SP': {
            'type': 'int', 'value': 300, 'unit': 'ms',
            'lolim': 0, 'hilim': 1000},
        'IsInjDuration-RB': {
            'type': 'int', 'value': 300, 'unit': 'ms',
            'lolim': 0, 'hilim': 1000},

        'AccumState-Sel': {
            'type': 'enum', 'value': _ct.OffOn.Off,
            'enums': _et.OFF_ON, 'unit': 'Off_On'},
        'AccumState-Sts': {
            'type': 'enum', 'value': _ct.AccumSts.Off, 'enums': _et.ACCUMSTS,
            'unit': 'Off_Wai_TOn_Inj_TOff_Skip'},
        'AccumPeriod-SP': {
            'type': 'int', 'value': 5, 'unit': 's',
            'lolim': 1, 'hilim': 60*60},
        'AccumPeriod-RB': {
            'type': 'int', 'value': 5, 'unit': 's',
            'lolim': 1, 'hilim': 60*60},

        'TopUpState-Sel': {
            'type': 'enum', 'value': _ct.OffOn.Off,
            'enums': _et.OFF_ON, 'unit': 'Off_On'},
        'TopUpState-Sts': {
            'type': 'enum', 'value': _ct.TopUpSts.Off, 'enums': _et.TOPUPSTS,
            'unit': 'Off_Wai_TOn_Inj_TOff_Skip'},
        'TopUpPeriod-SP': {
            'type': 'int', 'value': 3, 'unit': 'min',
            'lolim': 1, 'hilim': 6*60},
        'TopUpPeriod-RB': {
            'type': 'int', 'value': 3, 'unit': 'min',
            'lolim': 1, 'hilim': 6*60},
        'TopUpHeadStartTime-SP': {
            'type': 'float', 'value': 0, 'unit': 's', 'prec': 2,
            'lolim': 0, 'hilim': 2*60},
        'TopUpHeadStartTime-RB': {
            'type': 'float', 'value': 0, 'unit': 's', 'prec': 2,
            'lolim': 0, 'hilim': 2*60},
        'TopUpPUStandbyEnbl-Sel': {
            'type': 'enum', 'value': _ct.DsblEnbl.Dsbl,
            'enums': _et.DSBL_ENBL, 'unit': 'Dsbl_Enbl'},
        'TopUpPUStandbyEnbl-Sts': {
            'type': 'enum', 'value': _ct.DsblEnbl.Dsbl,
            'enums': _et.DSBL_ENBL, 'unit': 'Dsbl_Enbl'},
        'TopUpPUWarmUpTime-SP': {
            'type': 'float', 'value': 30, 'unit': 's', 'prec': 1,
            'lolim': 0, 'hilim': 2*60},
        'TopUpPUWarmUpTime-RB': {
            'type': 'float', 'value': 30, 'unit': 's', 'prec': 1,
            'lolim': 0, 'hilim': 2*60},
        'TopUpLIWarmUpEnbl-Sel': {
            'type': 'enum', 'value': _ct.DsblEnbl.Dsbl,
            'enums': _et.DSBL_ENBL, 'unit': 'Dsbl_Enbl'},
        'TopUpLIWarmUpEnbl-Sts': {
            'type': 'enum', 'value': _ct.DsblEnbl.Dsbl,
            'enums': _et.DSBL_ENBL, 'unit': 'Dsbl_Enbl'},
        'TopUpLIWarmUpTime-SP': {
            'type': 'float', 'value': 30, 'unit': 's', 'prec': 1,
            'lolim': 0, 'hilim': 2*60},
        'TopUpLIWarmUpTime-RB': {
            'type': 'float', 'value': 30, 'unit': 's', 'prec': 1,
            'lolim': 0, 'hilim': 2*60},
        'TopUpBOPSStandbyEnbl-Sel': {
            'type': 'enum', 'value': _ct.DsblEnbl.Dsbl,
            'enums': _et.DSBL_ENBL, 'unit': 'Dsbl_Enbl'},
        'TopUpBOPSStandbyEnbl-Sts': {
            'type': 'enum', 'value': _ct.DsblEnbl.Dsbl,
            'enums': _et.DSBL_ENBL, 'unit': 'Dsbl_Enbl'},
        'TopUpBOPSWarmUpTime-SP': {
            'type': 'float', 'value': 10, 'unit': 's', 'prec': 1,
            'lolim': 0, 'hilim': 2*60},
        'TopUpBOPSWarmUpTime-RB': {
            'type': 'float', 'value': 10, 'unit': 's', 'prec': 1,
            'lolim': 0, 'hilim': 2*60},
        'TopUpBORFStandbyEnbl-Sel': {
            'type': 'enum', 'value': _ct.DsblEnbl.Dsbl,
            'enums': _et.DSBL_ENBL, 'unit': 'Dsbl_Enbl'},
        'TopUpBORFStandbyEnbl-Sts': {
            'type': 'enum', 'value': _ct.DsblEnbl.Dsbl,
            'enums': _et.DSBL_ENBL, 'unit': 'Dsbl_Enbl'},
        'TopUpBORFWarmUpTime-SP': {
            'type': 'float', 'value': 10, 'unit': 's', 'prec': 1,
            'lolim': 0, 'hilim': 2*60},
        'TopUpBORFWarmUpTime-RB': {
            'type': 'float', 'value': 10, 'unit': 's', 'prec': 1,
            'lolim': 0, 'hilim': 2*60},
        'TopUpNextInj-Mon': {
            'type': 'float', 'value': 0.0, 'unit': 's'},
        'TopUpNrPulses-SP': {
            'type': 'int', 'value': 1, 'unit': 'pulses',
            'lolim': _ct.MIN_BKT, 'hilim': _ct.MAX_BKT},
        'TopUpNrPulses-RB': {
            'type': 'int', 'value': 1, 'unit': 'pulses',
            'lolim': _ct.MIN_BKT, 'hilim': _ct.MAX_BKT},

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

        'RFKillBeam-Cmd': {'type': 'int', 'value': 0, 'unit': '#'},
        'RFKillBeam-Mon': {
            'type': 'enum', 'value': _ct.RFKillBeamMon.Idle,
            'enums': _et.RFKILLBEAMMON, 'unit': 'Idle_Kill'},

        'DiagStatusLI-Mon': {
            'type': 'int', 'value': 2**len(_ct.LI_STATUS_LABELS)-1,
            'unit': '2^_Eg_PS_PU_RF_TI'},
        'DiagStatusLILabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.LI_STATUS_LABELS)},
        'DiagStatusTB-Mon': {
            'type': 'int', 'value': 2**len(_ct.TL_STATUS_LABELS)-1,
            'unit': '2^_PS_PU_TI'},
        'DiagStatusTBLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.TL_STATUS_LABELS)},
        'DiagStatusBO-Mon': {
            'type': 'int', 'value': 2**len(_ct.SR_STATUS_LABELS)-1,
            'unit': '2^_PS_PU_RF_TI'},
        'DiagStatusBOLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.SR_STATUS_LABELS)},
        'DiagStatusTS-Mon': {
            'type': 'int', 'value': 2**len(_ct.TL_STATUS_LABELS)-1,
            'unit': '2^_PS_PU_TI'},
        'DiagStatusTSLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.TL_STATUS_LABELS)},
        'DiagStatusSI-Mon': {
            'type': 'int', 'value': 2**len(_ct.SR_STATUS_LABELS)-1,
            'unit': '2^_PS_PU_RF_TI'},
        'DiagStatusSILabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.SR_STATUS_LABELS)},
        'DiagStatusAS-Mon': {
            'type': 'int', 'value': 2**len(_ct.AS_STATUS_LABELS)-1,
            'unit': '2^_TI'},
        'DiagStatusASLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.AS_STATUS_LABELS)},
        'DiagStatus-Mon': {
            'type': 'int', 'value': 2**len(_ct.GEN_STATUS_LABELS)-1,
            'unit': '2^_LI_TB_BO_TS_SI_AS'},
        'DiagStatusLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.GEN_STATUS_LABELS)},
        'InjStatus-Mon': {
            'type': 'int', 'value': 2**len(_ct.INJ_STATUS_LABELS)-1,
            'unit': '2^Evt_BucL_Bias_Fila_HV_Pulse_Trig_InjS'},
        'InjStatusLabels-Cte': {
            'type': 'char', 'count': 1000,
            'value': '\n'.join(_ct.INJ_STATUS_LABELS)},
    }
    dbase = _csdev.add_pvslist_cte(dbase)
    return dbase


def get_biasfb_database():
    """."""
    dbase = {
        'LoopState-Sel': {
            'type': 'enum', 'value': _ct.OffOn.On, 'enums': _et.OFF_ON,
            'unit': 'Off_On'},
        'LoopState-Sts': {
            'type': 'enum', 'value': _ct.OffOn.On, 'enums': _et.OFF_ON,
            'unit': 'Off_On'},
        'MinVoltage-SP': {
            'type': 'float', 'value': -52, 'unit': 'V',
            'prec': 1, 'lolim': -120, 'hilim': -30.0},
        'MinVoltage-RB': {
            'type': 'float', 'value': -52, 'unit': 'V',
            'prec': 1, 'lolim': -120, 'hilim': -30.0},
        'MaxVoltage-SP': {
            'type': 'float', 'value': -45, 'unit': 'V',
            'prec': 1, 'lolim': -120, 'hilim': -30.0},
        'MaxVoltage-RB': {
            'type': 'float', 'value': -45, 'unit': 'V',
            'prec': 1, 'lolim': -120, 'hilim': -30.0},

        'ModelType-Sel': {
            'type': 'enum', 'value': _ct.BiasFBModelTypes.GaussianProcess,
            'enums': _et.BIASFB_MODEL_TYPES, 'unit': 'Lin_GP'},
        'ModelType-Sts': {
            'type': 'enum', 'value': _ct.BiasFBModelTypes.GaussianProcess,
            'enums': _et.BIASFB_MODEL_TYPES, 'unit': 'Lin_GP'},
        'ModelMaxNrPts-SP': {
            'type': 'int', 'value': 20, 'unit': '#',
            'lolim': 2, 'hilim': _ct.BIASFB_MAX_DATA_SIZE},
        'ModelMaxNrPts-RB': {
            'type': 'int', 'value': 20, 'unit': '#',
            'lolim': 2, 'hilim': _ct.BIASFB_MAX_DATA_SIZE},
        'ModelNrPts-Mon': {
            'type': 'int', 'value': 20, 'unit': '#',
            'lolim': 2, 'hilim': _ct.BIASFB_MAX_DATA_SIZE},
        'ModelFitParamsNow-Cmd': {'type': 'int', 'value': 0},
        'ModelAutoFitParams-Sel': {
            'type': 'enum', 'value': _ct.OffOn.On, 'enums': _et.OFF_ON,
            'unit': 'Off_On'},
        'ModelAutoFitParams-Sts': {
            'type': 'enum', 'value': _ct.OffOn.On, 'enums': _et.OFF_ON,
            'unit': 'Off_On'},
        'ModelAutoFitEveryNrPts-SP': {
            'type': 'int', 'value': 1, 'unit': '#',
            'lolim': 1, 'hilim': _ct.BIASFB_MAX_DATA_SIZE},
        'ModelAutoFitEveryNrPts-RB': {
            'type': 'int', 'value': 1, 'unit': '#',
            'lolim': 1, 'hilim': _ct.BIASFB_MAX_DATA_SIZE},
        'ModelNrPtsAfterFit-Mon': {
            'type': 'int', 'value': 1, 'unit': '#',
            'lolim': 1, 'hilim': _ct.BIASFB_MAX_DATA_SIZE},
        'ModelUpdateData-Sel': {
            'type': 'enum', 'value': _ct.OffOn.On, 'enums': _et.OFF_ON,
            'unit': 'Off_On'},
        'ModelUpdateData-Sts': {
            'type': 'enum', 'value': _ct.OffOn.On, 'enums': _et.OFF_ON,
            'unit': 'Off_On'},
        'ModelDataBias-SP': {
            'type': 'float', 'count': _ct.BIASFB_MAX_DATA_SIZE,
            'value': [0]*_ct.BIASFB_MAX_DATA_SIZE, 'unit': 'V'},
        'ModelDataBias-RB': {
            'type': 'float', 'count': _ct.BIASFB_MAX_DATA_SIZE,
            'value': [0]*_ct.BIASFB_MAX_DATA_SIZE, 'unit': 'V'},
        'ModelDataBias-Mon': {
            'type': 'float', 'count': _ct.BIASFB_MAX_DATA_SIZE,
            'value': [0]*_ct.BIASFB_MAX_DATA_SIZE, 'unit': 'V'},
        'ModelDataInjCurr-SP': {
            'type': 'float', 'count': _ct.BIASFB_MAX_DATA_SIZE,
            'value': [0]*_ct.BIASFB_MAX_DATA_SIZE, 'unit': 'mA'},
        'ModelDataInjCurr-RB': {
            'type': 'float', 'count': _ct.BIASFB_MAX_DATA_SIZE,
            'value': [0]*_ct.BIASFB_MAX_DATA_SIZE, 'unit': 'mA'},
        'ModelDataInjCurr-Mon': {
            'type': 'float', 'count': _ct.BIASFB_MAX_DATA_SIZE,
            'value': [0]*_ct.BIASFB_MAX_DATA_SIZE, 'unit': 'mA'},

        'LinModAngCoeff-SP': {
            'type': 'float', 'value': 15, 'unit': 'V/mA',
            'prec': 2, 'lolim': 0.1, 'hilim': 30.0},
        'LinModAngCoeff-RB': {
            'type': 'float', 'value': 15, 'unit': 'V/mA',
            'prec': 2, 'lolim': 0.1, 'hilim': 30.0},
        'LinModAngCoeff-Mon': {
            'type': 'float', 'value': 15, 'unit': 'V/mA',
            'prec': 2, 'lolim': 0.1, 'hilim': 30.0},
        'LinModOffCoeff-SP': {
            'type': 'float', 'value': -52, 'unit': 'V/mA',
            'prec': 2, 'lolim': -120, 'hilim': -30.0},
        'LinModOffCoeff-RB': {
            'type': 'float', 'value': -52, 'unit': 'V/mA',
            'prec': 2, 'lolim': -120, 'hilim': -30.0},
        'LinModOffCoeff-Mon': {
            'type': 'float', 'value': -52, 'unit': 'V/mA',
            'prec': 2, 'lolim': -120, 'hilim': -30.0},

        # These are used to give the model inference about the bias
        # Generally ploted in Injcurr X Bias graphs
        'LinModInferenceInjCurr-Mon': {
            'type': 'float', 'count': 100, 'value': [0]*100, 'unit': 'mA'},
        'LinModInferenceBias-Mon': {
            'type': 'float', 'count': 100, 'value': [0]*100, 'unit': 'V'},

        # These are used to give the model prediction about current
        # Generally ploted in Bias x InjCurr graphs to check model sanity
        'LinModPredBias-Mon': {
            'type': 'float', 'count': 100, 'value': [0]*100, 'unit': 'V'},
        'LinModPredInjCurrAvg-Mon': {
            'type': 'float', 'count': 100, 'value': [0]*100, 'unit': 'mA'},

        'GPModNoiseStd-SP': {
            'type': 'float', 'value': 0.0316, 'unit': 'mA', 'prec': 4,
            'lolim': 0.005, 'hilim': 0.5},
        'GPModNoiseStd-RB': {
            'type': 'float', 'value': 0.0316, 'unit': 'mA', 'prec': 4,
            'lolim': 0.005, 'hilim': 0.5},
        'GPModNoiseStd-Mon': {
            'type': 'float', 'value': 0.0316, 'unit': 'mA', 'prec': 4,
            'lolim': 0.005, 'hilim': 0.5},
        'GPModKernStd-SP': {
            'type': 'float', 'value': 0.432, 'unit': 'mA', 'prec': 3,
            'lolim': 0.05, 'hilim': 1},
        'GPModKernStd-RB': {
            'type': 'float', 'value': 0.432, 'unit': 'mA', 'prec': 3,
            'lolim': 0.05, 'hilim': 1},
        'GPModKernStd-Mon': {
            'type': 'float', 'value': 0.432, 'unit': 'mA', 'prec': 3,
            'lolim': 0.05, 'hilim': 1},
        'GPModKernLenScl-SP': {
            'type': 'float', 'value': 4, 'unit': 'V', 'prec': 3,
            'lolim': 2, 'hilim': 10},
        'GPModKernLenScl-RB': {
            'type': 'float', 'value': 4, 'unit': 'V', 'prec': 3,
            'lolim': 2, 'hilim': 10},
        'GPModKernLenScl-Mon': {
            'type': 'float', 'value': 4, 'unit': 'V', 'prec': 3,
            'lolim': 2, 'hilim': 10},

        # These properties are used to fix or unfix the fitting of the
        # gp parameters.
        'GPModNoiseStdFit-Sel': {
            'type': 'enum', 'value': _ct.FixedUnfixed.Unfixed,
            'enums': _et.FIXED_UNFIXED, 'unit': 'Fixed_Unfixed'},
        'GPModNoiseStdFit-Sts': {
            'type': 'enum', 'value': _ct.FixedUnfixed.Unfixed,
            'enums': _et.FIXED_UNFIXED, 'unit': 'Fixed_Unfixed'},
        'GPModKernStdFit-Sel': {
            'type': 'enum', 'value': _ct.FixedUnfixed.Unfixed,
            'enums': _et.FIXED_UNFIXED, 'unit': 'Fixed_Unfixed'},
        'GPModKernStdFit-Sts': {
            'type': 'enum', 'value': _ct.FixedUnfixed.Unfixed,
            'enums': _et.FIXED_UNFIXED, 'unit': 'Fixed_Unfixed'},
        'GPModKernLenSclFit-Sel': {
            'type': 'enum', 'value': _ct.FixedUnfixed.Fixed,
            'enums': _et.FIXED_UNFIXED, 'unit': 'Fixed_Unfixed'},
        'GPModKernLenSclFit-Sts': {
            'type': 'enum', 'value': _ct.FixedUnfixed.Fixed,
            'enums': _et.FIXED_UNFIXED, 'unit': 'Fixed_Unfixed'},


        # These are used to give the model inference about the bias
        # Generally ploted in Injcurr X Bias graphs
        'GPModInferenceInjCurr-Mon': {
            'type': 'float', 'count': 100, 'value': [0]*100, 'unit': 'mA'},
        'GPModInferenceBias-Mon': {
            'type': 'float', 'count': 100, 'value': [0]*100, 'unit': 'V'},

        # These are used to give the model prediction about current
        # Generally ploted in Bias x InjCurr graphs to check model sanity
        'GPModPredBias-Mon': {
            'type': 'float', 'count': 100, 'value': [0]*100, 'unit': 'V'},
        'GPModPredInjCurrAvg-Mon': {
            'type': 'float', 'count': 100, 'value': [0]*100, 'unit': 'mA'},
        'GPModPredInjCurrStd-Mon': {
            'type': 'float', 'count': 100, 'value': [0]*100, 'unit': 'mA'},
        }
    return {_ct.BIASFB_PROPTY_PREFIX+k: v for k, v in dbase.items()}
