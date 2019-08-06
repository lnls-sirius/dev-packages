"""Waveform classes."""

import numpy as _np

from mathphys import constants as _c
from mathphys import units as _u
from siriuspy.csdevice.pwrsupply import DEF_WFMSIZE as _DEF_WFMSIZE
from siriuspy.ramp import util as _rutil
from siriuspy.ramp.magnet import Magnet as _Magnet


class WaveformParam:
    """Dipole parameterized Waveforms."""

    N = _np.array([0, 1, 2, 3])

    def __init__(
            self,
            duration=_rutil.DEFAULT_PS_RAMP_DURATION,
            rampup1_start_time=_rutil.DEFAULT_PS_RAMP_RAMPUP1_START_TIME,
            rampup2_start_time=_rutil.DEFAULT_PS_RAMP_RAMPUP2_START_TIME,
            rampdown_start_time=_rutil.DEFAULT_PS_RAMP_RAMPDOWN_START_TIME,
            rampdown_stop_time=_rutil.DEFAULT_PS_RAMP_RAMPDOWN_STOP_TIME,
            rampup_range=_rutil.DEFAULT_PS_RAMP_RAMPUP_RANGE,
            rampdown_range=_rutil.DEFAULT_PS_RAMP_RAMPDOWN_RANGE,
            start_energy=_rutil.DEFAULT_PS_RAMP_START_ENERGY,
            rampup1_start_energy=_rutil.DEFAULT_PS_RAMP_RAMPUP1_START_ENERGY,
            rampup2_start_energy=_rutil.DEFAULT_PS_RAMP_RAMPUP2_START_ENERGY,
            rampdown_start_energy=_rutil.DEFAULT_PS_RAMP_RAMPDOWN_START_ENERGY,
            rampdown_stop_energy=_rutil.DEFAULT_PS_RAMP_RAMPDOWN_STOP_ENERGY,
            rampup_delta=_rutil.DEFAULT_PS_RAMP_RAMPUP_DELTA,
            rampdown_delta=_rutil.DEFAULT_PS_RAMP_RAMPDOWN_DELTA):
        """Init method."""
        self._duration = duration
        self._start_energy = start_energy
        self._rampup1_start_time = rampup1_start_time
        self._rampup1_start_energy = rampup1_start_energy
        self._rampup_range = rampup_range
        self._rampup_delta = rampup_delta
        self._rampup2_start_time = rampup2_start_time
        self._rampup2_start_energy = rampup2_start_energy
        self._rampdown_range = rampdown_range
        self._rampdown_delta = rampdown_delta
        self._rampdown_start_time = rampdown_start_time
        self._rampdown_start_energy = rampdown_start_energy
        self._rampdown_stop_time = rampdown_stop_time
        self._rampdown_stop_energy = rampdown_stop_energy
        self._update()

    @property
    def duration(self):
        """Return duration."""
        return self._duration

    @property
    def start_energy(self):
        """Return start_energy."""
        return self._start_energy

    @property
    def rampup1_start_time(self):
        """Return rampup1_start_time."""
        return self._rampup1_start_time

    @property
    def rampup1_start_energy(self):
        """Return rampup1_start_energy."""
        return self._rampup1_start_energy

    @property
    def rampup2_start_time(self):
        """Return rampup2_start_time."""
        return self._rampup2_start_time

    @property
    def rampup2_start_energy(self):
        """Return rampup2_start_energy."""
        return self._rampup2_start_energy

    @property
    def rampdown_start_time(self):
        """Return rampdown_start_time."""
        return self._rampdown_start_time

    @property
    def rampdown_start_energy(self):
        """Return rampdown_start_energy."""
        return self._rampdown_start_energy

    @property
    def rampdown_stop_time(self):
        """Return rampdown_stop_time."""
        return self._rampdown_stop_time

    @property
    def rampdown_stop_energy(self):
        """Return rampdown_stop_energy."""
        return self._rampdown_stop_energy

    @property
    def rampup_range(self):
        """Return rampup_range."""
        return self._rampup_range

    @property
    def rampup_delta(self):
        """Return rampup_delta."""
        return self._rampup_delta

    @property
    def rampdown_range(self):
        """Return rampdown_range."""
        return self._rampdown_range

    @property
    def rampdown_delta(self):
        """Return rampdown_delta."""
        return self._rampdown_delta

    @duration.setter
    def duration(self, value):
        """Set duration."""
        self._duration = value
        self._update()

    @start_energy.setter
    def start_energy(self, value):
        """Set start_energy."""
        self._start_energy = value
        self._update()

    @rampup1_start_time.setter
    def rampup1_start_time(self, value):
        """Set rampup1_start_time."""
        self._rampup1_start_time = value
        self._update()

    @rampup1_start_energy.setter
    def rampup1_start_energy(self, value):
        """Set rampup1_start_energy."""
        self._rampup1_start_energy = value
        self._update()

    @rampup2_start_time.setter
    def rampup2_start_time(self, value):
        """Set rampup2_start_time."""
        self._rampup2_start_time = value
        self._update()

    @rampup2_start_energy.setter
    def rampup2_start_energy(self, value):
        """Set rampup2_start_energy."""
        self._rampup2_start_energy = value

    @rampdown_start_time.setter
    def rampdown_start_time(self, value):
        """Set rampdown_start_time."""
        self._rampdown_start_time = value
        self._update()

    @rampdown_start_energy.setter
    def rampdown_start_energy(self, value):
        """Set rampdown_start_energy."""
        self._rampdown_start_energy = value
        self._update()

    @rampdown_stop_time.setter
    def rampdown_stop_time(self, value):
        """Set rampdown_stop_time."""
        self._rampdown_stop_time = value
        self._update()

    @rampdown_stop_energy.setter
    def rampdown_stop_energy(self, value):
        """Set rampdown_stop_energy."""
        self._rampdown_stop_energy = value
        self._update()

    @rampup_range.setter
    def rampup_range(self, value):
        """Set rampup_range."""
        self._rampup_range = value
        self._update()

    @rampup_delta.setter
    def rampup_delta(self, value):
        """Set rampup_delta."""
        self._rampup_delta = value
        self._update()

    @rampdown_range.setter
    def rampdown_range(self, value):
        """Set rampdown_range."""
        self._rampdown_range = value
        self._update()

    @rampdown_delta.setter
    def rampdown_delta(self, value):
        """Set rampdown_delta."""
        self._rampdown_delta = value
        self._update()

    @property
    def rampup1_slope(self):
        """Return rampup1 slope."""
        return self._c[1][1]

    @property
    def rampup2_slope(self):
        """Return rampup2 slope."""
        return self._c[2][1]

    @property
    def rampdown_slope(self):
        """Return rampdown slope."""
        return self._c[3][1]



    def eval_at(self, time):
        """."""
        time = _np.array(time)
        value = _np.zeros(time.shape)
        stop0 = self._rampup1_start_time
        stop12 = 0.5 * (self._rampup2_start_time + self._rampdown_start_time)
        stop23 = self._rampdown_stop_time
        # region 0
        sel = (time <= stop0)
        if _np.any(sel):
            value[sel] = self._func_polynom(0, time[sel])
        # region 12
        sel = (time > stop0) & (time <= stop12)
        if _np.any(sel):
            value[sel] = self._func_region_12(time[sel])
        # region 23
        sel = (time > stop12) & (time <= stop23)
        if _np.any(sel):
            value[sel] = self._func_region_23(time[sel])
        # region 4
        sel = (time > stop23)
        if _np.any(sel):
            value[sel] = self._func_polynom(4, time[sel])
        return value

    def _update(self):

        self._t = []  # start and stop times
        self._v = []  # start amd stop values
        self._c = []  # polynomial coefficients

        # region 0 - cubic
        self._t.append(_np.array([0.0, self._rampup1_start_time]))
        self._v.append(_np.array([self._start_energy, self._rampup1_start_energy]))
        self._c.append([0.0, 0.0, 0.0, 0.0])
        # region 1 - linear rampup1
        time = _np.array([self._rampup1_start_time, self._rampup2_start_time])
        value = _np.array([self._rampup1_start_energy,
                           self._rampup2_start_energy])
        self._t.append(time)
        self._v.append(value)
        coeff_a = value[0]
        coeff_b = (value[1] - value[0])/(time[1] - time[0])
        self._c.append([coeff_a, coeff_b, 0.0, 0.0])
        # region 2 - linear rampup2
        time = _np.array([self._rampup2_start_time, self._rampdown_start_time])
        value = _np.array([self._rampup2_start_energy,
                           self._rampdown_start_energy])
        self._t.append(time)
        self._v.append(value)
        coeff_a = value[0]
        coeff_b = (value[1] - value[0])/(time[1] - time[0])
        self._c.append([coeff_a, coeff_b, 0.0, 0.0])
        # region 3 - linear rampdown
        time = _np.array([self._rampdown_start_time,
                          self._rampdown_stop_time])
        value = _np.array([self._rampdown_start_energy,
                           self._rampdown_stop_energy])
        self._t.append(time)
        self._v.append(value)
        coeff_a = value[0]
        coeff_b = (value[1] - value[0])/(time[1] - time[0])
        self._c.append([coeff_a, coeff_b, 0.0, 0.0])
        # region 4 - cubic
        self._t.append(_np.array([self._rampdown_stop_time, self._duration]))
        self._v.append(_np.array([self._rampdown_stop_energy, self._start_energy]))
        self._c.append([0.0, 0.0, 0.0, 0.0])

        # set coeffs for region 0
        idx = 0
        dt = self._t[idx][1] - self._t[idx][0]
        dv = self._v[idx][1] - self._v[idx][0]
        coeff_b_region1 = self._c[1][1]
        coeff_a = self._v[idx][0]
        coeff_b = 0.0
        coeff_c = (3*dv - coeff_b_region1*dt)/dt**2
        coeff_d = -(2*dv - coeff_b_region1*dt)/dt**3
        self._c[idx] = [coeff_a, coeff_b, coeff_c, coeff_d]

        # set coeffs for region 4
        idx = 4
        dt = self._t[idx][1] - self._t[idx][0]
        dv = self._v[idx][1] - self._v[idx][0]
        coeff_b_region3 = self._c[3][1]
        coeff_a = self._v[idx][0]
        coeff_b = coeff_b_region3
        coeff_c = (+3*(dv - coeff_b_region3*dt) + coeff_b_region3*dt)/dt**2
        coeff_d = (-2*(dv - coeff_b_region3*dt) - coeff_b_region3*dt)/dt**3
        self._c[idx] = [coeff_a, coeff_b, coeff_c, coeff_d]

        # define regions
        ts = self._rampup2_start_time
        # t1 = ts - (ts - self._rampup1_start_time)/4
        # t2 = ts + (self._rampdown_start_time - ts)/4
        t1 = ts - self._rampup_range/2
        t2 = ts + self._rampup_range/2
        self._region12_t = [t1, ts, t2]
        ts = self._rampdown_start_time
        # t1 = ts - (ts - self._rampup2_start_time)/4
        # t2 = ts + (self._rampdown_stop_time - ts)/4
        t1 = ts - self._rampdown_range/2
        t2 = ts + self._rampdown_range/2
        self._region23_t = [t1, ts, t2]

    def _func_region_12(self, time, delta=None):
        """Evaluate function in regions 1 and 2."""
        if delta is None:
            delta = self._rampup_delta
        return self._func_region(time, delta, self._region12_t, 1, 2)

    def _func_region_23(self, time, delta=None):
        """Evaluate function in regions 2 and 3."""
        if delta is None:
            delta = self._rampdown_delta
        return self._func_region(time, delta, self._region23_t, 2, 3)

    def _func_region(self, time, delta, region_t, region_idx1, region_idx2):
        """Evaluate function in regions (1 and 2) or (2 and 3)."""
        v = _np.zeros(time.shape)
        t1, ts, t2 = region_t
        sel = (time <= t1)
        v[sel] = self._func_polynom(region_idx1, time[sel])
        sel = (time >= t2)
        v[sel] = self._func_polynom(region_idx2, time[sel])
        sel = (t1 < time) & (time < t2)
        if _np.any(sel):
            poly1 = self._func_polynom(region_idx1, time[sel])
            poly2 = self._func_polynom(region_idx2, time[sel])
            vm = (poly1 + poly2) / 2
            vd = poly1 - poly2
            T1, T2 = ts - t1, t2 - ts
            T = T1 + (T2 - T1)*(time[sel] - t1)/(t2 - t1)
            f3 = (time[sel] - ts)/T
            f4 = (1 + _np.cos(_np.pi*f3)) / 2
            vp = vm + 0.5 * _np.sqrt(vd**2 + (2*delta)**2*(f4**2)**0.5)
            vn = vm - 0.5 * _np.sqrt(vd**2 + (2*delta)**2*(f4**2)**0.5)
            b1 = self._c[region_idx1][1]
            b2 = self._c[region_idx2][1]
            vt = vp if b2 >= b1 else vn
            v[sel] = vt
        return v

    def _func_polynom(self, region_idx, time):
        """Return evaluation of polynomial in region of interest."""
        time = _np.tile(_np.reshape(time, (-1, 1)), len(WaveformParam.N))
        time0 = self._t[region_idx][0]
        dtime = time - time0
        dtpowern = dtime ** WaveformParam.N
        coeffs = self._c[region_idx]
        value = _np.dot(dtpowern, coeffs)
        return value


