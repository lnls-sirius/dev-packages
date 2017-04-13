import uuid as _uuid
import numpy as _np
import threading as _threading
import time as _time
import timing_devices_data as _timedata

_PwrFreq = 60
_FINE_DELAY_STEP = 5e-12
RF_FREQ_DIV = 4

_EVNTS_AVAIL = list(range(50)) + list(range(80,120)) + list(range(160,256))

_EVENT_LABEL_TEMPLATE = 'Ev{0:02x}'
_CLOCK_LABEL_TEMPLATE = 'Cl{0:1d}'

EVENT_LABEL_TEMPLATE = _timedata.EVENT_LABEL_TEMPLATE
CLOCK_LABEL_TEMPLATE = _timedata.CLOCK_LABEL_TEMPLATE
OPT_LABEL_TEMPLATE   = _timedata.OPT_LABEL_TEMPLATE
OUT_LABEL_TEMPLATE   = _timedata.OUT_LABEL_TEMPLATE

class CallBack:

    def __init__(self, callbacks=None, prefix = None):
        self.prefix = prefix or ''
        self._callbacks = dict(callbacks) if callbacks else dict()

    def _callback(self,propty,value,**kwargs):
        return NotImplemented

    def _call_callbacks(self, propty, value, **kwargs):
        for uuid, callback in self._callbacks.items():
            callback(self.prefix + propty, value, **kwargs)

    def add_callback(self,*args):
        if len(args)<2 and isinstance(args[0],dict):
            self._callbacks.update(args[0])
        elif len(args) == 2:
            uuid, callback = args
            self._callbacks[uuid] = callback
        else:
            raise Exception('wrong input for add_callback')

    def remove_callback(self,uuid):
        self._callbacks.pop(uuid)


class _BaseSim(CallBack):

    _attributes = {}

    def __init__(self,callbacks=None):
        super().__init__(callbacks)

    def __getattr__(self,name):
        if name in self.__class__._attributes:
            return self.__dict__['_'+name]
        else:
            return super().__getattr__(name)

    def __setattr__(self,name,value):
        if name in self.__class__._attributes:
            self.__dict__['_'+name] = value
            self._call_callbacks(name,value)
        else:
            super().__setattr__(name, value)


class _BaseIOC(CallBack):

    @classmethod
    def get_database(cls, prefix=''):
        db = dict()
        return NotImplemented #return db

    def __init__(self, controller, callbacks = None, prefix = None):
        super().__init__(callbacks, prefix = prefix)
        self.uuid = _uuid.uuid4()
        self._pvname2attr = { value:key for key,value in self._attr2pvname.items() }
        self._controller = controller
        self._controller.add_callback({self.uuid:self._callback})
        self.base_freq = self._controller.base_freq
        self._set_init_values()

    def __getattr__(self,name):
        if name in self.__class__._attr2pvname.keys():
            return self.__dict__['_'+name]
        else:
            return super().__getattr__(name)

    def __setattr__(self,name,value):
        if name in self.__class__._attr2pvname.keys():
            if name.endswith(('_sp','_sel')):
                self._controller.__setattr__(  name[:-3], self._attr2expr[name](value)  )
                self.__dict__['_'+name] = value
            elif name.endswith(('_rb','_sts')):
                self.__dict__['_'+name] = self._attr2expr[name](value)
            self._call_callbacks(self._attr2pvname[name],value)
        else:
            super().__setattr__(name, value)

    def _set_init_values(self):
        db = self.get_database()
        for attr,pv in self._attr2pvname.items():
            self.__setattr__('_' + attr, db[pv]['value'])

    def get_propty(self,reason):
        reason = reason[len(self.prefix):]
        if reason not in self._pvname2attr.keys():
            return None
        return self.__getattr__(self._pvname2attr[reason])

    def set_propty(self,reason,value):
        reason = reason[len(self.prefix):]
        if reason not in self._pvname2attr.keys() or reason.endswith(('-RB','-Sts')):
            return False
        self.__setattr__(self._pvname2attr[reason],value)
        return True


##############################################################
############## Event Generator Part ##########################
##############################################################

