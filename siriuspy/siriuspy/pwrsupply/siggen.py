"""Power Supply Signal Generator."""


import numpy as _np


class SigGenConfig:
    """Signal Generator config class."""

    TYPES = ('Sine', 'DampedSine', 'Trapezoidal')

    def __init__(self, data=None,
                 type=None,  # Sine, DampedSine, Trapezoidal
                 nr_cycles=None,  # Sine, DampedSine, Trapezoidal
                 freq=None,  # [Hz] Sine, DampedSine
                 amplitude=None,  # [A] Sine, DampedSine, Trapezoidal
                 offset=None,  # [A] Sine, DampedSine, Trapezoidal
                 aux_param=None,  # Sine, DampedSine, Trapezoidal
                 rampup_time=None,  # [s] Trapezoidal
                 rampdown_time=None,  # [s] Trapezoidal
                 plateau_time=None,  # [s] Trapezoidal
                 theta_begin=None,  # Sine, DampedSine
                 theta_end=None,  # Sine, DampedSine
                 decay_time=None):  # DampedSine
        """Init method."""
        # set default values
        self._set_default_config()
        # process input arguments
        if data is not None:
            self.type = str(data[0])
            self.nr_cycles = int(data[1])
            self.freq = float(data[2])
            self.amplitude = float(data[3])
            self.offset = float(data[4])
            self.aux_param = [float(d) for d in data[5:9]]
        self.type = str(type) if type is not None else self.type
        self.nr_cycles = int(nr_cycles) if nr_cycles is not None \
            else self.nr_cycles
        self.freq = float(freq) if freq is not None else self.freq
        self.amplitude = float(amplitude) if amplitude is not None \
            else self.amplitude
        self.offset = float(offset) if offset is not None \
            else self.offset
        if aux_param is not None:
            self.aux_param = [float(d) for d in aux_param[0:4]]
        self.aux_param[0] = float(rampup_time) if rampup_time is not None \
            else self.aux_param[0]
        self.aux_param[1] = float(rampdown_time) if rampdown_time is not None \
            else self.aux_param[1]
        self.aux_param[2] = float(plateau_time) if plateau_time is not None \
            else self.aux_param[2]
        self.aux_param[0] = float(theta_begin) if theta_begin is not None \
            else self.aux_param[0]
        self.aux_param[1] = float(theta_end) if theta_end is not None \
            else self.aux_param[1]
        self.aux_param[2] = float(decay_time) if decay_time is not None \
            else self.aux_param[2]

    # --- public methods ---

    @property
    def duration(self):
        """Duration of signal [s]."""
        return self.nr_cycles / self.freq

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

    def get_waveform(self, nr_points=100):
        """Return list with signal waveform."""
        t = _np.linspace(0.0, self.duration, nr_points)
        if self.type in ('Sine', 'DampedSine'):
            # TODO: confirm!
            if self.type == 'Sine':
                amp = self.amplitude * _np.ones(t.shape)
            else:
                amp = self.amplitude * _np.exp(-t/self.decay_time)
            wfm = self.offset * _np.ones(t.shape)
            phase = self.freq*t % (2*_np.pi)
            sel_in = (phase >= self.theta_begin) and (phase <= self.theta_end)
            wfm_delta = amp * _np.sin(phase)
            wfm[sel_in] += wfm_delta[sel_in]
        else:
            # TODO: implement get_waveform for 'Trapezoidal' type.
            wfm = _np.zeros(t.shape) + self.offset
        return wfm

    # --- private methods ---

    def _set_default_config(self):
        self.type = 'Sine'
        self.nr_cycles = 1
        self.freq = 100.0  # [A]
        self.amplitude = 0.0
        self.offset = 0.0  # [A]
        self.aux_param = [0.0, 0.0, 0.0, 0.0]
