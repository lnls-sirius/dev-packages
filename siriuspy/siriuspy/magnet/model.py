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
import epics as _epics
from siriuspy import util as _util
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply.model import PowerSupplyEpicsSync \
    as _PowerSupplyEpicsSync
from siriuspy.magnet import util as _mutil
from siriuspy.magnet.data import MAData as _MAData
from siriuspy import envars as _envars

_connection_timeout = None

_magfuncs = _mutil.get_magfunc_2_multipole_dict()


class _MagnetNormalizer:
    """Base class for converting magnet properties: current and strength."""

    def __init__(self, maname, left='linear', right='linear'):
        """Class constructor."""
        self._maname = _SiriusPVName(maname)

        self._madata = _MAData(maname=self._maname)
        self._magfunc = self._madata.magfunc(self._madata.psnames[0])
        self._left = left
        self._right = right
        self._mfmult = _magfuncs[self._magfunc]

        self._psname = self._power_supplies()[0]

    def _conv_current_2_multipoles(self, current):
        if current is None:
            return None
        msum = {}
        if self._magfunc != 'dipole':
            for psname in self._madata.psnames:
                excdata = self._madata.excdata(psname)
                m = excdata.interp_curr2mult(
                    current, left=self._left, right=self._right)
                msum = _mutil.sum_magnetic_multipoles(msum, m)
        else:
            excdata = self._madata.excdata(self._psname)
            m = excdata.interp_curr2mult(
                current, left=self._left, right=self._right)
            msum = _mutil.sum_magnetic_multipoles(msum, m)
        return msum

    def _conv_current_2_intfield(self, current):
        m = self._conv_current_2_multipoles(current)
        if m is None:
            return None
        mf = self._mfmult
        intfield = m[mf['type']][mf['harmonic']]
        return intfield

    def _get_energy(self, current_dipole):
        return self._dipole.conv_current_2_strength(current=current_dipole)

    def _get_brho(self, current_dipole):
        """Get Magnetic Rigidity."""
        if not current_dipole:
            return 0
        energy = self._get_energy(current_dipole)
        if not energy:
            return 0
        brho = _util.beam_rigidity(energy)
        return brho

    def conv_current_2_strength(self, current, **kwargs):
        intfield = self._conv_current_2_intfield(current)
        if intfield is None:
            return 0.0
        strength = self._conv_intfield_2_strength(intfield, **kwargs)
        return strength

    def conv_strength_2_current(self, strength, **kwargs):
        intfield = self._conv_strength_2_intfield(strength, **kwargs)
        mf = self._mfmult
        # excdata = self._get_main_excdata()
        excdata = self._madata.excdata(self._psname)
        current = excdata.interp_mult2curr(
            intfield, mf['harmonic'], mf['type'],
            left=self._left, right=self._right)
        return current

    def _power_supplies(self):
        return [self._maname.replace(":MA", ":PS")]


class DipoleNormalizer(_MagnetNormalizer):
    """Convert magnet current to strength and vice versa."""

    _ref_angles = _mutil.get_nominal_dipole_angles()

    def __init__(self, maname, **kwargs):
        """Class constructor."""
        super(DipoleNormalizer, self).__init__(maname, **kwargs)
        self._set_reference_dipole_data()

    def _set_reference_dipole_data(self):
        ang = DipoleNormalizer._ref_angles
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

    def _get_energy(self, current_dipole):
        return self.conv_current_2_strength(current=current_dipole)

    def _conv_strength_2_intfield(self, strength, **kwargs):
        if self._maname.section == 'SI':
            intfield = (- self._ref_angle * (self._ref_brho / self._ref_energy)
                        * strength - self._ref_BL_BC)
        else:
            intfield = (- self._ref_angle * (self._ref_brho / self._ref_energy)
                        * strength)
        return intfield

    def _conv_intfield_2_strength(self, intfield, **kwargs):
        if self._maname.section == 'SI':
            strength = ((self._ref_energy / self._ref_brho) *
                        (- intfield - self._ref_BL_BC) / self._ref_angle)
        else:
            strength = ((self._ref_energy / self._ref_brho) *
                        (-intfield) / self._ref_angle)
        return strength

    def _power_supplies(self):
        return self._madata.psnames


