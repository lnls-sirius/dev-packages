#!/usr/local/bin/python-sirius
"""PS Diag PVs."""

import numpy as _np
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.pwrsupply import ETypes as _ETypes
from siriuspy.search import PSSearch as _PSSearch
from siriuspy.computer import Computer
from siriuspy.namesys import SiriusPVName as _PVName


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
    BIT_OPMODEDIF = 0b00010000
    BIT_CURRTDIFF = 0b00100000
    BIT_INTERLKOK = 0b01000000
    BIT_BOWFMDIFF = 0b10000000

    PWRSTE_STS = 0
    INTLK_SOFT = 1
    INTLK_HARD = 2
    OPMODE_SEL = 3
    OPMODE_STS = 4
    CURRT_DIFF = 5
    MAOPMD_SEL = 6
    PSCONN_MON = 7
    WAVFRM_MON = 8

    DTOLWFM_DICT = dict()

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute PS Status PV."""
        psname = _PVName(computed_pv.pvs[0].pvname).device_name
        value = 0
        # ps connected?
        disconnected = \
            not computed_pv.pvs[PSStatusPV.PWRSTE_STS].connected or \
            not computed_pv.pvs[PSStatusPV.INTLK_SOFT].connected or \
            not computed_pv.pvs[PSStatusPV.INTLK_HARD].connected or \
            not computed_pv.pvs[PSStatusPV.OPMODE_SEL].connected or \
            not computed_pv.pvs[PSStatusPV.OPMODE_STS].connected or \
            not computed_pv.pvs[PSStatusPV.CURRT_DIFF].connected
        if disconnected:
            value |= PSStatusPV.BIT_PSCONNECT
            value |= PSStatusPV.BIT_PWRSTATON
            value |= PSStatusPV.BIT_INTERLKOK
            value |= PSStatusPV.BIT_OPMODEDIF
            value |= PSStatusPV.BIT_CURRTDIFF
            value |= PSStatusPV.BIT_BOWFMDIFF
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
        sel = computed_pv.pvs[PSStatusPV.OPMODE_SEL].value
        sts = computed_pv.pvs[PSStatusPV.OPMODE_STS].value
        if sel is not None and sts is not None:
            opmode_sel = _ETypes.OPMODES[sel]
            opmode_sts = _ETypes.STATES[sts]
            if opmode_sel != opmode_sts:
                value |= PSStatusPV.BIT_OPMODEDIF
            # current-diff?
            if sts == _PSConst.States.SlowRef:
                severity = computed_pv.pvs[PSStatusPV.CURRT_DIFF].severity
                if severity != 0:
                    value |= PSStatusPV.BIT_CURRTDIFF
            # waveform diff?
            elif (psname.sec == 'BO') and (sts == _PSConst.States.RmpWfm):
                mon = computed_pv.pvs[PSStatusPV.WAVFRM_MON].value
                if psname not in PSStatusPV.DTOLWFM_DICT.keys():
                    pstype = _PSSearch.conv_psname_2_pstype(psname)
                    PSStatusPV.DTOLWFM_DICT[psname] = _PSSearch.get_splims(
                        pstype, 'DTOL_WFM')
                if not _np.allclose(mon, 0.0,
                                    atol=PSStatusPV.DTOLWFM_DICT[psname]):
                    value |= PSStatusPV.BIT_BOWFMDIFF
        else:
            value |= PSStatusPV.BIT_OPMODEDIF

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
