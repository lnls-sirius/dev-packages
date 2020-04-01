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

    # TODO: make class thread-safe!

    # pvnames can math only one regexp/simulator?
    PV_DATABASE_UNIQUE = True

    # stores register on/off state
    _register_state = True

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

    @staticmethod
    def register_state_get():
        """Return registration state."""
        return Simulation._register_state

    @staticmethod
    def register_state_set_on():
        """Set simulation to accept registration of SimPVs."""
        Simulation._register_state = True

    @staticmethod
    def register_state_set_off():
        """Set simulation not to accept registration of SimPVs."""
        Simulation._register_state = False

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
        sims = set(Simulation.simulator_find(pvname))
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
    def get_pvnames(simulator=None):
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
    def simulator_find(pvname, unique=False):
        """Return simulators set for a given pvname."""
        set_ = set()
        for sim in Simulation._SIMULS:
            if sim.pv_check(pvname):
                set_.add(sim)
        return set_.pop() if unique and set_ else set_

    @staticmethod
    def simulator_update(pvname, **kwargs):
        """Execute callback to update/synchronize simulator for pvname."""
        _, sims, *_ = Simulation._SIMPVS[pvname]
        for sim in sims:
            sim.update(pvname, **kwargs)

    @staticmethod
    def pv_check(pvname):
        """Return True of SimPV is registered in simulation."""
        return \
            Simulation._register_state and (
                Simulation.simulator_find(pvname, True) or
                Simulation.pv_find(pvname))

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
        list_ = list()
        for rege, item in zip(Simulation._REGEXP, itemlist):
            if rege.match(pvname):
                list_.append(item)

        # if unique and more than one item, raise exception.
        if unique and len(list_) > 1:
            raise ValueError(
                'Conflicting items for pvname "{}"'.format(pvname))

        # return list
        return list_.pop() if unique and list_ else list_

    @staticmethod
    def _pvnames_register(simulator, pvnames_regexp, dbase):
        """Register simulator pvnames regular expressions."""
        Simulation._REGEXP.append(_re.compile(pvnames_regexp))
        Simulation._SIMULS.append(simulator)
        Simulation._DBASES.append(dbase)
