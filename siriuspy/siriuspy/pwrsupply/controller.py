
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
import copy as _copy

from epics import PV as _PV


_connection_timeout = 0.05 # [s]
_controller_wfmlabels         = ('Waveform1','Waveform2','Waveform3','Waveform4','Waveform5','Waveform6')
_controller_trigger_timeout   = 20 # [s]

class Controller:

    def __init__(self, current_min=None,     # mininum current setpoint value
                       current_max=None,     # maximum current setpoint value
                       callback=None):
        self._current_min = current_min
        self._current_max = current_max
        self._callback = callback

    def __str__(self):
        self._update_state()
        st = '--- Controller ---\n'
        propty = 'opmode';          st += '\n{0:<20s}: {1}'.format(propty, _et.key('PSOpModeTyp', self.opmode))
        propty = 'pwrstate';        st += '\n{0:<20s}: {1}'.format(propty, _et.key('OffOnTyp', self.pwrstate))
        #propty = 'abort';           st += '\n{0:<20s}: {1}'.format(propty, self.abort)
        #propty = 'abort_flag';      st += '\n{0:<20s}: {1}'.format(propty, self._abort_flag)
        #propty = 'reset';           st += '\n{0:<20s}: {1}'.format(propty, self.reset)
        propty = 'current_sp';      st += '\n{0:<20s}: {1}'.format(propty, self.current_sp)
        propty = 'current_ref';     st += '\n{0:<20s}: {1}'.format(propty, self.current_ref)
        propty = 'current_load';    st += '\n{0:<20s}: {1}'.format(propty, self.current_load)
        propty = 'current_min';     st += '\n{0:<20s}: {1}'.format(propty, self.current_min)
        propty = 'current_max';     st += '\n{0:<20s}: {1}'.format(propty, self.current_max)
        propty = 'wfmload';         st += '\n{0:<20s}: {1}'.format(propty, self.wfmload)
        propty = 'wfmdata';         st += '\n{0:<20s}: {1}'.format(propty, '['+str(self.wfmdata[0])+' ... '+str(self.wfmdata[-1])+']')
        propty = 'wfmsave';         st += '\n{0:<20s}: {1}'.format(propty, self.wfmsave)
        propty = 'wfmindex';        st += '\n{0:<20s}: {1}'.format(propty, self.wfmindex)
        try:
            propty = '_ramping_mode';        st += '\n{0:<20s}: {1}'.format(propty, self._ramping_mode)
        except:
            pass
        try:
            propty = '_timestamp_now';       st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(_time.time()))
            propty = '_timestamp_trigger';   st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_trigger))
            propty = '_timestamp_opmode';    st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_opmode))
            propty = '_timestamp_pwrstate';  st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_pwrstate))
        except:
            pass

        return st

    def _check_current_ref_limits(self, value):
        value = value if self.current_min is None else max(value,self.current_min)
        value = value if self.current_max is None else min(value,self.current_max)
        return float(value)


