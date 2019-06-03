"""MA data class definition."""
from siriuspy.search import MASearch as _MASearch
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.csdevice.pwrsupply \
    import get_ma_propty_database as _get_ma_propty_database
from siriuspy.csdevice.pwrsupply \
    import get_pm_propty_database as _get_pm_propty_database
from siriuspy.csdevice.pwrsupply \
    import get_li_ma_propty_database as _get_li_ma_propty_database


class MAData:
    """MAData Class.

    Class objects that group magnet data.
    """

    def __init__(self, maname):
        """Init method."""
        self._maname = _SiriusPVName(maname)
        self._splims = _MASearch.conv_maname_2_splims(self._maname)
        psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self._psdata = {}
        for psname in psnames:
            self._psdata[psname] = _PSData(psname=psname)
        psmodel = self._psdata[psnames[0]].psmodel
        self._splims_unit = \
            _MASearch.get_splims_unit(psmodel=psmodel)
        # TODO: cleanup code
        if 'PM-' in maname:
            self._propty_databases = _get_pm_propty_database(self._maname)
        elif self._maname.sec == 'LI':
            self._propty_databases = _get_li_ma_propty_database(self._maname)
        else:
            self._propty_databases = _get_ma_propty_database(self._maname)

    @property
    def maname(self):
        """Magnet name."""
        return self._maname

    @property
    def splims_unit(self):
        """Return unit of setpoint limits."""
        return self._splims_unit

    @property
    def splims(self):
        """Setpoint limits dictinary."""
        if self._splims is None:
            return None
        else:
            return self._splims.copy()

    @property
    def psnames(self):
        """List of power supply names that excite the magnet."""
        return list(self._psdata.keys())

    def magfunc(self, psname):
        """Return magnet function."""
        return self._psdata[psname].magfunc

    def excdata(self, psname):
        """Return excitation data for a power supply."""
        return self._psdata[psname].excdata

    def __getitem__(self, psname):
        """Get item."""
        return self._psdata[psname]

    def get_database(self, psname):
        """Get database."""
        return self._propty_databases[psname]
