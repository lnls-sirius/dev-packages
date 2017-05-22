import logging as _log
import copy as _copy
from siriuspy.timesys.time_data import Connections, IOs, Triggers, Clocks, Events
from siriuspy.namesys import SiriusPVName as _PVName
from ll_classes import get_ll_trigger_object
from ll_classes import LL_Event

def _get_initial_trig_hl2ll():


Connections.add_bbb_info()
Connections.add_crates_info()
EVRs = Connections.get_devices('EVR')
EVEs = Connections.get_devices('EVE')
AFCs = Connections.get_devices('AFC')
twds_evg = Connections.get_connections_twds_evg()


def get_hl_trigger_object(prefix,callback,channels,events,trigger_type):
    HL_TRIGGER_CLASSES = {
        'simple':   _HL_TrigSimple,
        'rmpbo':    _HL_TrigRmpBO,
        'cavity':   _HL_TrigCavity,
        'PSSI':     _HL_TrigPSSI,
        'generic':  _HL_TrigGeneric,
        }
    ty = trigger_type
    cls_ = HL_TRIGGER_CLASSES.get(ty)
    if not cls_:
        raise Exception('High Level Trigger Class not defined for trigger type '+ty+'.')
    return cls_(prefix,callback,channels,events)


class _HL_Base:

    _HL_PROPS = {}

    def get_database(self):
        db = dict() # deictionary must have key fun_set_pv for the driver to use in write method
        pre = self.prefix
        return db

    def __init__(self,prefix,callback,channels):
        _log.info(prefix+' Starting.')
        self._HLPROP_2_PVSP = self._get_HLPROP_2_PVSP()
        self._PVSP_2_HLPROP = {  val:key for key,val in self._HLPROP_2_PVSP.items()  }
        self._HLPROP_2_PVRB = self._get_HLPROP_2_PVRB()
        self._PVRB_2_HLPROP = {  val:key for key,val in self._HLPROP_2_PVRB.items()  }
        self._RB_FUNS  = self._get_RB_FUNS()
        self._SP_FUNS = self._get_SP_FUNS()
        self.callback = callback
        self.prefix = prefix
        self._hl2ll = self._get_initial_hl2ll()
        self._ll_objs_names = self._get_LL_OBJS_NAMES(channels)
        _log.debug(self.prefix+ ' LL names: '+' '.join([tr for tr in self._ll_objs_names]))
        len_rb = len(self._ll_obj_names)
        self._values_rb = {  key:len_rb*[val] for key,val in self._hl2ll.items()  }
        self._ll_objs = dict()
        self._ll_objs_conn_sts = list()

    def _get_HLPROP_2_PVSP(self):
        map_ = dict()
        return map_

    def _get_HLPROP_2_PVRB(self):
        map_ = dict()
        return map_

    def _get_SP_FUNS(self):
        map_ = {
        }
        return map_

    def _get_RB_FUNS(self):
        map_ = {
        }
        return map_

    def _get_LL_OBJS_NAMES(self,channels=None):
        return None

    def _get_LL_OBJ(self,**kwargs):
        return None # must return the low level object.

    def connect(self):
        _log.info(self.prefix+' -> connecting to LL Devices')
        for chan in self._ll_objs_names:
            _log.debug(self.prefix +' -> connecting to {0:s}'.format(chan))
            low_lev_obj = self._get_LL_OBJ(
                                channel = chan,
                                callback = self._pvs_values_rb,
                                connection_callback = self._ll_on_connection,
                                initial_hl2ll=_copy.deepcopy(self._hl2ll),
                                )
            self._ll_objs[chan] = low_lev_obj
            self._ll_objs_conn_sts.append(0)

    def check(self):
        for obj in self._ll_objs.values():
            obj.check()

    def _ll_on_connection(self,channel,status):
        ind = self._ll_obj_names.index(channel)
        _log.debug(self.prefix+' channel = {0:s}; status = {1:d}; ind = {2:d}; len(_ll_objs) = {3:d}'.format(channel,int(status),ind,len(self._ll_trigs_conn_sts)))
        if len(self._ll_objs_conn_sts) > ind:
            self._ll_objs_conn_sts[ind] = int(status)
        else:
            _log.error(self.prefix + 'ind > _ll_objs_conn_sts.')
        status = all(self._ll_objs_conn_sts)
        self.callback( self.prefix + 'Connections-Mon', self._ll_objs_conn_sts )

    def _get_initial_hl2ll(self):
        map_ = {
            }
        return map_

    def _pvs_values_rb(self, channel, prop, value):
        if prop not in self._HL_PROPS:
            if self._hl2ll[prop] != value:
                _log.warning(self.prefix+' RB propty = '+prop+' (not HL); '+' LL Device = '+channel+
                            '; New Value = '+str(value)+'; Expected Value = '+str(self._hl2ll[prop]))
                return
        _log.debug(self.prefix+' RB propty = {0:s}; LL Device = {1:s}; New Value = {2:s}'.format(prop,channel,str(value)))
        ind = self._ll_objs_names.index(channel)
        self._values_rb[prop][ind] = self._RB_FUNS[prop](value)
        self.callback( self.prefix + self._HLPROP_2_PVRB[prop], self._values_rb[prop]  )

    def set_propty(self,prop,value):
        if value == self._hl2ll[prop]:
            _log.debug(self.prefix+' new value = old value.')
            return True
        v = self._SP_FUNS[prop](value)
        _log.debug(self.prefix+' propty {0:10s}; Value = {1:s} -> {2:s}'.format(prop,str(value),str(v)))
        self._hl2ll[prop] = v
        for dev, obj in self._ll_objs.items():
            _log.debug(self.prefix+' Sending to LL device = {0:s}'.format(dev))
            obj.set_propty(prop,self._hl2ll[prop])
        return True


