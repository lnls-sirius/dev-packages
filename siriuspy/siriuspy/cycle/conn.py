"""Connectors for cycle."""

import time as _time
from epics import PV as _PV
from math import isclose as _isclose
import numpy as _np

from siriuspy.namesys import SiriusPVName as _PVName, \
    get_pair_sprb as _get_pair_sprb
from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.search import MASearch as _MASearch, PSSearch as _PSSearch, \
    LLTimeSearch as _LLTimeSearch
from siriuspy.csdevice.pwrsupply import Const as _PSConst, ETypes as _PSet
from siriuspy.csdevice.timesys import Const as _TIConst, \
    get_hl_trigger_database as _get_trig_db

from .util import pv_timed_get as _pv_timed_get, pv_conn_put as _pv_conn_put
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

    _trigger_list = [
        'TB-Glob:TI-Mags', 'BO-Glob:TI-Mags', 'BO-Glob:TI-Corrs']
    # TODO: uncomment when using TS and SI
    #     'TS-Glob:TI-Mags', 'SI-Glob:TI-Dips', 'SI-Glob:TI-Quads',
    #     'SI-Glob:TI-Sexts', 'SI-Glob:TI-Skews', 'SI-Glob:TI-Corrs']

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

    def prepare(self, mode, sections=list()):
        """Initialize properties."""
        # Enable EVG
        self.enable_evg()
        # Disable Injection
        self.set_injection_state(_TIConst.DsblEnbl.Dsbl)
        # Config. triggers and events
        pvs_2_init = self.get_pvname_2_defval_dict(mode, sections)
        for prop, defval in pvs_2_init.items():
            pv = Timing._pvs[prop]
            pv.get()  # force connection
            if pv.connected:
                pv.value = defval
                _time.sleep(1.5*SLEEP_CAPUT)
        # Update events
        self.update_events()

    def check(self, mode, sections=list()):
        """Check if timing is configured."""
        pvs_2_init = self.get_pvname_2_defval_dict(mode, sections)
        for prop, defval in pvs_2_init.items():
            try:
                prop_sts = _get_pair_sprb(prop)[1]
            except TypeError:
                continue
            pv = Timing._pvs[prop_sts]
            pv.get()  # force connection
            if not pv.connected:
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
        """Trigger timming to cycle magnets."""
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

    # ----- auxiliar methods -----

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
        for trig in self._trigger_list:
            pv = Timing._pvs[trig+':Src-Sel']
            pv.value = _TIConst.DsblEnbl.Dsbl
            pv = Timing._pvs[trig+':State-Sel']
            pv.value = _TIConst.DsblEnbl.Dsbl

    def get_pvnames_by_section(self, sections=list()):
        pvnames = set()
        for mode in Timing.properties:
            for prop in Timing.properties[mode]:
                prop = _PVName(prop)
                if prop.dev == 'EVG' or prop.sec in sections:
                    pvnames.add(prop)
        return pvnames

    def get_pvname_2_defval_dict(self, mode, sections=list()):
        pvname_2_defval_dict = dict()
        for prop, defval in Timing.properties[mode].items():
            if defval is None:
                continue
            prop = _PVName(prop)
            if prop.dev == 'EVG' or prop.sec in sections:
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
                self._initial_state[pvname] = Timing._pvs[pvname].get()

                if pvname.propty_suffix == 'SP':
                    pvname_sts = pvname.substitute(propty_suffix='RB')
                elif pvname.propty_suffix == 'Sel':
                    pvname_sts = pvname.substitute(propty_suffix='Sts')
                else:
                    continue
                Timing._pvs[pvname_sts] = _PV(
                    VACA_PREFIX+pvname_sts,
                    connection_timeout=TIMEOUT_CONNECTION)
                Timing._pvs[pvname_sts].get()  # force connection

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

        for trig in cls._trigger_list:
            for mode in ['Cycle', 'Ramp']:
                props[mode][trig+':Src-Sel'] = cls.EVTNAME_CYCLE
                props[mode][trig+':Duration-SP'] = cls.DEFAULT_DURATION
                props[mode][trig+':NrPulses-SP'] = cls.DEFAULT_NRPULSES
                props[mode][trig+':Delay-SP'] = cls.DEFAULT_DELAY
                props[mode][trig+':Polarity-Sel'] = cls.DEFAULT_POLARITY
                props[mode][trig+':State-Sel'] = _TIConst.DsblEnbl.Enbl

            _trig_db = _get_trig_db(trig)
            cls.cycle_idx[trig] = _trig_db['Src-Sel']['enums'].index('Cycle')
        cls.properties = props


