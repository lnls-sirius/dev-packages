"""Power Supply Models."""

import copy as _copy
import time as _time
import uuid as _uuid
import numpy as _np
import threading as _threading
import collections as _collections
from epics import PV as _PV
from siriuspy import envars as _envars
# from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.pwrsupply_orig.data import PSData as _PSData
from siriuspy.pwrsupply_orig.controller import ControllerSim as _ControllerSim
from siriuspy.pwrsupply_orig.controller import ControllerEpics as \
    _ControllerEpics
from numpy import ndarray as _ndarray


class PowerSupply(_PSData):

    def __init__(self, psname,
                       controller=None,
                       callback=None,
                       current_std=0.0,
                       enum_keys=False):

        #self._psdata = _PSData(psname=psname)
        super().__init__(psname=psname)
        self._enum_keys = enum_keys
        self._ctrlmode_mon = _et.idx.Remote
        self._controller = controller
        self._callbacks = {} if callback is None else {_uuid.uuid4():callback}
        self._controller_init(current_std)

    # --- class interface ---

    def update_state(self):
        self._controller.update_state()

    def add_callback(self, callback, index=None):
        index = _uuid.uuid4() if index is None else index
        self._callbacks[index] = callback
        return index

    def remove_callback(self, index):
        if index in self._callbacks:
            del self._callbacks[index]

    def clear_callbacks(self):
        self._callbacks.clear()

    @property
    def connected(self):
        return self._get_connected()

    @property
    def splims(self):
        return _copy.deepcopy(self._splims)

    @property
    def database(self):
        return self._get_database()

    @property
    def ctrlmode_mon(self):
        return self._eget('RmtLocTyp', self._ctrlmode_mon)

    def set_ctrlmode(self, value):
        value = self._eget('RmtLocTyp', value, enum_keys=False)
        if value is not None:
            self._ctrlmode_mon = value

    @property
    def opmode_sel(self):
        return self._eget('PSOpModeTyp', self._opmode_sel)

    @opmode_sel.setter
    def opmode_sel(self, value):
        if self._ctrlmode_mon != _et.idx.Remote: return
        value = self._eget('PSOpModeTyp', value, enum_keys=False)
        if value is not None and value != self.opmode_sts:
            self._opmode_sel = value
            self._set_opmode_sel(value)

    @property
    def opmode_sts(self):
        return self._get_opmode_sts()

    @property
    def reset(self):
        return self._controller.reset_counter

    @reset.setter
    def reset(self,value):
        self._controller.reset()

    @property
    def abort(self):
        return self._controller.abort_counter

    @abort.setter
    def abort(self,value):
        self._controller.abort()

    @property
    def pwrstate_sel(self):
        return self._eget('OffOnTyp', self._pwrstate_sel)

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        if self._ctrlmode_mon != _et.idx.Remote: return
        value = self._eget('OffOnTyp', value, enum_keys=False)
        if value is not None and value != self.pwrstate_sts:
            self._pwrstate_sel = value
            self._set_pwrstate_sel(value)

    @property
    def pwrstate_sts(self):
        return self._eget('OffOnTyp', self._controller.pwrstate)

    @property
    def current_sp(self):
        return self._current_sp

    @current_sp.setter
    def current_sp(self, value):
        #print('[PSL] [setter] current_sp ', value)
        if self._ctrlmode_mon != _et.idx.Remote: return
        #if value not in (self.current_sp, self.current_rb):

        #if value != self.current_rb or value != self._current_sp:
        # if value != self._current_sp:
        #     self._current_sp = value
        #     self._set_current_sp(value)

        self._current_sp = value
        self._set_current_sp(value)

    @property
    def current_rb(self):
        return self._get_current_rb()

    @property
    def currentref_mon(self):
        return self._get_currentref_mon()

    @property
    def current_mon(self):
        return self._controller.current_load

    @property
    def intlk_mon(self):
        return self._controller.intlk

    @property
    def intlklabels_cte(self):
        return self._controller.intlklabels

    # --- class implementation ---

    @property
    def wfmindex_mon(self):
        return self._get_wfmindex_mon()

    @property
    def wfmlabels_mon(self):
        return self._get_wfmlabels_mon()

    @property
    def wfmlabel_sp(self):
        return self._wfmlabel_sp

    @property
    def wfmlabel_rb(self):
        return self._get_wfmlabel_rb()

    @wfmlabel_sp.setter
    def wfmlabel_sp(self, value):
        if self._ctrlmode_mon != _et.idx.Remote: return
        if value != self.wfmlabel_rb:
            self._wfmlabel_sp = value
            self._set_wfmlabel_sp(value)

    @property
    def wfmdata_sp(self):
        return _np.array(self._wfmdata_sp)

    @property
    def wfmdata_rb(self):
        return self._get_wfmdata_rb()

    @wfmdata_sp.setter
    def wfmdata_sp(self, value):
        if self._ctrlmode_mon != _et.idx.Remote: return
        value = _np.array(value)
        if (value != self.wfmdata_rb).any():
            self._wfmdata_sp = _np.array(value)
            self._set_wfmdata_sp(value)

    @property
    def wfmload_sel(self):
        slot = self._wfmload_sel
        if not self._enum_keys:
            return slot
        else:
            wfmlabels = self._get_wfmlabels_mon()
            return wfmlabels[slot]

    @wfmload_sel.setter
    def wfmload_sel(self, value):
        if self._ctrlmode_mon != _et.idx.Remote: return
        wfmlabels = self._get_wfmlabels_mon()
        #slot = _np.where(wfmlabels == value)[0][0] if self._enum_keys else value

        if self._enum_keys:
            if not isinstance(value, str):
                raise ValueError("Type must be str, not {}".format(type(value)))
            if value not in wfmlabels:
                raise KeyError("There is no waveform name {}".format(value))
            slot = _np.where(wfmlabels == value)[0][0]
        else:
            if not isinstance(value, int):
                raise ValueError("Type must be int, not {}".format(type(value)))
            slot = value

        self._wfmload_sel = slot
        self._set_wfmload_sel(slot)

    @property
    def wfmload_sts(self):
        slot = self._get_wfmload_sts()
        if not self._enum_keys:
            return slot
        else:
            wfmlabels = self._get_wfmlabels_mon()
            return wfmlabels[slot]

    @property
    def wfmsave_cmd(self):
        return self._get_wfmsave_cmd()

    @wfmsave_cmd.setter
    def wfmsave_cmd(self, value):
        if self._ctrlmode_mon != _et.idx.Remote: return
        self._controller.wfmsave = value

    # --- class implementation ---

    def _controller_init(self, current_std):
        if self._controller is None:
            #lims = self._psdata.splims # set controller setpoint limits according to PS database
            lims = self._splims
            self._controller = _ControllerSim(current_min = lims['DRVL'],
                                              current_max = lims['DRVH'],
                                              callback = self._mycallback,
                                              current_std = current_std,
                                              psname=self.psname)

            self._pwrstate_sel = self.propty_database['PwrState-Sel']['value']
            self._opmode_sel   = self.propty_database['OpMode-Sel']['value']
            self._current_sp   = self.propty_database['Current-SP']['value']
            self._wfmlabel_sp  = self._controller.wfmlabel
            self._wfmload_sel  = self.propty_database['WfmLoad-Sel']['value']
            self._wfmdata_sp   = self.propty_database['WfmData-SP']['value']
            self._controller.pwrstate   = self._pwrstate_sel
            self._controller.opmode     = self._opmode_sel
            self._controller.current_sp = self._current_sp
            self._controller.wfmload    = self._wfmload_sel
            self._controller.wfmdata_sp = self._wfmdata_sp
        else:
            self._pwrstate_sel = self._controller.pwrstate
            self._opmode_sel   = self._controller.opmode
            self._current_sp   = self._controller.current_sp
            self._wfmlabel_sp  = self._controller.wfmlabel
            self._wfmload_sel  = self._controller.wfmload
            self._wfmdata_sp   = self._controller.wfmdata

        self._callback_index = self._controller.add_callback(self._mycallback)
        self._controller.update_state()

    def _get_database(self):
        """Return an updated  PV database whose keys correspond to PS properties."""
        db = self.propty_database
        value = self.ctrlmode_mon; db['CtrlMode-Mon']['value'] = _et.enums('RmtLocTyp').index(value) if self._enum_keys else value
        value = self.opmode_sel;   db['OpMode-Sel']['value'] = _et.enums('PSOpModeTyp').index(value) if self._enum_keys else value
        value = self.opmode_sts;   db['OpMode-Sts']['value'] = _et.enums('PSOpModeTyp').index(value) if self._enum_keys else value
        value = self.pwrstate_sel; db['PwrState-Sel']['value'] = _et.enums('OffOnTyp').index(value) if self._enum_keys else value
        value = self.pwrstate_sts; db['PwrState-Sts']['value'] = _et.enums('OffOnTyp').index(value) if self._enum_keys else value
        db['Reset-Cmd']['value'] = self.reset
        db['Abort-Cmd']['value'] = self.abort
        wfmlabels = self._get_wfmlabels_mon()
        db['WfmLoad-Sel']['enums'] = wfmlabels
        db['WfmLoad-Sts']['enums'] = wfmlabels
        value = self.wfmload_sel;  db['WfmLoad-Sel']['value'] = _np.where(wfmlabels == value)[0][0] if self._enum_keys else value
        value = self.wfmload_sts;  db['WfmLoad-Sts']['value'] = _np.where(wfmlabels == value)[0][0] if self._enum_keys else value
        db['WfmLabel-SP']['value']    = self.wfmlabel_sp
        db['WfmLabel-RB']['value']    = self.wfmlabel_rb
        db['WfmLabels-Mon']['value']  = self.wfmlabels_mon
        db['WfmData-SP']['value']     = self.wfmdata_sp
        db['WfmData-RB']['value']     = self.wfmdata_rb
        db['WfmSave-Cmd']['value']    = self.wfmsave_cmd
        db['WfmIndex-Mon']['value']   = self.wfmindex_mon
        db['Current-SP']['value']     = self.current_sp
        db['Current-RB']['value']     = self.current_rb
        db['CurrentRef-Mon']['value'] = self.currentref_mon
        db['Current-Mon']['value']    = self.current_mon
        db['Intlk-Mon']['value']      = self.intlk_mon
        return db

    def _get_connected(self):
        if isinstance(self._controller, _ControllerEpics):
            return self._controller.connected
        else:
            return True

    def _set_opmode_sel(self, value):
        self._controller.opmode = value

    def _get_opmode_sts(self):
        return self._eget('PSOpModeTyp',self._controller.opmode)

    def _set_pwrstate_sel(self, value):
            self._pwrstate_sel = value
            self._controller.pwrstate = value

    def _set_current_sp(self, value):
            self._pwrstate_sp = value
            self._controller.current_sp = value

    def _get_current_rb(self):
        return self._controller.current_sp

    def _get_currentref_mon(self):
        return self._controller.current_ref

    def _get_wfmindex_mon(self):
        return self._controller.wfmindex

    def _get_wfmlabels_mon(self):
        return self._controller.wfmlabels

    def _get_wfmlabel_rb(self):
        return self._controller.wfmlabel

    def _set_wfmlabel_sp(self, value):
        self._controller.wfmlabel = value

    def _get_wfmdata_rb(self):
        return _np.array(self._controller.wfmdata)

    def _set_wfmdata_sp(self, value):
        self._controller.wfmdata = value

    def _get_wfmload_sts(self):
        return self._controller.wfmload

    def _set_wfmload_sel(self, value):
        self._controller.wfmload = value

    def _get_wfmsave_cmd(self):
        return self._controller.wfmsave

    # --- class private methods ---

    def _eget(self,typ,value,enum_keys=None):
        enum_keys = self._enum_keys if enum_keys is None else enum_keys
        try:
            if enum_keys:
                if isinstance(value, str):
                    return value
                else:
                    return _et.conv_idx2key(typ, value)
            else:
                if isinstance(value, str):
                    return _et.conv_key2idx(typ, value)
                else:
                    return value
        except:
            return None

    def _mycallback(self, pvname, value, **kwargs):
        if isinstance(self._controller, _ControllerEpics):
            #print('[PS] [callback] ', pvname, value)
            if 'CtrlMode-Mon' in pvname:
                self._ctrlmode_mon = value
            elif 'OpMode-Sel' in pvname:
                self._opmode_sel   = value
            elif 'PwrState-Sel' in pvname:
                self._pwrstate_sel = value
            elif 'WfmLoad-Sel' in pvname:
                self._wfmload_sel  = value
            elif 'WfmLabel-SP' in pvname:
                self._wfmlabel_sp  = value
            elif 'WfmData-SP' in pvname:
                self._wfmdata_sp   = value
            elif 'Current-SP' in pvname:
                self._current_sp   = value

            for callback in self._callbacks.values():
                callback(pvname,value,**kwargs)

        elif isinstance(self._controller, _ControllerSim):
            for callback in self._callbacks.values():
                if pvname == 'opmode':
                    callback(self.psname + ':OpMode-Sts', value, **kwargs)
                elif pvname == 'pwrstate':
                    callback(self.psname + ':PwrState-Sts', value, **kwargs)
                elif pvname == 'wfmload':
                    callback(self.psname + ':WfmLoad-Sel', value, **kwargs)
                elif pvname == 'wfmlabel':
                    callback(self.psname + ':WfmLabel-RB', value, **kwargs)
                elif pvname == 'wfmdata':
                    callback(self.psname + ':WfmLoad-Sel', value, **kwargs)
                elif pvname == 'current_sp':
                    callback(self.psname + ':Current-RB', value, **kwargs)
                elif pvname == 'current_ref':
                    callback(self.psname + ':CurrentRef-Mon', value, **kwargs)
                elif pvname == 'current_load':
                    callback(self.psname + ':Current-Mon', value, **kwargs)
                elif pvname == 'abort':
                    callback(self.psname + ':Abort-Cmd', value, **kwargs)
                elif pvname == 'reset':
                    callback(self.psname + ':Reset-Cmd', value, **kwargs)


