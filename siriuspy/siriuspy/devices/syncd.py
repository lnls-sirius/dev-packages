"""Synchronized Devices."""

from ..namesys import SiriusPVName as _SiriusPVName
from .device import Device as _Device


class DevicesSync(_Device):
    """Synchronized devices."""

    def __init__(
            self, devnames, propty_sync, propty_async=None,
            devname=None, auto_monitor_mon=False):
        """."""
        self._devnames = [_SiriusPVName(dev) for dev in devnames]
        self._props_sync = list(propty_sync)
        self._props_async = [] if propty_async is None else propty_async

        # get properties
        properties, self._prop2prop = self._get_properties()

        # call base class constructor
        super().__init__(
            devname, auto_monitor_mon=auto_monitor_mon, props2init=properties)

    @property
    def devnames(self):
        """Return device names."""
        return self._devnames

    @property
    def properties_sync(self):
        """Return sync properties."""
        return self._props_sync

    @property
    def properties_async(self):
        """Return async properties."""
        return self._props_async

    @property
    def synchronized(self):
        """Return True if devices are synchronized."""
        for devprop in self._props_sync:
            props = self._prop2prop[devprop]
            values = {self[prop] for prop in props}
            if len(values) > 1:
                return False
        return True

    def get_value(self, propty):
        """Return property value."""
        if not self.connected:
            return
        props = self._prop2prop[propty]
        values = [self[prop] for prop in props]
        if None in values:
            # NOTE: None values sometimes are being returned
            # even after connected check!
            # This is happening with 'TS-01:PU-EjeSeptG:Voltage-Mon'
            # of sirius-ioc-as-pu-conv, in particular.
            return
        return sum(values) / len(values)

    def set_value(self, propty, value):
        """Set property."""
        if not self.connected:
            return
        props = self._prop2prop[propty]
        for prop in props:
            self[prop] = value

    def _get_properties(self):
        properties = list()
        prop2prop = dict()
        for devname in self._devnames:
            for propty in self._props_sync + self._props_async:
                pvname = devname.substitute(propty=devname.propty_name+propty)
                if propty not in prop2prop:
                    prop2prop[propty] = [pvname]
                else:
                    prop2prop[propty].append(pvname)
                properties.append(pvname)
        return properties, prop2prop
