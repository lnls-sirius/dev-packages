
import copy as _copy
import uuid as _uuid
from .psdata import conv_psname_2_pstype as _conv_psname_2_pstype
from .psdata import get_setpoint_limits as _sp_limits
from .psdata import get_polarity as _get_polarity
import siriuspy.csdevice as _csdevice
from .controller import ControllerSim as _ControllerSim
from .controller import ControllerEpics as _ControllerEpics
from siriuspy.csdevice.enumtypes import EnumTypes as _et


class PowerSupply(object):

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

    def _controller_init(self, current_std):
        if self._controller is None:
            lims = self._setpoint_limits # set controller setpoint limits according to PS database
            self._controller = _ControllerSim(current_min = self._setpoint_limits['DRVL'],
                                              current_max = self._setpoint_limits['DRVH'],
                                              callback = self._mycallback,
                                              current_std = current_std)
            self._pwrstate_sel = self._database['PwrState-Sel']['value']
            self._opmode_sel   = self._database['OpMode-Sel']['value']
            self._current_sp   = self._database['Current-SP']['value']
            self._wfmdata_sp   = self._database['WfmData-SP']['value']
            self._controller.pwrstate   = self._pwrstate_sel
            self._controller.opmode     = self._opmode_sel
            self._controller.current_sp = self._current_sp
            self._controller.wfmdata_sp = self._wfmdata_sp
        else:
            self._pwrstate_sel = self._controller.pwrstate
            self._opmode_sel   = self._controller.opmode
            self._current_sp   = self._controller.current_sp
            self._wfmdata_sp   = self._controller.wfmdata

        self.callback = self._mycallback
        self._controller.update_state()

    @property
    def ps_name(self):
        return self._ps_name

    @property
    def pstype_name(self):
        return self._pstype_name

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
        """Return a PV database whose keys correspond to PS properties."""
        db = _copy.deepcopy(self._database)
        db['CtrlMode-Mon']['value'] = self.ctrlmode_mon
        db['PwrState-Sel']['value'] = self.pwrstate_sel
        db['PwrState-Sts']['value'] = self.pwrstate_sts
        db['OpMode-Sel']['value'] = self.opmode_sel
        db['OpMode-Sts']['value'] = self.opmode_sts
        db['Current-SP']['value'] = self.current_sp
        db['Current-RB']['value'] = self.current_rb
        db['CurrentRef-Mon']['value'] = self.currentref_mon
        db['Current-Mon']['value'] = self.current_mon
        return db

    @property
    def ctrlmode_mon(self):
        return self._eget('RmtLocTyp', self._ctrlmode_mon)

    def set_ctrlmode(self, value):
        value = self._eget('RmtLocTyp', value, enum_keys=False)
        if value is not None:
            self._ctrlmode_mon = value

    @property
    def pwrstate_sel(self):
        return self._pwrstate_sel

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        if self._ctrlmode_mon != _et.idx.Remote: return
        value = self._eget('OffOnTyp', value, enum_keys=False)
        if value is not None and value != self.pwrstate_sts:
            self._pwrstate_sel = value
            self._controller.pwrstate = value

    @property
    def pwrstate_sts(self):
        return self._eget('OffOnTyp', self._controller.pwrstate)

    @property
    def opmode_sel(self):
        return self._eget('PSOpModeTyp', self._opmode_sel)

    @opmode_sel.setter
    def opmode_sel(self, value):
        if self._ctrlmode_mon != _et.idx.Remote: return
        value = self._eget('PSOpModeTyp', value, enum_keys=False)
        if value is not None and value != self.opmode_sts:
            self._opmode_sel = value
            self._controller.opmode = value

    @property
    def opmode_sts(self):
        return self._eget('PSOpModeTyp',self._controller.pwrstate)

    @property
    def current_sp(self):
        return self._current_sp

    @current_sp.setter
    def current_sp(self, value):
        if self._ctrlmode_mon != _et.idx.Remote: return
        if value not in (self.current_sp, self.current_rb):
            self._current_sp = value
            self._controller.current_sp = value

    @property
    def current_rb(self):
        return self._controller.current_sp

    @property
    def currentref_mon(self):
        return self._controller.current_ref

    @property
    def current_mon(self):
        return self._controller.current_load

    @property
    def wfmdata_sp(self):
        return [datum for datum in self._wfmdata_sp]

    @property
    def wfmdata_rb(self):
        return self._controller.wfmdata

    @wfmdata_sp.setter
    def wfmdata_sp(self, value):
        if self._ctrlmode_mon != _et.idx.Remote: return
        if value != self.wfmdata_sp:
            self._wfmdata_sp = [datum for datum in value]
            self._controller.wfmdata = value

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


