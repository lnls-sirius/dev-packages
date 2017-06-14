import math as _math
#from abc import abstractmethod as _abstractmethod
#from abc import ABCMeta as _ABCMeta
from siriuspy import util as _util
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply.controller import ControllerEpics as _ControllerEpics
from siriuspy.pwrsupply.model import PowerSupply as _PowerSupply
from siriuspy.pwrsupply.model import PowerSupplySync as _PowerSupplySync
from siriuspy.magnet import util as _mutil
from siriuspy.magnet.data import MAData as _MAData
#from siriuspy.magnet.data import MAStrengthBase as _MAStrengthBase
from siriuspy.magnet.data import MAStrengthDip as _MAStrengthDip
from siriuspy.magnet.data import MAStrength as _MAStrength
from siriuspy.magnet.data import MAStrengthTrim as _MAStrengthTrim


_connection_timeout = None


class Magnet:

    _magfuncs = {
        'dipole' : {'type':'normal', 'harmonic':0},
        'corrector-horizontal' : {'type':'normal', 'harmonic':0},
        'corrector-vertical' : {'type':'skew', 'harmonic':0},
        'quadrupole' : {'type':'normal', 'harmonic':1},
        'quadrupole-skew' : {'type':'skew', 'harmonic':1},
        'sextupole' : {'type':'normal', 'harmonic':2},
    }

    def __init__(self, magfunc,
                       psupplies,
                       left='linear',
                       right='linear'):
        self._magfunc = magfunc
        self._psupplies = psupplies
        self._left = left
        self._right = right

    def get_multipoles(self, current_attr):
        msum = {}
        for ps in self._psupplies:
            current = getattr(ps, current_attr)
            m = ps.psdata.excdata.interp_curr2mult(current)
            msum = _mutil.sum_magnetic_multipoles(msum, m)
        return msum

    def get_intfield(self, current_attr):
        m = self.get_multipoles(current_attr=current_attr)
        mf = Magnet._magfuncs[self._magfunc]
        intfield = m[mf['type']][mf['harmonic']]
        return intfield


class MagnetQuad(Magnet):

    def __init__(self, maname, dipole, **kwargs):
        kwargs['magfunc'] = 'quadrupole'
        super().__init__(**kwargs)
        self._maname = _SiriusPVName(maname)
        self._dipole = dipole
        self._psmain = self._psupplies[0]


    @property
    def dipole(self):
        return self._dipole

    def get_kl(self, current_attr):
        brho = self._dipole.get_brho(current_attr=current_attr)
        intfield = self.get_intfield(current_attr=current_attr)
        kl = -intfield / brho
        return kl

    def set_kl(self, kl):
        brho = self._dipole.get_brho(current_attr='current_sp')
        intfield = -kl / brho
        mf = Magnet._magfuncs[self._magfunc]
        interp_mult2curr = self._psmain.psdata.excdata.interp_mult2curr
        current = interp_mult2curr(intfield, mf['harmonic'], mf['type'],
                                   left=self._left, right=self._right)
        self._psmain.current_sp = current


class MagnetQuadTrim(Magnet):

    def __init__(self, maname, dipole, family, **kwargs):
        kwargs['magfunc'] = 'quadrupole'
        super().__init__(**kwargs)
        self._maname = _SiriusPVName(maname)
        self._dipole = dipole
        self._family = family
        self._psmain = self._psupplies[0]
        self._kl = self.get_kl(current_attr='current_sp')

    def get_kl(self, current_attr):
        brho = self._dipole.get_brho(current_attr=current_attr)
        infield_family = self._family.get_intfield(current_attr=current_attr)
        infield_trim = self.get_intfield(current_attr=current_attr)
        intfield = infield_family + infield_trim
        kl = -intfield / brho
        return kl

    def set_kl(self, kl):
        self._kl = kl
        brho = self._dipole.get_brho(current_attr='current_sp')
        intfield = -kl / brho
        infield_family = self._family.get_intfield(current_attr='current_sp')
        intfield_trim = intfield - intfield_family
        mf = Magnet._magfuncs[self._magfunc]
        interp_mult2curr = self._psmain.psdata.excdata.interp_mult2curr
        current = interp_mult2curr(intfield_trim, mf['harmonic'], mf['type'],
                                   left=self._left, right=self._right)
        self._psmain.current_sp = current


