"""Base Simulator."""

import re as _re
import random as _random
from abc import ABC, abstractmethod
import numpy as _np

from .simpv import SimPV as _PVSim


class Sim(ABC):
    """Simulator.

    Independent and markovian PVs simulator,

    dbase_default : epics database used as default if no other dbase
                    is defined with pvname patterns with 'dbase_insert_regexp'

    """

    def __init__(self, dbase_default=None):
        """."""
        if dbase_default is None:
            dbase_default = {'type': 'float', 'value': 0}
        self._dbase_default = dbase_default
        self._pvs = dict()
        self._dbase_regexp = list()

    # --- abstract classes that subclasses MUST implement ---

    @abstractmethod
    def callback_get(self, pvname, **kwargs):
        """Execute callback function prior to SimPV readout."""

    @abstractmethod
    def callback_set(self, pvname, value, **kwargs):
        """Execute callback function prior to SimPV setpoint.

        Return True if setpoint is acceptable, False otherwise.
        """

    @abstractmethod
    def callback_add_pv(self, sim_pvobj):
        """Execute callback method after a new SimPV is added to simulator."""

    @abstractmethod
    def callback_update(self, **kwargs):
        """Execute callback to update/synchronize simulator."""

    # --- general methods ---

    @property
    def pvnames(self):
        """Return name of SimPVs."""
        return tuple(pvname for pvname in self._pvs)

    @property
    def values(self):
        """Return a dict with pvnames and associated values."""
        vals = dict()
        for pvname, pvobj in self._pvs.items():
            vals[pvname] = pvobj.value
        return vals

    def pv_obj_get(self, pvname):
        """Return SimPV object."""
        return self._pvs[pvname]

    def pv_obj_add(self, sim_pvobj):
        """Add SimPV to simulator."""
        # check if pvobj is of type SimPV
        if not isinstance(sim_pvobj, _PVSim):
            raise TypeError

        # Add SimPV to internal dictionary.
        self._pvs[sim_pvobj.pvname] = sim_pvobj

        # invoke callback
        self.callback_add_pv(sim_pvobj)

    def pv_value_get(self, pvname):
        """Get SimPV value without invoking simulator callback."""
        return self._pvs[pvname].sim_get()

    def pv_value_put(self, pvname, value):
        """Set SimPV value without invoking simulator callback."""
        self._pvs[pvname].sim_put(value)

    def pv_database_get(self, pvname):
        """Return epics database for a SimPV."""
        for regexp, dbase in self._dbase_regexp:
            if regexp.match(pvname):
                return dbase
        if self._dbase_default:
            return self._dbase_default

        raise ValueError('No database defined for SimPV "{}" !'.format(pvname))

    def pv_database_regexp_add(self, pvname_regexp, dbase):
        """Add filter to be user to apply database to pvnames."""
        regexp = _re.compile(pvname_regexp)
        self._dbase_regexp.append((regexp, dbase))

    def pv_database_regexp_get(self):
        """Return filters to be user to apply database to pvnames."""
        return self._dbase_regexp

    def __contains__(self, pvname):
        """Return True if SimPV is in simulator."""
        return pvname in self._pvs

    # --- utility methods ---

    @staticmethod
    def util_add_fluctuations(value, relative=0, absolute=0):
        """."""
        if isinstance(value, _np.ndarray):
            rnd_rel = _np.random.uniform(
                1-relative, 1+relative, len(value)) if relative else 1
            rnd_abs = _np.random.uniform(
                -absolute, +absolute, len(value)) if absolute else 0
        else:
            rnd_rel = _random.uniform(
                1-relative, 1+relative) if relative else 1
            rnd_abs = _random.uniform(
                -absolute, +absolute) if absolute else 0

        value_new = value * rnd_rel + rnd_abs
        return value_new
