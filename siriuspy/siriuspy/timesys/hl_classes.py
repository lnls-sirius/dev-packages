"""Define the high level classes."""

import time as _time
from functools import partial as _partial, reduce as _reduce
from operator import or_ as _or_, and_ as _and_
import logging as _log
from threading import Lock as _Lock

import numpy as _np

from ..util import mode as _mode
from ..thread import RepeaterThread as _Timer
from ..search import HLTimeSearch as _HLSearch
from ..namesys import SiriusPVName as _PVName
from ..callbacks import Callback as _Callback

from .csdev import get_hl_trigger_database as _get_hl_trigger_database
from .ll_classes import get_ll_trigger as _get_ll_trigger


# HL == High Level
class _BaseHL(_Callback):
    """Define a High Level interface.

    Determine how to connect the driver with the classes which communicate
    with low level IOCs.
    """

    class Alarm:
        """."""

        NO = 0
        STATE = 7
        COMM = 9
        LINK = 14

    class Severity:
        """."""

        NO = 0
        MINOR = 1
        MAJOR = 2
        INVALID = 3

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
    def connected(self):
        """."""
        return all(map(lambda x: x.connected, self._ll_objs))

    def process(self):
        """."""
        return

    def wait_for_connection(self, timeout=None):
        """."""
        return all(map(
            lambda x: x.wait_for_connection(timeout=timeout), self._ll_objs))

    @property
    def locked(self):
        """."""
        dic_ = self._combine_default(map(lambda x: x.locked, self._ll_objs))
        return dic_['value']

    @locked.setter
    def locked(self, value):
        for obj in self._ll_objs:
            obj.locked = bool(value)
        self.run_callbacks(self._get_pv_name('LowLvlLock'), value=bool(value))

    def get_database(self):
        """."""
        return dict()

    def write(self, prop_name, value):
        """Write function to be called by the IOC to set high level properties.

        It not only sets the new high level property value but also forwards it
        to the low level classes.
        """
        if value is None:
            return False
        return _reduce(_and_, map(
            lambda x: x.write(prop_name, value), self._ll_objs))

    def read(self, prop_name, is_sp=False):
        """Read."""
        fun = self._funs_combine_values.get(prop_name, self._combine_default)
        vals = [x.read(prop_name, is_sp=is_sp) for x in self._ll_objs]
        return fun(vals)

    def readall(self, is_sp=False):
        """Read all."""
        values = dict()
        for prop, suf in self._all_props_suffix.items():
            if _PVName.is_cmd_pv(suf) or (is_sp and not _PVName.is_rb_pv(suf)):
                continue
            value = self.read(prop, is_sp=is_sp)
            if value is None or not value:
                continue
            values[prop] = value
        return values

    def get_map2writepvs(self):
        """Get the database."""
        dbase = self.get_database()
        map2write = dict()
        for pvname in dbase:
            prop = self._get_prop_name(pvname)
            if _PVName.is_write_pv(pvname):
                map2write[pvname] = _partial(self.write, prop)
        return map2write

    def get_map2readpvs(self):
        """Get the database."""
        dbase = self.get_database()
        map2readpvs = dict()
        for pvname in dbase:
            if _PVName.is_cte_pv(pvname) or _PVName.is_cmd_pv(pvname):
                continue
            prop = self._get_prop_name(pvname)
            map2readpvs[pvname] = _partial(
                self.read, prop, is_sp=_PVName.is_sp_pv(pvname))
        return map2readpvs

    def _on_change_pvs(self, *args, **kwargs):
        _ = args
        _ = kwargs
        self._start_timer()

    def _start_timer(self, *args, **kwargs):
        if self._timer is not None and self._timer.is_alive():
            self._timer.reset()
        else:
            self._timer = _Timer(0, self._update_pvs_thread, niter=1)
            self._timer.start()

    def _update_pvs_thread(self):
        _time.sleep(1/10)  # limit update in 10Hz
        for prop, suf in self._all_props_suffix.items():
            if _PVName.is_cmd_pv(suf):
                continue
            value = self.read(prop)
            if value is None:
                return
            self.run_callbacks(self._get_pv_name(prop), **value)
            # Uncomment this if you want to update setpoint PVs as well
            # This is not recommended though, because it can create very
            # strange unusual behavior with widgets such as spinbox in PyDM
            # and CS-Studio.
            if not _PVName.is_rb_pv(suf):
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
        dbase = self.get_database()
        props = dict()
        for pvname in dbase:
            if not _PVName.is_sp_pv(pvname) and not _PVName.is_cte_pv(pvname):
                prop, suf = self._get_prop_name(pvname, with_suffix=True)
                props[prop] = suf
        return props

    def _get_pv_name(self, prop, is_sp=False):
        pvname = self.prefix + prop + self._all_props_suffix[prop]
        if is_sp:
            pvname = _PVName.from_rb2sp(pvname)
        return pvname

    def _get_prop_name(self, pvname, with_suffix=False):
        ret = pvname[len(self.prefix):].split('-')
        if with_suffix:
            return ret[0], '-' + ret[1]
        else:
            return ret[0]

    def _combine_default(self, values):
        dic_ = {
            'alarm': self.Alarm.COMM,
            'severity': self.Severity.INVALID}
        values = [val for val in values if val is not None]
        if not values:
            dic_['value'] = None
            return dic_
        value, cnt = _mode(sorted(values))
        dic_['value'] = value
        if cnt == len(self._ll_objs):
            dic_['alarm'] = self.Alarm.NO
            dic_['severity'] = self.Severity.NO
        return dic_


