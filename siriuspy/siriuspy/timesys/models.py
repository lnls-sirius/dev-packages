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


class EventSim(CallBack):

    def __init__(self,base_freq,callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._delay_type = None
        self._delay = 0
        self._mode = 0

    @property
    def delay(self):
        return self._delay
    @delay.setter
    def delay(self,value):
        self._delay = value
        self._call_callbacks('delay',value)

    @property
    def mode(self):
        return self._mode
    @mode.setter
    def mode(self,value):
        self._mode = value
        self._call_callbacks('mode',value)

    @property
    def delay_type(self):
        return self._delay_type
    @delay_type.setter
    def delay_type(self,value):
        self._delay_type = value
        self._call_callbacks('delay_type',value)

    def get_base_freq(self):
        return self.base_freq

    def generate(self):
        if self._mode > 0:
            return {'delay':self._delay/self.base_freq}


class EventIOC(CallBack):

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
        super().__init__(callbacks, prefix = prefix)
        self._uuid = _uuid.uuid4()
        self._base_freq = base_freq
        if controller is None:
            self._controller = EventSim(self.base_freq, {self._uuid:self._callback})
        else:
            self._controller = controller
            self._controller.add_callback({self._uuid:self._callback})
            self.base_freq = self._controller.get_base_freq()
        self._delay_sp = None
        self._delay_rb = None
        self._mode_sp = None
        self._mode_rb = None
        self._delay_type_sp = None
        self._delay_type_rb = None
        self._set_init_values()

    def _set_init_values(self):
        db = self.get_database()
        self._delay_sp = db['Delay-SP']['value']
        self._delay_rb = db['Delay-RB']['value']
        self._mode_sp = db['Mode-Sel']['value']
        self._mode_rb = db['Mode-Sts']['value']
        self._delay_type_sp = db['DelayType-Sel']['value']
        self._delay_type_rb = db['DelayType-Sts']['value']

    @property
    def delay_sp(self):
        return self._delay_sp
    @delay_sp.setter
    def delay_sp(self,value):
        self._delay_sp = value
        self._controller.delay = round( value * self._base_freq) #integer
        self._call_callbacks('Delay-SP',value)

    @property
    def delay_rb(self):
        return self._delay_rb
    @delay_rb.setter
    def delay_rb(self,value):
        self._delay_rb = value * (1/self._base_freq)
        self._call_callbacks('Delay-RB',self._delay_rb)

    @property
    def mode_sp(self):
        return self._mode_sp
    @mode_sp.setter
    def mode_sp(self,value):
        if value <len(self._modes):
            self._mode_sp = value
            self._controller.mode = value
            self._call_callbacks('Mode-Sel',value)

    @property
    def mode_rb(self):
        return self._mode_rb
    @mode_rb.setter
    def mode_rb(self,value):
        if value <len(self._modes):
            self._mode_rb = value
            self._call_callbacks('Mode-Sts',value)

    @property
    def delay_type_sp(self):
        return self._delay_type_sp
    @delay_type_sp.setter
    def delay_type_sp(self,value):
        if value <len(self._delay_types):
            self._delay_type_sp = value
            self._controller.delay_type = value
            self._call_callbacks('DelayType-Sel',value)

    @property
    def delay_type_rb(self):
        return self._delay_type_rb
    @delay_type_rb.setter
    def delay_type_rb(self,value):
        if value <len(self._delay_types):
            self._delay_type_rb = value
            self._call_callbacks('DelayType-Sts',value)

    def _callback(self,propty,value,**kwargs):
        if propty == 'delay':
            self.delay_rb = value
        if propty == 'mode':
            self.mode_rb = value
        if propty == 'delay_type':
            self.delay_type_rb = value

    def get_propty(self,reason):
        reason = reason[len(self.prefix):]
        if reason  == 'Mode-Sel':
            return self.mode_sp
        elif reason  == 'Mode-Sts':
            return self.mode_rb
        elif reason  == 'DelayType-Sel':
            return self.delay_type_sp
        elif reason  == 'DelayType-Sts':
            return self.delay_type_rb
        elif reason == 'Delay-SP':
            return self.delay_sp
        elif reason == 'Delay-RB':
            return self.delay_rb
        else:
            return None

    def set_propty(self,reason,value):
        reason = reason[len(self.prefix):]
        if reason  == 'Mode-Sel':
            self.mode_sp = value
        elif reason  == 'DelayType-Sel':
            self.delay_type_sp = value
        elif reason == 'Delay-SP':
            self.delay_sp = value
        else:
            return False
        return True


class ClockSim(CallBack):

    def __init__(self,callbacks=None):
        super().__init__(callbacks)
        self._frequency = 1
        self._state = 0

    @property
    def state(self):
        return self._state
    @state.setter
    def state(self,value):
        self._state = value
        self._call_callbacks('state',value)

    @property
    def frequency(self):
        return self._frequency
    @frequency.setter
    def frequency(self,value):
        self._frequency = value
        self._call_callbacks('frequency',value)

    def generate(self):
        if self._state > 0:
            return {'frequency':self.base_freq/self._frequency}


class ClockIOC(CallBack):

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
        super().__init__(callbacks, prefix = prefix)
        self._uuid = _uuid.uuid4()
        self._base_frequency = base_freq
        if controller is None:
            self._controller = ClockSim({self._uuid:self._callback})
        else:
            self._controller = controller
            self._controller.add_callback({self._uuid:self._callback})
        self._frequency_sp = None
        self._frequency_rb = None
        self._state_sp = None
        self._state_rb = None
        self._set_init_values()

    def _set_init_values(self):
        db = self.get_database()
        self._frequency_sp = db['Freq-SP']['value']
        self._frequency_rb = db['Freq-RB']['value']
        self._state_sp = db['State-Sel']['value']
        self._state_rb = db['State-Sts']['value']

    @property
    def frequency_sp(self):
        return self._frequency_sp
    @frequency_sp.setter
    def frequency_sp(self,value):
        self._frequency_sp = value
        self._controller.frequency = round(self._base_frequency / value) #integer
        self._call_callbacks('Freq-SP',value)

    @property
    def frequency_rb(self):
        return self._frequency_rb
    @frequency_rb.setter
    def frequency_rb(self,value):
        self._frequency_rb = value * self._base_frequency
        self._call_callbacks('Freq-RB',self._frequency_rb)

    @property
    def state_sp(self):
        return self._state_sp
    @state_sp.setter
    def state_sp(self,value):
        if value <len(self._states):
            self._state_sp = value
            self._controller.state = value
            self._call_callbacks('State-Sel',value)

    @property
    def state_rb(self):
        return self._state_rb
    @state_rb.setter
    def state_rb(self,value):
        if value <len(self._states):
            self._state_rb = value
            self._call_callbacks('State-Sts',value)

    def _callback(self, propty,value,**kwargs):
        if propty == 'frequency':
            self.frequency_rb = value
        if propty == 'state':
            self.state_rb = value

    def get_propty(self,reason):
        reason = reason[len(self.prefix):]
        if reason  == 'State-Sel':
            return self.state_sp
        elif reason  == 'State-Sts':
            return self.state_rb
        elif reason == 'Freq-SP':
            return self.frequency_sp
        elif reason == 'Freq-RB':
            return self.frequency_rb
        else:
            return None

    def set_propty(self,reason,value):
        reason = reason[len(self.prefix):]
        if reason  == 'State-Sel':
            self.state_sp = value
        elif reason == 'Freq-SP':
            self.frequency_sp = value
        else:
            return False
        return True


class EVGSim(CallBack):

    def __init__(self, callbacks= None):
        super().__init__(callbacks)
        self._continuous = 1
        self._injection = 0
        self._injection_callbacks = dict()
        self._cyclic_injection = 0
        self._single = 0
        self._single_callbacks = dict()
        self._bucket_list = _np.zeros(864)
        self._repetition_rate = 30
        self.events = list()
        for i in range(256):
            self.events.append(EventSim())
        self.clocks = list()
        for i in range(8):
            self.clocks.append(ClockSim())

    @property
    def continuous(self):
        return self._continuous
    @continuous.setter
    def continuous(self,value):
        self._continuous = value
        self._call_callbacks('continuous',value)

    @property
    def cyclic_injection(self):
        return self._cyclic_injection
    @cyclic_injection.setter
    def cyclic_injection(self,value):
        self._cyclic_injection = value
        self._call_callbacks('cyclic_injection',value)

    @property
    def bucket_list(self):
        return self._bucket_list
    @bucket_list.setter
    def bucket_list(self,value):
        self._bucket_list = value
        # self._call_callbacks('bucket_list',value)

    @property
    def repetition_rate(self):
        return self._repetition_rate
    @repetition_rate.setter
    def repetition_rate(self,value):
        self._repetition_rate = value
        self._call_callbacks('repetition_rate',value)

    ########### Functions related to Injection simulation #############
    @property
    def injection(self):
        return self._injection
    @injection.setter
    def injection(self,value):
        if value:
            if not self._injection and self._continuous:
                self._injection = value
                _threading.Thread(target=self._injection_fun).start()
        else:
            self._injection = value
        self._call_callbacks('injection',value)

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
    @property
    def single(self):
        return self._single
    @single.setter
    def single(self,value):
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


class EVGIOC(CallBack):

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
        db[p + 'BucketList'] = {'type' : 'int', 'count': 864, 'value':0}
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
        self._single_sp = None
        self._single_rb = None
        self._injection_sp = False
        self._injection_rb = False
        self._cyclic_injection_sp = None
        self._cyclic_injection_rb = None
        self._continuous_sp = None
        self._continuous_rb = None
        self._bucket_list = _np.zeros(864)
        self._repetition_rate_sp = None
        self._repetition_rate_rb = None
        self._set_init_values()

    def _set_init_values(self):
        db = self.get_database()
        self._single_sp = db['SingleState-Sel']['value']
        self._single_rb = db['SingleState-Sts']['value']
        self._injection_sp = db['InjectionState-Sel']['value']
        self._injection_rb = db['InjectionState-Sts']['value']
        self._cyclic_injection_sp = db['InjCyclic-Sel']['value']
        self._cyclic_injection_rb = db['InjCyclic-Sts']['value']
        self._continuous_sp = db['ContinuousState-Sel']['value']
        self._continuous_rb = db['ContinuousState-Sts']['value']
        self._repetition_rate_sp = db['RepRate-SP']['value']
        self._repetition_rate_rb = db['RepRate-RB']['value']
        self._bucket_list = _np.ones(864)*db['BucketList']['value']


    def _ioc_callback(self,propty,value, **kwargs):
        self._call_callbacks(propty, value, **kwargs)

    def _sim_callback(self,propty,value, **kwargs):
        if propty == 'continuous':
            self.continuous_rb = value
        elif propty == 'clyclic_injection':
            self.clyclic_injection_rb = value
        elif propty == 'bucket_list':
            if _np.any(value != self._bucket_list):
                self.bucket_list = value
                self._call_callbacks('BucketList',value)
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

    @property
    def continuous_sp(self):
        return self._continuous_sp
    @continuous_sp.setter
    def continuous_sp(self,value):
        if value <len(self._states):
            self._continuous_sp = value
            self._controller.continuous = value
            self._call_callbacks('ContinuousState-Sel',value)

    @property
    def continuous_rb(self):
        return self._continuous_rb
    @continuous_rb.setter
    def continuous_rb(self,value):
        if value <len(self._states):
            self._continuous_rb = value
            self._call_callbacks('ContinuousState-Sts',value)

    @property
    def injection_sp(self):
        return self._injection_sp
    @injection_sp.setter
    def injection_sp(self,value):
        if value <len(self._states):
            self._injection_sp = value
            self._controller.injection = value
            self._call_callbacks('InjectionState-Sel',value)

    @property
    def injection_rb(self):
        return self._injection_rb
    @injection_rb.setter
    def injection_rb(self,value):
        if value <len(self._states):
            self._injection_rb = value
            self._call_callbacks('InjectionState-Sts',value)

    @property
    def single_sp(self):
        return self._single_sp
    @single_sp.setter
    def single_sp(self,value):
        if value <len(self._states):
            self._single_sp = value
            self._controller.single = value
            self._call_callbacks('SingleState-Sel',value)

    @property
    def single_rb(self):
        return self._single_rb
    @single_rb.setter
    def single_rb(self,value):
        if value <len(self._states):
            self._single_rb = value
            self._call_callbacks('SingleState-Sts',value)

    @property
    def cyclic_injection_sp(self):
        return self._cyclic_injection_sp
    @cyclic_injection_sp.setter
    def cyclic_injection_sp(self,value):
        if value <len(self._states):
            self._cyclic_injection_sp = value
            self._controller.cyclic_injection = value
            self._call_callbacks('InjCyclic-Sel',value)

    @property
    def cyclic_injection_rb(self):
        return self._cyclic_injection_rb
    @cyclic_injection_rb.setter
    def cyclic_injection_rb(self,value):
        if value <len(self._states):
            self._cyclic_injection_rb = value
            self._call_callbacks('InjCyclic-Sts',value)

    @property
    def bucket_list(self):
        return self._bucket_list.tolist()
    @bucket_list.setter
    def bucket_list(self,value):
        for i in range(min(len(value),864)):
            if value[i]<=0: break
            self._bucket_list[i] = ((value[i]-1) % 864) + 1
        self._bucket_list[i:] = 0
        self._controller.bucket_list = value
        self._call_callbacks('BucketList',value)

    @property
    def repetition_rate(self):
        return self._repetition_rate
    @repetition_rate.setter
    def repetition_rate(self,value):
        n = round(60/value)
        n = n if n<60 else 60
        self._repetition_rate = 60 / n

    @property
    def repetition_rate_sp(self):
        return self._repetition_rate_sp
    @repetition_rate_sp.setter
    def repetition_rate_sp(self,value):
        self._repetition_rate_sp = value
        self._controller.repetition_rate = round(_PwrFreq / value) #integer
        self._call_callbacks('RepRate-SP',value)

    @property
    def repetition_rate_rb(self):
        return self._repetition_rate_rb
    @repetition_rate_rb.setter
    def repetition_rate_rb(self,value):
        self._repetition_rate_rb = value * _PwrFreq
        self._call_callbacks('RepRate-RB',self._repetition_rate_rb)

    def get_propty(self,reason):
        if reason  == 'SingleState-Sel':
            return self.single_sp
        elif reason  == 'SingleState-Sts':
            return self.single_rb
        elif reason == 'InjCyclic-Sel':
            return self.cyclic_injection_sp
        elif reason == 'InjCyclic-Sts':
            return self.cyclic_injection_rb
        elif reason == 'ContinuousState-Sel':
            return self.continuous_sp
        elif reason == 'ContinuousState-Sts':
            return self.continuous_rb
        elif reason == 'InjectionState-Sel':
            return self.injection_sp
        elif reason == 'InjectionState-Sts':
            return self.injection_rb
        elif reason == 'BucketList':
            return self.bucket_list
        elif reason == 'RepRate-SP':
            return self.repetition_rate_sp
        elif reason == 'RepRate-RB':
            return self.repetition_rate_rb
        elif reason.startswith(tuple(self.clocks.keys())):
            return self.clocks[reason[:6]].get_propty(reason)#Not general enough
        elif reason.startswith(tuple(self.events.keys())):
            return self.events[reason[:5]].get_propty(reason)#Absolutely not general enough
        else:
            return None

    def set_propty(self,reason,value):
        if reason  == 'SingleState-Sel':
            self.single_sp = value
        elif reason  == 'InjCyclic-Sel':
            self.cyclic_injection_sp = value
        elif reason == 'ContinuousState-Sel':
            self.continuous_sp = value
        elif reason == 'InjectionState-Sel':
            self.injection_sp = value
        elif reason == 'BucketList':
            self.bucket_list = value
        elif reason == 'RepRate-SP':
            self.repetition_rate_sp = value
        elif reason.startswith(tuple(self.clocks.keys())):
            return self.clocks[reason[:6]].set_propty(reason, value)#Not general enough
        elif reason.startswith(tuple(self.events.keys())):
            return self.events[reason[:5]].set_propty(reason, value)#Absolutely not general enough
        else:
            return False
        return True


class TriggerSim(CallBack):

    def __init__(self,base_freq,callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._optic_channel = 0
        self._delay = 0
        self._fine_delay = 0

    @property
    def fine_delay(self):
        return self._fine_delay
    @fine_delay.setter
    def fine_delay(self,value):
        self._fine_delay = value
        self._call_callbacks('fine_delay',value)

    @property
    def delay(self):
        return self._delay
    @delay.setter
    def delay(self,value):
        self._delay = value
        self._call_callbacks('delay',value)

    @property
    def optic_channel(self):
        return self._optic_channel
    @optic_channel.setter
    def optic_channel(self,value):
        self._optic_channel = value
        self._call_callbacks('optic_channel',value)

    def receive_events(self, events):
        lab = _OPT_LABEL_TEMPLATE.format(self._optic_channel)
        dic = events.get(lab,None)
        if dic is None: return
        dic['delay'] += self._delay/self.base_freq + self._fine_delay * _FINE_DELAY_STEP
        return dic


class EVRTriggerIOC(CallBack):

    _optic_channels = tuple(  [ _OPT_LABEL_TEMPLATE.format(i) for i in range(EVRSim._NR_INTERNAL_OPT_CHANNELS) ]  )

    @staticmethod
    def get_database(prefix=''):
        db = dict()
        db[prefix + 'FineDelay-SP']   = {'type' : 'float', 'unit':'ps', 'value': 0.0, 'prec': 0}
        db[prefix + 'FineDelay-RB']   = {'type' : 'float', 'unit':'ps', 'value': 0.0, 'prec': 0}
        db[prefix + 'Delay-SP']   = {'type' : 'float', 'unit':'us', 'value': 0.0, 'prec': 0}
        db[prefix + 'Delay-RB']   = {'type' : 'float', 'unit':'us', 'value': 0.0, 'prec': 0}
        db[prefix + 'OptCh-Sel']   = {'type' : 'enum', 'enums':EVRTriggerIOC._OptChs, 'value':0}
        db[prefix + 'OptCh-Sts']   = {'type' : 'enum', 'enums':EVRTriggerIOC._OptChs, 'value':0}
        return db

    def __init__(self, base_freq, callbacks = None, prefix = None, controller = None):
        super().__init__(callbacks, prefix = prefix)
        self._uuid = _uuid.uuid4()
        self._base_freq = base_freq
        if controller is None:
            self._controller = TriggerSim(self.base_freq, {self._uuid:self._callback})
        else:
            self._controller = controller
            self._controller.add_callback({self._uuid:self._callback})
        self._delay_sp = 0
        self._delay_rb = 0
        self._optic_channel_sp = 0
        self._optic_channel_rb = 0
        self._fine_delay_sp = 0
        self._fine_delay_rb = 0
        self._set_init_values()

    def _set_init_values(self):
        db = self.get_database()
        self._delay_sp = db['Delay-SP']['value']
        self._delay_rb = db['Delay-RB']['value']
        self._optic_channel_sp = db['OptCh-Sel']['value']
        self._optic_channel_rb = db['OptCh-Sts']['value']
        self._fine_delay_sp = db['FineDelay-SP']['value']
        self._fine_delay_rb = db['FineDelay-RB']['value']

    @property
    def fine_delay_sp(self):
        return self._fine_delay_sp
    @fine_delay_sp.setter
    def fine_delay_sp(self,value):
        self._fine_delay_sp = value
        self._controller.fine_delay = round(value / _FINE_DELAY_STEP ) #integer
        self._call_callbacks('FineDelay-SP',value)

    @property
    def fine_delay_rb(self):
        return self._fine_delay_rb
    @fine_delay_rb.setter
    def fine_delay_rb(self,value):
        self._fine_delay_rb = value * _FINE_DELAY_STEP
        self._call_callbacks('FineDelay-RB',self._fine_delay_rb)

    @property
    def delay_sp(self):
        return self._delay_sp
    @delay_sp.setter
    def delay_sp(self,value):
        self._delay_sp = value
        self._controller.delay = round(value * self._base_frequency ) #integer
        self._call_callbacks('Delay-SP',value)

    @property
    def delay_rb(self):
        return self._delay_rb
    @delay_rb.setter
    def delay_rb(self,value):
        self._delay_rb = value / self._base_frequency
        self._call_callbacks('Delay-RB',self._delay_rb)

    @property
    def optic_channel_sp(self):
        return self._optic_channel_sp
    @optic_channel_sp.setter
    def optic_channel_sp(self,value):
        if value <len(self._optic_channels):
            self._optic_channel_sp = value
            self._controller.optic_channel = value
            self._call_callbacks('OptCh-Sel',value)

    @property
    def optic_channel_rb(self):
        return self._optic_channel_rb
    @optic_channel_rb.setter
    def optic_channel_rb(self,value):
        if value <len(self._optic_channels):
            self._optic_channel_rb = value
            self._call_callbacks('OptCh-Sts',value)

    def _callback(self, propty,value,**kwargs):
        if propty == 'delay':
            self.delay_rb = value
        if propty == 'fine_delay':
            self.fine_delay_rb = value
        if propty == 'optic_channel':
            self.optic_channel_rb = value

    def get_propty(self,reason):
        reason = reason[len(self.prefix):]
        if reason  == 'OptCh-Sel':
            return self.optic_channel_sp
        elif reason  == 'OptCh-Sts':
            return self.optic_channel_rb
        elif reason == 'Delay-SP':
            return self.delay_sp
        elif reason == 'Delay-RB':
            return self.delay_rb
        elif reason == 'FineDelay-SP':
            return self.fine_delay_sp
        elif reason == 'FineDelay-RB':
            return self.fine_delay_rb
        else:
            return None

    def set_propty(self,reason,value):
        reason = reason[len(self.prefix):]
        if reason  == 'OptCh-Sel':
            self.optic_channel_sp = value
        elif reason == 'Delay-SP':
            self.delay_sp = value
        elif reason == 'FineDelay-SP':
            self.fine_delay_sp = value
        else:
            return False
        return True

class EVETriggerIOC(EVRTriggerIOC):
    _optic_channels = tuple(  [ _OPT_LABEL_TEMPLATE.format(i) for i in range(EVRSim._NR_INTERNAL_OPT_CHANNELS) ]  )

##hele

class OpticChannelSim(CallBack):

    def __init__(self,base_freq,callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self._state = 0
        self._width = 0
        self._delay = 0
        self._polarity = 0
        self._event = 0
        self._pulses = 1

    @property
    def state(self):
        return self._state
    @state.setter
    def state(self,value):
        self._state = value
        self._call_callbacks('state',value)

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self,value):
        self._width = value
        self._call_callbacks('width',value)

    @property
    def delay(self):
        return self._delay
    @delay.setter
    def delay(self,value):
        self._delay = value
        self._call_callbacks('delay',value)

    @property
    def polarity(self):
        return self._polarity
    @polarity.setter
    def polarity(self,value):
        self._polarity = value
        self._call_callbacks('polarity',value)

    @property
    def event(self):
        return self._event
    @event.setter
    def event(self,value):
        self._event = value
        self._call_callbacks('event',value)

    @property
    def pulses(self):
        return self._pulses
    @pulses.setter
    def pulses(self,value):
        self._pulses = value
        self._call_callbacks('pulses',value)

    def receive_events(self, events):
        if self._state == 0: return
        lab = _EVENT_LABEL_TEMPLATE.format(self._event)
        ev = events.get(lab,None)
        if ev is None: return
        delay = ev['delay'] + self._delay/self.base_freq
        return dict(  { 'pulses':self._pulses, 'width':self._width/self.base_freq, 'delay':delay }  )

class EVRSim(CallBack):

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

    @property
    def state(self):
        return self._state
    @state.setter
    def state(self,value):
        self._state = value
        self._call_callbacks('state',value)

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
            triggers.append(tri_ch.deal_with_opt_ch(opt_out))
        return triggers


class EVESim(EVRSim):

    _NR_INTERNAL_OPT_CHANNELS = 16
    _NR_OPT_CHANNELS_OUT = 0
