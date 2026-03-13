"""Beam Loss Monitor devices."""

import numbers as _numbers

import numpy as _np

from ..search import GammaMonitorSearch as _GammaMonitorSearch
from ..util import ClassProperty as _classproperty
from .device import Device as _Device, DeviceSet as _DeviceSet


class GammaMonitor(_Device):
    """Gamma Monitor Device."""

    class DEVICES:
        """Devices names."""
        __NAMES = None

        @_classproperty
        def ALL(cls):  # noqa: N802, N805
            """."""
            if cls.__NAMES is None:
                cls.__NAMES = _GammaMonitorSearch.get_gammanames()
            return cls.__NAMES

    PROPERTIES_DEFAULT = ('Count-Mon',)

    def __init__(self, devname, props2init='all'):
        """."""
        if devname not in GammaMonitor.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def counts(self):
        """Return Gamma Monitor count value [pulse/s]."""
        return self['Count-Mon']


class GammaCounter(_Device):
    """Gamma Monitor Counter Device."""

    class DEVICES:
        """Devices names."""
        __NAMES = None

        @_classproperty
        def ALL(cls):  # noqa: N802, N805
            """."""
            if cls.__NAMES is None:
                cls.__NAMES = _GammaMonitorSearch.get_counter_names()
            return cls.__NAMES

    PROPERTIES_DEFAULT = ('TimeBase-SP',)

    def __init__(self, devname, props2init='all'):
        """."""
        if devname not in GammaCounter.DEVICES.ALL:
            raise NotImplementedError(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def time_base(self):
        """Return Gamma Monitor Counter time base value."""
        return self['TimeBase-SP']

    @time_base.setter
    def time_base(self, value):
        """Set Gamma Monitor Counter time base value."""
        self['TimeBase-SP'] = int(value)


class FamGammaMonitors(_DeviceSet):
    """Gamma Monitor Device Set."""

    def __init__(self, props2init='all'):
        """."""
        self.monitors = [
            GammaMonitor(devname, props2init=props2init)
            for devname in GammaMonitor.DEVICES.ALL
        ]
        self.counters = [
            GammaCounter(devname, props2init=props2init)
            for devname in GammaCounter.DEVICES.ALL
        ]
        super().__init__(self.monitors + self.counters)

    @property
    def counts(self):
        """Return list of Gamma Monitor count values [pulse/s]."""
        return _np.array([dev.counts for dev in self.monitors])

    @property
    def time_bases(self):
        """Return list of Gamma Monitor Counter time base values."""
        return _np.array([counter.time_base for counter in self.counters])

    @time_bases.setter
    def time_bases(self, value):
        """Set list of Gamma Monitor Counter time base values."""
        if isinstance(value, _numbers.Number):
            value = [value] * len(self.counters)
        if not isinstance(value, (_np.ndarray, list, tuple)):
            raise ValueError(
                'Value must be a number, list, tuple or numpy array.'
            )
        if len(value) != len(self.counters):
            raise ValueError(
                f'Value must have the same length as the number of counters '
                f'({len(self.counters)}).'
            )
        for counter, time_base in zip(self.counters, value):
            counter.time_base = time_base

    @property
    def monitor_names(self):
        """Return list of Gamma Monitor names."""
        return [dev.devname for dev in self.monitors]

    @property
    def counter_names(self):
        """Return list of Gamma Monitor Counter names."""
        return [dev.devname for dev in self.counters]
