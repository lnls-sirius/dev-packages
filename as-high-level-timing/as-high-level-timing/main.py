import pvs as _pvs
import time as _time
import re as _re
import epics as _epics
from siriuspy.timesys import time_data as _timedata
from siriuspy.namesys import SiriusPVName as _PVName
from data.triggers import get_triggers as _get_triggers

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

EVENT_REGEXP  = _re.compile(  '('  +  '|'.join( _timedata.EVENT_MAPPING.keys() )  +  ')'  +  '([\w-]+)'  )
TRIGCH_REGEXP = _re.compile('([a-z]+)([0-9]*)',_re.IGNORECASE)

def check_triggers_consistency():
    triggers = _get_triggers()
    time_rel = _timedata.get_connections_from_evg()
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


def get_low_level_trigger_object(device,callback):

    return obj

_HIGH_LEVEL_TRIGGER_CLASSES = {
    'simple':   TriggerSimple,
    'rmpbo':    TriggerRmpBO,
    'cavity':   TriggerCavity,
    'pssi':     TriggerPSSI,
    'generic':  TriggerGeneric,
    }

def get_high_level_trigger_object(trigger,callback,devices,event,trigger_type):
    ty = trigger_type
    cls_ = _HIGH_LEVEL_TRIGGER_CLASSES.get(ty)
    if not cls_: raise Exception('High Level Trigger Class not defined for trigger type '+ty+'.')
    return cls_(trigger,callback,devices,event)

class TriggerSimple:
    _STATES = ('Dsbl','Enbl')

    @classmethod
    def get_database(cls,prefix=''):
        db = dict()
        db[prefix + 'Delay-SP']  = {'type' : 'float', 'value': 0.0, 'unit':'us', 'prec': 4}
        db[prefix + 'Delay-RB']  = {'type' : 'float', 'value': 0.0, 'unit':'us', 'prec': 4}
        db[prefix + 'State-Sel'] = {'type' : 'enum', 'enums':cls._STATES, 'value':0}
        db[prefix + 'State-Sts'] = {'type' : 'enum', 'enums':cls._STATES, 'value':0}
        return db

    def __init__(self,trigger,callback,devices,event):
        self._devices = dict()
        self._props = {
            'event'      : event,
            'delay'      : 0.0,
            'delay_type' : 'Incr',
            'pulses'     : 1,
            'width'      : 150,
            'state'      : 'Dsbl',
            'polarity'   : 'Normal',
            }
        for dev in devices:
            low_lev_obj = get_low_level_trigger_object(dev,self._callback)
            self._devices[dev] = low_lev_obj
            for prop, val in self._props.items():
                low_lev_obj.set(prop,val)

    def set_propty(pv,value):
        if 'Delay-SP' in pv and value != self._props['delay']:
            self._props['delay'] = value
            for dev, obj in self._devices.keys():
                obj.set('delay',self._props['delay'])
        elif 'State-SP' in pv and value != self._STATES.index(self._props['state']):
            self._props['state'] = self.STATES[value]
            for dev, obj in self._devices.keys():
                obj.set('state',self._props['state'])

class TriggerRmpBO:
    _STATES = ('Dsbl','Enbl')

    @classmethod
    def get_database(cls,prefix=''):
        db = dict()
        db[prefix + 'State-Sel'] = {'type' : 'enum', 'enums':cls._STATES, 'value':0}
        db[prefix + 'State-Sts'] = {'type' : 'enum', 'enums':cls._STATES, 'value':0}
        return db

    def __init__(self,trigger,callback,devices,event):
        self._devices = dict()
        self._props = {
            'event'      : event,
            'delay'      : 0.0,
            'delay_type' : 'Incr',
            'pulses'     : 2000,
            'width'      : 490e3/2000,
            'state'      : 'Dsbl',
            'polarity'   : 'Normal',
            }
        for dev in devices:
            low_lev_obj = get_low_level_trigger_object(dev,self._callback)
            self._devices[dev] = low_lev_obj
            for prop, val in self._props.items():
                low_lev_obj.set(prop,val)

    def set_propty(pv,value):
        if 'State-SP' in pv and value != self._STATES.index(self._props['state']):
            self._props['state'] = self.STATES[value]
            for dev, obj in self._devices.keys():
                obj.set('state',self._props['state'])


class TriggerCavity:
    _STATES = ('Dsbl','Enbl')

    @classmethod
    def get_database(cls,prefix=''):
        db = dict()
        db[prefix + 'State-Sel'] = {'type' : 'enum', 'enums':cls._STATES, 'value':0}
        db[prefix + 'State-Sts'] = {'type' : 'enum', 'enums':cls._STATES, 'value':0}
        return db

    def __init__(self,trigger,callback,devices,event):
        self._devices = dict()
        self._props = {
            'event'      : event,
            'delay'      : 0.0,
            'delay_type' : 'Incr',
            'pulses'     : 2000,
            'width'      : 490e3/2000,
            'state'      : 'Dsbl',
            'polarity'   : 'Normal',
            }
        for dev in devices:
            low_lev_obj = get_low_level_trigger_object(dev,self._callback)
            self._devices[dev] = low_lev_obj
            for prop, val in self._props.items():
                low_lev_obj.set(prop,val)

    def set_propty(pv,value):
        if 'State-SP' in pv and value != self._STATES.index(self._props['state']):
            self._props['state'] = self.STATES[value]
            for dev, obj in self._devices.keys():
                obj.set('state',self._props['state'])


