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

RFFREQ = 299792458/518.396*864


_ALL_DEVICES = _timedata.get_all_devices()
_pv_fun = lambda x,y: _PVName(x).dev_type.lower() == y.lower()
_get_devs = lambda x: { dev for dev in _ALL_DEVICES if _pv_fun(dev,x) }

EVG  = _get_devs('evg').pop()
EVRs = _get_devs('evr')
EVEs = _get_devs('eve')
AFCs = _get_devs('afc')

EVENT_REGEXP  = _re.compile(  '('  +  '|'.join( _timedata.EVENT_MAPPING.keys() )  +  ')'  +  '([\w-]+)'  )
TRIGCH_REGEXP = _re.compile('([a-z]+)([0-9]*)',_re.IGNORECASE)

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
        for trig, prop in _triggers.itmes():
            self._triggers = get_high_level_trigger_object(trig,self._update_driver,**prop)

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


def _get_initial_hl2ll():
    map_ = {
        'work_as'    : 0,
        'clock'      : 0,
        'event'      : 0,
        'delay'      : 0.0,
        'delay_type' : 0,
        'pulses'     : 1,
        'width'      : 150,
        'state'      : 0,
        'polarity'   : 0,
        }
    return map_


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


def get_trigger_channels(devs):
    from_evg = _timedata.get_connections_from_evg()
    twds_evg = _timedata.get_connections_twrds_evg()
    channels = tuple()
    for dev in devs:
        dev,conn = twds_evg[dev].pop()
        while dev not in EVRs | EVEs |AFCs:
            dev, conn = twds_evg[dev][conn]
        channels += (dev+':'+conn,)
    return sorted(channels)


_LOW_LEVEL_TRIGGER_CLASSES = {
    ('evr','mfo'): LL_TrigEVRMFO,
    ('evr','opt'): LL_TrigEVROPT,
    ('eve','elp'): LL_TrigEVRELP,
    ('eve','opt'): LL_TrigEVROPT,
    ('afc','elp'): LL_TrigEVRELP,
    ('afc','opt'): LL_TrigEVROPT,
    }
def get_low_level_trigger_object(device,callback,initial_hl2ll):
    dev = _PVName(device)
    conn, num = TRIGCH_REGEXP.findall(dev.propty.lower())
    key = (dev.dev_type.lower(), conn)
    cls_ = _LOW_LEVEL_TRIGGER_CLASSES.get(key)
    if not cls_:
        raise Exception('Low Level Trigger Class not defined for device type '+key[0]+' and connection type '+key[1]+'.')
    return cls_(dev.dev_name, conn, num, callback, initial_hl2ll)


_HIGH_LEVEL_TRIGGER_CLASSES = {
    'simple':   HL_TrigSimple,
    'rmpbo':    HL_TrigRmpBO,
    'cavity':   HL_TrigCavity,
    'pssi':     HL_TrigPSSI,
    'generic':  HL_TrigGeneric,
    }
def get_high_level_trigger_object(trigger,callback,devices,event,trigger_type):
    ty = trigger_type
    cls_ = _HIGH_LEVEL_TRIGGER_CLASSES.get(ty)
    if not cls_:
        raise Exception('High Level Trigger Class not defined for trigger type '+ty+'.')
    return cls_(trigger,callback,devices,event)


