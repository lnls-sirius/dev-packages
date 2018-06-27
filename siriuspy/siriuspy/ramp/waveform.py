"""Waveform classes."""

import numpy as _np

from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE as _MAX_WFMSIZE
from siriuspy.ramp import util as _util
from siriuspy.ramp.magnet import Magnet as _Magnet


_np.seterr(all='ignore')


class WaveformParam:
    """Dipole parameterized Waveforms."""

    def __init__(
            self,
            duration=_util.DEFAULT_RAMP_DURATION,
            start_energy=_util.DEFAULT_RAMP_START_ENERGY,
            rampup_start_time=_util.DEFAULT_RAMP_RAMPUP_START_TIME,
            rampup_start_energy=_util.DEFAULT_RAMP_RAMPUP_START_ENERGY,
            rampup_stop_time=_util.DEFAULT_RAMP_RAMPUP_STOP_TIME,
            rampup_stop_energy=_util.DEFAULT_RAMP_RAMPUP_STOP_ENERGY,
            plateau_energy=_util.DEFAULT_RAMP_PLATEAU_ENERGY,
            rampdown_start_time=_util.DEFAULT_RAMP_RAMPDOWN_START_TIME,
            rampdown_start_energy=_util.DEFAULT_RAMP_RAMPDOWN_START_ENERGY,
            rampdown_stop_time=_util.DEFAULT_RAMP_RAMPDOWN_STOP_TIME,
            rampdown_stop_energy=_util.DEFAULT_RAMP_RAMPDOWN_STOP_ENERGY,
            **kwargs):
        """Init method."""
        self._duration = duration
        self._start_energy = start_energy
        self._rampup_start_time = rampup_start_time
        self._rampup_start_energy = rampup_start_energy
        self._rampup_stop_time = rampup_stop_time
        self._rampup_stop_energy = rampup_stop_energy
        self._plateau_energy = plateau_energy
        self._rampdown_start_time = rampdown_start_time
        self._rampdown_start_energy = rampdown_start_energy
        self._rampdown_stop_time = rampdown_stop_time
        self._rampdown_stop_energy = rampdown_stop_energy
        self._changed = True

    def eval_at(self, t):
        """Return waveform value at a time instant."""
        def _get_at(t):
            if 0.0 <= t < self._rampup_start_time:
                return self._func_region1(t)
            elif self._rampup_start_time <= t < self._rampup_stop_time:
                return self._func_region2(t)
            elif self._rampup_stop_time <= t < self._rampdown_start_time:
                return self._func_region5(t)
            elif self._rampdown_start_time <= t < self._rampdown_stop_time:
                return self._func_region3(t)
            elif self._rampdown_stop_time <= t <= self._duration:
                return self._func_region4(t)
            else:
                raise ValueError()
        self.update()
        if self._invalid:
            raise ValueError('Invalid parameters')
        if isinstance(t, (list, tuple, _np.ndarray)):
            return [_get_at(t1) for t1 in t]
        else:
            return _get_at(t)

    def update(self):
        """Update calculation."""
        if self._changed:
            self._clear_errors()
            if not self._errors:
                self._check_valid_parameters_times()
            if not self._errors:
                self._check_valid_parameters_energies()
            if self._errors:
                self._invalid = True
            else:
                self._invalid = False
            if not self._errors:
                self._calc_region1_parms()
                self._calc_region2_parms()
                self._calc_region3_parms()
                self._calc_region4_parms()
                self._calc_region5_parms()
            self._changed = False

    @ property
    def changed(self):
        """State of change."""
        return self._changed

    @property
    def errors(self):
        """Return errors."""
        self.update()
        return self._errors

    @property
    def invalid(self):
        """Invalid state."""
        self.update()
        return self._invalid

    @property
    def start_energy(self):
        """Return waveform value at the left-end and first region boundary."""
        return self._start_energy

    @property
    def rampup_start_energy(self):
        """Return waveform value at the second region boundary."""
        return self._rampup_start_energy

    @property
    def rampup_start_time(self):
        """Instant in time when rampup starts."""
        return self._rampup_start_time

    @property
    def rampup_stop_energy(self):
        """Return waveform value at the 3rd region boundary."""
        return self._rampup_stop_energy

    @property
    def rampup_stop_time(self):
        """Instant in time when rampup stops."""
        return self._rampup_stop_time

    @property
    def plateau_start_time(self):
        """Instant in time when plateau starts."""
        self.update()
        if self._invalid:
            raise ValueError('Invalid parameters')
        return self._t_pb

    @property
    def plateau_energy(self):
        """Return waveform value at the 4th and 5th region boundaries."""
        return self._plateau_energy

    @property
    def plateau_stop_time(self):
        """Instant in time when plateau stops."""
        self.update()
        if self._invalid:
            raise ValueError('Invalid parameters')
        return self._t_pe

    @property
    def rampdown_start_energy(self):
        """Return waveform value at the 6h region boundary."""
        return self._rampdown_start_energy

    @property
    def rampdown_start_time(self):
        """Instant in time when rampdown starts."""
        return self._rampdown_start_time

    @property
    def rampdown_stop_energy(self):
        """Return waveform value at the 7th region boundary."""
        return self._rampdown_stop_energy

    @property
    def rampdown_stop_time(self):
        """Instant in time when rampdown stops."""
        return self._rampdown_stop_time

    @property
    def duration(self):
        """Ramp duration."""
        return self._duration

    @start_energy.setter
    def start_energy(self, value):
        """Set start energy."""
        self._start_energy = float(value)
        self._changed = True

    @rampup_start_time.setter
    def rampup_start_time(self, value):
        """Set time of rampup start."""
        self._rampup_start_time = float(value)
        self._changed = True

    @rampup_start_energy.setter
    def rampup_start_energy(self, value):
        """Set energy of rampup start."""
        self._rampup_start_energy = float(value)
        self._changed = True

    @rampup_stop_time.setter
    def rampup_stop_time(self, value):
        """Set time of rampup stop."""
        self._rampup_stop_time = float(value)
        self._changed = True

    @rampup_stop_energy.setter
    def rampup_stop_energy(self, value):
        """Set energy of rampup stop."""
        self._rampup_stop_energy = float(value)
        self._changed = True

    @plateau_energy.setter
    def plateau_energy(self, value):
        """Set energy of plateau."""
        self._plateau_energy = float(value)
        self._changed = True

    @rampdown_start_time.setter
    def rampdown_start_time(self, value):
        """Set time of rampdown start."""
        self._rampdown_start_time = float(value)
        self._changed = True

    @rampdown_start_energy.setter
    def rampdown_start_energy(self, value):
        """Set energy of rampdown start."""
        self._rampdown_start_energy = float(value)
        self._changed = True

    @rampdown_stop_time.setter
    def rampdown_stop_time(self, value):
        """Set time of rampdown stop."""
        self._rampdown_stop_time = float(value)
        self._changed = True

    @rampdown_stop_energy.setter
    def rampdown_stop_energy(self, value):
        """Set energy of rampdown stop."""
        self._rampdown_stop_energy = float(value)
        self._changed = True

    # --- private methods ---

    def _clear_errors(self):
        self._errors = set()
        self._invalid = False

    def _check_valid_parameters_times(self):
        if 0 >= self._rampup_start_time:
            self._errors.add('0 >= rampup_start_time')
        elif self._rampup_start_time >= self._rampup_stop_time:
            self._errors.add('rampup_start_time >= rampup_stop_time')
        elif self._rampup_stop_time > self._rampdown_start_time:
            self._errors.add('rampup_stop_time > rampdown_start_time')
        elif self._rampdown_start_time >= self._rampdown_stop_time:
            self._errors.add('rampdown_start_time >= rampdown_stop_time')
        elif self._rampdown_stop_time > self._duration:
            self._errors.add('rampdown_stop_time > duration')

    def _check_valid_parameters_energies(self):
        if self._start_energy < 0.0:
            self._errors.add('start_energy < 0.0')
        elif self._start_energy > self._rampup_start_energy:
            self._errors.add('start_energy > rampup_start_energy')
        elif self._rampup_start_energy >= self._rampup_stop_energy:
            self._errors.add('rampup_start_energy > rampup_start_energy')
        elif self._rampup_stop_energy > self._plateau_energy:
            self._errors.add('rampup_stop_energy > plateau_energy')
        elif self._plateau_energy < self._rampdown_start_energy:
            self._errors.add('plateau_energy < rampdown_start_energy')
        elif self._rampdown_start_energy <= self._rampdown_stop_energy:
            self._errors.add('rampdown_start_energy <= rampdown_stop_energy')
        elif self._rampdown_stop_energy < self._start_energy:
            self._errors.add('rampdown_stop_energy < start_energy')

    def _func_region1(self, t):
        """Region1 function."""
        v0 = self._start_energy
        d = t - 0.0
        v = v0 + self._c2_1*d**2 + self._c3_1*d**3
        return v

    def _func_region2(self, t):
        """Region2 function."""
        t1, v1 = self._rampup_start_time, self._rampup_start_energy
        d = t - t1
        v = v1 + self._c1_2*d
        return v

    def _func_region3(self, t):
        """Region3 function."""
        t3, v3 = self._rampdown_start_time, self._rampdown_start_energy
        d = t - t3
        v = v3 + self._c1_3*d
        return v

    def _func_region4(self, t):
        """Region4 function."""
        v0 = self._start_energy
        d = self._duration - t
        v = v0 + self._c2_4*d**2 + self._c3_4*d**3
        return v

    def _func_region5(self, t):
        """Region5 function."""
        t2, v2 = self._rampup_stop_time, self._rampup_stop_energy
        t3, v3 = self._rampdown_start_time, self._rampdown_start_energy
        Du, Dd = self._t_pb_D, self._t_pe_D
        n = self._n
        if t < self._t_pb:
            ts = self._t_pb - t2
            d = t - t2
            v = v2 + Du * (ts**n*d - d**(n+1)/(n+1.0)) / ts**n
        elif self._t_pb <= t <= self._t_pe:
            v = self._plateau_energy
        else:
            ts = t3 - self._t_pe
            d = t3 - t
            v = v3 + Dd * (-ts**n*d + d**(n+1)/(n+1.0)) / ts**n
        return v

    def _calc_Du(self):
        t1, v1 = self._rampup_start_time, self._rampup_start_energy
        t2, v2 = self._rampup_stop_time, self._rampup_stop_energy
        Du = (v2 - v1) / (t2 - t1)
        return Du

    def _calc_Dd(self):
        t3, v3 = self._rampdown_start_time, self._rampdown_start_energy
        t4, v4 = self._rampdown_stop_time, self._rampdown_stop_energy
        Dd = (v4 - v3) / (t4 - t3)
        return Dd

    def _calc_region1_parms(self):
        v0 = self._start_energy
        t1, v1 = self._rampup_start_time, self._rampup_start_energy
        Du = self._calc_Du()
        # calc poly coeffs
        v = (v1 - v0, Du)
        m = ((t1**2, t1**3),
             (2.0*t1, 3*t1**2))
        detm = m[0][0]*m[1][1] - m[0][1]*m[1][0]
        self._c2_1 = (m[1][1] * v[0] - m[0][1] * v[1]) / detm
        self._c3_1 = (-m[1][0] * v[0] + m[0][0] * v[1]) / detm
        # check monotonicity
        self._tex_1 = -2.0*self._c2_1/self._c3_1/3.0
        self._vex_1 = self._func_region1(self._tex_1)
        if 0.0 < self._tex_1 < t1:
            self._errors.add('there is a maximum in region 1')

    def _calc_region2_parms(self):
        # calc poly coeffs
        self._c1_2 = self._calc_Du()
        # check crescent function
        if self._c1_2 < 0.0:
            self._errors.add('rampup is incorrect')

    def _calc_region3_parms(self):
        # calc poly coeffs
        self._c1_3 = self._calc_Dd()
        # check crescent function
        if self._c1_3 > 0.0:
            self._errors.add('rampdown is incorrect')

    def _calc_region4_parms(self):
        t4, v4 = self._rampdown_stop_time, self._rampdown_stop_energy
        v0 = self._start_energy
        Dd = self._calc_Dd()
        # calc poly coeffs
        v = (v4 - v0, Dd)
        d = self._duration - t4
        m = ((d**2, d**3),
             (-2.0*d, -3*d**2))
        detm = m[0][0]*m[1][1] - m[0][1]*m[1][0]
        self._c2_4 = (m[1][1] * v[0] - m[0][1] * v[1]) / detm
        self._c3_4 = (-m[1][0] * v[0] + m[0][0] * v[1]) / detm
        # check monotonicity
        self._tex_4 = self._duration + 2.0*self._c2_4/self._c3_4/3.0
        self._vex_4 = self._func_region4(self._tex_4)
        if t4 < self._tex_4 < self._duration:
            self._errors.add('there is a maximum in region 4')

    def _calc_region5_parms(self):
        # calculate where constant derivatives need extension to that
        # rampup and rampdown reach plateau value
        t2, v2 = self._rampup_stop_time, self._rampup_stop_energy
        t3, v3 = self._rampdown_start_time, self._rampdown_start_energy
        vm = self._plateau_energy
        Du = self._calc_Du()
        Dd = self._calc_Dd()
        t_pb = t2 + (vm - v2) / Du
        t_pe = t3 + (vm - v3) / Dd
        # print(t_pb, t_pe)
        if t_pb > t_pe:
            self._errors.add('non-monotonic plateau transition')
            self._t_pb = t2
            self._t_pe = t3
            return
        self._n = 2
        while True:
            A = vm - v2
            ts = (self._n+1.0)/self._n * A / Du
            self._t_pb = t2 + ts
            self._t_pb_D = Du
            A = vm - v3
            ts = (self._n+1.0)/self._n * A / Dd
            self._t_pe = t3 + ts
            self._t_pe_D = Dd
            if self._t_pb <= self._t_pe:
                # solution found
                break
            self._n += 1


