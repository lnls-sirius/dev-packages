#!/usr/bin/env python-sirius

from epics import PV


class Klystron:

    def __init__(self):
        self._sp = PV('LA-RF:LLRF:KLY2:SET_AMP')
        self._rb = PV('LA-RF:LLRF:KLY2:GET_AMP')

    @property
    def amplitude(self):
        return self._rb.value

    @amplitude.setter
    def amplitude(self, value):
        self._sp.value = value

    @property
    def connected(self):
        return self._sp.connected & self._rb.connected
