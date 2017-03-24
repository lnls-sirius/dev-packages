
from siriuspy.csdevice.enumtypes import EnumTypes as _et
import random as _random
import time as _time
import uuid as _uuid
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
_fluctuation_rms = 0.0


class Controller:

    def __init__(self, current_min=None, # mininum current setpoint value
                       current_max=None, # maximum current setpoint value
                       waveform=None,    # wafeform used in WfmRef mode
                       callback=None,    # callback function to signal
                       index=None):      # callback index in dictionary

        """Controller Class.

        This is a pure virtual class that implements the logic of controllers used by
        power supply IOCs. It can be subclassed to either a controller state
        simulator or to a front-end object that may interact bellow with another
        IOC (such as VACA), or with a hardware controller.

        The idea with this class is to concentrate most of the logic of the
        controller signals within this pure virtual super class, thus minimizing
        as much as possible algorithm replication and code maintenance.

        A broad range of controller types can be implemented as subclasses due
        to the fact that many of the methods that may require specific actions
        are implemented as virtual methods.
        """

        # controller limits
        self._current_min = current_min
        self._current_max = current_max
        # waveform
        if waveform is None:
            waveform = _PSWaveForm.wfm_constant(2000,value=0.0)
        self._waveform = waveform
        self._waveform_step = 0
        # timestamps
        now = _time.time()
        self._timestamp_pwrstate = now
        self._timestamp_opmode   = now
        # callback function
        self._callbacks = {}
        if callback is not None:
            if index is None: index = _uuid.uuid4()
            self._callbacks[index] = callback
        self.update_state()

    # --- pure virtual properties and methods ---

    @_abstractmethod
    def _getter_pwrstate_sel(self):
        """Virtual method that retrieves the state of PwrState-Sel."""
        pass

    @_abstractmethod
    def _setter_pwrstate_sel(self, value):
        """Virtual method that sets the state of PwrState-Sel.
        It returns True if state has changed."""
        pass

    @_abstractproperty
    def pwrstate_sts(self):
        """Virtual property that returns state of PwrState-Sts."""
        pass

    @_abstractmethod
    def _getter_opmode_sel(self):
        """Virtual method that retrieves the state of OpMode-Sel."""
        pass

    @_abstractmethod
    def _setter_opmode_sel(self, value):
        """Virtual method that sets the state of OpMode-Sel.
        It returns True is state has changed."""
        pass

    @_abstractproperty
    def opmode_sts(self):
        """Virtual property that returns state of OpMode-Sts."""
        pass

    @_abstractmethod
    def _getter_current_sp(self):
        """Virtual method that returns state of Current-SP."""
        pass

    @_abstractmethod
    def _setter_current_sp(self, value):
        """Virtual method that sets the state of Current-SP.
        It returns True is state has changed."""
        pass

    @_abstractproperty
    def current_rb(self):
        """Virtual property that retrieves the state of Current-RB."""
        pass

    @_abstractmethod
    def _setter_current_rb(self, value):
        """Virtual method that sets the state of Current-RB.
        It returns True is state is changed.
        This method is used in the internal logic of the controller.
        """
        pass

    # --- virtual methods used to update the state of the controller ---

    def _update_opmode_slowref(self):
        pass

    def _update_opmode_fastref(self):
        pass

    def _update_opmode_wfmref(self):
        pass

    def _update_opmode_siggen(self):
        pass

    def _add_errors():
        """Virtual method that can be used to add fluctuations to readout
        properties of the controller."""
        pass

    def _process_callbacks(self, propty, value, **kwargs):
        """This virtual method is used to signal up registered callback functions
        when the state of the controller has changed. It is invoked at the end
        of the update_state method."""
        pass

    # --- super class setters, properties and methods that should
    #     implement most of the logic of the controller

    @property
    def pwrstate_sel(self):
        """Return the state of PwrState-Sel."""
        return self.__getter_pwrstate_sel()
    def __getter_pwrstate_sel(self):
        return self._getter_pwrstate_sel()

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        """Set state of PwrState-Sel and update state of controller."""
        self._timestamp_pwrstate = _time.time()
        if self.__setter_pwrstate_sel(value):
            self.update_state()
    def __setter_pwrstate_sel(self, value):
        return self._setter_pwrstate_sel(value)

    @property
    def opmode_sel(self):
        """Return the state of POpMode-Sel."""
        return self.__getter_opmode_sel()
    def __getter_opmode_sel(self):
        return self._getter_opmode_sel()

    @opmode_sel.setter
    def opmode_sel(self, value):
        """Set state of PwrState-Sel and update state of controller."""
        self._timestamp_opmode = _time.time()
        if self.__setter_opmode_sel(value):
            self.update_state()
    def __setter_opmode_sel(self, value):
        return self._setter_opmode_sel(value)

    @property
    def current_sp(self):
        """Return the state of Current-SP."""
        return self.__getter_current_sp()
    def __getter_current_sp(self):
        return self._getter_current_sp()

    @current_sp.setter
    def current_sp(self, value):
        """Set state of PwrState-Sel and update state of controller."""
        value = self._check_current_ref_limits(value)
        if self.__setter_current_sp(value):
            self.update_state()
    def __setter_current_sp(self, value):
        return self._setter_current_sp(value)

    def _check_current_ref_limits(self, value):
        value = value if self._current_min is None else max(value,self._current_min)
        value = value if self._current_max is None else min(value,self._current_max)
        return value

    def update_state(self):
        """Method that update controller state. It implements most of the
        controller logic regarding the interdependency of the controller
        properties."""
        if self.pwrstate_sts == _Off:
            self._setter_current_rb(0.0)
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
            self._add_errors()
        else:
            raise Exception('Invalid controller PwrState-Sts!')
        self._process_callbacks(propty=None,value=None)

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
        propty = '_timestamp_pwrstate'; st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_pwrstate))
        propty = '_timestamp_opmode';   st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_opmode))
        return st

