import math as _math

# Make it more general by implementing a base class that defines an abstract interface!

class PSCycGenerator:

    def __init__(self, interval, cycgen_type=None, **kwargs):
        self._interval = interval
        self._type = cycgen_type
        self._parameters = {}
        if cycgen_type == 'exp_cos':
            self._parameters['period'] = kwargs['period']
            self._parameters['tau'] = kwargs['tau']
            self._parameters['amplitude'] = kwargs['amplitude']
        elif cycgen_type == 'triangle':
            self._parameters['period'] = kwargs['period']
            self._parameters['amplitude'] = kwargs['amplitude']

    def out_of_range(self, dt):
        return dt > self._interval

    def get_signal(self, dt):
        if self.out_of_range(dt): return 0.0
        if self._type is None:
            return 0.0
        elif self._type == 'exp_cos':
            parms = self._parameters
            A,tau,period = parms['amplitude'],parms['tau'],parms['period']
            exp,cos,pi = _math.exp,_math.cos,_math.pi
            value = A * exp(-dt/tau) * cos(2*pi*dt/period)
            return value
        elif self._type == 'triangle':
            parms = self._parameters
            A,a = parms['amplitude'],parms['period']/2.0
            tmp = _math.floor(dt/a+1.0/2.0)
            value = A * abs(2*(dt/a-tmp))
            return value
