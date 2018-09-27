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
        return conn

    @property
    def is_ok(self):
        ok = super().is_ok
        pv = self._config_pvs_rb['ACQStatus']
        stts = _csbpm.AcqStates
        return ok and pv.value not in (
            stts.Error, stts.NoMemory,
            stts.TooFewSamples, stts.TooManySamples)

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
        return ORB_CONV*self._posx.value if self._posx.connected else None

    @property
    def posy(self):
        return ORB_CONV*self._posy.value if self._posy.connected else None

    @property
    def spposx(self):
        return ORB_CONV*self._spposx.value if self._spposx.connected else None

    @property
    def spposy(self):
        return ORB_CONV*self._spposy.value if self._spposy.connected else None

    @property
    def spsum(self):
        return ORB_CONV*self._spsum.value if self._spsum.connected else None

    @property
    def mtposx(self):
        return ORB_CONV*self._arrayx.value if self._arrayx.connected else None

    @property
    def mtposy(self):
        return ORB_CONV*self._arrayy.value if self._arrayy.connected else None

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
    def nrsamples(self):
        pv = self._config_pvs_rb['ACQNrSamplesPost']
        return pv.value if pv.connected else None

    @nrsamples.setter
    def nrsamples(self, val):
        pv = self._config_pvs_sp['ACQNrSamplesPost']
        if pv.connected:
            self._config_ok_vals['ACQNrSamplesPost'] = val
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
        db['OrbitTrigNrSamples-SP'][prop] = self.set_trig_acq_nrsamples
        db['OrbitTrigNrShots-SP'][prop] = self.set_trig_acq_nrshots
        db['OrbitTrigDownSample-SP'][prop] = self.set_trig_acq_downsample
        db['OrbitRefX-SP'][prop] = _part(self.set_ref_orbit, 'x')
        db['OrbitRefY-SP'][prop] = _part(self.set_ref_orbit, 'y')
        db['OrbitOfflineX-SP'][prop] = _part(self.set_offline_orbit, 'x')
        db['OrbitOfflineY-SP'][prop] = _part(self.set_offline_orbit, 'y')
        db['OrbitSmoothNPnts-SP'][prop] = self.set_smooth_npts
        db['OrbitAcqRate-SP'][prop] = self.set_orbit_acq_rate
        db = super().get_database(db)
        return db

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)
        self._mode = _csorb.OrbitMode.Online
        self.ref_orbs = {
                'x': _np.zeros(self._const.NR_BPMS),
                'y': _np.zeros(self._const.NR_BPMS)}
        self._load_ref_orbs()
        self.raw_orbs = {'x': [], 'y': []}
        self.raw_sporbs = {'x': [], 'y': [], 's': []}
        self.raw_mtorbs = {'x': [], 'y': []}
        self._lock_raw_orbs = Lock()
        self.smooth_orb = {'x': None, 'y': None}
        self.smooth_sporb = {'x': None, 'y': None, 's': None}
        self.smooth_mtorb = {'x': None, 'y': None}
        self.offline_orbit = {
                'x': _np.zeros(self._const.NR_BPMS),
                'y': _np.zeros(self._const.NR_BPMS)}
        self._smooth_npts = 1
        self._acqrate = 10
        self._oldacqrate = self._acqrate
        self._acqtrignrsamples = 200
        self._acqtrignrshots = 1
        self._multiturnidx = 0
        self._acqtrigdownsample = 1
        self.bpms = [BPM(name) for name in self._const.BPM_NAMES]
        self.timing = TimingConfig(acc)
        self._orbit_thread = _Repeat(
                        1/self._acqrate, self._update_orbits, niter=0)
        self._orbit_thread.start()

    @property
    def mode(self):
        return self._mode

    def get_orbit(self, reset=False):
        """Return the orbit distortion."""
        if self._mode == _csorb.OrbitMode.Offline:
            orbx = self.offline_orbit['x']
            orby = self.offline_orbit['y']
            refx = self.ref_orbs['x']
            refy = self.ref_orbs['y']
            return _np.hstack([orbx-refx, orby-refy])

        if reset:
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
            if orbs['x'] is None or orbs['y'] is None:
                _time.sleep(1/self._acqrate)
                continue
            orbx, orby = getorb(orbs)
            break
        else:
            self._update_log('ERR: get orbit function timeout.')
            orbx = self.ref_orbs['x']
            orby = self.ref_orbs['y']

        refx = self.ref_orbs['x']
        refy = self.ref_orbs['y']
        return _np.hstack([orbx-refx, orby-refy])

    def _get_orbit_online(self, orbs):
        return orbs['x'], orbs['y']

    def _get_orbit_singlepass(self, orbs):
        return orbs['x'], orbs['y']

    def _get_orbit_multiturn(self, orbs):
        idx = self._multiturnidx
        return orbs['x'][idx, :], orbs['y'][idx, :]

    def set_offline_orbit(self, plane, value):
        self._update_log('Setting New Offline Orbit.')
        if len(value) != self._const.NR_BPMS:
            self._update_log('ERR: Wrong Size.')
            return False
        self.offline_orbit[plane] = _np.array(value)
        self.run_callbacks(
                    'OrbitOffline'+plane.upper()+'-RB', _np.array(value))
        return True

    def set_smooth_npts(self, num):
        self._update_log('Setting new number of points for median.')
        self._smooth_npts = num
        self.run_callbacks('OrbitSmoothNPnts-RB', num)
        return True

    def set_ref_orbit(self, plane, orb):
        self._update_log('Setting New Reference Orbit.')
        if len(orb) != self._const.NR_BPMS:
            self._update_log('ERR: Wrong Size.')
            return False
        self.ref_orbs[plane] = _np.array(orb, dtype=float)
        self._save_ref_orbits()
        self._reset_orbs()
        self.run_callbacks('OrbitRef'+plane.upper()+'-RB', orb)
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
        if bo1 == bo2:
            acqrate = self._oldacqrate
            self._oldacqrate = self._acqrate
            self.run_callbacks('OrbitAcqRate-SP', acqrate)
            self.set_orbit_acq_rate(acqrate)
        self._mode = value
        self._reset_orbs()
        if self._mode in trigmds:
            self.trig_acq_config_bpms()
        return True

    def set_orbit_multiturn_idx(self, value):
        maxidx = self._acqtrignrsamples * self._acqtrignrshots
        maxidx //= self._acqtrigdownsample
        if value > maxidx:
            self._update_log('ERR: MultiTurnIdx is too large')
            return False
        self._multiturnidx = int(value)
        self.run_callbacks('OrbitMultiTurnIdx-RB', self._multiturnidx)

    def trig_acq_config_bpms(self, *args):
        trigmds = (_csorb.OrbitMode.MultiTurn, _csorb.OrbitMode.SinglePass)
        if self._mode != trigmds:
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

    def set_trig_acq_channel(self, value):
        try:
            val = _csorb.OrbitAcqChan._fields[value]
            val = _csbpm.AcqChan._fields.index(val)
        except (IndexError, ValueError):
            return False
        for bpm in self.bpms:
            bpm.acq_type = val
        self.run_callbacks('OrbitTrigAcqChan-Sts', value)
        return True

    def set_trig_acq_trigger(self, value):
        for bpm in self.bpms:
            bpm.acq_trigger = value + 1  # See PVs Database definition
        self.run_callbacks('OrbitTrigAcqTrigger-Sts', value)

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

    def set_trig_acq_datathres(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datathres = value
        self.run_callbacks('OrbitTrigDataSel-Sts', value)

    def set_trig_acq_datahyst(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datahyst = value
        self.run_callbacks('OrbitTrigDataHyst-Sts', value)

    def set_trig_acq_datapol(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datapol = value
        self.run_callbacks('OrbitTrigDataPol-Sts', value)

    def set_trig_acq_extduration(self, value):
        self.timing.duration = value
        self.run_callbacks('OrbitTrigExtDuration-RB')

    def set_trig_acq_extdelay(self, value):
        self.timing.delay = value
        self.run_callbacks('OrbitTrigExtDelay-RB')

    def set_trig_acq_extsource(self, value):
        self.timing.evtsrc = value
        self.run_callbacks('OrbitTrigExtEvtSrc-Sts')

    def set_trig_acq_nrsamples(self, value):
        for bpm in self.bpms:
            bpm.nrsamples = value
        self._reset_orbs()
        self._acqtrignrsamples = value
        self.run_callbacks('OrbitTrigNrSamples-RB', value)

    def set_trig_acq_nrshots(self, value):
        for bpm in self.bpms:
            bpm.nrsamples = value
        self.timing.nrpulses = value
        self._reset_orbs()
        self._acqtrignrshots = value
        self.run_callbacks('OrbitTrigNrShots-RB', value)

    def set_trig_acq_downsample(self, value):
        nrspls = self._acqtrignrsamples * self._acqtrignrshots
        if value > nrspls:
            self._update_log(
                'ERR: DwnSpl must smaller than NRSamples x NRShots')
            return False
        self._acqtrigdownsample = value
        self.run_callbacks('OrbitTrigDownSample-RB', value)

    def _load_ref_orbs(self):
        if _os.path.isfile(self.REF_ORBIT_FILENAME):
            self.ref_orbs['x'], self.ref_orbs['y'] = _np.loadtxt(
                                        self.REF_ORBIT_FILENAME, unpack=True)

    def _save_ref_orbits(self):
        orbs = _np.array([self.ref_orbs['x'], self.ref_orbs['y']]).T
        _np.savetxt(self.REF_ORBIT_FILENAME, orbs)

    def _reset_orbs(self):
        with self._lock_raw_orbs:
            self.raw_orbs = {'x': [], 'y': []}
            self.smooth_orb = {'x': None, 'y': None}
            self.raw_sporbs = {'x': [], 'y': [], 's': []}
            self.smooth_sporb = {'x': None, 'y': None, 's': None}
            self.raw_mtorbs = {'x': [], 'y': []}
            self.smooth_mtorb = {'x': None, 'y': None}

    def _update_orbits(self):
        if self._mode == _csorb.OrbitMode.MultiTurn:
            self._update_multiturn_orbits()
        elif self._mode == _csorb.OrbitMode.SinglePass:
            self._update_online_orbits(sp=True)
        else:
            self._update_online_orbits(sp=False)

    def _update_online_orbits(self, sp=False):
        orb = _np.zeros(self._const.NR_BPMS, dtype=float)
        orbs = {'x': orb, 'y': orb.copy()}
        if sp:
            orbs['s'] = orb.copy()
        ref = self.ref_orbs
        if sp:
            for i, bpm in enumerate(self.bpms):
                orbs['x'][i] = bpm.spposx or ref['x'][i]
                orbs['y'][i] = bpm.spposy or ref['y'][i]
                orbs['s'][i] = bpm.spsum or 0.0
        else:
            for i, bpm in enumerate(self.bpms):
                orbs['x'][i] = bpm.posx or ref['x'][i]
                orbs['y'][i] = bpm.posy or ref['y'][i]

        planes = ('x', 'y', 's') if sp else ('x', 'y')
        pref = 'SinglePass' if sp else ''
        for plane in planes:
            name = pref + ('Sum' if plane == 's' else plane.upper())
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
        orbs = {'x': [], 'y': []}
        down = self._acqtrigdownsample
        nrspls = self._acqtrignrsamples * self._acqtrignrshots
        samp = down * (nrspls // down)
        nr_bpms = self._const.NR_BPMS
        for i, bpm in enumerate(self.bpms):
            posx = bpm.mtposx
            if posx is None or posx.size < samp:
                posx = _np.full(samp, self.ref_orbs['x'][i])
            posy = bpm.mtposy
            if posy is None or posy.size < samp:
                posy = _np.full(samp, self.ref_orbs['y'][i])
            orbs['x'].append(posx[:samp])
            orbs['y'].append(posy[:samp])

        for plane in ('x', 'y'):
            with self._lock_raw_orbs:
                raws = self.raw_mtorbs
                norb = _np.array(orbs[plane])
                raws[plane].append(norb)
                raws[plane] = raws[plane][-self._smooth_npts:]
                orb = _np.mean(raws[plane], axis=0)
                orb = _np.mean(orb.reshape(nr_bpms, -1, down), axis=2)
                self.smooth_mtorb[plane] = orb.transpose()
            self.run_callbacks(
                'OrbitsMultiTurn'+plane.upper()+'-Mon', orb.flatten())
            self.run_callbacks(
                'OrbitMultiTurn'+plane.upper()+'-Mon',
                orb[:, self._multiturnidx].flatten())

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
