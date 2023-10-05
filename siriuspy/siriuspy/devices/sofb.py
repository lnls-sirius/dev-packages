"""."""

import time as _time

import numpy as _np

from ..sofb.csdev import SOFBFactory
from ..sofb.utils import si_calculate_bump as _si_calculate_bump
from .device import Device as _Device


class SOFB(_Device):
    """SOFB Device."""

    class DEVICES:
        """Devices names."""

        TB = 'TB-Glob:AP-SOFB'
        BO = 'BO-Glob:AP-SOFB'
        TS = 'TS-Glob:AP-SOFB'
        SI = 'SI-Glob:AP-SOFB'
        ALL = (TB, BO, TS, SI)

    def __new__(cls, devname, props2init='all'):
        """."""
        # check if device exists
        if devname not in SOFB.DEVICES.ALL:
            raise NotImplementedError(devname)

        # SOFB object
        data = SOFBFactory.create(devname[:2])

        if data.acc == 'SI':
            return SISOFB(devname, data, props2init=props2init)
        elif data.isring:
            return BOSOFB(devname, data, props2init=props2init)
        return TLSOFB(devname, data, props2init=props2init)


class TLSOFB(_Device):
    """SOFB Device."""

    PROPERTIES_DEFAULT = (
        'TrigAcqChan-Sel', 'TrigAcqChan-Sts', 'OrbStatus-Mon',
        'RespMat-SP', 'RespMat-RB', 'RespMat-Mon', 'InvRespMat-Mon',
        'KickCH-Mon', 'KickCV-Mon',
        'DeltaKickCH-Mon', 'DeltaKickCV-Mon',
        'DeltaKickCH-SP', 'DeltaKickCV-SP',
        'MaxDeltaKickCH-RB', 'MaxDeltaKickCV-RB',
        'MaxDeltaKickCH-SP', 'MaxDeltaKickCV-SP',
        'ManCorrGainCH-SP', 'ManCorrGainCV-SP',
        'ManCorrGainCH-RB', 'ManCorrGainCV-RB',
        'RefOrbX-SP', 'RefOrbY-SP',
        'RefOrbX-RB', 'RefOrbY-RB',
        'BPMXEnblList-SP', 'BPMYEnblList-SP',
        'BPMXEnblList-RB', 'BPMYEnblList-RB',
        'CHEnblList-SP', 'CVEnblList-SP',
        'CHEnblList-RB', 'CVEnblList-RB',
        'CalcDelta-Cmd', 'ApplyDelta-Cmd', 'SmoothReset-Cmd',
        'ApplyDelta-Mon',
        'SmoothNrPts-SP', 'SmoothNrPts-RB',
        'BufferCount-Mon',
        'TrigNrSamplesPre-SP',
        'TrigNrSamplesPre-RB',
        'TrigNrSamplesPost-SP',
        'TrigNrSamplesPost-RB',
        'SPassSum-Mon', 'SPassOrbX-Mon', 'SPassOrbY-Mon',
        'MeasRespMat-Cmd', 'MeasRespMat-Mon',
        'MeasRespMatKickCH-SP', 'MeasRespMatKickCH-RB',
        'MeasRespMatKickCV-SP', 'MeasRespMatKickCV-RB',
        'MeasRespMatWait-SP', 'MeasRespMatWait-RB',
        'NrSingValues-Mon', 'MinSingValue-SP', 'MinSingValue-RB',
        'TrigAcqCtrl-Sel', 'TrigAcqCtrl-Sts', 'TrigAcqConfig-Cmd',
        'SyncBPMs-Cmd',
        )

    _default_timeout = 10  # [s]
    _default_timeout_respm = 2 * 60 * 60  # [s]
    _default_timeout_kick_apply = 2  # [s]

    def __init__(self, devname, data=None, props2init='all'):
        """."""
        # check if device exists
        if devname not in SOFB.DEVICES.ALL:
            raise NotImplementedError(devname)

        # SOFB object
        self._data = data or SOFBFactory.create(devname[:2])
        # call base class constructor
        super().__init__(devname, props2init=props2init)

    @property
    def data(self):
        """."""
        return self._data

    @property
    def trigchannel(self):
        """."""
        return self['TrigAcqChan-Sts']

    @trigchannel.setter
    def trigchannel(self, value):
        self._enum_setter(
            'TrigAcqChan-Sel', value, self._data.TrigAcqChan)

    @property
    def respmat(self):
        """Raw response matrix."""
        return self['RespMat-RB'].reshape(self._data.nr_bpms*2, -1)

    @respmat.setter
    def respmat(self, mat):
        self['RespMat-SP'] = _np.array(mat).ravel()

    @property
    def respmat_mon(self):
        """Applied response matrix."""
        return self['RespMat-Mon'].reshape(self._data.nr_bpms*2, -1)

    @property
    def invrespmat(self):
        """Inverse response matrix."""
        return self['InvRespMat-Mon'].reshape(-1, self._data.nr_bpms*2)

    @property
    def trigchannel_str(self):
        """."""
        return self._data.TrigAcqChan._fields[self['TrigAcqChan-Sts']]

    @property
    def sp_trajx(self):
        """."""
        return self['SPassOrbX-Mon']

    @property
    def sp_trajy(self):
        """."""
        return self['SPassOrbY-Mon']

    @property
    def sp_sum(self):
        """."""
        return self['SPassSum-Mon']

    @property
    def trajx(self):
        """."""
        return self.sp_trajx

    @property
    def trajy(self):
        """."""
        return self.sp_trajy

    @property
    def sum(self):
        """."""
        return self.sp_sum

    @property
    def kickch(self):
        """."""
        return self['KickCH-Mon']

    @property
    def kickcv(self):
        """."""
        return self['KickCV-Mon']

    @property
    def deltakickch(self):
        """."""
        return self['DeltaKickCH-Mon']

    @deltakickch.setter
    def deltakickch(self, value):
        """."""
        self['DeltaKickCH-SP'] = value

    @property
    def deltakickcv(self):
        """."""
        return self['DeltaKickCV-Mon']

    @deltakickcv.setter
    def deltakickcv(self, value):
        """."""
        self['DeltaKickCV-SP'] = value

    @property
    def maxdeltakickch(self):
        """."""
        return self['MaxDeltaKickCH-RB']

    @maxdeltakickch.setter
    def maxdeltakickch(self, value):
        """."""
        self['MaxDeltaKickCH-SP'] = value

    @property
    def maxdeltakickcv(self):
        """."""
        return self['MaxDeltaKickCV-RB']

    @maxdeltakickcv.setter
    def maxdeltakickcv(self, value):
        """."""
        self['MaxDeltaKickCV-SP'] = value

    @property
    def mancorrgainch(self):
        """."""
        return self['ManCorrGainCH-RB']

    @mancorrgainch.setter
    def mancorrgainch(self, value):
        """."""
        self['ManCorrGainCH-SP'] = value

    @property
    def mancorrgaincv(self):
        """."""
        return self['ManCorrGainCV-RB']

    @mancorrgaincv.setter
    def mancorrgaincv(self, value):
        """."""
        self['ManCorrGainCV-SP'] = value

    @property
    def refx(self):
        """."""
        return self['RefOrbX-RB']

    @refx.setter
    def refx(self, value):
        """."""
        self['RefOrbX-SP'] = value

    @property
    def refy(self):
        """."""
        return self['RefOrbY-RB']

    @refy.setter
    def refy(self, value):
        """."""
        self['RefOrbY-SP'] = value

    @property
    def bpmxenbl(self):
        """."""
        return _np.array(self['BPMXEnblList-RB'], dtype=bool)

    @bpmxenbl.setter
    def bpmxenbl(self, value):
        """."""
        self['BPMXEnblList-SP'] = value

    @property
    def bpmyenbl(self):
        """."""
        return _np.array(self['BPMYEnblList-RB'], dtype=bool)

    @bpmyenbl.setter
    def bpmyenbl(self, value):
        """."""
        self['BPMYEnblList-SP'] = value

    @property
    def chenbl(self):
        """."""
        return _np.array(self['CHEnblList-RB'], dtype=bool)

    @chenbl.setter
    def chenbl(self, value):
        """."""
        self['CHEnblList-SP'] = value

    @property
    def cvenbl(self):
        """."""
        return _np.array(self['CVEnblList-RB'], dtype=bool)

    @cvenbl.setter
    def cvenbl(self, value):
        """."""
        self['CVEnblList-SP'] = value

    @property
    def buffer_count(self):
        """."""
        return self['BufferCount-Mon']

    @property
    def nr_points(self):
        """."""
        return self['SmoothNrPts-RB']

    @nr_points.setter
    def nr_points(self, value):
        """."""
        self['SmoothNrPts-SP'] = int(value)

    @property
    def nr_singvals(self):
        """."""
        return self['NrSingValues-Mon']

    @property
    def singval_min(self):
        """."""
        return self['MinSingValue-RB']

    @singval_min.setter
    def singval_min(self, value):
        """."""
        self['MinSingValue-SP'] = value

    @property
    def trigacq(self):
        """."""
        return self['TrigAcqCtrl-Sts']

    @property
    def trigsamplepre(self):
        """."""
        return self['TrigNrSamplesPre-RB']

    @trigsamplepre.setter
    def trigsamplepre(self, value):
        """."""
        self['TrigNrSamplesPre-SP'] = int(value)

    @property
    def trigsamplepost(self):
        """."""
        return self['TrigNrSamplesPost-RB']

    @trigsamplepost.setter
    def trigsamplepost(self, value):
        """."""
        self['TrigNrSamplesPost-SP'] = int(value)

    def cmd_reset(self):
        """."""
        prop = 'SmoothReset-Cmd'
        val = self[prop]
        self[prop] = 1
        return self._wait(prop, val+1)

    def cmd_calccorr(self):
        """."""
        prop = 'CalcDelta-Cmd'
        val = self[prop]
        self[prop] = 1
        return self._wait(prop, val+1)

    def cmd_applycorr_ch(self):
        """."""
        prop = 'ApplyDelta-Cmd'
        val = self[prop]
        self[prop] = self._data.ApplyDelta.CH
        return self._wait(prop, val+1)

    def cmd_applycorr_cv(self):
        """."""
        prop = 'ApplyDelta-Cmd'
        val = self[prop]
        self[prop] = self._data.ApplyDelta.CV
        return self._wait(prop, val+1)

    def cmd_applycorr_rf(self):
        """."""
        prop = 'ApplyDelta-Cmd'
        val = self[prop]
        self[prop] = self._data.ApplyDelta.RF
        return self._wait(prop, val+1)

    def cmd_applycorr_all(self):
        """."""
        prop = 'ApplyDelta-Cmd'
        val = self[prop]
        self[prop] = self._data.ApplyDelta.All
        return self._wait(prop, val+1)

    def cmd_measrespmat_start(self):
        """."""
        prop = 'MeasRespMat-Cmd'
        val = self[prop]
        self[prop] = 0
        return self._wait(prop, val+1)

    def cmd_measrespmat_stop(self):
        """."""
        prop = 'MeasRespMat-Cmd'
        val = self[prop]
        self[prop] = 1
        return self._wait(prop, val+1)

    def cmd_measrespmat_reset(self):
        """."""
        prop = 'MeasRespMat-Cmd'
        val = self[prop]
        self[prop] = 2
        return self._wait(prop, val+1)

    def cmd_trigacq_start(self, timeout=10):
        """."""
        self['TrigAcqCtrl-Sel'] = 'Start'
        ret = self._wait(
            'TrigAcqCtrl-Sts', self._data.TrigAcqCtrl.Start, timeout=timeout)
        if not ret:
            return False
        _time.sleep(0.6)  # Status PV updates at 2Hz
        return self.wait_orb_status_ok(timeout=timeout)

    def cmd_trigacq_stop(self, timeout=10):
        """."""
        self['TrigAcqCtrl-Sel'] = 'Stop'
        ret = self._wait(
            'TrigAcqCtrl-Sts', self._data.TrigAcqCtrl.Stop, timeout=timeout)
        if not ret:
            return False
        _time.sleep(0.6)  # Status PV updates at 2Hz
        return self.wait_orb_status_ok(timeout=timeout)

    def cmd_trigacq_abort(self, timeout=10):
        """."""
        self['TrigAcqCtrl-Sel'] = 'Abort'
        ret = self._wait(
            'TrigAcqCtrl-Sts', self._data.TrigAcqCtrl.Abort, timeout=timeout)
        if not ret:
            return False
        _time.sleep(0.6)  # Status PV updates at 2Hz
        return self.wait_orb_status_ok(timeout=timeout)

    def cmd_trigacq_config(self, timeout=10):
        """."""
        self['TrigAcqConfig-Cmd'] = 1
        return self.wait_orb_status_ok(timeout=timeout)

    @property
    def applydeltakick_mon(self):
        """."""
        return self['ApplyDelta-Mon']

    @property
    def measrespmat_mon(self):
        """."""
        return self['MeasRespMat-Mon']

    @property
    def measrespmat_kickch(self):
        """."""
        return self['MeasRespMatKickCH-RB']

    @measrespmat_kickch.setter
    def measrespmat_kickch(self, value):
        self['MeasRespMatKickCH-SP'] = value

    @property
    def measrespmat_kickcv(self):
        """."""
        return self['MeasRespMatKickCV-RB']

    @measrespmat_kickcv.setter
    def measrespmat_kickcv(self, value):
        self['MeasRespMatKickCV-SP'] = value

    @property
    def measrespmat_wait(self):
        """."""
        return self['MeasRespMatWait-RB']

    @measrespmat_wait.setter
    def measrespmat_wait(self, value):
        self['MeasRespMatWait-SP'] = value

    def correct_orbit_manually(self, nr_iters=10, residue=5):
        """."""
        self.cmd_turn_off_autocorr()
        for i in range(nr_iters):
            resx = self.orbx - self.refx
            resy = self.orby - self.refy
            resx = resx[self.bpmxenbl.nonzero()[0]]
            resy = resy[self.bpmyenbl.nonzero()[0]]
            resx = _np.sqrt(_np.sum(resx*resx)/resx.size)
            resy = _np.sqrt(_np.sum(resy*resy)/resy.size)
            if resx < residue and resy < residue:
                break
            self.wait_buffer()
            self.cmd_calccorr()
            self.cmd_applycorr_all()
            self.wait_apply_delta_kick()
            self.cmd_reset()
        return i, resx, resy

    def wait_buffer(self, timeout=None):
        """."""
        timeout = timeout or self._default_timeout
        return self._wait(
            'BufferCount-Mon', self.nr_points, timeout=timeout, comp='ge')

    def wait_apply_delta_kick(self, timeout=None):
        """."""
        def_timeout = min(1.05*self.deltakickrf, self.maxdeltakickrf) // 20
        def_timeout = max(self._default_timeout_kick_apply, def_timeout)
        timeout = timeout or def_timeout
        return self._wait(
            'ApplyDelta-Mon', self._data.ApplyDeltaMon.Applying,
            timeout=timeout, comp='ne')

    def wait_respm_meas(self, timeout=None):
        """."""
        timeout = timeout or self._default_timeout_respm
        return self._wait(
            'MeasRespMat-Mon', self._data.MeasRespMatMon.Measuring,
            timeout=timeout, comp='ne')

    def wait_orb_status_ok(self, timeout=10):
        """."""
        return self._wait('OrbStatus-Mon', 0, timeout=timeout)

    def cmd_sync_bpms(self):
        """Synchronize BPMs."""
        prop = 'SyncBPMs-Cmd'
        val = self[prop]
        self[prop] = 1
        return self._wait(prop, val+1)


