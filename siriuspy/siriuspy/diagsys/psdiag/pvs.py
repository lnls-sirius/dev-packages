#!/usr/local/bin/python-sirius
"""PS Diag PVs."""

import numpy as _np

from ...util import get_bit as _get_bit
from ...namesys import SiriusPVName as _PVName
from ...search import PSSearch as _PSSearch
from ...pwrsupply.csdev import Const as _PSConst, ETypes as _ETypes, \
    PS_LI_INTLK_THRS as _PS_LI_INTLK_THRS


class PSDiffPV:
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
        value_sp = computed_pv.pvs[PSDiffPV.CURRT_SP].value
        value_rb = computed_pv.pvs[PSDiffPV.CURRT_MON].value
        diff = value_rb - value_sp
        return {'value': diff}


class PSStatusPV:
    """Power Supply Status PV."""

    BIT_PSCONNECT = 0b000001
    BIT_PWRSTATON = 0b000010
    BIT_CURRTDIFF = 0b000100
    BIT_INTERLOCK = 0b001000
    BIT_OPMODEDIF = 0b010000
    BIT_BOWFMDIFF = 0b100000

    PWRSTE_STS = 0
    CURRT_DIFF = 1
    INTRLCK_LI = 2
    WARNSTS_LI = 3
    OPMODE_SEL = 2
    OPMODE_STS = 3
    WAVFRM_MON = 4

    DTOLWFM_DICT = dict()

    def __init__(self):
        """Init attributs."""
        self.INTLK_PVS = list()
        self.intlkwarn_bit = _ETypes.LINAC_INTLCK_WARN.index('LoadI Over Thrs')

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute PS Status PV."""
        psname = _PVName(computed_pv.pvs[0].pvname).device_name
        value = 0
        # ps connected?
        if psname.sec != 'LI':
            disconnected = \
                not computed_pv.pvs[PSStatusPV.PWRSTE_STS].connected or \
                not computed_pv.pvs[PSStatusPV.CURRT_DIFF].connected or \
                not computed_pv.pvs[PSStatusPV.OPMODE_SEL].connected or \
                not computed_pv.pvs[PSStatusPV.OPMODE_STS].connected or \
                not computed_pv.pvs[PSStatusPV.WAVFRM_MON].connected
            for intlk in self.INTLK_PVS:
                disconnected |= not computed_pv.pvs[intlk].connected
        else:
            disconnected = \
                not computed_pv.pvs[PSStatusPV.PWRSTE_STS].connected or \
                not computed_pv.pvs[PSStatusPV.CURRT_DIFF].connected or \
                not computed_pv.pvs[PSStatusPV.INTRLCK_LI].connected
        if disconnected:
            value |= PSStatusPV.BIT_PSCONNECT
            value |= PSStatusPV.BIT_PWRSTATON
            value |= PSStatusPV.BIT_CURRTDIFF
            value |= PSStatusPV.BIT_INTERLOCK
            value |= PSStatusPV.BIT_OPMODEDIF
            value |= PSStatusPV.BIT_BOWFMDIFF
            return {'value': value}

        # pwrstate?
        pwrsts = computed_pv.pvs[PSStatusPV.PWRSTE_STS].value
        if pwrsts != _PSConst.PwrStateSts.On or pwrsts is None:
            value |= PSStatusPV.BIT_PWRSTATON

        if psname.sec != 'LI':
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
            for intlk in self.INTLK_PVS:
                intlkval = computed_pv.pvs[intlk].value
                if intlkval != 0 or intlkval is None:
                    value |= PSStatusPV.BIT_INTERLOCK
                    break

        else:
            # current-diff?
            severity = computed_pv.pvs[PSStatusPV.CURRT_DIFF].severity
            if severity != 0:
                value |= PSStatusPV.BIT_CURRTDIFF

            # interlocks?
            intlk = computed_pv.pvs[PSStatusPV.INTRLCK_LI].value
            if psname.dev == 'Spect':
                intlkwarn = computed_pv.pvs[PSStatusPV.WARNSTS_LI].value
                if _get_bit(intlkwarn, self.intlkwarn_bit):
                    intlk -= 2**self.intlkwarn_bit
            if intlk > _PS_LI_INTLK_THRS or intlk is None:
                value |= PSStatusPV.BIT_INTERLOCK

        return {'value': value}
