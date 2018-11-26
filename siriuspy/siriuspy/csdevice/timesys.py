"""Define properties of all timing devices and their connections."""

from copy import deepcopy as _dcopy
from siriuspy.mathphys import constants as _c
from siriuspy.optics import constants as _oc
from siriuspy.util import get_namedtuple as _get_namedtuple
from siriuspy.csdevice.util import ETypes as _et
from siriuspy.search import HLTimeSearch as _HLTimeSearch


events_hl2ll_map = {
    'Linac': 'Evt01', 'InjBO': 'Evt02',
    'InjSI': 'Evt03', 'RmpBO': 'Evt04',
    'MigSI': 'Evt05', 'DigLI': 'Evt06',
    'DigTB': 'Evt07', 'DigBO': 'Evt08',
    'DigTS': 'Evt09', 'DigSI': 'Evt10',
    'OrbSI': 'Evt11', 'CplSI': 'Evt12',
    'TunSI': 'Evt13', 'Study': 'Evt14',
    'OrbBO': 'Evt15'}
events_ll2hl_map = {val: key for key, val in events_hl2ll_map.items()}

events_ll_tmp = 'Evt{0:02d}'
events_hl_pref = 'AS-Glob:TI-EVG:'

events_ll_codes = list(range(1, 64))
events_ll_names = []
for i in events_ll_codes:
    events_ll_names.append(events_ll_tmp.format(i))
events_ll = _get_namedtuple(
                'EventsLL', events_ll_names, values=events_ll_codes)
del(i, events_ll_codes, events_ll_names)  # cleanup class namespace

events_modes = _get_namedtuple(
                'EvtModes',
                ('Disabled', 'Continuous', 'Injection', 'External'))
events_delay_types = _get_namedtuple('EvtDlyTyp', _et.FIXED_INCR)
clocks_states = _get_namedtuple('ClockState', _et.DSBL_ENBL)

clocks_ll_tmp = 'Clock{0:d}'
clocks_hl_tmp = 'Clock{0:d}'
clocks_hl_pref = 'AS-Glob:TI-EVG:'

clocks_hl2ll_map = dict()
for i in range(8):
    clocks_hl2ll_map[clocks_hl_tmp.format(i)] = clocks_ll_tmp.format(i)
del(i)  # cleanup class namespace

clocks_ll2hl_map = {val: key for key, val in clocks_hl2ll_map.items()}

triggers_states = _get_namedtuple('TrigStates', _et.DSBL_ENBL)
triggers_intlk = _get_namedtuple('TrigIntlk', _et.DSBL_ENBL)
triggers_polarities = _get_namedtuple('TrigPol', _et.NORM_INV)
triggers_delay_types = _get_namedtuple('TrigDlyTyp', _et.FIXED_INCR)
triggers_src_ll = _get_namedtuple(
                        'TrigSrcLL',
                        ('Dsbl',  'Trigger', 'Clock0', 'Clock1', 'Clock2',
                         'Clock3', 'Clock4', 'Clock5', 'Clock6', 'Clock7'))


class Const:
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


def get_otp_database(otp_num=0, prefix=None):
    """Return otp_database."""
    def_prefix = 'OTP{0:02d}'.format(otp_num)
    prefix = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': triggers_states._fields}
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

    dic_ = {'type': 'enum', 'value': 0, 'enums': triggers_polarities._fields}
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

    dic_ = {'type': 'enum', 'value': 0, 'enums': triggers_intlk._fields}
    db[prefix+'ByPassIntlk-Sts'] = dic_
    db[prefix+'ByPassIntlk-Sel'] = _dcopy(dic_)

    return db


def get_out_database(out_num=0, equip='EVR', prefix=None):
    """Return out_database."""
    def_prefix = 'OUT{0:d}'.format(out_num)
    prefix = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': triggers_src_ll._fields}
    db[prefix+'Src-Sts'] = dic_
    db[prefix+'Src-Sel'] = _dcopy(dic_)

    dic_ = {'type': 'enum', 'value': 0, 'enums': triggers_delay_types._fields}
    db[prefix+'DelayType-Sts'] = dic_
    db[prefix+'DelayType-Sel'] = _dcopy(dic_)

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
    db.pop(prefix + 'ByPassIntlk-Sel')
    db.pop(prefix + 'ByPassIntlk-Sts')
    dic_ = {'type': 'enum', 'value': 0, 'enums': triggers_src_ll._fields}
    db[prefix+'Src-Sts'] = dic_
    db[prefix+'Src-Sel'] = _dcopy(dic_)

    return db


