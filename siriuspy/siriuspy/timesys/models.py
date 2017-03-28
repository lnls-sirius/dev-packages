import uuid as _uuid
import numpy as _np
import threading as _threading
import time as _time

_EventMapping = {'Linac':0, 'InjBO':1,  'InjSI':2,  'RmpBO':3,
                 'RmpSI':4, 'DigLI':5,  'DigTB':6,  'DigBO':7,
                 'DigTS':8, 'DigSI':9}
_PwrFreq = 60
_FINE_DELAY_STEP = 5e-12

_EVENT_LABEL_TEMPLATE = 'Ev{0:02x}'
_CLOCK_LABEL_TEMPLATE = 'Cl{0:1d}'
_OPT_LABEL_TEMPLATE   = 'OPT{0:2d}'
_OUT_LABEL_TEMPLATE   = 'OUT{0:1d}'

class CallBack:

    def __init__(self, callbacks=None, prefix = None):
        self.prefix = prefix or ''
        self._callbacks = dict(callbacks) if callbacks else dict()

    def _callback(self,propty,value,**kwargs):
        return NotImplemented()

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


class BaseIOC(CallBack):

    @staticmethod
    def get_database(prefix=''):
        db = dict()
        return NotImplemented() #return db

    def __init__(self, callbacks = None, prefix = None):
        super().__init__(callbacks, prefix = prefix)
        self._uuid = _uuid.uuid4()
        self._attr2pvname = {} ## fill here this way: {'fine_delay_sp':   'FineDelay-SP'}
        self._attr2expr  = {} ## must be filled
        self._pvname2attr = { value:key for key,value in self._attr2pvname.items() }
        self._set_init_values()

    def _attribute_expression(self, attri, value):
        return self._attr2expr[attri](value)

    def __getattr__(self,name):
        if name in self._attr2pvname.keys():
            return self.__dict__['_'+name]
        raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__,name))

    def __setattr__(self,name,value):
        if name not in self._attr2pvname.keys():
            raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__,name))
        if name.endswith(('_sp','_sel')):
            self._controller.__setattr__(name[:-3], self._attribute_expression(value))
            self.__dict__['_'+name] = value
            self._call_callbacks(self._attr2pvname[name],value)

    def _set_init_values(self):
        db = self.get_database()
        for attr,pv in self._attr2pvname.items():
            self.__dict__['_'+name] = db[pv]['value']

    def _callback(self, propty,value,**kwargs):
        return NotImplemented()

    def get_propty(self,reason):
        reason = reason[len(self.prefix):]
        if reason not in self._pvname2attr.keys():
            return None
        return self.__getattr__(self._pvname2attr[reason])

    def set_propty(self,reason,value):
        reason = reason[len(self.prefix):]
        if reason not in self._pvname2attr.keys() and reason.endswith(('-RB','-Sts')):
            return False
        self.__setattr__(self._pvname2attr[reason],value)
        return True


class BaseSim(CallBack):

    _attributes = {'fine_delay','delay','optic_channel'}

    def __init__(self,callbacks=None):
        super().__init__(callbacks)

    def __getattr__(self,name):
        if name in self._attributes:
            return self.__dict__['_'+name]
        raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__,name))

    def __setattr__(self,name,value):
        if name not in self._attributes:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__,name))
        self.__dict__['_'+name] = value
        self._call_callbacks(name,value)


