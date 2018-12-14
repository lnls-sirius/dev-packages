"""Define the high level classes."""

import time as _time
from functools import partial as _partial, reduce as _reduce
from operator import or_ as _or_, and_ as _and_
import logging as _log
from pcaspy import Alarm as _Alarm, Severity as _Severity
from siriuspy.util import get_bit as _get_bit, mode as _mode
from siriuspy.callbacks import Callback
from siriuspy.thread import RepeaterThread as _Timer
from siriuspy.search import HLTimeSearch as _HLSearch
from siriuspy.csdevice import timesys as _cstime
from .ll_classes import get_ll_trigger as _get_ll_trigger, \
            LLEvent as _LLEvent, get_evg_name as _get_evg_name

_INTERVAL = 0.01


# HL == High Level
class _HLBase(Callback):
    """Define a High Level interface.

    Determine how to connect the driver with the classes which communicate
    with low level IOCs.
    """

    _SUFFIX_FOR_PROPS = {}

    def __init__(self, prefix, ll_objs, callback=None):
        """Appropriately initialize the instance.

        prefix = first part of the pv name of this object.
        callback = callable to be called when readbacks are updated.
        """
        super().__init__(callback=callback)
        _log.info(prefix + ' Starting.')
        self.prefix = prefix
        self._ll_objs = ll_objs
        self._funs_combine_values = self._define_funs_combine_values()
        self._all_props_suffix = self._get_properties_suffix()
        self._timer = None
        self._start_timer()
        for obj in self._ll_objs:
            obj.add_callback(self._on_change_pvs)

    @property
    def locked(self):
        return _reduce(_and_, map(lambda x: x.locked, self._ll_objs))

    @locked.setter
    def locked(self, value):
        for obj in self._ll_objs:
            obj.locked = bool(value)

    def get_database(self):
        return NotImplemented

    def write(self, prop_name, value):
        """Function to be called by the IOC to set high level properties.

        It not only sets the new high level property value but also forwards it
        to the low level classes.
        """
        return _reduce(_and_, map(
                    lambda x: x.write(prop_name, value), self._ll_objs))

    def read(self, prop_name, is_sp=False):
        fun = self._funs_combine_values.get(prop_name, self._combine_default)
        vals = map(lambda x: x.read(prop_name, is_sp=is_sp), self._ll_objs)
        return fun(vals)

    def readall(self, is_sp=False):
        values = dict()
        for prop, suf in self._all_props_suffix.items():
            if suf == '-Cmd' or (is_sp and suf not in ('-RB', '-Sts')):
                continue
            value = self.read(prop, is_sp=is_sp)
            if value is None or not value:
                return
            values[prop] = value
        return values

    def get_map2writepvs(self):
        """Get the database."""
        db = self.get_database()
        map2write = dict()
        for pvname in db:
            prop = self._get_prop_name(pvname)
            if pvname.endswith(('-SP', '-Sel', '-Cmd')):
                map2write[pvname] = _partial(self.write, prop)
        return map2write

    def get_map2readpvs(self):
        """Get the database."""
        db = self.get_database()
        map2readpvs = dict()
        for pvname in db:
            if self._isctepv(pvname) or self._iscmdpv(pvname):
                continue
            prop = self._get_prop_name(pvname)
            map2readpvs[pvname] = _partial(
                            self.read, prop, is_sp=self._issppv(pvname))
        return map2readpvs

    def _on_change_pvs(self, channel, prop, value, is_sp=False, **kwargs):
        self._start_timer()

    def _start_timer(self, *args, **kwargs):
        if self._timer is not None and self._timer.is_alive():
            self._timer.reset()
        else:
            self._timer = _Timer(0, self._update_pvs_thread, niter=1)
            self._timer.start()

    def _update_pvs_thread(self):
        _time.sleep(_INTERVAL)  # limit update in 100Hz
        for prop, suf in self._all_props_suffix.items():
            if suf == '-Cmd':
                continue
            value = self.read(prop)
            if value is None:
                return
            self.run_callbacks(self._get_pv_name(prop), **value)
            if suf not in ('-RB', '-Sts'):
                continue
            value = self.read(prop, is_sp=True)
            if value is None:
                return
            self.run_callbacks(self._get_pv_name(prop, is_sp=True), **value)

    def _define_funs_combine_values(self):
        """Define a dictionary of functions to combine low level values.

        Any property not defined here will use the default method:
            _combine_default.
        """
        return dict()

    def _get_properties_suffix(self):
        db = self.get_database()
        props = dict()
        for pvname in db:
            if not pvname.endswith('-Cte'):
                prop, suf = self._get_prop_name(pvname, with_suffix=True)
                props[prop] = suf
        return props

    def _get_pv_name(self, prop, is_sp=False):
        pvname = self.prefix + prop + self._all_props_suffix[prop]
        if is_sp:
            pvname = pvname.replace('-RB', '-SP').replace('-Sts', '-Sel')
        return pvname

    def _get_prop_name(self, pvname, with_suffix=False):
        ret = pvname[len(self.prefix):].split('-')
        if with_suffix:
            return ret[0], '-' + ret[1]
        else:
            return ret[0]

    def _combine_default(self, values):
        value, cnt = _mode(sorted(values))
        alarm = _Alarm.NO_ALARM
        severity = _Severity.NO_ALARM
        if cnt < len(self._ll_objs):
            alarm = _Alarm.COMM_ALARM
            severity = _Severity.INVALID_ALARM
        return {'value': value, 'alarm': alarm, 'severity': severity}


