#!/usr/bin/env python-sirius
"""."""

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