class ControllerSim(Controller):

    def __init__(self, current_std=0.0,
                       **kwargs):

        super().__init__(**kwargs)
        now = _time.time()
        self._current_std = current_std
        self._pwrstate = _et.idx.Off
        self._opmode = _et.idx.SlowRef
        self._current_sp = 0.0
        self._current_ref = self._current_sp
        self._current_load = self._current_ref
        self._timestamp_pwrstate = now # last time pwrstate was changed
        self._timestamp_opmode   = now # last time opmode was changed
        self._timestamp_trigger  = now # last time trigger received
        self._cmd_abort_issued = False
        self._cmd_reset_issued = False
        self._ramping_mode     = False
        self._pending_wfmdata = False  # pending wfm slot number
        self._pending_wfmload = False # epnding wfm slot number
        self._pending_abort   = False
        self._init_waveforms()

    def _init_waveforms(self):
        self._wfmindex = 0
        self._wfmsave = 0
        self._wfmslot = 0
        self._wfmlabels = []
        for i in range(len(_controller_wfmlabels)):
            wfm = self._load_waveform_from_slot(i)
            self._wfmlabels.append(wfm.label)
            if i == self._wfmslot:
                self._waveform = wfm
                self._wfmdata_in_use = [datum for datum in wfm.data]

    def _load_waveform_from_slot(self, slot):
        fname = _controller_wfmlabels[slot]
        try:
            return _PSWaveForm(filename=fname+'.txt')
        except FileNotFoundError:
            wfm = _PSWaveForm.wfm_constant(label=fname)
            wfm.save_to_file(filename=fname+'.txt')
            return wfm

    def _load_waveform_from_label(self, label):
        if label in self._wfmlabels:
            slot = self._wfmlabels.index(label)
            return slot, self._load_waveform_from_slot(slot)
        else:
            return None

    def _save_waveform_to_slot(self, slot):
        fname = _controller_wfmlabels[slot]
        try:
            self._waveform.save_to_file(filename=fname+'.txt')
        except PermissionError:
            raise Exception('Could not write file "' + fname+'.txt' + '"!')

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, value):
        self._callback = value

    @property
    def wfmindex(self):
        return self._wfmindex

    @property
    def wfmlabels(self):
        return [label for label in self._wfmlabels]

    @property
    def wfmlabel(self):
        return self._waveform.label

    @wfmlabel.setter
    def wfmlabel(self, value):
        if value != self._waveform.label:
            self._waveform.label = value
            self._wfmlabels[self._wfmslot] = value
            self._mycallback(pvname='wfmlabel')
            self._update_state(wfmlabel=True)

    @property
    def wfmload(self):
        return self._waveform.label

    @wfmload.setter
    def wfmload(self, value):
        # load waveform stored in non-volatile memory
        slot, wfm = self._load_waveform_from_label(value)
        if wfm is not None and wfm != self._waveform:
            self._pending_wfmload = True
            self._wfmslot, self._waveform = slot, wfm
            self._mycallback(pvname='wfmload')
            self._update_state(wfmload=True)

    @property
    def wfmdata(self):
        return [datum for datum in self._waveform.data]

    @wfmdata.setter
    def wfmdata(self, value):
        if value != self._waveform.data:
            self._pending_wfmdata = True
            self._waveform.data = [datum for datum in value]
            self._mycallback(pvname='wfmdata')
            self._update_state(wfmdata=True)

    @property
    def wfmsave(self):
        return self._wfmsave

    @wfmsave.setter
    def wfmsave(self, value):
        self._wfmsave += 1
        self._save_waveform_to_slot(self._wfmslot)
        self._mycallback(pvname='wfmsave')
        self._update_state(wfmsave=True)

    @property
    def pwrstate(self):
        return self._pwrstate

    @pwrstate.setter
    def pwrstate(self, value):
        if value not in _et.values('OffOnTyp'): return
        if value != self._pwrstate:
            self._timestamp_pwrstate = _time.time()
            self._pwrstate = value
            self._mycallback(pvname='pwrstate')
            self._update_state(pwrstate=True)

    @property
    def opmode(self):
        return self._opmode

    @opmode.setter
    def opmode(self, value):
        if value not in _et.values('PSOpModeTyp'): return
        if value != self._opmode:
            self._timestamp_opmode = _time.time()
            previous_opmode = self._opmode
            self._opmode = value
            self._mycallback(pvname='opmode')
            self._update_state(opmode=previous_opmode)

    @property
    def current_min(self):
        return self._current_min

    @property
    def current_max(self):
        return self._current_max

    @property
    def current_sp(self):
        return self._current_sp

    @current_sp.setter
    def current_sp(self, value):
        value = self._check_current_ref_limits(value)
        if value != self._current_sp:
            self._current_sp = value
            self._mycallback(pvname='current_sp')
            self._update_state(current_sp=True)

    @property
    def current_ref(self):
        return self._current_ref

    @property
    def current_load(self):
        return self._current_load

    def send_trigger(self):
        now = self._update_ramping_state()
        self._timestamp_trigger = now
        self._update_state(trigger_signal=True)

    def _update_ramping_state(self):
        now = _time.time()
        if self._ramping_mode:
            if now - self._timestamp_trigger > _controller_trigger_timeout:
                self._wfmindex = 0
                self._ramping_mode = False
        return now

    def _change_opmode(self, previous_mode):
        self._wfmindex = 0
        self._ramping_mode = False
        self._current_sp = self._current_ref

    def _update_state(self, **kwargs):
        if 'opmode' in kwargs:
            self._change_opmode(previous_mode=kwargs['opmode'])
        now = self._update_ramping_state()
        self._check_pending_waveform_writes()
        if self._opmode == _et.idx.SlowRef:
            self._update_SlowRef(**kwargs)
        elif self._opmode == _et.idx.SyncRef:
            self._update_SyncRef(**kwargs)
        elif self._opmode == _et.idx.FastRef:
            self._update_FastRef(**kwargs)
        elif self._opmode == _et.idx.RmpMultWfm:
            self._update_RmpMultWfm(**kwargs)
        elif self._opmode == _et.idx.MigMultWfm:
            self._update_MigMultWfm(**kwargs)
        elif self._opmode == _et.idx.RmpSglWfm:
            self._update_RmpSglWfm(**kwargs)
        elif self._opmode == _et.idx.MigSglWfm:
            self._update_MigSglWfm(**kwargs)
        elif self._opmode == _et.idx.SigGen:
            self._update_SigGen(**kwargs)
        elif self._opmode == _et.idx.CycGen:
            self._update_CycGen(**kwargs)
        else:
            raise Exception('Invalid controller opmode')

    def _check_pending_waveform_writes(self):
        if not self._ramping_mode or self._wfmindex == 0:
            if self._pending_wfmdata:
                self._pending_wfmdata = False
                self._wfmdata_in_use = [datum for datum in self._waveform.data]
            if self._pending_wfmload:
                self._pending_wfmload = False
                self._wfmdata_in_use = [datum for datum in self._waveform.data]

    def _update_current_ref(self, value):
        if value != self._current_ref:
            self._current_ref = value
            self._mycallback(pvname='current_ref')
        if self._pwrstate == _et.idx.Off:
            return
        value = _random.gauss(self._current_ref, self._current_std)
        if value != self._current_load:
            self._current_load = value
            self._mycallback(pvname='current_load')

    def _update_SlowRef(self, **kwargs):
        self._update_current_ref(self._current_sp)

    def _update_SyncRef(self, **kwargs):
        if 'trigger_signal' in kwargs:
            self._update_current_ref(self._current_sp)
        else:
            self._update_current_ref(self._current_ref)

    def _update_FastRef(self, **kwargs):
        pass

    def _update_RmpMultWfm(self, **kwargs):
        if 'trigger_signal' in kwargs:
            self._ramping_mode = True
            scan_value = self._wfmdata_in_use[self._wfmindex]
            if self._cmd_abort_issued and self._wfmindex == 0:
                # end of ramp and abort has been issued.
                self._abort_issued = False
                self.opmode = _et.idx.SlowRef
            else:
                self._wfmindex = (self._wfmindex + 1) % len(self._wfmdata_in_use)
        else:
            scan_value = self._current_ref
        self._update_current_ref(scan_value)

    def _update_MigMultWfm(self, **kwargs):
        pass

    def _update_RmpSglWfm(self, **kwargs):
        pass

    def _update_MigSglWfm(self, **kwargs):
        pass

    def _update_SigGen(self, **kwargs):
        self._check_pending_waveform_writes()

    def _update_CycGen(self, **kwargs):
        self._check_pending_waveform_writes()

    def _mycallback(self, pvname):
        print('mycallback: ' + pvname)
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
            self._callback(pvname='wfmload', value=self._wfmload)
        elif pvname == 'wfmdata':
            self._callback(pvname='wfmdata', value=self._wfmdata)
        elif pvname == 'wfmlabel':
            self._callback(pvname='wfmlabel', value=self._wfmlabel)
        elif pvname == 'wfmsave':
            self._callback(pvname='wfmsave', value=self._wfmsave)
        else:
            raise NotImplementedError


