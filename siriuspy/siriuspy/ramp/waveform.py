"""Waveform classes."""

import numpy as _np

from mathphys import constants as _c
from mathphys import units as _mu

from ..pwrsupply.csdev import DEF_WFMSIZE_OTHERS as \
    _DEF_WFMSIZE_OTHERS
from ..search import MASearch as _MASearch

from . import util as _ru
from .magnet import get_magnet as _get_magnet


class WaveformParam:
    """Dipole parameterized Waveforms."""

    N = _np.array([0, 1, 2, 3])

    def __init__(
            self,
            duration=_ru.DEFAULT_PS_RAMP_DURATION,
            rampup1_start_time=_ru.DEFAULT_PS_RAMP_RAMPUP1_START_TIME,
            rampup2_start_time=_ru.DEFAULT_PS_RAMP_RAMPUP2_START_TIME,
            rampdown_start_time=_ru.DEFAULT_PS_RAMP_RAMPDOWN_START_TIME,
            rampdown_stop_time=_ru.DEFAULT_PS_RAMP_RAMPDOWN_STOP_TIME,
            rampup_smooth_intvl=_ru.DEFAULT_PS_RAMP_RAMPUP_SMOOTH_INTVL,
            rampdown_smooth_intvl=_ru.DEFAULT_PS_RAMP_RAMPDOWN_SMOOTH_INTVL,
            start_value=_ru.DEFAULT_PS_RAMP_START_CURRENT,
            rampup1_start_value=_ru.DEFAULT_PS_RAMP_RAMPUP1_START_CURRENT,
            rampup2_start_value=_ru.DEFAULT_PS_RAMP_RAMPUP2_START_CURRENT,
            rampdown_start_value=_ru.DEFAULT_PS_RAMP_RAMPDOWN_START_CURRENT,
            rampdown_stop_value=_ru.DEFAULT_PS_RAMP_RAMPDOWN_STOP_CURRENT,
            rampup_smooth_value=_ru.DEFAULT_PS_RAMP_RAMPUP_SMOOTH_CURRENT,
            rampdown_smooth_value=_ru.DEFAULT_PS_RAMP_RAMPDOWN_SMOOTH_CURRENT
                ):
        """Init method."""
        self._duration = duration
        self._start_value = start_value
        self._rampup1_start_time = rampup1_start_time
        self._rampup1_start_value = rampup1_start_value
        self._rampup_smooth_intvl = rampup_smooth_intvl
        self._rampup_smooth_value = rampup_smooth_value
        self._rampup2_start_time = rampup2_start_time
        self._rampup2_start_value = rampup2_start_value
        self._rampdown_smooth_intvl = rampdown_smooth_intvl
        self._rampdown_smooth_value = rampdown_smooth_value
        self._rampdown_start_time = rampdown_start_time
        self._rampdown_start_value = rampdown_start_value
        self._rampdown_stop_time = rampdown_stop_time
        self._rampdown_stop_value = rampdown_stop_value
        self._update()

    @property
    def duration(self):
        """Return duration."""
        return self._duration

    @property
    def start_value(self):
        """Return start_value."""
        return self._start_value

    @property
    def rampup1_start_time(self):
        """Return rampup1_start_time."""
        return self._rampup1_start_time

    @property
    def rampup1_start_value(self):
        """Return rampup1_start_value."""
        return self._rampup1_start_value

    @property
    def rampup2_start_time(self):
        """Return rampup2_start_time."""
        return self._rampup2_start_time

    @property
    def rampup2_start_value(self):
        """Return rampup2_start_value."""
        return self._rampup2_start_value

    @property
    def rampdown_start_time(self):
        """Return rampdown_start_time."""
        return self._rampdown_start_time

    @property
    def rampdown_start_value(self):
        """Return rampdown_start_value."""
        return self._rampdown_start_value

    @property
    def rampdown_stop_time(self):
        """Return rampdown_stop_time."""
        return self._rampdown_stop_time

    @property
    def rampdown_stop_value(self):
        """Return rampdown_stop_value."""
        return self._rampdown_stop_value

    @property
    def rampup_smooth_intvl(self):
        """Return rampup_smooth_intvl."""
        return self._rampup_smooth_intvl

    @property
    def rampup_smooth_value(self):
        """Return rampup_smooth_value."""
        return self._rampup_smooth_value

    @property
    def rampdown_smooth_intvl(self):
        """Return rampdown_smooth_intvl."""
        return self._rampdown_smooth_intvl

    @property
    def rampdown_smooth_value(self):
        """Return rampdown_smooth_value."""
        return self._rampdown_smooth_value

    @duration.setter
    def duration(self, value):
        """Set duration."""
        self._duration = value
        self._update()

    @start_value.setter
    def start_value(self, value):
        """Set start_value."""
        self._start_value = float(value)
        self._update()

    @rampup1_start_time.setter
    def rampup1_start_time(self, value):
        """Set rampup1_start_time."""
        self._rampup1_start_time = value
        self._update()

    @rampup1_start_value.setter
    def rampup1_start_value(self, value):
        """Set rampup1_start_value."""
        self._rampup1_start_value = float(value)
        self._update()

    @rampup2_start_time.setter
    def rampup2_start_time(self, value):
        """Set rampup2_start_time."""
        self._rampup2_start_time = value
        self._update()

    @rampup2_start_value.setter
    def rampup2_start_value(self, value):
        """Set rampup2_start_value."""
        self._rampup2_start_value = float(value)
        self._update()

    @rampdown_start_time.setter
    def rampdown_start_time(self, value):
        """Set rampdown_start_time."""
        self._rampdown_start_time = value
        self._update()

    @rampdown_start_value.setter
    def rampdown_start_value(self, value):
        """Set rampdown_start_value."""
        self._rampdown_start_value = float(value)
        self._update()

    @rampdown_stop_time.setter
    def rampdown_stop_time(self, value):
        """Set rampdown_stop_time."""
        self._rampdown_stop_time = value
        self._update()

    @rampdown_stop_value.setter
    def rampdown_stop_value(self, value):
        """Set rampdown_stop_value."""
        self._rampdown_stop_value = float(value)
        self._update()

    @rampup_smooth_intvl.setter
    def rampup_smooth_intvl(self, value):
        """Set rampup_smooth_intvl."""
        self._rampup_smooth_intvl = value
        self._update()

    @rampup_smooth_value.setter
    def rampup_smooth_value(self, value):
        """Set rampup_smooth_value."""
        self._rampup_smooth_value = value
        self._update()

    @rampdown_smooth_intvl.setter
    def rampdown_smooth_intvl(self, value):
        """Set rampdown_smooth_intvl."""
        self._rampdown_smooth_intvl = value
        self._update()

    @rampdown_smooth_value.setter
    def rampdown_smooth_value(self, value):
        """Set rampdown_smooth_value."""
        self._rampdown_smooth_value = value
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
        self._v.append(_np.array([self._start_value,
                                  self._rampup1_start_value]))
        self._c.append([0.0, 0.0, 0.0, 0.0])
        # region 1 - linear rampup1
        time = _np.array([self._rampup1_start_time, self._rampup2_start_time])
        value = _np.array([self._rampup1_start_value,
                           self._rampup2_start_value])
        self._t.append(time)
        self._v.append(value)
        coeff_a = value[0]
        coeff_b = (value[1] - value[0])/(time[1] - time[0])
        self._c.append([coeff_a, coeff_b, 0.0, 0.0])
        # region 2 - linear rampup2
        time = _np.array([self._rampup2_start_time, self._rampdown_start_time])
        value = _np.array([self._rampup2_start_value,
                           self._rampdown_start_value])
        self._t.append(time)
        self._v.append(value)
        coeff_a = value[0]
        coeff_b = (value[1] - value[0])/(time[1] - time[0])
        self._c.append([coeff_a, coeff_b, 0.0, 0.0])
        # region 3 - linear rampdown
        time = _np.array([self._rampdown_start_time,
                          self._rampdown_stop_time])
        value = _np.array([self._rampdown_start_value,
                           self._rampdown_stop_value])
        self._t.append(time)
        self._v.append(value)
        coeff_a = value[0]
        coeff_b = (value[1] - value[0])/(time[1] - time[0])
        self._c.append([coeff_a, coeff_b, 0.0, 0.0])
        # region 4 - cubic
        self._t.append(_np.array([self._rampdown_stop_time,
                                  self._duration]))
        self._v.append(_np.array([self._rampdown_stop_value,
                                  self._start_value]))
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
        stime = self._rampup2_start_time
        # time1 = stime - (stime - self._rampup1_start_time)/4
        # time2 = stime + (self._rampdown_start_time - stime)/4
        time1 = stime - self._rampup_smooth_intvl/2
        time2 = stime + self._rampup_smooth_intvl/2
        self._region12_t = [time1, stime, time2]
        stime = self._rampdown_start_time
        # time1 = stime - (stime - self._rampup2_start_time)/4
        # time2 = stime + (self._rampdown_stop_time - stime)/4
        time1 = stime - self._rampdown_smooth_intvl/2
        time2 = stime + self._rampdown_smooth_intvl/2
        self._region23_t = [time1, stime, time2]

    def _func_region_12(self, time, delta=None):
        """Evaluate function in regions 1 and 2."""
        if delta is None:
            delta = self._rampup_smooth_value
        return self._func_region(time, delta, self._region12_t, 1, 2)

    def _func_region_23(self, time, delta=None):
        """Evaluate function in regions 2 and 3."""
        if delta is None:
            delta = self._rampdown_smooth_value
        return self._func_region(time, delta, self._region23_t, 2, 3)

    def _func_region(self, time, delta, region_t, region_idx1, region_idx2):
        """Evaluate function in regions (1 and 2) or (2 and 3)."""
        v = _np.zeros(time.shape)
        time1, stime, time2 = region_t
        sel = (time <= time1)
        v[sel] = self._func_polynom(region_idx1, time[sel])
        sel = (time >= time2)
        v[sel] = self._func_polynom(region_idx2, time[sel])
        sel = (time1 < time) & (time < time2)
        if _np.any(sel):
            poly1 = self._func_polynom(region_idx1, time[sel])
            poly2 = self._func_polynom(region_idx2, time[sel])
            vm = (poly1 + poly2) / 2
            vd = poly1 - poly2
            dt1, dt2 = stime - time1, time2 - stime
            T = dt1 + (dt2 - dt1)*(time[sel] - time1)/(time2 - time1)
            f3 = (time[sel] - stime)/T
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

    def __init__(self, psname, wfm_nrpoints=_DEF_WFMSIZE_OTHERS):
        maname = _MASearch.conv_psname_2_psmaname(psname)
        self._magnet = _get_magnet(maname)
        self._psname = psname
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
        return self._magnet.conv_current_2_strength(currents, **kwargs)

    def conv_strength_2_current(self, strengths, **kwargs):
        return self._magnet.conv_strength_2_current(strengths, **kwargs)

    def get_current_from_time(self, time):
        return _np.interp(time, self.times, self.currents)

    def get_strength_from_time(self, time):
        return _np.interp(time, self.times, self.strengths)


