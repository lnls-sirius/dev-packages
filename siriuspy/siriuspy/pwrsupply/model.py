
import copy as _copy
import time as _time
import uuid as _uuid
import numpy as _np
import threading as _threading
from epics import PV as _PV
from siriuspy import envars as _envars
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.controller import ControllerSim as _ControllerSim
from siriuspy.pwrsupply.controller import ControllerEpics as _ControllerEpics


_connection_timeout = 0.1


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
                    return _et.key(typ, value)
            else:
                if isinstance(value, str):
                    return _et.get_idx(typ, value)
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

    wait_pv_put   = True
    sync_interval = 1.0

    def __init__(self,
                 maname,
                 use_vaca=False,
                 vaca_prefix=None,
                 lock=True,
                 callback=None,
                 thread_local=True,
                 connection_timeout=None):

        self._thread_local = thread_local
        self._callback = callback

        if self._thread_local:
            self._finish = False
            self._threads = list()

        self._maname = _SiriusPVName(maname)
        self._use_vaca = use_vaca
        self._vaca_prefix = vaca_prefix
        self._connection_timeout = connection_timeout
        self._lock = lock
        self._set_psnames()
        self._psname_master = self._psnames[0]
        #super().__init__(psname=self._psname_master)
        self._create_epics_pvs()

        if not self._thread_local:
            if self._lock:
                self._thread = _threading.Thread(target=self._force_lock)
                self._thread.start()

    @property
    def connected(self):
        for pv_dict in self._pvs.values():
            for pv in pv_dict.values():
                if not pv.connected:
                    return False
        return True

    def disconnect(self):
        if not self._thread_local:
            self._finished = True
        if self._thread_local:
            self._lock = False
            if self._threads:
                for t in self._threads:
                    if t.is_alive():
                        t.join()

    @property
    def upper_alarm_limit(self):
        return self._get_limit('upper_alarm_limit', min)

    @property
    def upper_warning_limit(self):
        return self._get_limit('upper_warning_limit', min)

    @property
    def upper_disp_limit(self):
        return self._get_limit('upper_disp_limit', min)

    @property
    def lower_disp_limit(self):
        return self._get_limit('lower_disp_limit', max)

    @property
    def lower_warning_limit(self):
        return self._get_limit('lower_warning_limit', max)

    @property
    def lower_alarm_limit(self):
        return self._get_limit('lower_alarm_limit', max)

    @property
    def maname(self):
        return self._maname

    @property
    def psnames(self):
        return tuple([psname for psname in self._psnames])

    # Current getters/setters
    @property
    def current_sp(self):
        return self._current_sp

    @property
    def current_rb(self):
        return self._current_rb

    @property
    def currentref_mon(self):
        return self._currentref_mon

    @property
    def current_mon(self):
        return self._current_mon

    @current_sp.setter
    def current_sp(self, value):
        self._set_current_sp(value)

    def _set_current_sp(self, value):
        if not self._thread_local:
            self._lock = False
        self._current_sp = value
        for psname, pv in self._pvs['Current-SP'].items():
            pv.put(self._current_sp, wait=PowerSupplyEpicsSync.wait_pv_put)
        if not self._thread_local:
            self._lock = True

    @current_rb.setter
    def current_rb(self, value):
        raise NotImplementedError

    @currentref_mon.setter
    def currentref_mon(self, value):
        raise NotImplementedError

    @current_mon.setter
    def current_mon(self, value):
        raise NotImplementedError

    #OpMode getter/setter
    @property
    def opmode_sel(self):
        return self._opmode_sel

    @opmode_sel.setter
    def opmode_sel(self, value):
        self._set_opmode_sel(value)

    def _set_opmode_sel(self, value):
        if not self._thread_local:
            self._lock = False
        self._opmode_sel = value
        for psname, pv in self._pvs['OpMode-Sel'].items():
            pv.put(self._opmode_sel, wait=PowerSupplyEpicsSync.wait_pv_put)
        if not self._thread_local:
            self._lock = True

    @property
    def opmode_sts(self):
        return self._opmode_sts

    @property
    def pwrstate_sel(self):
        return self._pwrstate_sel

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        self._set_pwrstate_sel(value)

    def _set_pwrstate_sel(self, value):
        if not self._thread_local:
            self._lock = False
        self._pwrstate_sel = value
        for psname, pv in self._pvs['PwrState-Sel'].items():
            pv.put(self._pwrstate_sel, wait=PowerSupplyEpicsSync.wait_pv_put)
        if not self._thread_local:
            self._lock = True

    @property
    def pwrstate_sts(self):
        return self._pwrstate_sts

    def _get_limit(self, attr, maxmin):
        if not self.connected: return None
        lim = None
        for psname in self._psnames:
            pv = self._pvs['Current-SP'][psname]
            value = getattr(pv, attr)
            lim = value if lim is None else maxmin(lim,value)
        return lim

    def _set_psnames(self):
        if 'MA-B1B2' in self._maname:
            self._psnames = ['SI-Fam:PS-B1B2-1','SI-Fam:PS-B1B2-2']
        elif 'MA-B-' in self._maname:
            self._psnames = ['BO-Fam:PS-B-1','BO-Fam:PS-B-2']
        else:
            self._psnames = [self._maname.replace('MA-','PS-'),]

    def _create_epics_pvs(self):

        if self._use_vaca:
            if self._vaca_prefix is None:
                self._vaca_prefix = _envars.vaca_prefix
        else:
            self._vaca_prefix = ''

        # put it back !!!
        if self._thread_local:
            self._current = 0.0
            self._opmode_sel = 0
            self._pwrstate_sel = 0

        self._properties = {
            'OpMode-Sel'     : self._pvchange_opmode_sel,
            'OpMode-Sts'     : self._pvchange_opmode_sts,
            'PwrState-Sel'   : self._pvchange_pwrstate_sel,
            'PwrState-Sts'   : self._pvchange_pwrstate_sts,
            'Current-SP'     : self._pvchange_current_sp,
            'Current-RB'     : self._pvchange_current_rb,
            'CurrentRef-Mon' : self._pvchange_currentref_mon,
            'Current-Mon'    : self._pvchange_current_mon,
        }

        lock = self._lock
        self._lock = False

        self._pvs = {}
        index = None
        for propty in self._properties:
            self._pvs[propty] = {}
        for psname in self._psnames:
            pv = self._vaca_prefix + psname
            for propty, callback in self._properties.items():
                self._pvs[propty][psname] = _PV(pv + ':' + propty, connection_timeout=self._connection_timeout)
                self._pvs[propty][psname].wait_for_connection(timeout=self._connection_timeout)
                index = self._pvs[propty][psname].add_callback(callback=callback, index=index)

        psname = self._psnames[0]
        self.opmode_sel = self._pvs['OpMode-Sel'][psname].value
        self._opmode_sts = self._pvs['OpMode-Sts'][psname].value
        self.pwrstate_sel = self._pvs['PwrState-Sel'][psname].value
        self._pwrstate_sts = self._pvs['PwrState-Sts'][psname].value
        self.current_sp = self._pvs['Current-SP'][psname].value
        self._current_rb = self._pvs['Current-RB'][psname].value
        self._currentref_mon = self._pvs['CurrentRef-Mon'][psname].value
        self._current_mon = self._pvs['Current-Mon'][psname].value

        self._lock = lock

    def _force_lock(self):
        self._finished = False
        while not self._finished:
            #print('looping force')
            if self._lock:
                _time.sleep(PowerSupplyEpicsSync.sync_interval)
                for psname in self._psnames:
                    ps_value = self._pvs['Current-SP'][psname].value
                    if  ps_value != self._current_sp:
                        self._pvs['Current-SP'][psname].put(self._current_sp, wait=PowerSupplyEpicsSync.wait_pv_put)
                    opmode_sel_value = self._pvs['OpMode-Sel'][psname].value
                    if  opmode_sel_value != self.opmode_sel:
                        self._pvs['OpMode-Sel'][psname].put(self._opmode_sel, wait=PowerSupplyEpicsSync.wait_pv_put)
                    pwrstate_sel_value = self._pvs['PwrState-Sel'][psname].value
                    if  pwrstate_sel_value != self.pwrstate_sel:
                        self._pvs['PwrState-Sel'][psname].put(self._pwrstate_sel, wait=PowerSupplyEpicsSync.wait_pv_put)

    def _clear_threads(self):
        self._threads = [t for t in self._threads if t.is_alive]

    def _trigger_callback(self, pvname, value, **kwargs):
        if self._callback:
            self._callback(pvname, value, **kwargs)

    def _pvchange_opmode_sel(self, pvname, value, **kwargs):
        if not self._thread_local:
            pass
        if self._thread_local:
            if self._lock:
                if value != self._opmode_sel:
                    self._clear_threads()
                    self._threads.append(_threading.Thread(target=self._set_opmode_sel, args=[self._opmode_sel]))
                    self._threads[-1].start()
                else:
                    self._trigger_callback(pvname, value, **kwargs)
    def _pvchange_opmode_sts(self, pvname, value, **kwargs):
        self._opmode_sts = value
        self._trigger_callback(pvname, value, **kwargs)
    def _pvchange_pwrstate_sel(self, pvname, value, **kwargs):
        if not self._thread_local:
            pass
        if self._thread_local:
            if self._lock:
                if value != self._pwrstate_sel:
                    self._clear_threads()
                    self._threads.append(_threading.Thread(target=self._set_pwrstate_sel, args=[self._pwrstate_sel]))
                    self._threads[-1].start()
                else:
                    self._trigger_callback(pvname, value, **kwargs)
    def _pvchange_pwrstate_sts(self, pvname, value, **kwargs):
        self._pwrstate_sts = value
        self._trigger_callback(pvname, value, **kwargs)
    def _pvchange_current_sp(self, pvname, value, **kwargs):
        if not self._thread_local:
            pass
        if self._thread_local:
            if self._lock:
                if value != self._current_sp:
                    self._clear_threads()
                    self._threads.append(_threading.Thread(target=self._set_current_sp, args=[self._current_sp]))
                    self._threads[-1].start()
                else:
                    self._trigger_callback(pvname, value, **kwargs)
    def _pvchange_current_rb(self, pvname, value, **kwargs):
        self._current_rb = value
        self._trigger_callback(pvname, value, **kwargs)
    def _pvchange_currentref_mon(self, pvname, value, **kwargs):
        self._currentref_mon = value
        self._trigger_callback(pvname, value, **kwargs)
    def _pvchange_current_mon(self, pvname, value, **kwargs):
        self._current_mon = value
        self._trigger_callback(pvname, value, **kwargs)

    @property
    def database(self):
        return _get_database()

    def _get_database(self):
        db = dict()
        for prop in self._properties:
            attr = prop.replace("-", "_").lower()
            db[prop] = getattr(self, attr)

        return db


