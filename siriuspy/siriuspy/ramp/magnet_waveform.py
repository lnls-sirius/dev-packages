"""MagnetWaveform Module."""

import numpy as _np
import weakref as _weakref
from siriuspy.ramp.waveform import Waveform as _Waveform
from siriuspy.ramp.magnet import Magnet as _Magnet
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.ramp.optics import _nominal_intkl
from siriuspy.magnet import util as _mutil


_nominal_strengths = {
    'SI-Fam:MA-QFA': +0.7146305692912001,
    'SI-Fam:MA-QDA': -0.2270152048045000,
    'SI-Fam:MA-QFB': +1.2344424683922000,
    'SI-Fam:MA-QDB2': -0.4782973132726601,
    'SI-Fam:MA-QDB1': -0.2808906119138000,
    'SI-Fam:MA-QFP': +1.2344424683922000,
    'SI-Fam:MA-QDP2': -0.4782973132726601,
    'SI-Fam:MA-QDP1': -0.2808906119138000,
    'SI-Fam:MA-Q1': +0.5631612043340000,
    'SI-Fam:MA-Q2': +0.8684629376249999,
    'SI-Fam:MA-Q3': +0.6471254242426001,
    'SI-Fam:MA-Q4': +0.7867827142062001,
    'SI-Fam:MA-SDA0': -12.1250549999999979,
    'SI-Fam:MA-SDB0': -09.7413299999999996,
    'SI-Fam:MA-SDP0': -09.7413299999999996,
    'SI-Fam:MA-SDA1': -24.4479749999999996,
    'SI-Fam:MA-SDB1': -21.2453849999999989,
    'SI-Fam:MA-SDP1': -21.3459000000000003,
    'SI-Fam:MA-SDA2': -13.3280999999999992,
    'SI-Fam:MA-SDB2': -18.3342150000000004,
    'SI-Fam:MA-SDP2': -18.3421500000000002,
    'SI-Fam:MA-SDA3': -20.9911199999999987,
    'SI-Fam:MA-SDB3': -26.0718599999999974,
    'SI-Fam:MA-SDP3': -26.1236099999999993,
    'SI-Fam:MA-SFA0': +07.8854400000000000,
    'SI-Fam:MA-SFB0': +11.0610149999999994,
    'SI-Fam:MA-SFP0': +11.0610149999999994,
    'SI-Fam:MA-SFA1': +28.7742599999999982,
    'SI-Fam:MA-SFB1': +34.1821950000000001,
    'SI-Fam:MA-SFP1': +34.3873949999999979,
    'SI-Fam:MA-SFA2': +22.6153800000000018,
    'SI-Fam:MA-SFB2': +29.6730900000000020,
    'SI-Fam:MA-SFP2': +29.7755099999999970,
    'BO-Fam:MA-QD': +0.0011197961538728,
    'BO-Fam:MA-QF': +0.3770999232791374,
    'BO-Fam:MA-SD': +0.5258382119529604,
    'BO-Fam:MA-SF': +1.1898514030258744,
}


