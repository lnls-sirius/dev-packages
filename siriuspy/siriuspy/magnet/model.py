"""This module contain classes for dealing with magnets.

MagnetPowerSupplyDipole
    Handle dipole magnets.
MagnetPowerSupply
    Handle family and individual magnets.
MagnetPowerSupplyTrim
    Handle trim magnets.
"""

import epics as _epics
from siriuspy import util as _util
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply.model import PowerSupplyEpicsSync \
    as _PowerSupplyEpicsSync
from siriuspy.magnet import util as _mutil
from siriuspy.magnet.data import MAData as _MAData
from siriuspy import envars as _envars
from siriuspy.magnet import normalizer as _norm

_connection_timeout = None
_magfuncs = _mutil.get_magfunc_2_multipole_dict()


def create_magnet_normalizer(magnet):
    """Return appropriate normalizer object for a magnet."""
    if magnet.magfunc in ('dipole'):
        return _norm.DipoleNormalizer(magnet.maname, magnet_conv_sign=-1.0)
    elif magnet.magfunc == 'quadrupole' and \
            magnet.maname.section == 'SI' and \
            magnet.maname.subsection != 'Fam':
            return _norm.TrimNormalizer(magnet.maname,
                                        magnet_conv_sign=-1.0,
                                        dipole_name=magnet.dipole_name,
                                        fam_name=magnet.fam_name)
    elif magnet.magfunc in ('corrector-horizontal', 'quadrupole-skew'):
        return _norm.MagnetNormalizer(magnet.maname,
                                      dipole_name=magnet.dipole_name,
                                      magnet_conv_sign=+1.0)
    else:
        return _norm.MagnetNormalizer(magnet.maname,
                                      dipole_name=magnet.dipole_name,
                                      magnet_conv_sign=-1.0)


