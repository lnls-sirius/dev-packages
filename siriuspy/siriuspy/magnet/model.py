
import copy as _copy
from siriuspy.magnet import util as _util
from siriuspy.magnet import magdata as _magdata
from siriuspy.magnet import ExcitationData as _ExcData
from siriuspy.pwrsupply import psdata as _psdata
from siriuspy.pwrsupply import PowerSupply as _PowerSupply
from siriuspy.pwrsupply.controller import ControllerEpics as _ControllerEpics
from .magdata import get_magps_setpoint_limits as _mag_sp_lims
from .util import conv_epics2pcaspy_lim_names as _conv_lim_names

_connection_timeout = 0.05


_magnet_types = {'normal_dipole':     ('normal', 0, 'BL', 'rad'),
                 'normal_dipole_fam': ('normal', 0, 'BL', 'rad'),
                 'normal_quadrupole': ('normal', 1, 'KL', 'KL'),
                 'normal_sextupole':  ('normal', 2, 'SL', 'SL'),
                 'normal_corrector':  ('normal', 0, 'HKick', 'rad'),
                 'skew_corrector':    ('skew',   0, 'VKick', 'rad'),
                }


class PowerSupplyDipMagEpics:

    def __init__(self, ma_base_fam_name, prefix=''):
        self._prefix = prefix
        self._ma_base_fam_name = ma_base_fam_name
        ps_base_fam_name = ma_base_fam_name.replace('MA-','PS-')
        self._ps_names = (ps_base_fam_name + '-1', ps_base_fam_name + '-2')
        self._setpoint_limits = _mag_sp_lims(self._ma_base_fam_name)
        ctrl1 = _ControllerEpics(ps_name = prefix + self._ps_names[0],
                                 current_min = self._setpoint_limits['DRVL'],
                                 current_max = self._setpoint_limits['DRVH'],
                                 connection_timeout = _connection_timeout,
                                 )
        ctrl2 = _ControllerEpics(ps_name = prefix + self._ps_names[1],
                                 current_min = self._setpoint_limits['DRVL'],
                                 current_max = self._setpoint_limits['DRVH'],
                                 connection_timeout = _connection_timeout,
                                 )
        self._ps_list = (
             _PowerSupply(ps_name = self._ps_names[0], controller=ctrl1, callback=self._mycallback, enum_keys=True),
             _PowerSupply(ps_name = self._ps_names[1], controller=ctrl2, callback=self._mycallback, enum_keys=True),
        )

    def _mycallback(self, pvname, value, **kwargs):
        pass


class Magnet:

    def __init__(self,
                 name,
                 power_supplies=None,
                 left=None,   # type of left-side multipole interpolation
                 right=None,  # type of right-side multipole interpolation
                 ):

        #print(name)
        self._name = name
        self._ps_dict = {}
        self._excdata = {}
        self._callback = None
        self._left = 'linear' if left is None else left
        self._right = 'linear' if left is None else right
        self.add_power_supplies(power_supplies)

    @property
    def database(self):
        db = {}
        for ps_name in self.ps_names:
            db.update(self._ps_dict[ps_name].database)
        return db

    def update_state(self):
        for psname, ps in self._ps_dict.items():
            ps.update_state()

    def _mycallback(self, pvname, value, **kwargs):
        #print('magnet', pvname, self._callback)
        if self._callback is not None:
            self._callback(pvname, value, **kwargs)

    def set_callback(self, callback):
        #print('set_callback', callback)
        self._callback = callback

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

        for ps_name, ps in self._ps_dict.items():
            ps.set_callback(self._mycallback)

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

    def get_current_rb(self, ps_names=None):
        if ps_names is None:
            return {name:self._ps_dict[name].current_rb for name in self.ps_names}
        elif isinstance(ps_names, str):
            return self._ps_dict[ps_names].current_rb
        else:
            return {name:self._ps_dict[name].current_rb for name in ps_names}

    def get_current_sp(self, ps_names=None):
        if ps_names is None:
            return {name:self._ps_dict[name].current_sp for name in self.ps_names}
        elif isinstance(ps_names, str):
            return self._ps_dict[ps_names].current_sp
        else:
            return {name:self._ps_dict[name].current_sp for name in ps_names}

    def set_current(self, value, ps_name=None):
        if ps_name is None:
            for ps_name,v in value.items():
                self._ps_dict[ps_name].current_sp = v
        else:
            self._ps_dict[ps_name].current_sp = value

    def conv_currents2multipoles(self,currents):
        m_list = []
        for ps_name in currents:
            current = currents[ps_name]

            m = self._excdata[ps_name].interp_curr2mult(current, left=self._left, right=self._right)
            m_list.append(m)
        return _util.add_multipoles(m_list)

    def get_integrated_multipoles(self, ps_names=None):
        currents_rb = self.get_current_rb(ps_names=ps_names)
        return self.conv_currents2multipoles(currents_rb)

