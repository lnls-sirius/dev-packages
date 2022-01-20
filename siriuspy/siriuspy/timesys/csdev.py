"""Define properties of all timing devices and their connections."""

from copy import deepcopy as _dcopy
import numpy as _np
from mathphys import constants as _c

from ..util import ClassProperty as _classproperty
from .. import csdev as _csdev
from ..optics import constants as _oc
from ..search import HLTimeSearch as _HLTimeSearch


# --- Enumeration Types ---

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    EVT_MODES = ('Disabled', 'Continuous', 'Injection', 'OneShot', 'External')
    TRIG_SRC_LL = (
        'Dsbl', 'Trigger', 'Clock0', 'Clock1', 'Clock2',
        'Clock3', 'Clock4', 'Clock5', 'Clock6', 'Clock7')
    LOCKLL = ('Unlocked', 'Locked')
    DLYTYP = ('Manual', 'Auto')
    ININJTAB = ('No', 'Yes')
    RFOUT = ('OFF', '5RF/2', '5RF/4', 'RF', 'RF/2', 'RF/4')


_et = ETypes  # syntactic sugar


class Const(_csdev.Const):
    """Constants important for the timing system."""

    AC_FREQUENCY = 60  # [Hz]
    RF_DIVISION = 4
    RF_FREQUENCY = \
        _c.light_speed / _oc.SI.circumference * _oc.SI.harmonic_number
    BASE_FREQUENCY = RF_FREQUENCY / RF_DIVISION
    RF_PERIOD = 1/RF_FREQUENCY
    BASE_DELAY = 1 / BASE_FREQUENCY
    RF_DELAY = BASE_DELAY / 20
    FINE_DELAY = 5e-12  # [s] (five picoseconds)

    EvtModes = _csdev.Const.register('EvtModes', _et.EVT_MODES)
    EvtDlyTyp = _csdev.Const.register('EvtDlyTyp', _et.FIXED_INCR)
    ClockStates = _csdev.Const.register('ClockStates', _et.DSBL_ENBL)
    TrigStates = _csdev.Const.register('TrigStates', _et.DSBL_ENBL)
    TrigPol = _csdev.Const.register('TrigPol', _et.NORM_INV)
    LowLvlLock = _csdev.Const.register('LowLvlLock', _et.LOCKLL)
    TrigDlyTyp = _csdev.Const.register('TrigDlyTyp', _et.DLYTYP)
    InInjTab = _csdev.Const.register('TrigDlyTyp', _et.ININJTAB)
    TrigSrcLL = _csdev.Const.register('TrigSrcLL', _et.TRIG_SRC_LL)
    HLTrigStatusLabels = (
        'All PVs connected',
        'Device Enabled',
        'Fout Enabled',
        'EVG Enabled',
        'Network Ok',
        'UPLink Ok',
        'DownLink Ok',
        'Fout DownLink Ok',
        'EVG DownLink Ok',
        'Interlock Status',
        )

    __EvtHL2LLMap = None
    __EvtLL2HLMap = None

    evt_ll_codes = list(range(64)) + [124]
    evt_ll_names = ['Evt{0:02d}'.format(i) for i in evt_ll_codes]
    EvtLL = _csdev.Const.register(
                    'EventsLL', evt_ll_names, values=evt_ll_codes)
    del evt_ll_codes, evt_ll_names  # cleanup class namespace

    ClkHL2LLMap = {
        'Clock0': 'Clk0', 'Clock1': 'Clk1',
        'Clock2': 'Clk2', 'Clock3': 'Clk3',
        'Clock4': 'Clk4', 'Clock5': 'Clk5',
        'Clock6': 'Clk6', 'Clock7': 'Clk7'}
    ClkLL2HLMap = {val: key for key, val in ClkHL2LLMap.items()}

    clk_ll_codes = list(range(8))
    clk_ll_names = ['Clk{0:d}'.format(i) for i in clk_ll_codes]
    ClkLL = _csdev.Const.register(
                    'ClocksLL', clk_ll_names, values=clk_ll_codes)
    del clk_ll_names, clk_ll_codes

    @_classproperty
    def EvtHL2LLMap(cls):
        """."""
        if cls.__EvtHL2LLMap is None:
            cls.__EvtHL2LLMap = _HLTimeSearch.get_hl_events()
            cls.__EvtLL2HLMap = {
                val: key for key, val in cls.__EvtHL2LLMap.items()}
        return cls.__EvtHL2LLMap

    @_classproperty
    def EvtLL2HLMap(cls):
        """."""
        cls.EvtHL2LLMap
        return cls.__EvtLL2HLMap


