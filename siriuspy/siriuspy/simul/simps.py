"""State Simulator."""

import random as _random

from ..search import PSSearch as _PSSearch
from ..pwrsupply.csdev import get_ps_propty_database as _get_database

from .sim import Sim as _Sim


# NOTE: This is a toymodel PowerSupply simulator, just to test the
# Simulator infrastructure. Other PVs such as PwrState-* and
# OpMode-* should be added!

class SimPowerSupply(_Sim):
    """Power supply current simulator."""

    _properties = (
        'Current-SP', 'Current-RB', 'CurrentRef-Mon', 'Current-Mon'
        )

    def __init__(self, psname):
        """."""
        self._psname = psname

        # call base class constructor
        super().__init__()

        # set dbase regexp
        self._pstype, self._psmodel = self._set_dbase_regexp()

    @property
    def psname(self):
        """Return psname."""
        return self._psname

    @property
    def pstype(self):
        """Return pstype."""
        return self._pstype

    @property
    def psmodel(self):
        """Return psmodel."""
        return self._psmodel

    # --- Sim interface ---

    def callback_get(self, pvname, **kwargs):
        """Execute base class callback."""

    def callback_set(self, pvname, value, **kwargs):
        """Execute callback setpoint to synchronize SimPVs."""
        # if not -SP pv, does not accept write by returning False
        if not pvname.endswith('-SP'):
            return False

        # synchronize other current PVs
        self.callback_update(pvname=pvname, value=value, **kwargs)

        # Return status that setpoint was applied
        return True

    def callback_update(self, **kwargs):
        """Execute synchronization of simulation.

        At this point, synchronization of Current propties.
        """
        # return if SP PV not in simul.
        pvname_sp = self._get_setpoint_property()
        if not pvname_sp:
            return

        # get current sp value
        if 'pvname' in kwargs and kwargs['pvname'] == pvname_sp:
            value_sp = kwargs['value']
        else:
            value_sp = \
                self.pv_get(pvname_sp).value if pvname_sp in self else None

        # synchronize Current PVs
        pvn = pvname_sp.replace('-SP', '-RB')
        if pvn in self:
            self.pv_value_put(pvn, value_sp)
        pvn = pvname_sp.replace('-SP', 'Ref-Mon')
        if pvn in self:
            self.pv_value_put(pvn, value_sp)
        pvn = pvname_sp.replace('-SP', '-Mon')
        if pvn in self:
            value = value_sp * (1.0 + _random.uniform(-0.001, +0.001))
            self.pv_value_put(pvn, value)

    # --- private methods ---

    def _set_dbase_regexp(self):
        pstype = _PSSearch.conv_psname_2_pstype(self._psname)
        psmodel = _PSSearch.conv_psname_2_psmodel(self._psname)
        dbpvs = _get_database(psmodel, pstype)
        for propty in self._properties:
            dbase = dbpvs[propty]
            pvname_regexp = '.*:' + propty
            super().pv_database_regexp_add(pvname_regexp, dbase)
        return pstype, psmodel

    def _get_setpoint_property(self):
        for pvname in self.pvnames:
            if pvname.endswith('-SP'):
                return pvname
        return None
