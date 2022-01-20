#!/usr/local/bin/python-sirius
"""RF Diag PVs."""

import numpy as _np

from .csdev import Const as _Const


class BORFStatusPV:
    """BO RF Status PV."""

    BIT_DISCONN = 0b00001
    BIT_SIINTLK = 0b00010
    BIT_LLINTLK = 0b00100
    BIT_RMPDSBL = 0b01000
    BIT_RMPNRDY = 0b10000

    PV_SIRIUS_INTLK = 0
    PV_LLRF_INTLK = 1
    PV_RMP_ENBLD = 2
    PV_RMP_READY = 3

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute Status PV."""
        value = 0

        # connected?
        disconnected = \
            not computed_pv.pvs[BORFStatusPV.PV_SIRIUS_INTLK].connected or \
            not computed_pv.pvs[BORFStatusPV.PV_LLRF_INTLK].connected or \
            not computed_pv.pvs[BORFStatusPV.PV_RMP_ENBLD].connected or \
            not computed_pv.pvs[BORFStatusPV.PV_RMP_READY].connected

        if disconnected:
            value |= BORFStatusPV.BIT_DISCONN
            value |= BORFStatusPV.BIT_SIINTLK
            value |= BORFStatusPV.BIT_LLINTLK
            value |= BORFStatusPV.BIT_RMPDSBL
            value |= BORFStatusPV.BIT_RMPNRDY
            return {'value': value}

        # sirius interlock?
        sts = computed_pv.pvs[BORFStatusPV.PV_SIRIUS_INTLK].value
        if sts != 0 or sts is None:
            value |= BORFStatusPV.BIT_SIINTLK

        # llrf interlock?
        sts = computed_pv.pvs[BORFStatusPV.PV_LLRF_INTLK].value
        if sts != 0 or sts is None:
            value |= BORFStatusPV.BIT_LLINTLK

        # rmp enabled?
        sts = computed_pv.pvs[BORFStatusPV.PV_RMP_ENBLD].value
        if sts != _Const.DsblEnbl.Enbl or sts is None:
            value |= BORFStatusPV.BIT_RMPDSBL

        # rmp ready?
        sts = computed_pv.pvs[BORFStatusPV.PV_RMP_READY].value
        if sts != _Const.DsblEnbl.Enbl or sts is None:
            value |= BORFStatusPV.BIT_RMPNRDY

        return {'value': value}


class CheckErrPV:
    """Check error PV and filter spurious spikes."""

    PV_ERR = 0
    _tol = 0

    def __init__(self):
        self._hist = [0]*10
        self._idx = 0

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Check error exceeds tolerance."""
        if not computed_pv.pvs[CheckErrPV.PV_ERR].connected:
            return None
        value = computed_pv.pvs[CheckErrPV.PV_ERR].value
        self._hist[self._idx] = value
        self._idx += 1
        self._idx %= 10
        sts = 1 if _np.all([v > self._tol for v in self._hist]) else 0
        return {'value': sts}


class SICheckAmpErrPV(CheckErrPV):
    """Check amplitude error."""

    _tol = _Const.SI_SL_ERRTOL_AMP


class SICheckPhsErrPV(CheckErrPV):
    """Check phase error."""

    _tol = _Const.SI_SL_ERRTOL_PHS


class SICheckDTuneErrPV(CheckErrPV):
    """Check detune error."""

    _tol = _Const.SI_SL_ERRTOL_DTU


class SIRFStatusPV:
    """SI RF Status PV."""

    BIT_DISCONN = 0b000001
    BIT_SIINTLK = 0b000010
    BIT_LLINTLK = 0b000100
    BIT_AMPLERR = 0b001000
    BIT_PHSEERR = 0b010000
    BIT_DTUNERR = 0b100000

    PV_SIRIUS_INTLK = 0
    PV_LLRF_INTLK = 1
    PV_AMPL_ERR = 2
    PV_PHSE_ERR = 3
    PV_DTUN_ERR = 4

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compute Status PV."""
        value = 0

        # connected?
        disconnected = \
            not computed_pv.pvs[SIRFStatusPV.PV_SIRIUS_INTLK].connected or \
            not computed_pv.pvs[SIRFStatusPV.PV_LLRF_INTLK].connected or \
            not computed_pv.pvs[SIRFStatusPV.PV_AMPL_ERR].connected or \
            not computed_pv.pvs[SIRFStatusPV.PV_PHSE_ERR].connected or \
            not computed_pv.pvs[SIRFStatusPV.PV_DTUN_ERR].connected
        if disconnected:
            value |= SIRFStatusPV.BIT_DISCONN
            value |= SIRFStatusPV.BIT_SIINTLK
            value |= SIRFStatusPV.BIT_LLINTLK
            value |= SIRFStatusPV.BIT_AMPLERR
            value |= SIRFStatusPV.BIT_PHSEERR
            value |= SIRFStatusPV.BIT_DTUNERR
            return {'value': value}

        # sirius interlock?
        sts = computed_pv.pvs[SIRFStatusPV.PV_SIRIUS_INTLK].value
        if sts != 0 or sts is None:
            value |= SIRFStatusPV.BIT_SIINTLK

        # llrf interlock?
        sts = computed_pv.pvs[SIRFStatusPV.PV_LLRF_INTLK].value
        if sts != 0 or sts is None:
            value |= SIRFStatusPV.BIT_LLINTLK

        # amplitude error?
        severity = computed_pv.pvs[SIRFStatusPV.PV_AMPL_ERR].severity
        if severity != 0:
            value |= SIRFStatusPV.BIT_AMPLERR

        # phase error?
        severity = computed_pv.pvs[SIRFStatusPV.PV_PHSE_ERR].severity
        if severity != 0:
            value |= SIRFStatusPV.BIT_PHSEERR

        # detune error?
        severity = computed_pv.pvs[SIRFStatusPV.PV_DTUN_ERR].severity
        if severity != 0:
            value |= SIRFStatusPV.BIT_DTUNERR

        return {'value': value}
