import uuid as _uuid
import numpy as _np
import threading as _threading
import time as _time

__EventMapping = {'Linac':0, 'InjBO':1,  'InjSI':2,  'RmpBO':3,
                 'RmpSI':4, 'DigLI':5,  'DigTB':6,  'DigBO':7,
                 'DigTS':8, 'DigSI':9}
__PwrFreq = 60
__FINE_DELAY_STEP = 5e-12

__EVENT_LABEL_TEMPLATE = 'Ev{0:02x}'
__CLOCK_LABEL_TEMPLATE = 'Cl{0:1d}'
__OPT_LABEL_TEMPLATE   = 'OPT{0:2d}'
__OUT_LABEL_TEMPLATE   = 'OUT{0:1d}'

class CallBack:

    def __init__(self, callbacks=None, prefix = None):
        self.prefix = prefix or ''
        self.__callbacks = dict(callbacks) if callbacks else dict()

    def __callback(self,propty,value,**kwargs):
        return NotImplemented()

    def __call_callbacks(self, propty, value, **kwargs):
        for uuid, callback in self.__callbacks.items():
            callback(self.prefix + propty, value, **kwargs)

    def add_callback(self,*args):
        if len(args)<2 and isinstance(args[0],dict):
            self.__callbacks.update(args[0])
        elif len(args) == 2:
            uuid, callback = args
            self.__callbacks[uuid] = callback
        else:
            raise Exception('wrong input for add_callback')

    def remove_callback(self,uuid):
        self.__callbacks.pop(uuid)


