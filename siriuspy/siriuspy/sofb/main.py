"""Main Module of the program."""

from time import time as _time, sleep as _sleep
import logging as _log
from functools import partial as _part

import numpy as _np

from ..epics import PV as _PV, CAThread as _Thread
from ..devices import HLFOFB

from .matrix import BaseMatrix as _BaseMatrix
from .orbit import BaseOrbit as _BaseOrbit
from .correctors import BaseCorrectors as _BaseCorrectors
from .base_class import BaseClass as _BaseClass, \
    compare_kicks as _compare_kicks

INTERVAL = 1


class SOFB(_BaseClass):
    """Main Class of the IOC."""

    def __init__(
            self, acc, prefix='', callback=None, orbit=None, matrix=None,
            correctors=None, tests=False):
        """Initialize Object."""
        super().__init__(acc, prefix=prefix, callback=callback)
        _log.info('Starting SOFB...')

        self._tests = tests
        self._orbit = self._correctors = self._matrix = None
        self._loop_state = self._csorb.LoopState.Open
        self._loop_freq = self._csorb.BPMsFreq
        self._loop_print_every_num_iter = 200
        self._loop_use_pssofb = False
        self._loop_max_orb_distortion = self._csorb.DEF_MAX_ORB_DISTORTION
        zer = _np.zeros(self._csorb.nr_corrs, dtype=float)
        self._pid_errs = [zer, zer.copy(), zer.copy()]
        self._pid_gains = dict(
            ch=dict(kp=0.0, ki=0.2, kd=0.0),
            cv=dict(kp=0.0, ki=0.2, kd=0.0),
            rf=dict(kp=0.0, ki=0.2, kd=0.0))
        self._measuring_respmat = False
        self._mancorr_gain = {'ch': 1.00, 'cv': 1.00}
        self._max_kick = {'ch': 300, 'cv': 300}
        self._max_delta_kick = {'ch': 5, 'cv': 5}
        self._meas_respmat_kick = {'ch': 15, 'cv': 22.5}
        if self.isring:
            self._mancorr_gain['rf'] = 1.00
            self._max_kick['rf'] = 1e12  # a very large value
            self._max_delta_kick['rf'] = 10
            self._meas_respmat_kick['rf'] = 75
        if self.acc == 'SI':
            self.fofb = HLFOFB()
            self._download_fofb_kicks = True
            self._download_fofb_kicks_perc = 0.04
            self._update_fofb_reforb = False
            self._update_fofb_reforb_perc = 0.0
            self._donot_affect_fofb_bpms = False
            self._project_onto_fofb_nullspace = False
            self._drive_divisor = 12
            self._drive_nrcycles = 10
            self._drive_amplitude = 5
            self._drive_phase = 0
            self._drive_corr_index = 0
            self._drive_bpm_index = 0
            self._drive_type = self._csorb.DriveType.Sine
            self._drive_state = self._csorb.DriveState.Open
        self._meas_respmat_wait = 1  # seconds
        self._dtheta = None
        self._ref_corr_kicks = None
        self._thread = None
        self._havebeam_pv = _PV('SI-Glob:AP-CurrInfo:StoredEBeam-Mon')

        self.orbit = orbit
        self.correctors = correctors
        self.matrix = matrix
        self._amcs = [
            _PV(f'IA-{i:02d}RaBPM:TI-AMCFPGAEVR:RefClkLocked-Mon')
            for i in range(1, 21)]

    def get_map2write(self):
        """Get the database of the class."""
        dbase = {
            'LoopState-Sel': self.set_auto_corr,
            'LoopFreq-SP': self.set_auto_corr_frequency,
            'LoopPrintEveryNumIters-SP': self.set_print_every_num_iters,
            'LoopPIDKpCH-SP': _part(self.set_pid_gain, 'kp', 'ch'),
            'LoopPIDKpCV-SP': _part(self.set_pid_gain, 'kp', 'cv'),
            'LoopPIDKiCH-SP': _part(self.set_pid_gain, 'ki', 'ch'),
            'LoopPIDKiCV-SP': _part(self.set_pid_gain, 'ki', 'cv'),
            'LoopPIDKdCH-SP': _part(self.set_pid_gain, 'kd', 'ch'),
            'LoopPIDKdCV-SP': _part(self.set_pid_gain, 'kd', 'cv'),
            'LoopMaxOrbDistortion-SP': self.set_max_orbit_dist,
            'MeasRespMat-Cmd': self.set_respmat_meas_state,
            'CalcDelta-Cmd': self.calc_correction,
            'ManCorrGainCH-SP': _part(self.set_mancorr_gain, 'ch'),
            'ManCorrGainCV-SP': _part(self.set_mancorr_gain, 'cv'),
            'MaxKickCH-SP': _part(self.set_max_kick, 'ch'),
            'MaxKickCV-SP': _part(self.set_max_kick, 'cv'),
            'MaxDeltaKickCH-SP': _part(self.set_max_delta_kick, 'ch'),
            'MaxDeltaKickCV-SP': _part(self.set_max_delta_kick, 'cv'),
            'DeltaKickCH-SP': _part(
                self.set_delta_kick, self._csorb.ApplyDelta.CH),
            'DeltaKickCV-SP': _part(
                self.set_delta_kick, self._csorb.ApplyDelta.CV),
            'MeasRespMatKickCH-SP': _part(self.set_respmat_kick, 'ch'),
            'MeasRespMatKickCV-SP': _part(self.set_respmat_kick, 'cv'),
            'MeasRespMatWait-SP': self.set_respmat_wait_time,
            'ApplyDelta-Cmd': self.apply_corr,
            }
        if self.isring:
            dbase['LoopPIDKpRF-SP'] = _part(self.set_pid_gain, 'kp', 'rf')
            dbase['LoopPIDKiRF-SP'] = _part(self.set_pid_gain, 'ki', 'rf')
            dbase['LoopPIDKdRF-SP'] = _part(self.set_pid_gain, 'kd', 'rf')
            dbase['ManCorrGainRF-SP'] = _part(self.set_mancorr_gain, 'rf')
            dbase['MaxDeltaKickRF-SP'] = _part(self.set_max_delta_kick, 'rf')
            dbase['DeltaKickRF-SP'] = _part(
                self.set_delta_kick, self._csorb.ApplyDelta.RF)
            dbase['MeasRespMatKickRF-SP'] = _part(self.set_respmat_kick, 'rf')
        if self.acc == 'SI':
            dbase['CorrPSSOFBEnbl-Sel'] = self.set_use_pssofb
            dbase['FOFBDownloadKicksPerc-SP'] = self.set_fofb_download_perc
            dbase['FOFBDownloadKicks-Sel'] = _part(
                self.set_fofb_interaction_props, 'downloadkicks')
            dbase['FOFBUpdateRefOrbPerc-SP'] = self.set_fofb_updatereforb_perc
            dbase['FOFBUpdateRefOrb-Sel'] = _part(
                self.set_fofb_interaction_props, 'updatereforb')
            dbase['FOFBNullSpaceProj-Sel'] = _part(
                self.set_fofb_interaction_props, 'nullspaceproj')
            dbase['FOFBZeroDistortionAtBPMs-Sel'] = _part(
                self.set_fofb_interaction_props, 'zerodistortion')
            dbase['DriveFreqDivisor-SP'] = self.set_drive_divisor
            dbase['DriveNrCycles-SP'] = self.set_drive_nrcycles
            dbase['DriveAmplitude-SP'] = self.set_drive_amplitude
            dbase['DrivePhase-SP'] = self.set_drive_phase
            dbase['DriveCorrIndex-SP'] = self.set_drive_corr_index
            dbase['DriveBPMIndex-SP'] = self.set_drive_bpm_index
            dbase['DriveType-Sel'] = self.set_drive_type
            dbase['DriveState-Sel'] = self.set_drive_state
        return dbase

    @property
    def orbit(self):
        """."""
        return self._orbit

    @orbit.setter
    def orbit(self, orb):
        """."""
        if isinstance(orb, _BaseOrbit):
            self._map2write.update(orb.get_map2write())
            self._orbit = orb
            self._orbit.sofb = self

    @property
    def correctors(self):
        """."""
        return self._correctors

    @correctors.setter
    def correctors(self, corrs):
        """."""
        if isinstance(corrs, _BaseCorrectors):
            self._map2write.update(corrs.get_map2write())
            self._correctors = corrs
            self._correctors.sofb = self

    @property
    def matrix(self):
        """."""
        return self._matrix

    @matrix.setter
    def matrix(self, mat):
        """."""
        if isinstance(mat, _BaseMatrix):
            self._map2write.update(mat.get_map2write())
            self._matrix = mat
            self._matrix.sofb = self

    @property
    def havebeam(self):
        """."""
        if self._tests or self.acc != 'SI':
            return True
        return self._havebeam_pv.connected and self._havebeam_pv.value

    @property
    def is_amc_connected(self):
        """."""
        for amc in self._amcs:
            if not amc.connected:
                return False
        return True

    @property
    def is_amc_locked(self):
        """."""
        for amc in self._amcs:
            if not amc.connected or not amc.value:
                return False
        return True

    def process(self):
        """Run continuously in the main thread."""
        time0 = _time()
        self.status
        tfin = _time()
        dtime = INTERVAL - (tfin-time0)
        if dtime > 0:
            _sleep(dtime)
        else:
            _log.debug('process took {0:f}ms.'.format((tfin-time0)*1000))

    def set_use_pssofb(self, val):
        """Set whether or not closed loop will use PSSOFB.

        Args:
            val (bool): desired state.

        Returns:
            bool: Whether setting was successful.

        """
        if self._thread and self._thread.is_alive():
            msg = 'ERR: Performing some task. Cannot change PSSOFB state!'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        self._loop_use_pssofb = bool(val)
        self.run_callbacks('CorrPSSOFBEnbl-Sts', val)
        return True

    def set_print_every_num_iters(self, value: float) -> bool:
        """Define number of iterations between loop statistics calculation.

        Args:
            value (float): number of iterations to wait.

        Returns:
            bool: whether property was properly set.

        """
        self._loop_print_every_num_iter = int(value)
        self.run_callbacks('LoopPrintEveryNumIters-RB', int(value))
        return True

    def set_fofb_interaction_props(self, prop: str, value: int):
        """Set properties related to FOFB interaction.

        Args:
            prop (str): name of the property
            value (int): value of the property

        Returns:
            bool: Whether property was set.

        """
        value = bool(value)
        if prop.lower().startswith('download'):
            self._download_fofb_kicks = value
            self.run_callbacks('FOFBDownloadKicks-Sts', value)
        elif prop.lower().startswith('update'):
            self._update_fofb_reforb = value
            self.run_callbacks('FOFBUpdateRefOrb-Sts', value)
        elif prop.lower().startswith('null'):
            self._project_onto_fofb_nullspace = value
            self.run_callbacks('FOFBNullSpaceProj-Sts', value)
        elif prop.lower().startswith('zero'):
            self._donot_affect_fofb_bpms = value
            self.run_callbacks('FOFBZeroDistortionAtBPMs-Sts', value)
        else:
            return False
        return True

    def set_fofb_download_perc(self, value: float):
        """Set percentage of kicks to be downloaded from FOFB.

        Args:
            value (float): percentage of kicks. must be in [0, 100].

        Returns:
            bool: Whether property was set.

        """
        value = min(max(value/100, 0), 1)
        self._download_fofb_kicks_perc = value
        self.run_callbacks('FOFBDownloadKicksPerc-RB', value*100)
        return True

    def set_fofb_updatereforb_perc(self, value: float):
        """Set percentage of reference orbit update in FOFB.

        Args:
            value (float): percentage of calculated orbit.
                Must be in [-100, 100].

        Returns:
            bool: Whether property was set.

        """
        value = min(max(value/100, -1), 1)
        self._update_fofb_reforb_perc = value
        self.run_callbacks('FOFBUpdateRefOrbPerc-RB', value*100)
        return True

    def apply_corr(self, code):
        """Apply calculated kicks on the correctors."""
        if self.acc == 'BO':
            msg = 'ERR: Cannot correct orbit for this accelerator.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False

        if self._thread and self._thread.is_alive():
            msg = 'ERR: Loop is Closed or MeasRespMat is On.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        if self._dtheta is None:
            msg = 'ERR: Cannot Apply Kick. Calc Corr first.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        self._apply_corr(code=code)
        return True

    def calc_correction(self, val):
        """Calculate correction."""
        self.run_callbacks('ApplyDelta-Mon', self._csorb.ApplyDeltaMon.Idle)
        if self._thread and self._thread.is_alive():
            msg = 'ERR: Loop is Closed or MeasRespMat is On.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        self._calc_correction()
        return True

    def set_delta_kick(self, code, dkicks):
        """Calculate correction."""
        if self._thread and self._thread.is_alive():
            msg = 'ERR: Loop is Closed or MeasRespMat is On.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        self._set_delta_kick(code=code, dkicks=dkicks)
        return True

    def set_respmat_meas_state(self, value):
        """."""
        if value == self._csorb.MeasRespMatCmd.Start:
            self._start_meas_respmat()
        elif value == self._csorb.MeasRespMatCmd.Stop:
            self._stop_meas_respmat()
        elif value == self._csorb.MeasRespMatCmd.Reset:
            self._reset_meas_respmat()
        return True

    def set_auto_corr(self, value):
        """."""
        if self.acc != 'SI':
            msg = 'ERR: Cannot close loop for this accelerator.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False

        if value == self._csorb.LoopState.Closed:
            if self._loop_state == self._csorb.LoopState.Closed:
                msg = 'ERR: Loop is Already closed.'
                self._update_log(msg)
                _log.error(msg[5:])
                return False
            if self._thread and self._thread.is_alive():
                msg = 'ERR: Measuring RespMat or Drive is closed. Stopping!'
                self._update_log(msg)
                _log.error(msg[5:])
                return False
            if not self.havebeam:
                msg = 'ERR: Cannot Correct, We do not have stored beam!'
                self._update_log(msg)
                _log.error(msg[5:])
                return False
            msg = 'Closing the Loop.'
            self._update_log(msg)
            _log.info(msg)
            self._loop_state = value
            self._thread = _Thread(target=self._do_auto_corr, daemon=True)
            self._thread.start()
        elif value == self._csorb.LoopState.Open:
            msg = 'Opening the Loop.'
            self._update_log(msg)
            _log.info(msg)
            self._loop_state = value
        return True

    def set_drive_divisor(self, value):
        """."""
        val = abs(int(value))
        self._drive_divisor = min(
            val, self._csorb.MAX_DRIVE_DATA // (3*self._drive_nrcycles))

        self.run_callbacks('DriveFreqDivisor-RB', self._drive_divisor)
        freq = self._csorb.BPMsFreq/self._drive_divisor
        self.run_callbacks('DriveFrequency-Mon', freq)
        self.run_callbacks('DriveDuration-Mon', self._drive_nrcycles/freq)
        return True

    def set_drive_nrcycles(self, value):
        """."""
        val = max(abs(int(value)), 1)
        self._drive_nrcycles = min(
            val, self._csorb.MAX_DRIVE_DATA // (3*self._drive_divisor))

        self.run_callbacks('DriveNrCycles-RB', self._drive_nrcycles)
        freq = self._csorb.BPMsFreq/self._drive_divisor
        self.run_callbacks('DriveDuration-Mon', self._drive_nrcycles/freq)
        return True

    def set_drive_amplitude(self, value):
        """."""
        self._drive_amplitude = value
        self.run_callbacks('DriveAmplitude-RB', value)
        return True

    def set_drive_phase(self, value):
        """."""
        self._drive_phase = value
        self.run_callbacks('DrivePhase-RB', value)
        return True

    def set_drive_corr_index(self, value):
        """."""
        if -self._csorb.nr_corrs < value < self._csorb.nr_corrs:
            self._drive_corr_index = int(value)
            self.run_callbacks('DriveCorrIndex-RB', int(value))
            return True
        return False

    def set_drive_bpm_index(self, value):
        """."""
        if -self._csorb.nr_bpms*2 < value < self._csorb.nr_bpms*2:
            self._drive_bpm_index = int(value)
            self.run_callbacks('DriveBPMIndex-RB', int(value))
            return True
        return False

    def set_drive_type(self, value):
        """."""
        self._drive_type = int(value)
        self.run_callbacks('DriveType-Sts', int(value))
        return True

    def set_drive_state(self, value):
        """."""
        if value == self._csorb.DriveState.Closed:
            if self._drive_state == self._csorb.DriveState.Closed:
                msg = 'ERR: Loop is Already closed.'
                self._update_log(msg)
                _log.error(msg[5:])
                return False
            if self._thread and self._thread.is_alive():
                msg = 'ERR: Measuring RespMat or Loop is Closed. Stopping!'
                self._update_log(msg)
                _log.error(msg[5:])
                return False
            if not self.havebeam:
                msg = 'ERR: Cannot Drive, We do not have stored beam!'
                self._update_log(msg)
                _log.error(msg[5:])
                return False
            msg = 'Closing the Drive Loop.'
            self._update_log(msg)
            _log.info(msg)
            self._drive_state = value
            self._thread = _Thread(target=self._do_drive, daemon=True)
            self._thread.start()
        elif value == self._csorb.LoopState.Open:
            msg = 'Opening the Drive Loop.'
            self._update_log(msg)
            _log.info(msg)
            self._drive_state = value
        return True

    def set_auto_corr_frequency(self, value):
        """."""
        bpmfreq = self._csorb.BPMsFreq
        value = bpmfreq / max(int(bpmfreq/value), 1)
        self._loop_freq = value
        self.run_callbacks('LoopFreq-RB', value)
        return True

    def set_pid_gain(self, ctrlr, plane, value):
        """."""
        ctrlr = ctrlr.lower()
        plane = plane.lower()
        self._pid_gains[plane][ctrlr] = float(value)
        self.run_callbacks(
            'LoopPID'+ctrlr.title()+plane.upper()+'-RB', float(value))
        return True

    def set_max_kick(self, plane, value):
        """."""
        self._max_kick[plane] = float(value)
        self.run_callbacks('MaxKick'+plane.upper()+'-RB', float(value))
        return True

    def set_max_delta_kick(self, plane, value):
        """."""
        self._max_delta_kick[plane] = float(value)
        self.run_callbacks('MaxDeltaKick'+plane.upper()+'-RB', float(value))
        return True

    def set_mancorr_gain(self, plane, value):
        """."""
        self._mancorr_gain[plane] = value/100
        msg = 'ManCorrGain{0:s} set to {1:6.2f}'.format(plane.upper(), value)
        self._update_log(msg)
        _log.info(msg)
        self.run_callbacks('ManCorrGain'+plane.upper()+'-RB', value)
        return True

    def set_respmat_kick(self, plane, value):
        """."""
        self._meas_respmat_kick[plane] = value
        self.run_callbacks('MeasRespMatKick'+plane.upper()+'-RB', value)
        return True

    def set_respmat_wait_time(self, value):
        """."""
        self._meas_respmat_wait = value
        self.run_callbacks('MeasRespMatWait-RB', value)
        return True

    def set_max_orbit_dist(self, value):
        """."""
        self._loop_max_orb_distortion = value
        self.run_callbacks('LoopMaxOrbDistortion-RB', value)
        return True

    def _update_status(self):
        self._status = bool(
            self._correctors.status | self._matrix.status | self._orbit.status)
        self.run_callbacks('Status-Mon', self._status)

        if self.acc != 'SI':
            return
        # Update PVs related to interaction with FOFB:
        fofb_state = self.fofb.connected and self.fofb.loop_state
        download = self._download_fofb_kicks and fofb_state
        update = self._update_fofb_reforb and fofb_state
        project = self._project_onto_fofb_nullspace and fofb_state
        donot = self._donot_affect_fofb_bpms and fofb_state
        self.run_callbacks('FOFBDownloadKicks-Mon', download)
        self.run_callbacks('FOFBUpdateRefOrb-Mon', update)
        self.run_callbacks('FOFBNullSpaceProj-Mon', project)
        self.run_callbacks('FOFBZeroDistortionAtBPMs-Mon', donot)

    def _set_delta_kick(self, code, dkicks):
        nr_ch = self._csorb.nr_ch
        nr_chcv = self._csorb.nr_chcv
        self._ref_corr_kicks = self.correctors.get_strength()
        if self._dtheta is None:
            self._dtheta = _np.zeros(self._ref_corr_kicks.size, dtype=float)
        if code == self._csorb.ApplyDelta.CH:
            self._dtheta[:nr_ch] = dkicks
            self.run_callbacks('DeltaKickCH-RB', list(dkicks))
            self.run_callbacks('DeltaKickCH-Mon', list(dkicks))
        elif code == self._csorb.ApplyDelta.CV:
            self._dtheta[nr_ch:nr_chcv] = dkicks
            self.run_callbacks('DeltaKickCV-RB', list(dkicks))
            self.run_callbacks('DeltaKickCV-Mon', list(dkicks))
        elif self.isring and code == self._csorb.ApplyDelta.RF:
            self._dtheta[-1] = dkicks
            self.run_callbacks('DeltaKickRF-RB', float(dkicks))
            self.run_callbacks('DeltaKickRF-Mon', float(dkicks))

    def _apply_corr(self, code):
        self.run_callbacks(
            'ApplyDelta-Mon', self._csorb.ApplyDeltaMon.Applying)
        nr_ch = self._csorb.nr_ch
        if self._dtheta is None:
            msg = 'Err: All kicks are zero.'
            self._update_log(msg)
            _log.warning(msg[6:])
            self.run_callbacks(
                'ApplyDelta-Mon', self._csorb.ApplyDeltaMon.Error)
            return
        dkicks = self._dtheta.copy()
        if code == self._csorb.ApplyDelta.CH:
            dkicks[nr_ch:] = 0
        elif code == self._csorb.ApplyDelta.CV:
            dkicks[:nr_ch] = 0
            if self.isring:
                dkicks[-1] = 0
        elif self.isring and code == self._csorb.ApplyDelta.RF:
            dkicks[:-1] = 0
        msg = f'Applying {self._csorb.ApplyDelta._fields[code]:s} kicks.'
        self._update_log(msg)
        _log.info(msg)

        kicks, dkicks = self._process_kicks(self._ref_corr_kicks, dkicks)
        if kicks is None:
            self.run_callbacks(
                'ApplyDelta-Mon', self._csorb.ApplyDeltaMon.Error)
            return

        if self.acc == 'SI':
            kicks = self._interact_with_fofb_in_apply_kicks(kicks, dkicks)
            if kicks is None:
                self.run_callbacks(
                    'ApplyDelta-Mon', self._csorb.ApplyDeltaMon.Error)
                return

        ret = self.correctors.apply_kicks(kicks)
        if ret is None:
            msg = 'ERR: There is some problem with a corrector!'
            self._update_log(msg)
            _log.error(msg[:5])
            self.run_callbacks(
                'ApplyDelta-Mon', self._csorb.ApplyDeltaMon.Error)
            return
        elif ret == -1:
            msg = 'WARN: Last was not applied yet'
            self._update_log(msg)
            _log.error(msg[:5])
        elif ret == 0:
            msg = 'kicks applied!'
            self._update_log(msg)
            _log.info(msg)
        else:
            msg = f'WARN: {ret:03d} kicks were not applied previously!'
            self._update_log(msg)
            _log.warning(msg[:6])
        self.run_callbacks('ApplyDelta-Mon', self._csorb.ApplyDeltaMon.Done)

    def _stop_meas_respmat(self):
        if not self._measuring_respmat:
            msg = 'ERR: No Measurement ocurring.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        msg = 'Aborting measurement. Wait...'
        self._update_log(msg)
        _log.info(msg)
        self._measuring_respmat = False
        return True

    def _reset_meas_respmat(self):
        if self._measuring_respmat:
            msg = 'Cannot Reset, Measurement in process.'
            self._update_log(msg)
            _log.info(msg)
            return False
        msg = 'Reseting measurement status.'
        self._update_log(msg)
        _log.info(msg)
        self.run_callbacks('MeasRespMat-Mon', self._csorb.MeasRespMatMon.Idle)
        return True

    def _start_meas_respmat(self):
        if self._measuring_respmat:
            msg = 'ERR: Measurement already in process.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        if self._thread and self._thread.is_alive():
            msg = 'ERR: Loop is Closed or Drive is Running. Stopping!'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        if not self.havebeam:
            msg = 'ERR: Cannot Measure, We do not have stored beam!'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        msg = 'Starting RespMat measurement.'
        self._update_log(msg)
        _log.info(msg)
        self._measuring_respmat = True
        self._thread = _Thread(target=self._do_meas_respmat, daemon=True)
        self._thread.start()
        return True

    def _do_meas_respmat(self):
        self.run_callbacks(
            'MeasRespMat-Mon', self._csorb.MeasRespMatMon.Measuring)
        mat = list()
        orig_kicks = self.correctors.get_strength()
        enbllist = self.matrix.corrs_enbllist
        sum_enbld = sum(enbllist)
        j = 1
        nr_corrs = len(orig_kicks)
        orbzero = _np.zeros(len(self.matrix.bpm_enbllist), dtype=float)
        for i in range(nr_corrs):
            if not self._measuring_respmat:
                self.run_callbacks(
                    'MeasRespMat-Mon', self._csorb.MeasRespMatMon.Aborted)
                msg = 'Measurement stopped.'
                self._update_log(msg)
                _log.info(msg)
                for _ in range(i, nr_corrs):
                    mat.append(orbzero)
                break
            if not self.havebeam:
                self.run_callbacks(
                    'MeasRespMat-Mon', self._csorb.MeasRespMatMon.Aborted)
                msg = 'ERR: Cannot Measure, We do not have stored beam!'
                self._update_log(msg)
                _log.info(msg)
                for _ in range(i, nr_corrs):
                    mat.append(orbzero)
                break
            if not enbllist[i]:
                mat.append(orbzero)
                continue
            msg = '{0:d}/{1:d} -> {2:s}'.format(
                j, sum_enbld, self.correctors.corrs[i].name)
            self._update_log(msg)
            _log.info(msg)
            j += 1

            if i < self._csorb.nr_ch:
                delta = self._meas_respmat_kick['ch']
            elif i < self._csorb.nr_ch + self._csorb.nr_cv:
                delta = self._meas_respmat_kick['cv']
            elif i < self._csorb.nr_corrs:
                delta = self._meas_respmat_kick['rf']

            kicks = _np.array([None, ] * nr_corrs, dtype=float)
            kicks[i] = orig_kicks[i] + delta/2
            self.correctors.apply_kicks(kicks)
            _sleep(self._meas_respmat_wait)
            orbp = self.orbit.get_orbit(reset=True)

            kicks[i] = orig_kicks[i] - delta/2
            self.correctors.apply_kicks(kicks)
            _sleep(self._meas_respmat_wait)
            orbn = self.orbit.get_orbit(reset=True)
            mat.append((orbp-orbn)/delta)

            kicks[i] = orig_kicks[i]
            self.correctors.apply_kicks(kicks)

        mat = _np.array(mat).T
        self.matrix.set_respmat(list(mat.ravel()))
        self.run_callbacks(
            'MeasRespMat-Mon', self._csorb.MeasRespMatMon.Completed)
        self._measuring_respmat = False
        msg = 'RespMat Measurement Completed!'
        self._update_log(msg)
        _log.info(msg)

    def _do_drive(self):
        self.run_callbacks('DriveState-Sts', self._csorb.DriveState.Closed)

        freqdiv = self._drive_divisor
        nrcycles = self._drive_nrcycles
        ampl = self._drive_amplitude
        phase = self._drive_phase / 180 * _np.pi
        corridx = self._drive_corr_index
        bpmidx = self._drive_bpm_index
        dr_type = self._drive_type

        x = _np.arange(freqdiv * nrcycles)
        if dr_type == self._csorb.DriveType.Sine:
            wfm = ampl*_np.sin(2*_np.pi/freqdiv * x + phase)
        elif dr_type == self._csorb.DriveType.Square:
            wfm = _np.zeros(x.size, dtype=float)
            wfm[wfm.size//2:-1] += ampl
        elif dr_type == self._csorb.DriveType.Impulse:
            wfm = _np.zeros(x.size, dtype=float)
            wfm[wfm.size//2] += ampl

        refkicks = self.correctors.get_strength()
        orb = self.orbit.get_orbit(synced=True)
        tim0 = _time()
        data = []
        for idx in range(x.size):
            if self._drive_state != self._csorb.DriveState.Closed:
                break
            if not self.havebeam:
                msg = 'ERR: Cannot Drive, We do not have stored beam!'
                self._update_log(msg)
                _log.info(msg)
                break

            orb = self.orbit.get_orbit(synced=True)
            kicks = refkicks.copy()
            tim = _time() - tim0
            kicks[corridx] += wfm[idx]
            ret = self.correctors.apply_kicks(kicks)
            data.extend([tim, kicks[corridx], orb[bpmidx]])

            if ret == -2:
                self._drive_state = self._csorb.DriveState.Open
                self.run_callbacks(
                    'DriveState-Sel', self._csorb.DriveState.Open)
                break
            elif ret == -1:
                # means that correctors are not ready yet
                # skip this iteration
                continue
        else:
            self._drive_state = self._csorb.DriveState.Open
            self.run_callbacks(
                'DriveState-Sel', self._csorb.DriveState.Open)

        ret = self.correctors.apply_kicks(refkicks)
        if len(data) < 6:
            data.extend((6-len(data)) * [0.0])
        self.run_callbacks('DriveData-Mon', data)
        msg = 'Drive Loop opened!'
        self._update_log(msg)
        _log.info(msg)
        self.run_callbacks('DriveState-Sts', self._csorb.DriveState.Open)

    def _do_auto_corr(self):
        self.run_callbacks('LoopState-Sts', self._csorb.LoopState.Closed)
        times, rets = [], []
        tim0 = _time()
        bpmsfreq = self._csorb.BPMsFreq
        zer = _np.zeros(self._csorb.nr_corrs, dtype=float)
        self._pid_errs = [zer, zer.copy(), zer.copy()]
        fofb = self.fofb
        refx0 = refy0 = None
        if fofb.connected:
            refx0 = fofb.refx
            refy0 = fofb.refy

        if self._loop_use_pssofb:
            msg = 'Turning on PSSOFB...'
            self._update_log(msg)
            _log.info(msg)
            self.correctors.use_pssofb = True
            msg = 'PSSOFB ready!'
            self._update_log(msg)
            _log.info(msg)

            if self.correctors.sync_kicks != self._csorb.CorrSync.Off:
                msg = 'Setting Trigger to listen to EVG Clock...'
                self._update_log(msg)
                _log.info(msg)
                self.run_callbacks('CorrSync-Sts', self._csorb.CorrSync.Clock)
                self.correctors.set_corrs_mode(self._csorb.CorrSync.Clock)
                msg = 'Trigger ready!'
                self._update_log(msg)
                _log.info(msg)

        tims = []
        while self._loop_state == self._csorb.LoopState.Closed:
            if not self.havebeam:
                msg = 'ERR: We do not have stored beam!'
                self._update_log(msg)
                _log.error(msg[5:])
                break
            if not self.is_amc_connected:
                msg = 'ERR: At least one AMC is not connected!'
                self._update_log(msg)
                _log.error(msg[5:])
                break
            if not self.is_amc_locked:
                msg = 'ERR: At least one AMC is not locked!'
                self._update_log(msg)
                _log.error(msg[5:])
                break
            itern = len(times)
            self.run_callbacks('LoopNumIters-Mon', itern)
            if itern >= self._loop_print_every_num_iter:
                self._LQTHREAD.put((
                    self._print_auto_corr_info, (times, rets, _time()-tim0)))
                times, rets = [], []
                tim0 = _time()

            interval = 1/self._loop_freq
            use_pssofb = self.correctors.use_pssofb
            norbs = 1
            if use_pssofb:
                norbs = max(int(bpmsfreq*interval), 1)
            elif tims:
                # if not pssofb wait for interval to be satisfied
                dtime = tims[0] - tims[-1]
                dtime += interval
                _sleep(max(dtime, 0))

            tims = []
            tims.append(_time())
            orb = self.orbit.get_orbit(synced=True)
            for i in range(1, norbs):
                interval = 1/self._loop_freq
                norbs_up = max(int(bpmsfreq*interval), 1)
                if i >= norbs_up:
                    break
                orb = self.orbit.get_orbit(synced=True)

            if self._tests:
                orb *= 0
                orb += _np.random.rand(orb.size)
                orb -= orb.mean()  # avoid RF integration error.
                orb *= 2 * 3  # Maximum orbit distortion of 3 um

            tims.append(_time())

            self._ref_corr_kicks = self.correctors.get_strength()
            tims.append(_time())

            orb = self._interact_with_fofb_in_calc_kicks(orb)

            dkicks = self.matrix.calc_kicks(orb)
            tims.append(_time())

            if not self._check_valid_orbit(orb):
                break

            dkicks = self._process_pid(dkicks, interval)

            kicks, dkicks = self._process_kicks(
                self._ref_corr_kicks, dkicks, apply_gain=False)
            if kicks is None:
                break

            kicks = self._interact_with_fofb_in_apply_kicks(
                kicks, dkicks, refx0, refy0)
            if kicks is None:
                break
            tims.append(_time())

            ret = self.correctors.apply_kicks(kicks)
            rets.append(ret)
            tims.append(_time())
            tims.append(tims[1])  # to compute total time - get_orbit
            times.append(tims)
            # if ret == -2:
            if ret < 0:  # change here for debug
                break
            elif ret == -1:
                # means that correctors are not ready yet
                # skip this iteration
                continue

        if self._loop_use_pssofb:
            msg = 'Turning off PSSOFB...'
            self._update_log(msg)
            _log.info(msg)
            self.correctors.use_pssofb = False
            msg = 'PSSOFB is off!'
            self._update_log(msg)
            _log.info(msg)

            if self.correctors.sync_kicks != self._csorb.CorrSync.Off:
                msg = 'Setting Trigger to listen to Event...'
                self._update_log(msg)
                _log.info(msg)
                self.run_callbacks('CorrSync-Sts', self._csorb.CorrSync.Event)
                self.correctors.set_corrs_mode(self._csorb.CorrSync.Event)
                msg = 'Trigger ready!'
                self._update_log(msg)
                _log.info(msg)

        if self._loop_state == self._csorb.LoopState.Closed:
            self._loop_state = self._csorb.LoopState.Open
            self.run_callbacks('LoopState-Sel', self._csorb.LoopState.Open)

        msg = 'Loop opened!'
        self._update_log(msg)
        _log.info(msg)
        self.run_callbacks('LoopState-Sts', self._csorb.LoopState.Open)

    def _process_pid(self, dkicks, interval):
        """Velocity algorithm of PID."""
        if dkicks is None:
            return None

        self._pid_errs.append(dkicks.copy())
        del self._pid_errs[0]

        gains = self._pid_gains
        errs = self._pid_errs
        nr_ch = self._csorb.nr_ch
        slcs = {'ch': slice(None, nr_ch), 'cv': slice(nr_ch, None)}
        if self.isring:
            slcs = {
                'ch': slice(None, nr_ch),
                'cv': slice(nr_ch, -1),
                'rf': slice(-1, None)}
        for pln in sorted(slcs.keys()):
            slc = slcs[pln]
            gin = gains[pln]
            kpt = gin['kp']
            kdt = gin['kd']/interval
            kit = gin['ki']*interval

            if self._tests:
                # Do not use integrators when testing without beam:
                kit = 0
                if pln == 'rf':
                    # Do not use RF when testing without beam:
                    kpt = kdt = 0

            qq0 = kpt + kdt + kit
            qq1 = -kpt - 2*kdt
            qq2 = kdt
            dkicks[slc] *= qq0
            dkicks[slc] += qq1*errs[-2][slc]  # previous error
            dkicks[slc] += qq2*errs[-3][slc]  # pre-previous error
        return dkicks

    def _print_auto_corr_info(self, times, rets, dtim):
        """."""
        self.run_callbacks('LoopEffectiveRate-Mon', len(times)/dtim)

        rets = _np.array(rets)
        ok_ = _np.sum(rets == 0) / rets.size * 100
        tout = _np.sum(rets == -1) / rets.size * 100
        bo_diff = rets > 0
        diff = _np.sum(bo_diff) / rets.size * 100
        _log.info('PERFORMANCE:')
        self.run_callbacks('LoopPerfItersOk-Mon', ok_)
        self.run_callbacks('LoopPerfItersTOut-Mon', tout)
        self.run_callbacks('LoopPerfItersDiff-Mon', diff)
        psmax = psavg = psstd = 0
        if diff:
            drets = rets[bo_diff]
            psmax = drets.max()
            psavg = drets.mean()
            psstd = drets.std()
        self.run_callbacks('LoopPerfDiffNrPSMax-Mon', psmax)
        self.run_callbacks('LoopPerfDiffNrPSAvg-Mon', psavg)
        self.run_callbacks('LoopPerfDiffNrPSStd-Mon', psstd)

        dtimes = _np.diff(times, axis=1).T * 1000
        dtimes[-1] *= -1
        max_ = dtimes.max(axis=1)
        min_ = dtimes.min(axis=1)
        avg_ = dtimes.mean(axis=1)
        std_ = dtimes.std(axis=1)
        labs = ['GetO', 'GetK', 'Calc', 'Proc', 'App', 'Tot']
        for i, lab in enumerate(labs):
            self.run_callbacks(f'LoopPerfTim{lab:s}Max-Mon', max_[i])
            self.run_callbacks(f'LoopPerfTim{lab:s}Min-Mon', min_[i])
            self.run_callbacks(f'LoopPerfTim{lab:s}Avg-Mon', avg_[i])
            self.run_callbacks(f'LoopPerfTim{lab:s}Std-Mon', std_[i])

    def _check_valid_orbit(self, orbit):
        conn = _np.array([bpm.connected for bpm in self._orbit.bpms])
        conn = _np.tile(conn, [2, ])
        enbl = self._matrix.bpm_enbllist
        nconn = ~conn & enbl
        if _np.any(nconn):
            names = self._csorb.bpm_names
            leng = len(names)
            for i, nco in enumerate(nconn):
                if nco:
                    msg = f'ERR: {names[i%leng]} not connected!'
                    self._update_log(msg)
                    _log.error(msg[5:])
            return False

        maxo = _np.abs(orbit[enbl]).max()
        if maxo > self._loop_max_orb_distortion:
            msg = 'ERR: Orbit distortion above threshold!'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        return True

    def _interact_with_fofb_in_calc_kicks(self, orb):
        fofb = self.fofb

        if self._donot_affect_fofb_bpms and fofb.loop_state:
            enbllist = _np.r_[fofb.bpmxenbl, fofb.bpmyenbl]
            orb[enbllist] = 0.0

        if self._project_onto_fofb_nullspace and fofb.loop_state:
            # this approach is similar to what is proposed by APS:
            # https://www.aps.anl.gov/sites/www.aps.anl.gov/files/APS-Uploads/Workshops/BES-Light-Sources/Nick%20Sereno%20-%20Fast%20Orbit%20Feedback%20at%20APS.pdf
            imat_fofb = fofb.invrespmat_mon
            imat_fofb[-1] *= 0  # RF correction is never applied by FOFB.
            orb -= _np.dot(fofb.respmat, _np.dot(imat_fofb, orb))
        return orb

    def _interact_with_fofb_in_apply_kicks(
            self, kicks, dkicks, refx=None, refy=None):
        fofb = self.fofb

        # if refx is None or refy is None:
        #     refx = fofb.refx
        #     refy = fofb.refy

        if self._update_fofb_reforb and fofb.loop_state:
            dorb = self.matrix.estimate_orbit_variation(dkicks)
            dorb *= self._update_fofb_reforb_perc
            # NOTE: According to my understanding of SOLEIL's paper on this
            # subject:
            # https://accelconf.web.cern.ch/d09/papers/mooc01.pdf
            # https://accelconf.web.cern.ch/d09/talks/mooc01_talk.pdf
            # this is what they do there:
            fofb.refx -= dorb[:dorb.size//2]
            fofb.refy -= dorb[dorb.size//2:]
            # But it seems this may also be a possibility:
            # fofb.refx = refx - dorb[:dorb.size//2]
            # fofb.refy = refy - dorb[dorb.size//2:]
            fofb.cmd_fofbctrl_syncreforb()

        if self._download_fofb_kicks and fofb.loop_state:
            # NOTE: Do not download kicks from correctors not in the loop:
            kickch = fofb.kickch_acc.copy()
            kickcv = fofb.kickcv_acc.copy()
            kickch[~fofb.chenbl] = 0
            kickcv[~fofb.cvenbl] = 0

            kicks_fofb = _np.r_[kickch, kickcv, 0]
            dorb = _np.dot(fofb.respmat, kicks_fofb)
            # NOTE: calc_kicks return the kicks to correct dorb, which means
            # that a minus sign is already applied by this method. To negate
            # this correction, we need an extra minus sign here:
            dkicks2 = self.matrix.calc_kicks(dorb)
            dkicks2 *= -self._download_fofb_kicks_perc

            kicks, dkicks2 = self._process_kicks(
                self._ref_corr_kicks, dkicks + dkicks2, apply_gain=False)
        return kicks

    def _calc_correction(self):
        msg = 'Getting the orbit.'
        self._update_log(msg)
        _log.info(msg)
        orb = self.orbit.get_orbit()

        if self.acc == 'SI':
            orb = self._interact_with_fofb_in_calc_kicks(orb)

        msg = 'Calculating kicks.'
        self._update_log(msg)
        _log.info(msg)
        self._ref_corr_kicks = self.correctors.get_strength()
        dkicks = self.matrix.calc_kicks(orb)
        if dkicks is not None:
            self._dtheta = dkicks
        msg = 'Kicks calculated!'
        self._update_log(msg)
        _log.info(msg)

    def _process_kicks(self, kicks, dkicks, apply_gain=True):
        if dkicks is None:
            return None, dkicks

        # keep track of which dkicks were originally different from zero:
        newkicks = _np.full(dkicks.shape, _np.nan, dtype=float)
        apply_idcs = ~_compare_kicks(dkicks, 0)
        if not apply_idcs.any():
            return newkicks, dkicks

        nr_ch = self._csorb.nr_ch
        slcs = {'ch': slice(None, nr_ch), 'cv': slice(nr_ch, None)}
        if self.isring:
            slcs = {
                'ch': slice(None, nr_ch),
                'cv': slice(nr_ch, -1),
                'rf': slice(-1, None)}
        for pln in sorted(slcs.keys()):
            slc = slcs[pln]
            idcs_pln = apply_idcs[slc]
            if not idcs_pln.any():
                continue
            dk_slc = dkicks[slc][idcs_pln]
            k_slc = kicks[slc][idcs_pln]
            fac1 = self._mancorr_gain[pln] if apply_gain else 1
            dk_slc *= fac1

            # Check if any kick is larger than the maximum allowed:
            ind = (_np.abs(k_slc) >= self._max_kick[pln]).nonzero()[0]
            if ind.size:
                msg = 'ERR: Kicks above MaxKick{0:s}.'.format(pln.upper())
                self._update_log(msg)
                _log.error(msg[5:])
                return None, dkicks

            # Check if any delta kick is larger the maximum allowed
            max_delta_kick = _np.max(_np.abs(dk_slc))
            fac2 = 1.0
            if max_delta_kick > self._max_delta_kick[pln]:
                fac2 = self._max_delta_kick[pln]/max_delta_kick
                dk_slc *= fac2
                percent = fac1 * fac2 * 100
                msg = 'WARN: reach MaxDeltaKick{0:s}. Using {1:5.2f}%'.format(
                    pln.upper(), percent)
                self._update_log(msg)
                _log.warning(msg[6:])

            # Check if any kick + delta kick is larger than the maximum allowed
            max_kick = _np.max(_np.abs(k_slc + dk_slc))
            fac3 = 1.0
            if max_kick > self._max_kick[pln]:
                que = _np.ones((2, k_slc.size), dtype=float)
                # perform the modulus inequality:
                que[0, :] = (-self._max_kick[pln] - k_slc) / dk_slc
                que[1, :] = (self._max_kick[pln] - k_slc) / dk_slc
                # since we know that any initial kick is lesser than max_kick
                # from the previous comparison, at this point each column of Q
                # has a positive and a negative value. We must consider only
                # the positive one and take the minimum value along the columns
                # to be the multiplicative factor:
                que = _np.max(que, axis=0)
                fac3 = min(_np.min(que), 1.0)
                if fac3 < 1e-4:
                    msg = f'ERR: Some {pln.upper():s} Corr is saturated.'
                    self._update_log(msg)
                    _log.error(msg[5:])
                    return None, dkicks
                dk_slc *= fac3
                percent = fac1 * fac2 * fac3 * 100
                msg = 'WARN: reach MaxKick{0:s}. Using {1:5.2f}%'.format(
                    pln.upper(), percent)
                self._update_log(msg)
                _log.warning(msg[6:])

            dkicks[slc][idcs_pln] = dk_slc

        newkicks[apply_idcs] = kicks[apply_idcs] + dkicks[apply_idcs]
        return newkicks, dkicks
