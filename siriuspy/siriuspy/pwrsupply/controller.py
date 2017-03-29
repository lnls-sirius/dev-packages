
from siriuspy.csdevice.enumtypes import EnumTypes as _et
import random as _random
import time as _time
import uuid as _uuid
import math as _math
from siriuspy.util import get_timestamp as _get_timestamp
from .waveform import PSWaveForm as _PSWaveForm
from siriuspy.epics import SiriusPV as _SiriusPV
from abc import abstractmethod as _abstractmethod
from abc import abstractproperty as _abstractproperty

from epics import PV as _PV


_Off     = _et.idx('OffOnTyp','Off')
_On      = _et.idx('OffOnTyp','On')
_SlowRef = _et.idx('PSOpModeTyp','SlowRef')
_FastRef = _et.idx('PSOpModeTyp','FastRef')
_WfmRef  = _et.idx('PSOpModeTyp','WfmRef')
_SigGen  = _et.idx('PSOpModeTyp','SigGen')


_connection_timeout = 0.05
_error_std = 0.0

class Controller:

    def __init__(self):
        pass

    def __str__(self):
        st = '--- Controller ---\n'
        propty = 'pwrstate_sel';        st +=   '{0:<20s}: {1}'.format(propty, _et.key('OffOnTyp', self.pwrstate_sel))
        propty = 'pwrstate_sts';        st += '\n{0:<20s}: {1}'.format(propty, _et.key('OffOnTyp', self.pwrstate_sts))
        propty = 'opmode_sel';          st += '\n{0:<20s}: {1}'.format(propty, _et.key('PSOpModeTyp', self.opmode_sel))
        propty = 'opmode_sts';          st += '\n{0:<20s}: {1}'.format(propty, _et.key('PSOpModeTyp', self.opmode_sts))
        propty = 'current_sp';          st += '\n{0:<20s}: {1}'.format(propty, self.current_sp)
        propty = 'current_rb';          st += '\n{0:<20s}: {1}'.format(propty, self.current_rb)
        propty = '_current_min';        st += '\n{0:<20s}: {1}'.format(propty, self._current_min)
        propty = '_current_max';        st += '\n{0:<20s}: {1}'.format(propty, self._current_max)
        try:
            propty = '_timestamp_pwrstate'; st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_pwrstate))
            propty = '_timestamp_opmode';   st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_opmode))
        except:
            pass

        return st

    def _check_current_ref_limits(self, value):
        value = value if self._current_min is None else max(value,self._current_min)
        value = value if self._current_max is None else min(value,self._current_max)
        return value

    def set_callback(self, callback):
        self._callback = callback

class ControllerSim(Controller):

    def __init__(self, current_min=None,     # mininum current setpoint value
                       current_max=None,     # maximum current setpoint value
                       waveform=None,        # wafeform used in WfmRef mode
                       error_std=_error_std,
                       callback=None,
                       ):

        self._current_min = current_min
        self._current_max = current_max
        self._error_std = error_std
        # waveform
        if waveform is None:
            waveform = _PSWaveForm.wfm_constant(2000,value=0.0)
        self._waveform = waveform
        self._waveform_step = 0
        # timestamps
        now = _time.time()
        self._timestamp_pwrstate = now
        self._timestamp_opmode   = now
        # internal state
        self._pwrstate = _Off
        self._opmode = _SlowRef
        self._current_sp = 0.0
        self._current_rb = 0.0
        # callback functions
        self._callback = callback

    @property
    def pwrstate_sel(self):
        return self._pwrstate

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        if value not in _et.values('OffOnTyp'): raise Exception('Invalid value of pwrstate_sel')
        if value != self._pwrstate:
            self._timestamp_pwrstate = _time.time()
            self._pwrstate = value
            self._run_callback(pvname='PwrState-Sel')
            self.update_state()

    @property
    def pwrstate_sts(self):
        return self._pwrstate

    @property
    def opmode_sel(self):
        return self._opmode

    @opmode_sel.setter
    def opmode_sel(self, value):
        if value not in _et.values('PSOpModeTyp'): raise Exception('Invalid value of opmode_sel')
        if value != self._opmode:
            self._timestamp_opmode = _time.time()
            self._opmode = value
            self._mycallback(pvname='OpMode-Sel')
            self.update_state()

    @property
    def opmode_sts(self):
        return self._opmode

    @property
    def current_sp(self):
        return self._current_sp

    @current_sp.setter
    def current_sp(self, value):
        value = self._check_current_ref_limits(value)
        if value != self._current_sp:
            self._current_sp = value
            self._run_callback(pvname='Current-SP')
            self.update_state()

    @property
    def current_rb(self):
        return self._current_rb

    def _mycallback(self, pvname):
        if self._callback is None:
            return
        elif pvname in ('PwrState-Sel','PwrState-Sts'):
            self._callback(pvname='PwrState-Sel', value=self._pwrstate)
            self._callback(pvname='PwrState-Sts', value=self._pwrstate)
        elif pvname in ('OpMode-Sel','OpMode-Sts'):
            self._callback(pvname='OpMode-Sel', value=self._opmode)
            self._callback(pvname='OpMode-Sts', value=self._opmode)
        elif pvname == 'Current-SP':
            self._callback(pvname='Current-SP', value=self._current_sp)
        elif pvname == 'Current-RB':
            self._callback(pvname='Current-RB', value=self._current_rb)

    def _update_opmode_slowref(self):
        self._current_rb = _random.gauss(self._current_sp, self._error_std)
        self._run_callback(pvname='Current-RB')

    def _update_opmode_fastref(self):
        self._current_rb = _random.unform(self.current_min, self.current_max)
        self._mycallback(pvname='Current-RB')

    def _update_opmode_wfmref(self):
        pass

    def _update_opmode_siggen(self):
        if self._opmode == _SigGen:
            dt = (_time.time() - self._timestamp_opmode) % 20
            value = self._current_min + (self._current_max-self._current_min) * _math.exp(-dt/10.0) * _math.cos(2*_math.pi*dt/1.0) ** 2
            self._current_rb = _random.gauss(value, self._error_std)
            self._run_callback(pvname='Current-RB')

    def timing_trigger(self):
        if self._opmode == _WfmRef:
            ramp_value = self._waveform_step = (self._waveform_step + 1) % self._waveform.nr_points
            self._current_rb = _random.gauss(ramp_value, self._error_std)
            self._mycallback(pvname='Current-RB')

    def update_state(self):
        """Method that update controller state. It implements most of the
        controller logic regarding the interdependency of the controller
        properties."""
        if self.pwrstate_sts == _Off:
            if self._current_rb != 0.0:
                self._current_rb = 0.0
                self._mycallback(pvname='Current-RB')
        elif self.pwrstate_sts == _On:
            opmode = self.opmode_sts
            if opmode == _SlowRef:
                self._update_opmode_slowref()
            elif opmode == _FastRef:
                self._update_opmode_fastref()
            elif opmode == _WfmRef:
                self._update_opmode_wfmref()
            elif opmode == _SigGen:
                self._update_opmode_siggen()
            else:
                raise Exception('Invalid controller OpMode-Sts!')
        else:
            raise Exception('Invalid controller PwrState-Sts!')

