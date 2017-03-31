import uuid as _uuid
from . import device_models as _device_models
import siriuspy.namesys as _namesys


_EventMapping = {'Linac':0,  'InjBO':1,  'InjSI':2,  'RmpBO':3,  'RmpSI':4,
                 'DigLI':5,  'DigTB':6,  'DigBO':7,  'DigTS':8,  'DigSI':9,
                 'Orbit':10, 'Coupl':11,  'Tunes':12,}

EVG_PREFIX = 'AS-Glob:TI-EVG:'
EVR_PREFIX = 'AS-Glob:TI-EVR-{0:d}:'
EVE_PREFIX = 'AS-Glob:TI-EVE-{0:d}:'
AFC_PREFIX = 'AS-CRT{0:02d}:TI-AFC:'

NR_EVRs = 7
NR_EVEs = 4
NR_AFCs = 20


class TimingSimulation(_device_models.CallBack):

    @classmethod
    def get_database(cls, prefix = ''):
        db = dict()
        db.update(  _device_models.EVGIOC.get_database( prefix = prefix + EVG_PREFIX )  )
        for i in range(NR_EVRs):
            pref = prefix + EVR_PREFIX.format(i)
            db.update(  _device_models.EVRIOC.get_database( prefix = pref )  )
        for i in range(NR_EVEs):
            pref = prefix + EVE_PREFIX.format(i)
            db.update(  _device_models.EVEIOC.get_database( prefix = pref )  )
        for i in range(NR_AFCs):
            pref = prefix + AFC_PREFIX.format(i)
            db.update(  _device_models.AFCIOC.get_database( prefix = pref )  )
        return db

    def __init__(self,rf_frequency,callbacks=None, prefix = ''):
        super().__init__(callbacks,prefix='')
        self.uuid = _uuid.uuid4()
        self.evg = _device_models.EVGIOC(rf_frequency,
                                         callbacks={self.uuid:self._callback},
                                         prefix = prefix + EVG_PREFIX  )
        self.evrs = dict()
        for i in range(NR_EVRs):
            pref = prefix + EVR_PREFIX.format(i)
            evr = _device_models.EVRIOC( rf_frequency/_device_models.RF_FREQ_DIV,
                                         callbacks={self.uuid:self._callback},
                                         prefix = pref )
            self.evg.add_pending_devices_callback(evr.uuid, evr.receive_events)
            self.evrs[pref] = evr

        self.eves = dict()
        for i in range(NR_EVEs):
            pref = prefix + EVE_PREFIX.format(i)
            eve = _device_models.EVEIOC( rf_frequency/_device_models.RF_FREQ_DIV,
                                         callbacks={self.uuid:self._callback},
                                         prefix = pref )
            self.evg.add_pending_devices_callback(eve.uuid, eve.receive_events)
            self.eves[pref] = eve

        self.afcs = dict()
        for i in range(NR_AFCs):
            pref = prefix + AFC_PREFIX.format(i)
            afc = _device_models.AFCIOC( rf_frequency/_device_models.RF_FREQ_DIV,
                                         callbacks={self.uuid:self._callback},
                                         prefix = pref )
            self.evg.add_pending_devices_callback(afc.uuid, afc.receive_events)
            self.afcs[pref] = afc

    def _callback(self,propty,value, **kwargs):
        self._call_callbacks(propty, value, **kwargs)

    def add_injection_callback(self, uuid, callback):
        self.evg.add_injection_callback(uuid, callback)

    def remove_injection_callback(self, uuid):
        self.evg.remove_injection_callback(uuid)

    def add_single_callback(self, uuid, callback):
        self.evg.add_single_callback(uuid, callback)

    def remove_single_callback(self, uuid):
        self.evg.remove_single_callback(uuid)

    def get_propty(self, reason):
        reason = reason[len(self.prefix):]
        parts = _namesys.SiriusPVName(reason)
        if parts.dev_type == 'EVG':
            return self.evg.get_propty(reason)
        elif parts.dev_name+':' in self.evrs.keys():
            return self.evrs[parts.dev_name+':'].get_propty(reason)
        elif parts.dev_name+':' in self.eves.keys():
            return self.eves[parts.dev_name+':'].get_propty(reason)
        elif parts.dev_name+':' in self.afcs.keys():
            return self.afcs[parts.dev_name+':'].get_propty(reason)
        else:
            return None

    def set_propty(self, reason, value):
        reason = reason[len(self.prefix):]
        parts = _namesys.SiriusPVName(reason)
        if parts.dev_type == 'EVG':
            return self.evg.set_propty(reason,value)
        elif parts.dev_name+':' in self.evrs.keys():
            return self.evrs[parts.dev_name+':'].set_propty(reason,value)
        elif parts.dev_name+':' in self.eves.keys():
            return self.eves[parts.dev_name+':'].set_propty(reason,value)
        elif parts.dev_name+':' in self.afcs.keys():
            return self.afcs[parts.dev_name+':'].set_propty(reason,value)
        else:
            return False