class MagnetNormalizer(_MagnetNormalizer):
    """Convert magnet current to strength and vice versa."""

    def __init__(self, maname, dipole_name, **kwargs):
        """Call super and initializes a dipole."""
        super(MagnetNormalizer, self).__init__(maname, **kwargs)
        self._dipole = DipoleNormalizer(dipole_name, **kwargs)

    def _conv_strength_2_intfield(self, strength, **kwargs):
        brho = self._get_brho(current_dipole=kwargs['current_dipole'])
        intfield = - brho * strength
        return intfield

    def _conv_intfield_2_strength(self, intfield, **kwargs):
        brho = self._get_brho(current_dipole=kwargs['current_dipole'])
        if brho == 0:
            return 0
        strength = - intfield / brho
        return strength


class TrimNormalizer(_MagnetNormalizer):
    """Convert trim magnet current to strength and vice versa."""

    def __init__(self, maname, dipole_name, fam_name, **kwargs):
        """Call super and initializes a dipole and the family magnet."""
        super(TrimNormalizer, self).__init__(maname, **kwargs)
        self._dipole = DipoleNormalizer(dipole_name, **kwargs)
        self._fam = MagnetNormalizer(fam_name, dipole_name, **kwargs)

    def _conv_strength_2_intfield(self, strength, **kwargs):
        strength_fam = self._fam.conv_current_2_strength(
            current=kwargs["current_family"],
            current_dipole=kwargs["current_dipole"])
        brho = self._get_brho(current_dipole=kwargs['current_dipole'])
        intfield = - brho * (strength - strength_fam)
        return intfield

    def _conv_intfield_2_strength(self, intfield, **kwargs):
        brho = self._get_brho(current_dipole=kwargs['current_dipole'])
        if brho == 0:
            return 0
        strength_trim = - intfield / brho
        strength_fam = self._fam.conv_current_2_strength(
            current=kwargs["current_family"],
            current_dipole=kwargs["current_dipole"])
        return strength_trim + strength_fam


