"""Pulsed magnet data class definition."""
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.csdevice.pwrsupply \
    import get_pm_propty_database as _get_pm_propty_database
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.search import MASearch as _MASearch
from siriuspy.pulsedps.data import PUData as _PUData


class PMData(_MAData):
    """Pulsed magnet data class."""

    def __init__(self, maname):
        """Class constructor."""
        self._maname = _SiriusPVName(maname)
        self._splims_unit = _MASearch.get_splims_unit()[1]
        self._psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self._psdata = {}
        for psname in self._psnames:
            self._psdata[psname] = _PUData(psname=psname)
        self._propty_databases = \
            _get_pm_propty_database(self._maname, self._psdata)
