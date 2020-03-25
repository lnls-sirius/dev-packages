"""."""
from ..callbacks import Callback

from .csdev import Const as _Const


class BaseClass(Callback, _Const):

    def __init__(self, callback=None):
        self._map2read = self.get_map2read()
        self._map2write = self.get_map2write()
        super().__init__(callback=callback)

    def get_map2write(self):
        return dict()

    def get_map2read(self):
        return dict()

    def get(self, prop):
        if prop in self._map2read:
            return self._map2read[prop]()
        return self.__getattribute__(prop)

    def read(self, prop):
        return self.get(prop)

    def write(self, prop, value):
        if prop in self._map2write:
            return self._map2write[prop](value)
        try:
            self.__setattr__(prop, value)
        except Exception:
            return False
        return True
