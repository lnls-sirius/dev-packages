"""Simulation."""

import re as _re


class Simulation:
    """Simulation class."""

    # lists of pvnames regexp, databases and corresponding simulators
    _REGEXP = list()
    _SIMULS = list()
    _DBASES = list()

    # simulated PVs
    _SIMPVS = dict()

    @staticmethod
    def pvnames(simulator=None):
        """Return pvnames of registered SimPVs of a given simulator."""
        if simulator is None:
            return list(Simulation._SIMPVS.keys())
        pvnames = list()
        for pvobj, simuls in Simulation._SIMPVS:
            for simul in simuls:
                if simul == simulator:
                    pvnames.append(pvobj.pvname)
                    break
        return pvnames

    @staticmethod
    def pv_register(pvobj):
        """Register SimPV object."""
        pvname = pvobj.pvname
        if pvname in Simulation._SIMPVS:
            # return False if SimPV already registered.
            return False
        simuls = Simulation.simulator_find(pvname)
        Simulation._SIMPVS[pvname] = (pvobj, simuls)
        # execute simulators callback
        for simul in simuls:
            simul.pv_register(pvobj)
        return True

    @staticmethod
    def pv_find(pvname):
        """Return SimPV object."""
        pv_item = Simulation._SIMPVS.get(pvname, None)
        if not pv_item:
            return None
        pvobj, *_ = pv_item
        return pvobj

    @staticmethod
    def pv_callback_get(pvname, **kwargs):
        """Execute callback function prior to SimPV readout."""
        _, simuls, *_ = Simulation._SIMPVS[pvname]
        for simul in simuls:
            simul.callback_pv_get(pvname, **kwargs)

    @staticmethod
    def pv_callback_put(pvname, value, **kwargs):
        """Execute callback function prior to SimPV setpoint.

        Return True if setpoint is acceptable, False otherwise.
        """
        _, simuls, *_ = Simulation._SIMPVS[pvname]
        state = True
        for simul in simuls:
            state &= simul.callback_pv_put(pvname, value, **kwargs)
        return state

    @staticmethod
    def pv_callback_update(pvname, **kwargs):
        """Execute callback to update/synchronize simulator."""
        _, simuls, *_ = Simulation._SIMPVS[pvname]
        for simul in simuls:
            simul.callback_update(pvname, **kwargs)

    @staticmethod
    def pvnames_register(simulator, pvnames_regexp, dbase):
        """Register simulator pvnames regular expressions."""
        Simulation._REGEXP.append(_re.compile(pvnames_regexp))
        Simulation._SIMULS.append(simulator)
        Simulation._DBASES.append(dbase)

    @staticmethod
    def simulator_register(simulator):
        """Register simulator in simulation."""
        pvname_regexp = simulator.init_pvname_dbase()
        for regexp, dbase in pvname_regexp.items():
            Simulation.pvnames_register(simulator, regexp, dbase)

    @staticmethod
    def simulator_unregister(simulator):
        """Unregister simulator."""
        regexp, simuls = list(), list()
        for rege, simu in zip(Simulation._REGEXP, Simulation._SIMULS):
            if simu != simulator:
                regexp.append(rege)
                simuls.append(simu)
        Simulation._REGEXP, Simulation._SIMULS = regexp, simuls

    @staticmethod
    def simulator_find(pvname, unique=False):
        """Return simulators for a given pvname."""
        return Simulation._find(pvname, Simulation._SIMULS, unique)

    @staticmethod
    def dbase_find(pvname, unique=False):
        """Return databases for a given psname."""
        return Simulation._find(pvname, Simulation._DBASES, unique)

    @staticmethod
    def _find(pvname, itemlist, unique):
        itemset = list()
        for rege, item in zip(Simulation._REGEXP, itemlist):
            if rege.match(pvname):
                itemset.append(item)
        try:
            itemset = set(itemset)
        except TypeError:
            pass

        if unique and len(itemset) > 1:
            # if unique and more than one item, raise exception.
            raise ValueError(
                'Conflicting items for pvname "{}"'.format(pvname))
        if unique:
            # if unique and non-empty return item object,
            return itemset.pop() if itemset else itemset

        return itemset