class HL_TrigBase:
    _STATES      = ('Dsbl','Enbl')
    _POLARITIES  = ('Normal','Inverse')
    _DELAY_TYPES = ('Incr','Fixed')
    _FUNCTION_TYPES = ('Trigger', 'Clock')
    _CLOCKS = tuple([_timedata.CLOCK_LABEL_TEMPLATE.format(i) for i in range(8)])

    _WRITABLE_PROPS = {'work_as','clock','event','delay','delay_type','pulses','width','state','polarity'}

    _WRITE_MAP = {
        'work_as'    :'WorkAs-Sel',
        'clock'      :'Clock-Sel',
        'event'      :'Event-Sel',
        'delay'      :'Delay-SP',
        'delay_type' :'DelayType-Sel',
        'pulses'     :'Pulses-SP',
        'width'      :'Duration-SP',
        'state'      :'State-Sel',
        'polarity'   :'Polrty-Sel',
        }
    _WRITE_MAP_INV = {  val:key for key,val in HL_TrigBase._WRITE_MAP.items()  }
    _READ_MAP = {
        'work_as'    :'WorkAs-Sts',
        'clock'      :'Clock-Sts',
        'event'      :'Event-Sts',
        'delay'      :'Delay-RB',
        'delay_type' :'DelayType-Sts',
        'pulses'     :'Pulses-RB',
        'width'      :'Duration-RB',
        'state'      :'State-Sts',
        'polarity'   :'Polrty-Sts',
        }

    @classmethod
    def _get_not_my_props(cls):
        return cls._WRITE_MAP.keys() - cls._WRITABLE_PROPS

    def __init__(self,trigger,callback,devices,events):
        self._READ_FUNS  = self._get_read_funs_map()
        self._WRITE_FUNS = self._get_write_funs_map()
        self._EVENTS = events
        self.callback = callback
        self.prefix = trigger + ':'
        self._channel_names = get_trigger_channels(devices)
        len_rb = len(self._channel_names)
        self._hl2ll = self._get_initial_hl2ll() # high level to low level interface
        self._values_rb = {  key:len_rb*[val] for key,val in self._hl2ll.items()  }
        self._channels = dict()
        for dev in self._channel_names:
            low_lev_obj = get_low_level_trigger_object(
                                device = dev,
                                callback = self._pvs_value_rb,
                                initial_hl2ll=_copy.deepcopy(self._hl2ll)
                                )
            self._channel_names.append(dev)
            self._channels[dev] = low_lev_obj
            for prop, val in self._hl2ll.items():
                low_lev_obj.set_propty(prop,val)

    def _get_initial_hl2ll(self): return _get_initial_hl2ll()

    def _get_write_funs_map(self):
        map_ = {
            'work_as'    : lambda x,y: self._FUNCTION_TYPES[x],
            'clock'      : lambda x,y: self._CLOCKS[x],
            'event'      : lambda x,y: _timedata.EVENT_MAPPING[self._EVENTS[x]],
            'delay'      : lambda x,y: x,
            'delay_type' : lambda x,y: self._DELAY_TYPES[x],
            'pulses'     : lambda x,y: x,
            'width'      : lambda x,y: x / self._hl2ll['pulses']*1e3,
            'state'      : lambda x,y: self._STATES[x],
            'polarity'   : lambda x,y: self._POLARITIES[x],
            }
        return map_

    def _get_read_funs_map(self):
        map_ = {
            'work_as'    : lambda x: self._FUNCTION_TYPES.index(x),
            'clock'      : lambda x: self._CLOCKS.index(x),
            'event'      : lambda x: self._EVENTS.index(_timedata.EVENT_MAPPING_INV[x]),
            'delay'      : lambda x: x,
            'delay_type' : lambda x: self._DELAY_TYPES.index(x),
            'pulses'     : lambda x: x,
            'width'      : lambda x: x * self._values_rb[y]['pulses'] * 1e-3,
            'state'      : lambda x: self._STATES.index(x),
            'polarity'   : lambda x: self._POLARITIES.index(x),
            }
        return map_

    def get_database(self):
        db = dict()
        pre = self.prefix
        len_rb = len(self._channels)
        db[pre + 'State-Sel']   = {'type':'enum', 'value':0, 'enums':self._STATES}
        db[pre + 'State-Sts']   = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'WorkAs-Sel']  = {'type':'enum', 'value':0, 'enums':self._FUNCTION_TYPES}
        db[pre + 'WorkAs-Sts']  = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'Event-Sel']   = {'type':'enum', 'value':0, 'enums':self._EVENTS}
        db[pre + 'Event-Sts']   = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'Clock-Sel']   = {'type':'enum', 'value':0, 'enums':self._CLOCKS}
        db[pre + 'Clock-Sts']   = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'Delay-SP']    = {'type':'float','value':0.0, 'unit':'us', 'prec': 4}
        db[pre + 'Delay-RB']    = {'type':'float','value':0.0, 'unit':'us', 'prec': 4, 'count':len_rb}
        db[pre + 'Pulses-SP']   = {'type':'int',  'value':1}
        db[pre + 'Pulses-RB']   = {'type':'int',  'value':1, 'count':len_rb}
        db[pre + 'Duration-SP'] = {'type':'float','value':0.0, 'unit':'ms', 'prec': 4}
        db[pre + 'Duration-RB'] = {'type':'float','value':0.0, 'unit':'ms', 'prec': 4, 'count':len_rb}
        db[pre + 'Polrty-Sel']  = {'type':'enum', 'value':0, 'enums':self._POLARITIES}
        db[pre + 'Polrty-Sts']  = {'type':'int',  'value':0, 'count':len_rb}

        db2 = dict()
        for prop in self._WRITABLE_PROPS:
            db2[pre + self._WRITE_MAP[prop]] = db[self._WRITE_MAP[prop]]
            db2[pre + self._READ_MAP[prop] ] = db[self._READ_MAP[prop] ]
        return db2

    def _pvs_values_rb(self, channel, prop, value):
        if prop not in self._WRITABLE_PROPS: return
        ind = self._channel_names.index(channel)
        self._values_rb[prop][ind] = self._READ_FUNS[prop](value,ind)
        self.callback( self.prefix + self._READ_MAP[prop], self._values_rb[prop]  )

    def set_propty(pv,value):
        prop = self._WRITE_MAP_INV[pv]
        if prop not in self._WRITABLE_PROPS: return
        if value == self._hl2ll[prop]: return
        self._hl2ll[prop] = self._WRITE_FUNS[prop](value)
        for dev, obj in self._channels.keys():
            obj.set_propty(prop,self._hl2ll[prop])


