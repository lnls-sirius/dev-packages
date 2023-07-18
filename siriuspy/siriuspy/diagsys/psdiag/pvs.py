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
    CURRT_REF = 2
    OPMODESTS = 3

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute difference between SP and Mon current values."""
        psname = _PVName(computed_pv.pvs[0].pvname).device_name
        disconn = \
            not computed_pv.pvs[PSDiffPV.CURRT_SP].connected or \
            not computed_pv.pvs[PSDiffPV.CURRT_MON].connected
        if psname.dev in ['FCH', 'FCV']:
            disconn |= not computed_pv.pvs[PSDiffPV.CURRT_REF].connected
            disconn |= not computed_pv.pvs[PSDiffPV.OPMODESTS].connected
        if disconn:
            return None

        value_sp = computed_pv.pvs[PSDiffPV.CURRT_SP].value
        value_mon = computed_pv.pvs[PSDiffPV.CURRT_MON].value
        diff = value_mon - value_sp
        if psname.dev in ['FCH', 'FCV']:
            opmode = computed_pv.pvs[PSDiffPV.OPMODESTS].value
            if opmode == _PSConst.OpModeFOFBSts.fofb:
                value_ref = computed_pv.pvs[PSDiffPV.CURRT_REF].value
                diff = value_mon - value_ref

        return {'value': diff}


class PSStatusPV:
    """Power Supply Status PV."""

    BIT_PSCONNECT = 0b00000001
    BIT_PWRSTATON = 0b00000010
    BIT_CURRTDIFF = 0b00000100
    BIT_INTERLOCK = 0b00001000
    BIT_ALARMSSET = 0b00010000
    BIT_OPMODEDIF = 0b00100000
    BIT_BOWFMDIFF = 0b01000000
    BIT_TRIGMDENB = 0b10000000

    PWRSTE_STS = 0
    CURRT_DIFF = 1
    INTRLCK_LI = 2
    WARNSTS_LI = 3
    CONNCTD_LI = 4
    OPMODE_SEL = 2
    OPMODE_STS = 3
    WAVFRM_MON = 4
    TRIGEN_STS = 4

    DTOLWFM_DICT = dict()

    def __init__(self):
        """Init attributs."""
        self.INTLK_PVS = list()
        self.ALARM_PVS = list()
        self.intlkwarn_bit = _ETypes.LINAC_INTLCK_WARN.index('LoadI Over Thrs')

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute PS Status PV."""
        psname = _PVName(computed_pv.pvs[0].pvname).device_name
        value = 0
        # ps connected?
        if psname.sec != 'LI':
            disconn = \
                not computed_pv.pvs[PSStatusPV.PWRSTE_STS].connected or \
                not computed_pv.pvs[PSStatusPV.CURRT_DIFF].connected or \
                not computed_pv.pvs[PSStatusPV.OPMODE_SEL].connected or \
                not computed_pv.pvs[PSStatusPV.OPMODE_STS].connected
            if psname.dev not in ['FCH', 'FCV']:
                disconn |= not computed_pv.pvs[PSStatusPV.WAVFRM_MON].connected

            for intlk in self.INTLK_PVS:
                disconn |= not computed_pv.pvs[intlk].connected
            for alarm in self.ALARM_PVS:
                disconn |= not computed_pv.pvs[alarm].connected

            if not disconn and psname.dev not in ['FCH', 'FCV']:  # comm ok?
                commsts = computed_pv.pvs[PSStatusPV.PWRSTE_STS].status
                if commsts != 0 or commsts is None:
                    disconn = True
        else:
            disconn = \
                not computed_pv.pvs[PSStatusPV.PWRSTE_STS].connected or \
                not computed_pv.pvs[PSStatusPV.CURRT_DIFF].connected or \
                not computed_pv.pvs[PSStatusPV.INTRLCK_LI].connected

            if not disconn:  # comm ok?
                commval = computed_pv.pvs[PSStatusPV.CONNCTD_LI].value
                commsts = computed_pv.pvs[PSStatusPV.CONNCTD_LI].status
                if commval != 0 or commval is None or commsts != 0:
                    disconn = True
        if disconn:
            value |= PSStatusPV.BIT_PSCONNECT
            value |= PSStatusPV.BIT_PWRSTATON
            value |= PSStatusPV.BIT_CURRTDIFF
            value |= PSStatusPV.BIT_INTERLOCK
            value |= PSStatusPV.BIT_ALARMSSET
            value |= PSStatusPV.BIT_OPMODEDIF
            value |= PSStatusPV.BIT_BOWFMDIFF
            value |= PSStatusPV.BIT_TRIGMDENB
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
                if psname.dev in ['FCH', 'FCV']:
                    opmode_sel = _ETypes.FOFB_OPMODES_SEL[sel]
                    opmode_sts = _ETypes.FOFB_OPMODES_STS[sts]
                    checkdiff = sts in [
                        _PSConst.OpModeFOFBSts.manual,
                        _PSConst.OpModeFOFBSts.fofb]
                else:
                    opmode_sel = _ETypes.OPMODES[sel]
                    opmode_sts = _ETypes.STATES[sts]
                    checkdiff = sts == _PSConst.States.SlowRef
                if opmode_sel != opmode_sts:
                    value |= PSStatusPV.BIT_OPMODEDIF
                # current-diff?
                if checkdiff:
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
                    if not _np.allclose(
                            mon, 0.0, atol=PSStatusPV.DTOLWFM_DICT[psname]):
                        value |= PSStatusPV.BIT_BOWFMDIFF
            else:
                value |= PSStatusPV.BIT_OPMODEDIF

            # interlocks?
            for intlk in self.INTLK_PVS:
                intlkval = computed_pv.pvs[intlk].value
                if intlkval != 0 or intlkval is None:
                    value |= PSStatusPV.BIT_INTERLOCK
                    break

            # alarms?
            for alarm in self.ALARM_PVS:
                alarmval = computed_pv.pvs[alarm].value
                if alarmval != 0 or alarmval is None:
                    value |= PSStatusPV.BIT_ALARMSSET
                    break

            # triggered mode enable?
            if psname.dev in ['FCH', 'FCV']:
                trigen = computed_pv.pvs[PSStatusPV.TRIGEN_STS].value
                if trigen or trigen is None:
                    value |= PSStatusPV.BIT_TRIGMDENB

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
