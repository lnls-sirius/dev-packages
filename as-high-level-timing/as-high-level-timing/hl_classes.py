import logging as _log
import copy as _copy
from siriuspy.timesys.time_data import Connections, IOs, Triggers, Clocks, Events
from siriuspy.namesys import SiriusPVName as _PVName
from ll_classes import get_ll_trigger_object
from ll_classes import LL_Event

def _get_initial_trig_hl2ll():
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

Connections.add_bbb_info()
Connections.add_crates_info()
EVRs = Connections.get_devices('EVR')
EVEs = Connections.get_devices('EVE')
AFCs = Connections.get_devices('AFC')
twds_evg = Connections.get_connections_twds_evg()

def _get_ll_trig_names(chans):
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


def get_hl_trigger_object(trig_prefix,callback,channels,events,trigger_type):
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
    return cls_(trig_prefix,callback,channels,events)


class _HL_TrigBase:
    _WORKAS_ENUMS = ('Trigger', 'Clock')

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
    _PVSP_2_HLPROP = {  val:key for key,val in _HLPROP_2_PVSP.items()  }
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

    def __init__(self,trig_prefix,callback,channels,events):
        _log.info(trig_prefix +' Starting.')
        self._RB_FUNS  = self._get_RB_FUNS()
        self._SP_FUNS = self._get_SP_FUNS()
        self._EVENTS = events
        self.callback = callback
        self.prefix = trig_prefix
        self._ll_trig_names = _get_ll_trig_names(channels)
        _log.debug(self.prefix+ ' LL trigger names: '+' '.join([tr for tr in self._ll_trig_names]))
        len_rb = len(self._ll_trig_names)
        self._hl2ll = self._get_initial_hl2ll() # high level to low level interface
        self._values_rb = {  key:len_rb*[val] for key,val in self._hl2ll.items()  }
        self._ll_trigs = dict()
        self._ll_trigs_conn_sts = list()

    def connect(self):
        _log.info(self.prefix+' -> connecting to LL Devices')
        for chan in self._ll_trig_names:
            _log.debug(self.prefix +' -> connecting to {0:s}'.format(chan))
            low_lev_obj = get_ll_trigger_object(
                                channel = chan,
                                callback = self._pvs_values_rb,
                                connection_callback = self._ll_on_connection,
                                initial_hl2ll=_copy.deepcopy(self._hl2ll),
                                )
            self._ll_trigs[chan] = low_lev_obj
            self._ll_trigs_conn_sts.append(0)

    def _ll_on_connection(self,channel,status):
        ind = self._ll_trig_names.index(device)
        self._ll_trigs_conn_sts[ind] = int(status)
        status = all(self._ll_trigs_conn_sts)
        self.callback( self.prefix + 'Connections-Mon', self._ll_trigs_conn_sts )

    def _get_initial_hl2ll(self): return _get_initial_trig_hl2ll()

    def _get_SP_FUNS(self):
        map_ = {
            'work_as'    : lambda x: self._WORKAS_ENUMS[x],
            'clock'      : lambda x: Triggers.CLOCKS[x],
            'event'      : lambda x: Events.HL2LL_MAP[self._EVENTS[x]],
            'delay'      : lambda x: x,
            'pulses'     : lambda x: x,
            'width'      : lambda x: x / self._hl2ll['pulses']*1e3,
            'state'      : lambda x: Triggers.STATES[x],
            'polarity'   : lambda x: Triggers.POLARITIES[x],
            }
        return map_

    def _get_RB_FUNS(self):
        map_ = {
            'work_as'    : lambda x: x,
            'clock'      : lambda x: x,
            'event'      : lambda x: self._EVENTS.index(Events.LL2HL_MAP[x]),
            'delay'      : lambda x: x,
            'pulses'     : lambda x: x,
            'width'      : lambda x: x * self._values_rb[y]['pulses'] * 1e-3,
            'state'      : lambda x: x,
            'polarity'   : lambda x: x,
            }
        return map_

    def _pvs_values_rb(self, channel, prop, value):
        if prop not in self._HL_PROPS:
            if self._hl2ll[prop] != value:
                _log.warning(self.prefix+' RB propty = '+prop+' (not HL); '+' LL Device = '+channel+
                        '; New Value = '+str(value)+'; Expected Value = '+str(self._hl2ll[prop]))
            return
        _log.debug(self.prefix+' RB propty = {0:s}; LL Device = {1:s}; New Value = {2:s}'.format(prop,channel,str(value)))
        ind = self._ll_trig_names.index(channel)
        self._values_rb[prop][ind] = self._RB_FUNS[prop](value)
        self.callback( self.prefix + self._HLPROP_2_PVRB[prop], self._values_rb[prop]  )

    def set_propty(self,reason,value):
        _log.debug(self.prefix+' set_propty receive {0:15s}; Value = {1:s}'.format(reason,str(value)))
        pv = pv.split(self.prefix)
        if len(pv) == 1:
            _log.debug(self.prefix+' Not my PV.')
            return False
        prop = self._PVSP_2_HLPROP.get(pv[1])
        if prop not in self._HL_PROPS:
            _log.debug(self.prefix+' propty = {0:s} not recognized.'.format(prop))
            return False
        if value == self._hl2ll[prop]:
            _log.debug(self.prefix+' new value = old value.')
            return True
        self._hl2ll[prop] = self._SP_FUNS[prop](value)
        for dev, obj in self._ll_trigs.keys():
            _log.debug(self.prefix+' Sending to LL device = {0:s}'.format(dev))
            obj.set_propty(prop,self._hl2ll[prop])
        return True


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
            for dev, obj in self._ll_trigs.keys():
                obj.set_propty(prop,self._hl2ll[prop])

        return Events.HL2LL_MAP[self._EVENTS[ev]]