class MagnetWaveform(_Magnet):
    """MagnetWaveform Class."""

    def __init__(self,
                 maname,
                 dipole=None,
                 family=None):
        """Class init."""
        self._dependents = set()
        _Magnet.__init__(self, maname=maname)
        self._dipole = dipole
        if self._dipole is not None:
            self._dipole._add_dep_magwfm(self)
        self._family = family
        if self._family is not None:
            self._family._add_dep_magwfm(self)
        self._init_waveform()

    # --- properties ---

    @property
    def deprecated(self):
        """Deprecated state."""
        return self._deprecated or self._waveform.deprecated

    @property
    def waveform(self):
        """Return current waveform."""
        return self._waveform

    @property
    def currents(self):
        """Return waveform currents values."""
        return self._waveform.waveform

    @currents.setter
    def currents(self, currents):
        """Waveform currents."""
        self._waveform.waveform = currents  # This will set deprecated state.

    @property
    def strengths(self):
        """Return strength waveform."""
        if self.deprecated:
            self._update_strength()
        return self._strengths

    @strengths.setter
    def strengths(self, strengths):
        """Waveform strengths."""
        currents = self._calc_currents(strengths)
        self._waveform.waveform = currents  # This will set deprecated state.

    @property
    def i07(self):
        """Return list of regions boundaries."""
        return self._waveform.i07

    @property
    def i0(self):
        """Return index of the first region boundary."""
        return self._waveform.i0

    @property
    def i1(self):
        """Return index of the second region boundary."""
        return self._waveform.i1

    @property
    def i2(self):
        """Return index of the third region boundary."""
        return self._waveform.i2

    @property
    def i3(self):
        """Return index of the fourth region boundary."""
        return self._waveform.i3

    @property
    def i4(self):
        """Return index of the fifth region boundary."""
        return self._waveform.i4

    @property
    def i5(self):
        """Return index of the sixth region boundary."""
        return self._waveform.i5

    @property
    def i6(self):
        """Return index of the seventh region boundary."""
        return self._waveform.i6

    @property
    def i7(self):
        """Return index of the eightth region boundary."""
        return self._waveform.i7

    @property
    def vL0(self):
        """Return waveform value at the left-end and first region boundary."""
        if self.deprecated:
            self._update_strength()
        return self._strengths[self._waveform.i0]

    @property
    def v1(self):
        """Return waveform value at the second region boundary."""
        if self.deprecated:
            self._update_strength()
        return self._strengths[self._waveform.i1]

    @property
    def v2(self):
        """Return waveform value at the 3rd region boundary."""
        if self.deprecated:
            self._update_strength()
        return self._strengths[self._waveform.i2]

    @property
    def v34(self):
        """Return waveform value at the 4th and 5th region boundaries."""
        if self.deprecated:
            self._update_strength()
        return self._strengths[self._waveform.i3]

    @property
    def v5(self):
        """Return waveform value at the 6h region boundary."""
        if self.deprecated:
            self._update_strength()
        return self._strengths[self._waveform.i5]

    @property
    def v6(self):
        """Return waveform value at the 7th region boundary."""
        if self.deprecated:
            self._update_strength()
        return self._strengths[self._waveform.i6]

    @property
    def v7R(self):
        """Return waveform value at the 8th and right-end region boundaries."""
        if self.deprecated:
            self._update_strength()
        return self._strengths[self._waveform.i7]

    @i0.setter
    def i0(self, idx):
        """Set index of the first region boundary."""
        self._waveform.i0 = idx
        self._set_deprecated(True)

    @i1.setter
    def i1(self, idx):
        """Set index of the second region boundary."""
        self._waveform.i1 = idx
        self._set_deprecated(True)

    @i2.setter
    def i2(self, idx):
        """Set index of the third region boundary."""
        self._waveform.i2 = idx
        self._set_deprecated(True)

    @i3.setter
    def i3(self, idx):
        """Set index of the fourth region boundary."""
        self._waveform.i3 = idx
        self._set_deprecated(True)

    @i4.setter
    def i4(self, idx):
        """Set index of the fifth region boundary."""
        self._waveform.i4 = idx
        self._set_deprecated(True)

    @i5.setter
    def i5(self, idx):
        """Set index of the sixth region boundary."""
        self._waveform.i5 = idx
        self._set_deprecated(True)

    @i6.setter
    def i6(self, idx):
        """Set index of the 7th region boundary."""
        self._waveform.i7 = idx
        self._set_deprecated(True)

    @i7.setter
    def i7(self, idx):
        """Set index of the 8th region boundary."""
        self._waveform.i7 = idx
        self._set_deprecated(True)

    @vL0.setter
    def vL0(self, value):
        """Set waveform value at the left-end and 1st boundary."""
        current = self._calc_currents(value)
        self._waveform.vL0 = current  # This will set deprecated state.

    @v1.setter
    def v1(self, value):
        """Set waveform value at the 2nd region boundary."""
        current = self._calc_currents(value)
        self._waveform.v1 = current  # This will set deprecated state.

    @v2.setter
    def v2(self, value):
        """Set waveform value at the 3rd region boundary."""
        current = self._calc_currents(value)
        self._waveform.v2 = current  # This will set deprecated state.

    @v34.setter
    def v34(self, value):
        """Set waveform value at the 4th and 5th region boundaries."""
        current = self._calc_currents(value)
        self._waveform.v34 = current  # This will set deprecated state.

    @v5.setter
    def v5(self, value):
        """Set waveform value at the 6th region boundary."""
        current = self._calc_currents(value)
        self._waveform.v5 = current  # This will set deprecated state.

    @v6.setter
    def v6(self, value):
        """Set waveform value at the 7th region boundary."""
        current = self._calc_currents(value)
        self._waveform.v6 = current  # This will set deprecated state.

    @v7R.setter
    def v7R(self, value):
        """Set waveform value at the 8th and right-end region boundaries."""
        current = self._calc_currents(value)
        self._waveform.v7R = current  # This will set deprecated state.

    # --- public methods ---

    def change_plateau(self, value):
        """Change waveform plateau value."""
        current = self._calc_currents(value)
        self._waveform.change_plateau(current)

    def change_ramp_up(self,
                       start=None, stop=None,
                       start_value=None, stop_value=None):
        """Change waveform ramp up."""
        i1 = start
        i2 = stop
        v1 = start_value
        v2 = stop_value
        c1, c2 = self._calc_currents([v1, v2])
        self._waveform.change_ramp_up(start=i1, stop=i2,
                                      start_value=c1, stop_value=c2)

    def change_ramp_down(self,
                         start=None, stop=None,
                         start_value=None, stop_value=None):
        """Change waveform ramp down."""
        i5 = start
        i6 = stop
        v5 = start_value
        v6 = stop_value
        c5, c6 = self._calc_currents([v5, v6])
        self._waveform.change_ramp_down(i5=i5, i6=i6, v5=c5, v6=c6)

    def clear_bumps(self):
        """Clear waveform bumps."""
        self._waveform.clear_bumps()
        self._set_deprecated(True)  # clear_bumps DOES NOT set deprecated.

    # --- private methods ---

    def _add_dep_magwfm(self, magwfm):
        """Add dependent magnet waveform."""
        if isinstance(magwfm, MagnetWaveform):
            # add weakref of magwfm object.
            # this way the GC can delete it.
            self._dependents.add(_weakref.ref(magwfm))
        else:
            raise TypeError('Invalid argument type!')

    def _remove_dep_magwfm(self, magwfm):
        """Remove dependent magnet waveform."""
        try:
            self.remove(_weakref.ref(magwfm))
        except KeyError:
            pass

    def _calc_strengths(self, waveform):
        kwargs = {'currents': waveform}
        if self._dipole is not None:
            kwargs['currents_dipole'] = self._dipole.waveform
        if self._family is not None:
            kwargs['currents_family'] = self._family.waveform
        strengths = self.conv_current_2_strength(**kwargs)
        return strengths

    def _calc_currents(self, strength):
        kwargs = {'strengths': strength}
        if self._dipole is not None:
            kwargs['currents_dipole'] = self._dipole.currents
        if self._family is not None:
            kwargs['currents_family'] = self._family.currents
        currents = self.conv_strength_2_current(**kwargs)
        return currents

    def _update_strength(self):
        currents = self.currents  # This updates waveform.
        self._strengths = self._calc_strengths(currents)
        self._set_deprecated(False)

    def _init_waveform(self):
        if self.maname == 'BO-Fam:MA-B':
            eje_energy = 3.0  # [GeV]
            eje_current = self.conv_strength_2_current(eje_energy)
            self._waveform = \
                _Waveform(scale=eje_current)
        elif self.maname == 'SI-Fam:MA-B1B2':
            eje_energy = 3.0  # [GeV]
            eje_current = self.conv_strength_2_current(eje_energy)
            self._waveform = _Waveform()
            self._waveform.waveform = eje_current
        elif self.maname in _nominal_strengths:
            strengths = _nominal_strengths[self.maname] * \
                _np.ones(_Waveform.wfmsize)
            currents = self._calc_currents(strengths)
            self._waveform = _Waveform()
            v07 = currents[self._waveform.i07]
            self._waveform.vL0 = currents[0]
            self._waveform.v1 = v07[1]
            self._waveform.v2 = v07[2]
            self._waveform.v34 = v07[3]
            self._waveform.v5 = v07[5]
            self._waveform.v6 = v07[6]
            self._waveform.v7R = currents[-1]
            # in general, if excitation curves are not exactly linear, a
            # parameterized current waveform becomes, when converted to
            # strength, a waveform that cannot be parameterized using the
            # same polynomials. Therefore waveform_bumps have to accomodate
            # the difference between the closest parameterized current
            # waveform and the waveform that coresponds to the general
            # strength ramp.
            self._waveform.waveform = currents  # force wfm_bumps calculation.
        else:
            self._waveform = _Waveform(scale=0.0)
        self._set_deprecated(True)

    def _set_deprecated(self, state):
        self._deprecated = state
        if state is True:
            for dependent in self._dependents:
                obj = dependent()
                # only sets deprecated state of object if its weakref is valid.
                if obj is None:
                    self._dependents.remove(obj)
                else:
                    obj._set_deprecated()


