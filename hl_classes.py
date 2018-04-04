"""Define the high level classes."""

import functools
import operator
import logging as _log
from copy import deepcopy as _dcopy
from threading import Lock as _Lock
from scipy.stats import mode as _mode
from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity
from siriuspy.thread import RepeaterThread as _Timer
from siriuspy.timesys.time_data import Triggers as _Triggers
from siriuspy.timesys.time_data import Clocks as _Clocks
from siriuspy.timesys.time_data import Events as _Events
from as_ti_control.ll_classes import get_ll_trigger_object as \
    _get_ll_trigger_object
from as_ti_control.ll_classes import INTERVAL as _INTERVAL

from as_ti_control.ll_classes import get_ll_trigger_obj_names as \
    _get_ll_trigger_obj_names
from as_ti_control.ll_classes import LL_Event as _LL_Event
from as_ti_control.ll_classes import LL_Clock as _LL_Clock
from as_ti_control.ll_classes import LL_EVG as _LL_EVG
from as_ti_control.ll_classes import EVG_NAME as _EVG_NAME


# HL == High Level
class _HL_Base:
    """Define a High Level interface.

    Determine how to connect the driver with the classes which communicate
    with low level IOCs.
    """

    _SUFFIX_FOR_PROPS = {}

    @staticmethod
    def _get_LL_OBJ(**kwargs):
        return None  # must return the low level object.

    def get_database(self, db):
        """Get the database."""
        db2 = dict()
        for prop_name in self._interface_props:
            name = self._get_pv_name(prop_name)
            db2[name] = db[name]
            name = name.replace('-RB', '-SP').replace('-Sts', '-Sel')
            db2[name] = db[name]
        return db2      # dictionary must have key fun_set_pv

    def __init__(self, prefix, callback, connect_kwargs=dict()):
        """Appropriately initialize the instance.

        prefix = is the first part of the pv name of this object.
        callback = is the callable to be called when readbacks are updated.
        """
        _log.info(prefix + ' Starting.')
        self.callback = callback
        self.prefix = prefix
        self._connect_kwargs = connect_kwargs
        self._funs_combine_rb_values = self._get_funs_combine_rb_values()
        self._initialize_rb_values()
        self._timer = _Timer(_INTERVAL, self._deal_with_rb_news, niter=0)
        self._timer.start()

    def connect(self):
        self._ll_objs = dict()
        _log.info(self.prefix+' -> connecting to LL Devices')
        for chan in self._ll_objs_names:
            self._ll_objs[chan] = self._get_LL_OBJ(
                                channel=chan,
                                callback=self._on_change_pvs_rb,
                                init_hl_state=_dcopy(self._my_state),
                                **self._connect_kwargs)

    def write(self, prop_name, value):
        """Function to be called by the IOC to set high level properties.

        It not only sets the new high level property value but also forwards it
        to the low level classes.
        """
        if value == self._my_state[prop_name]:
            return True
        self._my_state[prop_name] = value
        for dev, obj in self._ll_objs.items():
            obj.write(prop_name, value)
        return True

    def _on_change_pvs_rb(self, channel, prop_name, value):
        if prop_name not in self._interface_props:
            if self._my_state[prop_name] != value:
                _log.warning(self.prefix + prop_name +
                             ' (not HL); ' + ' LL Device = ' + channel +
                             '; New Value = ' + str(value) +
                             '; Expected Value = ' +
                             str(self._my_state[prop_name]))
            return
        with self._lock_rb_to_deal:
            self._rb_values[prop_name][channel] = value
            self._rb_news[prop_name] = True

    def _deal_with_rb_news(self):
        for k, v in self._rb_news.items():
            if not v:
                continue
            fun = self._funs_combine_rb_values.get(k, self._combine_default)
            with self._lock_rb_to_deal:
                dic_ = self._rb_values[k]
                value = fun(dic_)
                self._rb_news[k] = False
            self.callback(self._get_pv_name(k), **value)

    def _get_funs_combine_rb_values(self):
        """Define a dictionary of functions to combine low level values.

        Any property not defined here will use the default method:
            _combine_default.
        """
        return dict()

    def _get_pv_name(self, prop_name):
        return self.prefix + prop_name + self._SUFFIX_FOR_PROPS[prop_name]

    def _initialize_rb_values(self):
        self._lock_rb_to_deal = _Lock()
        self._rb_values = dict()
        self._rb_news = dict()
        db = self.get_database()
        for k in self._interface_props:
            self._rb_news[k] = False
            self._rb_values[k] = dict()
            for k2 in self._ll_objs_names:
                self._rb_values[k][k2] = db[self._get_pv_name(k)]['value']

    def _combine_default(self, dic_):
        res = _mode(sorted(dic_.values()))
        value = res.mode[0]
        alarm = _Alarm.NO_ALARM
        severity = _Severity.NO_ALARM
        if res.count[0] < len(self._ll_objs_names):
            alarm = _Alarm.COMM_ALARM
            severity = _Severity.INVALID_ALARM
        return {'value': value, 'alarm': alarm, 'severity': severity}


