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
from .opticscorr import OpticsCorr as _OpticsCorr

from siriuspy.devices import Tune as _TuneDevice, BunchbyBunch as _BbBDevice

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

        self._loop_state = _Const.LoopState.Open
        self._loop_state_lastsp = _Const.LoopState.Open
        self._loop_freq = 3.0
        self._thread_loopstate = None
        self._abort_thread_loopstate = False

        self._tune_source = _Const.TuneSource.Fake
        self._tune_aux_device = None

        self._max_tune_err = 99.00
        self._ref_tunex = 0.16
        self._ref_tuney = 0.22

        zer = _np.zeros(len(self._psfams), dtype=float)
        self._pid_errs = [zer, zer.copy(), zer.copy()]
        self._pid_gains = dict(kp=0.0, ki=3.0, kd=0.0)

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

            'IDKLDriftAmp-SP': self._set_id_kldrift_amp,
            'FakeNoiseAmp-SP': self._set_fakenoise_amp,

        })

        self._thread_fb_quit = False
        self._thread_fb = None

        # SIMULATION ##########################################################
        # model prep
        _model = _si.create_accelerator()
        self.SIMQUAD_LENG = 0.1

        _mia = _pyacc.lattice.find_indices(_model, 'fam_name', 'mia')[-1]
        _mib = _pyacc.lattice.find_indices(_model, 'fam_name', 'mib')[2]
        self._sim_quad_indices = [_mib-1, _mia-1]

        for idx in self._sim_quad_indices:
            _model[idx].KL = 0
            _model[idx].pass_method = 'str_mpole_symplectic4_pass' # noqa

        self._sim_tunecorr = TuneCorr(_model, 'SI')
        self._sim_tunecorr.method = 0 \
            if self._corr_method == _Const.CorrMeth.Proportional else 1
        self._sim_tunecorr.grouping = self._corr_group
        self._sim_tunecorr.correct_parameters(
            goal_parameters=[49+self._ref_tunex, 14+self._ref_tuney],
        )
        self._nominal_matrix = self._sim_tunecorr.calc_jacobian_matrix().ravel().tolist()  # noqa
        self._psfam_refkl = self._sim_get_intstrength()
        self._psfam_nom_intstr = [kl for kl in self._psfam_refkl.values()]
        self._opticscorr = _OpticsCorr(
            magnetfams_ordering=self._psfams,
            nominal_matrix=self._nominal_matrix,
            nominal_intstrengths=self._psfam_nom_intstr,
            nominal_opticsparam=self._nominal_opticsparam,
            magnetfams_focusing=self._opticscorr.magnetfams_focusing,
            magnetfams_defocusing=self._opticscorr.magnetfams_defocusing
        )

        # fake tune prep
        self._faketunex = 0.0
        self._faketuney = 0.0
        self._fakenoise_amp = 0.5
        self._rng = _np.random.default_rng(seed=111)

        self._update_log('INFO: Loading noise data...')
        self._id_kldrift_len = 1_000  # possible cut
        path = '/home/vitor/repos/dev-packages/siriuspy/siriuspy/opticscorr/'
        self._id_kldrift = _np.load(path+'klnoise.npy').copy()
        l0 = len(self._id_kldrift)
        self._id_kldrift = self._id_kldrift[:self._id_kldrift_len]
        self._id_kldrift_len = len(self._id_kldrift)
        self._update_log(f'INFO: Loaded {self._id_kldrift_len}/{l0} data points!')
        self._id_kldrift = self._id_kldrift.tolist()
        self._id_kldrift_idx = 0
        self._id_kldrift_amp = 0.0

        #######################################################################
        self._storedebeam_pv.add_callback(self._loop_checkbeam)

    def set_tune_source(self, value):
        """Set tune source."""
        if not 0 <= value < len(_ETypes.TUNE_SOURCE):
            self._update_log('ERR: Invalid tune source.')
            return False
        if value == _Const.TuneSource.Fake:
            pvx = _SiriusPVName('SI-Glob:AP-TuneCorr:FakeTuneX-Mon')
            pvy = _SiriusPVName('SI-Glob:AP-TuneCorr:FakeTuneY-Mon')
        elif value == _Const.TuneSource.TuneSpec:
            pvx = _SiriusPVName('SI-Glob:DI-Tune-H:TuneFrac-Mon')
            pvy = _SiriusPVName('SI-Glob:DI-Tune-V:TuneFrac-Mon')
        elif value == _Const.TuneSource.BbB_SB_M1:
            pvx = _SiriusPVName('SI-Glob:DI-BbBProc-H:SB_M1_TUNE')
            pvy = _SiriusPVName('SI-Glob:DI-BbBProc-V:SB_M1_TUNE')
        elif value == _Const.TuneSource.BbB_SRAM_M1:
            pvx = _SiriusPVName('SI-Glob:DI-BbBProc-H:SRAM_M1_TUNE')
            pvy = _SiriusPVName('SI-Glob:DI-BbBProc-V:SRAM_M1_TUNE')
        elif value == _Const.TuneSource.BbB_BRAM_M1:
            pvx = _SiriusPVName('SI-Glob:DI-BbBProc-H:BRAM_M1_TUNE')
            pvy = _SiriusPVName('SI-Glob:DI-BbBProc-V:BRAM_M1_TUNE')
        self.run_callbacks('TuneSourcePVList-Mon', (pvx, pvy))
        self.run_callbacks('TuneSource-Sts', value)
        self._tune_x_pv = _PV(pvx.substitute(prefix=_vaca_prefix))
        self._tune_y_pv = _PV(pvy.substitute(prefix=_vaca_prefix))
        return True

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
        return True

    def set_loop_state(self, value, abort=False):
        """Set loop state."""
        if not 0 <= value < len(_ETypes.OPEN_CLOSED):
            self._update_log('ERR: Invalid loop state.')
            return False

        self._loop_state_lastsp = value
        # if value and not self._is_storedebeam:
        #     self._update_log('ERR: Do not have stored beam. Aborted.')
        #     return False

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
        self._thread_loopstate.join()
        return True

    def _set_loop_state_inthread(self, value, abort):
        if value:  # closing the loop
            self._update_log('Closing the loop...')

            self._sim_update_ref()
            # self._update_ref()
            self._update_log('Reference updated!')

            # close the loop
            if self._thread_fb is not None:
                if self._thread_fb.is_alive():
                    self._loop_state = _Const.LoopState.Open
                    self._inloop = False
                    self._thread_fb_quit = True
                    self._thread_fb.join()
            self._thread_fb_quit = False
            self._thread_fb = self._create_feedbackthread()
            self._inloop = True
            self._loop_state = value
            self._thread_fb.start()

            self.run_callbacks('LoopState-Sts', self._loop_state)
            self._update_log('Loop closed.')
            return

        else:  # opening the loop
            self._update_log('Opening the loop...')
            self._loop_state = value
            self._inloop = False

            self._sim_update_ref()
            # self._update_ref()
            self._update_log('Reference updated!')

            self.run_callbacks('LoopState-Sts', self._loop_state)
            self._update_log('Loop opened.')
            return

    def _check_abort_thread(self):
        if self._abort_thread_loopstate:
            self._update_log('WARN:Set Loop State thread aborted.')
            self._abort_thread_loopstate = False
            return True
        return False

    def _loop_checkbeam(self, pvname, value, **kws):
        if not value and self._inloop:
            self._update_log('FATAL: Opening Tune Feedback loop...')
            self.set_loop_state(self._const.LoopState.Open)

    def set_pid_gain(self, kparam, value):
        """."""
        kparam = kparam.lower()
        self._pid_gains[kparam] = float(value)
        self.run_callbacks("LoopPID" + kparam.title() + "-RB", float(value))
        return True

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
        self.run_callbacks('TuneSourcePVList-Mon', (
            'SI-Glob:AP-TuneCorr:FakeTuneX-Mon',
            'SI-Glob:AP-TuneCorr:FakeTuneY-Mon'
        ))

        # SIMULATION ##########################################################
        self.run_callbacks('FakeTuneX-Mon', self._faketunex)
        self.run_callbacks('FakeTuneY-Mon', self._faketuney)

        self.run_callbacks('FakeNoiseAmp-SP', self._fakenoise_amp)
        self.run_callbacks('FakeNoiseAmp-RB', self._fakenoise_amp)

        self.run_callbacks('IDKLDriftAmp-SP', self._id_kldrift_amp)
        self.run_callbacks('IDKLDriftAmp-RB', self._id_kldrift_amp)

        self.run_callbacks('CorrGroup-Sts', self._corr_group)  # needed ?
        self.run_callbacks('CorrGroup-Sel', self._corr_group)  # needed ?
        self.run_callbacks('CorrMeth-Sts', self._corr_method)  # needed ?
        self.run_callbacks('CorrMeth-Sel', self._corr_method)  # needed ?
        #######################################################################

    def process(self, interval):
        """."""
        _t0 = _time()

        if self._id_kldrift_idx >= self._id_kldrift_len:
            self._id_kldrift_idx = 0
        id_kldrift = self._id_kldrift[self._id_kldrift_idx]
        for kl, idx in zip(id_kldrift, self._sim_quad_indices):  # noqa
            self._sim_tunecorr.model[idx].KL = kl * self._id_kldrift_amp
        self._id_kldrift_idx += 1

        self._faketunex, self._faketuney = self._sim_get_tunes()

        fakenoise = self._rng.normal(0, 0.0005, 2) * self._fakenoise_amp
        self._faketunex += fakenoise[0]
        self._faketuney += fakenoise[1]
        self.run_callbacks('FakeTuneX-Mon', self._faketunex)
        self.run_callbacks('FakeTuneY-Mon', self._faketuney)

        dtime = _time() - _t0
        sleep_time = interval - dtime
        if sleep_time > 0:
            super().process(sleep_time)

    def _set_fakenoise_amp(self, value):
        self._fakenoise_amp = float(value)
        self.run_callbacks('FakeNoiseAmp-RB', float(value))
        return True

    def _set_id_kldrift_amp(self, value):
        self._id_kldrift_amp = float(value)
        self.run_callbacks('IDKLDriftAmp-RB', float(value))
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
            tplanned = 1.0/self._loop_freq
            _t0 = _time()

            if self._loop_state != _Const.LoopState.Closed:
                self._do_sleep(_t0, tplanned)
                continue
            elif self._thread_loopstate is not None and \
                self._thread_loopstate.is_alive():
                self._thread_loopstate.join()
                self._do_sleep(_t0, tplanned, do_warn=False)
                continue

            # ! # sts = self._update_ref()
            # ! sts = self._sim_update_ref()
            # if not sts:
            #     self._update_log('ERR: Could not UPDATE REFERENCE.')
            #     self._thread_fb_quit = True
            #     self._do_sleep(_t0, tplanned)
            #     continue

            sts = self._process_pid()
            if not sts:
                self._thread_fb_quit = True
                continue

            # sts = self._apply_corr()
            sts = self._sim_apply_corr()
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

    def _process_pid(self):
        sts, (tunex, tuney) = self._get_tunes()
        if not sts:
            return False

        if not self._check_tunes(tunex, tuney):
            return False

        self._delta_tunex = self._ref_tunex - tunex
        self._delta_tuney = self._ref_tuney - tuney

        delta_kl_prev = _np.array([self._lastcalc_deltakl[fam]
            for fam in self._psfams])

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

        return True

    def _get_tunes(self):
        tunex, tuney = 0.0, 0.0
        if self._tune_x_pv.connected:
            tunex = self._tune_x_pv.value
        else:
            sts = False
        if sts and self._tune_y_pv.connected:
            tuney = self._tune_y_pv.value
        if not sts:
            self._update_log('ERR: Could not get the tunes!')
        return sts, (tunex, tuney)

    def _check_tunes(self, tunex, tuney):

        sts = self._check_tunes_reliability(tunex, tuney)
        sts &= self._check_tunes_distortion(tunex, tuney)
        return sts

    def _check_tunes_distortion(self, tunex, tuney):
        # check if tunes are within allowed range
        sts = (abs(tunex - self._ref_tunex) <= self._max_tune_err)
        if not sts:
            self._update_log('WARN: Tune X is out of range.')
        sts = sts and (abs(tuney - self._ref_tuney) <= self._max_tune_err)
        if not sts:
            self._update_log('WARN: Tune Y is out of range.')
        return sts

    def _check_tunes_reliability(self, tunex, tuney):
        return True

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