class TriggerPSSI:
    _STATES = ('Dsbl','Enbl')

    @classmethod
    def get_database(cls,prefix=''):
        db = dict()
        db[prefix + 'Duration-SP']  = {'type' : 'float', 'value': 0.0, 'unit':'us', 'prec': 4}
        db[prefix + 'Duration-RB']  = {'type' : 'float', 'value': 0.0, 'unit':'us', 'prec': 4}
        db[prefix + 'State-Sel'] = {'type' : 'enum', 'enums':cls._STATES, 'value':0}
        db[prefix + 'State-Sts'] = {'type' : 'enum', 'enums':cls._STATES, 'value':0}
        return db

    def __init__(self,trigger,callback,devices,event):
        self._devices = dict()
        self._props = {
            'event'      : event,
            'delay'      : 0.0,
            'delay_type' : 'Incr',
            'pulses'     : 2000,
            'width'      : 490e3/2000,
            'state'      : 'Dsbl',
            'polarity'   : 'Normal',
            }
        for dev in devices:
            low_lev_obj = get_low_level_trigger_object(dev,self._callback)
            self._devices[dev] = low_lev_obj
            for prop, val in self._props.items():
                low_lev_obj.set(prop,val)

    def set_propty(pv,value):
        if 'State-SP' in pv and value != self._STATES.index(self._props['state']):
            self._props['state'] = self.STATES[value]
            for dev, obj in self._devices.keys():
                obj.set('state',self._props['state'])


class App:

    pvs_database = _pvs.pvs_database

    def __init__(self,driver):
        self._driver = driver
        self._events = dict()
        for ev in _timedata.EVENT_MAPPING.keys():
            self._events[ev] = EventInterface(ev,self._callback)

        if not check_triggers_consistency():
            raise Exception('Triggers not consistent.')

        self._triggers = dict()
        triggers = _get_triggers()
        for trig, prop in _triggers.itmes():
            self._triggers = get_high_level_trigger_object(trig,self._callback,**prop)

    def _callback(self,pv_name,pv_value,**kwargs):
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


