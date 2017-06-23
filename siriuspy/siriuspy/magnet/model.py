"""This module contain classes for dealing with magnets.

MagnetPowerSupplyDipole
    Handle dipole magnets.
MagnetPowerSupply
    Handle family and individual magnets.
MagnetPowerSupplyTrim
    Handle trim magnets.
"""

import math as _math
import re as _re
from siriuspy import util as _util
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply.controller import ControllerEpics as _ControllerEpics
from siriuspy.pwrsupply.model import PowerSupplySync as _PowerSupplySync
from siriuspy.pwrsupply.model import PowerSupplyEpicsSync \
    as _PowerSupplyEpicsSync
from siriuspy.magnet import util as _mutil
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.magnet.data import MAStrengthDip as _MAStrengthDip
from siriuspy.magnet.data import MAStrength as _MAStrength
from siriuspy.magnet.data import MAStrengthTrim as _MAStrengthTrim


_connection_timeout = None


class MagnetPowerSupplyDipole(_PowerSupplyEpicsSync):
    """Class responsible for controlling a Magnet of type dipole."""

    def __init__(self, maname,
                 use_vaca=False,
                 vaca_prefix=None,
                 callback=None,
                 connection_timeout=None):
        """Class Constructor."""
        super().__init__(maname=maname,
                         use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         lock=True,
                         callback=callback,
                         connection_timeout=connection_timeout)

        self._strength_sp = self._conv_current_2_strength(self.current_sp)
        self._strength_rb = self._conv_current_2_strength(self.current_rb)
        self._strengthref_mon = self._conv_current_2_strength(
            self.currentref_mon)
        self._strength_mon = self._conv_current_2_strength(self.current_mon)

    def _conv_current_2_strength(self, current):
        return 3.0 * (current/394.0)

    def _conv_strength_2_current(self, strength):
        return 394.0*strength/3.0

    def get_brho(self, current):
        """Get Magnetic Rigidity."""
        energy = self._conv_current_2_strength(current=current)
        brho = _util.beam_rigidity(energy)
        return brho

    @property
    def strength_sp(self):
        """Return strength set point."""
        return self._strength_sp

    @strength_sp.setter
    def strength_sp(self, value):
        current = self._conv_strength_2_current(value)
        self.current_sp = current

    @property
    def strength_rb(self):
        """Return strength readback."""
        return self._strength_rb

    @property
    def strengthref_mon(self):
        """Return strength ref mon."""
        return self._strengthref_mon

    @property
    def strength_mon(self):
        """Return strength mon."""
        return self._strength_mon

    def _set_current_sp(self, value):
        super()._set_current_sp(value)
        self._strength_sp = self._conv_current_2_strength(value)

    def _pvchange_current_rb(self, pvname, value, **kwargs):
        super()._pvchange_current_rb(pvname, value, **kwargs)
        self._strength_rb = self._conv_current_2_strength(value)
        self._trigger_callback(pvname.replace('Current', 'Energy'),
                               value, **kwargs)

    def _pvchange_currentref_mon(self, pvname, value, **kwargs):
        super()._pvchange_currentref_mon(pvname, value, **kwargs)
        self._strengthref_mon = self._conv_current_2_strength(value)
        self._trigger_callback(pvname.replace('Current', 'Energy'),
                               value, **kwargs)

    def _pvchange_current_mon(self, pvname, value, **kwargs):
        super()._pvchange_current_mon(pvname, value, **kwargs)
        self._strength_mon = self._conv_current_2_strength(value)
        self._trigger_callback(pvname.replace('Current', 'Energy'),
                               value, **kwargs)


