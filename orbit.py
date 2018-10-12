"""Module to deal with orbit acquisition."""

import time as _time
import os as _os
from functools import partial as _part
from threading import Lock
import numpy as _np
from epics import PV as _PV
import siriuspy.util as _util
import siriuspy.csdevice.orbitcorr as _csorb
import siriuspy.csdevice.bpms as _csbpm
import siriuspy.csdevice.timesys as _cstiming
from siriuspy.thread import RepeaterThread as _Repeat
from siriuspy.envars import vaca_prefix as LL_PREF
from .base_class import (
    BaseClass as _BaseClass,
    BaseTimingConfig as _BaseTimingConfig)

TIMEOUT = 0.05
ORB_CONV = _csorb.ORBIT_CONVERSION_UNIT


class BPM(_BaseTimingConfig):

    def __init__(self, name):
        super().__init__(name[:2])
        self._name = name
        opt = {'connection_timeout': TIMEOUT}
        self._posx = _PV(LL_PREF + self._name + ':PosX-Mon', **opt)
        self._posy = _PV(LL_PREF + self._name + ':PosY-Mon', **opt)
        self._spposx = _PV(LL_PREF + self._name + ':SPPosX-Mon', **opt)
        self._spposy = _PV(LL_PREF + self._name + ':SPPosY-Mon', **opt)
        self._spsum = _PV(LL_PREF + self._name + ':SPPosSum-Mon', **opt)
        self._arrayx = _PV(LL_PREF + self._name + ':GEN_XArrayData', **opt)
        self._arrayy = _PV(LL_PREF + self._name + ':GEN_YArrayData', **opt)
        self._arrays = _PV(LL_PREF + self._name + ':GEN_SumArrayData', **opt)
        self._offsetx = _PV(LL_PREF + self._name + ':PosXOffset-RB', **opt)
        self._offsety = _PV(LL_PREF + self._name + ':PosYOffset-RB', **opt)
        self._config_ok_vals = {
            'asyn.ENBL': _csbpm.EnblTyp.Enable,
            'ACQBPMMode': _csbpm.OpModes.MultiBunch,
            'ACQChannel': _csbpm.AcqChan.Monit1,
            'ACQNrShots': 1,
            'ACQTriggerHwDly': 0.0,
            'ACQUpdateTime': 0,
            'ACQNrSamplesPre': 0,
            'ACQNrSamplesPost': 200,
            'ACQCtrl': _csbpm.AcqEvents.Stop,
            'ACQTriggerType': _csbpm.AcqTrigTyp.External,
            'ACQTriggerRep': _csbpm.AcqRepeat.Repetitive,
            'ACQTriggerDataChan': _csbpm.AcqChan.Monit1,
            'ACQTriggerDataSel': _csbpm.AcqDataTyp.Sum,
            'ACQTriggerDataThres': 10,
            'ACQTriggerDataPol': _csbpm.Polarity.Positive,
            'ACQTriggerDataHyst': 2}
        pvs = {
            'asyn.ENBL': 'asyn.ENBL',
            'asyn.CNCT': 'asyn.CNCT',
            'ACQBPMMode': 'ACQBPMMode-Sel',
            'ACQChannel': 'ACQChannel-Sel',
            'ACQNrShots': 'ACQNrShots-SP',
            'ACQTriggerHwDly': 'ACQTriggerHwDly-SP',
            'ACQUpdateTime': 'ACQUpdateTime-SP',
            'ACQNrSamplesPre': 'ACQNrSamplesPre-SP',
            'ACQNrSamplesPost': 'ACQNrSamplesPost-SP',
            'ACQCtrl': 'ACQCtrl-Sel',
            'ACQTriggerType': 'ACQTriggerType-Sel',
            'ACQTriggerRep': 'ACQTriggerRep-Sel',
            'ACQTriggerDataChan': 'ACQTriggerDataChan-Sel',
            'ACQTriggerDataSel': 'ACQTriggerDataSel-Sel',
            'ACQTriggerDataThres': 'ACQTriggerDataThres-SP',
            'ACQTriggerDataPol': 'ACQTriggerDataPol-Sel',
            'ACQTriggerDataHyst': 'ACQTriggerDataHyst-SP'}
        self._config_pvs_sp = {
            k: _PV(LL_PREF+self.name+':'+v, **opt) for k, v in pvs.items()}
        pvs = {
            'asyn.ENBL': 'asyn.ENBL',
            'asyn.CNCT': 'asyn.CNCT',
            'ACQBPMMode': 'ACQBPMMode-Sts',
            'ACQChannel': 'ACQChannel-Sts',
            'ACQNrShots': 'ACQNrShots-RB',
            'ACQTriggerHwDly': 'ACQTriggerHwDly-RB',
            'ACQUpdateTime': 'ACQUpdateTime-RB',
            'ACQNrSamplesPre': 'ACQNrSamplesPre-RB',
            'ACQNrSamplesPost': 'ACQNrSamplesPost-RB',
            'ACQCtrl': 'ACQCtrl-Sts',
            'ACQStatus': 'ACQStatus-Mon',
            'ACQTriggerType': 'ACQTriggerType-Sts',
            'ACQTriggerRep': 'ACQTriggerRep-Sts',
            'ACQTriggerDataChan': 'ACQTriggerDataChan-Sts',
            'ACQTriggerDataSel': 'ACQTriggerDataSel-Sts',
            'ACQTriggerDataThres': 'ACQTriggerDataThres-RB',
            'ACQTriggerDataPol': 'ACQTriggerDataPol-Sts',
            'ACQTriggerDataHyst': 'ACQTriggerDataHyst-RB'}
        self._config_pvs_rb = {
            k: _PV(LL_PREF+self.name+':'+v, **opt) for k, v in pvs.items()}

    @property
    def name(self):
        return self._name

    @property
    def connected(self):
        conn = super().connected
        conn &= self._posx.connected
        conn &= self._posy.connected
        conn &= self._spposx.connected
        conn &= self._spposy.connected
        conn &= self._spsum.connected
        conn &= self._arrayx.connected
        conn &= self._arrayy.connected
        conn &= self._arrays.connected
        conn &= self._offsetx.connected
        conn &= self._offsety.connected
        return conn

    @property
    def is_ok(self):
        ok = super().is_ok
        pv = self._config_pvs_rb['ACQStatus']
        stts = _csbpm.AcqStates
        return ok and pv.value not in (
            stts.Error, stts.No_Memory,
            stts.Too_Few_Samples, stts.Too_Many_Samples)

    @property
    def state(self):
        pv = self._config_pvs_rb['asyn.ENBL']
        return pv.value == _csbpm.EnblTyp.Enable if pv.connected else False

    @state.setter
    def state(self, boo):
        val = _csbpm.EnblTyp.Enable if boo else _csbpm.EnblTyp.Disable
        pv = self._config_pvs_sp['asyn.ENBL']
        if pv.connected:
            self._config_ok_vals['asyn.ENBL'] = val
            pv.put(val, wait=False)

    @property
    def posx(self):
        pv = self._posx
        return ORB_CONV*pv.value if pv.connected else None

    @property
    def posy(self):
        pv = self._posy
        return ORB_CONV*pv.value if pv.connected else None

    @property
    def spposx(self):
        pv = self._spposx
        return ORB_CONV*pv.value if pv.connected else None

    @property
    def spposy(self):
        pv = self._spposy
        return ORB_CONV*pv.value if pv.connected else None

    @property
    def spsum(self):
        pv = self._spsum
        return pv.value if pv.connected else None

    @property
    def mtposx(self):
        pv = self._arrayx
        return ORB_CONV*pv.value if pv.connected else None

    @property
    def mtposy(self):
        pv = self._arrayy
        return ORB_CONV*pv.value if pv.connected else None

    @property
    def mtsum(self):
        pv = self._arrays
        return pv.value if pv.connected else None

    @property
    def offsetx(self):
        pv = self._offsetx
        return ORB_CONV*pv.value if pv.connected else None

    @property
    def offsety(self):
        pv = self._offsety
        return ORB_CONV*pv.value if pv.connected else None

    @property
    def ctrl(self):
        pv = self._config_pvs_rb['ACQCtrl']
        return pv.value if pv.connected else None

    @ctrl.setter
    def ctrl(self, val):
        pv = self._config_pvs_sp['ACQCtrl']
        if pv.connected:
            self._config_ok_vals['ACQCtrl'] = val
            pv.put(val, wait=False)

    @property
    def acq_type(self):
        pv = self._config_pvs_rb['ACQChannel']
        return pv.value if pv.connected else None

    @acq_type.setter
    def acq_type(self, val):
        pv = self._config_pvs_sp['ACQChannel']
        if pv.connected:
            self._config_ok_vals['ACQChannel'] = val
            pv.put(val, wait=False)

    @property
    def acq_trigger(self):
        pv = self._config_pvs_rb['ACQTriggerType']
        return pv.value if pv.connected else None

    @acq_trigger.setter
    def acq_trigger(self, val):
        pv = self._config_pvs_sp['ACQTriggerType']
        if pv.connected:
            self._config_ok_vals['ACQTriggerType'] = val
            pv.put(val, wait=False)

    @property
    def acq_trig_datatype(self):
        pv = self._config_pvs_rb['ACQTriggerDataChan']
        return pv.value if pv.connected else None

    @acq_trig_datatype.setter
    def acq_trig_datatype(self, val):
        pv = self._config_pvs_sp['ACQTriggerDataChan']
        if pv.connected:
            self._config_ok_vals['ACQTriggerDataChan'] = val
            pv.put(val, wait=False)

    @property
    def acq_trig_datasel(self):
        pv = self._config_pvs_rb['ACQTriggerDataSel']
        return pv.value if pv.connected else None

    @acq_trig_datasel.setter
    def acq_trig_datasel(self, val):
        pv = self._config_pvs_sp['ACQTriggerDataSel']
        if pv.connected:
            self._config_ok_vals['ACQTriggerDataSel'] = val
            pv.put(val, wait=False)

    @property
    def acq_trig_datathres(self):
        pv = self._config_pvs_rb['ACQTriggerDataThres']
        return pv.value if pv.connected else None

    @acq_trig_datathres.setter
    def acq_trig_datathres(self, val):
        pv = self._config_pvs_sp['ACQTriggerDataThres']
        if pv.connected:
            self._config_ok_vals['ACQTriggerDataThres'] = val
            pv.put(val, wait=False)

    @property
    def acq_trig_datahyst(self):
        pv = self._config_pvs_rb['ACQTriggerDataHyst']
        return pv.value if pv.connected else None

    @acq_trig_datahyst.setter
    def acq_trig_datahyst(self, val):
        pv = self._config_pvs_sp['ACQTriggerDataHyst']
        if pv.connected:
            self._config_ok_vals['ACQTriggerDataHyst'] = val
            pv.put(val, wait=False)

    @property
    def acq_trig_datapol(self):
        pv = self._config_pvs_rb['ACQTriggerDataPol']
        return pv.value if pv.connected else None

    @acq_trig_datapol.setter
    def acq_trig_datapol(self, val):
        pv = self._config_pvs_sp['ACQTriggerDataPol']
        if pv.connected:
            self._config_ok_vals['ACQTriggerDataPol'] = val
            pv.put(val, wait=False)

    @property
    def nrsamplespost(self):
        pv = self._config_pvs_rb['ACQNrSamplesPost']
        return pv.value if pv.connected else None

    @nrsamplespost.setter
    def nrsamplespost(self, val):
        pv = self._config_pvs_sp['ACQNrSamplesPost']
        if pv.connected:
            self._config_ok_vals['ACQNrSamplesPost'] = val
            pv.put(val, wait=False)

    @property
    def nrsamplespre(self):
        pv = self._config_pvs_rb['ACQNrSamplesPre']
        return pv.value if pv.connected else None

    @nrsamplespre.setter
    def nrsamplespre(self, val):
        pv = self._config_pvs_sp['ACQNrSamplesPre']
        if pv.connected:
            self._config_ok_vals['ACQNrSamplesPre'] = val
            pv.put(val, wait=False)

    @property
    def nrshots(self):
        pv = self._config_pvs_rb['ACQNrShots']
        return pv.value if pv.connected else None

    @nrshots.setter
    def nrshots(self, val):
        pv = self._config_pvs_sp['ACQNrShots']
        if pv.connected:
            self._config_ok_vals['ACQNrShots'] = val
            pv.put(val, wait=False)