class PowerSupplyEpicsSync2:

    wait_pv_put   = True
    sync_interval = 1.0

    def __init__(self, psnames,
                       use_vaca=False,
                       vaca_prefix=None,
                       lock=True,
                       callback=None,
                       thread_local=True,
                       connection_timeout=None):

        self._callback = callback
        self._thread_local = thread_local

        if self._thread_local:
            self._finish = False
            self._threads = list()

        self._psnames = psnames
        self._psname_master = self._psnames[0]
        #super().__init__(psname=self._psname_master)
        self._connection_timeout = connection_timeout
        self._lock = lock
        self._set_vaca_prefix(use_vaca,vaca_prefix)
        self._create_pvs()

    @property
    def connected(self):
        for pv_dict in self._pvs.values():
            for pv in pv_dict.values():
                if not pv.connected:
                    return False
        return True

    def wait_for_connection(self, timeout=None):
        #print('wait_for_connection()')
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
                _time.sleep(min(timeout/2.0,0.1))
        return False

    def disconnect(self):
        if not self._thread_local:
            self._finished = True
        if self._thread_local:
            self._lock = False
            if self._threads:
                for t in self._threads:
                    if t.is_alive():
                        t.join()

        # if 'Current-SP' in self._scheduled and self._scheduled['Current-SP'] != self._propty['Current-SP']:
        #     self._clear_threads()
        #     thread = _threading.Thread(target=self._set_current_sp, args=[self._propty[propty]])
        #     self._threads.append(thread)
        #     thread.start()
        #
        # for t in self._threads:
        #     if t.is_alive():
        #         t.join()
        #
        # nr_pvs = len(self._pvs) * len(self._psnames)
        # pvs_ok = {}
        # while len(pvs_ok) < nr_pvs:
        #     for pv_dict in self._pvs.values():
        #         for pv in pv_dict.values():
        #             if pv.put_complete:
        #                 pvs_ok[pv.pvname] = True
        #                 pv.clear_callbacks()
        #                 pv.disconnect()

        #print('disconnect()')

    @property
    def psnames(self):
        return tuple([psname for psname in self._psnames])


    @property
    def opmode_sel(self):
        return self._propty['OpMode-Sel']

    @opmode_sel.setter
    def opmode_sel(self, value):
        #self._set_opmode_sel(value)
        self._set_propty_sp(value, 'OpMode-Sel')

    @property
    def opmode_sts(self):
        return self._propty['OpMode-Sts']

    @property
    def pwrstate_sel(self):
        return self._propty['PwrState-Sel']

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        #self._set_pwrstate_sel(value)
        self._set_propty_sp(value, 'PwrState-Sel')

    @property
    def pwrstate_sts(self):
        return self._propty['PwrState-Sts']

    @property
    def current_sp(self):
        return self._propty['Current-SP']

    @current_sp.setter
    def current_sp(self, value):
        #self._set_current_sp(value)
        self._set_propty_sp(value, 'Current-SP')

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
    def upper_alarm_limit(self):
        return self._get_limit('upper_alarm_limit', min)

    @property
    def upper_warning_limit(self):
        return self._get_limit('upper_warning_limit', min)

    @property
    def upper_disp_limit(self):
        return self._get_limit('upper_disp_limit', min)

    @property
    def lower_disp_limit(self):
        return self._get_limit('lower_disp_limit', max)

    @property
    def lower_warning_limit(self):
        return self._get_limit('lower_warning_limit', max)

    @property
    def lower_alarm_limit(self):
        return self._get_limit('lower_alarm_limit', max)

    def _set_vaca_prefix(self, use_vaca, vaca_prefix):
        if use_vaca:
            if vaca_prefix is None:
                self._vaca_prefix = _envars.vaca_prefix
            else:
                self._vaca_prefix = vaca_prefix
        else:
            self._vaca_prefix = ''

    def _create_pvs(self):

        self._propty_names = {
            'OpMode-Sel'     : (self._callback_connection_sp_pvs, self._callback_pvchange_sp_pvs),
            'OpMode-Sts'     : (self._callback_connection_rb_pvs, self._callback_pvchange_rb_pvs),
            'PwrState-Sel'   : (self._callback_connection_sp_pvs, self._callback_pvchange_sp_pvs),
            'PwrState-Sts'   : (self._callback_connection_rb_pvs, self._callback_pvchange_rb_pvs),
            'Current-SP'     : (self._callback_connection_sp_pvs, self._callback_pvchange_sp_pvs),
            'Current-RB'     : (self._callback_connection_rb_pvs, self._callback_pvchange_rb_pvs),
            'CurrentRef-Mon' : (self._callback_connection_rb_pvs, self._callback_pvchange_rb_pvs),
            'Current-Mon'    : (self._callback_connection_rb_pvs, self._callback_pvchange_rb_pvs),
        }

        # init _local properties
        self._propty = {propty:None for propty in self._propty_names}

        lock = self._lock
        self._lock = False

        self._callback_index = None
        self._pvs = {}
        for propty in self._propty_names:
            self._pvs[propty] = {}
        for psname in self._psnames:
            pv = self._vaca_prefix + psname
            for propty, callbacks in self._propty_names.items():
                connection_callback, callback = callbacks
                self._pvs[propty][psname] = _PV(pv + ':' + propty, connection_callback=connection_callback, connection_timeout=0.010)
                #self._pvs[propty][psname].wait_for_connection(timeout=3.0)
                self._callback_index = self._pvs[propty][psname].add_callback(callback=callback, index=self._callback_index)

        if self.connected:
            psname = self._psname_master
            propty='OpMode-Sel'; self._propty[propty] = self._pvs[propty][psname].value
            propty='OpMode-Sts'; self._propty[propty] = self._pvs[propty][psname].value
            propty='PwrState-Sel'; self._propty[propty] = self._pvs[propty][psname].value
            propty='PwrState-Sts'; self._propty[propty] = self._pvs[propty][psname].value
            propty='Current-SP'; self._propty[propty] = self._pvs[propty][psname].value
            propty='Current-RB'; self._propty[propty] = self._pvs[propty][psname].value
            propty='CurrentRef-Mon'; self._propty[propty] = self._pvs[propty][psname].value
            propty='Current-Mon'; self._propty[propty] = self._pvs[propty][psname].value

        self._lock = lock

    def _force_lock(self):
        self._finished = False
        while not self._finished:
            #print('looping force')
            if self._lock:
                _time.sleep(PowerSupplyEpicsSync2.sync_interval)
                for psname in self._psnames:
                    ps_value = self._pvs['Current-SP'][psname].value
                    if  ps_value != self._current_sp:
                        self._pvs['Current-SP'][psname].put(self._current_sp, wait=PowerSupplyEpicsSync2.wait_pv_put)
                    opmode_sel_value = self._pvs['OpMode-Sel'][psname].value
                    if  opmode_sel_value != self.opmode_sel:
                        self._pvs['OpMode-Sel'][psname].put(self._opmode_sel, wait=PowerSupplyEpicsSync2.wait_pv_put)
                    pwrstate_sel_value = self._pvs['PwrState-Sel'][psname].value
                    if  pwrstate_sel_value != self.pwrstate_sel:
                        self._pvs['PwrState-Sel'][psname].put(self._pwrstate_sel, wait=PowerSupplyEpicsSync2.wait_pv_put)

    def _clear_threads(self):
        self._threads = [t for t in self._threads if t.is_alive]

    def _get_limit(self, attr, maxmin):
        if not self.connected: return None
        lim = None
        for psname in self._psnames:
            pv = self._pvs['Current-SP'][psname]
            value = getattr(pv, attr)
            lim = value if lim is None else maxmin(lim,value)
        return lim

    def _set_propty_sp(self, value, propty):
        if not self._thread_local:
            self._lock = False
        self._propty[propty] = value
        for psname, pv in self._pvs[propty].items():
            pv.put(self._propty[propty], wait=PowerSupplyEpicsSync.wait_pv_put)
        if not self._thread_local:
            self._lock = True

    def _trigger_callback(self, pvname, value, **kwargs):
        if self._callback:
            self._callback(pvname, value, **kwargs)

    def _callback_connection_sp_pvs(self, pvname, conn,**kwargs):
        #print('callback_connection_sp: ', pvname, conn)
        pass

    def _callback_connection_rb_pvs(self, pvname, conn,**kwargs):
        #print('callback_connection_rb: ', pvname, conn)
        pass

    def _callback_pvchange_sp_pvs(self, pvname, value, **kwargs):
        #print('callback_pvchange_sp: ', pvname, value)
        *parts, propty = pvname.split(':')
        if self._propty[propty] is None:
            self._propty[propty] = value
            return
        if not self._thread_local:
            pass
        if self._thread_local:
            if self._lock:
                if value != self._propty[propty]:
                    self._clear_threads()
                    self._threads.append(_threading.Thread(target=self._set_propty_sp, args=[self._propty[propty], propty]))
                    self._threads[-1].start()
                else:
                    self._trigger_callback(pvname, value, **kwargs)

    def _callback_pvchange_rb_pvs(self, pvname, value, **kwargs):
        #print('callback_pvchange_sp: ', pvname, value)
        *_, propty = pvname.split(':')
        self._propty[propty] = value
        self._trigger_callback(pvname, value, **kwargs)


