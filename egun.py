#!/usr/bin/env python-sirius
"""."""

from collections import namedtuple
from epics import PV


class Bias:
    """."""

    STATUS = namedtuple('Status', 'Off On')(0, 1)

    def __init__(self):
        """."""
        self._volt_sp = PV('LI-01:EG-BiasPS:voltoutsoft')
        self._volt_rb = PV('LI-01:EG-BiasPS:voltinsoft')
        self._curr_rb = PV('LI-01:EG-BiasPS:currentinsoft')
        self._switch = PV('LI-01:EG-BiasPS:switch')
        self._switch_sts = PV('LI-01:EG-BiasPS:swstatus')

    @property
    def voltage(self):
        """."""
        return self._volt_rb.value

    @voltage.setter
    def voltage(self, value):
        """."""
        self._volt_sp.value = value

    @property
    def current(self):
        """."""
        return self._curr_rb.value

    @property
    def connected(self):
        """."""
        conn = self._volt_sp.connected
        conn &= self._volt_rb.connected
        conn &= self._curr_rb.connected
        conn &= self._switch.connected
        conn &= self._switch_sts.connected
        return conn

    def turn_on(self):
        """."""
        self._switch.value = self.STATUS.On

    def turn_off(self):
        """."""
        self._switch.value = self.STATUS.Off

    def is_on(self):
        """."""
        return self._switch_sts.value == self.STATUS.On


class Filament:
    """."""

    STATUS = namedtuple('Status', 'Off On')(0, 1)

    def __init__(self):
        """."""
        self._volt_rb = PV('LI-01:EG-FilaPS:voltinsoft')
        self._curr_rb = PV('LI-01:EG-FilaPS:currentinsoft')
        self._curr_sp = PV('LI-01:EG-FilaPS:currentoutsoft')
        self._switch = PV('LI-01:EG-FilaPS:switch')
        self._switch_sts = PV('LI-01:EG-FilaPS:swstatus')

    @property
    def voltage(self):
        """."""
        return self._volt_rb.value

    @property
    def current(self):
        """."""
        return self._curr_rb.value

    @current.setter
    def current(self, value):
        self._curr_sp.value = value

    @property
    def connected(self):
        """."""
        conn = self._volt_rb.connected
        conn &= self._curr_rb.connected
        conn &= self._curr_sp.connected
        conn &= self._switch.connected
        conn &= self._switch_sts.connected
        return conn

    def turn_on(self):
        """."""
        self._switch.value = self.STATUS.On

    def turn_off(self):
        """."""
        self._switch.value = self.STATUS.Off

    def is_on(self):
        """."""
        return self._switch_sts.value == self.STATUS.On


class HVPS:
    """."""

    STATUS = namedtuple('Status', 'Off On')(0, 1)

    def __init__(self):
        """."""
        self._curr_rb = PV('LI-01:EG-HVPS:currentinsoft')
        self._curr_sp = PV('LI-01:EG-HVPS:currentoutsoft')
        self._volt_rb = PV('LI-01:EG-HVPS:voltinsoft')
        self._volt_sp = PV('LI-01:EG-HVPS:voltoutsoft')
        self._enable = PV('LI-01:EG-HVPS:enable')
        self._enable_sts = PV('LI-01:EG-HVPS:enstatus')
        self._switch = PV('LI-01:EG-HVPS:switch')
        self._switch_sts = PV('LI-01:EG-HVPS:swstatus')

    @property
    def current(self):
        """."""
        return self._curr_rb.value

    @current.setter
    def current(self, value):
        self._curr_sp.value = value

    @property
    def voltage(self):
        """."""
        return self._volt_rb.value

    @voltage.setter
    def voltage(self, value):
        self._volt_sp.value = value

    @property
    def connected(self):
        """."""
        conn = self._curr_rb.connected
        conn &= self._curr_sp.connected
        conn &= self._volt_sp.connected
        conn &= self._volt_rb.connected
        conn &= self._enable.connected
        conn &= self._enable_sts.connected
        conn &= self._switch.connected
        conn &= self._switch_sts.connected
        return conn

    def turn_on(self):
        """."""
        self._enable.value = self.STATUS.On
        self._switch.value = self.STATUS.On

    def turn_off(self):
        """."""
        self._enable.value = self.STATUS.Off
        self._switch.value = self.STATUS.Off

    def is_on(self):
        """."""
        ison = self._enable_sts.value == self.STATUS.On
        ison &= self._switch_sts.value == self.STATUS.On
        return ison
