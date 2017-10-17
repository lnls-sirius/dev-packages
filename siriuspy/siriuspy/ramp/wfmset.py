"""wfm utilities."""

import numpy as _np
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.ramp.magnet import Magnet as _Magnet
from siriuspy.ramp.optics import _nominal_intkl
from siriuspy.magnet import util as _mutil


class WfmSet:
    """Class WfmSet."""

    energy_inj_gev = 0.150  # [GeV]
    energy_eje_gev = 3.000  # [GeV]
    _default_wfm = _mutil.get_default_ramp_waveform()

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
                wfm_strength = \
                    [WfmSet.energy_eje_gev * v for v in WfmSet._default_wfm]
            elif self.section in ('SI', 'TS') and m.magfunc == 'dipole':
                wfm_strength = \
                    [WfmSet.energy_eje_gev for _ in WfmSet._default_wfm]
            elif self.section == 'TB' and m.magfunc == 'dipole':
                wfm_strength = \
                    [WfmSet.energy_inj_gev for _ in WfmSet._default_wfm]
            elif maname in _nominal_intkl:
                wfm_strength = _nominal_intkl[maname]
            else:
                wfm_strength = [0.0 for _ in WfmSet._default_wfm]
            self._wfms_strength[maname] = wfm_strength
        if type(wfm_strength) in (int, float):
            wfm_strength = [wfm_strength for _ in WfmSet._default_wfm]
        if type(wfm_current) in (int, float):
            wfm_current = [wfm_current for _ in WfmSet._default_wfm]
        return wfm_strength, wfm_current

    def _update_dipole_wfm(self,
                           maname,
                           wfm_strength,
                           wfm_current):
        m = self._magnets[maname]
        if wfm_strength:
            wfm_current = \
                [m.conv_strength_2_current(v) for v in wfm_strength]
        else:
            wfm_strength = \
                [m.conv_current_2_strength(v) for v in wfm_current]
        self._wfms_current[maname] = wfm_current
        self._wfms_strength[maname] = wfm_strength
        # recursively invoke itself to update families
        for name, mag in self._magnets.items():
            if mag.dipole_name is not None and mag.family_name is None:
                # update all families
                strength = self._wfms_strength[name]
                self._update_family_wfm(name, wfm_strength=strength)

    def _update_family_wfm(self,
                           maname,
                           wfm_strength,
                           wfm_current):
        m = self._magnets[maname]
        c_dip = self._wfms_current[self._dipole_maname]
        if wfm_strength:
            wfm_current = [m.conv_strength_2_current(
                           wfm_strength[i],
                           current_dipole=c_dip[i])
                           for i in range(len(wfm_strength))]
        else:
            wfm_strength = [m.conv_current_2_strength(
                            wfm_current[i],
                            current_dipole=c_dip[i])
                            for i in range(len(wfm_current))]
        self._wfms_current[maname] = wfm_current
        self._wfms_strength[maname] = wfm_strength
        # recursively invoke itself to update trims
        for name, mag in self._magnets.items():
            if mag.dipole_name is not None and mag.family_name is not None:
                # update all trims
                strength = self._wfms_strength[name]
                self._update_trim_wfm(name, wfm_strength=strength)

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
                           current_dipole=c_dip[i],
                           current_family=c_fam[i])
                           for i in range(len(wfm_strength))]
        else:
            wfm_strength = [m.conv_current_2_strength(
                            wfm_current[i],
                            current_dipole=c_dip[i],
                            current_family=c_fam[i])
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
