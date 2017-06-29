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
import numpy as _np
from siriuspy import util as _util
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply.controller import ControllerEpics as _ControllerEpics
from siriuspy.pwrsupply.model import PowerSupplyEpicsSync \
    as _PowerSupplyEpicsSync
from siriuspy.magnet import util as _mutil
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.magnet.data import MAData as _MAData
from siriuspy.magnet.data import MAStrengthDip as _MAStrengthDip
from siriuspy.magnet.data import MAStrength as _MAStrength
from siriuspy.magnet.data import MAStrengthTrim as _MAStrengthTrim
from abc import abstractmethod as _abstractmethod
from abc import ABCMeta as _ABCMeta

_connection_timeout = None

_magfuncs = _mutil.get_magfunc_2_multipole_dict()


class _MagnetPowerSupply(_PowerSupplyEpicsSync):

    def __init__(self, maname,
                 use_vaca=False,
                 vaca_prefix=None,
                 callback=None,
                 connection_timeout=None,
                 left='linear',
                 right='linear'):

        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(maname=self._maname)
        self._magfunc = self._madata.magfunc(self._madata.psnames[0])
        self._left = left
        self._right = right
        self._mfmult = _magfuncs[self.magfunc]
        self._strength_label = self._get_strength_label()
        self._init_subclass()

        super().__init__(psnames=self._madata.psnames,
                         use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         lock=True)

    def _init_propty(self):
        super()._init_propty()
        self._propty[self._strength_label + '-SP'] = None
        self._propty[self._strength_label + '-RB'] = None
        self._propty[self._strength_label + 'Ref-Mon'] = None
        self._propty[self._strength_label + '-Mon'] = None

    def _init_subclass(self):
        raise NotImplementedError

    @property
    def magfunc(self):
        return self._magfunc

    @property
    def current_sp(self):
        return self._propty['Current-SP']

    @current_sp.setter
    def current_sp(self, value):
        value = float(value)
        self._set_current_sp(value)
        kwargs = self._get_currents_dict('Current-SP')
        strength = self.conv_current_2_strength(value, **kwargs)
        self._propty[self._strength_label + '-SP'] = strength
        pvname = self._maname + ':' + self._strength_label + '-SP'
        self._trigger_callback(pvname, strength)

    @property
    def strength_sp(self):
        return self._propty[self._strength_label+'-SP']

    @strength_sp.setter
    def strength_sp(self, value):
        value = float(value)
        self._propty[self._strength_label + '-SP'] = value
        pvname = self._maname + ':' + self._strength_label + '-SP'
        self._trigger_callback(pvname, value)
        kwargs = self._get_currents_dict('Current-SP')
        current = self.conv_strength_2_current(value, **kwargs)
        #self.current_sp = current
        self._set_current_sp(current)

    @property
    def strength_rb(self):
        return self._propty[self._strength_label+'-RB']

    @property
    def strengthref_mon(self):
        return self._propty[self._strength_label+'Ref-Mon']

    @property
    def strength_mon(self):
        return self._propty[self._strength_label+'-Mon']

    def _get_strength_label(self):
        if self.magfunc == 'dipole':
            return 'Energy'
        elif self.magfunc in ('quadrupole', 'quarupole-skew'):
            return 'KL'
        elif self.magafunc in ('sextupole',):
            return 'SL'
        elif self.magafunc in ('corrector-horizontal', 'corrector-vertical'):
            return 'Kick'

    def conv_current_2_multipoles(self, current):
        if current is None:
            return None
        msum = {}
        if self.magfunc != 'dipole':
            for psname in self._madata.psnames:
                excdata = self._madata.excdata(psname)
                m = excdata.interp_curr2mult(current, left=self._left, right=self._right)
                msum = _mutil.sum_magnetic_multipoles(msum, m)
        else:
            excdata = self._madata.excdata(self._psname_master)
            m = excdata.interp_curr2mult(current, left=self._left, right=self._right)
            msum = _mutil.sum_magnetic_multipoles(msum, m)
        return msum

    def conv_current_2_intfield(self, current):
        m = self.conv_current_2_multipoles(current)
        if m is None:
            return None
        mf = self._mfmult
        intfield = m[mf['type']][mf['harmonic']]
        return intfield

    def conv_current_2_strength(self, current, **kwargs):
        intfield = self.conv_current_2_intfield(current)
        if intfield is None:
            return None
        strength = self.conv_intfield_2_strength(intfield, **kwargs)
        return strength

    def get_brho(self, current_dipole):
        """Get Magnetic Rigidity."""
        energy = self._get_energy(current_dipole)
        brho = _util.beam_rigidity(energy)
        return brho

    def conv_strength_2_current(self, strength, **kwargs):
        intfield = self.conv_strength_2_intfield(strength, **kwargs)
        mf = self._mfmult
        # excdata = self._get_main_excdata()
        excdata = self._madata.excdata(self._psname_master)
        current = excdata.interp_mult2curr(intfield, mf['harmonic'], mf['type'], left=self._left, right=self._right)
        return current

    def _trigger_callback(self, pvname, value, **kwargs):
        *parts, propty = pvname.split(':')
        pvname = self._maname + ':' + propty
        for callback in self._callbacks.values():
            callback(pvname, value, **kwargs)

    def _callback_change_sp_pv(self, pvname, value, **kwargs):
        #*parts, propty = pvname.split(':')
        #pvname = self._maname + ':' + propty
        super()._callback_change_sp_pv(pvname, value, **kwargs)
        # invoking callback for strength sp
        label = self._strength_label
        *parts, propty = pvname.split(':')
        if self._propty[label+'-SP'] is None and propty == 'Current-SP':
            propty_strength = propty.replace('Current', label)
            kwargs = self._get_currents_dict('Current-SP')
            #print(); print(); print('sp kwargs: ', kwargs)
            strength = self.conv_current_2_strength(value, **kwargs)
            if strength is not None:
                self._propty[propty_strength] = strength
                pvname = self._maname + ':'+label+'-SP'
                self._trigger_callback(pvname, strength, **kwargs)

    def _callback_change_rb_pv(self, pvname, value, **kwargs):
        #*parts, propty = pvname.split(':')
        #pvname = self._maname + ':' + propty
        super()._callback_change_rb_pv(pvname, value, **kwargs)
        # invoking callback for strength sp
        *parts, propty = pvname.split(':')
        if "Current" in propty:
            label = self._strength_label
            propty_strength = propty.replace('Current', label)
            kwargs = self._get_currents_dict(propty)
            #print(); print(); print('rb kwargs: ', kwargs)
            strength = self.conv_current_2_strength(value, **kwargs)
            if strength is not None:
                self._propty[propty_strength] = strength
                pvname = self._maname + ':' + propty_strength
                self._trigger_callback(pvname, strength, **kwargs)

    def _get_database(self, prefix=''):
        """Return an updated PV database. Keys correspond to PS properties."""
        db = self._madata._propty_databases[self._psnames[0]]
        # value = self.ctrlmode_mon
        # db['CtrlMode-Mon']['value'] = _et.enums('RmtLocTyp').index(value) \
        #     if self._enum_keys else value
        value = self.opmode_sel
        db['OpMode-Sel']['value'] = _et.enums('PSOpModeTyp').index(value) \
            if self._enum_keys else value
        value = self.opmode_sts
        db['OpMode-Sts']['value'] = _et.enums('PSOpModeTyp').index(value) \
            if self._enum_keys else value
        value = self.pwrstate_sel
        db['PwrState-Sel']['value'] = _et.enums('OffOnTyp').index(value) \
            if self._enum_keys else value
        value = self.pwrstate_sts
        db['PwrState-Sts']['value'] = _et.enums('OffOnTyp').index(value) \
            if self._enum_keys else value
        # db['Reset-Cmd']['value'] = self.reset
        # db['Abort-Cmd']['value'] = self.abort
        # wfmlabels = self._get_wfmlabels_mon()
        # db['WfmLoad-Sel']['enums'] = wfmlabels
        # db['WfmLoad-Sts']['enums'] = wfmlabels
        # value = self.wfmload_sel
        # db['WfmLoad-Sel']['value'] = _np.where(wfmlabels == value)[0][0] \
        #     if self._enum_keys else value
        # value = self.wfmload_sts
        # db['WfmLoad-Sts']['value'] = _np.where(wfmlabels == value)[0][0] \
        #     if self._enum_keys else value
        # db['WfmLabel-SP']['value'] = self.wfmlabel_sp
        # db['WfmLabel-RB']['value'] = self.wfmlabel_rb
        # db['WfmLabels-Mon']['value'] = self.wfmlabels_mon
        # db['WfmData-SP']['value'] = self.wfmdata_sp
        # db['WfmData-RB']['value'] = self.wfmdata_rb
        # db['WfmSave-Cmd']['value'] = self.wfmsave_cmd
        # db['WfmIndex-Mon']['value'] = self.wfmindex_mon
        db['Current-SP']['value'] = self.current_sp
        db['Current-RB']['value'] = self.current_rb
        db['CurrentRef-Mon']['value'] = self.currentref_mon
        db['Current-Mon']['value'] = self.current_mon
        # db['Intlk-Mon']['value'] = self.intlk_mon

        label = self._strength_label

        # Set strength values
        db[label + '-SP']['value'] = self.strength_sp
        db[label + '-RB']['value'] = self.strength_rb
        db[label + 'Ref-Mon']['value'] = self.strengthref_mon
        db[label + '-Mon']['value'] = self.strength_mon

        prefixed_db = dict()
        for key, value in db.items():
            prefixed_db[prefix + ':' + key] = value

        return prefixed_db


    # --- methods below this line need implementation in subclasses
    def _get_main_excdata(self):
        #return self._madata.excdata(self._psname_master)
        raise NotImplementedError

    def _get_currents_dict(self, current_attr):
        #return {}
        raise NotImplementedError

    def _get_energy(self, current_dipole):

        raise NotImplementedError

    def conv_intfield_2_strength(self, intfield, **kwargs):
        # if self._maname.section == 'SI':
        #     strength = (self._ref_energy / self._ref_brho) * (- intfield - self._ref_BL_BC) / self._ref_angle
        # else:
        #     strength = (self._ref_energy / self._ref_brho) * (-intfield) / self._ref_angle
        raise NotImplementedError

    def conv_strength_2_intfield(self, strength, **kwargs):
        # if self._maname.section == 'SI':
        #     intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * strength - self._ref_BL_BC
        # else:
        #     intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * strength
        raise NotImplementedError


