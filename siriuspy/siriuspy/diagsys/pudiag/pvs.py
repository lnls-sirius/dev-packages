#!/usr/local/bin/python-sirius
"""PU Diag PVs."""

from ...namesys import SiriusPVName as _PVName
from ...pwrsupply.csdev import Const as _PSConst


class PUDiffPV:
    """Diff of a PU voltage setpoint and a monitor."""

    VOLTAGE_SP = 0
    VOLTAGE_MON = 1

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute difference between SP and Mon voltage values."""
        disconnected = \
            not computed_pv.pvs[PUDiffPV.VOLTAGE_SP].connected or \
            not computed_pv.pvs[PUDiffPV.VOLTAGE_MON].connected
        if disconnected:
            return None

        value_sp = computed_pv.pvs[PUDiffPV.VOLTAGE_SP].value
        value_rb = computed_pv.pvs[PUDiffPV.VOLTAGE_MON].value
        diff = value_rb - value_sp
        return {'value': diff}


class PUStatusPV:
    """Pulsed Power Supply Status PV."""

    BIT_PUCONNECT = 0b00001
    BIT_PWRSTATON = 0b00010
    BIT_PULSEISON = 0b00100
    BIT_VOLTGDIFF = 0b01000
    BIT_INTERLOCK = 0b10000

    PWRST_STS = 0
    PULSE_STS = 1
    DIFFVOLTG = 2
    INTRLCK_1 = 3
    INTRLCK_2 = 4
    INTRLCK_3 = 5
    INTRLCK_4 = 6
    INTRLCK_5 = 7
    INTRLCK_6 = 8
    INTRLCK_7 = 9
    INTRLCK_8 = 10

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute PU Status PV."""
        puname = _PVName(computed_pv.pvs[0].pvname).device_name
        value = 0
        # connected?
        disconnected = \
            not computed_pv.pvs[PUStatusPV.PWRST_STS].connected or \
            not computed_pv.pvs[PUStatusPV.PULSE_STS].connected or \
            not computed_pv.pvs[PUStatusPV.DIFFVOLTG].connected or \
            not computed_pv.pvs[PUStatusPV.INTRLCK_1].connected or \
            not computed_pv.pvs[PUStatusPV.INTRLCK_2].connected or \
            not computed_pv.pvs[PUStatusPV.INTRLCK_3].connected or \
            not computed_pv.pvs[PUStatusPV.INTRLCK_4].connected or \
            not computed_pv.pvs[PUStatusPV.INTRLCK_5].connected or \
            not computed_pv.pvs[PUStatusPV.INTRLCK_6].connected or \
            not computed_pv.pvs[PUStatusPV.INTRLCK_7].connected
        if 'Sept' not in puname:
            disconnected |= not computed_pv.pvs[PUStatusPV.INTRLCK_8].connected
        if disconnected:
            value |= PUStatusPV.BIT_PUCONNECT
            value |= PUStatusPV.BIT_PWRSTATON
            value |= PUStatusPV.BIT_PULSEISON
            value |= PUStatusPV.BIT_VOLTGDIFF
            value |= PUStatusPV.BIT_INTERLOCK
            return {'value': value}

        # pwrstate?
        pwrsts = computed_pv.pvs[PUStatusPV.PWRST_STS].value
        if pwrsts != _PSConst.OffOn.On or pwrsts is None:
            value |= PUStatusPV.BIT_PWRSTATON
        else:
            # voltage-diff?
            severity = computed_pv.pvs[PUStatusPV.DIFFVOLTG].severity
            if severity != 0:
                value |= PUStatusPV.BIT_VOLTGDIFF

        # pulse?
        pulsests = computed_pv.pvs[PUStatusPV.PULSE_STS].value
        if pulsests != _PSConst.OffOn.On or pulsests is None:
            value |= PUStatusPV.BIT_PULSEISON

        # interlocks?
        intlk1 = computed_pv.pvs[PUStatusPV.INTRLCK_1].value
        intlk2 = computed_pv.pvs[PUStatusPV.INTRLCK_2].value
        intlk3 = computed_pv.pvs[PUStatusPV.INTRLCK_3].value
        intlk4 = computed_pv.pvs[PUStatusPV.INTRLCK_4].value
        intlk5 = computed_pv.pvs[PUStatusPV.INTRLCK_5].value
        intlk6 = computed_pv.pvs[PUStatusPV.INTRLCK_6].value
        intlk7 = computed_pv.pvs[PUStatusPV.INTRLCK_7].value
        cond = intlk1 != 1 or intlk1 is None
        cond |= intlk2 != 1 or intlk2 is None
        cond |= intlk3 != 1 or intlk3 is None
        cond |= intlk4 != 1 or intlk4 is None
        cond |= intlk5 != 1 or intlk5 is None
        cond |= intlk6 != 1 or intlk6 is None
        cond |= intlk7 != 1 or intlk7 is None
        if 'Sept' not in puname:
            intlk8 = computed_pv.pvs[PUStatusPV.INTRLCK_8].value
            cond |= intlk8 != 1 or intlk8 is None
        if cond:
            value |= PUStatusPV.BIT_INTERLOCK

        return {'value': value}
