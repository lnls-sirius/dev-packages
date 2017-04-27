from siriuspy.timesys import time_data as _tm
from siriuspy.namesys import SiriusPVName as _PVName
from data.triggers import get_triggers as _get_triggers
from .ll_classes import get_low_level_trigger_object

_ALL_DEVICES = _tm.get_all_devices()
_pv_fun = lambda x,y: _PVName(x).dev_type.lower() == y.lower()
_get_devs = lambda x: { dev for dev in _ALL_DEVICES if _pv_fun(dev,x) }

EVG  = _get_devs('evg').pop()
EVRs = _get_devs('evr')
EVEs = _get_devs('eve')
AFCs = _get_devs('afc')


def _get_initial_hl2ll():
    map_ = {
        'work_as'    : 0,
        'clock'      : 0,
        'event'      : 0,
        'delay'      : 0.0,
        'pulses'     : 1,
        'width'      : 150,
        'state'      : 0,
        'polarity'   : 0,
        }
    return map_


def _get_ll_trig_names(devs):
    from_evg = _tm.get_connections_from_evg()
    twds_evg = _tm.get_connections_twrds_evg()
    channels = tuple()
    for dev in devs:
        dev,conn = twds_evg[dev].pop()
        while dev not in EVRs | EVEs |AFCs:
            dev, conn = twds_evg[dev][conn]
        channels += (dev+':'+conn,)
    return sorted(channels)


_HIGH_LEVEL_TRIGGER_CLASSES = {
    'simple':   _HL_TrigSimple,
    'rmpbo':    _HL_TrigRmpBO,
    'cavity':   _HL_TrigCavity,
    'pssi':     _HL_TrigPSSI,
    'generic':  _HL_TrigGeneric,
    }
def get_high_level_trigger_object(trigger,callback,devices,event,trigger_type):
    ty = trigger_type
    cls_ = _HIGH_LEVEL_TRIGGER_CLASSES.get(ty)
    if not cls_:
        raise Exception('High Level Trigger Class not defined for trigger type '+ty+'.')
    return cls_(trigger,callback,devices,event)


