"""Eppics Device module."""

import time as _time

from ..epics import PV as _PV
from ..namesys import SiriusPVName as _SiriusPVName


class Device:
    """General Epics Device."""

    def __init__(self, devname, properties):
        """."""
        self._devname = _SiriusPVName(devname)
        self._properties = properties[:]
        self._pvs = self._create_pvs()

    @property
    def devname(self):
        """."""
        return self._devname

    @property
    def properties(self):
        """."""
        return self._properties

    @property
    def pvnames(self):
        """."""
        pvnames = [pv.pvname for pv in self._pvs.values()]
        return pvnames

    @property
    def connected(self):
        """."""
        for pvobj in self._pvs.values():
            if not pvobj.connected:
                return False
        return True

    @property
    def disconnected_pvnames(self):
        """."""
        dlist = list()
        for pvname, pvobj in self._pvs.items():
            if not pvobj.connected:
                dlist.append(pvname)
        return dlist

    def get(self, propty):
        """Return value of proerty."""
        pvobj = self._pvs[propty]
        value = pvobj.get()
        return value

    # --- private methods ---

    def _create_pvs(self):
        func = self._devname.substitute
        pvs = dict()
        for propty in self._properties:
            pvname = func(propty=propty)
            auto_monitor = not pvname.endswith('-Mon')
            pvs[propty] = _PV(pvname, auto_monitor=auto_monitor)
        return pvs

    def _wait(self, propty, value, timeout=10):
        """."""
        interval = 0.050  # [s]
        ntrials = int(timeout/interval)
        _time.sleep(4*interval)
        for _ in range(ntrials):
            if self.get(propty) == value:
                break
            _time.sleep(interval)
