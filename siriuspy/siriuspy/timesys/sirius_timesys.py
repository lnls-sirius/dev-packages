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
