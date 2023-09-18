"""Beam Loss Monitor devices."""

from ..util import ClassProperty as _classproperty
from ..search import BLMSearch as _BLMSearch
from .device import Device as _Device


class BLM(_Device):
    """Beam Loss Monitor Device."""

    class DEVICES:
        """Devices names."""
        __SENSOR1 = __SENSOR2 = __SENSOR3 = __SENSOR4 = None
        __SENSOR5 = __SENSOR6 = __SENSOR7 = __SENSOR8 = None

        @_classproperty
        def SENSOR1(cls):
            """."""
            if cls.__SENSOR1 is None:
                cls.__SENSOR1 = _BLMSearch.conv_blmname_2_devname('SENSOR1')
            return cls.__SENSOR1

        @_classproperty
        def SENSOR2(cls):
            """."""
            if cls.__SENSOR2 is None:
                cls.__SENSOR2 = _BLMSearch.conv_blmname_2_devname('SENSOR2')
            return cls.__SENSOR2

        @_classproperty
        def SENSOR3(cls):
            """."""
            if cls.__SENSOR3 is None:
                cls.__SENSOR3 = _BLMSearch.conv_blmname_2_devname('SENSOR3')
            return cls.__SENSOR3

        @_classproperty
        def SENSOR4(cls):
            """."""
            if cls.__SENSOR4 is None:
                cls.__SENSOR4 = _BLMSearch.conv_blmname_2_devname('SENSOR4')
            return cls.__SENSOR4

        @_classproperty
        def SENSOR5(cls):
            """."""
            if cls.__SENSOR5 is None:
                cls.__SENSOR5 = _BLMSearch.conv_blmname_2_devname('SENSOR5')
            return cls.__SENSOR5

        @_classproperty
        def SENSOR6(cls):
            """."""
            if cls.__SENSOR6 is None:
                cls.__SENSOR6 = _BLMSearch.conv_blmname_2_devname('SENSOR6')
            return cls.__SENSOR6

        @_classproperty
        def SENSOR7(cls):
            """."""
            if cls.__SENSOR7 is None:
                cls.__SENSOR7 = _BLMSearch.conv_blmname_2_devname('SENSOR7')
            return cls.__SENSOR7

        @_classproperty
        def SENSOR8(cls):
            """."""
            if cls.__SENSOR8 is None:
                cls.__SENSOR8 = _BLMSearch.conv_blmname_2_devname('SENSOR8')
            return cls.__SENSOR8

        @_classproperty
        def ALL(cls):
            return (
                cls.SENSOR1, cls.SENSOR2, cls.SENSOR3, cls.SENSOR4,
                cls.SENSOR5, cls.SENSOR6, cls.SENSOR7, cls.SENSOR8)

    PROPERTIES_DEFAULT = (
        'Count-Mon', )

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
    def count_mon(self):
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
