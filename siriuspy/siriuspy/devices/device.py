"""Epics Device module."""

import time as _time

from ..epics import PV as _PV
from ..namesys import SiriusPVName as _SiriusPVName


class Device:
    """General Epics Device."""

    def __init__(self, devname, properties):
        """."""
        # TODO: uncomment when all devices comlpy with naming system
        # self._devname = _SiriusPVName(devname)
        self._devname = devname

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

    def __getitem__(self, propty):
        """Return value of property."""
        pvobj = self._pvs[propty]
        value = pvobj.get()
        return value

    def __setitem__(self, propty, value):
        """Set value of property."""
        pvobj = self._pvs[propty]
        pvobj.value = value

    # --- private methods ---

    def _create_pvs(self):
        pvs = dict()
        for propty in self._properties:
            pvname = self._devname + ':' + propty
            auto_monitor = not pvname.endswith('-Mon')
            pvs[propty] = _PV(pvname, auto_monitor=auto_monitor)
        return pvs

    # TODO: uncomment when all devices comlpy with naming system
    # def _create_pvs(self):
    #     func = self._devname.substitute
    #     pvs = dict()
    #     for propty in self._properties:
    #         pvname = func(propty=propty)
    #         auto_monitor = not pvname.endswith('-Mon')
    #         pvs[propty] = _PV(pvname, auto_monitor=auto_monitor)
    #     return pvs

    def _wait(self, propty, value, timeout=10):
        """."""
        interval = 0.050  # [s]
        ntrials = int(timeout/interval)
        _time.sleep(4*interval)
        for _ in range(ntrials):
            if self[propty] == value:
                break
            _time.sleep(interval)


class Devices:
    """."""

    def __init__(self, devname, devices):
        """."""
        self._devname = _SiriusPVName(devname)
        self._devices = devices

        self._properties = ()
        for dev in self._devices:
            self._properties += dev.properties

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
        pvnames = []
        for dev in self._devices:
            pvnames += dev.pvnames
        return pvnames

    @property
    def connected(self):
        """."""
        for dev in self._devices:
            if not dev.connected:
                return False
        return True

    @property
    def disconnected_pvnames(self):
        """."""
        dlist = list()
        for dev in self._devices:
            dlist += dev.disconnected_pvnames
        return dlist

    @property
    def devices(self):
        """Return devices."""
        return self._devices

    def _prop_get(self, devidx, propty):
        """Return value of property."""
        return self._devices[devidx][propty]

    def _prop_set(self, devidx, propty, value):
        """Set value of property."""
        self._devices[devidx][propty] = value

    def __getitem__(self, devidx):
        """Return device."""
        return self._devices[devidx]