class MagnetFam(Magnet):

    def __init__(self,
                 magnet_type,
                 **kwargs):
        super().__init__(**kwargs)
        self._magnet_type = magnet_type
        self._mag_sp_lims = _mag_sp_lims(magps=self._name)

    def _mycallback(self, pvname, value, **kwargs):
        #print('magnetfam', pvname, value)
        if self._callback is None: return
        super()._mycallback(pvname, value, **kwargs)
        if 'Current' in pvname:
            typ, h, str_kl, unit = _magnet_types[self._magnet_type]
            reason_kl = pvname.replace('Current',str_kl)
            value_kl = self.kl_sp if 'SP' in pvname else self.kl_rb
            #print('magnetfam_kl', reason_kl, value_kl)
            self._callback(reason_kl, value_kl, **kwargs)

    @property
    def magnet_type(self):
        return self._magnet_type

    @property
    def kl_sp(self):
        currents = self.get_current_sp()
        m = self.conv_currents2multipoles(currents)
        typ, h, str_kl, unit = _magnet_types[self._magnet_type]
        return m[typ][h]

    @kl_sp.setter
    def kl_sp(self, value):
        typ, h, str_kl, unit = _magnet_types[self._magnet_type]
        (ps_name, ps), = self._ps_dict.items() # does not work with more than one PS !!!
        excdata = self._excdata[ps_name]
        current = excdata.interp_mult2curr(multipole=value, harmonic=h, multipole_type=typ, left='linear', right='linear')
        ps.current_sp = current

    @property
    def kl_rb(self):
        currents = self.get_current_rb()
        m = self.conv_currents2multipoles(currents)
        typ, h, str_kl, unit = _magnet_types[self._magnet_type]
        return m[typ][h]

    def _get_db_kl(self, ps_name, key_ps, db_value, sp_lims):
        typ, h, str_kl, unit = _magnet_types[self._magnet_type]
        family, propty = key_ps.split(':')
        key_kl = family + ':' + propty.replace('Current',str_kl)
        hlim = self.conv_currents2multipoles({ps_name:sp_lims['HIHI']})
        llim = self.conv_currents2multipoles({ps_name:sp_lims['LOLO']})
        inverted = llim[typ][h] > hlim[typ][h]
        db_kl = _copy.deepcopy(db_value)
        # convert limits
        for epics_name, lim in sp_lims.items():
            pcaspy_name = _conv_lim_names(epics_name, inverted=inverted)
            m = self.conv_currents2multipoles({ps_name:lim})
            db_kl[pcaspy_name] = m[typ][h]
        # convert actual value
        m = self.get_integrated_multipoles()
        db_kl['value'] = m[typ][h]
        return key_kl, db_kl

    @property
    def database(self):
        db_ma = {}
        for ps_name in self.ps_names:
            if 'Fam' in ps_name:
                sp_lims = _mag_sp_lims(magps=self._name)
                db_ps = self._ps_dict[ps_name].database
                for key,db_value in db_ps.items():
                    family, propty = key.split(':')
                    if propty in ('Current-SP','Current-RB'):
                        # apply MA over PS limits
                        for epics_name, lim in sp_lims.items():
                            pcaspy_name = _conv_lim_names(epics_name)
                            db_value[pcaspy_name] = lim
                        # add ps database
                        db_ma[key] = db_value
                        # add bl/kl/sl property, converting current to proper units
                        key_kl, db_kl = self._get_db_kl(ps_name, key, db_value, sp_lims)
                        db_ma[key_kl] = db_kl
                    else:
                        db_ma[key] = db_value
            else:
                db_ps = self._ps_dict[ps_name].database
                db_ma.update(db_ps)
        return db_ma

class MagnetFamDip(MagnetFam):

    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)
        self._mag_sp_lims = _mag_sp_lims(magps=self._name)

    def _update_excdata(self):
        for ps_name, ps in self._ps_dict.items():
            if ps_name not in self._excdata:
                if ps.pstype_name == 'si-dipole-b1b2-fam':
                    # b1 to B1B2-1 and b2 to B1B2-2 attributions are arbitrary but an effective solution.
                    self._excdata['SI-Fam:PS-B1B2-1'] = _ExcData(filename_web='si-dipole-b1.txt')
                    self._excdata['SI-Fam:PS-B1B2-2'] = _ExcData(filename_web='si-dipole-b2.txt')
                else:
                    raise Exception('excitation curve for ' + ps_name + 'not defined!')


                #self._excdata[ps_name] = _ExcData(filename_web=fname)

    @property
    def database(self):
        db_ma = {}
        ps_name = self.ps_names[0]
        db_ps = self._ps_dict[ps_name].database
        #ps_name = ps_name.replace('-1','').replace('-2','')
        sp_lims = _mag_sp_lims(magps=self._name)
        for key,db_value in db_ps.items():
            family, propty = key.split(':')
            if propty in ('Current-SP','Current-RB'):
                # apply MA over PS limits
                for epics_name, lim in sp_lims.items():
                    pcaspy_name = _conv_lim_names(epics_name)
                    db_value[pcaspy_name] = lim
                # add ps database
                db_ma[key.replace('-1','').replace('-2','')] = db_value
                # add bl/kl/sl property, converting current to proper units
                key_kl, db_kl = self._get_db_kl(ps_name, key, db_value, sp_lims)
                db_ma[key_kl.replace('-1','').replace('-2','')] = db_kl
            else:
                db_ma[key.replace('-1','').replace('-2','')] = db_value
        return db_ma
