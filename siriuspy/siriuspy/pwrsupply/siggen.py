"""Power Supply Signal Generator."""

import time as _t
import math as _math
# import numpy as _np


class Signal:
    """Signal from SigGen."""

    def __init__(self,
                 type,
                 num_cycles,  # Sine, DampedSine, Trapezoidal
                 freq,  # [Hz] Sine, DampedSine
                 amplitude,  # [A] Sine, DampedSine, Trapezoidal
                 offset,  # [A] Sine, DampedSine, Trapezoidal
                 aux_param,  # Sine, DampedSine, Trapezoidal)
                 **kwargs
                 ):
        """Init method."""
        self.type = type
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
        return value

    @property
    def theta_begin(self):
        """Initial phase for Sine or DampedSine signals."""
        return self.aux_param[0]

    @theta_begin.setter
    def theta_begin(self, value):
        """Set Initial phase for Sine or DampedSine signals."""
        self.aux_param[0] = value
        return value

    @property
    def rampdown_time(self):
        """Rampdown time for Trapezoidal signals."""
        return self.aux_param[1]

    @rampdown_time.setter
    def rampdown_time(self, value):
        """Set Rampdown time for Trapezoidal signals."""
        self.aux_param[1] = value
        return value

    @property
    def theta_end(self):
        """Final phase for Sine or DampedSine signals."""
        return self.aux_param[1]

    @theta_end.setter
    def theta_end(self, value):
        """Set Final phase for Sine or DampedSine signals."""
        self.aux_param[1] = value
        return value

    @property
    def plateau_time(self):
        """Plateau time for Trapezoidal signals."""
        return self.aux_param[2]

    @plateau_time.setter
    def plateau_time(self, value):
        """Set Plateau time for Trapezoidal signals."""
        self.aux_param[2] = value
        return value

    @property
    def decay_time(self):
        """Decay time constant for DampedSine signals."""
        return self.aux_param[2]

    @decay_time.setter
    def decay_time(self, value):
        """Set Decay time constant for DampedSine signals."""
        self.aux_param[2] = value
        return value

    # def get_waveform(self, nr_points=100):
    #     """Return list with signal waveform."""
    #     d2r = _np.pi/180.0
    #     t = _np.linspace(0.0, self.duration, nr_points)
    #     if self.type in ('Sine', 'DampedSine'):
    #         # TODO: confirm!
    #         if self.type == 'Sine':
    #             amp = self.amplitude * _np.ones(t.shape)
    #         else:
    #             amp = self.amplitude * _np.exp(-t/self.decay_time)
    #         wfm = self.offset * _np.ones(t.shape)
    #         phase = (2*_np.pi) * (self.freq*t % 1)
    #         sel_in = \
    #             (phase >= d2r * self.theta_begin) & \
    #             (phase <= d2r * self.theta_end)
    #         wfm_delta = amp * _np.sin(phase)
    #         # wfm = wfm_delta
    #         wfm[sel_in] += wfm_delta[sel_in]
    #     else:
    #         # TODO: implement get_waveform for 'Trapezoidal' type.
    #         wfm = _np.zeros(t.shape) + self.offset
    #     return wfm, sel_in, phase, wfm_delta

    # --- virtual methods ---

    def _get_duration(self):
        raise NotImplementedError

    def _get_cycle_time(self):
        raise NotImplementedError

    def _get_value(self, time_delta):
        raise NotImplementedError


class SignalTrapezoidal(Signal):
    """Trapezoidal signal."""

    def __init__(self, **kwargs):
        """Init method."""
        super().__init__(**kwargs)

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
            target = self.offset + self.amplitude
            if cycle_pos < self.rampup_time:
                return self.offset + \
                    (cycle_pos/self.rampup_time)*(target - self.offset)
            elif cycle_pos < (self.rampup_time + self.plateau_time):
                return target
            else:
                down_time = cycle_pos - (self.rampup_time + self.plateau_time)
                return target - \
                    (down_time / self.rampdown_time)*(target - self.offset)

    def _check(self):
        if self.rampup_time == 0:
            self.rampup_time = 0.1
        if self.plateau_time == 0:
            self.plateau_time = 0.1
        if self.rampdown_time == 0:
            self.rampdown_time = 0.1