class ControllerError(Controller):
    """Controller Error Class.

    Pure virtual class of controller with added gaussian error in the Current-RB
    property.
    """
    def __init__(self, error_std=0.0, **kwargs):

        self._error_std = error_std
        # At last, after state parameters within the subclass are defined,
        # super class __init__ can be invoked.
        super().__init__(**kwargs)

    def _add_errors(self):
        self._setter_current_rb(_random.gauss(self.current_rb,self._error_std))

class ControllerSim(ControllerError):
    """Controller Simulation Class.

    This controller subclass derives from ControllerError and implements a
    controller simulation where its state is stored as class attributes.
    """
    def __init__(self, fluctuation_rms=0, **kwargs):

        # define initial state of controller
        self._pwrstate = _Off
        self._opmode = _SlowRef
        self._current_sp = 0.0
        self._current_rb = 0.0

        self._fluctuation_rms = fluctuation_rms
        # At last, after state parameters within the subclass are defined,
        # super class __init__ can be invoked.
        super().__init__(**kwargs)

    # --- pwrstate_sel getter ---
    def _getter_pwrstate_sel(self):
        return self._pwrstate
    # --- pwrstate_sel setter ---
    def _setter_pwrstate_sel(self, value):
        """Return True if property has changed."""
        if value == self._pwrstate: return False
        self._pwrstate = value
        return True


    # --- pwrstate_sel getter ---
    @property
    def pwrstate_sts(self):
        return self._pwrstate

    # --- opmode_sel getter ---
    def _getter_opmode_sel(self):
        return self._opmode
    # --- opmode_sel setter ---
    def _setter_opmode_sel(self, value):
        """Return True if property has changed."""
        if value == self._opmode: return False
        self._opmode = value
        return True
    # --- opmode_sel getter ---
    @property
    def opmode_sts(self):
        return self._opmode

    # --- current_sp getter ---
    def _getter_current_sp(self):
        return self._current_sp
    # --- current_sp setter ---
    def _setter_current_sp(self, value):
        """Return True if property has changed."""
        if value == self._current_sp: return False
        self._current_sp = value
        return True
    # --- current_sp getter ---
    @property
    def current_rb(self):
        return self._current_rb

    # --- current_rb getter ---
    @property
    def current_rb(self):
        return self._current_rb
    def _setter_current_rb(self, value):
        self._current_rb = value

    def _update_opmode_slowref(self):
        self._current_rb = self._current_sp

    # def _add_errors(self):
    #     self._current_rb += 2*(_random.random()-0.5)*self._fluctuation_rms

    def _process_callbacks(self, propty, values, **kwargs):
        for index, callback in self._callbacks.items():
            callback('PwrState-Sel', self.pwrstate_sel)
            callback('PwrState-Sts', self.pwrstate_sts)
            callback('OpMode-Sel', self.opmode_sel)
            callback('OpMode-Sts', self.opmode_sts)
            callback('Current-SP', self.current_sp)
            callback('Current-RB', self.current_rb)