class BOSOFB(TLSOFB):
    """SOFB Device."""

    PROPERTIES_DEFAULT = TLSOFB.PROPERTIES_DEFAULT + (
        'MTurnAcquire-Cmd',
        'MTurnSum-Mon', 'MTurnOrbX-Mon', 'MTurnOrbY-Mon',
        'MTurnIdxOrbX-Mon', 'MTurnIdxOrbY-Mon', 'MTurnIdxSum-Mon',
        'MTurnTime-Mon',
        )

    @property
    def mt_trajx(self):
        """."""
        return self['MTurnOrbX-Mon']

    @property
    def mt_trajy(self):
        """."""
        return self['MTurnOrbY-Mon']

    @property
    def mt_sum(self):
        """."""
        return self['MTurnSum-Mon']

    @property
    def mt_time(self):
        """."""
        return self['MTurnTime-Mon']

    @property
    def mt_trajx_idx(self):
        """."""
        return self['MTurnIdxOrbX-Mon']

    @property
    def mt_trajy_idx(self):
        """."""
        return self['MTurnIdxOrbY-Mon']

    @property
    def mt_sum_idx(self):
        """."""
        return self['MTurnIdxSum-Mon']

    @property
    def trajx(self):
        """."""
        return self.mt_trajx_idx

    @property
    def trajy(self):
        """."""
        return self.mt_trajy_idx

    @property
    def sum(self):
        """."""
        return self.mt_sum_idx

    def cmd_mturn_acquire(self):
        """."""
        prop = 'MTurnAcquire-Cmd'
        val = self[prop]
        self[prop] = 1
        return self._wait(prop, val+1)


