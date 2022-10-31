"""High Level FOFB main application."""

import os as _os
import logging as _log
import time as _time
from functools import partial as _part
from threading import Thread as _Thread
import numpy as _np

from ..util import update_bit as _updt_bit
from ..epics import PV as _PV
from ..callbacks import Callback as _Callback
from ..envars import VACA_PREFIX as _vaca_prefix
from ..namesys import SiriusPVName as _PVName
from ..devices import FamFOFBControllers as _FamFOFBCtrls, \
    FamFastCorrs as _FamFastCorrs, SOFB as _SOFB, RFGen as _RFGen

from .csdev import HLFOFBConst as _Const, ETypes as _ETypes


class App(_Callback):
    """High Level FOFB main application."""

    SCAN_FREQUENCY = 1  # [Hz]

    def __init__(self, tests=False):
        """Class constructor."""
        super().__init__()
        self._const = _Const()
        self._pvs_database = self._const.get_hlfofb_database()
        self._tests = tests
        self._init = False

        # internal states
        self._loop_state = self._const.LoopState.Open
        self._loop_state_lastsp = self._const.LoopState.Open
        self._loop_gain_h = 0.1
        self._loop_gain_mon_h = 0
        self._loop_gain_v = 0.1
        self._loop_gain_mon_v = 0
        self._thread_loopstate = None
        self._abort_thread = False
        self._loop_max_orb_dist = self._const.DEF_MAX_ORB_DISTORTION
        self._loop_max_orb_dist_enbl = self._const.DsblEnbl.Dsbl
        self._corr_status = self._pvs_database['CorrStatus-Mon']['value']
        self._corr_confall_count = 0
        self._corr_setpwrstateon_count = 0
        self._corr_setopmodemanual_count = 0
        self._corr_setaccfreezeenbl_count = 0
        self._corr_setaccfreezedsbl_count = 0
        self._corr_setaccclear_count = 0
        self._corr_setcurrzero_count = 0
        self._ch_maxacccurr = self._pvs_database['CHAccSatMax-RB']['value']
        self._cv_maxacccurr = self._pvs_database['CVAccSatMax-RB']['value']
        self._time_frame_len = self._pvs_database['TimeFrameLen-RB']['value']
        self._fofbctrl_status = self._pvs_database['CtrlrStatus-Mon']['value']
        self._fofbctrl_confbpmid_count = 0
        self._fofbctrl_syncnet_count = 0
        self._fofbctrl_syncref_count = 0
        self._fofbctrl_synctframelen_count = 0
        self._fofbctrl_confbpmlogtrg_count = 0
        self._fofbctrl_syncmaxorbdist_count = 0
        self._fofbctrl_reset_count = 0
        self._fofbctrl_syncenbllist = _np.ones(self._const.nr_bpms, dtype=bool)
        self._fofbctrl_syncuseenbllist = 0
        self._reforb_x = _np.zeros(self._const.nr_bpms, dtype=float)
        self._reforbhw_x = _np.zeros(self._const.nr_bpms, dtype=float)
        self._reforb_y = _np.zeros(self._const.nr_bpms, dtype=float)
        self._reforbhw_y = _np.zeros(self._const.nr_bpms, dtype=float)
        self._respmat = _np.zeros(
            [2*self._const.nr_bpms, self._const.nr_corrs], dtype=float)
        self._invrespmat = self._respmat.copy().T
        self._invrespmatconv = self._invrespmat.copy()
        self._enable_lists = {
            'bpmx': _np.ones(self._const.nr_bpms, dtype=bool),
            'bpmy': _np.ones(self._const.nr_bpms, dtype=bool),
            'ch': _np.ones(self._const.nr_ch, dtype=bool),
            'cv': _np.ones(self._const.nr_cv, dtype=bool),
            'rf': _np.ones(1, dtype=bool),
        }
        self._min_sing_val = self._const.MIN_SING_VAL
        self._tikhonov_reg_const = self._const.TIKHONOV_REG_CONST
        self._invrespmat_normmode = self._const.GlobIndiv.Global
        self._pscoeffs = self._invrespmatconv[:-1].copy()
        self._psgains = _np.ones(self._const.nr_chcv, dtype=float)
        self._meas_respmat_count = 0
        self._meas_respmat_kick = {
            'ch': 15,  # [urad]
            'cv': 15,  # [urad]
            'rf': 80,  # [Hz]
        }
        self._meas_respmat_wait = 1  # [s]
        self._meas_respmat_thread = None
        self._measuring_respmat = False

        # devices and connections
        self._sisofb_dev = _SOFB(_SOFB.DEVICES.SI)
        ppties_automon_off = [
            'MTurnSum-Mon', 'MTurnOrbX-Mon', 'MTurnOrbY-Mon', 'MTurnTime-Mon',
            'MTurnIdxOrbX-Mon', 'MTurnIdxOrbY-Mon', 'MTurnIdxSum-Mon',
            'SlowOrbX-Mon', 'SlowOrbY-Mon',
            'KickCH-Mon', 'KickCV-Mon', 'KickRF-Mon',
            'DeltaKickCH-Mon', 'DeltaKickCV-Mon', 'DeltaKickRF-Mon',
        ]
        for ppty in ppties_automon_off:
            self._sisofb_dev.set_auto_monitor(ppty, False)

        corrnames = self._const.ch_names + self._const.cv_names
        self._corrs_dev = _FamFastCorrs(corrnames)

        self._kick_buffer = []
        self._kick_buffer_size = self._const.DEF_KICK_BUFFER_SIZE
        for idx, pso in enumerate(self._corrs_dev.psdevs):
            pvo = pso.pv_object('CurrentRef-Mon')
            pvo.auto_monitor = True
            self._kick_buffer.append([])
            pvo.add_callback(_part(self._update_kick_buffer, ps_index=idx))

        self._rf_dev = _RFGen()

        self._llfofb_dev = _FamFOFBCtrls()

        self._intlk_pvs = list()
        for dev in self._llfofb_dev.ctrlrefdevs.values():
            pvo = dev.pv_object('Intlk-Mon')
            pvo.auto_monitor = True
            pvo.add_callback(self._callback_orbintlk)
            self._intlk_pvs.append(pvo)

        self._corrs_dev.wait_for_connection(self._const.DEF_TIMEWAIT)

        havebeam_pvname = _PVName(
            'SI-Glob:AP-CurrInfo:StoredEBeam-Mon').substitute(
                prefix=_vaca_prefix)
        self._havebeam_pv = _PV(
            havebeam_pvname, connection_timeout=0.05,
            callback=self._callback_havebeam)

        # pvs to write methods
        self.map_pv2write = {
            'LoopState-Sel': self.set_loop_state,
            'LoopGainH-SP': _part(self.set_loop_gain, 'h'),
            'LoopGainV-SP': _part(self.set_loop_gain, 'v'),
            'LoopMaxOrbDistortion-SP': self.set_loop_max_orbit_dist,
            'LoopMaxOrbDistortionEnbl-Sel': self.set_loop_max_orbit_dist_enbl,
            'CorrConfig-Cmd': self.cmd_corr_configure,
            'CorrSetPwrStateOn-Cmd': self.cmd_corr_pwrstate_on,
            'CorrSetOpModeManual-Cmd': self.cmd_corr_opmode_manual,
            'CorrSetAccFreezeDsbl-Cmd': self.cmd_corr_accfreeze_dsbl,
            'CorrSetAccFreezeEnbl-Cmd': self.cmd_corr_accfreeze_enbl,
            'CorrSetAccClear-Cmd': self.cmd_corr_accclear,
            'CorrSetCurrZero-Cmd': self.cmd_corr_currzero,
            'CHAccSatMax-SP': _part(self.set_corr_accsatmax, 'ch'),
            'CVAccSatMax-SP': _part(self.set_corr_accsatmax, 'cv'),
            'TimeFrameLen-SP': self.set_timeframelen,
            'CtrlrConfBPMId-Cmd': self.cmd_fofbctrl_confbpmid,
            'CtrlrSyncNet-Cmd': self.cmd_fofbctrl_syncnet,
            'CtrlrSyncRefOrb-Cmd': self.cmd_fofbctrl_syncreforb,
            'CtrlrSyncTFrameLen-Cmd': self.cmd_fofbctrl_synctframelen,
            'CtrlrConfBPMLogTrg-Cmd': self.cmd_fofbctrl_confbpmlogtrg,
            'CtrlrSyncUseEnblList-Sel': self.set_fofbctrl_syncuseenablelist,
            'CtrlrSyncMaxOrbDist-Cmd': self.cmd_fofbctrl_syncmaxorbdist,
            'CtrlrReset-Cmd': self.cmd_fofbctrl_reset,
            'KickBufferSize-SP': self.set_kicker_buffer_size,
            'RefOrbX-SP': _part(self.set_reforbit, 'x'),
            'RefOrbY-SP': _part(self.set_reforbit, 'y'),
            'RespMat-SP': self.set_respmat,
            'BPMXEnblList-SP': _part(self.set_enbllist, 'bpmx'),
            'BPMYEnblList-SP': _part(self.set_enbllist, 'bpmy'),
            'CHEnblList-SP': _part(self.set_enbllist, 'ch'),
            'CVEnblList-SP': _part(self.set_enbllist, 'cv'),
            'UseRF-Sel': _part(self.set_enbllist, 'rf'),
            'MinSingValue-SP': self.set_min_sing_value,
            'TikhonovRegConst-SP': self.set_tikhonov_reg_const,
            'InvRespMatNormMode-Sel': self.set_invrespmat_normmode,
            'MeasRespMat-Cmd': self.set_respmat_meas_state,
            'MeasRespMatKickCH-SP': _part(self.set_respmat_meas_kick, 'ch'),
            'MeasRespMatKickCV-SP': _part(self.set_respmat_meas_kick, 'cv'),
            'MeasRespMatKickRF-SP': _part(self.set_respmat_meas_kick, 'rf'),
            'MeasRespMatWait-SP': self.set_respmat_meas_wait_time,
        }

        # configuration scanning
        self.quit = False
        self.scanning = False
        self.thread_check_configs = _Thread(
            target=self._check_configs, daemon=True)
        self.thread_check_configs.start()

    def init_database(self):
        """Set initial PV values."""
        self.run_callbacks('LoopState-Sel', self._loop_state)
        self.run_callbacks('LoopState-Sts', self._loop_state)
        self.run_callbacks('LoopGainH-SP', self._loop_gain_h)
        self.run_callbacks('LoopGainH-RB', self._loop_gain_h)
        self.run_callbacks('LoopGainH-Mon', self._loop_gain_mon_h)
        self.run_callbacks('LoopGainV-SP', self._loop_gain_v)
        self.run_callbacks('LoopGainV-RB', self._loop_gain_v)
        self.run_callbacks('LoopGainV-Mon', self._loop_gain_mon_v)
        self.run_callbacks('LoopMaxOrbDistortion-SP', self._loop_max_orb_dist)
        self.run_callbacks('LoopMaxOrbDistortion-RB', self._loop_max_orb_dist)
        self.run_callbacks(
            'LoopMaxOrbDistortionEnbl-Sel', self._loop_max_orb_dist_enbl)
        self.run_callbacks(
            'LoopMaxOrbDistortionEnbl-Sts', self._loop_max_orb_dist_enbl)
        self.run_callbacks('CorrStatus-Mon', self._corr_status)
        self.run_callbacks('CorrConfig-Cmd', self._corr_confall_count)
        self.run_callbacks(
            'CorrSetPwrStateOn-Cmd', self._corr_setpwrstateon_count)
        self.run_callbacks(
            'CorrSetOpModeManual-Cmd', self._corr_setopmodemanual_count)
        self.run_callbacks(
            'CorrSetAccFreezeDsbl-Cmd', self._corr_setaccfreezedsbl_count)
        self.run_callbacks(
            'CorrSetAccFreezeEnbl-Cmd', self._corr_setaccfreezeenbl_count)
        self.run_callbacks(
            'CorrSetAccClear-Cmd', self._corr_setaccclear_count)
        self.run_callbacks(
            'CorrSetCurrZero-Cmd', self._corr_setcurrzero_count)
        self.run_callbacks('CHAccSatMax-SP', self._ch_maxacccurr)
        self.run_callbacks('CHAccSatMax-RB', self._ch_maxacccurr)
        self.run_callbacks('CVAccSatMax-SP', self._cv_maxacccurr)
        self.run_callbacks('CVAccSatMax-RB', self._cv_maxacccurr)
        self.run_callbacks('TimeFrameLen-SP', self._time_frame_len)
        self.run_callbacks('TimeFrameLen-RB', self._time_frame_len)
        self.run_callbacks('CtrlrStatus-Mon', self._fofbctrl_status)
        self.run_callbacks(
            'CtrlrConfBPMId-Cmd', self._fofbctrl_confbpmid_count)
        self.run_callbacks(
            'CtrlrSyncNet-Cmd', self._fofbctrl_syncnet_count)
        self.run_callbacks(
            'CtrlrSyncUseEnblList-Sel', self._fofbctrl_syncuseenbllist)
        self.run_callbacks(
            'CtrlrSyncUseEnblList-Sts', self._fofbctrl_syncuseenbllist)
        self.run_callbacks(
            'CtrlrSyncEnblList-Mon', self._fofbctrl_syncenbllist)
        self.run_callbacks(
            'CtrlrSyncRefOrb-Cmd', self._fofbctrl_syncref_count)
        self.run_callbacks(
            'CtrlrSyncTFrameLen-Cmd', self._fofbctrl_synctframelen_count)
        self.run_callbacks(
            'CtrlrConfBPMLogTrg-Cmd', self._fofbctrl_confbpmlogtrg_count)
        self.run_callbacks(
            'CtrlrSyncMaxOrbDist-Cmd', self._fofbctrl_syncmaxorbdist_count)
        self.run_callbacks('CtrlrReset-Cmd', self._fofbctrl_reset_count)
        self.run_callbacks('KickBufferSize-SP', self._kick_buffer_size)
        self.run_callbacks('KickBufferSize-RB', self._kick_buffer_size)
        self.run_callbacks('KickBufferSize-Mon', self._kick_buffer_size)
        self.run_callbacks(
            'KickCH-Mon', _np.zeros(self._const.nr_ch, dtype=float))
        self.run_callbacks(
            'KickCV-Mon', _np.zeros(self._const.nr_cv, dtype=float))
        self.run_callbacks('RefOrbX-SP', self._reforb_x)
        self.run_callbacks('RefOrbX-RB', self._reforb_x)
        self.run_callbacks('RefOrbY-SP', self._reforb_y)
        self.run_callbacks('RefOrbY-RB', self._reforb_y)
        self.run_callbacks('RefOrbHwX-Mon', self._reforbhw_x)
        self.run_callbacks('RefOrbHwY-Mon', self._reforbhw_y)
        self.run_callbacks('BPMXEnblList-SP', self._enable_lists['bpmx'])
        self.run_callbacks('BPMXEnblList-RB', self._enable_lists['bpmx'])
        self.run_callbacks('BPMYEnblList-SP', self._enable_lists['bpmy'])
        self.run_callbacks('BPMYEnblList-RB', self._enable_lists['bpmy'])
        self.run_callbacks('CHEnblList-SP', self._enable_lists['ch'])
        self.run_callbacks('CHEnblList-RB', self._enable_lists['ch'])
        self.run_callbacks('CVEnblList-SP', self._enable_lists['cv'])
        self.run_callbacks('CVEnblList-RB', self._enable_lists['cv'])
        self.run_callbacks(
            'UseRF-Sel', bool(self._enable_lists['rf']))
        self.run_callbacks(
            'UseRF-Sts', bool(self._enable_lists['rf']))
        self.run_callbacks('MinSingValue-SP', self._min_sing_val)
        self.run_callbacks('MinSingValue-RB', self._min_sing_val)
        self.run_callbacks('TikhonovRegConst-SP', self._tikhonov_reg_const)
        self.run_callbacks('TikhonovRegConst-RB', self._tikhonov_reg_const)
        self.run_callbacks('InvRespMatNormMode-Sel', self._invrespmat_normmode)
        self.run_callbacks('InvRespMatNormMode-Sts', self._invrespmat_normmode)
        self._load_respmat()
        self.run_callbacks('RespMat-SP', list(self._respmat.ravel()))
        self.run_callbacks('MeasRespMat-Cmd', self._meas_respmat_count)
        self.run_callbacks('MeasRespMat-Mon', self._const.MeasRespMatMon.Idle)
        self.run_callbacks(
            'MeasRespMatKickCH-SP', self._meas_respmat_kick['ch'])
        self.run_callbacks(
            'MeasRespMatKickCH-RB', self._meas_respmat_kick['ch'])
        self.run_callbacks(
            'MeasRespMatKickCV-SP', self._meas_respmat_kick['cv'])
        self.run_callbacks(
            'MeasRespMatKickCV-RB', self._meas_respmat_kick['cv'])
        self.run_callbacks(
            'MeasRespMatKickRF-SP', self._meas_respmat_kick['rf'])
        self.run_callbacks(
            'MeasRespMatKickRF-RB', self._meas_respmat_kick['rf'])
        self.run_callbacks('MeasRespMatWait-SP', self._meas_respmat_wait)
        self.run_callbacks('MeasRespMatWait-RB', self._meas_respmat_wait)
        self._update_log('Started.')
        self._init = True

    @property
    def pvs_database(self):
        """Return pvs_database."""
        return self._pvs_database

    def process(self, interval):
        """Sleep."""
        t0_ = _time.time()
        self._update_kicks()

        dtime = interval - (_time.time()-t0_)
        if dtime > 0:
            _time.sleep(dtime)

    def read(self, reason):
        """Read from IOC database."""
        value = None
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        _log.info('Write received for: %s --> %s', reason, str(value))
        if reason in self.map_pv2write.keys():
            status = self.map_pv2write[reason](value)
            _log.info('%s Write for: %s --> %s',
                      str(status).upper(), reason, str(value))
            return status
        _log.warning('PV %s does not have a set function.', reason)
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

    # --- loop control ---

    def set_loop_state(self, value, reset=False):
        """Set loop state."""
        if not 0 <= value < len(_ETypes.OPEN_CLOSED):
            return False

        self._loop_state_lastsp = value
        if value:
            if not self.havebeam:
                self._update_log('ERR: Do not have stored beam. Aborted.')
                return False
            if _np.any([pvo.value for pvo in self._intlk_pvs]):
                self._update_log('ERR: Reset interlocks before closing')
                self._update_log('ERR: the loop.')
                return False

        if self._thread_loopstate is not None and \
                self._thread_loopstate.is_alive():
            self._update_log('WARN:Interrupting Loop Enable thread...')
            self._abort_thread = True
            self._thread_loopstate.join()

        self._thread_loopstate = _Thread(
            target=self._thread_set_loop_state,
            args=[value, reset], daemon=True)
        self._thread_loopstate.start()
        return True

    def _thread_set_loop_state(self, value, reset):
        if value:  # closing the loop
            # set gains to zero, recalculate gains and coeffs
            self._update_log('Setting Loop Gain to zero...')
            self._loop_gain_mon_h, self._loop_gain_mon_v = 0, 0
            self._calc_corrs_coeffs(log=False)
            # set and wait corrector gains and coeffs to zero
            if not self._set_corrs_coeffs(log=False):
                return
            self._update_log('Waiting for coefficients and gains...')
            if not self._wait_coeffs_and_gains():
                self.run_callbacks('LoopState-Sel', self._loop_state)
                return

            if self._check_abort_thread():
                return

            # close the loop
            self._update_log('...done. Closing the loop...')
            self._loop_state = value
            if not self._check_set_corrs_opmode():
                self._loop_state = self._const.LoopState.Open
                self.run_callbacks('LoopState-Sel', self._loop_state)
                return
            self.run_callbacks('LoopState-Sts', self._loop_state)

            if self._check_abort_thread():
                return

            # do ramp up
            self._update_log('...done. Starting Loop Gain ramp up...')
            if self._do_loop_gain_ramp(ramp='up'):
                self._update_log('LoopGain ramp up finished!')

        else:  # opening the loop
            # do ramp down
            self._update_log('Starting Loop Gain ramp down...')
            if self._do_loop_gain_ramp(ramp='down'):
                self._update_log('Loop Gain ramp down finished!')

            if self._check_abort_thread():
                return

            # open the loop
            self._loop_state = value
            self._check_set_corrs_opmode()
            self.run_callbacks('LoopState-Sts', self._loop_state)

        if reset:
            self._update_log('Reseting FOFB controllers...')
            if self._llfofb_dev.cmd_reset():
                self._update_log('...done!')
            else:
                self._update_log('ERR:Failed to reset controllers.')

    def _do_loop_gain_ramp(self, ramp='up'):
        xdata = _np.linspace(0, 1, self._const.LOOPGAIN_RMP_NPTS)
        power = 1
        if ramp == 'up':
            ydata = xdata**power
            ydata_h = ydata * self._loop_gain_h
            ydata_v = ydata * self._loop_gain_v
        else:
            ydata = (1-xdata)**power
            ydata_h = ydata * self._loop_gain_mon_h
            ydata_v = ydata * self._loop_gain_mon_v
        for i in range(self._const.LOOPGAIN_RMP_NPTS):
            if not self.havebeam:
                self._update_log('ERR: Do not have stored beam. Aborted.')
                self._loop_gain_mon_h, self._loop_gain_mon_v = 0, 0
                self.run_callbacks('LoopGainH-Mon', self._loop_gain_mon_h)
                self.run_callbacks('LoopGainV-Mon', self._loop_gain_mon_v)
                self._calc_corrs_coeffs()
                self._set_corrs_coeffs()
                self._wait_coeffs_and_gains()
                return False
            if self._check_abort_thread():
                return False

            self._loop_gain_mon_h = ydata_h[i]
            self._loop_gain_mon_v = ydata_v[i]
            self.run_callbacks('LoopGainH-Mon', self._loop_gain_mon_h)
            self.run_callbacks('LoopGainV-Mon', self._loop_gain_mon_v)
            self._update_log(
                f'{i+1:02d}/{len(ydata):02d} -> Loop Gain: '
                f'H={ydata_h[i]:.3f}, V={ydata_v[i]:.3f}')
            self._calc_corrs_coeffs(log=False)
            self._set_corrs_coeffs(log=False)
            _t0 = _time.time()
            if not self._wait_coeffs_and_gains():
                return False
            _td = 1/self._const.LOOPGAIN_RMP_FREQ - (_time.time() - _t0)
            if _td > 0:
                _time.sleep(_td)
        return True

    def _wait_coeffs_and_gains(self):
        _t0 = _time.time()
        while _time.time() - _t0 < self._const.DEF_TIMEOUT:
            _time.sleep(self._const.DEF_TIMESLEEP)
            if self._corrs_dev.check_invrespmat_row(self._pscoeffs) and \
                    self._corrs_dev.check_fofbacc_gain(self._psgains):
                return True
        self._update_log('ERR:Timed out waiting for correctors to')
        self._update_log('ERR:implement gains and coefficients.')
        return False

    def _check_abort_thread(self):
        if self._abort_thread:
            self._update_log('WARN: Loop state thread aborted.')
            self._abort_thread = False
            return True
        return False

    def set_loop_gain(self, plane, value):
        """Set loop gain."""
        if not -2**3 <= value <= 2**3-1:
            return False

        if self._thread_loopstate is not None and \
                self._thread_loopstate.is_alive():
            self._update_log('ERR:Wait for Loop Gain ramp before ')
            self._update_log('ERR:setting new value.')
            return False

        setattr(self, '_loop_gain_' + plane, value)

        # if loop closed, calculate new gains and coefficients
        if self._loop_state:
            setattr(self, '_loop_gain_mon_' + plane, value)
            self.run_callbacks(f'LoopGain{plane.upper()}-Mon', value)
            self._calc_corrs_coeffs()
            self._set_corrs_coeffs()

        self._update_log(f'Changed Loop Gain {plane.upper()} to {value}.')
        self.run_callbacks(f'LoopGain{plane.upper()}-RB', value)
        return True

    def set_loop_max_orbit_dist(self, value):
        """Set maximum orbit distortion threshold."""
        if not 0 <= value <= 10000:
            return False
        if not self._check_fofbctrl_connection():
            return False

        self._loop_max_orb_dist = value
        self._update_log('Setting orbit distortion threshold...')
        if self._llfofb_dev.set_max_orb_distortion(
                value=value * self._const.CONV_UM_2_NM,
                timeout=self._const.DEF_TIMEWAIT):
            self._update_log('...done!')
        else:
            self._update_log('ERR:Failed to set threshold.')

        self.run_callbacks('LoopMaxOrbDistortion-RB', value)
        return True

    def set_loop_max_orbit_dist_enbl(self, value):
        """Set orbit distortion threshold verification enable status."""
        if not self._check_fofbctrl_connection():
            return False

        act = ('En' if value else 'Dis')
        self._loop_max_orb_dist_enbl = value
        self._update_log(act+'abling orbit distortion detection...')
        if self._llfofb_dev.set_max_orb_distortion_enbl(
                value=value, timeout=self._const.DEF_TIMEWAIT):
            self._update_log('...done!')
        else:
            self._update_log('ERR:Failed to '+act+'able detection.')

        self.run_callbacks('LoopMaxOrbDistortionEnbl-Sts', value)
        return True

    # --- devices configuration ---

    def cmd_corr_configure(self, _):
        """Configure corrector command."""
        self._update_log('Received configure corrector command...')
        if not self._check_corr_connection():
            return False

        # opmode
        self._check_set_corrs_opmode()
        # fofbacc_freeze
        self._set_corrs_fofbacc_freeze()
        # matrix coefficients
        self._set_corrs_coeffs()

        self._update_log('Correctors configuration done!')

        self._corr_confall_count += 1
        self.run_callbacks('CorrConfig-Cmd', self._corr_confall_count)
        return False

    def cmd_corr_pwrstate_on(self, _):
        """Set all corrector pwrstate to on."""
        self._update_log('Received set corrector pwrstate to on...')
        if not self._check_corr_connection():
            return False

        self._update_log('Setting all corrector pwrstate to on...')
        self._corrs_dev.set_pwrstate(self._const.OffOn.On)
        self._update_log('...done!')

        self._corr_setpwrstateon_count += 1
        self.run_callbacks(
            'CorrSetPwrStateOn-Cmd', self._corr_setpwrstateon_count)
        return False

    def cmd_corr_opmode_manual(self, _):
        """Set all corrector opmode to manual."""
        self._update_log('Received set corrector opmode to manual...')
        if not self._check_corr_connection():
            return False

        self._update_log('Setting all corrector opmode to manual...')
        self._corrs_dev.set_opmode(self._corrs_dev.OPMODE_STS.manual)
        self._update_log('...done!')

        self._corr_setopmodemanual_count += 1
        self.run_callbacks(
            'CorrSetOpModeManual-Cmd', self._corr_setopmodemanual_count)
        return False

    def cmd_corr_accfreeze_dsbl(self, _):
        """Set all corrector accumulator freeze state to Dsbl."""
        self._update_log('Received set corrector AccFreeze to Dsbl...')
        if not self._check_corr_connection():
            return False

        self._update_log('Setting AccFreeze to Dsbl...')
        self._corrs_dev.set_fofbacc_freeze(self._const.DsblEnbl.Dsbl)
        self._update_log('...done!')

        self._corr_setaccfreezedsbl_count += 1
        self.run_callbacks(
            'CorrSetAccFreezeDsbl-Cmd', self._corr_setaccfreezedsbl_count)
        return False

    def cmd_corr_accfreeze_enbl(self, _):
        """Set all corrector accumulator freeze state to Enbl."""
        self._update_log('Received set corrector AccFreeze to Enbl...')
        if not self._check_corr_connection():
            return False

        self._update_log('Setting AccFreeze to Enbl...')
        self._corrs_dev.set_fofbacc_freeze(self._const.DsblEnbl.Enbl)
        self._update_log('...done!')

        self._corr_setaccfreezeenbl_count += 1
        self.run_callbacks(
            'CorrSetAccFreezeEnbl-Cmd', self._corr_setaccfreezeenbl_count)
        return False

    def cmd_corr_accclear(self, _):
        """Clear all corrector accumulator."""
        self._update_log('Received clear all corrector accumulator...')
        if not self._check_corr_connection():
            return False

        self._update_log('Sending clear accumulator command...')
        self._corrs_dev.cmd_fofbacc_clear()
        self._update_log('...done!')

        self._corr_setaccclear_count += 1
        self.run_callbacks(
            'CorrSetAccClear-Cmd', self._corr_setaccclear_count)
        return False

    def cmd_corr_currzero(self, _):
        """Set all corrector current to zero."""
        self._update_log('Received set corrector current to zero...')
        if not self._check_corr_connection():
            return False

        self._update_log('Sending all corrector current to zero...')
        self._corrs_dev.set_current(0)
        self._update_log('...done!')

        self._corr_setcurrzero_count += 1
        self.run_callbacks(
            'CorrSetCurrZero-Cmd', self._corr_setcurrzero_count)
        return False

    def set_corr_accsatmax(self, device, value):
        """Set device FOFB accumulator saturation limits."""
        if not self._check_corr_connection():
            return False
        if not 0 <= value <= 0.95:
            return False

        setattr(self, '_'+device+'_maxacccurr', value)
        self._update_log('Setting '+device.upper()+' saturation limits...')
        psnames = getattr(self._const, device+'_names')
        self._corrs_dev.set_fofbacc_satmax(value, psnames=psnames)
        self._corrs_dev.set_fofbacc_satmin(-value, psnames=psnames)
        self._update_log('...done!')

        self._update_log(
            'Changed '+device.upper()+' saturation limits to '+str(value)+'A.')
        self.run_callbacks(device.upper()+'AccSatMax-RB', value)
        return True

    def set_timeframelen(self, value):
        """Set FOFB controllers TimeFrameLen."""
        if not 500 <= value <= 10000:
            return False
        if not self._check_fofbctrl_connection():
            return False

        self._time_frame_len = value
        self._update_log(f'Setting TimeFrameLen to {value}...')
        self._llfofb_dev.set_time_frame_len(
            value=self._time_frame_len, timeout=self._const.DEF_TIMEWAIT)
        self._update_log('...done!')

        self.run_callbacks('TimeFrameLen-RB', self._time_frame_len)
        return True

    def cmd_fofbctrl_confbpmid(self, _):
        """Configure FOFB DCC BPMId command."""
        self._update_log('Received configure FOFB DCC BPMId command...')
        if not self._check_fofbctrl_connection():
            return False
        self._update_log('Checking...')
        if not self._llfofb_dev.bpm_id_configured:
            self._update_log('Configuring DCC BPMIds...')
            if self._llfofb_dev.cmd_config_bpm_id():
                self._update_log('Sent configuration to DCCs.')
            else:
                self._update_log('ERR:Failed to configure DCCs.')
        else:
            self._update_log('FOFB DCC BPMIds already configured.')

        self._fofbctrl_confbpmid_count += 1
        self.run_callbacks(
            'CtrlrConfBPMId-Cmd', self._fofbctrl_confbpmid_count)
        return False

    def cmd_fofbctrl_syncnet(self, _):
        """Sync FOFB net command."""
        self._update_log('Received sync FOFB net command...')
        if not self._check_fofbctrl_connection():
            return False
        self._update_log('Checking...')
        self._do_fofbctrl_syncnet()

        self._fofbctrl_syncnet_count += 1
        self.run_callbacks(
            'CtrlrSyncNet-Cmd', self._fofbctrl_syncnet_count)
        return False

    def cmd_fofbctrl_syncreforb(self, _):
        """Sync FOFB RefOrb command."""
        self._update_log('Received sync FOFB RefOrb command...')
        if not self._check_fofbctrl_connection():
            return False
        self._update_log('Checking...')
        reforb = _np.hstack([self._reforbhw_x, self._reforbhw_y])
        if not self._llfofb_dev.check_reforb(reforb):
            self._update_log('Syncing FOFB RefOrb...')
            self._llfofb_dev.set_reforb(reforb)
            self._update_log('...done!')
        else:
            self._update_log('FOFB RefOrb already synced.')

        self._fofbctrl_syncref_count += 1
        self.run_callbacks(
            'CtrlrSyncRefOrb-Cmd', self._fofbctrl_syncref_count)
        return False

    def cmd_fofbctrl_synctframelen(self, _):
        """Sync FOFB controllers TimeFrameLen command."""
        self._update_log('Received configure FOFB controllers')
        self._update_log('TimeFrameLen command... Checking...')
        if not self._check_fofbctrl_connection():
            return False
        timeframe = self._time_frame_len
        if not _np.all(self._llfofb_dev.time_frame_len == timeframe):
            self._update_log('Configuring TimeFrameLen PVs...')
            if self._llfofb_dev.set_time_frame_len(timeframe):
                self._update_log('...done!')
            else:
                self._update_log('ERR:Failed to configure TimeFrameLen.')
        else:
            self._update_log('TimeFrameLen PVs already configured.')

        self._fofbctrl_synctframelen_count += 1
        self.run_callbacks(
            'CtrlrSyncTFrameLen-Cmd', self._fofbctrl_synctframelen_count)
        return False

    def cmd_fofbctrl_confbpmlogtrg(self, _):
        """Configure BPM logical triggers command."""
        self._update_log('Received configure BPM Logical')
        if not self._check_fofbctrl_connection():
            return False
        self._update_log('triggers command... Checking...')
        if not self._llfofb_dev.bpm_trigs_configured:
            self._update_log('Configuring BPM logical triggers...')
            if self._llfofb_dev.cmd_config_bpm_trigs():
                self._update_log('...done!')
            else:
                self._update_log('ERR:Failed to configure BPM log.trigs.')
        else:
            self._update_log('BPM logical triggers already configured.')

        self._fofbctrl_confbpmlogtrg_count += 1
        self.run_callbacks(
            'CtrlrConfBPMLogTrg-Cmd', self._fofbctrl_confbpmlogtrg_count)
        return False

    def set_fofbctrl_syncuseenablelist(self, value):
        """Set whether to use or not BPMEnblList in sync."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False

        self._fofbctrl_syncuseenbllist = value
        self._update_fofbctrl_sync_enbllist()

        self._update_log('Changed sync net command to ')
        self._update_log(('' if value else 'not ')+'use BPM EnableList.')
        self.run_callbacks('CtrlrSyncUseEnblList-Sts', value)
        return True

    def cmd_fofbctrl_syncmaxorbdist(self, _):
        """Sync FOFB controllers orbit distortion detection command."""
        self._update_log('Received sync FOFB controllers orbit')
        self._update_log('distortion detection command...Checking...')
        if not self._check_fofbctrl_connection():
            return False

        tout = self._const.DEF_TIMEWAIT

        # threshold
        thres = self._loop_max_orb_dist * self._const.CONV_UM_2_NM
        if not _np.all(self._llfofb_dev.max_orb_distortion == thres):
            self._update_log('Setting MaxOrbDistortion PVs...')
            if self._llfofb_dev.set_max_orb_distortion(thres, timeout=tout):
                self._update_log('...done!')
            else:
                self._update_log('ERR:Failed to sync threshold.')
        else:
            self._update_log('MaxOrbDistortion PVs already configured.')

        # enable status
        sts = self._loop_max_orb_dist_enbl
        if not _np.all(self._llfofb_dev.max_orb_distortion_enbl == sts):
            self._update_log('Setting MaxOrbDistortionEnbl PVs...')
            if self._llfofb_dev.set_max_orb_distortion_enbl(sts, timeout=tout):
                self._update_log('...done!')
            else:
                self._update_log('ERR:Failed to sync enable status.')
        else:
            self._update_log('MaxOrbDistortionEnbl PVs already configured.')

        self._fofbctrl_syncmaxorbdist_count += 1
        self.run_callbacks(
            'CtrlrSyncMaxOrbDist-Cmd', self._fofbctrl_syncmaxorbdist_count)
        return False

    def cmd_fofbctrl_reset(self, _):
        """Reset FOFB controllers interlock command."""
        self._update_log('Received reset FOFB controllers command...')
        if not self._check_fofbctrl_connection():
            return False

        self._update_log('Reseting FOFB controllers...')
        if self._llfofb_dev.cmd_reset(timeout=self._const.DEF_TIMEWAIT):
            self._update_log('...done!')
        else:
            self._update_log('ERR:Failed to reset controllers.')

        self._fofbctrl_reset_count += 1
        self.run_callbacks('CtrlrReset-Cmd', self._fofbctrl_reset_count)
        return False

    # --- kicks buffer and kicks update ---

    def set_kicker_buffer_size(self, value: int):
        """Set size of the kick buffer.

        Args:
            value (int): New value for the buffer size.

        Returns:
            bool: Whether property was properly set.

        """
        self._kick_buffer_size = max(1, int(value))
        self.run_callbacks('KickBufferSize-RB', self._kick_buffer_size)
        return True

    def _update_kick_buffer(self, pvname, value, ps_index, **kwargs):
        _ = kwargs, pvname
        if value is None:
            return
        val = self._corrs_dev.psconvs[ps_index].conv_current_2_strength(value)
        if val is None:
            return
        self._kick_buffer[ps_index].append(val)
        del self._kick_buffer[ps_index][:-self._kick_buffer_size]

    def _update_kicks(self):
        kickch, kickcv = [], []
        lenb = self._kick_buffer_size if self._loop_state else 1

        rlenb = 0
        for i in range(self._const.nr_ch):
            buff = self._kick_buffer[i][-lenb:]
            rlenb = max(rlenb, len(buff))
            val = _np.mean(buff) if buff else 0.0
            kickch.append(val)

        for i in range(self._const.nr_ch, self._const.nr_chcv):
            buff = self._kick_buffer[i][-lenb:]
            rlenb = max(rlenb, len(buff))
            val = _np.mean(buff) if buff else 0.0
            kickcv.append(val)

        self.run_callbacks('KickCH-Mon', kickch)
        self.run_callbacks('KickCV-Mon', kickcv)
        self.run_callbacks('KickBufferSize-Mon', rlenb)

    # --- reference orbit ---

    def set_reforbit(self, plane, value):
        """Set reference orbit."""
        self._update_log(f'Setting New RefOrb{plane.upper()}...')

        # check size
        ref = _np.array(value, dtype=float)
        if ref.size != self._const.reforb_size:
            self._update_log('ERR: Wrong RefOrb Size.')
            return False

        # set internal states and LLFOFB reforb
        # physical units
        setattr(self, '_reforb_' + plane.lower(), ref)
        # hardware units
        refhw = ref * self._const.CONV_UM_2_NM
        refhw = _np.round(refhw)  # round, low level expect it to be int
        refhw = _np.roll(refhw, 1)  # make BPM 01M1 the first element
        setattr(self, '_reforbhw_' + plane.lower(), refhw)

        # update readback PV
        self.run_callbacks(f'RefOrb{plane.upper()}-RB', list(ref.ravel()))
        self.run_callbacks(f'RefOrbHw{plane.upper()}-Mon', refhw)
        self._update_log('...done!')
        return True

    # --- matrix manipulation ---

    def set_respmat(self, value):
        """Set response matrix."""
        self._update_log('Setting New RespMat...')

        # check size
        mat = _np.array(value, dtype=float)
        matb = mat
        if mat.size != self._const.matrix_size:
            self._update_log(
                f'ERR: Wrong RespMat Size ({mat.size}, '
                f'expected {self._const.matrix_size}).')
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
        self._save_respmat(matb)

        # update readback pv
        self.run_callbacks('RespMat-RB', list(self._respmat.ravel()))

        return True

    def _load_respmat(self):
        filename = self._const.respmat_fname
        if _os.path.isfile(filename):
            self._update_log('Loading RespMat from file...')
            if self.set_respmat(_np.loadtxt(filename)):
                msg = 'Loaded RespMat!'
            else:
                msg = 'ERR: Problem loading RespMat from file.'
            self._update_log(msg)

    def _save_respmat(self, mat):
        path = _os.path.split(self._const.respmat_fname)[0]
        _os.makedirs(path, exist_ok=True)
        _np.savetxt(self._const.respmat_fname, mat)

    def set_enbllist(self, device, value):
        """Set enable list for device."""
        self._update_log('Setting {0:s} EnblList'.format(device.upper()))

        # check size
        bkup = self._enable_lists[device]
        new = _np.array(value, dtype=bool)
        if bkup.size != new.size:
            self._update_log(
                'ERR: Wrong {0:s} EnblList size.'.format(device.upper()))
            return False

        # check if matrix is invertible
        self._enable_lists[device] = new
        if not self._calc_matrices():
            self._enable_lists[device] = bkup
            return False

        # update corrector AccFreeze state
        if device in ['ch', 'cv']:
            if self._check_corr_connection():
                self._check_set_corrs_opmode()
        elif device in ['bpmx', 'bpmy']:
            self._update_fofbctrl_sync_enbllist()
            if self._check_fofbctrl_connection():
                self._do_fofbctrl_syncnet()

        # update readback pv
        if device == 'rf':
            self.run_callbacks('UseRF-Sts', bool(value))
        else:
            self.run_callbacks(device.upper()+'EnblList-RB', new)

        return True

    @property
    def bpm_enbllist(self):
        """BPM enable list."""
        enbl = self._enable_lists
        return _np.hstack([enbl['bpmx'], enbl['bpmy']])

    @property
    def corr_enbllist(self):
        """Corrector enable list."""
        enbl = self._enable_lists
        return _np.hstack([enbl['ch'], enbl['cv'], enbl['rf']])

    def set_min_sing_value(self, value):
        """Set minimum singular values."""
        bkup = self._min_sing_val
        self._min_sing_val = float(value)
        if not self._calc_matrices():
            self._min_sing_val = bkup
            return False
        self.run_callbacks('MinSingValue-RB', self._min_sing_val)
        return True

    def set_tikhonov_reg_const(self, value):
        """Set Tikhonov regularization constant."""
        bkup = self._tikhonov_reg_const
        self._tikhonov_reg_const = float(value)
        if not self._calc_matrices():
            self._tikhonov_reg_const = bkup
            return False
        self.run_callbacks('TikhonovRegConst-RB', self._tikhonov_reg_const)
        return True

    def set_invrespmat_normmode(self, value):
        """Set corrector coefficients normalization mode."""
        if not 0 <= value < len(_ETypes.GLOB_INDIV):
            return False

        self._update_log(
            'Changed normalization mode to ' + str(
                self._const.GlobIndiv._fields[value])+'.')
        self._invrespmat_normmode = value

        self._calc_corrs_coeffs()
        self._set_corrs_coeffs()

        self.run_callbacks(
            'InvRespMatNormMode-Sts', self._invrespmat_normmode)
        return True

    def _calc_matrices(self):
        self._update_log('Calculating Inverse Matrix...')

        if not self._check_corr_connection():
            return False

        selbpm = self.bpm_enbllist
        if not any(selbpm):
            self._update_log('ERR: No BPM selected in EnblList')
            return False
        selcorr = self.corr_enbllist
        if not any(selcorr):
            self._update_log('ERR: No Corrector selected in EnblList')
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
            self._update_log('ERR: Could not calculate SVD')
            return False

        # handle singular values
        # select singular values greater than minimum
        idcs = _so > self._min_sing_val
        _sr = _so[idcs]
        nrs = _np.sum(idcs)
        if not nrs:
            self._update_log('ERR: All Singular Values below minimum.')
            return False
        # apply Tikhonov regularization
        regc = self._tikhonov_reg_const
        regc *= regc
        inv_s = _np.zeros(_so.size, dtype=float)
        inv_s[idcs] = _sr/(_sr*_sr + regc)
        # calculate processed singular values
        _sp = _np.zeros(_so.size, dtype=float)
        _sp[idcs] = 1/inv_s[idcs]

        # check if inverse matrix is valid
        invmat = _np.dot(_vo.T*inv_s, _uo.T)
        if _np.any(_np.isnan(invmat)) or _np.any(_np.isinf(invmat)):
            self._update_log('ERR: Inverse contains nan or inf.')
            return False

        # reconstruct filtered and regularized matrix in physical units
        matr = _np.dot(_uo*_sp, _vo)

        # convert matrix to hardware units
        str2curr = _np.r_[self._corrs_dev.strength_2_current_factor, 1.0]
        currgain = _np.r_[self._corrs_dev.curr_gain, 1.0]
        if _np.any(str2curr == 0) or _np.any(currgain == 0):
            self._update_log('ERR:Could not calculate hardware unit')
            self._update_log('ERR:matrix, CurrGain or "urad to A" ')
            self._update_log('ERR:factor have zero values.')
            return False
        # unit convertion: um/urad (1)-> nm/urad (2)-> nm/A (3)-> nm/counts
        matc = matr * self._const.CONV_UM_2_NM
        matc = matc / str2curr[selcorr]
        matc = matc * currgain[selcorr]

        # obtain pseudoinverse
        # calculate SVD for converted matrix
        _uc, _sc, _vc = _np.linalg.svd(matc, full_matrices=False)
        # handle singular value selection
        idcsc = _sc/_sc.max() >= self._const.SINGVALHW_THRS
        inv_sc = _np.zeros(_so.size, dtype=float)
        inv_sc[idcsc] = 1/_sc[idcsc]
        # calculate pseudoinverse of converted matrix from SVD
        invmatc = _np.dot(_vc.T*inv_sc, _uc.T)

        # update internal states and PVs
        sing_vals = _np.zeros(self._const.nr_svals, dtype=float)
        sing_vals[:_so.size] = _so
        self.run_callbacks('SingValuesRaw-Mon', sing_vals)

        sing_vals = _np.zeros(self._const.nr_svals, dtype=float)
        sing_vals[:_sp.size] = _sp
        self.run_callbacks('SingValues-Mon', sing_vals)
        self.run_callbacks('NrSingValues-Mon', nrs)

        self._invrespmat = _np.zeros(self._respmat.shape, dtype=float).T
        self._invrespmat[selmat.T] = invmat.ravel()
        self.run_callbacks('InvRespMat-Mon', list(self._invrespmat.ravel()))

        respmat_proc = _np.zeros(self._respmat.shape, dtype=float)
        respmat_proc[selmat] = matr.ravel()
        self.run_callbacks('RespMat-Mon', list(respmat_proc.ravel()))

        sing_vals = _np.zeros(self._const.nr_svals, dtype=float)
        sing_vals[:_sc.size] = _sc
        self.run_callbacks('SingValuesHw-Mon', sing_vals)

        self._invrespmatconv = _np.zeros(self._respmat.shape, dtype=float).T
        self._invrespmatconv[selmat.T] = invmatc.ravel()
        self.run_callbacks(
            'InvRespMatHw-Mon', list(self._invrespmatconv.ravel()))

        respmatconv_proc = _np.zeros(self._respmat.shape, dtype=float)
        respmatconv_proc[selmat] = matc.ravel()
        self.run_callbacks('RespMatHw-Mon', list(respmatconv_proc.ravel()))

        # send new matrix to low level FOFB
        self._calc_corrs_coeffs()
        if self._init:
            self._set_corrs_coeffs()

        self._update_log('Ok!')
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
        self._meas_respmat_count += 1
        self.run_callbacks('MeasRespMat-Cmd', self._meas_respmat_count)
        return True

    def set_respmat_meas_kick(self, plane, value):
        """Set response matrix measure kick value for plane [urad]."""
        self._meas_respmat_kick[plane] = value
        self.run_callbacks('MeasRespMatKick'+plane.upper()+'-RB', value)
        return True

    def set_respmat_meas_wait_time(self, value):
        """Set response matrix measure wait time [s]."""
        self._meas_respmat_wait = value
        self.run_callbacks('MeasRespMatWait-RB', value)
        return True

    def _start_meas_respmat(self):
        if self._loop_state == self._const.LoopState.Closed:
            self._update_log('ERR: Open FOFB loop before continue.')
            return False
        if not self._sofb_check_config():
            self._update_log('ERR: Aborted.')
            return False
        if self._measuring_respmat:
            self._update_log('ERR: Measurement already in progress...')
            return False
        if not self.havebeam:
            self._update_log('ERR: Do not have stored beam. Aborted.')
            return False
        self._update_log('Starting RespMat measurement.')
        self._measuring_respmat = True
        self._meas_respmat_thread = _Thread(
            target=self._do_meas_respmat, daemon=True)
        self._meas_respmat_thread.start()
        return True

    def _stop_meas_respmat(self):
        if not self._measuring_respmat:
            self._update_log('ERR: No Measurement occurring.')
            return False
        self._update_log('Aborting measurement. Wait...')
        self._measuring_respmat = False
        return True

    def _reset_meas_respmat(self):
        if self._measuring_respmat:
            self._update_log('WARN: measurement in progress...')
            return False
        self._update_log('Reseting measurement status.')
        self.run_callbacks('MeasRespMat-Mon', self._const.MeasRespMatMon.Idle)
        return True

    def _do_meas_respmat(self):
        self.run_callbacks(
            'MeasRespMat-Mon', self._const.MeasRespMatMon.Measuring)
        mat = list()
        enbllist = self.corr_enbllist
        sum_enbld = sum(enbllist)

        orbzero = _np.zeros(len(self.bpm_enbllist), dtype=float)
        for i in range(self._const.nr_corrs):
            if not self._measuring_respmat:
                self.run_callbacks(
                    'MeasRespMat-Mon', self._const.MeasRespMatMon.Aborted)
                self._update_log('Measurement stopped.')
                for _ in range(i, self._const.nr_corrs):
                    mat.append(orbzero)
                break
            if not self.havebeam:
                self.run_callbacks(
                    'MeasRespMat-Mon', self._const.MeasRespMatMon.Aborted)
                self._update_log(
                    'ERR: Cannot Measure, We do not have stored beam!')
                for _ in range(i, self._const.nr_corrs):
                    mat.append(orbzero)
                break
            if not enbllist[i]:
                mat.append(orbzero)
                continue

            if i < self._const.nr_ch + self._const.nr_cv:
                dev = self._corrs_dev[i]
                self._update_log('{0:d}/{1:d} -> {2:s}'.format(
                    i+1, sum_enbld, dev.devname))

                corrtype = 'ch' if 'FCH' in dev.devname else 'cv'
                delta = self._meas_respmat_kick[corrtype]

                orig_kick = dev.strength

                dev.strength = orig_kick + delta/2
                _time.sleep(self._meas_respmat_wait)
                orbp = self._sofb_get_orbit()

                dev.strength = orig_kick - delta/2
                _time.sleep(self._meas_respmat_wait)
                orbn = self._sofb_get_orbit()

                dev.strength = orig_kick
            elif i < self._const.nr_corrs:
                dev = self.rf_dev
                self._update_log('{0:d}/{1:d} -> {2:s}'.format(
                    i+1, sum_enbld, dev.devname))

                delta = self._meas_respmat_kick['rf']

                orig_freq = dev.frequency

                dev.frequency = orig_freq + delta/2
                _time.sleep(self._meas_respmat_wait)
                orbp = self._sofb_get_orbit()

                dev.frequency = orig_freq - delta/2
                _time.sleep(self._meas_respmat_wait)
                orbn = self._sofb_get_orbit()

                dev.frequency = orig_freq
            mat.append((orbp - orbn)/delta)

        mat = _np.array(mat).T
        self.set_respmat(list(mat.ravel()))
        self.run_callbacks(
            'MeasRespMat-Mon', self._const.MeasRespMatMon.Completed)
        self._measuring_respmat = False
        self._update_log('RespMat Measurement Completed!')

    def _sofb_check_config(self):
        if not self._sisofb_dev.autocorrsts == _Const.LoopState.Open:
            self._update_log('ERR: Open SOFB loop before continue.')
            return False
        if not self._sisofb_dev.opmode_str == 'SlowOrb':
            self._update_log('ERR: SOFBMode is different from SlowOrb.')
            return False
        if not self._sisofb_dev.wait_orb_status_ok(timeout=0.5):
            self._update_log('ERR: SOFB orbit status is not ok.')
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
            self._update_log('FATAL: We do not have stored beam!')
            self._update_log('FATAL: Opening FOFB loop...')
            self.set_loop_state(self._const.LoopState.Open)

    def _callback_orbintlk(self, pvname, value, **kws):
        sub = _PVName(pvname).sub[:2]
        if value != 0:
            text = ('FATAL' if self._loop_state else 'WARN')
            text += ':Ctrlr.'+sub+' detected large orb.dist.!'
            self._update_log(text)
            if self._loop_state != self._const.LoopState.Closed:
                return

            if self._thread_loopstate is None or \
                    (self._thread_loopstate is not None and
                     not self._thread_loopstate.is_alive()) or \
                    (self._thread_loopstate is not None and
                     self._thread_loopstate.is_alive() and
                     self._loop_state_lastsp != self._const.LoopState.Open):
                self._update_log('FATAL: Opening FOFB loop...')
                self.run_callbacks('LoopState-Sel', self._const.LoopState.Open)
                self.run_callbacks('LoopState-Sts', self._const.LoopState.Open)
                self.set_loop_state(self._const.LoopState.Open, reset=True)

    # --- auxiliary corrector and fofbcontroller methods ---

    def _check_corr_connection(self):
        if self._corrs_dev.connected:
            return True
        self._update_log('ERR:Correctors not connected... aborted.')
        return False

    def _check_set_corrs_opmode(self):
        """Check and configure opmode.

        Control only correctors that are in the enable list.
        """
        self._update_log('Checking corrector opmode...')
        opmode = self._corrs_dev.OPMODE_STS.manual \
            if self._loop_state == self._const.LoopState.Open \
            else self._corrs_dev.OPMODE_STS.fofb
        is_ok = 1 * (self._corrs_dev.opmode == opmode)
        idcs = _np.where((1 * self.corr_enbllist[:-1] - is_ok) > 0)[0]
        if idcs.size:
            self._update_log('Configuring corrector opmode...')
            self._corrs_dev.set_opmode(opmode, psindices=idcs)
            if self._corrs_dev.check_opmode(opmode, psindices=idcs, timeout=5):
                self._update_log('...done!')
                return True
            self._update_log('ERR:Failed to set corrector opmode.')
            return False
        self._update_log('All ok.')
        return True

    def _set_corrs_fofbacc_freeze(self):
        """Configure FOFBAccFreeze state.

        Keep in accordance with enable list and loop_state.
        """
        self._update_log('Setting corrector FOFCAccFreeze...')
        freeze = self._get_corrs_fofbacc_freeze_desired()
        self._corrs_dev.set_fofbacc_freeze(freeze)
        self._update_log('...done!')

    def _get_corrs_fofbacc_freeze_desired(self):
        if self._loop_state == self._const.LoopState.Open:
            freeze = _np.ones(len(self.corr_enbllist[:-1]))
        else:
            freeze = 1 * _np.logical_not(self.corr_enbllist[:-1])
        return freeze

    def _calc_corrs_coeffs(self, log=True):
        """Calculate corrector coefficients and gains."""
        if log:
            self._update_log('Calculating corrector coefficients ')
            self._update_log('and FOFB pre-accumulator gains...')

        # calculate coefficients and gains
        invmat = self._invrespmatconv[:-1]  # remove RF line
        coeffs = _np.zeros(invmat.shape)
        gains = _np.zeros(self._const.nr_chcv)

        loop_gain_h, loop_gain_v = self._loop_gain_mon_h, self._loop_gain_mon_v
        nrch, nrcv = self._const.nr_ch, self._const.nr_cv
        slch, slcv = slice(0, nrch), slice(nrch, nrch+nrcv)

        reso = self._const.ACCGAIN_RESO

        if self._invrespmat_normmode == self._const.GlobIndiv.Global:
            maxval = _np.amax(abs(invmat))
            gain_h = _np.ceil(maxval * loop_gain_h / reso) * reso
            if gain_h != 0:
                norm_h = gain_h / loop_gain_h
                coeffs[slch, :] = invmat[slch, :] / norm_h
                gains[slch] = gain_h * _np.ones(nrch)
            gain_v = _np.ceil(maxval * loop_gain_v / reso) * reso
            if gain_v != 0:
                norm_v = gain_v / loop_gain_v
                coeffs[slcv, :] = invmat[slcv, :] / norm_v
                gains[slcv] = gain_v * _np.ones(nrcv)
        elif self._invrespmat_normmode == self._const.GlobIndiv.Individual:
            maxval = _np.amax(abs(invmat), axis=1)
            gains[slch] = _np.ceil(maxval[slch] * loop_gain_h / reso) * reso
            gains[slcv] = _np.ceil(maxval[slcv] * loop_gain_v / reso) * reso
            norm = _np.zeros(self._const.nr_chcv)
            norm[slch] = gains[slch] / loop_gain_h
            norm[slcv] = gains[slcv] / loop_gain_v
            idcs = norm > 0
            coeffs[idcs] = invmat[idcs] / norm[idcs][:, None]

        # handle FOFB BPM ordering
        nrbpm = self._const.nr_bpms
        coeffs[:, :nrbpm] = _np.roll(coeffs[:, :nrbpm], 1, axis=1)
        coeffs[:, nrbpm:] = _np.roll(coeffs[:, nrbpm:], 1, axis=1)

        # set internal states
        self._pscoeffs = coeffs
        self._psgains = gains
        # update PVs
        self.run_callbacks('CorrCoeffs-Mon', list(self._pscoeffs.ravel()))
        self.run_callbacks('CorrGains-Mon', list(self._psgains.ravel()))

        if log:
            self._update_log('...done!')

    def _set_corrs_coeffs(self, log=True):
        """Set corrector coefficients and gains."""
        if log:
            self._update_log('Setting corrector gains and coefficients...')
        if not self._check_corr_connection():
            return False
        self._corrs_dev.set_invrespmat_row(self._pscoeffs)
        self._corrs_dev.set_fofbacc_gain(self._psgains)
        if log:
            self._update_log('...done!')
        return True

    def _check_fofbctrl_connection(self):
        if self._llfofb_dev.connected:
            return True
        self._update_log('ERR:FOFB Controllers not connected...')
        self._update_log('ERR:aborted.')
        return False

    def _update_fofbctrl_sync_enbllist(self):
        if self._fofbctrl_syncuseenbllist:
            bpmx = self._enable_lists['bpmx']
            bpmy = self._enable_lists['bpmy']
            dccenbl = _np.logical_or(bpmx, bpmy)
            dccenbl[self._const.bpm_dccenbl_idcs] = True
            bpms = self._llfofb_dev.get_dccfmc_visible_bpms([
                self._const.bpm_names[i] for i, s in enumerate(dccenbl) if s])
            dccenbl = _np.array([b in bpms for b in self._const.bpm_names])
        else:
            dccenbl = _np.ones(self._const.nr_bpms, dtype=bool)
        self._fofbctrl_syncenbllist = dccenbl
        self.run_callbacks('CtrlrSyncEnblList-Mon', dccenbl)

    def _get_fofbctrl_bpmdcc_enbl(self):
        return [self._const.bpm_names[i] for i, s in
                enumerate(self._fofbctrl_syncenbllist) if s]

    def _do_fofbctrl_syncnet(self):
        bpms = self._get_fofbctrl_bpmdcc_enbl()
        if not self._llfofb_dev.check_net_synced(bpms=bpms):
            self._update_log('Syncing FOFB net...')
            if self._llfofb_dev.cmd_sync_net(bpms=bpms):
                self._update_log('Sync sent to FOFB net.')
            else:
                self._update_log('ERR:Failed to sync FOFB net.')
        else:
            self._update_log('FOFB net already synced.')

    # --- auxiliary log methods ---

    def _update_log(self, msg):
        if 'ERR' in msg:
            _log.error(msg[4:])
        elif 'FATAL' in msg:
            _log.error(msg[6:])
        elif 'WARN' in msg:
            _log.warning(msg[5:])
        else:
            _log.info(msg)
        self.run_callbacks('Log-Mon', msg)

    def _check_configs(self):
        tplanned = 1.0/App.SCAN_FREQUENCY
        while not self.quit:
            if not self.scanning:
                _time.sleep(tplanned)
                continue

            _t0 = _time.time()

            # correctors status
            value = 0
            if self._corrs_dev.connected:
                idcs = _np.where(self.corr_enbllist[:-1] == 1)[0]
                # PwrStateOn
                state = self._const.OffOn.On
                if not self._corrs_dev.check_pwrstate(
                        state, psindices=idcs, timeout=0.2):
                    value = _updt_bit(value, 1, 1)
                # OpModeConfigured
                opmode = self._corrs_dev.OPMODE_STS.manual \
                    if self._loop_state == self._const.LoopState.Open \
                    else self._corrs_dev.OPMODE_STS.fofb
                if not self._corrs_dev.check_opmode(
                        opmode, psindices=idcs, timeout=0.2):
                    value = _updt_bit(value, 2, 1)
                # AccFreezeConfigured
                freeze = self._get_corrs_fofbacc_freeze_desired()
                if not self._corrs_dev.check_fofbacc_freeze(
                        freeze, timeout=0.2):
                    value = _updt_bit(value, 3, 1)
                # InvRespMatRowSynced
                if not self._corrs_dev.check_invrespmat_row(self._pscoeffs):
                    value = _updt_bit(value, 4, 1)
                # AccGainSynced
                if not self._corrs_dev.check_fofbacc_gain(self._psgains):
                    value = _updt_bit(value, 5, 1)
                # AccSatLimsSynced
                chn, chl = self._const.ch_names, self._ch_maxacccurr
                cvn, cvl = self._const.cv_names, self._cv_maxacccurr
                isok = self._corrs_dev.check_fofbacc_satmax(chl, psnames=chn)
                isok &= self._corrs_dev.check_fofbacc_satmin(-chl, psnames=chn)
                isok &= self._corrs_dev.check_fofbacc_satmax(cvl, psnames=cvn)
                isok &= self._corrs_dev.check_fofbacc_satmin(-cvl, psnames=cvn)
                if not isok:
                    value = _updt_bit(value, 6, 1)
            else:
                value = 0b1111111

            self._corr_status = value
            self.run_callbacks('CorrStatus-Mon', self._corr_status)

            # FOFB controllers status
            value = 0
            if self._llfofb_dev.connected:
                # BPMIdsConfigured
                if not self._llfofb_dev.bpm_id_configured:
                    value = _updt_bit(value, 1, 1)
                # NetSynced
                bpms = self._get_fofbctrl_bpmdcc_enbl()
                if not self._llfofb_dev.check_net_synced(bpms=bpms):
                    value = _updt_bit(value, 2, 1)
                # LinkPartnerConnected
                if not self._llfofb_dev.linkpartners_connected:
                    value = _updt_bit(value, 3, 1)
                # RefOrbSynced
                reforb = _np.hstack([self._reforbhw_x, self._reforbhw_y])
                if not self._llfofb_dev.check_reforb(reforb):
                    value = _updt_bit(value, 4, 1)
                # TimeFrameLenSynced
                tframelen = self._time_frame_len
                if not _np.all(self._llfofb_dev.time_frame_len == tframelen):
                    value = _updt_bit(value, 5, 1)
                # BPMLogTrigsConfigured
                if not self._llfofb_dev.bpm_trigs_configured:
                    value = _updt_bit(value, 6, 1)
                # OrbDistortionDetectionSynced
                sts = self._loop_max_orb_dist_enbl
                sts_ok = self._llfofb_dev.max_orb_distortion_enbl == sts
                thres = self._loop_max_orb_dist*self._const.CONV_UM_2_NM
                thres_ok = self._llfofb_dev.max_orb_distortion == thres
                if not _np.all(sts_ok) or not _np.all(thres_ok):
                    value = _updt_bit(value, 7, 1)
                # LoopInterlockOk
                if not self._llfofb_dev.interlock_ok:
                    value = _updt_bit(value, 8, 1)
            else:
                value = 0b111111111

            self._fofbctrl_status = value
            self.run_callbacks('CtrlrStatus-Mon', self._fofbctrl_status)

            ttook = _time.time() - _t0
            tsleep = tplanned - ttook
            if tsleep > 0:
                _time.sleep(tsleep)
            else:
                _log.warning(
                    'Configuration check took more than planned... '
                    '{0:.3f}/{1:.3f} s'.format(ttook, tplanned))
