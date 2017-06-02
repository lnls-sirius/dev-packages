
import time as _time
import uuid as _uuid
import math as _math
import copy as _copy
import random as _random
import numpy as _np
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.csdevice.pwrsupply import default_wfmlabels as _default_wfmlabels
from siriuspy.csdevice.pwrsupply import default_intlklabels as _default_intlklabels
from siriuspy.util import get_timestamp as _get_timestamp
from .waveform import PSWaveForm as _PSWaveForm
from .cycgen import PSCycGenerator as _PSCycGenerator
from abc import abstractmethod as _abstractmethod
from abc import ABCMeta as _ABCMeta
from epics import PV as _PV


_connection_timeout = 0.05 # [seconds]


class Controller(metaclass=_ABCMeta):

    """Base class that implements a controller interface.

        This class contains a number of pure virtual methods that should be
    implemented in sub classes. It also contains methods that implement
    most of the controller logic."""

    trigger_timeout = 10000000 # [seconds]
    #trigger_timout  = 0.002 # [seconds]

    def __init__(self, callback=None, psname=None, cycgen=None):
        self._callback = callback
        self._psname = psname
        #self._cycgen = _PSCycGenerator(interval=5) if cycgen is None else cycgen
        current_amp = abs(self.current_max)
        if cycgen is None:
            self._cycgen = _PSCycGenerator(interval=30, cycgen_type='exp_cos', tau=10, period=2.0, current_amp=current_amp)
        else:
            self._cycgen = cycgen

        self._set_cycling_state(False)

        self.update_state(init=True)

    # --- class interface - properties ---

    @property
    def pwrstate(self):
        return self._get_pwrstate()

    @pwrstate.setter
    def pwrstate(self, value):
        if value not in _et.values('OffOnTyp'): return
        if value != self.pwrstate:
            self._set_pwrstate(value)
            self.update_state(pwrstate=True)

    @property
    def opmode(self):
        return self._get_opmode()

    @opmode.setter
    def opmode(self, value):
        if value not in _et.values('PSOpModeTyp'): return
        if value != self.opmode:
            self._set_cycling_state(False)
            self._set_timestamp_trigger(None)
            self._set_wfmindex(0)
            self._set_cmd_abort_issued(False)
            if value in (_et.idx.SlowRef,_et.idx.SlowRefSync):
                self.current_sp = self.current_ref
            self._set_opmode(value)
            self.update_state(opmode=True)

    @property
    def reset_counter(self):
        return self._get_reset_counter()

    def reset(self):
        self._inc_reset_counter()
        self.current_sp = 0.0
        self._set_current_ref(0.0)
        self.opmode = _et.idx.SlowRef
        self._intlk_reset() # Try to reset interlock
        self.update_state(reset=True)

    @property
    def abort_counter(self):
        return self._get_abort_counter()

    def abort(self):
        self._inc_abort_counter()
        if self.opmode in (_et.idx.SlowRefSync, _et.idx.FastRef, _et.idx.MigWfm):
            self.opmode = _et.idx.SlowRef
        elif self.opmode == _et.idx.RmpWfm:
            self._set_cmd_abort_issued(True)
        self.update_state(abort=True)

    @property
    def timestamp_trigger(self):
        return self._get_timestamp_trigger()

    @property
    def trigger_timed_out(self):
        return self._get_trigger_timed_out()

    @property
    def intlk(self):
        return self._get_intlk()

    @property
    def intlklabels(self):
        return self._get_intlklabels()

    @property
    def current_min(self):
        return self._get_current_min()

    @property
    def current_max(self):
        return self._get_current_max()

    @current_min.setter
    def current_min(self, value):
        if value is None or self.current_max is None or value <= self.current_max:
            self._set_current_min(value)
        else:
            raise ValueError('Attribution of current_min > current_max!')

    @current_max.setter
    def current_max(self, value):
        if value is None or self.current_min is None or value >= self.current_min:
            self._set_current_max(value)
        else:
            raise ValueError('Attribution of current_max < current_min!')

    @property
    def current_sp(self):
        return self._get_current_sp()

    @current_sp.setter
    def current_sp(self, value):
        if value != self.current_sp:
            self._set_current_sp(float(value))
            self.update_state(current_sp=True)

    @property
    def current_ref(self):
        return self._get_current_ref()

    @property
    def current_load(self):
        return self._get_current_load()

    @property
    def wfmindex(self):
        return self._get_wfmindex()

    @property
    def wfmlabels(self):
        return self._get_wfmlabels()

    @property
    def wfmlabel(self):
        return self._get_wfmlabel()

    @wfmlabel.setter
    def wfmlabel(self, value):
        if value != self.wfmlabel:
            self._set_wfmlabel(value)
            self.update_state(wfmlabel=True)

    @property
    def wfmload(self):
        return self._get_wfmload()

    @wfmload.setter
    def wfmload(self, value):
        if value < len(_default_wfmlabels):
            self._set_wfmload(value)
            self.update_state(wfmload=True)

    @property
    def _wfmload_changed(self):
        return self._get_wfmload_changed()

    @_wfmload_changed.setter
    def _wfmload_changed(self, value):
        self._set_wfmload_changed(value)

    @property
    def wfmdata(self):
        return self._get_wfmdata()

    @wfmdata.setter
    def wfmdata(self, value):
        if (value != self.wfmdata).any():
            self._set_wfmdata_changed(True)
            self._set_wfmdata(value)
            self.update_state(wfmdata=True)

    @property
    def _wfmdata_changed(self):
        return self._get_wfmdata_changed()

    @_wfmdata_changed.setter
    def _wfmdata_changed(self, value):
        self._set_wfmdata_changed(value)

    @property
    def wfmsave(self):
        return self._get_wfmsave()

    @wfmsave.setter
    def wfmsave(self, value):
        self._set_wfmsave(value)
        self.update_state(wfmsave=True)

    @property
    def time(self):
        return self._get_time()

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, value):
        if callable(value):
            self._callback = value
        else:
            self._callback = None


    # --- class interface - methods ---

    def trigger_signal(self, delay=0, nrpts=1, width=0.0):
        if delay != 0: _time.sleep(delay)
        self._process_trigger_timeout()
        self._process_trigger_signal(nrpts,width)

    def update_state(self, **kwargs):
        self._process_trigger_timeout()
        self._process_pending_waveform_update()
        if self.opmode == _et.idx.SlowRef:
            self._update_SlowRef(**kwargs)
        elif self.opmode == _et.idx.SlowRefSync:
            self._update_SlowRefSync(**kwargs)
        elif self.opmode == _et.idx.FastRef:
            self._update_FastRef(**kwargs)
        elif self.opmode == _et.idx.RmpWfm:
            self._update_RmpWfm(**kwargs)
        elif self.opmode == _et.idx.MigWfm:
            self._update_MigWfm(**kwargs)
        elif self.opmode == _et.idx.Cycle:
            self._update_Cycle(**kwargs)
        else:
            pass
            #raise Exception('Invalid controller opmode')


    def fofb_signal(self):
        pass

    def _process_trigger_timeout(self):
        if self.opmode != _et.idx.RmpWfm: return
        if self.trigger_timed_out:
            self.wfmindex = 0

    def _process_pending_waveform_update(self):
        if self.wfmindex == 0:
            if self._wfmdata_changed:
                self._wfmdata_changed = False
                self._wfmdata_in_use = [datum for datum in self._waveform.data]
            if self._wfmload_changed:
                self._wfmload_changed = False
                self._wfmdata_in_use = [datum for datum in self._waveform.data]

    def _update_current_ref(self, value):
        if self.pwrstate == _et.idx.Off:
            self._set_current_ref(0.0)
        else:
            value = self._check_current_ref_limits(value)
            self._set_current_ref(value)

    def _finilize_cycgen(self):
        self._update_current_ref(0.0)
        self.opmode = _et.idx.SlowRef

    def _update_SlowRef(self, **kwargs):
        self._update_current_ref(self.current_sp)

    def _update_SlowRefSync(self, **kwargs):
        if 'trigger_signal' in kwargs:
            self._update_current_ref(self.current_sp)
        else:
            self._update_current_ref(self.current_ref)

    def _update_FastRef(self, **kwargs):
        pass

    def _update_RmpWfm(self, **kwargs):
        if 'trigger_signal' in kwargs:
            #print(self._cmd_abort_issued, self._wfmindex)
            scan_value = self._wfmdata_in_use[self._wfmindex]
            self._wfmindex = (self._wfmindex + 1) % len(self._wfmdata_in_use)
            if self._cmd_abort_issued and self._wfmindex == 0:
                #print('end of scan')
                self.opmode = _et.idx.SlowRef
        #elif 'pwrstate' in kwargs:
        else:
            scan_value = self.current_ref
        self._update_current_ref(scan_value)

    def _update_MigWfm(self, **kwargs):
        if 'trigger_signal' in kwargs:
            scan_value = self._wfmdata_in_use[self._wfmindex]
            if self._cmd_abort_issued:
                self.opmode = _et.idx.SlowRef
            else:
                self._wfmindex = (self._wfmindex + 1) % len(self._wfmdata_in_use)
            self._update_current_ref(scan_value)
            if self._wfmindex == 0:
                self.opmode = _et.idx.SlowRef
        else:
            self._update_current_ref(self.current_ref)

    def _update_Cycle(self, **kwargs):
        if 'trigger_signal' in kwargs:
            self._set_cycling_state(True)
        if 'pwrstate' in kwargs:
            self._set_timestamp_opmode(self.time)
        self._process_Cycle()


    def _check_current_ref_limits(self, value):
        value = value if self.current_min is None else max(value,self.current_min)
        value = value if self.current_max is None else min(value,self.current_max)
        return float(value)

    def __str__(self):
        self.update_state()
        st = '--- Controller ---\n'
        propty = 'opmode';            st += '\n{0:<20s}: {1}'.format(propty, _et.key('PSOpModeTyp', self.opmode))
        propty = 'pwrstate';          st += '\n{0:<20s}: {1}'.format(propty, _et.key('OffOnTyp', self.pwrstate))
        propty = 'intlk';             st += '\n{0:<20s}: {1}'.format(propty, self.intlk)
        propty = 'intlklabels';       st += '\n{0:<20s}: {1}'.format(propty, self.intlklabels)
        propty = 'reset_counter';     st += '\n{0:<20s}: {1}'.format(propty, self.reset_counter)
        propty = 'abort_counter';     st += '\n{0:<20s}: {1}'.format(propty, self.abort_counter)
        propty = 'current_min';       st += '\n{0:<20s}: {1}'.format(propty, self.current_min)
        propty = 'current_max';       st += '\n{0:<20s}: {1}'.format(propty, self.current_max)
        propty = 'current_sp';        st += '\n{0:<20s}: {1}'.format(propty, self.current_sp)
        propty = 'current_ref';       st += '\n{0:<20s}: {1}'.format(propty, self.current_ref)
        propty = 'current_load';      st += '\n{0:<20s}: {1}'.format(propty, self.current_load)
        propty = 'wfmload';           st += '\n{0:<20s}: {1}'.format(propty, self.wfmlabels[self.wfmload])
        propty = 'wfmdata';           st += '\n{0:<20s}: {1}'.format(propty, '['+str(self.wfmdata[0])+' ... '+str(self.wfmdata[-1])+']')
        propty = 'wfmsave';           st += '\n{0:<20s}: {1}'.format(propty, self.wfmsave)
        propty = 'wfmindex';          st += '\n{0:<20s}: {1}'.format(propty, self.wfmindex)
        propty = 'trigger_timed_out'; st += '\n{0:<20s}: {1}'.format(propty, self.trigger_timed_out)

        try:
            propty = '_timestamp_now';       st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self.time))
            if self.timestamp_trigger is not None:
                propty = '_timestamp_trigger';   st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self.timestamp_trigger))
            else:
                propty = '_timestamp_trigger';   st += '\n{0:<20s}: {1}'.format(propty, str(None))
            propty = '_timestamp_opmode';    st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_opmode))
            propty = '_timestamp_pwrstate';  st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_pwrstate))
        except:
            pass

        return st


    # --- pure virtual methods ---

    @_abstractmethod
    def _get_pwrstate(self):
        pass

    @_abstractmethod
    def _set_pwrstate(self, value):
        pass

    @_abstractmethod
    def _get_opmode(self):
        pass

    @_abstractmethod
    def _set_opmode(self, value):
        pass

    @_abstractmethod
    def _set_cmd_abort_issued(self, value):
        pass

    @_abstractmethod
    def _get_reset_counter(self):
        pass

    @_abstractmethod
    def _inc_reset_counter(self):
        pass

    @_abstractmethod
    def _get_abort_counter(self):
        pass

    @_abstractmethod
    def _inc_abort_counter(self):
        pass

    @_abstractmethod
    def _get_timestamp_trigger(self):
        pass

    @_abstractmethod
    def _set_timestamp_trigger(self, value):
        pass

    @_abstractmethod
    def _get_timestamp_opmode(self):
        pass

    @_abstractmethod
    def _set_timestamp_opmode(self, value):
        pass

    @_abstractmethod
    def _get_intlk(self):
        pass

    @_abstractmethod
    def _intlk_reset(self):
        pass

    @_abstractmethod
    def _get_intlklabels(self):
        pass

    @_abstractmethod
    def _get_trigger_timed_out(self, delay):
        pass

    @_abstractmethod
    def _set_trigger_timed_out(self):
        pass

    @_abstractmethod
    def _get_current_min(self):
        pass

    @_abstractmethod
    def _get_current_max(self):
        pass

    @_abstractmethod
    def _set_current_min(self, value):
        pass

    @_abstractmethod
    def _set_current_max(self, value):
        pass

    @_abstractmethod
    def _get_current_sp(self):
        pass

    @_abstractmethod
    def _set_current_sp(self, value):
        pass

    @_abstractmethod
    def _get_current_ref(self):
        pass

    @_abstractmethod
    def _get_current_load(self):
        pass

    @_abstractmethod
    def _get_wfmindex(self):
        pass

    @_abstractmethod
    def _get_wfmlabels(self):
        pass

    @_abstractmethod
    def _get_wfmlabel(self):
        pass

    @_abstractmethod
    def _set_wfmlabel(self, value):
        pass

    @_abstractmethod
    def _get_wfmload(self):
        pass

    @_abstractmethod
    def _set_wfmload(self, value):
        pass

    @_abstractmethod
    def _get_wfmload_changed(self):
        pass

    @_abstractmethod
    def _set_wfmload_changed(self, value):
        pass

    @_abstractmethod
    def _get_wfmdata(self):
        pass

    @_abstractmethod
    def _set_wfmdata(self, value):
        pass

    @_abstractmethod
    def _get_wfmdata_changed(self):
        pass

    @_abstractmethod
    def _set_wfmdata_changed(self, value):
        pass

    @_abstractmethod
    def _get_wfmsave(self):
        pass

    @_abstractmethod
    def _set_wfmsave(self, value):
        pass

    @_abstractmethod
    def _set_current_ref(self, value):
        pass

    @_abstractmethod
    def _set_wfmindex(self, value):
        pass

    @_abstractmethod
    def _get_time(self):
        pass

    @_abstractmethod
    def _process_trigger_signal(self, nrpts, width):
        pass

    @_abstractmethod
    def _get_cycling_state(self):
        pass

    @_abstractmethod
    def _set_cycling_state(self, value):
        pass

    @_abstractmethod
    def _process_Cycle(self):
        pass