class HLTrigger(_BaseHL):
    """High level Trigger interface."""

    def __init__(self, hl_trigger, callback=None):
        """Appropriately initialize the instance."""

        src_enums = _get_hl_trigger_database(hl_trigger=hl_trigger)
        src_enums = src_enums['Src-Sel']['enums']
        ll_obj_names = _HLSearch.get_ll_trigger_names(hl_trigger)

        self._hldelay_lock = _Lock()
        self._hldelay = 0
        self._hldeltadelay = _np.zeros(len(ll_obj_names), dtype=int)

        ll_objs = list()
        for name in ll_obj_names:
            ll_objs.append(_get_ll_trigger(
                channel=name, source_enums=src_enums))
        super().__init__(hl_trigger + ':', ll_objs, callback=callback)

    def process(self):
        """."""
        value = self.read('InInjTable')
        if value is None:
            return
        self.run_callbacks(self._get_pv_name('InInjTable'), **value)
        return

    def write(self, prop_name, value):
        """Call to set high level properties.

        It not only sets the new high level property value but also forwards it
        to the low level classes.
        """
        if value is None:
            return False
        if prop_name.startswith('DelayRaw'):
            with self._hldelay_lock:
                self._hldelay = int(value)
                value = self._hldelay + self._hldeltadelay
        elif prop_name.startswith('Delay'):
            prop_name = prop_name.replace('Delay', 'DelayRaw')
            with self._hldelay_lock:
                self._hldelay = int(round(value / self._ll_objs[0].base_del))
                value = self._hldelay + self._hldeltadelay
        elif prop_name.startswith('DeltaDelayRaw'):
            prop_name = prop_name.replace('DeltaDelayRaw', 'DelayRaw')
            with self._hldelay_lock:
                value = _np.array(value, dtype=int, ndmin=1)
                self._update_deltadelay(value)
                value = self._hldelay + self._hldeltadelay
        elif prop_name.startswith('DeltaDelay'):
            prop_name = prop_name.replace('DeltaDelay', 'DelayRaw')
            with self._hldelay_lock:
                value = _np.array(value, ndmin=1)
                value = _np.round(value / self._ll_objs[0].base_del)
                value = _np.array(value, dtype=int)
                self._update_deltadelay(value)
                value = self._hldelay + self._hldeltadelay
        else:
            value = len(self._ll_objs) * [value, ]

        boo = True
        for val, obj in zip(value, self._ll_objs):
            boo &= obj.write(prop_name, val)
        return boo

    def read(self, prop_name, is_sp=False):
        """."""
        fun = self._funs_combine_values.get(prop_name, self._combine_default)
        if prop_name.startswith('DeltaDelay'):
            prop_name = prop_name.replace('DeltaDelay', 'Delay')
        if prop_name.startswith('DeltaDelayRaw'):
            prop_name = prop_name.replace('DeltaDelayRaw', 'DelayRaw')
        if prop_name.startswith('LowLvlLock') and is_sp:
            vals = len(self._ll_objs) * [self.locked, ]
        else:
            vals = [x.read(prop_name, is_sp=is_sp) for x in self._ll_objs]
        return fun(vals)

    def get_database(self):
        """Get the database."""
        return _get_hl_trigger_database(
            hl_trigger=self.prefix[:-1], prefix=self.prefix)

    def get_ll_triggers(self):
        """."""
        return self._ll_objs

    def get_ll_trigger_names(self):
        """."""
        return _HLSearch.get_ll_trigger_names(self.prefix[:-1])

    def get_ll_channels(self):
        """."""
        return _HLSearch.get_hl_trigger_channels(self.prefix[:-1])

    def _update_deltadelay(self, value):
        siz = min(value.size, self._hldeltadelay.size)
        self._hldeltadelay[:siz] = value[:siz]
        mini = self._hldeltadelay.min()
        self._hldelay += mini
        self._hldeltadelay -= mini
        self._hldelay = 0 if self._hldelay <= 0 else self._hldelay

    def _combine_status(self, values):
        status_or = _reduce(_or_, values)
        status_and = _reduce(_and_, values)
        alarm = self.Alarm.NO
        severity = self.Severity.NO
        if status_or != status_and:
            alarm = self.Alarm.COMM
            severity = self.Severity.INVALID
        return {'value': status_or, 'alarm': alarm, 'severity': severity}

    def _combine_deltadelay(self, values):
        if any(map(lambda x: x is None, values)):
            return {
                'value': None,
                'alarm': self.Alarm.COMM,
                'severity': self.Severity.INVALID}
        alarm = self.Alarm.NO
        severity = self.Severity.NO
        values = _np.array(values) - min(values)
        return {'value': values, 'alarm': alarm, 'severity': severity}

    def _combine_delay(self, values):
        if any(map(lambda x: x is None, values)):
            return {
                'value': None,
                'alarm': self.Alarm.COMM,
                'severity': self.Severity.INVALID}
        alarm = self.Alarm.NO
        severity = self.Severity.NO
        values = min(values)
        return {'value': values, 'alarm': alarm, 'severity': severity}

    def _define_funs_combine_values(self):
        """Define a dictionary of functions to combine low level values."""
        return {
            'Status': self._combine_status,
            'DeltaDelay': self._combine_deltadelay,
            'DeltaDelayRaw': self._combine_deltadelay,
            'Delay': self._combine_delay,
            'DelayRaw': self._combine_delay,
            'TotalDelay': self._combine_delay,
            'TotalDelayRaw': self._combine_delay}
