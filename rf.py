#!/usr/bin/env python-sirius

import time as _time
from epics import PV


class RF:

    def __init__(self):
        self._phase_sp = PV('BR-RF-DLLRF-01:PL:REF:S')
        self._phase_rb = PV('BR-RF-DLLRF-01:SL:INP:PHS')
        self._voltage_sp = PV('BR-RF-DLLRF-01:mV:AL:REF:S')
        self._voltage_rb = PV('BR-RF-DLLRF-01:SL:REF:AMP')
        self._power_mon = PV('RA-RaBO01:RF-LLRFCalSys:PwrW1-Mon')
        self._frequency_sp = PV('RF-Gen:GeneralFreq-SP')
        self._frequency_rb = PV('RF-Gen:GeneralFreq-RB')

    @property
    def connected(self):
        conn = self._phase_rb.connected
        conn &= self._phase_sp.connected
        conn &= self._voltage_sp.connected
        conn &= self._voltage_rb.connected
        conn &= self._power_mon.connected
        conn &= self._frequency_sp.connected
        conn &= self._frequency_rb.connected
        return conn

    @property
    def power(self):
        return self._power_mon.value

    @property
    def phase(self):
        return self._phase_rb.value

    @phase.setter
    def phase(self, value):
        self._phase_sp.value = value

    @property
    def voltage(self):
        return self._voltage_rb.value

    @voltage.setter
    def voltage(self, value):
        self._voltage_sp.value = value

    @property
    def frequency(self):
        return self._frequency_rb.value

    @frequency.setter
    def frequency(self, value):
        self._frequency_sp.value = value

    def set_voltage(self, value, timeout=10):
        self.voltage = value
        self.wait(timeout, 'voltage')

    def set_phase(self, value, timeout=10):
        self.phase = value
        self.wait(timeout, 'phase')

    def set_frequency(self, value, timeout=10):
        self.frequency = value
        self.wait(timeout, 'frequency')

    def wait(self, timeout=10, prop=None):
        nrp = int(timeout / 0.1)
        for _ in range(nrp):
            _time.sleep(0.1)
            if prop == 'phase':
                if abs(self.phase - self._phase_sp.value) < 0.1:
                    break
            elif prop == 'voltage':
                if abs(self.voltage - self._voltage_sp.value) < 0.1:
                    break
            elif prop == 'frequency':
                if abs(self.frequency - self._frequency_sp.value) < 0.1:
                    break
            else:
                raise Exception(
                    'Set RF property (phase, voltage or frequency)')
        else:
            print('timed out waiting RF.')