class MagnetPowerSupplyDipole(_MagnetPowerSupply):

    _ref_angles = {
        'SI_BC': _math.radians(4.2966),
        'SI_B1': _math.radians(2.7553),
        'SI_B2': _math.radians(4.0964),
        'TS': _math.radians(5.3333),
        'BO': _math.radians(7.2000),
        'TB': _math.radians(15.000),
    }

    def _init_subclass(self):
        self._set_reference_dipole_data()

    def _set_reference_dipole_data(self):
        ang = MagnetPowerSupplyDipole._ref_angles
        if self._maname.section == 'SI':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_BL_BC = - self._ref_brho * ang['SI_BC']
            self._ref_angle = ang['SI_B1'] + ang['SI_B2'] + ang['SI_BC']
            self._ref_BL = - self._ref_brho * self._ref_angle - self._ref_BL_BC
        elif self._maname.section == 'BO':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['BO']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif self._maname.section == 'TS':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TS']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif self._maname.section == 'TB':
            self._ref_energy = 0.150  # [GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TB']
            self._ref_BL = - self._ref_brho * self._ref_angle
        else:
            raise NotImplementedError

    def _get_main_excdata(self):
        return self._madata.excdata(self._psname_master)

    def _get_currents_dict(self, current_attr):
        return {}

    def _get_energy(self, current_dipole):
        return self.conv_current_2_strength(current=current_dipole)

    def conv_strength_2_intfield(self, strength, **kwargs):
        if self._maname.section == 'SI':
            intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * strength - self._ref_BL_BC
        else:
            intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * strength
        return intfield

    def conv_intfield_2_strength(self, intfield, **kwargs):
        if self._maname.section == 'SI':
            strength = (self._ref_energy / self._ref_brho) * (- intfield - self._ref_BL_BC) / self._ref_angle
        else:
            strength = (self._ref_energy / self._ref_brho) * (-intfield) / self._ref_angle
        return strength



class MagnetPowerSupply(_MagnetPowerSupply):

    def __init__(self, maname, dipole, **kwargs):
        self._dipole = dipole
        self._dipole.add_callback(self._callback_dipole_updated)
        super().__init__(maname, **kwargs)

    def _init_subclass(self):
        pass

    def _get_main_excdata(self):
        psname = self._maname.replace(':MA-',':PS-')
        return self._madata.excdata(psname)

    def _get_currents_dict(self, current_attr):
        if current_attr == 'Current-SP':
            current = self._dipole.current_sp
        elif current_attr == 'Current-RB':
            current = self._dipole.current_rb
        elif current_attr == 'CurrentRef-Mon':
            current = self._dipole.currentref_mon
        elif current_attr == 'Current-Mon':
            current = self._dipole.current_mon
        else:
            raise ValueError('Invalid argument "' + str(current_attr) + '" to _get_currents_dict!')
        return {'current_dipole':current}

    def _get_energy(self, current_dipole):
        return self._dipole.conv_current_2_strength(current=current_dipole)

    def conv_strength_2_intfield(self, strength, **kwargs):
        brho = self.get_brho(current_dipole=kwargs['current_dipole'])
        intfield = - brho * strength
        return intfield

    def conv_intfield_2_strength(self, intfield, **kwargs):
        brho = self.get_brho(current_dipole=kwargs['current_dipole'])
        strength = - intfield / brho
        return strength

    def _callback_dipole_updated(self, pvname, value, **kwargs):
        # Get dipole new current and update self current value
        label = self._strength_label
        *parts, propty = pvname.split(':')
        if 'Current' in propty:
            strength = self.conv_current_2_strength(current=self._propty[propty], current_dipole=value)
            propty_strength = propty.replace('Current', label)
            print(propty_strength, strength)
            self._propty[propty_strength] = strength
            pvname = self._maname + ':' + propty_strength
            self._trigger_callback(pvname, strength)







