"""."""
import time as _time

import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from .device import Device as _Device, ProptyDevice as _ProptyDevice, \
    Devices as _Devices
from ..timesys.csdev import ETypes as _ETypes, Const as _TIConst, \
    get_hl_trigger_database as _get_hl_trigger_database
from ..search import HLTimeSearch as _HLTimeSearch
from ..util import get_bit as _get_bit


class EVG(_Device):
    """Device EVG."""

    DEVNAME = 'AS-RaMO:TI-EVG'
    StateMachine = _get_namedtuple('StateMachine', (
        'Initializing', 'Stopped', 'Continuous', 'Injection',
        'Preparing_Continuous', 'Preparing_Injection',
        'Restarting_Continuous'))

    _properties = (
        'InjectionEvt-Sel', 'InjectionEvt-Sts', 'UpdateEvt-Cmd',
        'ContinuousEvt-Sel', 'ContinuousEvt-Sts', 'STATEMACHINE',
        'RepeatBucketList-SP', 'RepeatBucketList-RB',
        'BucketList-SP', 'BucketList-RB', 'BucketList-Mon',
        'BucketListLen-Mon', 'TotalInjCount-Mon', 'InjCount-Mon',
        'BucketListSyncStatus-Mon')

    def __init__(self):
        """."""
        super().__init__(EVG.DEVNAME, properties=EVG._properties)

    @property
    def nrpulses(self):
        """Number of pulses to repeat Bucket List."""
        return self['RepeatBucketList-RB']

    @nrpulses.setter
    def nrpulses(self, value):
        """Set number of pulses to repeat Bucket List."""
        self['RepeatBucketList-SP'] = bool(value)

    @property
    def bucketlist_len(self):
        """Bucket List Length."""
        value = self['BucketListLen-Mon']
        return int(value) if value is not None else None

    @property
    def bucketlist_mon(self):
        """Implemented Bucket List."""
        return self['BucketList-Mon'][:self.bucketlist_len]

    @property
    def bucketlist(self):
        """Last setpoint accepted for Bucket List."""
        return self['BucketList-RB'][:self.bucketlist_len]

    @bucketlist.setter
    def bucketlist(self, value):
        """Set Bucket List."""
        self['BucketList-SP'] = _np.array(value, dtype=int)

    @property
    def bucketlist_sync(self):
        """Bucket list syncronized status."""
        return self['BucketListSyncStatus-Mon']

    @property
    def continuous_state(self):
        """."""
        return bool(self['ContinuousEvt-Sts'])

    @continuous_state.setter
    def continuous_state(self, value):
        """."""
        new_val = bool(value)
        if self.continuous_state != new_val:
            self['ContinuousEvt-Sel'] = int(new_val)

    @property
    def state_machine(self):
        """."""
        return self['STATEMACHINE']

    @property
    def state_machine_str(self):
        """."""
        return self.StateMachine._fields[self.state_machine]

    @property
    def injection_state(self):
        """."""
        return bool(self['InjectionEvt-Sts'])

    @injection_state.setter
    def injection_state(self, value):
        """."""
        new_val = bool(value)
        if self.injection_state != new_val:
            self['InjectionEvt-Sel'] = int(new_val)

    @property
    def injection_count_total(self):
        """."""
        return self['TotalInjCount-Mon']

    @property
    def injection_count(self):
        """."""
        return self['InjCount-Mon']

    def fill_bucketlist(self, stop, start=1, step=30, timeout=10):
        """Fill bucket list."""
        if (step > 0) and (start > stop):
            stop += 864
        if (step < 0) and (stop > start):
            stop -= 864
        value = _np.arange(start, stop, step)
        value = (value-1) % 864 + 1
        self.bucketlist = value
        rb_value = _np.zeros(864)
        rb_value[:len(value)] = value
        return self._wait('BucketList-RB', rb_value, timeout=timeout)

    def wait_injection_finish(self, timeout=10):
        """."""
        return self._wait(propty='InjectionEvt-Sts', value=0, timeout=timeout)

    def cmd_update_events(self, timeout=10):
        """."""
        val = self.continuous_state
        self['UpdateEvt-Cmd'] = 1
        _time.sleep(0.1)
        return self._wait(
            propty='ContinuousEvt-Sts', value=val, timeout=timeout)

    def cmd_turn_on_injection(self, timeout=10):
        """."""
        self.injection_state = 1
        return self._wait(propty='InjectionEvt-Sel', value=1, timeout=timeout)

    def cmd_turn_off_injection(self, timeout=10):
        """."""
        self.injection_state = 0
        return self._wait(propty='InjectionEvt-Sel', value=0, timeout=timeout)

    def cmd_turn_on_continuous(self, timeout=10):
        """."""
        self.continuous_state = 1
        return self._wait(propty='ContinuousEvt-Sel', value=1, timeout=timeout)

    def cmd_turn_off_continuous(self, timeout=10):
        """."""
        self.continuous_state = 0
        return self._wait(propty='ContinuousEvt-Sel', value=0, timeout=timeout)

    def set_nrpulses(self, value, timeout=10):
        """Set and wait number of pulses."""
        self['RepeatBucketList-SP'] = value
        return self._wait('RepeatBucketList-RB', value, timeout=timeout)


