"""Beam Loss Monitor devices."""

from ..search import BLMSearch as _BLMSearch
from .device import Device as _Device


class BLM(_Device):
    """Beam Loss Monitor Device."""

    class DEVICES:
        """Devices names."""
        SENSOR1 = _BLMSearch.conv_blmname_2_sensor_devname('SENSOR1')
        SENSOR2 = _BLMSearch.conv_blmname_2_sensor_devname('SENSOR2')
        SENSOR3 = _BLMSearch.conv_blmname_2_sensor_devname('SENSOR3')
        SENSOR4 = _BLMSearch.conv_blmname_2_sensor_devname('SENSOR4')
        SENSOR5 = _BLMSearch.conv_blmname_2_sensor_devname('SENSOR5')
        SENSOR6 = _BLMSearch.conv_blmname_2_sensor_devname('SENSOR6')
        SENSOR7 = _BLMSearch.conv_blmname_2_sensor_devname('SENSOR7')
        SENSOR8 = _BLMSearch.conv_blmname_2_sensor_devname('SENSOR8')
        ALL = (
            SENSOR1, SENSOR2, SENSOR3, SENSOR4,
            SENSOR5, SENSOR6, SENSOR7, SENSOR8)

    PROPERTIES_DEFAULT = (
        'Count-Mon')

    def __init__(self, devname, props2init='all'):
        """."""
        if devname not in BLM.DEVICES.ALL:
            raise NotImplementedError(devname)

        super().__init__(self, devname, props2init=props2init)