class _MagnetPowerSupply(_PowerSupplyEpicsSync):
    """Base class for handling magnets."""

    def __init__(self, maname,
                 use_vaca=False,
                 vaca_prefix=None,
                 lock=True,
                 callback=None,
                 connection_timeout=None):
        self._maname = _SiriusPVName(maname)
        self._dipole_name = _mutil.get_section_dipole_name(self._maname)
        self._fam_name = _mutil.get_magnet_fam_name(self._maname)
        self._madata = _MAData(maname=self._maname)
        self._magfunc = self._madata.magfunc(self._madata.psnames[0])
        self._mfmult = _magfuncs[self.magfunc]
        self._current_min = self._madata._splims['DRVL']
        self._current_max = self._madata._splims['DRVH']
        self._strength_obj = create_magnet_normalizer(self)
        self._strength_label = _util.get_strength_label(self._magfunc)
        self._set_vaca_prefix(use_vaca, vaca_prefix)

        super().__init__(psnames=self._power_supplies(),
                         use_vaca=use_vaca,
                         vaca_prefix=vaca_prefix,
                         lock=lock)

        self._db = self._madata._propty_databases[self._psnames[0]]

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
        low, high, lolo, hihi, lolim, hilim = \
            self._get_strength_limit(**kwargs)

        if value > hilim:
            value = hilim
        elif value < lolim:
            value = lolim

        return value

    @property
    def dipole_name(self):
        return self._dipole_name

    @property
    def fam_name(self):
        return self._fam_name

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
        label = self._strength_label

        if self.connected:

            value = self.ctrlmode_mon
            if value is not None:
                self._db['CtrlMode-Mon']['value'] = value
            value = self.opmode_sel
            if value is not None:
                self._db['OpMode-Sel']['value'] = value
            value = self.opmode_sts
            if value is not None:
                self._db['OpMode-Sts']['value'] = value
            value = self.pwrstate_sel
            if value is not None:
                self._db['PwrState-Sel']['value'] = value
            value = self.pwrstate_sts
            if value is not None:
                self._db['PwrState-Sts']['value'] = value
            value = self.reset_cmd
            if value is not None:
                self._db['Reset-Cmd']['value'] = self.reset_cmd
            value = self.abort_cmd
            if value is not None:
                self._db['Abort-Cmd']['value'] = self.abort_cmd
            value = self.wfmlabels_mon
            if value is not None:
                self._db['WfmLoad-Sel']['enums'] = value
                self._db['WfmLoad-Sts']['enums'] = value
            value = self.wfmload_sel
            if value is not None:
                self._db['WfmLoad-Sel']['value'] = value
            value = self.wfmload_sts
            if value is not None:
                self._db['WfmLoad-Sts']['value'] = value

            value = self.wfmlabel_sp
            if value is not None:
                self._db['WfmLabel-SP']['value'] = self.wfmlabel_sp
            value = self.wfmlabel_rb
            if value is not None:
                self._db['WfmLabel-RB']['value'] = self.wfmlabel_rb
            value = self.wfmlabels_mon
            if value is not None:
                self._db['WfmLabels-Mon']['value'] = self.wfmlabels_mon
            value = self.wfmdata_sp
            if value is not None:
                self._db['WfmData-SP']['value'] = self.wfmdata_sp
            value = self.wfmdata_rb
            if value is not None:
                self._db['WfmData-RB']['value'] = self.wfmdata_rb
            value = self.wfmsave_cmd
            if value is not None:
                self._db['WfmSave-Cmd']['value'] = self.wfmsave_cmd
            value = self.wfmindex_mon
            if value is not None:
                self._db['WfmIndex-Mon']['value'] = self.wfmindex_mon
            value = self.current_sp
            if value is not None:
                self._db['Current-SP']['value'] = self.current_sp
            value = self.current_rb
            if value is not None:
                self._db['Current-RB']['value'] = self.current_rb
            value = self.currentref_mon
            if value is not None:
                self._db['CurrentRef-Mon']['value'] = self.currentref_mon
            value = self.current_mon
            if value is not None:
                self._db['Current-Mon']['value'] = self.current_mon
            value = self.intlk_mon
            if value is not None:
                self._db['Intlk-Mon']['value'] = self.intlk_mon

            # Set strength values
            value = self.strength_sp
            if value is not None:
                self._db[label + '-SP']['value'] = self.strength_sp
            value = self.strength_rb
            if value is not None:
                self._db[label + '-RB']['value'] = self.strength_rb
            value = self.strength_mon
            if value is not None:
                self._db[label + '-Mon']['value'] = self.strength_mon
            value = self.strengthref_mon
            if value is not None:
                self._db[label + 'Ref-Mon']['value'] = self.strengthref_mon

        kwargs = self._get_currents_dict('Current-SP')
        low, high, lolo, hihi, lolim, hilim = \
            self._get_strength_limit(**kwargs)

        # Set strength values
        self._db[label + '-SP']['high'] = high
        self._db[label + '-SP']['low'] = low
        self._db[label + '-SP']['hilim'] = hilim
        self._db[label + '-SP']['lolim'] = lolim
        self._db[label + '-SP']['hihi'] = hihi
        self._db[label + '-SP']['lolo'] = lolo

        if prefix is None:
            return self._db

        prefixed_db = dict()
        for key, value in self._db.items():
            prefixed_db[prefix + ':' + key] = value
        return prefixed_db

    def _get_strength_limit(self, **kwargs):
        # for dipoles limits could be calculated only once.
        low = self._strength_obj.conv_current_2_strength(
            self._db["Current-SP"]["low"], **kwargs)
        high = self._strength_obj.conv_current_2_strength(
            self._db["Current-SP"]["high"], **kwargs)
        if high < low:
            high, low = low, high

        lolo = self._strength_obj.conv_current_2_strength(
            self._db["Current-SP"]["lolo"], **kwargs)
        hihi = self._strength_obj.conv_current_2_strength(
            self._db["Current-SP"]["hihi"], **kwargs)
        if hihi < lolo:
            hihi, lolo = lolo, hihi

        lolim = self._strength_obj.conv_current_2_strength(
            self._db["Current-SP"]["lolim"], **kwargs)
        hilim = self._strength_obj.conv_current_2_strength(
            self._db["Current-SP"]["hilim"], **kwargs)
        if hilim < lolim:
            hilim, lolim = lolim, hilim
        return (low, high, lolo, hihi, lolim, hilim)

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

        self._dipole_current_sp = 0.0
        self._dipole_current_rb = 0.0
        self._dipole_currentref_mon = 0.0
        self._dipole_current_mon = 0.0
        self._fam_current_sp = 0.0
        self._fam_current_rb = 0.0
        self._fam_currentref_mon = 0.0
        self._fam_current_mon = 0.0
        # self._dipole_current_sp = self._dipole.get('Current-SP')
        # self._dipole_current_rb = self._dipole.get('Current-RB')
        # self._dipole_currentref_mon = self._dipole.get('CurrentRef-Mon')
        # self._dipole_current_mon = self._dipole.get('Current-Mon')

        for attr in attrs:
            self._dipole[attr] = _epics.PV(pvname=prefix + ":" + attr)
            self._dipole[attr].add_callback(self._callback_dipole_updated)

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
        return {'currents_dipole': current}

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
                currents=self._propty[propty], **kwargs)

            propty_strength = propty.replace('Current', label)
            self._propty[propty_strength] = strength

            pvname = self._maname + ':' + propty_strength
            try:
                low, high, lolo, hihi, lolim, hilim = \
                    self._get_strength_limit(**kwargs)
                self._trigger_callback(
                    pvname, strength, high=high, low=low, hihi=hihi, lolo=lolo,
                    hilim=hilim, lolim=lolim)
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
        self._fam = {}
        prefix = self._vaca_prefix + self._fam_name
        # self._fam = _epics.Device(prefix, delim=':', attrs=attrs)

        # self._fam_current_sp = 0.0
        # self._fam_current_rb = 0.0
        # self._fam_currentref_mon = 0.0
        # self._fam_current_mon = 0.0
        # self._fam_current_sp = self._fam.get('Current-SP')
        # self._fam_current_rb = self._fam.get('Current-RB')
        # self._fam_currentref_mon = self._fam.get('CurrentRef-Mon')
        # self._fam_current_mon = self._fam.get('Current-Mon')

        for attr in attrs:
            self._fam[attr] = _epics.PV(pvname=prefix + ":" + attr)
            self._fam[attr].add_callback(self._callback_family_updated)

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

        return {'currents_dipole': current_dipole,
                'currents_family': current_family}

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
                currents=self._propty[propty], **kwargs)

            propty_strength = propty.replace('Current', label)
            self._propty[propty_strength] = strength

            pvname = self._maname + ':' + propty_strength
            try:
                low, high, lolo, hihi, lolim, hilim = \
                    self._get_strength_limit(**kwargs)
                self._trigger_callback(
                    pvname, strength, high=high, low=low, hihi=hihi, lolo=lolo,
                    hilim=hilim, lolim=lolim)
            except (KeyError, AttributeError) as e:
                self._trigger_callback(pvname, strength)
