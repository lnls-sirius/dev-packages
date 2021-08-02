#!/usr/local/bin/python-sirius
"""LI Diag PVs."""

import numpy as _np

from .csdev import Const as _Const


class LIScalarDiffPV:
    """Diff of a LI setpoint and a readback PVs."""

    SP = 0
    RB = 1

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute difference between SP and RB values."""
        disconnected = \
            not computed_pv.pvs[LIScalarDiffPV.SP].connected or \
            not computed_pv.pvs[LIScalarDiffPV.RB].connected
        if disconnected:
            return None
        value_sp = computed_pv.pvs[LIScalarDiffPV.SP].value
        value_rb = computed_pv.pvs[LIScalarDiffPV.RB].value
        diff = value_rb - value_sp
        return {'value': diff}


class LIVecDiffPV:
    """Diff of a LI setpoint and a readback PVs."""

    I_SETT = 0
    Q_SETT = 1
    I_DATA = 2
    Q_DATA = 3

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute difference between SP and RB values."""
        disconnected = \
            not computed_pv.pvs[LIVecDiffPV.I_SETT].connected or \
            not computed_pv.pvs[LIVecDiffPV.Q_SETT].connected or \
            not computed_pv.pvs[LIVecDiffPV.I_DATA].connected or \
            not computed_pv.pvs[LIVecDiffPV.Q_DATA].connected
        if disconnected:
            return None
        sp_i = computed_pv.pvs[LIVecDiffPV.I_SETT].value
        sp_q = computed_pv.pvs[LIVecDiffPV.Q_SETT].value
        sp_vec = _np.array([sp_i, sp_q])
        rb_i = computed_pv.pvs[LIVecDiffPV.I_DATA].value
        rb_q = computed_pv.pvs[LIVecDiffPV.Q_DATA].value
        rb_vec = _np.array([rb_i, rb_q])
        diff = _np.linalg.norm(rb_vec - sp_vec)
        return {'value': diff}