class _WaveformMagnet:
    """Base class of magnet waveforms."""

    _magnets = dict()  # dict with magnets objects to improve efficiency

    def __init__(self, maname, wfm_nrpoints=_DEF_WFMSIZE, **kwargs):
        if maname not in _WaveformMagnet._magnets:
            _WaveformMagnet._magnets[maname] = _Magnet(maname)
        self._maname = maname
        self._wfm_nrpoints = wfm_nrpoints

    @property
    def times(self):
        return _np.linspace(0, self.duration, self.wfm_nrpoints)

    @property
    def currents(self):
        return self._get_currents()

    @property
    def strengths(self):
        return self._get_strengths()

    @strengths.setter
    def strengths(self, value):
        self._set_strengths(value)

    @property
    def wfm_nrpoints(self):
        return self._wfm_nrpoints

    def __getitem__(self, index):
        """Return waveform at index."""
        wfm = self.waveform
        return wfm[index]

    def __iter__(self):
        """Return iterator for waveform."""
        wfm = self.waveform
        for i in range(len(wfm)):
            yield(wfm[i])

    def __reversed__(self):
        """Return reverse iterator for waveform."""
        wfm = self.waveform
        for i in range(len(wfm)-1, -1, -1):
            yield(wfm[i])

    def __len__(self):
        """Return length of waveform."""
        return self.wfm_nrpoints

    def __contains__(self, value):
        """Check whether value is in waveform."""
        return value in self.waveform

    def __eq__(self, value):
        """Compare waveforms."""
        return self.waveform == value

    def conv_current_2_strength(self, currents, **kwargs):
        return _WaveformMagnet._magnets[self._maname].conv_current_2_strength(
            currents, **kwargs)

    def conv_strength_2_current(self, strengths, **kwargs):
        return _WaveformMagnet._magnets[self._maname].conv_strength_2_current(
            strengths, **kwargs)


