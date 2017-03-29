
import copy as _copy
import uuid as _uuid
from .psdata import conv_psname_2_pstype as _conv_psname_2_pstype
from .psdata import get_setpoint_limits as _sp_limits
from .psdata import get_polarity as _get_polarity
import siriuspy.csdevice as _csdevice
from .controller import ControllerSim as _ControllerSim
from siriuspy.csdevice.enumtypes import EnumTypes as _et


class PowerSupply:
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
        self._ctrlmode_mon = _et.idx('RmtLocTyp', 'Remote')

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
        """Return a database whose keys correspond to PS properties prefixed by the device instance name."""
        db = _copy.deepcopy(self._database)
        db['CtrlMode-Mon']['value'] = self._ctrlmode_mon
        db['PwrState-Sel']['value'] = self._controller.pwrstate_sel
        db['PwrState-Sts']['value'] = self._controller.pwrstate_sts
        db['OpMode-Sel']['value'] = self._controller.opmode_sel
        db['OpMode-Sts']['value'] = self._controller.opmode_sts
        db['Current-SP']['value'] = self._controller.current_sp
        db['Current-RB']['value'] = self._controller.current_rb
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
            self._controller.set_callback(self._mycallback)

        # controller update triggers update state in PS
        self._controller.update_state()

    def _mycallback(self, pvname, value, **kwargs):
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


class PowerSupplyMA(PowerSupply):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
