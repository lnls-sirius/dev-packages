"""Simulated PV."""


from ..namesys import SiriusPVName as _SiriusPVName
from ..epics.pv_fake import add_to_database as _add_to_database
from ..epics.pv_fake import PVFake as _PVFake


class SimPV(_PVFake):
    """."""

    # This  dictionary contains all SimPV objects in simulation.
    PVS = dict()

    def __new__(cls, pvname, *args, **kwargs):
        """Return existing SimPV object or return a new one."""
        _, _ = args, kwargs  # throwaway arguments
        pvname = _SiriusPVName(pvname)
        if pvname in SimPV.PVS:
            instance = SimPV.PVS[pvname]
        else:
            instance = super(SimPV, cls).__new__(cls)
        return instance

    def __init__(
            self, pvname, simul, **kwargs):
        """."""
        # if object already exists, no initialization needed.
        if pvname in SimPV.PVS:
            return

        # add object to PVs
        SimPV.PVS[pvname] = self

        # --- initializations ---

        self._simul = simul

        # get pv database
        dbase = dict()
        dbase[pvname] = self._simul.pv_database_get(pvname)

        # init pv database
        _add_to_database(dbase, '')

        # call base class constructor
        super().__init__(pvname, **kwargs)

        # add this pvsim to simul
        self._simul.pv_obj_add(self)

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
        status = self._simul.callback_set(self.pvname, value, **kwargs)
        if status:
            super().put(value, **kwargs)

    def sim_get(self):
        """Get SimPV value without invoking simulator callback."""
        return super().get()

    def sim_put(self, value):
        """Set SimPV value without invoking simulator callback."""
        super().put(value)