class ControllerEpics(ControllerError):
    """Controller Epics Class.
    """

    def __init__(self, ps_name,
                       connection_timeout=_connection_timeout,
                       **kwargs):

        self._ps_name = ps_name
        self._uuid = _uuid.uuid4()
        self._connection_timeout = connection_timeout
        self._current_rb = 0.0
        self._create_epics_pvs()
        super().__init__(**kwargs)


    @property
    def ps_name(self):
        return self._ps_name

    def _connected(self):
        if not self._pvs['PwrState-Sel'].connected: return False
        if not self._pvs['PwrState-Sts'].connected: return False
        if not self._pvs['OpMode-Sel'].connected: return False
        if not self._pvs['OpMode-Sts'].connected: return False
        if not self._pvs['Current-SP'].connected: return False
        if not self._pvs['Current-RB'].connected: return False
        return True


    def update_state(self):
        if not self._connected(): return
        super().update_state()
        
    def _process_callbacks(self, propty, value, **kwargs):
        """This virtual method is used to signal up registered callback functions
        when the state of the controller has changed. It is invoked at the end
        of the update_state method."""
        for index, callback in self._callbacks.items():
            callback('PwrState-Sel', self.pwrstate_sel)
            callback('PwrState-Sts', self.pwrstate_sts)
            callback('OpMode-Sel', self.opmode_sel)
            callback('OpMode-Sts', self.opmode_sts)
            callback('Current-SP', self.current_sp)
            callback('Current-RB', self.current_rb)

    def _callback(self, propty, value, **kwargs):
        self._process_callbacks(propty=propty, value=value)

    def _create_epics_pvs(self):
        self._pvs = {}
        pvname = self._ps_name
        self._pvs['PwrState-Sel'] = _PV(pvname + ':PwrState-Sel', connection_timeout=self._connection_timeout)
        self._pvs['PwrState-Sts'] = _PV(pvname + ':PwrState-Sts', callback=self._callback, connection_timeout=self._connection_timeout)
        self._pvs['OpMode-Sel']   = _PV(pvname + ':OpMode-Sel', connection_timeout=self._connection_timeout)
        self._pvs['OpMode-Sts']   = _PV(pvname + ':OpMode-Sts', callback=self._callback, connection_timeout=self._connection_timeout)
        self._pvs['Current-SP']   = _PV(pvname + ':Current-SP', callback=self._callback, connection_timeout=self._connection_timeout)
        self._pvs['Current-RB']   = _PV(pvname + ':Current-RB', callback=self._callback, connection_timeout=self._connection_timeout)


    @_abstractmethod
    def _getter_pwrstate_sel(self):
        """Virtual method that retrieves the state of PwrState-Sel."""
        return self._pvs['PwrState-Sel'].value

    @_abstractmethod
    def _setter_pwrstate_sel(self, value):
        """Virtual method that sets the state of PwrState-Sel.
        It returns True if state has changed."""
        prev_value = self._pvs['PwrState-Sel'].value
        if prev_value == value: return False
        self._pvs['PwrState-Sel'].value = value
        return True

    @_abstractproperty
    def pwrstate_sts(self):
        """Virtual property that returns state of PwrState-Sts."""
        return self._pvs['PwrState-Sts'].value

    @_abstractmethod
    def _getter_opmode_sel(self):
        """Virtual method that retrieves the state of OpMode-Sel."""
        return self._pvs['OpMode-Sel'].value

    @_abstractmethod
    def _setter_opmode_sel(self, value):
        """Virtual method that sets the state of OpMode-Sel.
        It returns True is state has changed."""
        prev_value = self._pvs['OpMode-Sel'].value
        if prev_value == value: return False
        self._pvs['OpMode-Sel'].value = value
        return True

    @_abstractproperty
    def opmode_sts(self):
        """Virtual property that returns state of OpMode-Sts."""
        return self._pvs['OpMode-Sts'].value

    @_abstractmethod
    def _getter_current_sp(self):
        """Virtual method that returns state of Current-SP."""
        return self._pvs['Current-SP'].value

    @_abstractmethod
    def _setter_current_sp(self, value):
        """Virtual method that sets the state of Current-SP.
        It returns True is state has changed."""
        prev_value = self._pvs['Current-SP'].value
        if prev_value == value: return False
        self._pvs['Current-SP'].value = value
        return True

    @_abstractproperty
    def current_rb(self):
        """Virtual property that retrieves the state of Current-RB."""
        return self._current_rb

    @_abstractmethod
    def _setter_current_rb(self, value):
        """Virtual method that sets the state of Current-RB.
        It returns True is state is changed.
        This method is used in the internal logic of the controller.
        """
        self._current_rb = value

    # --- virtual methods used to update the state of the controller ---

    def _update_opmode_slowref(self):
        self._current_rb = self.current_sp

    def _update_opmode_fastref(self):
        pass

    def _update_opmode_wfmref(self):
        pass

    def _update_opmode_siggen(self):
        pass



