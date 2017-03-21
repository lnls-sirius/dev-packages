
import copy as _copy
from .psdata import conv_psname_2_pstype as _conv_psname_2_pstype
from .psdata import get_setpoint_limits as _sp_limits
from .psdata import get_polarity as _get_polarity
import siriuspy.csdevice as _csdevice
from .controller import ControllerSim as _ControllerSim


class PowerSupply:
    """Magnet Power Supply model

    This class implements a model of the basic power supply of magnets.
    All basic properties, CtrlMode-Mon, PwrState-(Sel/Sts), OprMode-(Sel/Sts) and
    Current-(SP/RB) are implemented. Additional specific properties may be
    implemented in subclasses.

    The model uses a Controller object to drive updates of property values.
    a) The default controller object is a power supply drive simulator.
    b) It could also be an object that updates the model properties by reading
    the physical power supply. In this case the PS model can be used to feed
    the IOC with PV data.
    c) Another application of the PS model is where the controller updates the
    model properties by readinf a lower level PS IOC.
    """

    def __init__(self, ps_name, controller=None, enum_keys=False):

        self._ps_name = ps_name
        self._pstype_name = _conv_psname_2_pstype(ps_name)
        self._polarity = _get_polarity(self._pstype_name)
        self._setpoint_limits = _sp_limits(self._pstype_name)
        self._database = _csdevice.get_database(self._pstype_name)
        if self._database is None:
            raise Exception('no database defined for power supply type "' + self._pstype_name + '"!')
        self._enum_keys = enum_keys
        self._controller = controller
        self._controller_init()

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
        return _copy.deepcopy(self._database) # deepcopy for safety

    @property
    def setpoint_limits(self):
        return _copy.deepcopy(self._setpoint_limits)

    @property
    def reset_cmd(self):
        return None

    @property
    def ctrlmode_mon(self):
        self._controller_read_status()
        return self._get('CtrlMode-Mon')

    @property
    def pwrstate_sel(self):
        return self._get('PwrState-Sel')

    @property
    def opmode_sel(self):
        return self._get('OpMode-Sel')

    @property
    def current_sp(self):
        self._controller_read_status()
        return self._get('Current-SP')

    @property
    def pwrstate_sts(self):
        self._controller_read_status()
        return self._get('PwrState-Sts')

    @property
    def opmode_sts(self):
        self._controller_read_status()
        return self._get('OpMode-Sts')

    @property
    def current_rb(self):
        self._controller_read_status()
        return self._get('Current-RB')

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        if self._get_enum('CtrlMode-Mon') != 'Remote': return
        self._set('PwrState-Sel',value)
        self._controller.pwrstate = self._get_idx('PwrState-Sel')
        self._controller_read_status()

    @opmode_sel.setter
    def opmode_sel(self, value):
        if self._get_enum('CtrlMode-Mon') != 'Remote': return
        self._set('OpMode-Sel',value)
        #self._controller.current = self._get('Current-SP')
        self._controller.opmode = self._get_idx('OpMode-Sel')
        self._controller_read_status()

    @current_sp.setter
    def current_sp(self, value):
        if self._get_enum('CtrlMode-Mon') != 'Remote': return
        value = float(value)
        value = self._check_IOC_setpoint_limits(value)
        self._set('Current-SP',value)
        self._controller.current_ref = value
        self._controller_read_status()

    @reset_cmd.setter
    def reset_cmd(self, value):
        if self._get_enum('CtrlMode-Mon') != 'Remote': return
        self.opmode_sel = self._get_value('OpMode-Sel','SlowRef')
        self.current_sp = 0.0
        # reset status flags to be implemented!
        self._controller_read_status()

    def timing_trigger(self):
        self._controller.timing_trigger()

    def _check_IOC_setpoint_limits(self, value):
        l = self.setpoint_limits.values()
        _min, _max = min(l), max(l)
        value = _min if value < _min else value
        value = _max if value > _max else value
        return value
        # l = self.setpoint_limits
        # if value > l['HIHI']: return l['HIHI']
        # if value < l['LOLO']: return l['LOLO']
        # return value

    def _controller_init(self):
        if self._controller is None:
            l = self.setpoint_limits
            self._controller = _ControllerSim(current_min = l['DRVL'],
                                              current_max = l['DRVH'],
                                              fluctuation_rms=0.050)
        # initial config of controller
        self._controller.IOC = self
        self._controller.pwrstate = self._get_idx('PwrState-Sel')
        self._controller.opmode = self._get_idx('OpMode-Sel')
        self._controller.current_ref = self._get_idx('Current-SP')

    def _controller_read_status(self):
        self._set_idx('PwrState-Sts', self._controller.pwrstate)
        self._set_idx('OpMode-Sts', self._controller.opmode)
        self._set('Current-RB', self._controller.current)


    def _get_value(self, propty_name, enum_value):
        "Return either the passed enum_value, of enum_keys is set, or its index."
        p = self._database[propty_name]
        return enum_value if self._enum_keys else p['enums'].index(enum_value)

    def _get_enum(self, propty_name):
        """Return the enum value of a enum property in the DB, if applicable."""
        p = self._database[propty_name]
        return p['enums'][p['value']] if p['type'] == 'enum' else p['value']

    def _get_idx(self, propty_name):
        """Return the index value of a enum property in the DB, or the value of a non-enum property."""
        p = self._database[propty_name]
        return p['value']

    def _get(self, propty_name):
        """return either the enum or index value of enum properties in DB, if applicable."""
        # return either the index or the enum value of a enum property
        p = self._database[propty_name]
        return p['value'] if (p['type'] != 'enum' or not self._enum_keys) else self._get_enum(propty_name)

    def _set_enum(self, propty_name, value):
        p = self._database[propty_name]
        p['value'] = p['enums'].index(value)

    def _set_idx(self, propty_name, value):
        p = self._database[propty_name]
        p['value'] = value

    def _set(self, propty_name, value):
        p = self._database[propty_name]
        if self._enum_keys and p['type'] == 'enum':
            self._set_enum(propty_name, value)
        else:
            p['value'] = value

    def __str__(self):
        self._controller_read_status()
        st_controller = self._controller.__str__()
        st  =   '{0:<20s}: {1}'.format('power_supply', self._ps_name)
        st += '\n{0:<20s}: {1}'.format('type', self._pstype_name)
        st += '\n{0:<20s}: {1}'.format('polarity', self._polarity)
        l = self.setpoint_limits
        st += '\n{0:<20s}: {1} {2}'.format('limits', min(l.values()),max(l.values()))
        st += '\n--- IOC ---'
        propty = 'CtrlMode-Mon';  st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'PwrState-Sel';  st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'PwrState-Sts';  st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'OpMode-Sel';    st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'OpMode-Sts';    st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'Current-SP';    st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'Current-RB';    st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        st += '\n' + st_controller
        return st
