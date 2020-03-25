"""Connectors for cycle."""

import time as _time
from math import isclose as _isclose

import numpy as _np
from epics import PV as _PV

from ..namesys import SiriusPVName as _PVName, \
    get_pair_sprb as _get_pair_sprb
from ..envars import VACA_PREFIX
from ..search import PSSearch as _PSSearch, LLTimeSearch as _LLTimeSearch
from ..pwrsupply.csdev import Const as _PSConst, ETypes as _PSet
from ..timesys.csdev import Const as _TIConst, \
    get_hl_trigger_database as _get_trig_db

from .util import pv_timed_get as _pv_timed_get, pv_conn_put as _pv_conn_put, \
    get_trigger_by_psname as _get_trigger_by_psname, \
    TRIGGER_NAMES as _TRIGGER_NAMES
from .bo_cycle_data import DEFAULT_RAMP_NRCYCLES, DEFAULT_RAMP_TOTDURATION, \
    bo_get_default_waveform as _bo_get_default_waveform
from .li_cycle_data import li_get_default_waveform as _li_get_default_waveform

TIMEOUT_CONNECTION = 0.05
SLEEP_CAPUT = 0.1
TIMEOUT_CHECK = 20


class Timing:
    """Timing."""

    EVTNAME_CYCLE = 'Cycle'

    DEFAULT_DURATION = 150  # [us]
    DEFAULT_NRPULSES = 1
    DEFAULT_DELAY = 0  # [us]
    DEFAULT_POLARITY = _TIConst.TrigPol.Normal

    _pvs = dict()
    properties = dict()
    cycle_idx = dict()
    evg_name = ''

    def __init__(self):
        """Init."""
        self._init_properties()
        self._initial_state = dict()
        self._create_pvs()

    def connected(self, sections=list(), return_disconn=False):
        """Return connected state."""
        disconn = set()
        for name, pv in Timing._pvs.items():
            name = _PVName(name)
            if (name.dev == 'EVG' or name.sec in sections) and\
                    not pv.connected:
                disconn.add(pv.pvname)
        if return_disconn:
            return disconn
        return not bool(disconn)

    # ----- main commands -----

    def prepare(self, mode, triggers=list()):
        """Initialize properties."""
        # Enable EVG
        self.enable_evg()
        # Disable Injection
        self.set_injection_state(_TIConst.DsblEnbl.Dsbl)
        # Config. triggers and events
        pvs_2_init = self.get_pvname_2_defval_dict(mode, triggers)
        for prop, defval in pvs_2_init.items():
            pv = Timing._pvs[prop]
            if pv.wait_for_connection(TIMEOUT_CONNECTION):
                pv.value = defval
                _time.sleep(1.5*SLEEP_CAPUT)
        # Update events
        self.update_events()

    def check(self, mode, triggers=list()):
        """Check if timing is configured."""
        pvs_2_init = self.get_pvname_2_defval_dict(mode, triggers)
        for prop, defval in pvs_2_init.items():
            try:
                prop_sts = _get_pair_sprb(prop)[1]
            except TypeError:
                continue
            pv = Timing._pvs[prop_sts]
            if not pv.wait_for_connection(TIMEOUT_CONNECTION):
                return False
            else:
                if prop_sts.propty_name == 'Src':
                    defval = Timing.cycle_idx[prop_sts.device_name]

                if prop_sts.propty_name.endswith(('Duration', 'Delay')):
                    tol = 0.008 * 15
                    if not _isclose(pv.value, defval, abs_tol=tol):
                        # print(pv.pvname, pv.value, defval)
                        return False
                elif isinstance(defval, (_np.ndarray, list, tuple)):
                    if _np.any(pv.value[0:len(defval)] != defval):
                        # print(pv.pvname, pv.value, defval)
                        return False
                elif pv.value != defval:
                    # print(pv.pvname, pv.value, defval)
                    return False
        return True

    def trigger(self, mode):
        """Trigger timming to cycle power supply."""
        if mode == 'Cycle':
            pv = Timing._pvs[Timing.evg_name+':CycleExtTrig-Cmd']
            pv.value = 1
        else:
            pv = Timing._pvs[Timing.evg_name+':InjectionEvt-Sel']
            pv.value = _TIConst.DsblEnbl.Enbl

            pv = Timing._pvs[Timing.evg_name+':InjectionEvt-Sts']
            t0 = _time.time()
            while _time.time() - t0 < TIMEOUT_CHECK*3:
                if pv.value == _TIConst.DsblEnbl.Enbl:
                    break
                _time.sleep(SLEEP_CAPUT)

    # ----- private methods -----

    def enable_evg(self):
        """Enable EVG."""
        pv = Timing._pvs[Timing.evg_name+':DevEnbl-Sts']
        if pv.value == _TIConst.DsblEnbl.Enbl:
            return
        pv_sel = Timing._pvs[Timing.evg_name+':DevEnbl-Sel']
        pv_sel.value = _TIConst.DsblEnbl.Enbl

    def set_injection_state(self, state):
        """Turn on/off InjectionEvt-Sel."""
        pv = Timing._pvs[Timing.evg_name+':InjectionEvt-Sel']
        pv.value = state

    def update_events(self):
        """Update events."""
        pv = Timing._pvs[Timing.evg_name+':UpdateEvt-Cmd']
        pv.value = 1

    def get_cycle_count(self):
        """Get InjCount value."""
        pv = Timing._pvs[Timing.evg_name+':InjCount-Mon']
        return pv.value

    def check_ramp_end(self):
        """Check InjCount == DEFAULT_RAMP_NRCYCLES."""
        pv = Timing._pvs[Timing.evg_name+':InjCount-Mon']
        return (pv.value == DEFAULT_RAMP_NRCYCLES)

    def restore_initial_state(self):
        """Restore initial state."""
        # Config. triggers and events to initial state
        for pvname, init_val in self._initial_state.items():
            if init_val is None:
                continue
            if ':InjectionEvt-Sel' in pvname:
                inj_state = init_val
                continue
            elif ':BucketList-SP' in pvname and isinstance(init_val, int):
                init_val = [init_val, ]
            Timing._pvs[pvname].put(init_val)
            _time.sleep(1.5*SLEEP_CAPUT)
        # Update events
        self.update_events()
        # Set initial injection state
        self.set_injection_state(inj_state)

    def turnoff(self):
        """Turn timing off."""
        pv_event = Timing._pvs[Timing.evg_name+':CycleMode-Sel']
        pv_event.value = _TIConst.EvtModes.Disabled
        pv_bktlist = Timing._pvs[Timing.evg_name+':RepeatBucketList-SP']
        pv_bktlist.value = 0
        for trig in _TRIGGER_NAMES:
            pv = Timing._pvs[trig+':Src-Sel']
            pv.value = _TIConst.DsblEnbl.Dsbl
            pv = Timing._pvs[trig+':State-Sel']
            pv.value = _TIConst.DsblEnbl.Dsbl

    def get_pvnames_by_psnames(self, psnames=list()):
        triggers = _get_trigger_by_psname(psnames)
        pvnames = set()
        for mode in Timing.properties:
            for prop in Timing.properties[mode]:
                prop = _PVName(prop)
                if prop.dev == 'EVG' or prop.device_name in triggers:
                    pvnames.add(prop)
        return pvnames

    def get_pvname_2_defval_dict(self, mode, triggers=list()):
        pvname_2_defval_dict = dict()
        for prop, defval in Timing.properties[mode].items():
            if defval is None:
                continue
            prop = _PVName(prop)
            if prop.dev == 'EVG' or prop.device_name in triggers:
                pvname_2_defval_dict[prop] = defval
        return pvname_2_defval_dict

    # ----- private methods -----

    def _create_pvs(self):
        """Create PVs."""
        Timing._pvs = dict()
        for mode, dict_ in Timing.properties.items():
            for pvname in dict_.keys():
                if pvname in Timing._pvs.keys():
                    continue
                pvname = _PVName(pvname)
                Timing._pvs[pvname] = _PV(
                    VACA_PREFIX+pvname, connection_timeout=TIMEOUT_CONNECTION)

                if pvname.propty_suffix == 'Cmd':
                    continue

                self._initial_state[pvname] = Timing._pvs[pvname].value

                if pvname.propty_suffix == 'SP':
                    pvname_sts = pvname.substitute(propty_suffix='RB')
                elif pvname.propty_suffix == 'Sel':
                    pvname_sts = pvname.substitute(propty_suffix='Sts')
                else:
                    continue
                Timing._pvs[pvname_sts] = _PV(
                    VACA_PREFIX+pvname_sts,
                    connection_timeout=TIMEOUT_CONNECTION)

    @classmethod
    def _init_properties(cls):
        if cls.properties:
            return
        cls.evg_name = _LLTimeSearch.get_evg_name()
        props = {
            'Cycle': {
                # EVG settings
                cls.evg_name+':DevEnbl-Sel': None,
                cls.evg_name+':DevEnbl-Sts': None,
                cls.evg_name+':InjectionEvt-Sel': None,
                cls.evg_name+':UpdateEvt-Cmd': None,

                # Cycle event settings
                cls.evg_name+':CycleMode-Sel': _TIConst.EvtModes.External,
                cls.evg_name+':CycleDelayType-Sel': _TIConst.EvtDlyTyp.Fixed,
                cls.evg_name+':CycleDelay-SP': cls.DEFAULT_DELAY,
                cls.evg_name+':CycleExtTrig-Cmd': None,
            },
            'Ramp': {
                # EVG settings
                cls.evg_name+':DevEnbl-Sel': None,
                cls.evg_name+':DevEnbl-Sts': None,
                cls.evg_name+':InjectionEvt-Sel': None,
                cls.evg_name+':BucketList-SP': [1, ],
                cls.evg_name+':RepeatBucketList-SP': DEFAULT_RAMP_NRCYCLES,
                cls.evg_name+':InjCount-Mon': None,
                cls.evg_name+':UpdateEvt-Cmd': None,

                # Cycle event settings
                cls.evg_name+':CycleMode-Sel': _TIConst.EvtModes.Injection,
                cls.evg_name+':CycleDelayType-Sel': _TIConst.EvtDlyTyp.Incr,
                cls.evg_name+':CycleDelay-SP': cls.DEFAULT_DELAY,
            }
        }

        for trig in _TRIGGER_NAMES:
            for mode in ('Cycle', 'Ramp'):
                props[mode][trig+':Src-Sel'] = cls.EVTNAME_CYCLE
                props[mode][trig+':Duration-SP'] = cls.DEFAULT_DURATION
                props[mode][trig+':NrPulses-SP'] = cls.DEFAULT_NRPULSES
                props[mode][trig+':Delay-SP'] = cls.DEFAULT_DELAY
                props[mode][trig+':Polarity-Sel'] = cls.DEFAULT_POLARITY
                props[mode][trig+':State-Sel'] = _TIConst.DsblEnbl.Enbl

            _trig_db = _get_trig_db(trig)
            cls.cycle_idx[trig] = _trig_db['Src-Sel']['enums'].index('Cycle')
        cls.properties = props


