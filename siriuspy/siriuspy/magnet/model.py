
from siriuspy.pwrsupply import psdata as _psdata
from siriuspy.magnet import magdata as _magdata
from siriuspy.magnet import ExcitationData as _ExcData
from siriuspy.pwrsupply import PowerSupply as _PowerSupply
from siriuspy.magnet import util as _util


class Magnet:

    def __init__(self,
                 name,
                 left=None,   # type of left-side multipole interpolation
                 right=None,  # type of right-side multipole interpolation
                 ):
        self._name = name
        self._ps_names = ()
        self._ps = {}
        self._excdata = {}
        self._left = 'linear' if left is None else left
        self._right = 'linear' if left is None else right
        self._init_ps()

    def _init_ps(self):
        self._ps_names = _magdata.conv_magnet_2_psnames(self._name)
        self._excdata = {}
        self._ps = {}
        for ps_name in self._ps_names:
            self._ps[ps_name] = _PowerSupply(ps_name=ps_name,
                                             controller=None,
                                             callback=None,
                                             enum_keys=True)
            self._ps[ps_name].pwrstate_sel = 'On'
            self._ps[ps_name].opmode_sel = 'SlowRef'
            fname = pstype_name = self._ps[ps_name].pstype_name + '.txt'
            self._excdata[ps_name] = _ExcData(filename_web=fname)

    @property
    def name(self):
        return self._name

    @property
    def ps_names(self):
        return self._ps_names

    def get_ps(self, ps_name):
        return self._ps[ps_name]

    def get_current(self, ps_name):
        return self._ps[ps_name].current_rb

    def set_current(self, ps_name, value):
        self._ps[ps_name].current_sp = value

    def get_integrated_multipoles(self):
        m_list = []
        for ps_name, excdata in self._excdata.items():
            current = self._ps[ps_name].current_rb
            m = excdata.interp_curr2mult(current,
                                         left=self._left, right=self._right)
            m_list.append(m)
        return _util.add_multipoles(m_list)
