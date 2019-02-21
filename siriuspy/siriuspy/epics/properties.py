"""Epics PV derived classes."""

import time as _time
import epics as _epics


import numpy as _np
from siriuspy.envars import vaca_prefix as _prefix
from siriuspy.namesys.implementation import \
    SiriusPVName as _SiriusPVName, \
    get_pair_sprb as _get_pair_sprb


class EpicsProperty:
    """Pair of Epics PVs."""

    def __init__(self, name, prefix=_prefix, default_value=None,
                 connection_callback=None, callback=None):
        """Init."""
        try:
            self._name = _SiriusPVName(name)
            try:
                [self._pvname_sp, self._pvname_rb] = _get_pair_sprb(self._name)
            except TypeError:
                self._pvname_sp = name
                self._pvname_rb = name
        except Exception:
            self._name = name
            self._pvname_sp = name
            self._pvname_rb = name
        self._prefix = prefix
        self._default = default_value

        # Set callbacks
        self._connection_callback = connection_callback
        self._callback = callback
        callbacks = {'connection_callback': self._pv_connection_callback,
                     'callback': self._pv_callback}

        self._pv_sp = _epics.PV(self._prefix + self._pvname_sp, **callbacks)
        self._pv_rb = _epics.PV(self._prefix + self._pvname_rb, **callbacks)

    @property
    def name(self):
        """PV name."""
        return self._name

    @property
    def prefix(self):
        """PV prefix."""
        return self._prefix

    @property
    def suffix_sp(self):
        """PV SP suffix."""
        try:
            return self._pvname_sp.propty_suffix
        except Exception:
            return self._pvname_sp

    @property
    def suffix_rb(self):
        """PV RB suffix."""
        try:
            return self._pvname_rb.propty_suffix
        except Exception:
            return self._pvname_rb

    @property
    def pvname_sp(self):
        """Return SP pvname (without prefix)."""
        return self._pvname_sp

    @property
    def pvname_rb(self):
        """Return RB pvname (without prefix)."""
        return self._pvname_rb

    @property
    def connected(self):
        """State of connection."""
        return self._pv_sp.connected and self._pv_rb.connected

    @property
    def readback(self):
        """Property readback."""
        return self._pv_rb.get(timeout=0)

    @property
    def setpoint(self):
        """Property setpoint."""
        return self._pv_sp.get(timeout=0)

    @property
    def default(self):
        """Return default value."""
        return self._default

    @setpoint.setter
    def setpoint(self, value):
        """Set setpoint value."""
        if value is not None:
            self._pv_sp.value = value

    def set_setpoint_check(self, value, timeout):
        """Set setpoint value and check readback."""
        # setpoint
        self._pv_sp.value = value
        # check
        t0 = _time.time()
        while True:
            if self._pv_rb.value == value:
                return True
            if _time.time() - t0 > timeout:
                return False
            _time.sleep(min(0.1, timeout))

    def reset_default(self):
        """Reset to default value."""
        if self._default is not None:
            self.setpoint = self._default

    def set_callback(self, callback):
        """Set callback."""
        self._callback = callback

    def set_connection_callback(self, connection_callback):
        """Set connection callback."""
        self._connection_callback = connection_callback

    def _pv_connection_callback(self, **kwargs):
        if self._connection_callback is not None:
            kwargs['property'] = self
            self._connection_callback(**kwargs)

    def _pv_callback(self, **kwargs):
        if self._callback is not None:
            kwargs['property'] = self
            self._callback(**kwargs)


class EpicsPropertiesList:
    """List of Epics properties."""

    def __init__(self, properties):
        """Init."""
        self._properties = dict()
        for property in properties:
            self._properties[property.name] = property
        self._default = {p.name: p.default for p in self._properties.values()}

    @property
    def connected(self):
        """State of connection."""
        for property in self._properties.values():
            if not property.connected:
                return False
        return True

    @property
    def disconnected_properties(self):
        """Return list of disconnected properties."""
        props = []
        for name, property in self._properties.items():
            if not property.connected:
                props.append(name)
        return sorted(props)

    @property
    def properties(self):
        """Properties."""
        return sorted(self._properties.keys())

    @property
    def default(self):
        """Return default values dict."""
        return self._default

    @property
    def readbacks(self):
        """Return dict with all readbacks."""
        readbacks = dict()
        for name, property in self._properties.items():
            readbacks[name] = property.readback
        return readbacks

    def get_readback(self, name):
        """Return readback value of a property."""
        property = self._properties[name]
        return property.readback

    def get_setpoint(self, name):
        """Return setpoint value of a property."""
        property = self._properties[name]
        return property.setpoint

    def set_setpoints_check(self, setpoints, timeout, order=None):
        """Set setpoints of properties."""
        if order is None:
            order = list(setpoints.keys())
        # setpoints
        for name in order:
            value = setpoints[name]
            if value is not None:
                property = self._properties[name]
                property.setpoint = value
        # check
        t0 = _time.time()
        while True:
            finished = True
            for pvname, value in setpoints.items():
                property = self._properties[pvname]
                if value is None:
                    continue
                if isinstance(value, _np.ndarray):
                    if not all(property.readback == value):
                        finished = False
                        break
                else:
                    if not property.readback == value:
                        finished = False
                        break
            if finished or _time.time()-t0 > timeout:
                break
            _time.sleep(min(0.1, timeout))
        return finished

    def reset_default(self):
        """Reset properties to default values."""
        for property in self._properties.values():
            property.reset_default()

    def set_callback(self, callback):
        """Set callback."""
        for property in self._properties.values():
            property.set_callback(callback)

    def set_connection_callback(self, connection_callback):
        """Set connection callback."""
        for property in self._properties.values():
            property.set_connection_callback(connection_callback)

    def __getitem__(self, key):
        """Property item."""
        if isinstance(key, int):
            properties = self.properties
            key = properties[key]
        return self._properties[key]
