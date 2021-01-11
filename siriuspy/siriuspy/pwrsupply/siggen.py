"""Power Supply Signal Generator."""

import time as _t
import math as _math


DEFAULT_SIGGEN_CONFIG = (
    0,      # sigtype  [0:Sine]
    100,    # num_cycles
    2.0,    # freq [Hz]
    0.0,    # amplitude [A] (Maximum amplitude)
    0.0,    # offset [A]
    0.0,    # aux_param[0]
            #   (Sine|DampedSine|DampedSquaredSine: theta_beg,
            #    Trapezoidal: ramp up[s])
    0.0,    # aux_param[1]
            #   (Sine|DampedSine|DampedSquaredSine: theta_end,
            #    Trapezoidal: ramp down[s])
    0.0,    # aux_param[2]
            #   (DampedSine|DampedSquaredSine: decay time [s])
    0.0     # aux_param[3]
            #   (reserved)
    )


class Signal:
    """Signal from SigGen."""

    def __init__(self,
                 sigtype,
                 num_cycles,  # Sine, DampedSine, DampedSqrdSin, Trapezoidal
                 freq,  # [Hz] Sine, DampedSine, DampedSqrdSin
                 amplitude,  # [A] Sine, DampedSine, DampedSqrdSin, Trapezoidal
                 offset,  # [A] Sine, DampedSine, DampedSqrdSin, Trapezoidal
                 aux_param,  # Sine, DampedSine, DampedSqrdSin, Trapezoidal)
                 **kwargs
                 ):
        """Init method."""
        _ = kwargs  # throwaway arguments
        self.sigtype = sigtype
        self.num_cycles = num_cycles
        self.freq = freq
        self.amplitude = amplitude
        self.offset = offset
        self.aux_param = aux_param
        self.enable = True
        self.time_init = _t.time()
        self.time_delta = self.time_init

    @property
    def duration(self):
        """Return total duration. Zero is infinite time."""
        return self._get_duration()

    @property
    def value(self):
        """Return current signal value."""
        if self.enable:
            self.time_delta = _t.time() - self.time_init
        return self._get_value(self.time_delta)

    @property
    def cycle_time(self):
        """Return period of signal."""
        return self._get_cycle_time()

    @property
    def rampup_time(self):
        """Rampup time for Trapezoidal signals."""
        return self.aux_param[0]

    @rampup_time.setter
    def rampup_time(self, value):
        """Set Rampup time for Trapezoidal signals."""
        self.aux_param[0] = value
        self._update()
        return value

    @property
    def theta_begin(self):
        """Return initial phase for Sine or Damped(Squared)Sine signals."""
        return self.aux_param[0]

    @theta_begin.setter
    def theta_begin(self, value):
        """Set Initial phase for Sine or Damped(Squared)Sine signals."""
        self.aux_param[0] = value
        self._update()
        return value

    @property
    def rampdown_time(self):
        """Rampdown time for Trapezoidal signals."""
        return self.aux_param[2]

    @rampdown_time.setter
    def rampdown_time(self, value):
        """Set Rampdown time for Trapezoidal signals."""
        self.aux_param[2] = value
        self._update()
        return value

    @property
    def theta_end(self):
        """Return final phase for Sine or Damped(Squared)Sine signals."""
        return self.aux_param[1]

    @theta_end.setter
    def theta_end(self, value):
        """Set Final phase for Sine or Damped(Squared)Sine signals."""
        self.aux_param[1] = value
        self._update()
        return value

    @property
    def plateau_time(self):
        """Plateau time for Trapezoidal signals."""
        return self.aux_param[1]

    @plateau_time.setter
    def plateau_time(self, value):
        """Set Plateau time for Trapezoidal signals."""
        self.aux_param[1] = value
        self._update()
        return value

    @property
    def decay_time(self):
        """Decay time constant for Damped(Squared)Sine signals."""
        return self.aux_param[2]

    @decay_time.setter
    def decay_time(self, value):
        """Set Decay time constant for Damped(Squared)Sine signals."""
        self.aux_param[2] = value
        self._update()
        return value

    def reset(self):
        """Reset init time."""
        self.time_init = _t.time()

    def get_waveform(self, nrpts=100):
        """."""
        tmax = self.duration
        tstep = tmax/(nrpts-1) if nrpts > 1 else tmax
        tval, wval = [], []
        time = 0
        while True:
            wvalue = self._get_value(time)
            _ = tval.append(time), wval.append(wvalue)
            if len(tval) == nrpts:
                break
            time += tstep
            if time > tmax:
                time = tmax
        return wval, tval

    # --- virtual methods ---

    def _get_duration(self):
        raise NotImplementedError

    def _get_cycle_time(self):
        raise NotImplementedError

    def _get_value(self, time_delta):
        raise NotImplementedError

    def _update(self):
        raise NotImplementedError