class SignalSine(Signal):
    """Sine signal."""

    def __init__(self, **kwargs):
        """Init method."""
        super().__init__(**kwargs)

    def _get_duration(self):
        return self.num_cycles / self.freq

    def _get_cycle_time(self):
        return 1.0 / self.freq

    def _get_value(self, time_delta):
        if self.duration > 0 and time_delta > self.duration:
            # self.enable = False
            return self.offset
        else:
            value = self.offset + self._get_sin_signal(time_delta)
            return value

    def _get_sin_signal(self, time_delta):
        # TODO: use theta_beg and theta_end!
        value = self.amplitude * \
            _math.sin(2 * _math.pi * self.freq * time_delta)
        return value


class SignalDampedSine(SignalSine):
    """DampedSine signal."""

    def __init__(self, **kwargs):
        """Init method."""
        super().__init__(**kwargs)

    def _get_sin_signal(self, time_delta):
        sinsig = super()._get_sin_signal(time_delta)
        expsig = _math.exp(-time_delta/self.decay_time)
        value = self.offset + sinsig * expsig
        return value


class SignalFactory:
    """Signal Generator Factory."""

    TYPES = {'Sine': 0, 'DampedSine': 1, 'Trapezoidal': 2}

    @staticmethod
    def factory(data=None, **kwargs):
        """Init method."""
        # type
        # num_cycles=None,  # Sine, DampedSine, Trapezoidal
        # freq=None,  # [Hz] Sine, DampedSine
        # amplitude=None,  # [A] Sine, DampedSine, Trapezoidal
        # offset=None,  # [A] Sine, DampedSine, Trapezoidal
        # aux_param=None,  # Sine, DampedSine, Trapezoidal
        # rampup_time=None,  # [s] Trapezoidal
        # rampdown_time=None,  # [s] Trapezoidal
        # plateau_time=None,  # [s] Trapezoidal
        # theta_begin=None,  # [deg] Sine, DampedSine
        # theta_end=None,  # [deg] Sine, DampedSine
        # decay_time=None):  # [s] DampedSine
        #
        kw = dict()
        kw.update(kwargs)
        if 'type' in kw and isinstance(kw['type'], str):
            kw['type'] = SignalFactory.TYPES[kw['type']]

        if kw['type'] == SignalFactory.TYPES['Trapezoidal']:
            return SignalTrapezoidal(**kw)
        elif kw['type'] == SignalFactory.TYPES['Sine']:
            kw['num_cycles'] = 1
            kw['freq'] = 100.0  # [A]
            kw['amplitude'] = 0.0
            kw['offset'] = 0.0  # [A]
            kw['aux_param'] = [0.0, 360.0, 0.0, 0.0]
        elif kw['type'] == SignalFactory.TYPES['DampedSine']:
            kw['num_cycles'] = 1
            kw['freq'] = 100.0  # [A]
            kw['amplitude'] = 0.0
            kw['offset'] = 0.0  # [A]
            kw['aux_param'] = [0.0, 360.0, 0.0, 0.0]
            return SignalDampedSine(**kw)
        else:
            raise NotImplementedError('Signal type not implemented!')


        # set default values
        if data is not None:
            kw['type'] = data[0]
            kw['num_cycles'] = int(data[1])
            kw['freq'] = float(data[2])
            kw['amplitude'] = float(data[3])
            kw['offset'] = float(data[4])
            kw['aux_param'] = [float(d) for d in data[5:9]]

        if 'rampup_time' in kw:
            kw['aux_param'][0] = float(kw['rampup_time'])
        if 'rampdown_time' in kw:
            kw['aux_param'][1] = float(kw['rampdown_time'])
        if 'plateau_time' in kw:
            kw['aux_param'][2] = float(kw['plateau_time'])
        if 'theta_begin' in kw:
            kw['aux_param'][0] = float(kw['theta_begin'])
        if 'theta_end' in kw:
            kw['aux_param'][1] = float(kw['theta_end'])
        if 'decay_time' in kw:
            kw['aux_param'][2] = float(kw['decay_time'])

        if type == SignalFactory.TYPES['Trapezoidal']:
            return SignalTrapezoidal(**kw)
        elif type == SignalFactory.TYPES['Sine']:
            return SignalSine(**kw)
        elif type == SignalFactory.TYPES['DampedSine']:
            return SignalDampedSine(**kw)
        else:
            raise NotImplementedError('Signal type not implemented!')
