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

import pyaccel as _pyacc
from pymodels import si as _si
from apsuite.optics_analysis.tune_correction import TuneCorr

TWOPI = 2 * _np.pi


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
            self.run_callbacks('Log-Mon',
                'ERR: Cant set DeltaTuneX while the feedback loop is closed.')
            return False
        self._delta_tunex = value
        self.run_callbacks('DeltaTuneX-RB', value)
        self._calc_intstrength()
        return True

    def set_dtune_y(self, value):
        """Set DeltaTuneY."""
        if self._inloop:
            self.run_callbacks('Log-Mon',
                'ERR: Cant set DeltaTuneY while the feedback loop is closed.')
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
            return True
        self.run_callbacks('Log-Mon', f'{self._inloop=}')
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
        try:
            sts = self._sim_apply_corr()
            return sts
        except Exception as e:
            self.run_callbacks('Log-Mon', f'ERR: {e}.')
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
        try:
            return self._sim_update_ref()
        except Exception:
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

        # True = 1 = UsingDKLs, False = 0 = UsingDTune, -1 = An in Experiment
        self._using_pid_overdkls = -1
        if self._using_pid_overdkls == 1:
            self._pid_errs = [0.0, 0.0, 0.0]
        elif self._using_pid_overdkls == 0:
            self._pid_errs = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
        else:
            self._pid_errs = []

        self._pid_gains = dict(
            x=dict(kp=1.0, ki=0.0, kd=0.0),
            y=dict(kp=1.0, ki=0.0, kd=0.0),
        )
        self._thread_ramp_pid_gain = dict(
            x=dict(kp=None, ki=None, kd=None),
            y=dict(kp=None, ki=None, kd=None),
        )

        self._loop_state = _Const.LoopState.Open
        self._loop_state_lastsp = _Const.LoopState.Open
        self._loop_freq = 3.0
        self._thread_loopstate = None
        self._abort_thread_loopstate = False

        self._max_tune_err = 99.00
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

            # 'SimIDQuadShakeKL-SP': self._set_sim_idquadshakekl,
            'SimNoiseAmp-SP': self._set_klnoise_amp,
        })

        self._thread_fb_quit = False
        self._thread_fb = None

        # SIMULATION ##########################################################
        # model prep
        _model = _si.create_accelerator()
        self.SIMQUAD_LENG = 0.1

        _mia = _pyacc.lattice.find_indices(_model, 'fam_name', 'mia')[-1]
        _mib = _pyacc.lattice.find_indices(_model, 'fam_name', 'mib')[2]

        self._sim_quad_indices = [_mib, _mia]

        for i, idx in enumerate(self._sim_quad_indices):
            _model.insert(idx+i, _pyacc.elements.quadrupole(
                f'SimID_{i}', self.SIMQUAD_LENG, 0.0))
            self._sim_quad_indices[i] = idx + i

        self._sim_tunecorr = TuneCorr(_model, 'SI')
        self._sim_tunecorr.method = 0 \
            if self._corr_method == _Const.CorrMeth.Proportional else 1
        self._sim_tunecorr.grouping = self._corr_group
        self._sim_tunecorr.correct_parameters(
            [49+self._ref_tunex, 14+self._ref_tuney])
        self._psfam_refkl = self._sim_get_intstrength()

        # fake tune prep
        # self._sim_id_kl = []
        self._faketunex = 0.0
        self._faketuney = 0.0

        self._update_log('INFO: Loading noise data...')
        self._klnoise_len = 100_000  # possible cut
        path = '/home/vitor/repos/dev-packages/siriuspy/siriuspy/opticscorr/'
        self._klnoise = _np.load(path+'klnoise.npy').copy()
        self._update_log(f'INFO: Loaded {len(self._klnoise)} noise points!')
        self._klnoise = self._klnoise[:self._klnoise_len]
        self._klnoise_len = len(self._klnoise)
        self._klnoise = self._klnoise.tolist()
        self._klnoise_idx = 0
        self._klnoise_amp = 1.0
        # self._rng = _np.random.default_rng(111)

        #######################################################################

        self.tunex_buffer = [0.0, 0.0, 0.0]
        self.tuney_buffer = [0.0, 0.0, 0.0]
        self._last_delta_tunex = 0.0
        self._last_delta_tuney = 0.0

        # self._tune_x_pv.add_callback(self._fill_tunex_buffer)
        # self._tune_y_pv.add_callback(self._fill_tuney_buffer)
        # self._storedebeam_pv.add_callback(self._loop_checkbeam)

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

        # the tune buffers must be resized
        # tunes are read at 10 Hz
        # if the loop freq is 1 Hz, the tune buffer must be resized to 9
        # if the loop freq is 3 Hz, the tune buffer must be resized to 3

        buffer_size = int(9.5 / self._loop_freq)

        self.tunex_buffer = self.tunex_buffer[-buffer_size:]
        buffer_current_size = len(self.tunex_buffer)
        if buffer_current_size < buffer_size:
            self.tunex_buffer = [0.0] * (buffer_size - buffer_current_size) + \
                self.tunex_buffer

        self.tuney_buffer = self.tuney_buffer[-buffer_size:]
        buffer_current_size = len(self.tuney_buffer)
        if buffer_current_size < buffer_size:
            self.tuney_buffer = [0.0] * (buffer_size - buffer_current_size) + \
            self.tuney_buffer

        self.run_callbacks('LoopFreq-RB', float(value))
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
            target=self._set_loop_state_inthread,
            args=[value, abort], daemon=True)
        self._thread_loopstate.start()
        return True

    def _set_loop_state_inthread(self, value, abort):
        if value:  # closing the loop
            self._update_log('Closing the loop...')

            # set gains to zero
            self._update_log('Setting PID gains to zero...')
            self._inloop = False
            pid_gains = dict()
            for g in ['x', 'y']:
                pid_gains[g] = {
                    'kp': self._pid_gains[g]['kp'],
                    'ki': self._pid_gains[g]['ki'],
                    'kd': self._pid_gains[g]['kd']}
                self.set_pid_gain('kp', g, 0.0)
                self.set_pid_gain('ki', g, 0.0)
                self.set_pid_gain('kd', g, 0.0)

            # close the loop
            if self._thread_fb is not None:
                if self._thread_fb.is_alive():
                    self._loop_state = _Const.LoopState.Open
                    self._inloop = False
                    self._thread_fb_quit = True
                    self._thread_fb.join()
            self._thread_fb_quit = False
            self._thread_fb = self._create_feedbackthread()
            self._last_delta_tunex = 0.0
            self._last_delta_tuney = 0.0
            self._loop_state = value
            self._inloop = True
            self._thread_fb.start()

            # ramp up pid gains
            _sleep(0.2)
            self._update_log('Ramping up PID gains...')
            for g in ['x', 'y']:
                for k in ['kp', 'ki', 'kd']:
                    self.set_pid_gain(k, g, pid_gains[g][k])
            _sleep(1)
            self.run_callbacks('LoopState-Sts', self._loop_state)
            self._update_log('Loop closed.')
            return

        else:  # opening the loop
            # ramp down pid gains
            self._update_log('Ramping down PID gains...')
            pid_gains = dict()
            for g in ['x', 'y']:
                pid_gains[g] = {
                    'kp': self._pid_gains[g]['kp'],
                    'ki': self._pid_gains[g]['ki'],
                    'kd': self._pid_gains[g]['kd']}
                self.set_pid_gain('kp', g, 0.0)
                self.set_pid_gain('ki', g, 0.0)
                self.set_pid_gain('kd', g, 0.0)

            # open the loop
            _sleep(1)
            self._update_log('Opening the loop...')
            self._inloop = False
            self._loop_state = value
            _sleep(0.2)

            # restore pid gains
            for g in ['x', 'y']:
                self.set_pid_gain('kp', g, pid_gains[g]['kp'])
                self.set_pid_gain('ki', g, pid_gains[g]['ki'])
                self.set_pid_gain('kd', g, pid_gains[g]['kd'])
            self._update_log('PID gains restored.')

            self.run_callbacks('LoopState-Sts', self._loop_state)
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
        return self._ramp_pid_gain(kparam, plane, value)

    def _ramp_pid_gain(self, kparam, plane, value, abort=False):
        if self._thread_ramp_pid_gain[plane][kparam] is not None and \
            self._thread_ramp_pid_gain[plane][kparam].is_alive():
            self._thread_ramp_pid_gain[plane][kparam].join()

        self._thread_ramp_pid_gain[plane][kparam] = _epics.ca.CAThread(
            target=self._ramp_pid_gain_inthread,
            args=[kparam, plane, value, abort], daemon=True)
        self._thread_ramp_pid_gain[plane][kparam].start()
        return True

    def _ramp_pid_gain_inthread(self, kparam, plane, value, abort):
        deltapidgain = value - self._pid_gains[plane][kparam]
        max_delta_pid_gain_per_step = 0.15
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

        self.run_callbacks('MaxTuneErr-SP', self._max_tune_err)
        self.run_callbacks('MaxTuneErr-RB', self._max_tune_err)

        # SIMULATION ##########################################################
        self.run_callbacks('FakeTuneX-Mon', self._faketunex)
        self.run_callbacks('FakeTuneY-Mon', self._faketuney)
        self.run_callbacks('SimNoiseAmp-SP', self._klnoise_amp)
        self.run_callbacks('SimNoiseAmp-RB', self._klnoise_amp)
        self.run_callbacks('CorrGroup-Sts', self._corr_group)  # needed ?
        self.run_callbacks('CorrGroup-Sel', self._corr_group)  # needed ?
        self.run_callbacks('CorrMeth-Sts', self._corr_method)  # needed ?
        self.run_callbacks('CorrMeth-Sel', self._corr_method)  # needed ?
        #######################################################################

    def process(self, interval):
        """."""
        _t0 = _time()

        # if len(self._sim_id_kl) > 0:
        #     _k = self._sim_id_kl[0] / self.SIMQUAD_LENG
        #     self._sim_tunecorr.model[self._sim_id_quad_idx].K = float(+_k)
        #     del self._sim_id_kl[0]
        #     if len(self._sim_id_kl) == 0:
        #         self.run_callbacks('SimIDQuadShakeKL-RB', 0.0)

        if self._klnoise_idx >= self._klnoise_len:
            self._klnoise_idx = 0
        for kl, idx in zip(self._klnoise[self._klnoise_idx], self._sim_quad_indices):  # ruff:ignore[zip-without-explicit-strict, line-too-long]
            self._sim_tunecorr.model[idx].KL = kl * self._klnoise_amp
        self._klnoise_idx += 1

        self._faketunex, self._faketuney = self._sim_get_tunes()

        self._fill_tunex_buffer()
        self._fill_tuney_buffer()

        self.run_callbacks('FakeTuneX-Mon', self._faketunex)
        self.run_callbacks('FakeTuneY-Mon', self._faketuney)

        dtime = _time() - _t0
        sleep_time = interval - dtime
        if sleep_time > 0:
            super().process(sleep_time)

    def _fill_tunex_buffer(self):
        # if self._tune_x_pv.connected:
        if True:
            # self.tunex_buffer += [self._tune_x_pv.value]
            self.tunex_buffer += [self._faketunex]
            del self.tunex_buffer[0]
            return True
        return False

    def _fill_tuney_buffer(self):
        # if self._tune_y_pv.connected:
        if True:
            # self.tuney_buffer += [self._tune_y_pv.value]
            self.tuney_buffer += [self._faketuney]
            del self.tuney_buffer[0]
            return True
        return False

    # def _set_sim_idquadshakekl(self, value):
    #     pint = int(value)
    #     pfrac = float(value) - pint
    #     pint = abs(pint)
    #     x = _np.linspace(-1, 1, pint)
    #     y = 1 - x**4
    #     self._sim_id_kl += ([0.0] + list(y * pfrac) + [0.0])
    #     self.run_callbacks('SimIDQuadShakeKL-RB', float(value))
    #     return True

    def _set_klnoise_amp(self, value):
        self._klnoise_amp = float(value)
        self.run_callbacks('SimNoiseAmp-RB', float(value))
        return True

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
            elif self._thread_loopstate is not None and \
                self._thread_loopstate.is_alive():
                self._thread_loopstate.join()
                self._do_sleep(_t0, tplanned, do_warn=False)
                continue

            # is it really necessary?
            # _update_ref already check the _status
            # if not self._status:
            #     self._update_log('WARN: Connection problems.')
            #     self._do_sleep(_t0, tplanned)
            #     continue

            # sts = self._update_ref()
            sts = self._sim_update_ref()
            if not sts:
                self._update_log('ERR: Could not UPDATE REFERENCE.')
                self._thread_fb_quit = True
                self._do_sleep(_t0, tplanned)
                continue

            sts = self._check_tunes()
            if not sts:
                self._update_log('ERR: Tunes above limits!')
                self._thread_fb_quit = True
                # self._do_sleep(_t0, tplanned)
                continue

            ################################
            if self._using_pid_overdkls == 1:
                self._delta_tunex = self._ref_tunex - self.tunex_buffer[-1]
                self._delta_tuney = self._ref_tuney - self.tuney_buffer[-1]
                # tunexb = self.tunex_buffer.copy()
                # tuneyb = self.tuney_buffer.copy()
                # self._delta_tunex = self._ref_tunex-tunexb[tunexb != 0].mean()
                # self._delta_tuney = self._ref_tuney-tuneyb[tuneyb != 0].mean()
                self._calc_intstrength()
                self._process_pid_overdkls()

            elif self._using_pid_overdkls == 0:
                self._process_pid_overdtune()
                self._calc_intstrength()

            else:  # self._using_pid_overdkls == -1
                self._delta_tunex = self._pid_gains['x']['kp'] * \
                    (self._ref_tunex - self.tunex_buffer[-1])
                self._delta_tuney = self._pid_gains['y']['kp'] * \
                    (self._ref_tuney - self.tuney_buffer[-1])
                self._calc_intstrength()
            ################################

            # sts = self._apply_corr()  # ! #########
            sts = self._sim_apply_corr()  # ! #########
            # sts = True
            if not sts:
                self._update_log('ERR: Could not apply the correction.')
                self._do_sleep(_t0, tplanned)
                continue

            self._do_sleep(_t0, tplanned)

        self._set_loop_state_inthread(_Const.LoopState.Open, False)
        self._thread_fb_quit = False

    def _sim_update_ref(self):
        meankl_per_fam = self._sim_get_intstrength()
        for fam in self._psfams:
            self._psfam_refkl[fam] = meankl_per_fam[fam]
            self.run_callbacks('DeltaKL' + fam + '-Mon', 0)
            self._lastcalc_deltakl[fam] = 0
        self._last_delta_tunex = 0.0 + self._delta_tunex
        self._last_delta_tuney = 0.0 + self._delta_tuney
        self._delta_tunex = 0
        self._delta_tuney = 0
        self.run_callbacks('DeltaTuneX-SP', self._delta_tunex)
        self.run_callbacks('DeltaTuneX-RB', self._delta_tunex)
        self.run_callbacks('DeltaTuneY-SP', self._delta_tuney)
        self.run_callbacks('DeltaTuneY-RB', self._delta_tuney)
        return True

    def _sim_apply_corr(self):
        self._sim_tunecorr.grouping = self._corr_group
        self._sim_tunecorr.method = 0 \
            if self._corr_method == _Const.CorrMeth.Proportional else 1
        kls = {fam: self._psfam_refkl[fam]+self._lastcalc_deltakl[fam]
                    for fam in self._psfams}
        self._sim_apply_intstrength(kls)
        if not self._inloop:
            self._update_log('Applied correction.')
        if self._sync_corr == _Const.SyncCorr.On:
            # self._event_exttrig_cmd.put(0)
            if not self._inloop:
                self._update_log('Generated trigger.')
        return True

    def _sim_get_intstrength(self):
        return {fam: _np.mean([sum([self._sim_tunecorr.model[seg].KL
            for seg in mag])
            for mag in self._sim_tunecorr.fam[fam]['index']])
            for fam in self._psfams}

    def _sim_apply_intstrength(self, kls):
        meankl_per_fam = self._sim_get_intstrength()
        for fam in self._psfams:
            for mag in self._sim_tunecorr.fam[fam]['index']:
                newkl = kls[fam] - meankl_per_fam[fam]
                for seg in mag:
                    self._sim_tunecorr.model[seg].KL += newkl / len(mag)

    def _sim_get_tunes(self):
        _ed = _pyacc.optics.calc_edwards_teng(self._sim_tunecorr.model)[0]
        return _np.array([_ed.mu1[-1]/TWOPI-49, _ed.mu2[-1]/TWOPI-14])

    def _process_pid_overdkls(self):
        err = _np.array([self._lastcalc_deltakl[f] for f in self._psfams])
        self._pid_errs.append(err)
        del self._pid_errs[0]

        interval = 1/self._loop_freq

        kp = self._pid_gains['x']['kp']
        ki = self._pid_gains['x']['ki'] * interval
        kd = self._pid_gains['x']['kd'] / interval

        turn_on_pid = 1

        a0 = kp + turn_on_pid * (ki + kd)
        a1 = turn_on_pid * (-kp - 2*kd)
        a2 = turn_on_pid * (kd)

        e0 = self._pid_errs[-1]
        e1 = self._pid_errs[-2]
        e2 = self._pid_errs[-3]

        u = e0*a0 + a1*e1 + a2*e2

        for i, fam in enumerate(self._psfams):
            self._lastcalc_deltakl[fam] = u[i]

    def _process_pid_overdtune(self):
        tunexb = self.tunex_buffer.copy()
        tuneyb = self.tuney_buffer.copy()
        errx = self._ref_tunex-tunexb[tunexb != 0].mean()
        erry = self._ref_tuney-tuneyb[tuneyb != 0].mean()
        # errx = self._ref_tunex - self.tunex_buffer[-1]
        # erry = self._ref_tuney - self.tuney_buffer[-1]
        self._pid_errs.append([errx, erry])
        del self._pid_errs[0]

        interval = 1/self._loop_freq

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

        e0 = self._pid_errs[-1]
        e1 = self._pid_errs[-2]
        e2 = self._pid_errs[-3]

        # Update Delta Tunes
        self._delta_tunex = self._last_delta_tunex + \
            a0x*e0[0] + a1x*e1[0] + a2x*e2[0]
        self._delta_tuney = self._last_delta_tuney + \
            a0y*e0[1] + a1y*e1[1] + a2y*e2[1]

    def _check_tunes(self):
        """."""
        last_tunex = self.tunex_buffer[-1]
        last_tuney = self.tuney_buffer[-1]

        sts = True
        sts = sts and not _np.isclose(last_tunex, 0, atol=1e-3)
        sts = sts and not _np.isclose(last_tuney, 0, atol=1e-3)
        if not sts:
            self._update_log('ERR: Could not get tunes.')
            return sts

        # check if tunes are within allowed range
        sts = sts and (abs(last_tunex - self._ref_tunex) <= self._max_tune_err)
        if not sts:
            self._update_log('WARN: Tune X is out of range.')
        sts = sts and (abs(last_tuney - self._ref_tuney) <= self._max_tune_err)
        if not sts:
            self._update_log('WARN: Tune Y is out of range.')
        return sts

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
