import math as _math
from abc import abstractmethod as _abstractmethod
from abc import ABCMeta as _ABCMeta
from siriuspy import util as _util
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply.controller import ControllerEpics as _ControllerEpics
from siriuspy.pwrsupply.model import PowerSupply as _PowerSupply
from siriuspy.pwrsupply.model import PowerSupplyEpicsSync as _PSEpicsSync
from siriuspy.magnet import util as _mutil
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.magnet.data import MAStrengthBase as _MAStrengthBase
from siriuspy.magnet.data import MAStrengthDip as _MAStrengthDip
from siriuspy.magnet.data import MAStrength as _MAStrength
from siriuspy.magnet.data import MAStrengthTrim as _MAStrengthTrim


_connection_timeout = None



# class _Magnet(metaclass=_ABCMeta):
#
#     _dipoles_maname = {
#         'SI':'SI-Fam:MA-B1B2',
#         'TS':'TS-Fam:MA-B',
#         'BO':'BO-Fam:MA-B',
#         'TB':'TB-Fam:MA-B',
#     }
#
#     @staticmethod
#     def get_dipole_sector_maname(section=None, maname=None):
#         if section is None:
#             pvname = _SiriusPVName(maname)
#             section = pvname.section
#         return section, _Magnet._dipoles_maname[section]
#
#     @property
#     def multipoles(self):
#         return self._conv_currents_2_multipoles('current_mon')
#
#     @property
#     def multipoles_sp(self):
#         return self._conv_currents_2_multipoles('current_sp')
#
#     @property
#     def strength(self):
#         return self._conv_multipoles_2_strength(self.multipoles, 'current_mon', self.brho)
#
#     @property
#     def strength_sp(self):
#         return self._conv_multipoles_2_strength(self.multipoles_sp, 'current_sp', self.brho_sp)
#
#     @property
#     def brho(self):
#         return self._get_brho()
#
#     @property
#     def brho_sp(self):
#         return self._get_brho_sp()
#
#     @property
#     def currents(self):
#         return self._get_currents('current_mon')
#
#     @property
#     def currents_sp(self):
#         return self._get_currents('current_sp')
#
#     @_abstractmethod
#     def _get_currents(self, current_attr):
#         pass
#
#     @_abstractmethod
#     def _conv_currents_2_multipoles(self, current_attr):
#         pass
#
#     @_abstractmethod
#     def _conv_multipoles_2_strength(self, multipoles, brho):
#         pass
#
#     @_abstractmethod
#     def _get_brho(self):
#         pass
#
#     @_abstractmethod
#     def _get_brho_sp(self):
#         pass
#
#
# class MagnetDipole(_MAData, _Magnet):
#
#     _ref_angles = {
#         'SI_BC': _math.radians(4.2966),
#         'SI_B1': _math.radians(2.7553),
#         'SI_B2': _math.radians(4.0964),
#         'TS'   : _math.radians(5.3333),
#         'BO'   : _math.radians(7.2000),
#         'TB'   : _math.radians(15.000),
#     }
#
#     def __init__(self, maname, psupplies=None,
#                        left='linear',
#                        right='linear'):
#         _MAData.__init__(self, maname=maname)
#         self._left = left
#         self._right = right
#         self._psupplies = [_PowerSupply(psname=psname) for psname in self.psnames] if psupplies is None else psupplies
#         self._set_reference_dipole_data()
#         self._m_type = self.excdata(self.psnames[0]).main_multipole_type
#         self._m_harm = self.excdata(self.psnames[0]).main_multipole_harmonic
#
#     def _set_reference_dipole_data(self):
#         ang = MagnetDipole._ref_angles
#         if self._maname.section == 'SI':
#             self._ref_energy = 3.0 #[GeV]
#             self._ref_brho = _util.beam_rigidity(self._ref_energy)
#             self._ref_BL_BC =  - self._ref_brho * ang['SI_BC']
#             self._ref_angle = ang['SI_B1'] + ang['SI_B2'] + ang['SI_BC']
#             self._ref_BL = - self._ref_brho * self._ref_angle - self._ref_BL_BC
#         elif self._maname.section == 'BO':
#             self._ref_energy = 3.0 #[GeV]
#             self._ref_brho = _util.beam_rigidity(self._ref_energy)
#             self._ref_angle = ang['BO']
#             self._ref_BL = - self._ref_brho * self._ref_angle
#         elif self._maname.section == 'TS':
#             self._ref_energy = 3.0 #[GeV]
#             self._ref_brho = _util.beam_rigidity(self._ref_energy)
#             self._ref_angle = ang['TS']
#             self._ref_BL = - self._ref_brho * self._ref_angle
#         elif self._maname.section == 'TB':
#             self._ref_energy = 0.150 #[GeV]
#             self._ref_brho = _util.beam_rigidity(self._ref_energy)
#             self._ref_angle = ang['TB']
#             self._ref_BL = - self._ref_brho * self._ref_angle
#         else:
#             raise NotImplementedError
#
#     def _get_currents(self, current_attr):
#         return {ps.psname:getattr(ps, current_attr) for ps in self._psupplies}
#
#     def _conv_currents_2_multipoles(self, current_attr):
#         m_sum = {}
#         for ps in self._psupplies:
#             m = ps.psdata.excdata.interp_curr2mult(getattr(ps, current_attr),
#                                             left=self._left, right=self._right)
#             m_sum = _mutil.sum_magnetic_multipoles(m_sum, m)
#         return m_sum
#
#     def _conv_multipoles_2_strength(self, multipoles, brho=None):
#         intfield = multipoles[self._m_type][self._m_harm]
#         if self._maname.section == 'SI':
#             strength = (self._ref_energy / self._ref_brho) * (- intfield - self._ref_BL_BC) / self._ref_angle
#         else:
#             strength = (self._ref_energy / self._ref_brho) * (-intfield) / self._ref_angle
#         return strength
#
#     def _get_brho(self):
#         m = self._conv_currents_2_multipoles('current_mon')
#         energy = self._conv_multipoles_2_strength(m, brho=None)
#         #energy = self.strength
#         brho = _util.beam_rigidity(energy)
#         return brho
#
#     def _get_brho_sp(self):
#         m = self._conv_currents_2_multipoles('current_sp')
#         energy = self._conv_multipoles_2_strength(m, brho=None)
#         #energy = self.strength_sp
#         brho = _util.beam_rigidity(energy)
#         return brho
#
#
# _Magnet.register(MagnetDipole)
#
#
# class Magnet(_MAData, _Magnet):
#
#     def __init__(self, maname, psupplies=None,
#                                dipole=None,
#                                left='linear',
#                                right='linear'):
#         _MAData.__init__(self, maname=maname)
#         self._left = left
#         self._right = right
#         if psupplies is None:
#             # creates simulator power supply
#             self._psupplies = [_PowerSupply(psname=psname) for psname in self.psnames]
#             maname_dipole = _Magnet.get_dipole_sector_maname(maname=maname)
#             self._dipole = MagnetDipole(maname=maname_dipole, psupplies=None, left=left, right=right)
#         else:
#             self._psupplies = psupplies
#             self._dipole = dipole
#         self._m_type = self.excdata(self.psnames[0]).main_multipole_type
#         self._m_harm = self.excdata(self.psnames[0]).main_multipole_harmonic
#
#     def _get_currents(self, current_attr):
#         return {ps.psname:getattr(ps, current_attr) for ps in self._psupplies}
#
#     def _conv_currents_2_multipoles(self, current_attr):
#         m_sum = {}
#         for ps in self._psupplies:
#             m = ps.psdata.excdata.interp_curr2mult(getattr(ps, current_attr),
#                                             left=self._left, right=self._right)
#             m_sum = _mutil.sum_magnetic_multipoles(m_sum, m)
#         return m_sum
#
#     def _conv_multipoles_2_strength(self, multipoles, brho):
#         intfield = multipoles[self._m_type][self._m_harm]
#         return -intfield / brho
#
#     def _get_brho(self):
#         return self._dipole.brho
#
#     def _get_brho_sp(self):
#         return self._dipole.brho_sp
#
# _Magnet.register(Magnet)
#