class MagnetPowerSupply(_PowerSupplyEpicsSync):
    """Class responsible for controlling family and individual magnets."""

    def __init__(self, maname, dipole,
                 use_vaca=False,
                 vaca_prefix=None,
                 callback=None,
                 connection_timeout=None):
        """Class constructor."""
        self._dipole = dipole

        if _re.search("(?:QD|QF|Q[0-9]|QS).*", maname):
            self._strength = "KL"
        elif _re.search("(?:SD|SF).*", maname):
            self._strength = "SL"
        elif _re.search("F{0,1}(?:CH|CV).*", maname):
            self._strength = "Kick"
        else:
            raise NotImplementedError

        super().__init__(maname=maname, use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         lock=True,
                         callback=callback,
                         connection_timeout=connection_timeout)

        self._strength_sp = self._conv_current_2_strength(
            self.current_sp, self._dipole.current_sp)
        self._strength_rb = self._conv_current_2_strength(
            self.current_rb, self._dipole.current_sp)
        self._strengthref_mon = self._conv_current_2_strength(
            self.currentref_mon, self._dipole.current_sp)
        self._strength_mon = self._conv_current_2_strength(
            self.current_mon, self._dipole.current_sp)

    def _conv_current_2_strength(self, current, dipole_current):
        intfield = current/2.0
        brho = self._dipole.get_brho(dipole_current)
        return intfield/brho

    def _conv_strength_2_current(self, strength, dipole_current):
        brho = self._dipole.get_brho(dipole_current)
        intfield = strength*brho
        return intfield*2

    @property
    def strength_sp(self):
        """Return strength set point."""
        return self._strength_sp

    @strength_sp.setter
    def strength_sp(self, value):
        current = self._conv_strength_2_current(value, self._dipole.current_sp)
        self.current_sp = current

    @property
    def strength_rb(self):
        """Return strength readback."""
        return self._strength_rb

    @property
    def strengthref_mon(self):
        """Return strength ref mon."""
        return self._strengthref_mon

    @property
    def strength_mon(self):
        """Return strength mon."""
        return self._strength_mon

    def _set_current_sp(self, value):
        super()._set_current_sp(value)
        self._strength_sp = self._conv_current_2_strength(
            value, self._dipole.current_sp)

    def _pvchange_current_rb(self, pvname, value, **kwargs):
        super()._pvchange_current_rb(pvname, value, **kwargs)
        self._strength_rb = self._conv_current_2_strength(
            value, self._dipole.current_rb)
        self._trigger_callback(
            pvname.replace('Current', self._strength), value, **kwargs)

    def _pvchange_currentref_mon(self, pvname, value, **kwargs):
        super()._pvchange_currentref_mon(pvname, value, **kwargs)
        self._strengthref_mon = self._conv_current_2_strength(
            value, self._dipole.currentref_mon)
        self._trigger_callback(
            pvname.replace('Current', self._strength), value, **kwargs)

    def _pvchange_current_mon(self, pvname, value, **kwargs):
        super()._pvchange_current_mon(pvname, value, **kwargs)
        self._strength_mon = self._conv_current_2_strength(
            value, self._dipole.current_mon)
        self._trigger_callback(
            pvname.replace('Current', self._strength), value, **kwargs)


