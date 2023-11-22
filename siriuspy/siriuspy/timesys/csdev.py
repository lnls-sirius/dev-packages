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

    EVT_MODES = ('Disable', 'Continuous', 'Injection', 'OneShot', 'External')
    TRIG_SRC_LL = (
        'Dsbl', 'Trigger', 'Clock0', 'Clock1', 'Clock2',
        'Clock3', 'Clock4', 'Clock5', 'Clock6', 'Clock7')
    LOCKLL = ('Unlocked', 'Locked')
    DLYTYP = ('Manual', 'Auto')
    DIRECTION = ('Receive', 'Transmit')
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
    TrigDir = _csdev.Const.register('TrigDir', _et.DIRECTION)
    InInjTab = _csdev.Const.register('InInjTab', _et.ININJTAB)
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
    __EvtLL = None

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
        if cls.__EvtHL2LLMap is not None:
            return cls.__EvtHL2LLMap

        emap = _HLTimeSearch.get_hl_events()
        cls.__EvtHL2LLMap = emap
        cls.__EvtLL2HLMap = {val: key for key, val in emap.items()}

        names = sorted({f'Evt{i:02d}' for i in range(64)} | set(emap.values()))
        codes = [int(n[3:]) for n in names]
        codes, names = list(zip(*sorted(zip(codes, names))))
        cls.__EvtLL = _csdev.Const.register('EventsLL', names, values=codes)
        return cls.__EvtHL2LLMap

    @_classproperty
    def EvtLL2HLMap(cls):
        """."""
        cls.EvtHL2LLMap
        return cls.__EvtLL2HLMap

    @_classproperty
    def EvtLL(cls):
        """."""
        cls.EvtHL2LLMap
        return cls.__EvtLL


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


