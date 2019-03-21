#!/usr/local/bin/python-sirius
"""PSCurrenDiffPV."""

from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.computer import Computer


class PSCurrentDiffPV(Computer):
    """Diff of a setpoint and a readback."""

    OPMODE_SEL = 0
    OPMODE_STS = 1
    CURRENT_SP = 2
    CURRENT_MON = 3

    def __init__(self, epsilon):
        """."""
        self._epsilon = epsilon

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compare PVs to check wether they are equal."""
        opmode_sts = computed_pv.pvs[PSCurrentDiffPV.OPMODE_STS].get()
        if opmode_sts != _PSConst.States.SlowRef:  # Slowref
            return {'value': 0}  # Ok
        else:
            sp = computed_pv.pvs[PSCurrentDiffPV.CURRENT_SP].get()
            rb = computed_pv.pvs[PSCurrentDiffPV.CURRENT_MON].get()
            if abs(sp - rb) > self._epsilon:
                return {'value': 1}
            else:
                return {'value': 0}

    def compute_put(self, computed_pv, value):
        """Not needed."""

    def compute_limits(self, computed_pv, updated_pv_name=None):
        """Not needed."""
