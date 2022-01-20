"""."""
import time as _time

import numpy as _np

from .device import Device as _Device, ProptyDevice as _ProptyDevice
from ..timesys.csdev import ETypes as _ETypes, Const as _TIConst, \
    get_hl_trigger_database as _get_hl_trigger_database
from ..util import get_bit as _get_bit


class EVG(_Device):
    """Device EVG."""

    DEVNAME = 'AS-RaMO:TI-EVG'

    _properties = (
        'InjectionEvt-Sel', 'InjectionEvt-Sts', 'UpdateEvt-Cmd',
        'ContinuousEvt-Sel', 'ContinuousEvt-Sts',
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
        return self['ContinuousEvt-Sts']

    @continuous_state.setter
    def continuous_state(self, value):
        """."""
        self['ContinuousEvt-Sel'] = bool(value)

    @property
    def injection_state(self):
        """."""
        return self['InjectionEvt-Sts']

    @injection_state.setter
    def injection_state(self, value):
        """."""
        self['InjectionEvt-Sel'] = bool(value)

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
        return Event.MODES[self['Mode-Sts']]

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
        return Event.DELAYTYPES[self['DelayType-Sts']]

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