class WaveformDipole(_WaveformMagnet, WaveformParam):
    """Waveform for Dipole."""

    _E0 = _c.electron_rest_energy * _mu.joule_2_GeV

    def __init__(
            self, psname='BO-Fam:PS-B-1', wfm_nrpoints=_DEF_WFMSIZE_OTHERS,
            duration=_ru.DEFAULT_PS_RAMP_DURATION,
            start_energy=_ru.DEFAULT_PS_RAMP_START_ENERGY,
            rampup1_start_time=_ru.DEFAULT_PS_RAMP_RAMPUP1_START_TIME,
            rampup1_start_energy=_ru.DEFAULT_PS_RAMP_RAMPUP1_START_ENERGY,
            rampup2_start_time=_ru.DEFAULT_PS_RAMP_RAMPUP2_START_TIME,
            rampup2_start_energy=_ru.DEFAULT_PS_RAMP_RAMPUP2_START_ENERGY,
            rampup_smooth_intvl=_ru.DEFAULT_PS_RAMP_RAMPUP_SMOOTH_INTVL,
            rampup_smooth_energy=_ru.DEFAULT_PS_RAMP_RAMPUP_SMOOTH_ENERGY,
            rampdown_start_time=_ru.DEFAULT_PS_RAMP_RAMPDOWN_START_TIME,
            rampdown_start_energy=_ru.DEFAULT_PS_RAMP_RAMPDOWN_START_ENERGY,
            rampdown_stop_time=_ru.DEFAULT_PS_RAMP_RAMPDOWN_STOP_TIME,
            rampdown_stop_energy=_ru.DEFAULT_PS_RAMP_RAMPDOWN_STOP_ENERGY,
            rampdown_smooth_intvl=_ru.DEFAULT_PS_RAMP_RAMPDOWN_SMOOTH_INTVL,
            rampdown_smooth_energy=_ru.DEFAULT_PS_RAMP_RAMPDOWN_SMOOTH_ENERGY
            ):
        """Constructor."""
        _WaveformMagnet.__init__(self, psname, wfm_nrpoints)

        self._start_energy = start_energy
        self._rampup1_start_energy = rampup1_start_energy
        self._rampup2_start_energy = rampup2_start_energy
        self._rampdown_start_energy = rampdown_start_energy
        self._rampdown_stop_energy = rampdown_stop_energy
        self._rampup_smooth_energy = rampup_smooth_energy
        self._rampdown_smooth_energy = rampdown_smooth_energy

        _conv_func = self.conv_strength_2_current
        start_value = _conv_func(start_energy)
        rampup1_start_value = _conv_func(rampup1_start_energy)
        rampup2_start_value = _conv_func(rampup2_start_energy)
        rampdown_start_value = _conv_func(rampdown_start_energy)
        rampdown_stop_value = _conv_func(rampdown_stop_energy)
        rampup_smooth_value = _conv_func(rampup_smooth_energy)
        rampdown_smooth_value = _conv_func(rampdown_smooth_energy)
        WaveformParam.__init__(
            self,
            duration=duration,
            rampup1_start_time=rampup1_start_time,
            rampup2_start_time=rampup2_start_time,
            rampdown_start_time=rampdown_start_time,
            rampdown_stop_time=rampdown_stop_time,
            rampup_smooth_intvl=rampup_smooth_intvl,
            rampdown_smooth_intvl=rampdown_smooth_intvl,
            start_value=start_value,
            rampup1_start_value=rampup1_start_value,
            rampup2_start_value=rampup2_start_value,
            rampdown_start_value=rampdown_start_value,
            rampdown_stop_value=rampdown_stop_value,
            rampup_smooth_value=rampup_smooth_value,
            rampdown_smooth_value=rampdown_smooth_value)
        self._currents = self.eval_at(self.times)
        self._strengths = self.conv_current_2_strength(self._currents)

    @property
    def waveform(self):
        """Magnet waveform."""
        return self.strengths

    @property
    def start_energy(self):
        """Return start_energy."""
        return self._start_energy

    @property
    def rampup1_start_energy(self):
        """Return rampup1_start_energy."""
        return self._rampup1_start_energy

    @property
    def rampup2_start_energy(self):
        """Return rampup2_start_energy."""
        return self._rampup2_start_energy

    @property
    def rampdown_start_energy(self):
        """Return rampdown_start_energy."""
        return self._rampdown_start_energy

    @property
    def rampdown_stop_energy(self):
        """Return rampdown_stop_energy."""
        return self._rampdown_stop_energy

    @property
    def rampup_smooth_energy(self):
        """Return rampup_smooth_energy."""
        return self._rampup_smooth_energy

    @property
    def rampdown_smooth_energy(self):
        """Return rampdown_smooth_energy."""
        return self._rampdown_smooth_energy

    @start_energy.setter
    def start_energy(self, value):
        """Set start_energy."""
        value = float(value) if value > self._E0 else self._E0
        self._start_energy = float(value)
        current_value = self.conv_strength_2_current(value)
        WaveformParam.start_value.fset(self, current_value)

    @rampup1_start_energy.setter
    def rampup1_start_energy(self, value):
        """Set rampup1_start_energy."""
        value = float(value) if value > self._E0 else self._E0
        self._rampup1_start_energy = value
        current_value = self.conv_strength_2_current(value)
        WaveformParam.rampup1_start_value.fset(self, current_value)

    @rampup2_start_energy.setter
    def rampup2_start_energy(self, value):
        """Set rampup2_start_energy."""
        value = float(value) if value > self._E0 else self._E0
        self._rampup2_start_energy = value
        current_value = self.conv_strength_2_current(value)
        WaveformParam.rampup2_start_value.fset(self, current_value)

    @rampdown_start_energy.setter
    def rampdown_start_energy(self, value):
        """Set rampdown_start_energy."""
        value = float(value) if value > self._E0 else self._E0
        self._rampdown_start_energy = value
        current_value = self.conv_strength_2_current(value)
        WaveformParam.rampdown_start_value.fset(self, current_value)

    @rampdown_stop_energy.setter
    def rampdown_stop_energy(self, value):
        """Set rampdown_stop_energy."""
        value = float(value) if value > self._E0 else self._E0
        self._rampdown_stop_energy = value
        current_value = self.conv_strength_2_current(value)
        WaveformParam.rampdown_stop_value.fset(self, current_value)

    @rampup_smooth_energy.setter
    def rampup_smooth_energy(self, value):
        """Set rampup_smooth_energy."""
        self._rampup_smooth_energy = value
        current_value = self.conv_strength_2_current(value)
        WaveformParam.rampup_smooth_value.fset(self, current_value)

    @rampdown_smooth_energy.setter
    def rampdown_smooth_energy(self, value):
        """Set rampdown_smooth_energy."""
        self._rampdown_smooth_energy = value
        current_value = self.conv_strength_2_current(value)
        WaveformParam.rampdown_smooth_value.fset(self, current_value)

    @WaveformParam.start_value.setter
    def start_value(self, value):
        """Set start_value."""
        WaveformParam.start_value.fset(self, value)
        new_energy = self.conv_current_2_strength(float(value))
        if new_energy < self._E0:
            new_energy = self._E0
        self._start_energy = new_energy

    @WaveformParam.rampup1_start_value.setter
    def rampup1_start_value(self, value):
        """Set rampup1_start_value."""
        WaveformParam.rampup1_start_value.fset(self, value)
        new_energy = self.conv_current_2_strength(float(value))
        if new_energy < self._E0:
            new_energy = self._E0
        self._rampup1_start_energy = new_energy

    @WaveformParam.rampup2_start_value.setter
    def rampup2_start_value(self, value):
        """Set rampup2_start_value."""
        WaveformParam.rampup2_start_value.fset(self, value)
        new_energy = self.conv_current_2_strength(float(value))
        if new_energy < self._E0:
            new_energy = self._E0
        self._rampup2_start_energy = new_energy

    @WaveformParam.rampdown_start_value.setter
    def rampdown_start_value(self, value):
        """Set rampdown_start_value."""
        WaveformParam.rampdown_start_value.fset(self, value)
        new_energy = self.conv_current_2_strength(float(value))
        if new_energy < self._E0:
            new_energy = self._E0
        self._rampdown_start_energy = new_energy

    @WaveformParam.rampdown_stop_value.setter
    def rampdown_stop_value(self, value):
        """Set rampdown_stop_value."""
        WaveformParam.rampdown_stop_value.fset(self, value)
        new_energy = self.conv_current_2_strength(float(value))
        if new_energy < self._E0:
            new_energy = self._E0
        self._rampdown_stop_energy = new_energy

    @WaveformParam.rampup_smooth_value.setter
    def rampup_smooth_value(self, value):
        """Set rampup_smooth_value."""
        WaveformParam.rampup_smooth_value.fset(self, value)
        self._rampup_smooth_energy = self.conv_current_2_strength(value)

    @WaveformParam.rampdown_smooth_value.setter
    def rampdown_smooth_value(self, value):
        """Set rampdown_smooth_value."""
        WaveformParam.rampdown_smooth_value.fset(self, value)
        self._rampdown_smooth_energy = self.conv_current_2_strength(value)

    def _get_currents(self):
        self._currents = self.eval_at(self.times)
        return self._currents

    def _get_strengths(self):
        self._strengths = self.conv_current_2_strength(self.currents)
        return self._strengths

    def __str__(self):
        ppties = (
            'duration [ms]',
            'rampup1_start_time [ms]',
            'rampup2_start_time [ms]',
            'rampdown_start_time [ms]',
            'rampdown_stop_time [ms]',
            'rampup_smooth_intvl [ms]',
            'rampdown_smooth_intvl [ms]',
            'start_energy [GeV]',
            'rampup1_start_energy [GeV]',
            'rampup2_start_energy [GeV]',
            'rampdown_start_energy [GeV]',
            'rampdown_stop_energy [GeV]',
            'rampup_smooth_energy [GeV]',
            'rampdown_smooth_energy [GeV]',
            'start_value [A]',
            'rampup1_start_value [A]',
            'rampup2_start_value [A]',
            'rampdown_start_value [A]',
            'rampdown_stop_value [A]',
            'rampup_smooth_value [A]',
            'rampdown_smooth_value [A]',
        )
        maxlen = max(tuple(len(p) for p in ppties) + (len('name'),))
        strfmt = '{:<' + str(maxlen) + 's}: {}\n'
        text = ''
        for ppty in ppties:
            text += strfmt.format(ppty, getattr(self, ppty.split(' ')[0]))
        return text