class TriggerInterface:
    _STATES = ('Dsbl','Enbl')
    _POLARITIES = ('Normal','Inverse')
    _FUNCTION_TYPES = ('Trigger', 'Clock')
    _EVR_NUM_OPT   = 12
    _EVR_NUM_LC    = 8
    _EVE_NUM_ELP   = 8
    _AFC_NUM_OPT   = 10
    _AFC_NUM_ELP   = 8
    _EVENTS = tuple(  sorted( _timedata.EVENT_MAPPING.keys() )  )
    _CLOCKS = tuple([_timedata.CLOCK_LABEL_TEMPLATE.format(i) for i in range(8)])

    @classmethod
    def get_database(cls,prefix=''):
        db = dict()
        db[prefix + 'TIDevice-Cte']  = {'type' : 'string', 'value':'AS-01:TI-AFC:LC1'}
        db[prefix + 'State-Sel']     = {'type' : 'enum', 'enums':cls._STATES, 'value':0}
        db[prefix + 'State-Sts']     = {'type' : 'enum', 'enums':cls._STATES, 'value':0}
        db[prefix + 'WorkAs-Sel']    = {'type' : 'enum', 'enums':cls._FUNCTION_TYPES,'value':0}
        db[prefix + 'WorkAs-Sts']    = {'type' : 'enum', 'enums':cls._FUNCTION_TYPES,'value':0}
        db[prefix + 'Event-Sel']     = {'type' : 'enum', 'enums':cls._EVENTS, 'value':0}
        db[prefix + 'Event-Sts']     = {'type' : 'enum', 'enums':cls._EVENTS, 'value':0}
        db[prefix + 'Clock-Sel']     = {'type' : 'enum', 'enums':cls._CLOCKS, 'value':0}
        db[prefix + 'Clock-Sts']     = {'type' : 'enum', 'enums':cls._CLOCKS, 'value':0}
        db[prefix + 'Delay-SP']      = {'type' : 'float', 'unit':'us', 'value': 0.0, 'prec': 0}
        db[prefix + 'Delay-RB']      = {'type' : 'float', 'unit':'us', 'value': 0.0, 'prec': 0}
        db[prefix + 'Pulses-SP']     = {'type' : 'int',  'value': 1}
        db[prefix + 'Pulses-RB']     = {'type' : 'int',  'value': 1}
        db[prefix + 'Duration-SP']   = {'type' : 'float', 'value': 0.0, 'unit':'ms', 'prec': 3}
        db[prefix + 'Duration-RB']   = {'type' : 'float', 'value': 0.0, 'unit':'ms', 'prec': 3}
        db[prefix + 'Polrty-Sel']    = {'type' : 'enum', 'enums':cls._POLARITIES, 'value':0}
        db[prefix + 'Polrty-Sts']    = {'type' : 'enum', 'enums':cls._POLARITIES, 'value':0}

    _LOW_LEVEL_PVS = {
        'commom': set(
            'State-Sel', 'State-Sts', 'Pulses-SP', 'Pulses-RB', 'Width-SP', 'Width-RB',
            'Delay-SP', 'Delay-RB', 'Polrty-Sel', 'Polrty-Sts', 'Event-Sel', 'Event-Sts',),
        ('evr','lc'): set(
            'FineDelay-SP', 'FineDelay-RB', 'Delay-SP', 'Delay-RB','OptCh-Sel', 'OptCh-Sts'),
        ('evr','opt'): set(),
        ('eve','opt'): set(),
        ('eve','lc'): set(
            'FineDelay-SP', 'FineDelay-RB', 'Delay-SP', 'Delay-RB','OptCh-Sel', 'OptCh-Sts' ),
        ('afc','opt'): set(
            'OptCh-Sel', 'OptCh-Sts' ),
        ('afc','elp'): set(
            'OptCh-Sel', 'OptCh-Sts' ),
        }

    def __init__(self, prefix, device, output, callback=None):
        self._callback = callback
        self.prefix = prefix

        # gets the device and output types
        parts = _PVName(device)
        if parts.dev_type not in {'AFC','EVR','EVE'}:
            raise Exception('Wrong device type for TriggerInterface initialization.')
        match = TRIGCH_REGEXP.find_all(output)
        if not match:
            raise Exception('Wrong output definition for TriggerInterface initialization.')
        # sets the device and output types
        self.device_type = parts.dev_type
        self.out_type, self.out_num = match[0]

        gets the prefix for the low_level internal trigger p
        inter_pref     = device + ':' + _timedata.OPT_LABEL_TEMPLATE.format(int(self.out_num))
        # gets the prefix for the low level output pvs
        if self.device_type == 'evr':
            if self.out_type == 'opt':
                if int(self.out_num) > self._EVR_NUM_OPT:
                    raise Exception('Wrong output number for TriggerInterface initialization.')
                pref = inter_pref
            elif self.out_type == 'lc':
                num = int(self.out_num) - self._EVR_NUM_OPT
                if not (0 < num <= self._EVR_NUM_LC):
                    raise Exception('Wrong output number for TriggerInterface initialization.')
                pref = device + ':' + _timedata.OUT_LABEL_TEMPLATE.format(num)
            else:
                raise Exception('Wrong output type for TriggerInterface initialization.')
        elif self.device_type == 'eve':
            if self.out_type != 'opt':
                raise Exception('Wrong output type for TriggerInterface initialization.')
            if int(self.out_num) > self._EVE_NUM_ELP:
                raise Exception('Wrong output number for TriggerInterface initialization.')
            pref = device + ':' + _timedata.OUT_LABEL_TEMPLATE.format(int(self.out_num))
        else:
            if self.out_type == 'opt':
                if int(self.out_num) > self._AFC_NUM_OPT:
                    raise Exception('Wrong output number for TriggerInterface initialization.')
                pref = device + ':' + _timedata.OPT_LABEL_TEMPLATE.format(int(self.out_num))
            elif self.out_type == 'elp':
                num = int(self.out_num) - self._AFC_NUM_OPT
                if not (0 < num <= self._AFC_NUM_ELP):
                    raise Exception('Wrong output number for TriggerInterface initialization.')
                pref = device + ':' + _timedata.OUT_LABEL_TEMPLATE.format(num)
            else:
                raise Exception('Wrong output type for TriggerInterface initialization.')
        #sets the prefix for the low level pvs as an attribute
        self.device_prefix = pref

        # build the dictionary with the low level pvs
        self.low_level_pvs = dict()
        options = dict(callback=self._low_level_callback, connection_timeout=_TIMEOUT)
        for pv in self._LOW_LEVEL_PVS['common'] | self._LOW_LEVEL_PVS[(self.device_type,self.out_type)]:
            self._low_level_pvs[pv] = _epics.PV(self.device_prefix + pv)

        self.low_level_label = EVG + ':' + _timedata.EVENT_LABEL_TEMPLATE.format(self.code)
        for pv in self.get_database().keys():
            self.low_level_pvs[pv] = _epics.PV(self.low_level_label+pv,**options )

    def get(self,pv):
        return self.low_level_pvs[pv].value

    def set(self,pv, value):
        self.low_level_pvs[pv].value = value

    def _low_level_callback(self,pv_name,pv_value,**kwargs):
        pv_name = self.low_level_label + pv_name
        if self._callback: self._callback(pv_name,pv_value,**kwargs)