class EVGSim(BaseSim):

    _attributes = {'continuous','cyclic_injection','bucket_list','repetition_rate','injection','single'}

    def __init__(self, callbacks= None):
        super().__init__(callbacks)
        self._continuous = 1
        self._injection = 0
        self._injection_callbacks = dict()
        self._cyclic_injection = 0
        self._single = 0
        self._single_callbacks = dict()
        self._bucket_list = [0.0]*864
        self._repetition_rate = 30
        self.events = list()
        for i in range(256):
            self.events.append(EventSim())
        self.clocks = list()
        for i in range(8):
            self.clocks.append(ClockSim())

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
                    for callback in self._single_callbacks.values():
                        callback(evnts)
            else:
                self._single = value
            self._call_callbacks('single',value)
        else:
            super().__setattr__(attr,value)

    ######################################################################
    ########### Functions related to Single Pulse simulation #############
    def add_injection_callback(self,uuid,callback):
        self._injection_callbacks.update({uuid:callback})

    def remove_injection_callback(self,uuid):
        self._injection_callbacks.pop(uuid, None)

    def _injection_fun(self):
        while True:
            for i in self._bucket_list:
                if not self._can_inject(): return
                if i<=0: break
                evnts = self._generate_events((1,2))
                for callback in self._injection_callbacks.values():
                    callback(i,evnts)
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
            if not ev.mode in tables: continue
            dic = ev.generate()
            if not dic: continue
            lab = _EVENT_LABEL_TEMPLATE.format(i)
            events.update(  { lab : dic }  )
        for i, cl in enumerate(self.clocks):
            dic = cl.generate()
            if not dic: continue
            lab = _CLOCK_LABEL_TEMPLATE.format(i)
            events.update(  { lab : dic }  )
        return events