class SignalSine(Signal):
    """Sine signal."""

    def _get_duration(self):
        return self.num_cycles / self.freq

    def _get_cycle_time(self):
        return 1.0 / self.freq

    def _get_value(self, time_delta):
        if self.duration > 0 and time_delta > self.duration:
            # self.enable = False
            return self.offset
        else:
            value = self.offset + self.amplitude * \
                self._get_sin_signal(time_delta)
            return value

    def _get_sin_signal(self, time_delta):
        value = _math.sin(2 * _math.pi * self.freq * time_delta +
                          _math.radians(self.theta_begin))
        return value

    def _update(self):
        pass


class SignalDampedNSine(SignalSine):
    """DampedNSine signal."""

    def __init__(self, n, **kwargs):
        """Init method."""
        super().__init__(**kwargs)
        self.n = n
        self._update()

    def _get_sin_signal(self, time_delta):
        sinsig = (super()._get_sin_signal(time_delta))**self.n
        expsig = self._f * _math.exp(-time_delta/self.decay_time)
        value = sinsig * expsig
        return value

    def _update(self):
        self.wfreq = 2*_math.pi*self.freq
        if self.wfreq != 0.0:
            self._t0 = _math.atan(self.wfreq*self.decay_time*self.n)/self.wfreq
        else:
            self._t0 = 0.0
        self._f = _math.exp(self._t0/self.decay_time) / \
            _math.sin(self.wfreq*self._t0)**self.n


class SignalDampedSine(SignalDampedNSine):
    """DampedSine signal."""

    def __init__(self, **kwargs):
        """Init method."""
        super().__init__(n=1, **kwargs)


class SignalDampedSquaredSine(SignalDampedNSine):
    """DampedSquaredSine signal."""

    def __init__(self, **kwargs):
        """Init method."""
        super().__init__(n=2, **kwargs)


class SignalTrapezoidal(Signal):
    """Trapezoidal signal."""

    def _get_duration(self):
        return self.cycle_time * self.num_cycles

    def _get_cycle_time(self):
        return self.rampup_time + self.plateau_time + self.rampdown_time

    def _get_value(self, time_delta):
        if self.duration > 0 and time_delta > self.duration:
            # self.enable = False
            return self.offset
        else:
            cycle_pos = time_delta % self.cycle_time
            if cycle_pos < self.rampup_time:
                value = self.amplitude*cycle_pos/self.rampup_time
            elif cycle_pos < (self.rampup_time + self.plateau_time):
                value = self.amplitude
            else:
                down_time = cycle_pos - (self.rampup_time + self.plateau_time)
                value = self.amplitude*(1 - down_time/self.rampdown_time)
            return self.offset + value

    def _check(self):
        # TODO: avoid this workaround!
        if self.rampup_time == 0:
            self.rampup_time = 0.1
        if self.plateau_time == 0:
            self.plateau_time = 0.1
        if self.rampdown_time == 0:
            self.rampdown_time = 0.1

    def _update(self):
        pass


class SignalSquare(SignalSine):
    """Square signal."""

    def _get_value(self, time_delta):
        if self.duration > 0 and time_delta > self.duration:
            value = self.offset
        elif self._get_sin_signal(time_delta) < 0:
            value = - self.amplitude + self.offset
        else:
            value = self.amplitude + self.offset
        return value


