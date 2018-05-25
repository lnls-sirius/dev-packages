"""Waveform classes."""

import numpy as _np

from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE as _MAX_WFMSIZE
from siriuspy.ramp import util as _util
from siriuspy.ramp.magnet import Magnet as _Magnet


_np.seterr(all='ignore')


class WaveformParam:
    """Dipole parameterized Waveforms."""

    def __init__(self,
                 scale=None,
                 start_value=None,
                 stop_value=None,
                 boundary_indices=None,
                 boundary_values=None,
                 wfm_nrpoints=_MAX_WFMSIZE,
                 duration=_util.DEFAULT_RAMP_DURATION):
        """Init method."""
        self._wfm_nrpoints = wfm_nrpoints
        self._duration = duration
        self._set_params(scale,
                         vL=start_value, vR=stop_value,
                         i07=boundary_indices, v07=boundary_values)
        self.update()

    # --- public properties ---

    @property
    def start_value(self):
        """Return waveform value at the left-end and first region boundary."""
        return self._vL

    @property
    def rampup_start_index(self):
        """Return index of the second region boundary."""
        return self._i[1]

    @property
    def rampup_start_value(self):
        """Return waveform value at the second region boundary."""
        return self._v[1]

    @property
    def rampup_start_time(self):
        """Instant in time when rampup starts."""
        return self.rampup_start_index * \
            self.duration / (self.wfm_nrpoints - 1.0)

    @property
    def rampup_stop_index(self):
        """Return index of the third region boundary."""
        return self._i[2]

    @property
    def rampup_stop_value(self):
        """Return waveform value at the 3rd region boundary."""
        return self._v[2]

    @property
    def rampup_stop_time(self):
        """Instant in time when rampup stops."""
        return self.rampup_stop_index * \
            self.duration / (self.wfm_nrpoints - 1.0)

    @property
    def plateau_start_index(self):
        """Return index of the fourth region boundary."""
        return self._i[3]

    @property
    def plateau_start_time(self):
        """Instant in time when plateau starts."""
        return self.plateau_start_index * \
            self.duration / (self.wfm_nrpoints - 1.0)

    @property
    def plateau_stop_index(self):
        """Return index of the fifth region boundary."""
        return self._i[4]

    @property
    def plateau_stop_time(self):
        """Instant in time when plateau stops."""
        return self.plateau_stop_index * \
            self.duration / (self.wfm_nrpoints - 1.0)

    @property
    def plateau_value(self):
        """Return waveform value at the 4th and 5th region boundaries."""
        return self._v[3]

    @property
    def rampdown_start_index(self):
        """Return index of the sixth region boundary."""
        return self._i[5]

    @property
    def rampdown_start_value(self):
        """Return waveform value at the 6h region boundary."""
        return self._v[5]

    @property
    def rampdown_start_time(self):
        """Instant in time when rampdown starts."""
        return self.rampdown_start_index * \
            self.duration / (self.wfm_nrpoints - 1.0)

    @property
    def rampdown_stop_index(self):
        """Return index of the seventh region boundary."""
        return self._i[6]

    @property
    def rampdown_stop_value(self):
        """Return waveform value at the 7th region boundary."""
        return self._v[6]

    @property
    def rampdown_stop_time(self):
        """Instant in time when rampdown stops."""
        return self.rampdown_stop_index * \
            self.duration / (self.wfm_nrpoints - 1.0)

    @property
    def stop_value(self):
        """Return waveform value at the 8th and right-end region boundaries."""
        return self._vR

    @property
    def waveform(self):
        """Waveform."""
        if self._deprecated:
            self.update()
        return self._waveform

    @property
    def boundary_indices(self):
        """Return list of regions boundary indices."""
        return [i for i in self._i]

    @property
    def boundary_times(self):
        """Return list of regions boundary instants."""
        return [i * self.duration / (self.wfm_nrpoints - 1.0) for i in self._i]

    @property
    def wfm_nrpoints(self):
        """Waveform nrpoints."""
        return self._wfm_nrpoints

    @property
    def duration(self):
        """Ramp duration."""
        return self._duration

    @property
    def deprecated(self):
        """Deprecated state."""
        return self._deprecated

    # --- public setters ---

    @start_value.setter
    def start_value(self, value):
        """Set waveform value at the left-end and 1st boundary."""
        self._vL = value
        self._v[0] = value
        self._deprecated = True

    @rampup_start_index.setter
    def rampup_start_index(self, idx):
        """Set index of the second region boundary."""
        i = 1
        if self._i[i-1] <= idx <= self._i[i+1]:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @rampup_start_value.setter
    def rampup_start_value(self, value):
        """Set waveform value at the 2nd region boundary."""
        self._v[1] = value
        self._deprecated = True

    @rampup_stop_index.setter
    def rampup_stop_index(self, idx):
        """Set index of the third region boundary."""
        i = 2
        if self._i[i-1] <= idx <= self._i[i+1]:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @rampup_stop_value.setter
    def rampup_stop_value(self, value):
        """Set waveform value at the 3rd region boundary."""
        self._v[2] = value
        self._deprecated = True

    @plateau_start_index.setter
    def plateau_start_index(self, idx):
        """Set index of the fourth region boundary."""
        i = 3
        if self._i[i-1] <= idx <= self._i[i+1]:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @plateau_stop_index.setter
    def plateau_stop_index(self, idx):
        """Set index of the fifth region boundary."""
        i = 4
        if self._i[i-1] <= idx <= self._i[i+1]:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @plateau_value.setter
    def plateau_value(self, value):
        """Set waveform value at the 4th and 5th region boundaries."""
        if value < self.rampup_stop_value or value < self.rampdown_start_value:
            raise ValueError('Invalid plateau parameter !')
        self._v[3] = value
        self._v[4] = value
        self._deprecated = True

    @rampdown_start_index.setter
    def rampdown_start_index(self, idx):
        """Set index of the sixth region boundary."""
        i = 5
        if self._i[i-1] <= idx < self.wfm_nrpoints:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @rampdown_start_value.setter
    def rampdown_start_value(self, value):
        """Set waveform value at the 6th region boundary."""
        self._v[5] = value
        self._deprecated = True

    @rampdown_stop_index.setter
    def rampdown_stop_index(self, idx):
        """Set index of the 7th region boundary."""
        i = 6
        if self._i[i-1] <= idx < self.wfm_nrpoints:
            self._i[i] = idx
        else:
            raise ValueError(('Index is inconsistent with labeled '
                              'region boundary points.'))
        self._deprecated = True

    @rampdown_stop_value.setter
    def rampdown_stop_value(self, value):
        """Set waveform value at the 7th region boundary."""
        self._v[6] = value
        self._deprecated = True

    @stop_value.setter
    def stop_value(self, value):
        """Set waveform value at the 8th and right-end region boundaries."""
        self._v[7] = value
        self._vR = value
        self._deprecated = True

    # --- public methods ---

    def rampup_change(self,
                      start=None, stop=None,
                      start_value=None, stop_value=None):
        """Change waveform ramp up avoiding overshootings."""
        i1 = start
        i2 = stop
        v1 = start_value
        v2 = stop_value
        i1 = self.rampup_start_index if i1 is None else i1
        i2 = self.rampup_stop_index if i2 is None else i2
        v1 = self.rampup_start_value if v1 is None else v1
        v2 = self.rampup_stop_value if v2 is None else v2
        if i1 < self._i[0] or i2 <= i1 or i2 >= self.plateau_stop_index or \
           v1 >= v2 or v1 <= self.start_value or v2 >= self.plateau_value:
            raise ValueError('Invalid ramp up parameters !')
        i3 = self._find_i3(i1, i2, v1, v2)
        if i3 is None:
            raise ValueError('Could not find solution '
                             'for plateau_start_index !')
        i0 = self._find_i0(i1, i2, v1, v2)
        if i0 is None:
            raise ValueError('Could not find solution for i0 !')
        # change internal data - deprecated is automatically set to True.
        self.rampup_start_index = i1
        self.rampup_stop_index = i2
        self.rampup_start_value = v1
        self.rampup_stop_value = v2
        self.plateau_start_index = i3
        self._i[0], self._deprecated = i0, True

    def rampdown_change(self,
                        start=None, stop=None,
                        start_value=None, stop_value=None):
        """Change waveform ramp down."""
        i5 = start
        i6 = stop
        v5 = start_value
        v6 = stop_value
        i5 = self.rampdown_start_index if i5 is None else i5
        i6 = self.rampdown_stop_index if i6 is None else i6
        v5 = self.rampdown_start_value if v5 is None else v5
        v6 = self.rampdown_stop_value if v6 is None else v6
        if i5 < self.plateau_stop_index or i6 <= i5 or \
           i6 >= self.wfm_nrpoints or v5 <= v6 or \
           v5 >= self.plateau_value or v6 <= self.stop_value:
            raise ValueError('Invalid ramp down parameters !')
        i7 = self._find_i7(i5, i6, v5, v6)
        if i7 is None:
            raise ValueError('Could not find solution for i7 !')
        i4 = self._find_i4(i5, i6, v5, v6)
        if i4 is None:
            raise ValueError('Could not find solution '
                             'for plateau_stop_index !')
        # change internal data - deprecated is automatically set to True.
        self.rampdown_start_index = i5
        self.rampdown_stop_index = i6
        self.rampdown_start_value = v5
        self.rampdown_stop_value = v6
        self._i[7], self._deprecated = i7, True
        self.plateau_stop_index = i4

    def update(self):
        """Update object."""
        self._set_coeffs()
        self._waveform = self._eval_index()
        self._deprecated = False

    def check(self):
        """Check consistency of parameters."""
        try:
            self._set_coeffs()
            self._eval_index()
            self.rampup_change()
            self.rampdown_change()
            return True
        except ValueError:
            return False

    # --- list methods ---

    def __getitem__(self, index):
        """Return waveform at index."""
        if self._deprecated:
            self.update()
        if isinstance(index, slice):
            wp = self._waveform[index]
            return _np.array([wp[i] for i in range(len(wp))])
        elif isinstance(index, int):
            return self._waveform[index]
        else:
            raise IndexError

    def __iter__(self):
        """Return iterator for waveform."""
        if self._deprecated:
            self.update()
        for i in range(len(self._waveform)):
            yield(self._waveform[i])

    def __reversed__(self):
        """Return reverse iterator for waveform."""
        if self._deprecated:
            self.update()
        for i in range(len(self._waveform)-1, -1, -1):
            yield(self._waveform[i])

    def __len__(self):
        """Return length of waveform."""
        return self.wfm_nrpoints

    def __contains__(self, value):
        """Check whether value is in waveform."""
        return value in self.waveform

    def __eq__(self, value):
        """Compare waveforms."""
        return self.waveform == value

    # --- private methods ---

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

    def _set_params(self, scale, vL, vR, i07, v07):
        scale = 1.0 if scale is None else scale
        self._vL = 0.01*scale if vL is None else vL
        self._vR = 0.01*scale if vR is None else vR
        if i07 is None:
            i07 = _np.array([1, 104, 2480,
                             2576, 2640, 2736, 3840, 3999])
        if v07 is None:
            v07 = scale * _np.array([0.01, 0.026250000000000006,
                                     1.0339285714285713, 1.05, 1.05, 1.0, 0.07,
                                     0.01])
        try:
            if len(i07) != 8:
                raise ValueError('Size of i07 is not 8!')
            if i07[0] < 0:
                raise ValueError('i0 < 0 !')
            if i07[-1] > self.wfm_nrpoints:
                raise ValueError('i7 >= {} !'.format(self.wfm_nrpoints))
            for i in range(0, len(i07)-1):
                if i07[i+1] < i07[i]:
                    raise ValueError('Boundary indices list is not sorted!')
            self._i = [int(i) for i in i07]
        except TypeError:
            raise TypeError('Invalid type of boundary indices list!')
        try:
            v07[0]
            if len(v07) != 8:
                raise ValueError('Lenght of boundary values list is not 8 !')
            self._v = v07.copy()
        except TypeError:
            raise TypeError('Invalid type boundary values list!')

    def _set_coeffs(self):
        self._coeffs = [None] * 9
        self._D0 = (self._v[0] - self._vL) / (self._i[0] - 0)
        self._D2 = (self._v[2] - self._v[1]) / (self._i[2] - self._i[1])
        self._D4 = (self._v[4] - self._v[3]) / (self._i[4] - self._i[3])
        self._D6 = (self._v[6] - self._v[5]) / (self._i[6] - self._i[5])
        self._D8 = (self._vR - self._v[7]) / \
            (self.wfm_nrpoints - self._i[7])
        # region 0
        self._coeffs[0] = _np.array([self._D0, 0.0, 0.0])
        # region 1
        d = self._i[1] - self._i[0]
        dv = self._v[1] - self._v[0]
        self._coeffs[1] = WaveformParam._calccoeffs(d, dv, self._D0, self._D2)
        # region 2
        self._coeffs[2] = _np.array([self._D2, 0.0, 0.0])
        # region 3
        d = self._i[3] - self._i[2]
        dv = self._v[3] - self._v[2]
        self._coeffs[3] = WaveformParam._calccoeffs(d, dv, self._D2, self._D4)
        # region 4
        self._coeffs[4] = _np.array([self._D4, 0.0, 0.0])
        # region 5
        d = self._i[5] - self._i[4]
        dv = self._v[5] - self._v[4]
        self._coeffs[5] = WaveformParam._calccoeffs(d, dv, self._D4, self._D6)
        # region 6
        self._coeffs[6] = [self._D6, 0.0, 0.0]
        # region 7
        d = self._i[7] - self._i[6]
        dv = self._v[7] - self._v[6]
        self._coeffs[7] = WaveformParam._calccoeffs(d, dv, self._D6, self._D8)
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
        i = _np.array(tuple(range(self._i[7], self.wfm_nrpoints)))
        dv = calcdv(i, iref, coeffs)
        wfm.extend(vref + dv)
        return _np.array(wfm)

    def _find_i3(self, i1, i2, v1, v2):
        # first calculate polynomial fit coeffs (a,b,c) as function
        # of tentative i3
        D2 = (v2 - v1) / (i2 - i1)
        dv = self._v[3] - v2
        i3 = _np.arange(i2+1, self._i[4])
        D4 = (self._v[4] - self._v[3]) / (self._i[4] - i3)
        d = i3 - i2
        a, b, c = WaveformParam._calccoeffs(d, dv, D2, D4)
        # now, we find there the first derivative of waveform within region R3
        # is for each value of i3.
        phi = b**2 - 3*c*a
        i3_r1 = i2 + (-b + _np.sqrt(phi))/3.0/c
        i3_r2 = i2 + (-b - _np.sqrt(phi))/3.0/c
        cond = ((i3_r1 < i2) | (i3_r1 >= i3) | _np.isnan(i3_r1)) & \
               ((i3_r2 < i2) | (i3_r2 >= i3) | _np.isnan(i3_r2))
        # we accept a solution only if both roots of null first derivatives
        # equation fall outside region.
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
        a, b, c = WaveformParam._calccoeffs(d, dv, D0, D2)
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
        dv = self._v[7] - v6
        iR = self.wfm_nrpoints
        i7 = _np.arange(i6+1, iR)
        D8 = (self._vR - self._v[7]) / (iR - i7)
        d = i7 - i6
        a, b, c = WaveformParam._calccoeffs(d, dv, D6, D8)
        phi = b**2 - 3*c*a
        i7_r1 = i6 + (-b + _np.sqrt(phi))/3.0/c
        i7_r2 = i6 + (-b - _np.sqrt(phi))/3.0/c
        cond = ((i7_r1 < i6) | (i7_r1 >= i7) | _np.isnan(i7_r1)) & \
               ((i7_r2 < i6) | (i7_r2 >= i7) | _np.isnan(i7_r2))
        # for i in range(len(i7)):
        #     di = i7[i] - self._i[7]
        #     print(('{},  d:{}, i7_r1:{:.1f}, i7_r2:{:.1f}, '
        #            'i6:{}, i7:{}').format(cond[i], di, i7_r1[i], i7_r2[i],
        #                                   i6, i7[i]))
        i7_solutions = i7[cond]
        if i7_solutions.size:
            i7_delta = min(i7_solutions - self._i[7], key=abs)
            return self._i[7] + i7_delta
        else:
            return None

    def _find_i4(self, i5, i6, v5, v6):
        D6 = (v6 - v5) / (i6 - i5)
        dv = v5 - self._v[4]
        i4 = _np.arange(self._i[3]+1, self._i[5])
        D4 = (self._v[4] - self._v[3]) / (i4 - self._i[3])
        d = i5 - i4
        a, b, c = WaveformParam._calccoeffs(d, dv, D4, D6)
        phi = b**2 - 3*c*a
        i4_r1 = i4 + (-b + _np.sqrt(phi))/3.0/c
        i4_r2 = i4 + (-b - _np.sqrt(phi))/3.0/c
        cond = ((i4_r1 <= i4) | (i4_r1 >= i5) | _np.isnan(i4_r1)) & \
               ((i4_r2 <= i4) | (i4_r2 >= i5) | _np.isnan(i4_r2))
        i4_solutions = i4[cond]
        if i4_solutions.size:
            i4_delta = min(i4_solutions - self._i[4], key=abs)
            return self._i[4] + i4_delta
        else:
            return None