class HL_Event(_HL_Base):

    _HL_PROPS = {'delay','mode','delay_type'}

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'Delay-SP']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us', 'prec': 3,
                                     'fun_set_pv':lambda x: self.set_propty('delay',x)}
        db[pre + 'Delay-RB']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us','prec': 3}
        db[pre + 'Mode-Sel']      = {'type' : 'enum', 'enums':Events.MODES, 'value':1,
                                     'fun_set_pv':lambda x: self.set_propty('mode',x)}
        db[pre + 'Mode-Sts']      = {'type' : 'enum', 'enums':Events.MODES, 'value':1}
        db[pre + 'DelayType-Sel'] = {'type' : 'enum', 'enums':Events.DELAY_TYPES, 'value':1,
                                     'fun_set_pv':lambda x: self.set_propty('delay_type',x)}
        db[pre + 'DelayType-Sts'] = {'type' : 'enum', 'enums':Events.DELAY_TYPES, 'value':1}
        db[pre + 'Connections-Mon']  = {'type':'int',  'value':0}
        return db

    def __init__(self,prefix,callback,code):
        super().__init__(prefix,callback,code)

    def _get_initial_hl2ll(self):
        map_ = {
            'delay'      : 0,
            'mode'       : 0,
            'delay_type' : 0,
            }
        return map_

    def _get_HLPROP_2_PVSP(self):
        map_ = { # This dictionary converts the internal property name to the SP pv name
            'delay'      : 'Delay-SP',
            'mode'       : 'Mode-Sel',
            'delay_type' : 'DelayType-Sel',
            }
        return map_

    def _get_HLPROP_2_PVRB(self):
        map_ = {
            'delay'      : 'Delay-RB',
            'mode'       : 'Mode-Sts',
            'delay_type' : 'DelayType-Sts',
            }
        return map_

    def _get_SP_FUNS(self):
        map_ = {
            'delay'      : lambda x: x,
            'mode'       : lambda x: x,
            'delay_type' : lambda x: x,
            }
        return map_

    def _get_RB_FUNS(self):
        map_ = {
            'delay'      : lambda x: x,
            'mode'       : lambda x: x,
            'delay_type' : lambda x: x,
            }
        return map_

    def _get_LL_OBJS_NAMES(self,code):
        channels = [EVG + ':' + Events.LL_TMP.format(code) ]
        return channels

    def _get_LL_OBJ(self,**kwargs):
        return LL_Event(**kwargs)