class ControllerSim(Controller):

    def __init__(self, current_min=None,
                       current_max=None,
                       current_std=0.0,
                       random_seed=None,
                       psname=None,
                       **kwargs):

        self._time_simulated  = None
        now = self.time
        if random_seed is not None:
            _random.seed(random_seed)
        self._psname = psname
        self._pwrstate    = _et.idx.Off          # power state
        self._timestamp_pwrstate = now           # last time pwrstate was changed
        self._opmode      = _et.idx.SlowRef      # operation mode state
        self._timestamp_opmode   = now           # last time opmode was changed
        self._timestamp_cycle_start = now
        self._abort_counter = 0                  # abort command counter
        self._cmd_abort_issued = False
        self._reset_counter = 0                  # reset command counter
        self._cmd_reset_issued = False
        self._intlk = 0                          # interlock signals
        self._intlklabels = _default_intlklabels
        self._timestamp_trigger  = None          # last time trigger signal was received

        self.current_max = current_max
        self.current_min = current_min
        self._current_std = current_std          # standard dev of error added to output current
        self._current_sp   = 0.0                 # init SP value
        self._current_ref  = self._current_sp    # reference current of DSP
        self._current_load = self._current_ref   # current value supplied to magnets
        self._init_waveforms()                   # initialize waveform data

        super().__init__(psname=psname,**kwargs)

    def _get_pwrstate(self):
        return self._pwrstate

    def _set_pwrstate(self, value):
        self._timestamp_pwrstate = self.time
        self._pwrstate = value
        self._mycallback(pvname='pwrstate')

    def _get_opmode(self):
        return self._opmode

    def _set_opmode(self, value):
        self._timestamp_opmode = self.time
        self._opmode = value
        self._mycallback(pvname='opmode')

    def _set_cmd_abort_issued(self, value):
        self._cmd_abort_issued = value

    def _get_reset_counter(self):
        return self._reset_counter

    def _inc_reset_counter(self):
        self._reset_counter += 1
        self._mycallback(pvname='reset')

    def _get_abort_counter(self):
        return self._abort_counter

    def _inc_abort_counter(self):
        self._abort_counter += 1
        self._mycallback(pvname='abort')

    def _get_timestamp_trigger(self):
        return self._timestamp_trigger

    def _set_timestamp_trigger(self, value):
        self._timestamp_trigger = value

    def _get_timestamp_opmode(self):
        return self._timestamp_opmode

    def _set_timestamp_opmode(self, value):
        self._timestamp_opmode = value

    def _get_intlk(self):
        return self._intlk

    def _intlk_reset(self):
        self._intlk = 0

    def _get_intlklabels(self):
        return self._intlklabels

    def _get_current_min(self):
        return None if not hasattr(self, '_current_min') else self._current_min

    def _get_current_max(self):
        return None if not hasattr(self, '_current_max') else self._current_max

    def _set_current_min(self, value):
        self._current_min = value

    def _set_current_max(self, value):
        self._current_max = value

    def _get_current_sp(self):
        return self._current_sp

    def _set_current_sp(self, value):
        self._current_sp = value
        self._mycallback(pvname='current_sp')

    def _get_current_ref(self):
        return self._current_ref

    def _get_current_load(self):
        return self._current_load

    def _get_wfmindex(self):
        return self._wfmindex

    def _set_wfmindex(self, value):
        self._wfmindex = value

    def _get_wfmlabels(self):
        return _np.array([label for label in self._wfmlabels])

    def _get_wfmlabel(self):
        return self._waveform.label

    def _set_wfmlabel(self, value):
        self._waveform.label = value
        self._wfmlabels[self._wfmslot] = value
        self._mycallback(pvname='wfmlabel')

    def _get_wfmload(self):
        return self._wfmslot

    def _set_wfmload(self, value):
        # load waveform stored in non-volatile memory
        self._wfmslot = value
        wfm = self._load_waveform_from_slot(self._wfmslot)
        if wfm != self._waveform:
            self._pending_wfmload = True
            self._waveform = wfm
            self._mycallback(pvname='wfmload')

    def _get_wfmload_changed(self):
        return self._wfmload_changed_state

    def _set_wfmload_changed(self, value):
        self._wfmload_changed_state = value

    def _get_wfmdata(self):
        return _np.array(self._waveform.data)

    def _set_wfmdata(self, value):
        self._waveform.data = _np.array(value)
        self._mycallback(pvname='wfmdata')

    def _get_wfmdata_changed(self):
        return self._wfmdata_changed_state

    def _set_wfmdata_changed(self, value):
        self._wfmdata_changed_state = value

    def _get_wfmsave(self):
        return self._wfmsave

    def _set_wfmsave(self, value):
        self._wfmsave += 1
        self._save_waveform_to_slot(self._wfmslot)
        self._mycallback(pvname='wfmsave')

    def _get_trigger_timed_out(self):
        if self._timestamp_trigger is not None and self.time - self._timestamp_trigger > Controller.trigger_timeout:
            return True
        else:
            return False

    def _set_trigger_timed_out(self, value):
        self._trigger_timed_out = value

    def _get_time(self):
        if self._time_simulated is None:
            return _time.time()
        else:
            return self._time_simulated

    def _process_trigger_signal(self, nrpts, width):
        now = self.time
        if nrpts == 1:
            self._set_timestamp_trigger(now)
            self.update_state(trigger_signal=True)
        else:
            self._time_simulated = now
            for i in range(nrpts):
                self._time_simulated = now + i * width
                self._set_timestamp_trigger(self._time_simulated)
                self.update_state(trigger_signal=True)
            self._time_simulated = None

    def _set_current_ref(self, value):
        if value != self._current_ref:
            self._current_ref = value
            self._mycallback(pvname='current_ref')
        if self._time_simulated is not None:
            _random.seed(self._time_simulated) # if time is frozen, generated same error.
        value = _random.gauss(self._current_ref, self._current_std)
        if value != self._current_load:
            self._current_load = value
            self._mycallback(pvname='current_load')

    def _get_cycling_state(self):
        return self._cycling_state

    def _set_cycling_state(self, value):
        if value and not self._cycling_state:
            self._timestamp_cycle_start = self.time
        self._cycling_state = value

    def _process_Cycle(self):
        if self._get_cycling_state():
            dt  = self.time - self._timestamp_cycle_start
            if self._cycgen.out_of_range(dt):
                self._finilize_cycgen()
            else:
                scan_value = self._cycgen.get_current(dt)
                self._update_current_ref(scan_value)


    def _mycallback(self, pvname):
        if self._callback is None:
            return
        elif pvname == 'pwrstate':
            self._callback(pvname='pwrstate', value=self._pwrstate)
        elif pvname == 'opmode':
            self._callback(pvname='opmode', value=self._opmode)
        elif pvname == 'current_sp':
            self._callback(pvname='current_sp', value=self._current_sp)
        elif pvname == 'current_ref':
            self._callback(pvname='current_ref', value=self._current_ref)
        elif pvname == 'current_load':
            self._callback(pvname='current_load', value=self._current_load)
        elif pvname == 'wfmload':
            self._callback(pvname='wfmload', value=self._wfmslot)
        elif pvname == 'wfmdata':
            self._callback(pvname='wfmdata', value=self._waveform.data)
        elif pvname == 'wfmlabel':
            self._callback(pvname='wfmlabel', value=self._waveform.label)
        elif pvname == 'wfmsave':
            self._callback(pvname='wfmsave', value=self._wfmsave)
        elif pvname == 'reset':
            self._callback(pvname='reset', value=self._wfmsave)
        elif pvname == 'abort':
            self._callback(pvname='abort', value=self._wfmsave)
        else:
            raise NotImplementedError

    def _init_waveforms(self):
        self._wfmindex  = 0   # updated index selecting value of current in waveform in use
        self._wfmsave   = 0   # waveform save command counter
        self._wfmslot   = 0   # selected waveform slot index
        self._wfmlabels = []  # updated array with waveform labels
        self._wfmdata_changed_state = False
        self._wfmload_changed_state = False
        for i in range(len(_default_wfmlabels)):
            wfm = self._load_waveform_from_slot(i)
            self._wfmlabels.append(wfm.label)
            if i == self._wfmslot:
                self._waveform = wfm
                self._wfmdata_in_use = _np.array(wfm.data)

    def _load_waveform_from_slot(self, slot):
        if self._psname is not None:
            fname = self._psname + ':' + _default_wfmlabels[slot]
        else:
            fname = _default_wfmlabels[slot]
        try:
            return _PSWaveForm(label= _default_wfmlabels[slot],filename=fname+'.txt')
        except FileNotFoundError:
            wfm = _PSWaveForm.wfm_constant(label= _default_wfmlabels[slot],filename=fname+'.txt')
            wfm.save_to_file(filename=fname+'.txt')
            return wfm

    def _load_waveform_from_label(self, label):
        if label in self._wfmlabels:
            slot = self._wfmlabels.index(label)
            return slot, self._load_waveform_from_slot(slot)
        else:
            return None

    def _save_waveform_to_slot(self, slot):
        if self._psname is not None:
            fname = self._psname + ':' + _default_wfmlabels[slot]
        else:
            fname = _default_wfmlabels[slot]
        try:
            self._waveform.save_to_file(filename=fname+'.txt')
        except PermissionError:
            raise Exception('Could not write file "' + fname+'.txt' + '"!')

