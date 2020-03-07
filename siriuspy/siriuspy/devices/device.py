"""Epics Devices and Device Application."""

import time as _time

from ..epics import PV as _PV
from ..namesys import SiriusPVName as _SiriusPVName


class Device:
    """Epics Device."""

    _properties = ()

    def __init__(self, devname, properties):
        """."""
        self._properties = properties[:]
        self._devname, self._pvs = self._create_pvs(devname)

    @property
    def devname(self):
        """Return device name."""
        return self._devname

    @property
    def properties(self):
        """Return device properties."""
        return self._properties

    @property
    def pvnames(self):
        """Return device PV names."""
        pvnames = [pv.pvname for pv in self._pvs.values()]
        return pvnames

    @property
    def connected(self):
        """Return PVs connection status."""
        for pvobj in self._pvs.values():
            if not pvobj.connected:
                return False
        return True

    @property
    def disconnected_pvnames(self):
        """Return list of disconnected device PVs."""
        dlist = list()
        for pvname, pvobj in self._pvs.items():
            if not pvobj.connected:
                dlist.append(pvname)
        return dlist

    def update(self):
        """Update device properties."""
        for pvobj in self._pvs.values():
            pvobj.get()

    def pv_object(self, propty):
        """Return PV object for a given device property."""
        return self._pvs[propty]

    def pv_attribute_values(self, attribute):
        """Return property-value dict of a given attribute for all PVs."""
        attributes = dict()
        for propty in self._properties:
            pvobj = self._pvs[propty]
            attributes[propty] = getattr(pvobj, attribute)
        return attributes

    @property
    def hosts(self):
        """Return dict of IOC hosts providing device properties."""
        return self.pv_attribute_values('host')

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

    def _create_pvs(self, devname):
        if devname:
            devname = _SiriusPVName(devname)
        pvs = dict()
        for propty in self._properties:
            if devname:
                func = devname.substitute
                pvname = func(propty=propty)
            else:
                pvname = propty
            auto_monitor = not pvname.endswith('-Mon')
            pvs[propty] = _PV(pvname, auto_monitor=auto_monitor)
        return devname, pvs

    def _wait(self, propty, value, timeout=10):
        """."""
        interval = 0.050  # [s]
        ntrials = int(timeout/interval)
        _time.sleep(4*interval)
        for _ in range(ntrials):
            if self[propty] == value:
                break
            _time.sleep(interval)


# NOTE: This class is temporary. It should become deprecated once all
# devices names are in accordance with Sirius naming system
class DeviceNC(Device):
    """Non-compliant Devices.

    This device class is to be used for those devices whose
    names and PVs are not compliant to the Sirius naming system.
    """

    def _create_pvs(self, devname):
        pvs = dict()
        devname = '' if not self._devname else self._devname
        for propty in self._properties:
            pvname = devname + ':' + propty
            auto_monitor = not pvname.endswith('-Mon')
            pvs[propty] = _PV(pvname, auto_monitor=auto_monitor)
        return devname, pvs


class DeviceApp(Device):
    """Application Device.

    This kind of device groups properties of other devices.
    """

    def __init__(self, properties, devname=None):
        """."""
        self._devname_app = devname

        # call base class constructor
        super().__init__(None, properties=self._properties)

    @property
    def devname(self):
        """Return application device name."""
        return self._devname_app


class Devices:
    """."""

    def __init__(self, devname, devices):
        """."""
        self._devname = devname
        self._devices = devices

        self._properties = ()
        for dev in self._devices:
            self._properties += dev.properties

    @property
    def devname(self):
        """Return device name."""
        return self._devname

    @property
    def properties(self):
        """Return device properties."""
        return self._properties

    @property
    def pvnames(self):
        """Return device PV names."""
        pvnames = []
        for dev in self._devices:
            pvnames += dev.pvnames
        return pvnames

    @property
    def connected(self):
        """Return PVs connection status."""
        for dev in self._devices:
            if not dev.connected:
                return False
        return True

    @property
    def disconnected_pvnames(self):
        """Return list of disconnected device PVs."""
        dlist = list()
        for dev in self._devices:
            dlist += dev.disconnected_pvnames
        return dlist

    def update(self):
        """Update device properties."""
        for dev in self._devices:
            dev.update()

    @property
    def devices(self):
        """Return devices."""
        return self._devices

    def _prop_get(self, devidx, propty):
        """Return value of a device property."""
        return self._devices[devidx][propty]

    def _prop_set(self, devidx, propty, value):
        """Set value of device property."""
        self._devices[devidx][propty] = value

    def __getitem__(self, devidx):
        """Return device."""
        return self._devices[devidx]
