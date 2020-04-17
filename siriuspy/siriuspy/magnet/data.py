"""MA data class definition."""

from ..search import MASearch as _MASearch
from ..namesys import SiriusPVName as _SiriusPVName
from ..pwrsupply.data import PSData as _PSData


class MAData:
    """MAData Class.

    Class objects that group magnet data.
    """

    def __init__(self, maname):
        """Init method."""
        self._maname = _SiriusPVName(maname)
        psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self._psdata = {}
        for psname in psnames:
            self._psdata[psname] = _PSData(psname=psname)

    @property
    def maname(self):
        """Magnet name."""
        return self._maname

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
