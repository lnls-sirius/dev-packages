"""Module to simulate timing system."""

from siriuspy.namesys import SiriusPVName as _PVName
from .device_models import CallBack as _CallBack
from .device_models import EVGIOC as _EVGIOC
from .device_models import EVRIOC as _EVRIOC
from .device_models import EVEIOC as _EVEIOC
from .device_models import AFCIOC as _AFCIOC
from .device_models import FOUTIOC as _FOUTIOC
from siriuspy.timesys.time_data import Connections as _Connections
from siriuspy.timesys.time_data import RF_DIVISION as _RFDIV


class TimingSimulation(_CallBack):
    """Class to simulate timing system."""

    EVG_PREFIX = None
    EVRs = None
    EVEs = None
    AFCs = None
    FOUTs = None

    @classmethod
    def get_database(cls, prefix=''):
        """Get the database of the Class."""
        cls._get_constants()
        db = dict()
        pre = prefix + cls.EVG_PREFIX
        db.update(_EVGIOC.get_database(prefix=pre))
        for dev in cls.EVRs:
            pre = prefix + dev + ':'
            db.update(_EVRIOC.get_database(prefix=pre))
        for dev in cls.EVEs:
            pre = prefix + dev + ':'
            db.update(_EVEIOC.get_database(prefix=pre))
        for dev in cls.AFCs:
            pre = prefix + dev + ':'
            db.update(_AFCIOC.get_database(prefix=pre))
        for dev in cls.FOUTs:
            pre = prefix + dev + ':'
            db.update(_FOUTIOC.get_database(prefix=pre))
        return db

    def __init__(self, rf_freq, callbacks=None, prefix=''):
        """Initialize the instance."""
        self._get_constants()
        super().__init__(callbacks, prefix='')
        evg = _EVGIOC(rf_freq,
                      callbacks={self.uuid: self._on_pvs_change},
                      prefix=prefix + self.EVG_PREFIX)
        self.evrs = dict()
        for dev in self.EVRs:
            pref = prefix + dev + ':'
            evr = _EVRIOC(rf_freq/_RFDIV,
                          callbacks={self.uuid: self._on_pvs_change},
                          prefix=pref)
            evg.add_pending_devices_callback(evr.uuid, evr.receive_events)
            self.evrs[pref] = evr

        self.eves = dict()
        for dev in self.EVEs:
            pref = prefix + dev + ':'
            eve = _EVEIOC(rf_freq/_RFDIV,
                          callbacks={self.uuid: self._on_pvs_change},
                          prefix=pref)
            evg.add_pending_devices_callback(eve.uuid, eve.receive_events)
            self.eves[pref] = eve

        self.afcs = dict()
        for dev in self.AFCs:
            pref = prefix + dev + ':'
            afc = _AFCIOC(rf_freq/_RFDIV,
                          callbacks={self.uuid: self._on_pvs_change},
                          prefix=pref)
            evg.add_pending_devices_callback(afc.uuid, afc.receive_events)
            self.afcs[pref] = afc

        self.fouts = dict()
        for dev in self.FOUTs:
            pref = prefix + dev + ':'
            fout = _FOUTIOC(rf_freq/_RFDIV,
                            callbacks={self.uuid: self._on_pvs_change},
                            prefix=pref)
            # evg.add_pending_devices_callback(fout.uuid, fout.receive_events)
            self.fouts[pref] = fout
        self.evg = evg

    def add_injection_callback(self, uuid, callback):
        """Add injection callback."""
        self.evg.add_injection_callback(uuid, callback)

    def remove_injection_callback(self, uuid):
        """Remove injection callback."""
        self.evg.remove_injection_callback(uuid)

    def get_propty(self, reason):
        """Get property by PV name."""
        reason = reason[len(self.prefix):]
        parts = _PVName(reason)
        if parts.dev == 'EVG':
            return self.evg.get_propty(reason)
        elif parts.device_name+':' in self.evrs.keys():
            return self.evrs[parts.device_name+':'].get_propty(reason)
        elif parts.device_name+':' in self.eves.keys():
            return self.eves[parts.device_name+':'].get_propty(reason)
        elif parts.device_name+':' in self.afcs.keys():
            return self.afcs[parts.device_name+':'].get_propty(reason)
        elif parts.device_name+':' in self.fouts.keys():
            return self.fouts[parts.device_name+':'].get_propty(reason)
        else:
            return None

    def set_propty(self, reason, value):
        """Set property by PV Name."""
        reason = reason[len(self.prefix):]
        parts = _PVName(reason)
        if parts.dev == 'EVG':
            return self.evg.set_propty(reason, value)
        elif parts.device_name+':' in self.evrs.keys():
            return self.evrs[parts.device_name+':'].set_propty(reason, value)
        elif parts.device_name+':' in self.eves.keys():
            return self.eves[parts.device_name+':'].set_propty(reason, value)
        elif parts.device_name+':' in self.afcs.keys():
            return self.afcs[parts.device_name+':'].set_propty(reason, value)
        elif parts.device_name+':' in self.fouts.keys():
            return self.fouts[parts.device_name+':'].set_propty(reason, value)
        else:
            return False

    def _on_pvs_change(self, propty, value, **kwargs):
        self._call_callbacks(propty, value, **kwargs)

    @classmethod
    def _get_constants(cls):
        if cls.EVG_PREFIX:
            return
        cls.EVG_PREFIX = _Connections.get_devices('EVG').pop() + ':'
        cls.EVRs = _Connections.get_devices('EVR')
        cls.EVEs = _Connections.get_devices('EVE')
        cls.AFCs = _Connections.get_devices('AFC')
        cls.FOUTs = _Connections.get_devices('FOUT')
