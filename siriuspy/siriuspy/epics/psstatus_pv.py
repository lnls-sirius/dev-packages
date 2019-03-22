#!/usr/local/bin/python-sirius
"""PSStatusPV."""

from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.computer import Computer


class PSStatusPV(Computer):
    """Power Supply Status PV."""

    # TODO: Add other interlocks for some PS types

    OPMODE_SEL = 0
    OPMODE_STS = 1
    INTLCK_SOFT = 2
    INTLCK_HARD = 3
    CURRENT_DIFF = 4

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute PS Status PV."""
        # connected?
        connected = \
            computed_pv.pvs[PSStatusPV.OPMODE_SEL].connected and \
            computed_pv.pvs[PSStatusPV.OPMODE_STS].connected and \
            computed_pv.pvs[PSStatusPV.INTLCK_SOFT].connected and \
            computed_pv.pvs[PSStatusPV.INTLCK_HARD].connected and \
            computed_pv.pvs[PSStatusPV.CURRENT_DIFF].value is not None
        if not connected:
            return {'value': 1}
        # interlock
        intlck_soft = computed_pv.pvs[PSStatusPV.INTLCK_SOFT].get()
        intlck_hard = computed_pv.pvs[PSStatusPV.INTLCK_HARD].get()
        if intlck_soft != 0 or intlck_hard != 0:
            return {'value': 1}
        # consistent opmode?
        opmode_sel = computed_pv.pvs[PSStatusPV.OPMODE_SEL].get()
        opmode_sts = computed_pv.pvs[PSStatusPV.OPMODE_STS].get()
        if opmode_sts != opmode_sel:
            return {'value': 1}
        # if in slowref, check current-diff
        if opmode_sts != _PSConst.States.SlowRef:
            return {'value': 0}
        else:
            severity = computed_pv.pvs[PSStatusPV.CURRENT_DIFF].severity
            return {'value': 0 if severity == 0 else 1}

    def compute_put(self, computed_pv, value):
        """Not needed."""

    def compute_limits(self, computed_pv, updated_pv_name=None):
        """Not needed."""