def get_evr_database(evr_num=1, prefix=None):
    """Return evr_database."""
    def_prefix = 'AS-Glob:TI-EVR-{0:d}:'.format(evr_num)
    prefix = def_prefix if prefix is None else prefix
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
    def_prefix = 'AS-Glob:TI-EVE-{0:d}:'.format(eve_num)
    prefix = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'enum', 'value': 0, 'enums': _et.DSBL_ENBL}
    db[prefix+'DevEnbl-Sts'] = dic_
    db[prefix+'DevEnbl-Sel'] = _dcopy(dic_)

    RFOUT = ('OFF', '5RF/2', '5RF/4', 'RF', 'RF/2', 'RF/4')
    dic_ = {'type': 'enum', 'value': 0, 'enums': RFOUT}
    db[prefix+'RFOut-Sts'] = dic_
    db[prefix+'RFOut-Sel'] = _dcopy(dic_)

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

    for i in range(16):
        db2 = get_otp_database(otp_num=i)
        for k, v in db2.items():
            db[prefix + k] = v

    for i in range(8):
        db2 = get_out_database(out_num=i, equip='EVE')
        for k, v in db2.items():
            db[prefix + k] = v

    return db


def get_afc_database(afc_sec=1, has_idx=False, idx=1, prefix=None):
    """Return adc_database."""
    def_prefix = 'AS-{0:02d}:TI-AMCFPGAEVR:'.format(afc_sec)
    if has_idx:
        def_prefix = 'AS-{0:02d}:TI-AMCFPGAEVR-{1:d}:'.format(afc_sec, idx)

    prefix = def_prefix if prefix is None else prefix
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

    for i in range(8):
        db2 = get_afc_out_database(out_num=i, out_tp='CRT')
        for k, v in db2.items():
            db[prefix + k] = v

    for i in range(10):
        db2 = get_afc_out_database(out_num=i, out_tp='FMC')
        for k, v in db2.items():
            db[prefix + k] = v

    return db


def get_fout_database(fout_num=1, prefix=None):
    """Return fout_database."""
    def_prefix = 'AS-Glob:TI-Fout-{0:d}:'.format(fout_num)
    prefix = def_prefix if prefix is None else prefix
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
    dic_ = {'type': 'enum', 'enums': events_modes._fields, 'value': 1}
    db[prefix + 'Mode-Sel'] = _dcopy(dic_)
    db[prefix + 'Mode-Sts'] = dic_
    dic_ = {'type': 'enum', 'enums': events_delay_types._fields, 'value': 1}
    db[prefix + 'DelayType-Sel'] = _dcopy(dic_)
    db[prefix + 'DelayType-Sts'] = dic_
    dic_ = {'type': 'string', 'value': ''}
    db[prefix + 'Desc-SP'] = _dcopy(dic_)
    db[prefix + 'Desc-RB'] = dic_
    db[prefix + 'ExtTrig-Cmd'] = {'type': 'int', 'value': 0}
    return db


def get_clock_database(clock_num=0, prefix=None):
    """Return clock_database."""
    def_prefix = 'Clock{0:d}'.format(clock_num)
    prefix = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'int', 'value': 124948114,
            'lolo': 2, 'low': 2, 'lolim': 2,
            'hilim': 2**31-1, 'high': 2**31-1, 'hihi': 2**31-1}
    db[prefix + 'MuxDiv-SP'] = _dcopy(dic_)
    db[prefix + 'MuxDiv-RB'] = dic_
    dic_ = {'type': 'enum', 'enums': clocks_states._fields, 'value': 0}
    db[prefix + 'MuxEnbl-Sel'] = _dcopy(dic_)
    db[prefix + 'MuxEnbl-Sts'] = dic_
    return db


def get_evg_database(prefix=None, only_evg=False):
    """Return evg_database."""
    def_prefix = 'AS-Glob:TI-EVG:'
    prefix = def_prefix if prefix is None else prefix
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

    for clc in clocks_ll2hl_map.keys():
        db.update(get_clock_database(prefix=prefix+clc))
    for ev in events_ll._fields:
        db.update(get_event_database(prefix=prefix+ev))
    return db


def get_hl_clock_database(prefix='Clock0'):
    """Return database of a high level Clock."""
    db = dict()

    dic_ = {
        'type': 'float', 'value': 1.0,
        'unit': 'kHz', 'prec': 6,
        'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
        'hilim': 125000000, 'high': 125000000, 'hihi': 125000000}
    db[prefix + 'Freq-RB'] = _dcopy(dic_)
    db[prefix + 'Freq-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': clocks_states._fields, 'value': 0}
    db[prefix + 'State-Sel'] = _dcopy(dic_)
    db[prefix + 'State-Sts'] = dic_
    return db