def get_mapping_timing_devs_2_receivers():
    mapping = {
               ('AS-Glob:TI-EVR-1',  'OUT1'):(('LI-01','EGun:MultiBun'),),
               ('AS-Glob:TI-EVR-1',  'OUT2'):(('LI-01','EGun:SglBun'),),
               ('AS-Glob:TI-EVR-1', 'OPT01'):(('LI-01','Modltr-1'),),
               ('AS-Glob:TI-EVR-1', 'OPT02'):(('LI-01','Modltr-2'),),
               ('AS-Glob:TI-EVR-1', 'OPT03'):(('LI-01','SSA-1'),),
               ('AS-Glob:TI-EVR-1', 'OPT04'):(('LI-01','SSA-2'),),
               ('AS-Glob:TI-EVR-1', 'OPT05'):(('LI-01','SSA-3'),),
               ('AS-Glob:TI-EVR-1', 'OPT06'):(('LI-01','LLRF-1'),),
               ('AS-Glob:TI-EVR-1', 'OPT07'):(('LI-01','LLRF-2'),),
               ('AS-Glob:TI-EVR-1', 'OPT08'):(('LI-01','LLRF-3'),),

               ('AS-Glob:TI-EVR-2', 'OPT01'):(('TB-04',  'InjS'),),
               ('AS-Glob:TI-EVR-2', 'OPT02'):(('BO-01D', 'InjK'),),
               ('AS-Glob:TI-EVR-2', 'OPT03'):(('BO-48D', 'EjeK'),),
               ('AS-Glob:TI-EVR-2', 'OPT04'):(('TS-01',  'EjeSF'),),
               ('AS-Glob:TI-EVR-2', 'OPT05'):(('TS-01',  'EjeSG'),),
               ('AS-Glob:TI-EVR-2', 'OPT06'):(('TS-Fam', 'InjSG'),),
               ('AS-Glob:TI-EVR-2', 'OPT07'):(('TS-04',  'InjSF'),),
               ('AS-Glob:TI-EVR-2', 'OPT08'):(('SI-01SA','InjK'),),
               ('AS-Glob:TI-EVR-2', 'OPT09'):(('BO-05D', 'P5Cav'),),
               ('AS-Glob:TI-EVR-2', 'OPT10'):(('BO-05D', 'LLRF'),),
               ('AS-Glob:TI-EVR-2',  'OUT1'):( ('BO-01U','CH'),   ('BO-03U','CH'),   ('BO-05U','CH'),   ('BO-07U','CH'),   ('BO-09U','CH'),  ## FOUT, maybe
                                               ('BO-11U','CH'),   ('BO-13U','CH'),   ('BO-15U','CH'),   ('BO-17U','CH'),   ('BO-19U','CH'),
                                               ('BO-11U','CH'),   ('BO-23U','CH'),   ('BO-25U','CH'),   ('BO-27U','CH'),   ('BO-29U','CH'),
                                               ('BO-11U','CH'),   ('BO-33U','CH'),   ('BO-35U','CH'),   ('BO-37U','CH'),   ('BO-39U','CH'),
                                               ('BO-11U','CH'),   ('BO-43U','CH'),   ('BO-45U','CH'),   ('BO-47U','CH'),   ('BO-49U','CH'),  ),
               ('AS-Glob:TI-EVR-2',  'OUT2'):( ('BO-01U','CV'),   ('BO-03U','CV'),   ('BO-05U','CV'),   ('BO-07U','CV'),   ('BO-09U','CV'),  ## FOUT, maybe
                                               ('BO-11U','CV'),   ('BO-13U','CV'),   ('BO-15U','CV'),   ('BO-17U','CV'),   ('BO-19U','CV'),
                                               ('BO-11U','CV'),   ('BO-23U','CV'),   ('BO-25U','CV'),   ('BO-27U','CV'),   ('BO-29U','CV'),
                                               ('BO-11U','CV'),   ('BO-33U','CV'),   ('BO-35U','CV'),   ('BO-37U','CV'),   ('BO-39U','CV'),
                                               ('BO-11U','CV'),   ('BO-43U','CV'),   ('BO-45U','CV'),   ('BO-47U','CV'),   ('BO-49U','CV'),  ),
               ('AS-Glob:TI-EVR-2',  'OUT3'):( ('BO-Fam','B-1'),  ('BO-Fam','B-2'),  ('BO-Fam','QF'),   ('BO-Fam','QD'),
                                               ('BO-Fam','SD'),   ('BO-Fam','SF'),   ('BO-02D','QS'), ),







              }
