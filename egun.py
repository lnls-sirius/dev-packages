#!/usr/bin/env python-sirius

from epics import PV


class Bias:

    def __init__(self):
        self._volt_sp = PV('LI-01:EG-BiasPS:voltoutsoft')
        self._volt_rb = PV('LI-01:EG-BiasPS:voltinsoft')
        self._curr_rb = PV('LI-01:EG-BiasPS:currentinsoft')
        self._switch = PV('LI-01:EG-BiasPS:switch')
        self._switch_sts = PV('LI-01:EG-BiasPS:swstatus')
        self._on_state = 1
        self._off_state = 0

    @property
    def voltage(self):
        return self._volt_rb.value

    @voltage.setter
    def voltage(self, value):
        self._volt_sp.value = value

    @property
    def current(self):
        return self._curr_rb.value

    @property
    def connected(self):
        conn = self._volt_sp.connected
        conn &= self._volt_rb.connected
        conn &= self._curr_rb.connected
        conn &= self._switch.connected
        conn &= self._switch_sts.connected
        return conn

    def turn_on(self):
        self._switch.value = self._on_state

    def turn_off(self):
        self._switch.value = self._off_state

    def is_on(self):
        return self._switch_sts.value == self._on_state


class Filament:

    def __init__(self):
        self._volt_rb = PV('LI-01:EG-FilaPS:voltinsoft')
        self._curr_rb = PV('LI-01:EG-FilaPS:currentinsoft')
        self._curr_sp = PV('LI-01:EG-FilaPS:currentoutsoft')
        self._switch = PV('LI-01:EG-FilaPS:switch')
        self._switch_sts = PV('LI-01:EG-FilaPS:swstatus')
        self._on_state = 1
        self._off_state = 0

    @property
    def voltage(self):
        return self._volt_rb.value

    @property
    def current(self):
        return self._curr_rb.value

    @current.setter
    def current(self, value):
        self._curr_sp.value = value

    @property
    def connected(self):
        conn = self._volt_rb.connected
        conn &= self._curr_rb.connected
        conn &= self._curr_sp.connected
        conn &= self._switch.connected
        conn &= self._switch_sts.connected
        return conn

    def turn_on(self):
        self._switch.value = self._on_state

    def turn_off(self):
        self._switch.value = self._off_state

    def is_on(self):
        return self._switch_sts.value == self._on_state


class LeakCurr:

    def __init__(self):
        self._curr_rb = PV('LI-01:EG-HVPS:currentinsoft')
        self._curr_sp = PV('LI-01:EG-HVPS:currentoutsoft')
        self._enable = PV('LI-01:EG-HVPS:enable')
        self._enable_sts = PV('LI-01:EG-HVPS:enstatus')
        self._on_state = 1
        self._off_state = 0

    @property
    def current(self):
        return self._curr_rb.value

    @current.setter
    def current(self, value):
        self._curr_sp.value = value

    @property
    def connected(self):
        conn = self._curr_rb.connected
        conn &= self._curr_sp.connected
        conn &= self._enable.connected
        conn &= self._enable_sts.connected
        return conn

    def turn_on(self):
        self._enable.value = self._on_state

    def turn_off(self):
        self._enable.value = self._off_state

    def is_on(self):
        return self._enable_sts.value == self._on_state


class HighVoltage:

    def __init__(self):
        self._volt_sp = PV('LI-01:EG-BiasPS:voltoutsoft')
        self._volt_rb = PV('LI-01:EG-BiasPS:voltinsoft')
        self._switch = PV('LI-01:EG-BiasPS:switch')
        self._switch_sts = PV('LI-01:EG-BiasPS:swstatus')
        self._on_state = 1
        self._off_state = 0

    @property
    def voltage(self):
        return self._volt_rb.value

    @voltage.setter
    def voltage(self, value):
        self._volt_sp.value = value

    @property
    def connected(self):
        conn = self._volt_sp.connected
        conn &= self._volt_rb.connected
        conn &= self._switch.connected
        conn &= self._switch_sts.connected
        return conn

    def turn_on(self):
        self._switch.value = self._on_state

    def turn_off(self):
        self._switch.value = self._off_state

    def is_on(self):
        return self._switch_sts.value == self._on_state