class TimingConfig(_BaseTimingConfig):

    def __init__(self, acc):
        super().__init__(acc)
        trig = _csorb.TRIGGER_NAME
        opt = {'connection_timeout': TIMEOUT}
        evt = 'Dig' + acc
        self._config_ok_vals = {
            'Src': _csorb.OrbitAcqExtEvtSrc._fields.index(evt),
            'Delay': 0.0,
            'DelayType': _cstiming.triggers_delay_types.Fixed,
            'NrPulses': 1,
            'Duration': 0.001,
            'State': _cstiming.triggers_states.Enbl,
            'Polarity': _cstiming.triggers_polarities.Normal}
        pref_name = LL_PREF + trig
        self._config_pvs_rb = {
            'Src': _PV(pref_name + 'Src-Sts', **opt),
            'Delay': _PV(pref_name + 'Delay-RB', **opt),
            'DelayType': _PV(pref_name + 'DelayType-Sts', **opt),
            'NrPulses': _PV(pref_name + 'NrPulses-RB', **opt),
            'Duration': _PV(pref_name + 'Duration-RB', **opt),
            'State': _PV(pref_name + 'State-Sts', **opt),
            'Polarity': _PV(pref_name + 'Polarity-Sts', **opt)}
        self._config_pvs_sp = {
            'Src': _PV(pref_name + 'Src-Sel', **opt),
            'Delay': _PV(pref_name + 'Delay-SP', **opt),
            'DelayType': _PV(pref_name + 'DelayType-Sel', **opt),
            'NrPulses': _PV(pref_name + 'NrPulses-SP', **opt),
            'Duration': _PV(pref_name + 'Duration-SP', **opt),
            'State': _PV(pref_name + 'State-Sel', **opt),
            'Polarity': _PV(pref_name + 'Polarity-Sel', **opt)}

    @property
    def nrpulses(self):
        pv = self._config_pvs_rb['NrPulses']
        return pv.value if pv.connected else None

    @nrpulses.setter
    def nrpulses(self, val):
        pv = self._config_pvs_sp['NrPulses']
        if pv.connected:
            self._config_ok_vals['NrPulses'] = val
            pv.put(val, wait=False)

    @property
    def duration(self):
        pv = self._config_pvs_rb['Duration']
        return pv.value if pv.connected else None

    @duration.setter
    def duration(self, val):
        pv = self._config_pvs_sp['Duration']
        if pv.connected:
            self._config_ok_vals['Duration'] = val
            pv.put(val, wait=False)

    @property
    def delay(self):
        pv = self._config_pvs_rb['Delay']
        return pv.value if pv.connected else None

    @delay.setter
    def delay(self, val):
        pv = self._config_pvs_sp['Delay']
        if pv.connected:
            self._config_ok_vals['Delay'] = val
            pv.put(val, wait=False)

    @property
    def evtsrc(self):
        pv = self._config_pvs_rb['Src']
        return pv.value if pv.connected else None

    @evtsrc.setter
    def evtsrc(self, val):
        pv = self._config_pvs_sp['Src']
        if pv.connected:
            self._config_ok_vals['Src'] = val
            pv.put(val, wait=False)