class MagnetCycler:
    """Handle magnet properties related to Cycle and RmpWfm ps modes."""

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
        'IntlkSoft-Mon', 'IntlkHard-Mon'
    ]

    def __init__(self, maname, ramp_config=None):
        """Constructor."""
        self._maname = maname
        self._psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self._ramp_config = ramp_config
        self._waveform = None
        self._siggen = None
        self._init_wfm_pulsecnt = None
        self._pvs = dict()
        for prop in MagnetCycler.properties:
            if prop not in self._pvs.keys():
                pvname = VACA_PREFIX + self._maname + ':' + prop
                self._pvs[prop] = _PV(
                    pvname, connection_timeout=TIMEOUT_CONNECTION)
                self._pvs[prop].get()

    @property
    def maname(self):
        """Magnet name."""
        return self._maname

    @property
    def connected(self):
        """Connection state."""
        for prop in MagnetCycler.properties:
            if prop in ['Wfm-SP', 'Wfm-RB', 'WfmIndex-Mon',
                        'WfmSyncPulseCount-Mon'] and 'TB' in self.maname:
                pass
            elif not self[prop].connected:
                return False
        return True

    @property
    def waveform(self):
        """Default waveform."""
        if self._waveform is None:
            self._waveform = _bo_get_default_waveform(
                maname=self.maname, ramp_config=self._ramp_config)
        return self._waveform

    @property
    def siggen(self):
        """Default siggen."""
        if self._siggen is None:
            self._siggen = _PSSearch.conv_psname_2_siggenconf(self._psnames[0])
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
        """Return wether magnet PS is on."""
        return _pv_timed_get(self['PwrState-Sts'], _PSConst.PwrStateSts.On)

    def set_current_zero(self):
        """Set PS current to zero ."""
        return _pv_conn_put(self['Current-SP'], 0)

    def check_current_zero(self):
        """Return wether magnet PS current is zero."""
        if not self.connected:
            return False
        return _isclose(self['CurrentRef-Mon'].value, 0, abs_tol=0.05)

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
        else:
            status &= _pv_conn_put(self['Wfm-SP'], self.waveform)
        return status

    def check_params(self, mode):
        """Return wether magnet cycling parameters are set."""
        status = True
        if mode == 'Cycle':
            type_idx = _PSet.CYCLE_TYPES.index(self.siggen.type)
            status &= _pv_timed_get(self['CycleType-Sts'], type_idx)
            status &= _pv_timed_get(self['CycleFreq-RB'], self.siggen.freq)
            status &= _pv_timed_get(
                self['CycleAmpl-RB'], self.siggen.amplitude)
            status &= _pv_timed_get(self['CycleOffset-RB'], self.siggen.offset)
            status &= _pv_timed_get(
                self['CycleAuxParam-RB'], self.siggen.aux_param)
            status &= _pv_timed_get(
                self['CycleNrCycles-RB'], self.siggen.num_cycles)
        else:
            status &= _pv_timed_get(self['Wfm-RB'], self.waveform)
        return status

    def prepare(self, mode):
        """Config magnet to cycling mode."""
        status = True

        status &= self.set_opmode_slowref()
        status &= _pv_timed_get(self['OpMode-Sts'], _PSConst.States.SlowRef)

        status &= self.set_current_zero()
        status &= self.check_current_zero()

        status &= self.set_params(mode)
        status &= self.check_params(mode)

        self.update_wfm_pulsecnt()
        return status

    def is_prepared(self, mode):
        """Return wether magnet is ready."""
        status = True
        status &= self.check_current_zero()
        status &= self.check_params(mode)
        return status

    def set_opmode(self, opmode):
        """Set magnet opmode to mode."""
        return _pv_conn_put(self['OpMode-Sel'], opmode)

    def set_opmode_slowref(self):
        return self.set_opmode(_PSConst.OpMode.SlowRef)

    def set_opmode_cycle(self, mode):
        opmode = _PSConst.OpMode.Cycle if mode == 'Cycle'\
            else _PSConst.OpMode.RmpWfm
        return self.set_opmode(opmode)

    def check_opmode_cycle(self, mode):
        """Return wether magnet is in mode."""
        opmode = _PSConst.States.Cycle if mode == 'Cycle'\
            else _PSConst.States.RmpWfm
        return _pv_timed_get(self['OpMode-Sts'], opmode)

    def get_cycle_enable(self):
        if not self.connected:
            return False
        return self['CycleEnbl-Mon'].value == _PSConst.DsblEnbl.Enbl

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

            status = self.set_opmode_slowref()
            status &= _pv_timed_get(
                self['OpMode-Sts'], _PSConst.States.SlowRef)
            if not status:
                return 2  # indicate opmode is not in slowref yet
        else:
            status = _pv_timed_get(self['CycleEnbl-Mon'], 0, wait=10.0)
            if not status:
                return 3  # indicate cycling not finished yet

        status = self.check_intlks()
        if not status:
            return 4  # indicate interlock problems

        return 0

    def __getitem__(self, prop):
        """Return item."""
        return self._pvs[prop]