class MagnetPowerSupplyDipoleOld(_PowerSupplyEpicsSync):
    """Class responsible for controlling a Magnet of type dipole."""

    _ref_angles = {
        'SI_BC': _math.radians(4.2966),
        'SI_B1': _math.radians(2.7553),
        'SI_B2': _math.radians(4.0964),
        'TS'   : _math.radians(5.3333),
        'BO'   : _math.radians(7.2000),
        'TB'   : _math.radians(15.000),
    }

    def __init__(self, maname,
                 use_vaca=False,
                 vaca_prefix=None,
                 callback=None,
                 connection_timeout=None,
                 left='linear',
                 right='linear'):
        """Class Constructor."""
        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(maname=self._maname)
        self._set_reference_dipole_data()
        self._left = left
        self._right = right

        super().__init__(psnames=self._madata.psnames,
                         use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         lock=True)
                        #  callback=callback,
                        #  connection_timeout=connection_timeout)

    def _init_propty(self):
        super()._init_propty()
        self._propty['Energy-SP'] = None
        self._propty['Energy-RB'] = None
        self._propty['EnergyRef-Mon'] = None
        self._propty['Energy-Mon'] = None

    def _set_reference_dipole_data(self):
        ang = MagnetPowerSupplyDipole._ref_angles
        if self._maname.section == 'SI':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_BL_BC = - self._ref_brho * ang['SI_BC']
            self._ref_angle = ang['SI_B1'] + ang['SI_B2'] + ang['SI_BC']
            self._ref_BL = - self._ref_brho * self._ref_angle - self._ref_BL_BC
        elif self._maname.section == 'BO':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['BO']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif self._maname.section == 'TS':
            self._ref_energy = 3.0  # [GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TS']
            self._ref_BL = - self._ref_brho * self._ref_angle
        elif self._maname.section == 'TB':
            self._ref_energy = 0.150  # [GeV]
            self._ref_brho = _util.beam_rigidity(self._ref_energy)
            self._ref_angle = ang['TB']
            self._ref_BL = - self._ref_brho * self._ref_angle
        else:
            raise NotImplementedError

    def conv_current_2_multipoles(self, current):
        msum = {}
        # for psname in self._madata.psnames:
        #     excdata = self._madata.excdata(psname)
        #     m = excdata.interp_curr2mult(current)
        #     msum = _mutil.sum_magnetic_multipoles(msum, m)
        excdata = self._madata.excdata(self._psname_master)
        m = excdata.interp_curr2mult(current, left=self._left, right=self._right)
        msum = _mutil.sum_magnetic_multipoles(msum, m)
        return msum

    def conv_current_2_intfield(self, current):
        m = self.conv_current_2_multipoles(current)
        mf = _magfuncs['dipole']
        intfield = m[mf['type']][mf['harmonic']]
        return intfield

    def conv_current_2_strength(self, current):
        intfield = self.conv_current_2_intfield(current)
        if self._maname.section == 'SI':
            strength = (self._ref_energy / self._ref_brho) * (- intfield - self._ref_BL_BC) / self._ref_angle
        else:
            strength = (self._ref_energy / self._ref_brho) * (-intfield) / self._ref_angle
        return strength

    def conv_current_2_brho(self, current):
        """Get Magnetic Rigidity."""
        energy = self.conv_current_2_strength(current=current)
        brho = _util.beam_rigidity(energy)
        return brho

    def conv_strength_2_current(self, strength):
        if self._maname.section == 'SI':
            intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * strength - self._ref_BL_BC
        else:
            intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * strength
        mf = _magfuncs['dipole']
        excdata = self._madata.excdata(self._psname_master)
        current = excdata.interp_mult2curr(intfield, mf['harmonic'], mf['type'],
                                   left=self._left, right=self._right)
        return current

    @property
    def current_sp(self):
        return self._propty['Current-SP']

    @current_sp.setter
    def current_sp(self, value):
        self._set_current_sp(value)
        strength = self.conv_current_2_strength(value)
        self._propty['Energy-SP'] = strength
        pvname = self._maname + ':' + 'Energy-SP'
        self._trigger_callback(pvname, strength)

    @property
    def strength_sp(self):
        """Return strength set point."""
        return self._propty['Energy-SP']

    @strength_sp.setter
    def strength_sp(self, value):
        value = float(value)
        self._propty['Energy-SP'] = value
        self.current_sp = self.conv_strength_2_current(value)
        pvname = self._maname + ':' + 'Energy-SP'
        self._trigger_callback(pvname, value)

    @property
    def strength_rb(self):
        """Return strength readback."""
        return self._propty['Energy-RB']

    @property
    def strengthref_mon(self):
        """Return strength ref mon."""
        return self._propty['EnergyRef-Mon']

    @property
    def strength_mon(self):
        """Return strength mon."""
        return self._propty['Energy-Mon']

    def _trigger_callback(self, pvname, value, **kwargs):
        for callback in self._callbacks.values():
            pvname = pvname.replace(":PS", ":MA")
            pvname = pvname.replace("-1", "")
            pvname = pvname.replace("-2", "")
            callback(pvname, value, **kwargs)

    def _callback_change_sp_pv(self, pvname, value, **kwargs):
        super()._callback_change_sp_pv(pvname, value, **kwargs)
        *parts, propty = pvname.split(':')
        if self._propty['Energy-SP'] is None and propty == 'Current-SP':
            propty_strength = propty.replace('Current','Energy')
            strength = self.conv_current_2_strength(value)
            self._propty[propty_strength] = strength
            pvname = self._maname + ':Energy-SP'
            self._trigger_callback(pvname, strength, **kwargs)

    def _callback_change_rb_pv(self, pvname, value, **kwargs):
        super()._callback_change_rb_pv(pvname, value, **kwargs)
        *parts, propty = pvname.split(':')
        if "Current" in propty:
            propty_strength = propty.replace('Current','Energy')
            strength = self.conv_current_2_strength(value)
            self._propty[propty_strength] = strength
            pvname = self._maname + ':' + propty_strength
            self._trigger_callback(pvname, strength, **kwargs)

    def _get_database(self, prefix=''):
        """Return an updated PV database. Keys correspond to PS properties."""
        db = self._madata._propty_databases[self._psnames[0]]
        # value = self.ctrlmode_mon
        # db['CtrlMode-Mon']['value'] = _et.enums('RmtLocTyp').index(value) \
        #     if self._enum_keys else value
        value = self.opmode_sel
        db['OpMode-Sel']['value'] = _et.enums('PSOpModeTyp').index(value) \
            if self._enum_keys else value
        value = self.opmode_sts
        db['OpMode-Sts']['value'] = _et.enums('PSOpModeTyp').index(value) \
            if self._enum_keys else value
        value = self.pwrstate_sel
        db['PwrState-Sel']['value'] = _et.enums('OffOnTyp').index(value) \
            if self._enum_keys else value
        value = self.pwrstate_sts
        db['PwrState-Sts']['value'] = _et.enums('OffOnTyp').index(value) \
            if self._enum_keys else value
        # db['Reset-Cmd']['value'] = self.reset
        # db['Abort-Cmd']['value'] = self.abort
        # wfmlabels = self._get_wfmlabels_mon()
        # db['WfmLoad-Sel']['enums'] = wfmlabels
        # db['WfmLoad-Sts']['enums'] = wfmlabels
        # value = self.wfmload_sel
        # db['WfmLoad-Sel']['value'] = _np.where(wfmlabels == value)[0][0] \
        #     if self._enum_keys else value
        # value = self.wfmload_sts
        # db['WfmLoad-Sts']['value'] = _np.where(wfmlabels == value)[0][0] \
        #     if self._enum_keys else value
        # db['WfmLabel-SP']['value'] = self.wfmlabel_sp
        # db['WfmLabel-RB']['value'] = self.wfmlabel_rb
        # db['WfmLabels-Mon']['value'] = self.wfmlabels_mon
        # db['WfmData-SP']['value'] = self.wfmdata_sp
        # db['WfmData-RB']['value'] = self.wfmdata_rb
        # db['WfmSave-Cmd']['value'] = self.wfmsave_cmd
        # db['WfmIndex-Mon']['value'] = self.wfmindex_mon
        db['Current-SP']['value'] = self.current_sp
        db['Current-RB']['value'] = self.current_rb
        db['CurrentRef-Mon']['value'] = self.currentref_mon
        db['Current-Mon']['value'] = self.current_mon
        # db['Intlk-Mon']['value'] = self.intlk_mon

        strength = "Energy"

        # Set strength values
        db[strength + '-SP']['value'] = self.strength_sp
        db[strength + '-RB']['value'] = self.strength_rb
        db[strength + 'Ref-Mon']['value'] = self.strengthref_mon
        db[strength + '-Mon']['value'] = self.strength_mon

        prefixed_db = dict()
        for key, value in db.items():
            prefixed_db[prefix + ':' + key] = value

        return prefixed_db