class Waveform(_WaveformMagnet):
    """Waveform class for general magnets."""

    def __init__(self, psname, dipole=None, family=None, strengths=None,
                 currents=None, wfm_nrpoints=_DEF_WFMSIZE_OTHERS):
        """Constructor."""
        if dipole is None:
            raise ValueError('{} waveform needs an associated '
                             'dipole waveform!'.format(psname))
        _WaveformMagnet.__init__(self, psname, wfm_nrpoints=wfm_nrpoints)
        self._dipole = dipole
        self._family = family
        if currents is not None:
            strengths = self._conv_currents_2_strengths(currents)
        if strengths is None:
            if psname in _ru.NOMINAL_STRENGTHS:
                nom_strengths = _ru.NOMINAL_STRENGTHS[psname]
            else:
                nom_strengths = 0.0
            strengths = [nom_strengths, ] * self._wfm_nrpoints
        self._currents = self._conv_strengths_2_currents(strengths)
        self._strengths = self._conv_currents_2_strengths(self._currents)

    @property
    def duration(self):
        """Ramp duration."""
        return self._dipole.duration

    def update(self):
        """Update object."""
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
            if self._dipole.wfm_nrpoints != self._wfm_nrpoints:
                dip_strengths = _np.interp(
                    self.times, self._dipole.times, self._dipole.strengths)
            else:
                dip_strengths = self._dipole.strengths
            kwargs['strengths_dipole'] = dip_strengths
        if self._family is not None:
            if self._family.wfm_nrpoints != self._wfm_nrpoints:
                fam_strengths = _np.interp(
                    self.times, self._family.times, self._family.strengths)
            else:
                fam_strengths = self._family.strengths
            kwargs['strengths_family'] = fam_strengths
        return self.conv_current_2_strength(**kwargs)

    def _conv_strengths_2_currents(self, strengths):
        kwargs = {'strengths': strengths}
        if self._dipole is not None:
            if self._dipole.wfm_nrpoints != self._wfm_nrpoints:
                dip_strengths = _np.interp(
                    self.times, self._dipole.times, self._dipole.strengths)
            else:
                dip_strengths = self._dipole.strengths
            kwargs['strengths_dipole'] = dip_strengths
        if self._family is not None:
            if self._family.wfm_nrpoints != self._wfm_nrpoints:
                fam_strengths = _np.interp(
                    self.times, self._family.times, self._family.strengths)
            else:
                fam_strengths = self._family.strengths
            kwargs['strengths_family'] = fam_strengths
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