class PowerSupplySim(PowerSupply):

    def __init__(self,
                 psname,
                 controller=None,
                 current_std=0.0,
                 enum_keys=False,
                 **kwargs):

        super().__init__(psname=psname,
                         controller=controller,
                         current_std=current_std,
                         enum_keys=enum_keys
                         )


class PowerSupplyEpicsSync:

    class PVsPutThread:
        """Class for objects responsible to manage communication queue."""

        def __init__(self, pvs_dict, get_disconnect_state):
            """Init method of PVsPutThread."""
            self._pvs_dict = pvs_dict
            self._get_disconnect_state = get_disconnect_state
            self._thread = _threading.Thread(target=self.process, daemon=True)
            self._lock = _threading.Lock()
            self._sp_pvnames = _collections.deque()
            self._sp_values = _collections.deque()

        def _add_put_locked2(self, pvname, value):
            self._lock.acquire()
            try:
                try:
                    # I think I should change this to accept all puts
                    idx = self._sp_pvnames.index(pvname)
                    self._sp_values[idx] = value
                except ValueError:
                    self._sp_pvnames.append(pvname)
                    self._sp_values.append(value)
            finally:
                self._lock.release()

        def _add_put_locked(self, pvname, value):
            self._lock.acquire()
            try:
                self._sp_pvnames.append(pvname)
                self._sp_values.append(value)
            finally:
                self._lock.release()

        def _retrieve_put_locked(self):
            self._lock.acquire()
            try:
                if self._sp_pvnames:
                    pvname = self._sp_pvnames.popleft()
                    value = self._sp_values.popleft()
                else:
                    return None, None, True
            finally:
                self._lock.release()
            return pvname, value, False

        def put(self, pvname, value):
            """Put a value of a pv into queue."""
            if pvname not in self._pvs_dict:
                raise ValueError('invalid pvname "' + pvname +
                                 '" in add_setpoint')
            self._add_put_locked(pvname, value)
            if not self._thread.is_alive():
                self._thread = _threading.Thread(target=self.process,
                                                 daemon=True)
                self._thread.start()

        def process(self):
            """Process queue."""
            while not self._get_disconnect_state():
                pvname, value, empty_buffer = self._retrieve_put_locked()
                if empty_buffer:
                    break
                try:
                    if self._pvs_dict[pvname].connected:
                        # if PV is connected push put down
                        self._pvs_dict[pvname].value = value
                    else:
                        # if PV not connected move put to end of queue
                        # self._add_put_locked(pvname, value)
                        pass
                except:
                    pass

        def join(self):
            """Join thread."""
            if self._thread.is_alive():
                self._thread.join()

        @property
        def queu_length(self):
            """Return queue length."""
            self._lock.acquire()
            length = None
            try:
                length = len(self._sp_pvnames)
            finally:
                self._lock.release()
            return length

    def __init__(self,
                 psnames,
                 callback=None,
                 use_vaca=False,
                 vaca_prefix=None,
                 lock=True,
                 ):
        """Init method of PowerSupplyEpicsSync."""
        self._callbacks = {} if callback is None else {_uuid.uuid4(): callback}
        #self._enum_keys = False
        self._psnames = psnames
        self._psname_master = self._psnames[0]
        self._lock = lock
        self._disconnect = False
        self._disconnect_lock = _threading.Lock()
        self._set_vaca_prefix(use_vaca, vaca_prefix)
        self._propty_callbacks = {
            'CtrlMode-Mon':    self._callback_change_rb_pv,
            'OpMode-Sel':      self._callback_change_sp_pv,
            'OpMode-Sts':      self._callback_change_rb_pv,
            'PwrState-Sel':    self._callback_change_sp_pv,
            'PwrState-Sts':    self._callback_change_rb_pv,
            'Current-SP':      self._callback_change_sp_pv,
            'Current-RB':      self._callback_change_rb_pv,
            'CurrentRef-Mon':  self._callback_change_rb_pv,
            'Current-Mon':     self._callback_change_rb_pv,
            'Reset-Cmd':       self._callback_change_rb_pv,
            'Abort-Cmd':       self._callback_change_rb_pv,
            'WfmSave-Cmd':     self._callback_change_rb_pv,
            'WfmIndex-Mon':    self._callback_change_rb_pv,
            'WfmLabels-Mon':   self._callback_change_rb_pv,
            'WfmLabel-SP':     self._callback_change_sp_pv,
            'WfmLabel-RB':     self._callback_change_rb_pv,
            'WfmLoad-Sel':     self._callback_change_sp_pv,
            'WfmLoad-Sts':     self._callback_change_rb_pv,
            'WfmData-SP':      self._callback_change_sp_pv,
            'WfmData-RB':      self._callback_change_rb_pv,
            'Intlk-Mon':       self._callback_change_rb_pv,
            'IntlkLabels-Cte': self._callback_change_rb_pv,
        }
        self._init_propty()
        self._init_pvs()

    def _set_vaca_prefix(self, use_vaca, vaca_prefix):
        if use_vaca:
            if vaca_prefix is None:
                self._vaca_prefix = _envars.vaca_prefix
            else:
                self._vaca_prefix = vaca_prefix
        else:
            self._vaca_prefix = ''

    def _init_propty(self):
        self._propty = {propty: None for propty in self._propty_callbacks}

    def _init_pvs(self):

        self._pvs = {}
        for psname in self._psnames:
            for propty, callback in self._propty_callbacks.items():
                pvname = self._vaca_prefix + psname + ':' + propty
                self._pvs[pvname] = _PV(pvname=pvname,
                                        connection_callback=None,
                                        connection_timeout=None)

        self._put_thread = PowerSupplyEpicsSync.PVsPutThread(
                            self._pvs,
                            self._get_disconnect_state)

        for psname in self._psnames:
            for propty, callback in self._propty_callbacks.items():
                pvname = self._vaca_prefix + psname + ':' + propty
                self._pvs[pvname].add_callback(callback)

    def _conn_cb(self, pvname, conn, **kwargs):
        if conn:
            propty = pvname.split(":")[-1]
            self._trigger_callback(pvname=pvname, value=self._propty[propty])

    def wait_for_connection(self, timeout=None):
        """Wait for connection method."""
        if timeout is None:
            while True:
                if self.connected:
                    return True
                _time.sleep(0.1)
        else:
            t0 = _time.time()
            while _time.time() - t0 < timeout:
                if self.connected:
                    return True
                _time.sleep(min(timeout/2.0, 0.1))
        return False

    @property
    def connected(self):
        for _, pv in self._pvs.items():
            if not pv.connected:
                return False
        return True

    @property
    def ctrlmode_mon(self):
        return self._propty['CtrlMode-Mon']

    @property
    def opmode_sel(self):
        return self._propty['OpMode-Sel']

    @opmode_sel.setter
    def opmode_sel(self, value):
        value = int(value)
        self._put_sp_property('OpMode-Sel', value)

    @property
    def opmode_sts(self):
        return self._propty['OpMode-Sts']

    @property
    def pwrstate_sel(self):
        return self._propty['PwrState-Sel']

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        value = int(value)
        self._put_sp_property('PwrState-Sel', value)

    @property
    def pwrstate_sts(self):
        return self._propty['PwrState-Sts']

    @property
    def current_sp(self):
        return self._propty['Current-SP']

    @current_sp.setter
    def current_sp(self, value):
        self._set_current_sp(value)

    def _set_current_sp(self, value):
        value = float(value)
        self._put_sp_property('Current-SP', value)

    @property
    def current_rb(self):
        return self._propty['Current-RB']

    @property
    def currentref_mon(self):
        return self._propty['CurrentRef-Mon']

    @property
    def current_mon(self):
        return self._propty['Current-Mon']

    @property
    def reset_cmd(self):
        return self._propty['Reset-Cmd']

    @reset_cmd.setter
    def reset_cmd(self, value):
        self._put_sp_property('Reset-Cmd', value)

    @property
    def abort_cmd(self):
        return self._propty['Abort-Cmd']

    @abort_cmd.setter
    def abort_cmd(self, value):
        self._put_sp_property('Abort-Cmd', value)

    @property
    def wfmsave_cmd(self):
        return self._propty['WfmSave-Cmd']

    @wfmsave_cmd.setter
    def wfmsave_cmd(self, value):
        self._put_sp_property('WfmSave-Cmd', value)

    @property
    def wfmindex_mon(self):
        return self._propty['WfmIndex-Mon']

    @property
    def wfmlabels_mon(self):
        return self._propty['WfmLabels-Mon']

    @property
    def wfmlabel_sp(self):
        return self._propty['WfmLabel-SP']

    @wfmlabel_sp.setter
    def wfmlabel_sp(self, value):
        value = int(value)
        self._put_sp_property('WfmLabel-SP', value)

    @property
    def wfmlabel_rb(self):
        return self._propty['WfmLabel-RB']

    @property
    def wfmload_sel(self):
        return self._propty['WfmLoad-Sel']

    @wfmload_sel.setter
    def wfmload_sel(self, value):
        value = int(value)
        self._set_propty_sp('WfmLoad-Sel', value)

    @property
    def wfmload_sts(self):
        return self._propty['WfmLoad-Sts']

    @property
    def wfmdata_sp(self):
        return self._propty['WfmData-SP']

    @wfmdata_sp.setter
    def wfmdata_sp(self, value):
        value = _ndarray(value)
        self._set_propty_sp('WfmData-SP', value)

    @property
    def wfmdata_rb(self):
        return self._propty['WfmData-RB']

    @property
    def intlk_mon(self):
        return self._propty['Intlk-Mon']

    @property
    def intlklabels_cte(self):
        return self._propty['IntlkLabels-Cte']

    def _put_sp_property(self, propty, value):
        if 'Cmd' not in propty:
            self._propty[propty] = value
        for pvname, pv in self._pvs.items():
            if propty in pvname:
                disconnect = self._get_disconnect_state()
                if not disconnect:
                    self._put_thread.put(pvname=pvname, value=value)

    def _get_disconnect_state(self):
        # return self._disconnect
        self._disconnect_lock.acquire()
        try:
            disconnect = self._disconnect
        finally:
            self._disconnect_lock.release()
        return disconnect

    @property
    def callbacks(self):
        """Return callback."""
        return self._callbacks

    def add_callback(self, callback, index=None):
        """Add a callback."""
        index = _uuid.uuid4() if index is None else index
        self._callbacks[index] = callback
        return index

    def _trigger_callback(self, pvname, value, **kwargs):
        for callback in self._callbacks.values():
            callback(pvname, value, **kwargs)

    def _callback_change_sp_pv(self, pvname, value, **kwargs):
        # *parts, propty = pvname.split(':')
        # if self._propty[propty] is None:
        #     self._propty[propty] = value
        # elif value != self._propty[propty]:
        #     disconnect = self._get_disconnect_state()
        #     if not disconnect:
        #         self._put_thread.put(pvname, self._propty[propty])
        *parts, propty = pvname.split(':')
        if self._propty[propty] is None:
            # init property with value from IOC
            self._propty[propty] = value
            self._put_sp_property(propty, value)
        else:
            if isinstance(value, _ndarray):
                changed = (value != self._propty[propty]).any()
            else:
                changed = (value != self._propty[propty])
            if self._lock:
                # if value != self._propty[propty]:
                if changed:
                    disconnect = self._get_disconnect_state()
                    if not disconnect:
                        self._put_thread.put(pvname, self._propty[propty])
            else:
                # if value != self._propty[propty]:
                if changed:
                    self._propty[propty] = value
                    self._put_sp_property(propty, value)
        self._trigger_callback(pvname, value, **kwargs)

    def _callback_change_rb_pv(self, pvname, value, **kwargs):
        *parts, propty = pvname.split(':')
        self._propty[propty] = value
        self._trigger_callback(pvname, value, **kwargs)

    def process_puts(self, wait=None):
        if self.connected:
            t0 = _time.time()
            while (wait is None or (_time.time() - t0 < wait)) and self._put_thread.queu_length > 0:
                _time.sleep(0.010)
        else:
            if wait is not None:
                _time.sleep(wait)

    def disconnect(self, wait=None):
        """Disconnect PVs method."""
        # wait for synchronization
        self.process_puts(wait=wait)

        # signal disconnect triggered
        self._disconnect_lock.acquire()
        try:
            self._disconnect = True
        finally:
            self._disconnect_lock.release()

        # wait for threads to finish
        self._put_thread.join()

        # disconnect all PVs (clearing all callbacks)
        for pvname, pv in self._pvs.items():
            pv.disconnect()
