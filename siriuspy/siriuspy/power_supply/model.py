
from .psdata import get_ps_data as _get_ps_data
import siriuspy.cs_device as _cs_device
import copy as _copy


_psdata = _get_ps_data()


class MagnetPSModel:

    def __init__(self, name, enum_keys=False):

        self._name = name
        self._pstype_name = _psdata.get_ps2pstype(name)
        self._polarity = _psdata.get_polarity(self._pstype_name)
        self._setpoint_limits = _psdata.get_setpoint_limits(self._pstype_name)
        device = _cs_device.get_psclass(self._pstype_name)
        self._database = device.get_database()
        self._enum_keys = enum_keys
        self._controller_DCCT_current = self.current_rb

    @property
    def name(self):
        return self._name

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
    def enum_keys(self):
        return self._enum_keys

    @property
    def ctrlmode_mon(self):
        return self._get('CtrlMode-Mon')

    @property
    def pwrstate_sel(self):
        return self._get('PwrState-Sel')

    @property
    def pwrstate_sts(self):
        return self._get('PwrState-Sts')

    @property
    def opmode_sel(self):
        return self._get('OpMode-Sel')

    @property
    def opmode_sts(self):
        return self._get('OpMode-Sts')

    @property
    def current_rb(self):
        return self._get('Current-RB')

    @property
    def current_sp(self):
        return self._get('Current-SP')

    @current_sp.setter
    def current_sp(self, value):
        if self._get_enum('CtrlMode-Mon') != 'Remote': return
        #if value == self._get('Current-SP') : return # ???

        value = self._check_IOC_setpoint_limits(value)
        self._set('Current-SP',value) # is this correct?
        self._controller_setpoint(value)
        self._controller_read_status()

    @opmode_sel.setter
    def opmode_sel(self, value):
        if self._get_enum('CtrlMode-Mon') != 'Remote': return
        #if value == self._get('OpMode-Sel') : return # ???

        self._set('OpMode-Sel',value)
        self._controller_setopmode(value)
        self._controller_read_status()

    @pwrstate_sel.setter
    def pwrstate_sel(self, value):
        if self._get_enum('CtrlMode-Mon') != 'Remote': return
        #if value == self._get('PwrState-Sel') : return # ???

        self._set('PwrState-Sel',value)
        if self._get_enum('PwrState-Sel') == 'Off':
            self._controller_power_off()
        else:
            self._controller_power_on()
        self._controller_read_status()

    def _check_IOC_setpoint_limits(self, value):
        l = self.setpoint_limits
        if value > l['HIHI']: return l['HIHI']
        if value < l['LOLO']: return l['LOLO']
        return value

    def _controller_read_status(self):
        self._set('Current-RB', self._controller_DCCT_current)

    def _controller_power_off(self):
        self._set_enum('PwrState-Sts','Off')
        self._controller_DCCT_current = 0.0

    def _controller_power_on(self):
        self._set_enum('PwrState-Sts','On')
        if self._get_enum('OpMode-Sts') == 'SlowRef':
            self._controller_DCCT_current = self._get('Current-SP')

    def _controller_setpoint(self, value):
        if self._get_enum('PwrState-Sts') == 'On':
            if self._get_enum('OpMode-Sts') == 'SlowRef':
                self._controller_DCCT_current = value

    def _controller_setopmode(self, value):
        self._set('OpMode-Sts',value)
        self._controller_setpoint(self._get('Current-SP'))

    def _get_enum(self, propty_name):
        # return the enum value of a enum property, if applicable
        p = self._database[propty_name]
        return p['enums'][p['value']] if p['type'] == 'enum' else p['value']

    def _get(self, propty_name):
        # return either the index or the enum value of a enum property
        p = self._database[propty_name]
        return p['value'] if (p['type'] != 'enum' or not self._enum_keys) else self._get_enum(propty_name)

    def _set_enum(self, propty_name, value):
        p = self._database[propty_name]
        p['value'] = p['enums'].index(value)

    def _set(self, propty_name, value):
        p = self._database[propty_name]
        if self._enum_keys and p['type'] == 'enum':
            self._set_enum(propty_name, value)
        else:
            p['value'] = value

    def __str__(self):
        st = ''
        propty = 'CtrlMode-Mon';  st +=   '{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'PwrState-Sel';  st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'PwrState-Sts';  st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'OpMode-Sel';    st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'OpMode-Sts';    st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'Current-SP';    st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        propty = 'Current-RB';    st += '\n{0:<20s}: {1}'.format(propty, self._get_enum(propty))
        return st
