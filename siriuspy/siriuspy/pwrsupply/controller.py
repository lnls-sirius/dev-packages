
from siriuspy.csdevice.enumtypes import EnumTypes as _et
import random as _random
import time as _time
import uuid as _uuid
from siriuspy.util import get_timestamp as _get_timestamp
from .waveform import PSWaveForm as _PSWaveForm
from siriuspy.epics import SiriusPV as _SiriusPV

_Off     = _et.idx('OffOnTyp','Off')
_On      = _et.idx('OffOnTyp','On')
_SlowRef = _et.idx('PSOpModeTyp','SlowRef')
_FastRef = _et.idx('PSOpModeTyp','FastRef')
_WfmRef  = _et.idx('PSOpModeTyp','WfmRef')
_SigGen  = _et.idx('PSOpModeTyp','SigGen')


_connection_timeout = 0.05
_fluctuation_rms = 0.0
_wfm_nr_points = 2000


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
        if waveform is None: waveform = _PSWaveForm.wfm_constant(_wfm_nr_points)
        self._waveform = waveform
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
        self.update_state()
        return self._pwrstate

    @property
    def opmode(self):
        self.update_state()
        return self._opmode

    @IOC.setter
    def IOC(self, value):
        self._IOC = value

    @current.setter
    def current_ref(self, value):
        value = self._check_current_ref_limits(value)
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
        if value in tuple(range(len(_et.enums('PSOpModeTyp')))):
            self._opmode = value
        else:
            raise Exception('Invalid value!')
        self.update_state()

    def timing_trigger(self):
        if self._opmode == _WfmRef:
            self._current_dcct = self._waveform[self._waveform_step]
            self._waveform_step += 1
            if self._waveform_step >= self._waveform.nr_points:
                self._waveform_step = 0
            self.update_state()

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

    def _check_current_ref_limits(self, value):
        value = value if self._current_min is None else max(value,self._current_min)
        value = value if self._current_max is None else min(value,self._current_max)
        return value

    def __str__(self):
        st = '--- Controller ---\n'
        propty = 'pwrstate';     st +=   '{0:<20s}: {1}'.format(propty, _et.key('OffOnTyp', self._pwrstate))
        propty = 'opmode';       st += '\n{0:<20s}: {1}'.format(propty, _et.key('PSOpModeTyp', self._opmode))
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

    def __init__(self, fluctuation_rms=_fluctuation_rms,
                       **kwargs):
        super().__init__(**kwargs)
        self._fluctuation_rms = fluctuation_rms

    def _update_opmode_fastref(self):
        # fast reference setpoints (FOFB)
        if self._current_min is not None and self._current_max is not None:
            self._current_dcct = self._current_min + _random.random()*(self._current_max - self._current_min)

    def _update_opmode_siggen(self):
        # demagnetization curve, for example
        if self._current_min is not None and self._current_max is not None:
            ramp_fraction = ((_time.time() - self._timestamp_opmode)/20) % 1
            self._current_dcct = self._current_min + ramp_fraction*(self._current_max - self._current_min)

    def _update_add_fluctuations(self):
        self._current_dcct += 2*(_random.random()-0.5)*self._fluctuation_rms


class ControllerEpicsPS(ControllerSim):

    def __init__(self, prefix,
                       ps_name,
                       connection_timeout = _connection_timeout,
                       callback = None,
                       **kwargs):
        super().__init__(**kwargs)

        self._uuid = _uuid.uuid4()  # unique ID for the class object
        self._prefix = prefix
        self._ps_name = ps_name
        self._connection_timeout = connection_timeout
        self._callbacks = {} if callback is None else {callback}
        self._create_pvs()
        self.update_state()

    @property
    def prefix(self):
        return self.prefix

    @property
    def ps_name(self):
        return self._ps_name

    @property
    def current_ref(self):
        return super().current_ref

    @current_ref.setter
    def current_ref(self, value):
        value = self._check_current_ref_limits(value)
        self._pvs['Current-SP'].value = value
        # invocation of _pvs_callback will update internal state of controller

    @property
    def pwrstate(self): # necessary for setter
        return super().pwrstate

    @pwrstate.setter
    def pwrstate(self, value):
        self._pvs['PwrState-Sel'].value = value
        # invocation of _pvs_callback will update internal state of controller

    @property # necessary for setter
    def opmode(self):
        return super().opmode

    @opmode.setter
    def opmode(self, value):
        self._pvs['OpMode-Sel'].value = value
        # invocation of _pvs_callback will update internal state of controller

    def add_callback(self, callback, index):
        self._callbacks[index] = callback

    def _create_pvs(self):
        self._pvs = {}
        pvname = self._prefix + self._ps_name
        self._pvs['PwrState-Sel'] = _SiriusPV(pvname + ':PwrState-Sel', connection_timeout=self._connection_timeout)
        self._pvs['PwrState-Sts'] = _SiriusPV(pvname + ':PwrState-Sts', callback=self._pvs_callback, connection_timeout=self._connection_timeout)
        self._pvs['OpMode-Sel'] = _SiriusPV(pvname + ':OpMode-Sel', connection_timeout=self._connection_timeout)
        self._pvs['OpMode-Sts'] = _SiriusPV(pvname + ':OpMode-Sts', callback=self._pvs_callback, connection_timeout=self._connection_timeout)
        self._pvs['Current-SP'] = _SiriusPV(pvname + ':Current-SP', callback=self._pvs_callback, connection_timeout=self._connection_timeout)
        self._pvs['Current-RB'] = _SiriusPV(pvname + ':Current-RB', callback=self._pvs_callback, connection_timeout=self._connection_timeout)

    def _pvs_callback(self, pvname, value, **kwargs):
        #print('conrtoller callback', pvname, value)
        if 'PwrState-Sts' in pvname:
            self._pwrstate = value
        elif 'OpMode-Sts' in pvname:
            self._opmode = value
        elif 'Current-RB' in pvname:
            self._current_dcct = value
        elif 'Current-SP' in pvname:
            self._current_ref = value
        self.update_state()
        for index, callback in self._callbacks.items():
            callback(pvname, value, **kwargs)
