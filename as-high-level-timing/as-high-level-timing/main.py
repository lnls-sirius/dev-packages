import pvs as _pvs
import time as _time
from siriuspy.timesys import time_data as _tm
from siriuspy.namesys import SiriusPVName as _PVName
from data.triggers import get_triggers as _get_triggers
from .hl_classes import get_high_level_trigger_object
from .ll_classes import EventInterface

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

def check_triggers_consistency():
    triggers = _get_triggers()
    _tm.add_bbb_info()
    _tm.add_crates_info()
    from_evg = _tm.get_connections_from_evg()
    twds_evg = _tm.get_connections_twrds_evg()
    for trig, val in triggers.items():
        devs = set(val['devices'])
        for dev in devs:
            _tmp = twds_evg.get(dev)
            if _tmp is None:
                print('Device '+dev+' defined in the high level trigger '+trig+' not specified in timing connections data.')
                return False
            conn,up_dev = _tmp.popitem()
            diff_devs = set(from_evg[up_dev[0]][up_dev[1]]) - devs
            if diff_devs:
                print('Devices: '+diff_devs+' are connected to the same output of '+up_dev+' as '+dev+' but are not related to the sam trigger ('+trig+').')
                return False
    return True


class App:
    pvs_database = _pvs.pvs_database

    def __init__(self,driver):
        self._driver = driver
        self._events = dict()
        if not check_triggers_consistency():
            raise Exception('Triggers not consistent.')
        # Build Event's Variables:
        for ev in _tm.EVENT_MAPPING.keys():
            self._events[ev] = EventInterface(ev,self._update_driver)
        # Build triggers from data dictionary:
        self._triggers = dict()
        triggers = _get_triggers()
        for trig_prefix, prop in triggers.items():
            parts = _PVName(trig_prefix)
            trig = get_high_level_trigger_object(trig_prefix, self._update_driver, **prop)
            self._set_trigger_obj(parts,trig)


    def _set_trigger_obj(self,parts,trig):
        fp = self._triggers.get(parts.dev_name)
        if fp is None:
            self._triggers[key] = {parts.propty:trig}
        else:
            fp.update( {parts.propty:trig} )

    def get_trigger_obj(self,parts):
        fp = self._triggers.get(parts.dev_name)
        if fp is not None:
            return [ fp[sp] for sp in fp.keys() if parts.propty.startswith(sp) ][0]

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
            return self._events[ev].set_propty(pv, value)

        trig = self.get_triggers_obj(parts)
        if trig is not None:
            return trig.set_propty(reason,value)

        return False