class MagnetPowerSupplyTrim(_PowerSupplyEpicsSync):
    """Class responsible for controlling trim magnets."""

    def __init__(self, maname, dipole, fam,
                 use_vaca=False,
                 vaca_prefix=None,
                 callback=None,
                 connection_timeout=None):
        """Class constructor."""
        self._dipole = dipole
        self._fam = fam

        if _re.search("(?:QD|QF|Q[0-9]|QS).*", maname):
            self._strength = "KL"
        else:
            raise NotImplementedError("Trims only implemented for quadrupoles")

        super().__init__(maname=maname, use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         lock=True,
                         callback=callback,
                         connection_timeout=connection_timeout)

        self._strength_sp = self._conv_current_2_strength(
            self.current_sp, self._dipole.current_sp, self._fam.current_sp)
        self._strength_rb = self._conv_current_2_strength(
            self.current_rb, self._dipole.current_rb, self._fam.current_rb)
        self._strengthref_mon = self._conv_current_2_strength(
            self.currentref_mon, self._dipole.currentref_mon,
            self._fam.currentref_mon)
        self._strength_mon = self._conv_current_2_strength(
            self.current_mon, self._dipole.current_mon, self._fam.current_mon)

    def _conv_current_2_strength(self, current, current_dipole, current_fam):
        intfield_trim = current/2.0
        brho = self._dipole.get_brho(current_dipole)
        strength_trim = intfield_trim/brho
        strength_fam = self._fam._conv_current_2_strength(
            current_fam, current_dipole)
        return strength_fam + strength_trim

    def _conv_strength_2_current(self, strength, current_dipole, current_fam):
        strength_fam = self._fam._conv_current_2_strength(
            current_fam, current_dipole)
        strength_trim = strength - strength_fam
        brho = self._dipole.get_brho(current_dipole)
        intfield = strength_trim*brho
        return intfield*2

    @property
    def strength_sp(self):
        """Return strength set point."""
        return self._strength_sp

    @strength_sp.setter
    def strength_sp(self, value):
        current = self._conv_strength_2_current(
            value, self._dipole.current_sp, self._fam.current_sp)
        self.current_sp = current

    @property
    def strength_rb(self):
        """Return strength readback."""
        return self._strength_rb

    @property
    def strengthref_mon(self):
        """Return strength ref mon."""
        return self._strengthref_mon

    @property
    def strength_mon(self):
        """Return strength monitor value."""
        return self._strength_mon

    def _set_current_sp(self, value):
        super()._set_current_sp(value)
        self._strength_sp = self._conv_current_2_strength(
            value, self._dipole.current_sp, self._fam.current_sp)

    def _pvchange_current_rb(self, pvname, value, **kwargs):
        super()._pvchange_current_rb(pvname, value, **kwargs)
        self._strength_rb = self._conv_current_2_strength(
            value, self._dipole.current_rb, self._fam.current_rb)
        self._trigger_callback(
            pvname.replace('Current', self._strength), value, **kwargs)

    def _pvchange_currentref_mon(self, pvname, value, **kwargs):
        super()._pvchange_currentref_mon(pvname, value, **kwargs)
        self._strengthref_mon = self._conv_current_2_strength(
            value, self._dipole.currentref_mon, self._fam.currentref_mon)
        self._trigger_callback(
            pvname.replace('Current', self._strength), value, **kwargs)

    def _pvchange_current_mon(self, pvname, value, **kwargs):
        super()._pvchange_current_mon(pvname, value, **kwargs)
        self._strength_mon = self._conv_current_2_strength(
            value, self._dipole.current_mon, self._fam.current_mon)
        self._trigger_callback(
            pvname.replace('Current', self._strength), value, **kwargs)


class Magnet:

    _magfuncs = _mutil.get_magfunc_2_multipole_dict()

    def __init__(self, magfunc,
                       psupplies,
                       left='linear',
                       right='linear'):
        self._magfunc = magfunc
        self._psupplies = psupplies
        self._left = left
        self._right = right
        self.psmain = self._psupplies[0] if psmain is None else psmain

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

    @property
    def psmain(self):
        return self._psmain

    @psmain.setter
    def psmain(self, ps):
        self._psmain = ps


class MagnetQuad(Magnet):

    def __init__(self, maname,
                       magnet_dipole,
                       psmain=None,
                       **kwargs):
        kwargs['magfunc'] = 'quadrupole'
        super().__init__(**kwargs)
        self._maname = _SiriusPVName(maname)
        self._magnet_dipole = magnet_dipole


    @property
    def magnet_dipole(self):
        return self._magnet_dipole

    def get_kl(self, current_attr):
        brho = self._magnet_dipole.get_brho(current_attr=current_attr)
        intfield = self.get_intfield(current_attr=current_attr)
        kl = -intfield / brho

        return kl

    def conv_kl_2_current(self, kl):
        brho = self._magnet_dipole.get_brho(current_attr='current_sp')
        intfield = -kl * brho
        mf = Magnet._magfuncs[self._magfunc]
        interp_mult2curr = self.psmain.psdata.excdata.interp_mult2curr
        current = interp_mult2curr(intfield, mf['harmonic'], mf['type'],
                                   left=self._left, right=self._right)
        return current