class LIRFStatusPV:
    """LI RF Status PV."""

    BIT_DISCONN = 0b00000001
    BIT_STATOFF = 0b00000010
    BIT_TRIGOFF = 0b00000100
    BIT_INTGOFF = 0b00001000
    BIT_FBMDOFF = 0b00010000
    BIT_AMPDIFF = 0b00100000
    BIT_PHSDIFF = 0b01000000
    BIT_IXQDIFF = 0b10000000

    PV_STREAM = 0
    PV_EXTTRG = 1
    PV_INTEGR = 2
    PV_FBMODE = 3
    PV_AMPDIF = 4
    PV_PHSDIF = 5
    PV_IXQDIF = 6

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute Status PV."""
        value = 0

        # connected?
        disconnected = \
            not computed_pv.pvs[LIRFStatusPV.PV_STREAM].connected or \
            not computed_pv.pvs[LIRFStatusPV.PV_EXTTRG].connected or \
            not computed_pv.pvs[LIRFStatusPV.PV_INTEGR].connected or \
            not computed_pv.pvs[LIRFStatusPV.PV_FBMODE].connected or \
            not computed_pv.pvs[LIRFStatusPV.PV_AMPDIF].connected or \
            not computed_pv.pvs[LIRFStatusPV.PV_PHSDIF].connected or \
            not computed_pv.pvs[LIRFStatusPV.PV_IXQDIF].connected
        if disconnected:
            value |= LIRFStatusPV.BIT_DISCONN
            value |= LIRFStatusPV.BIT_STATOFF
            value |= LIRFStatusPV.BIT_TRIGOFF
            value |= LIRFStatusPV.BIT_INTGOFF
            value |= LIRFStatusPV.BIT_FBMDOFF
            value |= LIRFStatusPV.BIT_AMPDIFF
            value |= LIRFStatusPV.BIT_PHSDIFF
            value |= LIRFStatusPV.BIT_IXQDIFF
            return {'value': value}

        # state?
        sts = computed_pv.pvs[LIRFStatusPV.PV_STREAM].value
        if sts != _Const.OffOn.On or sts is None:
            value |= LIRFStatusPV.BIT_STATOFF

        # trigger?
        sts = computed_pv.pvs[LIRFStatusPV.PV_EXTTRG].value
        if sts != _Const.OffOn.On or sts is None:
            value |= LIRFStatusPV.BIT_TRIGOFF

        # integral?
        sts = computed_pv.pvs[LIRFStatusPV.PV_INTEGR].value
        if sts != _Const.OffOn.On or sts is None:
            value |= LIRFStatusPV.BIT_INTGOFF

        # feedback?
        sts = computed_pv.pvs[LIRFStatusPV.PV_FBMODE].value
        if sts != _Const.OffOn.On or sts is None:
            value |= LIRFStatusPV.BIT_FBMDOFF

        # amp diff?
        severity = computed_pv.pvs[LIRFStatusPV.PV_AMPDIF].severity
        if severity != 0:
            value |= LIRFStatusPV.BIT_AMPDIFF

        # phase diff?
        severity = computed_pv.pvs[LIRFStatusPV.PV_PHSDIF].severity
        if severity != 0:
            value |= LIRFStatusPV.BIT_PHSDIFF

        # IxQ diff?
        severity = computed_pv.pvs[LIRFStatusPV.PV_IXQDIF].severity
        if severity != 0:
            value |= LIRFStatusPV.BIT_IXQDIFF

        return {'value': value}


class LIPUStatusPV:
    """LI PU Status PV."""

    BIT_DISCONN = 0b000000000000000001
    BIT_RUNSTOP = 0b000000000000000010
    BIT_PREHEAT = 0b000000000000000100
    BIT_CHRALLW = 0b000000000000001000
    BIT_TRGALLW = 0b000000000000010000
    BIT_EMRSTOP = 0b000000000000100000
    BIT_CPS_ALL = 0b000000000001000000
    BIT_THYHEAT = 0b000000000010000000
    BIT_KLYHEAT = 0b000000000100000000
    BIT_LVRDYOK = 0b000000001000000000
    BIT_HVRDYOK = 0b000000010000000000
    BIT_TRRDYOK = 0b000000100000000000
    BIT_SELFFLT = 0b000001000000000000
    BIT_SYS_RDY = 0b000010000000000000
    BIT_TRGNORM = 0b000100000000000000
    BIT_PLSCURR = 0b001000000000000000
    BIT_VLTDIFF = 0b010000000000000000
    BIT_CRRDIFF = 0b100000000000000000

    PV_RUNSTOP = 0
    PV_PREHEAT = 1
    PV_CHRALLW = 2
    PV_TRGALLW = 3
    PV_EMRSTOP = 4
    PV_CPS_ALL = 5
    PV_THYHEAT = 6
    PV_KLYHEAT = 7
    PV_LVRDYOK = 8
    PV_HVRDYOK = 9
    PV_TRRDYOK = 10
    PV_SELFFLT = 11
    PV_SYS_RDY = 12
    PV_TRGNORM = 13
    PV_PLSCURR = 14
    PV_VLTDIFF = 15
    PV_CRRDIFF = 16

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute Status PV."""
        value = 0

        # connected?
        disconnected = \
            not computed_pv.pvs[LIPUStatusPV.PV_RUNSTOP].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_PREHEAT].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_CHRALLW].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_TRGALLW].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_EMRSTOP].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_CPS_ALL].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_THYHEAT].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_KLYHEAT].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_LVRDYOK].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_HVRDYOK].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_TRRDYOK].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_SELFFLT].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_SYS_RDY].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_TRGNORM].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_PLSCURR].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_VLTDIFF].connected or \
            not computed_pv.pvs[LIPUStatusPV.PV_CRRDIFF].connected
        if disconnected:
            value |= LIPUStatusPV.BIT_DISCONN
            value |= LIPUStatusPV.BIT_RUNSTOP
            value |= LIPUStatusPV.BIT_PREHEAT
            value |= LIPUStatusPV.BIT_CHRALLW
            value |= LIPUStatusPV.BIT_TRGALLW
            value |= LIPUStatusPV.BIT_EMRSTOP
            value |= LIPUStatusPV.BIT_CPS_ALL
            value |= LIPUStatusPV.BIT_THYHEAT
            value |= LIPUStatusPV.BIT_KLYHEAT
            value |= LIPUStatusPV.BIT_LVRDYOK
            value |= LIPUStatusPV.BIT_HVRDYOK
            value |= LIPUStatusPV.BIT_TRRDYOK
            value |= LIPUStatusPV.BIT_SELFFLT
            value |= LIPUStatusPV.BIT_SYS_RDY
            value |= LIPUStatusPV.BIT_TRGNORM
            value |= LIPUStatusPV.BIT_PLSCURR
            value |= LIPUStatusPV.BIT_VLTDIFF
            value |= LIPUStatusPV.BIT_CRRDIFF
            return {'value': value}

        # Run/Stop
        sts = computed_pv.pvs[LIPUStatusPV.PV_RUNSTOP].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_RUNSTOP

        # PreHeat
        sts = computed_pv.pvs[LIPUStatusPV.PV_PREHEAT].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_PREHEAT

        # Charge_Allowed
        sts = computed_pv.pvs[LIPUStatusPV.PV_CHRALLW].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_CHRALLW

        # TrigOut_Allowed
        sts = computed_pv.pvs[LIPUStatusPV.PV_TRGALLW].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_TRGALLW

        # Emer_Stop
        sts = computed_pv.pvs[LIPUStatusPV.PV_EMRSTOP].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_EMRSTOP

        # CPS_ALL
        sts = computed_pv.pvs[LIPUStatusPV.PV_CPS_ALL].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_CPS_ALL

        # Thy_Heat
        sts = computed_pv.pvs[LIPUStatusPV.PV_THYHEAT].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_THYHEAT

        # Kly_Heat
        sts = computed_pv.pvs[LIPUStatusPV.PV_KLYHEAT].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_KLYHEAT

        # LV_Rdy_OK
        sts = computed_pv.pvs[LIPUStatusPV.PV_LVRDYOK].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_LVRDYOK

        # HV_Rdy_OK
        sts = computed_pv.pvs[LIPUStatusPV.PV_HVRDYOK].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_HVRDYOK

        # TRIG_Rdy_OK
        sts = computed_pv.pvs[LIPUStatusPV.PV_TRRDYOK].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_TRRDYOK

        # MOD_Self_Fault
        sts = computed_pv.pvs[LIPUStatusPV.PV_SELFFLT].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_SELFFLT

        # MOD_Sys_Ready
        sts = computed_pv.pvs[LIPUStatusPV.PV_SYS_RDY].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_SYS_RDY

        # TRIG_Norm
        sts = computed_pv.pvs[LIPUStatusPV.PV_TRGNORM].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_TRGNORM

        # Pulse_Current
        sts = computed_pv.pvs[LIPUStatusPV.PV_PLSCURR].value
        if sts != 1 or sts is None:
            value |= LIPUStatusPV.BIT_PLSCURR

        # volt diff?
        severity = computed_pv.pvs[LIPUStatusPV.PV_VLTDIFF].severity
        if severity != 0:
            value |= LIPUStatusPV.BIT_VLTDIFF

        # current diff?
        severity = computed_pv.pvs[LIPUStatusPV.PV_CRRDIFF].severity
        if severity != 0:
            value |= LIPUStatusPV.BIT_CRRDIFF

        return {'value': value}