class SISOFB(BOSOFB):
    """SOFB Device."""

    PROPERTIES_DEFAULT = BOSOFB.PROPERTIES_DEFAULT + (
        'SOFBMode-Sel', 'SOFBMode-Sts',
        'KickRF-Mon',
        'DeltaKickRF-Mon', 'DeltaKickRF-SP',
        'MaxDeltaKickRF-RB', 'MaxDeltaKickRF-SP',
        'ManCorrGainRF-SP', 'ManCorrGainRF-RB',
        'MeasRespMatKickRF-SP', 'MeasRespMatKickRF-RB',
        'RFEnbl-Sel', 'RFEnbl-Sts',
        'SlowOrbX-Mon', 'SlowOrbY-Mon',
        'LoopState-Sts', 'LoopState-Sel',
        'CorrSync-Sts', 'CorrSync-Sel',
        'LoopPIDKpCH-SP', 'LoopPIDKiCH-SP', 'LoopPIDKdCH-SP',
        'LoopPIDKpCH-RB', 'LoopPIDKiCH-RB', 'LoopPIDKdCH-RB',
        'LoopPIDKpCV-SP', 'LoopPIDKiCV-SP', 'LoopPIDKdCV-SP',
        'LoopPIDKpCV-RB', 'LoopPIDKiCV-RB', 'LoopPIDKdCV-RB',
        'LoopPIDKpRF-SP', 'LoopPIDKiRF-SP', 'LoopPIDKdRF-SP',
        'LoopPIDKpRF-RB', 'LoopPIDKiRF-RB', 'LoopPIDKdRF-RB',
        'DriveFreqDivisor-SP', 'DriveFreqDivisor-RB', 'DriveFrequency-Mon',
        'DriveNrCycles-SP', 'DriveNrCycles-RB', 'DriveDuration-Mon',
        'DriveAmplitude-SP', 'DriveAmplitude-RB',
        'DrivePhase-SP', 'DrivePhase-RB',
        'DriveCorrIndex-SP', 'DriveCorrIndex-RB',
        'DriveBPMIndex-SP', 'DriveBPMIndex-RB',
        'DriveType-Sel', 'DriveType-Sts',
        'DriveState-Sel', 'DriveState-Sts',
        'DriveData-Mon',
        )

    @property
    def opmode(self):
        """."""
        return self['SOFBMode-Sts']

    @opmode.setter
    def opmode(self, value):
        self._enum_setter(
            'SOFBMode-Sel', value, self._data.SOFBMode)

    @property
    def opmode_str(self):
        """."""
        return self._data.SOFBMode._fields[self['SOFBMode-Sts']]

    def cmd_change_opmode_to_multiturn(self, timeout=10):
        """."""
        mode = self._data.SOFBMode.MultiTurn
        self.opmode = mode
        ret = self._wait('SOFBMode-Sts', mode, timeout=timeout)
        if not ret:
            return False
        _time.sleep(1)  # Status PV updates at 2Hz
        return self.wait_orb_status_ok(timeout=timeout)

    def cmd_change_opmode_to_sloworb(self, timeout=10):
        """."""
        mode = self._data.SOFBMode.SlowOrb
        self.opmode = mode
        ret = self._wait('SOFBMode-Sts', mode, timeout=timeout)
        if not ret:
            return False
        _time.sleep(0.6)  # Status PV updates at 2Hz
        return self.wait_orb_status_ok(timeout=timeout)

    @property
    def loop_pid_ch_kp(self):
        """Loop PID Kp parameter for CH."""
        return self['LoopPIDKpCH-RB']

    @loop_pid_ch_kp.setter
    def loop_pid_ch_kp(self, value):
        self['LoopPIDKpCH-SP'] = value

    @property
    def loop_pid_ch_ki(self):
        """Loop PID Ki parameter for CH."""
        return self['LoopPIDKiCH-RB']

    @loop_pid_ch_ki.setter
    def loop_pid_ch_ki(self, value):
        self['LoopPIDKiCH-SP'] = value

    @property
    def loop_pid_ch_kd(self):
        """Loop PID Kd parameter for CH."""
        return self['LoopPIDKdCH-RB']

    @loop_pid_ch_kd.setter
    def loop_pid_ch_kd(self, value):
        self['LoopPIDKdCH-SP'] = value

    @property
    def loop_pid_cv_kp(self):
        """Loop PID Kp parameter for CV."""
        return self['LoopPIDKpCV-RB']

    @loop_pid_cv_kp.setter
    def loop_pid_cv_kp(self, value):
        self['LoopPIDKpCV-SP'] = value

    @property
    def loop_pid_cv_ki(self):
        """Loop PID Ki parameter for CV."""
        return self['LoopPIDKiCV-RB']

    @loop_pid_cv_ki.setter
    def loop_pid_cv_ki(self, value):
        self['LoopPIDKiCV-SP'] = value

    @property
    def loop_pid_cv_kd(self):
        """Loop PID Kd parameter for CV."""
        return self['LoopPIDKdCV-RB']

    @loop_pid_cv_kd.setter
    def loop_pid_cv_kd(self, value):
        self['LoopPIDKdCV-SP'] = value

    @property
    def loop_pid_rf_kp(self):
        """Loop PID Kp parameter for RF."""
        return self['LoopPIDKpRF-RB']

    @loop_pid_rf_kp.setter
    def loop_pid_rf_kp(self, value):
        self['LoopPIDKpRF-SP'] = value

    @property
    def loop_pid_rf_ki(self):
        """Loop PID Ki parameter for RF."""
        return self['LoopPIDKiRF-RB']

    @loop_pid_rf_ki.setter
    def loop_pid_rf_ki(self, value):
        self['LoopPIDKiRF-SP'] = value

    @property
    def loop_pid_rf_kd(self):
        """Loop PID Kd parameter for RF."""
        return self['LoopPIDKdRF-RB']

    @loop_pid_rf_kd.setter
    def loop_pid_rf_kd(self, value):
        self['LoopPIDKdRF-SP'] = value

    @property
    def drivests(self):
        """."""
        return self['DriveState-Sts']

    @property
    def drivetype(self):
        """."""
        return self['DriveType-Sts']

    @drivetype.setter
    def drivetype(self, value):
        self._enum_setter(
            'DriveType-Sel', value, self._data.DriveType)

    @property
    def drivetype_str(self):
        """."""
        return self._data.DriveType._fields[self['DriveType-Sts']]

    @property
    def drivefreqdivisor(self):
        """."""
        return self['DriveFreqDivisor-RB']

    @drivefreqdivisor.setter
    def drivefreqdivisor(self, value):
        """."""
        self['DriveFreqDivisor-SP'] = value

    @property
    def drivefrequency_mon(self):
        """."""
        return self['DriveFrequency-Mon']

    @property
    def drivenrcycles(self):
        """."""
        return self['DriveNrCycles-RB']

    @drivenrcycles.setter
    def drivenrcycles(self, value):
        """."""
        self['DriveNrCycles-SP'] = value

    @property
    def driveduration_mon(self):
        """."""
        return self['DriveDuration-Mon']

    @property
    def driveamplitude(self):
        """."""
        return self['DriveAmplitude-RB']

    @driveamplitude.setter
    def driveamplitude(self, value):
        """."""
        self['DriveAmplitude-SP'] = value

    @property
    def drivephase(self):
        """."""
        return self['DrivePhase-RB']

    @drivephase.setter
    def drivephase(self, value):
        """."""
        self['DrivePhase-SP'] = value

    @property
    def drivecorridx(self):
        """."""
        return self['DriveCorrIndex-RB']

    @drivecorridx.setter
    def drivecorridx(self, value):
        """."""
        self['DriveCorrIndex-SP'] = value

    @property
    def drivebpmidx(self):
        """."""
        return self['DriveBPMIndex-RB']

    @drivebpmidx.setter
    def drivebpmidx(self, value):
        """."""
        self['DriveBPMIndex-SP'] = value

    @property
    def drivedata_time(self):
        """."""
        return self['DriveData-Mon'][::3]

    @property
    def drivedata_corr(self):
        """."""
        return self['DriveData-Mon'][1::3]

    @property
    def drivedata_bpm(self):
        """."""
        return self['DriveData-Mon'][2::3]

    @property
    def orbx(self):
        """."""
        return self['SlowOrbX-Mon'] if self._data.isring else None

    @property
    def orby(self):
        """."""
        return self['SlowOrbY-Mon'] if self._data.isring else None

    @property
    def kickrf(self):
        """."""
        return self['KickRF-Mon']

    @property
    def deltakickrf(self):
        """."""
        return self['DeltaKickRF-Mon']

    @deltakickrf.setter
    def deltakickrf(self, value):
        """."""
        self['DeltaKickRF-SP'] = value

    @property
    def maxdeltakickrf(self):
        """."""
        return self['MaxDeltaKickRF-RB']

    @maxdeltakickrf.setter
    def maxdeltakickrf(self, value):
        """."""
        self['MaxDeltaKickRF-SP'] = value

    @property
    def mancorrgainrf(self):
        """."""
        return self['ManCorrGainRF-RB']

    @mancorrgainrf.setter
    def mancorrgainrf(self, value):
        """."""
        self['ManCorrGainRF-SP'] = value

    @property
    def rfenbl(self):
        """."""
        if self._data.acc_idx == self._data.Rings.SI:
            return bool(self['RFEnbl-Sts'])

    @rfenbl.setter
    def rfenbl(self, value):
        """."""
        if self._data.acc_idx == self._data.Rings.SI:
            self['RFEnbl-Sel'] = value

    @property
    def measrespmat_kickrf(self):
        """."""
        return self['MeasRespMatKickRF-RB']

    @measrespmat_kickrf.setter
    def measrespmat_kickrf(self, value):
        self['MeasRespMatKickRF-SP'] = value

    @property
    def autocorrsts(self):
        """."""
        return self['LoopState-Sts']

    def cmd_turn_on_autocorr(self, timeout=None):
        """."""
        timeout = timeout or self._default_timeout
        if self.autocorrsts == self._data.LoopState.Closed:
            return True
        self['LoopState-Sel'] = self._data.LoopState.Closed
        return self._wait(
            'LoopState-Sts', self._data.LoopState.Closed, timeout=timeout)

    def cmd_turn_off_autocorr(self, timeout=None):
        """."""
        timeout = timeout or self._default_timeout
        if self.autocorrsts == self._data.LoopState.Open:
            return True
        self['LoopState-Sel'] = self._data.LoopState.Open
        return self._wait(
            'LoopState-Sts', self._data.LoopState.Open, timeout=timeout)

    @property
    def synckicksts(self):
        """Correction syncronization status."""
        return self['CorrSync-Sts']

    @synckicksts.setter
    def synckicksts(self, value):
        self._enum_setter('CorrSync-Sel', value, self._data.CorrSync)

    @property
    def synckicksts_str(self):
        """Correction syncronization status enum string."""
        return self._data.CorrSync._fields[self['CorrSync-Sts']]

    def cmd_turn_off_synckick(self, timeout=None):
        """Turn off correction synchronization."""
        timeout = timeout or self._default_timeout
        if self.synckicksts == self._data.CorrSync.Off:
            return True
        self['CorrSync-Sel'] = self._data.CorrSync.Off
        return self._wait(
            'CorrSync-Sts', self._data.CorrSync.Off, timeout=timeout)

    def cmd_turn_on_drive(self, timeout=None):
        """."""
        timeout = timeout or self._default_timeout
        if self.drivests == self._data.DriveState.Closed:
            return True
        self['DriveState-Sel'] = self._data.DriveState.Closed
        return self._wait(
            'DriveState-Sts', self._data.DriveState.Closed, timeout=timeout)

    def cmd_turn_off_drive(self, timeout=None):
        """."""
        timeout = timeout or self._default_timeout
        if self.drivests == self._data.DriveState.Open:
            return True
        self['DriveState-Sel'] = self._data.DriveState.Open
        return self.wait_drive(timeout=timeout)

    def wait_drive(self, timeout=None):
        """."""
        timeout = timeout or self._default_timeout_respm
        return self._wait(
            'DriveState-Sts', self._data.DriveState.Open, timeout=timeout)

    @staticmethod
    def si_calculate_bumps(orbx, orby, subsec, agx=0, agy=0, psx=0, psy=0):
        """."""
        return _si_calculate_bump(
            orbx, orby, subsec, agx=agx, agy=agy, psx=psx, psy=psy)

    @property
    def trajx(self):
        """."""
        if self.opmode == self._data.SOFBMode.MultiTurn:
            return self.mt_trajx_idx
        return self.sp_trajx

    @property
    def trajy(self):
        """."""
        if self.opmode == self._data.SOFBMode.MultiTurn:
            return self.mt_trajy_idx
        return self.sp_trajy

    @property
    def sum(self):
        """."""
        if self.opmode == self._data.SOFBMode.MultiTurn:
            return self.mt_sum_idx
        return self.sp_sum