class ControllerPyaccel(Controller):
    """Controller PyEpics model.

    (pending!)
    This pure virtual class implements basic functionality of a controller that
    gets its internal state from an accelerator Pyaccel model. The class is
    supposed to be subclasses elsewhere.
    """
    pass


# class Ctrller:
#     """Base Controller Class
#
#     This is a simple power supply controller that responds immediatelly
#     to setpoints.
#
#     all enum properties (pwrstate, opmode, etc) are set in ints.
#     """
#
#     def __init__(self, current_min=None, current_max=None, waveform=None):
#
#         # --- default initial controller state ---
#         self._current_min = current_min
#         self._current_max = current_max
#         if waveform is None: waveform = _PSWaveForm.wfm_constant(_wfm_nr_points)
#         self._waveform = waveform
#         self._waveform_step = 0
#         now = _time.time()
#         self._timestamp_pwrstate = now
#         self._timestamp_opmode   = now
#
#
#     @property
#     def pwrstate_sel(self):
#         return self.__getter_pwrstate_sel()
#
#     @pwrstate_sel.setter
#     def pwrstate_sel(self, value):
#         self._timestamp_pwrstate = _time.time()
#         self.__setter_pwrstate_sel(value)
#         self._update_state()
#
#     def __getter_pwrstate_sel(self):
#         return self._getter_pwrstate_sel()
#     def _getter_pwrstate_sel(self):
#         raise NotImplementedError
#
#     def __setter_pwrstate_sel(self):
#         self._setter_pwrstate_sel()
#     def _setter_pwrstate_sel(self, value):
#         raise NotImplementedError
#
#
#
#
#     @property
#     def pwrstate_sts(self):
#         raise NotImplementedError
#
#     @property
#     def opmode_sts(self):
#         raise NotImplementedError
#
#     def _getter_opmode_sel(self):
#         raise NotImplementedError
#
#     def _setter_opmode_sel(self, value):
#         raise NotImplementedError
#
#     @property
#     def current_rb(self):
#         raise NotImplementedError
#
#     def _getter_current_sp(self):
#         raise NotImplementedError
#
#     def _setter_current_sp(self, value):
#         raise NotImplementedError
#
#
#     @property
#     def opmode_sel(self):
#         return self.__getter_opmode_sel()
#     @opmode_sel.setter
#     def opmode_sel(self, value):
#         self._timestamp_opmode = _time.time()
#         self.__setter_opmode_sel(value)
#         self._update_state()
#     def __getter_opmode_sel(self):
#         return self._getter_opmode_sel()
#     def __setter_opmode_sel(self):
#         self._setter_opmode_sel()
#
#     @property
#     def current_sp(self):
#         return self.__getter_current_sp()
#     @current_sp.setter
#     def current_sp(self, value):
#         self.__setter_current_sp(value)
#         self._update_state()
#     def __getter_current_sp(self):
#         return self._getter_current_sp()
#     def __setter_current_sp(self, value):
#         value = self._check_current_ref_limits(value)
#         self._setter_current_sp(value)
#
#     def timing_trigger(self):
#         if self.opmode == _WfmRef:
#             self._current_rb = self._waveform[self._waveform_step]
#             self._waveform_step += 1
#             if self._waveform_step >= self._waveform.nr_points:
#                 self._waveform_step = 0
#             self.update_state()
#
#     def _callback(self, pvname, value, **kwargs):
#         raise NotImplementedError
#
#     def update_state(self):
#         if self.pwrstate == _Off:
#             self._set_current_rb(0.0)
#         else:
#             if self.opmode == _SlowRef:
#                 self._update_opmode_slowref()
#             elif self.opmode == _FastRef:
#                 self._update_opmode_fastref()
#             elif self.opmode == _WfmRef:
#                 self._update_opmode_wfmref()
#             elif self.opmode == _SigGen:
#                 self._update_opmode_siggen()
#             self._update_fluctuations()
#
#     def _set_current_rb(value):
#         raise NotImplementedError
#
#     def _update_opmode_slowref(self):
#         # slow reference setpoint mode
#         pass
#
#     def _update_opmode_fastref(self):
#         # fast reference setpoints (FOFB)
#         pass
#
#     def _update_opmode_wfmref(self):
#         # ramp driven by timing system signal
#         pass
#
#     def _update_opmode_siggen(self):
#         # demagnetization curve, for example
#         pass
#     def _update_fluctuations(self):
#         pass
#
#     def _check_current_ref_limits(self, value):
#         value = value if self._current_min is None else max(value,self._current_min)
#         value = value if self._current_max is None else min(value,self._current_max)
#         return value
#
#     def __str__(self):
#         st = '--- Controller ---\n'
#         propty = 'pwrstate_sel';       st +=   '{0:<20s}: {1}'.format(propty, _et.key('OffOnTyp', self.pwrstate_sel))
#         propty = 'pwrstate_sts';       st += '\n{0:<20s}: {1}'.format(propty, _et.key('OffOnTyp', self.pwrstate_sts))
#         propty = 'opmode_sel';         st += '\n{0:<20s}: {1}'.format(propty, _et.key('PSOpModeTyp', self.opmode_sel))
#         propty = 'opmode_sts';         st += '\n{0:<20s}: {1}'.format(propty, _et.key('PSOpModeTyp', self.opmode_sts))
#         propty = 'current_sp';         st += '\n{0:<20s}: {1}'.format(propty, self.current_sp)
#         propty = 'current_rb';         st += '\n{0:<20s}: {1}'.format(propty, self.current_rb)
#         propty = 'timestamp_pwrstate'; st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_pwrstate))
#         propty = 'timestamp_opmode';   st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_opmode))
#         return st
#
#

