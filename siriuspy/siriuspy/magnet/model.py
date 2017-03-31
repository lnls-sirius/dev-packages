
from siriuspy.pwrsupply import psdata as _psdata
from siriuspy.magnet import magdata as _magdata
from siriuspy.magnet import ExcitationData as _ExcData
from siriuspy.pwrsupply import PowerSupply as _PowerSupply
from siriuspy.magnet import util as _util


class Magnet:

    def __init__(self,
                 name,
                 power_supplies=None,
                 left=None,   # type of left-side multipole interpolation
                 right=None,  # type of right-side multipole interpolation
                 ):
        self._name = name
        self._ps_dict = {}
        self._excdata = {}
        self._left = 'linear' if left is None else left
        self._right = 'linear' if left is None else right
        self.add_power_supplies(power_supplies)


    def add_power_supplies(self, power_supplies):
        if power_supplies is None: return
        if isinstance(power_supplies, (tuple,list)):
            for ps in power_supplies:
                self._ps_dict[ps.ps_name] = ps
        elif isinstance(power_supplies, _PowerSupply):
            self._ps_dict[power_supplies.ps_name] = power_supplies
        elif isinstance(power_supplies, dict):
            self._ps_dict.update(power_supplies)
        else:
            raise TypeError
        self._update_excdata()

    def _update_excdata(self):
        for ps_name, ps in self._ps_dict.items():
            if ps_name not in self._excdata:
                fname = ps.pstype_name + '.txt'
                self._excdata[ps_name] = _ExcData(filename_web=fname)

    @property
    def name(self):
        return self._name

    @property
    def ps_names(self):
        return tuple(self._ps_dict.keys())

    def get_ps(self, ps_name):
        return self._ps_dict[ps_name]

    def list_exc_ps_names(self):
        return _magdata.conv_magnet_2_psnames(self._name)

    def get_power_supply(self, ps_name):
        return self._ps_dict[ps_name]

    def get_current(self, ps_name=None):
        if ps_name is None:
            return {name:self._ps_dict[name].current_rb for name in self.ps_names}
        else:
            return self._ps_dict[ps_name].current_rb

    def set_current(self, value, ps_name=None):
        if ps_name is None:
            for ps_name,v in value.items():
                self._ps_dict[ps_name].current_sp = v
        else:
            self._ps_dict[ps_name].current_sp = value

    def get_integrated_multipoles(self, ps_name=None):
        if ps_name is None:
            m_list = []
            for ps_name, excdata in self._excdata.items():
                current = self._ps_dict[ps_name].current_rb
                m = excdata.interp_curr2mult(current,
                                             left=self._left, right=self._right)
                m_list.append(m)
            return _util.add_multipoles(m_list)
        else:
            current = self._ps_dict[ps_name].current_rb
            m = excdata.interp_curr2mult(current,
                                         left=self._left, right=self._right)
            return m