class LinacMagnetCycler:
    """Handle Linac magnet properties to cycle."""

    properties = [
        'seti', 'rdi', 'setpwm', 'interlock'
    ]

    def __init__(self, maname, ramp_config=None):
        """Constructor."""
        self._maname = maname
        self._waveform = None
        self._cycle_duration = None
        self._pvs = dict()
        for prop in LinacMagnetCycler.properties:
            if prop not in self._pvs.keys():
                pvname = VACA_PREFIX + self._maname + ':' + prop
                self._pvs[prop] = _PV(
                    pvname, connection_timeout=TIMEOUT_CONNECTION)
                self._pvs[prop].get()

    @property
    def maname(self):
        """Magnet name."""
        return self._maname

    @property
    def connected(self):
        """Return connected state."""
        for prop in LinacMagnetCycler.properties:
            if not self[prop].connected:
                return False
        return True

    @property
    def waveform(self):
        if self._waveform is None:
            self._get_duration_and_waveform()
        return self._waveform

    def cycle_duration(self, mode):
        """Return the duration of the cycling in seconds."""
        if self._cycle_duration is None:
            self._get_duration_and_waveform()
        return self._cycle_duration

    def check_intlks(self):
        if not self.connected:
            return False
        return self['interlock'].value < 55

    def check_on(self):
        """Return wether magnet PS is on."""
        return _pv_timed_get(self['setpwm'], 1)

    def set_current_zero(self):
        """Set PS current to zero ."""
        return _pv_conn_put(self['seti'], 0)

    def check_current_zero(self):
        """Return wether magnet PS current is zero."""
        if not self.connected:
            return False
        return _isclose(self['rdi'].value, 0, abs_tol=0.1)

    def prepare(self, mode):
        """Config magnet to cycling mode."""
        status = self.set_current_zero()
        return status

    def is_prepared(self, mode):
        """Return wether magnet is ready."""
        status = self.check_current_zero()
        return status

    def cycle(self):
        """Cycle. This function may run in a thread."""
        for i in range(len(self._waveform)-1):
            self['seti'].value = self._waveform[i]
            _time.sleep(self._times[i+1] - self._times[i])
        self['seti'].value = self._waveform[-1]

    def check_final_state(self, mode):
        status = True
        status &= self.check_on()
        status &= self.check_intlks()
        if not status:
            return 4  # indicate interlock problems
        return 0

    def _get_duration_and_waveform(self):
        """Get duration and waveform."""
        t, w = _li_get_default_waveform(psname=self.maname)
        self._times = t
        self._cycle_duration = max(t)
        self._waveform = w

    def __getitem__(self, prop):
        """Return item."""
        return self._pvs[prop]
