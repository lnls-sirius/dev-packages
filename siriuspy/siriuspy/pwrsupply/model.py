import copy as _copy
import uuid as _uuid
import numpy as _np
from .psdata import conv_psname_2_pstype as _conv_psname_2_pstype
from .psdata import get_setpoint_limits as _sp_limits
from .psdata import get_polarity as _get_polarity
import siriuspy.csdevice as _csdevice
from .controller import ControllerSim as _ControllerSim
from .controller import ControllerEpics as _ControllerEpics
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.csdevice.pwrsupply import default_wfmlabels as _default_wfmlabels


_connection_timeout = 0.0


class PowerSupplyLinac(object):

    def __init__(self, name_ps,
                       controller=None,
                       callback=None,
                       current_std=0.0,
                       enum_keys=False):

        self._name_ps = name_ps
        self._name_pstype = _conv_psname_2_pstype(self._name_ps)
        self._callback = callback
        self._enum_keys = enum_keys
        self._database = _csdevice.get_database(self._name_pstype)
        self._ctrlmode_mon = _et.idx.Remote
        self._setpoint_limits = _sp_limits(self._name_pstype)
        self._controller = controller
        self._controller_init(current_std)

    # --- class interface ---

    @property
    def name_ps(self):
        return self._name_ps

    @property
    def name_pstype(self):
        return self._name_pstype

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
    def setpoint_limits(self):
        return _copy.deepcopy(self._setpoint_limits)

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
        if self._ctrlmode_mon != _et.idx.Remote: return
        if value not in (self.current_sp, self.current_rb):
            self._current_sp = value
            self._set_current_sp(value)

    @property
    def current_mon(self):
        return self._controller.current_load

    @property
    def intlk_mon(self):
        # This will eventually be implemented in _PowerSupply!
        return self._controller.intlk

    @property
    def intlklabels_cte(self):
        return self._controller.intlklabels

        # --- class implementation ---

    def _get_database(self):
        """Return a PV database whose keys correspond to PS properties."""
        db = _copy.deepcopy(self._database)
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
            lims = self._setpoint_limits # set controller setpoint limits according to PS database
            self._controller = _ControllerSim(current_min = self._setpoint_limits['DRVL'],
                                              current_max = self._setpoint_limits['DRVH'],
                                              callback = self._mycallback,
                                              current_std = current_std)
            self._pwrstate_sel = self._database['PwrState-Sel']['value']
            self._current_sp   = self._database['Current-SP']['value']
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
            lims = self._setpoint_limits # set controller setpoint limits according to PS database
            self._controller = _ControllerSim(current_min = self._setpoint_limits['DRVL'],
                                              current_max = self._setpoint_limits['DRVH'],
                                              callback = self._mycallback,
                                              current_std = current_std,
                                              name_ps=self._name_ps)
            #print(self._name_ps)
            self._pwrstate_sel = self._database['PwrState-Sel']['value']
            self._opmode_sel   = self._database['OpMode-Sel']['value']
            self._current_sp   = self._database['Current-SP']['value']
            self._wfmlabel_sp  = self._controller.wfmlabel
            self._wfmload_sel  = self._database['WfmLoad-Sel']['value']
            self._wfmdata_sp   = self._database['WfmData-SP']['value']
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

        #self.callback = self._mycallback
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
        """Return a PV database whose keys correspond to PS properties."""
        db = _copy.deepcopy(self._database)
        value = self.ctrlmode_mon; db['CtrlMode-Mon']['value'] = _et.enums('RmtLocTyp').index(value) if self._enum_keys else value
        value = self.opmode_sel;   db['OpMode-Sel']['value'] = _et.enums('PSOpModeTyp').index(value) if self._enum_keys else value
        value = self.opmode_sts;   db['OpMode-Sts']['value'] = _et.enums('PSOpModeTyp').index(value) if self._enum_keys else value
        value = self.pwrstate_sel; db['PwrState-Sel']['value'] = _et.enums('OffOnTyp').index(value) if self._enum_keys else value
        value = self.pwrstate_sts; db['PwrState-Sts']['value'] = _et.enums('OffOnTyp').index(value) if self._enum_keys else value
        db['Reset-Cmd']['value'] = self.reset
        db['Abort-Cmd']['value'] = self.abort
        wfmlabels = self._get_wfmlabels_mon()
        #print(type(wfmlabels))
        #print(wfmlabels)
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
            #print(pvname, value)
            if 'CtrlMode-Mon' in pvname:
                self._ctrlmode_mon = value
            elif 'OpMode-Sel' in pvname:
                self._opmode_sel   = value
            elif 'PwrState-Sel' in pvname:
                self._pwrstate_sel = value
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

class PowerSupplyEpicsSync(PowerSupply):

    def __init__(self, controllers, **kwargs):
        self._controllers = controllers
        super().__init__(controller=controllers[0], **kwargs)

    def _controller_init(self, current_std):
        c0 = self._controllers[0]
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
        for c in self._controllers:
            c.current_sp = value

class PowerSupplyMagnet(PowerSupply):

    def __init__(self, name_ps, **kwargs):
        super().__init__(name_ps, **kwargs)

    @property
    def database(self):
        """Return property database as a dictionary.
        It prepends power supply family name to each dictionary key.
        """
        _database = {}
        dd = super().database
        _, family = self.ps_name.split('PS-')
        if not isinstance(family,str):
            raise Exception('invalid pv_name!')
        for propty, db in super().database.items():
            key = family + ':' + propty
            _database[key] = _copy.deepcopy(db)
        return _database
