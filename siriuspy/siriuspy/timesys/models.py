import uuid as _uuid


class CallBack:

    def __init__(self, callbacks=None):
        if callbacks: self._callbacks = dict(callbacks)

    def _callback(self,propty,value,**kwargs):
        return NotImplemented()

    def _call_callbacks(self, propty, value, **kwargs):
        for uuid, callback in self._callbacks.items():
            callback(propty, value, **kwargs)

    def add_callback(self,uuid, callback):
        self._callbacks[uuid] = callback

    def remove_callback(self,uuid):
        self._callbacks.pop(uuid)


class EventSim(CallBack):


    def __init__(self,callbacks):
        super().__init__(self,callbacks)
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


class EventIOC(CallBack):


    _modes = ('Disabled','Continuous','Injection','Single')
    _delay_types = ('Fixed','Incr')

    @staticmethod
    def get_database(prefix):
        db = dict()
        db[prefix + 'Delay-SP']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us', 'prec': 3}
        db[prefix + 'Delay-RB']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'unit':'us','prec': 3}
        db[prefix + 'Mode-Sel']      = {'type' : 'enum', 'enums':Event._modes, 'value':1}
        db[prefix + 'Mode-Sts']      = {'type' : 'enum', 'enums':Event._modes, 'value':1}
        db[prefix + 'DelayType-Sel'] = {'type' : 'enum', 'enums':Event._delay_types, 'value':1}
        db[prefix + 'DelayType-Sts'] = {'type' : 'enum', 'enums':Event._delay_types, 'value':1}
        return db

    def __init__(self,name,base_freq,callbacks = None, controller = None):
        super().__init__(self,callbacks)
        self._uuid = _uuid.uuid4()
        self._base_frequency = base_freq
        if controller is None: self._controller = EventSim({self._uuid:self._callback})
        self.name = name
        self._mode = None
        self._delay_type = None
        self._delay_sp = None
        self._delay_rb = None
        self._mode_sp = None
        self._mode_rb = None
        self._delay_type_sp = None
        self._delay_type_rb = None

    @property
    def delay_sp(self):
        return self._delay_sp
    @delay_sp.setter
    def delay_sp(self,value):
        self._delay_sp = value
        self._controller.delay = round(value * self._base_frequency) #integer
        self._call_callbacks(self.name+'Delay-SP',value)

    @property
    def delay_rb(self):
        return self._delay_rb
    @delay_rb.setter
    def delay_rb(self,value):
        self._delay_rb = value * (1/self._base_frequency)
        self._call_callbacks(self.name+'Delay-RB',self._delay_rb)

    @property
    def mode_sp(self):
        return self._mode_sp
    @mode_sp.setter
    def mode_sp(self,value):
        if value <len(self._modes):
            self._mode_sp = value
            self._controller.mode = value
            self._call_callbacks(self.name+'Mode-Sel',value)

    @property
    def mode_rb(self):
        return self._mode_rb
    @mode_rb.setter
    def mode_rb(self,value):
        if value <len(self._modes):
            self._mode_rb = value
            self._call_callbacks(self.name+'Mode-Sts',value)

    @property
    def delay_type_sp(self):
        return self._delay_type_sp
    @delay_type_sp.setter
    def delay_type_sp(self,value):
        if value <len(self._delay_types):
            self._delay_type_sp = value
            self._controller.delay_type = value
            self._call_callbacks(self.name+'DelayType-Sel',value)

    @property
    def delay_type_rb(self):
        return self._delay_type_rb
    @delay_type_rb.setter
    def delay_type_rb(self,value):
        if value <len(self._delay_types):
            self._delay_type_rb = value
            self._call_callbacks(self.name+'DelayType-Sts',value)

    def _callback(propty,value,**kwargs):
        if propty == 'delay':
            self.delay_rb = value
        if propty == 'mode':
            self.mode_rb = value
        if propty == 'delay_type':
            self.delay_type_rb = value

    def get_propty(self,reason):
        reason = reason[len(self.name):]
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
        super().__init__(self,callbacks)
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
        self._frequency = frequency
        self._call_callbacks('frequency',value)