class BaseOrbit(_BaseClass):
    pass


class EpicsOrbit(BaseOrbit):
    """Class to deal with orbit acquisition."""
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    REF_ORBIT_FILENAME = _os.path.join(path_, 'data', 'reference_orbit.siorb')
    del path_

    def get_database(self):
        """Get the database of the class."""
        db = _csorb.get_orbit_database(self.acc)
        prop = 'fun_set_pv'
        db['OrbitMode-Sel'][prop] = self.set_orbit_mode
        db['OrbitMultiTurnIdx-SP'][prop] = self.set_orbit_multiturn_idx
        db['OrbitTrigAcqConfig-Cmd'][prop] = self.trig_acq_config_bpms
        db['OrbitTrigAcqCtrl-Sel'][prop] = self.set_trig_acq_control
        db['OrbitTrigAcqChan-Sel'][prop] = self.set_trig_acq_channel
        db['OrbitTrigAcqTrigger-Sel'][prop] = self.set_trig_acq_trigger
        db['OrbitTrigDataChan-Sel'][prop] = self.set_trig_acq_datachan
        db['OrbitTrigDataSel-Sel'][prop] = self.set_trig_acq_datasel
        db['OrbitTrigDataThres-SP'][prop] = self.set_trig_acq_datathres
        db['OrbitTrigDataHyst-SP'][prop] = self.set_trig_acq_datahyst
        db['OrbitTrigDataPol-Sel'][prop] = self.set_trig_acq_datapol
        db['OrbitTrigExtDuration-SP'][prop] = self.set_trig_acq_extduration
        db['OrbitTrigExtDelay-SP'][prop] = self.set_trig_acq_extdelay
        db['OrbitTrigExtEvtSrc-Sel'][prop] = self.set_trig_acq_extsource
        db['OrbitTrigNrSamplesPre-SP'][prop] = _part(
            self.set_trig_acq_nrsamples, ispost=False)
        db['OrbitTrigNrSamplesPost-SP'][prop] = _part(
            self.set_trig_acq_nrsamples, ispost=True)
        db['OrbitTrigNrShots-SP'][prop] = self.set_trig_acq_nrshots
        db['OrbitTrigDownSample-SP'][prop] = self.set_trig_acq_downsample
        db['OrbitRefX-SP'][prop] = _part(self.set_ref_orbit, 'X')
        db['OrbitRefY-SP'][prop] = _part(self.set_ref_orbit, 'Y')
        db['OrbitOfflineX-SP'][prop] = _part(self.set_offline_orbit, 'X')
        db['OrbitOfflineY-SP'][prop] = _part(self.set_offline_orbit, 'Y')
        db['OrbitSmoothNPnts-SP'][prop] = self.set_smooth_npts
        db['OrbitSmoothReset-Cmd'][prop] = self.set_smooth_reset
        db['OrbitAcqRate-SP'][prop] = self.set_orbit_acq_rate
        db = super().get_database(db)
        return db

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)
        self._mode = _csorb.OrbitMode.Online
        self.ref_orbs = {
                'X': _np.zeros(self._const.NR_BPMS),
                'Y': _np.zeros(self._const.NR_BPMS)}
        self._load_ref_orbs()
        self.raw_orbs = {'X': [], 'Y': []}
        self.raw_sporbs = {'X': [], 'Y': [], 'Sum': []}
        self.raw_mtorbs = {'X': [], 'Y': [], 'Sum': []}
        self._lock_raw_orbs = Lock()
        self.smooth_orb = {'X': None, 'Y': None}
        self.smooth_sporb = {'X': None, 'Y': None, 'Sum': None}
        self.smooth_mtorb = {'X': None, 'Y': None, 'Sum': None}
        self.offline_orbit = {
                'X': _np.zeros(self._const.NR_BPMS),
                'Y': _np.zeros(self._const.NR_BPMS)}
        self._smooth_npts = 1
        self._acqrate = 10
        self._oldacqrate = self._acqrate
        self._acqtrignrsamplespre = 0
        self._acqtrignrsamplespost = 200
        self._acqtrignrshots = 1
        self._multiturnidx = 0
        self._acqtrigdownsample = 1
        self._timevector = None
        self.bpms = [BPM(name) for name in self._const.BPM_NAMES]
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

    def get_orbit(self, reset=False):
        """Return the orbit distortion."""
        if self._mode == _csorb.OrbitMode.Offline:
            orbx = self.offline_orbit['X']
            orby = self.offline_orbit['Y']
            refx = self.ref_orbs['X']
            refy = self.ref_orbs['Y']
            return _np.hstack([orbx-refx, orby-refy])

        if reset:
            with self._lock_raw_orbs:
                self._reset_orbs()
            _time.sleep(self._smooth_npts/self._acqrate)

        if self._mode == _csorb.OrbitMode.MultiTurn:
            orbs = self.smooth_mtorb
            getorb = self._get_orbit_multiturn
        elif self._mode == _csorb.OrbitMode.SinglePass:
            orbs = self.smooth_sporb
            getorb = self._get_orbit_singlepass
        elif self._mode == _csorb.OrbitMode.Online:
            orbs = self.smooth_orb
            getorb = self._get_orbit_online

        for _ in range(3 * self._smooth_npts):
            if orbs['X'] is None or orbs['Y'] is None:
                _time.sleep(1/self._acqrate)
                continue
            orbx, orby = getorb(orbs)
            break
        else:
            self._update_log('ERR: get orbit function timeout.')
            orbx = self.ref_orbs['X']
            orby = self.ref_orbs['Y']

        refx = self.ref_orbs['X']
        refy = self.ref_orbs['Y']
        return _np.hstack([orbx-refx, orby-refy])

    def _get_orbit_online(self, orbs):
        return orbs['X'], orbs['Y']

    def _get_orbit_singlepass(self, orbs):
        return orbs['X'], orbs['Y']

    def _get_orbit_multiturn(self, orbs):
        idx = self._multiturnidx
        return orbs['X'][idx, :], orbs['Y'][idx, :]

    def set_offline_orbit(self, plane, orb):
        self._update_log('Setting New Offline Orbit.')
        if len(orb) != self._const.NR_BPMS:
            self._update_log('ERR: Wrong Size.')
            return False
        self.offline_orbit[plane] = _np.array(orb)
        self.run_callbacks('OrbitOffline'+plane+'-RB', orb)
        return True

    def set_smooth_npts(self, num):
        self._smooth_npts = num
        self.run_callbacks('OrbitSmoothNPnts-RB', num)
        return True

    def set_smooth_reset(self, _):
        with self._lock_raw_orbs:
            self._reset_orbs()

    def set_ref_orbit(self, plane, orb):
        self._update_log('Setting New Reference Orbit.')
        if len(orb) != self._const.NR_BPMS:
            self._update_log('ERR: Wrong Size.')
            return False
        self.ref_orbs[plane] = _np.array(orb, dtype=float)
        self._save_ref_orbits()
        with self._lock_raw_orbs:
            self._reset_orbs()
        self.run_callbacks('OrbitRef'+plane+'-RB', orb)
        return True

    def set_orbit_acq_rate(self, value):
        trigmds = (_csorb.OrbitMode.MultiTurn, _csorb.OrbitMode.SinglePass)
        if self._mode in trigmds and value > 2:
            self._update_log('ERR: In triggered mode cannot set rate > 2.')
            return False
        self._acqrate = value
        self._orbit_thread.interval = 1/value
        self.run_callbacks('OrbitAcqRate-RB', value)
        return True

    def set_orbit_mode(self, value):
        trigmds = (_csorb.OrbitMode.MultiTurn, _csorb.OrbitMode.SinglePass)
        bo1 = self._mode in trigmds
        bo2 = value not in trigmds
        self._mode = value
        if bo1 == bo2:
            acqrate = 2 if not bo2 else self._oldacqrate
            self._oldacqrate = self._acqrate
            self.run_callbacks('OrbitAcqRate-SP', acqrate)
            self.set_orbit_acq_rate(acqrate)
        self.run_callbacks('OrbitMode-Sts', value)
        with self._lock_raw_orbs:
            self._reset_orbs()
            if self._mode in trigmds:
                self.trig_acq_config_bpms()
        return True

    def set_orbit_multiturn_idx(self, value):
        maxidx = self.acqtrignrsamples // self._acqtrigdownsample
        maxidx *= self._acqtrignrshots
        if value >= maxidx:
            value = maxidx-1
            self._update_log(
                'WARN: MultiTurnIdx is too large. Redefining...')
        with self._lock_raw_orbs:
            self._multiturnidx = int(value)
        self.run_callbacks('OrbitMultiTurnIdx-RB', self._multiturnidx)
        self.run_callbacks(
            'OrbitMultiTurnIdxTime-Mon', self._timevector[self._multiturnidx])
        return True

    def trig_acq_config_bpms(self, *args):
        trigmds = (_csorb.OrbitMode.MultiTurn, _csorb.OrbitMode.SinglePass)
        if self._mode not in trigmds:
            self._update_log('ERR: Change to SinglePass/MultiTurn first.')
            return False
        for bpm in self.bpms:
            bpm.configure()
        self.timing.configure()
        return True

    def set_trig_acq_control(self, value):
        for bpm in self.bpms:
            bpm.ctrl = value
        self.run_callbacks('OrbitTrigAcqCtrl-Sts', value)
        return True

    def set_trig_acq_channel(self, value):
        try:
            val = _csorb.OrbitAcqChan._fields[value]
            val = _csbpm.AcqChan._fields.index(val)
        except (IndexError, ValueError):
            return False
        for bpm in self.bpms:
            bpm.acq_type = val
        self.run_callbacks('OrbitTrigAcqChan-Sts', value)
        self._update_time_vector(channel=value)
        return True

    def set_trig_acq_trigger(self, value):
        for bpm in self.bpms:
            bpm.acq_trigger = value + 1  # See PVs Database definition
        self.run_callbacks('OrbitTrigAcqTrigger-Sts', value)
        return True

    def set_trig_acq_datachan(self, value):
        try:
            val = _csorb.OrbitAcqDataChan._fields[value]
            val = _csbpm.AcqChan._fields.index(val)
        except (IndexError, ValueError):
            return False
        for bpm in self.bpms:
            bpm.acq_trig_datatype = val
        self.run_callbacks('OrbitTrigDataChan-Sts', value)
        return True

    def set_trig_acq_datasel(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datasel = value
        self.run_callbacks('OrbitTrigDataSel-Sts', value)
        return True

    def set_trig_acq_datathres(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datathres = value
        self.run_callbacks('OrbitTrigDataSel-SP', value)
        return True

    def set_trig_acq_datahyst(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datahyst = value
        self.run_callbacks('OrbitTrigDataHyst-RB', value)
        return True

    def set_trig_acq_datapol(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datapol = value
        self.run_callbacks('OrbitTrigDataPol-Sts', value)
        return True

    def set_trig_acq_extduration(self, value):
        self.timing.duration = value
        self._update_time_vector(duration=value)
        self.run_callbacks('OrbitTrigExtDuration-RB', value)
        return True

    def set_trig_acq_extdelay(self, value):
        self.timing.delay = value
        self._update_time_vector(delay=value)
        self.run_callbacks('OrbitTrigExtDelay-RB', value)
        return True

    def set_trig_acq_extsource(self, value):
        self.timing.evtsrc = value
        self.run_callbacks('OrbitTrigExtEvtSrc-Sts', value)
        return True

    def set_trig_acq_nrsamples(self, value, ispost=True):
        Nmax = _csorb.MAX_MT_ORBS // self._acqtrignrshots
        Nmax *= self._acqtrigdownsample
        suf = 'post' if ispost else 'pre'
        osuf = 'pre' if ispost else 'post'
        value += getattr(self, '_acqtrignrsamples'+osuf)

        nval = value if value <= Nmax else Nmax
        nval = self._find_new_nrsamples(nval, self._acqtrigdownsample)
        if nval != value:
            value = nval
            self._update_log(
                'WARN: Not possible to set NrSamples. Redefining..')

        value -= getattr(self, '_acqtrignrsamples'+osuf)
        with self._lock_raw_orbs:
            for bpm in self.bpms:
                setattr(bpm, 'nrsamples'+suf, value)
            self._reset_orbs()
            setattr(self, '_acqtrignrsamples'+suf, value)
        self.run_callbacks('OrbitTrigNrSamples'+suf.title()+'-RB', value)
        self._update_time_vector()
        return True

    def set_trig_acq_nrshots(self, value):
        pntspshot = self.acqtrignrsamples // self._acqtrigdownsample
        nrpoints = pntspshot * value
        if nrpoints > _csorb.MAX_MT_ORBS:
            value = _csorb.MAX_MT_ORBS // pntspshot
            self._update_log(
                'WARN: Not possible to set NrShots. Redefining...')
        with self._lock_raw_orbs:
            for bpm in self.bpms:
                bpm.nrshots = value
            self.timing.nrpulses = value
            self._reset_orbs()
            self._acqtrignrshots = value
        self.run_callbacks('OrbitTrigNrShots-RB', value)
        self._update_time_vector()
        return True

    def set_trig_acq_downsample(self, value):
        down = self._find_new_downsample(self.acqtrignrsamples, value)
        nrpoints = (self.acqtrignrsamples // down) * self._acqtrignrshots
        if nrpoints > _csorb.MAX_MT_ORBS:
            down = self._find_new_downsample(
                self.acqtrignrsamples, value, onlyup=True)
        if down != value:
            value = down
            self._update_log(
                'WARN: DwnSpl Must divide NRSamples. Redefining...')
        self._acqtrigdownsample = value
        self.run_callbacks('OrbitTrigDownSample-RB', value)
        self._update_time_vector()
        return True

    def _update_time_vector(self, delay=None, duration=None, channel=None):
        dl = (delay or self.timing.delay or 0.0) / 1000
        dur = duration or self.timing.duration or 0.0
        channel = channel or self.bpms[0].acq_type or 0
        # revolution period in ms
        T0 = (496.8 if self._acc == 'BO' else 518.396) / 299792458 * 1000
        if channel == _csorb.OrbitAcqChan.Monit1:
            dt = 578 * T0
        elif channel == _csorb.OrbitAcqChan.FOFB:
            dt = 5 * T0
        else:
            dt = T0

        dt *= self._acqtrigdownsample
        nrptpst = self.acqtrignrsamples // self._acqtrigdownsample
        offset = self._acqtrignrsamplespre / self._acqtrigdownsample
        nrst = self._acqtrignrshots
        a = _np.arange(nrst)
        b = _np.arange(nrptpst, dtype=float) + (0.5 - offset)
        vect = dl + dur/nrst*a[:, None] + dt*b[None, :]
        self._timevector = vect.flatten()
        self.run_callbacks('OrbitMultiTurnTime-Mon', self._timevector)
        self.set_orbit_multiturn_idx(self._multiturnidx)

    def _load_ref_orbs(self):
        if _os.path.isfile(self.REF_ORBIT_FILENAME):
            self.ref_orbs['X'], self.ref_orbs['Y'] = _np.loadtxt(
                                        self.REF_ORBIT_FILENAME, unpack=True)

    def _save_ref_orbits(self):
        orbs = _np.array([self.ref_orbs['X'], self.ref_orbs['Y']]).T
        try:
            _np.savetxt(self.REF_ORBIT_FILENAME, orbs)
        except FileNotFoundError:
            self._update_log('WARN: Could not save reference orbit in file.')

    def _reset_orbs(self):
        self.raw_orbs = {'X': [], 'Y': []}
        self.smooth_orb = {'X': None, 'Y': None}
        self.raw_sporbs = {'X': [], 'Y': [], 'Sum': []}
        self.smooth_sporb = {'X': None, 'Y': None, 'Sum': None}
        self.raw_mtorbs = {'X': [], 'Y': [], 'Sum': []}
        self.smooth_mtorb = {'X': None, 'Y': None, 'Sum': None}

    def _update_orbits(self):
        if self._mode == _csorb.OrbitMode.MultiTurn:
            self._update_multiturn_orbits()
        elif self._mode == _csorb.OrbitMode.SinglePass:
            self._update_online_orbits(sp=True)
        else:
            self._update_online_orbits(sp=False)

    def _update_online_orbits(self, sp=False):
        orb = _np.zeros(self._const.NR_BPMS, dtype=float)
        orbs = {'X': orb, 'Y': orb.copy()}
        if sp:
            orbs['Sum'] = orb.copy()
        ref = self.ref_orbs
        if sp:
            for i, bpm in enumerate(self.bpms):
                orbs['X'][i] = bpm.spposx or ref['X'][i]
                orbs['Y'][i] = bpm.spposy or ref['Y'][i]
                orbs['Sum'][i] = bpm.spsum or 0.0
        else:
            for i, bpm in enumerate(self.bpms):
                orbs['X'][i] = bpm.posx or ref['X'][i]
                orbs['Y'][i] = bpm.posy or ref['Y'][i]

        planes = ('X', 'Y', 'Sum') if sp else ('X', 'Y')
        pref = 'SinglePass' if sp else ''
        for plane in planes:
            name = pref + plane
            self.run_callbacks('OrbitRaw' + name + '-Mon', list(orb))
            with self._lock_raw_orbs:
                raws = self.raw_sporbs if sp else self.raw_orbs
                raws[plane].append(orbs[plane])
                raws[plane] = raws[plane][-self._smooth_npts:]
                orb = _np.mean(raws[plane], axis=0)
            if sp:
                self.smooth_sporb[plane] = orb
            else:
                self.smooth_orb[plane] = orb
            self.run_callbacks('OrbitSmooth' + name + '-Mon', list(orb))

    def _update_multiturn_orbits(self):
        orbs = {'X': [], 'Y': [], 'Sum': []}
        with self._lock_raw_orbs:  # I need the lock here to assure consistency
            samp = self.acqtrignrsamples * self._acqtrignrshots
            nr_bpms = self._const.NR_BPMS
            down = self._acqtrigdownsample
            idx = self._multiturnidx
            nr_pts = self._smooth_npts
            for i, bpm in enumerate(self.bpms):
                posx = bpm.mtposx
                if posx is None or posx.size < samp:
                    posx = _np.full(samp, self.ref_orbs['X'][i])
                posy = bpm.mtposy
                if posy is None or posy.size < samp:
                    posy = _np.full(samp, self.ref_orbs['Y'][i])
                psum = bpm.mtsum
                if psum is None or psum.size < samp:
                    psum = _np.full(samp, 0)
                orbs['X'].append(posx[:samp])
                orbs['Y'].append(posy[:samp])
                orbs['Sum'].append(psum[:samp])

            for pln, raw in self.raw_mtorbs.items():
                norb = _np.array(orbs[pln], dtype=float)
                norb += float(_np.random.rand(1)*1000)
                raw.append(norb)
                del raw[:-nr_pts]
                orb = _np.mean(raw, axis=0)
                if down > 1:
                    orb = _np.mean(orb.reshape(nr_bpms, -1, down), axis=2)
                orb = orb.transpose()
                self.smooth_mtorb[pln] = orb
                orbs[pln] = orb
        for pln, orb in orbs.items():
            self.run_callbacks('OrbitsMultiTurn'+pln+'-Mon', orb.flatten())
            self.run_callbacks(
                'OrbitMultiTurn'+pln+'-Mon', orb[idx, :].flatten())

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
        self.run_callbacks('OrbitStatus-Mon', status)
        self._update_bpmoffsets()

    def _update_bpmoffsets(self):
        orbx = _np.zeros(self._const.NR_BPMS, dtype=float)
        orby = orbx.copy()
        for i, bpm in enumerate(self.bpms):
            orbx[i] = bpm.offsetx or 0
            orby[i] = bpm.offsety or 0
        self.run_callbacks('BPMOffsetsX-Mon', orbx)
        self.run_callbacks('BPMOffsetsY-Mon', orby)

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

    @staticmethod
    def _find_new_nrsamples(N, d):
        return d*(N//d) if N >= d else d