class PSCycler:
    """Handle power supplies properties related to Cycle and RmpWfm modes."""

    properties = [
        'Current-SP', 'Current-RB', 'CurrentRef-Mon',
        'PwrState-Sel', 'PwrState-Sts',
        'OpMode-Sel', 'OpMode-Sts',
        'CycleType-Sel', 'CycleType-Sts',
        'CycleFreq-SP', 'CycleFreq-RB',
        'CycleAmpl-SP', 'CycleAmpl-RB',
        'CycleOffset-SP', 'CycleOffset-RB',
        'CycleNrCycles-SP', 'CycleNrCycles-RB',
        'CycleAuxParam-SP', 'CycleAuxParam-RB',
        'CycleEnbl-Mon',
        'Wfm-SP', 'Wfm-RB',
        'WfmIndex-Mon', 'WfmSyncPulseCount-Mon',
        'IntlkSoft-Mon', 'IntlkHard-Mon',
        'SyncPulse-Cmd'
    ]

    def __init__(self, psname, ramp_config=None):
        """Constructor."""
        self._psname = psname
        self._ramp_config = ramp_config
        self._waveform = None
        self._siggen = None
        self._init_wfm_pulsecnt = None
        self._pvs = dict()
        for prop in PSCycler.properties:
            if prop not in self._pvs.keys():
                self._pvs[prop] = _PV(
                    VACA_PREFIX + self._psname + ':' + prop,
                    connection_timeout=TIMEOUT_CONNECTION)

    @property
    def psname(self):
        """Power supply name."""
        return self._psname

    @property
    def connected(self):
        """Connection state."""
        for prop in PSCycler.properties:
            if not self[prop].connected:
                return False
        return True

    def wait_for_connection(self, timeout=0.5):
        for pv in self._pvs.values():
            if not pv.wait_for_connection(timeout):
                return False
        return True

    @property
    def waveform(self):
        """Default waveform."""
        if self._waveform is None:
            self._waveform = _bo_get_default_waveform(
                psname=self.psname, ramp_config=self._ramp_config)
        return self._waveform

    @property
    def siggen(self):
        """Default siggen."""
        if self._siggen is None:
            self._siggen = _PSSearch.conv_psname_2_siggenconf(self._psname)
        return self._siggen

    @property
    def init_wfm_pulsecnt(self):
        """Initial waveform sync pulse count."""
        if self._init_wfm_pulsecnt is None:
            self.update_wfm_pulsecnt()
        return self._init_wfm_pulsecnt

    def update_wfm_pulsecnt(self):
        """Update waveform sync pulse count to current value."""
        self._init_wfm_pulsecnt = self._pvs['WfmSyncPulseCount-Mon'].get()

    def cycle_duration(self, mode):
        """Return the duration of the cycling in seconds."""
        if mode == 'Cycle':
            return self.siggen.num_cycles/self.siggen.freq
        else:
            return (DEFAULT_RAMP_TOTDURATION)

    def check_intlks(self):
        status = _pv_timed_get(self['IntlkSoft-Mon'], 0, wait=1.0)
        status &= _pv_timed_get(self['IntlkHard-Mon'], 0, wait=1.0)
        return status

    def check_on(self):
        """Return wether power supply PS is on."""
        return _pv_timed_get(self['PwrState-Sts'], _PSConst.PwrStateSts.On)

    def set_current_zero(self):
        """Set PS current to zero ."""
        status = _pv_conn_put(self['Current-SP'], 0)
        return status

    def check_current_zero(self, wait=5):
        """Return wether power supply PS current is zero."""
        return _pv_timed_get(
            self['CurrentRef-Mon'], 0, abs_tol=0.05, wait=wait)

    def set_params(self, mode):
        """Set params to cycle."""
        status = True
        if mode == 'Cycle':
            status &= _pv_conn_put(self['CycleType-Sel'], self.siggen.type)
            _time.sleep(SLEEP_CAPUT)
            status &= _pv_conn_put(self['CycleFreq-SP'], self.siggen.freq)
            _time.sleep(SLEEP_CAPUT)
            status &= _pv_conn_put(self['CycleAmpl-SP'], self.siggen.amplitude)
            _time.sleep(SLEEP_CAPUT)
            status &= _pv_conn_put(self['CycleOffset-SP'], self.siggen.offset)
            _time.sleep(SLEEP_CAPUT)
            status &= _pv_conn_put(self['CycleAuxParam-SP'],
                                   self.siggen.aux_param)
            _time.sleep(SLEEP_CAPUT)
            status &= _pv_conn_put(self['CycleNrCycles-SP'],
                                   self.siggen.num_cycles)
            _time.sleep(SLEEP_CAPUT)
        else:
            status &= _pv_conn_put(self['Wfm-SP'], self.waveform)
            _time.sleep(SLEEP_CAPUT)
        return status

    def check_params(self, mode, wait=5):
        """Return wether power supply cycling parameters are set."""
        status = True
        if mode == 'Cycle':
            type_idx = _PSet.CYCLE_TYPES.index(self.siggen.type)
            status &= _pv_timed_get(self['CycleType-Sts'], type_idx, wait=wait)
            status &= _pv_timed_get(
                self['CycleFreq-RB'], self.siggen.freq, wait=wait)
            status &= _pv_timed_get(
                self['CycleAmpl-RB'], self.siggen.amplitude, wait=wait)
            status &= _pv_timed_get(
                self['CycleOffset-RB'], self.siggen.offset, wait=wait)
            status &= _pv_timed_get(
                self['CycleAuxParam-RB'], self.siggen.aux_param, wait=wait)
            status &= _pv_timed_get(
                self['CycleNrCycles-RB'], self.siggen.num_cycles, wait=wait)
        else:
            status &= _pv_timed_get(self['Wfm-RB'], self.waveform, wait=wait)
        return status

    def prepare(self, mode):
        """Config power supply to cycling mode."""
        if not self.check_opmode_slowref(wait=0.5):
            self.set_opmode_slowref()
            if not self.check_opmode_slowref():
                return False

        if not self.check_current_zero(wait=0.5):
            self.set_current_zero()
            if not self.check_current_zero():
                return False

        if not self.check_params(mode, wait=0.5):
            self.set_params(mode)

        self.update_wfm_pulsecnt()
        return True

    def is_prepared(self, mode):
        """Return wether power supply is ready."""
        if not self.check_current_zero():
            return False
        if not self.check_params(mode):
            return False
        return True

    def set_opmode(self, opmode):
        """Set power supply opmode to mode."""
        return _pv_conn_put(self['OpMode-Sel'], opmode)

    def set_opmode_slowref(self):
        status = self.set_opmode(_PSConst.OpMode.SlowRef)
        _time.sleep(SLEEP_CAPUT)
        return status

    def check_opmode_slowref(self, wait=10):
        return _pv_timed_get(
            self['OpMode-Sts'], _PSConst.States.SlowRef, wait=wait)

    def set_opmode_cycle(self, mode):
        opmode = _PSConst.OpMode.Cycle if mode == 'Cycle'\
            else _PSConst.OpMode.RmpWfm
        return self.set_opmode(opmode)

    def check_opmode_cycle(self, mode, wait=5):
        """Return wether power supply is in mode."""
        opmode = _PSConst.States.Cycle if mode == 'Cycle'\
            else _PSConst.States.RmpWfm
        return _pv_timed_get(self['OpMode-Sts'], opmode, wait=wait)

    def get_cycle_enable(self):
        if not self.connected:
            return False
        return self['CycleEnbl-Mon'].value == _PSConst.DsblEnbl.Enbl

    def pulse(self):
        return _pv_conn_put(self['SyncPulse-Cmd'], 1)

    def check_final_state(self, mode):
        if mode == 'Ramp':
            indices = len(self.waveform)
            status = _pv_timed_get(self['WfmIndex-Mon'], indices, wait=10.0)
            status &= _pv_timed_get(
                self['WfmSyncPulseCount-Mon'],
                self.init_wfm_pulsecnt + DEFAULT_RAMP_NRCYCLES, wait=10.0)
            self.update_wfm_pulsecnt()
            if not status:
                return 1  # indicate lack of trigger pulses
        else:
            status = _pv_timed_get(self['CycleEnbl-Mon'], 0, wait=10.0)
            if not status:
                return 3  # indicate cycling not finished yet

        status = self.check_intlks()
        if not status:
            return 4  # indicate interlock problems

        status = self.set_opmode_slowref()
        status &= self.check_opmode_slowref()
        if not status:
            return 2  # indicate opmode is not in slowref yet

        return 0

    def __getitem__(self, prop):
        """Return item."""
        return self._pvs[prop]