class MagnetDipole(Magnet):

    _ref_angles = {
        'SI_BC': _math.radians(4.2966),
        'SI_B1': _math.radians(2.7553),
        'SI_B2': _math.radians(4.0964),
        'TS'   : _math.radians(5.3333),
        'BO'   : _math.radians(7.2000),
        'TB'   : _math.radians(15.000),
    }

    def __init__(self, maname, **kwargs):
        kwargs['magfunc'] = 'dipole'
        super().__init__(**kwargs)
        self._maname = _SiriusPVName(maname)
        self._set_reference_dipole_data()
        self._psmain = self._psupplies[0]

    def _set_reference_dipole_data(self):
        ang = MagnetDipole._ref_angles
        if self._maname.section == 'SI':
            self._ref_energy = 3.0 #[GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_BL_BC =  - self._ref_brho * ang['SI_BC']
            self._ref_angle = ang['SI_B1'] + ang['SI_B2'] + ang['SI_BC']
            self._ref_BL = - self._ref_brho * self._ref_angle - self._ref_BL_BC
        elif self._maname.section == 'BO':
            self._ref_energy = 3.0 #[GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['BO']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif self._maname.section == 'TS':
            self._ref_energy = 3.0 #[GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TS']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif self._maname.section == 'TB':
            self._ref_energy = 0.150 #[GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TB']
            self._ref_BL = - self._ref_brho * self._ref_angle
        else:
            raise NotImplementedError

    def get_energy(self, current_attr):
        intfield = self.get_intfield(current_attr=current_attr)
        if self._maname.section == 'SI':
            energy = (self._ref_energy / self._ref_brho) * (- intfield - self._ref_BL_BC) / self._ref_angle
        else:
            energy = (self._ref_energy / self._ref_brho) * (-intfield) / self._ref_angle
        return energy

    def set_energy(self, energy):
        if self._maname.section == 'SI':
            intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * energy - self._ref_BL_BC
        else:
            intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * energy
        mf = Magnet._magfuncs[self._magfunc]
        interp_mult2curr = self._psmain.psdata.excdata.interp_mult2curr
        current = interp_mult2curr(intfield, mf['harmonic'], mf['type'],
                                   left=self._left, right=self._right)
        self._psmain.current_sp = current

    def get_brho(self, current_attr):
        energy = self.get_energy(current_attr=current_attr)
        brho = _util.beam_rigidity(energy)
        return brho


