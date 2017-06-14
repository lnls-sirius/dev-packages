
import copy as _copy
import numpy as _np
import threading as _threading
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.pwrsupply.data import PSData as _PSData
from siriuspy.pwrsupply.controller import ControllerSim as _ControllerSim
from siriuspy.pwrsupply.controller import ControllerEpics as _ControllerEpics


_connection_timeout = 0.1


class PowerSupplyLinac(object):

    def __init__(self, psname,
                       controller=None,
                       callback=None,
                       current_std=0.0,
                       enum_keys=False):

        self._psdata = _PSData(psname=psname)
        self._callback = callback
        self._enum_keys = enum_keys
        self._ctrlmode_mon = _et.idx.Remote
        self._controller = controller
        self._controller_init(current_std)

    # --- class interface ---

    @property
    def connected(self):
        return self._get_connected()

    @property
    def psname(self):
        return self._psdata.psname

    @property
    def pstype(self):
        return self._psdata.pstype

    @property
    def psdata(self):
        return self._psdata

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, value):
        if callable(value):
            self._callback = value
        else:
            self._callback = None

    @property
    def splims(self):
        return _copy.deepcopy(self._psdata.splims)

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
        if value != self.current_rb or value != self._current_sp:
            self._current_sp = value
            self._set_current_sp(value)

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

    def _get_connected(self):
        if isinstance(self._controller, _ControllerEpics):
            return self._controller.connected
        else:
            return True

    def _get_database(self):
        """Return an updated PV database whose keys correspond to PS properties."""
        db = self._psdata.propty_database
        value = self.ctrlmode_mon; db['CtrlMode-Mon']['value'] = _et.enums('RmtLocTyp').index(value) if self._enum_keys else value
        value = self.pwrstate_sel; db['PwrState-Sel']['value'] = _et.enums('OffOnTyp').index(value) if self._enum_keys else value
        value = self.pwrstate_sts; db['PwrState-Sts']['value'] = _et.enums('OffOnTyp').index(value) if self._enum_keys else value
        db['Current-SP']['value']  = self.current_sp
        db['Current-Mon']['value'] = self.current_mon
        return db

    def _set_pwrstate_sel(self, value):
            self._pwrstate_sel = value
            self._controller.pwrstate = value

    def _set_current_sp(self, value):
            self._pwrstate_sp = value
            self._controller.current_sp = value

    def _controller_init(self, current_std):
        if self._controller is None:
            lims = self._psdata.splims # set controller setpoint limits according to PS database
            self._controller = _ControllerSim(current_min = self._psdata.splims['DRVL'],
                                              current_max = self._psdata.splims['DRVH'],
                                              callback = self._mycallback,
                                              current_std = current_std,
                                              psname=self._psdata.psname)
            self._pwrstate_sel = self._psdata.propty_database['PwrState-Sel']['value']
            self._current_sp   = self._psdata.propty_database['Current-SP']['value']
            self._controller.pwrstate   = self._pwrstate_sel
            self._controller.current_sp = self._current_sp
        else:
            self._pwrstate_sel = self._controller.pwrstate
            self._current_sp   = self._controller.current_sp

        #self.callback = self._mycallback # ????
        self._controller.update_state()

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
        pass


class PowerSupply(PowerSupplyLinac):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _controller_init(self, current_std):
        if self._controller is None:
            lims = self._psdata.splims # set controller setpoint limits according to PS database
            self._controller = _ControllerSim(current_min = self._psdata.splims['DRVL'],
                                              current_max = self._psdata.splims['DRVH'],
                                              callback = self._mycallback,
                                              current_std = current_std,
                                              psname=self._psdata.psname)

            self._pwrstate_sel = self._psdata.propty_database['PwrState-Sel']['value']
            self._opmode_sel   = self._psdata.propty_database['OpMode-Sel']['value']
            self._current_sp   = self._psdata.propty_database['Current-SP']['value']
            self._wfmlabel_sp  = self._controller.wfmlabel
            self._wfmload_sel  = self._psdata.propty_database['WfmLoad-Sel']['value']
            self._wfmdata_sp   = self._psdata.propty_database['WfmData-SP']['value']
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

        self._controller.callback = self._mycallback
        self._controller.update_state()

    # --- class interface ---

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
    def current_rb(self):
        return self._get_current_rb()

    @property
    def currentref_mon(self):
        return self._get_currentref_mon()

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

    def _get_database(self):
        """Return an updated  PV database whose keys correspond to PS properties."""
        db = self._psdata.propty_database
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

    def _set_opmode_sel(self, value):
        self._controller.opmode = value

    def _get_opmode_sts(self):
        return self._eget('PSOpModeTyp',self._controller.opmode)

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
            if self.callback is not None:
                self.callback(pvname, value, **kwargs)
        elif isinstance(self._controller, _ControllerSim):
            if self.callback is not None:
                if pvname == 'opmode':
                    self.callback(self.psname + ':OpMode-Sts', value, **kwargs)
                elif pvname == 'pwrstate':
                    self.callback(self.psname + ':PwrState-Sts', value, **kwargs)
                elif pvname == 'wfmload':
                    self.callback(self.psname + ':WfmLoad-Sel', value, **kwargs)
                elif pvname == 'wfmlabel':
                    self.callback(self.psname + ':WfmLabel-RB', value, **kwargs)
                elif pvname == 'wfmdata':
                    self.callback(self.psname + ':WfmLoad-Sel', value, **kwargs)
                elif pvname == 'current_sp':
                    self.callback(self.psname + ':Current-RB', value, **kwargs)
                elif pvname == 'current_ref':
                    self.callback(self.psname + ':CurrentRef-Mon', value, **kwargs)
                elif pvname == 'current_load':
                    self.callback(self.psname + ':Current-Mon', value, **kwargs)