def get_hl_trigger_database(hl_trigger, prefix=''):
    """Return database of the specified hl_trigger."""
    dbase = dict()
    is_digital_input = _HLTimeSearch.is_digital_input(hl_trigger)
    trig_db = _HLTimeSearch.get_hl_trigger_predef_db(
        hl_trigger, has_commom_evts=not is_digital_input)
    ll_trig_names = _HLTimeSearch.get_ll_trigger_names(hl_trigger)

    dic_ = {'type': 'enum', 'enums': _et.LOCKLL, 'value': 0}
    dbase['LowLvlLock-Sts'] = _dcopy(dic_)
    dbase['LowLvlLock-Sel'] = dic_

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

    dic_ = {'type': 'enum', 'enums': _et.NORM_INV}
    dic_.update(trig_db['Polarity'])
    dbase['Polarity-Sts'] = _dcopy(dic_)
    dbase['Polarity-Sel'] = dic_

    if _HLTimeSearch.has_log(hl_trigger):
        dic_ = {'type': 'enum', 'enums': _et.DSBL_ENBL}
        dic_.update(trig_db.get('Log', dict()))
        dbase['Log-Sts'] = _dcopy(dic_)
        dbase['Log-Sel'] = dic_

    # NOTE: we need to add plus 1 to the PVs count due to some unexpected
    # behavior of pcaspy
    labs = '\n'.join(Const.HLTrigStatusLabels)
    dbase['StatusLabels-Cte'] = {
        'type': 'char', 'count': len(labs)+1, 'value': labs}

    ll_trigs = '\n'.join(ll_trig_names)
    dbase['LowLvlTriggers-Cte'] = {
        'type': 'char', 'count': len(ll_trigs)+1, 'value': ll_trigs}
    channels = '\n'.join(_HLTimeSearch.get_hl_trigger_channels(hl_trigger))
    dbase['CtrldChannels-Cte'] = {
        'type': 'char', 'count': len(channels)+1, 'value': channels}

    dbase['Status-Mon'] = {'type': 'int', 'value': 0b1111111111}
    dbase['InInjTable-Mon'] = {
        'type': 'enum', 'enums': _et.ININJTAB, 'value': 0}

    if is_digital_input:
        return {prefix + pv: dt for pv, dt in dbase.items()}

    max_dur = 17e6
    max_wid_raw = 2**31 - 1
    dic_ = {
        'type': 'float', 'unit': 'us', 'prec': 3,
        'lolim': 0.008, 'hilim': max_dur}
    dic_.update(trig_db['Duration'])
    dbase['Duration-RB'] = _dcopy(dic_)
    dbase['Duration-SP'] = dic_

    # Have to be float for spinbox to work properly
    dic_ = {
        'type': 'float', 'unit': 'hard', 'prec': 0, 'value': 0,
        'lolim': 1.0, 'hilim': max_wid_raw}
    dic_.update(trig_db.get('WidthRaw', dict()))
    dbase['WidthRaw-RB'] = _dcopy(dic_)
    dbase['WidthRaw-SP'] = dic_

    dic_ = {
        'type': 'int', 'unit': 'pulses', 'lolim': 1, 'hilim': 100000}
    dic_.update(trig_db['NrPulses'])
    dbase['NrPulses-RB'] = _dcopy(dic_)
    dbase['NrPulses-SP'] = dic_

    max_dly_raw = 2**31 - 1
    max_dly = 17e6
    dic_ = {
        'type': 'float', 'unit': 'us', 'prec': 3, 'value': 0,
        'lolim': 0.0, 'hilim': max_dly}
    dic_.update(trig_db['Delay'])
    dbase['Delay-RB'] = _dcopy(dic_)
    dbase['Delay-SP'] = dic_

    # Have to be float for spinbox to work properly
    dic_ = {
        'type': 'float', 'unit': 'hard', 'prec': 0, 'value': 0,
        'lolim': 0.0, 'hilim': max_dly_raw}
    dic_.update(trig_db.get('DelayRaw', dict()))
    dbase['DelayRaw-RB'] = _dcopy(dic_)
    dbase['DelayRaw-SP'] = dic_

    dic_ = {
        'type': 'float', 'unit': 'us', 'prec': 3, 'value': 0.0,
        'lolim': 0.0, 'hilim': max_dly}
    dbase['TotalDelay-Mon'] = dic_

    # Have to be float for spinbox to work properly
    dic_ = {
        'type': 'float', 'unit': 'hard', 'prec': 0, 'value': 0,
        'lolim': 0.0, 'hilim': max_dly_raw}
    dbase['TotalDelayRaw-Mon'] = dic_

    siz = len(ll_trig_names)
    dic_ = {
        'type': 'float', 'unit': 'us', 'prec': 3, 'count': siz,
        'value': _np.zeros(siz), 'lolim': -max_dly, 'hilim': max_dly}
    dic_.update(trig_db.get('DeltaDelay', dict()))
    dbase['DeltaDelay-RB'] = _dcopy(dic_)
    dbase['DeltaDelay-SP'] = dic_

    dic_ = {
        'type': 'float', 'unit': 'hard', 'prec': 0,
        'count': siz, 'value': _np.zeros(siz),
        'lolim': -max_dly_raw, 'hilim': max_dly_raw}
    dic_.update(trig_db.get('DeltaDelayRaw', dict()))
    dbase['DeltaDelayRaw-RB'] = _dcopy(dic_)
    dbase['DeltaDelayRaw-SP'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.DLYTYP}
    dic_.update(trig_db['RFDelayType'])
    if _HLTimeSearch.has_delay_type(hl_trigger):
        dbase['RFDelayType-Sts'] = _dcopy(dic_)
        dbase['RFDelayType-Sel'] = dic_

    dic_ = {'type': 'enum', 'enums': _et.DIRECTION}
    dic_.update(trig_db.get('Direction', dict()))
    if _HLTimeSearch.has_direction(hl_trigger):
        dbase['Direction-Sel'] = _dcopy(dic_)
        dbase['Direction-Sts'] = dic_

    return {prefix + pv: dt for pv, dt in dbase.items()}
