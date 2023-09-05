"""Beam Loss Monitor devices."""

from ..search import BLMSearch as _BLMSearch
from .device import Device as _Device


class BLM(_Device):
    """Beam Loss Monitor Device."""

    class DEVICES:
        """Devices names."""
        SENSOR1 = _BLMSearch.conv_blmname_2_devname('SENSOR1')
        SENSOR2 = _BLMSearch.conv_blmname_2_devname('SENSOR2')
        SENSOR3 = _BLMSearch.conv_blmname_2_devname('SENSOR3')
        SENSOR4 = _BLMSearch.conv_blmname_2_devname('SENSOR4')
        SENSOR5 = _BLMSearch.conv_blmname_2_devname('SENSOR5')
        SENSOR6 = _BLMSearch.conv_blmname_2_devname('SENSOR6')
        SENSOR7 = _BLMSearch.conv_blmname_2_devname('SENSOR7')
        SENSOR8 = _BLMSearch.conv_blmname_2_devname('SENSOR8')
        ALL = (
            SENSOR1, SENSOR2, SENSOR3, SENSOR4,
            SENSOR5, SENSOR6, SENSOR7, SENSOR8)

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
