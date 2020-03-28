"""State Simulator."""

import re as _re
import random as _random
import numpy as _np

from ..search import PSSearch as _PSSearch
from ..pwrsupply.csdev import get_ps_propty_database as _get_database

from .sim import Sim as _Sim


# NOTE: This is a toymodel PowerSupply simulator, just to test the
# Simulator infrastructure. Other PVs such as PwrState-* and
# OpMode-* should be added!

class SimPowerSupply(_Sim):
    """Power supply current simulator."""

    _setpoint_regexp = _setpoint_regexp = _re.compile('^.*-(SP|Sel|Cmd)$')

    _properties = (
        'PwrState-Sel', 'PwrState-Sts',
        'OpMode-Sel', 'OpMode-Sts',
        'Current-SP', 'Current-RB',
        'CurrentRef-Mon', 'Current-Mon',
        'SOFBCurrent-SP', 'SOFBCurrent-RB',
        'SOFBCurrentRef-Mon', 'SOFBCurrent-Mon',
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
        if not SimPowerSupply._setpoint_regexp.match(pvname):
            return False

        # synchronize other current PVs
        self.callback_update(pvname=pvname, value=value, **kwargs)

        # Return status that setpoint was applied
        return True

    def callback_update(self, **kwargs):
        """Execute synchronization of simulation.

        At this point, synchronization of Current propties.
        """
        # get setpoints
        if 'pvname' in kwargs:
            pvname = kwargs['pvname']
            setpoints = dict()
            setpoints[pvname] = kwargs['value']
        else:
            setpoints = self._get_setpoint_properties()

        # synchronize Current PVs
        for sp_pvname, sp_value in setpoints.items():
            if '-SP' in sp_pvname:
                pvn = sp_pvname.replace('-SP', '-RB')
                if pvn in self:
                    self.pv_value_put(pvn, sp_value)
                pvn = sp_pvname.replace('-SP', 'Ref-Mon')
                if pvn in self:
                    self.pv_value_put(pvn, sp_value)
                pvn = sp_pvname.replace('-SP', '-Mon')
                if pvn in self:
                    if isinstance(sp_value, _np.ndarray):
                        rnd = _np.random.uniform(
                            1-0.001, 1+0.001, len(sp_value))
                    else:
                        rnd = _random.uniform(1-0.001, 1+0.001)
                    self.pv_value_put(pvn, sp_value * rnd)
            elif '-Sel' in sp_pvname:
                pvn = sp_pvname.replace('-Sel', '-Sts')
                if pvn in self:
                    self.pv_value_put(pvn, sp_value)

    # --- private methods ---

    def _set_dbase_regexp(self):
        pstype = _PSSearch.conv_psname_2_pstype(self._psname)
        psmodel = _PSSearch.conv_psname_2_psmodel(self._psname)
        dbpvs = _get_database(psmodel, pstype)
        for propty in self._properties:
            if propty in dbpvs:
                dbase = dbpvs[propty]
                pvname_regexp = '.*:' + propty
                super().pv_database_regexp_add(pvname_regexp, dbase)
        return pstype, psmodel

    def _get_setpoint_properties(self):
        setpoints = dict()
        for pvname in self.pvnames:
            if SimPowerSupply._setpoint_regexp.match(pvname):
                setpoints[pvname] = self.pv_get(pvname).value
        return setpoints
