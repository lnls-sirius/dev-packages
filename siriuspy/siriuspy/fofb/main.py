"""High Level FOFB main application."""

import os as _os
import time as _time
from functools import partial as _part

import epics as _epics
import numpy as _np

from ..callbacks import Callback as _Callback
from ..devices import Device as _Device, FamFastCorrs as _FamFastCorrs, \
    FamFOFBControllers as _FamFOFBCtrls, RFGen as _RFGen, SOFB as _SOFB
from ..envars import VACA_PREFIX as _VACA_PREFIX
from ..epics import PV as _PV
from ..logging import get_logger as _get_logger
from ..namesys import SiriusPVName as _PVName
from ..util import get_bit as _get_bit, update_bit as _updt_bit
from .csdev import ETypes as _ETypes, HLFOFBConst as _Const


class App(_Callback):
    """High Level FOFB main application."""

    SCAN_FREQUENCY = 1  # [Hz]

    def __init__(self, tests=False):
        """Class constructor."""
        super().__init__()
        self._logger = _get_logger(self)
        self._const = _Const()
        self._pvs_database = self._const.get_hlfofb_database()
        self._tests = tests
        self._init = False

        # internal states
        self._loop_state = self._const.LoopState.Open
        self._loop_state_lastsp = self._const.LoopState.Open
        self._loop_gain_h = 0.0520
        self._loop_gain_mon_h = 0
        self._loop_gain_v = 0.0520
        self._loop_gain_mon_v = 0
        self._thread_loopstate = None
        self._abort_thread = False
        self._loop_max_orb_dist = self._const.DEF_MAX_ORB_DISTORTION
        self._loop_max_orb_dist_enbl = self._const.DsblEnbl.Dsbl
        self._loop_packloss_detec_enbl = self._const.DsblEnbl.Dsbl
        self._corr_status = self._pvs_database["CorrStatus-Mon"]["value"]
        self._corr_setcurrzero_dur = 5
        self._thread_currzero = None
        self._abort_thread_currzero = False
        self._ch_maxacccurr = self._pvs_database["CHAccSatMax-RB"]["value"]
        self._cv_maxacccurr = self._pvs_database["CVAccSatMax-RB"]["value"]
        self._time_frame_len = self._pvs_database["TimeFrameLen-RB"]["value"]
        self._fofbctrl_status = self._pvs_database["CtrlrStatus-Mon"]["value"]
        self._thread_syncnet = None
        self._thread_reset = None
        self._fofbctrl_syncenbllist = _np.ones(self._const.nr_bpms, dtype=bool)
        self._fofbctrl_syncuseenbllist = self._const.DsblEnbl.Enbl
        self._reforb_x = _np.zeros(self._const.nr_bpms, dtype=float)
        self._reforbhw_x = _np.zeros(self._const.nr_bpms, dtype=float)
        self._reforb_y = _np.zeros(self._const.nr_bpms, dtype=float)
        self._reforbhw_y = _np.zeros(self._const.nr_bpms, dtype=float)
        self._respmat = _np.zeros(
            [2 * self._const.nr_bpms, self._const.nr_corrs], dtype=float
        )
        self._invrespmat = self._respmat.copy().T
        self._invrespmatconv = self._invrespmat.copy()
        self._enable_lists = {
            "bpmx": _np.ones(self._const.nr_bpms, dtype=bool),
            "bpmy": _np.ones(self._const.nr_bpms, dtype=bool),
            "ch": _np.ones(self._const.nr_ch, dtype=bool),
            "cv": _np.ones(self._const.nr_cv, dtype=bool),
            "rf": _np.ones(1, dtype=bool),
        }
        self._corr_accdec_val = 1
        self._corr_accdec_enm = self._const.DecOpt.FOFB
        self._thread_enbllist = None
        self._abort_thread_enbllist = False
        self._min_sing_val = self._const.MIN_SING_VAL
        self._tikhonov_reg_const = self._const.TIKHONOV_REG_CONST
        self._invrespmat_normmode = self._const.GlobIndiv.Global
        self._pscoeffs = self._invrespmatconv[:-1].copy()
        self._psgains = _np.ones(self._const.nr_chcv, dtype=float)
        self._meas_respmat_kick = {
            "ch": 15,  # [urad]
            "cv": 22.5,  # [urad]
            "rf": 75,  # [Hz]
        }
        self._meas_respmat_wait = 1  # [s]
        self._meas_respmat_thread = None
        self._measuring_respmat = False

        # devices and connections
        self._sisofb_dev = _SOFB(_SOFB.DEVICES.SI)

        corrnames = self._const.ch_names + self._const.cv_names
        self._corrs_dev = _FamFastCorrs(corrnames)

        self._rf_dev = _RFGen()

        self._llfofb_dev = _FamFOFBCtrls()

        self._intlk_pvs = list()
        self._intlk_values = dict()
        for dev in self._llfofb_dev.ctrlrefdevs.values():
            pvo = dev.pv_object("LoopIntlk-Mon")
            self._intlk_values[pvo.pvname] = 0
            pvo.add_callback(self._callback_loopintlk, with_ctrlvars=False)
            self._intlk_pvs.append(pvo)

        self._corrs_dev.wait_for_connection(self._const.DEF_TIMEWAIT)

        self._auxbpm = _Device(
            "SI-01M1:DI-BPM",
            props2init=("INFOFOFBRate-RB", "INFOMONITRate-RB"),
        )

        havebeam_pvname = _PVName(
            "SI-Glob:AP-CurrInfo:StoredEBeam-Mon"
        ).substitute(prefix=_VACA_PREFIX)
        self._havebeam_pv = _PV(
            havebeam_pvname,
            connection_timeout=0.05,
            callback=self._callback_havebeam,
        )

        # pvs to write methods
        self.map_pv2write = {
            "LoopState-Sel": self.set_loop_state,
            "LoopGainH-SP": _part(self.set_loop_gain, "h"),
            "LoopGainV-SP": _part(self.set_loop_gain, "v"),
            "LoopMaxOrbDistortion-SP": self.set_loop_max_orbit_dist,
            "LoopMaxOrbDistortionEnbl-Sel": self.set_loop_max_orbit_dist_enbl,
            "LoopPacketLossDetecEnbl-Sel": self.set_loop_packloss_detec_enbl,
            "CorrConfig-Cmd": self.cmd_corr_configure,
            "CorrSetPwrStateOn-Cmd": self.cmd_corr_pwrstate_on,
            "CorrSetPwrStateOff-Cmd": self.cmd_corr_pwrstate_off,
            "CorrSetOpModeManual-Cmd": self.cmd_corr_opmode_manual,
            "CorrSetAccFreezeDsbl-Cmd": self.cmd_corr_accfreeze_dsbl,
            "CorrSetAccFreezeEnbl-Cmd": self.cmd_corr_accfreeze_enbl,
            "CorrSetAccClear-Cmd": self.cmd_corr_accclear,
            "CorrSetCurrZero-Cmd": self.cmd_corr_currzero,
            "CorrSetCurrZeroDuration-SP": self.set_corr_currzero_duration,
            "CHAccSatMax-SP": _part(self.set_corr_accsatmax, "ch"),
            "CVAccSatMax-SP": _part(self.set_corr_accsatmax, "cv"),
            "TimeFrameLen-SP": self.set_timeframelen,
            "CtrlrConfBPMId-Cmd": self.cmd_fofbctrl_confbpmid,
            "CtrlrSyncNet-Cmd": self.cmd_fofbctrl_syncnet,
            "CtrlrSyncRefOrb-Cmd": self.cmd_fofbctrl_syncreforb,
            "CtrlrSyncTFrameLen-Cmd": self.cmd_fofbctrl_synctframelen,
            "CtrlrConfBPMLogTrg-Cmd": self.cmd_fofbctrl_confbpmlogtrg,
            "CtrlrSyncUseEnblList-Sel": self.set_fofbctrl_syncuseenablelist,
            "CtrlrSyncMaxOrbDist-Cmd": self.cmd_fofbctrl_syncmaxorbdist,
            "CtrlrSyncPacketLossDetec-Cmd": self.cmd_fofbctrl_syncpacklossdet,
            "CtrlrReset-Cmd": self.cmd_fofbctrl_reset,
            "CtrlrDsblSYSIDExc-Cmd": self.cmd_fofbctrl_dsblsysid,
            "FOFBAccDecimation-Sel": _part(self.set_corr_accdec, "enum"),
            "FOFBAccDecimation-SP": _part(self.set_corr_accdec, "value"),
            "RefOrbX-SP": _part(self.set_reforbit, "x"),
            "RefOrbY-SP": _part(self.set_reforbit, "y"),
            "RespMat-SP": self.set_respmat,
            "BPMXEnblList-SP": _part(self.set_enbllist, "bpmx"),
            "BPMYEnblList-SP": _part(self.set_enbllist, "bpmy"),
            "CHEnblList-SP": _part(self.set_enbllist, "ch"),
            "CVEnblList-SP": _part(self.set_enbllist, "cv"),
            "UseRF-Sel": _part(self.set_enbllist, "rf"),
            "MinSingValue-SP": self.set_min_sing_value,
            "TikhonovRegConst-SP": self.set_tikhonov_reg_const,
            "InvRespMatNormMode-Sel": self.set_invrespmat_normmode,
            "MeasRespMat-Cmd": self.set_respmat_meas_state,
            "MeasRespMatKickCH-SP": _part(self.set_respmat_meas_kick, "ch"),
            "MeasRespMatKickCV-SP": _part(self.set_respmat_meas_kick, "cv"),
            "MeasRespMatKickRF-SP": _part(self.set_respmat_meas_kick, "rf"),
            "MeasRespMatWait-SP": self.set_respmat_meas_wait_time,
        }

        # configuration scanning
        self.quit = False
        self.scanning = False
        self.thread_check_corrs_configs = _epics.ca.CAThread(
            target=self._check_corrs_configs, daemon=True
        )
        self.thread_check_corrs_configs.start()
        self.thread_check_ctrls_configs = _epics.ca.CAThread(
            target=self._check_ctrls_configs, daemon=True
        )
        self.thread_check_ctrls_configs.start()

    def init_database(self):
        """Set initial PV values."""
        pvn2vals = {
            "LoopState-Sel": self._loop_state,
            "LoopState-Sts": self._loop_state,
            "LoopGainH-SP": self._loop_gain_h,
            "LoopGainH-RB": self._loop_gain_h,
            "LoopGainH-Mon": self._loop_gain_mon_h,
            "LoopGainV-SP": self._loop_gain_v,
            "LoopGainV-RB": self._loop_gain_v,
            "LoopGainV-Mon": self._loop_gain_mon_v,
            "LoopMaxOrbDistortion-SP": self._loop_max_orb_dist,
            "LoopMaxOrbDistortion-RB": self._loop_max_orb_dist,
            "LoopMaxOrbDistortionEnbl-Sel": self._loop_max_orb_dist_enbl,
            "LoopMaxOrbDistortionEnbl-Sts": self._loop_max_orb_dist_enbl,
            "LoopPacketLossDetecEnbl-Sel": self._loop_packloss_detec_enbl,
            "LoopPacketLossDetecEnbl-Sts": self._loop_packloss_detec_enbl,
            "CorrStatus-Mon": self._corr_status,
            "CorrConfig-Cmd": 0,
            "CorrSetPwrStateOn-Cmd": 0,
            "CorrSetOpModeManual-Cmd": 0,
            "CorrSetAccFreezeDsbl-Cmd": 0,
            "CorrSetAccFreezeEnbl-Cmd": 0,
            "CorrSetAccClear-Cmd": 0,
            "CorrSetCurrZero-Cmd": 0,
            "CorrSetCurrZeroDuration-SP": self._corr_setcurrzero_dur,
            "CorrSetCurrZeroDuration-RB": self._corr_setcurrzero_dur,
            "CHAccSatMax-SP": self._ch_maxacccurr,
            "CHAccSatMax-RB": self._ch_maxacccurr,
            "CVAccSatMax-SP": self._cv_maxacccurr,
            "CVAccSatMax-RB": self._cv_maxacccurr,
            "TimeFrameLen-SP": self._time_frame_len,
            "TimeFrameLen-RB": self._time_frame_len,
            "CtrlrStatus-Mon": self._fofbctrl_status,
            "CtrlrConfBPMId-Cmd": 0,
            "CtrlrSyncNet-Cmd": 0,
            "CtrlrSyncUseEnblList-Sel": self._fofbctrl_syncuseenbllist,
            "CtrlrSyncUseEnblList-Sts": self._fofbctrl_syncuseenbllist,
            "CtrlrSyncEnblList-Mon": self._fofbctrl_syncenbllist,
            "CtrlrSyncRefOrb-Cmd": 0,
            "CtrlrSyncTFrameLen-Cmd": 0,
            "CtrlrConfBPMLogTrg-Cmd": 0,
            "CtrlrSyncMaxOrbDist-Cmd": 0,
            "CtrlrSyncPacketLossDetec-Cmd": 0,
            "CtrlrReset-Cmd": 0,
            "CtrlrDsblSYSIDExc-Cmd": 0,
            "FOFBAccDecimation-Sel": self._corr_accdec_enm,
            "FOFBAccDecimation-Sts": self._corr_accdec_enm,
            "FOFBAccDecimation-SP": self._corr_accdec_val,
            "FOFBAccDecimation-RB": self._corr_accdec_val,
            "MinSingValue-SP": self._min_sing_val,
            "MinSingValue-RB": self._min_sing_val,
            "TikhonovRegConst-SP": self._tikhonov_reg_const,
            "TikhonovRegConst-RB": self._tikhonov_reg_const,
            "InvRespMatNormMode-Sel": self._invrespmat_normmode,
            "InvRespMatNormMode-Sts": self._invrespmat_normmode,
            "MeasRespMat-Cmd": 0,
            "MeasRespMat-Mon": self._const.MeasRespMatMon.Idle,
            "MeasRespMatKickCH-SP": self._meas_respmat_kick["ch"],
            "MeasRespMatKickCH-RB": self._meas_respmat_kick["ch"],
            "MeasRespMatKickCV-SP": self._meas_respmat_kick["cv"],
            "MeasRespMatKickCV-RB": self._meas_respmat_kick["cv"],
            "MeasRespMatKickRF-SP": self._meas_respmat_kick["rf"],
            "MeasRespMatKickRF-RB": self._meas_respmat_kick["rf"],
            "MeasRespMatWait-SP": self._meas_respmat_wait,
            "MeasRespMatWait-RB": self._meas_respmat_wait,
        }
        for pvn, val in pvn2vals.items():
            self.run_callbacks(pvn, val)

        # load autosave data
        # enable lists
        for dev in ["bpmx", "bpmy", "ch", "cv", "rf"]:
            okl = self._load_enbllist(dev)
            pvn = f"{dev.upper()}EnblList-SP" if dev != "rf" else "UseRF-Sel"
            enb = self._enable_lists[dev]
            pvv = enb if dev != "rf" else bool(enb)
            self.run_callbacks(pvn, pvv)
            if not okl:
                self.run_callbacks(
                    pvn.replace("SP", "RB").replace("Sel", "Sts"), pvv
                )
        self._update_fofbctrl_sync_enbllist()
        # matrix
        okm = self._load_respmat()
        self.run_callbacks("RespMat-SP", list(self._respmat.ravel()))
        if not okm:
            self.run_callbacks("RespMat-RB", list(self._respmat.ravel()))
        # ref orbits
        okr = self._load_reforbit()
        for plan in ["x", "y"]:
            pvn = f"RefOrb{plan.upper()}-SP"
            pvv = getattr(self, f"_reforb_{plan}")
            self.run_callbacks(pvn, pvv)
            if not okr:
                self.run_callbacks(pvn.replace("SP", "RB"), pvv)
        self._logger.info("Started.")
        self._init = True

    @property
    def pvs_database(self):
        """Return pvs_database."""
        return self._pvs_database

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        value = None
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        self._logger.info(
            "Write received for: %s --> %s",
            reason,
            str(value),
            extra={"ioc_only": True},
        )
        if reason in self.map_pv2write.keys():
            status = self.map_pv2write[reason](value)
            self._logger.info(
                "%s Write for: %s --> %s",
                str(status).upper(),
                reason,
                str(value),
                extra={"ioc_only": True},
            )
            return status
        self._logger.warning(
            "PV %s does not have a set function.",
            reason,
            extra={"ioc_only": True},
        )
        return False

    @property
    def fastcorrs_dev(self):
        """Fast corrector device."""
        return self._corrs_dev

    @property
    def rf_dev(self):
        """RF device."""
        return self._rf_dev

    @property
    def llfofb_dev(self):
        """LL FOFB device."""
        return self._llfofb_dev

    @property
    def havebeam(self):
        """Return if there is stored beam."""
        if self._tests:
            return True
        return self._havebeam_pv.connected and self._havebeam_pv.value

    def update_log(self, msg):
        """This method will be called by the IOC to update Log-Mon PV."""
        self.run_callbacks("Log-Mon", msg)

    # --- loop control ---

    def set_loop_state(self, value, abort=False):
        """Set loop state."""
        if not 0 <= value < len(_ETypes.OPEN_CLOSED):
            return False

        self._loop_state_lastsp = value
        if value:
            if not self.havebeam:
                self._logger.error("Do not have stored beam. Aborted.")
                return False
            if _np.any([pvo.value for pvo in self._intlk_pvs]):
                self._logger.error("Reset interlocks before closing")
                self._logger.error("the loop.")
                return False

        if (
            self._thread_loopstate is not None
            and self._thread_loopstate.is_alive()
        ):
            self._logger.warning("Interrupting Loop Enable thread...")
            self._abort_thread = True
            self._thread_loopstate.join()

        self._thread_loopstate = _epics.ca.CAThread(
            target=self._thread_set_loop_state,
            args=[value, abort],
            daemon=True,
        )
        self._thread_loopstate.start()
        return True

    def _thread_set_loop_state(self, value, abort):
        if value:  # closing the loop
            # set gains to zero, recalculate gains and coeffs
            self._logger.info("Setting Loop Gain to zero...")
            self._loop_gain_mon_h, self._loop_gain_mon_v = 0, 0
            self._calc_corrs_coeffs(log=False)
            # set and wait corrector gains and coeffs to zero
            if not self._set_corrs_coeffs(log=False):
                return
            self._logger.info("Waiting for coefficients and gains...")
            if not self._wait_coeffs_and_gains():
                self.run_callbacks("LoopState-Sel", self._loop_state)
                return

            if self._check_abort_thread():
                return

            # close the loop
            self._logger.info("...done. Closing the loop...")
            self._loop_state = value
            if not self._check_set_corrs_opmode():
                self._loop_state = self._const.LoopState.Open
                self.run_callbacks("LoopState-Sel", self._loop_state)
                return
            self.run_callbacks("LoopState-Sts", self._loop_state)

            if self._check_abort_thread():
                return

            # do ramp up
            self._logger.info("...done. Starting Loop Gain ramp up...")
            if self._do_loop_gain_ramp(ramp="up"):
                self._logger.info("LoopGain ramp up finished!")

        else:  # opening the loop
            # do ramp down
            self._logger.info("Starting Loop Gain ramp down...")
            if self._do_loop_gain_ramp(ramp="down", abort=abort):
                self._logger.info("Loop Gain ramp down finished!")

            if self._check_abort_thread():
                return

            # open the loop
            self._loop_state = value
            self._check_set_corrs_opmode()
            self.run_callbacks("LoopState-Sts", self._loop_state)

    def _do_loop_gain_ramp(self, ramp="up", abort=False):
        xdata = _np.linspace(0, 1, self._const.LOOPGAIN_RMP_NPTS)
        power = 1
        if ramp == "up":
            ydata = xdata**power
            ydata_h = ydata * self._loop_gain_h
            ydata_v = ydata * self._loop_gain_v
        else:
            ydata = (1 - xdata) ** power
            ydata_h = ydata * self._loop_gain_mon_h
            ydata_v = ydata * self._loop_gain_mon_v
        for i in range(self._const.LOOPGAIN_RMP_NPTS):
            if not self.havebeam or abort:
                if not self.havebeam:
                    self._logger.error("There is no beam stored.")
                self._logger.warning("Gain ramp aborted.")
                self._logger.warning("Setting gain to zero.")
                self._loop_gain_mon_h, self._loop_gain_mon_v = 0, 0
                self.run_callbacks("LoopGainH-Mon", self._loop_gain_mon_h)
                self.run_callbacks("LoopGainV-Mon", self._loop_gain_mon_v)
                self._calc_corrs_coeffs()
                self._set_corrs_coeffs()
                self._wait_coeffs_and_gains()
                return False
            if self._check_abort_thread():
                return False

            self._loop_gain_mon_h = ydata_h[i]
            self._loop_gain_mon_v = ydata_v[i]
            self.run_callbacks("LoopGainH-Mon", self._loop_gain_mon_h)
            self.run_callbacks("LoopGainV-Mon", self._loop_gain_mon_v)
            self._logger.info(
                f"{i+1:02d}/{len(ydata):02d} -> Loop Gain: "
                f"H={ydata_h[i]:.3f}, V={ydata_v[i]:.3f}"
            )
            self._calc_corrs_coeffs(log=False)
            self._set_corrs_coeffs(log=False)
            _t0 = _time.time()
            if not self._wait_coeffs_and_gains():
                return False
            _td = 1 / self._const.LOOPGAIN_RMP_FREQ - (_time.time() - _t0)
            if _td > 0:
                _time.sleep(_td)
        return True

    def _wait_coeffs_and_gains(self):
        _t0 = _time.time()
        while _time.time() - _t0 < self._const.DEF_TIMEOUT:
            _time.sleep(self._const.DEF_TIMESLEEP)
            if self._corrs_dev.check_invrespmat_row(
                self._pscoeffs
            ) and self._corrs_dev.check_fofbacc_gain(self._psgains):
                return True
            if self._check_abort_thread():
                return False
        self._logger.error("Timed out waiting for correctors to")
        self._logger.error("implement gains and coefficients.")
        return False

    def _check_abort_thread(self):
        if self._abort_thread:
            self._logger.warning("Loop state thread aborted.")
            self._abort_thread = False
            return True
        return False

    def set_loop_gain(self, plane, value):
        """Set loop gain."""
        if not -(2**3) <= value <= 2**3 - 1:
            return False

        if (
            self._thread_loopstate is not None
            and self._thread_loopstate.is_alive()
        ):
            self._logger.error("Wait for Loop Gain ramp before ")
            self._logger.error("setting new value.")
            return False

        setattr(self, "_loop_gain_" + plane, value)

        # if loop closed, calculate new gains and coefficients
        if self._loop_state:
            setattr(self, "_loop_gain_mon_" + plane, value)
            self.run_callbacks(f"LoopGain{plane.upper()}-Mon", value)
            self._calc_corrs_coeffs()
            self._set_corrs_coeffs()

        self._logger.info(f"Changed Loop Gain {plane.upper()} to {value}.")
        self.run_callbacks(f"LoopGain{plane.upper()}-RB", value)
        return True

    def set_loop_max_orbit_dist(self, value):
        """Set maximum orbit distortion threshold."""
        if not 0 <= value <= 10000:
            return False
        if not self._check_fofbctrl_connection():
            return False

        self._loop_max_orb_dist = value
        self._logger.info("Setting orbit distortion threshold...")
        if self._llfofb_dev.set_max_orb_distortion(
            value=value * self._const.CONV_UM_2_NM,
            timeout=self._const.DEF_TIMEWAIT,
        ):
            self._logger.info("...done!")
        else:
            self._logger.error("Failed to set threshold.")

        self.run_callbacks("LoopMaxOrbDistortion-RB", value)
        return True

    def set_loop_max_orbit_dist_enbl(self, value):
        """Set orbit distortion detection enable status."""
        if not self._check_fofbctrl_connection():
            return False

        act = "En" if value else "Dis"
        self._loop_max_orb_dist_enbl = value
        self._logger.info(act + "abling orbit distortion detection...")
        if self._llfofb_dev.set_max_orb_distortion_enbl(
            value=value, timeout=self._const.DEF_TIMEWAIT
        ):
            self._logger.info("...done!")
        else:
            self._logger.error("Failed to " + act + "able detection.")

        self.run_callbacks("LoopMaxOrbDistortionEnbl-Sts", value)
        return True

    def set_loop_packloss_detec_enbl(self, value):
        """Set packet loss detection enable status."""
        if not self._check_fofbctrl_connection():
            return False

        act = "En" if value else "Dis"
        self._loop_packloss_detec_enbl = value
        self._logger.info(act + "abling packet loss detection...")
        if self._llfofb_dev.set_min_bpm_count_enbl(
            value=value, timeout=self._const.DEF_TIMEWAIT
        ):
            self._logger.info("...done!")
        else:
            self._logger.error("Failed to " + act + "able detection.")

        self.run_callbacks("LoopPacketLossDetecEnbl-Sts", value)
        return True

    # --- devices configuration ---

    def cmd_corr_configure(self, _):
        """Configure corrector command."""
        self._logger.info("Received configure corrector command...")
        if not self._check_corr_connection():
            return False

        # saturation limits
        self._logger.info("Setting corrector saturation limits...")
        chn, chl = self._const.ch_names, self._ch_maxacccurr
        cvn, cvl = self._const.cv_names, self._cv_maxacccurr
        self._corrs_dev.set_fofbacc_satmax(chl, psnames=chn)
        self._corrs_dev.set_fofbacc_satmin(-chl, psnames=chn)
        self._corrs_dev.set_fofbacc_satmax(cvl, psnames=cvn)
        self._corrs_dev.set_fofbacc_satmin(-cvl, psnames=cvn)
        self._logger.info("...done!")
        # pwrstate
        self._check_set_corrs_pwrstate()
        # opmode
        self._check_set_corrs_opmode()
        # fofbacc_freeze
        self._set_corrs_fofbacc_freeze()
        # matrix coefficients
        self._set_corrs_coeffs()

        self._logger.info("Correctors configuration done!")
        return True

    def cmd_corr_pwrstate_on(self, _):
        """Set all corrector pwrstate to on."""
        self._logger.info("Received set corrector pwrstate to on...")
        if not self._check_corr_connection():
            return False

        self._logger.info("Setting all corrector pwrstate to on...")
        self._corrs_dev.set_pwrstate(self._const.OffOn.On)
        self._logger.info("...done!")
        return True

    def cmd_corr_pwrstate_off(self, _):
        """Set all corrector pwrstate to off."""
        self._logger.info("Received set corrector pwrstate to off...")
        if not self._check_corr_connection():
            return False

        self._logger.info("Setting all corrector pwrstate to off...")
        self._corrs_dev.set_pwrstate(self._const.OffOn.Off)
        self._logger.info("...done!")
        return True

    def cmd_corr_opmode_manual(self, _):
        """Set all corrector opmode to manual."""
        self._logger.info("Received set corrector opmode to manual...")
        if not self._check_corr_connection():
            return False

        self._logger.info("Setting all corrector opmode to manual...")
        self._corrs_dev.set_opmode(self._corrs_dev.OPMODE_STS.manual)
        self._logger.info("...done!")
        return True

    def cmd_corr_accfreeze_dsbl(self, _):
        """Set all corrector accumulator freeze state to Dsbl."""
        self._logger.info("Received set corrector AccFreeze to Dsbl...")
        if not self._check_corr_connection():
            return False

        self._logger.info("Setting AccFreeze to Dsbl...")
        self._corrs_dev.set_fofbacc_freeze(self._const.DsblEnbl.Dsbl)
        self._logger.info("...done!")
        return True

    def cmd_corr_accfreeze_enbl(self, _):
        """Set all corrector accumulator freeze state to Enbl."""
        self._logger.info("Received set corrector AccFreeze to Enbl...")
        if not self._check_corr_connection():
            return False

        self._logger.info("Setting AccFreeze to Enbl...")
        self._corrs_dev.set_fofbacc_freeze(self._const.DsblEnbl.Enbl)
        self._logger.info("...done!")
        return True

    def cmd_corr_accclear(self, _):
        """Clear all corrector accumulator."""
        self._logger.info("Received clear all corrector accumulator...")
        if not self._check_corr_connection():
            return False

        self._logger.info("Sending clear accumulator command...")
        self._corrs_dev.cmd_fofbacc_clear()
        self._logger.info("...done!")
        return True

    def cmd_corr_currzero(self, _):
        """Set all corrector current to zero."""
        self._logger.info("Received set corrector current to zero...")
        if not self._check_corr_connection():
            return False
        if (
            self._thread_currzero is not None
            and self._thread_currzero.is_alive()
        ):
            self._logger.error("Current ramp down already in progress.")
            return False

        self._thread_currzero = _epics.ca.CAThread(
            target=self._thread_corr_currzero, daemon=True
        )
        self._thread_currzero.start()
        return True

    def set_corr_currzero_duration(self, value):
        """Set corrector ramp down current duration."""
        if not 0 <= value <= 1000:
            return False

        self._corr_setcurrzero_dur = value
        self._logger.info("Changed corrector current ramp duration.")
        if (
            self._thread_currzero is not None
            and self._thread_currzero.is_alive()
        ):
            self._abort_thread_currzero = True
            self._thread_currzero.join()
            self._thread_currzero = _epics.ca.CAThread(
                target=self._thread_corr_currzero, daemon=True
            )
            self._thread_currzero.start()
        self.run_callbacks("CorrSetCurrZeroDuration-RB", value)
        return True

    def set_corr_accdec(self, option, value):
        """Set corrector accumulator decimation."""
        if (
            self._corr_accdec_enm != self._const.DecOpt.Custom
            and option == "value"
        ):
            return False

        if option == "enum":
            if value == self._const.DecOpt.FOFB:
                dec = 1
            elif value == self._const.DecOpt.Monit:
                if self._auxbpm.connected:
                    monit = self._auxbpm["INFOMONITRate-RB"]
                    fofb = self._auxbpm["INFOFOFBRate-RB"]
                    dec = monit // fofb
                else:
                    self._logger.warning("Could not read decimation from BPM")
                    self._logger.warning("rates. Using value 4600.")
                    dec = 4600
            else:
                dec = self._corr_accdec_val
            self._corr_accdec_enm = value
            self.run_callbacks("FOFBAccDecimation-Sts", value)
            self.run_callbacks("FOFBAccDecimation-SP", dec)
        else:
            dec = value
        self._corr_accdec_val = dec
        self.run_callbacks("FOFBAccDecimation-RB", dec)

        self._logger.info("Setting FOFB Acc decimation...")
        self._corrs_dev.set_fofbacc_decimation(dec)
        self._logger.info("...done!")

        return True

    def _thread_corr_currzero(self):
        if self._corrs_dev.check_current(0):
            self._logger.info("Current of all correctors already zeroed.")
            return

        self._logger.info("Sending all corrector current to zero...")

        init_curr = self._corrs_dev.current
        npts = int(self._corr_setcurrzero_dur * self._const.CURRZERO_RMP_FREQ)
        if npts != 0:
            xdata = _np.linspace(1, 0, npts)
            for idx, step in enumerate(xdata):
                curr = init_curr * step
                if self._check_thread_currzero_abort():
                    self._logger.info("...aborted.")
                    return
                self._logger.info(
                    f"{idx+1:02d}/{len(xdata):02d} -> Current={100*step:.1f}%"
                )
                self._corrs_dev.set_current(curr)
                _time.sleep(1 / self._const.CURRZERO_RMP_FREQ)

        self._corrs_dev.set_current(0)
        self._logger.info("...done!")

    def _check_thread_currzero_abort(self):
        if self._abort_thread_currzero:
            self._abort_thread_currzero = False
            return True
        return False

    def set_corr_accsatmax(self, device, value):
        """Set device FOFB accumulator saturation limits."""
        if not self._check_corr_connection():
            return False
        if not 0 <= value <= 0.95:
            return False

        setattr(self, "_" + device + "_maxacccurr", value)
        self._logger.info(
            "Setting " + device.upper() + " saturation limits..."
        )
        psnames = getattr(self._const, device + "_names")
        self._corrs_dev.set_fofbacc_satmax(value, psnames=psnames)
        self._corrs_dev.set_fofbacc_satmin(-value, psnames=psnames)
        self._logger.info("...done!")

        self._logger.info(
            "Changed "
            + device.upper()
            + " saturation limits to "
            + str(value)
            + "A."
        )
        self.run_callbacks(device.upper() + "AccSatMax-RB", value)
        return True

    def set_timeframelen(self, value):
        """Set FOFB controllers TimeFrameLen."""
        if not 500 <= value <= 10000:
            return False
        if not self._check_fofbctrl_connection():
            return False

        self._time_frame_len = value
        self._logger.info(f"Setting TimeFrameLen to {value}...")
        self._llfofb_dev.set_time_frame_len(
            value=self._time_frame_len, timeout=self._const.DEF_TIMEWAIT
        )
        self._logger.info("...done!")

        self.run_callbacks("TimeFrameLen-RB", self._time_frame_len)
        return True

    def cmd_fofbctrl_confbpmid(self, _):
        """Configure FOFB DCC BPMId command."""
        self._logger.info("Received configure FOFB DCC BPMId command...")
        if not self._check_fofbctrl_connection():
            return False
        self._logger.info("Checking...")
        if not self._llfofb_dev.bpm_id_configured:
            self._logger.info("Configuring DCC BPMIds...")
            if self._llfofb_dev.cmd_config_bpm_id():
                self._logger.info("Sent configuration to DCCs.")
            else:
                self._logger.error("Failed to configure DCCs.")
        else:
            self._logger.info("FOFB DCC BPMIds already configured.")
        return True

    def cmd_fofbctrl_syncnet(self, _):
        """Sync FOFB net command."""
        self._logger.info("Received sync FOFB net command...")
        if not self._check_fofbctrl_connection():
            return False
        self._logger.info("Checking...")

        if (
            self._thread_syncnet is not None
            and self._thread_syncnet.is_alive()
        ):
            self._logger.error("Net sync already in progress.")
            return False

        self._thread_syncnet = _epics.ca.CAThread(
            target=self._thread_fofbctrl_syncnet, daemon=True
        )
        self._thread_syncnet.start()
        return True

    def _thread_fofbctrl_syncnet(self):
        steps = [
            self._dsbl_fofbctrl_minbpmcnt_enbl,
            self._do_fofbctrl_syncnet,
            self._wait_fofbctrl_netsync,
            self._conf_fofbctrl_minbpmcnt_enbl,
        ]
        for func in steps:
            if not func():
                break

    def cmd_fofbctrl_syncreforb(self, _):
        """Sync FOFB RefOrb command."""
        self._logger.info("Received sync FOFB RefOrb command...")
        if not self._check_fofbctrl_connection():
            return False
        self._logger.info("Checking...")
        if not self._llfofb_dev.check_reforbx(
            self._reforbhw_x
        ) or not self._llfofb_dev.check_reforby(self._reforbhw_y):
            self._logger.info("Syncing FOFB RefOrb...")
            self._llfofb_dev.set_reforbx(self._reforbhw_x)
            self._llfofb_dev.set_reforby(self._reforbhw_y)
            self._logger.info("...done!")
        else:
            self._logger.info("FOFB RefOrb already synced.")
        return True

    def cmd_fofbctrl_synctframelen(self, _):
        """Sync FOFB controllers TimeFrameLen command."""
        self._logger.info("Received configure FOFB controllers")
        self._logger.info("TimeFrameLen command... Checking...")
        if not self._check_fofbctrl_connection():
            return False
        timeframe = self._time_frame_len
        if not _np.all(self._llfofb_dev.time_frame_len == timeframe):
            self._logger.info("Configuring TimeFrameLen PVs...")
            if self._llfofb_dev.set_time_frame_len(timeframe):
                self._logger.info("...done!")
            else:
                self._logger.error("Failed to configure TimeFrameLen.")
        else:
            self._logger.info("TimeFrameLen PVs already configured.")
        return True

    def cmd_fofbctrl_confbpmlogtrg(self, _):
        """Configure BPM logical triggers command."""
        self._logger.info("Received configure BPM Logical")
        if not self._check_fofbctrl_connection():
            return False
        self._logger.info("triggers command... Checking...")
        if not self._llfofb_dev.bpm_trigs_configured:
            self._logger.info("Configuring BPM logical triggers...")
            if self._llfofb_dev.cmd_config_bpm_trigs():
                self._logger.info("...done!")
            else:
                self._logger.error("Failed to configure BPM log.trigs.")
        else:
            self._logger.info("BPM logical triggers already configured.")
        return True

    def set_fofbctrl_syncuseenablelist(self, value):
        """Set whether to use or not BPMEnblList in sync."""
        if not self._check_fofbctrl_connection():
            return False
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False

        self._fofbctrl_syncuseenbllist = value
        self._update_fofbctrl_sync_enbllist()
        self._conf_fofbctrl_packetlossdetec()

        self._logger.info("Changed sync net command to ")
        self._logger.info(("" if value else "not ") + "use BPM EnableList.")
        self.run_callbacks("CtrlrSyncUseEnblList-Sts", value)
        return True

    def cmd_fofbctrl_syncmaxorbdist(self, _):
        """Sync FOFB controllers orbit distortion detection command."""
        self._logger.info("Received sync FOFB controllers orbit")
        self._logger.info("distortion detection command...Checking...")
        if not self._check_fofbctrl_connection():
            return False

        tout = self._const.DEF_TIMEWAIT

        # threshold
        thres = self._loop_max_orb_dist * self._const.CONV_UM_2_NM
        if not _np.all(self._llfofb_dev.max_orb_distortion == thres):
            self._logger.info("Setting MaxOrbDistortion PVs...")
            if self._llfofb_dev.set_max_orb_distortion(thres, timeout=tout):
                self._logger.info("...done!")
            else:
                self._logger.error("Failed to sync threshold.")
        else:
            self._logger.info("MaxOrbDistortion PVs already configured.")

        # enable status
        sts = self._loop_max_orb_dist_enbl
        if not _np.all(self._llfofb_dev.max_orb_distortion_enbl == sts):
            self._logger.info("Setting MaxOrbDistortionEnbl PVs...")
            if self._llfofb_dev.set_max_orb_distortion_enbl(sts, timeout=tout):
                self._logger.info("...done!")
            else:
                self._logger.error("Failed to sync enable status.")
        else:
            self._logger.info("MaxOrbDistortionEnbl PVs already configured.")
        return True

    def cmd_fofbctrl_syncpacklossdet(self, _):
        """Sync FOFB controllers packet loss detection command."""
        self._logger.info("Received sync FOFB controllers packet")
        self._logger.info("loss detection command...Checking...")
        if not self._check_fofbctrl_connection():
            return False
        self._conf_fofbctrl_packetlossdetec()
        return True

    def cmd_fofbctrl_reset(self, _):
        """Reset FOFB controllers interlock command."""
        self._logger.info("Received reset FOFB controllers command...")
        if not self._check_fofbctrl_connection():
            return False
        self._do_fofbctrl_reset()
        return True

    def cmd_fofbctrl_dsblsysid(self, _):
        """Disable FOFB controllers system identification excitation."""
        self._logger.info("Received disable FOFB controllers SYSID...")
        if not self._check_fofbctrl_connection():
            return False
        self._logger.info("Disabling SYSID excitation...")
        self._llfofb_dev.cmd_dsbl_sysid_exc()
        self._logger.info("...done!")
        return True

    # --- reference orbit ---

    def set_reforbit(self, plane, value):
        """Set reference orbit."""
        self._logger.info(f"Setting New RefOrb{plane.upper()}...")

        # check size
        ref = _np.array(value, dtype=float)
        if ref.size != self._const.reforb_size:
            self._logger.error(" Wrong RefOrb Size.")
            return False

        # set internal states and LLFOFB reforb
        # physical units
        setattr(self, "_reforb_" + plane.lower(), ref)
        # hardware units
        refhw = ref * self._const.CONV_UM_2_NM
        refhw = _np.round(refhw)  # round, low level expect it to be int
        refhw = _np.roll(refhw, 1)  # make BPM 01M1 the first element
        setattr(self, "_reforbhw_" + plane.lower(), refhw)

        # do not set reforb to controllers and save to file in initialization
        if self._init:
            # set reforb to FOFB controllers
            func = getattr(self._llfofb_dev, "set_reforb" + plane.lower())
            func(refhw)

            # save to autosave file
            self._save_reforbit()

        # update readback PV
        self.run_callbacks(f"RefOrb{plane.upper()}-RB", list(ref.ravel()))
        self.run_callbacks(f"RefOrbHw{plane.upper()}-Mon", refhw)
        self._logger.info("...done!")
        return True

    def _load_reforbit(self):
        filename = self._const.reforb_fname
        if not _os.path.isfile(filename):
            return False
        self._logger.info("Loading RefOrbits from file...")
        refx, refy = _np.loadtxt(filename, unpack=True)
        okx = self.set_reforbit("x", refx)
        oky = self.set_reforbit("y", refy)
        okk = all([okx, oky])
        if okk:
            self._logger.info("Loaded RefOrbits!")
        else:
            self._logger.error("Problem loading RefOrbits from file.")
        return okk

    def _save_reforbit(self):
        filename = self._const.reforb_fname
        refx, refy = self._reforb_x, self._reforb_y
        orbs = _np.array([refx, refy]).T
        try:
            path = _os.path.split(filename)[0]
            _os.makedirs(path, exist_ok=True)
            _np.savetxt(filename, orbs)
        except FileNotFoundError:
            self._logger.warning("Could not save ref.orbit to file.")

    # --- matrix manipulation ---

    def set_respmat(self, value):
        """Set response matrix."""
        self._logger.info("Setting New RespMat...")

        # check size
        mat = _np.array(value, dtype=float)
        matb = mat
        if mat.size != self._const.matrix_size:
            self._logger.error(
                f"Wrong RespMat Size ({mat.size}, "
                f"expected {self._const.matrix_size})."
            )
            return False

        # reshape
        nrc = self._const.nr_corrs
        mat = _np.reshape(mat, [-1, nrc])

        # check if matrix is invertible
        old_ = self._respmat.copy()
        self._respmat = mat
        if not self._calc_matrices():
            self._respmat = old_
            return False

        # if ok, save matrix
        if self._init:
            self._save_respmat(matb)

        # update readback pv
        self.run_callbacks("RespMat-RB", list(self._respmat.ravel()))

        return True

    def _load_respmat(self):
        filename = self._const.respmat_fname
        if not _os.path.isfile(filename):
            return False
        self._logger.info("Loading RespMat from file...")
        okk = self.set_respmat(_np.loadtxt(filename))
        if okk:
            self._logger.info("Loaded RespMat!")
        else:
            self._logger.error("Problem loading RespMat from file.")
        return okk

    def _save_respmat(self, mat):
        try:
            filename = self._const.respmat_fname
            path = _os.path.split(filename)[0]
            _os.makedirs(path, exist_ok=True)
            _np.savetxt(filename, mat)
        except FileNotFoundError:
            self._logger.warning("Could not save matrix to file.")

    def set_enbllist(self, device, value):
        """Set enable list for device."""
        if self._loop_state:
            self._logger.error("Open loop before continuing.")
            return False
        if (
            self._thread_enbllist is not None
            and self._thread_enbllist.is_alive()
        ):
            self._abort_thread_enbllist = True
            self._thread_enbllist.join()
        self._logger.info("Setting {0:s} EnblList".format(device.upper()))

        # check size
        bkup = self._enable_lists[device]
        new = _np.array(value, dtype=bool)
        if bkup.size != new.size:
            self._logger.error(
                "Wrong {0:s} EnblList size.".format(device.upper())
            )
            return False

        self._enable_lists[device] = new

        # do not set enable lists and save to file in initialization
        if self._init:
            # check if matrix is invertible
            if not self._calc_matrices():
                self._enable_lists[device] = bkup
                return False

            # handle devices enable configuration
            self._thread_enbllist = _epics.ca.CAThread(
                target=self._handle_devices_enblconfig,
                args=[device],
                daemon=True,
            )
            self._thread_enbllist.start()

            # save to autosave files
            self._save_enbllist(device, _np.array([value], dtype=bool))

        # update readback pv
        if device == "rf":
            self.run_callbacks("UseRF-Sts", bool(value))
        else:
            self.run_callbacks(device.upper() + "EnblList-RB", new)

        return True

    def _handle_devices_enblconfig(self, device):
        if device in ["ch", "cv"]:
            if self._check_corr_connection():
                self._check_set_corrs_opmode()
        elif device in ["bpmx", "bpmy"]:
            self._update_fofbctrl_sync_enbllist()
            if self._check_fofbctrl_connection():
                steps = [
                    self._dsbl_fofbctrl_minbpmcnt_enbl,
                    self._do_fofbctrl_syncnet,
                    self._wait_fofbctrl_netsync,
                    self._conf_fofbctrl_minbpmcnt,
                    self._conf_fofbctrl_minbpmcnt_enbl,
                ]
                for func in steps:
                    if self._check_thread_enbllist_abort():
                        break
                    if not func():
                        break

    def _check_thread_enbllist_abort(self):
        if self._abort_thread_enbllist:
            self._abort_thread_enbllist = False
            return True
        return False

    @property
    def bpm_enbllist(self):
        """BPM enable list."""
        enbl = self._enable_lists
        return _np.hstack([enbl["bpmx"], enbl["bpmy"]])

    @property
    def corr_enbllist(self):
        """Corrector enable list."""
        enbl = self._enable_lists
        return _np.hstack([enbl["ch"], enbl["cv"], enbl["rf"]])

    def _load_enbllist(self, device):
        filename = getattr(self._const, device + "enbl_fname")
        if not _os.path.isfile(filename):
            return
        okl = self.set_enbllist(device, _np.loadtxt(filename))
        if okl:
            self._logger.info(f"Loaded {device} enable list!")
        else:
            self._logger.error(
                f"Problem loading {device} enable list from file."
            )
        return okl

    def _save_enbllist(self, device, value):
        try:
            filename = getattr(self._const, device + "enbl_fname")
            path = _os.path.split(filename)[0]
            _os.makedirs(path, exist_ok=True)
            _np.savetxt(filename, value)
        except FileNotFoundError:
            self._logger.warning(
                f"Could not save {device} enable list to file."
            )

    def set_min_sing_value(self, value):
        """Set minimum singular values."""
        bkup = self._min_sing_val
        self._min_sing_val = float(value)
        if not self._calc_matrices():
            self._min_sing_val = bkup
            return False
        self.run_callbacks("MinSingValue-RB", self._min_sing_val)
        return True

    def set_tikhonov_reg_const(self, value):
        """Set Tikhonov regularization constant."""
        bkup = self._tikhonov_reg_const
        self._tikhonov_reg_const = float(value)
        if not self._calc_matrices():
            self._tikhonov_reg_const = bkup
            return False
        self.run_callbacks("TikhonovRegConst-RB", self._tikhonov_reg_const)
        return True

    def set_invrespmat_normmode(self, value):
        """Set corrector coefficients normalization mode."""
        if not 0 <= value < len(_ETypes.GLOB_INDIV):
            return False

        self._logger.info(
            "Changed normalization mode to "
            + str(self._const.GlobIndiv._fields[value])
            + "."
        )
        self._invrespmat_normmode = value

        self._calc_corrs_coeffs()
        self._set_corrs_coeffs()

        self.run_callbacks("InvRespMatNormMode-Sts", self._invrespmat_normmode)
        return True

    def _calc_matrices(self):
        self._logger.info("Calculating Inverse Matrix...")

        if not self._check_corr_connection():
            return False

        selbpm = self.bpm_enbllist
        if not any(selbpm):
            self._logger.error("No BPM selected in EnblList")
            return False
        selcorr = self.corr_enbllist
        if not any(selcorr):
            self._logger.error("No Corrector selected in EnblList")
            return False

        # apply device selection
        selmat = selbpm[:, None] * selcorr[None, :]
        if selmat.size != self._respmat.size:
            return False
        mat = self._respmat.copy()
        mat = mat[selmat]
        mat = _np.reshape(mat, [sum(selbpm), sum(selcorr)])

        # calculate SVD
        try:
            _uo, _so, _vo = _np.linalg.svd(mat, full_matrices=False)
        except _np.linalg.LinAlgError():
            self._logger.error("Could not calculate SVD")
            return False

        # handle singular values
        # select singular values greater than minimum
        idcs = _so > self._min_sing_val
        _sr = _so[idcs]
        nrs = _np.sum(idcs)
        if not nrs:
            self._logger.error("All Singular Values below minimum.")
            return False
        # apply Tikhonov regularization
        regc = self._tikhonov_reg_const
        regc *= regc
        inv_s = _np.zeros(_so.size, dtype=float)
        inv_s[idcs] = _sr / (_sr * _sr + regc)
        # calculate processed singular values
        _sp = _np.zeros(_so.size, dtype=float)
        _sp[idcs] = 1 / inv_s[idcs]

        # check if inverse matrix is valid
        invmat = _np.dot(_vo.T * inv_s, _uo.T)
        if _np.any(_np.isnan(invmat)) or _np.any(_np.isinf(invmat)):
            self._logger.error("Inverse contains nan or inf.")
            return False

        # reconstruct filtered and regularized matrix in physical units
        matr = _np.dot(_uo * _sp, _vo)

        # convert matrix to hardware units
        str2curr = _np.r_[self._corrs_dev.strength_2_current_factor, 1.0]
        currgain = _np.r_[self._corrs_dev.curr_gain, 1.0]
        if _np.any(str2curr == 0) or _np.any(currgain == 0):
            self._logger.error("Could not calculate hardware unit")
            self._logger.error('matrix, CurrGain or "urad to A" ')
            self._logger.error("factor have zero values.")
            return False
        # unit convertion: um/urad (1)-> nm/urad (2)-> nm/A (3)-> nm/counts
        matc = matr * self._const.CONV_UM_2_NM
        matc = matc / str2curr[selcorr]
        matc = matc * currgain[selcorr]

        # obtain pseudoinverse
        # calculate SVD for converted matrix
        _uc, _sc, _vc = _np.linalg.svd(matc, full_matrices=False)
        # handle singular value selection
        idcsc = _sc / _sc.max() >= self._const.SINGVALHW_THRS
        inv_sc = _np.zeros(_so.size, dtype=float)
        inv_sc[idcsc] = 1 / _sc[idcsc]
        # calculate pseudoinverse of converted matrix from SVD
        invmatc = _np.dot(_vc.T * inv_sc, _uc.T)

        # update internal states and PVs
        sing_vals = _np.zeros(self._const.nr_svals, dtype=float)
        sing_vals[: _so.size] = _so
        self.run_callbacks("SingValuesRaw-Mon", sing_vals)

        sing_vals = _np.zeros(self._const.nr_svals, dtype=float)
        sing_vals[: _sp.size] = _sp
        self.run_callbacks("SingValues-Mon", sing_vals)
        self.run_callbacks("NrSingValues-Mon", nrs)

        self._invrespmat = _np.zeros(self._respmat.shape, dtype=float).T
        self._invrespmat[selmat.T] = invmat.ravel()
        self.run_callbacks("InvRespMat-Mon", list(self._invrespmat.ravel()))

        respmat_proc = _np.zeros(self._respmat.shape, dtype=float)
        respmat_proc[selmat] = matr.ravel()
        self.run_callbacks("RespMat-Mon", list(respmat_proc.ravel()))

        sing_vals = _np.zeros(self._const.nr_svals, dtype=float)
        sing_vals[: _sc.size] = _sc
        self.run_callbacks("SingValuesHw-Mon", sing_vals)

        self._invrespmatconv = _np.zeros(self._respmat.shape, dtype=float).T
        self._invrespmatconv[selmat.T] = invmatc.ravel()
        self.run_callbacks(
            "InvRespMatHw-Mon", list(self._invrespmatconv.ravel())
        )

        respmatconv_proc = _np.zeros(self._respmat.shape, dtype=float)
        respmatconv_proc[selmat] = matc.ravel()
        self.run_callbacks("RespMatHw-Mon", list(respmatconv_proc.ravel()))

        # send new matrix to low level FOFB
        self._calc_corrs_coeffs()
        if self._init:
            self._set_corrs_coeffs()

        self._logger.info("Ok!")
        return True

    # --- matrix measurement ---

    def set_respmat_meas_state(self, value):
        """Set response matrix measure state."""
        if value == self._const.MeasRespMatCmd.Start:
            return self._start_meas_respmat()
        if value == self._const.MeasRespMatCmd.Stop:
            return self._stop_meas_respmat()
        if value == self._const.MeasRespMatCmd.Reset:
            return self._reset_meas_respmat()
        return True

    def set_respmat_meas_kick(self, plane, value):
        """Set response matrix measure kick value for plane [urad]."""
        self._meas_respmat_kick[plane] = value
        self.run_callbacks("MeasRespMatKick" + plane.upper() + "-RB", value)
        return True

    def set_respmat_meas_wait_time(self, value):
        """Set response matrix measure wait time [s]."""
        self._meas_respmat_wait = value
        self.run_callbacks("MeasRespMatWait-RB", value)
        return True

    def _start_meas_respmat(self):
        if self._loop_state == self._const.LoopState.Closed:
            self._logger.error("Open FOFB loop before continue.")
            return False
        if not self._sofb_check_config():
            self._logger.error("Aborted.")
            return False
        if self._measuring_respmat:
            self._logger.error("Measurement already in progress...")
            return False
        if not self.havebeam:
            self._logger.error("Do not have stored beam. Aborted.")
            return False
        self._logger.info("Starting RespMat measurement.")
        self._measuring_respmat = True
        self._meas_respmat_thread = _epics.ca.CAThread(
            target=self._do_meas_respmat, daemon=True
        )
        self._meas_respmat_thread.start()
        return True

    def _stop_meas_respmat(self):
        if not self._measuring_respmat:
            self._logger.error("No Measurement occurring.")
            return False
        self._logger.info("Aborting measurement. Wait...")
        self._measuring_respmat = False
        return True

    def _reset_meas_respmat(self):
        if self._measuring_respmat:
            self._logger.warning("measurement in progress...")
            return False
        self._logger.info("Reseting measurement status.")
        self.run_callbacks("MeasRespMat-Mon", self._const.MeasRespMatMon.Idle)
        return True

    def _do_meas_respmat(self):
        self.run_callbacks(
            "MeasRespMat-Mon", self._const.MeasRespMatMon.Measuring
        )
        mat = list()
        enbllist = self.corr_enbllist
        sum_enbld = sum(enbllist)

        orbzero = _np.zeros(len(self.bpm_enbllist), dtype=float)
        for i in range(self._const.nr_corrs):
            if not self._measuring_respmat:
                self.run_callbacks(
                    "MeasRespMat-Mon", self._const.MeasRespMatMon.Aborted
                )
                self._logger.info("Measurement stopped.")
                for _ in range(i, self._const.nr_corrs):
                    mat.append(orbzero)
                break
            if not self.havebeam:
                self.run_callbacks(
                    "MeasRespMat-Mon", self._const.MeasRespMatMon.Aborted
                )
                self._logger.error(
                    "Cannot Measure, We do not have stored beam!"
                )
                for _ in range(i, self._const.nr_corrs):
                    mat.append(orbzero)
                break
            if not enbllist[i]:
                mat.append(orbzero)
                continue

            if i < self._const.nr_ch + self._const.nr_cv:
                dev = self._corrs_dev[i]
                conv = self._corrs_dev.psconvs[i]
                self._logger.info("%d/%d -> %s", i + 1, sum_enbld, dev.devname)

                corrtype = "ch" if "FCH" in dev.devname else "cv"
                delta = self._meas_respmat_kick[corrtype]

                orig_kick = dev.strength
                orig_curr = dev.current

                kickp = orig_kick + delta / 2
                dev.current = conv.conv_strength_2_current(kickp)
                _time.sleep(self._meas_respmat_wait)
                orbp = self._sofb_get_orbit()

                kickn = orig_kick - delta / 2
                dev.current = conv.conv_strength_2_current(kickn)
                _time.sleep(self._meas_respmat_wait)
                orbn = self._sofb_get_orbit()

                dev.current = orig_curr
            elif i < self._const.nr_corrs:
                dev = self.rf_dev
                self._logger.info("%d/%d -> %s", i + 1, sum_enbld, dev.devname)

                delta = self._meas_respmat_kick["rf"]

                orig_freq = dev.frequency

                dev.frequency = orig_freq + delta / 2
                _time.sleep(self._meas_respmat_wait)
                orbp = self._sofb_get_orbit()

                dev.frequency = orig_freq - delta / 2
                _time.sleep(self._meas_respmat_wait)
                orbn = self._sofb_get_orbit()

                dev.frequency = orig_freq
            mat.append((orbp - orbn) / delta)

        mat = _np.array(mat).T
        self.set_respmat(list(mat.ravel()))
        self.run_callbacks(
            "MeasRespMat-Mon", self._const.MeasRespMatMon.Completed
        )
        self._measuring_respmat = False
        self._logger.info("RespMat Measurement Completed!")

    def _sofb_check_config(self):
        if not self._sisofb_dev.autocorrsts == _Const.LoopState.Open:
            self._logger.error("Open SOFB loop before continue.")
            return False
        if not self._sisofb_dev.opmode_str == "SlowOrb":
            self._logger.error("SOFBMode is different from SlowOrb.")
            return False
        if not self._sisofb_dev.wait_orb_status_ok(timeout=0.5):
            self._logger.error("SOFB orbit status is not ok.")
            return False
        return True

    def _sofb_get_orbit(self):
        self._sisofb_dev.cmd_reset()
        _time.sleep(self._const.DEF_TIMESLEEP)
        self._sisofb_dev.wait_buffer()
        orbx, orby = self._sisofb_dev.orbx, self._sisofb_dev.orby
        return _np.hstack([orbx, orby])

    # --- callbacks ---

    def _callback_havebeam(self, value, **kws):
        if not value and self._loop_state == self._const.LoopState.Closed:
            self._logger.fatal("We do not have stored beam!")
            self._logger.fatal("Opening FOFB loop...")
            self.set_loop_state(self._const.LoopState.Open, abort=True)

    def _callback_loopintlk(self, pvname, value, **kws):
        sub = _PVName(pvname).sub[:2]
        old = self._intlk_values[pvname]
        orbdis = _get_bit(value, 0) and not _get_bit(old, 0)
        paclos = _get_bit(value, 1) and not _get_bit(old, 1)
        self._intlk_values[pvname] = value
        if value != 0:
            if orbdis or paclos:
                fun = getattr(
                    self._logger, "fatal" if self._loop_state else "warning"
                )
                msg = ":Ctrlr." + sub + " detected "
                msg += "large orb.dist.!" if orbdis else "packet loss!"
                fun(msg)

            if self._loop_state != self._const.LoopState.Closed:
                return

            if (
                self._thread_loopstate is None
                or (
                    self._thread_loopstate is not None
                    and not self._thread_loopstate.is_alive()
                )
                or (
                    self._thread_loopstate is not None
                    and self._thread_loopstate.is_alive()
                    and self._loop_state_lastsp != self._const.LoopState.Open
                )
            ):
                self._logger.fatal("Opening FOFB loop...")
                self.run_callbacks("LoopState-Sel", self._const.LoopState.Open)
                self.run_callbacks("LoopState-Sts", self._const.LoopState.Open)
                self.set_loop_state(self._const.LoopState.Open, abort=True)

    # --- auxiliary corrector and fofbcontroller methods ---

    def _check_corr_connection(self):
        if self._corrs_dev.connected:
            return True
        self._logger.error("Correctors not connected... aborted.")
        return False

    def _check_set_corrs_pwrstate(self):
        """Check and configure pwrstate.

        Control only correctors that are in the enable list.
        """
        self._logger.info("Checking corrector pwrstate...")
        pwrstate = _Const.OffOn.On
        is_ok = 1 * (self._corrs_dev.pwrstate == pwrstate)
        idcs = _np.where((1 * self.corr_enbllist[:-1] - is_ok) > 0)[0]
        if idcs.size:
            self._logger.info("Configuring corrector pwrstate...")
            self._corrs_dev.set_pwrstate(pwrstate, psindices=idcs)
            if self._corrs_dev.check_pwrstate(
                pwrstate, psindices=idcs, timeout=5
            ):
                self._logger.info("...done!")
                return True
            self._logger.error("Failed to set corrector pwrstate.")
            return False
        self._logger.info("All ok.")
        return True

    def _check_set_corrs_opmode(self):
        """Check and configure opmode.

        Control only correctors that are in the enable list.
        """
        self._logger.info("Checking corrector opmode...")
        opmode = (
            self._corrs_dev.OPMODE_STS.manual
            if self._loop_state == self._const.LoopState.Open
            else self._corrs_dev.OPMODE_STS.fofb
        )
        is_ok = 1 * (self._corrs_dev.opmode == opmode)
        idcs = _np.where((1 * self.corr_enbllist[:-1] - is_ok) > 0)[0]
        if idcs.size:
            self._logger.info("Configuring corrector opmode...")
            self._corrs_dev.set_opmode(opmode, psindices=idcs)
            if self._corrs_dev.check_opmode(opmode, psindices=idcs, timeout=5):
                self._logger.info("...done!")
                return True
            self._logger.error("Failed to set corrector opmode.")
            return False
        self._logger.info("All ok.")
        return True

    def _set_corrs_fofbacc_freeze(self):
        """Configure FOFBAccFreeze state.

        Keep in accordance with enable list and loop_state.
        """
        self._logger.info("Setting corrector FOFCAccFreeze...")
        freeze = self._get_corrs_fofbacc_freeze_desired()
        self._corrs_dev.set_fofbacc_freeze(freeze)
        self._logger.info("...done!")

    def _get_corrs_fofbacc_freeze_desired(self):
        if self._loop_state == self._const.LoopState.Open:
            freeze = _np.ones(len(self.corr_enbllist[:-1]))
        else:
            freeze = 1 * _np.logical_not(self.corr_enbllist[:-1])
        return freeze

    def _calc_corrs_coeffs(self, log=True):
        """Calculate corrector coefficients and gains."""
        if log:
            self._logger.info("Calculating corrector coefficients ")
            self._logger.info("and FOFB pre-accumulator gains...")

        # calculate coefficients and gains
        invmat = self._invrespmatconv[:-1]  # remove RF line
        coeffs = _np.zeros(invmat.shape)
        gains_mon = _np.zeros(self._const.nr_chcv)

        lgain_h, lgain_h_mon = self._loop_gain_h, self._loop_gain_mon_h
        lgain_v, lgain_v_mon = self._loop_gain_v, self._loop_gain_mon_v
        nrch, nrcv = self._const.nr_ch, self._const.nr_cv
        slch, slcv = slice(0, nrch), slice(nrch, nrch + nrcv)

        reso = self._const.ACCGAIN_RESO

        if self._invrespmat_normmode == self._const.GlobIndiv.Global:
            maxval = _np.amax(abs(invmat))

            gain_h_mon = _np.ceil(maxval * lgain_h_mon / reso) * reso
            gain_h = _np.ceil(maxval * lgain_h / reso) * reso
            if gain_h != 0:
                norm_h = gain_h / lgain_h
                coeffs[slch, :] = invmat[slch, :] / norm_h
                gains_mon[slch] = gain_h_mon * _np.ones(nrch)

            gain_v_mon = _np.ceil(maxval * lgain_v_mon / reso) * reso
            gain_v = _np.ceil(maxval * lgain_v / reso) * reso
            if gain_v != 0:
                norm_v = gain_v / lgain_v
                coeffs[slcv, :] = invmat[slcv, :] / norm_v
                gains_mon[slcv] = gain_v_mon * _np.ones(nrcv)

        elif self._invrespmat_normmode == self._const.GlobIndiv.Individual:
            maxval = _np.amax(abs(invmat), axis=1)

            gains_mon[slch] = (
                _np.ceil(maxval[slch] * lgain_h_mon / reso) * reso
            )
            gains_mon[slcv] = (
                _np.ceil(maxval[slcv] * lgain_v_mon / reso) * reso
            )

            gains = _np.zeros(self._const.nr_chcv)
            gains[slch] = _np.ceil(maxval[slch] * lgain_h / reso) * reso
            gains[slcv] = _np.ceil(maxval[slcv] * lgain_v / reso) * reso
            norm = _np.zeros(self._const.nr_chcv)
            norm[slch] = gains[slch] / lgain_h
            norm[slcv] = gains[slcv] / lgain_v
            idcs = norm > 0
            coeffs[idcs] = invmat[idcs] / norm[idcs][:, None]

        # handle FOFB BPM ordering
        nrbpm = self._const.nr_bpms
        coeffs[:, :nrbpm] = _np.roll(coeffs[:, :nrbpm], 1, axis=1)
        coeffs[:, nrbpm:] = _np.roll(coeffs[:, nrbpm:], 1, axis=1)

        # set internal states
        self._pscoeffs = coeffs
        self._psgains = gains_mon
        # update PVs
        self.run_callbacks("CorrCoeffs-Mon", list(self._pscoeffs.ravel()))
        self.run_callbacks("CorrGains-Mon", list(self._psgains.ravel()))

        if log:
            self._logger.info("...done!")

    def _set_corrs_coeffs(self, log=True):
        """Set corrector coefficients and gains."""
        if log:
            self._logger.info("Setting corrector gains and coefficients...")
        if not self._check_corr_connection():
            return False
        if not self._corrs_dev.check_invrespmat_row(self._pscoeffs):
            self._corrs_dev.set_invrespmat_row(self._pscoeffs)
        self._corrs_dev.set_fofbacc_gain(self._psgains)
        if log:
            self._logger.info("...done!")
        return True

    def _check_fofbctrl_connection(self):
        if self._llfofb_dev.connected:
            return True
        self._logger.error("FOFB Controllers not connected...")
        self._logger.error("aborted.")
        return False

    def _update_fofbctrl_sync_enbllist(self):
        if self._fofbctrl_syncuseenbllist:
            bpmx = self._enable_lists["bpmx"]
            bpmy = self._enable_lists["bpmy"]
            mini = self._const.dccenbl_min
            dccenbl = _np.logical_or.reduce([bpmx, bpmy, mini])
            bpms = self._llfofb_dev.get_dccfmc_visible_bpms(
                [self._const.bpm_names[i] for i, s in enumerate(dccenbl) if s]
            )
            dccenbl = _np.array([b in bpms for b in self._const.bpm_names])
        else:
            dccenbl = _np.ones(self._const.nr_bpms, dtype=bool)
        self._fofbctrl_syncenbllist = dccenbl
        self.run_callbacks("CtrlrSyncEnblList-Mon", dccenbl)

    def _get_fofbctrl_bpmdcc_enbl(self):
        return [
            self._const.bpm_names[i]
            for i, s in enumerate(self._fofbctrl_syncenbllist)
            if s
        ]

    def _do_fofbctrl_syncnet(self):
        bpms = self._get_fofbctrl_bpmdcc_enbl()
        self._logger.info("Syncing FOFB net...")
        if self._llfofb_dev.cmd_sync_net(bpms=bpms):
            self._logger.info("Sync sent to FOFB net.")
            return True
        self._logger.error("Failed to sync FOFB net.")
        return False

    def _wait_fofbctrl_netsync(self):
        bpms = self._get_fofbctrl_bpmdcc_enbl()
        _t0 = _time.time()
        while _time.time() - _t0 < self._const.DEF_TIMEMINWAIT:
            if self._llfofb_dev.check_net_synced(bpms=bpms):
                self._logger.info("Net synced, continuing...")
                return True
        self._logger.error("Net not synced.")
        return False

    def _conf_fofbctrl_packetlossdetec(self):
        # disable enable status
        self._dsbl_fofbctrl_minbpmcnt_enbl()
        # set minimum packet count
        self._conf_fofbctrl_minbpmcnt()
        # return enable status
        self._conf_fofbctrl_minbpmcnt_enbl()

    def _dsbl_fofbctrl_minbpmcnt_enbl(self):
        timeout = self._const.DEF_TIMEWAIT
        self._logger.info("Disabling packet loss detection...")
        self._llfofb_dev.set_min_bpm_count_enbl(0, timeout=timeout)
        self._logger.info("...done!")
        return True

    def _conf_fofbctrl_minbpmcnt(self):
        timeout = self._const.DEF_TIMEWAIT
        count = int(_np.sum(self._fofbctrl_syncenbllist))
        if not _np.all(self._llfofb_dev.min_bpm_count == count):
            self._logger.info("Setting MinBPMCnt PVs...")
            if self._llfofb_dev.set_min_bpm_count(count, timeout=timeout):
                self._logger.info("...done!")
            else:
                self._logger.error("Failed to sync MinBPMCnt.")
        else:
            self._logger.info("MinBPMCnt PVs already configured.")
        return True

    def _conf_fofbctrl_minbpmcnt_enbl(self):
        timeout = self._const.DEF_TIMEWAIT
        sts = self._loop_packloss_detec_enbl
        if not _np.all(self._llfofb_dev.min_bpm_count_enbl == sts):
            self._logger.info("Setting MinBPMCntEnbl PVs...")
            if self._llfofb_dev.set_min_bpm_count_enbl(sts, timeout=timeout):
                self._logger.info("...done!")
            else:
                self._logger.error("Failed to sync enable status.")
        else:
            self._logger.info("MinBPMCntEnbl PVs already configured.")
        return True

    def _do_fofbctrl_reset(self):
        if self._thread_reset is not None and self._thread_reset.is_alive():
            self._logger.error("reset already in progress.")
            return False

        self._thread_reset = _epics.ca.CAThread(
            target=self._thread_fofbctrl_reset, daemon=True
        )
        self._thread_reset.start()
        return True

    def _thread_fofbctrl_reset(self):
        self._logger.info("Reseting FOFB loop...")

        # disabling packet loss detection
        self._dsbl_fofbctrl_minbpmcnt_enbl()

        # reset interlock
        self._logger.info("Sending reset to FOFB controllers...")
        if self._llfofb_dev.cmd_reset():
            self._logger.info("...done!")
        else:
            self._logger.error("Failed to reset controllers.")
            return

        # wait for packet count to be correct
        if not self._wait_fofbctrl_netsync():
            return

        # return packet loss detection to correct status
        self._logger.info("Reconfiguring packet loss detection...")
        self._conf_fofbctrl_minbpmcnt_enbl()

    # --- auxiliary log methods ---

    def _check_corrs_configs(self):
        tplanned = 1.0 / App.SCAN_FREQUENCY
        while not self.quit:
            if not self.scanning:
                _time.sleep(tplanned)
                continue

            _t0 = _time.time()

            # correctors status
            value = 0
            cdev = self._corrs_dev
            if self._corrs_dev.connected:
                idcs = _np.where(self.corr_enbllist[:-1] == 1)[0]
                # PwrStateOn
                state = self._const.OffOn.On
                value = _updt_bit(
                    value,
                    1,
                    not cdev.check_pwrstate(
                        state, psindices=idcs, timeout=0.2
                    ),
                )
                # OpModeConfigured
                opmode = (
                    cdev.OPMODE_STS.manual
                    if self._loop_state == self._const.LoopState.Open
                    else cdev.OPMODE_STS.fofb
                )
                value = _updt_bit(
                    value,
                    2,
                    not cdev.check_opmode(opmode, psindices=idcs, timeout=0.2),
                )
                # AccFreezeConfigured
                freeze = self._get_corrs_fofbacc_freeze_desired()
                value = _updt_bit(
                    value,
                    3,
                    not cdev.check_fofbacc_freeze(freeze, timeout=0.2),
                )
                # InvRespMatRowSynced
                value = _updt_bit(
                    value, 4, not cdev.check_invrespmat_row(self._pscoeffs)
                )
                # AccGainSynced
                value = _updt_bit(
                    value, 5, not cdev.check_fofbacc_gain(self._psgains)
                )
                # AccSatLimsSynced
                chn, chl = self._const.ch_names, self._ch_maxacccurr
                cvn, cvl = self._const.cv_names, self._cv_maxacccurr
                isok = cdev.check_fofbacc_satmax(chl, psnames=chn)
                isok &= cdev.check_fofbacc_satmin(-chl, psnames=chn)
                isok &= cdev.check_fofbacc_satmax(cvl, psnames=cvn)
                isok &= cdev.check_fofbacc_satmin(-cvl, psnames=cvn)
                value = _updt_bit(value, 6, not isok)
                # AccDecimationSynced
                dec = self._corr_accdec_val
                value = _updt_bit(
                    value, 7, not cdev.check_fofbacc_decimation(dec)
                )
            else:
                value = 0b11111111

            self._corr_status = value
            self.run_callbacks("CorrStatus-Mon", self._corr_status)

            ttook = _time.time() - _t0
            tsleep = tplanned - ttook
            if tsleep > 0:
                _time.sleep(tsleep)
                continue
            self._logger.warning(
                "Corrector check took more than planned: %.3f/%.3f",
                ttook,
                tplanned,
                extra={"ioc_only": True},
            )

    def _check_ctrls_configs(self):
        tplanned = 1.0 / App.SCAN_FREQUENCY
        while not self.quit:
            if not self.scanning:
                _time.sleep(tplanned)
                continue

            _t0 = _time.time()

            # FOFB controllers status
            value = 0
            fdev = self._llfofb_dev
            if fdev.connected:
                # BPMIdsConfigured
                value = _updt_bit(value, 1, not fdev.bpm_id_configured)
                # NetSynced
                bpms = self._get_fofbctrl_bpmdcc_enbl()
                value = _updt_bit(
                    value, 2, not fdev.check_net_synced(bpms=bpms)
                )
                # LinkPartnerConnected
                value = _updt_bit(value, 3, not fdev.linkpartners_connected)
                # RefOrbSynced
                value = _updt_bit(
                    value,
                    4,
                    not fdev.check_reforbx(self._reforbhw_x)
                    or not fdev.check_reforby(self._reforbhw_y),
                )
                # TimeFrameLenSynced
                tframelen = self._time_frame_len
                value = _updt_bit(
                    value, 5, not _np.all(fdev.time_frame_len == tframelen)
                )
                # BPMLogTrigsConfigured
                value = _updt_bit(value, 6, not fdev.bpm_trigs_configured)
                # OrbDistortionDetectionSynced
                sts = self._loop_max_orb_dist_enbl
                sts_ok = fdev.max_orb_distortion_enbl == sts
                thres = self._loop_max_orb_dist * self._const.CONV_UM_2_NM
                thres_ok = fdev.max_orb_distortion == thres
                value = _updt_bit(
                    value, 7, not _np.all(sts_ok) or not _np.all(thres_ok)
                )
                # PacketLossDetectionSynced
                sts = self._loop_packloss_detec_enbl
                sts_ok = fdev.min_bpm_count_enbl == sts
                count = int(_np.sum(self._fofbctrl_syncenbllist))
                count_ok = fdev.min_bpm_count == count
                value = _updt_bit(
                    value, 8, not _np.all(sts_ok) or not _np.all(count_ok)
                )
                # LoopInterlockOk
                value = _updt_bit(value, 9, not fdev.interlock_ok)
                # SYSIDExcitationDisabled
                value = _updt_bit(
                    value, 10, not fdev.check_sysid_exc_disabled()
                )
            else:
                value = 0b11111111111

            self._fofbctrl_status = value
            self.run_callbacks("CtrlrStatus-Mon", self._fofbctrl_status)

            ttook = _time.time() - _t0
            tsleep = tplanned - ttook
            if tsleep > 0:
                _time.sleep(tsleep)
                continue
            self._logger.warning(
                "Controllers check took more than planned... %.3f/%.3f",
                ttook,
                tplanned,
                extra={"ioc_only": True},
            )
