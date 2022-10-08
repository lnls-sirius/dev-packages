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

    SCAN_FREQUENCY = 0.5  # [Hz]
    TIMEOUT_CONN = 2  # [s]

    def __init__(self, tests=False):
        """Class constructor."""
        super().__init__()
        self._const = _Const()
        self._pvs_database = self._const.get_hlfofb_database()
        self._tests = tests
        self._init = False

        # internal states
        self._loop_state = self._const.LoopState.Open
        self._loop_gain = 1
        self._loop_gain_mon = 0
        self._thread_loopstate = None
        self._abort_thread = False
        self._corr_status = self._pvs_database['CorrStatus-Mon']['value']
        self._corr_confall_count = 0
        self._corr_setopmodemanual_count = 0
        self._corr_setaccfreezeenbl_count = 0
        self._corr_setaccfreezedsbl_count = 0
        self._corr_setaccclear_count = 0
        self._corr_setcurrzero_count = 0
        self._corr_maxacccurr = self._pvs_database['CorrAccSatMax-SP']['value']
        self._fofbctrl_status = \
            self._pvs_database['FOFBCtrlStatus-Mon']['value']
        self._fofbctrl_syncnet_count = 0
        self._fofbctrl_syncref_count = 0
        self._fofbctrl_conftframelen_count = 0
        self._fofbctrl_confbpmlogtrg_count = 0
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
        self._rf_dev = _RFGen()

        self._llfofb_dev = _FamFOFBCtrls()

        self._sisofb_dev.wait_for_connection(self.TIMEOUT_CONN)
        self._corrs_dev.wait_for_connection(3*self.TIMEOUT_CONN)
        self._rf_dev.wait_for_connection(self.TIMEOUT_CONN)
        self._llfofb_dev.wait_for_connection(self.TIMEOUT_CONN)

        havebeam_pvname = _PVName(
            'SI-Glob:AP-CurrInfo:StoredEBeam-Mon').substitute(
                prefix=_vaca_prefix)
        self._havebeam_pv = _PV(
            havebeam_pvname, connection_timeout=0.05,
            callback=self._callback_havebeam)

        # pvs to write methods
        self.map_pv2write = {
            'LoopState-Sel': self.set_loopstate,
            'LoopGain-SP': self.set_loopgain,
            'CorrConfig-Cmd': self.cmd_corr_configure,
            'CorrSetOpModeManual-Cmd': self.cmd_corr_opmode_manual,
            'CorrSetAccFreezeDsbl-Cmd': self.cmd_corr_accfreeze_dsbl,
            'CorrSetAccFreezeEnbl-Cmd': self.cmd_corr_accfreeze_enbl,
            'CorrSetAccClear-Cmd': self.cmd_corr_accclear,
            'CorrSetCurrZero-Cmd': self.cmd_corr_currzero,
            'CorrAccSatMax-SP': self.set_corr_accsatmax,
            'FOFBCtrlSyncNet-Cmd': self.cmd_fofbctrl_syncnet,
            'FOFBCtrlSyncRefOrb-Cmd': self.cmd_fofbctrl_syncreforb,
            'FOFBCtrlConfTFrameLen-Cmd': self.cmd_fofbctrl_conftframelen,
            'FOFBCtrlConfBPMLogTrg-Cmd': self.cmd_fofbctrl_confbpmlogtrg,
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
        self.run_callbacks('LoopGain-SP', self._loop_gain)
        self.run_callbacks('LoopGain-RB', self._loop_gain)
        self.run_callbacks('LoopGain-Mon', self._loop_gain_mon)
        self.run_callbacks('CorrStatus-Mon', self._corr_status)
        self.run_callbacks('CorrConfig-Cmd', self._corr_confall_count)
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
        self.run_callbacks('CorrAccSatMax-SP', self._corr_maxacccurr)
        self.run_callbacks('CorrAccSatMax-RB', self._corr_maxacccurr)
        self.run_callbacks('FOFBCtrlStatus-Mon', self._fofbctrl_status)
        self.run_callbacks(
            'FOFBCtrlSyncNet-Cmd', self._fofbctrl_syncnet_count)
        self.run_callbacks(
            'FOFBCtrlSyncRefOrb-Cmd', self._fofbctrl_syncref_count)
        self.run_callbacks(
            'FOFBCtrlConfTFrameLen-Cmd', self._fofbctrl_conftframelen_count)
        self.run_callbacks(
            'FOFBCtrlConfBPMLogTrg-Cmd', self._fofbctrl_confbpmlogtrg_count)
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
        _time.sleep(interval)

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

    def set_loopstate(self, value):
        """Set loop state."""
        if not 0 <= value < len(_ETypes.OPEN_CLOSED):
            return False

        if value and not self.havebeam:
            self._update_log('ERR: Do not have stored beam. Aborted.')
            return False

        if self._thread_loopstate is not None and \
                self._thread_loopstate.is_alive():
            self._update_log('WARN:Interrupting Loop Enable thread...')
            self._abort_thread = True
            self._thread_loopstate.join()

        self._thread_loopstate = _Thread(
            target=self._thread_set_loop_state, args=[value, ], daemon=True)
        self._thread_loopstate.start()
        return True

    def _thread_set_loop_state(self, value):
        if value:  # closing the loop
            # set gains to zero, recalculate gains and coeffs
            self._update_log('Setting Loop Gain to zero...')
            self._loop_gain_mon = 0
            self._calc_corrs_coeffs(log=False)
            # set and wait corrector gains and coeffs to zero
            self._set_corrs_coeffs(log=False)
            _t0 = _time.time()
            while _time.time() - _t0 < self._const.DEF_TIMEOUT:
                _time.sleep(self._const.DEF_TIMESLEEP)
                if self._corrs_dev.check_invrespmat_row(self._pscoeffs) and \
                        self._corrs_dev.check_fofbacc_gain(self._psgains):
                    break
            else:
                self._update_log('ERR:Timed out waiting for correctors to')
                self._update_log('ERR:implement gains and coefficients.')
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

            if self._check_abort_thread():
                return

            # do ramp up
            self._update_log('...done. Starting Loop Gain ramp up...')
            if self._do_loop_gain_ramp(ramp='up'):
                self._update_log('LoopGain ramp up finished!')

        else:  # opening the loop
            if self.havebeam:
                # do ramp down
                self._update_log('Starting Loop Gain ramp down...')
                if self._do_loop_gain_ramp(ramp='down'):
                    self._update_log('Loop Gain ramp down finished!')
            else:
                self._loop_gain_mon = 0.0
                self.run_callbacks('LoopGain-Mon', self._loop_gain_mon)
                self._calc_corrs_coeffs()
                self._set_corrs_coeffs()

            if self._check_abort_thread():
                return

            # open the loop
            self._loop_state = value
            self._check_set_corrs_opmode()

        self.run_callbacks('LoopState-Sts', self._loop_state)

    def _do_loop_gain_ramp(self, ramp='up'):
        end = self._loop_gain if ramp == 'up' else 0.0
        steps = _np.linspace(
            self._loop_gain_mon, end, self._const.LOOPGAIN_RMP_NPTS)
        for i, val in enumerate(steps):
            if not self.havebeam:
                self._update_log('ERR: Do not have stored beam. Aborted.')
                return False
            if self._check_abort_thread():
                return False

            self._loop_gain_mon = val
            self.run_callbacks('LoopGain-Mon', self._loop_gain_mon)
            self._update_log(
                f'{i+1:02d}/{len(steps):02d} -> Loop Gain = {val:.3f}')
            self._calc_corrs_coeffs(log=False)
            self._set_corrs_coeffs(log=False)
            _time.sleep(1/self._const.LOOPGAIN_RMP_FREQ)
        return True

    def _check_abort_thread(self):
        if self._abort_thread:
            self._update_log('WARN: Loop state thread aborted.')
            self._abort_thread = False
            return True
        return False

    def set_loopgain(self, value):
        """Set loop gain."""
        if not -2**3 <= value <= 2**3-1:
            return False

        if self._thread_loopstate is not None and \
                self._thread_loopstate.is_alive():
            self._update_log('ERR:Wait for Loop Gain ramp before ')
            self._update_log('ERR:setting new value.')
            return False

        self._loop_gain = value

        # if loop closed, calculate new gains and coefficients
        if self._loop_state:
            self._loop_gain_mon = value
            self.run_callbacks('LoopGain-Mon', self._loop_gain_mon)
            self._calc_corrs_coeffs()
            # self._set_corrs_coeffs()

        self._update_log('Changed Loop Gain to '+str(value)+'.')
        self.run_callbacks('LoopGain-RB', self._loop_gain)
        return True

    # --- devices configuration ---

    def cmd_corr_configure(self, _):
        """Configure corrector command."""
        self._update_log('Received configure corrector command...')

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

    def cmd_corr_opmode_manual(self, _):
        """Set all corrector opmode."""
        self._update_log('Received set corrector opmode to manual...')

        self._update_log('Setting all corrector opmode to manual...')
        self._corrs_dev.set_opmode(self._corrs_dev.OPMODE_STS.manual)
        self._update_log('Done.')

        self._corr_setopmodemanual_count += 1
        self.run_callbacks(
            'CorrSetOpModeManual-Cmd', self._corr_setopmodemanual_count)
        return False

    def cmd_corr_accfreeze_dsbl(self, _):
        """Set all corrector accumulator freeze state to Dsbl."""
        self._update_log('Received set corrector AccFreeze to Dsbl...')

        self._update_log('Setting AccFreeze to Dsbl...')
        self._corrs_dev.set_fofbacc_freeze(self._const.DsblEnbl.Dsbl)
        self._update_log('Done.')

        self._corr_setaccfreezedsbl_count += 1
        self.run_callbacks(
            'CorrSetAccFreezeDsbl-Cmd', self._corr_setaccfreezedsbl_count)
        return False

    def cmd_corr_accfreeze_enbl(self, _):
        """Set all corrector accumulator freeze state to Enbl."""
        self._update_log('Received set corrector AccFreeze to Enbl...')

        self._update_log('Setting AccFreeze to Enbl...')
        self._corrs_dev.set_fofbacc_freeze(self._const.DsblEnbl.Enbl)
        self._update_log('Done.')

        self._corr_setaccfreezeenbl_count += 1
        self.run_callbacks(
            'CorrSetAccFreezeEnbl-Cmd', self._corr_setaccfreezeenbl_count)
        return False

    def cmd_corr_accclear(self, _):
        """Clear all corrector accumulator."""
        self._update_log('Received clear all corrector accumulator...')

        self._update_log('Sending clear accumulator command...')
        self._corrs_dev.cmd_fofbacc_clear()
        self._update_log('Done.')

        self._corr_setaccclear_count += 1
        self.run_callbacks(
            'CorrSetAccClear-Cmd', self._corr_setaccclear_count)
        return False

    def cmd_corr_currzero(self, _):
        """Set all corrector current to zero."""
        self._update_log('Received set corrector current to zero...')

        self._update_log('Sending all corrector current to zero...')
        self._corrs_dev.set_current(0)
        self._update_log('Done.')

        self._corr_setcurrzero_count += 1
        self.run_callbacks(
            'CorrSetCurrZero-Cmd', self._corr_setcurrzero_count)
        return False

    def set_corr_accsatmax(self, value):
        """Set corrector FOFB accumulator saturation limits."""
        if not 0 <= value <= 0.95:
            return False

        self._corr_maxacccurr = value
        self._update_log('Setting corrector saturation limits...')
        self._corrs_dev.set_fofbacc_satmax(self._corr_maxacccurr)
        self._corrs_dev.set_fofbacc_satmin(-self._corr_maxacccurr)
        self._update_log('...done!')

        self._update_log('Changed corrector saturation limits to ')
        self._update_log(str(value)+'A.')
        self.run_callbacks('CorrAccSatMax-RB', self._corr_maxacccurr)
        return True

    def cmd_fofbctrl_syncnet(self, _):
        """Sync FOFB net command."""
        self._update_log('Received sync FOFB net command...')
        self._update_log('Checking...')
        if not self._llfofb_dev.net_synced:
            self._update_log('Syncing FOFB net...')
            if self._llfofb_dev.cmd_sync_net():
                self._update_log('Sync sent to FOFB net.')
            else:
                self._update_log('ERR:Failed to sync FOFB net.')
        else:
            self._update_log('FOFB net already synced.')

        self._fofbctrl_syncnet_count += 1
        self.run_callbacks(
            'FOFBCtrlSyncNet-Cmd', self._fofbctrl_syncnet_count)
        return False

    def cmd_fofbctrl_syncreforb(self, _):
        """Sync FOFB RefOrb command."""
        self._update_log('Received sync FOFB RefOrb command...')
        self._update_log('Checking...')
        if not self._llfofb_dev.check_reforbx(self._reforbhw_x) or \
                not self._llfofb_dev.check_reforby(self._reforbhw_y):
            self._update_log('Syncing FOFB RefOrb...')
            self._llfofb_dev.set_reforbx(self._reforbhw_x)
            self._llfofb_dev.set_reforby(self._reforbhw_y)
            self._update_log('Sent RefOrb to FOFB controllers.')
        else:
            self._update_log('FOFB RefOrb already synced.')

        self._fofbctrl_syncref_count += 1
        self.run_callbacks(
            'FOFBCtrlSyncRefOrb-Cmd', self._fofbctrl_syncref_count)
        return False

    def cmd_fofbctrl_conftframelen(self, _):
        """Configure FOFB controllers TimeFrameLen command."""
        self._update_log('Received configure FOFB controllers')
        self._update_log('TimeFrameLen command... Checking...')
        deftimeframe = self._llfofb_dev.DEF_DCC_TIMEFRAMELEN
        if not _np.all(self._llfofb_dev.time_frame_len == deftimeframe):
            self._update_log('Configuring TimeFrameLen PVs...')
            if self._llfofb_dev.set_time_frame_len():
                self._update_log('TimeFrameLen PVs configured!')
            else:
                self._update_log('ERR:Failed to configure TimeFrameLen.')
        else:
            self._update_log('TimeFrameLen PVs already configured.')

        self._fofbctrl_conftframelen_count += 1
        self.run_callbacks(
            'FOFBCtrlConfTFrameLen-Cmd', self._fofbctrl_conftframelen_count)
        return False

    def cmd_fofbctrl_confbpmlogtrg(self, _):
        """Configure BPM logical triggers command."""
        self._update_log('Received configure BPM Logical')
        self._update_log('triggers command... Checking...')
        if not self._llfofb_dev.bpm_trigs_configured:
            self._update_log('Configuring BPM logical triggers...')
            if self._llfofb_dev.cmd_config_bpm_trigs():
                self._update_log('BPM logical triggers configured!')
            else:
                self._update_log('ERR:Failed to configure BPM log.trigs.')
        else:
            self._update_log('BPM logical triggers already configured.')

        self._fofbctrl_confbpmlogtrg_count += 1
        self.run_callbacks(
            'FOFBCtrlConfBPMLogTrg-Cmd', self._fofbctrl_confbpmlogtrg_count)
        return False

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
        fun = getattr(self._llfofb_dev, 'set_reforb' + plane.lower())
        fun(refhw)

        # update readback PV
        self.run_callbacks(f'RefOrb{plane.upper()}-RB', list(ref.ravel()))
        self.run_callbacks(f'RefOrbHw{plane.upper()}-Mon', refhw)
        self._update_log('Done!')
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
            self._set_corrs_fofbacc_freeze()

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
        # self._set_corrs_coeffs()

        self.run_callbacks(
            'InvRespMatNormMode-Sts', self._invrespmat_normmode)
        return True

    def _calc_matrices(self):
        self._update_log('Calculating Inverse Matrix...')

        if not self._corrs_dev.connected:
            self._update_log('ERR:Correctors not connected... aborted.')
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
        # if self._init:
        #     self._set_corrs_coeffs()

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
        if self._sofb_check_config():
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
        if not self._sisofb_dev.opmode == 'SlowOrb':
            self._update_log('ERR: SOFBMode is different from SlowOrb.')
            return False
        if not self._sisofb_dev.wait_orb_status_ok(timeout=0.5):
            self._update_log('ERR: SOFB orbit status is not ok.')
            return False
        return True

    def _sofb_get_orbit(self):
        orbx, orby = self._sisofb_dev.orbx, self._sisofb_dev.orby
        return _np.hstack([orbx, orby])

    # --- callbacks ---

    def _callback_havebeam(self, value, **kws):
        if not value and self._loop_state == self._const.LoopState.Closed:
            self._update_log('FATAL: We do not have stored beam!')
            self._update_log('FATAL: Opening FOFB loop...')
            self.set_loopstate(self._const.LoopState.Open)
            self._update_log('Done.')

    # --- auxiliary corrector and fofbcontroller methods ---

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
                self._update_log('Done.')
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
        self._update_log('Done!')

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
        loop_gain = self._loop_gain_mon
        if loop_gain == 0:
            gains = _np.zeros(self._const.nr_chcv)
        else:
            reso = self._const.ACCGAIN_RESO
            if self._invrespmat_normmode == self._const.GlobIndiv.Global:
                maxval = _np.amax(abs(invmat))
                gain = _np.ceil(maxval * loop_gain / reso) * reso
                norm = gain / loop_gain
                if norm != 0:
                    coeffs = invmat / norm
                gains = gain * _np.ones(self._const.nr_chcv)
            elif self._invrespmat_normmode == self._const.GlobIndiv.Individual:
                maxval = _np.amax(abs(invmat), axis=1)
                gains = _np.ceil(maxval * loop_gain / reso) * reso
                norm = gains / loop_gain
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
            self._update_log('Done!')

    def _set_corrs_coeffs(self, log=True):
        """Set corrector coefficients and gains."""
        if log:
            self._update_log('Setting corrector gains and coefficients...')
        self._corrs_dev.set_invrespmat_row(self._pscoeffs)
        self._corrs_dev.set_fofbacc_gain(self._psgains)
        if log:
            self._update_log('Done!')

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
                lim = self._corr_maxacccurr
                if not self._corrs_dev.check_fofbacc_satmax(lim) or \
                        not self._corrs_dev.check_fofbacc_satmin(-lim):
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
                if not self._llfofb_dev.net_synced:
                    value = _updt_bit(value, 2, 1)
                # LinkPartnerConnected
                if not self._llfofb_dev.linkpartners_connected:
                    value = _updt_bit(value, 3, 1)
                # RefOrbSynced
                if not self._llfofb_dev.check_reforbx(self._reforbhw_x) or \
                        not self._llfofb_dev.check_reforby(self._reforbhw_y):
                    value = _updt_bit(value, 4, 1)
                # TimeFrameLenConfigured
                tframelen = self._llfofb_dev.DEF_DCC_TIMEFRAMELEN
                if not _np.all(self._llfofb_dev.time_frame_len == tframelen):
                    value = _updt_bit(value, 5, 1)
                # BPMLogTrigsConfigured
                if not self._llfofb_dev.bpm_trigs_configured:
                    value = _updt_bit(value, 6, 1)
            else:
                value = 0b1111111

            self._fofbctrl_status = value
            self.run_callbacks('FOFBCtrlStatus-Mon', self._fofbctrl_status)

            ttook = _time.time() - _t0
            tsleep = tplanned - ttook
            if tsleep > 0:
                _time.sleep(tsleep)
            else:
                _log.warning(
                    'Configuration check took more than planned... '
                    '{0:.3f}/{1:.3f} s'.format(ttook, tplanned))
