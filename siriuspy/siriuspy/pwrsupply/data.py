"""Power Supply Data."""

import copy as _copy


from ..search import PSSearch as _PSSearch

from .csdev import get_ps_propty_database as _get_ps_propty_database


class PSData:
    """PSData Class.

    Class objects that group power supply data.
    """

    def __init__(self, psname):
        """Init method."""
        if psname not in _PSSearch.get_psnames(filter_auxps=False):
            raise ValueError(psname + ' is not a valid power supply name.')
        self._psname = psname
        self._psmodel = _PSSearch.conv_psname_2_psmodel(self._psname)
        self._pstype = _PSSearch.conv_psname_2_pstype(self._psname)
        self._magfunc = _PSSearch.conv_pstype_2_magfunc(self._pstype)
        if self._magfunc != 'none':
            self._polarity = _PSSearch.conv_pstype_2_polarity(self._pstype)
            self._splims = _PSSearch.conv_pstype_2_splims(self._pstype)
            self._splims_unit = _PSSearch.get_splims_unit(self._psmodel)
            self._excdata = _PSSearch.conv_psname_2_excdata(self._psname)
        self._propty_database = \
            _get_ps_propty_database(self._psmodel, self._pstype)

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
        """Return unit of power supply setpoint limits."""
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

    def __str__(self):
        """__str__ method."""
        rst = ''
        rst += 'psname      : ' + str(self.psname)
        rst += '\n' + 'pstype      : ' + str(self.pstype)
        rst += '\n' + 'polarity    : ' + str(self.polarity)
        rst += '\n' + 'magfunc     : ' + str(self.magfunc)
        rst += '\n' + 'splims_unit : ' + str(self.splims_unit)

        if self.splims is None:
            rst += '\n' + 'splims      : ' + str(None)
        else:
            rst += '\n' + 'splims      : ' + \
                'DRVH:{0:+09.3f} DRVL:{1:+09.3f}'.format(
                    self.splims['DRVH'], self.splims['DRVL'])
            rst += '\n' + '              ' + \
                'HIHI:{0:+09.3f} LOLO:{1:+09.3f}'.format(
                    self.splims['HIHI'],    self.splims['LOLO'])
            rst += '\n' + '              ' + \
                'HIGH:{0:+09.3f} LOW :{1:+09.3f}'.format(
                    self.splims['HIGH'], self.splims['LOW'])
            rst += '\n' + '              ' + \
                'HOPR:{0:+09.3f} LOPR:{1:+09.3f}'.format(
                    self.splims['HOPR'], self.splims['LOPR'])

        return rst
