#!/usr/local/bin/python-sirius
"""LI Diag PVs."""

import numpy as _np

from ...util import update_bit as _update_bit
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

    BIT = _Const.register(
        'BIT',
        ['DISCONN', 'RUNSTOP', 'PREHEAT', 'CHRALLW', 'TRGALLW',
         'EMRSTOP', 'CPS_ALL', 'THYHEAT', 'KLYHEAT', 'LVRDYOK',
         'HVRDYOK', 'TRRDYOK', 'SELFFLT', 'SYS_RDY', 'TRGNORM',
         'PLSCURR', 'VLTDIFF', 'CRRDIFF'])

    PV = _Const.register(
        'PV',
        ['RUNSTOP', 'PREHEAT', 'CHRALLW', 'TRGALLW', 'EMRSTOP',
         'CPS_ALL', 'THYHEAT', 'KLYHEAT', 'LVRDYOK', 'HVRDYOK',
         'TRRDYOK', 'SELFFLT', 'SYS_RDY', 'TRGNORM', 'PLSCURR',
         'VLTDIFF', 'CRRDIFF'])

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute Status PV."""
        value = 0

        # connected?
        disconnected = \
            any([not computed_pv.pvs[i].connected for i in LIPUStatusPV.PV])
        if disconnected:
            value = (1 << len(LIPUStatusPV.BIT)+1)-1
            return {'value': value}

        for pvi, attr in enumerate(LIPUStatusPV.PV._fields):
            bit = getattr(LIPUStatusPV.BIT, attr)
            if 'DIFF' in attr:
                sts = computed_pv.pvs[pvi].severity
                value = _update_bit(value, bit, sts != 0)
            else:
                sts = computed_pv.pvs[pvi].value
                value = _update_bit(value, bit, sts != 1 or sts is None)

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