class PowerSupply2:
    """Magnet Power Supply model

    This class implements a model of the basic power supply of magnets.
    All basic properties, CtrlMode-Mon, PwrState-(Sel/Sts), OprMode-(Sel/Sts) and
    Current-(SP/RB) are implemented and theirs states are stored in a database
    dictionary. Additional specific properties may be implemented in subclasses.

    The model uses a Controller object to drive updates of property values.
    a) The default controller object is a power supply drive simulator.
    b) It could also be an object that updates the model properties by reading
    the physical power supply. In this case the PS model can be used to feed
    the IOC with PV data.
    c) Another application of the PS model is where the controller updates the
    model properties by reading a lower level PS IOC.
    """

    def __init__(self, ps_name,
                       controller=None,
                       callback=None,
                       enum_keys=False):

        self._uuid = _uuid.uuid4()
        self._ps_name = ps_name
        self._pstype_name = _conv_psname_2_pstype(ps_name)
        self._polarity = _get_polarity(self._pstype_name)
        self._setpoint_limits = _sp_limits(self._pstype_name)
        self._database = _csdevice.get_database(self._pstype_name)
        if self._database is None:
            raise Exception('no database defined for power supply type "' + self._pstype_name + '"!')
        self._enum_keys = enum_keys
        self._callback = callback
        self._controller = controller
        self._controller_init()
        self._ctrlmode_mon = _et.idx.Remote

    @property
    def ps_name(self):
        return self._ps_name

    @property
    def pstype_name(self):
        return self._pstype_name

    @property
    def polarity(self):
        return self._polarity

    @property
    def database(self):
        """Return a PV database whose keys correspond to PS properties."""
        db = _copy.deepcopy(self._database)
        db['CtrlMode-Mon']['value'] = self._ctrlmode_mon
        db['PwrState-Sel']['value'] = self._controller.pwrstate
        db['PwrState-Sts']['value'] = self._controller.pwrstate
        db['OpMode-Sel']['value'] = self._controller.opmode
        db['OpMode-Sts']['value'] = self._controller.opmode
        db['Current-SP']['value'] = self._controller.current_sp
        db['Current-RB']['value'] = self._controller.current_load
        return db

    @property
    def setpoint_limits(self):
        return _copy.deepcopy(self._setpoint_limits)

    @property
    def reset_cmd(self):
        return None

    @property
    def ctrlmode_mon(self):
        value = self._ctrlmode_mon
        return value if not self._enum_keys else _et.key('RmtLocTyp', value)

    @property
    def pwrstate_sel(self):
        value = self._controller.pwrstate_sel
        return value if not self._enum_keys else _et.key('OffOnTyp', value)

    @property
    def pwrstate_sts(self):
        value = self._controller.pwrstate_sts
        return value if not self._enum_keys else _et.key('OffOnTyp', value)

    @property
    def opmode_sel(self):
        value = self._controller.opmode_sel
        return value if not self._enum_keys else _et.key('PSOpModeTyp', value)

    @property
    def opmode_sts(self):
        value = self._controller.opmode_sts
        return value if not self._enum_keys else _et.key('PSOpModeTyp', value)

    @property
    def current_rb(self):
        return self._controller.current_rb

    @property
    def current_sp(self):
        return self._controller.current_sp

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        if self._ctrlmode_mon != _et.idx('RmtLocTyp', 'Remote'): return
        self._controller.pwrstate_sel = value if not self._enum_keys else _et.idx('OffOnTyp', value)

    @opmode_sel.setter
    def opmode_sel(self, value):
        if self._ctrlmode_mon != _et.idx('RmtLocTyp', 'Remote'): return
        self._controller.opmode_sel = value if not self._enum_keys else _et.idx('PSOpModeTyp', value)

    @current_sp.setter
    def current_sp(self, value):
        if self._ctrlmode_mon != _et.idx('RmtLocTyp', 'Remote'): return
        value = self._check_IOC_setpoint_limits(float(value))
        self._controller.current_sp = value

    @reset_cmd.setter
    def reset_cmd(self, value):
        if self._ctrlmode_mon != _et.idx('RmtLocTyp', 'Remote'): return
        self._controller.reset_cmd()

    def timing_trigger(self):
        self._controller.timing_trigger()

    def _check_IOC_setpoint_limits(self, value):
        l = self.setpoint_limits.values()
        _min, _max = min(l), max(l)
        value = _min if value < _min else value
        value = _max if value > _max else value
        return value

    def update_state(self):
        self._controller.update_state()

    def set_callback(self, callback):
        self._callback = callback

    def _controller_init(self):
        # set controller setpoint limits according to PS database
        if self._controller is None:
            l = self.setpoint_limits
            self._controller = _ControllerSim(current_min = l['DRVL'],
                                              current_max = l['DRVH'],
                                              callback=self._mycallback,
                                              error_std=_default_error_std)
        else:
            # add model callback to controller callback list
            self._controller.callback = self._mycallback

        # controller update triggers update state in PS
        self._controller._update_state()

    def _mycallback(self, pvname, value, **kwargs):
        print('pwrsup', pvname)
        if self._callback is None:
            return
        else:
            self._callback(pvname=pvname, value=value, **kwargs)

    def __str__(self):
        #self._controller_read_status()
        st_controller = self._controller.__str__()
        st  =   '{0:<20s}: {1}'.format('power_supply', self.ps_name)
        st += '\n{0:<20s}: {1}'.format('type', self.pstype_name)
        st += '\n{0:<20s}: {1}'.format('polarity', self.polarity)
        l = self.setpoint_limits
        st += '\n{0:<20s}: {1} {2}'.format('limits', min(l.values()),max(l.values()))
        st += '\n--- IOC ---'
        propty = 'CtrlMode-Mon';  st += '\n{0:<20s}: {1}'.format(propty, self.ctrlmode_mon)
        propty = 'PwrState-Sel';  st += '\n{0:<20s}: {1}'.format(propty, self.pwrstate_sel)
        propty = 'PwrState-Sts';  st += '\n{0:<20s}: {1}'.format(propty, self.pwrstate_sts)
        propty = 'OpMode-Sel';    st += '\n{0:<20s}: {1}'.format(propty, self.opmode_sel)
        propty = 'OpMode-Sts';    st += '\n{0:<20s}: {1}'.format(propty, self.opmode_sts)
        propty = 'Current-SP';    st += '\n{0:<20s}: {1}'.format(propty, self.current_sp)
        propty = 'Current-RB';    st += '\n{0:<20s}: {1}'.format(propty, self.current_rb)
        st += '\n' + st_controller
        return st


class PowerSupplyMAFam(PowerSupply):

    def __init__(self, ps_name, **kwargs):
        super().__init__(ps_name, **kwargs)

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
