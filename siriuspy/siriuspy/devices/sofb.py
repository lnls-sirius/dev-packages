"""."""

import time as _time

import numpy as _np

from ..sofb.csdev import SOFBFactory
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

    _propty_tmpl = (
        'SOFBMode-Sel', 'SOFBMode-Sts',
        'TrigAcqChan-Sel', 'TrigAcqChan-Sts',
        'RespMat-SP', 'RespMat-RB',
        'KickCH-Mon', 'KickCV-Mon',
        'DeltaKickCH-Mon', 'DeltaKickCV-Mon',
        'DeltaKickCH-SP', 'DeltaKickCV-SP',
        'ManCorrGainCH-SP', 'ManCorrGainCV-SP',
        'ManCorrGainCH-RB', 'ManCorrGainCV-RB',
        'RefOrbX-SP', 'RefOrbY-SP',
        'RefOrbX-RB', 'RefOrbY-RB',
        'BPMXEnblList-SP', 'BPMYEnblList-SP',
        'BPMXEnblList-RB', 'BPMYEnblList-RB',
        'CHEnblList-SP', 'CVEnblList-SP',
        'CHEnblList-RB', 'CVEnblList-RB',
        'RFEnbl-Sel', 'RFEnbl-Sts',
        'CalcDelta-Cmd', 'ApplyDelta-Cmd', 'SmoothReset-Cmd',
        'SmoothNrPts-SP', 'SmoothNrPts-RB',
        'BufferCount-Mon',
        'TrigNrSamplesPost-SP',
        'TrigNrSamplesPost-RB',
        'LoopState-Sts', 'LoopState-Sel',
        'SPassSum-Mon', 'SPassOrbX-Mon', 'SPassOrbY-Mon',
        'MeasRespMat-Cmd', 'MeasRespMat-Mon',
        'MeasRespMatKickCH-SP', 'MeasRespMatKickCH-RB',
        'MeasRespMatKickCV-SP', 'MeasRespMatKickCV-RB',
        'MeasRespMatKickRF-SP', 'MeasRespMatKickRF-RB',
        'MeasRespMatWait-SP', 'MeasRespMatWait-RB',
        # properties used only for ring-type accelerators:
        'MTurnAcquire-Cmd',
        'SlowOrbX-Mon', 'SlowOrbY-Mon',
        'MTurnSum-Mon', 'MTurnOrbX-Mon', 'MTurnOrbY-Mon',
        'MTurnIdxOrbX-Mon', 'MTurnIdxOrbY-Mon', 'MTurnIdxSum-Mon',
        'MTurnTime-Mon')

    _default_timeout = 10  # [s]
    _default_timeout_respm = 2 * 60 * 60  # [s]

    def __init__(self, devname):
        """."""
        # check if device exists
        if devname not in SOFB.DEVICES.ALL:
            raise NotImplementedError(devname)

        # SOFB object
        self.data = SOFBFactory.create(devname[:2])

        propts = SOFB._propty_tmpl
        if not self.data.isring:
            propts = [p for p in propts if not p.startswith(('MTurn', 'Slow'))]

        # call base class constructor
        super().__init__(devname, properties=propts)

    @property
    def opmode(self):
        """."""
        return self['SOFBMode-Sts']

    @opmode.setter
    def opmode(self, value):
        if value is None:
            return
        if isinstance(value, str) and value in self.data.SOFBMode._fields:
            self['SOFBMode-Sel'] = self.data.SOFBMode._fields.index(value)
        elif int(value) in self.data.SOFBMode:
            self['SOFBMode-Sel'] = int(value)

    @property
    def opmode_str(self):
        """."""
        return self.data.SOFBMode._fields[self['SOFBMode-Sts']]

    @property
    def trigchannel(self):
        """."""
        return self['TrigAcqChan-Sts']

    @trigchannel.setter
    def trigchannel(self, value):
        if value is None:
            return
        if isinstance(value, str) and value in self.data.TrigAcqChan._fields:
            self['TrigAcqChan-Sel'] = \
                self.data.TrigAcqChan._fields.index(value)
        elif int(value) in self.data.TrigAcqChan:
            self['TrigAcqChan-Sel'] = int(value)

    @property
    def respmat(self):
        """."""
        return self['RespMat-RB']

    @respmat.setter
    def respmat(self, mat):
        """."""
        self['RespMat-SP'] = _np.array(mat)

    @property
    def trigchannel_str(self):
        """."""
        return self.data.TrigAcqChan._fields[self['TrigAcqChan-Sts']]

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
    def mt_trajx(self):
        """."""
        return self['MTurnOrbX-Mon'] if self.data.isring else None

    @property
    def mt_trajy(self):
        """."""
        return self['MTurnOrbY-Mon'] if self.data.isring else None

    @property
    def mt_sum(self):
        """."""
        return self['MTurnSum-Mon'] if self.data.isring else None

    @property
    def mt_time(self):
        """."""
        return self['MTurnTime-Mon'] if self.data.isring else None

    @property
    def mt_trajx_idx(self):
        """."""
        return self['MTurnIdxOrbX-Mon'] if self.data.isring else None

    @property
    def mt_trajy_idx(self):
        """."""
        return self['MTurnIdxOrbY-Mon'] if self.data.isring else None

    @property
    def mt_sum_idx(self):
        """."""
        return self['MTurnIdxSum-Mon'] if self.data.isring else None

    @property
    def trajx(self):
        """."""
        if self.data.isring and self.opmode == self.data.SOFBMode.MultiTurn:
            return self.mt_trajx_idx
        return self.sp_trajx

    @property
    def trajy(self):
        """."""
        if self.data.isring and self.opmode == self.data.SOFBMode.MultiTurn:
            return self.mt_trajy_idx
        return self.sp_trajy

    @property
    def sum(self):
        """."""
        if self.data.isring and self.opmode == self.data.SOFBMode.MultiTurn:
            return self.mt_sum_idx
        return self.sp_sum

    @property
    def orbx(self):
        """."""
        return self['SlowOrbX-Mon'] if self.data.isring else None

    @property
    def orby(self):
        """."""
        return self['SlowOrbY-Mon'] if self.data.isring else None

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
        return self['BPMXEnblList-RB']

    @bpmxenbl.setter
    def bpmxenbl(self, value):
        """."""
        self['BPMXEnblList-SP'] = value

    @property
    def bpmyenbl(self):
        """."""
        return self['BPMYEnblList-RB']

    @bpmyenbl.setter
    def bpmyenbl(self, value):
        """."""
        self['BPMYEnblList-SP'] = value

    @property
    def chenbl(self):
        """."""
        return self['CHEnblList-RB']

    @chenbl.setter
    def chenbl(self, value):
        """."""
        self['CHEnblList-SP'] = value

    @property
    def cvenbl(self):
        """."""
        return self['CVEnblList-RB']

    @cvenbl.setter
    def cvenbl(self, value):
        """."""
        self['CVEnblList-SP'] = value

    @property
    def rfenbl(self):
        """."""
        dta = self.data
        return self['RFEnbl-Sts'] if dta.acc_idx == dta.Rings.SI else None

    @rfenbl.setter
    def rfenbl(self, value):
        """."""
        if self.data.acc_idx == self.data.Rings.SI:
            self['RFEnbl-Sel'] = value

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
    def trigsample(self):
        """."""
        return self['TrigNrSamplesPost-RB']

    @trigsample.setter
    def trigsample(self, value):
        """."""
        self['TrigNrSamplesPost-SP'] = int(value)

    def cmd_mturn_acquire(self):
        """."""
        self['MTurnAcquire-Cmd'] = 1

    def cmd_reset(self):
        """."""
        self['SmoothReset-Cmd'] = 1

    def cmd_calccorr(self):
        """."""
        self['CalcDelta-Cmd'] = 1

    def cmd_applycorr_ch(self):
        """."""
        self['ApplyDelta-Cmd'] = self.data.ApplyDelta.CH

    def cmd_applycorr_cv(self):
        """."""
        self['ApplyDelta-Cmd'] = self.data.ApplyDelta.CV

    def cmd_applycorr_rf(self):
        """."""
        self['ApplyDelta-Cmd'] = self.data.ApplyDelta.RF

    def cmd_applycorr_all(self):
        """."""
        self['ApplyDelta-Cmd'] = self.data.ApplyDelta.All

    def cmd_measrespmat_start(self):
        """."""
        self['MeasRespMat-Cmd'] = 0

    def cmd_measrespmat_stop(self):
        """."""
        self['MeasRespMat-Cmd'] = 1

    def cmd_measrespmat_reset(self):
        """."""
        self['MeasRespMat-Cmd'] = 2

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
    def measrespmat_kickrf(self):
        """."""
        return self['MeasRespMatKickRF-RB']

    @measrespmat_kickrf.setter
    def measrespmat_kickrf(self, value):
        self['MeasRespMatKickRF-SP'] = value

    @property
    def measrespmat_wait(self):
        """."""
        return self['MeasRespMatWait-RB']

    @measrespmat_wait.setter
    def measrespmat_wait(self, value):
        self['MeasRespMatWait-SP'] = value

    @property
    def autocorrsts(self):
        """."""
        return self['LoopState-Sts']

    def correct_orbit_manually(self, nr_iters=10):
        """."""
        self.cmd_turn_off_autocorr()

        for i in range(nr_iters):
            self.cmd_calccorr()
            _time.sleep(0.5)
            self.cmd_applycorr_all()
            _time.sleep(0.5)
            self.cmd_reset()
            self.wait_buffer()

    def cmd_turn_on_autocorr(self, timeout=None):
        """."""
        timeout = timeout or SOFB._default_timeout
        self['LoopState-Sel'] = self.data.LoopState.Closed
        self._wait(
            'LoopState-Sts', self.data.LoopState.Closed, timeout=timeout)

    def cmd_turn_off_autocorr(self, timeout=None):
        """."""
        timeout = timeout or SOFB._default_timeout
        self['LoopState-Sel'] = self.data.LoopState.Open
        self._wait(
            'LoopState-Sts', self.data.LoopState.Open, timeout=timeout)

    def wait_buffer(self, timeout=None):
        """."""
        timeout = timeout or SOFB._default_timeout
        interval = 0.050  # [s]
        ntrials = int(timeout/interval)
        _time.sleep(10*interval)
        for _ in range(ntrials):
            if self.buffer_count >= self['SmoothNrPts-SP']:
                break
            _time.sleep(interval)
        else:
            print('WARN: Timed out waiting orbit.')

    def wait_respm_meas(self, timeout=None):
        """."""
        timeout = timeout or SOFB._default_timeout_respm
        interval = 1  # [s]
        ntrials = int(timeout/interval)
        for _ in range(ntrials):
            if not self.measrespmat_mon == self.data.MeasRespMatMon.Measuring:
                break
            _time.sleep(interval)
        else:
            print('WARN: Timed out waiting respm measurement.')