class MagnetPowerSupplyOld(_PowerSupplyEpicsSync):
    """Class responsible for controlling family and individual magnets."""

    def __init__(self, maname, dipole,
                 use_vaca=False,
                 vaca_prefix=None,
                 callback=None,
                 connection_timeout=None):
        """Class constructor."""
        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(maname=self._maname)
        self._magfunc = self._madata.magfunc(self._madata.psnames[0])

        if self._magfunc in ('quadrupole', 'quadrupole-skew'):
            self._strength = "KL"
        elif self._magfunc == 'sextupole':
            self._strength = "SL"
        elif self._magfunc in ("corrector-vertical", "corrector-horizontal"):
            self._strength = "Kick"

        self._dipole = dipole
        self._dipole.add_callback(self._dipole_updated)

        # super().__init__(maname=maname, use_vaca=use_vaca,
        #                  vaca_prefix=vaca_prefix,
        #                  lock=True,
        #                  callback=callback,
        #                  connection_timeout=connection_timeout)
        super().__init__(psnames=[self._maname.replace(":MA", ":PS")],
                         use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         lock=True)
                         #callback=callback,
                         #connection_timeout=connection_timeout)

        self._propty['Strength-SP'] = self._conv_current_2_strength(
            self.current_sp, self._dipole.current_sp) if self.current_sp is not None else None
        self._propty['Strength-RB'] = self._conv_current_2_strength(
            self.current_rb, self._dipole.current_rb) if self.current_rb is not None else None
        self._propty['StrengthRef-Mon'] = self._conv_current_2_strength(
            self.currentref_mon, self._dipole.currentref_mon) if self.currentref_mon is not None else None
        self._propty['Strength-Mon'] = self._conv_current_2_strength(
            self.current_mon, self._dipole.current_mon) if self.current_mon is not None else None

    # def conv_current_2_multipoles(self, current):
    #     msum = {}
    #     for psname in self._madata.psnames:
    #         excdata = self._madata.excdata(psname)
    #         m = excdata.interp_curr2mult(current)
    #         msum = _mutil.sum_magnetic_multipoles(msum, m)
    #     return msum
    #
    # def conv_current_2_intfield(self, current):
    #     m = self.conv_current_2_multipoles(current)
    #     mf = _magfuncs['dipole']
    #     intfield = m[mf['type']][mf['harmonic']]
    #     return intfield
    #
    # def conv_current_2_strength(self, current):
    #     intfield = self.conv_current_2_intfield(current)
    #     if self._maname.section == 'SI':
    #         strength = (self._ref_energy / self._ref_brho) * (- intfield - self._ref_BL_BC) / self._ref_angle
    #     else:
    #         strength = (self._ref_energy / self._ref_brho) * (-intfield) / self._ref_angle
    #     return strength
    #
    # def conv_current_2_brho(self, current):
    #     """Get Magnetic Rigidity."""
    #     energy = self.conv_current_2_strength(current=current)
    #     brho = _util.beam_rigidity(energy)
    #     return brho
    #
    # def conv_strength_2_current(self, strength):
    #     if self._maname.section == 'SI':
    #         intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * strength - self._ref_BL_BC
    #     else:
    #         intfield = - self._ref_angle * (self._ref_brho / self._ref_energy) * strength
    #     mf = _magfuncs['dipole']
    #     excdata = self._madata.excdata(self._psname_master)
    #     current = excdata.interp_mult2curr(intfield, mf['harmonic'], mf['type'],
    #                                left=self._left, right=self._right)
    #     return current

    def _conv_current_2_strength(self, current, dipole_current):
        if current is None:
            return 0
        intfield = current/2.0
        brho = self._dipole.conv_current_2_brho(dipole_current)
        return intfield/brho

    def _conv_strength_2_current(self, strength, dipole_current):
        brho = self._dipole.conv_current_2_brho(dipole_current)
        intfield = strength*brho
        return intfield*2

    @property
    def strength_sp(self):
        """Return strength set point."""
        return self._propty['Strength-SP']

    @strength_sp.setter
    def strength_sp(self, value):
        current = self._conv_strength_2_current(value, self._dipole.current_sp)
        self.current_sp = current

    @property
    def strength_rb(self):
        """Return strength readback."""
        return self._propty['Strength-RB']

    @property
    def strengthref_mon(self):
        """Return strength ref mon."""
        return self._propty['StrengthRef-Mon']

    @property
    def strength_mon(self):
        """Return strength mon."""
        return self._propty['Strength-Mon']

    def _set_current_sp(self, value):
        super()._set_current_sp(value)
        self._set_strength_sp(value, self._dipole.current_sp)

    def _set_strength_sp(self, value, current_dipole):
        self._propty['Strength-SP'] = self._conv_current_2_strength(
            value, current_dipole)

    def _trigger_callback(self, pvname, value, **kwargs):
        for callback in self._callbacks.values():
            callback(pvname.replace(":PS", ":MA"), value, **kwargs)

    def _callback_change_sp_pv(self, pvname, value, **kwargs):
        super()._callback_change_sp_pv(pvname, value, **kwargs)
        if "Current" in pvname:
            self._propty['Strength-SP'] = self._conv_current_2_strength(value, self._dipole.current_sp)
            self._trigger_callback(pvname.replace('Current', 'Energy'),
                                   self._propty['Strength-SP'], **kwargs)

    def _callback_change_rb_pv(self, pvname, value, **kwargs):
        super()._callback_change_rb_pv(pvname, value, **kwargs)
        if "Current" in pvname:
            *parts, propty = pvname.split(':')
            current_attr = propty.replace("-", "_").lower()
            attr = "_" + propty.replace("Current", "strength").replace("-", "_").lower()
            strength = self._conv_current_2_strength(value, getattr(self._dipole, current_attr))
            # Set attribute value
            setattr(self, attr, strength)
            # Trigger callbacks
            self._trigger_callback(pvname.replace('Current', self._strength),
                               strength, **kwargs)

    # def _pvchange_current_rb(self, pvname, value, **kwargs):
    #     super()._pvchange_current_rb(pvname, value, **kwargs)
    #     self._propty['Strength-RB'] = self._conv_current_2_strength(
    #         value, self._dipole.current_rb)
    #     self._trigger_callback(
    #         pvname.replace('Current', self._strength),
    #         self._propty['Strength-RB'], **kwargs)
    #
    # def _pvchange_currentref_mon(self, pvname, value, **kwargs):
    #     super()._pvchange_currentref_mon(pvname, value, **kwargs)
    #     self._propty['StrengthRef-Mon'] = self._conv_current_2_strength(
    #         value, self._dipole.currentref_mon)
    #     self._trigger_callback(
    #         pvname.replace(
    #             'Current', self._strength), self._propty['StrengthRef-Mon'], **kwargs)
    #
    # def _pvchange_current_mon(self, pvname, value, **kwargs):
    #     super()._pvchange_current_mon(pvname, value, **kwargs)
    #     self._propty['Strength-Mon'] = self._conv_current_2_strength(
    #         value, self._dipole.current_mon)
    #     self._trigger_callback(
    #         pvname.replace(
    #             'Current', self._strength), self._propty['Strength-Mon'], **kwargs)

    def _dipole_updated(self, pvname, value, **kwargs):
        # Get dipole new current and update self current value
        trigger_callback = False
        new_value = None
        field = None
        if "Current-SP" in pvname:
            self._setpropty['Strength-SP'](self.current_sp, value)
            new_value = self._propty['Strength-SP']
            field = "-SP"
            trigger_callback = True
        if "Current-RB" in pvname:
            self._propty['Strength-RB'] = self._conv_current_2_strength(
                self.current_rb, value)
            new_value = self._propty['Strength-RB']
            field = "-RB"
            trigger_callback = True
        if "CurrentRef-Mon" in pvname:
            self._propty['StrengthRef-Mon'] = self._conv_current_2_strength(
                self.currentref_mon, value)
            new_value = self._propty['StrengthRef-Mon']
            field = "Ref-Mon"
            trigger_callback = True
        if "Current-Mon" in pvname:
            self._propty['Strength-Mon'] = self._conv_current_2_strength(
                self.current_mon, value)
            new_value = self._propty['Strength-Mon']
            field = "-Mon"
            trigger_callback = True

        if trigger_callback:
            self._trigger_callback(
                self._maname + ":" + self._strength + field,
                new_value, **kwargs)

    def _get_database(self, prefix=''):
        """Return an updated PV database."""
        db = self._madata._propty_databases[self._psnames[0]]
        # value = self.ctrlmode_mon
        # db['CtrlMode-Mon']['value'] = _et.enums('RmtLocTyp').index(value) \
        #     if self._enum_keys else value
        value = self.opmode_sel
        db['OpMode-Sel']['value'] = _et.enums('PSOpModeTyp').index(value) \
            if self._enum_keys else value
        value = self.opmode_sts
        db['OpMode-Sts']['value'] = _et.enums('PSOpModeTyp').index(value) \
            if self._enum_keys else value
        value = self.pwrstate_sel
        db['PwrState-Sel']['value'] = _et.enums('OffOnTyp').index(value) \
            if self._enum_keys else value
        value = self.pwrstate_sts
        db['PwrState-Sts']['value'] = _et.enums('OffOnTyp').index(value) \
            if self._enum_keys else value
        # db['Reset-Cmd']['value'] = self.reset
        # db['Abort-Cmd']['value'] = self.abort
        # wfmlabels = self._get_wfmlabels_mon()
        # db['WfmLoad-Sel']['enums'] = wfmlabels
        # db['WfmLoad-Sts']['enums'] = wfmlabels
        # value = self.wfmload_sel
        # db['WfmLoad-Sel']['value'] = _np.where(wfmlabels == value)[0][0] \
        #     if self._enum_keys else value
        # value = self.wfmload_sts
        # db['WfmLoad-Sts']['value'] = _np.where(wfmlabels == value)[0][0] \
        #     if self._enum_keys else value
        # db['WfmLabel-SP']['value'] = self.wfmlabel_sp
        # db['WfmLabel-RB']['value'] = self.wfmlabel_rb
        # db['WfmLabels-Mon']['value'] = self.wfmlabels_mon
        # db['WfmData-SP']['value'] = self.wfmdata_sp
        # db['WfmData-RB']['value'] = self.wfmdata_rb
        # db['WfmSave-Cmd']['value'] = self.wfmsave_cmd
        # db['WfmIndex-Mon']['value'] = self.wfmindex_mon
        db['Current-SP']['value'] = self.current_sp
        db['Current-RB']['value'] = self.current_rb
        db['CurrentRef-Mon']['value'] = self.currentref_mon
        db['Current-Mon']['value'] = self.current_mon
        # db['Intlk-Mon']['value'] = self.intlk_mon

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


