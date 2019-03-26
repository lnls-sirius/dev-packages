#!/usr/local/bin/python-sirius
"""PS Diag PVs."""

from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.pwrsupply import ETypes as _ETypes
from siriuspy.computer import Computer


class PSDiffPV(Computer):
    """Diff of a PS current setpoint and a readback."""

    CURRT_SP = 0
    CURRT_MON = 1

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute difference between SP and Mon current values."""
        disconnected = \
            not computed_pv.pvs[PSDiffPV.CURRT_SP].connected or \
            not computed_pv.pvs[PSDiffPV.CURRT_MON].connected
        if disconnected:
            return None
        sp = computed_pv.pvs[PSDiffPV.CURRT_SP].value
        rb = computed_pv.pvs[PSDiffPV.CURRT_MON].value
        diff = rb - sp
        return {'value': diff}

    def compute_put(self, computed_pv, value):
        """Not needed."""

    def compute_limits(self, computed_pv, updated_pv_name=None):
        """Not needed."""


class PSStatusPV(Computer):
    """Power Supply Status PV."""

    # TODO: Add other interlocks for some PS types

    BIT_DISCONNTD = 0b00000001
    BIT_OPMODEDIF = 0b00000010
    BIT_CURRTDIFF = 0b00000100
    BIT_INTLKSOFT = 0b00001000
    BIT_INTLKHARD = 0b00010000

    OPMODE_SEL = 0
    OPMODE_STS = 1
    CURRT_DIFF = 2
    INTLK_SOFT = 3
    INTLK_HARD = 4

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute PS Status PV."""
        value = 0
        # connected?
        disconnected = \
            not computed_pv.pvs[PSStatusPV.OPMODE_SEL].connected or \
            not computed_pv.pvs[PSStatusPV.OPMODE_STS].connected or \
            not computed_pv.pvs[PSStatusPV.CURRT_DIFF].connected or \
            not computed_pv.pvs[PSStatusPV.INTLK_SOFT].connected or \
            not computed_pv.pvs[PSStatusPV.INTLK_HARD].connected
        if disconnected:
            value |= PSStatusPV.BIT_DISCONNTD
            return {'value': value}

        sel = computed_pv.pvs[PSStatusPV.OPMODE_SEL].value
        sts = computed_pv.pvs[PSStatusPV.OPMODE_STS].value
        if sel is not None and sts is not None:
            # opmode comparison
            opmode_sel = _ETypes.OPMODES[sel]
            opmode_sts = _ETypes.STATES[sts]
            if opmode_sel != opmode_sts:
                value |= PSStatusPV.BIT_OPMODEDIF
            # current diff
            if opmode_sts == _PSConst.States.SlowRef:
                severity = computed_pv.pvs[PSStatusPV.CURRT_DIFF].severity
                if severity != 0:
                    value |= PSStatusPV.BIT_CURRTDIFF
        else:
            value |= PSStatusPV.BIT_OPMODEDIF
        # interlock soft
        intlksoft = computed_pv.pvs[PSStatusPV.INTLK_SOFT].value
        if intlksoft != 0 or intlksoft is None:
            value |= PSStatusPV.BIT_INTLKSOFT
        # interlock hard
        intlkhard = computed_pv.pvs[PSStatusPV.INTLK_HARD].value
        if intlkhard != 0 or intlkhard is None:
            value |= PSStatusPV.BIT_INTLKHARD
        return {'value': value}

    def compute_put(self, computed_pv, value):
        """Not needed."""

    def compute_limits(self, computed_pv, updated_pv_name=None):
        """Not needed."""