def get_hl_event_database(prefix='Linac'):
    """Return database of a high level event."""
    db = dict()

    dic_ = {'type': 'float', 'unit': 'us', 'prec': 4, 'value': 0,
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
    db[prefix + 'Delay-RB'] = _dcopy(dic_)
    db[prefix + 'Delay-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': events_modes._fields,
            'value': 1,
            'states': ()}
    db[prefix + 'Mode-Sts'] = _dcopy(dic_)
    db[prefix + 'Mode-Sel'] = dic_

    dic_ = {'type': 'enum', 'enums': events_delay_types._fields, 'value': 1}
    db[prefix + 'DelayType-Sts'] = _dcopy(dic_)
    db[prefix + 'DelayType-Sel'] = dic_

    db[prefix + 'ExtTrig-Cmd'] = {
        'type': 'int', 'value': 0,
        'unit': 'When in External Mode generates Event.'}
    return db


def get_hl_evg_database(prefix=None, only_evg=False):
    """Return database of the high level PVs associated with the EVG."""
    def_prefix = 'AS-Glob:TI-EVG:'
    pre = def_prefix if prefix is None else prefix
    db = dict()

    dic_ = {'type': 'float', 'value': 2.0,
            'unit': 'Hz', 'prec': 6,
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 60, 'high': 60, 'hihi': 60}
    db[pre + 'RepRate-RB'] = _dcopy(dic_)
    db[pre + 'RepRate-SP'] = dic_

    if only_evg:
        return db

    for ev in events_hl2ll_map.keys():
        db.update(get_hl_event_database(prefix=prefix+ev))
    for clc in clocks_hl2ll_map.keys():
        db.update(get_hl_clock_database(prefix=prefix+clc))
    return db


def get_hl_trigger_database(hl_trigger, prefix=''):
    """Return database of the specified hl_trigger."""
    db = dict()
    trig_db = _HLTimeSearch.get_hl_trigger_database(hl_trigger)

    dic_ = {'type': 'enum', 'enums': triggers_states._fields}
    dic_.update(trig_db['State'])
    db['State-Sts'] = _dcopy(dic_)
    db['State-Sel'] = dic_

    dic_ = {'type': 'enum'}
    dic_.update(trig_db['Src'])
    dic_['enums'] = _HLTimeSearch.get_hl_trigger_sources(hl_trigger)
    dic_['value'] += 1 if _HLTimeSearch.has_clock(hl_trigger) else 0
    db['Src-Sts'] = _dcopy(dic_)
    db['Src-Sts']['enums'] += ('Invalid', )  # for completeness
    db['Src-Sel'] = dic_

    dic_ = {'type': 'float', 'unit': 'ms', 'prec': 6,
            'lolo': 0.000008, 'low': 0.000008, 'lolim': 0.000008,
            'hilim': 500, 'high': 1000, 'hihi': 10000}
    dic_.update(trig_db['Duration'])
    db['Duration-RB'] = _dcopy(dic_)
    db['Duration-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': triggers_polarities._fields}
    dic_.update(trig_db['Polarity'])
    db['Polarity-Sts'] = _dcopy(dic_)
    db['Polarity-Sel'] = dic_

    dic_ = {'type': 'int', 'unit': 'numer of pulses',
            # 'lolo': 1, 'low': 1, 'lolim': 1,
            'hilim': 2001, 'high': 10000, 'hihi': 100000}
    dic_.update(trig_db['NrPulses'])
    db['NrPulses-RB'] = _dcopy(dic_)
    db['NrPulses-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': triggers_intlk._fields}
    dic_.update(trig_db['ByPassIntlk'])
    db['ByPassIntlk-Sts'] = _dcopy(dic_)
    db['ByPassIntlk-Sel'] = dic_

    dic_ = {'type': 'float', 'unit': 'us', 'prec': 6,
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
    dic_.update(trig_db['Delay'])
    db['Delay-RB'] = _dcopy(dic_)
    db['Delay-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': triggers_delay_types._fields}
    dic_.update(trig_db['DelayType'])
    db['DelayType-Sts'] = _dcopy(dic_)
    db['DelayType-Sel'] = dic_

    dic_ = {'type': 'int', 'value': 1024}
    db['Status-Mon'] = _dcopy(dic_)

    db['Status-Cte'] = {
        'type': 'string', 'count': 10,
        'value': (
            'All PVs connected',
            'Device Enabled',
            'Fout Enabled',
            'EVG Enabled',
            'Network Ok',
            'UPLink Ok',
            'DownLink Ok',
            'Fout DownLink Ok',
            'EVG DownLink Ok',
            'External Interlock',
            )
        }
    interf = tuple(_HLTimeSearch.get_hl_trigger_interface(hl_trigger))
    return {prefix + pv: dt for pv, dt in db.items() if pv.startswith(interf)}