# class CtrllerSim(Ctrller):
#
#     def __init__(self, fluctuation_rms=_fluctuation_rms,
#                        **kwargs):
#         super().__init__(**kwargs)
#         self._fluctuation_rms = fluctuation_rms
#         self._pwrstate     = _et.idx('OffOnTyp', 'Off')
#         self._opmode       = _et.idx('PSOpModeTyp', 'SlowRef')
#         self._current_sp   = 0.0
#         self._current_rb   = self._current_sp
#         self._update_fluctuations()
#
#
#         def _getter_pwrstate_sel(self):
#             return self._pwrstate
#
#         def _setter_pwrstate_sel(self, value):
#             self._pwrstate = value
#
#
#
#
#
#
#
#         @property
#         def pwrstate_sts(self):
#             return self._pwrstate
#
#         @property
#         def opmode_sts(self):
#             return self._opmode
#
#         def _getter_opmode_sel(self):
#             return self._opmode
#
#         def _setter_opmode_sel(self, value):
#             self._opmode = value
#
#         @property
#         def current_rb(self):
#             return self._current_rb
#
#         def _getter_current_sp(self):
#             return self._current_sp
#
#         def _setter_current_sp(self, value):
#             self._current_sp = value
#
#
#     def timing_trigger(self):
#         if self.opmode == _WfmRef:
#             self._current_rb = self._waveform[self._waveform_step]
#             self._waveform_step += 1
#             if self._waveform_step >= self._waveform.nr_points:
#                 self._waveform_step = 0
#             self.update_state()
#
#     def _callback(self, pvname, value, **kwargs):
#         raise NotImplementedError
#
#     def update_state(self):
#         if self.pwrstate == _Off:
#             self._set_current_rb(0.0)
#         else:
#             if self.opmode == _SlowRef:
#                 self._update_opmode_slowref()
#             elif self.opmode == _FastRef:
#                 self._update_opmode_fastref()
#             elif self.opmode == _WfmRef:
#                 self._update_opmode_wfmref()
#             elif self.opmode == _SigGen:
#                 self._update_opmode_siggen()
#             self._update_add_fluctuations()
#
#     def _set_current_rb(value):
#         raise NotImplementedError
#
#     def _update_opmode_slowref(self):
#         # slow reference setpoint mode
#         pass
#
#     def _update_opmode_fastref(self):
#         # fast reference setpoints (FOFB)
#         pass
#
#     def _update_opmode_wfmref(self):
#         # ramp driven by timing system signal
#         pass
#
#     def _update_opmode_siggen(self):
#         # demagnetization curve, for example
#         pass
#
#     def _update_fluctuations(self):
#         self._current_rb += 2*(_random.random()-0.5)*self._fluctuation_rms
#
#     def _check_current_ref_limits(self, value):
#         value = value if self._current_min is None else max(value,self._current_min)
#         value = value if self._current_max is None else min(value,self._current_max)
#         return value
#

