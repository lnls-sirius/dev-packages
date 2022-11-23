"""Epics Devices and Device Application."""

import time as _time
import operator as _opr

from epics.ca import ChannelAccessGetFailure as _ChannelAccessGetFailure, \
    CASeverityException as _CASeverityException
import numpy as _np

from ..envars import VACA_PREFIX as _VACA_PREFIX
from ..epics import PV as _PV, CONNECTION_TIMEOUT as _CONN_TIMEOUT, \
    GET_TIMEOUT as _GET_TIMEOUT
from ..simul import SimPV as _PVSim
from ..simul import Simulation as _Simulation
from ..namesys import SiriusPVName as _SiriusPVName

_DEF_TIMEOUT = 10  # s
_TINY_INTERVAL = 0.050  # s


class Device:
    """Epics Device."""

    CONNECTION_TIMEOUT = _CONN_TIMEOUT
    GET_TIMEOUT = _GET_TIMEOUT
    _properties = ()

    def __init__(self, devname, properties, auto_mon=False):
        """."""
        self._properties = properties[:]
        self._auto_mon = auto_mon
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
    def simulators(self):
        """Return simulator."""
        sims = set()
        for pvname in self.pvnames:
            sims.update(_Simulation.simulator_find(pvname))
        return sims

    @property
    def pvnames(self):
        """Return device PV names."""
        pvnames = {pv.pvname for pv in self._pvs.values()}
        return pvnames

    @property
    def connected(self):
        """Return PVs connection status."""
        for pvobj in self._pvs.values():
            if not pvobj.connected:
                return False
        return True

    @property
    def auto_monitor_status(self):
        """Return PVs auto_monitor statuses."""
        return {pvn: pv.auto_monitor for pvn, pv in self._pvs.items()}

    @property
    def disconnected_pvnames(self):
        """Return list of disconnected device PVs."""
        set_ = set()
        for pvobj in self._pvs.values():
            if not pvobj.connected:
                set_.add(pvobj.pvname)
        return set_

    def set_auto_monitor(self, pvname, value):
        """Set auto_monitor state of individual PVs."""
        if pvname not in self._pvs:
            return False
        self._pvs[pvname].auto_monitor = int(value)
        return True

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
            attributes[pvobj.pvname] = getattr(pvobj, attribute)
        return attributes

    @property
    def hosts(self):
        """Return dict of IOC hosts providing device properties."""
        return self.pv_attribute_values('host')

    @property
    def values(self):
        """Return dict of property values."""
        return self.pv_attribute_values('value')

    def wait_for_connection(self, timeout=None):
        """Wait for connection."""
        for pvobj in self._pvs.values():
            res = pvobj.wait_for_connection(timeout)
            if not res:
                return False
        return True

    def __getitem__(self, propty):
        """Return value of property."""
        pvobj = self._pvs[propty]
        try:
            value = pvobj.get(timeout=Device.GET_TIMEOUT)
        except (_ChannelAccessGetFailure, _CASeverityException):
            # exceptions raised in a Virtual Circuit Disconnect (192)
            # event. If the PV IOC goes down, for example.
            print('Could not get value of {}'.format(pvobj.pvname))
            value = None
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
            pvname = self._get_pvname(devname, propty)
            auto_monitor = self._auto_mon or not pvname.endswith('-Mon')
            in_sim = _Simulation.pv_check(pvname)
            pvclass = _PVSim if in_sim else _PV
            pvs[propty] = pvclass(
                pvname, auto_monitor=auto_monitor,
                connection_timeout=Device.CONNECTION_TIMEOUT)
        return devname, pvs

    def _wait(self, propty, value, timeout=_DEF_TIMEOUT, comp='eq'):
        """."""
        def comp_(val):
            boo = comp(self[propty], val)
            if isinstance(boo, _np.ndarray):
                boo = _np.all(boo)
            return boo

        if isinstance(comp, str):
            comp = getattr(_opr, comp)

        if comp_(value):
            return True

        ntrials = int(timeout/_TINY_INTERVAL)
        for _ in range(ntrials):
            _time.sleep(_TINY_INTERVAL)
            if comp_(value):
                return True
        return False

    def _get_pvname(self, devname, propty):
        if devname:
            func = devname.substitute
            pvname = func(prefix=_VACA_PREFIX, propty=propty)
        else:
            pvname = _VACA_PREFIX + ('-' if _VACA_PREFIX else '') + propty
        return pvname

    def _enum_setter(self, propty, value, enums):
        if hasattr(enums, '_fields'):
            enums = enums._fields
        if value is None:
            return None
        elif isinstance(value, str) and value in enums:
            self[propty] = enums.index(value)
        elif 0 <= int(value) < len(enums):
            self[propty] = value