class Event(_ProptyDevice):
    """Device Timing Event."""

    _properties = (
        'Delay-SP', 'Delay-RB', 'DelayRaw-SP', 'DelayRaw-RB',
        'DelayType-Sel', 'DelayType-Sts', 'Mode-Sel', 'Mode-Sts',
        'Code-Mon', 'ExtTrig-Cmd',
        )

    MODES = _ETypes.EVT_MODES
    DELAYTYPES = ('Incr', 'Fixed')

    def __init__(self, evtname):
        """."""
        super().__init__(
            EVG.DEVNAME, evtname, properties=Event._properties)

    @property
    def mode(self):
        """."""
        return self['Mode-Sts']

    @mode.setter
    def mode(self, value):
        self._enum_setter('Mode-Sel', value, Event.MODES)

    @property
    def mode_str(self):
        """."""
        mode = self['Mode-Sts']
        if mode is not None:
            return Event.MODES[mode]
        return None

    @property
    def code(self):
        """."""
        return self['Code-Mon']

    @property
    def delay_type(self):
        """."""
        return self['DelayType-Sts']

    @delay_type.setter
    def delay_type(self, value):
        self._enum_setter('DelayType-Sel', value, Event.DELAYTYPES)

    @property
    def delay_type_str(self):
        """."""
        dlytyp = self['DelayType-Sts']
        if dlytyp is not None:
            return Event.DELAYTYPES[dlytyp]
        return None

    @property
    def delay(self):
        """."""
        return self['Delay-RB']

    @delay.setter
    def delay(self, value):
        self['Delay-SP'] = value

    @property
    def delay_raw(self):
        """."""
        return self['DelayRaw-RB']

    @delay_raw.setter
    def delay_raw(self, value):
        self['DelayRaw-SP'] = int(value)

    def cmd_external_trigger(self):
        """."""
        self['ExtTrig-Cmd'] = 1
        return True

    @property
    def is_in_inj_table(self):
        """."""
        return self.mode_str in Event.MODES[1:4]


