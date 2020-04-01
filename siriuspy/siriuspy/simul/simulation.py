"""Simulation."""

import re as _re


class Simulation:
    """Simulation class.

        This simulation class manages simulated epics control process
    variables by registered simulator objects. As a simulator is registered,
    its 'callback_pv_dbase' is executed in order to retrieve the simulator
    dictionary of pvname regular and epics database objects.

        When a SimPV is registered in the simulation, the existing set of
    regular expressions is searched for matches. Simulators that registered
    mathcing regexps are flaged so that callback methods are executed when that
    SimPV is registered or when its state changes (register/get/put actions).
    """

    PV_DATABASE_UNIQUE = True

    _REGEXP = list()  # pvname regular expression
    _SIMULS = list()  # registered simulators
    _DBASES = list()  # associated epics databases
    _SIMPVS = dict()  # registered SimPVs

    # --- registration methods ---

    @staticmethod
    def simulator_register(simulator):
        """Register simulator(s) in simulation."""
        if not isinstance(simulator, (tuple, list, set)):
            simulator = (simulator, )
        for sim in simulator:
            pvname_regexp = sim.callback_pv_dbase()
            for regexp, dbase in pvname_regexp.items():
                Simulation._pvnames_register(sim, regexp, dbase)

    @staticmethod
    def simulator_unregister(simulator):
        """Unregister simulator(s)."""
        if not isinstance(simulator, (tuple, list, set)):
            simulator = (simulator, )
        regexp, sims, dbases = list(), list(), list()
        for rege, sim, dbas in zip(
                Simulation._REGEXP,
                Simulation._SIMULS,
                Simulation._DBASES):
            if sim not in simulator:
                regexp.append(rege)
                sims.append(sim)
                dbases.append(dbas)
        Simulation._REGEXP, Simulation._SIMULS, Simulation._DBASES = \
            regexp, sims, dbases

    # --- PV methods (used mainly in SimPV methods) ---

    @staticmethod
    def pv_register(pvobj):
        """Register SimPV object.

        This is used by SimPV when a sim PV is created.
        """
        pvname = pvobj.pvname
        if pvname in Simulation._SIMPVS:
            # return False if SimPV already registered.
            return False
        sims = Simulation.find_simulators(pvname)
        Simulation._SIMPVS[pvname] = (pvobj, sims)
        # execute simulators callback
        for sim in sims:
            sim.callback_pv_register(pvobj)
        return True

    @staticmethod
    def pv_get(pvname, **kwargs):
        """Execute simulators callback functions, prior to SimPV readout.

        Used in SimPV getter methods.
        """
        _, sims, *_ = Simulation._SIMPVS[pvname]
        for sim in sims:
            sim.callback_pv_get(pvname, **kwargs)

    @staticmethod
    def pv_put(pvname, value, **kwargs):
        """Execute simulators callback functions, prior to SimPV setpoint.

        Used in SimPV setter methods. Simulator callback functions must
        return True if setpoint is acceptable in all simulators,
        False otherwise.
        """
        _, sims, *_ = Simulation._SIMPVS[pvname]
        state = True
        for sim in sims:
            state &= sim.callback_pv_put(pvname, value, **kwargs)
        return state

    @staticmethod
    def pv_find(pvname):
        """Return SimPV object.

        Used in SimPV to decide if a new SimPV is needed.
        """
        pv_item = Simulation._SIMPVS.get(pvname, None)
        if not pv_item:
            return None
        pvobj, *_ = pv_item
        return pvobj

    @staticmethod
    def pv_dbase_find(pvname, unique=False):
        """Return databases for a given psname.

        Used in SimPV with unique=True to get the first pvname matching
        database.
        """
        dbases = Simulation._find(pvname, Simulation._DBASES, unique=False)
        if Simulation.PV_DATABASE_UNIQUE and len(dbases) > 1:
            raise ValueError(
                'Database for PV "{}" is not unique!'.format(pvname))
        if not dbases:
            return None
        if unique:
            return dbases.pop()
        return dbases

    # --- utility methods (used mainly in Simulator implementations) ---

    @staticmethod
    def pvnames(simulator=None):
        """Return pvnames of registered SimPVs of a given simulator."""
        if simulator is None:
            return set(Simulation._SIMPVS.keys())
        pvnames = set()
        for pvobj, sims in Simulation._SIMPVS:
            for sim in sims:
                if sim == simulator:
                    pvnames.add(pvobj.pvname)
                    break
        return pvnames

    @staticmethod
    def reset():
        """Reset simulation."""
        for sim in Simulation._SIMULS:
            sim.reset()
        Simulation._init()

    @staticmethod
    def find_simulators(pvname, unique=False):
        """Return simulators for a given pvname."""
        return Simulation._find(pvname, Simulation._SIMULS, unique)

    @staticmethod
    def update_simulators(pvname, **kwargs):
        """Execute callback to update/synchronize simulator for pvname."""
        _, sims, *_ = Simulation._SIMPVS[pvname]
        for sim in sims:
            sim.update(pvname, **kwargs)

    @staticmethod
    def check_pvname(pvname):
        """Return True of pvname is registered in simulation."""
        if Simulation.find_simulators(pvname, True):
            return True
        if Simulation.pv_find(pvname):
            return True
        return False

    # --- private methods ---

    @staticmethod
    def _init():
        """Init Simulation class structures."""
        Simulation._REGEXP = list()
        Simulation._SIMULS = list()
        Simulation._DBASES = list()
        Simulation._SIMPVS = dict()

    @staticmethod
    def _find(pvname, itemlist, unique):
        set_ = list()
        for rege, item in zip(Simulation._REGEXP, itemlist):
            if rege.match(pvname):
                set_.append(item)
        try:
            set_ = set(set_)
        except TypeError:
            pass

        if unique and len(set_) > 1:
            # if unique and more than one item, raise exception.
            raise ValueError(
                'Conflicting items for pvname "{}"'.format(pvname))
        if unique:
            # if unique and non-empty return item object,
            return set_.pop() if set_ else set_

        return set_

    @staticmethod
    def _pvnames_register(simulator, pvnames_regexp, dbase):
        """Register simulator pvnames regular expressions."""
        Simulation._REGEXP.append(_re.compile(pvnames_regexp))
        Simulation._SIMULS.append(simulator)
        Simulation._DBASES.append(dbase)