class LinacPSCycler:
    """Handle Linac power supply properties to cycle."""

    properties = [
        'Current-SP', 'Current-Mon', 'PwrState-Sel', 'StatusIntlk-Mon'
    ]

    def __init__(self, psname, ramp_config=None):
        """Constructor."""
        self._psname = psname
        self._waveform = None
        self._cycle_duration = None
        self._times = None
        self._pvs = dict()
        for prop in LinacPSCycler.properties:
            if prop not in self._pvs.keys():
                self._pvs[prop] = _PV(
                    VACA_PREFIX + self._psname + ':' + prop,
                    connection_timeout=TIMEOUT_CONNECTION)

    @property
    def psname(self):
        """Power supply name."""
        return self._psname

    @property
    def connected(self):
        """Return connected state."""
        for prop in LinacPSCycler.properties:
            if not self[prop].connected:
                return False
        return True

    def wait_for_connection(self, timeout=0.5):
        """."""
        for pv in self._pvs.values():
            if not pv.wait_for_connection(timeout):
                return False
        return True

    @property
    def waveform(self):
        """."""
        if self._waveform is None:
            self._get_duration_and_waveform()
        return self._waveform

    def cycle_duration(self, mode):
        """Return the duration of the cycling in seconds."""
        if self._cycle_duration is None:
            self._get_duration_and_waveform()
        return self._cycle_duration

    def check_intlks(self):
        """."""
        if not self.connected:
            return False
        return self['StatusIntlk-Mon'].value < 55

    def check_on(self):
        """Return wether power supply PS is on."""
        return _pv_timed_get(self['PwrState-Sel'], 1)

    def set_current_zero(self):
        """Set PS current to zero ."""
        return _pv_conn_put(self['Current-SP'], 0)

    def check_current_zero(self, wait=5):
        """Return wether power supply PS current is zero."""
        return _pv_timed_get(self['Current-Mon'], 0, abs_tol=0.1, wait=wait)

    def prepare(self, mode):
        """Config power supply to cycling mode."""
        status = True
        if not self.check_current_zero(wait=0.5):
            status &= self.set_current_zero()
        return status

    def is_prepared(self, mode):
        """Return wether power supply is ready."""
        status = self.check_current_zero()
        return status

    def cycle(self):
        """Cycle. This function may run in a thread."""
        for i in range(len(self._waveform)-1):
            self['Current-SP'].value = self._waveform[i]
            _time.sleep(self._times[i+1] - self._times[i])
        self['Current-SP'].value = self._waveform[-1]

    def check_final_state(self, mode):
        status = True
        status &= self.check_on()
        status &= self.check_intlks()
        if not status:
            return 4  # indicate interlock problems
        return 0

    def _get_duration_and_waveform(self):
        """Get duration and waveform."""
        t, w = _li_get_default_waveform(psname=self.psname)
        self._times = t
        self._cycle_duration = max(t)
        self._waveform = w

    def __getitem__(self, prop):
        """Return item."""
        return self._pvs[prop]