class Trigger(_Device):
    """Device trigger."""

    STATES = ('Dsbl', 'Enbl')
    LOCKLL = ('Unlocked', 'Locked')
    POLARITIES = ('Normal', 'Inverse')

    def __init__(self, trigname):
        """Init."""
        self._database = _get_hl_trigger_database(trigname)
        self._properties = tuple(self._database)
        self._source_options = self._database['Src-Sel']['enums']
        super().__init__(trigname, properties=self._properties)

    @property
    def status(self):
        """Status."""
        return self['Status-Mon']

    @property
    def status_str(self):
        """Status string."""
        value = self.status
        strs = [d for i, d in enumerate(_TIConst.HLTrigStatusLabels)
                if _get_bit(value, i)]
        return ', '.join(strs) if strs else 'Ok'

    @property
    def status_labels(self):
        """Return Status labels of trigger.

        Returns:
            list: labels describing the possible statuses of the trigger.

        """
        pvo = self.pv_object('StatusLabels-Cte')
        return pvo.get(as_string=True).split('\n')

    @property
    def state(self):
        """State."""
        return self['State-Sts']

    @state.setter
    def state(self, value):
        self._enum_setter('State-Sel', value, Trigger.STATES)

    @property
    def state_str(self):
        """State string."""
        return Trigger.STATES[self['State-Sts']]

    @property
    def lock_low_level(self):
        """Lock low level status."""
        return self['LowLvlLock-Sts']

    @lock_low_level.setter
    def lock_low_level(self, value):
        self._enum_setter('LowLvlLock-Sel', value, Trigger.LOCKLL)

    @property
    def lock_low_level_str(self):
        """Lock low level status string."""
        return Trigger.LOCKLL[self['LowLvlLock-Sts']]

    @property
    def controlled_channels(self):
        """Return channels controlled by this trigger.

        Returns:
            list: names of the controlled channels.

        """
        pvo = self.pv_object('CtrldChannels-Cte')
        return pvo.get(as_string=True).split('\n')

    @property
    def low_level_triggers(self):
        """Return low level triggers controlled by this trigger.

        Returns:
            list: names of the controlled low level triggers.

        """
        pvo = self.pv_object('LowLvlTriggers-Cte')
        return pvo.get(as_string=True).split('\n')

    @property
    def source(self):
        """Source."""
        return self['Src-Sts']

    @source.setter
    def source(self, value):
        self._enum_setter('Src-Sel', value, self._source_options)

    @property
    def source_str(self):
        """Source string."""
        return self._source_options[self['Src-Sts']]

    @property
    def source_options(self):
        """Source options."""
        return self._source_options

    @property
    def duration(self):
        """Duration."""
        return self['Duration-RB']

    @duration.setter
    def duration(self, value):
        self['Duration-SP'] = value

    @property
    def polarity(self):
        """Polarity."""
        return self['Polarity-Sts']

    @polarity.setter
    def polarity(self, value):
        self._enum_setter('Polarity-Sel', value, Trigger.POLARITIES)

    @property
    def polarity_str(self):
        """Polarity string."""
        return Trigger.POLARITIES[self['Polarity-Sts']]

    @property
    def nr_pulses(self):
        """Nr. of pulses."""
        return self['NrPulses-RB']

    @nr_pulses.setter
    def nr_pulses(self, value):
        self['NrPulses-SP'] = value

    @property
    def delay(self):
        """Delay."""
        return self['Delay-RB']

    @delay.setter
    def delay(self, value):
        self['Delay-SP'] = value

    @property
    def total_delay(self):
        """Total delay."""
        return self['TotalDelay-Mon']

    @property
    def delta_delay(self):
        """Return delta delay array.

        Returns:
            numpy.ndarray: delta delays.

        """
        return self['DeltaDelay-RB']

    @delta_delay.setter
    def delta_delay(self, value):
        if not isinstance(value, (_np.ndarray, list, tuple)):
            raise TypeError('Value must be a numpy.ndarray, list or tuple.')

        value = _np.array(value)
        size = self.delta_delay.size
        if value.size != size:
            raise TypeError(f'Size of value must be {size:d}.')
        self['DeltaDelay-SP'] = value

    @property
    def delay_raw(self):
        """Delay raw."""
        return self['DelayRaw-RB']

    @delay_raw.setter
    def delay_raw(self, value):
        self['DelayRaw-SP'] = value

    @property
    def total_delay_raw(self):
        """Total delay raw."""
        return self['TotalDelayRaw-Mon']

    @property
    def delta_delay_raw(self):
        """Return delta delay raw array.

        Returns:
            numpy.ndarray: delta delays raw.

        """
        return self['DeltaDelayRaw-RB']

    @delta_delay_raw.setter
    def delta_delay_raw(self, value):
        if not isinstance(value, (_np.ndarray, list, tuple)):
            raise TypeError('Value must be a numpy.ndarray, list or tuple.')

        value = _np.array(value)
        size = self.delta_delay_raw.size
        if value.size != size:
            raise TypeError(f'Size of value must be {size:d}.')
        self['DeltaDelayRaw-SP'] = value

    @property
    def is_in_inj_table(self):
        """Is in Injection table."""
        return self['InInjTable-Mon']

    def cmd_enable(self, timeout=3):
        """Command enable."""
        self.state = 1
        return self._wait('State-Sts', 1, timeout)

    def cmd_disable(self, timeout=3):
        """Command disable."""
        self.state = 0
        return self._wait('State-Sts', 0, timeout)

    def cmd_lock_low_level(self, timeout=3):
        """Lock low level IOCs state."""
        self.lock_low_level = 1
        return self._wait('LowLvlLock-Sts', 1, timeout)

    def cmd_unlock_low_level(self, timeout=3):
        """Unlock low level IOCs state."""
        self.lock_low_level = 0
        return self._wait('LowLvlLock-Sts', 0, timeout)