class _HL_TrigBase(_HL_Base):
    _WORKAS_ENUMS = ('Trigger', 'Clock')

    _HL_PROPS = {'work_as','clock','event','delay','pulses','width','state','polarity'}

    def get_database(self):
        db = dict()
        pre = self.prefix
        len_rb = len(self._ll_trig_names)
        db[pre + 'State-Sel']   = {'type':'enum', 'value':0, 'enums':Triggers.STATES}
        db[pre + 'State-Sts']   = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'WorkAs-Sel']  = {'type':'enum', 'value':0, 'enums':self._WORKAS_ENUMS}
        db[pre + 'WorkAs-Sts']  = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'Event-Sel']   = {'type':'enum', 'value':0, 'enums':self._EVENTS}
        db[pre + 'Event-Sts']   = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'Clock-Sel']   = {'type':'enum', 'value':0, 'enums':Triggers.CLOCKS}
        db[pre + 'Clock-Sts']   = {'type':'int',  'value':0, 'count':len_rb}
        db[pre + 'Delay-SP']    = {'type':'float','value':0.0, 'unit':'us', 'prec': 4}
        db[pre + 'Delay-RB']    = {'type':'float','value':0.0, 'unit':'us', 'prec': 4, 'count':len_rb}
        db[pre + 'Pulses-SP']   = {'type':'int',  'value':1}
        db[pre + 'Pulses-RB']   = {'type':'int',  'value':1, 'count':len_rb}
        db[pre + 'Duration-SP'] = {'type':'float','value':0.0, 'unit':'ms', 'prec': 4}
        db[pre + 'Duration-RB'] = {'type':'float','value':0.0, 'unit':'ms', 'prec': 4, 'count':len_rb}
        db[pre + 'Polrty-Sel']  = {'type':'enum', 'value':0, 'enums':Triggers.POLARITIES}
        db[pre + 'Polrty-Sts']  = {'type':'int',  'value':0, 'count':len_rb}
        db2 = dict()
        for prop in self._HL_PROPS:
            db2[pre + self._HLPROP_2_PVSP[prop]] = db[pre + self._HLPROP_2_PVSP[prop]]
            db2[pre + self._HLPROP_2_PVRB[prop]] = db[pre + self._HLPROP_2_PVRB[prop]]

        db2[pre + 'Connections-Mon']  = {'type':'int',  'value':0, 'count':len_rb}
        return db2

    def __init__(self,prefix,callback,channels,events):
        super().__init__(prefix,callback,channels)
        self._EVENTS = events

    def _get_initial_hl2ll(self):
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

    def _get_HLPROP_2_PVSP(self):
        map_ = {
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
        return map_

    def _get_HLPROP_2_PVRB(self):
        map_ = {
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
        return map_

    def _get_SP_FUNS(self):
        map_ = {
            'work_as'    : lambda x: x,
            'clock'      : lambda x: x,
            'event'      : lambda x: Events.HL2LL_MAP[self._EVENTS[x]],
            'delay'      : lambda x: x,
            'pulses'     : lambda x: x,
            'width'      : lambda x: x / self._hl2ll['pulses']*1e3,
            'state'      : lambda x: x,
            'polarity'   : lambda x: x,
            }
        return map_

    def _get_RB_FUNS(self):
        map_ = {
            'work_as'    : lambda x: x,
            'clock'      : lambda x: x,
            'event'      : self._get_event,
            'delay'      : lambda x: x,
            'pulses'     : lambda x: x,
            'width'      : lambda x: x * self._hl2ll['pulses'] * 1e-3,
            'state'      : lambda x: x,
            'polarity'   : lambda x: x,
            }
        return map_

    def _get_LL_OBJ_NAMES(self,chans):
        channels = set()
        for chan in chans:
            up_dev = _PVName(list(twds_evg[chan])[0])
            while up_dev.dev_name not in EVRs | EVEs | AFCs:
                tmp_ = IOs.O2I_MAP[ up_dev.dev_type ]
                conn_up = tmp_.get( up_dev.propty )
                if conn_up is None:
                    print(IOs.O2I_MAP)
                    print(up_dev.dev_type, up_dev.propty)
                up_dev = _PVName(  list(twds_evg[ up_dev.dev_name +':'+ conn_up ])[0]  )
            channels |= {up_dev}
        return sorted(channels)

    def _get_LL_OBJ(self,**kwargs):
        return get_ll_trigger_object(**kwargs)

    def _get_event(self,x):
        _log.debug(self.prefix+' ll_event = '+str(x))
        hl = Events.LL2HL_MAP[x]
        _log.debug(self.prefix+' hl_event = '+hl+' possible hl_events = '+str(self._EVENTS))
        val = 1000
        if hl in self._EVENTS:
            val = self._EVENTS.index(hl)
        return val


class _HL_TrigSimple(_HL_TrigBase):
    _HL_PROPS = {'event','delay','state'}


class _HL_TrigRmpBO(_HL_TrigBase):
    _HL_PROPS = {'event','state'}

    def _get_initial_hl2ll(self):
        map_ = super()._get_initial_hl2ll()
        map_['width'] = 490e3/2000
        map_['pulses'] = 2000
        return map_


class _HL_TrigCavity(_HL_TrigRmpBO):
    _HL_PROPS = {'event','state','pulses'}


class _HL_TrigPSSI(_HL_TrigBase):
    _HL_PROPS = {'event','state','width','work_as','clock'}

    def _get_initial_hl2ll(self):
        map_ = super()._get_initial_hl2ll()
        map_['width'] = 2/2000
        map_['pulses'] = 2000
        return map_

    def _get_SP_FUNS(self):
        map_ = super()._get_SP_FUNS()
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
            for dev, obj in self._ll_trigs.items():
                obj.set_propty(prop,self._hl2ll[prop])

        return Events.HL2LL_MAP[self._EVENTS[ev]]


class _HL_TrigGeneric(_HL_TrigBase):
    _HL_PROPS = {'event','state','pulses','width','work_as','clock'}
