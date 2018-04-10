"""Define the high level classes."""

from functools import partial as _partial
from functools import reduce as _reduce
import operator
import logging as _log
from copy import deepcopy as _dcopy
from threading import Lock as _Lock
from scipy.stats import mode as _mode
from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity
from siriuspy.thread import RepeaterThread as _Timer
from siriuspy.search import HLTimeSearch as _HLSearch
from siriuspy.csdevice import timesys as _cstime
from as_ti_control.ll_classes import get_ll_trigger_object as \
    _get_ll_trigger_object
from as_ti_control.ll_classes import INTERVAL as _INTERVAL

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
        for pv, dt in db.items():
            prop = self._get_prop_name(pv)
            if prop not in self._interface_props:
                continue
            db2[pv] = _dcopy(dt)
            if pv.endswith(('-SP', '-Sel', '-Cmd')):
                db2[pv]['fun_set_pv'] = _partial(self.write, prop)
                print(pv, prop)
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
        print(prop_name)
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

    def _get_prop_name(self, pvname):
        return pvname[len(self.prefix):].split('-')[0]

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
        db = _cstime.get_hl_evg_database(self.prefix, only_evg=True)
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

    def get_database(self, prefix=None):
        """Get the database."""
        db = _cstime.get_hl_clock_database(self.prefix)
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
        db = _cstime.get_hl_event_database(self.prefix)
        db = super().get_database(db)
        db[self._get_pv_name('ExtTrig')]['fun_set_pv'] = self.set_ext_trig
        return db

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

    def get_database(self):
        """Get the database."""
        db = _cstime.get_hl_trigger_database(hl_trigger=self.prefix)
        return super().get_database(db)

    def __init__(self, hl_trigger, callback):
        """Appropriately initialize the instance."""
        self._interface_props = _HLSearch.get_hl_trigger_interface(hl_trigger)
        self._ll_objs_names = _HLSearch.get_ll_trigger_names(hl_trigger)
        self._my_state = dict()
        for prop in self._interface_props - {'Status'}:
            val = _HLSearch.get_hl_trigger_prop_value(hl_trigger, prop)
            self._my_state[prop] = val
        self._source_enums = _HLSearch.get_hl_trigger_sources(hl_trigger)
        super().__init__(
            hl_trigger, callback,
            connect_kwargs={'source_enums': self._source_enums}
            )

    def _combine_status(self, dic_):
        def get_bit(val, bit):
            return (val << bit) & 1

        status = _reduce(operator.or_, dic_.values())
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
