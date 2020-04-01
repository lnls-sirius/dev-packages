"""Simulators factory."""

import re as _re

from ..namesys import split_name as _split_name

from .simps import SimPSTypeModel as _SimPSTypeModel
from .simps import SimPUTypeModel as _SimPUTypeModel


class _SimFactoryData:
    """."""

    # NOTE: To add a new simulator append an item in this dictionary
    # and implement corresponding method. Note that order in dictionary
    # is important!

    SIMCLASS_2_CREATE = {
        _SimPSTypeModel: '_simpstypemodel',
        _SimPUTypeModel: '_simpstypemodel',
        }

    @staticmethod
    def _simpstypemodel(simclass, pvname,):
        """Create simulator for Sim(PS|PU)TypeModel and return check."""
        # Create branch
        kwargs = _split_name(pvname)
        devname = kwargs['device_name']
        typemodel = simclass.conv_psname2typemodel(devname)
        simulator = simclass(*typemodel)
        pv_in_sim = simulator.pv_check(pvname)
        return simulator, pv_in_sim


class SimFactory(_SimFactoryData):
    """Simulations factory."""

    @staticmethod
    def create(pvnames, sims=None):
        """Create or add simulators to the oringinal set.

        Parameters
        pvnames : iterable with devnames and/or pvnames.
        sims : set of existing simulators to be updated.

        """
        if isinstance(pvnames, str):
            pvnames = [pvnames]

        if sims is None:
            sims = set()

        for pvname in pvnames:
            if not SimFactory._add_pvname(pvname, sims):
                raise ValueError('Simulator not found for "{}"'.format(pvname))

        return sims

    @staticmethod
    def _add_pvname(pvname, sims):
        simtypes = {type(sim) for sim in sims}
        for simclass, func in _SimFactoryData.SIMCLASS_2_CREATE.items():
            method = getattr(_SimFactoryData, func)
            # create simulator
            sim, pv_in_sim = method(simclass, pvname)
            if pv_in_sim:
                if simclass in simtypes:
                    # simulator type already in set
                    return True
                # add simulator to set
                sims.add(sim)
                simtypes.add(simclass)
                return True
        return False