class ControllerEpics(Controller):

    def __init__(self, ps_name,           # power supply name
                       current_min=None,  # mininum current setpoint value
                       current_max=None,  # maximum current setpoint value
                       callback=None,
                       connection_timeout=_connection_timeout
                       ):

        self._ps_name = ps_name
        self._current_min = current_min
        self._current_max = current_max
        self._callback = callback
        self._connection_timeout = connection_timeout
        self._create_epics_pvs()

    def _create_epics_pvs(self):
        self._pvs = {}
        pv = self._ps_name
        self._pvs['PwrState-Sel'] = _PV(pv + ':PwrState-Sel', connection_timeout=self._connection_timeout)
        self._pvs['PwrState-Sts'] = _PV(pv + ':PwrState-Sts', connection_timeout=self._connection_timeout)
        self._pvs['OpMode-Sel']   = _PV(pv + ':OpMode-Sel', connection_timeout=self._connection_timeout)
        self._pvs['OpMode-Sts']   = _PV(pv + ':OpMode-Sts', connection_timeout=self._connection_timeout)
        self._pvs['Current-SP']   = _PV(pv + ':Current-SP', connection_timeout=self._connection_timeout)
        self._pvs['Current-RB']   = _PV(pv + ':Current-RB', connection_timeout=self._connection_timeout)
        self._pvs['PwrState-Sel'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['PwrState-Sts'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['OpMode-Sel'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['OpMode-Sts'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Current-SP'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Current-RB'].wait_for_connection(timeout=self._connection_timeout)
        # add callback
        uuid = _uuid.uuid4()
        self._pvs['PwrState-Sel'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['PwrState-Sts'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['OpMode-Sel'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['OpMode-Sts'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Current-SP'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Current-RB'].add_callback(callback=self._mycallback, index=uuid)

    def _mycallback(self, pvname, value, **kwargs):
        if self._callback is None:
            return
        else:
            self._callback(pvname=pvname, value=value, **kwargs)

    @property
    def pwrstate_sel(self):
        return self._pvs['PwrState-Sel'].get(timeout=self._connection_timeout)

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        if value not in _et.values('OffOnTyp'): raise Exception('Invalid value of pwrstate_sel')
        if value != self.pwrstate_sts:
            self._pvs['PwrState-Sel'].value = value
            self.update_state()

    @property
    def pwrstate_sts(self):
        return self._pvs['PwrState-Sts'].get(timeout=self._connection_timeout)

    @property
    def opmode_sel(self):
        return self._pvs['OpMode-Sel'].get(timeout=self._connection_timeout)

    @opmode_sel.setter
    def opmode_sel(self, value):
        if value not in _et.values('PSOpModeTyp'): raise Exception('Invalid value of opmode_sel')
        if value != self.opmode_sts:
            self._pvs['OpMode-Sel'].value = value
            self.update_state()

    @property
    def opmode_sts(self):
        return self._pvs['OpMode-Sts'].get(timeout=self._connection_timeout)

    @property
    def current_sp(self):
        return self._pvs['Current-SP'].get(timeout=self._connection_timeout)

    @current_sp.setter
    def current_sp(self, value):
        value = self._check_current_ref_limits(value)
        if value != self.current_sp:
            self._pvs['Current-SP'].value = value
            self.update_state()

    @property
    def current_rb(self):
        return self._pvs['Current-RB'].get(timeout=self._connection_timeout)

    def _update_opmode_slowref(self):
        pass

    def _update_opmode_fastref(self):
        pass

    def _update_opmode_wfmref(self):
        pass

    def _update_opmode_siggen(self):
        pass

    def timing_trigger(self):
        pass

    def update_state(self):
        """Method that update controller state. It implements most of the
        controller logic regarding the interdependency of the controller
        properties."""
        pass

class ControllerPyaccel(Controller):
    """Controller PyEpics model.

    (pending!)
    This pure virtual class implements basic functionality of a controller that
    gets its internal state from an accelerator Pyaccel model. The class is
    supposed to be subclasses elsewhere.
    """
    pass
