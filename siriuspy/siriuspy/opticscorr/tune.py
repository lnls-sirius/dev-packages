"""Main module of AS-AP-TuneCorr IOC."""

import numpy as _np
from epics import PV as _PV
import epics as _epics

import logging as _log
from time import time as _time, sleep as _sleep
from functools import partial as _part

from ..envars import VACA_PREFIX as _vaca_prefix
from ..namesys import SiriusPVName as _SiriusPVName

from .csdev import Const as _Const, ETypes as _ETypes
from .base import BaseApp as _BaseApp


class TuneCorrApp(_BaseApp):
    """Main application for handling tune correction."""

    _optics_param = 'tune'

    def __init__(self, acc):
        """Class constructor."""
        super().__init__(acc)

        # consts
        self._delta_tunex = 0.0
        self._delta_tuney = 0.0

        self._set_new_refkl_cmd_count = 0

        if self._acc == 'SI':
            self._meas_config_dkl_qf = 0.020
            self._meas_config_dkl_qd = 0.020

        # Connect to Quadrupoles Families
        self._psfam_refkl = {fam: 0 for fam in self._psfams}
        self._lastcalc_deltakl = {fam: 0 for fam in self._psfams}
        for fam in self._psfams:
            pvname = _SiriusPVName(self._acc+'-Fam:PS-'+fam+':KL-RB')
            pvname = pvname.substitute(prefix=_vaca_prefix)
            self._psfam_intstr_rb_pvs[fam] = _PV(
                pvname,
                callback=[self._callback_init_refkl,
                          self._callback_estimate_deltatune],
                connection_timeout=0.05)

        self.map_pv2write.update({
            'DeltaTuneX-SP': self.set_dtune_x,
            'DeltaTuneY-SP': self.set_dtune_y,
            'SetNewRefKL-Cmd': self.cmd_set_newref,
            'MeasConfigDeltaKLFamQF-SP': self.set_meas_config_dkl_qf,
            'MeasConfigDeltaKLFamQD-SP': self.set_meas_config_dkl_qd,
        })

    def update_corrparams_pvs(self):
        """Set initial correction parameters PVs values."""
        self.run_callbacks('RespMat-Mon', self._nominal_matrix)
        self.run_callbacks('NominalKL-Mon', self._psfam_nom_intstr)

    # ------ handle pv write methods -------

    def set_dtune_x(self, value):
        """Set DeltaTuneX."""
        self._delta_tunex = value
        self.run_callbacks('DeltaTuneX-RB', value)
        self._calc_intstrength()
        return True

    def set_dtune_y(self, value):
        """Set DeltaTuneY."""
        self._delta_tuney = value
        self.run_callbacks('DeltaTuneY-RB', value)
        self._calc_intstrength()
        return True

    def cmd_set_newref(self, value):
        """SetNewRefKL command."""
        if self._update_ref():
            self._set_new_refkl_cmd_count += 1
            self.run_callbacks(
                'SetNewRefKL-Cmd', self._set_new_refkl_cmd_count)
        return False

    def set_meas_config_dkl_qf(self, value):
        """Set MeasConfigDeltaKLFamQF."""
        if value == self._meas_config_dkl_qf:
            return False
        self._meas_config_dkl_qf = value
        self.run_callbacks('MeasConfigDeltaKLFamQF-RB', value)
        return True

    def set_meas_config_dkl_qd(self, value):
        """Set MeasConfigDeltaKLFamQD."""
        if value == self._meas_config_dkl_qd:
            return False
        self._meas_config_dkl_qd = value
        self.run_callbacks('MeasConfigDeltaKLFamQD-RB', value)
        return True

    # ---------- auxiliar methods ----------

    def _handle_corrparams_2_read(self, params):
        """Edit correction params."""
        nom_matrix = [item for sublist in params['matrix'] for item in sublist]
        nom_kl = params['nominal KLs']
        nom_deltakl = [0.0, 0.0]
        return nom_matrix, nom_kl, nom_deltakl

    def _handle_corrparams_2_save(self):
        matrix = _np.array(self._nominal_matrix)
        matrix = _np.reshape(matrix, [2, len(self._psfams)])

        value = {'matrix': matrix,
                 'nominal KLs': self._psfam_nom_intstr}
        return value

    def _calc_intstrength(self):
        method = 0 \
            if self._corr_method == _Const.CorrMeth.Proportional \
            else 1
        grouping = '2knobs' \
            if self._corr_group == _Const.CorrGroup.TwoKnobs \
            else 'svd'
        lastcalc_deltakl = self._opticscorr.calculate_delta_intstrengths(
            method=method, grouping=grouping,
            delta_opticsparam=[self._delta_tunex, self._delta_tuney])

        self.run_callbacks('Log-Mon', 'Calculated KL values.')

        for fam_idx, fam in enumerate(self._psfams):
            self._lastcalc_deltakl[fam] = lastcalc_deltakl[fam_idx]
            self.run_callbacks(
                'DeltaKL'+fam+'-Mon', self._lastcalc_deltakl[fam])

    def _apply_corr(self):
        if self._is_status_ok():
            kls = {fam: self._psfam_refkl[fam]+self._lastcalc_deltakl[fam]
                   for fam in self._psfams}
            self._apply_intstrength(kls)
            self.run_callbacks('Log-Mon', 'Applied correction.')

            if self._sync_corr == _Const.SyncCorr.On:
                self._event_exttrig_cmd.put(0)
                self.run_callbacks('Log-Mon', 'Generated trigger.')
            return True

        self.run_callbacks('Log-Mon', 'ERR: ApplyDelta-Cmd failed.')
        return False

    def _get_optics_param(self):
        """Return optics parameter."""
        return self._get_tunes()

    def _get_delta_intstrength(self, fam):
        """Get delta to apply in each family."""
        if 'QF' in fam:
            deltakl = self._meas_config_dkl_qf
        else:
            deltakl = self._meas_config_dkl_qd
        fam_idx = self._psfams.index(fam)
        nelm = self._psfam_nelm[fam_idx]
        return deltakl/nelm

    def _update_ref(self):
        if (self._status & 0x1) == 0:  # Check connection
            # update references
            for fam in self._psfams:
                value = self._psfam_intstr_rb_pvs[fam].get()
                if value is None:
                    self.run_callbacks(
                        'Log-Mon',
                        'ERR: Received a None value from {}.'.format(fam))
                    return False
                self._psfam_refkl[fam] = value
                self.run_callbacks(
                    'RefKL' + fam + '-Mon', self._psfam_refkl[fam])

                self._lastcalc_deltakl[fam] = 0
                self.run_callbacks('DeltaKL' + fam + '-Mon', 0)

            # the deltas from new kl references are zero
            self._delta_tunex = 0
            self._delta_tuney = 0
            self.run_callbacks('DeltaTuneX-SP', self._delta_tunex)
            self.run_callbacks('DeltaTuneX-RB', self._delta_tunex)
            self.run_callbacks('DeltaTuneY-SP', self._delta_tuney)
            self.run_callbacks('DeltaTuneY-RB', self._delta_tuney)

            self._estimate_current_deltatune()

            self.run_callbacks('Log-Mon', 'Updated KL references.')
            return True

        self.run_callbacks(
            'Log-Mon', 'ERR: Some magnet family is disconnected.')
        return False

    def _estimate_current_deltatune(self):
        psfam_deltakl = len(self._psfams)*[0]
        for fam_idx, fam in enumerate(self._psfams):
            psfam_deltakl[fam_idx] = \
                self._psfam_intstr_rb[fam] - self._psfam_refkl[fam]
        self._optprm_est = self._opticscorr.calculate_opticsparam(
            psfam_deltakl)
        self.run_callbacks('DeltaTuneX-Mon', self._optprm_est[0])
        self.run_callbacks('DeltaTuneY-Mon', self._optprm_est[1])

    # ---------- callbacks ----------

    def _callback_init_refkl(self, pvname, value, cb_info, **kws):
        """Initialize RefKL-Mon pvs and remove this callback."""
        # Get reference
        if value is None:
            return
        fam = _SiriusPVName(pvname).dev
        self._psfam_refkl[fam] = value
        self.run_callbacks('RefKL'+fam+'-Mon', self._psfam_refkl[fam])

        # Remove callback
        cb_info[1].remove_callback(cb_info[0])

    def _callback_estimate_deltatune(self, pvname, value, **kws):
        if value is None:
            return
        fam = _SiriusPVName(pvname).dev
        self._psfam_intstr_rb[fam] = value
        self._estimate_current_deltatune()