class ControllerEpics(Controller):

    def __init__(self, ps_name,
                       connection_timeout=_connection_timeout,
                       **kwargs):
        super().__init__(**kwargs)
        self._ps_name = ps_name
        self._connection_timeout = connection_timeout
        self._create_epics_pvs()

    def _create_epics_pvs(self):
        self._pvs = {}
        pv = self._ps_name
        self._pvs['PwrState-Sel']   = _PV(pv + ':PwrState-Sel',   connection_timeout=self._connection_timeout)
        self._pvs['PwrState-Sts']   = _PV(pv + ':PwrState-Sts',   connection_timeout=self._connection_timeout)
        self._pvs['OpMode-Sel']     = _PV(pv + ':OpMode-Sel',     connection_timeout=self._connection_timeout)
        self._pvs['OpMode-Sts']     = _PV(pv + ':OpMode-Sts',     connection_timeout=self._connection_timeout)
        self._pvs['Current-SP']     = _PV(pv + ':Current-SP',     connection_timeout=self._connection_timeout)
        self._pvs['Current-RB']     = _PV(pv + ':Current-RB',     connection_timeout=self._connection_timeout)
        self._pvs['CurrentRef-Mon'] = _PV(pv + ':CurrentRef-Mon', connection_timeout=self._connection_timeout)
        self._pvs['Current-Mon']    = _PV(pv + ':Current-Mon',    connection_timeout=self._connection_timeout)
        self._pvs['WfmIndex-Mon']   = _PV(pv + ':WfmIndex-Mon',   connection_timeout=self._connection_timeout)
        self._pvs['WfmLabels-Mon']  = _PV(pv + ':WfmLabels-Mon',  connection_timeout=self._connection_timeout)
        self._pvs['WfmLabel-SP']    = _PV(pv + ':WfmLabel-SP',    connection_timeout=self._connection_timeout)
        self._pvs['WfmLabel-RB']    = _PV(pv + ':WfmLabel-RB',    connection_timeout=self._connection_timeout)

        self._pvs['PwrState-Sel'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['PwrState-Sts'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['OpMode-Sel'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['OpMode-Sts'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Current-SP'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Current-RB'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['CurrentRef-Mon'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['Current-Mon'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmIndex-Mon'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmLabels-Mon'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmLabel-SP'].wait_for_connection(timeout=self._connection_timeout)
        self._pvs['WfmLabel-RB'].wait_for_connection(timeout=self._connection_timeout)

        # add callback
        uuid = _uuid.uuid4()
        self._pvs['PwrState-Sel'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['PwrState-Sts'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['OpMode-Sel'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['OpMode-Sts'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Current-SP'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Current-RB'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['CurrentRef-Mon'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['Current-Mon'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmIndex-Mon'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmLabels-Mon'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmLabel-SP'].add_callback(callback=self._mycallback, index=uuid)
        self._pvs['WfmLabel-RB'].add_callback(callback=self._mycallback, index=uuid)

    def _mycallback(self, pvname, value, **kwargs):
        if self._callback is None:
            return
        else:
            self._callback(pvname=pvname, value=value, **kwargs)

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, value):
        self._callback = value

    @property
    def wfmindex(self):
        return self._pvs['WfmIndex-Mon'].get(timeout=self._connection_timeout)

    @property
    def wfmlabels(self):
        return self._pvs['WfmLabels-Mon'].get(timeout=self._connection_timeout)

    @property
    def wfmlabel(self):
        return self._pvs['WfmLabel-RB'].get(timeout=self._connection_timeout)

    @property
    def pwrstate_sel(self):
        return self._pvs['PwrState-Sel'].get(timeout=self._connection_timeout)

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        if value not in _et.values('OffOnTyp'): raise Exception('Invalid value of pwrstate_sel')
        if value != self.pwrstate_sel or value != self.pwrstate_sts:
            self._pvs['PwrState-Sel'].value = value
            self._update_state()

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
            self._update_state()

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
            self._update_state()

    @property
    def current_rb(self):
        return self._pvs['Current-RB'].get(timeout=self._connection_timeout)

    @property
    def current_ref(self):
        return self._pvs['CurrentRef-Mon'].get(timeout=self._connection_timeout)

    @property
    def current_load(self):
        return self._pvs['Current-Mon'].get(timeout=self._connection_timeout)

# class ControllerEpics(Controller):
#
#     def __init__(self, ps_name,           # power supply name
#                        current_min=None,  # mininum current setpoint value
#                        current_max=None,  # maximum current setpoint value
#                        callback=None,
#                        connection_timeout=_connection_timeout
#                        ):
#
#         self._ps_name = ps_name
#         self._current_min = current_min
#         self._current_max = current_max
#         self._callback = callback
#         self._connection_timeout = connection_timeout
#         self._create_epics_pvs()
#
#     def _create_epics_pvs(self):
#         self._pvs = {}
#         pv = self._ps_name
#         self._pvs['PwrState-Sel'] = _PV(pv + ':PwrState-Sel', connection_timeout=self._connection_timeout)
#         self._pvs['PwrState-Sts'] = _PV(pv + ':PwrState-Sts', connection_timeout=self._connection_timeout)
#         self._pvs['OpMode-Sel']   = _PV(pv + ':OpMode-Sel', connection_timeout=self._connection_timeout)
#         self._pvs['OpMode-Sts']   = _PV(pv + ':OpMode-Sts', connection_timeout=self._connection_timeout)
#         self._pvs['Current-SP']   = _PV(pv + ':Current-SP', connection_timeout=self._connection_timeout)
#         self._pvs['Current-RB']   = _PV(pv + ':Current-RB', connection_timeout=self._connection_timeout)
#         self._pvs['PwrState-Sel'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['PwrState-Sts'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['OpMode-Sel'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['OpMode-Sts'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['Current-SP'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['Current-RB'].wait_for_connection(timeout=self._connection_timeout)
#         # add callback
#         uuid = _uuid.uuid4()
#         self._pvs['PwrState-Sel'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['PwrState-Sts'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['OpMode-Sel'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['OpMode-Sts'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['Current-SP'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['Current-RB'].add_callback(callback=self._mycallback, index=uuid)
#
#     def _mycallback(self, pvname, value, **kwargs):
#         if self._callback is None:
#             return
#         else:
#             self._callback(pvname=pvname, value=value, **kwargs)
#
#     @property
#     def pwrstate_sel(self):
#         return self._pvs['PwrState-Sel'].get(timeout=self._connection_timeout)
#
#     @pwrstate_sel.setter
#     def pwrstate_sel(self, value):
#         if value not in _et.values('OffOnTyp'): raise Exception('Invalid value of pwrstate_sel')
#         if value != self.pwrstate_sel or value != self.pwrstate_sts:
#             self._pvs['PwrState-Sel'].value = value
#             self.update_state()
#
#     @property
#     def pwrstate_sts(self):
#         return self._pvs['PwrState-Sts'].get(timeout=self._connection_timeout)
#
#     @property
#     def opmode_sel(self):
#         return self._pvs['OpMode-Sel'].get(timeout=self._connection_timeout)
#
#     @opmode_sel.setter
#     def opmode_sel(self, value):
#         if value not in _et.values('PSOpModeTyp'): raise Exception('Invalid value of opmode_sel')
#         if value != self.opmode_sts:
#             self._pvs['OpMode-Sel'].value = value
#             self.update_state()
#
#     @property
#     def opmode_sts(self):
#         return self._pvs['OpMode-Sts'].get(timeout=self._connection_timeout)
#
#     @property
#     def current_sp(self):
#         return self._pvs['Current-SP'].get(timeout=self._connection_timeout)
#
#     @current_sp.setter
#     def current_sp(self, value):
#         value = self._check_current_ref_limits(value)
#         if value != self.current_sp:
#             self._pvs['Current-SP'].value = value
#             self.update_state()
#
#     @property
#     def current_rb(self):
#         return self._pvs['Current-RB'].get(timeout=self._connection_timeout)
#
#     def _update_opmode_slowref(self):
#         pass
#
#     def _update_opmode_fastref(self):
#         pass
#
#     def _update_opmode_wfmref(self):
#         pass
#
#     def _update_opmode_siggen(self):
#         pass
#
#     def timing_trigger(self):
#         pass
#
#     def update_state(self):
#         """Method that update controller state. It implements most of the
#         controller logic regarding the interdependency of the controller
#         properties."""
#         pass




# class ControllerSim(Controller):
#
#     def __init__(self, current_min=None,     # mininum current setpoint value
#                        current_max=None,     # maximum current setpoint value
#                        current_std=_current_st,
#                        callback=None,
#                        ):
#         # process constructor arguments
#         self._callback = callback
#         self._current_min = current_min
#         self._current_max = current_max
#         self._current_std = current_std
#         self._init()
#
#     def _init(self):
#         # power state
#         self._pwrstate = _et.idx.Off
#         # operation mode
#         self._opmode = _et.idx.SlowRef
#         # current control
#         self._current_sp  = _current_sp_init
#         self._current_ref = self._current_sp
#         self._current_load = self._current_ref
#         # commands and signals
#         self._abort_flag    = False
#         self._trigger_timeout = False
#         self._abort_counter = 0
#         self._reset_counter = 0
#         # timestamps
#         now = _time.time()
#         self._timestamp_pwrstate = now # last time pwrstate was changed
#         self._timestamp_opmode   = now # last time opmode was changed
#         self._timestamp_trigger  = now # last time trigger received
#         # waveforms
#         self._init_waveforms()
#
#
#     @property
#     def abort(self):
#         return self._abort_counter
#
#     @abort.setter
#     def abort(self, value):
#         self._abort_counter += 1
#         self._mycallback(pvname='abort')
#         self.update_state(abort_signal = True)
#
#     @property
#     def reset(self):
#         return self._reset_counter
#
#     @reset.setter
#     def reset(self, value):
#         self._reset_counter += 1
#         self._mycallback(pvname='reset')
#         self.update_state(reset_signal = True)
#
#
#     def update_current_fofb(self, value):
#         self._update_current_ref(value)
#
#
#     def _update_opmode_syncref(self, trigger_signal, abort_signal, reset_signal):
#         if abort_signal:
#             self.opmode = _et.idx.SlowRef
#         elif trigger_signal:
#             self._update_current_ref(self._current_sp)
#
#     def _update_opmode_fastref(self):
#         value = _random.unform(self._current_min, self._current_max)
#         self.update_current_fofb(value)
#
#     def _update_opmode_rmpmultwfm(self, trigger_signal, abort_signal, reset_signal):
#         if abort_signal:
#             self._abort_flag = True # it flags so that abort is implemented at end of scan.
#         if trigger_signal:
#             now = _time.time()
#             timeout_flag = (now - self._timestamp_trigger) > _trigger_timeout
#             if timeout_flag:
#                 self._wfmpointer = 0
#             else:
#                 wfm = self._waveforms[self._wfmload_slot]
#                 self._wfmpointer = (self._wfmpointer + 1) % wfm.nr_points
#             if self._wfmpointer == 0 and self._abort_flag:
#                 # end of ramp and abort issued
#                 self._abort_flag = False
#                 self.opmode = _et.idx.SlowRef
#             else:
#                 scan_value = wfm[self._wfmpointer]
#                 self._update_current_ref(scan_value)



# class OldController:
#
#     def __init__(self):
#         pass
#
#     def __str__(self):
#         st = '--- Controller ---\n'
#         propty = 'pwrstate_sel';        st +=   '{0:<20s}: {1}'.format(propty, _et.key('OffOnTyp', self.pwrstate_sel))
#         propty = 'pwrstate_sts';        st += '\n{0:<20s}: {1}'.format(propty, _et.key('OffOnTyp', self.pwrstate_sts))
#         propty = 'opmode_sel';          st += '\n{0:<20s}: {1}'.format(propty, _et.key('PSOpModeTyp', self.opmode_sel))
#         propty = 'opmode_sts';          st += '\n{0:<20s}: {1}'.format(propty, _et.key('PSOpModeTyp', self.opmode_sts))
#         propty = 'current_sp';          st += '\n{0:<20s}: {1}'.format(propty, self.current_sp)
#         propty = 'current_rb';          st += '\n{0:<20s}: {1}'.format(propty, self.current_rb)
#         propty = '_current_min';        st += '\n{0:<20s}: {1}'.format(propty, self._current_min)
#         propty = '_current_max';        st += '\n{0:<20s}: {1}'.format(propty, self._current_max)
#         try:
#             propty = '_timestamp_pwrstate'; st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_pwrstate))
#             propty = '_timestamp_opmode';   st += '\n{0:<20s}: {1}'.format(propty, _get_timestamp(self._timestamp_opmode))
#         except:
#             pass
#
#         return st
#
#     def _check_current_ref_limits(self, value):
#         value = value if self._current_min is None else max(value,self._current_min)
#         value = value if self._current_max is None else min(value,self._current_max)
#         return value
#
#     def set_callback(self, callback):
#         self._callback = callback
#
# class ControllerSim(Controller):
#
#     def __init__(self, current_min=None,     # mininum current setpoint value
#                        current_max=None,     # maximum current setpoint value
#                        waveform=None,        # wafeform used in WfmRef mode
#                        error_std=_error_std,
#                        callback=None,
#                        ):
#
#         self._current_min = current_min
#         self._current_max = current_max
#         self._error_std = error_std
#         # waveform
#         if waveform is None:
#             waveform = _PSWaveForm.wfm_constant(2000,value=0.0)
#         self._waveform = waveform
#         self._waveform_step = 0
#         # timestamps
#         now = _time.time()
#         self._timestamp_pwrstate = now
#         self._timestamp_opmode   = now
#         # internal state
#         self._pwrstate = _Off
#         self._opmode = _SlowRef
#         self._current_sp = 0.0
#         self._current_rb = 0.0
#         # callback functions
#         self._callback = callback
#
#     @property
#     def pwrstate_sel(self):
#         return self._pwrstate
#
#     @pwrstate_sel.setter
#     def pwrstate_sel(self, value):
#         if value not in _et.values('OffOnTyp'): raise Exception('Invalid value of pwrstate_sel')
#         if value != self._pwrstate:
#             self._timestamp_pwrstate = _time.time()
#             self._pwrstate = value
#             self._mycallback(pvname='PwrState-Sel')
#             self.update_state()
#
#     @property
#     def pwrstate_sts(self):
#         return self._pwrstate
#
#     @property
#     def opmode_sel(self):
#         return self._opmode
#
#     @opmode_sel.setter
#     def opmode_sel(self, value):
#         if value not in _et.values('PSOpModeTyp'): raise Exception('Invalid value of opmode_sel')
#         if value != self._opmode:
#             self._timestamp_opmode = _time.time()
#             self._opmode = value
#             self._mycallback(pvname='OpMode-Sel')
#             self.update_state()
#
#     @property
#     def opmode_sts(self):
#         return self._opmode
#
#     @property
#     def current_sp(self):
#         return self._current_sp
#
#     @current_sp.setter
#     def current_sp(self, value):
#         value = self._check_current_ref_limits(value)
#         if value != self._current_sp:
#             self._current_sp = value
#             self._mycallback(pvname='Current-SP')
#             self.update_state()
#
#     @property
#     def current_rb(self):
#         return self._current_rb
#
#     def _mycallback(self, pvname):
#         if self._callback is None:
#             return
#         elif pvname in ('PwrState-Sel','PwrState-Sts'):
#             self._callback(pvname='PwrState-Sel', value=self._pwrstate)
#             self._callback(pvname='PwrState-Sts', value=self._pwrstate)
#         elif pvname in ('OpMode-Sel','OpMode-Sts'):
#             self._callback(pvname='OpMode-Sel', value=self._opmode)
#             self._callback(pvname='OpMode-Sts', value=self._opmode)
#         elif pvname == 'Current-SP':
#             self._callback(pvname='Current-SP', value=self._current_sp)
#         elif pvname == 'Current-RB':
#             self._callback(pvname='Current-RB', value=self._current_rb)
#
#     def _update_opmode_slowref(self):
#         self._current_rb = _random.gauss(self._current_sp, self._error_std)
#         self._mycallback(pvname='Current-RB')
#
#     def _update_opmode_fastref(self):
#         self._current_rb = _random.unform(self.current_min, self.current_max)
#         self._mycallback(pvname='Current-RB')
#
#     def _update_opmode_wfmref(self):
#         pass
#
#     def _update_opmode_siggen(self):
#         if self._opmode == _SigGen:
#             dt = (_time.time() - self._timestamp_opmode) % 20
#             value = self._current_min + (self._current_max-self._current_min) * _math.exp(-dt/10.0) * _math.cos(2*_math.pi*dt/1.0) ** 2
#             self._current_rb = _random.gauss(value, self._error_std)
#             self._mycallback(pvname='Current-RB')
#
#     def timing_trigger(self):
#         if self._opmode == _WfmRef:
#             ramp_value = self._waveform_step = (self._waveform_step + 1) % self._waveform.nr_points
#             self._current_rb = _random.gauss(ramp_value, self._error_std)
#             self._mycallback(pvname='Current-RB')
#
#     def update_state(self):
#         """Method that update controller state. It implements most of the
#         controller logic regarding the interdependency of the controller
#         properties."""
#         if self.pwrstate_sts == _Off:
#             if self._current_rb != 0.0:
#                 self._current_rb = 0.0
#                 self._mycallback(pvname='Current-RB')
#         elif self.pwrstate_sts == _On:
#             opmode = self.opmode_sts
#             if opmode == _SlowRef:
#                 self._update_opmode_slowref()
#             elif opmode == _FastRef:
#                 self._update_opmode_fastref()
#             elif opmode == _WfmRef:
#                 self._update_opmode_wfmref()
#             elif opmode == _SigGen:
#                 self._update_opmode_siggen()
#             else:
#                 raise Exception('Invalid controller OpMode-Sts!')
#         else:
#             raise Exception('Invalid controller PwrState-Sts!')
#


# class ControllerEpicsLinkedPair(Controller):
#
#     def __init__(self, ps_name,           # power supply name
#                        current_min=None,  # mininum current setpoint value
#                        current_max=None,  # maximum current setpoint value
#                        callback=None,
#                        connection_timeout=_connection_timeout
#                        ):
#
#         self._ps_name = ps_name
#         self._current_min = current_min
#         self._current_max = current_max
#         self._callback = callback
#         self._connection_timeout = connection_timeout
#         self._create_epics_pvs()
#
#     def _create_epics_pvs(self):
#         uuid = _uuid.uuid4()
#         self._pvs = {}
#         pv1 = self._ps_name + '-1'
#         pv2 = self._ps_name + '-2'
#         self._pvs['1:PwrState-Sel'] = _PV(pv1 + ':PwrState-Sel', connection_timeout=self._connection_timeout)
#         self._pvs['1:PwrState-Sts'] = _PV(pv1 + ':PwrState-Sts', connection_timeout=self._connection_timeout)
#         self._pvs['1:OpMode-Sel']   = _PV(pv1 + ':OpMode-Sel', connection_timeout=self._connection_timeout)
#         self._pvs['1:OpMode-Sts']   = _PV(pv1 + ':OpMode-Sts', connection_timeout=self._connection_timeout)
#         self._pvs['1:Current-SP']   = _PV(pv1 + ':Current-SP', connection_timeout=self._connection_timeout)
#         self._pvs['1:Current-RB']   = _PV(pv1 + ':Current-RB', connection_timeout=self._connection_timeout)
#         self._pvs['2:PwrState-Sel'] = _PV(pv2 + ':PwrState-Sel', connection_timeout=self._connection_timeout)
#         self._pvs['2:PwrState-Sts'] = _PV(pv2 + ':PwrState-Sts', connection_timeout=self._connection_timeout)
#         self._pvs['2:OpMode-Sel']   = _PV(pv2 + ':OpMode-Sel', connection_timeout=self._connection_timeout)
#         self._pvs['2:OpMode-Sts']   = _PV(pv2 + ':OpMode-Sts', connection_timeout=self._connection_timeout)
#         self._pvs['2:Current-SP']   = _PV(pv2 + ':Current-SP', connection_timeout=self._connection_timeout)
#         self._pvs['2:Current-RB']   = _PV(pv2 + ':Current-RB', connection_timeout=self._connection_timeout)
#         self._pvs['1:PwrState-Sel'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['1:PwrState-Sts'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['1:OpMode-Sel'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['1:OpMode-Sts'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['1:Current-SP'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['1:Current-RB'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['2:PwrState-Sel'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['2:PwrState-Sts'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['2:OpMode-Sel'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['2:OpMode-Sts'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['2:Current-SP'].wait_for_connection(timeout=self._connection_timeout)
#         self._pvs['2:Current-RB'].wait_for_connection(timeout=self._connection_timeout)
#         # add callback
#         self._pvs['1:PwrState-Sel'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['1:PwrState-Sts'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['1:OpMode-Sel'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['1:OpMode-Sts'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['1:Current-SP'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['1:Current-RB'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['2:PwrState-Sel'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['2:PwrState-Sts'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['2:OpMode-Sel'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['2:OpMode-Sts'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['2:Current-SP'].add_callback(callback=self._mycallback, index=uuid)
#         self._pvs['2:Current-RB'].add_callback(callback=self._mycallback, index=uuid)
#
#     def _mycallback(self, pvname, value, **kwargs):
#         if self._callback is None:
#             return
#         else:
#             sec, dev, propty = pvname.split(':')
#             tmp = dev.split('-'); dev = '-'.join(tmp[:-1])
#             pvname = ':'.join(sec,dev,propty)
#             self._callback(pvname=pvname, value=value, **kwargs)
#
#     @property
#     def pwrstate_sel(self):
#         v1 = self._pvs['1:PwrState-Sel'].get(timeout=self._connection_timeout)
#         v2 = self._pvs['2:PwrState-Sel'].get(timeout=self._connection_timeout)
#         return min(v1,v2) # if any ps is 'off', return 'off'
#
#     @pwrstate_sel.setter
#     def pwrstate_sel(self, value):
#         if value not in _et.values('OffOnTyp'): raise Exception('Invalid value of pwrstate_sel')
#         v1_sel = self._pvs['1:PwrState-Sel'].get(timeout=self._connection_timeout)
#         v1_sts = self._pvs['1:PwrState-Sts'].get(timeout=self._connection_timeout)
#         v2_sel = self._pvs['2:PwrState-Sel'].get(timeout=self._connection_timeout)
#         v2_sts = self._pvs['2:PwrState-Sts'].get(timeout=self._connection_timeout)
#         need_updating = False
#         if value != v1_sel or value != v1_sts:
#             self._pvs['1:PwrState-Sel'].value = value
#             need_updating = True
#         if value != v2_sel or value != v2_sts:
#             self._pvs['2:PwrState-Sel'].value = value
#             need_updating = True
#         if need_updating:
#             self.update_state()
#
#     @property
#     def pwrstate_sts(self):
#         v1 = self._pvs['1:PwrState-Sts'].get(timeout=self._connection_timeout)
#         v2 = self._pvs['2:PwrState-Sts'].get(timeout=self._connection_timeout)
#         return min(v1,v2) # if any ps is 'off', return 'off'
#
#     @property
#     def opmode_sel(self):
#         v1 = self._pvs['1:OpMode-Sel'].get(timeout=self._connection_timeout)
#         v2 = self._pvs['2:OpMode-Sel'].get(timeout=self._connection_timeout)
#         return max(v1,v2) # returns most complex mode, supposing enum is ordered in complexity
#
#     @opmode_sel.setter
#     def opmode_sel(self, value):
#         if value not in _et.values('PSOpModeTyp'): raise Exception('Invalid value of opmode_sel')
#         v1_sel = self._pvs['1:OpMode-Sel'].get(timeout=self._connection_timeout)
#         v1_sts = self._pvs['1:OpMode-Sts'].get(timeout=self._connection_timeout)
#         v2_sel = self._pvs['2:OpMode-Sel'].get(timeout=self._connection_timeout)
#         v2_sts = self._pvs['2:OpMode-Sts'].get(timeout=self._connection_timeout)
#         need_updating = False
#         if value != v1_sel or value != v1_sts:
#             self._pvs['1:OpMode-Sel'].value = value
#             need_updating = True
#         if value != v2_sel or value != v2_sts:
#             self._pvs['2:OpMode-Sel'].value = value
#             need_updating = True
#         if need_updating:
#             self.update_state()
#
#
#     @property
#     def opmode_sts(self):
#         v1 = self._pvs['1:OpMode-Sts'].get(timeout=self._connection_timeout)
#         v2 = self._pvs['2:OpMode-Sts'].get(timeout=self._connection_timeout)
#         return max(v1,v2) # returns most complex mode, supposing enum is ordered in complexity
#
#
#     @property
#     def current_sp(self):
#         v1 = self._pvs['1:Current-SP'].get(timeout=self._connection_timeout)
#         v2 = self._pvs['2:Current-SP'].get(timeout=self._connection_timeout)
#         return min(v1,v2) # returns minimum current setpoint value
#
#     @current_sp.setter
#     def current_sp(self, value):
#         value = self._check_current_ref_limits(value)
#         v1 = self._pvs['1:Current-SP'].get(timeout=self._connection_timeout)
#         v2 = self._pvs['2:Current-SP'].get(timeout=self._connection_timeout)
#         need_updating = False
#         if value != v1:
#             self._pvs['1:Current-SP'].value = value
#             need_updating = True
#         if value != v2:
#             self._pvs['2:Current-SP'].value = value
#             need_updating = True
#         if need_updating:
#             self.update_state()
#
#     @property
#     def current_rb(self):
#         v1 = self._pvs['1:Current-RB'].get(timeout=self._connection_timeout)
#         v2 = self._pvs['2:Current-RB'].get(timeout=self._connection_timeout)
#         return (v1+v2)/2.0 # in this case, return average of two measurements
#
#     def _update_opmode_slowref(self):
#         pass
#
#     def _update_opmode_fastref(self):
#         pass
#
#     def _update_opmode_wfmref(self):
#         pass
#
#     def _update_opmode_siggen(self):
#         pass
#
#     def timing_trigger(self):
#         pass
#
#     def update_state(self):
#         """Method that update controller state. It implements most of the
#         controller logic regarding the interdependency of the controller
#         properties."""
#         pass
#
# class ControllerPyaccel(Controller):
#     """Controller PyEpics model.
#
#     (pending!)
#     This pure virtual class implements basic functionality of a controller that
#     gets its internal state from an accelerator Pyaccel model. The class is
#     supposed to be subclasses elsewhere.
#     """
#     pass
