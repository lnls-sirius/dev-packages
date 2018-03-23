"""PS Data module."""

import copy as _copy
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import get_ps_propty_database as \
    _get_ps_propty_database
from siriuspy.csdevice.pwrsupply import get_pu_propty_database as \
    _get_pu_propty_database


class PSData:
    """MAData Class.

    Class objects that group power supply data.
    """

    def __init__(self, psname):
        """Init method."""
        if psname not in _PSSearch.get_psnames():
            raise ValueError(psname + ' is not a valid power supply name.')
        self._psname = psname
        self._pstype = _PSSearch.conv_psname_2_pstype(self._psname)
        self._psmodel = _PSSearch.conv_psname_2_psmodel(self._psname)
        self._ispulsed = _PSSearch.check_psname_ispulsed(self._psname)
        self._polarity = _PSSearch.conv_pstype_2_polarity(self._pstype)
        self._magfunc = _PSSearch.conv_pstype_2_magfunc(self._pstype)
        self._splims = _PSSearch.conv_pstype_2_splims(self._pstype)
        self._splims_unit = _PSSearch.get_splims_unit(self._ispulsed)
        self._excdata = _PSSearch.conv_psname_2_excdata(self._psname)
        self._bbbname = _PSSearch.conv_psname_2_bbbname(self._psname)
        if self._ispulsed:
            self._propty_database = _get_pu_propty_database(self._pstype)
        else:
            # self._propty_database = _get_ps_propty_database(self._pstype)
            if self._psmodel == 'FBP':
                self._propty_database = _get_ps_propty_database(self._pstype)
            else:
                raise ValueError(
                    'DB for psmodel {} not implemented!'.format(self._psmodel))

    @property
    def psname(self):
        """Power supply name."""
        return self._psname

    @property
    def pstype(self):
        """Power supply type."""
        return self._pstype

    @property
    def psmodel(self):
        """Power supply model."""
        return self._psmodel

    @property
    def polarity(self):
        """Power supply polarity.

        It can be either 'monopolar' or 'bipolar'.
        """
        return self._polarity

    @property
    def magfunc(self):
        """Magnetic function the power supply excites."""
        return self._magfunc

    @property
    def splims(self):
        """Setpoint limits of power supply."""
        if self._splims is None:
            return None
        else:
            return self._splims.copy()

    @property
    def splims_unit(self):
        """Unit of power supply setpoint limits."""
        return self._splims_unit

    @property
    def splims_labels(self):
        """EPICS labels of power supply setpoint limits."""
        return sorted(self._splims.keys())

    @property
    def propty_database(self):
        """Power supply properties database."""
        return _copy.deepcopy(self._propty_database)

    @property
    def excdata(self):
        """Excitation data associated with the power supply."""
        return self._excdata

    @property
    def bbbname(self):
        """Name of the BBB that controls this power supply."""
        return self._bbbname

    def __str__(self):
        """__str__ method."""
        st = ''
        st += 'psname      : ' + str(self.psname)
        st += '\n' + 'pstype      : ' + str(self.pstype)
        st += '\n' + 'polarity    : ' + str(self.polarity)
        st += '\n' + 'magfunc     : ' + str(self.magfunc)
        st += '\n' + 'splims_unit : ' + str(self.splims_unit)

        if self.splims is None:
            st += '\n' + 'splims      : ' + str(None)
        else:
            st += '\n' + 'splims      : ' + \
                'DRVH:{0:+09.3f} DRVL:{1:+09.3f}'.format(
                    self.splims['DRVH'], self.splims['DRVL'])
            st += '\n' + '              ' + \
                'HIHI:{0:+09.3f} LOLO:{1:+09.3f}'.format(
                    self.splims['HIHI'],    self.splims['LOLO'])
            st += '\n' + '              ' + \
                'HIGH:{0:+09.3f} LOW :{1:+09.3f}'.format(
                    self.splims['HIGH'], self.splims['LOW'])
            st += '\n' + '              ' + \
                'HOPR:{0:+09.3f} LOPR:{1:+09.3f}'.format(
                    self.splims['HOPR'], self.splims['LOPR'])

        return st
