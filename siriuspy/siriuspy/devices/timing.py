#!/usr/bin/env python-sirius
"""."""

import time as _time
from epics import PV


class Timing:
    """."""

    def __init__(self):
        """."""
        self._pulses_sp = PV('AS-RaMO:TI-EVG:InjectionEvt-Sel')
        self._pulses_rb = PV('AS-RaMO:TI-EVG:InjectionEvt-Sts')

    @property
    def connected(self):
        """."""
        return self._pulses_rb.connected and self._pulses_sp.connected

    @property
    def pulses(self):
        """."""
        return self._pulses_rb.value

    @pulses.setter
    def pulses(self, value):
        self._pulses_sp.value = bool(value)

    def wait(self, timeout=10):
        """."""
        inter = 0.1
        nt = int(timeout / inter)
        for _ in range(nt):
            _time.sleep(inter)
            if self._pulses_rb.value == self._pulses_sp.value:
                return

    def turn_pulses_on(self, timeout=10):
        """."""
        self.pulses = 1
        self.wait(timeout=timeout)

    def turn_pulses_off(self, timeout=10):
        """."""
        self.pulses = 0
        self.wait(timeout=timeout)
