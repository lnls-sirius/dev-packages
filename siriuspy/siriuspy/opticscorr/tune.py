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

    _DEF_CONN_TIMEOUT_PSFAM = 0.05  # [s]

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
                connection_timeout=TuneCorrApp._DEF_CONN_TIMEOUT_PSFAM)

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
        if self._loop_state == _Const.LoopState.Closed:
            msg = "ERR: Cant set DeltaTuneX while the feedback loop is closed."
            self.run_callbacks('Log-Mon', msg)
            return False
        self._delta_tunex = value
        self.run_callbacks('DeltaTuneX-RB', value)
        self._calc_intstrength()
        return True

    def set_dtune_y(self, value):
        """Set DeltaTuneY."""
        if self._loop_state == _Const.LoopState.Closed:
            msg = "ERR: Cant set DeltaTuneY while the feedback loop is closed."
            self.run_callbacks('Log-Mon', msg)
            return False
        self._delta_tuney = value
        self.run_callbacks('DeltaTuneY-RB', value)
        self._calc_intstrength()
        return True

    def cmd_set_newref(self, value):
        """SetNewRefKL command."""
        if self._loop_state == _Const.LoopState.Closed:
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

        if self._loop_state == _Const.LoopState.Open:
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

            if self._loop_state == _Const.LoopState.Open:
                self.run_callbacks('Log-Mon', 'Applied correction.')

            if self._sync_corr == _Const.SyncCorr.On:
                self._event_exttrig_cmd.put(0)
                if self._loop_state == _Const.LoopState.Open:
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

    _DEF_CONN_TIMEOUT_TUNE = 0.3  # [s]

    def __init__(self):
        """Class constructor."""
        super().__init__(acc='SI')

        self._loop_state = _Const.DEF_LOOPSTATE
        self._loop_freq = _Const.DEF_LOOPFREQ

        self._tunex_source = _Const.DEF_TUNESRC
        self._tuney_source = _Const.DEF_TUNESRC

        self._max_tunex_err = _Const.DEF_MAX_TUNE_ERR
        self._max_tuney_err = _Const.DEF_MAX_TUNE_ERR

        self._ref_tunex = _Const.DEF_REF_TUNEX
        self._ref_tuney = _Const.DEF_REF_TUNEY

        self._pid_errs = None  # created when feedback thread starts
        self._pid_gains = dict(
            x=dict(
                kp=_Const.DEF_PID_KP,
                ki=_Const.DEF_PID_KI,
                kd=_Const.DEF_PID_KD,
            ),
            y=dict(
                kp=_Const.DEF_PID_KP,
                ki=_Const.DEF_PID_KI,
                kd=_Const.DEF_PID_KD,
            ),
        )
        self._thread_fb = None

        self.map_pv2write.update({
            'LoopState-Sel': self.set_loop_state,
            'LoopFreq-SP': self.set_loop_freq,
            'TuneXSrc-Sel': _part(self.set_tune_source, "x"),
            'TuneYSrc-Sel': _part(self.set_tune_source, "y"),
            'RefTuneX-SP': _part(self.set_ref_tune, "x"),
            'RefTuneY-SP': _part(self.set_ref_tune, "y"),
            'MaxTuneXErr-SP': _part(self.set_max_tune_err, "x"),
            'MaxTuneYErr-SP': _part(self.set_max_tune_err, "y"),
            'LoopPIDKpX-SP': _part(self.set_pid_gain, "x", "kp"),
            'LoopPIDKiX-SP': _part(self.set_pid_gain, "x", "ki"),
            'LoopPIDKdX-SP': _part(self.set_pid_gain, "x", "kd"),
            'LoopPIDKpY-SP': _part(self.set_pid_gain, "y", "kp"),
            'LoopPIDKiY-SP': _part(self.set_pid_gain, "y", "ki"),
            'LoopPIDKdY-SP': _part(self.set_pid_gain, "y", "kd"),
        })

        self._tune_x_pv.add_callback(_part(self._callback_update_tunes, 'x'))
        self._tune_y_pv.add_callback(_part(self._callback_update_tunes, 'y'))

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
            self._thread_fb = _Thread(target=self._do_auto_corr, daemon=True)
            self._thread_fb.start()
        elif value == _Const.LoopState.Open:
            msg = "Opening the Loop."
            self._update_log(msg)
            self._loop_state = value
        return True

    def set_loop_freq(self, value):
        """Set loop frequency."""
        self._loop_freq = float(value)
        self.run_callbacks('LoopFreq-RB', float(value))
        return True

    def set_tune_source(self, plane, value):
        """Set tune source."""
        if self._loop_state == _Const.LoopState.Closed:
            msg = "ERR: Can\'t change tune source while the feedback is on."
            self._update_log(msg)
            return False
        if not 0 <= value < len(_ETypes.TUNE_SRC):
            msg = "ERR: Invalid tune source."
            self._update_log(msg)
            return False
        plane = plane.upper()
        pln_idx = None
        if plane == 'X':
            self._tunex_source = value
            pln_idx = 0
        elif plane == 'Y':
            self._tuney_source = value
            pln_idx = 1
        else:
            self._update_log("ERR: Invalid plane.")
            return False
        pv = _SiriusPVName(_ETypes.TUNE_SRC_PVS[value][pln_idx])
        if plane == 'X':
            self._tune_x_pv.clear_callbacks()
            self._tune_x_pv = _PV(
                pv.substitute(prefix=_vaca_prefix),
                connection_timeout=SITuneCorrApp._DEF_CONN_TIMEOUT_TUNE,
                auto_monitor=True,
                callback=_part(self._callback_update_tunes, 'x')
            )
        elif plane == 'Y':
            self._tune_y_pv.clear_callbacks()
            self._tune_y_pv = _PV(
                pv.substitute(prefix=_vaca_prefix),
                connection_timeout=SITuneCorrApp._DEF_CONN_TIMEOUT_TUNE,
                auto_monitor=True,
                callback=_part(self._callback_update_tunes, 'y')
            )
        self.run_callbacks('TuneSrcPVList-Mon', (
            self._tune_x_pv.pvname.substitute(prefix=''),
            self._tune_y_pv.pvname.substitute(prefix='')
        ))
        self.run_callbacks('Tune' + plane + 'Src-Sts', value)
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

    def set_max_tune_err(self, plane, value):
        """Set max tune error."""
        plane = plane.upper()
        if plane == 'X':
            self._max_tunex_err = float(value)
            self.run_callbacks('MaxTuneXErr-RB', float(value))
        elif plane == 'Y':
            self._max_tuney_err = float(value)
            self.run_callbacks('MaxTuneYErr-RB', float(value))
        return True

    def set_pid_gain(self, plane, kparam, value):
        """."""
        plane = plane.lower()
        kparam = kparam.lower()
        self._pid_gains[plane][kparam] = float(value)
        self.run_callbacks(
            "LoopPID" + kparam.title() + plane.upper() + "-RB", float(value)
        )
        return True

    # --- pv initialization ---
    def update_corrparams_pvs(self):
        """Set initial correction parameters PVs values."""
        super().update_corrparams_pvs()

        self.run_callbacks('LoopState-Sel', self._loop_state)
        self.run_callbacks('LoopState-Sts', self._loop_state)

        self.run_callbacks('LoopFreq-SP', self._loop_freq)
        self.run_callbacks('LoopFreq-RB', self._loop_freq)

        self.run_callbacks('LoopPIDKpX-SP', self._pid_gains['x']['kp'])
        self.run_callbacks('LoopPIDKpX-RB', self._pid_gains['x']['kp'])
        self.run_callbacks('LoopPIDKiX-SP', self._pid_gains['x']['ki'])
        self.run_callbacks('LoopPIDKiX-RB', self._pid_gains['x']['ki'])
        self.run_callbacks('LoopPIDKdX-SP', self._pid_gains['x']['kd'])
        self.run_callbacks('LoopPIDKdX-RB', self._pid_gains['x']['kd'])

        self.run_callbacks('LoopPIDKpY-SP', self._pid_gains['y']['kp'])
        self.run_callbacks('LoopPIDKpY-RB', self._pid_gains['y']['kp'])
        self.run_callbacks('LoopPIDKiY-SP', self._pid_gains['y']['ki'])
        self.run_callbacks('LoopPIDKiY-RB', self._pid_gains['y']['ki'])
        self.run_callbacks('LoopPIDKdY-SP', self._pid_gains['y']['kd'])
        self.run_callbacks('LoopPIDKdY-RB', self._pid_gains['y']['kd'])

        self.run_callbacks('RefTuneX-SP', self._ref_tunex)
        self.run_callbacks('RefTuneX-RB', self._ref_tunex)

        self.run_callbacks('RefTuneY-SP', self._ref_tuney)
        self.run_callbacks('RefTuneY-RB', self._ref_tuney)

        self.run_callbacks('MaxTuneXErr-SP', self._max_tunex_err)
        self.run_callbacks('MaxTuneXErr-RB', self._max_tunex_err)
        self.run_callbacks('MaxTuneYErr-SP', self._max_tuney_err)
        self.run_callbacks('MaxTuneYErr-RB', self._max_tuney_err)

        self.run_callbacks('TuneXSrc-Sel', self._tunex_source)
        self.run_callbacks('TuneXSrc-Sts', self._tunex_source)
        self.run_callbacks('TuneYSrc-Sel', self._tuney_source)
        self.run_callbacks('TuneYSrc-Sts', self._tuney_source)
        self.run_callbacks(
            'TuneSrcPVList-Mon',
            _ETypes.TUNE_SRC_PVS[self._tune_source]
        )

        self.run_callbacks('CorrGroup-Sts', self._corr_group)  # ? needed?
        self.run_callbacks('CorrGroup-Sel', self._corr_group)  # ? needed?
        self.run_callbacks('CorrMeth-Sts', self._corr_method)  # ? needed?
        self.run_callbacks('CorrMeth-Sel', self._corr_method)  # ? needed?

    # --- feedback methods ---
    def _do_auto_corr(self):
        """."""
        self._update_ref()
        self.run_callbacks("LoopState-Sts", _Const.LoopState.Closed)
        msg = "Loop closed!"
        self._update_log(msg)
        zer = _np.zeros(2, dtype=float)
        self._pid_errs = [zer, zer.copy(), zer.copy()]

        while self._loop_state == _Const.LoopState.Closed:
            tplanned = 1.0/self._loop_freq
            _t0 = _time()

            if not self._is_storedebeam:
                self._update_log('ERR: We do not have stored beam!')
                break

            sts, (tunex, tuney) = self._get_tunes()
            if not sts:
                break

            if not self._check_tunes(tunex, tuney):
                break

            self._process_pid(tunex, tuney)

            sts = self._apply_corr()
            if not sts:
                self._update_log('ERR: Could not apply the correction.')
                break

            self._do_sleep(_t0, tplanned)

        if self._loop_state == _Const.LoopState.Closed:
            self._loop_state = _Const.LoopState.Open
            self.run_callbacks("LoopState-Sel", _Const.LoopState.Open)

        msg = "Loop opened!"
        self._update_log(msg)
        self._update_ref()
        self.run_callbacks("LoopState-Sts", _Const.LoopState.Open)

    def _process_pid(self, tunex, tuney):
        e0 = _np.array([self._ref_tunex - tunex, self._ref_tuney - tuney])
        e1 = self._pid_errs[-1]
        e2 = self._pid_errs[-2]

        interval = 1.0 / self._loop_freq

        kpx = self._pid_gains['x']['kp']
        kix = self._pid_gains['x']['ki'] * interval
        kdx = self._pid_gains['x']['kd'] / interval

        kpy = self._pid_gains['y']['kp']
        kiy = self._pid_gains['y']['ki'] * interval
        kdy = self._pid_gains['y']['kd'] / interval

        a0x = kpx + kix + kdx
        a1x = -kpx - 2*kdx
        a2x = kdx

        a0y = kpy + kiy + kdy
        a1y = -kpy - 2*kdy
        a2y = kdy

        self._delta_tunex += a0x*e0[0] + a1x*e1[0] + a2x*e2[0]
        self._delta_tuney += a0y*e0[1] + a1y*e1[1] + a2y*e2[1]

        self._calc_intstrength()

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

    def _callback_update_tunes(self, plane, pvname, value, **kws):
        _ = (pvname, kws)
        if plane == 'x':
            self.run_callbacks('TuneX-Mon', value)
            return True
        elif plane == 'y':
            self.run_callbacks('TuneY-Mon', value)
            return True
        return False

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
        stsx_ok = abs(tunex - self._ref_tunex) <= self._max_tunex_err
        if not stsx_ok:
            self._update_log('WARN: Tune X is out of range.')
        stsy_ok = abs(tuney - self._ref_tuney) <= self._max_tuney_err
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