class HLTiming(_Devices):
    """."""

    SEARCH = _HLTimeSearch

    def __init__(self):
        """."""
        self.evg = EVG()
        evs = self.SEARCH.get_configurable_hl_events()
        self.events = {ev: Event(ev) for ev in evs.keys()}
        self.triggers = {t: Trigger(t) for t in self.SEARCH.get_hl_triggers()}
        devs = [self.evg, ]
        devs += list(self.events.values())
        devs += list(self.triggers.values())
        super().__init__('AS-Glob:TI-HLTiming', devs)

    def get_triggers_events(self):
        """."""
        map_ = {tn: tr.source_str for tn, tr in self.triggers.items()}
        inv_map = {ev: list() for ev in set(map_.values())}
        for tn, ev in map_.items():
            inv_map[ev].append(tn)
        return inv_map

    def change_triggers_source(self, trigs, new_src='Linac'):
        """."""
        notchanged = list()
        for tn in trigs:
            tr = self.triggers[tn]

            if new_src not in tr.source_options:
                print(f'{tn:25s} -> No Change: {new_src:s} is not an option.')
                notchanged.append(tn)
                continue

            dly_newsrc = 0
            if new_src in self.events:
                dly_newsrc = self.events[new_src].delay_raw

            dly_oldsrc = 0
            old_src = tr.source_str
            if old_src in self.events:
                dly_oldsrc = self.events[old_src].delay_raw

            dly = tr.delay_raw
            delta_dly = dly_oldsrc
            delta_dly -= dly_newsrc
            dly += delta_dly
            if dly < 0:
                notchanged.append(tn)
                print(f'{tn:25s} -> No Change: total delay not constant!')
                continue

            tr.delay_raw = dly
            tr.source = new_src
            print(f'{tn:25s} -> Change OK: .')
        return notchanged

    def change_event_delay(self, new_dly, event='Linac'):
        """."""
        if event not in self.events:
            print(f'{event} is not a valid event!')
            return False
        new_dly = int(new_dly)
        old_dly = self.events[event].delay_raw
        dlt_dly = old_dly - new_dly

        trigs = self.get_triggers_events()[event]
        for trn in trigs:
            dly = self.triggers[trn].delay_raw + dlt_dly
            if dly < 0:
                print(f'cannot change delay: {trn:s} would change!')
                return False

        for trn in trigs:
            self.triggers[trn].delay_raw += dlt_dly
        self.events[event].delay_raw = new_dly

        print('Delay changed!')
        return True