class HL_TrigSimple(HL_TrigBase):
    _WRITABLE_PROPS = {'event','delay','state'}


class HL_TrigRmpBO(HL_TrigBase):
    _WRITABLE_PROPS = {'event','state'}

    def _get_initial_hl2ll(self):
        map_ = super()._get_initial_hl2ll()
        map_['width'] = 490e3/2000
        map_['pulses'] = 2000
        return map_


class HL_TrigCavity(HL_TrigRmpBO):
    _WRITABLE_PROPS = {'event','state','pulses'}


class HL_TrigPSSI(HL_TrigBase):
    _WRITABLE_PROPS = {'event','state','width','work_as','clock'}

    def _get_initial_hl2ll(self):
        map_ = super()._get_initial_hl2ll()
        map_['width'] = 2/2000
        map_['pulses'] = 2000
        return map_

    def _get_write_funs_map(self):
        map_ = super()._get_write_funs_map()
        map_['event'] = self._set_event
        return map_

    def _set_event(self,ev):
        props = []
        if ev == 0:
            if self._hl2ll['pulses'] != 2000:
                self._hl2ll['pulses'] = 2000
                props.append('pulses')
            if self._hl2ll['work_as'] != 0:
                self._hl2ll['work_as'] = 0
                props.append('work_as')
            if self._hl2ll['width'] != 490e3/2000:
                self._hl2ll['width'] = 490e3/2000
                props.append('width')
        else:
            if self._hl2ll['pulses'] != 1:
                self._hl2ll['pulses'] = 1
                props.append('pulses')

        for prop in props:
            for dev, obj in self._channels.keys():
                obj.set_propty(prop,self._hl2ll[prop])

        return _timedata.EVENT_MAPPING[self._EVENTS[ev]]


class HL_TrigGeneric(HL_TrigBase):
    _WRITABLE_PROPS = {'event','state','pulses','width','work_as','clock'}