class HL_EVG(_HL_Base):
    """High Level control of the EVG.

    Designed to convert the repetition rate to Hz instead of the low level
    integer representing the numtiple of the AC line period.

    All other PVs of EVG, like bucket list, are read directly from the
    low level IOC.
    """

    _SUFFIX_FOR_PROPS = {'RepRate': '-RB'}

    @staticmethod
    def _get_LL_OBJ(**kwargs):
        return _LL_EVG(**kwargs)

    def get_database(self):
        """Get the database."""
        db = dict()
        pre = self.prefix
        dic_ = {'type': 'float', 'value': self._my_state['RepRate'],
                'unit': 'Hz', 'prec': 6,
                'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
                'hilim': 60, 'high': 60, 'hihi': 60}
        db[pre + 'RepRate-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('RepRate', x)
        db[pre + 'RepRate-SP'] = dic_
        return super().get_database(db)

    def __init__(self, callback):
        """Initialize the instance."""
        self._interface_props = {'RepRate'}
        self._my_state = {'RepRate': 2.0}
        self._ll_objs_names = [_EVG_NAME + ':', ]
        super().__init__(_EVG_NAME + ':', callback)


class HL_Clock(_HL_Base):
    """High Level control of the Clocks of the EVG."""

    _SUFFIX_FOR_PROPS = {'Freq': '-RB', 'State': '-Sts'}

    @staticmethod
    def _get_LL_OBJ(**kwargs):
        return _LL_Clock(**kwargs)

    def get_database(self):
        """Get the database."""
        db = dict()
        pre = self.prefix
        dic_ = {
            'type': 'float', 'value': self._my_state['Freq'],
            'unit': 'kHz', 'prec': 6,
            'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
            'hilim': 125000000, 'high': 125000000, 'hihi': 125000000}
        db[pre + 'Freq-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Freq', x)
        db[pre + 'Freq-SP'] = dic_

        db[pre + 'State-Sel'] = {
            'type': 'enum', 'enums': _Clocks.STATES,
            'value': self._my_state['State'],
            'fun_set_pv': lambda x: self.write('State', x)}
        db[pre + 'State-Sts'] = {
            'type': 'enum', 'enums': _Clocks.STATES,
            'value': self._my_state['State']}
        return super().get_database(db)

    def __init__(self, prefix, callback, cl_ll):
        """Initialize the instance.

        cl_ll: clock number
        """
        self._interface_props = {'Freq', 'State'}
        self._my_state = {'Freq': 1.0, 'State': 0}
        self._ll_objs_names = [_EVG_NAME + ':' + cl_ll]
        super().__init__(prefix, callback)


class HL_Event(_HL_Base):
    """High Level control of the Events of the EVG.

    Creates
    """

    _SUFFIX_FOR_PROPS = {
        'Delay': '-RB',
        'Mode': '-Sts',
        'DelayType': '-Sts',
        'ExtTrig': '-Cmd'}

    @staticmethod
    def _get_LL_OBJ(**kwargs):
        return _LL_Event(**kwargs)

    def get_database(self):
        """Create the database of the class."""
        db = dict()
        pre = self.prefix

        dic_ = {'type': 'float', 'unit': 'us', 'prec': 4,
                'value': self._my_state['Delay'],
                'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
                'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
        db[pre + 'Delay-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Delay', x)
        db[pre + 'Delay-SP'] = dic_

        dic_ = {'type': 'enum', 'enums': _Events.MODES,
                'value': self._my_state['Mode'],
                'states': ()}
        db[pre + 'Mode-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Mode', x)
        db[pre + 'Mode-Sel'] = dic_

        dic_ = {'type': 'enum', 'enums': _Events.DELAY_TYPES,
                'value': self._my_state['DelayType']}
        db[pre + 'DelayType-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('DelayType', x)
        db[pre + 'DelayType-Sel'] = dic_

        db[pre + 'ExtTrig-Cmd'] = {
            'type': 'int', 'value': self._my_state['ExtTrig'],
            'unit': 'When in External Mode generates Event.',
            'fun_set_pv': self.set_ext_trig}
        return super().get_database(db)

    def __init__(self, prefix, callback, ev_ll):
        """Initialize object.

        ev_ll: low level event code
        """
        self._interface_props = {'Delay', 'DelayType', 'Mode', 'ExtTrig'}
        self._my_state = {'Delay': 0, 'Mode': 1,
                          'DelayType': 1, 'ExtTrig': 0}
        self._ll_objs_names = [_EVG_NAME + ':' + ev_ll]
        super().__init__(prefix, callback)

    def set_ext_trig(self, value):
        """Set the external trigger command."""
        self._my_state['ExtTrig'] = 0
        return self.write('ExtTrig', value)


class HL_Trigger(_HL_Base):
    """High level Trigger interface."""

    _SUFFIX_FOR_PROPS = {
        'State': '-Sts',
        'Src': '-Sts',
        'Duration': '-RB',
        'Polarity': '-Sts',
        'Pulses': '-RB',
        'Intlk': '-Sts',
        'Delay': '-RB',
        'DelayType': '-Sts',
        'Status': '-Mon',
        }

    @staticmethod
    def _get_LL_OBJ(**kwargs):
        return _get_ll_trigger_object(**kwargs)

    @staticmethod
    def _get_ll_obj_names(chans):
        return _get_ll_trigger_obj_names(chans)

    def get_database(self):
        """Get the database."""
        db = dict()
        pre = self.prefix

        dic_ = {'type': 'enum', 'enums': _Triggers.STATES}
        dic_.update(self._pvs_config['State'])
        db[pre + 'State-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('State', x)
        db[pre + 'State-Sel'] = dic_

        dic_ = {'type': 'enum'}
        dic_.update(self._pvs_config['Src'])
        db[pre + 'Src-Sts'] = _dcopy(dic_)
        db[pre + 'Src-Sts']['enums'] += ('Invalid', )  # for completeness
        dic_['fun_set_pv'] = lambda x: self.write('Src', x)
        db[pre + 'Src-Sel'] = dic_

        dic_ = {'type': 'float', 'unit': 'ms', 'prec': 6,
                'lolo': 0.000008, 'low': 0.000008, 'lolim': 0.000008,
                'hilim': 500, 'high': 1000, 'hihi': 10000}
        dic_.update(self._pvs_config['Duration'])
        db[pre + 'Duration-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Duration', x)
        db[pre + 'Duration-SP'] = dic_

        dic_ = {'type': 'enum', 'enums': _Triggers.POLARITIES}
        dic_.update(self._pvs_config['Polarity'])
        db[pre + 'Polarity-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Polarity', x)
        db[pre + 'Polarity-Sel'] = dic_

        dic_ = {'type': 'int', 'unit': 'numer of pulses',
                # 'lolo': 1, 'low': 1, 'lolim': 1,
                'hilim': 2001, 'high': 10000, 'hihi': 100000}
        dic_.update(self._pvs_config['Pulses'])
        db[pre + 'Pulses-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Pulses', x)
        db[pre + 'Pulses-SP'] = dic_

        dic_ = {'type': 'enum', 'enums': _Triggers.INTLK}
        dic_.update(self._pvs_config['Intlk'])
        db[pre + 'Intlk-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Intlk', x)
        db[pre + 'Intlk-Sel'] = dic_

        dic_ = {'type': 'float', 'unit': 'us', 'prec': 6,
                'lolo': 0.0, 'low': 0.0, 'lolim': 0.0,
                'hilim': 500000, 'high': 1000000, 'hihi': 10000000}
        dic_.update(self._pvs_config['Delay'])
        db[pre + 'Delay-RB'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('Delay', x)
        db[pre + 'Delay-SP'] = dic_

        dic_ = {'type': 'enum'}
        dic_.update(self._pvs_config['DelayType'])
        db[pre + 'DelayType-Sts'] = _dcopy(dic_)
        dic_['fun_set_pv'] = lambda x: self.write('DelayType', x)
        db[pre + 'DelayType-Sel'] = dic_

        dic_ = {'type': 'int', 'value': 255}
        db[pre + 'Status-Mon'] = _dcopy(dic_)

        db[pre + 'Status-Cte'] = {
            'type': 'string', 'count': 8,
            'value': (
                'All PVs connected',
                'Device Enabled',
                'FOUT Enabled',
                'EVG Enabled',
                'Network Ok',
                'Interlock Not Active',
                'UPLink Ok',
                'DownLink Ok',
                )
            }
        return super().get_database(db)

    def __init__(self, prefix, callback, channels, hl_props, pvs_config):
        """Appropriately initialize the instance.

        channels = is a list of unique identifiers with the format:
            <DeviceName>:<Output>
        for all the low level objects associated with this object:
        hl_props = is a set with high level properties that will be available
          for changes in the High Level Interface. All the possible values are:
            {'State', 'Src', 'Duration', 'Polarity', 'Pulses', 'Intlk',
             'Delay', 'DelayType'}
        pvs_config = initial values for all the high level properties.
        """
        self._interface_props = hl_props | {'Status'}
        self._pvs_config = pvs_config
        self._ll_objs_names = self._get_ll_obj_names(channels)
        self._my_state = {k: v['value'] for k, v in pvs_config.items()}
        self._set_non_homogeneous_params()
        super().__init__(
            prefix, callback,
            connect_kwargs={'source_enums': self._source_enums}
            )

    def _has_delay_type(self, name):
        if name.dev in ('EVR', 'EVE') and name.propty.startswith('OUT'):
            return True
        else:
            return False

    def _has_clock(self, name):
        if name.dev in {'EVE', 'AFC'}:
            return True
        elif name.dev == 'EVR':
            return True if name.propty.startswith('OUT') else False
        else:
            raise Exception('Error: ' + name)

    def _set_non_homogeneous_params(self):
        has_clock = []
        has_delay_type = []
        for name in self._ll_objs_names:
            has_clock.append(self._has_clock(name))
            has_delay_type.append(self._has_delay_type(name))
        dic_ = self._pvs_config['Src']
        # EVG_params_ENUMS
        if all(has_clock):
            dic_['enums'] += tuple(sorted(_Clocks.HL2LL_MAP.keys()))+('Dsbl', )
        elif any(has_clock):
            _log.warning('Some triggers of ' + self.prefix +
                         ' are connected to unsimiliar low level devices.')
        self._source_enums = list(dic_['enums'])
        # Delay Typess
        dic_ = self._pvs_config['DelayType']
        dic_['enums'] = (_Triggers.DELAY_TYPES[0], )
        if all(has_delay_type):
            dic_['enums'] = _Triggers.DELAY_TYPES
        elif any(has_delay_type):
            _log.warning('Some triggers of ' + self.prefix +
                         ' are connected to unsimiliar low level devices.')
        else:
            self._interface_props.discard('DelayType')
            self._interface_props.discard('Intlk')
        return

    def _combine_status(self, dic_):
        def get_bit(val, bit):
            return (val << bit) & 1

        status = functools.reduce(operator.or_, dic_.values())
        alarm = _Alarm.NO_ALARM
        severity = _Severity.NO_ALARM
        if get_bit(status, 0):
            # 'PVsConn'
            alarm = _Alarm.COMM_ALARM
            severity = _Severity.INVALID_ALARM
        elif get_bit(status, 1) | get_bit(status, 2) | get_bit(status, 3):
            # 'DevEnbl', 'FOUTDevEnbl', 'EVGDevEnbl'
            alarm = _Alarm.DISABLE_ALARM
            severity = _Severity.INVALID_ALARM
        elif get_bit(status, 6) | get_bit(status, 7):
            # 'Link' 'Loss'
            alarm = _Alarm.LINK_ALARM
            severity = _Severity.INVALID_ALARM
        elif get_bit(status, 4):
            # 'Network'
            alarm = _Alarm.COMM_ALARM
            severity = _Severity.MINOR_ALARM
        elif get_bit(status, 5):
            # 'IntlkMon'
            alarm = _Alarm.STATE_ALARM
            severity = _Severity.MINOR_ALARM
        return {'value': status, 'alarm': alarm, 'severity': severity}

    def _get_funs_combine_rb_values(self):
        """Define a dictionary of functions to combine low level values."""
        return {'Status': self._combine_status}