# Previous Classes:
# =================
# class PowerSupplySync(PowerSupply):
#
#     def __init__(self, psnames, controller_type='ControllerEpics',
#                                 lock=False,
#                                 use_vaca=False, vaca_prefix=None,
#                                 connection_timeout=_connection_timeout,
#                                 **kwargs):
#         self._psnames = psnames
#         self._controller_psnames = list()
#         self._controllers = list()
#         self._lock = lock
#
#         # Create controller epics
#         for psname in self._psnames:
#             if controller_type == 'ControllerEpics':
#                 c = _ControllerEpics(psname=psname,
#                                      use_vaca=use_vaca, vaca_prefix=vaca_prefix,
#                                      connection_timeout=connection_timeout,
#                                      callback=self._mycallback)
#             elif controller_type == 'ControllerSim':
#                 psdata = _PSData(psname=psname)
#                 c  = _ControllerSim(psname=psname,
#                                     current_min = psdata.splims['DRVL'],
#                                     current_max = psdata.splims['DRVH'],
#                                     callback = self._mycallback)
#             self._controllers.append(c)
#         super().__init__(psname=psnames[0], controller=self._controllers[0], **kwargs)
#         #self._controller = None
#
#     def _get_connected(self):
#         for controller in self._controllers:
#             if not controller.connected: return False
#         return True
#
#     def _controller_init(self, current_std):
#         c0 = self._controllers[0]
#         if c0.connected:
#             self._pwrstate_sel = c0.pwrstate
#             self._opmode_sel = c0.opmode
#             self._current_sp = c0.current_sp
#             self._wfmlabel_sp  = c0.wfmlabel
#             self._wfmload_sel  = c0.wfmload
#             self._wfmdata_sp   = c0.wfmdata
#             for c in self._controllers:
#                 c.pwrstate = self._pwrstate_sel
#                 c.opmode = self._opmode_sel
#                 c.current_sp = self._current_sp
#                 c.wfmlabel = self._wfmlabel_sp
#                 c.wfmload = self._wfmload_sel
#                 c.wfmdata = self._wfmdata_sp
#                 c.update_state()
#         else:
#             self._pwrstate_sel = None
#             self._opmode_sel   = None
#             self._current_sp   = None
#             self._wfmlabel_sp  = None
#             self._wfmload_sel  = None
#             self._wfmdata_sp   = None
#
#     def _set_opmode_sel(self, value):
#         for c in self._controllers:
#             c.opmode = value
#
#     def _set_wfmlabel_sp(self, value):
#         for c in self._controllers:
#             c.wfmlabel = value
#
#     def _set_wfmdata_sp(self, value):
#         for c in self._controllers:
#             c.wfmdata = value
#
#     def _set_wfmload_sel(self, value):
#         for c in self._controllers:
#             c.wfmload = value
#
#     def _set_pwrstate_sel(self, value):
#         for c in self._controllers:
#             c.pwrstate = value
#
#     def _set_current_sp(self, value):
#         #print('[PSES] _set_current_sp ', value)
#         for c in self._controllers:
#             #print(c._psname)
#             #print(value)
#             c.current_sp = value
#
#     def _mycallback(self, pvname, value, **kwargs):
#         #print('[PSES] [callback] ', pvname, value)
#         if 'CtrlMode-Mon' in pvname:
#             self._ctrlmode_mon = value
#         elif self._lock:
#             if 'OpMode-Sel' in pvname:
#                 if self._opmode_sel != value:
#                     thread = _threading.Thread(target=self._set_opmode_sel, args=[self._opmode_sel])
#                     thread.start()
#                     value = self._opmode_sel
#             elif pvname == 'opmode':
#                 if self._opmode_sel != value:
#                     self._set_opmode_sel(self._opmode_sel)
#                     value = self._opmode_sel
#             elif 'PwrState-Sel' in pvname:
#                 if self._pwrstate_sel != value:
#                     thread = _threading.Thread(target=self._set_pwrstate_sel, args=[self._pwrstate_sel])
#                     thread.start()
#                     value = self._pwrstate_sel
#             elif pvname == 'pwrstate':
#                 if self._pwrstate_sel != value:
#                     self._set_pwrstate_sel(self._pwrstate_sel)
#                     value = self._pwrstate_sel
#             elif 'WfmLoad-Sel' in pvname:
#                 if self._wfmload_sel != value:
#                     thread = _threading.Thread(target=self._set_wfmload_sel, args=[self._wfmload_sel])
#                     thread.start()
#                     value = self._wfmload_sel
#             elif pvname == 'wfmload':
#                 if self._wfmload_sel != value:
#                     self._set_wfmload_sel(self._wfmload_sel)
#                     value = self._wfmload_sel
#             elif 'WfmLabel-SP' in pvname:
#                 if self._wfmlabel_sp != value:
#                     thread = _threading.Thread(target=self._set_wfmlabel_sp, args=[self._wfmlabel_sp])
#                     thread.start()
#                     value = self._wfmlabel_sp
#             elif pvname == 'wfmlabel':
#                 if self._wfmlabel_sp != value:
#                     self._set_wfmlabel_sp(self._wfmlabel_sp)
#                     value = self._wfmlabel_sp
#             elif 'WfmData-SP' in pvname:
#                 if _np.any(self._wfmdata_sp != value):
#                     thread = _threading.Thread(target=self._set_wfmdata_sp, args=[self._wfmdata_sp])
#                     thread.start()
#                     value = self._wfmdata_sp
#             elif pvname == 'wfmdata':
#                 if _np.any(self._wfmdata_sp != value):
#                     self._set_wfmdata_sp(self._wfmdata_sp)
#                     value = self._wfmdata_sp
#             elif 'Current-SP' in pvname:
#                 if self._current_sp != value: #Value was not changed by the MA-IOC
#                     thread = _threading.Thread(target=self._set_current_sp, args=[self._current_sp])
#                     thread.start()
#                     value = self._current_sp
#             elif pvname == 'current_sp':
#                 if self._current_sp != value: #Value was not changed by the MA-IOC
#                     self._set_current_sp(self._current_sp)
#                     value = self._current_sp
#         for callback in self._callbacks.values():
#             callback(pvname, value, **kwargs)
#
#
# class PowerSupplyEpics(PowerSupplySync):
#
#     def __init__(self, psname,
#                        use_vaca=False, vaca_prefix=None,
#                        connection_timeout=_connection_timeout,
#                        **kwargs):
#         super().__init__(psnames=[psname,],
#                          controller_type='ControllerEpics',
#                          lock=False,
#                          use_vaca=use_vaca, vaca_prefix=vaca_prefix,
#                          connection_timeout=connection_timeout,
#                          **kwargs)
