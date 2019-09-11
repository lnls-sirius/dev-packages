"""Connectors for cycle."""

import time as _time
from epics import PV as _PV
from math import isclose as _isclose
import numpy as _np

from siriuspy.namesys import SiriusPVName as _PVName, \
    get_pair_sprb as _get_pair_sprb
from siriuspy.envars import vaca_prefix as VACA_PREFIX
from siriuspy.search import MASearch as _MASearch, PSSearch as _PSSearch
from siriuspy.csdevice.pwrsupply import Const as _PSConst, ETypes as _PSet
from siriuspy.csdevice.timesys import Const as _TIConst, \
    get_hl_trigger_database as _get_trig_db

from .util import pv_timed_get as _pv_timed_get, pv_conn_put as _pv_conn_put
from .bo_cycle_data import DEFAULT_RAMP_NRCYCLES, DEFAULT_RAMP_DURATION,\
    DEFAULT_RAMP_NRPULSES, DEFAULT_RAMP_TOTDURATION, \
    bo_get_default_waveform as _bo_get_default_waveform
from .li_cycle_data import li_get_default_waveform as _li_get_default_waveform

TIMEOUT_CONNECTION = 0.05
SLEEP_CAPUT = 0.1
TIMEOUT_CHECK = 20


class Timing:
    """Timing."""

    EVTNAME_CYCLE = 'Cycle'

    DEFAULT_CYCLE_DURATION = 150  # [us]
    DEFAULT_CYCLE_NRPULSES = 1
    DEFAULT_DELAY = 0  # [us]
    DEFAULT_POLARITY = _TIConst.TrigPol.Normal  # test
    DEFAULT_STATE = _TIConst.DsblEnbl.Enbl

    _trigger_list = [
        'TB-Glob:TI-Mags', 'BO-Glob:TI-Mags', 'BO-Glob:TI-Corrs']
    # TODO: uncomment when using TS and SI
    #    'TS-Glob:TI-Mags', 'SI-Glob:TI-Dips', 'SI-Glob:TI-Quads',
    #    'SI-Glob:TI-Sexts', 'SI-Glob:TI-Skews', 'SI-Glob:TI-Corrs']

    properties = {
        'Cycle': {
            # EVG settings
            'AS-RaMO:TI-EVG:DevEnbl-Sel': DEFAULT_STATE,
            'AS-RaMO:TI-EVG:UpdateEvt-Cmd': 1,

            # Cycle event settings
            'AS-RaMO:TI-EVG:CycleMode-Sel': _TIConst.EvtModes.External,
            'AS-RaMO:TI-EVG:CycleDelayType-Sel': _TIConst.EvtDlyTyp.Fixed,
            'AS-RaMO:TI-EVG:CycleExtTrig-Cmd': None,
        },
        'Ramp': {
            # EVG settings
            'AS-RaMO:TI-EVG:DevEnbl-Sel': DEFAULT_STATE,
            'AS-RaMO:TI-EVG:InjectionEvt-Sel': _TIConst.DsblEnbl.Dsbl,
            'AS-RaMO:TI-EVG:BucketList-SP': [1, ],
            'AS-RaMO:TI-EVG:RepeatBucketList-SP': DEFAULT_RAMP_NRCYCLES,
            'AS-RaMO:TI-EVG:InjCount-Mon': None,

            # Cycle event settings
            'AS-RaMO:TI-EVG:CycleMode-Sel': _TIConst.EvtModes.Injection,
            'AS-RaMO:TI-EVG:CycleDelayType-Sel': _TIConst.EvtDlyTyp.Incr,
            'AS-RaMO:TI-EVG:CycleDelay-SP': DEFAULT_DELAY,
        }
    }

    cycle_idx = dict()
    for trig in _trigger_list:
        properties['Cycle'][trig+':Src-Sel'] = EVTNAME_CYCLE
        properties['Cycle'][trig+':Duration-SP'] = DEFAULT_CYCLE_DURATION
        properties['Cycle'][trig+':NrPulses-SP'] = DEFAULT_CYCLE_NRPULSES
        properties['Cycle'][trig+':Delay-SP'] = DEFAULT_DELAY
        properties['Cycle'][trig+':Polarity-Sel'] = DEFAULT_POLARITY
        properties['Cycle'][trig+':State-Sel'] = DEFAULT_STATE

        properties['Ramp'][trig+':Src-Sel'] = EVTNAME_CYCLE
        properties['Ramp'][trig+':Duration-SP'] = DEFAULT_RAMP_DURATION
        properties['Ramp'][trig+':NrPulses-SP'] = DEFAULT_RAMP_NRPULSES
        properties['Ramp'][trig+':Delay-SP'] = DEFAULT_DELAY
        properties['Ramp'][trig+':Polarity-Sel'] = DEFAULT_POLARITY
        properties['Ramp'][trig+':State-Sel'] = DEFAULT_STATE

        _trig_db = _get_trig_db(trig)
        cycle_idx[trig] = _trig_db['Src-Sel']['enums'].index('Cycle')

    _pvs = dict()

    def __init__(self):
        """Init."""
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

    def get_pvnames_by_section(self, sections=list()):
        pvnames = set()
        for mode in Timing.properties.keys():
            for prop in Timing.properties[mode].keys():
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

    def prepare(self, mode, sections=list()):
        """Initialize properties."""
        pvs_2_init = self.get_pvname_2_defval_dict(mode, sections)
        for prop, defval in pvs_2_init.items():
            pv = Timing._pvs[prop]
            pv.get()  # force connection
            if pv.connected:
                pv.value = defval
                _time.sleep(1.5*SLEEP_CAPUT)

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
                    tol = 0.008 * 1.5
                    if mode == 'Ramp':
                        tol *= DEFAULT_RAMP_NRPULSES
                    if not _isclose(pv.value, defval, abs_tol=tol):
                        return False
                elif isinstance(defval, (_np.ndarray, list, tuple)):
                    if _np.any(pv.value[0:len(defval)] != defval):
                        return False
                elif pv.value != defval:
                    return False
        return True

    def trigger(self, mode):
        """Trigger timming to cycle magnets."""
        if mode == 'Cycle':
            pv = Timing._pvs['AS-RaMO:TI-EVG:CycleExtTrig-Cmd']
            pv.value = 1
        else:
            pv = Timing._pvs['AS-RaMO:TI-EVG:InjectionEvt-Sel']
            pv.value = _TIConst.DsblEnbl.Enbl

            pv = Timing._pvs['AS-RaMO:TI-EVG:InjectionEvt-Sts']
            t0 = _time.time()
            while _time.time() - t0 < TIMEOUT_CHECK:
                if pv.value == _TIConst.DsblEnbl.Enbl:
                    break
                _time.sleep(SLEEP_CAPUT)

    def get_cycle_count(self):
        pv = Timing._pvs['AS-RaMO:TI-EVG:InjCount-Mon']
        return pv.value

    def check_ramp_end(self):
        pv = Timing._pvs['AS-RaMO:TI-EVG:InjCount-Mon']
        return (pv.value == DEFAULT_RAMP_NRCYCLES)

    def turnoff(self):
        """Turn timing off."""
        pv_event = Timing._pvs['AS-RaMO:TI-EVG:CycleMode-Sel']
        pv_event.value = _TIConst.EvtModes.Disabled
        pv_bktlist = Timing._pvs['AS-RaMO:TI-EVG:RepeatBucketList-SP']
        pv_bktlist.value = 0
        for trig in self._trigger_list:
            pv = Timing._pvs[trig+':Src-Sel']
            pv.value = _TIConst.DsblEnbl.Dsbl
            pv = Timing._pvs[trig+':State-Sel']
            pv.value = _TIConst.DsblEnbl.Dsbl

    def restore_initial_state(self):
        """Restore initial state."""
        for pvname, init_val in self._initial_state.items():
            if ':BucketList-SP' in pvname and isinstance(init_val, int):
                init_val = [init_val, ]
            Timing._pvs[pvname].put(init_val)
            _time.sleep(1.5*SLEEP_CAPUT)

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
        'WfmData-SP', 'WfmData-RB',
        'PRUSyncPulseCount-Mon',
        'IntlkSoft-Mon', 'IntlkHard-Mon'
    ]

    def __init__(self, maname, ramp_config=None):
        """Constructor."""
        self._maname = maname
        self._psnames = _MASearch.conv_maname_2_psnames(self._maname)
        self._siggen = None
        self._ramp_config = ramp_config
        self._waveform = None
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
        """Return connected state."""
        for prop in MagnetCycler.properties:
            if not self[prop].connected:
                return False
        return True

    @property
    def waveform(self):
        if self._waveform is None:
            self._waveform = _bo_get_default_waveform(
                maname=self.maname, ramp_config=self._ramp_config)
        return self._waveform

    @property
    def siggen(self):
        if self._siggen is None:
            self._siggen = _PSSearch.conv_psname_2_siggenconf(self._psnames[0])
        return self._siggen

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
            status &= _pv_conn_put(self['WfmData-SP'], self.waveform)
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
            status &= _pv_timed_get(self['WfmData-RB'], self.waveform)
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
            pulses = DEFAULT_RAMP_NRCYCLES*DEFAULT_RAMP_NRPULSES
            status = _pv_timed_get(
                self['PRUSyncPulseCount-Mon'], pulses, wait=10.0)
            if not status:
                return 1  # indicate lack of trigger pulses
            status = self.set_opmode_slowref()
            status &= _pv_timed_get(
                self['OpMode-Sts'], _PSConst.States.SlowRef)
        else:
            status = _pv_timed_get(self['CycleEnbl-Mon'], 0, wait=10.0)
            if not status:
                return 2  # indicate cycling not finished yet

        status &= self.check_intlks()
        if not status:
            return 3  # indicate interlock problems

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
            return 3  # indicate interlock problems
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