class _MagnetPowerSupply(_PowerSupplyEpicsSync):
    """Base class for handling magnets."""

    def __init__(self, maname,
                 use_vaca=False,
                 vaca_prefix=None,
                 callback=None,
                 connection_timeout=None,
                 left='linear',
                 right='linear'):

        self._maname = _SiriusPVName(maname)

        self._dipole_name = self._get_dipole_name()
        self._fam_name = self._get_fam_name()

        self._madata = _MAData(maname=self._maname)
        self._magfunc = self._madata.magfunc(self._madata.psnames[0])
        self._left = left
        self._right = right
        self._mfmult = _magfuncs[self.magfunc]
        self._current_min = self._madata._splims['DRVL']
        self._current_max = self._madata._splims['DRVH']

        self._strength_obj = self._get_strength_obj()

        self._strength_label = self._get_strength_label()

        self._set_vaca_prefix(use_vaca, vaca_prefix)


        super().__init__(psnames=self._power_supplies(),
                         use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         lock=True)

        self._init_subclass()

    def _set_vaca_prefix(self, use_vaca, vaca_prefix):
        if use_vaca:
            if vaca_prefix is None:
                self._vaca_prefix = _envars.vaca_prefix
            else:
                self._vaca_prefix = vaca_prefix
        else:
            self._vaca_prefix = ''

    def _init_propty(self):
        super()._init_propty()
        self._propty[self._strength_label + '-SP'] = None
        self._propty[self._strength_label + '-RB'] = None
        self._propty[self._strength_label + 'Ref-Mon'] = None
        self._propty[self._strength_label + '-Mon'] = None

    def _init_subclass(self):
        raise NotImplementedError

    def _check_current_limits(self, value):
        """Check current limits."""
        value = value if self.current_min is None else \
            max(value, self.current_min)
        value = value if self.current_max is None else \
            min(value, self.current_max)
        return float(value)

    def _check_strength_limits(self, value):
        """Check strength limits."""
        kwargs = self._get_currents_dict('Current-SP')
        high, low = self._get_strength_limit(**kwargs)
        print(high, low)

        if value > high:
            value = high
        elif value < low:
            value = low

        return value

    @property
    def database(self):
        return self._get_database()

    @property
    def current_min(self):
        return self._current_min

    @property
    def current_max(self):
        return self._current_max

    @property
    def maname(self):
        return self._maname

    @property
    def magfunc(self):
        return self._magfunc

    @property
    def current_sp(self):
        return self._propty['Current-SP']

    @current_sp.setter
    def current_sp(self, value):
        value = self._check_current_limits(value)
        self._set_current_sp(value)
        kwargs = self._get_currents_dict('Current-SP')
        strength = self._strength_obj.conv_current_2_strength(value, **kwargs)
        self._propty[self._strength_label + '-SP'] = strength
        pvname = self._maname + ':' + self._strength_label + '-SP'
        self._trigger_callback(pvname, strength)

    @property
    def strength_sp(self):
        return self._propty[self._strength_label+'-SP']

    @strength_sp.setter
    def strength_sp(self, value):
        value = self._check_strength_limits(value)
        self._propty[self._strength_label + '-SP'] = value
        pvname = self._maname + ':' + self._strength_label + '-SP'
        self._trigger_callback(pvname, value)
        kwargs = self._get_currents_dict('Current-SP')
        current = self._strength_obj.conv_strength_2_current(value, **kwargs)
        # self.current_sp = current
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
        elif self.magfunc in ('quadrupole', 'quadrupole-skew'):
            return 'KL'
        elif self.magfunc in ('sextupole',):
            return 'SL'
        elif self.magfunc in ('corrector-horizontal', 'corrector-vertical'):
            return 'Kick'
        else:
            raise NotImplementedError("magfunc {}".format(self.magfunc))

    def _get_dipole_name(self):
        if _re.match("B.*", self._maname.dev_type):
            return None
        elif self._maname.section == "SI":
            return "SI-Fam:MA-B1B2"
        elif self._maname.section == "BO":
            return "BO-Fam:MA-B"
        elif self._maname.section == "TB":
            return "TB-Fam:MA-B"
        elif self._maname.section == "TS":
            return "TS-Fam:MA-B"
        else:
            raise NotImplementedError(
                "No section named {}".format(self._maname.section))

    def _get_fam_name(self):
        if self._maname.section == "SI" \
                and self._maname.subsection != "Fam" \
                and _re.match("(?:QD|QF|Q[0-9]).*", self._maname.dev_type):
            return _re.sub("SI-\d{2}\w{2}:", "SI-Fam:", self._maname)
        else:
            return None

    def _trigger_callback(self, pvname, value, **kwargs):
        *parts, propty = pvname.split(':')
        pvname = self._maname + ':' + propty
        for callback in self._callbacks.values():
            callback(pvname, value, **kwargs)

    def _callback_change_sp_pv(self, pvname, value, **kwargs):
        super()._callback_change_sp_pv(pvname, value, **kwargs)
        # invoking callback for strength sp
        label = self._strength_label
        *parts, propty = pvname.split(':')

        if self._propty[label+'-SP'] is None and propty == 'Current-SP':
            propty_strength = propty.replace('Current', label)

            kwargs = self._get_currents_dict('Current-SP')
            strength = self._strength_obj.conv_current_2_strength(
                value, **kwargs)

            if strength is not None:
                self._propty[propty_strength] = strength
                pvname = self._maname + ':'+label+'-SP'
                self._trigger_callback(pvname, strength, **kwargs)

    def _callback_change_rb_pv(self, pvname, value, **kwargs):
        super()._callback_change_rb_pv(pvname, value, **kwargs)
        # Invoking callback for strength sp
        *parts, propty = pvname.split(':')

        if "Current" in propty:
            label = self._strength_label
            propty_strength = propty.replace('Current', label)

            kwargs = self._get_currents_dict(propty)
            strength = self._strength_obj.conv_current_2_strength(
                value, **kwargs)

            if strength is not None:
                self._propty[propty_strength] = strength
                pvname = self._maname + ':' + propty_strength
                self._trigger_callback(pvname, strength, **kwargs)

    def _get_database(self, prefix=None):
        """Return an updated PV database. Keys correspond to PS properties."""
        self._db = self._madata._propty_databases[self._psnames[0]]

        label = self._strength_label

        if self.connected:
            value = self.ctrlmode_mon
            self._db['CtrlMode-Mon']['value'] = \
              _et.enums('RmtLocTyp').index(value) if self._enum_keys else value
            value = self.opmode_sel
            self._db['OpMode-Sel']['value'] = \
              _et.enums('PSOpModeTyp').index(value) if self._enum_keys else value
            value = self.opmode_sts
            self._db['OpMode-Sts']['value'] = \
              _et.enums('PSOpModeTyp').index(value) if self._enum_keys else value
            value = self.pwrstate_sel
            self._db['PwrState-Sel']['value'] = \
              _et.enums('OffOnTyp').index(value) if self._enum_keys else value
            value = self.pwrstate_sts
            self._db['PwrState-Sts']['value'] = \
              _et.enums('OffOnTyp').index(value) if self._enum_keys else value
            self._db['Reset-Cmd']['value'] = self.reset_cmd
            self._db['Abort-Cmd']['value'] = self.abort_cmd
            wfmlabels = self.wfmlabels_mon
            self._db['WfmLoad-Sel']['enums'] = wfmlabels
            self._db['WfmLoad-Sts']['enums'] = wfmlabels
            value = self.wfmload_sel
            self._db['WfmLoad-Sel']['value'] = \
              _np.where(wfmlabels == value)[0][0] if self._enum_keys else value
            value = self.wfmload_sts
            self._db['WfmLoad-Sts']['value'] = \
              _np.where(wfmlabels == value)[0][0] if self._enum_keys else value
            self._db['WfmLabel-SP']['value'] = self.wfmlabel_sp
            self._db['WfmLabel-RB']['value'] = self.wfmlabel_rb
            self._db['WfmLabels-Mon']['value'] = self.wfmlabels_mon
            self._db['WfmData-SP']['value'] = self.wfmdata_sp
            self._db['WfmData-RB']['value'] = self.wfmdata_rb
            self._db['WfmSave-Cmd']['value'] = self.wfmsave_cmd
            self._db['WfmIndex-Mon']['value'] = self.wfmindex_mon
            self._db['Current-SP']['value'] = self.current_sp
            self._db['Current-RB']['value'] = self.current_rb
            self._db['CurrentRef-Mon']['value'] = self.currentref_mon
            self._db['Current-Mon']['value'] = self.current_mon
            self._db['Intlk-Mon']['value'] = self.intlk_mon

            # Set strength values
            self._db[label + '-SP']['value'] = self.strength_sp
            self._db[label + '-RB']['value'] = self.strength_rb
            self._db[label + '-Mon']['value'] = self.strength_mon
            self._db[label + 'Ref-Mon']['value'] = self.strengthref_mon

        kwargs = self._get_currents_dict('Current-SP')
        hihi, lolo = self._get_strength_limit(**kwargs)

        print(hihi, lolo)

        # Set strength values
        self._db[label + '-SP']['hilim'] = hihi
        self._db[label + '-SP']['lolim'] = lolo

        if prefix is None:
            return self._db

        prefixed_db = dict()
        for key, value in self._db.items():
            prefixed_db[prefix + ':' + key] = value
        return prefixed_db

    def _get_strength_limit(self, **kwargs):
        high = self._strength_obj.conv_current_2_strength(
            self._current_max, **kwargs)
        low = self._strength_obj.conv_current_2_strength(
            self._current_min, **kwargs)

        if high > low:
            hihi = high
            lolo = low
        else:
            hihi = low
            lolo = high

        return (hihi, lolo)

    def _power_supplies(self):
        return [self._maname.replace(":MA", ":PS")]

    # --- methods below this line need implementation in subclasses
    def _get_currents_dict(self, current_attr):
        # return {}
        raise NotImplementedError


