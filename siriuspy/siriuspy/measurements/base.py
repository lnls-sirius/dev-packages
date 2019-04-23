

class BaseClass:

    def __init__(self):
        self._map2read = self.get_map2read()
        self._map2write = self.get_map2write()

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
