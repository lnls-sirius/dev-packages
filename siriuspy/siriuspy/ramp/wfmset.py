"""Waveform Set Module."""

import numpy as _np
from siriuspy.csdevice.pwrsupply import default_wfmsize as _default_wfmsize
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.ramp.magnet import Magnet as _Magnet
from siriuspy.ramp.optics import _nominal_intkl
from siriuspy.magnet import util as _mutil


_np.seterr(all='ignore')


class Waveform:
    """Waveform parameter class."""

    def __init__(self,
                 vL=None,
                 vR=None,
                 i07=None,
                 v07=None,
                 waveform=None):
        """Init method."""
        self._set_params(vL, vR, i07, v07)
        self._update_wfm_parms()
        self._update_wfm_bumps(waveform)

    # --- properties ---

    @property
    def waveform(self):
        """Return waveform."""
        if self._deprecated:
            self._update_wfm_parms()
        return self._wfm_parms + self._wfm_bumps

    @waveform.setter
    def waveform(self, waveform):
        self._update_wfm_bumps(waveform)

    @property
    def i0(self):
        """Return index of the first region boundary."""
        return self._i[0]

    @property
    def i1(self):
        """Return index of the second region boundary."""
        return self._i[1]

    @property
    def i2(self):
        """Return index of the third region boundary."""
        return self._i[2]

    @property
    def i3(self):
        """Return index of the fourth region boundary."""
        return self._i[3]

    @property
    def i4(self):
        """Return index of the fifth region boundary."""
        return self._i[4]

    @property
    def i5(self):
        """Return index of the sixth region boundary."""
        return self._i[5]

    @property
    def i6(self):
        """Return index of the seventh region boundary."""
        return self._i[6]

    @property
    def i7(self):
        """Return index of the eightth region boundary."""
        return self._i[7]

    @property
    def vL0(self):
        """Return waveform value at the left-end and first region boundary."""
        return self._vL

    @property
    def v1(self):
        """Return waveform value at the second region boundary."""
        return self._v[1]

    @property
    def v2(self):
        """Return waveform value at the 3rd region boundary."""
        return self._v[2]

    @property
    def v34(self):
        """Return waveform value at the 4th and 5th region boundaries."""
        return self._v[3]

    @property
    def v5(self):
        """Return waveform value at the 6h region boundary."""
        return self._v[5]

    @property
    def v6(self):
        """Return waveform value at the 7th region boundary."""
        return self._v[6]

    @property
    def v7R(self):
        """Return waveform value at the 8th and right-end region boundaries."""
        return self._vR

    @i0.setter
    def i0(self, idx):
        """Set index of the first region boundary."""
        i = 0
        if 0 <= idx <= self._i[i+1]:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @i1.setter
    def i1(self, idx):
        """Set index of the second region boundary."""
        i = 1
        if self._i[i-1] <= idx <= self._i[i+1]:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @i2.setter
    def i2(self, idx):
        """Set index of the third region boundary."""
        i = 2
        if self._i[i-1] <= idx <= self._i[i+1]:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @i3.setter
    def i3(self, idx):
        """Set index of the fourth region boundary."""
        i = 3
        if self._i[i-1] <= idx <= self._i[i+1]:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @i4.setter
    def i4(self, idx):
        """Set index of the fifth region boundary."""
        i = 4
        if self._i[i-1] <= idx <= self._i[i+1]:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @i5.setter
    def i5(self, idx):
        """Set index of the sixth region boundary."""
        i = 5
        if self._i[i-1] <= idx < _default_wfmsize:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @i6.setter
    def i6(self, idx):
        """Set index of the 7th region boundary."""
        i = 6
        if self._i[i-1] <= idx < _default_wfmsize:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @i7.setter
    def i7(self, idx):
        """Set index of the 8th region boundary."""
        i = 7
        if self._i[i-1] <= idx < _default_wfmsize:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @vL0.setter
    def vL0(self, value):
        """Set waveform value at the left-end and 1st boundary."""
        self._vL = value
        self._v[0] = value
        self._deprecated = True

    @v1.setter
    def v1(self, value):
        """Set waveform value at the 2nd region boundary."""
        self._v[1] = value
        self._deprecated = True

    @v2.setter
    def v2(self, value):
        """Set waveform value at the 3rd region boundary."""
        self._v[2] = value
        self._deprecated = True

    @v34.setter
    def v34(self, value):
        """Set waveform value at the 4th and 5th region boundaries."""
        self._v[3] = value
        self._v[4] = value
        self._deprecated = True

    @v5.setter
    def v5(self, value):
        """Set waveform value at the 6th region boundary."""
        self._v[5] = value
        self._deprecated = True

    @v6.setter
    def v6(self, value):
        """Set waveform value at the 7th region boundary."""
        self._v[6] = value
        self._deprecated = True

    @v7R.setter
    def v7R(self, value):
        """Set waveform value at the 8th and right-end region boundaries."""
        self._v[7] = value
        self._vR = value
        self._deprecated = True

    # # --- public methods ---
    #
    # def eval(self, idx=None):
    #     """Evaluate parameterized waveform at idx values or at index
    #     values.
    #     """
    #     if self._deprecated:
    #         self._set_coeffs()
    #         self._deprecated = False
    #     if idx is None:
    #         # return waveform at index value
    #         return self._eval_index()
    #     # return waveform as idx values
    #     try:
    #         if type(idx) == _np.ndarray:
    #             v = _np.zeros(idx.shape)
    #         else:
    #             v = [0.0] * len(idx)
    #         for i in range(len(idx)):
    #             v[i] = self._eval_point(idx[i])
    #         return v
    #     except TypeError:
    #         return self._eval_point(idx)

    def change_ramp_up(self, i1, i2, v1, v2):
        """Change rampup."""
        if i1 < self._i[0] or i2 <= i1 or i2 >= self._i[4] or \
           v1 >= v2 or v1 <= self._v[0] or v2 >= self._v[3]:
            raise ValueError('Invalid ramp parameters !')
        i3 = self._find_i3(i1, i2, v1, v2)
        if i3 is None:
            raise ValueError('Could not find solution for i3 !')
        i0 = self._find_i0(i1, i2, v1, v2)
        if i0 is None:
            raise ValueError('Could not find solution for i0 !')
        self._i[0] = i0
        self._i[1] = i1
        self._i[2] = i2
        self._i[3] = i3
        self._v[1] = v1
        self._v[2] = v2
        self._deprecated = True

    def change_ramp_down(self, i5, i6, v5, v6):
        """Change rampup."""
        if i5 < self._i[4] or i6 <= i5 or i6 >= _default_wfmsize or \
           v5 <= v6 or v5 >= self._v[4] or v6 <= self._v[7]:
            raise ValueError('Invalid ramp parameters !')
        i7 = self._find_i7(i5, i6, v5, v6)
        if i7 is None:
            raise ValueError('Could not find solution for i7 !')
        i4 = self._find_i4(i5, i6, v5, v6)
        if i4 is None:
            raise ValueError('Could not find solution for i4 !')
        self._i[4] = i4
        self._i[5] = i5
        self._i[6] = i6
        self._i[7] = i7
        self._v[5] = v5
        self._v[6] = v6
        self._deprecated = True

    # --- private methods ---

    def _update_wfm_parms(self):
        self._set_coeffs()
        self._wfm_parms = self._eval_index()
        self._deprecated = False

    @staticmethod
    def _calccoeffs(d, dv, DL, DR):
        v1 = dv - DL * d
        v2 = DR - DL
        m11 = 3.0/d**2
        m12 = -1.0/d
        m21 = -2.0/d**3
        m22 = 1.0/d**2
        a0 = DL
        b0 = m11 * v1 + m12 * v2
        c0 = m21 * v1 + m22 * v2
        coeffs = [a0, b0, c0]
        return coeffs

    def _set_params(self, vL, vR, i07, v07):
        self._vL = 0.01 if vL is None else vL
        self._vR = 0.01 if vR is None else vR
        if i07 is None:
            i07 = _np.array([0, 104, 2480, 2576, 2640, 2736, 3840, 4000])
        if v07 is None:
            v07 = _np.array([0.01, 0.02625, 1.0339285714, 1.05,
                             1.05, 1.0, 0.07, 0.01])
        try:
            if len(i07) != 8:
                raise ValueError('Lenght of i07 is not 6 !')
            if i07[0] < 0:
                raise ValueError('i0 < 0 !')
            if i07[-1] > _default_wfmsize:
                raise ValueError('i7 >= {} !'.format(_default_wfmsize))
            for i in range(0, len(i07)-1):
                if i07[i+1] < i07[i]:
                    raise ValueError('i07 is not sorted !')
            self._i = [int(i) for i in i07]
        except TypeError:
            raise TypeError('Invalid type of i07 !')
        try:
            v07[0]
            if len(v07) != 8:
                raise ValueError('Lenght of v07 is not 8 !')
            self._v = v07.copy()
        except TypeError:
            raise TypeError('Invalid type v07 !')

    def _set_coeffs(self):
        self._coeffs = [None] * 9
        if self._i[0] == 0:
            self._D0 = 0.0
        else:
            self._D0 = (self._v[0] - self._vL) / (self._i[0] - 0)
        self._D2 = (self._v[2] - self._v[1]) / (self._i[2] - self._i[1])
        self._D4 = (self._v[4] - self._v[3]) / (self._i[4] - self._i[3])
        self._D6 = (self._v[6] - self._v[5]) / (self._i[6] - self._i[5])
        if self._i[7] == _default_wfmsize:
            self._D8 = 0.0
        else:
            self._D8 = (self._vR - self._v[7]) / \
                       (_default_wfmsize - self._i[7])
        # region 0
        self._coeffs[0] = _np.array([self._D0, 0.0, 0.0])
        # region 1
        d = self._i[1] - self._i[0]
        dv = self._v[1] - self._v[0]
        self._coeffs[1] = Waveform._calccoeffs(d, dv, self._D0, self._D2)
        # region 2
        self._coeffs[2] = _np.array([self._D2, 0.0, 0.0])
        # region 3
        d = self._i[3] - self._i[2]
        dv = self._v[3] - self._v[2]
        self._coeffs[3] = Waveform._calccoeffs(d, dv, self._D2, self._D4)
        # region 4
        self._coeffs[4] = _np.array([self._D4, 0.0, 0.0])
        # region 5
        d = self._i[5] - self._i[4]
        dv = self._v[5] - self._v[4]
        self._coeffs[5] = Waveform._calccoeffs(d, dv, self._D4, self._D6)
        # region 6
        self._coeffs[6] = [self._D6, 0.0, 0.0]
        # region 7
        d = self._i[7] - self._i[6]
        dv = self._v[7] - self._v[6]
        self._coeffs[7] = Waveform._calccoeffs(d, dv, self._D6, self._D8)
        # region 8
        self._coeffs[8] = [self._D8, 0.0, 0.0]

    def _eval_index(self):

        def calcdv(i, iref, coeffs):
            return coeffs[0] * (i - iref) + \
                   coeffs[1] * (i - iref)**2 + \
                   coeffs[2] * (i - iref)**3

        wfm = []
        # region 0
        coeffs = self._coeffs[0]
        iref, vref = 0, self._vL
        i = _np.array(tuple(range(self._i[0])))
        dv = calcdv(i, iref, coeffs)
        wfm.extend(vref + dv)
        # regions 1...7
        for i in range(1, 8):
            coeffs = self._coeffs[i]
            iref, vref = self._i[i-1], self._v[i-1]
            i = _np.array(tuple(range(self._i[i-1], self._i[i])))
            dv = calcdv(i, iref, coeffs)
            wfm.extend(vref + dv)
        # region 8
        coeffs = self._coeffs[8]
        iref, vref = self._i[7], self._v[7]
        i = _np.array(tuple(range(self._i[7], _default_wfmsize)))
        dv = calcdv(i, iref, coeffs)
        wfm.extend(vref + dv)
        return _np.array(wfm)

    def _find_i3(self, i1, i2, v1, v2):
        D2 = (v2 - v1) / (i2 - i1)
        dv = self._v[3] - v2
        i3 = _np.arange(i2+1, self._i[4])
        D4 = (self._v[4] - self._v[3]) / (self._i[4] - i3)
        d = i3 - i2
        a, b, c = Waveform._calccoeffs(d, dv, D2, D4)
        phi = b**2 - 3*c*a
        i3_r1 = i2 + (-b + _np.sqrt(phi))/3.0/c
        i3_r2 = i2 + (-b - _np.sqrt(phi))/3.0/c
        cond = ((i3_r1 < i2) | (i3_r1 >= i3) | _np.isnan(i3_r1)) & \
               ((i3_r2 < i2) | (i3_r2 >= i3) | _np.isnan(i3_r2))
        # for i in range(len(i3)):
        #     di = i3[i] - self._i[3]
        #     print(('{},  d:{}, i3_r1:{:.1f}, i3_r2:{:.1f}, '
        #            'i2:{}, i3:{}').format(cond[i], di, i3_r1[i], i3_r2[i],
        #                                   i2, i3[i]))
        i3_solutions = i3[cond]
        if i3_solutions.size:
            i3_delta = min(i3_solutions - self._i[3], key=abs)
            return self._i[3] + i3_delta
        else:
            return None

    def _find_i0(self, i1, i2, v1, v2):
        D2 = (v2 - v1) / (i2 - i1)
        dv = v1 - self._v[0]
        i0 = _np.arange(1, i1)
        D0 = (self._v[0] - self._vL) / (i0 - 0)
        d = i1 - i0
        a, b, c = Waveform._calccoeffs(d, dv, D0, D2)
        phi = b**2 - 3*c*a
        i0_r1 = i0 + (-b + _np.sqrt(phi))/3.0/c
        i0_r2 = i0 + (-b - _np.sqrt(phi))/3.0/c
        cond = ((i0_r1 <= i0) | (i0_r1 >= i1) | _np.isnan(i0_r1)) & \
               ((i0_r2 <= i0) | (i0_r2 >= i1) | _np.isnan(i0_r2))
        i0_solutions = i0[cond]
        if i0_solutions.size:
            i0_delta = min(i0_solutions - self._i[0], key=abs)
            return self._i[0] + i0_delta
        else:
            return None

    def _find_i7(self, i5, i6, v5, v6):
        D6 = (v6 - v5) / (i6 - i5)
        dv = self._v[3] - v2
        i3 = _np.arange(i2+1, self._i[4])
        D4 = (self._v[4] - self._v[3]) / (self._i[4] - i3)
        d = i3 - i2
        a, b, c = Waveform._calccoeffs(d, dv, D2, D4)
        phi = b**2 - 3*c*a
        i3_r1 = i2 + (-b + _np.sqrt(phi))/3.0/c
        i3_r2 = i2 + (-b - _np.sqrt(phi))/3.0/c
        cond = ((i3_r1 < i2) | (i3_r1 >= i3) | _np.isnan(i3_r1)) & \
               ((i3_r2 < i2) | (i3_r2 >= i3) | _np.isnan(i3_r2))
        # for i in range(len(i3)):
        #     di = i3[i] - self._i[3]
        #     print(('{},  d:{}, i3_r1:{:.1f}, i3_r2:{:.1f}, '
        #            'i2:{}, i3:{}').format(cond[i], di, i3_r1[i], i3_r2[i],
        #                                   i2, i3[i]))
        i3_solutions = i3[cond]
        if i3_solutions.size:
            i3_delta = min(i3_solutions - self._i[3], key=abs)
            return self._i[3] + i3_delta
        else:
            return None

    def _update_wfm_bumps(self, waveform):
        if waveform is None:
            self._wfm_bumps = _np.zeros((_default_wfmsize, ))
        else:
            if self._deprecated:
                self._update_wfm_parms()
            self._wfm_bumps = _np.array(waveform) - self._wfm_parms




    # def _eval_point(self, idx):
    #     if idx < 0 or idx >= _default_wfmsize:
    #         raise ValueError('idx value out of range: {}!'.format(idx))
    #     coeffs, v0 = None, None
    #     if idx < self._i[0]:
    #         coeffs = self._coeffs[0]
    #         i0, v0 = 0, self._vL
    #     elif idx > self._i[5]:
    #         coeffs = self._coeffs[6]
    #         i0, v0 = self._i[5], self._v[5]
    #     else:
    #         for i in range(len(self._i)):
    #             if idx <= self._i[i]:
    #                 i0, v0 = self._i[i-1], self._v[i-1]
    #                 coeffs = self._coeffs[i]
    #                 break
    #     dv = \
    #         coeffs[0] * (idx - i0) + \
    #         coeffs[1] * (idx - i0)**2 + \
    #         coeffs[2] * (idx - i0)**3
    #     return v0 + dv


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
