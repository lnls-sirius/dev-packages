
import copy as _copy
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import get_ps_propty_database as _get_ps_propty_database


class PSData:

    # really necessary ?
    _multipole_dict = {
        'dipole': ('normal', 0),
        'quadrupole': ('normal', 1),
        'sextupole': ('normal', 2),
        'corrector-horizontal': ('normal', 0),
        'corrector-vertical': ('skew', 0),
        'quadrupole-skew': ('skew', 1),
    }

    def __init__(self, psname):
        self._psname = psname
        self._pstype = _PSSearch.conv_psname_2_pstype(self._psname)
        self._polarity = _PSSearch.conv_pstype_2_polarity(self._pstype)
        self._magfunc = _PSSearch.conv_pstype_2_magfunc(self._pstype)
        self._splims = _PSSearch.conv_pstype_2_splims(self._pstype)
        self._splims_unit = _PSSearch.get_splims_unit()
        self._excdata = _PSSearch.conv_psname_2_excdata(self._psname)
        self._propty_database = _get_ps_propty_database(self._pstype)

    @property
    def psname(self):
        return self._psname

    @property
    def pstype(self):
        return self._pstype

    @property
    def polarity(self):
        return self._polarity

    @property
    def magfunc(self):
        return self._magfunc

    def multipole_main(self, current, left='linear', right='linear'):
        m_harm = self._excdata.main_multipole_harmonic
        m_type = self._excdata.main_multipole_type
        m = self._excdata.interp_curr2mult(self, current, left=left, right=right)
        return m[m_type][m_harm]

    def multipole_main(self, current, left='linear', right='linear'):
        return self._excdata.interp_curr2mult(self, current, left=left, right=right)

    @property
    def splims(self):
        if self._splims is None:
            return None
        else:
            return self._splims.copy()

    @property
    def splims_unit(self):
        return self._splims_unit

    @property
    def splims_labels(self):
        return sorted(self._slims.keys())

    @property
    def propty_database(self):
        return _copy.deepcopy(self._propty_database)

    @property
    def excdata(self):
        return self._excdata

    def __str__(self):
        st = ''
        st +=        'psname      : ' + str(self.psname)
        st += '\n' + 'pstype      : ' + str(self.pstype)
        st += '\n' + 'polarity    : ' + str(self.polarity)
        st += '\n' + 'magfunc     : ' + str(self.magfunc)
        st += '\n' + 'splims_unit : ' + str(self.splims_unit)

        if self.splims is None:
            st += '\n' + 'splims      : ' + str(None)
        else:
            st += '\n' + 'splims      : ' + 'DRVH:{0:+09.3f} DRVL:{1:+09.3f}'.format(self.splims['DRVH'],self.splims['DRVL'])
            st += '\n' + '              ' + 'HIHI:{0:+09.3f} LOLO:{1:+09.3f}'.format(self.splims['HIHI'],self.splims['LOLO'])
            st += '\n' + '              ' + 'HIGH:{0:+09.3f} LOW :{1:+09.3f}'.format(self.splims['HIGH'],self.splims['LOW'])
            st += '\n' + '              ' + 'HOPR:{0:+09.3f} LOPR:{1:+09.3f}'.format(self.splims['HOPR'],self.splims['LOPR'])

        return st