class WaveformDipole(_WaveformMagnet, WaveformParam):
    """Waveform for Dipole."""

    def __init__(self, maname='BO-Fam:MA-B', **kwargs):
        """Constructor."""
        _WaveformMagnet.__init__(self, maname, **kwargs)
        WaveformParam.__init__(self, **kwargs)
        self._waveform = None
        self._update_waveform()

    def update(self):
        """Update."""
        if self.changed:
            self._waveform = None
        WaveformParam.update(self)

    @property
    def waveform(self):
        """Magnet waveform."""
        self._update_waveform()
        return self._waveform

    def _update_waveform(self):
        if self._changed or self._waveform is None:
            t = self.times
            self._waveform = self.eval_at(t)

    def _get_currents(self):
        currents = self.conv_strength_2_current(self.waveform)
        return currents

    def _get_strengths(self):
        return self.waveform


class Waveform(_WaveformMagnet):
    """Waveform class for general magnets."""

    def __init__(self, maname, dipole=None, family=None, strengths=None):
        """Constructor."""
        if maname != 'SI-Fam:MA-B1B2' and dipole is None:
            raise ValueError(
                '{} waveform needs an associated dipole!'.format(maname))
        _WaveformMagnet.__init__(self, maname)
        self._dipole = dipole
        self._family = family
        if strengths is None:
            if maname in _rutil.NOMINAL_STRENGTHS:
                nom_strengths = _rutil.NOMINAL_STRENGTHS[maname]
            else:
                nom_strengths = 0.0
            strengths = [nom_strengths, ] * self._dipole.wfm_nrpoints
        self._currents = self._conv_strengths_2_currents(strengths)
        self._strengths = self._conv_currents_2_strengths(self._currents)

    @property
    def wfm_nrpoints(self):
        """Waveform nrpoints."""
        return self._dipole.wfm_nrpoints

    @property
    def duration(self):
        """Ramp duration."""
        return self._dipole.duration

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

    # --- list methods (strengths) ---

    def __getitem__(self, index):
        """Return waveform at index."""
        self.update()
        if isinstance(index, slice):
            wp = self._strengths[index]
            return _np.array([wp[i] for i in range(len(wp))])
        elif isinstance(index, int):
            return self._strengths[index]
        else:
            raise IndexError

    def __iter__(self):
        """Return iterator for waveform."""
        self.update()
        for i in range(len(self._strengths)):
            yield(self._strengths[i])

    def __reversed__(self):
        """Return reverse iterator for waveform."""
        self.update()
        for i in range(len(self._strengths)-1, -1, -1):
            yield(self._strengths[i])

    def __len__(self):
        """Return length of waveform."""
        return len(self._strengths)

    def __contains__(self, value):
        """Check whether value is in waveform."""
        return value in self._strengths

    def __eq__(self, value):
        """Compare waveforms."""
        return self._strengths == value