class OldWaveformParam:
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
        self._deprecated = True
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
        """Deprecate state."""
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

    @rampup_start_time.setter
    def rampup_start_time(self, value):
        """Set time of rampup start."""
        dt = self.duration / (self.wfm_nrpoints - 1.0)
        idx = round(value / dt)
        self.rampup_start_index = idx

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

    @rampup_stop_time.setter
    def rampup_stop_time(self, value):
        """Set time of rampup stop."""
        dt = self.duration / (self.wfm_nrpoints - 1.0)
        idx = round(value / dt)
        self.rampup_stop_index = idx

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
            raise ValueError('Invalid plateau parameter.')
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

    @rampdown_start_time.setter
    def rampdown_start_time(self, value):
        """Set time of rampdown start."""
        dt = self.duration / (self.wfm_nrpoints - 1.0)
        idx = round(value / dt)
        self.rampdown_start_index = idx

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

    @rampdown_stop_time.setter
    def rampdown_stop_time(self, value):
        """Set time of rampdown stop."""
        dt = self.duration / (self.wfm_nrpoints - 1.0)
        idx = round(value / dt)
        self.rampdown_stop_index = idx

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
            raise ValueError('Invalid ramp up parameters.')
        i3 = self._find_i3(i1, i2, v1, v2)
        if i3 is None:
            raise ValueError('Could not find solution '
                             'for plateau_start_index.')
        i0 = self._find_i0(i1, i2, v1, v2)
        if i0 is None:
            raise ValueError('Could not find solution for i0.')
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
            raise ValueError('Invalid ramp down parameters.')
        i7 = self._find_i7(i5, i6, v5, v6)
        if i7 is None:
            raise ValueError('Could not find solution for i7.')
        i4 = self._find_i4(i5, i6, v5, v6)
        if i4 is None:
            raise ValueError('Could not find solution '
                             'for plateau_stop_index.')
        # change internal data - deprecated is automatically set to True.
        self.rampdown_start_index = i5
        self.rampdown_stop_index = i6
        self.rampdown_start_value = v5
        self.rampdown_stop_value = v6
        self._i[7], self._deprecated = i7, True
        self.plateau_stop_index = i4

    def update(self):
        """Update object."""
        if self._deprecated:
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
                raise ValueError('i0 < 0')
            if i07[-1] > self.wfm_nrpoints:
                raise ValueError('i7 >= {}.'.format(self.wfm_nrpoints))
            for i in range(0, len(i07)-1):
                if i07[i+1] < i07[i]:
                    raise ValueError('Boundary indices list is not sorted!')
            self._i = [int(i) for i in i07]
        except TypeError:
            raise TypeError('Invalid type of boundary indices list!')
        try:
            v07[0]
            if len(v07) != 8:
                raise ValueError('Lenght of boundary values list is not 8.')
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

    def __init__(self, maname,
                 wfm_nrpoints=_MAX_WFMSIZE,
                 **kwargs):
        _Magnet.__init__(self, maname=maname)
        self._wfm_nrpoints = wfm_nrpoints

    @property
    def times(self):
        dt = self.duration / (self.wfm_nrpoints - 1.0)
        return [dt*i for i in range(self.wfm_nrpoints)]

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


class WaveformDipole(_WaveformMagnet, WaveformParam):
    """Waveform for Dipole."""

    def __init__(self, maname='BO-Fam:MA-B', **kwargs):
        """Constructor."""
        _WaveformMagnet.__init__(self, maname, **kwargs)
        WaveformParam.__init__(self, **kwargs)
        self._waveform = None

    def update(self):
        """Upate."""
        WaveformParam.update(self)
        self._waveform = None

    @property
    def waveform(self):
        """Magnet waveform."""
        if self._changed or self._waveform is None:
            t = self.times
            self._waveform = self.eval_at(t)
        return self._waveform

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
            if self.maname in _util.NOMINAL_STRENGTHS:
                nom_strengths = _util.NOMINAL_STRENGTHS[self.maname]
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
