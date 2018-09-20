"""Waveform classes."""

import numpy as _np

from siriuspy import util as _util
from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE as _MAX_WFMSIZE
from siriuspy.ramp import util as _rutil
from siriuspy.ramp.magnet import Magnet as _Magnet
from siriuspy.ramp.exceptions import RampInvalidDipoleWfmParms as \
    _RampInvalidDipoleWfmParms


class WaveformParam:
    """Dipole parameterized Waveforms."""

    def __init__(
            self,
            duration=_rutil.DEFAULT_RAMP_DURATION,
            start_energy=_rutil.DEFAULT_RAMP_START_ENERGY,
            rampup_start_time=_rutil.DEFAULT_RAMP_RAMPUP_START_TIME,
            rampup_start_energy=_rutil.DEFAULT_RAMP_RAMPUP_START_ENERGY,
            rampup_stop_time=_rutil.DEFAULT_RAMP_RAMPUP_STOP_TIME,
            rampup_stop_energy=_rutil.DEFAULT_RAMP_RAMPUP_STOP_ENERGY,
            plateau_energy=_rutil.DEFAULT_RAMP_PLATEAU_ENERGY,
            rampdown_start_time=_rutil.DEFAULT_RAMP_RAMPDOWN_START_TIME,
            rampdown_start_energy=_rutil.DEFAULT_RAMP_RAMPDOWN_START_ENERGY,
            rampdown_stop_time=_rutil.DEFAULT_RAMP_RAMPDOWN_STOP_TIME,
            rampdown_stop_energy=_rutil.DEFAULT_RAMP_RAMPDOWN_STOP_ENERGY,
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
                raise ValueError(str(t))
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
            self._update_invalid_state()
            if not self._invalid:
                self._calc_region1_parms()
                self._calc_region2_parms()
                self._calc_region3_parms()
                self._calc_region4_parms()
                self._calc_region5_parms()
            self._changed = False

    @property
    def changed(self):
        """State of change."""
        return self._changed

    @property
    def anomalies(self):
        """Return anomalies."""
        self.update()
        return self._anomalies

    @property
    def invalid(self):
        """Invalid state."""
        self._update_invalid_state()
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

    def _clear_anomalies(self):
        self._anomalies = set()
        self._invalid = False

    def _check_valid_parameters_times(self):
        if 0 >= self._rampup_start_time:
            self._anomalies.add('Rampup start time <= 0')
        elif self._rampup_start_time >= self._rampup_stop_time:
            self._anomalies.add('Rampup start time >= Rampup stop time')
        elif self._rampup_stop_time > self._rampdown_start_time:
            self._anomalies.add('Rampup stop time > rampdown start time')
        elif self._rampdown_start_time >= self._rampdown_stop_time:
            self._anomalies.add('Rampdown start time >= Rampdown stop time')
        elif self._rampdown_stop_time > self._duration:
            self._anomalies.add('Rampdown stop time > Duration')

    def _check_valid_parameters_energies(self):
        if self._start_energy < 0.0:
            self._anomalies.add('Start energy < 0.0')
        elif self._start_energy > self._rampup_start_energy:
            self._anomalies.add('Start energy > Rampup start energy')
        elif self._rampup_start_energy >= self._rampup_stop_energy:
            self._anomalies.add('Rampup start energy > Rampup stop energy')
        elif self._rampup_stop_energy > self._plateau_energy:
            self._anomalies.add('Rampup stop energy > Plateau energy')
        elif self._plateau_energy < self._rampdown_start_energy:
            self._anomalies.add('Plateau energy < Rampdown start energy')
        elif self._rampdown_start_energy <= self._rampdown_stop_energy:
            self._anomalies.add(
                'Rampdown start energy <= Rampdown stop energy')
        elif self._rampdown_stop_energy < self._start_energy:
            self._anomalies.add('Rampdown stop energy < Start energy')

    def _update_invalid_state(self):
        if self._changed:
            self._clear_anomalies()
            self._check_valid_parameters_times()
            self._check_valid_parameters_energies()
            if self._anomalies:
                self._invalid = True
            else:
                self._invalid = False

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
        if t < self._t_pb:
            Du, Dd = self._t_pb_D, self._t_pe_D
            n = self._n
            ts = self._t_pb - t2
            d = t - t2
            v = v2 + Du * (ts**n*d - d**(n+1)/(n+1.0)) / ts**n
        elif self._t_pb <= t <= self._t_pe:
            v = self._plateau_energy
        else:
            Du, Dd = self._t_pb_D, self._t_pe_D
            n = self._n
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
            self._anomalies.add('There is a minimum in region before rampup')

    def _calc_region2_parms(self):
        # calc poly coeffs
        self._c1_2 = self._calc_Du()
        # check crescent function
        if self._c1_2 < 0.0:
            self._anomalies.add('Rampup is decreasing')

    def _calc_region3_parms(self):
        # calc poly coeffs
        self._c1_3 = self._calc_Dd()
        # check crescent function
        if self._c1_3 > 0.0:
            self._anomalies.add('Rampdown is increasing')

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
            self._anomalies.add('There is a minimum in region after rampdown')

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
            self._anomalies.add(
                'Plateau region with non-defined curvature sign')
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


class _WaveformMagnet:
    """Base class of magnet waveforms."""

    _magnets = dict()  # dict with magnets objects to improve efficiency

    def __init__(self, maname,
                 wfm_nrpoints=_MAX_WFMSIZE,
                 **kwargs):
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

    _E0 = _util.get_electron_rest_energy()

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
            if _np.any(_np.array(self._waveform) < WaveformDipole._E0):
                raise _RampInvalidDipoleWfmParms(
                    'Dipole energy less than electron rest energy.')

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
