"""Base Simulator."""

import random as _random
from abc import ABC, abstractmethod
import numpy as _np

from . import DBASE_DEFAULT as _DBASE_DEF


class Simulator(ABC):
    """Simulator.

    Independent and markovian PVs simulator,

    dbase_default : epics database used as default if no other dbase
                    for pvname regular expression is initialized.

    """

    class Utils:
        """Utils class."""

        @staticmethod
        def add_fluctuations(value, relative=0, absolute=0):
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

    _DBASE_DEFAULT = _DBASE_DEF

    def __init__(self, dbase_default=None):
        """."""
        self._dbase_default = \
            dbase_default if dbase_default else Simulator._DBASE_DEFAULT

        # simulator stores it own dict of
        # used SimPVs for optimization
        self._pvs = dict()

    # --- abstract classes that subclasses MUST implement ---

    @abstractmethod
    def callback_pv_dbase(self):
        """Return dict of pvname regular expression and database.

        This method is called when simulator is registered in simulation.
        """

    @abstractmethod
    def callback_pv_add(self, pvname):
        """Execute callback method after a new SimPV is added to simulator.

        This method is called when a new SimPV is created and it is used in
        the simulator, as implicit defined in dbase initializations.
        """

    @abstractmethod
    def callback_pv_get(self, pvname, **kwargs):
        """Execute callback function prior to SimPV readout.

        This method is called when a SimPV value is requested.
        """

    @abstractmethod
    def callback_pv_put(self, pvname, value, **kwargs):
        """Execute callback function prior to SimPV setpoint.

        Return True if setpoint is acceptable, False otherwise.
        """

    @abstractmethod
    def callback_update(self, **kwargs):
        """Execute callback to update/synchronize simulator.

        This method is called when simulation state update is required.
        """

    # --- general methods ---

    @property
    def pvnames(self):
        """Return name of SimPVs of simulator."""
        return set(self._pvs.keys())

    @property
    def values(self):
        """Return dict with pvnames and associated values of simulator."""
        vals = dict()
        for pvname in self._pvs:
            vals[pvname] = self.pv_value_get(pvname)
        return vals

    def pv_check(self, pvname):
        """Check if SimPV belongs to simulator."""
        dbases = self.callback_pv_dbase()
        for regexp in dbases:
            if regexp.match(pvname):
                return True
        return False

    def pv_value_get(self, pvname):
        """Get SimPV value without invoking simulator callback."""
        return self._pvs[pvname].get_sim()

    def pv_value_put(self, pvname, value):
        """Set SimPV value without invoking simulator callback."""
        self._pvs[pvname].put_sim(value)

    def update(self, **kwargs):
        """Update simulator."""
        self.callback_update(**kwargs)

    def reset(self):
        """Reset simulator."""
        self._pvs = dict()

    def __contains__(self, pvname):
        """Return True if SimPV is in simulator."""
        return pvname in self._pvs

    # --- private methods ---

    # NOTE: not a _-private method, but its use should be,
    # accessable only by friend class Simulation.
    def callback_pv_register(self, pvobj):
        """Register SimPB.

        This method is be used solenely by Simulation class methods.
        """
        pvname = pvobj.pvname
        self._pvs[pvname] = pvobj
        self.callback_pv_add(pvname)
