#!/usr/local/bin/python-sirius
"""PS Diag PVs."""

from siriuspy.csdevice.pwrsupply import Const as _PSConst
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

    BIT_PSCONNECT = 0b00000001
    BIT_MACONNECT = 0b00000010
    BIT_PSMACOMOK = 0b00000100
    BIT_PWRSTATON = 0b00001000
    BIT_OPMDSLWRF = 0b00010000
    BIT_CURRTDIFF = 0b00100000
    BIT_INTERLKOK = 0b01000000

    PWRSTE_STS = 0
    INTLK_SOFT = 1
    INTLK_HARD = 2
    OPMODE_STS = 3
    CURRT_DIFF = 4
    MAOPMD_SEL = 5
    PSCONN_MON = 6

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute PS Status PV."""
        value = 0
        # ps connected?
        disconnected = \
            not computed_pv.pvs[PSStatusPV.PWRSTE_STS].connected or \
            not computed_pv.pvs[PSStatusPV.INTLK_SOFT].connected or \
            not computed_pv.pvs[PSStatusPV.INTLK_HARD].connected or \
            not computed_pv.pvs[PSStatusPV.OPMODE_STS].connected or \
            not computed_pv.pvs[PSStatusPV.CURRT_DIFF].connected
        if disconnected:
            value |= PSStatusPV.BIT_PSCONNECT
            value |= PSStatusPV.BIT_PWRSTATON
            value |= PSStatusPV.BIT_INTERLKOK
            value |= PSStatusPV.BIT_OPMDSLWRF
            value |= PSStatusPV.BIT_CURRTDIFF
            return {'value': value}

        # ma connected?
        disconnected = \
            not computed_pv.pvs[PSStatusPV.MAOPMD_SEL].connected
        if disconnected:
            value |= PSStatusPV.BIT_MACONNECT
            value |= PSStatusPV.BIT_PSMACOMOK
        else:
            # ps-ma comm ok?
            psconn = computed_pv.pvs[PSStatusPV.PSCONN_MON].value
            if psconn is None or psconn == 0:
                value |= PSStatusPV.BIT_PSMACOMOK

        # pwrstate?
        pwrsts = computed_pv.pvs[PSStatusPV.PWRSTE_STS].value
        if pwrsts != _PSConst.PwrStateSts.On or pwrsts is None:
            value |= PSStatusPV.BIT_PWRSTATON

        # opmode?
        opmsts = computed_pv.pvs[PSStatusPV.OPMODE_STS].value
        if opmsts is not None:
            if opmsts != _PSConst.States.SlowRef:
                value |= PSStatusPV.BIT_OPMDSLWRF
            # current-diff?
            else:
                severity = computed_pv.pvs[PSStatusPV.CURRT_DIFF].severity
                if severity != 0:
                    value |= PSStatusPV.BIT_CURRTDIFF
        else:
            value |= PSStatusPV.BIT_OPMDSLWRF

        # interlocks?
        intlksoft = computed_pv.pvs[PSStatusPV.INTLK_SOFT].value
        intlkhard = computed_pv.pvs[PSStatusPV.INTLK_HARD].value
        if intlksoft != 0 or intlksoft is None or \
                intlkhard != 0 or intlkhard is None:
            value |= PSStatusPV.BIT_INTERLKOK
        return {'value': value}

    def compute_put(self, computed_pv, value):
        """Not needed."""

    def compute_limits(self, computed_pv, updated_pv_name=None):
        """Not needed."""