class PowerSupplyMA(_PSEpicsSync):

    def __init__(self, maname, use_vaca=False,
                               vaca_prefix=None,
                               connection_timeout=_connection_timeout):
        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(self._maname)
        self._psname = self._madata.psnames
        super().__init__(psnames=self._get_ma_controllers(),
                         use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         connection_timeout=connection_timeout)
        self._init_pwrsupply(use_vaca=use_vaca,
                             vaca_prefix=vaca_prefix,
                             connection_timeout=connection_timeout)

    def _get_ma_controllers(self):
        ''' Method to get controllers that'll be created for given magnet '''
        if self.magfunc == "dipole":
            if self._maname.section == "SI":
                return ["SI-Fam:PS-B1B2-1", "SI-Fam:PS-B1B2-2"]
            elif self._maname.section == "BO":
                return ["BO-Fam:PS-B-1", "BO-Fam:PS-B-2"]
            else:
                raise NotImplementedError
        else:
            return [self._maname.replace(':MA', ':PS')]

    @property
    def magfunc(self):
        """Return string corresponding to the magnetic function excitated with the power supply."""
        return self._madata.magfunc(self._psname[0])

    @property
    def strength_sp(self):
        kwargs = {arg:controller.current_sp for arg,controller in self._strobj_kwargs.items()}
        return self._strobj.conv_current_2_strength(**kwargs)

    @strength_sp.setter
    def strength_sp(self, value):
        kwargs = {arg:controller.current_sp for arg,controller in self._strobj_kwargs.items()}
        self.current_sp = self._strobj.conv_strength_2_current(strength=value, **kwargs)

    @property
    def strength_mon(self):
        kwargs = {arg:controller.current_load for arg,controller in self._strobj_kwargs.items()}
        return self._strobj.conv_current_2_strength(**kwargs)

    def _get_database(self, prefix=''):
        """Return an updated  PV database whose keys correspond to PS properties."""
        db = self._madata._propty_databases[self._psname[0]]
        value = self.ctrlmode_mon; db['CtrlMode-Mon']['value'] = _et.enums('RmtLocTyp').index(value) if self._enum_keys else value
        value = self.opmode_sel;   db['OpMode-Sel']['value'] = _et.enums('PSOpModeTyp').index(value) if self._enum_keys else value
        value = self.opmode_sts;   db['OpMode-Sts']['value'] = _et.enums('PSOpModeTyp').index(value) if self._enum_keys else value
        value = self.pwrstate_sel; db['PwrState-Sel']['value'] = _et.enums('OffOnTyp').index(value) if self._enum_keys else value
        value = self.pwrstate_sts; db['PwrState-Sts']['value'] = _et.enums('OffOnTyp').index(value) if self._enum_keys else value
        db['Reset-Cmd']['value'] = self.reset
        db['Abort-Cmd']['value'] = self.abort
        wfmlabels = self._get_wfmlabels_mon()
        db['WfmLoad-Sel']['enums'] = wfmlabels
        db['WfmLoad-Sts']['enums'] = wfmlabels
        value = self.wfmload_sel;  db['WfmLoad-Sel']['value'] = _np.where(wfmlabels == value)[0][0] if self._enum_keys else value
        value = self.wfmload_sts;  db['WfmLoad-Sts']['value'] = _np.where(wfmlabels == value)[0][0] if self._enum_keys else value
        db['WfmLabel-SP']['value']    = self.wfmlabel_sp
        db['WfmLabel-RB']['value']    = self.wfmlabel_rb
        db['WfmLabels-Mon']['value']  = self.wfmlabels_mon
        db['WfmData-SP']['value']     = self.wfmdata_sp
        db['WfmData-RB']['value']     = self.wfmdata_rb
        db['WfmSave-Cmd']['value']    = self.wfmsave_cmd
        db['WfmIndex-Mon']['value']   = self.wfmindex_mon
        db['Current-SP']['value']     = self.current_sp
        db['Current-RB']['value']     = self.current_rb
        db['CurrentRef-Mon']['value'] = self.currentref_mon
        db['Current-Mon']['value']    = self.current_mon
        db['Intlk-Mon']['value']      = self.intlk_mon

        if 'KL-SP' in db:
            strength = 'KL'
        elif 'SL-SP' in db:
            strength = 'SL'
        elif 'Energy-SP' in db:
            strength = 'Energy'
        elif 'Kick-SP' in db:
            strength = 'Kick'
        else:
            raise ValueError("No strength defined")

        #Set strength values
        db[strength + '-SP']['value'] = self.strength_sp
        #db[strength + '-RB']['value'] = self.strength_rb
        #db[strength + 'Ref-Mon']['value'] = self.strengthref_mon
        #db[strength + '-Mon']['value'] = self.strength_mon

        prefixed_db = dict()
        for key, value in db.items():
            prefixed_db[prefix + ':' + key] = value

        return prefixed_db

    def _mycallback(self, pvname, value, **kwargs):
        #print('[PS] [callback] ', pvname, value)
        for psname in self._psname:
            pvname = pvname.replace(psname, self._maname)
        #Callbacks for strength: _rb, ref_mon, _mon
        if 'Current' in pvname:
            slot = ':'.join(pvname.split(':')[:2])
            self.callback(slot + ':KL-RB', self.strength_mon, **kwargs)
            self.callback(slot + ':KLRef-Mon', self.strength_mon, **kwargs)
            self.callback(slot + ':KL-Mon', self.strength_mon, **kwargs)
        super()._mycallback(pvname, value, **kwargs)


        # if 'CtrlMode-Mon' in pvname:
        #     self._ctrlmode_mon = value
        # elif 'OpMode-Sel' in pvname:
        #     if self._opmode_sel != value:
        #         self._set_opmode_sel(self._opmode_sel)
        # elif 'PwrState-Sel' in pvname:
        #     if self._pwrstate_sel != value:
        #         self._set_pwrstate_sel(self._pwrstate_sel)
        # elif 'WfmLoad-Sel' in pvname:
        #     if self._wfmload_sel != value:
        #         self._set_wfmload_sel(self._wfmload_sel)
        # elif 'WfmLabel-SP' in pvname:
        #     if self._wfmlabel_sp != value:
        #         self._set_wfmlabel_sp(self._wfmlabel_sp)
        # elif 'WfmData-SP' in pvname:
        #     if self._wfmdata_sp != value:
        #         self._set_wfmdata_sp(self._wfmdata_sp)
        # elif 'Current-SP' in pvname:
        #     if self._current_sp != value: #Value was not changed by the MA-IOC
        #         self._set_current_sp(self._current_sp)
        #
        # if self.callback is not None and callback:
        #     pfield = pvname.split(':')[-1]
        #     slot = ':'.join(pvname.split(':')[:2])
        #     if self._is_using_vaca:
        #         slot = slot[4:]
        #     if slot in ['SI-Fam:PS-B1B2-1', 'SI-Fam:PS-B1B2-2']:
        #         self.callback('SI-Fam:PS-B1B2:' + pfield, value, **kwargs)
        #     else:
        #         self.callback(pvname, value, **kwargs)

    def _init_pwrsupply(self, use_vaca, vaca_prefix, connection_timeout):
        sector, dipole_maname = _MAStrength.get_dipole_sector_maname(maname=self._maname)
        if self.magfunc == 'dipole' and self._maname.subsection == 'Fam':
            self._controller = self._controllers[0]
            self._strobj = _MAStrengthDip(maname=dipole_maname)
            self._strobj_kwargs = {'current':self._controller}
        else:
            madata_dipole = _MAData(maname=dipole_maname)
            self._controller_dipole = _ControllerEpics(psname=madata_dipole.psnames[0],
                                                       use_vaca=use_vaca,
                                                       vaca_prefix=vaca_prefix,
                                                       connection_timeout=connection_timeout)
            #print(self.magfunc)
            if self._maname.subsection == 'Fam' or self.magfunc in ('quadrupole-skew', 'corrector-horizontal'):
                self._strobj = _MAStrength(maname=self._maname)
                self._strobj_kwargs = {'current':self._controllers[0],
                                       'current_dipole':self._controller_dipole}
            elif self.magfunc in ('quadrupole'):
                pvname = _SiriusPVName(self._psname[0])
                family = pvname.replace(pvname.subsection, 'Fam')
                self._controller_family = _ControllerEpics(psname=family,
                                                           use_vaca=use_vaca,
                                                           vaca_prefix=vaca_prefix,
                                                           connection_timeout=connection_timeout)
                self._strobj = _MAStrengthTrim(maname=self._maname)
                self._strobj_kwargs = {'current':self._controllers[0],
                                       'current_dipole':self._controller_dipole,
                                       'current_family':self._controller_family}