class _HL_TrigGeneric(_HL_TrigBase):
    _HL_PROPS = {'event','state','pulses','width','work_as','clock'}


class HL_Event:
    _HLPROP_2_PVSP = { # This dictionary converts the internal property name to the SP pv name
        'delay'      : 'Delay-SP',
        'mode'       : 'Mode-Sel',
        'delay_type' : 'DelayType-Sel',
        }
    _PVSP_2_HLPROP = {  val:key for key,val in _HLPROP_2_PVSP.items()  }
    _HLPROP_2_PVRB = {
        'delay'      : 'Delay-RB',
        'mode'       : 'Mode-Sts',
        'delay_type' : 'DelayType-Sts',
        }

    def get_database(self):
        db = dict()
        pre = self.prefix
        db[pre + 'Delay-SP']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us', 'prec': 3}
        db[pre + 'Delay-RB']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us','prec': 3}
        db[pre + 'Mode-Sel']      = {'type' : 'enum', 'enums':Events.MODES, 'value':1}
        db[pre + 'Mode-Sts']      = {'type' : 'enum', 'enums':Events.MODES, 'value':1}
        db[pre + 'DelayType-Sel'] = {'type' : 'enum', 'enums':Events.DELAY_TYPES, 'value':1}
        db[pre + 'DelayType-Sts'] = {'type' : 'enum', 'enums':Events.DELAY_TYPES, 'value':1}
        db[pre + 'Connections-Mon']  = {'type':'int',  'value':0}
        return db

    def __init__(self,prefix,code,callback):
        _log.info('Event '+prefix+', code = '+str(code)+' Starting.')
        self._RB_FUNS  = self._get_RB_FUNS()
        self._SP_FUNS = self._get_SP_FUNS()
        self.callback = callback
        self.prefix = prefix
        self.ll_code  = code
        self._hl2ll = self._get_initial_hl2ll()
        self._values_rb = {  key:val for key,val in self._hl2ll.items()  }

    def connect(self):
        _log.info('Event '+self.prefix+' -> connecting to LL Devices')
        self.ll_obj_conn_sts = 0
        self.ll_obj = LL_Event( code = self.ll_code,
                                callback = self._pvs_values_rb,
                                connection_callback = self._ll_on_connection,
                                initial_hl2ll=_copy.deepcopy(self._hl2ll)
                                )

    def _ll_on_connection(self,status):
        self.ll_obj_conn_sts = int(status)
        self.callback( self.prefix + 'Connections-Mon', self._ll_trigs_conn_sts )

    def _get_initial_hl2ll(self):
        map_ = {
            'delay'      : 0,
            'mode'       : 0,
            'delay_type' : 0,
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

    def _pvs_values_rb(self, channel, prop, value):
        _log.debug('Event '+self.prefix+' RB propty = {0:s}; LL Device = {1:s}; New Value = {2:s}'.format(prop,channel,str(value)))
        self._values_rb[prop] = self._RB_FUNS[prop](value)
        self.callback( self.prefix + self._HLPROP_2_PVRB[prop], self._values_rb[prop]  )

    def set_propty(self,reason,value):
        _log.debug('Event '+self.prefix+' set_propty receive {0:15s}; Value = {0:s}'.format(reason,str(value)))
        pv = pv.split(self.prefix)
        if len(pv) == 1:
            _log.debug('Event '+self.prefix+' Not my PV.')
            return False
        prop = self._PVSP_2_HLPROP.get(pv[1])
        if value == self._hl2ll[prop]:
            _log.debug('Event '+self.prefix+' new value = old value.')
            return True
        self._hl2ll[prop] = self._SP_FUNS[prop](value)
        _log.debug('Event '+self.prefix+' Sending to LL device')
        self.ll_obj.set_propty(prop,self._hl2ll[prop])
        return True
