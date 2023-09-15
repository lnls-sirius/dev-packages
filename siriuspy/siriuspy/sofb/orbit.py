"""Module to deal with orbit acquisition."""
import os as _os
import time as _time
import logging as _log
from functools import partial as _part
from threading import Lock, Event as _Event
import traceback as _traceback

import numpy as _np
import bottleneck as _bn

from .. import util as _util
from ..diagbeam.bpm.csdev import Const as _csbpm
from ..thread import RepeaterThread as _Repeat
from ..epics import PV as _PV, CAThread as _Thread

from .base_class import BaseClass as _BaseClass
from .bpms import BPM, TimingConfig


class BaseOrbit(_BaseClass):
    """."""


class EpicsOrbit(BaseOrbit):
    """Class to deal with orbit acquisition."""

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)

        self._mode = 0  # first mode of the list
        self._sofb = None
        self._sync_with_inj = False
        self.ref_orbs = {
            'X': _np.zeros(self._csorb.nr_bpms),
            'Y': _np.zeros(self._csorb.nr_bpms)}
        self._load_ref_orbs()
        self.raw_orbs = {'X': [], 'Y': []}
        self.raw_sporbs = {'X': [], 'Y': [], 'Sum': []}
        self.raw_mtorbs = {'X': [], 'Y': [], 'Sum': []}
        self._lock_raw_orbs = Lock()
        self.smooth_orb = {'X': None, 'Y': None}
        self.smooth_sporb = {'X': None, 'Y': None, 'Sum': None}
        self.smooth_mtorb = {'X': None, 'Y': None, 'Sum': None}
        self._smooth_npts = 1
        self._smooth_meth = self._csorb.SmoothMeth.Average
        self._spass_mask = [0, 0]
        self._spass_average = 1
        self._acqtrignrsamplespre = 0
        self._acqtrignrsamplespost = 360
        self._acqtrignrshots = 1
        self._multiturnidx = 0
        self._mturndownsample = 1
        self._timevector = None
        self.bpms = [BPM(name, callback) for name in self._csorb.bpm_names]
        self.timing = TimingConfig(acc, callback)
        self.new_orbit = _Event()
        self._new_orbraw_flag = _Event()
        if self.acc == 'SI':
            self._sloworb_raw_pv = _PV(
                'SI-Glob:AP-SOFB:SlowOrbRaw-Mon',
                callback=self._update_sloworb_raw, auto_monitor=True)
        self._orbit_thread = _Repeat(
            1/self._csorb.ACQRATE_SLOWORB, self._update_orbits, niter=0)
        self._orbit_thread.start()
        self._thread_sync = None
        self._update_time_vector()

    @property
    def sofb(self):
        """."""
        return self._sofb

    @sofb.setter
    def sofb(self, sofb):
        self._sofb = sofb

    def shutdown(self):
        """."""
        self._orbit_thread.resume()
        self._orbit_thread.stop()
        self._orbit_thread.join()

    def get_map2write(self):
        """Get the write methods of the class."""
        dbase = {
            'SOFBMode-Sel': self.set_orbit_mode,
            'SyncWithInjection-Sel': self.set_sync_with_injection,
            'TrigAcqConfig-Cmd': self.acq_config_bpms,
            'TrigAcqCtrl-Sel': self.set_trig_acq_control,
            'TrigAcqChan-Sel': self.set_trig_acq_channel,
            'TrigAcqRepeat-Sel': self.set_trig_acq_repeat,
            'TrigNrSamplesPre-SP': _part(self.set_acq_nrsamples, ispost=False),
            'TrigNrSamplesPost-SP': _part(self.set_acq_nrsamples, ispost=True),
            'RefOrbX-SP': _part(self.set_reforb, 'X'),
            'RefOrbY-SP': _part(self.set_reforb, 'Y'),
            'SmoothNrPts-SP': self.set_smooth_npts,
            'SmoothMethod-Sel': self.set_smooth_method,
            'SmoothReset-Cmd': self.set_smooth_reset,
            'SPassMaskSplBeg-SP': _part(self.set_spass_mask, beg=True),
            'SPassMaskSplEnd-SP': _part(self.set_spass_mask, beg=False),
            'SPassAvgNrTurns-SP': self.set_spass_average,
            'TrigNrShots-SP': self.set_trig_acq_nrshots,
            'PolyCalibration-Sel': self.set_poly_calibration,
            'SyncBPMs-Cmd': self.sync_bpms,
            'TestDataEnbl-Sel': self.set_test_data_enbl,
            }
        if not self.isring:
            return dbase
        dbase.update({
            'MTurnAcquire-Cmd': self.acquire_mturn_orbit,
            'MTurnIdx-SP': self.set_orbit_multiturn_idx,
            'MTurnDownSample-SP': self.set_mturndownsample,
            'MTurnUseMask-Sel': self.set_mturn_usemask,
            'MTurnMaskSplBeg-SP': _part(self.set_mturnmask, beg=True),
            'MTurnMaskSplEnd-SP': _part(self.set_mturnmask, beg=False),
            })
        return dbase

    @property
    def mode(self):
        """."""
        return self._mode

    @property
    def acqtrignrsamples(self):
        """."""
        return self._acqtrignrsamplespre + self._acqtrignrsamplespost

    @property
    def update_raws(self):
        """."""
        return not self._sync_with_inj or self.timing.injecting

    def is_sloworb(self, mode=None):
        """Check is mode or self._mode is in SlowOrb mode."""
        if mode is None:
            mode = self._mode
        return self.acc == 'SI' and mode == self._csorb.SOFBMode.SlowOrb

    def is_multiturn(self, mode=None):
        """Check is mode or self._mode is in MultiTurn mode."""
        if mode is None:
            mode = self._mode
        return self.isring and mode == self._csorb.SOFBMode.MultiTurn

    def is_singlepass(self, mode=None):
        """Check is mode or self._mode is in SinglePass mode."""
        if mode is None:
            mode = self._mode
        return mode == self._csorb.SOFBMode.SinglePass

    def is_trigmode(self, mode=None):
        """Check is mode or self._mode is in any of the Triggered modes."""
        return self.is_singlepass(mode) or self.is_multiturn(mode)

    def get_orbit(self, reset=False, synced=False, timeout=1/5):
        """Return the orbit distortion."""
        nrb = self._csorb.nr_bpms
        refx = self.ref_orbs['X'][:nrb]
        refy = self.ref_orbs['Y'][:nrb]
        if reset:
            with self._lock_raw_orbs:
                msg = 'DEB: Reseting Orbit.'
                _log.debug(msg)
                self._reset_orbs()
                msg = 'DEB: Reseted Orbit.'
                _log.debug(msg)
            _time.sleep(self._smooth_npts/self._csorb.BPMsFreq)

        if self.is_multiturn():
            orbs = self.smooth_mtorb
            raws = self.raw_mtorbs
            getorb = self._get_orbit_multiturn
        elif self.is_singlepass():
            orbs = self.smooth_sporb
            raws = self.raw_sporbs
            getorb = self._get_orbit_singlepass
        elif self.is_sloworb():
            if synced:
                self.new_orbit.wait(timeout=timeout)
                self.new_orbit.clear()
            orbs = self.smooth_orb
            raws = self.raw_orbs
            getorb = self._get_orbit_online

        for _ in range(3 * self._smooth_npts):
            with self._lock_raw_orbs:
                isempty = orbs['X'] is None or orbs['Y'] is None
                if not isempty and len(raws['X']) >= self._smooth_npts:
                    orbx, orby = getorb(orbs)
                    break
            msg = 'DEB: Trying to get: '
            msg += f'empty={str(isempty):s}, smooth={len(raws["X"]):02d}.'
            _log.debug(msg)
            _time.sleep(1/self._csorb.BPMsFreq)
        else:
            msg = 'ERR: timeout waiting orbit.'
            self._update_log(msg)
            _log.error(msg[5:])
            orbx, orby = refx, refy
        # # for tests:
        # orbx -= _time.time()
        # orby -= _time.time()
        return _np.hstack([orbx-refx, orby-refy])

    def _get_orbit_online(self, orbs):
        """."""
        return orbs['X'], orbs['Y']

    def _get_orbit_singlepass(self, orbs):
        """."""
        return orbs['X'], orbs['Y']

    def _get_orbit_multiturn(self, orbs):
        """."""
        idx = self._multiturnidx
        return orbs['X'][idx, :], orbs['Y'][idx, :]

    def set_smooth_npts(self, num):
        """."""
        self._smooth_npts = num
        self.run_callbacks('SmoothNrPts-RB', num)
        return True

    def set_smooth_method(self, meth):
        """."""
        self._smooth_meth = meth
        self.run_callbacks('SmoothMethod-Sts', meth)
        return True

    def set_spass_mask(self, val, beg=True):
        """."""
        val = int(val) if val > 0 else 0
        other_mask = self._spass_mask[1 if beg else 0]
        maxsz = self.bpms[0].tbtrate - other_mask - 2
        val = val if val < maxsz else maxsz
        self._spass_mask[0 if beg else 1] = val
        name = 'Beg' if beg else 'End'
        self.run_callbacks('SPassMaskSpl' + name + '-RB', val)
        return True

    def set_mturn_usemask(self, val):
        """."""
        value = _csbpm.DsblEnbl.enabled
        if val == self._csorb.DsblEnbl.Dsbl:
            value = _csbpm.DsblEnbl.disabled

        mask = self._get_mask()
        for i, bpm in enumerate(self.bpms):
            bpm.put_enable = mask[i]
            bpm.tbt_mask_enbl = value

        self.run_callbacks('MTurnUseMask-Sts', val)
        return True

    def set_mturnmask(self, val, beg=True):
        """."""
        val = int(val) if val > 0 else 0
        bpms = self._get_used_bpms()
        omsk = \
            bpms[0].tbt_mask_begin if not beg else \
            bpms[0].tbt_mask_end
        omsk = omsk or 0
        maxsz = bpms[0].tbtrate - omsk - 2
        val = val if val < maxsz else maxsz

        mask = self._get_mask()
        for i, bpm in enumerate(self.bpms):
            bpm.put_enable = mask[i]
            if beg:
                bpm.tbt_mask_begin = val
            else:
                bpm.tbt_mask_end = val

        name = 'Beg' if beg else 'End'
        self.run_callbacks('MTurnMaskSpl' + name + '-RB', val)
        return True

    def set_spass_average(self, val):
        """."""
        val = int(val) if val > 1 else 1
        with self._lock_raw_orbs:
            self._spass_average = val
            self._reset_orbs()
        self.run_callbacks('SPassAvgNrTurns-RB', val)
        self._prepare_mode()
        return True

    def set_smooth_reset(self, _):
        """."""
        with self._lock_raw_orbs:
            self._reset_orbs()
        return True

    def set_reforb(self, plane, orb):
        """."""
        msg = 'Setting New Reference Orbit.'
        self._update_log(msg)
        _log.info(msg)
        orb = _np.array(orb, dtype=float)
        nrb = self._csorb.nr_bpms
        if orb.size % self._csorb.nr_bpms:
            msg = 'ERR: Wrong RefOrb Size.'
            self._update_log(msg)
            _log.error(msg[5:])
            self.run_callbacks(
                'RefOrb'+plane+'-SP', self.ref_orbs[plane][:nrb])
        elif orb.size < nrb:
            msg = 'WARN: Orb Size is too small. Replicating...'
            self._update_log(msg)
            _log.error(msg[6:])
            nrep = int(nrb//orb.size) + 1
            orb2 = _np.tile(orb, nrep)
            orb = orb2[:nrb]
        self.ref_orbs[plane] = orb
        self._save_ref_orbits()
        with self._lock_raw_orbs:
            self._reset_orbs()
        self.run_callbacks('RefOrb'+plane+'-RB', orb[:nrb])
        return True

    def set_orbit_mode(self, value):
        """."""
        omode = self._mode
        acqrate = self._csorb.ACQRATE_SLOWORB
        if self.is_trigmode(value):
            acqrate = self._csorb.ACQRATE_TRIGMODE

        with self._lock_raw_orbs:
            self._mode = value
            self._orbit_thread.interval = 1/acqrate
            self._reset_orbs()
        self.run_callbacks('SOFBMode-Sts', value)
        self._prepare_mode(oldmode=omode)
        return True

    def set_sync_with_injection(self, boo):
        """."""
        self._sync_with_inj = bool(boo)
        self.run_callbacks('SyncWithInjection-Sts', bool(boo))
        return True

    def set_test_data_enbl(self, val, is_thread=False):
        """."""
        if not is_thread:
            self._LQTHREAD.put((
                self.set_test_data_enbl, (val, ), {'is_thread': True}))
            return True

        value = _csbpm.DsblEnbl.enabled
        if val == self._csorb.DsblEnbl.Dsbl:
            value = _csbpm.DsblEnbl.disabled

        mask = self._get_mask()
        for i, bpm in enumerate(self.bpms):
            bpm.put_enable = mask[i]
            bpm.test_data_enbl = value
        self.run_callbacks('TestDataEnbl-Sts', val)

    def _prepare_mode(self, oldmode=None):
        """."""
        oldmode = self._mode if oldmode is None else oldmode
        self.set_trig_acq_control(self._csorb.TrigAcqCtrl.Abort)

        if not self.is_trigmode():
            self.acq_config_bpms()
            return True

        if self.is_singlepass():
            chan = self._csorb.TrigAcqChan.ADCSwp
            rep = self._csorb.TrigAcqRepeat.Repetitive
            points = self._spass_average * self.bpms[0].tbtrate
        elif self.is_multiturn():
            chan = self._csorb.TrigAcqChan.TbT
            rep = self._csorb.TrigAcqRepeat.Repetitive
            points = self._mturndownsample

        if self._mode != oldmode:
            self.run_callbacks('TrigAcqChan-Sel', chan)
            self.set_trig_acq_channel(chan)
            self.run_callbacks('TrigAcqRepeat-Sel', rep)
            self.set_trig_acq_repeat(rep)
            if self.acqtrignrsamples < points:
                pts = points - self._acqtrignrsamplespre
                self.run_callbacks('TrigNrSamplesPost-SP', pts)
                self.set_acq_nrsamples(pts, ispost=True)
        self._update_time_vector()
        self.acq_config_bpms()

        self.set_trig_acq_control(self._csorb.TrigAcqCtrl.Start)
        return True

    def set_orbit_multiturn_idx(self, value):
        """."""
        maxidx = self.acqtrignrsamples // self._mturndownsample
        maxidx *= self._acqtrignrshots
        if value >= maxidx:
            value = maxidx-1
            msg = 'WARN: MTurnIdx is too large. Redefining...'
            self._update_log(msg)
            _log.warning(msg[6:])
        with self._lock_raw_orbs:
            self._multiturnidx = int(value)
        self.run_callbacks('MTurnIdx-RB', self._multiturnidx)
        self.run_callbacks(
            'MTurnIdxTime-Mon', self._timevector[self._multiturnidx])
        self._update_multiturn_orbit_pvs()
        return True

    def acq_config_bpms(self, *args):
        """."""
        _ = args
        msg = 'Configuring BPMs...'
        self._update_log(msg)
        _log.info(msg)

        mask = self._get_mask()
        for i, bpm in enumerate(self.bpms):
            bpm.put_enable = mask[i]
            if self.is_multiturn():
                bpm.mode = _csbpm.OpModes.MultiBunch
                bpm.switching_mode = _csbpm.SwModes.direct
                bpm.configure()
                self.timing.configure()
            elif self.is_singlepass():
                bpm.mode = _csbpm.OpModes.MultiBunch
                bpm.switching_mode = _csbpm.SwModes.direct
                bpm.configure()
                self.timing.configure()
            elif self.is_sloworb():
                bpm.switching_mode = _csbpm.SwModes.switching
        self.sync_bpms(None)
        msg = 'Done configuring BPMs!'
        self._update_log(msg)
        _log.info(msg)
        return True

    def sync_bpms(self, *args):
        """Synchronize BPMs."""
        _ = args

        msg = 'Received sync BPMs command.'
        self._update_log(msg)
        _log.info(msg)

        if self._thread_sync is not None and \
                self._thread_sync.is_alive():
            msg = 'WARN: Previous sync. of BPMs still running.'
            self._update_log(msg)
            _log.warning(msg)
            return False

        self._thread_sync = _Thread(
            target=self._synchronize_bpms, daemon=True)
        self._thread_sync.start()
        return True

    def _synchronize_bpms(self):
        msg = 'Syncing BPMs.'
        self._update_log(msg)
        _log.info(msg)
        for bpm in self._get_used_bpms():
            # NOTE: Switching sync must always be enabled
            bpm.sw_sync_enbl = _csbpm.DsblEnbl.enabled

            bpm.tbt_sync_enbl = _csbpm.DsblEnbl.enabled
            bpm.fofb_sync_enbl = _csbpm.DsblEnbl.enabled
            bpm.facq_sync_enbl = _csbpm.DsblEnbl.enabled
            bpm.monit_sync_enbl = _csbpm.DsblEnbl.enabled
        _time.sleep(0.5)
        for bpm in self._get_used_bpms():
            bpm.tbt_sync_enbl = _csbpm.DsblEnbl.disabled
            bpm.fofb_sync_enbl = _csbpm.DsblEnbl.disabled
            bpm.monit_sync_enbl = _csbpm.DsblEnbl.disabled
            bpm.facq_sync_enbl = _csbpm.DsblEnbl.disabled

        if self.acc == 'SI' and self.sofb.fofb.connected:
            _time.sleep(0.2)
            msg = 'Syncing FOFB Net...'
            self._update_log(msg)
            _log.info(msg)
            self.sofb.fofb.cmd_fofbctrl_syncnet()

        msg = 'Syncing BPMs is done!'
        self._update_log(msg)
        _log.info(msg)

    def set_trig_acq_control(self, value):
        """."""
        mask = self._get_mask()
        for i, bpm in enumerate(self.bpms):
            bpm.put_enable = mask[i]
            bpm.ctrl = value
        self.run_callbacks('TrigAcqCtrl-Sts', value)
        return True

    def set_trig_acq_channel(self, value):
        """."""
        try:
            val = self._csorb.TrigAcqChan._fields[value]
            val = _csbpm.AcqChan._fields.index(val)
        except (IndexError, ValueError):
            return False

        mask = self._get_mask()
        for i, bpm in enumerate(self.bpms):
            bpm.put_enable = mask[i]
            bpm.acq_type = val

        self.run_callbacks('TrigAcqChan-Sts', value)
        self._update_time_vector(channel=val)
        return True

    def set_trig_acq_repeat(self, value):
        """."""
        mask = self._get_mask()
        for i, bpm in enumerate(self.bpms):
            bpm.put_enable = mask[i]
            bpm.acq_repeat = value
        self.run_callbacks('TrigAcqRepeat-Sts', value)
        return True

    def set_acq_nrsamples(self, val, ispost=True):
        """."""
        val = int(val) if val > 0 else 0
        val = val if val < 20000 else 20000
        suf = 'post' if ispost else 'pre'
        oth = 'post' if not ispost else 'pre'
        if getattr(self, '_acqtrignrsamples' + oth) == 0 and val == 0:
            self.run_callbacks(
                'TrigNrSamples'+suf.title()+'-SP',
                getattr(self, '_acqtrignrsamples' + suf))
        with self._lock_raw_orbs:
            mask = self._get_mask()
            for i, bpm in enumerate(self.bpms):
                bpm.put_enable = mask[i]
                setattr(bpm, 'nrsamples' + suf, val)
            self._reset_orbs()
            setattr(self, '_acqtrignrsamples' + suf, val)
        self.run_callbacks('TrigNrSamples'+suf.title()+'-RB', val)
        self._update_time_vector()
        return True

    def set_trig_acq_nrshots(self, val):
        """."""
        val = int(val) if val > 1 else 1
        val = val if val < 1000 else 1000
        with self._lock_raw_orbs:
            mask = self._get_mask()
            for i, bpm in enumerate(self.bpms):
                bpm.put_enable = mask[i]
                bpm.nrshots = val
            self.timing.nrpulses = val
            self._reset_orbs()
            self._acqtrignrshots = val
        self.run_callbacks('TrigNrShots-RB', val)
        self._update_time_vector()
        return True

    def set_poly_calibration(self, val):
        """."""
        value = _csbpm.DsblEnbl.enabled
        if val == self._csorb.DsblEnbl.Dsbl:
            value = _csbpm.DsblEnbl.disabled
        mask = self._get_mask()
        for i, bpm in enumerate(self.bpms):
            bpm.put_enable = mask[i]
            bpm.polycal = value
        self.run_callbacks('PolyCalibration-Sts', val)
        return True

    def set_mturndownsample(self, val):
        """."""
        val = int(val) if val > 1 else 1
        val = val if val < 1000 else 1000
        with self._lock_raw_orbs:
            self._mturndownsample = val
            self._reset_orbs()
        self.run_callbacks('MTurnDownSample-RB', val)
        self._prepare_mode()
        return True

    def acquire_mturn_orbit(self, _):
        """Acquire Multiturn data from BPMs."""
        self._update_multiturn_orbits(force_update=True)
        return True

    def _update_time_vector(self, delay=None, duration=None, channel=None):
        """."""
        if not self.isring:
            return
        dly = (delay or self.timing.totaldelay or 0.0) * 1e-6  # from us to s
        dur = (duration or self.timing.duration or 0.0) * 1e-6  # from us to s
        channel = channel or self.bpms[0].acq_type or 0

        # revolution period in s
        if channel == _csbpm.AcqChan.FAcq:
            dtime = self.bpms[0].facqperiod
        elif channel == _csbpm.AcqChan.FOFB:
            dtime = self.bpms[0].fofbperiod
        else:
            dtime = self.bpms[0].tbtperiod
        mult = self._mturndownsample
        dtime *= mult
        nrptpst = self.acqtrignrsamples // mult
        offset = self._acqtrignrsamplespre / mult
        nrst = self._acqtrignrshots
        shots = _np.arange(nrst)
        pts = _np.arange(nrptpst, dtype=float) + (0.5 - offset)
        vect = dly + dur/nrst*shots[:, None] + dtime*pts[None, :]
        self._timevector = vect.ravel()
        self.run_callbacks('MTurnTime-Mon', self._timevector)
        self.set_orbit_multiturn_idx(self._multiturnidx)

    def _load_ref_orbs(self):
        """."""
        if not _os.path.isfile(self._csorb.ref_orb_fname):
            return
        self.ref_orbs['X'], self.ref_orbs['Y'] = _np.loadtxt(
            self._csorb.ref_orb_fname, unpack=True)
        self.run_callbacks('RefOrbX-RB', self.ref_orbs['X'].copy())
        self.run_callbacks('RefOrbY-RB', self.ref_orbs['Y'].copy())

    def _save_ref_orbits(self):
        """."""
        refx = self.ref_orbs['X']
        refy = self.ref_orbs['Y']
        if refx.size < refy.size:
            ref = _np.zeros(refy.shape, dtype=float)
            ref[:refx.size] = refx
            refx = ref
        elif refy.size < refx.size:
            ref = _np.zeros(refx.shape, dtype=float)
            ref[:refy.size] = refy
            refy = ref
        orbs = _np.array([refx, refy]).T
        try:
            path = _os.path.split(self._csorb.ref_orb_fname)[0]
            _os.makedirs(path, exist_ok=True)
            _np.savetxt(self._csorb.ref_orb_fname, orbs)
        except FileNotFoundError:
            msg = 'WARN: Could not save reference orbit in file.'
            self._update_log(msg)
            _log.warning(msg[6:])

    def _reset_orbs(self):
        """."""
        raw = self.raw_orbs
        smt = self.smooth_orb
        raw['X'], raw['Y'] = [], []
        smt['X'], smt['Y'] = None, None
        raw = self.raw_sporbs
        smt = self.smooth_sporb
        raw['X'], raw['Y'], raw['Sum'] = [], [], []
        smt['X'], smt['Y'], smt['Sum'] = None, None, None
        raw = self.raw_mtorbs
        smt = self.smooth_mtorb
        raw['X'], raw['Y'], raw['Sum'] = [], [], []
        smt['X'], smt['Y'], smt['Sum'] = None, None, None
        self.run_callbacks('BufferCount-Mon', 0)

    def _update_orbits(self):
        """."""
        try:
            count = 0
            if self.is_multiturn():
                self._update_multiturn_orbits(force_update=False)
                count = len(self.raw_mtorbs['X'])
            elif self.is_singlepass():
                self._update_singlepass_orbits()
                count = len(self.raw_sporbs['X'])
            elif self.is_sloworb():
                self._update_online_orbits()
                count = len(self.raw_orbs['X'])
            self.run_callbacks('BufferCount-Mon', count)
        except Exception as err:
            self._update_log('ERR: ' + str(err))
            _log.error(_traceback.format_exc())

    def _update_online_orbits(self):
        """."""
        timeout = 1000/1000
        if not self._new_orbraw_flag.wait(timeout=timeout):
            msg = 'ERR: Raw orbit did not update.'
            self._update_log(msg)
            _log.error(msg[5:])
            return
        else:
            self._new_orbraw_flag.clear()

        orb = self._sloworb_raw_pv.value
        posx, posy = orb[:self._csorb.nr_bpms], orb[self._csorb.nr_bpms:]
        nanx = _np.isnan(posx)
        nany = _np.isnan(posy)
        posx[nanx] = self.ref_orbs['X'][nanx]
        posy[nany] = self.ref_orbs['Y'][nany]
        orbs = {'X': posx, 'Y': posy}

        for plane in ('X', 'Y'):
            with self._lock_raw_orbs:
                raws = self.raw_orbs
                raws[plane].append(orbs[plane])
                raws[plane] = raws[plane][-self._smooth_npts:]
                if not raws[plane]:
                    return
                if self._smooth_meth == self._csorb.SmoothMeth.Average:
                    orb = _np.mean(raws[plane], axis=0)
                else:
                    orb = _np.median(raws[plane], axis=0)
                self.smooth_orb[plane] = orb
        self.new_orbit.set()

        for plane in ('X', 'Y'):
            orb = self.smooth_orb[plane]
            if orb is None:
                return
            dorb = orb - self.ref_orbs[plane]
            self.run_callbacks(f'SlowOrb{plane:s}-Mon', _np.array(orb))
            self.run_callbacks(f'DeltaOrb{plane:s}Avg-Mon', _bn.nanmean(dorb))
            self.run_callbacks(f'DeltaOrb{plane:s}Std-Mon', _bn.nanstd(dorb))
            self.run_callbacks(f'DeltaOrb{plane:s}Min-Mon', _bn.nanmin(dorb))
            self.run_callbacks(f'DeltaOrb{plane:s}Max-Mon', _bn.nanmax(dorb))

    def _update_sloworb_raw(self, pvname, value, **kwrgs):
        _ = pvname, value, kwrgs
        self._new_orbraw_flag.set()

    def _update_multiturn_orbits(self, force_update=True):
        """."""
        orbs = {'X': [], 'Y': [], 'Sum': []}
        with self._lock_raw_orbs:  # I need the lock here to ensure consistency
            leng = len(self.raw_mtorbs['X'])
            samp = self.acqtrignrsamples
            down = self._mturndownsample
            samp -= samp % down
            if samp < 1:
                msg = 'ERR: Actual nr_samples in MTurn orb calc. is < 1.'
                self._update_log(msg)
                _log.error(msg[5:])
                return
            samp *= self._acqtrignrshots
            orbsz = self._csorb.nr_bpms
            nr_pts = self._smooth_npts
            do_update = force_update
            for i, bpm in enumerate(self.bpms):
                if not leng or bpm.needs_update_cnt > 0:
                    bpm.needs_update_cnt -= 1
                    do_update = True
                    posx = self._get_pos(
                        bpm.mtposx, self.ref_orbs['X'][i], samp)
                    posy = self._get_pos(
                        bpm.mtposy, self.ref_orbs['Y'][i], samp)
                    psum = self._get_pos(bpm.mtsum, 0, samp)
                else:
                    posx = self.raw_mtorbs['X'][-1][:, i].copy()
                    posy = self.raw_mtorbs['Y'][-1][:, i].copy()
                    psum = self.raw_mtorbs['Sum'][-1][:, i].copy()
                orbs['X'].append(posx)
                orbs['Y'].append(posy)
                orbs['Sum'].append(psum)

            # NOTE: Only update orbit when at least one BPM has news
            if not do_update:
                return

            for pln, raw in self.raw_mtorbs.items():
                norb = _np.array(orbs[pln], dtype=float)  # bpms x turns
                norb = norb.T.reshape(-1, orbsz)  # turns/rz x rz*bpms
                if self.update_raws:
                    raw.append(norb)
                del raw[:-nr_pts]
                if not raw:
                    return
                if self._smooth_meth == self._csorb.SmoothMeth.Average:
                    orb = _np.mean(raw, axis=0)
                else:
                    orb = _np.median(raw, axis=0)
                if down > 1:
                    orb = _np.mean(orb.reshape(-1, down, orbsz), axis=1)
                self.smooth_mtorb[pln] = orb
                orbs[pln] = orb
        self._update_multiturn_orbit_pvs()

    def _update_multiturn_orbit_pvs(self):
        for pln, orb in self.smooth_mtorb.items():
            if orb is None:
                continue
            idx = min(self._multiturnidx, orb.shape[0])
            name = ('Orb' if pln != 'Sum' else '') + pln
            self.run_callbacks('MTurn' + name + '-Mon', orb.ravel())
            self.run_callbacks(
                'MTurnIdx' + name + '-Mon', orb[idx, :].ravel())
            if pln == 'Sum':
                continue
            nrb = self._csorb.nr_bpms
            dorb = orb[idx, :].ravel() - self.ref_orbs[pln][:nrb]
            self.run_callbacks(f'DeltaOrb{pln:s}Avg-Mon', _bn.nanmean(dorb))
            self.run_callbacks(f'DeltaOrb{pln:s}Std-Mon', _bn.nanstd(dorb))
            self.run_callbacks(f'DeltaOrb{pln:s}Min-Mon', _bn.nanmin(dorb))
            self.run_callbacks(f'DeltaOrb{pln:s}Max-Mon', _bn.nanmax(dorb))

    @staticmethod
    def _get_pos(pos, ref, samp):
        if pos is None:
            posi = _np.full(samp, ref)
        elif pos.size < samp:
            posi = _np.full(samp, ref)
            posi[:pos.size] = pos
        else:
            posi = pos[:samp]
        return posi

    def _update_singlepass_orbits(self):
        """."""
        orbs = {'X': [], 'Y': [], 'Sum': []}
        down = self._spass_average
        with self._lock_raw_orbs:  # I need the lock here to assure consistency
            leng = len(self.raw_sporbs['X'])
            dic = {
                'maskbeg': self._spass_mask[0],
                'maskend': self._spass_mask[1],
                'nturns': down}
            nr_pts = self._smooth_npts
            do_update = False
            for i, bpm in enumerate(self.bpms):
                if not leng or bpm.needs_update_cnt > 0:
                    bpm.needs_update_cnt -= 1
                    do_update = True
                    dic.update({
                        'refx': self.ref_orbs['X'][i],
                        'refy': self.ref_orbs['Y'][i]})
                    orbx, orby, summ = bpm.calc_sp_multiturn_pos(**dic)
                else:
                    orbx = self.raw_sporbs['X'][-1][i].copy()
                    orby = self.raw_sporbs['Y'][-1][i].copy()
                    summ = self.raw_sporbs['Sum'][-1][i].copy()
                orbs['X'].append(orbx)
                orbs['Y'].append(orby)
                orbs['Sum'].append(summ)

            # NOTE: only update orbits when there are news from BPMs.
            if not do_update:
                return

            for pln, raw in self.raw_sporbs.items():
                norb = _np.array(orbs[pln], dtype=float).T  # turns x bpms
                norb = norb.reshape(-1)
                if self.update_raws:
                    raw.append(norb)
                del raw[:-nr_pts]
                if not raw:
                    return
                if self._smooth_meth == self._csorb.SmoothMeth.Average:
                    orb = _np.mean(raw, axis=0)
                else:
                    orb = _np.median(raw, axis=0)
                if down > 1:
                    orb = _np.mean(orb.reshape(down, -1), axis=0)
                self.smooth_sporb[pln] = orb

        for pln, orb in self.smooth_sporb.items():
            name = ('Orb' if pln != 'Sum' else '') + pln
            self.run_callbacks('SPass' + name + '-Mon', orb)

    def _update_status(self):
        """."""
        status = 0b11111

        if self.is_trigmode():
            tim_conn = self.timing.connected
            tim_conf = self.timing.is_ok
        else:
            tim_conn = True
            tim_conf = True
        status = _util.update_bit(status, bit_pos=0, bit_val=not tim_conn)
        status = _util.update_bit(status, bit_pos=1, bit_val=not tim_conf)

        bpms = self._get_used_bpms()
        bpm_conn = all(bpm.connected for bpm in bpms)
        bpm_stt = all(bpm.state for bpm in bpms)
        status = _util.update_bit(v=status, bit_pos=2, bit_val=not bpm_conn)
        status = _util.update_bit(v=status, bit_pos=3, bit_val=not bpm_stt)

        isok = True
        if self.is_trigmode():
            isok = all(map(lambda x: x.is_ok, bpms))
        elif self.is_sloworb():
            isok = all(map(
                lambda x: x.switching_mode == _csbpm.SwModes.switching, bpms))
        status = _util.update_bit(v=status, bit_pos=4, bit_val=not isok)

        # Check if test data is disabled
        isok = all(map(
            lambda x: x.test_data_enbl == _csbpm.DsblEnbl.disabled, bpms))
        status = _util.update_bit(v=status, bit_pos=5, bit_val=not isok)

        # Check if switching sync is enabled
        isok = all(map(
            lambda x: x.sw_sync_enbl == _csbpm.DsblEnbl.enabled, bpms))
        status = _util.update_bit(v=status, bit_pos=6, bit_val=not isok)

        orb_conn = self._sloworb_raw_pv.connected if self.acc == 'SI' else True
        status = _util.update_bit(v=status, bit_pos=7, bit_val=not orb_conn)

        self._status = status
        self.run_callbacks('OrbStatus-Mon', status)
        self._update_bpmoffsets()

    def _update_bpmoffsets(self):
        """."""
        nrb = self._csorb.nr_bpms
        orbx = _np.zeros(nrb, dtype=float)
        orby = orbx.copy()
        for i, bpm in enumerate(self.bpms):
            orbx[i::nrb] = bpm.offsetx or 0.0
            orby[i::nrb] = bpm.offsety or 0.0
        self.run_callbacks('BPMOffsetX-Mon', orbx)
        self.run_callbacks('BPMOffsetY-Mon', orby)

    def _get_mask(self):
        mask = _np.ones(self._csorb.nr_bpms, dtype=bool)
        if self.sofb is not None and self.sofb.matrix is not None:
            mask = self.sofb.matrix.bpm_enbllist
            mask = mask[:mask.size//2] & mask[mask.size//2:]
            mask = mask[:len(self.bpms)]
        return mask

    def _get_used_bpms(self):
        bpms = []
        mask = self._get_mask()
        for i, bpm in enumerate(self.bpms):
            bpm.put_enable = mask[i]
            if mask[i]:
                bpms.append(bpm)
        return bpms
