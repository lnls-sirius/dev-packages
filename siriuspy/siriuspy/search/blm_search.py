"""BLM Search module."""

from ..namesys import Filter as _Filter
from ..namesys import SiriusPVName as _SiriusPVName


class BLMSearch:
    """Beam Loss Monitor Search Class."""

    _blmname2data = {
        'SENSOR1': ('SI-09C3', 'BOTTOM', 'Ch7'),
        'SENSOR2': ('SI-09C3', 'TOP', 'Ch8'),
        'SENSOR3': ('SI-10M1', 'RIGHT', 'Ch7'),
        'SENSOR4': ('SI-10M1', 'LEFT', 'Ch8'),
        'SENSOR5': ('SI-18C3', 'BOTTOM', 'Ch7'),
        'SENSOR6': ('SI-18C3', 'TOP', 'Ch8'),
        'SENSOR7': ('SI-19M1', 'RIGHT', 'Ch7'),
        'SENSOR8': ('SI-19M1', 'LEFT', 'Ch8'),
    }

    @staticmethod
    def get_blmnames(filters=None):
        """Return a sorted and filtered list of all BLM names."""
        blmnames_list = list(BLMSearch._blmname2data.keys())
        blmnames = _Filter.process_filters(blmnames_list, filters=filters)
        return sorted(blmnames)

    @staticmethod
    def conv_blmname_2_secsub(blmname):
        """Return the sector-subsector where BLM is located."""
        sec = BLMSearch._blmname2data[blmname][0]
        return sec
    
    @staticmethod
    def conv_blmname_2_position(blmname):
        """Return the position of the BLM with sector."""
        pos = BLMSearch._blmname2data[blmname][1]
        return pos
    
    @staticmethod
    def conv_blmname_2_counter_channel(blmname):
        """Return the counter channel of a BLM."""
        chn = BLMSearch._blmname2locs[blmname][2]
        return chn

    @staticmethod
    def conv_blmname_2_sensor_devname(blmname):
        """Return device name of a BLM."""
        sec, _, chn = BLMSearch._blmname2data[blmname]
        devname = _SiriusPVName(sec + ':' + 'CO-Counter-' + chn)
        return devname
    
    @staticmethod
    def conv_blmname_2_sensor_pvname(blmname):
        """Return PV name of a BLM."""
        devname = BLMSearch.conv_blmname_2_sensor_devname(blmname)
        pvname = devname.substitute(propty='Count-Mon')
        return pvname
    
    @staticmethod
    def conv_blmname_2_timebase_pvname(blmname):
        """Return time base PV name of a BLM."""
        devname = BLMSearch.conv_blmname_2_sensor_devname(blmname)
        pvname = devname.substitute(idx='', propty='TimeBase-SP')
        return pvname
