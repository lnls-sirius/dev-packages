import pvs as _pvs
import time as _time
from siriuspy.timesys.time_data import Connections, Events
from siriuspy.namesys import SiriusPVName as _PVName
from data.triggers import get_triggers as _get_triggers
from hl_classes import get_hl_trigger_object, HL_Event

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
    Connections.add_bbb_info()
    Connections.add_crates_info()
    from_evg = Connections.get_connections_from_evg()
    twds_evg = Connections.get_connections_twrds_evg()
    for trig, val in triggers.items():
        print(trig)
        chans = {  _PVName(chan) for chan in val['channels']  }
        devs  = {  chan.dev_name for chan in chans  }
        for chan in chans:
            print(chan)
            tmp = twds_evg.get(chan.dev_name)
            if tmp is None:
                print('Device '+chan.dev_name+' defined in the high level trigger '+
                      trig+' not specified in timing connections data.')
                return False
            up_dev = tmp.get(chan.propty)
            if up_dev is None:
                print('Connection channel '+chan.propty+' defined in the high level trigger '
                      +trig+' not specified in timing connections data.')
                return False
            diff_devs = set(from_evg[up_dev[0]][up_dev[1]]) - devs
            if diff_devs:
                print('Devices: '+diff_devs+' are connected to the same output of '+up_dev+' as '
                       +chan.dev_name+' but are not related to the sam trigger ('+trig+').')
                return False
    return True


class App:

    def get_database(self):
        db = dict()
        for ev in self._events.values():
            db.update(ev.get_database())
        for trig in self._triggers.values():
            db.update(trig.get_database())
        return db

    def __init__(self,driver=None):
        self._driver = driver
        if not check_triggers_consistency():
            raise Exception('Triggers not consistent.')
        # Build Event's Variables:
        self._events = dict()
        for ev,code in Events.HL2LL_MAP.items():
            event = Events.HL_PREF + ev
            self._events[event] = HL_Event(event,code,self._update_driver)
        # Build triggers from data dictionary:
        self._triggers = dict()
        triggers = _get_triggers()
        for trig_prefix, prop in triggers.items():
            trig = get_hl_trigger_object(trig_prefix, self._update_driver, **prop)
            self._triggers[trig_prefix] = trig

    def _update_driver(self,pv_name,pv_value,**kwargs):
        self._driver.setParam(pv_name,pv_value)
        self._driver.updatePVs()

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self,driver):
        self._driver = driver

    def process(self,interval):
        _time.sleep(interval)

    def read(self,reason):
        return None # Driver will read from database

    def write(self,reason,value):
        parts = _PVName(reason)
        ev = [ val for key,val in self._events.items() if parts.startswith(key) ]
        if parts.dev_name == EVG:
            ev,pv = Events.HL_RGX.findall(parts.propty)[0]
            return self._events[ev].set_propty(pv, value)

        trig = [ val for key,val in self._triggers.items() if parts.startswith(key) ]
        if len(trig)>0:
            return trig[0].set_propty(reason,value)

        return False
