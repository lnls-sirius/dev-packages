import uuid as _uuid
from siriuspy.namesys import SiriusPVName as _PVName
from .  import device_models as _device_models
from ..time_data import Connections

class TimingSimulation(_device_models.CallBack):
    EVG_PREFIX  = None

    EVRs = None
    EVEs = None
    AFCs = None

    @classmethod
    def get_constants(cls):
        if cls.EVG_PREFIX: return
        cls.EVG_PREFIX  = Connections.get_devices('evg').pop() + ':'
        cls.EVRs = Connections.get_devices('evr')
        cls.EVEs = Connections.get_devices('eve')
        cls.AFCs = Connections.get_devices('afc')

    @classmethod
    def get_database(cls, prefix = ''):
        cls.get_constants()
        db = dict()
        db.update(  _device_models.EVGIOC.get_database( prefix = prefix + cls.EVG_PREFIX )  )
        for dev in cls.EVRs:
            db.update(  _device_models.EVRIOC.get_database( prefix = prefix + dev + ':' )  )
        for dev in cls.EVEs:
            db.update(  _device_models.EVEIOC.get_database( prefix = prefix + dev + ':' )  )
        for dev in cls.AFCs:
            db.update(  _device_models.AFCIOC.get_database( prefix = prefix + dev + ':' )  )
        return db

    def __init__(self,rf_frequency,callbacks=None, prefix = ''):
        self.get_constants()
        super().__init__(callbacks,prefix='')
        self.uuid = _uuid.uuid4()
        self.evg = _device_models.EVGIOC(rf_frequency,
                                         callbacks={self.uuid:self._callback},
                                         prefix = prefix + EVG_PREFIX  )
        self.evrs = dict()
        for dev in self.EVRs:
            pref = prefix + dev + ':'
            evr = _device_models.EVRIOC( rf_frequency/_device_models.RF_FREQ_DIV,
                                         callbacks={self.uuid:self._callback},
                                         prefix = pref )
            self.evg.add_pending_devices_callback(evr.uuid, evr.receive_events)
            self.evrs[pref] = evr

        self.eves = dict()
        for dev in self.EVEs:
            pref = prefix + dev + ':'
            eve = _device_models.EVEIOC( rf_frequency/_device_models.RF_FREQ_DIV,
                                         callbacks={self.uuid:self._callback},
                                         prefix = pref )
            self.evg.add_pending_devices_callback(eve.uuid, eve.receive_events)
            self.eves[pref] = eve

        self.afcs = dict()
        for dev in self.AFCs:
            pref = prefix + dev + ':'
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
        parts = _PVName(reason)
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
        parts = _PVName(reason)
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