# class Controller:
#     """Base Controller Class
#
#     This is a simple power supply controller that responds immediatelly
#     to setpoints.
#
#     all enum properties (pwrstate, opmode, etc) are set in ints.
#     """
#
#     def __init__(self, IOC=None,
#                        current_min=None,
#                        current_max=None,
#                        waveform=None):
#
#         self._IOC = IOC
#         # --- default initial controller state ---
#         self._pwrstate = _Off
#         self._opmode   = _SlowRef
#         self._current_ref  = 0.0  # PS feedback current setpoint
#         self._current_dcct = 0.0  # PS feedback current readback
#         self._current_min = current_min
#         self._current_max = current_max
#         if waveform is None: waveform = _PSWaveForm.wfm_constant(_wfm_nr_points)
#         self._waveform = waveform
#         self._waveform_step = 0
#         now = _time.time()
#         self._timestamp_pwrstate = now
#         self._timestamp_opmode   = now
#
#     @property
#     def IOC(self):
#         return self._IOC
#
#     @property
#     def current(self):
#         self.update_state()
#         return self._current_dcct
#
#     @property
#     def pwrstate(self):
#         self.update_state()
#         return self._pwrstate
#
#     @property
#     def opmode(self):
#         self.update_state()
#         return self._opmode
#
#     @IOC.setter
#     def IOC(self, value):
#         self._IOC = value
#
#     @current.setter
#     def current_ref(self, value):
#         value = self._check_current_ref_limits(value)
#         self._current_ref = value # Should it happen even with PS off?
#         self.update_state()
#
#     @pwrstate.setter
#     def pwrstate(self, value):
#         self._timestamp_pwrstate = _time.time()
#         if value == _Off:
#             self._pwrstate = _Off
#         elif value == _On:
#             self._pwrstate = _On
#         else:
#             raise Exception('Invalid value!')
#         self.update_state()
#
#     @opmode.setter
#     def opmode(self, value):
#         if value == self._opmode: return # ?
#         self._timestamp_opmode = _time.time()
#         self._waveform_step = 0
#         if value in tuple(range(len(_et.enums('PSOpModeTyp')))):
#             self._opmode = value
#         else:
#             raise Exception('Invalid value!')
#         self.update_state()
#
#     def timing_trigger(self):
#         if self._opmode == _WfmRef:
#             self._current_dcct = self._waveform[self._waveform_step]
#             self._waveform_step += 1
#             if self._waveform_step >= self._waveform.nr_points:
#                 self._waveform_step = 0
#             self.update_state()
#
#     def update_state(self):
#         if self._pwrstate == _Off:
#             self._current_dcct = 0.0
#         else:
#             if self._opmode == _SlowRef:
#                 self._update_opmode_slowref()
#             elif self._opmode == _FastRef:
#                 self._update_opmode_fastref()
#             elif self._opmode == _WfmRef:
#                 self._update_opmode_wfmref()
#             elif self._opmode == _SigGen:
#                 self._update_opmode_siggen()
#             self._update_add_fluctuations()
#
#     def _update_opmode_slowref(self):
#         # slow reference setpoint mode
#         self._current_dcct = self._current_ref
#
#     def _update_opmode_fastref(self):
#         # fast reference setpoints (FOFB)
#         pass
#
#     def _update_opmode_wfmref(self):
#         # ramp driven by timing system signal
#         pass
#
#     def _update_opmode_siggen(self):
#         # demagnetization curve, for example
#         pass
#
#     def _update_add_fluctuations(self):
#         pass
#
#     def _check_current_ref_limits(self, value):
#         value = value if self._current_min is None else max(value,self._current_min)
#         value = value if self._current_max is None else min(value,self._current_max)
#         return value
#
#     def __str__(self):
#         st = '--- Controller ---\n'
#         propty = 'pwrstate';     st +=   '{0:<20s}: {1}'.format(propty, _et.key('OffOnTyp', self._pwrstate))
#         propty = 'opmode';       st += '\n{0:<20s}: {1}'.format(propty, _et.key('PSOpModeTyp', self._opmode))
#         propty = 'current-ref';   st += '\n{0:<20s}: {1}'.format(propty, self._current_ref)
#         propty = 'current-dcct';   st += '\n{0:<20s}: {1}'.format(propty, self._current_dcct)
#         propty = 'timestamp-pwrstate'; st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_pwrstate))
#         propty = 'timestamp-opmode';   st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_opmode))
#         return st
#