class MagnetPowerSupplyDipole(_MagnetPowerSupply):
    """Handle dipole magnets."""

    def _init_subclass(self):
        pass

    def _get_strength_obj(self):
        return DipoleNormalizer(
            self._maname, left=self._left, right=self._right)

    def _get_currents_dict(self, current_attr):
        return {}

    def _power_supplies(self):
        return self._madata.psnames


class MagnetPowerSupply(_MagnetPowerSupply):
    """Handle individual magnets.

    A callback to the reference dipole current is used so the magnet object can
    renormalize its strength when the current of the dipole changes.
    """

    def _init_subclass(self):
        attrs = ('Current-SP', 'Current-RB', 'CurrentRef-Mon', 'Current-Mon')
        self._dipole = {}
        prefix = self._vaca_prefix + self._dipole_name
        # self._dipole = _epics.Device(prefix, delim=':', attrs=attrs, timeout=None)

        self._dipole_current_sp = 0.0
        self._dipole_current_rb = 0.0
        self._dipole_currentref_mon = 0.0
        self._dipole_current_mon = 0.0
        # self._dipole_current_sp = self._dipole.get('Current-SP')
        # self._dipole_current_rb = self._dipole.get('Current-RB')
        # self._dipole_currentref_mon = self._dipole.get('CurrentRef-Mon')
        # self._dipole_current_mon = self._dipole.get('Current-Mon')

        for attr in attrs:
            self._dipole[attr] = _epics.PV(pvname=prefix + ":" + attr)
            self._dipole[attr].add_callback(self._callback_dipole_updated)

    def _get_strength_obj(self):
        return MagnetNormalizer(self._maname, dipole_name=self._dipole_name,
                                left=self._left, right=self._right)

    def _get_currents_dict(self, current_attr):
        if current_attr == 'Current-SP':
            current = self._dipole_current_sp
        elif current_attr == 'Current-RB':
            current = self._dipole_current_rb
        elif current_attr == 'CurrentRef-Mon':
            current = self._dipole_currentref_mon
        elif current_attr == 'Current-Mon':
            current = self._dipole_current_mon
        else:
            raise ValueError(
                'Invalid argument "' +
                str(current_attr) +
                '" to _get_currents_dict!')
        return {'current_dipole': current}

    def _callback_dipole_updated(self, pvname, value, **kwargs):
        # Get dipole new current and update self current value
        label = self._strength_label
        *parts, propty = pvname.split(':')
        _, field = propty.split('-')

        if 'Current' in propty:

            if '-SP' in propty:
                self._dipole_current_sp = value
            elif '-RB' in propty:
                self._dipole_current_rb = value
            elif 'Ref-Mon' in propty:
                self._dipole_currentref_mon = value
            elif '-Mon' in propty:
                self._dipole_current_mon = value

            kwargs = self._get_currents_dict(propty)
            strength = self._strength_obj.conv_current_2_strength(
                current=self._propty[propty], **kwargs)

            propty_strength = propty.replace('Current', label)
            self._propty[propty_strength] = strength

            pvname = self._maname + ':' + propty_strength
            try:
                hilim, lolim = self._get_strength_limit(**kwargs)
                self._trigger_callback(
                    pvname, strength, hilim=hilim, lolim=lolim)
            except (KeyError, AttributeError):
                self._trigger_callback(pvname, strength)


