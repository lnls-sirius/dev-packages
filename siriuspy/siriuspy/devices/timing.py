"""."""

import time as _time

from .device import Device as _Device, ProptyDevice as _ProptyDevice


class EVG(_Device):
    """."""

    class DEVICES:
        """Devices names."""

        AS = 'AS-RaMO:TI-EVG'
        ALL = (AS, )

    _properties = (
        'InjectionEvt-Sel',
        'InjectionEvt-Sts')

    def __init__(self, devname=None):
        """."""
        if devname is None:
            devname = EVG.DEVICES.AS

        # check if device exists
        if devname not in EVG.DEVICES.ALL:
            raise NotImplementedError(devname)

        # call base class constructor
        super().__init__(devname, properties=EVG._properties)

    @property
    def pulses(self):
        """."""
        return self['InjectionEvt-Sts']

    @pulses.setter
    def pulses(self, value):
        self['InjectionEvt-Sel'] = bool(value)

    def wait(self, timeout=10):
        """."""
        interval = 0.1
        ntrials = int(timeout / interval)
        for _ in range(ntrials):
            _time.sleep(interval)
            if self.pulses == self['InjectionEvt-Sel']:
                return

    def cmd_turn_on_pulses(self, timeout=10):
        """."""
        self.pulses = 1
        self.wait(timeout=timeout)

    def cmd_turn_off_pulses(self, timeout=10):
        """."""
        self.pulses = 0
        self.wait(timeout=timeout)


class Event(_ProptyDevice):
    """."""

    _properties = (
        'Delay-SP', 'Delay-RB', 'DelayRaw-SP', 'DelayRaw-RB',
        'DelayType-Sel', 'DelayType-Sts', 'Mode-Sel', 'Mode-Sts',
        'Code-Mon', 'ExtTrig-Cmd',
        )

    MODES = ('Disable', 'Continuous', 'Injection', 'OneShot', 'External')
    DELAYTYPES = ('Incr', 'Fixed')

    def __init__(self, evtname):
        """."""
        super().__init__(
            EVG.DEVICES.AS, evtname, properties=Event._properties)

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

    def is_in_injection(self):
        """."""
        return self.mode_str in Event.MODES[1:4]
