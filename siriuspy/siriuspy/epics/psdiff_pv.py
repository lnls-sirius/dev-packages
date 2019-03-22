#!/usr/local/bin/python-sirius
"""PSCurrenDiffPV."""

from siriuspy.computer import Computer


class PSDiffPV(Computer):
    """Diff of a PS current setpoint and a readback."""

    CURRENT_SP = 2
    CURRENT_MON = 3

    def __init__(self, dtol):
        """."""
        self._dtol = dtol

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute difference between SP and Mon current values."""
        connected = \
            computed_pv.pvs[PSDiffPV.CURRENT_SP].connected and \
            computed_pv.pvs[PSDiffPV.CURRENT_MON].connected
        if not connected:
            return {'value': None}
        sp = computed_pv.pvs[PSDiffPV.CURRENT_SP].get()
        rb = computed_pv.pvs[PSDiffPV.CURRENT_MON].get()
        return {'value': rb - sp}

    def compute_put(self, computed_pv, value):
        """Not needed."""

    def compute_limits(self, computed_pv, updated_pv_name=None):
        """Not needed."""
