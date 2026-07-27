"""Main module of AS-AP-TuneCorr IOC."""

import numpy as _np
from epics import PV as _PV
from epics.ca import CAThread as _Thread

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

        self._inloop = False  # needed for the SI Tune Feedback

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
        if self._inloop:
            msg = "ERR: Cant set DeltaTuneX while the feedback loop is closed."
            self.run_callbacks('Log-Mon', msg)
            return False
        self._delta_tunex = value
        self.run_callbacks('DeltaTuneX-RB', value)
        self._calc_intstrength()
        return True

    def set_dtune_y(self, value):
        """Set DeltaTuneY."""
        if self._inloop:
            msg = "ERR: Cant set DeltaTuneY while the feedback loop is closed."
            self.run_callbacks('Log-Mon', msg)
            return False
        self._delta_tuney = value
        self.run_callbacks('DeltaTuneY-RB', value)
        self._calc_intstrength()
        return True

    def cmd_set_newref(self, value):
        """SetNewRefKL command."""
        if self._inloop:
            msg = "ERR: Cant update ref. while the feedback loop is closed."
            self.run_callbacks('Log-Mon', msg)
            return False
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

        if not self._inloop:
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
            if not self._inloop:
                self.run_callbacks('Log-Mon', 'Applied correction.')

            if self._sync_corr == _Const.SyncCorr.On:
                self._event_exttrig_cmd.put(0)
                if not self._inloop:
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

            if not self._inloop:
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

        self._loop_state = _Const.LoopState.Open
        self._loop_state_lastsp = _Const.LoopState.Open
        self._loop_freq = 3.0

        self._tune_source = _Const.TuneSource.TuneSpec

        self._max_tune_err = 0.02
        self._ref_tunex = 0.16
        self._ref_tuney = 0.22

        self._pid_errs = None  # created when feedback thread starts
        self._pid_gains = dict(kp=0.0, ki=3.0, kd=0.0)
        self._thread_fb = None

        self.map_pv2write.update({
            'LoopState-Sel': self.set_loop_state,
            'LoopFreq-SP': self.set_loop_freq,
            'TuneSource-Sel': self.set_tune_source,
            'RefTuneX-SP': _part(self.set_ref_tune, "x"),
            'RefTuneY-SP': _part(self.set_ref_tune, "y"),
            'MaxTuneErr-SP': self.set_max_tune_err,
            'LoopPIDKp-SP': _part(self.set_pid_gain, "kp"),
            'LoopPIDKi-SP': _part(self.set_pid_gain, "ki"),
            'LoopPIDKd-SP': _part(self.set_pid_gain, "kd"),
        })

        self._storedebeam_pv.add_callback(self._loop_checkbeam)

    # --- set methods ---
    def set_loop_state(self, value):
        """Set loop state."""
        if not 0 <= value < len(_ETypes.OPEN_CLOSED):
            msg = "ERR: Invalid loop state."
            self._update_log(msg)
            return False
        if value == _Const.LoopState.Closed:
            if self._loop_state == _Const.LoopState.Closed:
                msg = "ERR: Loop is Already closed."
                self._update_log(msg)
                return False
            if value and not self._is_storedebeam:
                msg = "ERR: Do not have stored beam. Aborted."
                self._update_log(msg)
                return False
            if self._thread_fb and self._thread_fb.is_alive():
                msg = 'ERR: Wait the feedback loop to open.'
                self._update_log(msg)
                return False
            msg = "Closing the Loop."
            self._update_log(msg)
            self._loop_state = value
            self._inloop = True
            self._thread_fb = _Thread(target=self._do_auto_corr, daemon=True)
            self._thread_fb.start()
        elif value == _Const.LoopState.Open:
            msg = "Opening the Loop."
            self._update_log(msg)
            self._loop_state = value
            self._inloop = False
        return True

    def set_loop_freq(self, value):
        """Set loop frequency."""
        self._loop_freq = float(value)
        self.run_callbacks('LoopFreq-RB', float(value))
        return True

    def set_tune_source(self, value):
        """Set tune source."""
        if self._loop_state == _Const.LoopState.Closed:
            msg = "ERR: Cannot change tune source while the loop is closed."
            self._update_log(msg)
            return False
        if not 0 <= value < len(_ETypes.TUNE_SOURCE):
            msg = "ERR: Invalid tune source."
            self._update_log(msg)
            return False
        self._tune_source = value
        pvnames = _ETypes.TUNE_SOURCE_PVS[self._tune_source]
        pvx, pvy = _SiriusPVName(pvnames[0]), _SiriusPVName(pvnames[1])
        self._tune_x_pv = _PV(
            pvx.substitute(prefix=_vaca_prefix),
            connection_timeout=0.3
        )
        self._tune_y_pv = _PV(
            pvy.substitute(prefix=_vaca_prefix),
            connection_timeout=0.3
        )
        msg = "INFO: Tune PVs {}!"
        status = "connected" if all(
            [self._tune_x_pv.connected, self._tune_y_pv.connected]
        ) else "not connected"
        self._update_log(msg.format(status))
        self.run_callbacks('TuneSourcePVList-Mon', (pvx, pvy))
        self.run_callbacks('TuneSource-Sts', value)
        return True

    def set_ref_tune(self, plane, value):
        """."""
        plane = plane.upper()
        if plane == 'X':
            self._ref_tunex = float(value)
        elif plane == 'Y':
            self._ref_tuney = float(value)
        else:
            return False
        self.run_callbacks('RefTune'+plane+'-RB', float(value))
        return True

    def set_max_tune_err(self, value):
        """Set max tune error."""
        self._max_tune_err = float(value)
        self.run_callbacks('MaxTuneErr-RB', float(value))
        return True

    def set_pid_gain(self, kparam, value):
        """."""
        kparam = kparam.lower()
        self._pid_gains[kparam] = float(value)
        self.run_callbacks("LoopPID" + kparam.title() + "-RB", float(value))
        return True

    # --- pv initialization ---
    def update_corrparams_pvs(self):
        """Set initial correction parameters PVs values."""
        super().update_corrparams_pvs()

        self.run_callbacks('LoopState-Sel', self._loop_state)
        self.run_callbacks('LoopState-Sts', self._loop_state)

        self.run_callbacks('LoopFreq-SP', self._loop_freq)
        self.run_callbacks('LoopFreq-RB', self._loop_freq)

        self.run_callbacks('LoopPIDKp-SP', self._pid_gains['kp'])
        self.run_callbacks('LoopPIDKp-RB', self._pid_gains['kp'])
        self.run_callbacks('LoopPIDKi-SP', self._pid_gains['ki'])
        self.run_callbacks('LoopPIDKi-RB', self._pid_gains['ki'])
        self.run_callbacks('LoopPIDKd-SP', self._pid_gains['kd'])
        self.run_callbacks('LoopPIDKd-RB', self._pid_gains['kd'])

        self.run_callbacks('RefTuneX-SP', self._ref_tunex)
        self.run_callbacks('RefTuneX-RB', self._ref_tunex)

        self.run_callbacks('RefTuneY-SP', self._ref_tuney)
        self.run_callbacks('RefTuneY-RB', self._ref_tuney)

        self.run_callbacks('MaxTuneErr-SP', self._max_tune_err)
        self.run_callbacks('MaxTuneErr-RB', self._max_tune_err)

        self.run_callbacks('TuneSource-Sel', self._tune_source)
        self.run_callbacks('TuneSource-Sts', self._tune_source)
        self.run_callbacks(
            'TuneSourcePVList-Mon',
            _ETypes.TUNE_SOURCE_PVS[self._tune_source]
        )

        self.run_callbacks('CorrGroup-Sts', self._corr_group)  # ? needed?
        self.run_callbacks('CorrGroup-Sel', self._corr_group)  # ? needed?
        self.run_callbacks('CorrMeth-Sts', self._corr_method)  # ? needed?
        self.run_callbacks('CorrMeth-Sel', self._corr_method)  # ? needed?

    # --- feedback methods ---
    def _do_auto_corr(self):
        """."""
        self.run_callbacks("LoopState-Sts", _Const.LoopState.Closed)

        self._update_ref()
        zer = _np.zeros(len(self._psfams), dtype=float)
        self._pid_errs = [zer, zer.copy(), zer.copy()]

        while self._loop_state == _Const.LoopState.Closed:
            tplanned = 1.0/self._loop_freq
            _t0 = _time()

            sts, (tunex, tuney) = self._get_tunes()
            if not sts:
                break

            if not self._check_tunes(tunex, tuney):
                break

            self._process_pid()

            sts = self._apply_corr()
            if not sts:
                self._update_log('ERR: Could not apply the correction.')
                self._do_sleep(_t0, tplanned)
                continue

            self._do_sleep(_t0, tplanned)

        if self._loop_state == _Const.LoopState.Closed:
            self._loop_state = _Const.LoopState.Open
            self.run_callbacks("LoopState-Sel", _Const.LoopState.Open)

        msg = "Loop opened!"
        self._update_log(msg)
        self._update_ref()
        self.run_callbacks("LoopState-Sts", _Const.LoopState.Open)

    def _process_pid(self, tunex, tuney):
        self._delta_tunex = self._ref_tunex - tunex
        self._delta_tuney = self._ref_tuney - tuney

        delta_kl_prev = _np.array([
            self._lastcalc_deltakl[fam] for fam in self._psfams
        ])

        self._calc_intstrength()

        e0 = _np.array([self._lastcalc_deltakl[fam] for fam in self._psfams])
        e1 = self._pid_errs[-1]
        e2 = self._pid_errs[-2]

        interval = 1.0 / self._loop_freq

        kp = self._pid_gains['kp']
        ki = self._pid_gains['ki'] * interval
        kd = self._pid_gains['kd'] / interval

        a0 = kp + ki + kd
        a1 = -kp - 2*kd
        a2 = kd

        delta_kl = delta_kl_prev + a0*e0 + a1*e1 + a2*e2
        for i, fam in enumerate(self._psfams):
            self._lastcalc_deltakl[fam] = delta_kl[i]

        self._pid_errs.append(e0)
        del self._pid_errs[0]

    # --- auxiliar methods ---
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

    def _loop_checkbeam(self, pvname, value, **kws):
        _ = (pvname, kws)
        if not value and self._loop_state == _Const.LoopState.Closed:
            self._update_log('FATAL: Opening Tune Feedback loop...')
            self._loop_state = _Const.LoopState.Open
            self._inloop = False

    def _get_tunes(self):  # overload (from BaseApp)
        tunex, tuney = 0.0, 0.0
        sts = bool(self._tune_x_pv.connected)
        if sts:
            tunex = self._tune_x_pv.value
        sts &= self._tune_y_pv.connected
        if sts:
            tuney = self._tune_y_pv.value
        if not sts:
            self._update_log('ERR: Could not get the tunes!')
        return sts, (tunex, tuney)

    def _check_tunes(self, tunex, tuney):
        sts = self._check_tunes_reliability(tunex, tuney)
        sts &= self._check_tunes_distortion(tunex, tuney)
        return sts

    def _check_tunes_reliability(self, tunex, tuney):
        _ = (tunex, tuney)
        return True

    def _check_tunes_distortion(self, tunex, tuney):
        stsx_ok = abs(tunex - self._ref_tunex) <= self._max_tune_err
        if not stsx_ok:
            self._update_log('WARN: Tune X is out of range.')
        stsy_ok = abs(tuney - self._ref_tuney) <= self._max_tune_err
        if not stsy_ok:
            self._update_log('WARN: Tune Y is out of range.')
        return stsx_ok and stsy_ok

    def _do_sleep(self, time0, tplanned, do_warn=True):
        ttook = _time() - time0
        tsleep = tplanned - ttook
        if tsleep > 0:
            _sleep(tsleep)
        elif do_warn:
            strf = (
                f'Feedback step took more than planned... '
                f'{ttook:.3f}/{tplanned:.3f} s')
            _log.warning(strf)