class MagnetQuadTrim(Magnet):

    def __init__(self, maname, dipole, family, **kwargs):
        kwargs['magfunc'] = 'quadrupole'
        super().__init__(**kwargs)
        self._maname = _SiriusPVName(maname)
        self._magnet_dipole = dipole
        self._magnet_family = family

    def get_kl(self, current_attr):
        brho = self._magnet_dipole.get_brho(current_attr=current_attr)
        infield_family = self._magnet_family.get_intfield(current_attr=current_attr)
        infield_trim = self.get_intfield(current_attr=current_attr)
        intfield = infield_family + infield_trim
        kl = -intfield / brho
        return kl

    def conv_kl_2_current(self, kl):
        brho = self._magnet_dipole.get_brho(current_attr='current_sp')
        intfield = -kl * brho
        infield_family = self._magnet_family.get_intfield(current_attr='current_sp')
        intfield_trim = intfield - intfield_family
        mf = Magnet._magfuncs[self._magfunc]
        interp_mult2curr = self.psmain.psdata.excdata.interp_mult2curr
        current = interp_mult2curr(intfield_trim, mf['harmonic'], mf['type'],
                                   left=self._left, right=self._right)
        return current


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
                               controller_dipole=None,
                               controller_family=None,
                               lock=True,
                               **kwargs
                               ):
        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(self._maname)
        super().__init__(psnames=self._get_psnames(),
                         use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         connection_timeout=connection_timeout,
                         lock=lock,
                         **kwargs)
        self._controller_dipole = controller_dipole
        self._controller_family = controller_family
        self._callback_indices = {}
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
        return self._madata.magfunc(self._madata.psnames[0])

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

    def _init_pwrsupply(self, use_vaca, vaca_prefix,
                              connection_timeout):
        sector, dipole_maname = _MAStrength.get_dipole_sector_maname(maname=self._maname)
        if self.magfunc == 'dipole' and self._maname.subsection == 'Fam':
            self._strobj = _MAStrengthDip(maname=dipole_maname)
            self._currents_sp  = {}
            self._currents_ref = {}
            self._currents_load = {}
        else:
            madata_dipole = _MAData(maname=dipole_maname)
            if self._controller_dipole is None:
                self._controller_dipole = _ControllerEpics(psname=madata_dipole.psnames[0],
                                                           use_vaca=use_vaca,
                                                           vaca_prefix=vaca_prefix,
                                                           connection_timeout=connection_timeout)
            self._callback_indices['dipole'] = self._controller_dipole.add_callback(self._mycallback_dipole)
            if self._maname.subsection == 'Fam' or self.magfunc in ('quadrupole-skew',
                                                                    'corrector-horizontal',
                                                                    'corrector-vertical'):
                self._strobj = _MAStrength(maname=self._maname)
                self._currents_sp   = {'current_dipole':self._controller_dipole.current_sp}
                self._currents_ref  = {'current_dipole':self._controller_dipole.current_ref}
                self._currents_load = {'current_dipole':self._controller_dipole.current_load}
            elif self.magfunc in ('quadrupole'):
                pvname = _SiriusPVName(self._psnames[0])
                family = pvname.replace(pvname.subsection, 'Fam')
                if self._controller_family is None:
                    self._controller_family = _ControllerEpics(psname=family,
                                                               use_vaca=use_vaca,
                                                               vaca_prefix=vaca_prefix,
                                                               connection_timeout=connection_timeout)
                self._callback_indices['family'] = self._controller_family.add_callback(self._mycallback_family)
                self._strobj = _MAStrengthTrim(maname=self._maname)
                self._currents_sp   = {'current_dipole':self._controller_dipole.current_sp,
                                       'current_family':self._controller_family.current_sp}
                self._currents_ref  = {'current_dipole':self._controller_dipole.current_ref,
                                       'current_family':self._controller_family.current_ref}
                self._currents_load = {'current_dipole':self._controller_dipole.current_load,
                                       'current_family':self._controller_family.current_load}

    def __del__(self):
        for typ,index in self._callback_indices.items():
            if typ == 'dipole' and self._controller_dipole is not None:
                self._controller_dipole.remove_callback(index=index)
            elif typ == 'family' and self._controller_family is not None:
                self._controller_family.remove_callback(index=index)
        if hasattr(super(), '__del__'):
            super().__del__()

    def _get_database(self, prefix=''):
        """Return an updated  PV database whose keys correspond to PS properties."""
        db = self._madata._propty_databases[self._psnames[0]]
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
        db['WfmLabel-SP']['value'] = self.wfmlabel_sp
        db['WfmLabel-RB']['value'] = self.wfmlabel_rb
        db['WfmLabels-Mon']['value'] = self.wfmlabels_mon
        db['WfmData-SP']['value'] = self.wfmdata_sp
        db['WfmData-RB']['value'] = self.wfmdata_rb
        db['WfmSave-Cmd']['value']= self.wfmsave_cmd
        db['WfmIndex-Mon']['value'] = self.wfmindex_mon
        db['Current-SP']['value'] = self.current_sp
        db['Current-RB']['value'] = self.current_rb
        db['CurrentRef-Mon']['value'] = self.currentref_mon
        db['Current-Mon']['value'] = self.current_mon
        db['Intlk-Mon']['value'] = self.intlk_mon

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

        # Set strength values
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
        self._currents_sp['current'] = value
        self._strength_sp = self._strobj.conv_current_2_strength(**self._currents_sp)

    def _mycallback(self, pvname, value, **kwargs):
        for psname in self._psnames:
            pvname = pvname.replace(psname, self._maname)
        # Callbacks for strength: _rb, ref_mon, _mon
        for callback in self._callbacks.values():
            slot = ':'.join(pvname.split(':')[:2])
            # Callbacks to update strngth PVs
            strength = self._get_strength_string()
            if 'Current-RB' in pvname:
                callback(slot + ':' + strength + '-RB',
                         self.strength_rb, **kwargs)
            elif 'CurrentRef-Mon' in pvname:
                callback(slot + ':' + strength + 'Ref-Mon',
                         self.strengthref_mon, **kwargs)
            elif 'Current-Mon' in pvname:
                callback(slot + ':' + strength + '-Mon', self.strength_mon, **kwargs)
        super()._mycallback(pvname, value, **kwargs)

    def _get_strength_string(self):
        if self.magfunc in ('dipole'):
            return "Energy"
        elif self.magfunc in ('quadrupole', 'quadrupole-skew'):
            return "KL"
        elif self.magfunc in ('corrector-horizontal', 'corrector-vertical'):
            return "Kick"
        elif self.magfunc in ('sextupole',):
            return "SL"
        else:
            raise ValueError("No such strength")

    def _mycallback_dipole(self, pvname, value, **kwargs):
        """Callback used for dipole PVs updates."""
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
        if run_callback and self._callbacks:
            # signals up changes in strengths
            if self.magfunc in ('quadrupole','quadrupole-skew'):
                pfield = pvname.split(':')[-1].replace("Current", "KL")
            elif self.magfunc in ('corrector-horizontal', 'corrector-vertical'):
                pfield = pvname.split(':')[-1].replace("Current", "Kick")
            elif self.magfunc in ('sextupole',):
                pfield = pvname.split(':')[-1].replace("Current", "SL")
            for callback in self._callbacks.values():
                callback(self._maname + ':' + pfield, new_value, **kwargs)

    def _mycallback_family(self, pvname, value, **kwargs):
        """Callback used for family PVs updates."""
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
        if run_callback and self._callbacks:
            # signals up changes in strengths
            if self.magfunc in ('quadrupole','quadrupole-skew'):
                pfield = pvname.split(':')[-1].replace("Current", "KL")
            elif self.magfunc in ('corrector-horizontal', 'corrector-vertical'):
                pfield = pvname.split(':')[-1].replace("Current", "Kick")
            elif self.magfunc in ('sextupole',):
                pfield = pvname.split(':')[-1].replace("Current", "SL")
            for callback in self._callbacks.values():
                callback(self._maname + ':' + pfield, new_value, **kwargs)
