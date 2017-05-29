import math as _math

class PSCycGenerator:

    def __init__(self, interval, cycgen_type=None, **kwargs):
        self._interval = interval
        self._type = cycgen_type
        self._parameters = {}
        if cycgen_type == 'exp_cos':
            self._parameters['period'] = kwargs['period']
            self._parameters['tau'] = kwargs['tau']
            self._parameters['current_amp'] = kwargs['current_amp']

    def out_of_range(self, dt):
        return dt > self._parameters['interval']

    def get_current(self, dt):
        if self.out_of_range(dt): return 0.0
        if self._type is None:
            return 0.0
        elif self._type == 'exp_cos':
            parms = self._parameters
            A,tau,period = parms['current_amp'],parms['tau'],parms['paeriod']
            exp,cos,pi = _math.exp,_math.cos,_math.pi
            value = A * exp(-dt/tau) * cos(2*pi*dt/period)
            return value
