"""."""

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
        )

    def __init__(self):
        """."""
        super().__init__(EVG.DEVNAME, properties=EVG._properties)

    @property
    def nrpulses(self):
        """."""
        return self['RepeatBucketList-RB']

    @nrpulses.setter
    def nrpulses(self, value):
        """."""
        self['RepeatBucketList-SP'] = bool(value)

    @property
    def bucketlist_len(self):
        """."""
        return self['BucketListLen-Mon']

    @property
    def bucketlist_mon(self):
        """."""
        return self['BucketList-Mon']

    @property
    def bucketlist(self):
        """."""
        return self['BucketList-RB']

    @bucketlist.setter
    def bucketlist(self, value):
        """."""
        self['BucketList-SP'] = _np.array(value, dtype=int)

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

    def fill_bucketlist(self, stop, start=1, step=30):
        """."""
        self.bucketlist = _np.arange(start=start, stop=stop, step=step)

    def wait_injection_finish(self, timeout=10):
        """."""
        return self._wait(propty='InjectionEvt-Sts', value=0, timeout=timeout)

    def cmd_update_events(self):
        """."""
        self['UpdateEvt-Cmd'] = 1

    def cmd_turn_on_injection(self, timeout=10):
        """."""
        self.injection_state = 1
        self._wait(propty='InjectionEvt-Sel', value=1, timeout=timeout)

    def cmd_turn_off_injection(self, timeout=10):
        """."""
        self.injection_state = 0
        self._wait(propty='InjectionEvt-Sel', value=0, timeout=timeout)

    def cmd_turn_on_continuous(self, timeout=10):
        """."""
        self.continuous_state = 1
        self._wait(propty='ContinuousEvt-Sel', value=1, timeout=timeout)

    def cmd_turn_off_continuous(self, timeout=10):
        """."""
        self.continuous_state = 0
        self._wait(propty='ContinuousEvt-Sel', value=0, timeout=timeout)


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

    @property
    def is_in_inj_table(self):
        """."""
        return self.mode_str in Event.MODES[1:4]


class Trigger(_Device):
    """Device trigger."""

    STATES = ('Dsbl', 'Enbl')
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
    def is_in_inj_table(self):
        """Is in Injection table."""
        return self['InInjTable-Mon']