# class ControllerSim(Controller):
#     """Simple Simulated Controller Class
#
#     This subclass of Controller introduces simulated measurement fluctuations
#     and OpModes other than SlowRef.
#     """
#
#     def __init__(self, fluctuation_rms=_fluctuation_rms,
#                        **kwargs):
#         super().__init__(**kwargs)
#         self._fluctuation_rms = fluctuation_rms
#
#     def _update_opmode_fastref(self):
#         # fast reference setpoints (FOFB)
#         if self._current_min is not None and self._current_max is not None:
#             self._current_dcct = self._current_min + _random.random()*(self._current_max - self._current_min)
#
#     def _update_opmode_siggen(self):
#         # demagnetization curve, for example
#         if self._current_min is not None and self._current_max is not None:
#             ramp_fraction = ((_time.time() - self._timestamp_opmode)/20) % 1
#             self._current_dcct = self._current_min + ramp_fraction*(self._current_max - self._current_min)
#
#     def _update_add_fluctuations(self):
#         self._current_dcct += 2*(_random.random()-0.5)*self._fluctuation_rms
#

# class ControllerEpicsPS(ControllerSim):
#
#     def __init__(self, prefix,
#                        ps_name,
#                        connection_timeout = _connection_timeout,
#                        callback = None,
#                        **kwargs):
#         super().__init__(**kwargs)
#
#         self._uuid = _uuid.uuid4()  # unique ID for the class object
#         self._prefix = prefix
#         self._ps_name = ps_name
#         self._connection_timeout = connection_timeout
#         self._callbacks = {} if callback is None else {callback}
#         self._create_pvs()
#         self.update_state()
#
#     @property
#     def prefix(self):
#         return self.prefix
#
#     @property
#     def ps_name(self):
#         return self._ps_name
#
#     @property
#     def current_ref(self):
#         return super().current_ref
#
#     @current_ref.setter
#     def current_ref(self, value):
#         #print('controller', 'current_ref', value)
#         value = self._check_current_ref_limits(value)
#         self._pvs['Current-SP'].value = value
#         # invocation of _pvs_callback will update internal state of controller
#
#     @property
#     def pwrstate(self): # necessary for setter
#         return super().pwrstate
#
#     @pwrstate.setter
#     def pwrstate(self, value):
#         self._pvs['PwrState-Sel'].value = value
#         # invocation of _pvs_callback will update internal state of controller
#
#     @property # necessary for setter
#     def opmode(self):
#         return super().opmode
#
#     @opmode.setter
#     def opmode(self, value):
#         self._pvs['OpMode-Sel'].value = value
#         # invocation of _pvs_callback will update internal state of controller
#
#     def add_callback(self, callback, index):
#         self._callbacks[index] = callback
#
#     def _create_pvs(self):
#         self._pvs = {}
#         pvname = self._prefix + self._ps_name
#         self._pvs['PwrState-Sel'] = _SiriusPV(pvname + ':PwrState-Sel', connection_timeout=self._connection_timeout)
#         self._pvs['PwrState-Sts'] = _SiriusPV(pvname + ':PwrState-Sts', callback=self._callback, connection_timeout=self._connection_timeout)
#         self._pvs['OpMode-Sel'] = _SiriusPV(pvname + ':OpMode-Sel', connection_timeout=self._connection_timeout)
#         self._pvs['OpMode-Sts'] = _SiriusPV(pvname + ':OpMode-Sts', callback=self._callback, connection_timeout=self._connection_timeout)
#         self._pvs['Current-SP'] = _SiriusPV(pvname + ':Current-SP', callback=self._callback, connection_timeout=self._connection_timeout)
#         self._pvs['Current-RB'] = _SiriusPV(pvname + ':Current-RB', callback=self._callback, connection_timeout=self._connection_timeout)
#
#     def _callback(self, pvname, value, **kwargs):
#
#         value_changed_flag = False
#         if 'PwrState-Sts' in pvname and value != self._pwrstate:
#             self._pwrstate = value; value_changed_flag = True
#         elif 'OpMode-Sts' in pvname and value != self._opmode:
#             self._opmode = value; value_changed_flag = True
#         elif 'Current-RB' in pvname and value != self._current_dcct:
#             self._current_dcct = value; value_changed_flag = True
#         elif 'Current-SP' in pvname and value != self._current_ref:
#             print('controller current-sp', value)
#             self._current_ref = value; value_changed_flag = True
#
#         if value_changed_flag:
#             self.update_state()
#             for index, callback in self._callbacks.items():
#                 callback(pvname, value, **kwargs)
