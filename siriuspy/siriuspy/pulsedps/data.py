"""Defines data class for pulsed power supplies."""
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.csdevice.pwrsupply \
    import get_pu_propty_database as _get_pu_propty_database


class PUData(_PSData):
    """Pulsed data class, inherits methods from PSData."""

    def __init__(self, psname):
        """Override PSData constructor."""
        self._psname = psname
        self._pstype = _PSSearch.conv_psname_2_pstype(self._psname)
        self._polarity = _PSSearch.conv_pstype_2_polarity(self._pstype)
        self._magfunc = _PSSearch.conv_pstype_2_magfunc(self._pstype)
        self._splims = _PSSearch.conv_pstype_2_splims(self._pstype)
        self._splims_unit = _PSSearch.get_splims_unit()[1]
        self._excdata = _PSSearch.conv_psname_2_excdata(self._psname)
        self._propty_database = _get_pu_propty_database(self._pstype)