Controller.register(ControllerSim)


class ControllerEpics(Controller):

    def __init__(self, psname,
                       connection_timeout=_connection_timeout,
                       **kwargs):

        self._psname = psname
        self._connection_timeout = connection_timeout
        self._callback = None
        self._create_epics_pvs()
        super().__init__(psname=psname,**kwargs)


        now = self.time
        self._timestamp_pwrstate = now # last time pwrstate was changed
        self._timestamp_opmode   = now # last time opmode was changed

    @property
    def connected(self):
        for name,pv in self._pvs.items():
            if not pv.connected: return False
        return True

    def _get_pwrstate(self):
        return self._pvs['PwrState-Sts'].get(timeout=self._connection_timeout)

    def _set_pwrstate(self, value):
        if value not in _et.values('OffOnTyp'): raise Exception('Invalid value of pwrstate_sel')
        if value != self.pwrstate:
            self._pvs['PwrState-Sel'].value = value
            self.update_state(pwrstate=True)

    def _get_opmode(self):
        return self._pvs['OpMode-Sts'].get(timeout=self._connection_timeout)

    def _set_opmode(self, value):
        if value not in _et.values('OffOnTyp'): raise Exception('Invalid value of pwrstate_sel')
        if value != self.opmode:
            self._pvs['OpMode-Sel'].value = value
            self.update_state(opmode=True)

    def _set_cmd_abort_issued(self, value):
        pass

    def _get_reset_counter(self):
        return self._pvs['Reset-Cmd'].get(timeout=self._connection_timeout)

    def _inc_reset_counter(self):
        self._pvs['Reset-Cmd'].value = 0
        self.update_state(reset=True)

    def _get_abort_counter(self):
        return self._pvs['Abort-Cmd'].get(timeout=self._connection_timeout)

    def _inc_abort_counter(self):
        self._pvs['Abort-Cmd'].value = 0
        self.update_state(reset=True)

    def _get_timestamp_trigger(self):
        raise Exception('Invalid method call')

    def _set_timestamp_trigger(self, value):
        pass

    def _get_timestamp_opmode(self):
        raise Exception('Invalid method call')

    def _set_timestamp_opmode(self, value):
        pass

    def _get_intlk(self):
        return self._pvs['Intlk-Mon'].get(timeout=self._connection_timeout)

    def _intlk_reset(self):
        pass

    def _get_intlklabels(self):
        return self._pvs['IntlkLabels-Cte'].get(timeout=self._connection_timeout)

    def _get_current_min(self):
        return self._pvs['Current-SP'].lower_ctrl_limit

    def _get_current_max(self):
        return self._pvs['Current-SP'].upper_ctrl_limit

    def _set_current_min(self):
        pass

    def _set_current_max(self):
        pass

    def _get_current_sp(self):
        return self._pvs['Current-SP'].get(timeout=self._connection_timeout)

    def _set_current_sp(self, value):
        if value != self.current_sp:
            self._pvs['Current-SP'].value = value
            self.update_state(current_sp=True)

    def _get_current_ref(self):
        return self._pvs['CurrentRef-Mon'].get(timeout=self._connection_timeout)

    def _get_current_load(self):
        return self._pvs['Current-Mon'].get(timeout=self._connection_timeout)

    def _get_wfmindex(self):
        return self._pvs['WfmIndex-Mon'].get(timeout=self._connection_timeout)

    def _set_wfmindex(self, value):
        pass

    def _get_wfmlabels(self):
        return self._pvs['WfmLabels-Mon'].get(timeout=self._connection_timeout)

    def _get_wfmlabel(self):
        return self._pvs['WfmLabel-RB'].get(timeout=self._connection_timeout)

    def _set_wfmlabel(self, value):
        if value != self.wfmlabel:
            self._pvs['WfmLabel-SP'].value = value
            self.update_state(wfmlabel=True)

    def _get_wfmload(self):
        return self._pvs['WfmLoad-Sts'].get(timeout=self._connection_timeout)

    def _set_wfmload(self, value):
        if value != self.wfmload:
            self._pvs['WfmLoad-Sel'].value = value
            self.update_state(wfmload=True)

    def _get_wfmload_changed(self):
        return False

    def _set_wfmload_changed(self, value):
        pass

    def _get_wfmdata(self):
        return self._pvs['WfmData-RB'].get(timeout=self._connection_timeout)

    def _set_wfmdata(self, value):
        if (value != self.wfmdata).any():
            self._pvs['WfmData-SP'].value = value
            self.update_state(wfmdata=True)

    def _get_wfmdata_changed(self):
        return False

    def _set_wfmdata_changed(self, value):
        pass

    def _get_wfmsave(self):
        return self._pvs['WfmSave-Cmd'].get(timeout=self._connection_timeout)

    def _set_wfmsave(self, value):
        self._pvs['WfmSave-Cmd'].value = value
        self.update_state(wfmsave=True)

    def _get_trigger_timed_out(self):
        return False

    def _set_trigger_timed_out(self, value):
        pass

    def _get_time(self):
        return _time.time()

    def _process_trigger_signal(self, nrpts, width):
        pass

    def _set_current_ref(self, value):
        pass

    def _get_cycling_state(self):
        pass

    def _set_cycling_state(self, value):
        pass

    def _process_Cycle(self):
        pass

    def _mycallback(self, pvname, value, **kwargs):
        if self._callback is None:
            return
        else:
            self._callback(pvname=pvname, value=value, **kwargs)

    def _create_epics_pvs(self):
        self._pvs = {}
        pv = self._psname
        self._pvs['PwrState-Sel']    = _PV(pv + ':PwrState-Sel',    connection_timeout=self._connection_timeout)
        self._pvs['PwrState-Sts']    = _PV(pv + ':PwrState-Sts',    connection_timeout=self._connection_timeout)
        self._pvs['OpMode-Sel']      = _PV(pv + ':OpMode-Sel',      connection_timeout=self._connection_timeout)
        self._pvs['OpMode-Sts']      = _PV(pv + ':OpMode-Sts',      connection_timeout=self._connection_timeout)
        self._pvs['Reset-Cmd']       = _PV(pv + ':Reset-Cmd',       connection_timeout=self._connection_timeout)
        self._pvs['Abort-Cmd']       = _PV(pv + ':Abort-Cmd',       connection_timeout=self._connection_timeout)
        self._pvs['Intlk-Mon']       = _PV(pv + ':Intlk-Mon',       connection_timeout=self._connection_timeout)
        self._pvs['IntlkLabels-Cte'] = _PV(pv + ':IntlkLabels-Cte', connection_timeout=self._connection_timeout)
        self._pvs['Current-SP']      = _PV(pv + ':Current-SP',      connection_timeout=self._connection_timeout)
        self._pvs['Current-RB']      = _PV(pv + ':Current-RB',      connection_timeout=self._connection_timeout)
        self._pvs['CurrentRef-Mon']  = _PV(pv + ':CurrentRef-Mon',  connection_timeout=self._connection_timeout)
        self._pvs['Current-Mon']     = _PV(pv + ':Current-Mon',     connection_timeout=self._connection_timeout)
        self._pvs['WfmIndex-Mon']    = _PV(pv + ':WfmIndex-Mon',    connection_timeout=self._connection_timeout)
        self._pvs['WfmLabels-Mon']   = _PV(pv + ':WfmLabels-Mon',   connection_timeout=self._connection_timeout)
        self._pvs['WfmLabel-SP']     = _PV(pv + ':WfmLabel-SP',     connection_timeout=self._connection_timeout)
        self._pvs['WfmLabel-RB']     = _PV(pv + ':WfmLabel-RB',     connection_timeout=self._connection_timeout)
        self._pvs['WfmLoad-Sel']     = _PV(pv + ':WfmLoad-Sel',     connection_timeout=self._connection_timeout)
        self._pvs['WfmLoad-Sts']     = _PV(pv + ':WfmLoad-Sts',     connection_timeout=self._connection_timeout)
        self._pvs['WfmData-SP']      = _PV(pv + ':WfmData-SP',      connection_timeout=self._connection_timeout)
        self._pvs['WfmData-RB']      = _PV(pv + ':WfmData-RB',      connection_timeout=self._connection_timeout)
        self._pvs['WfmSave-Cmd']     = _PV(pv + ':WfmSave-Cmd',     connection_timeout=self._connection_timeout)

        self._pvs['PwrState-Sel'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['PwrState-Sts'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['OpMode-Sel'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['OpMode-Sts'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Reset-Cmd'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Abort-Cmd'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Intlk-Mon'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['IntlkLabels-Cte'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Current-SP'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Current-RB'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['CurrentRef-Mon'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Current-Mon'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmIndex-Mon'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmLabels-Mon'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmLabel-SP'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmLabel-RB'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmLoad-Sel'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmLoad-Sts'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmData-SP'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmData-RB'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmSave-Cmd'].wait_for_connection(timeout=self._connection_timeout)

        # add callback
        uuid = _uuid.uuid4()
        self._pvs['PwrState-Sel'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['PwrState-Sts'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['OpMode-Sel'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['OpMode-Sts'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Reset-Cmd'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Abort-Cmd'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Intlk-Mon'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['IntlkLabels-Cte'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Current-SP'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Current-RB'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['CurrentRef-Mon'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Current-Mon'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmIndex-Mon'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmLabels-Mon'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmLabel-SP'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmLabel-RB'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmLoad-Sel'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmLoad-Sts'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmData-SP'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmData-RB'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmSave-Cmd'].add_callback(callback=self._mycallback, index=uuid)

Controller.register(ControllerEpics)
