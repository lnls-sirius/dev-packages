#!/usr/bin/env python-sirius
"""."""

from epics import PV


class ICT:
    """."""

    def __init__(self, name):
        """."""
        if name in ['ICT-1', 'ICT-2']:
            self._charge = PV('LI-01:DI-' + name + ':Charge-Mon')
            self._charge_avg = PV('LI-01:DI-' + name + 'ICT-1:ChargeAvg-Mon')
            self._charge_max = PV('LI-01:DI-' + name + 'ICT-1:ChargeMax-Mon')
            self._charge_min = PV('LI-01:DI-' + name + 'ICT-1:ChargeMin-Mon')
            self._charge_std = PV('LI-01:DI-' + name + 'ICT-1:ChargeStd-Mon')
            self._pulse_cnt = PV('LI-01:DI-' + name + ':PulseCount-Mon')
        else:
            raise Exception('Set device name: ICT-1 or ICT-2')

    @property
    def connected(self):
        """."""
        conn = self._charge.connected
        conn &= self._charge_avg.connected
        conn &= self._charge_max.connected
        conn &= self._charge_min.connected
        conn &= self._charge_std.connected
        conn &= self._pulse_cnt.connected
        return conn

    @property
    def charge(self):
        """."""
        return self._charge.get()

    @property
    def charge_avg(self):
        """."""
        return self._charge_avg.get()

    @property
    def charge_max(self):
        """."""
        return self._charge_max.get()

    @property
    def charge_min(self):
        """."""
        return self._charge_min.get()

    @property
    def charge_std(self):
        """."""
        return self._charge_std.get()

    @property
    def pulse_count(self):
        """."""
        return self._pulse_cnt.get()


class TranspEff:
    """."""

    def __init__(self):
        """."""
        self._eff = PV('LI-Glob:AP-TranspEff:Eff-Mon')

    @property
    def connected(self):
        """."""
        return self._eff.connected

    @property
    def efficiency(self):
        """."""
        return self._eff.get()