class ClockIOC(CallBack):

    _states = ('Dsbl','Enbl')

    @staticmethod
    def get_database(prefix):
        db = dict()
        db[prefix + 'Freq-SP']   = {'type' : 'float', 'count': 1, 'value': 0.0, 'prec': 10}
        db[prefix + 'Freq-RB']   = {'type' : 'float', 'count': 1, 'value': 0.0, 'prec': 10}
        db[prefix + 'State-Sel'] = {'type' : 'enum', 'enums':ClockIOC._states, 'value':1}
        db[prefix + 'State-Sts'] = {'type' : 'enum', 'enums':ClockIOC._states, 'value':1}
        return db

    def __init__(self,name, base_freq, callbacks = None, controller = None):
        super().__init__(self, callbacks)
        self.name = name
        self._uuid = _uuid.uuid4()
        self._base_frequency = base_freq
        if controller is None: self._controller = ClockSim({self._uuid:self._callback})
        self._frequency_sp = self._base_frequency
        self._frequency_rb = self._base_frequency
        self._state_sp = 0
        self._state_rb = 0

    @property
    def frequency_sp(self):
        return self._frequency_sp
    @frequency_sp.setter
    def frequency_sp(self,value):
        self._frequency_sp = value
        self._controller.frequency = round(self._base_frequency / value) #integer
        self._call_callbacks(self.name+'Freq-SP',value)

    @property
    def frequency_rb(self):
        return self._frequency_rb
    @frequency_rb.setter
    def frequency_rb(self,value):
        self._frequency_rb = value * self._base_frequency
        self._call_callbacks(self.name+'Freq-RB',self._frequency_rb)

    @property
    def state_sp(self):
        return self._state_sp
    @state_sp.setter
    def state_sp(self,value):
        if value <len(self._states):
            self._state_sp = value
            self._controller.state = value
            self._call_callbacks(self.name+'State-Sel',value)

    @property
    def state_rb(self):
        return self._state_rb
    @state_rb.setter
    def state_rb(self,value):
        if value <len(self._states):
            self._state_rb = value
            self._call_callbacks(self.name+'State-Sts',value)

    def _callback(propty,value,**kwargs):
        if propty == 'frequency':
            self.frequency_rb = value
        if propty == 'state':
            self.state_rb = value

    def get_propty(self,reason):
        reason = reason[len(self.name):]
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
        if reason  == 'State-Sel':
            self.state_sp = value
        elif reason == 'Freq-SP':
            self.frequency_sp = value
        else:
            return False
        return True


_EventMapping = {['Linac':0,  'InjBO':1,  'InjSI':2,  'RmpBO':3,
                  'RampSI':4, 'DigLI':5,  'DigTB':6,  'DigBO':7,
                  'DigTS':8,  'DigSI':9]}
_PwrFreq = 60

class EVGSim(CallBack):

    def __init__(self, callbacks):
        super().__init__(self,callbacks)
        self._frequency = None
        self._continuous = None
        self._injection = False
        self._injection_callbacks = dict()
        self._cyclic_injection = None
        self._single = None
        self._single_callbacks = dict()
        self._bucket_list = _np.zeros(864)
        self._repetition_rate = None
        self.events = dict()
        for i in range(len(_EventMapping.keys())):
            self.events[i] = EventSim()
        self.clocks = dict()
        for i in range(8):
            self.clocks[i] = ClockSim()

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
        self._call_callbacks('bucket_list',value)

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
            if not self._injection:
                self._injection = value
                _threading.Thread(target=self._injection_fun, kwargs={'callbacks':self._injection_callbacks}).start()
        else:
            self._injection = value
        self._call_callbacks('injection',value)

    def add_injection_callback(self,uuid,callback):
        self._injection_callbacks.update({uuid,callback})

    def remove_injection_callback(self,uuid):
        self._injection_callbacks.pop(uuid, None)

    def _injection_fun(self, callback):
        while True:
            for i in self.bucket_list:
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
        self._single_callbacks.update({uuid,callback})

    def remove_single_callback(self,uuid):
        self._single_callbacks.pop(uuid, None)
    ##########################################################################

    def _generate_events(self,tables):
        tables = tables if isinstance(tables,(list,tuple)) else (tables,)
        return [ev for ev in self.events.values() if ev.mode in tables]