class ProptyDevice(Device):
    """Device with a prefix property name."""

    def __init__(self, devname, propty_prefix, properties):
        """."""
        self._propty_prefix = propty_prefix
        # call base class constructor
        super().__init__(devname, properties=properties)

    def _get_pvname(self, devname, propty):
        if devname:
            func = devname.substitute
            pvname = func(propty=self._propty_prefix + propty)
        else:
            pvname = self._propty_prefix + propty
        return pvname


# NOTE: This class is temporary. It should become deprecated once all
# devices names are in accordance with Sirius naming system
class DeviceNC(Device):
    """Non-compliant Devices.

    This device class is to be used for those devices whose
    names and PVs are not compliant to the Sirius naming system.
    """
    DEVSEP = ':'

    def _create_pvs(self, devname):
        pvs = dict()
        devname = devname or ''
        for propty in self._properties:
            pvname = devname + self.DEVSEP + propty
            auto_monitor = not pvname.endswith('-Mon')
            pvs[propty] = _PV(pvname, auto_monitor=auto_monitor)
        return devname, pvs


class DeviceApp(Device):
    """Application Device.

    This kind of device groups properties of other devices.
    """

    def __init__(self, properties, devname=None, auto_mon=False):
        """."""
        self._devname_app = devname

        # call base class constructor
        super().__init__(None, properties=properties, auto_mon=auto_mon)

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

        self._properties = []
        for dev in self._devices:
            if dev is not None:
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
    def simulators(self):
        """Return list of simulators."""
        sims = set()
        for dev in self._devices:
            sims.update(dev.simulators)
        return sims

    @property
    def pvnames(self):
        """Return device PV names."""
        set_ = set()
        for dev in self._devices:
            set_.update(dev.pvnames)
        return set_

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
        set_ = set()
        for dev in self._devices:
            set_.update(dev.disconnected_pvnames)
        return set_

    @property
    def auto_monitor_status(self):
        """Return PVs auto_monitor statuses."""
        dic_ = dict()
        for dev in self._devices:
            dic_.update(dev.auto_monitor_status)
        return dic_

    def update(self):
        """Update device properties."""
        for dev in self._devices:
            dev.update()

    def pv_attribute_values(self, attribute):
        """Return property-value dict of a given attribute for all PVs."""
        attributes = dict()
        for dev in self._devices:
            attrs = dev.pv_attribute_values(attribute)
            attributes.update(attrs)
        return attributes

    @property
    def hosts(self):
        """Return dict of IOC hosts providing device properties."""
        return self.pv_attribute_values('host')

    @property
    def values(self):
        """Return dict of property values."""
        return self.pv_attribute_values('value')

    def wait_for_connection(self, timeout=None):
        """Wait for connection."""
        for dev in self._devices:
            if not dev.wait_for_connection(timeout=timeout):
                return False
        return True

    @property
    def devices(self):
        """Return devices."""
        return self._devices

    # --- private methods ---

    def _set_devices_propty(self, devices, propty, values, wait=0):
        """Set devices property to value(s)."""
        dev2val = self._get_dev_2_val(devices, values)
        for dev, val in dev2val.items():
            if dev.pv_object(propty).wait_for_connection():
                dev[propty] = val
                _time.sleep(wait)

    def _wait_devices_propty(
            self, devices, propty, values, comp='eq',
            timeout=_DEF_TIMEOUT, return_prob=False):
        """Wait for devices property to reach value(s)."""
        if isinstance(comp, str):
            comp = getattr(_opr, comp)
        dev2val = self._get_dev_2_val(devices, values)

        for _ in range(int(timeout/_TINY_INTERVAL)):
            okdevs = set()
            for k, v in dev2val.items():
                boo = comp(k[propty], v)
                if isinstance(boo, _np.ndarray):
                    boo = _np.all(boo)
                if boo:
                    okdevs.add(k)
            list(map(dev2val.__delitem__, okdevs))
            if not dev2val:
                break
            _time.sleep(_TINY_INTERVAL)

        allok = not dev2val
        if return_prob:
            return allok, [dev.devname+':'+propty for dev in dev2val]
        return allok

    def _get_dev_2_val(self, devices, values):
        """Get devices to values dict."""
        # always use an iterable object
        if not isinstance(devices, (tuple, list)):
            devices = [devices, ]
        # if 'values' is not iterable, consider the same value for all devices
        if not isinstance(values, (tuple, list)):
            values = len(devices)*[values]
        return {k: v for k, v in zip(devices, values)}

    def __getitem__(self, devidx):
        """Return device."""
        return self._devices[devidx]
