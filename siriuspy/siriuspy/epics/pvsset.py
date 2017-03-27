
from .pv import SiriusPV as _SiriusPV


class SiriusPVsSet:

    def __init__(self, pv_names=None, connection_callback=None, connection_timeout=None):

        self._connection_timeout = connection_timeout
        self._pv_names = []
        self._pvs = {}

        if pv_names:
            for pv_name in pv_names:
                self.add(pv_name, connection_callback=connection_callback)

    @property
    def connection_timeout(self):
        return self._connection_timeout

    @connection_timeout.setter
    def connection_timeout(self, value):
        self._connection_timeout = value
        for pv_name in self._pv_names:
            self._pvs[pv_name].connection_timeout = value

    @property
    def pv_names(self):
        return tuple(self._pv_names)

    @property
    def connected(self):
        for pv_name in self._pv_names:
            if not self._pvs[pv_name].connected:
                return False
        return True

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._pvs[key]
        elif isinstance(key, int):
            return self._pvs[self._pv_names[key]]
        else:
            raise KeyError

    def __setitem__(self, key, value):
        if isinstance(key, str):
            self._pvs[key].value = value
        elif isinstance(key, int):
            self._pvs[self._pv_names[key]].value = value
        else:
            raise KeyError

    def add(self, pv, connection_callback=None, connection_timeout=None):
        """Add a reference of passed SiriusPV object 'pv' or creates a new one, if passed argument is a pv name string."""
        if isinstance(pv, str):
            if pv not in self._pvs:
                self._pv_names.append(pv)
                self._pvs[pv] = _SiriusPV(pv, connection_callback=connection_callback, connection_timeout=connection_timeout)
                return True
        elif isinstance(pv, _SiriusPV):
            if pv.pv_name not in self._pvs:
                self._pv_names.append(pv.pv_name)
                self._pvs[pv] = pv
                return True
        else:
            raise ValueError
        return False

    def add_callback(self, callback, index):
        """Add callback function to all PVs in the set object.

        Arguments:
        callback -- reference to the callback function
        index    -- an immutable used as a key to the callback being added.
        """
        for pv_name in self._pv_names:
            self._pvs[pv_name].add_callback(callback=callback, index=index)

    def remove(self, pv):
        if isinstance(pv, str):
            if pv in self._pvs:
                self._pv_names.remove(pv)
                del(self._pvs[pv])
        elif isinstance(pv, _SiriusPV):
            if pv.pv_name in self._pvs:
                self._pv_names.remove(pv)
                del(self._pvs[pv.pv_name])

    def disconnect():
        for pv_name in self._pv_names:
            self._pvs[pv_name].disconnect()

    def __len__(self):
        return len(self._pvs)

    def __del__(self):
        for pv_name in self._pv_names:
            del(self._pvs[pv_name])
        self._pv_names = []
