
import epics as _epics


class SiriusPV(_epics.PV):

    def __init__(self, pv_name, connection_callback=None, connection_timeout=None, verbose=False):

        self._pv_name = pv_name
        super().__init__(pv_name,
                         connection_callback=connection_callback,
                         connection_timeout=connection_timeout,
                         verbose=verbose)

    @property
    def value_enum(self):
        if not self.connected:
            return None
        if super().type == 'time_enum':
            return super().enum_strs[super().value]
        else:
            return super().value

    @value_enum.setter
    def value_enum(self, value):
        if not self.connected:
            return None
        if super().type == 'time_enum':
            super().put(super().enum_strs.index(value))
        else:
            super().put(value)

    def get(self):
        return super().enum_strs.index(super().value)

    @property
    def pv_name(self):
        return self._pv_name

    @property
    def pv_name_property(self):
        return self.pv_name.split(':')[2]

    @property
    def pv_name_device(self):
        return self.pv_name.split(':')[1]

    @property
    def pv_name_area(self):
        return self.pv_name.split(':')[0]

    @property
    def pv_name_discipline(self):
        return self.pv_name.split(':')[1].split('-')[0]

    def __del__(self):
        super().disconnect()

    def __hash__(self):
        return hash(self._pv_name)
