#!/usr/bin/env python-sirius
"""."""

import time as _time
from epics import PV


class LiLLRF:
    """."""

    NAME_SHB = 'shb'
    NAME_K1 = 'kly1'
    NAME_K2 = 'kly2'

    def __init__(self, device_name):
        """."""
        if not set(self.NAME_SHB) - set(device_name.lower()):
            name = 'BUN1'
        elif not set(self.NAME_K1) - set(device_name.lower()):
            name = 'KLY1'
        elif not set(self.NAME_K2) - set(device_name.lower()):
            name = 'KLY2'
        else:
            raise Exception('Set device name: SHB, Klystron1 or Klystron2')

        self._amp_sp = PV('LA-RF:LLRF:' + name + ':SET_AMP')
        self._amp_rb = PV('LA-RF:LLRF:' + name + ':GET_AMP')
        self._ph_sp = PV('LA-RF:LLRF:' + name + ':SET_PHASE')
        self._ph_rb = PV('LA-RF:LLRF:' + name + ':GET_PHASE')

    @property
    def amplitude(self):
        """."""
        return self._amp_rb.value

    @amplitude.setter
    def amplitude(self, value):
        self._amp_sp.value = value

    @property
    def phase(self):
        """."""
        return self._ph_rb.value

    @phase.setter
    def phase(self, value):
        self._ph_rb.value = value

    @property
    def connected(self):
        """."""
        conn = self._amp_sp.connected
        conn &= self._amp_rb.connected
        conn &= self._ph_sp.connected
        conn &= self._ph_rb.connected
        return conn

    def wait(self, timeout=10, prop=None):
        """."""
        nrp = int(timeout / 0.1)
        for _ in range(nrp):
            _time.sleep(0.1)
            if prop == 'phase':
                if abs(self.phase - self._ph_sp.value) < 0.1:
                    break
            elif prop == 'amplitude':
                if abs(self.amplitude - self._amp_sp.value) < 0.1:
                    break
            else:
                raise Exception(
                    'Set LLRF property (phase or amplitude)')
        else:
            print('timed out waiting LLRF.')

    def set_phase(self, value, timeout=10):
        """."""
        self.phase = value
        self.wait(timeout, 'phase')

    def set_amplitude(self, value, timeout=30):
        """."""
        self.amplitude = value
        self.wait(timeout, 'amplitude')