class EVGIOC(CallBack):

    _states = ('Dsbl','Enbl')
    _cyclic_types = ('Off','On')

    @staticmethod:
    def get_database(prefix):
        db = dict()
        p = prefix
        db[p + 'SingleState-Sel']     = {'type' : 'enum', 'enums':EVG._states, 'value':0}
        db[p + 'SingleState-Sts']     = {'type' : 'enum', 'enums':EVG._states, 'value':0}
        db[p + 'InjectionState-Sel']  = {'type' : 'enum', 'enums':EVG._states, 'value':0}
        db[p + 'InjectionState-Sts']  = {'type' : 'enum', 'enums':EVG._states, 'value':0}
        db[p + 'InjCyclic-Sel']       = {'type' : 'enum', 'enums':EVG._cyclic_types, 'value':0}
        db[p + 'InjCyclic-Sts']       = {'type' : 'enum', 'enums':EVG._cyclic_types, 'value':0}
        db[p + 'ContinuousState-Sel'] = {'type' : 'enum', 'enums':EVG._states, 'value':1}
        db[p + 'ContinuousState-Sts'] = {'type' : 'enum', 'enums':EVG._states, 'value':1}
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

    def __init__(self, frequency, callbacks):
        supert().__init__(self, callbacks)
        self._uuid = _uuid.uuid4()
        self._base_frequency = base_freq
        if controller is None:
            self._controller = EVGSim({self._uuid:self._sim_callback})
            self.add_injection_callback    = self._controller.add_injection_callback
            self.remove_injection_callback = self._controller.remove_injection_callback
            self.add_single_callback       = self._controller.add_single_callback
            self.remove_single_callback    = self._controller.remove_single_callback
        self._frequency_sp = frequency
        self._frequency_rb = frequency
        self._single =
        self._continuous_sp = None
        self._continuous_rb = None
        self._cyclic_injection_sp = None
        self._cyclic_injection_rb = None
        self._bucket_list = _np.zeros(864)
        self._repetition_rate_sp = None
        self._repetition_rate_rb = None
        self._injection_sp = False
        self._injection_rb = False
        self.events = dict()
        for i,ev in enumerate(sorted(_EventMapping.keys())):
            cntler = self._controller.events[i]
            self.events[ev] = EventIOC(ev,self._frequency/4,{self._uuid:self._ioc_callback},controller = cntler)
        self.clocks = dict()
        for i in range(8):
            name = 'Clock{0:d}'.format(i)
            cntler = self._controller.clocks[i]
            self.clocks[name] = ClockIOC(name,self._frequency/4,{self._uuid:self._ioc_callback}, controller = cntler)

    def _ioc_callback(self,propty,value, **kwargs):
        for callback in self._call_callbacks.values():
            callback(propty,value, **kwargs)

    def _sim_callback(self,propty,value, **kwargs):
        if propty == 'continuous':
            self.continuous_rb = value
        elif propty == 'clyclic_injection':
            self.clyclic_injection_rb = value
        elif propty == 'bucket_list':
            if _np.any(value != self._bucket_list)
                self.bucket_list = value
                self._call_callbacks('BucketList',value)
        elif propty == 'repetition_rate':
            self.repetition_rate_rb = value
        elif propty == 'injection':
            self.injection_rb = value
            self._injection_sp = value
            self._call_callbacks('InjectionState-Sel',value)
        elif propty == 'single':
            self.single_rb = value
            self._single_sp = value
            self._call_callbacks('SingleState-Sel',value)

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
            return self.clocks[reason[:6]].get_propty(reason)#Absolutely not general enough
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
            return self.clocks[reason[:6]].set_propty(reason, value)#Absolutely not general enough
        else:
            return False
        return True
