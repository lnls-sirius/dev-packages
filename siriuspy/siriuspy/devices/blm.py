"""Beam Loss Monitor devices."""

import numpy as _np

from ..search import BLMSearch as _BLMSearch
from ..util import ClassProperty as _classproperty
from .device import Device as _Device, DeviceSet as _DeviceSet


class BLM(_Device):
    """Beam Loss Monitor Device."""

    class DEVICES:
        """Devices names."""

        __SENSOR1 = __SENSOR2 = __SENSOR3 = __SENSOR4 = None
        __SENSOR5 = __SENSOR6 = __SENSOR7 = __SENSOR8 = None

        @_classproperty
        def SENSOR1(cls):  # noqa: N802, N805
            """."""
            if cls.__SENSOR1 is None:
                cls.__SENSOR1 = _BLMSearch.conv_blmname_2_devname('SENSOR1')
            return cls.__SENSOR1

        @_classproperty
        def SENSOR2(cls):  # noqa: N802, N805
            """."""
            if cls.__SENSOR2 is None:
                cls.__SENSOR2 = _BLMSearch.conv_blmname_2_devname('SENSOR2')
            return cls.__SENSOR2

        @_classproperty
        def SENSOR3(cls):  # noqa: N802, N805
            """."""
            if cls.__SENSOR3 is None:
                cls.__SENSOR3 = _BLMSearch.conv_blmname_2_devname('SENSOR3')
            return cls.__SENSOR3

        @_classproperty
        def SENSOR4(cls):  # noqa: N802, N805
            """."""
            if cls.__SENSOR4 is None:
                cls.__SENSOR4 = _BLMSearch.conv_blmname_2_devname('SENSOR4')
            return cls.__SENSOR4

        @_classproperty
        def SENSOR5(cls):  # noqa: N802, N805
            """."""
            if cls.__SENSOR5 is None:
                cls.__SENSOR5 = _BLMSearch.conv_blmname_2_devname('SENSOR5')
            return cls.__SENSOR5

        @_classproperty
        def SENSOR6(cls):  # noqa: N802, N805
            """."""
            if cls.__SENSOR6 is None:
                cls.__SENSOR6 = _BLMSearch.conv_blmname_2_devname('SENSOR6')
            return cls.__SENSOR6

        @_classproperty
        def SENSOR7(cls):  # noqa: N802, N805
            """."""
            if cls.__SENSOR7 is None:
                cls.__SENSOR7 = _BLMSearch.conv_blmname_2_devname('SENSOR7')
            return cls.__SENSOR7

        @_classproperty
        def SENSOR8(cls):  # noqa: N802, N805
            """."""
            if cls.__SENSOR8 is None:
                cls.__SENSOR8 = _BLMSearch.conv_blmname_2_devname('SENSOR8')
            return cls.__SENSOR8

        @_classproperty
        def ALL(cls):  # noqa: N802, N805
            """."""
            return (
                cls.SENSOR1,
                cls.SENSOR2,
                cls.SENSOR3,
                cls.SENSOR4,
                cls.SENSOR5,
                cls.SENSOR6,
                cls.SENSOR7,
                cls.SENSOR8,
            )

    PROPERTIES_DEFAULT = ('Count-Mon',)

    def __init__(self, devname, props2init='all'):
        """."""
        if devname not in BLM.DEVICES.ALL:
            raise NotImplementedError(devname)
        self._blmname = _BLMSearch.conv_devname_2_blmname(devname)
        super().__init__(devname, props2init=props2init)

    @property
    def blmname(self):
        """Return BLM tag name."""
        return self._blmname

    @property
    def counts(self):
        """Return BLM count value [pulse/s]."""
        return self['Count-Mon']

    @property
    def secsub(self):
        """Return sector-subsector where BLM is located."""
        return _BLMSearch.conv_blmname_2_secsub(self.blmname)

    @property
    def position(self):
        """Return installation position of the BLM."""
        return _BLMSearch.conv_blmname_2_position(self.blmname)

    @property
    def channel(self):
        """Return counter channel of BLM."""
        return _BLMSearch.conv_blmname_2_counter_channel(self.blmname)


class FamBLMs(_DeviceSet):
    """Beam Loss Monitor Device Set."""

    def __init__(self, props2init='all'):
        """."""
        super().__init__([
            BLM(devname, props2init=props2init) for devname in BLM.DEVICES.ALL
        ])

    @property
    def blmnames(self):
        """Return list of BLM tag names."""
        return [dev.blmname for dev in self]

    @property
    def secsubs(self):
        """Return list of sector-subsector where BLMs are located."""
        return [dev.secsub for dev in self]

    @property
    def positions(self):
        """Return list of installation positions of the BLMs."""
        return [dev.position for dev in self]

    @property
    def channels(self):
        """Return list of counter channels of the BLMs."""
        return [dev.channel for dev in self]

    @property
    def counts(self):
        """Return list of BLM count values [pulse/s]."""
        return _np.array([dev.counts for dev in self])