class MagnetPowerSupplyTrim(_PowerSupplyEpicsSync):
    """Class responsible for controlling trim magnets."""

    def __init__(self, maname, dipole, fam,
                 use_vaca=False,
                 vaca_prefix=None,
                 callback=None,
                 connection_timeout=None):
        """Class constructor."""
        self._maname = _SiriusPVName(maname)
        self._madata = _MAData(maname=self._maname)
        self._dipole = dipole
        self._dipole.add_callback(self._dipole_updated)
        self._fam = fam
        self._fam.add_callback(self._family_updated)

        if _re.search("(?:QD|QF|Q[0-9]|QS).*", maname):
            self._strength = "KL"
        else:
            raise NotImplementedError("Trims only implemented for quadrupoles")

        super().__init__(psnames=[self._maname.replace(":MA", ":PS")],
                         use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         lock=True)
        # super().__init__(maname=maname, use_vaca=use_vaca,
        #                  vaca_prefix=vaca_prefix,
        #                  lock=True,
        #                  callback=callback,
        #                  connection_timeout=connection_timeout)

        self._propty['Strength-SP'] = self._conv_current_2_strength(
            self.current_sp, self._dipole.current_sp, self._fam.current_sp) if self.current_sp is not None else None
        self._propty['Strength-RB'] = self._conv_current_2_strength(
            self.current_rb, self._dipole.current_rb, self._fam.current_rb) if self.current_rb is not None else None
        self._propty['StrengthRef-Mon'] = self._conv_current_2_strength(
            self.currentref_mon, self._dipole.currentref_mon,
            self._fam.currentref_mon) if self.currentref_mon is not None else None
        self._propty['Strength-Mon'] = self._conv_current_2_strength(
            self.current_mon, self._dipole.current_mon, self._fam.current_mon) if self.current_mon is not None else None

    def _conv_current_2_strength(self, current, current_dipole, current_fam):
        if current is None:
            return 0
        intfield_trim = current/2.0
        brho = self._dipole.conv_current_2_brho(current_dipole)
        strength_trim = intfield_trim/brho
        strength_fam = self._fam._conv_current_2_strength(
            current_fam, current_dipole)
        return strength_fam + strength_trim

    def _conv_strength_2_current(self, strength, current_dipole, current_fam):
        strength_fam = self._fam._conv_current_2_strength(
            current_fam, current_dipole)
        strength_trim = strength - strength_fam
        brho = self._dipole.conv_current_2_brho(current_dipole)
        intfield = strength_trim*brho
        return intfield*2

    @property
    def strength_sp(self):
        """Return strength set point."""
        return self._propty['Strength-SP']

    @strength_sp.setter
    def strength_sp(self, value):
        current = self._conv_strength_2_current(
            value, self._dipole.current_sp, self._fam.current_sp)
        self.current_sp = current

    @property
    def strength_rb(self):
        """Return strength readback."""
        return self._propty['Strength-RB']

    @property
    def strengthref_mon(self):
        """Return strength ref mon."""
        return self._propty['StrengthRef-Mon']

    @property
    def strength_mon(self):
        """Return strength monitor value."""
        return self._propty['Strength-Mon']

    def _set_current_sp(self, value):
        super()._set_current_sp(value)
        self._set_strength_sp(
            value, self._dipole.current_sp, self._fam.current_sp)

    def _setpropty_strength_sp(self, value, current_dipole, current_fam):
        self._propty['Strength-SP'] = self._conv_current_2_strength(
            value, current_dipole, current_fam)

    def _trigger_callback(self, pvname, value, **kwargs):
        for callback in self._callbacks.values():
            callback(pvname.replace(":PS", ":MA"), value, **kwargs)

    def _callback_change_sp_pv(self, pvname, value, **kwargs):
        super()._callback_change_sp_pv(pvname, value, **kwargs)
        if "Current" in pvname:
            self._propty['Strength-SP'] = self._conv_current_2_strength(
                value, self._dipole.current_sp, self._fam.current_sp)
            self._trigger_callback(pvname.replace('Current', 'Energy'),
                                   self._propty['Strength-SP'], **kwargs)

    def _callback_change_rb_pv(self, pvname, value, **kwargs):
        super()._callback_change_rb_pv(pvname, value, **kwargs)
        if "Current" in pvname:
            *parts, propty = pvname.split(':')
            current_attr = propty.replace("-", "_").lower()
            strength_attr = "_" + propty.replace("Current", "strength").replace("-", "_").lower()
            strength = self._conv_current_2_strength(
                value,
                getattr(self._dipole, current_attr),
                getattr(self._fam, current_attr))
            # Set attribute value
            setattr(self, strength_attr, strength)
            # Trigger callbacks
            self._trigger_callback(pvname.replace('Current', self._strength),
                               strength, **kwargs)

    # def _pvchange_current_rb(self, pvname, value, **kwargs):
    #     super()._pvchange_current_rb(pvname, value, **kwargs)
    #     self._propty['Strength-RB'] = self._conv_current_2_strength(
    #         value, self._dipole.current_rb, self._fam.current_rb)
    #     self._trigger_callback(
    #         pvname.replace(
    #             'Current', self._strength), self._propty['Strength-RB'], **kwargs)
    #
    # def _pvchange_currentref_mon(self, pvname, value, **kwargs):
    #     super()._pvchange_currentref_mon(pvname, value, **kwargs)
    #     self._propty['StrengthRef-Mon'] = self._conv_current_2_strength(
    #         value, self._dipole.currentref_mon, self._fam.currentref_mon)
    #     self._trigger_callback(
    #         pvname.replace(
    #             'Current', self._strength), self._propty['StrengthRef-Mon'], **kwargs)
    #
    # def _pvchange_current_mon(self, pvname, value, **kwargs):
    #     super()._pvchange_current_mon(pvname, value, **kwargs)
    #     self._propty['Strength-Mon'] = self._conv_current_2_strength(
    #         value, self._dipole.current_mon, self._fam.current_mon)
    #     self._trigger_callback(
    #         pvname.replace(
    #             'Current', self._strength), self._propty['Strength-Mon'], **kwargs)

    def _dipole_updated(self, pvname, value, **kwargs):
        # Get dipole new current and update self strength value
        trigger_callback = False
        new_value = None
        field = None
        if "Current-SP" in pvname:
            self._set_strength_sp(
                self.current_sp, value, self._fam.current_sp)
            new_value = self._propty['Strength-SP']
            field = "-SP"
            trigger_callback = True
        if "Current-RB" in pvname:
            self._propty['Strength-RB'] = self._conv_current_2_strength(
                self.current_rb, value, self._fam.current_rb)
            new_value = self._propty['Strength-RB']
            field = "-RB"
            trigger_callback = True
        if "CurrentRef-Mon" in pvname:
            self._propty['StrengthRef-Mon'] = self._conv_current_2_strength(
                self.currentref_mon, value, self._fam.currentref_mon)
            new_value = self._propty['StrengthRef-Mon']
            field = "Ref-Mon"
            trigger_callback = True
        if "Current-Mon" in pvname:
            self._propty['Strength-Mon'] = self._conv_current_2_strength(
                self.current_mon, value, self._fam.current_mon)
            new_value = self._propty['Strength-Mon']
            field = "-Mon"
            trigger_callback = True

        if trigger_callback:
            self._trigger_callback(
                self._maname + ":" + self._strength + field,
                new_value, **kwargs)

    def _family_updated(self, pvname, value, **kwargs):
        # Get family new current and update self strength value
        trigger_callback = False
        new_value = None
        field = None
        if "Current-SP" in pvname:
            self._set_strength_sp(
                self.current_sp, self._dipole.current_sp, value)
            new_value = self._propty['Strength-SP']
            field = "-SP"
            trigger_callback = True
        if "Current-RB" in pvname:
            self._propty['Strength-RB'] = self._conv_current_2_strength(
                self.current_rb, self._dipole.current_rb, value)
            new_value = self._propty['Strength-RB']
            field = "-RB"
            trigger_callback = True
        if "CurrentRef-Mon" in pvname:
            self._propty['StrengthRef-Mon'] = self._conv_current_2_strength(
                self.currentref_mon, self._dipole.currentref_mon, value)
            new_value = self._propty['StrengthRef-Mon']
            field = "Ref-Mon"
            trigger_callback = True
        if "Current-Mon" in pvname:
            self._propty['Strength-Mon'] = self._conv_current_2_strength(
                self.current_mon, self._dipole.current_mon, value)
            new_value = self._propty['Strength-Mon']
            field = "-Mon"
            trigger_callback = True

        if trigger_callback:
            self._trigger_callback(
                self._maname + ":" + self._strength + field,
                new_value, **kwargs)

    def _get_database(self, prefix=''):
        """Return an updated PV database."""
        db = self._madata._propty_databases[self._psnames[0]]
        # value = self.ctrlmode_mon
        # db['CtrlMode-Mon']['value'] = _et.enums('RmtLocTyp').index(value) \
        #     if self._enum_keys else value
        value = self.opmode_sel
        db['OpMode-Sel']['value'] = _et.enums('PSOpModeTyp').index(value) \
            if self._enum_keys else value
        value = self.opmode_sts
        db['OpMode-Sts']['value'] = _et.enums('PSOpModeTyp').index(value) \
            if self._enum_keys else value
        value = self.pwrstate_sel
        db['PwrState-Sel']['value'] = _et.enums('OffOnTyp').index(value) \
            if self._enum_keys else value
        value = self.pwrstate_sts
        db['PwrState-Sts']['value'] = _et.enums('OffOnTyp').index(value) \
            if self._enum_keys else value
        # db['Reset-Cmd']['value'] = self.reset
        # db['Abort-Cmd']['value'] = self.abort
        # wfmlabels = self._get_wfmlabels_mon()
        # db['WfmLoad-Sel']['enums'] = wfmlabels
        # db['WfmLoad-Sts']['enums'] = wfmlabels
        # value = self.wfmload_sel
        # db['WfmLoad-Sel']['value'] = _np.where(wfmlabels == value)[0][0] \
        #     if self._enum_keys else value
        # value = self.wfmload_sts
        # db['WfmLoad-Sts']['value'] = _np.where(wfmlabels == value)[0][0] \
        #     if self._enum_keys else value
        # db['WfmLabel-SP']['value'] = self.wfmlabel_sp
        # db['WfmLabel-RB']['value'] = self.wfmlabel_rb
        # db['WfmLabels-Mon']['value'] = self.wfmlabels_mon
        # db['WfmData-SP']['value'] = self.wfmdata_sp
        # db['WfmData-RB']['value'] = self.wfmdata_rb
        # db['WfmSave-Cmd']['value'] = self.wfmsave_cmd
        # db['WfmIndex-Mon']['value'] = self.wfmindex_mon
        db['Current-SP']['value'] = self.current_sp
        db['Current-RB']['value'] = self.current_rb
        db['CurrentRef-Mon']['value'] = self.currentref_mon
        db['Current-Mon']['value'] = self.current_mon
        # db['Intlk-Mon']['value'] = self.intlk_mon

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


