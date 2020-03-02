"""."""

from collections import namedtuple
from siriuspy.epics import PV
from siriuspy.namesys import SiriusPVName


class Septum:
    """."""

    STATUS = namedtuple('Status', 'Off On')(0, 1)

    def __init__(self, name):
        """."""
        self._name = SiriusPVName(name)
        tiname = self._name.substitute(dis='TI')
        self._dly_sp = PV(tiname.substitute(propty='Delay-SP'))
        self._dly_rb = PV(tiname.substitute(propty='Delay-RB'))
        self._volt_sp = PV(self._name.substitute(propty='Voltage-SP'))
        self._volt_rb = PV(self._name.substitute(propty='Voltage-RB'))
        self._pulse_sp = PV(self._name.substitute(propty='Pulse-Sel'))
        self._pulse_rb = PV(self._name.substitute(propty='Pulse-Sts'))

    @property
    def name(self):
        """."""
        return self._name

    @property
    def voltage(self):
        """."""
        return self._volt_rb.value

    @voltage.setter
    def voltage(self, value):
        self._volt_sp.value = value

    @property
    def delay(self):
        """."""
        return self._dly_rb.value

    @delay.setter
    def delay(self, value):
        self._dly_sp.value = value

    @property
    def pulse(self):
        """."""
        return self._pulse_rb.value

    @pulse.setter
    def pulse(self, value):
        self._pulse_sp.value = value

    def turn_on_pulse(self):
        """."""
        self.pulse = self.STATUS.On

    def turn_off_pulse(self):
        """."""
        self.pulse = self.STATUS.Off

    @property
    def connected(self):
        """."""
        conn = self._volt_sp.connected
        conn &= self._volt_rb.connected
        conn &= self._dly_sp.connected
        conn &= self._dly_rb.connected
        conn &= self._pulse_sp.connected
        conn &= self._pulse_rb.connected
        return conn
