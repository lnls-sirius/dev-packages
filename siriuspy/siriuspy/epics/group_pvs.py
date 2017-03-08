from .sirius_pv import SiriusPV as _SiriusPV

class GroupPVs:

    def __init__(self, pv_names, connection_callback=None, connection_timeout=None):

        self._pv_names = tuple([item for item in pv_names])
        self._create_device_pvs(connection_callback, connection_timeout)

    def _create_device_pvs(self, connection_callback, connection_timeout):
        self._pvs = {}
        for pv_name in self._pv_names:
            self._pvs[pv_name] = _SiriusPV(pv_name,
                                           connection_callback=connection_callback,
                                           connection_timeout=connection_timeout)

    @property
    def pv_names_list(self):
        return self._pv_names

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._pvs[key]
        elif isinstance(key, int):
            return self._pvs[self._pv_names[key]]
        else:
            raise KeyError

    @property
    def connected(self):
        for prop, pv in self._pvs.items():
            if not pv.connected:
                return False
        return True

    def disconnect(self):
        for pv_name in self._pv_names:
            self._pvs[pv_name].disconnect()

    def __del__(self):
        self.disconnect()