class _HL_TrigBase:
    _FUNCTION_TYPES = ('Trigger', 'Clock')

    _HL_PROPS = {'work_as','clock','event','delay','pulses','width','state','polarity'}

    _HLPROP_2_PVSP = {
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
    _PVSP_2_HLPROP = {  val:key for key,val in _HL_TrigBase._HLPROP_2_PVSP.items()  }
    _HLPROP_2_PVRB = {
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

    def get_database(self):
        db = dict()
        pre = self.prefix
        len_rb = len(self._ll_trigs)
        db[pre + 'State-Sel']   = {'type':'enum', 'value':0, 'enums':_tm.STATES}
        db[pre + 'State-Sts']   = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'WorkAs-Sel']  = {'type':'enum', 'value':0, 'enums':self._FUNCTION_TYPES}
        db[pre + 'WorkAs-Sts']  = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'Event-Sel']   = {'type':'enum', 'value':0, 'enums':self._EVENTS}
        db[pre + 'Event-Sts']   = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'Clock-Sel']   = {'type':'enum', 'value':0, 'enums':_tm.CLOCKS}
        db[pre + 'Clock-Sts']   = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'Delay-SP']    = {'type':'float','value':0.0, 'unit':'us', 'prec': 4}
        db[pre + 'Delay-RB']    = {'type':'float','value':0.0, 'unit':'us', 'prec': 4, 'count':len_rb}
        db[pre + 'Pulses-SP']   = {'type':'int',  'value':1}
        db[pre + 'Pulses-RB']   = {'type':'int',  'value':1, 'count':len_rb}
        db[pre + 'Duration-SP'] = {'type':'float','value':0.0, 'unit':'ms', 'prec': 4}
        db[pre + 'Duration-RB'] = {'type':'float','value':0.0, 'unit':'ms', 'prec': 4, 'count':len_rb}
        db[pre + 'Polrty-Sel']  = {'type':'enum', 'value':0, 'enums':_tm.POLARITIES}
        db[pre + 'Polrty-Sts']  = {'type':'int',  'value':0, 'count':len_rb}

        db2 = dict()
        for prop in self._HL_PROPS:
            db2[pre + self._HLPROP_2_PVSP[prop]] = db[self._HLPROP_2_PVSP[prop]]
            db2[pre + self._HLPROP_2_PVRB[prop] ] = db[self._HLPROP_2_PVRB[prop] ]
        return db2

    def __init__(self,trigger,callback,devices,events):
        self._RB_FUNS  = self._get_read_funs_map()
        self._SP_FUNS = self._get_sp_funs_map()
        self._EVENTS = events
        self.callback = callback
        self.prefix = trigger + ':'
        self._ll_trig_names = _get_ll_trig_names(devices)
        len_rb = len(self._ll_trig_names)
        self._hl2ll = self._get_initial_hl2ll() # high level to low level interface
        self._values_rb = {  key:len_rb*[val] for key,val in self._hl2ll.items()  }
        self._ll_trigs = dict()
        for dev in self._ll_trig_names:
            low_lev_obj = get_low_level_trigger_object(
                                device = dev,
                                callback = self._pvs_value_rb,
                                initial_hl2ll=_copy.deepcopy(self._hl2ll)
                                )
            self._ll_trig_names.append(dev)
            self._ll_trigs[dev] = low_lev_obj
            for prop, val in self._hl2ll.items():
                low_lev_obj.set_propty(prop,val)

    def _get_initial_hl2ll(self): return _get_initial_hl2ll()

    def _get_sp_funs_map(self):
        map_ = {
            'work_as'    : lambda x: self._FUNCTION_TYPES[x],
            'clock'      : lambda x: _tm.CLOCKS[x],
            'event'      : lambda x: _tm.EVENT_MAPPING[self._EVENTS[x]],
            'delay'      : lambda x: x,
            'pulses'     : lambda x: x,
            'width'      : lambda x: x / self._hl2ll['pulses']*1e3,
            'state'      : lambda x: _tm.STATES[x],
            'polarity'   : lambda x: _tm.POLARITIES[x],
            }
        return map_

    def _get_read_funs_map(self):
        map_ = {
            'work_as'    : lambda x: self._FUNCTION_TYPES.index(x),
            'clock'      : lambda x: _tm.CLOCKS.index(x),
            'event'      : lambda x: self._EVENTS.index(_tm.EVENT_MAPPING_INV[x]),
            'delay'      : lambda x: x,
            'pulses'     : lambda x: x,
            'width'      : lambda x: x * self._values_rb[y]['pulses'] * 1e-3,
            'state'      : lambda x: _tm.STATES.index(x),
            'polarity'   : lambda x: _tm.POLARITIES.index(x),
            }
        return map_

    def _pvs_values_rb(self, channel, prop, value):
        if prop not in self._HL_PROPS: return
        ind = self._ll_trig_names.index(channel)
        self._values_rb[prop][ind] = self._RB_FUNS[prop](value,ind)
        self.callback( self.prefix + self._HLPROP_2_PVRB[prop], self._values_rb[prop]  )

    def set_propty(pv,value):
        prop = self._PVSP_2_HLPROP.get(pv)
        if prop not in self._HL_PROPS: return
        if value == self._hl2ll[prop]: return
        self._hl2ll[prop] = self._SP_FUNS[prop](value)
        for dev, obj in self._ll_trigs.keys():
            obj.set_propty(prop,self._hl2ll[prop])


class _HL_TrigSimple(HL_TrigBase):
    _HL_PROPS = {'event','delay','state'}


class _HL_TrigRmpBO(HL_TrigBase):
    _HL_PROPS = {'event','state'}

    def _get_initial_hl2ll(self):
        map_ = super()._get_initial_hl2ll()
        map_['width'] = 490e3/2000
        map_['pulses'] = 2000
        return map_


class _HL_TrigCavity(HL_TrigRmpBO):
    _HL_PROPS = {'event','state','pulses'}


class _HL_TrigPSSI(HL_TrigBase):
    _HL_PROPS = {'event','state','width','work_as','clock'}

    def _get_initial_hl2ll(self):
        map_ = super()._get_initial_hl2ll()
        map_['width'] = 2/2000
        map_['pulses'] = 2000
        return map_

    def _get_sp_funs_map(self):
        map_ = super()._get_sp_funs_map()
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
            for dev, obj in self._ll_trigs.keys():
                obj.set_propty(prop,self._hl2ll[prop])

        return _tm.EVENT_MAPPING[self._EVENTS[ev]]


class _HL_TrigGeneric(HL_TrigBase):
    _HL_PROPS = {'event','state','pulses','width','work_as','clock'}
