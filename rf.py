#!/usr/bin/env python-sirius
"""."""

import time as _time
from epics import PV


class RF:
    """."""

    def __init__(self, acc=None, is_cw=True):
        """."""
        if acc == 'SI':
            pre = 'SR'
            self._frequency_sp = PV('RF-SI-Gen:GeneralFreq-SP')
            self._frequency_rb = PV('RF-SI-Gen:GeneralFreq-RB')
        elif acc == 'BO':
            pre = 'BR'
            self._frequency_sp = PV('RF-Gen:GeneralFreq-SP')
            self._frequency_rb = PV('RF-Gen:GeneralFreq-RB')
        else:
            raise Exception('Set BO or SI.')
        self.is_cw = is_cw
        if self.is_cw:
            self._phase_sp = PV(pre+'-RF-DLLRF-01:PL:REF:S')
            self._phase_rb = PV(pre+'-RF-DLLRF-01:SL:INP:PHS')
        else:
            self._phase_bot_sp = PV(pre+'-RF-DLLRF-01:RmpPhsBot-SP')
            self._phase_bot_rb = PV(pre+'-RF-DLLRF-01:RmpPhsBot-SP')
            self._phase_top_sp = PV(pre+'-RF-DLLRF-01:RmpPhsTop-SP')
            self._phase_top_rb = PV(pre+'-RF-DLLRF-01:RmpPhsTop-SP')
        self._voltage_sp = PV(pre+'-RF-DLLRF-01:mV:AL:REF:S')
        self._voltage_rb = PV(pre+'-RF-DLLRF-01:SL:REF:AMP')
        self._power_mon = PV('RA-RaBO01:RF-LLRFCalSys:PwrW1-Mon')

    @property
    def connected(self):
        """."""
        if self.is_cw:
            conn = self._phase_rb.connected
            conn &= self._phase_sp.connected
        else:
            conn = self._phase_bot_rb.connected
            conn &= self._phase_bot_sp.connected
            conn &= self._phase_top_sp.connected
            conn &= self._phase_top_sp.connected
        conn &= self._voltage_sp.connected
        conn &= self._voltage_rb.connected
        conn &= self._power_mon.connected
        conn &= self._frequency_sp.connected
        conn &= self._frequency_rb.connected
        return conn

    @property
    def power(self):
        """."""
        return self._power_mon.value

    @property
    def phase(self):
        """."""
        return self._phase_rb.value if self.is_cw else self._phase_bot_rb.value

    @phase.setter
    def phase(self, value):
        if self.is_cw:
            self._phase_sp.value = value
        else:
            self._phase_bot_sp.value = value
            self._phase_top_sp.value = value

    @property
    def voltage(self):
        """."""
        return self._voltage_rb.value

    @voltage.setter
    def voltage(self, value):
        self._voltage_sp.value = value

    @property
    def frequency(self):
        """."""
        return self._frequency_rb.value

    @frequency.setter
    def frequency(self, value):
        self._frequency_sp.value = value

    def set_voltage(self, value, timeout=10):
        """."""
        self.voltage = value
        self.wait(timeout, 'voltage')

    def set_phase(self, value, timeout=10):
        """."""
        self.phase = value
        self.wait(timeout, 'phase')

    def set_frequency(self, value, timeout=10):
        """."""
        self.frequency = value
        self.wait(timeout, 'frequency')

    def wait(self, timeout=10, prop=None):
        """."""
        nrp = int(timeout / 0.1)
        for _ in range(nrp):
            _time.sleep(0.1)
            if prop == 'phase':
                if self.is_cw:
                    phase_sp = self._phase_sp.value
                else:
                    phase_sp = self._phase_bot_sp.value
                if abs(self.phase - phase_sp) < 0.1:
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