class LIEGHVStatusPV:
    """LI Egun HVPS Status PV."""

    BIT_DISCONN = 0b0001
    BIT_SWITOFF = 0b0010
    BIT_ENBLOFF = 0b0100
    BIT_VOLTDIF = 0b1000

    PV_SWITCH = 0
    PV_ENABLE = 1
    PV_VLTDIF = 2

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute Status PV."""
        value = 0

        # connected?
        disconnected = \
            not computed_pv.pvs[LIEGHVStatusPV.PV_SWITCH].connected or \
            not computed_pv.pvs[LIEGHVStatusPV.PV_ENABLE].connected or \
            not computed_pv.pvs[LIEGHVStatusPV.PV_VLTDIF].connected
        if disconnected:
            value |= LIEGHVStatusPV.BIT_DISCONN
            value |= LIEGHVStatusPV.BIT_SWITOFF
            value |= LIEGHVStatusPV.BIT_ENBLOFF
            value |= LIEGHVStatusPV.BIT_VOLTDIF
            return {'value': value}

        # switch?
        sts = computed_pv.pvs[LIEGHVStatusPV.PV_SWITCH].value
        if sts != _Const.OffOn.On or sts is None:
            value |= LIEGHVStatusPV.BIT_SWITOFF

        # enable?
        sts = computed_pv.pvs[LIEGHVStatusPV.PV_ENABLE].value
        if sts != _Const.OffOn.On or sts is None:
            value |= LIEGHVStatusPV.BIT_ENBLOFF

        # volt diff?
        severity = computed_pv.pvs[LIEGHVStatusPV.PV_VLTDIF].severity
        if severity != 0:
            value |= LIEGHVStatusPV.BIT_VOLTDIF

        return {'value': value}


class LIFilaPSStatusPV:
    """LI FilaPS Status PV."""

    BIT_DISCONN = 0b0001
    BIT_SWITOFF = 0b0010
    BIT_CURRDIF = 0b0100

    PV_SWITCH = 0
    PV_CURDIF = 1

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute Status PV."""
        value = 0

        # connected?
        disconnected = \
            not computed_pv.pvs[LIFilaPSStatusPV.PV_SWITCH].connected or \
            not computed_pv.pvs[LIFilaPSStatusPV.PV_CURDIF].connected
        if disconnected:
            value |= LIFilaPSStatusPV.BIT_DISCONN
            value |= LIFilaPSStatusPV.BIT_SWITOFF
            value |= LIFilaPSStatusPV.BIT_CURRDIF
            return {'value': value}

        # switch?
        sts = computed_pv.pvs[LIFilaPSStatusPV.PV_SWITCH].value
        if sts != _Const.OffOn.On or sts is None:
            value |= LIFilaPSStatusPV.BIT_SWITOFF

        # volt diff?
        severity = computed_pv.pvs[LIFilaPSStatusPV.PV_CURDIF].severity
        if severity != 0:
            value |= LIFilaPSStatusPV.BIT_CURRDIF

        return {'value': value}