class EVGIOC(BaseIOC):

    _states = ('Dsbl','Enbl')
    _cyclic_types = ('Off','On')

    @staticmethod
    def get_database(prefix=''):
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
            p = prefix + 'Clock{0:d}'.format(i)
            db.update(ClockIOC.get_database(p))
        for evnt in _EventMapping.keys():
            p = prefix + evnt
            db.update(EventIOC.get_database(p))

        return db

    def __init__(self, base_freq, callbacks = None, prefix = None, controller = None):
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
        _attr2expr = {
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
        super().__init__(callbacks = callbacks, prefix = prefix)
        self._uuid = _uuid.uuid4()
        self._base_freq = base_freq
        if controller is None:
            self._controller = EVGSim({self._uuid:self._sim_callback})
        else:
            self._controller = controller
            self._controller.add_callback({self._uuid:self._sim_callback})
        self.events = dict()
        for i,ev in enumerate(sorted(_EventMapping.keys())):
            cntler = self._controller.events[i]
            self.events[ev] = EventIOC(self._base_freq/4,
            callbacks = {self._uuid:self._ioc_callback},
            prefix = ev,
            controller = cntler)
        self.clocks = dict()
        for i in range(8):
            name = 'Clock{0:d}'.format(i)
            cntler = self._controller.clocks[i]
            self.clocks[name] = ClockIOC(self._base_freq/4,
            callbacks = {self._uuid:self._ioc_callback},
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
        self._bucket_list_sp = 864*[db['BucketList-SP']['value']]
        self._bucket_list_rb = 864*[db['BucketList-RB']['value']]


    def _ioc_callback(self,propty,value, **kwargs):
        self._call_callbacks(propty, value, **kwargs)

    def _sim_callback(self,propty,value, **kwargs):
        if propty == 'continuous':
            self.continuous_rb = value
        elif propty == 'clyclic_injection':
            self.clyclic_injection_rb = value
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

    def get_propty(self,reason):
        if reason.startswith(tuple(self.clocks.keys())):
            return self.clocks[reason[:6]].get_propty(reason)#Not general enough
        elif reason.startswith(tuple(self.events.keys())):
            return self.events[reason[:5]].get_propty(reason)#Absolutely not general enough
        else:
            return super().get_propty(reason)

    def set_propty(self,reason,value):
        if reason.startswith(tuple(self.clocks.keys())):
            return self.clocks[reason[:6]].set_propty(reason, value)#Not general enough
        elif reason.startswith(tuple(self.events.keys())):
            return self.events[reason[:5]].set_propty(reason, value)#Absolutely not general enough
        else:
            return super().set_propty(reason)


class EventSim(BaseSim):

    _attributes = {'delay','mode','delay_type',}

    def __init__(self,base_freq,callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._delay_type = None
        self._delay = 0
        self._mode = 0

    def get_base_freq(self):
        return self.base_freq

    def generate(self):
        if self._mode > 0:
            return {'delay':self._delay/self.base_freq}


class EventIOC(BaseIOC):


    _modes = ('Disabled','Continuous','Injection','Single')
    _delay_types = ('Fixed','Incr')

    @staticmethod
    def get_database(prefix=''):
        db = dict()
        db[prefix + 'Delay-SP']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us', 'prec': 3}
        db[prefix + 'Delay-RB']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us','prec': 3}
        db[prefix + 'Mode-Sel']      = {'type' : 'enum', 'enums':EventIOC._modes, 'value':1}
        db[prefix + 'Mode-Sts']      = {'type' : 'enum', 'enums':EventIOC._modes, 'value':1}
        db[prefix + 'DelayType-Sel'] = {'type' : 'enum', 'enums':EventIOC._delay_types, 'value':1}
        db[prefix + 'DelayType-Sts'] = {'type' : 'enum', 'enums':EventIOC._delay_types, 'value':1}
        return db

    def __init__(self,base_freq,callbacks = None, prefix = None, controller = None):
        _attr2pvname = {
            'delay_sp':'Delay-SP',
            'delay_rb':'Delay-RB',
            'mode_sp':'Mode-Sel',
            'mode_rb':'Mode-Sts',
            'delay_type_sp':'DelayType-Sel',
            'delay_type_rb':'DelayType-Sts',
            }
        self._attr2expr  = {
            'delay_sp': lambda x: int(round( value * self._base_freq)),
            'delay_rb': lambda x: x * (1/self._base_freq),
            'mode_sp': lambda x: int(x),
            'mode_rb': lambda x: x,
            'delay_type_sp': lambda x: int(x),
            'delay_type_rb': lambda x: x,
            }
        super().__init__(callbacks, prefix = prefix)
        self._base_freq = base_freq
        if controller is None:
            self._controller = EventSim(self.base_freq, {self._uuid:self._callback})
        else:
            self._controller = controller
            self._controller.add_callback({self._uuid:self._callback})
            self.base_freq = self._controller.get_base_freq()

    def _callback(self,propty,value,**kwargs):
        if propty == 'delay':
            self.delay_rb = value
        if propty == 'mode':
            self.mode_rb = value
        if propty == 'delay_type':
            self.delay_type_rb = value


class ClockSim(BaseSim):

    _attributes = {'state','frequency'}

    def __init__(self,callbacks=None):
        super().__init__(callbacks)
        self._frequency = 1
        self._state = 0

    def generate(self):
        if self._state > 0:
            return {'frequency':self.base_freq/self._frequency}


class ClockIOC(BaseIOC):

    _states = ('Dsbl','Enbl')

    @staticmethod
    def get_database(prefix=''):
        db = dict()
        db[prefix + 'Freq-SP']   = {'type' : 'float', 'count': 1, 'value': 1.0, 'prec': 10}
        db[prefix + 'Freq-RB']   = {'type' : 'float', 'count': 1, 'value': 1.0, 'prec': 10}
        db[prefix + 'State-Sel'] = {'type' : 'enum', 'enums':ClockIOC._states, 'value':0}
        db[prefix + 'State-Sts'] = {'type' : 'enum', 'enums':ClockIOC._states, 'value':0}
        return db

    def __init__(self, base_freq, callbacks = None, prefix = None, controller = None):
        self._attr2pvname = {
            'frequency_sp' :'Freq-SP',
            'frequency_rb' :'Freq-RB',
            'state_sp' :'State-Sel',
            'state_rb' :'State-Sts',
            }
        self._attr2expr  = {
            'frequency_sp': lambda x: int( round(self._base_frequency / value) ),
            'frequency_rb': lambda x: x * self._base_freq,
            'state_sp': lambda x: int(x),
            'state_rb': lambda x: x,
            }
        super().__init__(callbacks, prefix = prefix)
        self._base_freq = base_freq
        if controller is None:
            self._controller = ClockSim({self._uuid:self._callback})
        else:
            self._controller = controller
            self._controller.add_callback({self._uuid:self._callback})

    def _callback(self, propty,value,**kwargs):
        if propty == 'frequency':
            self.frequency_rb = value
        if propty == 'state':
            self.state_rb = value


class EVRSim(BaseSim):

    _attributes = {'state'}

    _NR_INTERNAL_OPT_CHANNELS = 24
    _NR_OPT_CHANNELS_OUT = 12

    def __init__(self, base_freq, callbacks= None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._state = 1
        self.optic_channels = list()
        for i in range(self._NR_INTERNAL_OPT_CHANNELS):
            self.optic_channels[i] = OpticChannelSim(self.base_freq)
        self.trigger_outputs = list()
        for i in range(8):
            self.trigger_outputs[i] = TriggerOutputSim(self.base_freq)

    def receive_events(self,events):
        opt_out = dict()
        triggers = dict()
        for i, opt_ch in enumerate(self.optic_channels):
            opt = opt_ch.receive_events(events)
            if opt is None: continue
            lab = _OPT_LABEL_TEMPLATE.format(i)
            opt_out.update( {lab:opt} )
            if i < _NR_OPT_CHANNELS_OUT: triggers.update( {lab:opt} )
        for tri_ch in self.trigger_outputs:
            triggers.append(tri_ch.receive_optical_channels(opt_out))
        return triggers


class EVESim(EVRSim):

    _NR_INTERNAL_OPT_CHANNELS = 16
    _NR_OPT_CHANNELS_OUT = 0


class EVRIOC(BaseIOC):
        _states = ('Dsbl','Enbl')
        _cyclic_types = ('Off','On')

        @staticmethod
        def get_database(prefix=''):
            db = dict()
            p = prefix
            db[p + 'State-Sel']     = {'type' : 'enum', 'enums':EVRIOC._states, 'value':0}
            db[p + 'State-Sts']     = {'type' : 'enum', 'enums':EVRIOC._states, 'value':0}
            for i in range(EVRSim._NR_INTERNAL_OPT_CHANNELS):
                p = prefix + 'OPT{0:02d}'.format(i)
                db.update(OpticChannelIOC.get_database(p))
            for out in range(8):
                p = prefix + 'OUT{0:d}'.format(out)
                db.update(EVRTriggerIOC.get_database(p))
            return db

        def __init__(self, base_freq, callbacks = None, prefix = None, controller = None):
            _attr2pvname = {
                'state_sp' : 'State-Sel',
                'state_rb' : 'State-Sts',
                }
            _attr2expr = {
                'state_sp' : lambda x: int(x),
                'state_rb' : lambda x: x,
                }
            super().__init__(callbacks = callbacks, prefix = prefix)
            self._uuid = _uuid.uuid4()
            self._base_freq = base_freq
            if controller is None:
                self._controller = EVRSim({self._uuid:self._sim_callback})
            else:
                self._controller = controller
                self._controller.add_callback({self._uuid:self._sim_callback})
            self.optic_channels = dict()
            for i in range(EVRSim._NR_INTERNAL_OPT_CHANNELS):
                name = 'OPT{0:02d}'.format(i)
                cntler = self._controller.events[i]
                self.events[ev] = EventIOC(self._base_freq/4,
                                           callbacks = {self._uuid:self._ioc_callback},
                                           prefix = ev,
                                           controller = cntler)
            self.clocks = dict()
            for i in range(8):
                name = 'Clock{0:d}'.format(i)
                cntler = self._controller.clocks[i]
                self.clocks[name] = ClockIOC(self._base_freq/4,
                                             callbacks = {self._uuid:self._ioc_callback},
                                             prefix = name,
                                             controller = cntler)

        def _ioc_callback(self,propty,value, **kwargs):
            self._call_callbacks(propty, value, **kwargs)

        def _sim_callback(self,propty,value, **kwargs):
            if propty == 'continuous':
                self.continuous_rb = value
            elif propty == 'clyclic_injection':
                self.clyclic_injection_rb = value
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

        def get_propty(self,reason):
            if reason.startswith(tuple(self.clocks.keys())):
                return self.clocks[reason[:6]].get_propty(reason)#Not general enough
            elif reason.startswith(tuple(self.events.keys())):
                return self.events[reason[:5]].get_propty(reason)#Absolutely not general enough
            else:
                return super().get_propty(reason)

        def set_propty(self,reason,value):
            if reason.startswith(tuple(self.clocks.keys())):
                return self.clocks[reason[:6]].set_propty(reason, value)#Not general enough
            elif reason.startswith(tuple(self.events.keys())):
                return self.events[reason[:5]].set_propty(reason, value)#Absolutely not general enough
            else:
                return super().set_propty(reason)


class TriggerSim(BaseSim):

    _attributes = {'fine_delay','delay','optic_channel'}

    def __init__(self,base_freq,callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._optic_channel = 0
        self._delay = 0
        self._fine_delay = 0

    def receive_optical_channels(self, opts):
        lab = _OPT_LABEL_TEMPLATE.format(self._optic_channel)
        dic = opts.get(lab,None)
        if dic is None: return
        dic['delay'] += self._delay/self.base_freq + self._fine_delay * _FINE_DELAY_STEP
        return dic


class EVRTriggerIOC(BaseIOC):

    _optic_channels = tuple(  [ _OPT_LABEL_TEMPLATE.format(i) for i in range(EVRSim._NR_INTERNAL_OPT_CHANNELS) ]  )

    @staticmethod
    def get_database(prefix=''):
        db = dict()
        db[prefix + 'FineDelay-SP']   = {'type' : 'float', 'unit':'ps', 'value': 0.0, 'prec': 0}
        db[prefix + 'FineDelay-RB']   = {'type' : 'float', 'unit':'ps', 'value': 0.0, 'prec': 0}
        db[prefix + 'Delay-SP']   = {'type' : 'float', 'unit':'us', 'value': 0.0, 'prec': 0}
        db[prefix + 'Delay-RB']   = {'type' : 'float', 'unit':'us', 'value': 0.0, 'prec': 0}
        db[prefix + 'OptCh-Sel']   = {'type' : 'enum', 'enums':EVRTriggerIOC._optic_channels, 'value':0}
        db[prefix + 'OptCh-Sts']   = {'type' : 'enum', 'enums':EVRTriggerIOC._optic_channels, 'value':0}
        return db

    def __init__(self, base_freq, callbacks = None, prefix = None, controller = None):
        _attr2pvname = {
            'fine_delay_sp':    'FineDelay-SP',
            'fine_delay_rb':    'FineDelay-RB',
            'delay_sp':         'Delay-SP',
            'delay_rb':         'Delay-RB',
            'optic_channel_sp': 'OptCh-Sel',
            'optic_channel_rb': 'OptCh-Sts',
            }
        _attr2expr  = {
            'fine_delay_sp':    lambda x: int(round(x / _FINE_DELAY_STEP )),
            'fine_delay_rb':    lambda x: x * _FINE_DELAY_STEP,
            'delay_sp':         lambda x: int(round(value * self._base_freq)),
            'delay_rb':         lambda x: x / self._base_freq,
            'optic_channel_sp': lambda x: int(x),
            'optic_channel_rb': lambda x: x,
            }
        super().__init__(callbacks, prefix = prefix)
        self._base_freq = base_freq
        if controller is None:
            self._controller = TriggerSim(self.base_freq, {self._uuid:self._callback})
        else:
            self._controller = controller
            self._controller.add_callback({self._uuid:self._callback})

    def _callback(self, propty,value,**kwargs):
        if propty == 'delay':
            self.delay_rb = value
        if propty == 'fine_delay':
            self.fine_delay_rb = value
        if propty == 'optic_channel':
            self.optic_channel_rb = value


class EVETriggerIOC(EVRTriggerIOC):
    _optic_channels = tuple(  [ _OPT_LABEL_TEMPLATE.format(i) for i in range(EVESim._NR_INTERNAL_OPT_CHANNELS) ]  )


class OpticChannelSim(BaseSim):

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

    def receive_events(self, events):
        if self._state == 0: return
        lab = _EVENT_LABEL_TEMPLATE.format(self._event)
        ev = events.get(lab,None)
        if ev is None: return
        delay = ev['delay'] + self._delay/self.base_freq
        return dict(  { 'pulses':self._pulses, 'width':self._width/self.base_freq, 'delay':delay }  )
