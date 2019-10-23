#!/usr/bin/env python-sirius

from siriuspy.epics import PV
from siriuspy.namesys import SiriusPVName


class Kicker:

    def __init__(self, name):
        self._name = SiriusPVName(name)
        self._dly_sp = PV(self._name.substitute(prpty='Delay-SP'))
        self._dly_rb = PV(self._name.substitute(prpty='Delay-RB'))
        self._volt_sp = PV(self._name.substitute(prpty='Voltage-SP'))
        self._volt_rb = PV(self._name.substitute(prpty='Voltage-RB'))
        self._pulse_sp = PV(self._name.substitute(prpty='Pulse-SP'))
        self._pulse_rb = PV(self._name.substitute(prpty='Pulse-RB'))

    @property
    def name(self):
        return self._name

    @property
    def voltage(self):
        return self._volt_rb.value

    @voltage.setter
    def voltage(self, value):
        self._volt_sp.value = value

    @property
    def delay(self):
        return self._dly_rb.value

    @delay.setter
    def delay(self, value):
        self._dly_sp.value = value

    @property
    def pulse(self):
        return self._pulse_rb.value

    @pulse.setter
    def pulse(self, value):
        self._pulse_sp.value = value

    def turnon_pulse(self):
        self.pulse = 1

    def turnoff_pulse(self):
        self.pulse = 0

    @property
    def connected(self):
        conn = self._volt_sp.connected
        conn &= self._volt_rb.connected
        conn &= self._dly_sp.connected
        conn &= self._dly_rb.connected
        conn &= self._pulse_sp.connected
        conn &= self._pulse_rb.connected
        return conn