class MagnetPowerSupplyTrim(MagnetPowerSupply):
    """Handle trim magnets.

    Two callbacks are defined so the objects can update itself when the
    reference dipole or the family power supply have their currents changed.
    """

    def _init_subclass(self):
        attrs = ('Current-SP', 'Current-RB', 'CurrentRef-Mon', 'Current-Mon')
        super(MagnetPowerSupplyTrim, self)._init_subclass()
        # self._dipole = _epics.Device(self._dipole_name,delim=':',attrs=attrs)
        prefix = self._vaca_prefix + self._fam_name
        self._fam = _epics.Device(prefix, delim=':', attrs=attrs)

        self._dipole_current_sp = 0.0
        self._dipole_current_rb = 0.0
        self._dipole_currentref_mon = 0.0
        self._dipole_current_mon = 0.0
        # self._dipole_current_sp = self._dipole.get('Current-SP')
        # self._dipole_current_rb = self._dipole.get('Current-RB')
        # self._dipole_currentref_mon = self._dipole.get('CurrentRef-Mon')
        # self._dipole_current_mon = self._dipole.get('Current-Mon')

        self._fam_current_sp = self._fam.get('Current-SP')
        self._fam_current_rb = self._fam.get('Current-RB')
        self._fam_currentref_mon = self._fam.get('CurrentRef-Mon')
        self._fam_current_mon = self._fam.get('Current-Mon')

        for attr in attrs:
            # self._dipole.add_callback(attr, self._callback_dipole_updated)
            self._fam.add_callback(attr, self._callback_family_updated)

    def _get_strength_obj(self):
        return TrimNormalizer(self._maname, dipole_name=self._dipole_name,
                              fam_name=self._fam_name, left=self._left,
                              right=self._right)

    def _get_currents_dict(self, current_attr):
        if current_attr == 'Current-SP':
            current_dipole = self._dipole_current_sp
            current_family = self._fam_current_sp
        elif current_attr == 'Current-RB':
            current_dipole = self._dipole_current_rb
            current_family = self._fam_current_rb
        elif current_attr == 'CurrentRef-Mon':
            current_dipole = self._dipole_currentref_mon
            current_family = self._fam_currentref_mon
        elif current_attr == 'Current-Mon':
            current_dipole = self._dipole_current_mon
            current_family = self._fam_current_mon
        else:
            raise ValueError(
                'Invalid argument "' +
                str(current_attr) +
                '" to _get_currents_dict!')

        return {'current_dipole': current_dipole,
                'current_family': current_family}

    # def _callback_dipole_updated(self, pvname, value, **kwargs):
    #     # Get dipole new current and update self current value
    #     label = self._strength_label
    #     *parts, propty = pvname.split(':')
    #
    #     if 'Current' in propty:
    #
    #         if '-SP' in propty:
    #             self._dipole_current_sp = value
    #         elif '-RB' in propty:
    #             self._dipole_current_rb = value
    #         elif 'Ref-Mon' in propty:
    #             self._dipole_currentref_mon = value
    #         elif '-Mon' in propty:
    #             self._dipole_current_mon = value
    #
    #         kwargs = self._get_currents_dict(propty)
    #         strength = self._strength_obj.conv_current_2_strength(
    #             current=self._propty[propty], **kwargs)
    #
    #         propty_strength = propty.replace('Current', label)
    #         self._propty[propty_strength] = strength
    #
    #         pvname = self._maname + ':' + propty_strength
    #         try:
    #             hilim, lolim = self._get_strength_limit(**kwargs)
    #             self._trigger_callback(
    #                 pvname, strength, hilim=hilim, lolim=lolim)
    #         except (KeyError, AttributeError):
    #             self._trigger_callback(pvname, strength)

    def _callback_family_updated(self, pvname, value, **kwargs):
        # Get dipole new current and update self current value
        label = self._strength_label
        *parts, propty = pvname.split(':')

        if 'Current' in propty:

            if '-SP' in propty:
                self._fam_current_sp = value
            elif '-RB' in propty:
                self._fam_current_rb = value
            elif 'Ref-Mon' in propty:
                self._fam_currentref_mon = value
            elif '-Mon' in propty:
                self._fam_current_mon = value

            kwargs = self._get_currents_dict(propty)
            strength = self._strength_obj.conv_current_2_strength(
                current=self._propty[propty], **kwargs)

            propty_strength = propty.replace('Current', label)
            self._propty[propty_strength] = strength

            pvname = self._maname + ':' + propty_strength
            self._trigger_callback(pvname, strength)
