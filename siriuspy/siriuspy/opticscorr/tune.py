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

        self._inloop = False

        # kllist = [0.002312133381724278,
        #     0.005410918928783577,
        #     0.002705311841611923,
        #     -0.0032361698526480256,
        #     -0.006444951374712347,
        #     0.0005707470671369916,
        #     -0.0032225964726197813,
        #     0.00028529427813982477]

        kllist = [ 0.71463554,  1.23452484,  1.23452484, -0.22673566, -0.28094844,
       -0.47888046, -0.28094844, -0.47888046]

        self._psfam_kl = {fam: j for (fam,j) in zip(self._psfams, kllist)}

        if self._acc == 'SI':
            self._meas_config_dkl_qf = 0.020
            self._meas_config_dkl_qd = 0.020

        # Connect to Quadrupoles Families
        # self._psfam_refkl = {fam: 0 for fam in self._psfams}
        self._psfam_refkl = {fam: j for (fam,j) in zip(self._psfams, kllist)}

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
            self.run_callbacks('Log-Mon',
                'ERR:Cant set DeltaTuneX while the feedback loop is closed.')
            return False
        self._delta_tunex = value
        self.run_callbacks('DeltaTuneX-RB', value)
        self._calc_intstrength()
        return True

    def set_dtune_y(self, value):
        """Set DeltaTuneY."""
        if self._inloop:
            self.run_callbacks('Log-Mon',
                'ERR:Cant set DeltaTuneY while the feedback loop is closed.')
            return False
        self._delta_tuney = value
        self.run_callbacks('DeltaTuneY-RB', value)
        self._calc_intstrength()
        return True

    def cmd_set_newref(self, value):
        """SetNewRefKL command."""
        if self._update_ref() and not self._inloop:
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
            self.run_callbacks('Log-Mon', f'Calculated KL values. {self._inloop}')

        for fam_idx, fam in enumerate(self._psfams):
            self._lastcalc_deltakl[fam] = lastcalc_deltakl[fam_idx]
            self.run_callbacks(
                'DeltaKL'+fam+'-Mon', self._lastcalc_deltakl[fam])

    def _apply_corr(self):
        if True:# if self._is_status_ok():
            kls = {fam: self._psfam_kl[fam]+self._lastcalc_deltakl[fam]
                   for fam in self._psfams}
            # self._apply_intstrength(kls)
            for fam in self._psfams:
                self._psfam_kl[fam] = kls[fam]
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

        zer = _np.zeros(2, dtype=float)
        self._pid_errs = [zer, zer.copy(), zer.copy()]
        self._pid_gains = dict(
            x=dict(kp=0.7, ki=0.2, kd=0.1),
            y=dict(kp=0.7, ki=0.2, kd=0.1),
        )
        self._thread_ramp_pid_gain = None
        self._abort_thread_ramp_pid_gain = False

        self._loop_state = _Const.LoopState.Open
        self._loop_state_lastsp = _Const.LoopState.Open
        self._loop_freq = 3.0
        self._thread_loopstate = None
        self._abort_thread_loopstate = False

        self._max_tune_err = 0.02
        self._ref_tunex = 0.16
        self._ref_tuney = 0.22

        self.map_pv2write.update({
            'LoopState-Sel': self.set_loop_state,
            'LoopFreq-SP': self.set_loop_freq,

            'LoopPIDKpX-SP': _part(self.set_pid_gain, "kp", "x"),
            'LoopPIDKiX-SP': _part(self.set_pid_gain, "ki", "x"),
            'LoopPIDKdX-SP': _part(self.set_pid_gain, "kd", "x"),
            'LoopPIDKpY-SP': _part(self.set_pid_gain, "kp", "y"),
            'LoopPIDKiY-SP': _part(self.set_pid_gain, "ki", "y"),
            'LoopPIDKdY-SP': _part(self.set_pid_gain, "kd", "y"),

            'RefTuneX-SP': _part(self.set_ref_tune, "x"),
            'RefTuneY-SP': _part(self.set_ref_tune, "y"),
            'MaxTuneErr-SP': self.set_max_tune_err,

            'SimIDTuneShiftAmp-SP': self._set_faketuneshiftamp,
        })

        # self._storedebeam_pv.add_callback(
        #     self._loop_checkbeam
        # )

        self._thread_fb_quit = False
        self._thread_fb = None

        self._sim_id_tuneshift_x = []
        self._sim_id_tuneshift_y = []
        self._faketunex = 0.0
        self._faketuney = 0.0

    def _create_feedbackthread(self):
        tgt = self.feedback_loop
        return _epics.ca.CAThread(target=tgt, daemon=True)

    def set_max_tune_err(self, value):
        """Set max tune error."""
        self._max_tune_err = float(value)
        self.run_callbacks('MaxTuneErr-RB', float(value))
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

    def set_loop_freq(self, value):
        """Set loop frequency."""
        self._loop_freq = float(value)
        self.run_callbacks('LoopFreq-RB', float(value))

        self._update_log(f'--- FB thread Quit = {self._thread_fb_quit}')
        self._update_log(f'--- FB thread is None? {self._thread_fb is None}')
        if self._thread_fb is not None:
            self._update_log(
                f'--- FB thread is alive? {self._thread_fb.is_alive()}')

        return True

    def set_loop_state(self, value, abort=False):
        """Set loop state."""
        if not 0 <= value < len(_ETypes.OPEN_CLOSED):
            self._update_log('ERR: Invalid loop state.')
            return False

        self._loop_state_lastsp = value
        # if value:
        #     if not self._is_storedebeam:
        #         self._update_log('ERR: Do not have stored beam. Aborted.')
        #         return False

        if self._thread_loopstate is not None and \
                self._thread_loopstate.is_alive():
            self._update_log('WARN: Wait until Loop State is set.')
            # self._abort_thread_loopstate = True
            self._thread_loopstate.join()
            return False

        self._thread_loopstate = _epics.ca.CAThread(
            target=self._thread_set_loop_state,
            args=[value, abort], daemon=True)
        self._thread_loopstate.start()
        return True

    def _thread_set_loop_state(self, value, abort):
        if value:  # closing the loop
            self._update_log('Closing the loop...')

            # set gains to zero and ramp up

            self._update_log('Setting PID gains to zero...')
            self._inloop = False
            for g in ['x', 'y']:
                self.set_pid_gain('kp', g, 0.0)
                self.set_pid_gain('ki', g, 0.0)
                self.set_pid_gain('kd', g, 0.0)
            self._inloop = True
            _sleep(0.2)
            self._update_log('PID set to zero...')
            self._update_log('Ramping up... (fake)')
            # for g in ['x', 'y']:
            #     for k in ['kp', 'ki', 'kd']:
            #         self.set_pid_gain(k, g, self._pid_gains[g][k])
            #         if self._thread_ramp_pid_gain is not None:
            #             self._thread_ramp_pid_gain.join()

            # if self._check_abort_thread():
            #     return
            self._update_log('Ramp up complete!')

            # close the loop
            if self._thread_fb is not None:
                if self._thread_fb.is_alive():
                    self._loop_state = _Const.LoopState.Open
                    self._inloop = False
                    self._thread_fb_quit = True
                    self._thread_fb.join()
            self._thread_fb_quit = False
            self._thread_fb = self._create_feedbackthread()
            self._loop_state = value
            self._inloop = True

            _sleep(0.1)

            self._thread_fb.start()
            self.run_callbacks('LoopState-Sts', self._loop_state)
            self._update_log('Loop closed.')
            return
        else:  # opening the loop

            # do ramp down

            # open the loop
            self._update_log('Opening the loop...')
            self._inloop = False
            self._loop_state = value
            _sleep(0.1)
            self.run_callbacks('LoopState-Sts', self._loop_state)
            # self.run_callbacks('LoopState-Sel', value)
            self._update_log('Loop opened.')
            return

    def _check_abort_thread(self):
        if self._abort_thread_loopstate:
            self._update_log('WARN:Set Loop State thread aborted.')
            self._abort_thread_loopstate = False
            return True
        return False

    def _loop_checkbeam(self, value, **kws):
        if not value and self._inloop:
            self._update_log('FATAL:Opening Tune Feedback loop...')
            self.set_loop_state(self._const.LoopState.Open)

    def set_pid_gain(self, kparam, plane, value):
        """."""
        if not self._inloop:
            kparam = kparam.lower()
            plane = plane.lower()
            self._pid_gains[plane][kparam] = float(value)
            self.run_callbacks(
                "LoopPID" + kparam.title() + plane.upper() + "-RB", float(value)
            )
            return True
        self._ramp_pid_gain(kparam, plane, value)
        return True

    def _ramp_pid_gain(self, kparam, plane, value, abort=False):
        if self._thread_ramp_pid_gain is not None and \
            self._thread_ramp_pid_gain.is_alive():
            self._thread_ramp_pid_gain.join()

        self._thread_ramp_pid_gain = _epics.ca.CAThread(
            target=self._thread_ramp_pid_gain,
            args=[kparam, plane, value, abort], daemon=True)
        self._thread_ramp_pid_gain.start()
        return True

    def _thread_ramp_pid_gain(self, kparam, plane, value, abort):
        self._update_log(f'ERR: Ramping up... {kparam} {plane} {value}')
        deltapidgain = value - self._pid_gains[plane][kparam]
        max_delta_pid_gain_per_step = 0.1
        pid_gain_ramp_interval = 0.1
        while not _np.isclose(deltapidgain, 0.0):

            if abs(deltapidgain) > max_delta_pid_gain_per_step:
                deltapidgain_step = _np.sign(deltapidgain) * \
                    max_delta_pid_gain_per_step
            else:
                deltapidgain_step = deltapidgain

            self._pid_gains[plane][kparam] += deltapidgain_step
            deltapidgain -= deltapidgain_step
            self.run_callbacks(
                "LoopPID" + kparam.title() + plane.upper() + "-RB",
                self._pid_gains[plane][kparam]
            )
            _sleep(pid_gain_ramp_interval)
            self._update_log(f'WARN: {kparam} {plane} {self._pid_gains[plane][kparam]}')

    def update_corrparams_pvs(self):
        """Set initial correction parameters PVs values."""
        super().update_corrparams_pvs()
        self.run_callbacks('LoopState-Sel', self._loop_state)
        self.run_callbacks('LoopState-Sts', self._loop_state)
        self.run_callbacks('LoopFreq-SP', self._loop_freq)
        self.run_callbacks('LoopFreq-RB', self._loop_freq)
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
        self.run_callbacks('RefTuneX-SP', self._ref_tunex)
        self.run_callbacks('RefTuneY-SP', self._ref_tuney)
        self.run_callbacks('RefTuneX-RB', self._ref_tunex)
        self.run_callbacks('RefTuneY-RB', self._ref_tuney)
        self.run_callbacks('MaxTuneErr-SP', self._max_tune_err)
        self.run_callbacks('MaxTuneErr-RB', self._max_tune_err)

        self.run_callbacks('FakeTuneX-Mon', self._faketunex)
        self.run_callbacks('FakeTuneY-Mon', self._faketuney)

    def process(self, interval):
        """."""
        _t0 = _time()

        try:
            dx = self._sim_id_tuneshift_x[0]
            dy = self._sim_id_tuneshift_y[0]

            if len(self._sim_id_tuneshift_x) > 1:
                del self._sim_id_tuneshift_x[0]

            if len(self._sim_id_tuneshift_y) > 1:
                del self._sim_id_tuneshift_y[0]
        except:
            dx = 0
            dy = 0
        mat = None
        try:
            meth = self._corr_method
            gp = 'svd' if self._corr_group == 1 else '2knobs'
            mat = self._opticscorr._choose_matrix(meth, gp)
        except:
            pass

        if mat is not None:
            est_tunes = [0.0, 0.0]
            for i, fam in enumerate(self._psfams):
                est_tunes[0] += mat[0, i] * self._psfam_kl[fam]
                est_tunes[1] += mat[1, i] * self._psfam_kl[fam]
            est_tunes[0] -= 48.173
            est_tunes[1] -= 1.23
            # self._update_log(f'etunes = {est_tunes}')
        else:
            est_tunes = [0.16, 0.22]

        dx += float(str(_t0)[-3:]) * 0.2e-5
        dy += float(str(_t0)[-4:-1]) * 0.2e-5

        self._faketunex = est_tunes[0] + dx
        self._faketuney = est_tunes[1] + dy

        self.run_callbacks('FakeTuneX-Mon', self._faketunex)
        self.run_callbacks('FakeTuneY-Mon', self._faketuney)

        dtime = _time() - _t0
        sleep_time = interval - dtime
        if sleep_time > 0:
            super().process(sleep_time)

    def _set_faketuneshiftamp(self, value):
        x = _np.linspace(0, 1.5, 10)
        y = x**2 + x
        try:
            tunex0 = self._sim_id_tuneshift_x[0]
            tuney0 = self._sim_id_tuneshift_y[0]
        except:
            tunex0 = 0
            tuney0 = 0
        self._sim_id_tuneshift_x += list(y * float(value) * 0.5 + tunex0)
        self._sim_id_tuneshift_y += list(y * float(value) * 0.7 + tuney0)
        self.run_callbacks('SimIDTuneShiftAmp-RB', float(value))

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

    def feedback_loop(self):
        """."""
        while not self._thread_fb_quit:
            # updating interval
            tplanned = 1.0/self._loop_freq

            # initial time
            _t0 = _time()
            # self._update_log(f'INFO: time = {_t0}.')

            if self._loop_state != _Const.LoopState.Closed:
                self._do_sleep(_t0, tplanned)
                continue

            # is it really necessary?
            # _update_ref already check the _status
            if not self._status:
                self._update_log('WARN: Connection problems.')
                self._do_sleep(_t0, tplanned)
                continue

            # sts = self._update_ref()
            sts = True
            if not sts:
                self._update_log('ERR: Could not UPDATE REFERENCE.')
                self._thread_fb_quit = True
                self._do_sleep(_t0, tplanned)
                continue

            ################################
            # next step: tune buffer and PID
            # sts, (tunex, tuney) = self._get_and_check_tunes()
            sts, (tunex, tuney) = True, (self._faketunex, self._faketuney)
            if not sts:
                self._update_log('WARN: Problem with the tunes.')
                self._do_sleep(_t0, tplanned)
                continue

            # sts = self._update_delta_tunes(tunex, tuney)
            self._delta_tunex = self._ref_tunex - tunex
            self._delta_tuney = self._ref_tuney - tuney

            # self._update_log(f'INFO: delta_tunex = {self._delta_tunex}')
            # self._update_log(f'INFO: delta_tuney = {self._delta_tuney}')

            self._calc_intstrength()
            ################################

            sts = self._apply_corr()  # ! #########
            # sts = True
            if not sts:
                self._update_log('ERR: Could not apply the correction.')
                self._do_sleep(_t0, tplanned)
                continue

            self._do_sleep(_t0, tplanned)

        self._thread_fb_quit = False
        _sleep(1)
        self._thread_set_loop_state(_Const.LoopState.Open, False)

    def _get_and_check_tunes(self):
        """."""
        sts, (tx, ty) = self._get_tunes()
        if not sts:
            self._update_log('ERR: Could not get tunes.')
        if sts:
            # check if tunes are within allowed range
            sts = sts and (abs(tx - self._ref_tunex) <= self._max_tune_err)
            if not sts:
                self._update_log('WARN: Tune X is out of range.')
            sts = sts and (abs(ty - self._ref_tuney) <= self._max_tune_err)
            if not sts:
                self._update_log('WARN: Tune Y is out of range.')
        return sts, (tx, ty)

    def _do_sleep(self, time0, tplanned):
        ttook = _time() - time0
        tsleep = tplanned - ttook
        if tsleep > 0:
            _sleep(tsleep)
        else:
            strf = (
                f'Feedback step took more than planned... '
                f'{ttook:.3f}/{tplanned:.3f} s')
            _log.warning(strf)