class HLEvent(_HLBase):
    """High Level control of the Events of the EVG.

    Creates
    """
    def __init__(self, ev_hl, callback=None):
        """Initialize object.

        ev_ll: low level event code
        """
        evg_name = _get_evg_name()
        ev_ll = _cstime.Const.EvtHL2LLMap[ev_hl]
        ll_objs = [_LLEvent(evg_name + ':' + ev_ll), ]
        prefix = evg_name + ':' + ev_hl
        super().__init__(prefix, ll_objs, callback=callback)

    def get_database(self):
        """Create the database of the class."""
        return _cstime.get_hl_event_database(self.prefix)


class HLTrigger(_HLBase):
    """High level Trigger interface."""

    def __init__(self, hl_trigger, callback=None):
        """Appropriately initialize the instance."""
        src_enums = _cstime.get_hl_trigger_database(hl_trigger=hl_trigger)
        src_enums = src_enums['Src-Sel']['enums']
        ll_objs = list()
        for name in _HLSearch.get_ll_trigger_names(hl_trigger):
            ll_objs.append(_get_ll_trigger(
                channel=name, source_enums=src_enums))
        super().__init__(hl_trigger + ':', ll_objs, callback=callback)

    def get_database(self):
        """Get the database."""
        return _cstime.get_hl_trigger_database(
            hl_trigger=self.prefix[:-1], prefix=self.prefix)

    def get_ll_triggers(self):
        return self._ll_objs

    def get_ll_trigger_names(self):
        return _HLSearch.get_ll_trigger_names(self.prefix[:-1])

    def get_ll_channels(self):
        return _HLSearch.get_hl_trigger_channels(self.prefix[:-1])

    def _combine_status(self, values):
        status = _reduce(_or_, values)
        alarm = _Alarm.NO_ALARM
        severity = _Severity.NO_ALARM
        if _get_bit(status, 0):
            # 'PVsConn'
            alarm = _Alarm.COMM_ALARM
            severity = _Severity.INVALID_ALARM
        elif _get_bit(status, 1) | _get_bit(status, 2) | _get_bit(status, 3):
            # 'DevEnbl', 'FoutDevEnbl', 'EVGDevEnbl'
            alarm = _Alarm.DISABLE_ALARM
            severity = _Severity.INVALID_ALARM
        elif (_get_bit(status, 5) | _get_bit(status, 6) |
              _get_bit(status, 7) | _get_bit(status, 8)):
            # 'Link' 'Loss'
            alarm = _Alarm.LINK_ALARM
            severity = _Severity.INVALID_ALARM
        elif _get_bit(status, 4):
            # 'Network'
            alarm = _Alarm.COMM_ALARM
            severity = _Severity.MINOR_ALARM
        elif _get_bit(status, 9):
            # 'IntlkMon'
            alarm = _Alarm.STATE_ALARM
            severity = _Severity.MINOR_ALARM
        return {'value': status, 'alarm': alarm, 'severity': severity}

    def _define_funs_combine_values(self):
        """Define a dictionary of functions to combine low level values."""
        return {'Status': self._combine_status}