class MagnetFactory:
    """Return proper magnet object, given the device name."""

    @staticmethod
    def get_dipole(maname):
        """Return corresponding dipole."""
        maname = _SiriusPVName(maname)
        if _re.match("B.*", maname.dev_type):
            return None
        elif maname.section == "SI":
            return "SI-Fam:MA-B1B2"
        elif maname.section == "BO":
            return "BO-Fam:MA-B"
        elif maname.section == "TB":
            raise NotImplementedError
        elif maname.section == "TS":
            raise NotImplementedError
        else:
            return None

    @staticmethod
    def get_fam(maname):
        """Static factory method."""
        maname = _SiriusPVName(maname)
        if maname.section == "SI" \
                and maname.subsection != "Fam" \
                and _re.match("(?:QD|QF|Q[0-9]).*", maname.dev_type):
            return _re.sub("SI-\d{2}\w{2}:", "SI-Fam:", maname)
        else:
            return None

    @staticmethod
    def factory(maname, dipole, fam,
                use_vaca=False,
                vaca_prefix=None,
                callback=None,
                connection_timeout=None):
        """Static factory method."""
        maname = _SiriusPVName(maname)
        if _re.match("B.*", maname.dev_type):
            return MagnetPowerSupplyDipole(
                maname=maname,
                callback=callback,
                use_vaca=use_vaca,
                vaca_prefix=vaca_prefix,
                connection_timeout=connection_timeout)

        elif maname.subsection == "Fam" or \
                _re.match("(?:CH|FCH|CV|FCV|QS|SD|SF).*", maname.dev_type):
            if not isinstance(dipole, MagnetPowerSupplyDipole):
                raise ValueError(
                    "Dipole must be of MagnetPowerSupplyDipole type")

            return MagnetPowerSupply(
                maname=maname,
                dipole=dipole,
                callback=callback,
                use_vaca=use_vaca,
                vaca_prefix=vaca_prefix,
                connection_timeout=connection_timeout)

        elif _re.match("(?:QD|QD|Q[0-9]).*", maname.dev_type):
            if not isinstance(dipole, MagnetPowerSupplyDipole):
                raise ValueError(
                    "Dipole must be of MagnetPowerSupplyDipole type")
            if not isinstance(fam, MagnetPowerSupply):
                raise ValueError(
                    "Family magnet must be of MagnetPowerSupply type")

            return MagnetPowerSupplyTrim(
                maname=maname,
                dipole=dipole,
                fam=fam,
                callback=callback,
                use_vaca=use_vaca,
                vaca_prefix=vaca_prefix,
                connection_timeout=connection_timeout)
        else:
            raise NotImplementedError




