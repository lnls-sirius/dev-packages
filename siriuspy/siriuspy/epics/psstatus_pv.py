#!/usr/local/bin/python-sirius
"""PSStatusPV."""

from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.computer import Computer


class PSDiffPV(Computer):
    """Diff of a PS current setpoint and a readback."""

    CURRT_SP = 0
    CURRT_MON = 1

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute difference between SP and Mon current values."""
        connected = \
            computed_pv.pvs[PSDiffPV.CURRT_SP].connected and \
            computed_pv.pvs[PSDiffPV.CURRT_MON].connected
        if not connected:
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

    BIT_CONNECTED = 0b00000001
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
        connected = \
            computed_pv.pvs[PSStatusPV.OPMODE_SEL].connected and \
            computed_pv.pvs[PSStatusPV.OPMODE_STS].connected and \
            computed_pv.pvs[PSStatusPV.CURRT_DIFF].connected and \
            computed_pv.pvs[PSStatusPV.INTLK_SOFT].connected and \
            computed_pv.pvs[PSStatusPV.INTLK_HARD].connected
        if not connected:
            value |= PSStatusPV.BIT_CONNECTED
        # opmode comparison
        opmode_sel = computed_pv.pvs[PSStatusPV.OPMODE_SEL].value
        opmode_sts = computed_pv.pvs[PSStatusPV.OPMODE_STS].value
        if opmode_sel != opmode_sts:
            value |= PSStatusPV.BIT_OPMODEDIF
        # current diff
        if opmode_sts == _PSConst.States.SlowRef or opmode_sel != opmode_sts:
            severity = computed_pv.pvs[PSStatusPV.CURRT_DIFF].severity
            if severity != 0:
                value |= PSStatusPV.BIT_CURRTDIFF
        # interlock soft
        intlksoft = computed_pv.pvs[PSStatusPV.INTLK_SOFT].value
        if intlksoft != 0:
            value |= PSStatusPV.BIT_INTLKSOFT
        # interlock hard
        intlkhard = computed_pv.pvs[PSStatusPV.INTLK_HARD].value
        if intlkhard != 0:
            value |= PSStatusPV.BIT_INTLKHARD
        return {'value': value}

    def compute_put(self, computed_pv, value):
        """Not needed."""

    def compute_limits(self, computed_pv, updated_pv_name=None):
        """Not needed."""