class EventSim(CallBack):

    def __init__(self,base_freq,callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self.__delay_type = None
        self.__delay = 0
        self.__mode = 0

    @property
    def delay(self):
        return self.__delay
    @delay.setter
    def delay(self,value):
        self.__delay = value
        self.__call_callbacks('delay',value)

    @property
    def mode(self):
        return self.__mode
    @mode.setter
    def mode(self,value):
        self.__mode = value
        self.__call_callbacks('mode',value)

    @property
    def delay_type(self):
        return self.__delay_type
    @delay_type.setter
    def delay_type(self,value):
        self.__delay_type = value
        self.__call_callbacks('delay_type',value)

    def get_base_freq(self):
        return self.base_freq

    def generate(self):
        if self.__mode > 0:
            return {'delay':self.__delay/self.base_freq}


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
        self.__uuid = _uuid.uuid4()
        self.__base_freq = base_freq
        if controller is None:
            self.__controller = EventSim(self.base_freq, {self.__uuid:self.__callback})
        else:
            self.__controller = controller
            self.__controller.add_callback({self.__uuid:self.__callback})
            self.base_freq = self.__controller.get_base_freq()
        self.__delay_sp = None
        self.__delay_rb = None
        self.__mode_sp = None
        self.__mode_rb = None
        self.__delay_type_sp = None
        self.__delay_type_rb = None
        self.__set_init_values()

    def __set_init_values(self):
        db = self.get_database()
        self.__delay_sp = db['Delay-SP']['value']
        self.__delay_rb = db['Delay-RB']['value']
        self.__mode_sp = db['Mode-Sel']['value']
        self.__mode_rb = db['Mode-Sts']['value']
        self.__delay_type_sp = db['DelayType-Sel']['value']
        self.__delay_type_rb = db['DelayType-Sts']['value']

    @property
    def delay_sp(self):
        return self.__delay_sp
    @delay_sp.setter
    def delay_sp(self,value):
        self.__delay_sp = value
        self.__controller.delay = round( value * self.__base_freq) #integer
        self.__call_callbacks('Delay-SP',value)

    @property
    def delay_rb(self):
        return self.__delay_rb
    @delay_rb.setter
    def delay_rb(self,value):
        self.__delay_rb = value * (1/self.__base_freq)
        self.__call_callbacks('Delay-RB',self.__delay_rb)

    @property
    def mode_sp(self):
        return self.__mode_sp
    @mode_sp.setter
    def mode_sp(self,value):
        if value <len(self.__modes):
            self.__mode_sp = value
            self.__controller.mode = value
            self.__call_callbacks('Mode-Sel',value)

    @property
    def mode_rb(self):
        return self.__mode_rb
    @mode_rb.setter
    def mode_rb(self,value):
        if value <len(self.__modes):
            self.__mode_rb = value
            self.__call_callbacks('Mode-Sts',value)

    @property
    def delay_type_sp(self):
        return self.__delay_type_sp
    @delay_type_sp.setter
    def delay_type_sp(self,value):
        if value <len(self.__delay_types):
            self.__delay_type_sp = value
            self.__controller.delay_type = value
            self.__call_callbacks('DelayType-Sel',value)

    @property
    def delay_type_rb(self):
        return self.__delay_type_rb
    @delay_type_rb.setter
    def delay_type_rb(self,value):
        if value <len(self.__delay_types):
            self.__delay_type_rb = value
            self.__call_callbacks('DelayType-Sts',value)

    def __callback(self,propty,value,**kwargs):
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
        self.__frequency = 1
        self.__state = 0

    @property
    def state(self):
        return self.__state
    @state.setter
    def state(self,value):
        self.__state = value
        self.__call_callbacks('state',value)

    @property
    def frequency(self):
        return self.__frequency
    @frequency.setter
    def frequency(self,value):
        self.__frequency = value
        self.__call_callbacks('frequency',value)

    def generate(self):
        if self.__state > 0:
            return {'frequency':self.base_freq/self.__frequency}


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
        self.__uuid = _uuid.uuid4()
        self.__base_frequency = base_freq
        if controller is None:
            self.__controller = ClockSim({self.__uuid:self.__callback})
        else:
            self.__controller = controller
            self.__controller.add_callback({self.__uuid:self.__callback})
        self.__frequency_sp = None
        self.__frequency_rb = None
        self.__state_sp = None
        self.__state_rb = None
        self.__set_init_values()

    def __set_init_values(self):
        db = self.get_database()
        self.__frequency_sp = db['Freq-SP']['value']
        self.__frequency_rb = db['Freq-RB']['value']
        self.__state_sp = db['State-Sel']['value']
        self.__state_rb = db['State-Sts']['value']

    @property
    def frequency_sp(self):
        return self.__frequency_sp
    @frequency_sp.setter
    def frequency_sp(self,value):
        self.__frequency_sp = value
        self.__controller.frequency = round(self.__base_frequency / value) #integer
        self.__call_callbacks('Freq-SP',value)

    @property
    def frequency_rb(self):
        return self.__frequency_rb
    @frequency_rb.setter
    def frequency_rb(self,value):
        self.__frequency_rb = value * self.__base_frequency
        self.__call_callbacks('Freq-RB',self.__frequency_rb)

    @property
    def state_sp(self):
        return self.__state_sp
    @state_sp.setter
    def state_sp(self,value):
        if value <len(self.__states):
            self.__state_sp = value
            self.__controller.state = value
            self.__call_callbacks('State-Sel',value)

    @property
    def state_rb(self):
        return self.__state_rb
    @state_rb.setter
    def state_rb(self,value):
        if value <len(self.__states):
            self.__state_rb = value
            self.__call_callbacks('State-Sts',value)

    def __callback(self, propty,value,**kwargs):
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
        self.__continuous = 1
        self.__injection = 0
        self.__injection_callbacks = dict()
        self.__cyclic_injection = 0
        self.__single = 0
        self.__single_callbacks = dict()
        self.__bucket_list = _np.zeros(864)
        self.__repetition_rate = 30
        self.events = list()
        for i in range(256):
            self.events.append(EventSim())
        self.clocks = list()
        for i in range(8):
            self.clocks.append(ClockSim())

    @property
    def continuous(self):
        return self.__continuous
    @continuous.setter
    def continuous(self,value):
        self.__continuous = value
        self.__call_callbacks('continuous',value)

    @property
    def cyclic_injection(self):
        return self.__cyclic_injection
    @cyclic_injection.setter
    def cyclic_injection(self,value):
        self.__cyclic_injection = value
        self.__call_callbacks('cyclic_injection',value)

    @property
    def bucket_list(self):
        return self.__bucket_list
    @bucket_list.setter
    def bucket_list(self,value):
        self.__bucket_list = value
        # self.__call_callbacks('bucket_list',value)

    @property
    def repetition_rate(self):
        return self.__repetition_rate
    @repetition_rate.setter
    def repetition_rate(self,value):
        self.__repetition_rate = value
        self.__call_callbacks('repetition_rate',value)

    ########### Functions related to Injection simulation #############
    @property
    def injection(self):
        return self.__injection
    @injection.setter
    def injection(self,value):
        if value:
            if not self.__injection and self.__continuous:
                self.__injection = value
                _threading.Thread(target=self.__injection_fun).start()
        else:
            self.__injection = value
        self.__call_callbacks('injection',value)

    def add_injection_callback(self,uuid,callback):
        self.__injection_callbacks.update({uuid:callback})

    def remove_injection_callback(self,uuid):
        self.__injection_callbacks.pop(uuid, None)

    def __injection_fun(self):
        while True:
            for i in self.__bucket_list:
                if not self.__can_inject(): return
                if i<=0: break
                evnts = self.__generate_events((1,2))
                for callback in self.__injection_callbacks.values():
                    callback(i,evnts)
                _time.sleep(self.__repetition_rate/_PwrFreq)
            if not self.__cyclic_injection:
                self.__injection = 0
                self.__call_callbacks('injection',0)
                return

    def __can_inject(self):
        if not self.__continuous or not self.__injection: return False
        return True
    ######################################################################
    ########### Functions related to Single Pulse simulation #############
    @property
    def single(self):
        return self.__single
    @single.setter
    def single(self,value):
        if value:
            if not self.__single:
                self.__single = value
                if not self.__continuous: return
                evnts = self.__generate_events(3)
                for callback in self.__single_callbacks.values():
                    callback(evnts)
        else:
            self.__single = value
        self.__call_callbacks('single',value)

    def add_single_callback(self,uuid,callback):
        self.__single_callbacks.update({uuid:callback})

    def remove_single_callback(self,uuid):
        self.__single_callbacks.pop(uuid, None)
    ##########################################################################

    def __generate_events(self,tables):
        tables = tables if isinstance(tables,(list,tuple)) else (tables,)
        events = dict()
        for i, ev in enumerate(self.events):
            if not ev.mode in tables: continue
            dic = ev.generate()
            if not dic: continue
            lab = __EVENT_LABEL_TEMPLATE.format(i)
            events.update(  { lab : dic }  )
        for i, cl in enumerate(self.clocks):
            dic = cl.generate()
            if not dic: continue
            lab = __CLOCK_LABEL_TEMPLATE.format(i)
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
        for evnt in __EventMapping.keys():
            p = prefix + evnt
            db.update(EventIOC.get_database(p))

        return db

    def __init__(self, base_freq, callbacks = None, prefix = None, controller = None):
        super().__init__(callbacks = callbacks, prefix = prefix)
        self.__uuid = _uuid.uuid4()
        self.__base_freq = base_freq
        if controller is None:
            self.__controller = EVGSim({self.__uuid:self.__sim_callback})
        else:
            self.__controller = controller
            self.__controller.add_callback({self.__uuid:self.__sim_callback})
        self.events = dict()
        for i,ev in enumerate(sorted(_EventMapping.keys())):
            cntler = self.__controller.events[i]
            self.events[ev] = EventIOC(self.__base_freq/4,
            callbacks = {self.__uuid:self.__ioc_callback},
            prefix = ev,
            controller = cntler)
        self.clocks = dict()
        for i in range(8):
            name = 'Clock{0:d}'.format(i)
            cntler = self.__controller.clocks[i]
            self.clocks[name] = ClockIOC(self.__base_freq/4,
            callbacks = {self.__uuid:self.__ioc_callback},
            prefix = name,
            controller = cntler)
        self.__single_sp = None
        self.__single_rb = None
        self.__injection_sp = False
        self.__injection_rb = False
        self.__cyclic_injection_sp = None
        self.__cyclic_injection_rb = None
        self.__continuous_sp = None
        self.__continuous_rb = None
        self.__bucket_list = _np.zeros(864)
        self.__repetition_rate_sp = None
        self.__repetition_rate_rb = None
        self.__set_init_values()

    def __set_init_values(self):
        db = self.get_database()
        self.__single_sp = db['SingleState-Sel']['value']
        self.__single_rb = db['SingleState-Sts']['value']
        self.__injection_sp = db['InjectionState-Sel']['value']
        self.__injection_rb = db['InjectionState-Sts']['value']
        self.__cyclic_injection_sp = db['InjCyclic-Sel']['value']
        self.__cyclic_injection_rb = db['InjCyclic-Sts']['value']
        self.__continuous_sp = db['ContinuousState-Sel']['value']
        self.__continuous_rb = db['ContinuousState-Sts']['value']
        self.__repetition_rate_sp = db['RepRate-SP']['value']
        self.__repetition_rate_rb = db['RepRate-RB']['value']
        self.__bucket_list = _np.ones(864)*db['BucketList']['value']


    def __ioc_callback(self,propty,value, **kwargs):
        self.__call_callbacks(propty, value, **kwargs)

    def __sim_callback(self,propty,value, **kwargs):
        if propty == 'continuous':
            self.continuous_rb = value
        elif propty == 'clyclic_injection':
            self.clyclic_injection_rb = value
        elif propty == 'bucket_list':
            if _np.any(value != self.__bucket_list):
                self.bucket_list = value
                self.__call_callbacks('BucketList',value)
        elif propty == 'repetition_rate':
            self.repetition_rate_rb = value
        elif propty == 'injection':
            self.injection_rb = value
            if value != self.__injection_sp:
                self.__injection_sp = value
                self.__call_callbacks('InjectionState-Sel',value)
        elif propty == 'single':
            self.single_rb = value
            self.__single_sp = value
            self.__call_callbacks('SingleState-Sel',value)

    def add_injection_callback(self, uuid,callback):
        self.__controller.add_injection_callback(uuid,callback)

    def remove_injection_callback(self, uuid):
        self.__controller.remove_injection_callback(uuid)

    def add_single_callback(self, uuid,callback):
        self.__controller.add_single_callback(uuid,callback)

    def remove_single_callback(self, uuid):
        self.__controller.remove_single_callback(uuid)

    @property
    def continuous_sp(self):
        return self.__continuous_sp
    @continuous_sp.setter
    def continuous_sp(self,value):
        if value <len(self.__states):
            self.__continuous_sp = value
            self.__controller.continuous = value
            self.__call_callbacks('ContinuousState-Sel',value)

    @property
    def continuous_rb(self):
        return self.__continuous_rb
    @continuous_rb.setter
    def continuous_rb(self,value):
        if value <len(self.__states):
            self.__continuous_rb = value
            self.__call_callbacks('ContinuousState-Sts',value)

    @property
    def injection_sp(self):
        return self.__injection_sp
    @injection_sp.setter
    def injection_sp(self,value):
        if value <len(self.__states):
            self.__injection_sp = value
            self.__controller.injection = value
            self.__call_callbacks('InjectionState-Sel',value)

    @property
    def injection_rb(self):
        return self.__injection_rb
    @injection_rb.setter
    def injection_rb(self,value):
        if value <len(self.__states):
            self.__injection_rb = value
            self.__call_callbacks('InjectionState-Sts',value)

    @property
    def single_sp(self):
        return self.__single_sp
    @single_sp.setter
    def single_sp(self,value):
        if value <len(self.__states):
            self.__single_sp = value
            self.__controller.single = value
            self.__call_callbacks('SingleState-Sel',value)

    @property
    def single_rb(self):
        return self.__single_rb
    @single_rb.setter
    def single_rb(self,value):
        if value <len(self.__states):
            self.__single_rb = value
            self.__call_callbacks('SingleState-Sts',value)

    @property
    def cyclic_injection_sp(self):
        return self.__cyclic_injection_sp
    @cyclic_injection_sp.setter
    def cyclic_injection_sp(self,value):
        if value <len(self.__states):
            self.__cyclic_injection_sp = value
            self.__controller.cyclic_injection = value
            self.__call_callbacks('InjCyclic-Sel',value)

    @property
    def cyclic_injection_rb(self):
        return self.__cyclic_injection_rb
    @cyclic_injection_rb.setter
    def cyclic_injection_rb(self,value):
        if value <len(self.__states):
            self.__cyclic_injection_rb = value
            self.__call_callbacks('InjCyclic-Sts',value)

    @property
    def bucket_list(self):
        return self.__bucket_list.tolist()
    @bucket_list.setter
    def bucket_list(self,value):
        for i in range(min(len(value),864)):
            if value[i]<=0: break
            self.__bucket_list[i] = ((value[i]-1) % 864) + 1
        self.__bucket_list[i:] = 0
        self.__controller.bucket_list = value
        self.__call_callbacks('BucketList',value)

    @property
    def repetition_rate(self):
        return self.__repetition_rate
    @repetition_rate.setter
    def repetition_rate(self,value):
        n = round(60/value)
        n = n if n<60 else 60
        self.__repetition_rate = 60 / n

    @property
    def repetition_rate_sp(self):
        return self.__repetition_rate_sp
    @repetition_rate_sp.setter
    def repetition_rate_sp(self,value):
        self.__repetition_rate_sp = value
        self.__controller.repetition_rate = round(_PwrFreq / value) #integer
        self.__call_callbacks('RepRate-SP',value)

    @property
    def repetition_rate_rb(self):
        return self.__repetition_rate_rb
    @repetition_rate_rb.setter
    def repetition_rate_rb(self,value):
        self.__repetition_rate_rb = value * __PwrFreq
        self.__call_callbacks('RepRate-RB',self.__repetition_rate_rb)

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
        self.__optic_channel = 0
        self.__delay = 0
        self.__fine_delay = 0

    @property
    def fine_delay(self):
        return self.__fine_delay
    @fine_delay.setter
    def fine_delay(self,value):
        self.__fine_delay = value
        self.__call_callbacks('fine_delay',value)

    @property
    def delay(self):
        return self.__delay
    @delay.setter
    def delay(self,value):
        self.__delay = value
        self.__call_callbacks('delay',value)

    @property
    def optic_channel(self):
        return self.__optic_channel
    @optic_channel.setter
    def optic_channel(self,value):
        self.__optic_channel = value
        self.__call_callbacks('optic_channel',value)

    def receive_events(self, events):
        lab = __OPT_LABEL_TEMPLATE.format(self.__optic_channel)
        dic = events.get(lab,None)
        if dic is None: return
        dic['delay'] += self.__delay/self.base_freq + self.__fine_delay * __FINE_DELAY_STEP
        return dic


class EVRTriggerIOC(CallBack):
    _optic_channels = tuple(  [ __OPT_LABEL_TEMPLATE.format(i) for i in range(EVRSim._NR_INTERNAL_OPT_CHANNELS) ]  )

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
        self.__uuid = _uuid.uuid4()
        self.__base_freq = base_freq
        if controller is None:
            self.__controller = TriggerSim(self.base_freq, {self.__uuid:self.__callback})
        else:
            self.__controller = controller
            self.__controller.add_callback({self.__uuid:self.__callback})
        self.__delay_sp = 0
        self.__delay_rb = 0
        self.__optic_channel_sp = 0
        self.__optic_channel_rb = 0
        self.__fine_delay_sp = 0
        self.__fine_delay_rb = 0
        self.__set_init_values()

    def __set_init_values(self):
        db = self.get_database()
        self.__delay_sp = db['Delay-SP']['value']
        self.__delay_rb = db['Delay-RB']['value']
        self.__optic_channel_sp = db['OptCh-Sel']['value']
        self.__optic_channel_rb = db['OptCh-Sts']['value']
        self.__fine_delay_sp = db['FineDelay-SP']['value']
        self.__fine_delay_rb = db['FineDelay-RB']['value']

    @property
    def fine_delay_sp(self):
        return self.__fine_delay_sp
    @fine_delay_sp.setter
    def fine_delay_sp(self,value):
        self.__fine_delay_sp = value
        self.__controller.fine_delay = round(value / __FINE_DELAY_STEP ) #integer
        self.__call_callbacks('FineDelay-SP',value)

    @property
    def fine_delay_rb(self):
        return self.__fine_delay_rb
    @fine_delay_rb.setter
    def fine_delay_rb(self,value):
        self.__fine_delay_rb = value * __FINE_DELAY_STEP
        self.__call_callbacks('FineDelay-RB',self.__fine_delay_rb)

    @property
    def delay_sp(self):
        return self.__delay_sp
    @delay_sp.setter
    def delay_sp(self,value):
        self.__delay_sp = value
        self.__controller.delay = round(value * self.__base_frequency ) #integer
        self.__call_callbacks('Delay-SP',value)

    @property
    def delay_rb(self):
        return self.__delay_rb
    @delay_rb.setter
    def delay_rb(self,value):
        self.__delay_rb = value / self.__base_frequency
        self.__call_callbacks('Delay-RB',self.__delay_rb)

    @property
    def optic_channel_sp(self):
        return self.__optic_channel_sp
    @optic_channel_sp.setter
    def optic_channel_sp(self,value):
        if value <len(self.__optic_channels):
            self.__optic_channel_sp = value
            self.__controller.optic_channel = value
            self.__call_callbacks('OptCh-Sel',value)

    @property
    def optic_channel_rb(self):
        return self.__optic_channel_rb
    @optic_channel_rb.setter
    def optic_channel_rb(self,value):
        if value <len(self.__optic_channels):
            self.__optic_channel_rb = value
            self.__call_callbacks('OptCh-Sts',value)

    def __callback(self, propty,value,**kwargs):
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
    _optic_channels = tuple(  [ __OPT_LABEL_TEMPLATE.format(i) for i in range(EVRSim._NR_INTERNAL_OPT_CHANNELS) ]  )

##hele

class OpticChannelSim(CallBack):

    def __init__(self,base_freq,callbacks=None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self.__state = 0
        self.__width = 0
        self.__delay = 0
        self.__polarity = 0
        self.__event = 0
        self.__pulses = 1

    @property
    def state(self):
        return self.__state
    @state.setter
    def state(self,value):
        self.__state = value
        self.__call_callbacks('state',value)

    @property
    def width(self):
        return self.__width
    @width.setter
    def width(self,value):
        self.__width = value
        self.__call_callbacks('width',value)

    @property
    def delay(self):
        return self.__delay
    @delay.setter
    def delay(self,value):
        self.__delay = value
        self.__call_callbacks('delay',value)

    @property
    def polarity(self):
        return self.__polarity
    @polarity.setter
    def polarity(self,value):
        self.__polarity = value
        self.__call_callbacks('polarity',value)

    @property
    def event(self):
        return self.__event
    @event.setter
    def event(self,value):
        self.__event = value
        self.__call_callbacks('event',value)

    @property
    def pulses(self):
        return self.__pulses
    @pulses.setter
    def pulses(self,value):
        self.__pulses = value
        self.__call_callbacks('pulses',value)

    def receive_events(self, events):
        if self.__state == 0: return
        lab = __EVENT_LABEL_TEMPLATE.format(self.__event)
        ev = events.get(lab,None)
        if ev is None: return
        delay = ev['delay'] + self.__delay/self.base_freq
        return dict(  { 'pulses':self.__pulses, 'width':self.__width/self.base_freq, 'delay':delay }  )

class EVRSim(CallBack):

    __NR_INTERNAL_OPT_CHANNELS = 24
    __NR_OPT_CHANNELS_OUT = 12

    def __init__(self, base_freq, callbacks= None):
        super().__init__(callbacks)
        self.base_freq = base_freq
        self.__state = 1
        self.optic_channels = list()
        for i in range(self.__NR_INTERNAL_OPT_CHANNELS):
            self.optic_channels[i] = OpticChannelSim(self.base_freq)
        self.trigger_outputs = list()
        for i in range(8):
            self.trigger_outputs[i] = TriggerOutputSim(self.base_freq)

    @property
    def state(self):
        return self.__state
    @state.setter
    def state(self,value):
        self.__state = value
        self.__call_callbacks('state',value)

    def receive_events(self,events):
        opt_out = dict()
        triggers = dict()
        for i, opt_ch in enumerate(self.optic_channels):
            opt = opt_ch.receive_events(events)
            if opt is None: continue
            lab = __OPT_LABEL_TEMPLATE.format(i)
            opt_out.update( {lab:opt} )
            if i < __NR_OPT_CHANNELS_OUT: triggers.update( {lab:opt} )
        for tri_ch in self.trigger_outputs:
            triggers.append(tri_ch.deal_with_opt_ch(opt_out))
        return triggers


class EVESim(EVRSim):

    __NR_INTERNAL_OPT_CHANNELS = 16
    __NR_OPT_CHANNELS_OUT = 0
