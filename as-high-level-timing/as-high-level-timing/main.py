import pvs as _pvs
import time as _time
import epics as _epics
from siriuspy.timesys import time_data as _timedata
from siriuspy.namesys import SiriusPVName as _PVName
from data.triggers import get_triggers as _get_triggers
from .hl_classes import get_high_level_trigger_object

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

__version__ = _pvs.__version__
_TIMEOUT = 0.05

class App:
    pvs_database = _pvs.pvs_database

    def __init__(self,driver):
        self._driver = driver
        self._events = dict()
        for ev in _timedata.EVENT_MAPPING.keys():
            self._events[ev] = EventInterface(ev,self._update_driver)

        if not check_triggers_consistency():
            raise Exception('Triggers not consistent.')

        self._triggers = dict()
        triggers = _get_triggers()
        for trig, prop in triggers.items():
            self._triggers[trig] = get_high_level_trigger_object(trig,self._update_driver,**prop)

    def _update_driver(self,pv_name,pv_value,**kwargs):
        self.driver.setParam(pv_name,pv_value)
        self.driver.updatePVs()

    @property
    def driver(self):
        return self._driver

    def process(self,interval):
        _time.sleep(interval)

    def read(self,reason):
        return None # Driver will read from database

    def write(self,reason,value):
        parts = _PVName(reason)
        if parts.dev_name == EVG:
            ev,pv = EVENT_REGEXP.findall(parts.propty)
            self._events[ev].set_propty(pv, value)
            return True # when returning True super().write of PCASDrive is invoked


def check_triggers_consistency():
    triggers = _get_triggers()
    from_evg = _timedata.get_connections_from_evg()
    twds_evg = _timedata.get_connections_twrds_evg()
    for trig, val in triggers.items():
        devs = set(val['devices'])
        for dev in devs:
            _tmp = twds_evg.get(dev)
            if not _tmp:
                print('Device '+dev+' defined in the high level trigger '+trig+' not specified in timing connections data.')
                return False
            conn,up_dev = _tmp.popitem()
            diff_devs = set(from_evg[up_dev[0]][up_dev[1]]) - devs
            if diff_devs:
                print('Devices: '+diff_devs+' are connected to the same output of '+up_dev+' as '+dev+' but are not related to the sam trigger ('+trig+').')
                return False
    return True


class EventInterface:
    _MODES = ('Disabled','Continuous','Injection','Single')
    _DELAY_TYPES = ('Fixed','Incr')

    @classmethod
    def get_database(cls,prefix=''):
        db = dict()
        db[prefix + 'Delay-SP']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us', 'prec': 3}
        db[prefix + 'Delay-RB']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us','prec': 3}
        db[prefix + 'Mode-Sel']      = {'type' : 'enum', 'enums':cls._MODES, 'value':1}
        db[prefix + 'Mode-Sts']      = {'type' : 'enum', 'enums':cls._MODES, 'value':1}
        db[prefix + 'DelayType-Sel'] = {'type' : 'enum', 'enums':cls._DELAY_TYPES, 'value':1}
        db[prefix + 'DelayType-Sts'] = {'type' : 'enum', 'enums':cls._DELAY_TYPES, 'value':1}

    def __init__(self,name,callback=None):
        self.callback = callback
        self.low_level_code  = _timedata.EVENT_MAPPING[name]
        self.low_level_label = EVG + ':' + _timedata.EVENT_LABEL_TEMPLATE.format(self.code)
        self.low_level_pvs = dict()
        options = dict(callback=self._call_callback, connection_timeout=_TIMEOUT)
        for pv in self.get_database().keys():
            self.low_level_pvs[pv] = _epics.PV(self.low_level_label+pv,**options )

    def get_propty(self,pv):
        return self.low_level_pvs[pv].value

    def set_propty(self,pv, value):
        self.low_level_pvs[pv].value = value

    def _call_callback(self,pv_name,pv_value,**kwargs):
        pv_name = self.low_level_label + pv_name
        if self._callback: self._callback(pv_name,pv_value,**kwargs)
