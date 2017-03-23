
class CallBack:

    def __init__(self):
        self._callbacks = dict()

    def _callback(self,propty,value,**kwargs):
        self.call_callbacks(propty,value,**kwargs)

    def _call_callbacks(self, propty, value, **kwargs):
        for uuid, callback in self._callbacks.items():
            callback(propty, value, **kwargs)

    def add_callback(self,uuid, callback):
        self._callbacks[uuid] = callback

    def remove_callback(self,uuid):
        self._callbacks.pop(uuid)


class Event(CallBack):


    _modes = ('Disabled','Continuous','Injection','Single')
    _delay_types = ('Fixed','Incr')

    @staticmethod
    def get_database(prefix):
        db = dict()
        db[prefix + 'Delay-SP']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'prec': 10}
        db[prefix + 'Delay-RB']      = {'type' : 'float', 'count': 1, 'value': 0.0, 'prec': 10}
        db[prefix + 'Mode-Sel']      = {'type' : 'enum', 'enums':Event._modes, 'value':1}
        db[prefix + 'Mode-Sts']      = {'type' : 'enum', 'enums':Event._modes, 'value':1}
        db[prefix + 'DelayType-Sel'] = {'type' : 'enum', 'enums':Event._delay_types, 'value':1}
        db[prefix + 'DelayType-Sts'] = {'type' : 'enum', 'enums':Event._delay_types, 'value':1}
        return db

    def __init__(self,name):
        super().__init__(self)
        self.name = name
        self._mode = None
        self._delay_type = None
        self._delay = 0
        self.mode = 0
        self.delay_type = 1

    @property
    def delay(self):
        return self._delay
    @delay.setter
    def delay(self,value):
        self._delay = (value // 8) * 8  #must respect steps of 8 ns

    @property
    def mode(self):
        return self._modes.index(self._mode)
    @mode.setter
    def mode(self,value):
        if value <len(self._modes):
            self._mode = self._modes[value]

    @property
    def delay_type(self):
        return self._delay_types.index(self._delay_type)
    @delay_type.setter
    def delay_type(self,value):
        if value <len(self._delay_types):
            self._delay_type = self._delay_types[value]


class Clock(CallBack):

    @staticmethod
    def get_database(prefix):
        db = dict()
        db[prefix + 'Freq-SP']   = {'type' : 'float', 'count': 1, 'value': 0.0, 'prec': 10}
        db[prefix + 'Freq-RB']   = {'type' : 'float', 'count': 1, 'value': 0.0, 'prec': 10}
        db[prefix + 'State-Sel'] = {'type' : 'enum', 'enums':('Dsbl','Enbl'), 'value':1}
        db[prefix + 'State-Sts'] = {'type' : 'enum', 'enums':('Dsbl','Enbl'), 'value':1}
        return db

    def __init__(self,base_freq):
        super().__init__(self)
        self._base_frequency = base_freq
        self._frequency = self._base_frequency
        self._state = 'Enbl'
        self._states = ('Dsbl','Enbl')

    @property
    def state(self):
        return self._states.index(self._state)
    @state.setter
    def state(self,value):
        if value <len(self._states):
            self._state = self._states[value]

    @property
    def frequency(self):
        return self._frequency
    @frequency.setter
    def frequency(self,value):
        n = round(60/value)
        n = n if n<2^32 else 2^32
        self._frequency = self._base_frequency / n


class EVG(CallBack):

    @staticmethod:
    def get_database(prefix):
        db = dict()
        p = prefix
        db[p + 'SingleState-Cmd'] = {'type' : 'enum', 'enums':('Dsbl','Enbl'), 'value':0}
        db[p + 'InjectionState-Sel'] = {'type' : 'enum', 'enums':('Dsbl','Enbl'), 'value':1}
        db[p + 'InjectionState-Sts'] = {'type' : 'enum', 'enums':('Dsbl','Enbl'), 'value':1}
        db[p + 'InjCyclic'] = {'type' : 'enum', 'enums':('Off','On'), 'value':1}
        db[p + 'ContinuousState-Sel'] = {'type' : 'enum', 'enums':('Dsbl','Enbl'), 'value':1}
        db[p + 'ContinuousState-Sts'] = {'type' : 'enum', 'enums':('Dsbl','Enbl'), 'value':1}
        db[p + 'BucketList'] = {'type' : 'int', 'count': 864, 'value':0}
        db[p + 'RepRate-SP'] = {'type' : 'float', 'count': 1, 'value': 0.0, 'prec': 10}
        db[p + 'RepRate-RB'] = {'type' : 'float', 'count': 1, 'value': 0.0, 'prec': 10}
        for i in range(8):
            p = prefix + 'Clock{0:d}'.format(i)
            db.update(Clock.get_database(p))
        for evnt in ['Linac','InjBO','InjSI','RmpBO','RampSI','DigLI','DigTB','DigBO','DigTS','DigSI']:
            p = prefix + evnt
            db.update(Event.get_database(p))

        return db

    def __init__(self, frequency, events):
        supert().__init__(self)
        self._frequency = frequency
        self._continuous = None
        self._continuous_types = ('Off','On')
        self._cyclic_injection = None
        self._cyclic_injection_types = ('Off','On')
        self._bucket_list = _np.zeros(864)
        self._repetition_rate = None
        self._injecting = False
        self.continuous = 1
        self.cyclic_injection = 0
        self.repetition_rate = 2
        self.events = dict()
        for ev in events:
            self.events[ev] = Event(ev)
        self.clocks = dict()
        for i in range(8):
            self.clocks['Clock{0:d}'.format(i)] = Clock(self._frequency/4)

    @property
    def continuous(self):
        return self._continuous_types.index(self._continuous)
    @continuous.setter
    def continuous(self,value):
        if value < len(self._continuous_types):
            self._continuous = self._continuous_types[value]

    @property
    def cyclic_injection(self):
        return self._cyclic_injection_types.index(self._cyclic_injection)
    @cyclic_injection.setter
    def cyclic_injection(self,value):
        if value < len(self._cyclic_injection_types):
            self._cyclic_injection = self._cyclic_injection_types[value]

    @property
    def bucket_list(self):
        return self._bucket_list.tolist()
    @bucket_list.setter
    def bucket_list(self,value):
        for i in range(min(len(value),864)):
            if value[i]<=0: break
            self._bucket_list[i] = ((value[i]-1) % 864) + 1
        self._bucket_list[i:] = 0

    @property
    def repetition_rate(self):
        return self._repetition_rate
    @repetition_rate.setter
    def repetition_rate(self,value):
        n = round(60/value)
        n = n if n<60 else 60
        self._repetition_rate = 60 / n

    def start_injection(self,callback):
        self._injecting = True
        _threading.Thread(target=self._injection, kwargs={'callback':callback}).start()

    def stop_injection(self):
        self._injecting = False

    def single_pulse(self,callback):
        if self._continuous == 'Off': return
        evnts = self._generate_events('Single')
        callback(evnts)

    ###function for internal use###
    def _injection(self, callback):
        while True:
            for i in self.bucket_list:
                if not self._can_inject(): return
                if i<=0: break
                evnts = self._generate_events(('Inj','Cont'))
                callback(i,evnts)
                _time.sleep(1/self.repetition_rate)
            if self._cyclic_injection == 'Off':
                self._injecting = False
                break

    def _generate_events(self,tables):
        tables = tables if isinstance(tables,(list,tuple)) else (tables,)
        return [ev for ev in self.events.values() if ev.mode in tables]

    def _can_inject(self):
        if self._continuous == 'Off' or not self._injecting: return False
        return True

    def get_propty(self,reason):
        if reason  == 'SingleState-Cmd':
            return 0
        elif reason == 'InjCyclic-SP':
            return self.cyclic_injection_sp
        elif reason == 'InjCyclic-RB':
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
            return self.evg.clocks[reason[:6]].get_property_from_reason(reason[6:])#Not general enough
        elif reason.startswith(tuple(self.events.keys())):
            return self.evg.clocks[reason[:6]].get_property_from_reason(reason[6:])#Absolutely not general enough

    def set_propty(self,reason,value):
        if reason  == 'SingleState-Cmd':
            self.single_pulse(self._single_pulse_synchronism)
        elif reason == 'InjCyclic-SP':
            self.cyclic_injection_sp = value
        elif reason == 'ContinuousState-Sel' or reason == 'ContinuousState-Sts':
            self.continuous
        elif reason == 'InjectionState-Sel':
            self.injection_sp  = value
        elif reason == 'BucketList':
            self.bucket_list = value
        elif reason == 'RepRate-SP':
            return self.repetition_rate_sp = value


        if reason == 'InjStart-Cmd':
            self.start_injection(self._injection_cycle)
        elif reason == 'InjStop-Cmd':
            self.stop_injection()
        elif reason == 'SinglePulse-Cmd':
            self.single_pulse(self._single_pulse_synchronism)
        elif reason == 'InjCyclic':
            self.cyclic_injection = value
        elif reason == 'Continuous':
            self.continuous = value
        elif reason == 'BucketList':
            self.bucket_list = value
        elif reason.endswith('Freq'):
            self.clocks[reason.rstrip('Freq')].frequency = value
        elif reason.endswith('State') and reason.startswith('Clck'):
            self.clocks[reason.rstrip('State')].state = value
        elif reason.endswith('Delay'):
            self.events[reason.rstrip('Delay')].delay = value
        elif reason.endswith('State'):
            self.events[reason.rstrip('Mode')].mode = value
        elif reason.endswith('DelayType'):
            self.events[reason.rstrip('DelayType')].delay_type = value
        else: return False
        return True
