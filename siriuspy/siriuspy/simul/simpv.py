"""Simulated PV."""


from ..epics.pv_fake import add_to_database as _add_to_database
from ..epics.pv_fake import PVFake as _PVFake


class PVSim(_PVFake):
    """."""

    def __init__(
            self, pvname, simul, **kwargs):
        """."""
        self._simul = simul

        # get pv database
        dbase = dict()
        dbase[pvname] = self._simul.pv_database_get(pvname)

        # init pv database
        _add_to_database(dbase, '')

        # call base class constructor
        super().__init__(pvname, **kwargs)

        # add this pvsim to simul
        self._simul.pv_insert(self)

    @property
    def value(self):
        """."""
        _ = self._simul.callback_get(self.pvname)
        return super().get()

    @value.setter
    def value(self, _value):
        """."""
        status = self._simul.callback_set(self.pvname, _value)
        if status:
            super().put(_value)

    def get(self, **kwargs):
        """."""
        _ = self._simul.callback_get(self.pvname, **kwargs)
        return super().get(**kwargs)

    def put(self, value, **kwargs):
        """."""
        _ = self._simul.callback_set(self.pvname, value, **kwargs)
        return super().put(value, **kwargs)

    def sim_put(self, value):
        """Set PVSim value withouf invoking simulator callback."""
        super().put(value)
