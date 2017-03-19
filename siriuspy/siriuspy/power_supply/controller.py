
from siriuspy.cs_device.enumtypes import enum_types as _enumt
import random as _random


_Off     = _enumt.OffOnTyp.index('Off')
_On      = _enumt.OffOnTyp.index('On')
_SlowRef = _enumt.PSOpModeTyp.index('SlowRef')
_FastRef = _enumt.PSOpModeTyp.index('FastRef')
_WfmRef  = _enumt.PSOpModeTyp.index('WfmRef')
_SigGen  = _enumt.PSOpModeTyp.index('SigGen')


_meas_rms = 0.000 # [A]


class Controller:
    """Base Controller Class

    This is a simple power supply controller that responds immediatelly
    to setpoints.

    all enum properties (pwrstate, opmode, etc) are set in ints.
    """

    def __init__(self, IOC=None,
                       current_min=None,
                       current_max=None):

        self._IOC = IOC
        # --- default initial controller state ---
        self._pwrstate = _Off
        self._opmode   = _SlowRef
        self._current_sp   = 0.0  # PS feedback current setpoint
        self._current_rb   = 0.0  # PS feedback current readback
        self._current_meas = 0.0  # PS feedback current measurement
        self._current_min = current_min
        self._current_max = current_max

    @property
    def IOC(self):
        return self._IOC

    @property
    def current(self):
        self.update_state()
        return self._current_meas

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
        self._current_sp = value # Should it happen even with PS off?
        self.update_state()

    @pwrstate.setter
    def pwrstate(self, value):
        if value == _Off:
            self._pwrstate = _Off
        elif value == _On:
            self._pwrstate = _On
        else:
            raise Exception('Invalid value!')
        self.update_state()

    @opmode.setter
    def opmode(self, value):
        if value in (_SlowRef, _FastRef, _WfmRef, _SigGen):
            self._opmode = value
        else:
            raise Exception('Invalid value!')
        self.update_state()

    def update_state(self):
        if self._pwrstate == _Off:
            self._current_rb   = 0.0
            self._current_meas = 0.0
        else:
            if self._opmode == _SlowRef:
                self._current_rb = self._current_sp
                self._current_meas = self._current_rb
                self._update_measurement_with_fluctuations()
            else:
                self._current_rb = self._current_min + _random.random()*(self._current_max - self._current_min)        
                self._update_measurement_with_fluctuations()

    def _update_measurement_with_fluctuations(self):
        #self._current_meas += 2*(_random.random()-0.5)*self._current_meas_rms
        pass

    def __str__(self):
        st = '--- Controller ---\n'
        propty = 'pwrstate';     st +=   '{0:<20s}: {1}'.format(propty, _enumt.OffOnTyp[self.pwrstate])
        propty = 'opmode';       st += '\n{0:<20s}: {1}'.format(propty, _enumt.PSOpModeTyp[self.opmode])
        propty = 'current-sp';   st += '\n{0:<20s}: {1}'.format(propty, self._current_sp)
        propty = 'current-rb';   st += '\n{0:<20s}: {1}'.format(propty, self._current_rb)
        propty = 'current-meas'; st += '\n{0:<20s}: {1}'.format(propty, self._current_meas)
        return st


class SimulController(Controller):
    """Simple Simulated Controller Class

    This subclass of Controller introduces measurement errors.
    """

    def __init__(self, IOC=None,
                       current_min=None,
                       current_max=None,
                       meas_rms=_meas_rms):

        self._IOC = IOC
        self._current_meas_rms = meas_rms
        # --- default initial controller state ---
        self._current_sp = 0.0
        self._current_rb = 0.0
        self._pwrstate = _Off
        self._opmode = _SlowRef
        self._current_min = current_min
        self._current_max = current_max

    @property
    def IOC(self):
        return self._IOC

    @property
    def current(self):
        self.update_state()
        return self._current_meas

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
        self._current_sp = value # Should it happen even with PS off?
        if self._pwrstate == _On:
            if self._opmode == _SlowRef:
                self._current_rb = self._current_sp

    @pwrstate.setter
    def pwrstate(self, value):
        if value == _Off:
            self._pwrstate = _Off
            self._current_rb = 0.0
            self._current_meas = 0.0
        elif value == _On:
            self._pwrstate = _On
            if self._opmode == _SlowRef:
                self._current_rb = self._current_sp
        else:
            raise Exception('Invalid value!')
        self.update_state()

    @opmode.setter
    def opmode(self, value):
        if value == _SlowRef:
            self._opmode = value
            if self._pwrstate == _On:
                self._current_rb = self._current_sp
        elif value in (_FastRef, _WfmRef, _SigGen):
            self._opmode = value
        else:
            raise Exception('Invalid value!')
        self.update_state()

    def update_state(self):
        if self._pwrstate == _Off:
            self.current_meas = self._current_rb
        elif self._opmode == _SlowRef:
            self._current_meas = self._current_rb + 2*(_random.random()-0.5)*self._current_meas_rms
        else:
            self._current_rb = self._current_min + _random.random()*(self._current_max - self._current_min)
            self._current_meas = self._current_rb + 2*(_random.random()-0.5)*self._current_meas_rms

    def __str__(self):
        st = '--- Controller ---\n'
        propty = 'pwrstate';     st +=   '{0:<20s}: {1}'.format(propty, _enumt.OffOnTyp[self.pwrstate])
        propty = 'opmode';       st += '\n{0:<20s}: {1}'.format(propty, _enumt.PSOpModeTyp[self.opmode])
        propty = 'current-sp';   st += '\n{0:<20s}: {1}'.format(propty, self._current_sp)
        propty = 'current-rb';   st += '\n{0:<20s}: {1}'.format(propty, self._current_rb)
        propty = 'current-meas'; st += '\n{0:<20s}: {1}'.format(propty, self._current_meas)
        return st
