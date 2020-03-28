"""Base Simulator."""

import re as _re

from .simpv import PVSim as _PVSim


class Sim:
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

    def pv_get(self, pvname):
        """Return PVSim object."""
        return self._pvs[pvname]

    def pv_insert(self, sim_pvobj):
        """Add PVSim to simulator."""
        # check if pvobj is of type PVSim
        if not isinstance(sim_pvobj, _PVSim):
            raise TypeError

        # Add PVSim to internal dictionary.
        self._pvs[sim_pvobj.pvname] = sim_pvobj

    def pv_value_put(self, pvname, value):
        """Set PVSim value without invoking simulator callback."""
        self._pvs[pvname].sim_put(value)

    def pv_database_get(self, pvname):
        """Return epics database for a PVSim."""
        for regexp, dbase in self._dbase_regexp:
            if regexp.match(pvname):
                return dbase
        if self._dbase_default:
            return self._dbase_default

        raise ValueError('No database defined for PVSim "{}" !'.format(pvname))

    def pv_database_regexp_add(self, pvname_regexp, dbase):
        """Add filter to be user to apply database to pvnames."""
        regexp = _re.compile(pvname_regexp)
        self._dbase_regexp.append((regexp, dbase))

    def pv_database_regexp_get(self):
        """Return filters to be user to apply database to pvnames."""
        return self._dbase_regexp

    def callback_get(self, pvname, **kwargs):
        """Execute callback function prior to PVSim readout."""
        _, _ = pvname, kwargs  # throwaway away arguments
        return True

    def callback_set(self, pvname, value, **kwargs):
        """Execute callback function prior to PVSim setpoint.

        Return True if setpoint is acceptable, False otherwise.
        """
        _, _, _ = pvname, value, kwargs  # throwaway away arguments
        return True

    def callback_update(self, **kwargs):
        """Execute callback update simulator."""

    def __contains__(self, pvname):
        """Return True if PVSim is in simulator."""
        return pvname in self._pvs