class PowerSupplyMA(_PowerSupplySync):

    def __init__(self, maname, use_vaca=False,
                               vaca_prefix=None,
                               connection_timeout=_connection_timeout,
                               **kwargs
                               ):
        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(self._maname)
        self._psname = self._madata.psnames
        super().__init__(psnames=self._get_psnames(),
                         use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         connection_timeout=connection_timeout,
                         **kwargs)
        self._init_pwrsupply(use_vaca=use_vaca,
                             vaca_prefix=vaca_prefix,
                             connection_timeout=connection_timeout)

        self._currents_sp['current'] = self._controller.current_sp
        self._strength_sp = self._strobj.conv_current_2_strength(**self._currents_sp)

    def _get_psnames(self):
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
        return self._strength_sp
        #self._currents_sp['current'] = self._controller.current_sp
        #return self._strobj.conv_current_2_strength(**self._currents_sp)

    @strength_sp.setter
    def strength_sp(self, value): #COMO SETAR strength DO TRIM
        if value != self._strength_sp:
            self._strength_sp = value
            self._currents_sp['current'] = self._controller.current_sp
            self.current_sp = self._strobj.conv_strength_2_current(strength=value, **self._currents_sp)

    @property
    def strength_rb(self):
        self._currents_sp['current'] = self._controller.current_sp
        return self._strobj.conv_current_2_strength(**self._currents_sp)

    @property
    def strengthref_mon(self):
        self._currents_ref['current'] = self._controller.current_ref
        return self._strobj.conv_current_2_strength(**self._currents_ref)

    @property
    def strength_mon(self):
        self._currents_load['current'] = self._controller.current_load
        return self._strobj.conv_current_2_strength(**self._currents_load)

    def _init_pwrsupply(self, use_vaca, vaca_prefix, connection_timeout):
        sector, dipole_maname = _MAStrength.get_dipole_sector_maname(maname=self._maname)
        if self.magfunc == 'dipole' and self._maname.subsection == 'Fam':
            self._controller = self._controllers[0]
            self._strobj = _MAStrengthDip(maname=dipole_maname)
            self._currents_sp  = {}
            self._currents_ref = {}
            self._currents_load = {}
        else:
            madata_dipole = _MAData(maname=dipole_maname)
            self._controller_dipole = _ControllerEpics(psname=madata_dipole.psnames[0],
                                                       use_vaca=use_vaca,
                                                       vaca_prefix=vaca_prefix,
                                                       connection_timeout=connection_timeout)
            if self._maname.subsection == 'Fam' or self.magfunc in ('quadrupole-skew',
                                                                    'corrector-horizontal',
                                                                    'corrector-vertical'):
                self._strobj = _MAStrength(maname=self._maname)
                self._currents_sp   = {'current_dipole':self._controller_dipole.current_sp}
                self._currents_ref  = {'current_dipole':self._controller_dipole.current_ref}
                self._currents_load = {'current_dipole':self._controller_dipole.current_load}
            elif self.magfunc in ('quadrupole'):
                pvname = _SiriusPVName(self._psname[0])
                family = pvname.replace(pvname.subsection, 'Fam')
                self._controller_family = _ControllerEpics(psname=family,
                                                           use_vaca=use_vaca,
                                                           vaca_prefix=vaca_prefix,
                                                           callback=self._mycallback_family,
                                                           connection_timeout=connection_timeout)
                self._strobj = _MAStrengthTrim(maname=self._maname)
                self._currents_sp   = {'current_dipole':self._controller_dipole.current_sp,
                                       'current_family':self._controller_family.current_sp}
                self._currents_ref  = {'current_dipole':self._controller_dipole.current_ref,
                                       'current_family':self._controller_family.current_ref}
                self._currents_load = {'current_dipole':self._controller_dipole.current_load,
                                       'current_family':self._controller_family.current_load}

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
        db[strength + '-RB']['value'] = self.strength_rb
        db[strength + 'Ref-Mon']['value'] = self.strengthref_mon
        db[strength + '-Mon']['value'] = self.strength_mon

        prefixed_db = dict()
        for key, value in db.items():
            prefixed_db[prefix + ':' + key] = value

        return prefixed_db

    def _set_current_sp(self, value):
        super()._set_current_sp(value)
        self._currents_sp['current'] = self._controller.current_sp
        self._strength_sp = self._strobj.conv_current_2_strength(**self._currents_sp)

    def _mycallback(self, pvname, value, **kwargs):
        #print('[PS] [callback] ', pvname, value)
        for psname in self._psname:
            pvname = pvname.replace(psname, self._maname)
        #Callbacks for strength: _rb, ref_mon, _mon
        if self._callback is not None:
            slot = ':'.join(pvname.split(':')[:2])
            #Callbacks to update strngth PVs
            if 'Current-RB' in pvname:
                self.callback(slot + ':KL-RB', self.strength_rb, **kwargs)
            elif 'CurrentRef-Mon' in pvname:
                self.callback(slot + ':KLRef-Mon', self.strengthref_mon, **kwargs)
            elif 'Current-Mon' in pvname:
                self.callback(slot + ':KL-Mon', self.strength_mon, **kwargs)
        super()._mycallback(pvname, value, **kwargs)

    def _mycallback_dipole(self, pvname, value, **kwargs):
        """ Callback used for dipole PVs updates. """
        run_callback = False
        if 'Current-RB' in pvname:
            self._currents_sp['current_dipole'] = value
            new_value = self.strength_rb
            run_callback = True
        elif 'CurrentRef-Mon' in pvname:
            self._currents_ref['current_dipole'] = value
            new_value = self.strengthref_mon
            run_callback = True
        elif 'Current-Mon' in pvname:
            self._currents_load['current_dipole'] = value
            new_value = self.strength_mon
            run_callback = True
        if run_callback:
            # signals up changes in strengths
            if self.magfunc in ('quadrupole','quadrupole-skew'):
                pfield = pvname.split(':')[-1].replace("Current", "KL")
            elif self.magfunc in ('corrector-horizontal', 'corrector-vertical'):
                pfield = pvname.split(':')[-1].replace("Current", "Kick")
            elif self.magfunc in ('sextupole',):
                pfield = pvname.split(':')[-1].replace("Current", "SL")
            self.callback(self._maname + ':' + pfield, new_value, **kwargs)

    def _mycallback_family(self, pvname, value, **kwargs):
        """ Callback used for family PVs updates. """
        run_callback = False
        if 'Current-RB' in pvname:
            self._currents_sp['current_family'] = value
            new_value = self.strength_rb
            run_callback = True
        elif 'CurrentRef-Mon' in pvname:
            self._currents_ref['current_family'] = value
            new_value = self.strengthref_mon
            run_callback = True
        elif 'Current-Mon' in pvname:
            self._currents_load['current_family'] = value
            new_value = self.strength_mon
            run_callback = True
        if run_callback:
            # signals up changes in strengths
            if self.magfunc in ('quadrupole','quadrupole-skew'):
                pfield = pvname.split(':')[-1].replace("Current", "KL")
            elif self.magfunc in ('corrector-horizontal', 'corrector-vertical'):
                pfield = pvname.split(':')[-1].replace("Current", "Kick")
            elif self.magfunc in ('sextupole',):
                pfield = pvname.split(':')[-1].replace("Current", "SL")
            self.callback(self._maname + ':' + pfield, new_value, **kwargs)
