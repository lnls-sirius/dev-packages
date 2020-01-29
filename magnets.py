#!/usr/bin/env python-sirius
"""."""

import time as _time
from collections import namedtuple
from siriuspy.epics import PV
from siriuspy.namesys import SiriusPVName


class BaseMagnet:

    STATUS = namedtuple('Status', 'Off On')(0, 1)

    def __init__(self, name, strengname='KL'):
        """."""
        self._name = SiriusPVName(name)
        self._current_sp = PV(self._name.substitute(propty='Current-SP'))
        self._current_rb = PV(self._name.substitute(propty='Current-RB'))
        self._stren_sp = PV(self._name.substitute(propty=strengname+'-SP'))
        self._stren_rb = PV(self._name.substitute(propty=strengname+'-RB'))
        self._pwr_state_sp = PV(self._name.substitute(propty='PwrState-Sel'))
        self._pwr_state_rb = PV(self._name.substitute(propty='PwrState-Sts'))

    @property
    def name(self):
        """."""
        return self._name

    @property
    def strength(self):
        """."""
        return self._stren_rb.value

    @strength.setter
    def strength(self, value):
        self._stren_sp.value = value

    @property
    def current(self):
        """."""
        return self._current_rb.value

    @current.setter
    def current(self, value):
        self._current_sp.value = value

    @property
    def pwr_state(self):
        """."""
        return self._pwr_state_rb.value

    @pwr_state.setter
    def pwr_state(self, value):
        self._pwr_state_sp.value = value

    def turnon(self, timeout=0.5):
        """."""
        self.pwr_state = self.STATUS.On
        self._wait(self.STATUS.On, timeout=timeout)

    def turnoff(self, timeout=0.5):
        """."""
        self.pwr_state = self.STATUS.Off
        self._wait(self.STATUS.Off, timeout=timeout)

    def _wait(self, value, timeout=10):
        """."""
        inter = 0.05
        n = int(timeout/inter)
        _time.sleep(4*inter)
        for _ in range(n):
            if self.pwr_state == value:
                break
            _time.sleep(inter)

    @property
    def connected(self):
        """."""
        conn = self._stren_sp.connected
        conn &= self._stren_rb.connected
        conn &= self._pwr_state_sp.connected
        conn &= self._pwr_state_rb.connected
        return conn


class TrimQuad(BaseMagnet):
    """."""

    def __init__(self, name):
        """."""
        super().__init__(name, strengname='KL')


class Corrector(BaseMagnet):
    """."""

    def __init__(self, name):
        """."""
        super().__init__(name, strengname='Kick')