class PowerSupplySync(PowerSupply):

    def __init__(self, psnames, controller_type='ControllerEpics',
                                lock=True,
                                use_vaca=False, vaca_prefix=None,
                                connection_timeout=_connection_timeout,
                                **kwargs):
        self._psnames = psnames
        self._controller_psnames = list()
        self._controllers = list()
        self._lock = lock

        # Create controller epics
        for psname in self._psnames:
            if controller_type == 'ControllerEpics':
                c = _ControllerEpics(psname=psname,
                                     use_vaca=use_vaca, vaca_prefix=vaca_prefix,
                                     connection_timeout=connection_timeout,
                                     callback=self._mycallback)
            elif controller_type == 'ControllerSim':
                psdata = _PSData(psname=psname)
                c  = _ControllerSim(psname=psname,
                                    current_min = psdata.splims['DRVL'],
                                    current_max = psdata.splims['DRVH'],
                                    callback = self._mycallback)
            self._controllers.append(c)

        super().__init__(psname=psnames[0], controller=self._controllers[0], **kwargs)

    def _get_connected(self):
        for controller in self._controllers:
            if not controller.connected: return False
        return True

    def _controller_init(self, current_std):
        c0 = self._controllers[0]
        if c0.connected:
            self._pwrstate_sel = c0.pwrstate
            self._opmode_sel = c0.opmode
            self._current_sp = c0.current_sp
            self._wfmlabel_sp  = c0.wfmlabel
            self._wfmload_sel  = c0.wfmload
            self._wfmdata_sp   = c0.wfmdata
            for c in self._controllers:
                c.pwrstate = self._pwrstate_sel
                c.opmode = self._opmode_sel
                c.current_sp = self._current_sp
                c.wfmlabel = self._wfmlabel_sp
                c.wfmload = self._wfmload_sel
                c.wfmdata = self._wfmdata_sp
                c.update_state()
        else:
            self._pwrstate_sel = None
            self._opmode_sel = None
            self._current_sp = None
            self._wfmlabel_sp  = None
            self._wfmload_sel  = None
            self._wfmdata_sp   = None

    def _set_opmode_sel(self, value):
        for c in self._controllers:
            c.opmode = value

    def _set_wfmlabel_sp(self, value):
        for c in self._controllers:
            c.wfmlabel = value

    def _set_wfmdata_sp(self, value):
        for c in self._controllers:
            c.wfmdata = value

    def _set_wfmload_sel(self, value):
        for c in self._controllers:
            c.wfmload = value

    def _set_pwrstate_sel(self, value):
        for c in self._controllers:
            c.pwrstate = value

    def _set_current_sp(self, value):
        #print('[PSES] _set_current_sp ', value)
        for c in self._controllers:
            #print(c._psname)
            c.current_sp = value

    def _mycallback(self, pvname, value, **kwargs):
        #print('[PSES] [callback] ', pvname, value)
        if 'CtrlMode-Mon' in pvname:
            self._ctrlmode_mon = value
        elif self._lock:
            if 'OpMode-Sel' in pvname:
                if self._opmode_sel != value:
                    thread = _threading.Thread(target=self._set_opmode_sel, args=[self._opmode_sel])
                    thread.start()
                    value = self._opmode_sel
            elif pvname == 'opmode':
                if self._opmode_sel != value:
                    self._set_opmode_sel(self._opmode_sel)
                    value = self._opmode_sel
            elif 'PwrState-Sel' in pvname:
                if self._pwrstate_sel != value:
                    thread = _threading.Thread(target=self._set_pwrstate_sel, args=[self._pwrstate_sel])
                    thread.start()
                    value = self._pwrstate_sel
            elif pvname == 'pwrstate':
                if self._pwrstate_sel != value:
                    self._set_pwrstate_sel(self._pwrstate_sel)
                    value = self._pwrstate_sel
            elif 'WfmLoad-Sel' in pvname:
                if self._wfmload_sel != value:
                    thread = _threading.Thread(target=self._set_wfmload_sel, args=[self._wfmload_sel])
                    thread.start()
                    value = self._wfmload_sel
            elif pvname == 'wfmload':
                if self._wfmload_sel != value:
                    self._set_wfmload_sel(self._wfmload_sel)
                    value = self._wfmload_sel
            elif 'WfmLabel-SP' in pvname:
                if self._wfmlabel_sp != value:
                    thread = _threading.Thread(target=self._set_wfmlabel_sp, args=[self._wfmlabel_sp])
                    thread.start()
                    value = self._wfmlabel_sp
            elif pvname == 'wfmlabel':
                if self._wfmlabel_sp != value:
                    self._set_wfmlabel_sp(self._wfmlabel_sp)
                    value = self._wfmlabel_sp
            elif 'WfmData-SP' in pvname:
                if _np.any(self._wfmdata_sp != value):
                    thread = _threading.Thread(target=self._set_wfmdata_sp, args=[self._wfmdata_sp])
                    thread.start()
                    value = self._wfmdata_sp
            elif pvname == 'wfmdata':
                if _np.any(self._wfmdata_sp != value):
                    self._set_wfmdata_sp(self._wfmdata_sp)
                    value = self._wfmdata_sp
            elif 'Current-SP' in pvname:
                if self._current_sp != value: #Value was not changed by the MA-IOC
                    thread = _threading.Thread(target=self._set_current_sp, args=[self._current_sp])
                    thread.start()
                    value = self._current_sp
            elif pvname == 'current_sp':
                if self._current_sp != value: #Value was not changed by the MA-IOC
                    self._set_current_sp(self._current_sp)
                    value = self._current_sp
        if self.callback is not None:
            self.callback(pvname, value, **kwargs)
