
from siriuspy.cs_device.enumtypes import enum_types as _enumt
import random as _random
import time as _time
from siriuspy.util import get_timestamp as _get_timestamp
from .waveform import PSWaveForm as _PSWaveForm


_Off     = _enumt.OffOnTyp.index('Off')
_On      = _enumt.OffOnTyp.index('On')
_SlowRef = _enumt.PSOpModeTyp.index('SlowRef')
_FastRef = _enumt.PSOpModeTyp.index('FastRef')
_WfmRef  = _enumt.PSOpModeTyp.index('WfmRef')
_SigGen  = _enumt.PSOpModeTyp.index('SigGen')


class Controller:
    """Base Controller Class

    This is a simple power supply controller that responds immediatelly
    to setpoints.

    all enum properties (pwrstate, opmode, etc) are set in ints.
    """

    def __init__(self, IOC=None,
                       current_min=None,
                       current_max=None,
                       waveform=None):

        self._IOC = IOC
        # --- default initial controller state ---
        self._pwrstate = _Off
        self._opmode   = _SlowRef
        self._current_ref  = 0.0  # PS feedback current setpoint
        self._current_dcct = 0.0  # PS feedback current readback
        self._current_min = current_min
        self._current_max = current_max
        self._waveform = _PSWaveForm.wfm_constant(2000)
        self._waveform_step = 0
        now = _time.time()
        self._timestamp_pwrstate = now
        self._timestamp_opmode   = now

    @property
    def IOC(self):
        return self._IOC

    @property
    def current(self):
        self.update_state()
        return self._current_dcct

    @property
    def pwrstate(self):
        return self._pwrstate

    @property
    def opmode(self):
        return self._opmode

    @IOC.setter
    def IOC(self, value):
        self._IOC = value

    @current.setter
    def current(self, value):
        value = value if self._current_min is None else max(value,self._current_min)
        value = value if self._current_max is None else min(value,self._current_max)
        self._current_ref = value # Should it happen even with PS off?
        self.update_state()

    @pwrstate.setter
    def pwrstate(self, value):
        self._timestamp_pwrstate = _time.time()
        if value == _Off:
            self._pwrstate = _Off
        elif value == _On:
            self._pwrstate = _On
        else:
            raise Exception('Invalid value!')
        self.update_state()

    @opmode.setter
    def opmode(self, value):
        if value == self._opmode: return # ?
        self._timestamp_opmode = _time.time()
        self._waveform_step = 0
        if value in tuple(range(len(_enumt.PSOpModeTyp))):
            self._opmode = value
        else:
            raise Exception('Invalid value!')
        self.update_state()

    def timing_trigger(self):
        if self._opmode == _WfmRef:
            self.current_dcct = self._waveform[self._waveform_step]
            self._waveform_step += 1
            if self._waveform_step >= self._waveform.nr_points:
                self._waveform_step = 0

    def update_state(self):
        if self._pwrstate == _Off:
            self._current_dcct = 0.0
        else:
            if self._opmode == _SlowRef:
                self._update_opmode_slowref()
            elif self._opmode == _FastRef:
                self._update_opmode_fastref()
            elif self._opmode == _WfmRef:
                self._update_opmode_wfmref()
            elif self._opmode == _SigGen:
                self._update_opmode_siggen()
            self._update_add_fluctuations()

    def _update_opmode_slowref(self):
        # slow reference setpoint mode
        self._current_dcct = self._current_ref

    def _update_opmode_fastref(self):
        # fast reference setpoints (FOFB)
        pass

    def _update_opmode_wfmref(self):
        # ramp driven by timing system signal
        pass

    def _update_opmode_siggen(self):
        # demagnetization curve, for example
        pass

    def _update_add_fluctuations(self):
        pass

    def __str__(self):
        st = '--- Controller ---\n'
        propty = 'pwrstate';     st +=   '{0:<20s}: {1}'.format(propty, _enumt.OffOnTyp[self.pwrstate])
        propty = 'opmode';       st += '\n{0:<20s}: {1}'.format(propty, _enumt.PSOpModeTyp[self.opmode])
        propty = 'current-ref';   st += '\n{0:<20s}: {1}'.format(propty, self._current_ref)
        propty = 'current-dcct';   st += '\n{0:<20s}: {1}'.format(propty, self._current_dcct)
        propty = 'timestamp-pwrstate'; st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_pwrstate))
        propty = 'timestamp-opmode';   st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_opmode))
        return st


class ControllerSim(Controller):
    """Simple Simulated Controller Class

    This subclass of Controller introduces simulated measurement fluctuations
    and OpModes other than SlowRef.
    """

    def __init__(self, IOC=None,
                       current_min=None,
                       current_max=None,
                       fluctuation_rms=0.0):
        super().__init__(IOC=IOC,
                         current_min=current_min,
                         current_max=current_max)
        self._fluctuation_rms = fluctuation_rms

    def _update_opmode_fastref(self):
        # fast reference setpoints (FOFB)
        self._current_dcct = self._current_min + _random.random()*(self._current_max - self._current_min)

    def _update_opmode_siggen(self):
        # demagnetization curve, for example
        ramp_fraction = ((_time.time() - self._timestamp_opmode)/10) % 1
        self._current_dcct = self._current_min + ramp_fraction*(self._current_max - self._current_min)

    def _update_add_fluctuations(self):
        self._current_dcct += 2*(_random.random()-0.5)*self._fluctuation_rms
