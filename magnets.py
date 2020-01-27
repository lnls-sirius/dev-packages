#!/usr/bin/env python-sirius
"""."""


from collections import namedtuple
from siriuspy.epics import PV
from siriuspy.namesys import SiriusPVName


class TrimQuad:
    """."""

    STATUS = namedtuple('Status', 'Off On')(0, 1)

    def __init__(self, name):
        """."""
        self._name = SiriusPVName(name)
        self._stren_sp = PV(self._name.substitute(propty='KL-SP'))
        self._stren_rb = PV(self._name.substitute(propty='KL-RB'))
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
    def pwr_state(self):
        """."""
        return self._pwr_state_rb.value

    @pwr_state.setter
    def pwr_state(self, value):
        self._pwr_state_sp.value = value

    def turnon(self, timeout=0.5):
        """."""
        self.pwr_state = self.STATUS.On

    def turnoff(self, timeout=0.5):
        """."""
        self.pwr_state = self.STATUS.Off

    @property
    def connected(self):
        """."""
        conn = self._stren_sp.connected
        conn &= self._stren_rb.connected
        conn &= self._pwr_state_sp.connected
        conn &= self._pwr_state_rb.connected
        return conn


class Corrector:
    """."""

    STATUS = namedtuple('Status', 'Off On')(0, 1)

    def __init__(self, name):
        """."""
        self._name = SiriusPVName(name)
        self._stren_sp = PV(self._name.substitute(propty='Kick-SP'))
        self._stren_rb = PV(self._name.substitute(propty='Kick-RB'))
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
    def pwr_state(self):
        """."""
        return self._pwr_state_rb.value

    @pwr_state.setter
    def pwr_state(self, value):
        self._pwr_state_sp.value = value

    def turnon(self, timeout=0.5):
        """."""
        self.pwr_state = self.STATUS.On

    def turnoff(self, timeout=0.5):
        """."""
        self.pwr_state = self.STATUS.Off

    @property
    def connected(self):
        """."""
        conn = self._stren_sp.connected
        conn &= self._stren_rb.connected
        conn &= self._pwr_state_sp.connected
        conn &= self._pwr_state_rb.connected
        return conn