class SITuneCorrApp(TuneCorrApp):
    """Main application for handling SI tune correction and feedback."""

    def __init__(self):
        """Class constructor."""
        super().__init__(acc='SI')

        zer = _np.zeros(2, dtype=float)
        self._pid_errs = [zer, zer.copy(), zer.copy()]
        self._pid_gains = dict(
            x=dict(kp=0.7, ki=0.2, kd=0.1),
            y=dict(kp=0.7, ki=0.2, kd=0.1),
        )
        self._loop_state = _Const.LoopState.Open
        self._loop_state_lastsp = _Const.LoopState.Open
        self._loop_freq = 3.0
        self._thread_loopstate = None
        self._abort_thread = False

        self.map_pv2write.update({
            'LoopState-Sel': self.set_loop_state,
            'LoopFreq-SP': self.set_loop_freq,
            'LoopPIDKpX-SP': _part(self.set_pid_gain, "kp", "x"),
            'LoopPIDKiX-SP': _part(self.set_pid_gain, "ki", "x"),
            'LoopPIDKdX-SP': _part(self.set_pid_gain, "kd", "x"),
            'LoopPIDKpY-SP': _part(self.set_pid_gain, "kp", "y"),
            'LoopPIDKiY-SP': _part(self.set_pid_gain, "ki", "y"),
            'LoopPIDKdY-SP': _part(self.set_pid_gain, "kd", "y"),
        })

    def set_loop_freq(self, value):
        """Set loop frequency."""
        self._loop_freq = float(value)
        self.run_callbacks('LoopFreq-RB', float(value))
        return True

    def set_loop_state(self, value, abort=False):
        """Set loop state."""
        if not 0 <= value < len(_ETypes.OPEN_CLOSED):
            self._update_log('ERR: Invalid loop state.')
            return False

        self._loop_state_lastsp = value
        # if value:
        #     if not self.havebeam:
        #         self._update_log('ERR:Do not have stored beam. Aborted.')
        #         return False
        #     if _np.any([pvo.value for pvo in self._intlk_pvs]):
        #         self._update_log('ERR:Reset interlocks before closing')
        #         self._update_log('ERR:the loop.')
        #         return False

        if self._thread_loopstate is not None and \
                self._thread_loopstate.is_alive():
            self._update_log('WARN:Interrupting Loop Enable thread...')
            self._abort_thread = True
            self._thread_loopstate.join()

        self._thread_loopstate = _epics.ca.CAThread(
            target=self._thread_set_loop_state,
            args=[value, abort], daemon=True)
        self._thread_loopstate.start()
        return True

    def _thread_set_loop_state(self, value, abort):
        if value:  # closing the loop
            # # set gains to zero, recalculate gains and coeffs
            # self._update_log('Setting Loop Gain to zero...')
            # self._loop_gain_mon_h, self._loop_gain_mon_v = 0, 0
            # self._calc_corrs_coeffs(log=False)
            # # set and wait corrector gains and coeffs to zero
            # if not self._set_corrs_coeffs(log=False):
            #     return
            # self._update_log('Waiting for coefficients and gains...')
            # if not self._wait_coeffs_and_gains():
            #     self.run_callbacks('LoopState-Sel', self._loop_state)
            #     return

            if self._check_abort_thread():
                return

            # close the loop
            self._update_log('Closing the loop...')
            self._loop_state = value
            # if not self._check_set_corrs_opmode():
            #     self._loop_state = self._const.LoopState.Open
            #     self.run_callbacks('LoopState-Sel', self._loop_state)
            #     return
            self.run_callbacks('LoopState-Sts', self._loop_state)
            self._update_log('Loop closed.')
            # if self._check_abort_thread():
            #     return

            # # do ramp up
            # self._update_log('...done. Starting Loop Gain ramp up...')
            # if self._do_loop_gain_ramp(ramp='up'):
            #     self._update_log('LoopGain ramp up finished!')

        else:  # opening the loop
            # # do ramp down
            # self._update_log('Starting Loop Gain ramp down...')
            # if self._do_loop_gain_ramp(ramp='down', abort=abort):
            #     self._update_log('Loop Gain ramp down finished!')

            # if self._check_abort_thread():
            #     return

            # open the loop
            self._update_log('Opening the loop...')
            self._loop_state = value
            # self._check_set_corrs_opmode()
            self.run_callbacks('LoopState-Sts', self._loop_state)
            self._update_log('Loop opened.')

    def _check_abort_thread(self):
        if self._abort_thread:
            self._update_log('WARN:Loop state thread aborted.')
            self._abort_thread = False
            return True
        return False

    def set_pid_gain(self, kparam, plane, value):
        """."""
        kparam = kparam.lower()
        plane = plane.lower()
        self._pid_gains[plane][kparam] = float(value)
        self.run_callbacks(
            "LoopPID" + kparam.title() + plane.upper() + "-RB", float(value)
        )
        return True

    def update_corrparams_pvs(self):
        """Set initial correction parameters PVs values."""
        super().update_corrparams_pvs()
        self.run_callbacks('LoopState-Sel', self._loop_state)
        self.run_callbacks('LoopState-Sts', self._loop_state)
        self.run_callbacks('LoopFreq-SP', self._loop_freq)
        self.run_callbacks('LoopFreq-RB', self._loop_freq)
        self.run_callbacks('FakeTune-Mon', 0.0)
        self.run_callbacks('LoopPIDKpX-SP', self._pid_gains['x']['kp'])
        self.run_callbacks('LoopPIDKiX-SP', self._pid_gains['x']['ki'])
        self.run_callbacks('LoopPIDKdX-SP', self._pid_gains['x']['kd'])
        self.run_callbacks('LoopPIDKpY-SP', self._pid_gains['y']['kp'])
        self.run_callbacks('LoopPIDKiY-SP', self._pid_gains['y']['ki'])
        self.run_callbacks('LoopPIDKdY-SP', self._pid_gains['y']['kd'])
        self.run_callbacks('LoopPIDKpX-RB', self._pid_gains['x']['kp'])
        self.run_callbacks('LoopPIDKiX-RB', self._pid_gains['x']['ki'])
        self.run_callbacks('LoopPIDKdX-RB', self._pid_gains['x']['kd'])
        self.run_callbacks('LoopPIDKpY-RB', self._pid_gains['y']['kp'])
        self.run_callbacks('LoopPIDKiY-RB', self._pid_gains['y']['ki'])
        self.run_callbacks('LoopPIDKdY-RB', self._pid_gains['y']['kd'])

    def process(self, interval):
        """."""
        _t0 = _time()
        self.run_callbacks(
            'FakeTune-Mon',
            float(str(_t0)[-3:]) * 1e-4
        )
        dtime = _time() - _t0
        sleep_time = interval - dtime
        if sleep_time > 0:
            super().process(sleep_time)

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