class SigGenFactory:
    """Signal Generator Factory."""

    TYPES = {
        'Sine': 0,
        'DampedSine': 1,
        'Trapezoidal': 2,
        'DampedSquaredSine': 3,
        'Square': 4}

    TYPES_IND = {v: k for k, v in TYPES.items()}

    DEFAULT_CONFIGS = {
        'Sine': DEFAULT_SIGGEN_CONFIG,
        'DampedSine': [1, 1, 100.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        'Trapezoidal': [2, 1, 0.0, 0.0, 0.0, 0.01, 0.01, 0.01, 0.0],
        'DampedSquaredSine': [3, 1, 100.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        'Square': [4, 3.0, 0.1, 5.0, 5.0, 270.0, 270.0, 0.0, 0.0],
        }

    @staticmethod
    def create(data=None, **kwargs):
        """Implement factory method.

            This methods returns a Signal object corresponding to the
        selected type.

        Valid arguments:

        sigtype: Signal type, int or str (Sine|DampedSine|Trapezoidal|Square)
        num_cycles: Number of cycles, int (Sine|DampedSine|Trapezoidal|Square)
        freq: Frequency [Hz], float, (Sine|DampedSine|Square)
        amplitude: Amplitude [A], float, (Sine|DampedSine|Trapezoidal|Square)
        offset: Offset [A], float, (Sine|DampedSine|Trapezoidal|Square)
        aux_param: Aux. Parameters, float4 (Sine|DampedSine|Trapezoidal|Square)
        rampup_time: Rampup time [s], float, (Trapezoidal) - aux_param[0]
        rampdown_time: Rampdown time [s], float, (Trapezoidal) - aux_param[1]
        plateau_time: Plateau time [s], float, (Trapezoidal) - aux_param[2]
        theta_begin: Initial phase[deg] (Sine|DampedSine|Square) - aux_param[0]
        theta_end: Final phase[deg] (Sine|DampedSine|Square) - aux_param[1]
        decay_time: Decay time [s] (DampedSine) - aux_param[2]
        """
        # set signal type
        if 'sigtype' in kwargs:
            sigtype = kwargs['sigtype']
        elif data is not None:
            sigtype = data[0]
        else:
            sigtype = SigGenFactory.TYPES['Sine']
        if isinstance(sigtype, str):
            sigtype = SigGenFactory.TYPES[sigtype]

        # set ps controller initial values
        kwa = SigGenFactory._set_kwa(kwargs, sigtype, data)

        if sigtype == SigGenFactory.TYPES['Trapezoidal']:
            return SignalTrapezoidal(**kwa)
        elif sigtype == SigGenFactory.TYPES['Sine']:
            return SignalSine(**kwa)
        elif sigtype == SigGenFactory.TYPES['DampedSine']:
            return SignalDampedSine(**kwa)
        elif sigtype == SigGenFactory.TYPES['DampedSquaredSine']:
            return SignalDampedSquaredSine(**kwa)
        elif sigtype == SigGenFactory.TYPES['Square']:
            return SignalSquare(**kwa)

        # NOTE: this point should not be reached!
        return None

    @staticmethod
    def _set_kwa(kwargs, sigtype, data):
        # set ps controller initial values
        kwa = dict()
        kwa.update(kwargs)
        kwa['sigtype'] = sigtype
        parms = SigGenFactory.DEFAULT_CONFIGS[SigGenFactory.TYPES_IND[sigtype]]

        kwa['num_cycles'] = parms[1]
        kwa['freq'] = parms[2]  # [A]
        kwa['amplitude'] = parms[3]
        kwa['offset'] = parms[4]  # [A]
        kwa['aux_param'] = parms[5:9]

        # process data argument
        # kwa = dict()
        if data is not None:
            kwa['sigtype'] = data[0]
            kwa['num_cycles'] = int(data[1])
            kwa['freq'] = float(data[2])
            kwa['amplitude'] = float(data[3])
            kwa['offset'] = float(data[4])
            kwa['aux_param'] = [float(d) for d in data[5:9]]

        # process type argument
        kwa.update(kwargs)
        if 'rampup_time' in kwa:
            kwa['aux_param'][0] = float(kwa['rampup_time'])
        if 'rampdown_time' in kwa:
            kwa['aux_param'][1] = float(kwa['rampdown_time'])
        if 'plateau_time' in kwa:
            kwa['aux_param'][2] = float(kwa['plateau_time'])
        if 'theta_begin' in kwa:
            kwa['aux_param'][0] = float(kwa['theta_begin'])
        if 'theta_end' in kwa:
            kwa['aux_param'][1] = float(kwa['theta_end'])
        if 'decay_time' in kwa:
            kwa['aux_param'][2] = float(kwa['decay_time'])

        return kwa
