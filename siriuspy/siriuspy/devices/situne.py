#!/usr/bin/env python-sirius
"""."""

from epics import PV


class SITune:
    """."""

    def __init__(self):
        """."""
        pre = 'SI-Glob:DI-Tune'
        prop = 'TuneFrac-Mon'
        prop_wf = 'Trace-Mon'
        self._tunex = PV(pre + '-H:' + prop)
        self._tuney = PV(pre + '-V:' + prop)
        self._tunex_wfm = PV(pre + 'Proc-H:' + prop_wf)
        self._tuney_wfm = PV(pre + 'Proc-V:' + prop_wf)

    @property
    def connected(self):
        """."""
        conn = self._tunex.connected
        conn &= self._tuney.connected
        conn &= self._tunex_wfm.connected
        conn &= self._tuney_wfm.connected
        return conn

    @property
    def tunex(self):
        """."""
        return self._tunex.value

    @property
    def tuney(self):
        """."""
        return self._tuney.value

    @property
    def tunex_wfm(self):
        """."""
        return self._tunex_wfm.value

    @property
    def tuney_wfm(self):
        """."""
        return self._tuney_wfm.value