class _WaveformMagnet(_Magnet):
    """Base class of magnet waveforms."""

    def __init__(self, maname):
        _Magnet.__init__(self, maname=maname)

    @property
    def currents(self):
        return self._get_currents()

    @property
    def strengths(self):
        return self._get_strengths()

    @strengths.setter
    def strengths(self, value):
        self._set_strengths(value)


class WaveformDipole(_WaveformMagnet, WaveformParam):
    """Waveform for Dipole."""

    def __init__(self, maname='BO-Fam:MA-B', **kwargs):
        """Constructor."""
        _WaveformMagnet.__init__(self, maname)
        eje_current = self.conv_strength_2_current(_util.BO_EJECTION_ENERGY)
        kwargs['scale'] = eje_current
        WaveformParam.__init__(self, **kwargs)

    def _get_currents(self):
        currents = self.conv_strength_2_current(self.waveform)
        return currents

    def _get_strengths(self):
        return self.waveform


class Waveform(_WaveformMagnet):
    """Waveform class for general magnets."""

    def __init__(self, maname, dipole=None, family=None):
        """Constructor."""
        if maname != 'SI-Fam:MA-B1B2' and dipole is None:
            raise ValueError(
                '{} waveform needs an associated dipole!'.format(maname))
        _WaveformMagnet.__init__(self, maname)
        self._dipole = dipole
        self._family = family
        if self.maname in _util.NOMINAL_STRENGTHS:
            nom_strengths = _util.NOMINAL_STRENGTHS[self.maname]
        else:
            nom_strengths = 0.0
        strengths = [nom_strengths, ] * self._dipole.wfm_nrpoints
        self._currents = self._conv_strengths_2_currents(strengths)
        self._strengths = self._conv_currents_2_strengths(self._currents)

    def update(self):
        """Update object."""
        if self._dipole is not None:
            self._dipole.update()
        if self._family is not None:
            self._family.update()
        self._currents = self._conv_strengths_2_currents(self._strengths)

    def _get_currents(self):
        self.update()
        return self._currents

    def _get_strengths(self):
        self.update()
        return self._strengths

    def _set_strengths(self, value):
        if isinstance(value, (int, float)):
            self._strengths = [value, ] * len(self._strengths)
        elif len(value) != len(self._strengths):
            raise ValueError('Incorrect length of passed strengths!')
        else:
            self._strengths = value.copy()

    def _conv_currents_2_strengths(self, currents):
        kwargs = {'currents': currents}
        if self._dipole is not None:
            kwargs['strengths_dipole'] = self._dipole.strengths
        if self._family is not None:
            kwargs['strengths_family'] = self._family.strengths
        return self.conv_current_2_strength(**kwargs)

    def _conv_strengths_2_currents(self, strengths):
        kwargs = {'strengths': strengths}
        if self._dipole is not None:
            kwargs['strengths_dipole'] = self._dipole.strengths
        if self._family is not None:
            kwargs['strengths_family'] = self._family.strengths
        return self.conv_strength_2_current(**kwargs)
