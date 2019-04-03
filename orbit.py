"""Module to deal with orbit acquisition."""
import os as _os
import time as _time
from math import ceil as _ceil
import logging as _log
from functools import partial as _part
from threading import Lock
import numpy as _np
import siriuspy.util as _util
import siriuspy.csdevice.bpms as _csbpm
from siriuspy.thread import RepeaterThread as _Repeat
from .base_class import BaseClass as _BaseClass
from .bpms import BPM, TimingConfig


class BaseOrbit(_BaseClass):
    pass


class EpicsOrbit(BaseOrbit):
    """Class to deal with orbit acquisition."""

    def get_database(self):
        """Get the database of the class."""
        db = self._csorb.get_orbit_database()
        prop = 'fun_set_pv'
        db['SOFBMode-Sel'][prop] = self.set_orbit_mode
        db['TrigAcqConfig-Cmd'][prop] = self.trig_acq_config_bpms
        db['TrigAcqCtrl-Sel'][prop] = self.set_trig_acq_control
        db['TrigAcqChan-Sel'][prop] = self.set_trig_acq_channel
        db['TrigDataChan-Sel'][prop] = self.set_trig_acq_datachan
        db['TrigAcqTrigger-Sel'][prop] = self.set_trig_acq_trigger
        db['TrigAcqRepeat-Sel'][prop] = self.set_trig_acq_repeat
        db['TrigDataSel-Sel'][prop] = self.set_trig_acq_datasel
        db['TrigDataThres-SP'][prop] = self.set_trig_acq_datathres
        db['TrigDataHyst-SP'][prop] = self.set_trig_acq_datahyst
        db['TrigDataPol-Sel'][prop] = self.set_trig_acq_datapol
        db['TrigExtDuration-SP'][prop] = self.set_trig_acq_extduration
        db['TrigExtDelay-SP'][prop] = self.set_trig_acq_extdelay
        db['TrigExtEvtSrc-Sel'][prop] = self.set_trig_acq_extsource
        db['TrigNrSamplesPre-SP'][prop] = _part(
            self.set_trig_acq_nrsamples, ispost=False)
        db['TrigNrSamplesPost-SP'][prop] = _part(
            self.set_trig_acq_nrsamples, ispost=True)
        db['RefOrbX-SP'][prop] = _part(self.set_ref_orbit, 'X')
        db['RefOrbY-SP'][prop] = _part(self.set_ref_orbit, 'Y')
        db['OfflineOrbX-SP'][prop] = _part(self.set_offline_orbit, 'X')
        db['OfflineOrbY-SP'][prop] = _part(self.set_offline_orbit, 'Y')
        db['SmoothNrPts-SP'][prop] = self.set_smooth_npts
        db['SmoothMethod-Sel'][prop] = self.set_smooth_method
        db['SmoothReset-Cmd'][prop] = self.set_smooth_reset
        db['SPassMethod-Sel'][prop] = self.set_spass_method
        db['SPassMaskSplBeg-SP'][prop] = _part(self.set_spass_mask, beg=True)
        db['SPassMaskSplEnd-SP'][prop] = _part(self.set_spass_mask, beg=False)
        db['SPassAvgNrTurns-SP'][prop] = self.set_spass_average
        db['OrbAcqRate-SP'][prop] = self.set_orbit_acq_rate
        db['TrigNrShots-SP'][prop] = self.set_trig_acq_nrshots
        if self.isring:
            db['MTurnIdx-SP'][prop] = self.set_orbit_multiturn_idx
            db['MTurnDownSample-SP'][prop] = self.set_mturndownsample

        db = super().get_database(db)
        return db

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)

        self._mode = self._csorb.SOFBMode.Offline
        self.ref_orbs = {
                'X': _np.zeros(self._csorb.NR_BPMS),
                'Y': _np.zeros(self._csorb.NR_BPMS)}
        self._load_ref_orbs()
        self.raw_orbs = {'X': [], 'Y': []}
        self.raw_sporbs = {'X': [], 'Y': [], 'Sum': []}
        self.raw_mtorbs = {'X': [], 'Y': [], 'Sum': []}
        self._lock_raw_orbs = Lock()
        self.smooth_orb = {'X': None, 'Y': None}
        self.smooth_sporb = {'X': None, 'Y': None, 'Sum': None}
        self.smooth_mtorb = {'X': None, 'Y': None, 'Sum': None}
        self.offline_orbit = {
                'X': _np.zeros(self._csorb.NR_BPMS),
                'Y': _np.zeros(self._csorb.NR_BPMS)}
        self._smooth_npts = 1
        self._smooth_meth = self._csorb.SmoothMeth.Average
        self._spass_method = self._csorb.SPassMethod.FromBPMs
        self._spass_mask = [0, 0]
        self._spass_average = 1
        self._acqrate = 10
        self._oldacqrate = self._acqrate
        self._acqtrignrsamplespre = 50
        self._acqtrignrsamplespost = 50
        self._acqtrignrshots = 1
        self._multiturnidx = 0
        self._mturndownsample = 1
        self._timevector = None
        self._ring_extension = 1
        self.bpms = [BPM(name) for name in self._csorb.BPM_NAMES]
        self.timing = TimingConfig(acc)
        self._orbit_thread = _Repeat(
                        1/self._acqrate, self._update_orbits, niter=0)
        self._orbit_thread.start()
        self._update_time_vector()

    @property
    def mode(self):
        return self._mode

    @property
    def acqtrignrsamples(self):
        return self._acqtrignrsamplespre + self._acqtrignrsamplespost

    def set_ring_extension(self, val):
        maval = self._csorb.MAX_RINGSZ
        val = 1 if val < 1 else int(val)
        val = maval if val > maval else val
        if val == self._ring_extension:
            return True
        with self._lock_raw_orbs:
            self._spass_average = 1
            self.run_callbacks('SPassAvgNrTurns-SP', 1)
            self.run_callbacks('SPassAvgNrTurns-RB', 1)
            self._mturndownsample = 1
            self.run_callbacks('MTurnDownSample-SP', 1)
            self.run_callbacks('MTurnDownSample-RB', 1)
            self._reset_orbs()
            self._ring_extension = val
            nrb = val * self._csorb.NR_BPMS
            for pln in self.offline_orbit.keys():
                orb = self.ref_orbs[pln]
                if orb.size < nrb:
                    nrep = _ceil(nrb/orb.size)
                    orb2 = _np.tile(orb, nrep)
                    orb = orb2[:nrb]
                self.ref_orbs[pln] = orb
                self.run_callbacks('RefOrb'+pln+'-RB', orb[:nrb])
                self.run_callbacks('RefOrb'+pln+'-SP', orb[:nrb])
                orb = self.offline_orbit[pln]
                if orb.size < nrb:
                    orb2 = self.ref_orbs[pln].copy()
                    orb2[:orb.size] = orb
                    orb = orb2
                self.offline_orbit[pln] = orb
                self.run_callbacks('OfflineOrb'+pln+'-RB', orb[:nrb])
                self.run_callbacks('OfflineOrb'+pln+'-SP', orb[:nrb])
        self._save_ref_orbits()
        return True

    def get_orbit(self, reset=False):
        """Return the orbit distortion."""
        nrb = self._ring_extension * self._csorb.NR_BPMS
        refx = self.ref_orbs['X'][:nrb]
        refy = self.ref_orbs['Y'][:nrb]
        if self._mode == self._csorb.SOFBMode.Offline:
            orbx = self.offline_orbit['X'][:nrb]
            orby = self.offline_orbit['Y'][:nrb]
            return _np.hstack([orbx-refx, orby-refy])

        if reset:
            with self._lock_raw_orbs:
                self._reset_orbs()
            _time.sleep(self._smooth_npts/self._acqrate)

        if self.isring and self._mode == self._csorb.SOFBMode.MultiTurn:
            orbs = self.smooth_mtorb
            getorb = self._get_orbit_multiturn
        elif self._mode == self._csorb.SOFBMode.SinglePass:
            orbs = self.smooth_sporb
            getorb = self._get_orbit_singlepass
        elif self.isring and self._mode == self._csorb.SOFBMode.SlowOrb:
            orbs = self.smooth_orb
            getorb = self._get_orbit_online

        for _ in range(3 * self._smooth_npts):
            if orbs['X'] is None or orbs['Y'] is None:
                _time.sleep(1/self._acqrate)
                continue
            orbx, orby = getorb(orbs)
            break
        else:
            msg = 'ERR: get orbit function timeout.'
            self._update_log(msg)
            _log.error(msg[5:])
            orbx = refx
            orby = refy
        return _np.hstack([orbx-refx, orby-refy])

    def _get_orbit_online(self, orbs):
        return orbs['X'], orbs['Y']

    def _get_orbit_singlepass(self, orbs):
        return orbs['X'], orbs['Y']

    def _get_orbit_multiturn(self, orbs):
        idx = self._multiturnidx
        return orbs['X'][idx, :], orbs['Y'][idx, :]

    def set_offline_orbit(self, plane, orb):
        msg = 'Setting New Offline Orbit.'
        self._update_log(msg)
        _log.info(msg)
        orb = _np.array(orb, dtype=float)
        nrb = self._ring_extension * self._csorb.NR_BPMS
        if orb.size % self._csorb.NR_BPMS:
            msg = 'ERR: Wrong OfflineOrb Size.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        elif orb.size < nrb:
            orb2 = _np.zeros(nrb, dtype=float)
            orb2[:orb.size] = orb
            orb = orb2
        self.offline_orbit[plane] = orb
        self.run_callbacks('OfflineOrb'+plane+'-RB', orb[:nrb])
        return True

    def set_smooth_npts(self, num):
        self._smooth_npts = num
        self.run_callbacks('SmoothNrPts-RB', num)
        return True

    def set_smooth_method(self, meth):
        self._smooth_meth = meth
        self.run_callbacks('SmoothMethod-Sts', meth)
        return True

    def set_spass_method(self, meth):
        if self._mode == self._csorb.SOFBMode.SinglePass:
            with self._lock_raw_orbs:
                self._spass_method = meth
                self._reset_orbs()
        self.run_callbacks('SPassMethod-Sts', meth)
        return True

    def set_spass_mask(self, val, beg=True):
        val = int(val) if val > 0 else 0
        other_mask = self._spass_mask[not beg]
        maxsz = self.bpms[0].tbtrate - other_mask - 2
        val = val if val < maxsz else maxsz
        self._spass_mask[beg] = val
        name = 'Beg' if beg else 'End'
        self.run_callbacks('SPassMaskSpl' + name + '-RB', val)

    def set_spass_average(self, val):
        if self._ring_extension != 1 and val != 1:
            msg = 'ERR: Cannot set SPassAvgNrTurns > 1 when RingSize > 1.'
            self._update_log(msg)
            _log.warning(msg[5:])
            return False
        val = int(val) if val > 1 else 1
        self._spass_average = val
        self.run_callbacks('SPassAvgNrTurns-RB', val)

    def set_smooth_reset(self, _):
        with self._lock_raw_orbs:
            self._reset_orbs()
        return True

    def set_ref_orbit(self, plane, orb):
        msg = 'Setting New Reference Orbit.'
        self._update_log(msg)
        _log.info(msg)
        orb = _np.array(orb, dtype=float)
        nrb = self._csorb.NR_BPMS * self._ring_extension
        if orb.size % self._csorb.NR_BPMS:
            msg = 'ERR: Wrong RefOrb Size.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
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

    def set_orbit_acq_rate(self, value):
        trigmds = [self._csorb.SOFBMode.SinglePass, ]
        if self.isring:
            trigmds.append(self._csorb.SOFBMode.MultiTurn)
        if self._mode in trigmds and value > 2:
            msg = 'ERR: In triggered mode cannot set rate > 2.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        self._acqrate = value
        self._orbit_thread.interval = 1/value
        self.run_callbacks('OrbAcqRate-RB', value)
        return True

    def set_orbit_mode(self, value):
        trigmds = [self._csorb.SOFBMode.SinglePass, ]
        if self.isring:
            trigmds.append(self._csorb.SOFBMode.MultiTurn)
        bo1 = self._mode in trigmds
        bo2 = value not in trigmds
        with self._lock_raw_orbs:
            self._mode = value
            if bo1 == bo2:
                acqrate = 2 if not bo2 else self._oldacqrate
                self._oldacqrate = self._acqrate
                self.run_callbacks('OrbAcqRate-SP', acqrate)
                self.set_orbit_acq_rate(acqrate)
            self._reset_orbs()
        if self._mode in trigmds:
            self.trig_acq_config_bpms()
        self.run_callbacks('SOFBMode-Sts', value)
        return True

    def set_orbit_multiturn_idx(self, value):
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
        return True

    def trig_acq_config_bpms(self, *args):
        trigmds = [self._csorb.SOFBMode.SinglePass, ]
        if self.isring:
            trigmds.append(self._csorb.SOFBMode.MultiTurn)
        if self._mode not in trigmds:
            msg = 'ERR: Change to a Triggered mode first.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        for bpm in self.bpms:
            if self.isring and self._mode == self._csorb.SOFBMode.MultiTurn:
                bpm.mode = _csbpm.OpModes.MultiBunch
            else:
                bpm.mode = _csbpm.OpModes.SinglePass
            bpm.configure()
        self.timing.configure()
        return True

    def set_trig_acq_control(self, value):
        for bpm in self.bpms:
            bpm.ctrl = value
        self.run_callbacks('TrigAcqCtrl-Sts', value)
        return True

    def set_trig_acq_channel(self, value):
        try:
            val = self._csorb.TrigAcqChan._fields[value]
            val = _csbpm.AcqChan._fields.index(val)
        except (IndexError, ValueError):
            return False
        for bpm in self.bpms:
            bpm.acq_type = val
        self.run_callbacks('TrigAcqChan-Sts', value)
        self._update_time_vector(channel=value)
        return True

    def set_trig_acq_trigger(self, value):
        val = _csbpm.AcqTrigTyp.Data
        if value == self._csorb.TrigAcqTrig.External:
            val = _csbpm.AcqTrigTyp.External
        for bpm in self.bpms:
            bpm.acq_trigger = val
        self.run_callbacks('TrigAcqTrigger-Sts', value)
        return True

    def set_trig_acq_repeat(self, value):
        for bpm in self.bpms:
            bpm.acq_repeat = value
        self.run_callbacks('TrigAcqRepeat-Sts', value)
        return True

    def set_trig_acq_datachan(self, value):
        try:
            val = self._csorb.TrigAcqDataChan._fields[value]
            val = _csbpm.AcqChan._fields.index(val)
        except (IndexError, ValueError):
            return False
        for bpm in self.bpms:
            bpm.acq_trig_datatype = val
        self.run_callbacks('TrigDataChan-Sts', value)
        return True

    def set_trig_acq_datasel(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datasel = value
        self.run_callbacks('TrigDataSel-Sts', value)
        return True

    def set_trig_acq_datathres(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datathres = value
        self.run_callbacks('TrigDataThres-RB', value)
        return True

    def set_trig_acq_datahyst(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datahyst = value
        self.run_callbacks('TrigDataHyst-RB', value)
        return True

    def set_trig_acq_datapol(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datapol = value
        self.run_callbacks('TrigDataPol-Sts', value)
        return True

    def set_trig_acq_extduration(self, value):
        self.timing.duration = value
        self._update_time_vector(duration=value)
        self.run_callbacks('TrigExtDuration-RB', value)
        return True

    def set_trig_acq_extdelay(self, value):
        self.timing.delay = value
        self._update_time_vector(delay=value)
        self.run_callbacks('TrigExtDelay-RB', value)
        return True

    def set_trig_acq_extsource(self, value):
        self.timing.evtsrc = self._csorb.AcqExtEvtSrc[value]
        self.run_callbacks('TrigExtEvtSrc-Sts', value)
        return True

    def set_trig_acq_nrsamples(self, val, ispost=True):
        val = int(val) if val > 4 else 4
        val = val if val < 20000 else 20000
        suf = 'post' if ispost else 'pre'
        with self._lock_raw_orbs:
            for bpm in self.bpms:
                setattr(bpm, 'nrsamples' + suf, val)
            self._reset_orbs()
            setattr(self, '_acqtrignrsamples' + suf, val)
        self.run_callbacks('TrigNrSamples'+suf.title()+'-RB', val)
        self._update_time_vector()
        return True

    def set_trig_acq_nrshots(self, val):
        val = int(val) if val > 1 else 1
        val = val if val < 1000 else 1000
        with self._lock_raw_orbs:
            for bpm in self.bpms:
                bpm.nrshots = val
            self.timing.nrpulses = val
            self._reset_orbs()
            self._acqtrignrshots = val
        self.run_callbacks('TrigNrShots-RB', val)
        self._update_time_vector()
        return True

    def set_mturndownsample(self, val):
        if self._ring_extension != 1 and val != 1:
            msg = 'ERR: Cannot set DownSample > 1 when RingSize > 1.'
            self._update_log(msg)
            _log.warning(msg[5:])
            return False
        val = int(val) if val > 1 else 1
        val = val if val < 1000 else 1000
        with self._lock_raw_orbs:
            self._mturndownsample = val
            self._reset_orbs()
        self.run_callbacks('MTurnDownSample-RB', val)
        self._update_time_vector()
        return True

    def _update_time_vector(self, delay=None, duration=None, channel=None):
        if not self.isring:
            return
        dl = (delay or self.timing.delay or 0.0) * 1e-6  # from us to s
        dur = (duration or self.timing.duration or 0.0) * 1e-6  # from us to s
        channel = channel or self.bpms[0].acq_type or 0
        # revolution period in s
        if channel == self._csorb.TrigAcqChan.Monit1:
            dt = self.bpms[0].monit1period
        elif channel == self._csorb.TrigAcqChan.FOFB:
            dt = self.bpms[0].fofbperiod
        else:
            dt = self.bpms[0].tbtperiod
        mult = self._mturndownsample * self._ring_extension
        dt *= mult
        nrptpst = self.acqtrignrsamples // mult
        offset = self._acqtrignrsamplespre / mult
        nrst = self._acqtrignrshots
        a = _np.arange(nrst)
        b = _np.arange(nrptpst, dtype=float) + (0.5 - offset)
        vect = dl + dur/nrst*a[:, None] + dt*b[None, :]
        self._timevector = vect.flatten()
        self.run_callbacks('MTurnTime-Mon', self._timevector)
        self.set_orbit_multiturn_idx(self._multiturnidx)

    def _load_ref_orbs(self):
        if _os.path.isfile(self._csorb.REFORBFNAME):
            self.ref_orbs['X'], self.ref_orbs['Y'] = _np.loadtxt(
                                        self._csorb.REFORBFNAME, unpack=True)

    def _save_ref_orbits(self):
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
            path = _os.path.split(self._csorb.REFORBFNAME)[0]
            if not _os.path.isdir(path):
                _os.mkdir(path)
            _np.savetxt(self._csorb.REFORBFNAME, orbs)
        except FileNotFoundError:
            msg = 'WARN: Could not save reference orbit in file.'
            self._update_log(msg)
            _log.warning(msg[6:])

    def _reset_orbs(self):
        self.raw_orbs = {'X': [], 'Y': []}
        self.smooth_orb = {'X': None, 'Y': None}
        self.raw_sporbs = {'X': [], 'Y': [], 'Sum': []}
        self.smooth_sporb = {'X': None, 'Y': None, 'Sum': None}
        self.raw_mtorbs = {'X': [], 'Y': [], 'Sum': []}
        self.smooth_mtorb = {'X': None, 'Y': None, 'Sum': None}

    def _update_orbits(self):
        count = 0
        if self.isring and self._mode == self._csorb.SOFBMode.MultiTurn:
            self._update_multiturn_orbits()
            count = len(self.raw_mtorbs['X'])
        elif self._mode == self._csorb.SOFBMode.SinglePass:
            if self._spass_method == self._csorb.SPassMethod.FromBPMs:
                self._update_online_orbits(sp=True)
            else:
                self._update_singlepass_orbits()
            count = len(self.raw_sporbs['X'])
        elif self.isring:
            self._update_online_orbits(sp=False)
            count = len(self.raw_orbs['X'])
        self.run_callbacks('BufferCount-Mon', count)

    def _update_online_orbits(self, sp=False):
        nrb = self._csorb.NR_BPMS
        orbsz = nrb * self._ring_extension
        orb = _np.zeros(orbsz, dtype=float)
        orbs = {'X': orb, 'Y': orb.copy(), 'Sum': orb.copy()}
        ref = self.ref_orbs
        for i, bpm in enumerate(self.bpms):
            pos = bpm.spposx if sp else bpm.posx
            orbs['X'][i::nrb] = ref['X'][i] if pos is None else pos
            pos = bpm.spposy if sp else bpm.posy
            orbs['Y'][i::nrb] = ref['Y'][i] if pos is None else pos
            pos = bpm.spsum if sp else 0.0
            orbs['Sum'][i::nrb] = 0.0 if pos is None else pos

        planes = ('X', 'Y', 'Sum') if sp else ('X', 'Y')
        smooth = self.smooth_sporb if sp else self.smooth_orb
        for plane in planes:
            with self._lock_raw_orbs:
                raws = self.raw_sporbs if sp else self.raw_orbs
                raws[plane].append(orbs[plane])
                raws[plane] = raws[plane][-self._smooth_npts:]
                if self._smooth_meth == self._csorb.SmoothMeth.Average:
                    orb = _np.mean(raws[plane], axis=0)
                else:
                    orb = _np.median(raws[plane], axis=0)
            smooth[plane] = orb
            pref = 'SPass' if sp else 'Slow'
            name = ('Orb' if plane != 'Sum' else '') + plane
            self.run_callbacks(pref + name + '-Mon', list(orb))

    def _update_multiturn_orbits(self):
        if self._ring_extension != 1 and self._mturndownsample != 1:
            return
        orbs = {'X': [], 'Y': [], 'Sum': []}
        with self._lock_raw_orbs:  # I need the lock here to ensure consistency
            samp = self.acqtrignrsamples
            down = self._mturndownsample
            ringsz = self._ring_extension
            samp -= samp % (ringsz*down)
            if samp < 1:
                msg = 'ERR: Actual nr_samples in MTurn orb calc. is < 1.'
                self._update_log(msg)
                _log.error(msg[5:])
                return
            samp *= self._acqtrignrshots
            orbsz = self._csorb.NR_BPMS * ringsz
            idx = self._multiturnidx
            nr_pts = self._smooth_npts
            for i, bpm in enumerate(self.bpms):
                pos = bpm.mtposx
                if pos is None:
                    posx = _np.full(samp, self.ref_orbs['X'][i])
                elif pos.size < samp:
                    posx = _np.full(samp, self.ref_orbs['X'][i])
                    posx[:pos.size] = pos
                else:
                    posx = pos[:samp]
                pos = bpm.mtposy
                if pos is None:
                    posy = _np.full(samp, self.ref_orbs['Y'][i])
                elif pos.size < samp:
                    posy = _np.full(samp, self.ref_orbs['Y'][i])
                    posy[:pos.size] = pos
                else:
                    posy = pos[:samp]
                pos = bpm.mtsum
                if pos is None:
                    psum = _np.full(samp, 0)
                elif pos.size < samp:
                    psum = _np.full(samp, 0)
                    psum[:pos.size] = pos
                else:
                    psum = pos[:samp]
                orbs['X'].append(posx)
                orbs['Y'].append(posy)
                orbs['Sum'].append(psum)

            for pln, raw in self.raw_mtorbs.items():
                norb = _np.array(orbs[pln], dtype=float)  # bpms x turns
                norb = norb.T.reshape(-1, orbsz)  # turns/rz x rz*bpms
                raw.append(norb)
                del raw[:-nr_pts]
                if self._smooth_meth == self._csorb.SmoothMeth.Average:
                    orb = _np.mean(raw, axis=0)
                else:
                    orb = _np.median(raw, axis=0)
                if down > 1:
                    orb = _np.mean(orb.reshape(-1, down, orbsz), axis=1)
                self.smooth_mtorb[pln] = orb
                orbs[pln] = orb
        for pln, orb in orbs.items():
            name = ('Orb' if pln != 'Sum' else '') + pln
            self.run_callbacks('MTurn' + name + '-Mon', orb.flatten())
            self.run_callbacks(
                'MTurnIdx' + name + '-Mon', orb[idx, :].flatten())

    def _update_singlepass_orbits(self):
        if self._ring_extension != 1 and self._spass_average != 1:
            return
        orbs = {'X': [], 'Y': [], 'Sum': []}
        ringsz = self._ring_extension
        down = self._spass_average
        nr_turns = ringsz * down
        with self._lock_raw_orbs:  # I need the lock here to assure consistency
            dic = {
                'maskbeg': self._spass_mask[0],
                'maskend': self._spass_mask[1],
                'nturns': ringsz * down}
            nr_pts = self._smooth_npts
            for i, bpm in enumerate(self.bpms):
                dic.update({
                    'refx': self.ref_orbs['X'][i],
                    'refy': self.ref_orbs['Y'][i]})
                orbx, orby, Sum = bpm.calc_sp_multiturn_pos(**dic)
                orbs['X'].append(orbx)
                orbs['Y'].append(orby)
                orbs['Sum'].append(Sum)

            for pln, raw in self.raw_sporbs.items():
                norb = _np.array(orbs[pln], dtype=float).T  # turns x bpms
                norb = norb.reshape(-1)
                raw.append(norb)
                del raw[:-nr_pts]
                if self._smooth_meth == self._csorb.SmoothMeth.Average:
                    orb = _np.mean(raw, axis=0)
                else:
                    orb = _np.median(raw, axis=0)
                if down > 1:
                    orb = _np.mean(orb.reshape(down, -1), axis=0)
                self.smooth_sporb[pln] = orb
                name = ('Orb' if pln != 'Sum' else '') + pln
                self.run_callbacks('SPass' + name + '-Mon', list(orb))

    def _update_status(self):
        status = 0b11111
        status = _util.update_bit(
                    status, bit_pos=0, bit_val=not self.timing.connected)
        status = _util.update_bit(
                    status, bit_pos=1, bit_val=not self.timing.is_ok)

        nok = not all(bpm.connected for bpm in self.bpms)
        status = _util.update_bit(v=status, bit_pos=2, bit_val=nok)

        nok = not all(bpm.state for bpm in self.bpms)
        status = _util.update_bit(v=status, bit_pos=3, bit_val=nok)

        nok = not all(bpm.is_ok for bpm in self.bpms)
        status = _util.update_bit(v=status, bit_pos=4, bit_val=nok)

        self._status = status
        self.run_callbacks('OrbStatus-Mon', status)
        self._update_bpmoffsets()

    def _update_bpmoffsets(self):
        nrb = self._csorb.NR_BPMS
        orbx = _np.zeros(nrb * self._ring_extension, dtype=float)
        orby = orbx.copy()
        for i, bpm in enumerate(self.bpms):
            orbx[i::nrb] = bpm.offsetx or 0.0
            orby[i::nrb] = bpm.offsety or 0.0
        self.run_callbacks('BPMOffsetX-Mon', orbx)
        self.run_callbacks('BPMOffsetY-Mon', orby)

    @staticmethod
    def _find_new_downsample(N, d, onlyup=False):
        if d > N:
            return N
        if not N % d:
            return d
        lim = min(N-d+1, d) if not onlyup else N-d+1
        for i in range(1, lim):
            if not N % (d+i):
                return d+i
            elif not onlyup and not N % (d-i):
                return d-i