class LL_TrigEVRMFO:
    _NUM_OPT   = 12
    _NUM_INT   = 24
    _INTTMP    = 'IntTrig{0:02d}'
    _OUTTMP    = 'MFO{0:d}'

    def __init__(self, device, conn, num,  callback=None, initial_hl2ll = None):
        self._WRITE_FUNS = self._get_write_funs_map()
        self._WRITE_PVS_MAP = self.get_map_pvs_sp()
        self._READ_PVS_MAP  = self.get_map_pvs_rb()
        self._READ_PVS_MAP_INV = { val:key for key,val in self._READ_PVS_MAP.items() }
        self.callback = callback
        self.prefix = device + ':'
        self._OUTLB = self._OUTTMP.format(num)
        self._INTLB = self._INTTMP.format(self._get_num_int(num))
        self._hl2ll = initial_hl2ll or _get_initial_hl2ll()
        self._pvs_sp = dict()
        self._pvs_rb = dict()
        for prop, pv in self._WRITE_PVS_MAP.items():
            self._pvs_sp[prop]  = _epics.PV(self.prefix + pv,
                                            callback = self._pvs_sp_callback,
                                            timeout=_TIMEOUT)
        for prop, pv in self._READ_PVS_MAP.items():
            self._pvs_rb[prop]  = _epics.PV(self.prefix + pv,
                                            callback = self._pvs_rb_callback,
                                            timeout=_TIMEOUT)

    def _get_num_int(self,num):
        return self._NUM_OPT + num

    def _get_map_pvs_sp(self):
        map_ = {
            'internal_trigger' : self._OUTLB + 'IntChan-SP'
            'event'      : self._INTLB + 'Event-SP',
            'delay1'     : self._INTLB + 'Delay-SP',
            'delay2'     : self._OUTLB + 'Delay-SP',
            'delay3'     : self._OUTLB + 'FineDelay-SP',
            'delay_type' : self._INTLB + 'DelayType-Sel',
            'pulses'     : self._INTLB + 'Pulses-Sel',
            'width'      : self._INTLB + 'Width-Sel',
            'state'      : self._INTLB + 'State-Sel',
            'polarity'   : self._INTLB + 'Polrty-Sel',
            }
        return map_

    def _get_map_pvs_rb(self):
        map_ = {
            'internal_trigger' : self._OUTLB + 'IntChan-RB'
            'event'      : self._INTLB + 'Event-RB',
            'delay1'     : self._INTLB + 'Delay-RB',
            'delay2'     : self._OUTLB + 'Delay-RB',
            'delay3'     : self._OUTLB + 'FineDelay-RB',
            'delay_type' : self._INTLB + 'DelayType-Sts',
            'pulses'     : self._INTLB + 'Pulses-Sts',
            'width'      : self._INTLB + 'Width-Sts',
            'state'      : self._INTLB + 'State-Sts',
            'polarity'   : self._INTLB + 'Polrty-Sts',
            }
        return map_

    def _get_write_funs_map(self):
        map_ = {
            'work_as'    : lambda x: self.set_int_channel('work_as',x),
            'clock'      : lambda x: self.set_int_channel('clock',x),
            'delay'      : self.set_delay,
            'event'      : lambda x: self.set_simple('event',x),
            'delay_type' : lambda x: self.set_simple('delay_type',x),
            'pulses'     : lambda x: self.set_simple('pulses',x),
            'width'      : lambda x: self.set_simple('width',x),
            'state'      : lambda x: self.set_simple('state',x),
            'polarity'   : lambda x: self.set_simple('polarity',x),
            }
        return map_

    def _pvs_rb_callback(self,pv_name,pv_value,**kwargs):
        pv = pv_name[len(self.prefix):]
        self.callback(self._READ_PVS_MAP_INV[pv], value)


    def set_simple(self,prop,value):
        self._hl2ll[prop]   = value
        self.pvs_sp[prop].value = value

    def set_delay(self,value):
        rf_per = 1/RFFREQ * 1e6
        delay1_unit = rf_per * 4
        delay2_unit = rf_per * 4 / 20
        delay1_unit = 5e-6 # five picoseconds

        delay1  = (value // delay1_unit) * delay1_unit
        value  -= delay1
        delay2  = (value // delay2_unit) * delay2_unit
        value  -= delay2
        delay3  = (value // delay3_unit) * delay3_unit * 1e3 # in nanoseconds

        self._hl2ll['delay'] = delay1 + delay2 + delay3/1e3
        self.pvs_sp['delay1'].value = delay1
        self.pvs_sp['delay2'].value = delay2
        self.pvs_sp['delay3'].value = delay3

    def set_int_channel(self,prop,value):
        self._hl2ll[prop] = value
        if not self._hl2ll['work_as']:
            self._pvs_sp['internal_trigger'].value = self._internal_trigger
        else:
            clock_num = self._hl2ll['clock']
            self._pvs_sp['internal_trigger'].value = self._NUM_INT + clock_num

    def _pvs_values_rb(self, channel, prop, value):
        if prop not in self._WRITABLE_PROPS: return
        ind = self._channel_names.index(channel)
        self._values_rb[prop][ind] = self._READ_FUNS[prop](value,ind)
        self.callback( self.prefix + self._READ_MAP[prop], self._values_rb[prop]  )

    def set_propty(prop,value):
        self._WRITE_FUNS[prop](value)


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
