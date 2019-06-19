"""Define properties of all timing devices and their connections."""

from copy import deepcopy as _dcopy
import numpy as _np
from mathphys import constants as _c
import siriuspy.csdevice.util as _cutil
from siriuspy.optics import constants as _oc
from siriuspy.search import HLTimeSearch as _HLTimeSearch


# --- Enumeration Types ---

class ETypes(_cutil.ETypes):
    """Local enumerate types."""

    EVT_MODES = ('Disabled', 'Continuous', 'Injection', 'External')
    TRIG_SRC_LL = (
        'Dsbl', 'Trigger', 'Clock0', 'Clock1', 'Clock2',
        'Clock3', 'Clock4', 'Clock5', 'Clock6', 'Clock7')
    LOCKLL = ('Unlocked', 'Locked')
    DLYTYP = ('Manual', 'Auto')
    RFOUT = ('OFF', '5RF/2', '5RF/4', 'RF', 'RF/2', 'RF/4')


_et = ETypes  # syntactic sugar


class Const(_cutil.Const):
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

    EvtModes = _cutil.Const.register('EvtModes', _et.EVT_MODES)
    EvtDlyTyp = _cutil.Const.register('EvtDlyTyp', _et.FIXED_INCR)
    ClockStates = _cutil.Const.register('ClockStates', _et.DSBL_ENBL)
    TrigStates = _cutil.Const.register('TrigStates', _et.DSBL_ENBL)
    TrigPol = _cutil.Const.register('TrigPol', _et.NORM_INV)
    LowLvlLock = _cutil.Const.register('LowLvlLock', _et.LOCKLL)
    TrigDlyTyp = _cutil.Const.register('TrigDlyTyp', _et.DLYTYP)
    TrigSrcLL = _cutil.Const.register('TrigSrcLL', _et.TRIG_SRC_LL)
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

    EvtHL2LLMap = _HLTimeSearch.get_hl_events()
    EvtLL2HLMap = {val: key for key, val in EvtHL2LLMap.items()}

    evt_ll_codes = list(range(64)) + [124]
    evt_ll_names = ['Evt{0:02d}'.format(i) for i in evt_ll_codes]
    EvtLL = _cutil.Const.register(
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
    ClkLL = _cutil.Const.register(
                    'ClocksLL', clk_ll_names, values=clk_ll_codes)
    del clk_ll_names, clk_ll_codes


def get_otp_database(otp_num=0, prefix=None):
    """Return otp_database."""
    def_prefix = 'OTP{0:02d}'.format(otp_num)
    prefix = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'State-Sts'] = dic_
    db[prefix+'State-Sel'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 1, 'low': 1, 'lolim': 1,
        'hilim': 63, 'high': 63, 'hihi': 63}
    db[prefix+'Evt-SP'] = dic_
    db[prefix+'Evt-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 1, 'low': 1, 'lolim': 1,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix+'Width-SP'] = dic_
    db[prefix+'Width-RB'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.NORM_INV}
    db[prefix+'Polarity-Sts'] = dic_
    db[prefix+'Polarity-Sel'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix+'NrPulses-SP'] = dic_
    db[prefix+'NrPulses-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix+'Delay-SP'] = dic_
    db[prefix+'Delay-RB'] = _dcopy(dic_)

    return db


def get_out_database(out_num=0, equip='EVR', prefix=None):
    """Return out_database."""
    def_prefix = 'OUT{0:d}'.format(out_num)
    prefix = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.TRIG_SRC_LL}
    db[prefix+'Src-Sts'] = dic_
    db[prefix+'Src-Sel'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DLYTYP}
    db[prefix+'RFDelayType-Sts'] = dic_
    db[prefix+'RFDelayType-Sel'] = _dcopy(dic_)

    max_trig = 23 if equip == 'EVR' else 15
    num_trig = out_num + 12 if equip == 'EVR' else out_num
    dic_ = {
        'type': 'int', 'value': num_trig, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': max_trig, 'high': max_trig, 'hihi': max_trig}
    db[prefix+'SrcTrig-SP'] = dic_
    db[prefix+'SrcTrig-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 30, 'high': 30, 'hihi': 30}
    db[prefix+'RFDelay-SP'] = dic_
    db[prefix+'RFDelay-RB'] = _dcopy(dic_)

    dic_ = {
        'type': 'int', 'value': 1, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 200, 'high': 200, 'hihi': 200}
    db[prefix+'FineDelay-SP'] = dic_
    db[prefix+'FineDelay-RB'] = _dcopy(dic_)

    return db


def get_afc_out_database(out_num=0, out_tp='FMC', prefix=None):
    """Return afc_database."""
    def_prefix = (out_tp + '{0:d}'.format(out_num))
    if out_tp == 'FMC':
        fmc = (out_num // 5) + 1
        ch = (out_num % 5) + 1
        def_prefix = (out_tp + '{0:d}CH{1:d}'.format(fmc, ch))

    prefix = def_prefix if prefix is None else prefix
    db = get_otp_database(prefix=prefix)
    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.TRIG_SRC_LL}
    db[prefix+'Src-Sts'] = dic_
    db[prefix+'Src-Sel'] = _dcopy(dic_)

    return db


def get_evr_database(prefix=None):
    """Return evr_database."""
    prefix = prefix or ''
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    db[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    db[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    db[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    db[prefix+'LinkStatus-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.UNLINK_LINK}

    db[prefix+'IntlkStatus-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}

    db[prefix+'IntlkEnbl-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}

    for i in range(24):
        db2 = get_otp_database(otp_num=i)
        for k, v in db2.items():
            db[prefix + k] = v

    for i in range(8):
        db2 = get_out_database(out_num=i, equip='EVR')
        for k, v in db2.items():
            db[prefix + k] = v
    return db


def get_eve_database(eve_num=1, prefix=None):
    """Return eve_database."""
    prefix = prefix or ''
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.RFOUT}
    db[prefix+'RFOut-Sts'] = dic_
    db[prefix+'RFOut-Sel'] = _dcopy(dic_)

    db[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    db[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    db[prefix+'LinkStatus-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.UNLINK_LINK}

    db[prefix+'IntlkStatus-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}

    db[prefix+'IntlkEnbl-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}

    for i in range(24):
        db2 = get_otp_database(otp_num=i)
        for k, v in db2.items():
            db[prefix + k] = v

    for i in range(8):
        db2 = get_out_database(out_num=i, equip='EVE')
        for k, v in db2.items():
            db[prefix + k] = v

    return db


def get_afc_database(prefix=None):
    """Return adc_database."""
    prefix = prefix or ''
    db = dict()
    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    db[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    db[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    db[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    db[prefix+'LinkStatus-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.UNLINK_LINK}

    db[prefix+'IntlkStatus-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}

    for i in range(8):
        db2 = get_afc_out_database(out_num=i, out_tp='AMC')
        for k, v in db2.items():
            db[prefix + k] = v

    for i in range(10):
        db2 = get_afc_out_database(out_num=i, out_tp='FMC')
        for k, v in db2.items():
            db[prefix + k] = v

    return db


def get_fout_database(prefix=None):
    """Return fout_database."""
    prefix = prefix or ''
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    db[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    db[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    db[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    db[prefix+'Link-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.UNLINK_LINK}

    db[prefix+'Intlk-Mon'] = {
            'type': 'enum', 'value': 0,
            'enums': _et.DSBL_ENBL}
    return db


def get_event_database(evt_num=0, prefix=None):
    """Return event_database."""
    def_prefix = 'Evt{0:02d}'.format(evt_num)
    prefix = def_prefix if prefix is None else prefix

    db = dict()
    dic_ = {'type': 'int', 'value': 0,
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix + 'Delay-SP'] = _dcopy(dic_)
    db[prefix + 'Delay-RB'] = dic_
    dic_ = {'type': 'enum', 'enums': _et.EVT_MODES, 'value': 1}
    db[prefix + 'Mode-Sel'] = _dcopy(dic_)
    db[prefix + 'Mode-Sts'] = dic_
    dic_ = {'type': 'enum', 'enums': _et.FIXED_INCR, 'value': 1}
    db[prefix + 'DelayType-Sel'] = _dcopy(dic_)
    db[prefix + 'DelayType-Sts'] = dic_
    dic_ = {'type': 'string', 'value': ''}
    db[prefix + 'Desc-SP'] = _dcopy(dic_)
    db[prefix + 'Desc-RB'] = dic_
    db[prefix + 'ExtTrig-Cmd'] = {'type': 'int', 'value': 0}
    return db


def get_clock_database(clock_num=0, prefix=None):
    """Return clock_database."""
    def_prefix = 'Clk{0:d}'.format(clock_num)
    prefix = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'int', 'value': 124948114,
            'lolo': 2, 'low': 2, 'lolim': 2,
            'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix + 'MuxDiv-SP'] = _dcopy(dic_)
    db[prefix + 'MuxDiv-RB'] = dic_
    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL, 'value': 0}
    db[prefix + 'MuxEnbl-Sel'] = _dcopy(dic_)
    db[prefix + 'MuxEnbl-Sts'] = dic_
    return db


def get_evg_database(prefix=None, only_evg=False):
    """Return evg_database."""
    prefix = prefix or ''
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL, 'value': 0}
    db[prefix + 'ContinuousEvt-Sel'] = _dcopy(dic_)
    db[prefix + 'ContinuousEvt-Sts'] = dic_

    dic_ = {'type': 'int', 'count': 864, 'value': 864*[1],
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 864, 'high': 864, 'hihi': 864
            }
    db[prefix + 'BucketList-SP'] = _dcopy(dic_)
    db[prefix + 'BucketList-RB'] = dic_
    db[prefix + 'BucketListLen-Mon'] = {
        'type': 'int', 'value': 864,
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 864, 'high': 864, 'hihi': 864}

    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL, 'value': 0}
    db[prefix + 'InjectionEvt-Sel'] = _dcopy(dic_)
    db[prefix + 'InjectionEvt-Sts'] = dic_

    dic_ = {'type': 'int', 'value': 0,
            'lolo': 0, 'low': 0, 'lolim': 0,
            'hilim': 100, 'high': 100, 'hihi': 100}
    db[prefix + 'RepeatBucketList-SP'] = _dcopy(dic_)
    db[prefix + 'RepeatBucketList-RB'] = dic_

    dic_ = {'type': 'int', 'value': 30,
            'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 60, 'high': 60, 'hihi': 60}
    db[prefix + 'ACDiv-SP'] = _dcopy(dic_)
    db[prefix + 'ACDiv-RB'] = dic_

    dic_ = {'type': 'int', 'value': 4,
            'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix + 'RFDiv-SP'] = _dcopy(dic_)
    db[prefix + 'RFDiv-RB'] = dic_

    db[prefix+'Los-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 255, 'high': 255, 'hihi': 255}

    db[prefix+'Alive-Mon'] = {
        'type': 'int', 'value': 0, 'unit': '',
        'lolo': 0, 'low': 0, 'lolim': 0,
        'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}

    db[prefix+'Network-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': _et.DISCONN_CONN}

    db[prefix+'RFStatus-Mon'] = {
            'type': 'enum', 'value': 1,
            'enums': ('Loss or Out of Range', 'Normal')}

    db[prefix+'StateMachine-Mon'] = {
            'type': 'enum', 'value': 4,
            'enums': (
                'Initializing', 'Stopped', 'Continuous', 'Injection',
                'Preparing Continuous', 'Preparing Injection'
                )}

    if only_evg:
        return db

    for clc in Const.ClkLL2HLMap:
        db.update(get_clock_database(prefix=prefix+clc))
    for ev in Const.EvtLL._fields:
        db.update(get_event_database(prefix=prefix+ev))
    return db


def get_hl_trigger_database(hl_trigger, prefix=''):
    """Return database of the specified hl_trigger."""
    db = dict()
    trig_db = _HLTimeSearch.get_hl_trigger_predef_db(hl_trigger)
    ll_trig_names = _HLTimeSearch.get_ll_trigger_names(hl_trigger)

    dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL}
    dic_.update(trig_db['State'])
    db['State-Sts'] = _dcopy(dic_)
    db['State-Sel'] = dic_

    dic_ = {'type': 'enum'}
    dic_.update(trig_db['Src'])
    if _HLTimeSearch.has_clock(hl_trigger):
        clocks = tuple(sorted(Const.ClkHL2LLMap))
        dic_['enums'] += clocks
    dic_['enums'] += ('Invalid', )  # for completeness
    db['Src-Sts'] = _dcopy(dic_)
    db['Src-Sel'] = dic_

    dic_ = {'type': 'float', 'unit': 'us', 'prec': 3,
            'lolo': 0.008, 'low': 0.008, 'lolim': 0.008,
            'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
    dic_.update(trig_db['Duration'])
    db['Duration-RB'] = _dcopy(dic_)
    db['Duration-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.NORM_INV}
    dic_.update(trig_db['Polarity'])
    db['Polarity-Sts'] = _dcopy(dic_)
    db['Polarity-Sel'] = dic_

    dic_ = {'type': 'int', 'unit': 'numer of pulses',
            # 'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 2001, 'high': 10000, 'hihi': 100000}
    dic_.update(trig_db['NrPulses'])
    db['NrPulses-RB'] = _dcopy(dic_)
    db['NrPulses-SP'] = dic_

    dic_ = {'type': 'float', 'unit': 'us', 'prec': 6,
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
    dic_.update(trig_db['Delay'])
    db['Delay-RB'] = _dcopy(dic_)
    db['Delay-SP'] = dic_

    siz = len(ll_trig_names)
    dic_ = {'type': 'float', 'unit': 'us', 'prec': 6,
            'count': siz, 'value': _np.zeros(siz),
            'lolo': -500000, 'low': -1000000, 'lolim': -10000000,
            'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
    db['DeltaDelay-RB'] = _dcopy(dic_)
    db['DeltaDelay-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.LOCKLL, 'value': 0}
    db['LowLvlLock-Sts'] = _dcopy(dic_)
    db['LowLvlLock-Sel'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.DLYTYP}
    dic_.update(trig_db['RFDelayType'])
    db['RFDelayType-Sts'] = _dcopy(dic_)
    db['RFDelayType-Sel'] = dic_
    if not _HLTimeSearch.has_delay_type(hl_trigger):
        db.pop('RFDelayType-Sts')
        db.pop('RFDelayType-Sel')

    dic_ = {'type': 'int', 'value': 0b1111111111}
    db['Status-Mon'] = _dcopy(dic_)

    db['StatusLabels-Cte'] = {
        'type': 'char', 'count': 1000,
        'value': '\n'.join(Const.HLTrigStatusLabels)
        }
    ll_trigs = '\n'.join(ll_trig_names)
    db['LowLvlTriggers-Cte'] = {
        'type': 'char', 'count': 5000, 'value': ll_trigs}
    channels = '\n'.join(_HLTimeSearch.get_hl_trigger_channels(hl_trigger))
    db['CtrldChannels-Cte'] = {
        'type': 'char', 'count': 5000, 'value': channels}

    return {prefix + pv: dt for pv, dt in db.items()}