class Magnet:

    _magfuncs = _mutil.get_magfunc_2_multipole_dict()

    def __init__(self, magfunc,
                       psupplies,
                       psmain=None,
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



# class PowerSupplyMA(_PowerSupplySync):
#
#     def __init__(self, maname, use_vaca=False,
#                                vaca_prefix=None,
#                                connection_timeout=_connection_timeout,
#                                controller_dipole=None,
#                                controller_family=None,
#                                lock=True,
#                                **kwargs
#                                ):
#         self._maname = _SiriusPVName(maname)
#         self._madata = _MAData(self._maname)
#         super().__init__(psnames=self._get_psnames(),
#                          use_vaca=use_vaca,
#                          vaca_prefix=vaca_prefix,
#                          connection_timeout=connection_timeout,
#                          lock=lock,
#                          **kwargs)
#         self._controller_dipole = controller_dipole
#         self._controller_family = controller_family
#         self._callback_indices = {}
#         self._init_pwrsupply(use_vaca=use_vaca,
#                              vaca_prefix=vaca_prefix,
#                              connection_timeout=connection_timeout)
#
#         self._currents_sp['current'] = self._controller.current_sp
#         self._strength_sp = self._strobj.conv_current_2_strength(**self._currents_sp)
#
#     def _get_psnames(self):
#         ''' Method to get controllers that'll be created for given magnet '''
#         if self.magfunc == "dipole":
#             if self._maname.section == "SI":
#                 return ["SI-Fam:PS-B1B2-1", "SI-Fam:PS-B1B2-2"]
#             elif self._maname.section == "BO":
#                 return ["BO-Fam:PS-B-1", "BO-Fam:PS-B-2"]
#             else:
#                 raise NotImplementedError
#         else:
#             return [self._maname.replace(':MA', ':PS')]
#
#     @property
#     def magfunc(self):
#         """Return string corresponding to the magnetic function excitated with the power supply."""
#         return self._madata.magfunc(self._madata.psnames[0])
#
#     @property
#     def strength_sp(self):
#         return self._strength_sp
#         #self._currents_sp['current'] = self._controller.current_sp
#         #return self._strobj.conv_current_2_strength(**self._currents_sp)
#
#     @strength_sp.setter
#     def strength_sp(self, value): #COMO SETAR strength DO TRIM
#         if value != self._strength_sp:
#             self._strength_sp = value
#             self._currents_sp['current'] = self._controller.current_sp
#             self.current_sp = self._strobj.conv_strength_2_current(strength=value, **self._currents_sp)
#
#     @property
#     def strength_rb(self):
#         self._currents_sp['current'] = self._controller.current_sp
#         return self._strobj.conv_current_2_strength(**self._currents_sp)
#
#     @property
#     def strengthref_mon(self):
#         self._currents_ref['current'] = self._controller.current_ref
#         return self._strobj.conv_current_2_strength(**self._currents_ref)
#
#     @property
#     def strength_mon(self):
#         self._currents_load['current'] = self._controller.current_load
#         return self._strobj.conv_current_2_strength(**self._currents_load)
#
#     def _init_pwrsupply(self, use_vaca, vaca_prefix,
#                               connection_timeout):
#         sector, dipole_maname = _MAStrength.get_dipole_sector_maname(maname=self._maname)
#         if self.magfunc == 'dipole' and self._maname.subsection == 'Fam':
#             self._strobj = _MAStrengthDip(maname=dipole_maname)
#             self._currents_sp  = {}
#             self._currents_ref = {}
#             self._currents_load = {}
#         else:
#             madata_dipole = _MAData(maname=dipole_maname)
#             if self._controller_dipole is None:
#                 self._controller_dipole = _ControllerEpics(psname=madata_dipole.psnames[0],
#                                                            use_vaca=use_vaca,
#                                                            vaca_prefix=vaca_prefix,
#                                                            connection_timeout=connection_timeout)
#             self._callback_indices['dipole'] = self._controller_dipole.add_callback(self._mycallback_dipole)
#             if self._maname.subsection == 'Fam' or self.magfunc in ('quadrupole-skew',
#                                                                     'corrector-horizontal',
#                                                                     'corrector-vertical'):
#                 self._strobj = _MAStrength(maname=self._maname)
#                 self._currents_sp   = {'current_dipole':self._controller_dipole.current_sp}
#                 self._currents_ref  = {'current_dipole':self._controller_dipole.current_ref}
#                 self._currents_load = {'current_dipole':self._controller_dipole.current_load}
#             elif self.magfunc in ('quadrupole'):
#                 pvname = _SiriusPVName(self._psnames[0])
#                 family = pvname.replace(pvname.subsection, 'Fam')
#                 if self._controller_family is None:
#                     self._controller_family = _ControllerEpics(psname=family,
#                                                                use_vaca=use_vaca,
#                                                                vaca_prefix=vaca_prefix,
#                                                                connection_timeout=connection_timeout)
#                 self._callback_indices['family'] = self._controller_family.add_callback(self._mycallback_family)
#                 self._strobj = _MAStrengthTrim(maname=self._maname)
#                 self._currents_sp   = {'current_dipole':self._controller_dipole.current_sp,
#                                        'current_family':self._controller_family.current_sp}
#                 self._currents_ref  = {'current_dipole':self._controller_dipole.current_ref,
#                                        'current_family':self._controller_family.current_ref}
#                 self._currents_load = {'current_dipole':self._controller_dipole.current_load,
#                                        'current_family':self._controller_family.current_load}
#
#     def __del__(self):
#         for typ,index in self._callback_indices.items():
#             if typ == 'dipole' and self._controller_dipole is not None:
#                 self._controller_dipole.remove_callback(index=index)
#             elif typ == 'family' and self._controller_family is not None:
#                 self._controller_family.remove_callback(index=index)
#         if hasattr(super(), '__del__'):
#             super().__del__()
#
#     def _get_database(self, prefix=''):
#         """Return an updated  PV database whose keys correspond to PS properties."""
#         db = self._madata._propty_databases[self._psnames[0]]
#         value = self.ctrlmode_mon; db['CtrlMode-Mon']['value'] = _et.enums('RmtLocTyp').index(value) if self._enum_keys else value
#         value = self.opmode_sel;   db['OpMode-Sel']['value'] = _et.enums('PSOpModeTyp').index(value) if self._enum_keys else value
#         value = self.opmode_sts;   db['OpMode-Sts']['value'] = _et.enums('PSOpModeTyp').index(value) if self._enum_keys else value
#         value = self.pwrstate_sel; db['PwrState-Sel']['value'] = _et.enums('OffOnTyp').index(value) if self._enum_keys else value
#         value = self.pwrstate_sts; db['PwrState-Sts']['value'] = _et.enums('OffOnTyp').index(value) if self._enum_keys else value
#         db['Reset-Cmd']['value'] = self.reset
#         db['Abort-Cmd']['value'] = self.abort
#         wfmlabels = self._get_wfmlabels_mon()
#         db['WfmLoad-Sel']['enums'] = wfmlabels
#         db['WfmLoad-Sts']['enums'] = wfmlabels
#         value = self.wfmload_sel;  db['WfmLoad-Sel']['value'] = _np.where(wfmlabels == value)[0][0] if self._enum_keys else value
#         value = self.wfmload_sts;  db['WfmLoad-Sts']['value'] = _np.where(wfmlabels == value)[0][0] if self._enum_keys else value
#         db['WfmLabel-SP']['value'] = self.wfmlabel_sp
#         db['WfmLabel-RB']['value'] = self.wfmlabel_rb
#         db['WfmLabels-Mon']['value'] = self.wfmlabels_mon
#         db['WfmData-SP']['value'] = self.wfmdata_sp
#         db['WfmData-RB']['value'] = self.wfmdata_rb
#         db['WfmSave-Cmd']['value']= self.wfmsave_cmd
#         db['WfmIndex-Mon']['value'] = self.wfmindex_mon
#         db['Current-SP']['value'] = self.current_sp
#         db['Current-RB']['value'] = self.current_rb
#         db['CurrentRef-Mon']['value'] = self.currentref_mon
#         db['Current-Mon']['value'] = self.current_mon
#         db['Intlk-Mon']['value'] = self.intlk_mon
#
#         if 'KL-SP' in db:
#             strength = 'KL'
#         elif 'SL-SP' in db:
#             strength = 'SL'
#         elif 'Energy-SP' in db:
#             strength = 'Energy'
#         elif 'Kick-SP' in db:
#             strength = 'Kick'
#         else:
#             raise ValueError("No strength defined")
#
#         # Set strength values
#         db[strength + '-SP']['value'] = self.strength_sp
#         db[strength + '-RB']['value'] = self.strength_rb
#         db[strength + 'Ref-Mon']['value'] = self.strengthref_mon
#         db[strength + '-Mon']['value'] = self.strength_mon
#
#         prefixed_db = dict()
#         for key, value in db.items():
#             prefixed_db[prefix + ':' + key] = value
#
#         return prefixed_db
#
#     def _set_current_sp(self, value):
#         super()._set_current_sp(value)
#         self._currents_sp['current'] = value
#         self._strength_sp = self._strobj.conv_current_2_strength(**self._currents_sp)
#
#     def _mycallback(self, pvname, value, **kwargs):
#         for psname in self._psnames:
#             pvname = pvname.replace(psname, self._maname)
#         # Callbacks for strength: _rb, ref_mon, _mon
#         for callback in self._callbacks.values():
#             slot = ':'.join(pvname.split(':')[:2])
#             # Callbacks to update strngth PVs
#             strength = self._get_strength_string()
#             if 'Current-RB' in pvname:
#                 callback(slot + ':' + strength + '-RB',
#                          self.strength_rb, **kwargs)
#             elif 'CurrentRef-Mon' in pvname:
#                 callback(slot + ':' + strength + 'Ref-Mon',
#                          self.strengthref_mon, **kwargs)
#             elif 'Current-Mon' in pvname:
#                 callback(slot + ':' + strength + '-Mon', self.strength_mon, **kwargs)
#         super()._mycallback(pvname, value, **kwargs)
#
#     def _get_strength_string(self):
#         if self.magfunc in ('dipole'):
#             return "Energy"
#         elif self.magfunc in ('quadrupole', 'quadrupole-skew'):
#             return "KL"
#         elif self.magfunc in ('corrector-horizontal', 'corrector-vertical'):
#             return "Kick"
#         elif self.magfunc in ('sextupole',):
#             return "SL"
#         else:
#             raise ValueError("No such strength")
#
#     def _mycallback_dipole(self, pvname, value, **kwargs):
#         """Callback used for dipole PVs updates."""
#         run_callback = False
#         if 'Current-RB' in pvname:
#             self._currents_sp['current_dipole'] = value
#             new_value = self.strength_rb
#             run_callback = True
#         elif 'CurrentRef-Mon' in pvname:
#             self._currents_ref['current_dipole'] = value
#             new_value = self.strengthref_mon
#             run_callback = True
#         elif 'Current-Mon' in pvname:
#             self._currents_load['current_dipole'] = value
#             new_value = self.strength_mon
#             run_callback = True
#         if run_callback and self._callbacks:
#             # signals up changes in strengths
#             if self.magfunc in ('quadrupole','quadrupole-skew'):
#                 pfield = pvname.split(':')[-1].replace("Current", "KL")
#             elif self.magfunc in ('corrector-horizontal', 'corrector-vertical'):
#                 pfield = pvname.split(':')[-1].replace("Current", "Kick")
#             elif self.magfunc in ('sextupole',):
#                 pfield = pvname.split(':')[-1].replace("Current", "SL")
#             for callback in self._callbacks.values():
#                 callback(self._maname + ':' + pfield, new_value, **kwargs)
#
#     def _mycallback_family(self, pvname, value, **kwargs):
#         """Callback used for family PVs updates."""
#         run_callback = False
#         if 'Current-RB' in pvname:
#             self._currents_sp['current_family'] = value
#             new_value = self.strength_rb
#             run_callback = True
#         elif 'CurrentRef-Mon' in pvname:
#             self._currents_ref['current_family'] = value
#             new_value = self.strengthref_mon
#             run_callback = True
#         elif 'Current-Mon' in pvname:
#             self._currents_load['current_family'] = value
#             new_value = self.strength_mon
#             run_callback = True
#         if run_callback and self._callbacks:
#             # signals up changes in strengths
#             if self.magfunc in ('quadrupole','quadrupole-skew'):
#                 pfield = pvname.split(':')[-1].replace("Current", "KL")
#             elif self.magfunc in ('corrector-horizontal', 'corrector-vertical'):
#                 pfield = pvname.split(':')[-1].replace("Current", "Kick")
#             elif self.magfunc in ('sextupole',):
#                 pfield = pvname.split(':')[-1].replace("Current", "SL")
#             for callback in self._callbacks.values():
#                 callback(self._maname + ':' + pfield, new_value, **kwargs)