class WfmSet:
    """Class WfmSet."""

    energy_inj_gev = 0.150  # [GeV]
    energy_eje_gev = 3.000  # [GeV]
    _default_wfm = _np.array(_mutil.get_default_ramp_waveform())

    def __init__(self,
                 dipole_maname,
                 dipole_wfm_strength=None,
                 dipole_wfm_current=None):
        """Init method.

        Parameters
        ----------
        dipole_maname : str | SiriusPVName
            dipole magnet device name for the wfm set.
        dipole_wfm_strength : list | int | float
            dipole wfm in current units.
        dipole_wfm_current : list | int | float
            dipole wfm in strength units.

        """
        self._magnets = {}
        self._wfms_strength = {}
        self._wfms_current = {}
        self._set_dipole(dipole_maname,
                         dipole_wfm_strength,
                         dipole_wfm_current)

    # --- properties ---

    @staticmethod
    def get_default_wfm_form(scale=1.0):
        """Return default wfm form."""
        return [scale * v for v in WfmSet._default_wfm]

    @property
    def magnets(self):
        """Return list of magnet names in wfm set."""
        return list(self._magnets.keys())

    @property
    def section(self):
        """Return section of wfm set."""
        return self._section

    @property
    def dipole_maname(self):
        """Return name of dipole in the wfm set."""
        return self._dipole_maname

    @property
    def index_energy_inj(self):
        """Return waveform index corresponding to the injection energy."""
        wfm_strength = self.get_wfm_strength(maname=self.dipole_maname)
        for i in range(len(wfm_strength)-1):
            if wfm_strength[i] <= WfmSet.energy_inj_gev < wfm_strength[i+1]:
                break
        return i

    @property
    def index_energy_eje(self):
        """Return waveform index corresponding to the ejection energy."""
        wfm_strength = self.get_wfm_strength(maname=self.dipole_maname)
        for i in range(len(wfm_strength)-1):
            if wfm_strength[i] < WfmSet.energy_eje_gev <= wfm_strength[i+1]:
                break
        return i

    # --- public methods ---

    def index_energy(self, energy, ramp_down=False):
        """Return waveform index corresponding to a given energy."""
        wfm = self._wfms_strength[self.dipole_maname]
        if not ramp_down:
            for i in range(1, len(wfm)):
                if wfm[i-1] <= energy < wfm[i]:
                    return i
        else:
            for i in range(1, len(wfm)):
                if wfm[i] <= energy < wfm[i-1]:
                    return i-1

    def set_wfm_strength(self, maname, wfm=None):
        """Set strength wfm for a specific magnet.

        Parameters
        ----------
        maname : str | SiriusPVName
            magnet device name.
        wfm : list | int | float
            magnet wfm in strength units.
        """
        self._update_magnet_wfm(maname, wfm_strength=wfm, wfm_current=None)

    def set_wfm_current(self, maname, wfm=None):
        """Set current wfm for a specific magnet.

        Parameters
        ----------
        maname : str | SiriusPVName
            magnet device name.
        wfm : list | int | float
            magnet wfm in current units.
        """
        self._update_magnet_wfm(maname, wfm_strength=None, wfm_current=wfm)

    def set_wfm_default(self):
        """Set wfm of quadrupoles and sextupoles.

        According to default nominal optics.
        """
        # zero trim power supplies first
        for maname, m in self._magnets.items():
            if m.family_name is not None and m.family_name in _nominal_intkl:
                strength = _nominal_intkl[maname]
                self._wfms_current[maname] = \
                    [0.0 for _ in WfmSet._default_wfm]
                self._wfms_strength[maname] = \
                    [strength for _ in WfmSet._default_wfm]
        # next, update all family power supplies
        for maname, strength in _nominal_intkl.items():
            maname = _SiriusPVName(maname)
            if maname.section == self.section:
                self.set_wfm_strength(maname, strength)

    def get_wfm_strength(self, maname):
        """Return strength wfm of given magnet."""
        return self._wfms_strength[maname].copy()

    def get_wfm_current(self, maname):
        """Return current wfm of given magnet."""
        return self._wfms_current[maname].copy()

    def add_wfm_strength(self, maname, delta,
                         start=None, stop=None, border=0,
                         method=None):
        """Add strength bump to waveform.

            Add strength bump to waveform in a specified region and with a
        certain number of smoothening left and right points.

        Parameters
        ----------

        maname : str | SiriusPVName
            magnet device name whose waveform strength is to be modified.
        delta : float
            strength delta value to be added to the waveform.
        start : int | float | None
            index of the initial point (inclusive) in the waveform to which
            the bump will be added.
        stop : int | float | None
            index of the final point (exclusive) in the waveform to which
            the bump will be added.
        border : int (default 0)| float
            the number of left and right points in the waveform to whose values
            a partial bump will be added in order to smoothen the bump.
            Cubic or tanh fitting is used to smooth the bump. For the Cubic
            fitting continuous first derivatives at both ends are guaranteed.
        method : 'tanh' (default) | 'cubic' | None (default)
            smoothening method to be applied.
        """
        wfm = self.get_wfm_strength(maname)
        start = 0 if start is None else start
        stop = len(wfm) if stop is None else stop
        if method == 'cubic':
            wfm = self._add_smooth_delta_cubic(wfm, delta, start, stop, border)
        else:
            wfm = self._add_smooth_delta_tanh(wfm, delta, start, stop, border)
        self.set_wfm_strength(maname, wfm=wfm)

    # --- private methods ---

    def _set_dipole(self,
                    dipole_maname,
                    dipole_wfm_strength,
                    dipole_wfm_current):
        m = _Magnet(dipole_maname)
        self._dipole_maname = dipole_maname
        self._section = m.maname.section
        self._update_magnet_wfm(dipole_maname,
                                dipole_wfm_strength,
                                dipole_wfm_current)

    def _process_wfm_inputs(self, maname, wfm_strength, wfm_current):
        m = self._magnets[maname]
        # strength or current setpoint?
        if wfm_strength and wfm_current:
            raise Exception('Specify either strength or current wfm for "' +
                            maname + '"!')
        if wfm_strength is None and wfm_current is None:
            if self.section == 'BO' and m.magfunc == 'dipole':
                wfm_strength = WfmSet.energy_eje_gev * WfmSet._default_wfm
                # wfm_strength = \
                #     [WfmSet.energy_eje_gev * v for v in WfmSet._default_wfm]
            elif self.section in ('SI', 'TS') and m.magfunc == 'dipole':
                wfm_strength = \
                    WfmSet.energy_eje_gev * _np.ones(WfmSet._default_wfm.shape)
                # wfm_strength = \
                #     [WfmSet.energy_eje_gev for _ in WfmSet._default_wfm]
            elif self.section == 'TB' and m.magfunc == 'dipole':
                wfm_strength = \
                    WfmSet.energy_inj_gev * _np.ones(WfmSet._default_wfm.shape)
                # wfm_strength = \
                #     [WfmSet.energy_inj_gev for _ in WfmSet._default_wfm]
            elif maname in _nominal_intkl:
                wfm_strength = _nominal_intkl[maname] * \
                    _np.ones(WfmSet._default_wfm.shape)
            else:
                wfm_strength = _np.zeros(WfmSet._default_wfm.shape)
            self._wfms_strength[maname] = wfm_strength
        if type(wfm_strength) in (int, float):
            wfm_strength = wfm_strength * _np.ones(WfmSet._default_wfm.shape)
        if type(wfm_current) in (int, float):
            wfm_current = wfm_current * _np.ones(WfmSet._default_wfm.shape)
        return wfm_strength, wfm_current

    def _update_dipole_wfm(self,
                           maname,
                           wfm_strength,
                           wfm_current):
        m = self._magnets[maname]
        if wfm_strength is not None:
            wfm_current = m.conv_strength_2_current(wfm_strength)
            # wfm_current = \
            #     [m.conv_strength_2_current(v) for v in wfm_strength]
        else:
            wfm_strength = m.conv_current_2_strength(wfm_current)
            # wfm_strength = \
            #     [m.conv_current_2_strength(v) for v in wfm_current]
        self._wfms_current[maname] = wfm_current
        self._wfms_strength[maname] = wfm_strength
        # recursively invoke itself to update families
        for name, mag in self._magnets.items():
            if mag.dipole_name is not None and mag.family_name is None:
                # update all families
                strength = self._wfms_strength[name]
                self._update_family_wfm(
                    name, wfm_strength=strength, wfm_current=wfm_current)

    def _update_family_wfm(self,
                           maname,
                           wfm_strength,
                           wfm_current):
        m = self._magnets[maname]
        c_dip = self._wfms_current[self._dipole_maname]
        if wfm_strength is not None:
            wfm_current = m.conv_strength_2_current(
                wfm_strength, currents_dipole=c_dip)
            # wfm_current = [m.conv_strength_2_current(
            #                wfm_strength[i],
            #                currents_dipole=c_dip[i])
            #                for i in range(len(wfm_strength))]
        else:
            wfm_strength = m.conv_current_2_strength(
                wfm_current, currents_dipole=c_dip)
        self._wfms_current[maname] = wfm_current
        self._wfms_strength[maname] = wfm_strength
        # recursively invoke itself to update trims
        for name, mag in self._magnets.items():
            if mag.dipole_name is not None and mag.family_name is not None:
                # update all trims
                strength = self._wfms_strength[name]
                self._update_trim_wfm(
                    name, wfm_strength=strength, wfm_current=wfm_current)

    def _update_trim_wfm(self,
                         maname,
                         wfm_strength,
                         wfm_current):
        m = self._magnets[maname]
        c_dip = self._wfms_current[self._dipole_maname]
        c_fam = self._wfms_current[self._family_name]
        if wfm_strength:
            wfm_current = [m.conv_strength_2_current(
                           wfm_strength[i],
                           currents_dipole=c_dip[i],
                           currents_family=c_fam[i])
                           for i in range(len(wfm_strength))]
        else:
            wfm_strength = [m.conv_current_2_strength(
                            wfm_current[i],
                            currents_dipole=c_dip[i],
                            currents_family=c_fam[i])
                            for i in range(len(wfm_current))]
        self._wfms_current[maname] = wfm_current
        self._wfms_strength[maname] = wfm_strength

    def _update_magnet_wfm(self,
                           maname,
                           wfm_strength,
                           wfm_current):
        # add magnet in dict if not there yet.
        if maname not in self._magnets:
            self._magnets[maname] = _Magnet(maname)

        wfm_strength, wfm_current = \
            self._process_wfm_inputs(maname, wfm_strength, wfm_current)

        m = self._magnets[maname]
        # set wfm acoording to type of magnet
        if m.dipole_name is None:
            self._update_dipole_wfm(maname, wfm_strength, wfm_current)
        elif m.family_name is None:
            self._update_family_wfm(maname, wfm_strength, wfm_current)
        else:
            self._update_trim_wfm(maname, wfm_strength, wfm_current)

    @staticmethod
    def _add_smooth_delta_cubic(wfm, D, start, stop, d):
        # left side smoothing
        wfm = wfm.copy()
        if d > 0:
            for i in range(0, d+1):
                f = i / (d+1)
                idx = i + start - (d+1)
                if idx >= 0:
                    wfm[idx] += D*f**2*(3-2*f)
        # center bump
        for i in range(start, stop):
            wfm[i] += D
        # right side smoothing
        if d > 0:
            for i in range(0, d+1):
                f = i / (d+1)
                idx = stop + (d+1) - i - 1
                if idx >= 0:
                    wfm[idx] += D*f**2*(3-2*f)
        return wfm

    @staticmethod
    def _add_smooth_delta_tanh(wfm, D, start, stop, border):
        if border == 0.0:
            wfm = wfm.copy()
            for i in range(max(0, int(start)), min(len(wfm), stop)):
                wfm[i] += D
        else:
            x = _np.linspace(0, len(wfm)-1.0, len(wfm))
            wL, wR = border, border
            xL, xR = start, stop-1
            dx = xR - xL
            Dstar = 2*D/(_np.tanh(dx/2.0/wL)+_np.tanh(dx/2.0/wR))
            dy = (Dstar/2.0) * (_np.tanh((x-xL)/wL) - _np.tanh((x-xR)/wR))
            wfm = [wfm[i]+dy[i] for i in range(len(wfm))]
        return wfm