def get_otp_database(otp_num=0, prefix=None):
    """Return otp_database."""
    def_prefix = 'OTP{0:02d}'.format(otp_num)
    prefix = def_prefix if prefix is None else prefix
    dbase = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    dbase[prefix+'State-Sts'] = dic_
    dbase[prefix+'State-Sel'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 1, 'low': 1, 'lolim': 1,
        'hilim': 63, 'high': 63, 'hihi': 63}
    dbase[prefix+'Evt-SP'] = dic_
    dbase[prefix+'Evt-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 1, 'low': 1, 'lolim': 1,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    dbase[prefix+'Width-SP'] = dic_
    dbase[prefix+'Width-RB'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.NORM_INV}
    dbase[prefix+'Polarity-Sts'] = dic_
    dbase[prefix+'Polarity-Sel'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    dbase[prefix+'NrPulses-SP'] = dic_
    dbase[prefix+'NrPulses-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    dbase[prefix+'Delay-SP'] = dic_
    dbase[prefix+'Delay-RB'] = _dcopy(dic_)

    return dbase


def get_out_database(out_num=0, equip='EVR', prefix=None):
    """Return out_database."""
    def_prefix = 'OUT{0:d}'.format(out_num)
    prefix = def_prefix if prefix is None else prefix
    dbase = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.TRIG_SRC_LL}
    dbase[prefix+'Src-Sts'] = dic_
    dbase[prefix+'Src-Sel'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DLYTYP}
    dbase[prefix+'RFDelayType-Sts'] = dic_
    dbase[prefix+'RFDelayType-Sel'] = _dcopy(dic_)

    max_trig = 23 if equip == 'EVR' else 15
    num_trig = out_num + 12 if equip == 'EVR' else out_num
    dic_ = {
        'type': 'int', 'value': num_trig, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': max_trig, 'high': max_trig, 'hihi': max_trig}
    dbase[prefix+'SrcTrig-SP'] = dic_
    dbase[prefix+'SrcTrig-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 30, 'high': 30, 'hihi': 30}
    dbase[prefix+'RFDelay-SP'] = dic_
    dbase[prefix+'RFDelay-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 200, 'high': 200, 'hihi': 200}
    dbase[prefix+'FineDelay-SP'] = dic_
    dbase[prefix+'FineDelay-RB'] = _dcopy(dic_)

    return dbase


def get_afc_out_database(out_num=0, out_tp='FMC', prefix=None):
    """Return afc_database."""
    def_prefix = (out_tp + '{0:d}'.format(out_num))
    if out_tp == 'FMC':
        fmc = (out_num // 5) + 1
        ch = (out_num % 5) + 1
        def_prefix = (out_tp + '{0:d}CH{1:d}'.format(fmc, ch))

    prefix = def_prefix if prefix is None else prefix
    dbase = get_otp_database(prefix=prefix)
    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.TRIG_SRC_LL}
    dbase[prefix+'Src-Sts'] = dic_
    dbase[prefix+'Src-Sel'] = _dcopy(dic_)

    return dbase


def get_evr_database(prefix=None):
    """Return evr_database."""
    prefix = prefix or ''
    dbase = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    dbase[prefix+'DevEnbl-Sts'] = dic_
    dbase[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    dbase[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    dbase[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    dbase[prefix+'Network-Mon'] = {
        'type': 'enum', 'value': 1,
        'enums': _et.DISCONN_CONN}

    dbase[prefix+'LinkStatus-Mon'] = {
        'type': 'enum', 'value': 1,
        'enums': _et.UNLINK_LINK}

    dbase[prefix+'IntlkStatus-Mon'] = {
        'type': 'enum', 'value': 0,
        'enums': _et.DSBL_ENBL}

    dbase[prefix+'IntlkEnbl-Mon'] = {
        'type': 'enum', 'value': 0,
        'enums': _et.DSBL_ENBL}

    for i in range(24):
        db2 = get_otp_database(otp_num=i)
        for k, v in db2.items():
            dbase[prefix + k] = v

    for i in range(8):
        db2 = get_out_database(out_num=i, equip='EVR')
        for k, v in db2.items():
            dbase[prefix + k] = v
    return dbase


def get_eve_database(eve_num=1, prefix=None):
    """Return eve_database."""
    prefix = prefix or ''
    dbase = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    dbase[prefix+'DevEnbl-Sts'] = dic_
    dbase[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.RFOUT}
    dbase[prefix+'RFOut-Sts'] = dic_
    dbase[prefix+'RFOut-Sel'] = _dcopy(dic_)

    dbase[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    dbase[prefix+'Network-Mon'] = {
        'type': 'enum', 'value': 1,
        'enums': _et.DISCONN_CONN}

    dbase[prefix+'LinkStatus-Mon'] = {
        'type': 'enum', 'value': 1,
        'enums': _et.UNLINK_LINK}

    dbase[prefix+'IntlkStatus-Mon'] = {
        'type': 'enum', 'value': 0,
        'enums': _et.DSBL_ENBL}

    dbase[prefix+'IntlkEnbl-Mon'] = {
        'type': 'enum', 'value': 0,
        'enums': _et.DSBL_ENBL}

    for i in range(24):
        db2 = get_otp_database(otp_num=i)
        for k, v in db2.items():
            dbase[prefix + k] = v

    for i in range(8):
        db2 = get_out_database(out_num=i, equip='EVE')
        for k, v in db2.items():
            dbase[prefix + k] = v

    return dbase


def get_afc_database(prefix=None):
    """Return adc_database."""
    prefix = prefix or ''
    dbase = dict()
    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    dbase[prefix+'DevEnbl-Sts'] = dic_
    dbase[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    dbase[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    dbase[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    dbase[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    dbase[prefix+'LinkStatus-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.UNLINK_LINK}

    dbase[prefix+'IntlkStatus-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}

    for i in range(8):
        db2 = get_afc_out_database(out_num=i, out_tp='AMC')
        for k, v in db2.items():
            dbase[prefix + k] = v

    for i in range(10):
        db2 = get_afc_out_database(out_num=i, out_tp='FMC')
        for k, v in db2.items():
            dbase[prefix + k] = v

    return dbase


def get_fout_database(prefix=None):
    """Return fout_database."""
    prefix = prefix or ''
    dbase = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    dbase[prefix+'DevEnbl-Sts'] = dic_
    dbase[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    dbase[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    dbase[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    dbase[prefix+'Network-Mon'] = {
        'type': 'enum', 'value': 1, 'enums': _et.DISCONN_CONN}

    dbase[prefix+'Link-Mon'] = {
        'type': 'enum', 'value': 1, 'enums': _et.UNLINK_LINK}

    dbase[prefix+'Intlk-Mon'] = {
        'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    return dbase


def get_event_database(evt_num=0, prefix=None):
    """Return event_database."""
    def_prefix = 'Evt{0:02d}'.format(evt_num)
    prefix = def_prefix if prefix is None else prefix

    dbase = dict()
    dic_ = {
        'type': 'int', 'value': 0, 'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    dbase[prefix + 'Delay-SP'] = _dcopy(dic_)
    dbase[prefix + 'Delay-RB'] = dic_
    dic_ = {'type': 'enum', 'enums': _et.EVT_MODES, 'value': 1}
    dbase[prefix + 'Mode-Sel'] = _dcopy(dic_)
    dbase[prefix + 'Mode-Sts'] = dic_
    dic_ = {'type': 'enum', 'enums': _et.FIXED_INCR, 'value': 1}
    dbase[prefix + 'DelayType-Sel'] = _dcopy(dic_)
    dbase[prefix + 'DelayType-Sts'] = dic_
    dic_ = {'type': 'string', 'value': ''}
    dbase[prefix + 'Desc-SP'] = _dcopy(dic_)
    dbase[prefix + 'Desc-RB'] = dic_
    dbase[prefix + 'ExtTrig-Cmd'] = {'type': 'int', 'value': 0}
    return dbase


def get_clock_database(clock_num=0, prefix=None):
    """Return clock_database."""
    def_prefix = 'Clk{0:d}'.format(clock_num)
    prefix = def_prefix if prefix is None else prefix
    dbase = dict()

    dic_ = {
        'type': 'int', 'value': 124948114, 'lolo': 2, 'low': 2, 'lolim': 2,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    dbase[prefix + 'MuxDiv-SP'] = _dcopy(dic_)
    dbase[prefix + 'MuxDiv-RB'] = dic_
    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL, 'value': 0}
    dbase[prefix + 'MuxEnbl-Sel'] = _dcopy(dic_)
    dbase[prefix + 'MuxEnbl-Sts'] = dic_
    return dbase


def get_evg_database(prefix=None, only_evg=False):
    """Return evg_database."""
    prefix = prefix or ''
    dbase = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    dbase[prefix+'DevEnbl-Sts'] = dic_
    dbase[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL, 'value': 0}
    dbase[prefix + 'ContinuousEvt-Sel'] = _dcopy(dic_)
    dbase[prefix + 'ContinuousEvt-Sts'] = dic_

    dic_ = {
        'type': 'int', 'count': 864, 'value': 864*[1],
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 864, 'high': 864, 'hihi': 864}
    dbase[prefix + 'BucketList-SP'] = _dcopy(dic_)
    dbase[prefix + 'BucketList-RB'] = dic_
    dbase[prefix + 'BucketListLen-Mon'] = {
        'type': 'int', 'value': 864,
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 864, 'high': 864, 'hihi': 864}

    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL, 'value': 0}
    dbase[prefix + 'InjectionEvt-Sel'] = _dcopy(dic_)
    dbase[prefix + 'InjectionEvt-Sts'] = dic_

    dic_ = {
        'type': 'int', 'value': 0, 'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 100, 'high': 100, 'hihi': 100}
    dbase[prefix + 'RepeatBucketList-SP'] = _dcopy(dic_)
    dbase[prefix + 'RepeatBucketList-RB'] = dic_

    dic_ = {
        'type': 'int', 'value': 30, 'lolo': 1, 'low': 1, 'lolim': 1,
        'hilim': 60, 'high': 60, 'hihi': 60}
    dbase[prefix + 'ACDiv-SP'] = _dcopy(dic_)
    dbase[prefix + 'ACDiv-RB'] = dic_

    dic_ = {
        'type': 'int', 'value': 4, 'lolo': 1, 'low': 1, 'lolim': 1,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    dbase[prefix + 'RFDiv-SP'] = _dcopy(dic_)
    dbase[prefix + 'RFDiv-RB'] = dic_

    dbase[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    dbase[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    dbase[prefix+'Network-Mon'] = {
        'type': 'enum', 'value': 1, 'enums': _et.DISCONN_CONN}

    dbase[prefix+'RFStatus-Mon'] = {
        'type': 'enum', 'value': 1,
        'enums': ('Loss or Out of Range', 'Normal')}

    dbase[prefix+'StateMachine-Mon'] = {
        'type': 'enum', 'value': 4,
        'enums': (
            'Initializing', 'Stopped', 'Continuous', 'Injection',
            'Preparing Continuous', 'Preparing Injection')
        }

    if only_evg:
        return dbase

    for clc in Const.ClkLL2HLMap:
        dbase.update(get_clock_database(prefix=prefix+clc))
    for ev in Const.EvtLL._fields:
        dbase.update(get_event_database(prefix=prefix+ev))
    return dbase


def get_hl_trigger_database(hl_trigger, prefix=''):
    """Return database of the specified hl_trigger."""
    dbase = dict()
    trig_db = _HLTimeSearch.get_hl_trigger_predef_db(hl_trigger)
    ll_trig_names = _HLTimeSearch.get_ll_trigger_names(hl_trigger)

    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL}
    dic_.update(trig_db['State'])
    dbase['State-Sts'] = _dcopy(dic_)
    dbase['State-Sel'] = dic_

    dic_ = {'type': 'enum'}
    dic_.update(trig_db['Src'])
    if _HLTimeSearch.has_clock(hl_trigger):
        clocks = tuple(sorted(Const.ClkHL2LLMap))
        dic_['enums'] += clocks
    dic_['enums'] += ('Invalid', )  # for completeness
    dbase['Src-Sts'] = _dcopy(dic_)
    dbase['Src-Sel'] = dic_

    dic_ = {
        'type': 'float', 'unit': 'us', 'prec': 3,
        'lolim': 0.008, 'low': 0.008, 'lolo': 0.008,
        'hilim': 17e6, 'high': 17e6, 'hihi': 17e6}
    dic_.update(trig_db['Duration'])
    dbase['Duration-RB'] = _dcopy(dic_)
    dbase['Duration-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.NORM_INV}
    dic_.update(trig_db['Polarity'])
    dbase['Polarity-Sts'] = _dcopy(dic_)
    dbase['Polarity-Sel'] = dic_

    dic_ = {
        'type': 'int', 'unit': 'pulses',
        # 'lolo': 1, 'low': 1, 'lolim': 1,
        'hilim': 100000, 'high': 100000, 'hihi': 100000}
    dic_.update(trig_db['NrPulses'])
    dbase['NrPulses-RB'] = _dcopy(dic_)
    dbase['NrPulses-SP'] = dic_

    max_dly_raw = 2123400000
    max_dly = 17e6
    dic_ = {
        'type': 'float', 'unit': 'us', 'prec': 3, 'value': 0,
        'lolim': 0.0, 'low': 0.0, 'lolo': 0.0,
        'hilim': max_dly, 'high': max_dly, 'hihi': max_dly}
    dic_.update(trig_db['Delay'])
    dbase['Delay-RB'] = _dcopy(dic_)
    dbase['Delay-SP'] = dic_

    # Have to be float for spinbox to work properly
    dic_ = {
        'type': 'float', 'unit': 'hard', 'prec': 0, 'value': 0,
        'lolim': 0.0, 'low': 0.0, 'lolo': 0.0,
        'hilim': max_dly_raw, 'high': max_dly_raw, 'hihi': max_dly_raw}
    dic_.update(trig_db.get('DelayRaw', dict()))
    dbase['DelayRaw-RB'] = _dcopy(dic_)
    dbase['DelayRaw-SP'] = dic_

    dic_ = {
        'type': 'float', 'unit': 'us', 'prec': 3, 'value': 0.0,
        'lolim': 0.0, 'low': 0.0, 'lolo': 0.0,
        'hilim': max_dly, 'high': max_dly, 'hihi': max_dly}
    dbase['TotalDelay-Mon'] = dic_

    # Have to be float for spinbox to work properly
    dic_ = {
        'type': 'float', 'unit': 'hard', 'prec': 0, 'value': 0,
        'lolim': 0.0, 'low': 0.0, 'lolo': 0.0,
        'hilim': max_dly_raw, 'high': max_dly_raw, 'hihi': max_dly_raw}
    dbase['TotalDelayRaw-Mon'] = dic_

    siz = len(ll_trig_names)
    dic_ = {
        'type': 'float', 'unit': 'us', 'prec': 3,
        'count': siz, 'value': _np.zeros(siz),
        'lolim': -max_dly, 'low': -max_dly, 'lolo': -max_dly,
        'hilim': max_dly, 'high': max_dly, 'hihi': max_dly}
    dic_.update(trig_db.get('DeltaDelay', dict()))
    dbase['DeltaDelay-RB'] = _dcopy(dic_)
    dbase['DeltaDelay-SP'] = dic_

    dic_ = {
        'type': 'float', 'unit': 'hard', 'prec': 0,
        'count': siz, 'value': _np.zeros(siz),
        'lolim': -max_dly_raw, 'low': -max_dly_raw, 'lolo': -max_dly_raw,
        'hilim': max_dly_raw, 'high': max_dly_raw, 'hihi': max_dly_raw}
    dic_.update(trig_db.get('DeltaDelayRaw', dict()))
    dbase['DeltaDelayRaw-RB'] = _dcopy(dic_)
    dbase['DeltaDelayRaw-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.LOCKLL, 'value': 0}
    dbase['LowLvlLock-Sts'] = _dcopy(dic_)
    dbase['LowLvlLock-Sel'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.DLYTYP}
    dic_.update(trig_db['RFDelayType'])
    dbase['RFDelayType-Sts'] = _dcopy(dic_)
    dbase['RFDelayType-Sel'] = dic_
    if not _HLTimeSearch.has_delay_type(hl_trigger):
        dbase.pop('RFDelayType-Sts')
        dbase.pop('RFDelayType-Sel')

    dbase['Status-Mon'] = {'type': 'int', 'value': 0b1111111111}
    dbase['InInjTable-Mon'] = {
        'type': 'enum', 'enums': _et.ININJTAB, 'value': 0}

    dbase['StatusLabels-Cte'] = {
        'type': 'char', 'count': 1000,
        'value': '\n'.join(Const.HLTrigStatusLabels)
        }
    ll_trigs = '\n'.join(ll_trig_names)
    dbase['LowLvlTriggers-Cte'] = {
        'type': 'char', 'count': 5000, 'value': ll_trigs}
    channels = '\n'.join(_HLTimeSearch.get_hl_trigger_channels(hl_trigger))
    dbase['CtrldChannels-Cte'] = {
        'type': 'char', 'count': 5000, 'value': channels}

    return {prefix + pv: dt for pv, dt in dbase.items()}