class _ClockSim(_BaseSim):

    _attributes = {'state','frequency'}

    def __init__(self, base_freq, callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._frequency = 1
        self._state = 0

    def generate(self):
        if self._state > 0:
            return {'frequency':self.base_freq/self._frequency}


class _EventSim(_BaseSim):

    _attributes = {'delay','mode','delay_type',}

    def __init__(self, base_freq, callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._delay_type = None
        self._delay = 0
        self._mode = 0

    def generate(self):
        if self._mode > 0:
            return {'delay':self._delay/self.base_freq}


class _EVGSim(_BaseSim):

    _attributes = {'continuous','cyclic_injection','bucket_list','repetition_rate','injection','single'}

    def __init__(self, base_freq, callbacks= None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._pending_devices_callbacks = dict()
        self._continuous = 1
        self._injection = 0
        self._injection_callbacks = dict()
        self._cyclic_injection = 0
        self._single = 0
        self._single_callbacks = dict()
        self._bucket_list = [0.0]*864
        self._repetition_rate = 30
        self.events = list()
        for i in _EVNTS_AVAIL:
            self.events.append(_EventSim(self.base_freq/RF_FREQ_DIV))
        self.clocks = list()
        for i in range(8):
            self.clocks.append(_ClockSim(self.base_freq/RF_FREQ_DIV))

    def __setattr__(self,attr,value):
        if attr == 'injection':
            if value:
                if not self._injection and self._continuous:
                    self._injection = value
                    _threading.Thread(target=self._injection_fun).start()
            else:
                self._injection = value
            self._call_callbacks('injection',value)
        elif attr == 'single':
            if value:
                if not self._single:
                    self._single = value
                    if not self._continuous: return
                    evnts = self._generate_events(3)
                    triggers = dict()
                    for callback in self._pending_devices_callbacks.values():
                        triggers.update(callback(0,evnts))
                    for callback in self._single_callbacks.values():
                        callback(triggers)
            else:
                self._single = value
            self._call_callbacks('single',value)
        else:
            super().__setattr__(attr,value)

    def add_pending_devices_callback(self, uuid,callback):
        self._pending_devices_callbacks.update({uuid:callback})

    def remove_pending_devices_callback(self, uuid):
        self._pending_devices_callbacks.pop(uuid,None)

    ########### Functions related to Single Pulse simulation #############
    def add_injection_callback(self,uuid,callback):
        self._injection_callbacks.update({uuid:callback})

    def remove_injection_callback(self,uuid):
        self._injection_callbacks.pop(uuid, None)

    def _injection_fun(self):
        while True:
            if not len(self._bucket_list): _time.sleep(0.1)
            for i in self._bucket_list:
                if not self._can_inject(): return

                if i<=0: break
                evnts = self._generate_events((1,2))
                triggers = dict()
                for callback in self._pending_devices_callbacks.values():
                    triggers.update(callback(i,evnts))
                for callback in self._injection_callbacks.values():
                    callback(i,triggers)
                _time.sleep(self._repetition_rate/_PwrFreq)
            if not self._cyclic_injection:
                self._injection = 0
                self._call_callbacks('injection',0)
                return

    def _can_inject(self):
        if not self._continuous or not self._injection: return False
        return True
    ######################################################################

    ########### Functions related to Single Pulse simulation #############
    def add_single_callback(self,uuid,callback):
        self._single_callbacks.update({uuid:callback})

    def remove_single_callback(self,uuid):
        self._single_callbacks.pop(uuid, None)
    ##########################################################################

    def _generate_events(self,tables):
        tables = tables if isinstance(tables,(list,tuple)) else (tables,)
        events = dict()
        for i, ev in enumerate(self.events):
            ev_nr = _EVNTS_AVAIL[i]
            if not ev.mode in tables: continue
            dic = ev.generate()
            if not dic: continue
            lab = _EVENT_LABEL_TEMPLATE.format(ev_nr)
            events.update(  { lab : dic }  )
        for i, cl in enumerate(self.clocks):
            dic = cl.generate()
            if not dic: continue
            lab = _CLOCK_LABEL_TEMPLATE.format(i)
            events.update(  { lab : dic }  )
        return events


class _EventIOC(_BaseIOC):

    _modes = ('Disabled','Continuous','Injection','Single')
    _delay_types = ('Fixed','Incr')

    _attr2pvname = {
        'delay_sp':'Delay-SP',
        'delay_rb':'Delay-RB',
        'mode_sp':'Mode-Sel',
        'mode_rb':'Mode-Sts',
        'delay_type_sp':'DelayType-Sel',
        'delay_type_rb':'DelayType-Sts',
        }

    @classmethod
    def get_database(cls, prefix=''):
        db = dict()
        db[prefix + 'Delay-SP']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us', 'prec': 3}
        db[prefix + 'Delay-RB']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us','prec': 3}
        db[prefix + 'Mode-Sel']      = {'type' : 'enum', 'enums':_EventIOC._modes, 'value':1}
        db[prefix + 'Mode-Sts']      = {'type' : 'enum', 'enums':_EventIOC._modes, 'value':1}
        db[prefix + 'DelayType-Sel'] = {'type' : 'enum', 'enums':_EventIOC._delay_types, 'value':1}
        db[prefix + 'DelayType-Sts'] = {'type' : 'enum', 'enums':_EventIOC._delay_types, 'value':1}
        return db

    def __init__(self,base_freq,callbacks = None, prefix = None, controller = None):
        self._attr2expr  = {
            'delay_sp': lambda x: int(round( x * self.base_freq)),
            'delay_rb': lambda x: x * (1/self.base_freq),
            'mode_sp': lambda x: int(x),
            'mode_rb': lambda x: x,
            'delay_type_sp': lambda x: int(x),
            'delay_type_rb': lambda x: x,
            }
        if controller is None: controller = _EventSim(base_freq)
        super().__init__(controller, callbacks, prefix = prefix)

    def _callback(self,propty,value,**kwargs):
        if propty == 'delay':
            self.delay_rb = value
        if propty == 'mode':
            self.mode_rb = value
        if propty == 'delay_type':
            self.delay_type_rb = value


class _ClockIOC(_BaseIOC):

    _states = ('Dsbl','Enbl')

    _attr2pvname = {
        'frequency_sp' :'Freq-SP',
        'frequency_rb' :'Freq-RB',
        'state_sp' :'State-Sel',
        'state_rb' :'State-Sts',
        }

    @classmethod
    def get_database(cls, prefix=''):
        db = dict()
        db[prefix + 'Freq-SP']   = {'type' : 'float', 'value': 1.0, 'prec': 10}
        db[prefix + 'Freq-RB']   = {'type' : 'float', 'value': 1.0, 'prec': 10}
        db[prefix + 'State-Sel'] = {'type' : 'enum', 'enums':_ClockIOC._states, 'value':0}
        db[prefix + 'State-Sts'] = {'type' : 'enum', 'enums':_ClockIOC._states, 'value':0}
        return db

    def __init__(self, base_freq, callbacks = None, prefix = None, controller = None):
        self._attr2expr  = {
            'frequency_sp': lambda x: int( round(self.base_frequency / x) ),
            'frequency_rb': lambda x: x * self.base_freq,
            'state_sp': lambda x: int(x),
            'state_rb': lambda x: x,
            }
        if controller is None: controller = _ClockSim(base_freq)
        super().__init__(controller, callbacks, prefix = prefix)

    def _callback(self, propty,value,**kwargs):
        if propty == 'frequency':
            self.frequency_rb = value
        if propty == 'state':
            self.state_rb = value


class EVGIOC(_BaseIOC):

    _states = ('Dsbl','Enbl')
    _cyclic_types = ('Off','On')

    _attr2pvname = {
        'single_sp' : 'SingleState-Sel',
        'single_rb' : 'SingleState-Sts',
        'injection_sp' : 'InjectionState-Sel',
        'injection_rb' : 'InjectionState-Sts',
        'cyclic_injection_sp' : 'InjCyclic-Sel',
        'cyclic_injection_rb' : 'InjCyclic-Sts',
        'continuous_sp' : 'ContinuousState-Sel',
        'continuous_rb' : 'ContinuousState-Sts',
        'repetition_rate_sp' : 'RepRate-SP',
        'repetition_rate_rb' : 'RepRate-RB',
        'bucket_list_sp' : 'BucketList-SP',
        'bucket_list_rb' : 'BucketList-RB',
        }

    @classmethod
    def get_database(cls, prefix=''):
        db = dict()
        p = prefix
        db[p + 'SingleState-Sel']     = {'type' : 'enum', 'enums':EVGIOC._states, 'value':0}
        db[p + 'SingleState-Sts']     = {'type' : 'enum', 'enums':EVGIOC._states, 'value':0}
        db[p + 'InjectionState-Sel']  = {'type' : 'enum', 'enums':EVGIOC._states, 'value':0}
        db[p + 'InjectionState-Sts']  = {'type' : 'enum', 'enums':EVGIOC._states, 'value':0}
        db[p + 'InjCyclic-Sel']       = {'type' : 'enum', 'enums':EVGIOC._cyclic_types, 'value':0}
        db[p + 'InjCyclic-Sts']       = {'type' : 'enum', 'enums':EVGIOC._cyclic_types, 'value':0}
        db[p + 'ContinuousState-Sel'] = {'type' : 'enum', 'enums':EVGIOC._states, 'value':1}
        db[p + 'ContinuousState-Sts'] = {'type' : 'enum', 'enums':EVGIOC._states, 'value':1}
        db[p + 'BucketList-SP'] = {'type' : 'int', 'count': 864, 'value':0}
        db[p + 'BucketList-RB'] = {'type' : 'int', 'count': 864, 'value':0}
        db[p + 'RepRate-SP'] = {'type' : 'float', 'unit':'Hz', 'value': 2.0, 'prec': 5}
        db[p + 'RepRate-RB'] = {'type' : 'float', 'unit':'Hz', 'value': 2.0, 'prec': 5}
        for i in range(8):
            p = prefix + CLOCK_LABEL_TEMPLATE.format(i)
            db.update(_ClockIOC.get_database(p))
        for i in _EVNTS_AVAIL:
            p = prefix + EVENT_LABEL_TEMPLATE.format(i)
            db.update(_EventIOC.get_database(p))

        return db

    def __init__(self, base_freq, callbacks = None, prefix = None, controller = None):
        self._attr2expr = {
            'single_sp' : lambda x: int(x),
            'single_rb' : lambda x: x,
            'injection_sp' : lambda x: int(x),
            'injection_rb' : lambda x: x,
            'cyclic_injection_sp' : lambda x: int(x),
            'cyclic_injection_rb' : lambda x: x,
            'continuous_sp' : lambda x: int(x),
            'continuous_rb' : lambda x: x,
            'repetition_rate_sp' : lambda x: int(round(_PwrFreq / x)),
            'repetition_rate_rb' : lambda x: x * _PwrFreq,
            'bucket_list_sp' : self._bucket_list_setter,
            'bucket_list_rb' : lambda x: x,
            }
        if controller is None: controller = _EVGSim(base_freq)
        super().__init__(controller, callbacks = callbacks, prefix = prefix)

        self.events = dict()
        for i,ev_nr in enumerate(_EVNTS_AVAIL):
            name = EVENT_LABEL_TEMPLATE.format(ev_nr)
            cntler = self._controller.events[i]
            self.events[name] = _EventIOC(self.base_freq/RF_FREQ_DIV,
                                         callbacks = {self.uuid:self._ioc_callback},
                                         prefix = name,
                                         controller = cntler)
        self.clocks = dict()
        for i in range(8):
            name = CLOCK_LABEL_TEMPLATE.format(i)
            cntler = self._controller.clocks[i]
            self.clocks[name] = _ClockIOC(self.base_freq/RF_FREQ_DIV,
                                         callbacks = {self.uuid:self._ioc_callback},
                                         prefix = name,
                                         controller = cntler)

    def _bucket_list_setter(self,value):
        bucket = []
        for i in range(min(len(value),864)):
            if value[i]<=0: break
            bucket.append(  int( (value[i]-1) % 864 ) + 1  )
        return bucket + ( 864-len(bucket) ) * [0]

    def _set_init_values(self):
        super()._set_init_values()
        db = self.get_database()
        self._bucket_list_sp = 864*[db['BucketList-SP']['value']]
        self._bucket_list_rb = 864*[db['BucketList-RB']['value']]


    def _ioc_callback(self,propty,value, **kwargs):
        self._call_callbacks(propty, value, **kwargs)

    def _callback(self,propty,value, **kwargs):
        if propty == 'continuous':
            self.continuous_rb = value
        elif propty == 'cyclic_injection':
            self.cyclic_injection_rb = value
        elif propty == 'bucket_list':
            self.bucket_list_rb = value
        elif propty == 'repetition_rate':
            self.repetition_rate_rb = value
        elif propty == 'injection':
            self.injection_rb = value
            if value != self._injection_sp:
                self._injection_sp = value
                self._call_callbacks('InjectionState-Sel',value)
        elif propty == 'single':
            self.single_rb = value
            self._single_sp = value
            self._call_callbacks('SingleState-Sel',value)

    def add_injection_callback(self, uuid,callback):
        self._controller.add_injection_callback(uuid,callback)

    def remove_injection_callback(self, uuid):
        self._controller.remove_injection_callback(uuid)

    def add_single_callback(self, uuid,callback):
        self._controller.add_single_callback(uuid,callback)

    def remove_single_callback(self, uuid):
        self._controller.remove_single_callback(uuid)

    def add_pending_devices_callback(self, uuid,callback):
        self._controller.add_pending_devices_callback(uuid,callback)

    def remove_pending_devices_callback(self, uuid):
        self._controller.remove_pending_devices_callback(uuid)

    def get_propty(self, reason):
        reason2 = reason[len(self.prefix):]
        if reason2.startswith(tuple(self.clocks.keys())):
            return self.clocks[reason2[:6]].get_propty(reason2)#Not general enough
        elif reason2.startswith(tuple(self.events.keys())):
            return self.events[reason2[:6]].get_propty(reason2)#Absolutely not general enough
        else:
            return super().get_propty(reason)

    def set_propty(self, reason, value):
        reason2 = reason[len(self.prefix):]
        if reason2.startswith(tuple(self.clocks.keys())):
            return self.clocks[reason2[:6]].set_propty(reason2, value)#Not general enough
        elif reason2.startswith(tuple(self.events.keys())):
            return self.events[reason2[:6]].set_propty(reason2, value)#Absolutely not general enough
        else:
            return super().set_propty(reason, value)


##############################################################
############## Event Receivers Part ##########################
##############################################################
class _TriggerSim(_BaseSim):

    _attributes = {'fine_delay','delay','optic_channel'}

    def __init__(self,base_freq,callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._optic_channel = 0
        self._delay = 0
        self._fine_delay = 0

    def receive_events(self, bucket, opts):
        lab = OPT_LABEL_TEMPLATE.format(self._optic_channel)
        dic = opts.get(lab,None)
        if dic is None: return
        dic['delay'] += self._delay/self.base_freq + self._fine_delay * _FINE_DELAY_STEP
        return dic


class _OpticChannelSim(_BaseSim):

    _attributes = {'state','width','delay','polarity','event','pulses'}

    def __init__(self,base_freq,callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._state = 0
        self._width = 0
        self._delay = 0
        self._polarity = 0
        self._event = 0
        self._pulses = 1

    def receive_events(self, bucket, events):
        if self._state == 0: return
        lab = _EVENT_LABEL_TEMPLATE.format(self._event)
        ev = events.get(lab,None)
        if ev is None: return
        delay = ev['delay'] + self._delay/self.base_freq
        return dict(  { 'pulses':self._pulses, 'width':self._width/self.base_freq, 'delay':delay }  )


class _EVRSim(_BaseSim):
    _ClassTrigSim = _TriggerSim
    _NR_INTERNAL_OPT_CHANNELS = 24
    _NR_OPT_CHANNELS = 12
    _NR_OUT_CHANNELS = 8

    _attributes = {'state'}

    def __init__(self, base_freq, callbacks= None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._state = 1

        self.optic_channels = list()
        for _ in range(self._NR_INTERNAL_OPT_CHANNELS):
            self.optic_channels.append( _OpticChannelSim(self.base_freq) )

        self.trigger_outputs = list()
        for _ in range(self._NR_OUT_CHANNELS):
            self.trigger_outputs.append(self._ClassTrigSim(self.base_freq) )

    def receive_events(self, bucket, events):
        triggers = dict()
        inp_dic = dict(events)
        for i, opt_ch in enumerate(self.optic_channels):
            opt = opt_ch.receive_events(bucket, inp_dic)
            if opt is None: continue
            lab = OPT_LABEL_TEMPLATE.format(i)
            inp_dic.update( {lab:opt} )
            if i < self._NR_OPT_CHANNELS: triggers.update( {lab:opt} )
        for tri_ch in self.trigger_outputs:
            out = tri_ch.receive_events(bucket, inp_dic)
            if out is None: continue
            lab = OUT_LABEL_TEMPLATE.format(i)
            triggers.update( {lab:out} )
        return triggers


class _EVESim(_EVRSim):
    _ClassTrigSim = _TriggerSim
    _NR_INTERNAL_OPT_CHANNELS = 16
    _NR_OPT_CHANNELS = 0
    _NR_OUT_CHANNELS = 8


class _AFCSim(_EVRSim):
    _ClassTrigSim = _OpticChannelSim
    _NR_INTERNAL_OPT_CHANNELS = 10
    _NR_OPT_CHANNELS = 10
    _NR_OUT_CHANNELS = 8


class _EVRTriggerIOC(_BaseIOC):

    _optic_channels = tuple(  [ OPT_LABEL_TEMPLATE.format(i) for i in range(_EVRSim._NR_INTERNAL_OPT_CHANNELS) ]  )

    _attr2pvname = {
        'fine_delay_sp':    'FineDelay-SP',
        'fine_delay_rb':    'FineDelay-RB',
        'delay_sp':         'Delay-SP',
        'delay_rb':         'Delay-RB',
        'optic_channel_sp': 'OptCh-Sel',
        'optic_channel_rb': 'OptCh-Sts',
        }

    @classmethod
    def get_database(cls, prefix=''):
        db = dict()
        db[prefix + 'FineDelay-SP']   = {'type' : 'float', 'unit':'ps', 'value': 0.0, 'prec': 0}
        db[prefix + 'FineDelay-RB']   = {'type' : 'float', 'unit':'ps', 'value': 0.0, 'prec': 0}
        db[prefix + 'Delay-SP']       = {'type' : 'float', 'unit':'us', 'value': 0.0, 'prec': 0}
        db[prefix + 'Delay-RB']       = {'type' : 'float', 'unit':'us', 'value': 0.0, 'prec': 0}
        db[prefix + 'OptCh-Sel']      = {'type' : 'int', 'value':0}
        db[prefix + 'OptCh-Sts']      = {'type' : 'int', 'value':0}
        # db[prefix + 'OptCh-Sel']      = {'type' : 'enum', 'enums':cls._optic_channels, 'value':0} # pcaspy only accepts 16 states for enum
        # db[prefix + 'OptCh-Sts']      = {'type' : 'enum', 'enums':cls._optic_channels, 'value':0}
        return db

    def __init__(self, base_freq, callbacks = None, prefix = None, controller = None):
        self._attr2expr  = {
            'fine_delay_sp':    lambda x: int(round(x / _FINE_DELAY_STEP )),
            'fine_delay_rb':    lambda x: x * _FINE_DELAY_STEP,
            'delay_sp':         lambda x: int(round( x * self.base_freq)),
            'delay_rb':         lambda x: x / self.base_freq,
            'optic_channel_sp': lambda x: int(x),
            'optic_channel_rb': lambda x: x,
            }
        if controller is None: controller = _TriggerSim(base_freq)
        super().__init__(controller, callbacks, prefix = prefix)

    def _callback(self, propty,value,**kwargs):
        if propty == 'delay':
            self.delay_rb = value
        if propty == 'fine_delay':
            self.fine_delay_rb = value
        if propty == 'optic_channel':
            self.optic_channel_rb = value


class _EVETriggerIOC(_EVRTriggerIOC):

    _optic_channels = tuple(  [ OPT_LABEL_TEMPLATE.format(i) for i in range(_EVESim._NR_INTERNAL_OPT_CHANNELS) ]  )


class _OpticChannelIOC(_BaseIOC):

    _states = ('Dsbl','Enbl')
    _polarities = ('Normal','Inverse')
    _delay_types = ('Fixed','Incr')
    _events = [EVENT_LABEL_TEMPLATE.format(i) for i in _EVNTS_AVAIL] + [CLOCK_LABEL_TEMPLATE.format(i) for i in range(8)]

    _attr2pvname = {
        'state_sp'      :'State-Sel',
        'state_rb'      :'State-Sts',
        'width_sp'      :'Width-SP',
        'width_rb'      :'Width-RB',
        'delay_sp'      :'Delay-SP',
        'delay_rb'      :'Delay-RB',
        'polarity_sp'   :'Polrty-Sel',
        'polarity_rb'   :'Polrty-Sts',
        'event_sp'      :'Event-Sel',
        'event_rb'      :'Event-Sts',
        'pulses_sp'     :'Pulses-SP',
        'pulses_rb'     :'Pulses-RB',
        }

    @classmethod
    def get_database(cls,prefix=''):
        db = dict()
        db[prefix + 'State-Sel']     = {'type' : 'enum', 'enums':cls._states, 'value':0}
        db[prefix + 'State-Sts']     = {'type' : 'enum', 'enums':cls._states, 'value':0}
        db[prefix + 'Width-SP']      = {'type' : 'float', 'value': 0.0, 'unit':'ns', 'prec': 3}
        db[prefix + 'Width-RB']      = {'type' : 'float', 'value': 0.0, 'unit':'ns', 'prec': 3}
        db[prefix + 'Delay-SP']      = {'type' : 'float', 'value': 0.0, 'unit':'us', 'prec': 3}
        db[prefix + 'Delay-RB']      = {'type' : 'float', 'value': 0.0, 'unit':'us', 'prec': 3}
        db[prefix + 'Polrty-Sel']    = {'type' : 'enum', 'enums':cls._polarities, 'value':0}
        db[prefix + 'Polrty-Sts']    = {'type' : 'enum', 'enums':cls._polarities, 'value':0}
        db[prefix + 'Event-Sel']     = {'type' : 'int', 'value':0}
        db[prefix + 'Event-Sts']     = {'type' : 'int', 'value':0}
        # db[prefix + 'Event-Sel']     = {'type' : 'enum', 'enums':cls._events, 'value':0}
        # db[prefix + 'Event-Sts']     = {'type' : 'enum', 'enums':cls._events, 'value':0}
        db[prefix + 'Pulses-SP']     = {'type' : 'float', 'value': 0.0, 'prec': 3}
        db[prefix + 'Pulses-RB']     = {'type' : 'float', 'value': 0.0, 'prec': 3}
        return db

    def __init__(self,base_freq,callbacks = None, prefix = None, controller = None):
        self._attr2expr  = {
            'state_sp'      : lambda x: int(x),
            'state_rb'      : lambda x: x,
            'width_sp'      : lambda x: int(round( x * self.base_freq)),
            'width_rb'      : lambda x: x * (1/self.base_freq),
            'delay_sp'      : lambda x: int(round( x * self.base_freq)),
            'delay_rb'      : lambda x: x * (1/self.base_freq),
            'polarity_sp'   : lambda x: int(x),
            'polarity_rb'   : lambda x: x,
            'event_sp'      : lambda x: int(x),
            'event_rb'      : lambda x: x,
            'pulses_sp'     : lambda x: int(x),
            'pulses_rb'     : lambda x: x,
            }
        if controller is None: controller = _OpticChannelSim(base_freq)
        super().__init__(controller, callbacks, prefix = prefix)

    def _callback(self,propty,value,**kwargs):
        if propty == 'state':
            self.state_rb = value
        if propty == 'width':
            self.width_rb = value
        if propty == 'delay':
            self.delay_rb = value
        if propty == 'polarity':
            self.polarity_rb = value
        if propty == 'event':
            self.event_rb = value
        if propty == 'pulses':
            self.pulses_rb = value


class EVRIOC(_BaseIOC):
    _ClassSim = _EVRSim
    _ClassTrigIOC = _EVRTriggerIOC

    _states = ('Dsbl','Enbl')

    _attr2pvname = {
        'state_sp' : 'State-Sel',
        'state_rb' : 'State-Sts',
        }

    @classmethod
    def get_database(cls,prefix=''):
        db = dict()
        p = prefix
        db[p + 'State-Sel']     = {'type' : 'enum', 'enums':cls._states, 'value':0}
        db[p + 'State-Sts']     = {'type' : 'enum', 'enums':cls._states, 'value':0}
        for i in range(cls._ClassSim._NR_INTERNAL_OPT_CHANNELS):
            p = prefix + 'OPT{0:02d}'.format(i)
            db.update(_OpticChannelIOC.get_database(p))
        for out in range(cls._ClassSim._NR_OUT_CHANNELS):
            p = prefix + 'OUT{0:d}'.format(out)
            db.update(cls._ClassTrigIOC.get_database(p))
        return db

    def __init__(self, base_freq, callbacks = None, prefix = None, controller = None):
        self._attr2expr = {
            'state_sp' : lambda x: int(x),
            'state_rb' : lambda x: x,
            }
        if controller is None: controller = self._ClassSim(base_freq)
        super().__init__(controller, callbacks = callbacks, prefix = prefix)

        self.optic_channels = dict()
        for i in range(self._ClassSim._NR_INTERNAL_OPT_CHANNELS):
            name = 'OPT{0:02d}'.format(i)
            cntler = self._controller.optic_channels[i]
            self.optic_channels[name] = _OpticChannelIOC(self.base_freq,
                                                        callbacks = {self.uuid:self._ioc_callback},
                                                        prefix = name,
                                                        controller = cntler)
        self.trigger_outputs = dict()
        for i in range(self._ClassSim._NR_OUT_CHANNELS):
            name = 'OUT{0:d}'.format(i)
            cntler = self._controller.trigger_outputs[i]
            self.trigger_outputs[name] = self._ClassTrigIOC(self.base_freq,
                                                            callbacks = {self.uuid:self._ioc_callback},
                                                            prefix = name,
                                                            controller = cntler)

    def _ioc_callback(self,propty,value, **kwargs):
        self._call_callbacks(propty, value, **kwargs)

    def _callback(self,propty,value,**kwargs):
        if propty == 'state':
            self.state_rb = value

    def get_propty(self, reason):
        reason2 = reason[len(self.prefix):]
        if reason2.startswith(tuple(self.trigger_outputs.keys())):
            return self.trigger_outputs[reason2[:4]].get_propty(reason2)#Not general enough
        elif reason2.startswith(tuple(self.optic_channels.keys())):
            return self.optic_channels[reason2[:5]].get_propty(reason2)#Absolutely not general enough
        else:
            return super().get_propty(reason)

    def set_propty(self, reason, value):
        reason2 = reason[len(self.prefix):]
        if reason2.startswith(tuple(self.trigger_outputs.keys())):
            return self.trigger_outputs[reason2[:4]].set_propty(reason2, value)#Not general enough
        elif reason2.startswith(tuple(self.optic_channels.keys())):
            return self.optic_channels[reason2[:5]].set_propty(reason2, value)#Absolutely not general enough
        else:
            return super().set_propty(reason, value)

    def receive_events(self, bucket, events):
        return { self.prefix : self._controller.receive_events(bucket, events) }


class EVEIOC(EVRIOC):
    _ClassSim = _EVESim
    _ClassTrigIOC = _EVETriggerIOC


class AFCIOC(EVRIOC):
    _ClassSim = _AFCSim
    _ClassTrigIOC = _OpticChannelIOC
