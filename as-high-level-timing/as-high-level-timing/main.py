import pvs as _pvs
import time as _time
import re as _re
import epics as _epics
from siriuspy.timesys import time_data as _timedata
from siriuspy.namesys import SiriusPVName as _PVName

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


_ALL_DEVICES = _timedata.get_all_devices()
_pv_fun = lambda x,y: _PVName(x).dev_type.lower() == y.lower()
_get_devs = lambda x: { dev for dev in _ALL_DEVICES if _pv_fun(dev,x) }

EVG  = _get_devs('evg').pop()
EVRs = _get_devs('evr')
EVEs = _get_devs('eve')
AFCs = _get_devs('afc')

EVENT_REGEXP = _re.compile(  '('  +  '|'.join( _timedata.EVENT_MAPPING.keys() )  +  ')'  +  '([\w-]+)'  )


class App:

    pvs_database = _pvs.pvs_database

    def __init__(self,driver):
        self._driver = driver
        self._events = dict()
        for ev in _timedata.EVENT_MAPPING.keys():
            self._events[ev] = EventInterface(ev,self._callback)

    def _callback(self,pv_name,pv_value,**kwargs):
        self.driver.setParam(pv_name,pv_value)
        self.driver.updatePVs()

    @property
    def driver(self):
        return self._driver

    def process(self,interval):
        _time.sleep(interval)

    def read(self,reason):
        parts = _PVName(reason)
        if parts.dev_name == EVG:
            ev,pv = EVENT_REGEXP.findall(parts.propty)
            return self._events[ev].get(pv)

    def write(self,reason,value):
        parts = _PVName(reason)
        if parts.dev_name == EVG:
            ev,pv = EVENT_REGEXP.findall(parts.propty)
            self._events[ev].set(pv, value)
            return True # when returning True super().write of PCASDrive is invoked


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
        self._callback = callback
        self.low_level_code  = _timedata.EVENT_MAPPING[name]
        self.low_level_label = EVG + ':' + _timedata.EVENT_LABEL_TEMPLATE.format(self.code)
        self.low_level_pvs = dict()
        options = dict(callback=self._low_level_callback, connection_timeout=_TIMEOUT)
        for pv in self.get_database().keys():
            self.low_level_pvs[pv] = _epics.PV(self.low_level_label+pv,**options )

    def get(self,pv):
        return self.low_level_pvs[pv].value

    def set(self,pv, value):
        self.low_level_pvs[pv].value = value

    def _low_level_callback(self,pv_name,pv_value,**kwargs):
        pv_name = self.low_level_label + pv_name
        if self._callback: self._callback(pv_name,pv_value,**kwargs)
