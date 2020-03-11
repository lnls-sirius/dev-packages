"""."""

import time as _time

from .device import Device as _Device


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
        if devname != EVG.DEVICES.ALL:
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
