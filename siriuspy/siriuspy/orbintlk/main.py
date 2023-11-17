"""High Level Orbit Interlock main application."""

import os as _os
import logging as _log
import time as _time
from functools import partial as _part

import numpy as _np

from ..util import update_bit as _updt_bit, get_bit as _get_bit
from ..namesys import SiriusPVName as _PVName
from ..search import LLTimeSearch as _LLTimeSearch, \
    HLTimeSearch as _HLTimeSearch
from ..thread import RepeaterThread as _Repeat
from ..epics import CAThread as _CAThread
from ..callbacks import Callback as _Callback
from ..devices import OrbitInterlock as _OrbitIntlk, FamBPMs as _FamBPMs, \
    EVG as _EVG, ASLLRF as _ASLLRF, Trigger as _Trigger, Device as _Device, \
    SOFB as _SOFB, HLFOFB as _FOFB

from .csdev import Const as _Const, ETypes as _ETypes


class App(_Callback):
    """High Level Orbit Interlock main application."""

    SCAN_FREQUENCY = 1  # [Hz]

    def __init__(self, tests=True):
        """Class constructor."""
        super().__init__()
        self._is_dry_run = tests
        self._const = _Const()
        self._pvs_database = self._const.get_database()
        self._init = False

        # internal states
        self._llrf_intlk_state = 0b111011 if self._is_dry_run else 0b000000
        self._state = self._const.OffOn.Off
        self._bpm_status = self._pvs_database['BPMStatus-Mon']['value']
        self._timing_status = self._pvs_database['TimingStatus-Mon']['value']
        self._enable_lists = {
            'pos': _np.zeros(self._const.nr_bpms, dtype=bool),
            'ang': _np.zeros(self._const.nr_bpms, dtype=bool),
            'minsum': _np.zeros(self._const.nr_bpms, dtype=bool),
            }
        self._limits = {
            'pos_x_min': _np.zeros(self._const.nr_bpms, dtype=int),
            'pos_x_max': _np.zeros(self._const.nr_bpms, dtype=int),
            'pos_y_min': _np.zeros(self._const.nr_bpms, dtype=int),
            'pos_y_max': _np.zeros(self._const.nr_bpms, dtype=int),
            'ang_x_min': _np.zeros(self._const.nr_bpms, dtype=int),
            'ang_x_max': _np.zeros(self._const.nr_bpms, dtype=int),
            'ang_y_min': _np.zeros(self._const.nr_bpms, dtype=int),
            'ang_y_max': _np.zeros(self._const.nr_bpms, dtype=int),
            'minsum': _np.zeros(self._const.nr_bpms, dtype=int),
            }
        self._acq_chan = self._pvs_database['PsMtmAcqChannel-Sel']['value']
        self._acq_spre = self._pvs_database['PsMtmAcqSamplesPre-SP']['value']
        self._acq_spost = self._pvs_database['PsMtmAcqSamplesPost-SP']['value']
        self._thread_acq = None
        self._thread_cbevgilk = None
        self._thread_cbevgrx = None
        self._thread_cbfout = {fout: None for fout in self._const.FOUTS_2_MON}
        self._thread_cbbpm = None
        self._ti_mon_devs = set()
        self._lock_threads = dict()
        self._lock_failures = set()
        self._lock_suspend = False

        # devices and connections
        # # EVG
        self._evg_dev = _EVG(props2init=[
            'IntlkCtrlEnbl-Sel', 'IntlkCtrlEnbl-Sts',
            'IntlkCtrlRst-Sel', 'IntlkCtrlRst-Sts',
            'IntlkCtrlRepeat-Sel', 'IntlkCtrlRepeat-Sts',
            'IntlkCtrlRepeatTime-SP', 'IntlkCtrlRepeatTime-RB',
            'IntlkTbl0to15-Sel', 'IntlkTbl0to15-Sts',
            'IntlkTbl16to27-Sel', 'IntlkTbl16to27-Sts',
            'IntlkEvtIn0-SP', 'IntlkEvtIn0-RB',
            'IntlkEvtOut-SP', 'IntlkEvtOut-SP',
            'IntlkEvtStatus-Mon',
            'RxEnbl-SP', 'RxEnbl-RB',
            'RxEnbl-SP.B0', 'RxEnbl-RB.B0',
            'RxEnbl-SP.B1', 'RxEnbl-RB.B1',
            'RxEnbl-SP.B2', 'RxEnbl-RB.B2',
            'RxEnbl-SP.B3', 'RxEnbl-RB.B3',
            'RxEnbl-SP.B4', 'RxEnbl-RB.B4',
            'RxEnbl-SP.B5', 'RxEnbl-RB.B5',
            'RxEnbl-SP.B6', 'RxEnbl-RB.B6',
            'RxEnbl-SP.B7', 'RxEnbl-RB.B7',
            'RxLockedLtc-Mon', 'RxLockedLtcRst-Cmd',
            ])
        # interlock callback
        pvo = self._evg_dev.pv_object('IntlkEvtStatus-Mon')
        pvo.auto_monitor = True
        pvo.add_callback(self._callback_evg_intlk)
        pvo.connection_callbacks.append(self._conn_callback_timing)
        # rxlock callback
        pvo = self._evg_dev.pv_object('RxLockedLtc-Mon')
        pvo.add_callback(self._callback_evg_rxlock)

        # # Fouts
        self._fout_devs = {
            devname: _Device(
                devname,
                props2init=[
                    'RxEnbl-SP', 'RxEnbl-RB',
                    'RxLockedLtc-Mon', 'RxLockedLtcRst-Cmd',
                ], auto_monitor_mon=True)
            for devname in self._const.FOUTS_2_MON
        }
        self._fout2rxenbl = dict()
        for devname, dev in self._fout_devs.items():
            pvo = dev.pv_object('RxLockedLtc-Mon')
            pvo.add_callback(self._callback_fout_rxlock)
            pvo.connection_callbacks.append(self._conn_callback_timing)
            self._fout2rxenbl[devname] = 0

        self._fout_dcct_dev = _Device(
            'CA-RaTim:TI-Fout-2',
            props2init=['RxEnbl-SP', 'RxEnbl-RB'])

        # # AFC timing
        self._afcti_devs = {
            idx+1: _Device(
                f'IA-{idx+1:02}RaBPM:TI-AMCFPGAEVR',
                props2init=[
                    'RTMClkLockedLtc-Mon', 'ClkLockedLtcRst-Cmd',
                    'RTMClkRst-Cmd',
                ], auto_monitor_mon=True)
            for idx in range(20)
        }
        for dev in self._afcti_devs.values():
            pvo = dev.pv_object('RTMClkLockedLtc-Mon')
            pvo.connection_callbacks.append(self._conn_callback_timing)

        # # RF EVE
        trgsrc = _HLTimeSearch.get_ll_trigger_names('SI-Glob:TI-LLRF-PsMtm')
        pvname = _LLTimeSearch.get_channel_output_port_pvname(trgsrc[0])
        self._llrf_evtcnt_pvname = f'{pvname}EvtCnt-Mon'
        self._everf_dev = _Device(
            pvname.device_name,
            props2init=[self._llrf_evtcnt_pvname, ],
            auto_monitor_mon=True)
        pvo = self._everf_dev.pv_object(self._llrf_evtcnt_pvname)
        pvo.wait_for_connection()
        pvo.connection_callbacks.append(self._conn_callback_timing)
        self._everf_evtcnt = pvo.get() or 0

        # # HL triggers
        self._llrf_trig = _Trigger(
            trigname='SI-Glob:TI-LLRF-PsMtm', props2init=[
                'Src-Sel', 'Src-Sts',
                'DelayRaw-SP', 'DelayRaw-RB',
                'State-Sel', 'State-Sts',
                'WidthRaw-SP', 'WidthRaw-RB',
                'Status-Mon',
            ], auto_monitor_mon=True)

        self._bpmpsmtn_trig = _Trigger(
            trigname='SI-Fam:TI-BPM-PsMtm', props2init=[
                'Src-Sel', 'Src-Sts',
                'DelayRaw-SP', 'DelayRaw-RB',
                'State-Sel', 'State-Sts',
                'WidthRaw-SP', 'WidthRaw-RB',
                'Status-Mon',
            ], auto_monitor_mon=True)

        self._orbintlk_trig = _Trigger(
            trigname='SI-Fam:TI-BPM-OrbIntlk', props2init=[
                'Src-Sel', 'Src-Sts',
                'DelayRaw-SP', 'DelayRaw-RB',
                'State-Sel', 'State-Sts',
                'WidthRaw-SP', 'WidthRaw-RB',
                'Direction-Sel', 'Direction-Sts',
                'Status-Mon',
            ], auto_monitor_mon=True)

        self._dcct13c4_trig = _Trigger(
            trigname='SI-13C4:TI-DCCT-PsMtm', props2init=[
                'Src-Sel', 'Src-Sts',
                'State-Sel', 'State-Sts',
                'Status-Mon',
            ], auto_monitor_mon=True)
        self._dcct14c4_trig = _Trigger(
            trigname='SI-14C4:TI-DCCT-PsMtm', props2init=[
                'Src-Sel', 'Src-Sts',
                'State-Sel', 'State-Sts',
                'Status-Mon',
            ], auto_monitor_mon=True)

        # # BPM devices
        self._orbintlk_dev = _OrbitIntlk()
        for dev in self._orbintlk_dev.devices:
            pvo = dev.pv_object('IntlkLtc-Mon')
            pvo.auto_monitor = True
            pvo.add_callback(self._callback_bpm_intlk)

        self._fambpm_dev = _FamBPMs(
            devname=_FamBPMs.DEVICES.SI, ispost_mortem=True,
            props2init=[
                'ACQChannel-Sel', 'ACQChannel-Sts',
                'ACQSamplesPre-SP', 'ACQSamplesPre-RB',
                'ACQSamplesPost-SP', 'ACQSamplesPost-RB',
                'ACQTriggerRep-Sel', 'ACQTriggerRep-Sts',
                'ACQTrigger-Sel', 'ACQTrigger-Sts',
                'ACQTriggerEvent-Sel', 'ACQTriggerEvent-Sts',
                'ACQStatus-Sts',
                'INFOFAcqRate-RB', 'INFOMONITRate-RB'])
        self._monit_rate, self._facq_rate = None, None
        self._monitsum2intlksum_factor = 0
        pvo = self._fambpm_dev.devices[0].pv_object('INFOMONITRate-RB')
        pvo.add_callback(self._callback_get_bpm_rates)
        pvo = self._fambpm_dev.devices[0].pv_object('INFOFAcqRate-RB')
        pvo.add_callback(self._callback_get_bpm_rates)

        # # RF devices
        self._llrf = _ASLLRF(
            devname=_ASLLRF.DEVICES.SI,
            props2init=[
                'ILK:BEAM:TRIP:S', 'ILK:BEAM:TRIP',
                'IntlkSet-Cmd',
            ])

        # # auxiliary devices
        self._fofb = _FOFB(
            props2init=['LoopState-Sts', ])
        self._sofb = _SOFB(
            _SOFB.DEVICES.SI,
            props2init=['LoopState-Sts', 'SlowSumRaw-Mon'])
        self._sofb.pv_object('SlowSumRaw-Mon').auto_monitor = True

        # pvs to write methods
        self.map_pv2write = {
            'Enable-Sel': self.set_enable,
            'PosEnblList-SP': _part(self.set_enbllist, 'pos'),
            'AngEnblList-SP': _part(self.set_enbllist, 'ang'),
            'MinSumEnblList-SP': _part(self.set_enbllist, 'minsum'),
            'PosXMinLim-SP': _part(self.set_intlk_lims, 'pos_x_min'),
            'PosXMaxLim-SP': _part(self.set_intlk_lims, 'pos_x_max'),
            'PosYMinLim-SP': _part(self.set_intlk_lims, 'pos_y_min'),
            'PosYMaxLim-SP': _part(self.set_intlk_lims, 'pos_y_max'),
            'AngXMinLim-SP': _part(self.set_intlk_lims, 'ang_x_min'),
            'AngXMaxLim-SP': _part(self.set_intlk_lims, 'ang_x_max'),
            'AngYMinLim-SP': _part(self.set_intlk_lims, 'ang_y_min'),
            'AngYMaxLim-SP': _part(self.set_intlk_lims, 'ang_y_max'),
            'MinSumLim-SP': _part(self.set_intlk_lims, 'minsum'),
            'ResetBPMGen-Cmd': _part(self.cmd_reset, 'bpm_gen'),
            'ResetBPMPos-Cmd': _part(self.cmd_reset, 'bpm_pos'),
            'ResetBPMAng-Cmd': _part(self.cmd_reset, 'bpm_ang'),
            'ResetBPM-Cmd': _part(self.cmd_reset, 'bpm_all'),
            'Reset-Cmd': _part(self.cmd_reset, 'all'),
            'PsMtmAcqChannel-Sel': self.set_acq_channel,
            'PsMtmAcqSamplesPre-SP': self.set_acq_nrspls_pre,
            'PsMtmAcqSamplesPost-SP': self.set_acq_nrspls_post,
            'PsMtmAcqConfig-Cmd': self.cmd_acq_config,
            'IntlkStateConfig-Cmd': self.cmd_state_config,
            'ResetTimingLockLatches-Cmd': self.cmd_reset_ti_lock_latch,
            'ResetAFCTimingRTMClk-Cmd': self.cmd_reset_afcti_rtmclk,
            }

        # configuration scanning
        self.thread_check_configs = _Repeat(
            1.0/App.SCAN_FREQUENCY, self._check_configs, niter=0,
            is_cathread=True)
        self.thread_check_configs.pause()
        self.thread_check_configs.start()

    def init_database(self):
        """Set initial PV values."""
        pvn2vals = {
            'Enable-Sel': self._state,
            'Enable-Sts': self._state,
            'BPMStatus-Mon': self._bpm_status,
            'TimingStatus-Mon': self._timing_status,
            'ResetBPMGen-Cmd': 0,
            'ResetBPMPos-Cmd': 0,
            'ResetBPMAng-Cmd': 0,
            'ResetBPM-Cmd': 0,
            'Reset-Cmd': 0,
            'PsMtmAcqChannel-Sel': self._acq_chan,
            'PsMtmAcqChannel-Sts': self._acq_chan,
            'PsMtmAcqSamplesPre-SP': self._acq_spre,
            'PsMtmAcqSamplesPre-RB': self._acq_spre,
            'PsMtmAcqSamplesPost-SP': self._acq_spost,
            'PsMtmAcqSamplesPost-RB': self._acq_spost,
            'PsMtmAcqConfig-Cmd': 0,
        }
        for pvn, val in pvn2vals.items():
            self.run_callbacks(pvn, val)

        # load autosave data

        # enable lists
        for ilk in ['Pos', 'Ang', 'MinSum']:
            ilkname = ilk.lower()
            okl = self._load_file(ilkname, 'enbl')
            pvn = f'{ilk}EnblList'
            enb = self._enable_lists[ilkname]
            self.run_callbacks(pvn+'-SP', enb)
            if not okl:
                self.run_callbacks(pvn+'-RB', enb)
        self._ti_mon_devs = self._get_ti_monitored_devices()
        self.run_callbacks(
            'TimingMonitoredDevices-Mon', '\n'.join(self._ti_mon_devs))

        # limits
        for ilk in ['Pos', 'Ang']:
            for pln in ['X', 'Y']:
                for lim in ['Min', 'Max']:
                    atn = f'{ilk}_{pln}_{lim}'.lower()
                    pvn = f'{ilk}{pln}{lim}Lim'
                    okl = self._load_file(atn, 'lim')
                    val = self._limits[atn]
                    self.run_callbacks(pvn+'-SP', val)
                    if not okl:
                        self.run_callbacks(pvn+'-RB', val)

        okl = self._load_file('minsum', 'lim')
        val = self._limits['minsum']
        self.run_callbacks('MinSumLim-SP', val)
        if not okl:
            self.run_callbacks('MinSumLim-RB', val)

        self._update_log('Started.')
        self._init = True

        self._init_devices_lock()

    def _init_devices_lock(self):
        self._update_log('Waiting 5s to start locking...')
        _time.sleep(5)

        conntimeout = self._const.DEF_TIMEOUT

        # EVG
        self._evg_dev.wait_for_connection(timeout=conntimeout)
        for propty_sp, desired_val in self._const.EVG_CONFIGS:
            propty_rb = _PVName.from_sp2rb(propty_sp)
            pvo = self._evg_dev.pv_object(propty_rb)
            pvo.add_callback(_part(
                self._callback_lock, self._evg_dev, propty_sp, desired_val))
            pvo.run_callbacks()

        # BPM Fouts
        for dev in self._fout_devs.values():
            dev.wait_for_connection(timeout=conntimeout)
            pvo = dev.pv_object('RxEnbl-RB')
            pvo.add_callback(self._callback_fout_lock)
            pvo.run_callbacks()

        # DCCT Fout
        self._fout_dcct_dev.wait_for_connection(timeout=conntimeout)
        for propty_sp, desired_val in self._const.FOUT2_CONFIGS:
            propty_rb = _PVName.from_sp2rb(propty_sp)
            pvo = self._fout_dcct_dev.pv_object(propty_rb)
            pvo.add_callback(_part(
                self._callback_lock, self._fout_dcct_dev,
                propty_sp, desired_val))
            pvo.run_callbacks()

        # triggers
        trig2config = {
            self._orbintlk_trig: self._const.ORBINTLKTRIG_CONFIG,
            self._llrf_trig: self._const.LLRFTRIG_CONFIG,
            self._bpmpsmtn_trig: self._const.BPMPSMTNTRIG_CONFIG,
            self._dcct13c4_trig: self._const.DCCT13C4TRIG_CONFIG,
            self._dcct14c4_trig: self._const.DCCT14C4TRIG_CONFIG,
        }
        for trig, configs in trig2config.items():
            trig.wait_for_connection(timeout=conntimeout)
            for prop_sp, desired_val in configs:
                prop_rb = _PVName.from_sp2rb(prop_sp)
                pvo = trig.pv_object(prop_rb)
                pvo.add_callback(
                    _part(self._callback_lock, trig, prop_sp, desired_val))
                pvo.run_callbacks()

        # LLRF
        self._llrf.wait_for_connection(timeout=conntimeout)
        pvo = self._llrf.pv_object('ILK:BEAM:TRIP')
        pvo.add_callback(_part(
            self._callback_lock, self._llrf,
            'ILK:BEAM:TRIP:S', self._llrf_intlk_state))
        pvo.run_callbacks()

        # BPM devices
        prop2lock = [
            'IntlkEn-Sts',
            'IntlkMinSumEn-Sts',
            'IntlkLmtMinSum-RB',
            'IntlkPosEn-Sts',
            'IntlkLmtPosMaxX-RB',
            'IntlkLmtPosMinX-RB',
            'IntlkLmtPosMaxY-RB',
            'IntlkLmtPosMinY-RB',
            'IntlkAngEn-Sts',
            'IntlkLmtAngMaxX-RB',
            'IntlkLmtAngMinX-RB',
            'IntlkLmtAngMaxY-RB',
            'IntlkLmtAngMinY-RB',
        ]
        self._orbintlk_dev.wait_for_connection(timeout=conntimeout)
        for dev in self._orbintlk_dev.devices:
            for prop in prop2lock:
                pvo = dev.pv_object(prop)
                pvo.add_callback(self._callback_bpm_lock)
                pvo.run_callbacks()

        self._update_log('...lock running.')

    @property
    def pvs_database(self):
        """Return pvs_database."""
        return self._pvs_database

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        _ = reason
        return None

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        _log.info('Write received for: %s --> %s', reason, str(value))
        if reason not in self.map_pv2write:
            _log.warning('PV %s does not have a set function.', reason)
            return False

        status = self.map_pv2write[reason](value)
        _log.info(
            '%s Write for: %s --> %s', str(status).upper(), reason, str(value))
        return status

    @property
    def evg_dev(self):
        """EVG device."""
        return self._evg_dev

    @property
    def orbintlk_dev(self):
        """Orbit interlock device."""
        return self._orbintlk_dev

    @property
    def fambpm_dev(self):
        """Return FamBPMs device."""
        return self._fambpm_dev

    # --- interlock control ---

    def set_enable(self, value):
        """Set orbit interlock state.
        Configure global BPM interlock enable and EVG interlock enable."""
        if not 0 <= value < len(_ETypes.DSBL_ENBL):
            return False

        if value:
            mondevs = self._get_ti_monitored_devices()
            if not self._check_devices_status(mondevs):
                self._update_log('ERR:Could not enable orbit interlock.')
                return False
            self._ti_mon_devs = mondevs
            self.run_callbacks(
                'TimingMonitoredDevices-Mon', '\n'.join(mondevs))

            glob_en = self._get_gen_bpm_intlk()
        else:
            glob_en = _np.zeros(self._const.nr_bpms, dtype=bool)

        bkup = int(self._state)
        self._state = value
        if not self._orbintlk_dev.set_gen_enable(list(glob_en)):
            self._update_log('ERR:Could not set BPM general')
            self._update_log('ERR:interlock enable.')
            self._state = bkup
            return False
        self._update_log('Configured BPM general interlock enable.')

        self._evg_dev['IntlkCtrlEnbl-Sel'] = value
        if not self._evg_dev._wait(
                'IntlkCtrlEnbl-Sts', value, timeout=self._const.DEF_TIMEOUT):
            self._update_log('ERR:Could not set EVG interlock enable.')
            self._state = bkup
            return False
        self._update_log('Configured EVG interlock enable.')

        self.run_callbacks('Enable-Sts', self._state)

        return True

    # --- enable lists ---

    def set_enbllist(self, intlk, value):
        """Set enable list for interlock type."""
        intlkname = intlk.capitalize().replace('sum', 'Sum')
        self._update_log(f'Setting {intlkname} EnblList...')

        # check size
        new = _np.array(value, dtype=bool)
        if self._const.nr_bpms != new.size:
            self._update_log(f'ERR:Wrong {intlkname} EnblList size.')
            return False

        # check coerence, down/up pair should have same enable state
        if not self._check_valid_bpmconfig(new):
            self._update_log('ERR:BPM should be enabled in pairs')
            self._update_log('ERR:(M1/M2,C1-1/C1-2,C2/C3-1,C3-2/C4)')
            return False

        # check if new enable list do not imply in orbit interlock failure
        bkup_enbllist = self._enable_lists[intlk]
        bkup_timondev = self._ti_mon_devs
        self._enable_lists[intlk] = new
        self._ti_mon_devs = self._get_ti_monitored_devices()
        self._config_fout_rxenbl()
        if not self._check_devices_status(self._ti_mon_devs):
            self._update_log('ERR:Could not set enable list.')
            self._enable_lists[intlk] = bkup_enbllist
            self._ti_mon_devs = bkup_timondev
            self._config_fout_rxenbl()
            return False
        self.run_callbacks(
            'TimingMonitoredDevices-Mon', '\n'.join(self._ti_mon_devs))

        # do not set enable lists and save to file in initialization
        if not self._init:
            # update readback pv
            self.run_callbacks(f'{intlkname}EnblList-RB', new)
            return True

        # handle device enable configuration

        # set BPM interlock specific enable state
        fun = getattr(self._orbintlk_dev, f'set_{intlk}_enable')
        ret = fun(list(value), return_prob=True)
        if not ret[0]:
            self._update_log(f'ERR:Could not set BPM {intlkname}')
            self._update_log('ERR:interlock enable.')
            for item in ret[1]:
                self._update_log(f'ERR:Verify:{item}')
            return False

        # if interlock is already enabled, update BPM general enable state
        if self._state and intlk in ['pos', 'ang']:
            glob_en = self._get_gen_bpm_intlk()
            ret = self._orbintlk_dev.set_gen_enable(
                list(glob_en), return_prob=True)
            if not ret[0]:
                self._update_log('ERR:Could not set BPM general')
                self._update_log('ERR:interlock enable.')
                for item in ret[1]:
                    self._update_log(f'ERR:Verify:{item}')
                return False

        # save to autosave files
        self._save_file(intlk, _np.array([value], dtype=bool), 'enbl')

        self._update_log('...done.')

        # update readback pv
        self.run_callbacks(f'{intlkname}EnblList-RB', new)
        return True

    # --- limits ---

    def set_intlk_lims(self, intlk_lim, value):
        """Set limits for interlock type."""
        parts = intlk_lim.split('_')
        if len(parts) > 1:
            ilk, pln, lim = parts
            limname = f'{ilk.capitalize()}{pln.capitalize()}{lim.capitalize()}'
        else:
            limname = intlk_lim.capitalize().replace('sum', 'Sum')
        self._update_log(f'Setting {limname} limits...')

        # check size
        new = _np.array(value, dtype=int)
        if self._const.nr_bpms != new.size:
            self._update_log(f'ERR: Wrong {limname} limits size.')
            return False

        # check coerence, down/up pair should have same limits
        if not self._check_valid_bpmconfig(new):
            self._update_log('ERR:BPM pairs should have equal limits')
            self._update_log('ERR:(M1/M2,C1-1/C1-2,C2/C3-1,C3-2/C4)')
            return False

        self._limits[intlk_lim] = new

        # do not set limits and save to file in initialization
        if not self._init:
            # update readback pv
            self.run_callbacks(f'{limname}Lim-RB', new)
            return True

        # handle device limits configuration

        # set BPM interlock limits
        fun = getattr(self._orbintlk_dev, f'set_{intlk_lim}_thres')
        ret = fun(list(value), return_prob=True)
        if not ret[0]:
            self._update_log(f'ERR:Could not set BPM {limname}')
            self._update_log('ERR:interlock limits.')
            for item in ret[1]:
                self._update_log(f'ERR:Verify:{item}')
            return False

        # save to autosave files
        self._save_file(intlk_lim, _np.array([value]), 'lim')

        self._update_log('...done.')

        # update readback pv
        self.run_callbacks(f'{limname}Lim-RB', new)
        return True

    # --- reset ---

    def cmd_reset(self, state, value=None):
        """Reset interlock states."""
        _ = value
        # if it is a BPM position, BPM general or a global reset
        if 'pos' in state or 'all' in state:
            self._orbintlk_dev.cmd_reset_pos()
            self._update_log('Sent reset BPM position flags.')
        # if it is a BPM angle, BPM general or a global reset
        if 'ang' in state or 'all' in state:
            self._orbintlk_dev.cmd_reset_ang()
            self._update_log('Sent reset BPM angle flags.')
        # if it is a BPM general or a global reset
        if 'gen' in state or 'all' in state:
            self._orbintlk_dev.cmd_reset_gen()
            self._update_log('Sent reset BPM general flags.')

        # if it is a global reset, reset EVG
        if state == 'all':
            self._evg_dev['IntlkCtrlRst-Sel'] = 1
            self._update_log('Sent reset EVG interlock flag.')

        return True

    def cmd_reset_ti_lock_latch(self, value=None):
        """Command to reset AFC timing and Fout clock lock latches."""
        _ = value
        # try to reset AFC timing clock lock latches, act only in necessary
        # devices, return false if fail
        for idx, afcti in self._afcti_devs.items():
            if afcti['RTMClkLockedLtc-Mon']:
                continue
            afcti['ClkLockedLtcRst-Cmd'] = 1
            msg = 'Reset' if afcti._wait('RTMClkLockedLtc-Mon', 1, timeout=3) \
                else 'ERR:Could not reset'
            self._update_log(f'{msg} AFC Timing {idx} lock latchs.')
            if 'not' in msg:
                return False
        # try to reset Fout rx lock latches, act only in necessary
        # devices, return false if fail
        for devname, fout in self._fout_devs.items():
            if fout['RxLockedLtc-Mon']:
                continue
            fout['RxLockedLtcRst-Cmd'] = 1
            rxv = self._fout2rxenbl[devname]
            msg = 'Reset' if fout._wait('RxLockedLtc-Mon', rxv, timeout=3) \
                else 'ERR:Could not reset'
            self._update_log(f'{msg} {devname} lock latchs.')
            if 'not' in msg:
                return False
        return True

    def cmd_reset_afcti_rtmclk(self, value=None):
        """Command to reset AFC timing clocks."""
        _ = value
        #  do not allow user to reset in case of correction loops closed
        if not self._fofb.connected or self._fofb['LoopState-Sts'] or \
                not self._sofb.connected or self._sofb['LoopState-Sts']:
            self._update_log('ERR:Open correction loops before ')
            self._update_log('ERR:reseting AFC Timing clocks.')
            return False

        # try to reset AFC timing clock, act only in necessary
        # devices, return false if fail
        for idx, afcti in self._afcti_devs.items():
            if afcti['RTMClkLockedLtc-Mon']:
                continue
            afcti['ClkLockedLtcRst-Cmd'] = 1
            if afcti._wait('RTMClkLockedLtc-Mon', 1, timeout=3):
                continue
            afcti['RTMClkRst-Cmd'] = 1
            self._update_log(f'Sent reset clock to AFC Timing {idx}.')

        # try to reset latches
        self.cmd_reset_ti_lock_latch()

        return True

    # --- configure acquisition ---

    def set_acq_channel(self, value):
        """Set BPM PsMtm acquisition channel."""
        self._acq_chan = value
        self.run_callbacks('PsMtmAcqChannel-Sts', value)
        return True

    def set_acq_nrspls_pre(self, value):
        """Set BPM PsMtm acquisition number of samples pre."""
        self._acq_spre = value
        self.run_callbacks('PsMtmAcqSamplesPre-RB', value)
        return True

    def set_acq_nrspls_post(self, value):
        """Set BPM PsMtm acquisition number of samples post."""
        self._acq_spost = value
        self.run_callbacks('PsMtmAcqSamplesPost-RB', value)
        return True

    def cmd_acq_config(self, value=None):
        """Configure BPM PsMtm acquisition."""
        if self._thread_acq and self._thread_acq.is_alive():
            self._update_log('WARN:BPM configuration already in progress.')
            return False
        self._thread_acq = _CAThread(target=self._acq_config, daemon=True)
        self._thread_acq.start()
        return True

    def _acq_config(self):
        self._update_log('Aborting BPM acquisition...')
        ret = self._fambpm_dev.cmd_mturn_acq_abort()
        if ret > 0:
            self._update_log('ERR:Failed to abort BPM acquisition.')
            return
        self._update_log('...done. Configuring BPM acquisition...')
        ret = self._fambpm_dev.mturn_config_acquisition(
            nr_points_before=self._acq_spre,
            nr_points_after=self._acq_spost,
            acq_rate=self._acq_chan,
            repeat=False,
            external=True)
        if ret < 0:
            self._update_log(
                'ERR:Failed to abort acquisition for ' +
                f'{self._const.bpm_names[-ret-1]:s}.')
            return
        if ret > 0:
            self._update_log(
                'ERR:Failed to start acquisition for ' +
                f'{self._const.bpm_names[ret-1]:s}.')
            return
        self._update_log('...done!')

    # --- status methods ---

    def cmd_state_config(self, value=None):
        """Configure Interlock State according to setpoints.

        Args:
            value (int, optional): Not used. Defaults to None.

        Returns:
            bool: True if configuration worked.
        """
        for name, enbl in self._enable_lists.items():
            if not self.set_enbllist(name, enbl):
                self._update_log(
                    f'ERR:Could not configure {name:s} enable list')
                return False

        for name, lim in self._limits.items():
            if not self.set_intlk_lims(name, lim):
                self._update_log(
                    f'ERR:Could not configure {name:s} limit')
                return False

        if not self.set_enable(self._state):
            return False
        return True

    def _config_fout_rxenbl(self):
        fout2rx = dict()
        for chn in self._ti_mon_devs:
            if 'Fout' not in chn:
                continue
            fout = chn.device_name
            out = int(chn.propty_name[-1])
            rx = fout2rx.get(fout, 0)
            rx += 1 << out
            fout2rx[fout] = rx

        for fout, dev in self._fout_devs.items():
            rxenbl = fout2rx.get(fout, 0)
            self._fout2rxenbl[fout] = rxenbl
            dev['RxEnbl-SP'] = rxenbl
            dev._wait('RxEnbl-RB', rxenbl)
            dev['RxLockedLtcRst-Cmd'] = 1
            if rxenbl:
                dev._wait('RxLockedLtc-Mon', rxenbl)

        return True

    def _get_enabled_sections(self):
        enbllist = self._get_gen_bpm_intlk()
        aux = _np.roll(enbllist, 1)
        subs = _np.where(_np.sum(aux.reshape(20, -1), axis=1) > 0)[0]
        subs += 1
        return subs

    def _get_ti_monitored_devices(self):
        value = set()
        if self._state:
            value.add(self._everf_dev.devname)
        for sec in self._get_enabled_sections():
            afcti = f'IA-{sec:02}RaBPM:TI-AMCFPGAEVR'
            value.add(afcti)
            foutout = _LLTimeSearch.get_trigsrc2fout_mapping()[afcti]
            value.add(foutout)
            evgout = _LLTimeSearch.get_evg_channel(foutout)
            value.add(evgout)
        return sorted(value)

    def _check_devices_status(self, devices):
        for devname in devices:
            devname = _PVName(devname)
            out = int(devname.propty[-1]) if devname.propty else None

            dev = self._evg_dev if 'EVG' in devname else \
                self._fout_devs[devname.device_name] if 'Fout' in devname \
                else self._afcti_devs[int(devname.sub[:2])]

            if not dev.connected:
                self._update_log(f'ERR:{dev.devname} not connected')
                return False
            if out and not _get_bit(dev['RxLockedLtc-Mon'], out):
                self._update_log(f'ERR:{dev.devname} OUT{out} not locked')
                return False
            if 'RTMClkLockedLtc-Mon' in dev.properties_in_use and \
                    not dev['RTMClkLockedLtc-Mon']:
                self._update_log(f'ERR:{dev.devname} RTM Clk not locked')
                return False
        return True

    def _get_gen_bpm_intlk(self):
        pos, ang = self._enable_lists['pos'], self._enable_lists['ang']
        return _np.logical_or(pos, ang)

    def _check_valid_bpmconfig(self, config):
        aux = _np.roll(config, 1)
        # check if pairs have the same config
        return not _np.any(_np.diff(aux.reshape(-1, 2), axis=1) != 0)

    def _check_configs(self):
        _t0 = _time.time()

        # bpm status
        dev = self._orbintlk_dev
        value = (1 << 9) - 1
        if dev.connected:
            value = _updt_bit(value, 0, 0)
            # PosEnblSynced
            val = _np.array_equal(
                dev.pos_enable, self._enable_lists['pos'])
            value = _updt_bit(value, 1, not val)
            # AngEnblSynced
            val = _np.array_equal(
                dev.ang_enable, self._enable_lists['ang'])
            value = _updt_bit(value, 2, not val)
            # MinSumEnblSynced
            val = _np.array_equal(
                dev.minsum_enable, self._enable_lists['minsum'])
            value = _updt_bit(value, 3, not val)
            # GlobEnblSynced
            genval = self._get_gen_bpm_intlk() if self._state else \
                _np.zeros(self._const.nr_bpms, dtype=bool)
            val = _np.array_equal(dev.gen_enable, genval)
            value = _updt_bit(value, 4, not val)
            # PosLimsSynced
            okp = True
            for prp in ['pos_x_min', 'pos_x_max', 'pos_y_min', 'pos_y_max']:
                okp &= _np.array_equal(
                    getattr(dev, prp+'_thres'), self._limits[prp])
            value = _updt_bit(value, 5, not okp)
            # AngLimsSynced
            oka = True
            for prp in ['ang_x_min', 'ang_x_max', 'ang_y_min', 'ang_y_max']:
                oka &= _np.array_equal(
                    getattr(dev, prp+'_thres'), self._limits[prp])
            value = _updt_bit(value, 6, not oka)
            # MinSumLimsSynced
            oks = _np.array_equal(dev.minsum_thres, self._limits['minsum'])
            value = _updt_bit(value, 7, not oks)
            # AcqConfigured
            bpms = self._fambpm_dev.devices
            okb = all(d.acq_channel == self._acq_chan for d in bpms)
            okb &= all([d.acq_nrsamples_post == self._acq_spost for d in bpms])
            okb &= all([d.acq_nrsamples_pre == self._acq_spre for d in bpms])
            okb &= all(
                d.acq_repeat == self._const.AcqRepeat.Normal for d in bpms)
            okb &= all(
                d.acq_trigger == self._const.AcqTrigTyp.External for d in bpms)
            value = _updt_bit(value, 8, not okb)

        self._bpm_status = value
        self.run_callbacks('BPMStatus-Mon', self._bpm_status)

        # Timing Status
        value = 0
        # EVG
        dev = self._evg_dev
        if dev.connected:
            val = dev['IntlkCtrlEnbl-Sts'] != self._state
            value = _updt_bit(value, 1, val)
            okg = True
            for prp, val in self._const.EVG_CONFIGS:
                prp_rb = prp.replace('-Sel', '-Sts').replace('-SP', '-RB')
                okg &= dev[prp_rb] == val
            value = _updt_bit(value, 2, not okg)
        else:
            value = 0b111
        # Fouts
        devs = self._fout_devs
        if all(devs[devn].connected for devn in self._const.FOUTS_2_MON):
            okg = True
            for devname, rxenbl in self._fout2rxenbl.items():
                dev = self._fout_devs[devname]
                okg &= dev['RxEnbl-RB'] == rxenbl
                okg &= dev['RxLockedLtc-Mon'] == rxenbl
            value = _updt_bit(value, 4, not okg)
        else:
            value += 0b11 << 3
        # Orbit Interlock trigger
        dev = self._orbintlk_trig
        if dev.connected:
            value = _updt_bit(value, 6, bool(dev['Status-Mon']))
            oko = True
            for prp, val in self._const.ORBINTLKTRIG_CONFIG:
                prp_rb = prp.replace('-Sel', '-Sts').replace('-SP', '-RB')
                oko &= dev[prp_rb] == val
            value = _updt_bit(value, 7, not oko)
        else:
            value += 0b111 << 5
        # LLRF PsMtm trigger
        dev = self._llrf_trig
        oko = False
        if dev.connected:
            value = _updt_bit(value, 9, bool(dev['Status-Mon']))
            oko = True
            for prp, val in self._const.LLRFTRIG_CONFIG:
                prp_rb = prp.replace('-Sel', '-Sts').replace('-SP', '-RB')
                oko &= dev[prp_rb] == val
            value = _updt_bit(value, 10, not oko)
        else:
            value += 0b111 << 8
        # BPM PsMtm trigger
        dev = self._bpmpsmtn_trig
        oko = False
        if dev.connected:
            value = _updt_bit(value, 12, bool(dev['Status-Mon']))
            oko = True
            for prp, val in self._const.BPMPSMTNTRIG_CONFIG:
                prp_rb = prp.replace('-Sel', '-Sts').replace('-SP', '-RB')
                oko &= dev[prp_rb] == val
            value = _updt_bit(value, 13, not oko)
        else:
            value += 0b111 << 11
        # DCCT 13C4 trigger
        dev = self._dcct13c4_trig
        oko = False
        if dev.connected:
            value = _updt_bit(value, 15, bool(dev['Status-Mon']))
            oko = True
            for prp, val in self._const.DCCT13C4TRIG_CONFIG:
                prp_rb = prp.replace('-Sel', '-Sts').replace('-SP', '-RB')
                oko &= dev[prp_rb] == val
            value = _updt_bit(value, 16, not oko)
        else:
            value += 0b111 << 14
        # DCCT 14C4 trigger
        dev = self._dcct14c4_trig
        oko = False
        if dev.connected:
            value = _updt_bit(value, 18, bool(dev['Status-Mon']))
            oko = True
            for prp, val in self._const.DCCT14C4TRIG_CONFIG:
                prp_rb = prp.replace('-Sel', '-Sts').replace('-SP', '-RB')
                oko &= dev[prp_rb] == val
            value = _updt_bit(value, 19, not oko)
        else:
            value += 0b111 << 17

        self._timing_status = value
        self.run_callbacks('TimingStatus-Mon', self._timing_status)

        # LLRF Status
        value = (1 << 2) - 1
        dev = self._llrf
        if dev.connected:
            value = _updt_bit(value, 0, 0)
            value = _updt_bit(
                value, 1, dev['ILK:BEAM:TRIP'] != self._llrf_intlk_state)
        self.run_callbacks('LLRFStatus-Mon', value)

        # check time elapsed
        ttook = _time.time() - _t0
        tplanned = self.thread_check_configs.interval
        tsleep = tplanned - ttook
        if tsleep <= 0:
            _log.warning(
                'Configuration check took more than planned... '
                '{0:.3f}/{1:.3f} s'.format(ttook, tplanned))

    # --- interlock methods ---

    def _callback_evg_intlk(self, value, **kws):
        _ = kws
        if not self._init:
            return
        if self._thread_cbevgilk and self._thread_cbevgilk.is_alive():
            return
        self._thread_cbevgilk = _CAThread(
            target=self._do_callback_evg_intlk, args=(value, ), daemon=True)
        self._thread_cbevgilk.start()

    def _do_callback_evg_intlk(self, value):
        if value == 0:
            return

        self._update_log('FATAL:Orbit interlock raised by EVG.')

        self._update_log('Waiting a little before rearming...')
        _time.sleep(self._const.DEF_TIME2WAIT_INTLKREARM)

        # reset latch flags for BPM interlock core and EVG
        self.cmd_reset('all')

        # reconfigure BPM configuration
        self.cmd_acq_config()

    def _callback_fout_rxlock(self, pvname, value, **kws):
        if not self._init:
            return
        nam = _PVName(pvname).device_name
        if self._thread_cbfout[nam] and self._thread_cbfout[nam].is_alive():
            return
        self._thread_cbfout[nam] = _CAThread(
            target=self._do_callback_rxlock,
            args=(pvname, value, ), daemon=True)
        self._thread_cbfout[nam].start()

    def _callback_evg_rxlock(self, pvname, value, **kws):
        if not self._init:
            return
        pvname = _PVName(pvname)
        configs = self._const.EVG_CONFIGS
        bits = [int(c[0][-1]) for c in configs if 'RxEnbl' in c[0]]
        if all([_get_bit(value, b) for b in bits]):  # all ok
            return
        if self._thread_cbevgrx and self._thread_cbevgrx.is_alive():
            return
        self._thread_cbevgrx = _CAThread(
            target=self._do_callback_rxlock,
            args=(pvname, value, ), daemon=True)
        self._thread_cbevgrx.start()

    def _do_callback_rxlock(self, pvname, value):
        pvname = _PVName(pvname)
        devname = pvname.device_name
        if pvname.dev == 'EVG':
            is_failure = False
            for bit in range(8):
                if _get_bit(value, bit):
                    continue
                outnam = f'OUT{bit}'
                self._update_log(f'FATAL:{outnam} of {devname} lost lock')
                devout = devname.substitute(propty_name=outnam)
                # verify if this is an orbit interlock reliability failure
                is_failure |= devout in self._ti_mon_devs
        else:
            out = None
            for dev in self._ti_mon_devs:
                if 'Fout' not in dev:
                    continue
                dev = _PVName(dev)
                if dev.device_name == devname:
                    out = int(dev.propty_name[-1])
                    break
            is_failure = out is not None and not _get_bit(value, out)
        if is_failure:
            self._update_log('FATAL:Orbit interlock reliability failure')
            self._handle_reliability_failure()

    def _conn_callback_timing(self, pvname, conn, **kws):
        if conn:
            return
        pvname = _PVName(pvname)
        self._update_log(f'FATAL:{pvname.device_name} disconnected')
        # verify if this is an orbit interlock reliability failure
        is_failure = False
        for dev in self._ti_mon_devs:
            is_failure |= _PVName(dev).device_name == pvname.device_name
        if is_failure:
            self._update_log('FATAL:Orbit interlock reliability failure')
            self._handle_reliability_failure()

    def _callback_bpm_intlk(self, pvname, value, **kws):
        _ = kws
        if not value:
            return
        if not self._init:
            return
        if self._thread_cbbpm and self._thread_cbbpm.is_alive():
            return
        bpmname = _PVName(pvname).device_name
        self._thread_cbbpm = _CAThread(
            target=self._do_callback_bpm_intlk, args=(bpmname, ), daemon=True)
        self._thread_cbbpm.start()

    def _do_callback_bpm_intlk(self, bpmname):
        self._update_log(f'FATAL:{bpmname} raised orbit interlock.')
        # send kill beam as fast as possible
        self._handle_reliability_failure()
        # wait minimum period for RF EVE event count to be updated
        _time.sleep(.1)
        # verify if RF EVE propagated the event PsMtm
        new_evtcnt = self._everf_dev[self._llrf_evtcnt_pvname]
        if new_evtcnt == self._everf_evtcnt:
            self._update_log('WARN:RF EVE did not propagate event PsMtm')
        self._everf_evtcnt = new_evtcnt
        # wait minimum period for BPM to update interlock PVs
        _time.sleep(2)
        # verify if EVG propagated the event Intlk
        evgintlksts = self._evg_dev['IntlkEvtStatus-Mon']
        if not evgintlksts & 0b1:
            self._update_log('WARN:EVG did not propagate event Intlk')
            # reset BPM orbit interlock, once EVG callback was not triggered
            self.cmd_reset('bpm_all')

    def _callback_get_bpm_rates(self, pvname, value, **kws):
        if value is None:
            return
        if 'MONIT' in pvname:
            self._monit_rate = value
        elif 'FAcq' in pvname:
            self._facq_rate = value
        monit = self._monit_rate
        facq = self._facq_rate
        if None in [monit, facq]:
            return
        frac = monit/facq
        factor = 2**_np.ceil(_np.log2(frac)) / frac
        self._monitsum2intlksum_factor = factor

    # --- reliability failure methods ---

    def _check_minsum_requirement(self, monit_sum=None):
        if monit_sum is None:
            monit_sum = self._sofb['SlowSumRaw-Mon']
        facq_sum = monit_sum * self._monitsum2intlksum_factor
        return _np.all(facq_sum > self._limits['minsum'])

    def _callback_monitor_sum(self, value, cb_info, **kws):
        # remove callback if is not anymore in a reliability failure
        if not self._lock_failures:
            cb_info[1].remove_callback(cb_info[0])

        # check whether sum value is higher than minsum
        if not self._check_minsum_requirement(value):
            return

        # if sum is higher than minsum and there is lock failures,
        # handle orbit interlock reliability failure
        self._update_log('FATAL:Orbit interlock reliability failure')
        for pvn in self._lock_failures:
            self._update_log(f'FATAL:Fail to lock {pvn}')
        self._handle_reliability_failure()
        # and remove callback
        cb_info[1].remove_callback(cb_info[0])

    def _handle_reliability_failure(self):
        # if in dry run, do not kill RF
        if self._is_dry_run:
            self._update_log('WARN:Dry run running, will not handle')
            self._update_log('WARN:reliability failure.')
            return
        if not self._state:
            self._update_log('WARN:Orbit interlock is not enabled.')
            return
        # if minimum sum condition is not satisfied, only monitor sum
        if not self._check_minsum_requirement():
            pvo = self._sofb.pv_object('SlowSumRaw-Mon')
            pvo.add_callback(self._callback_monitor_sum)
            return
        # send soft interlock to RF
        self._update_log('FATAL:sending soft interlock to LLRF.')
        self._llrf['IntlkSet-Cmd'] = 1
        _time.sleep(1)
        self._llrf['IntlkSet-Cmd'] = 0

    # --- device lock methods ---

    def _callback_lock(
            self, device, propty_sp, desired_value, pvname, value, **kwargs):
        thread = _CAThread(
            target=self._start_lock_thread,
            args=(device, propty_sp, desired_value, pvname, value),
            daemon=True)
        thread.start()

    def _callback_fout_lock(self, pvname, value, **kwargs):
        devname = _PVName(pvname).device_name
        desired_value = self._fout2rxenbl[devname]
        device = self._fout_devs[devname]
        thread = _CAThread(
            target=self._start_lock_thread,
            args=(device, 'RxEnbl-SP', desired_value, pvname, value),
            daemon=True)
        thread.start()

    def _callback_bpm_lock(self, pvname, value, **kws):
        pvname = _PVName(pvname)
        devname = pvname.device_name
        propty_rb = pvname.propty
        propty_sp = _PVName.from_rb2sp(propty_rb)
        devidx = self._orbintlk_dev.BPM_NAMES.index(devname)
        device = self._orbintlk_dev.devices[devidx]
        if propty_rb.endswith('En-Sts'):
            entyp = 'pos' if 'Pos' in propty_rb else \
                'ang' if 'Ang' in propty_rb else \
                'minsum' if 'MinSum' in propty_rb else \
                'gen'
            if entyp == 'gen':
                desired_value = self._get_gen_bpm_intlk()[devidx] \
                    if self._state else 0
            else:
                desired_value = self._enable_lists[entyp][devidx]
        elif 'Lmt' in propty_rb:
            limcls = 'pos' if 'Pos' in propty_rb else \
                'ang' if 'Ang' in propty_rb else 'minsum'
            limpln = '_x_' if 'X' in propty_rb else \
                '_y_' if 'Y' in propty_rb else ''
            limtyp = '' if 'MinSum' in propty_rb \
                else 'max' if 'Max' in propty_rb else 'min'
            limname = f'{limcls}{limpln}{limtyp}'
            desired_value = self._limits[limname][devidx]

        thread = _CAThread(
            target=self._start_lock_thread,
            args=(device, propty_sp, desired_value, pvname, value),
            daemon=True)
        thread.start()

    def _start_lock_thread(
            self, device, propty_sp, desired_value, pvname, value):
        if self._lock_suspend:
            return

        # if there is already a lock thread, return
        thread = self._lock_threads.get(pvname, None)
        if thread is not None and thread.is_alive():
            return

        # else, create lock thread with 10 attempts to lock PV
        interval = 1 / 50  # little sleep to avoid CPU load
        thread = _Repeat(
            interval, self._do_lock,
            args=(device, propty_sp, desired_value, pvname, value),
            niter=10, is_cathread=True)
        self._lock_threads[pvname] = thread
        thread.start()

    def _do_lock(self, device, propty_sp, desired_value, pvname, value):
        thread = self._lock_threads[pvname]

        # if value is equal desired, stop thread
        if value == desired_value:
            if pvname in self._lock_failures:
                self._lock_failures.remove(pvname)
            thread.stop()

        # else, apply value as desired
        if device == self._llrf:
            propty_rb = propty_sp.replace(':S', '')
        else:
            propty_rb = _PVName(pvname).propty
        device[propty_sp] = desired_value

        # if readback reached desired value, stop thread
        if device._wait(propty_rb, desired_value, timeout=0.11):
            if pvname in self._lock_failures:
                self._lock_failures.remove(pvname)
            thread.stop()

        # if this was the last iteration, raise a reliability failure
        if thread.cur_iter == thread.niters-1:
            self._lock_failures.add(pvname)
            self._update_log(f'FATAL:Fail to lock {pvname}')
            self._update_log('FATAL:Orbit interlock reliability failure')
            self._handle_reliability_failure()

    # --- auxiliary log methods ---

    def _update_log(self, msg):
        if 'ERR' in msg:
            _log.error(msg[4:])
        elif 'FATAL' in msg:
            _log.error(msg[6:])
        elif 'WARN' in msg:
            _log.warning(msg[5:])
        else:
            _log.info(msg)
        self.run_callbacks('Log-Mon', msg)

    # --- file handlers ---

    def _load_file(self, intlk, dtype='en'):
        suff = '_enbl_fname' if dtype.startswith('en') else '_lim_fname'
        msg = 'enable list' if dtype.startswith('en') else 'limits'
        filename = getattr(self._const, intlk + suff)
        if not _os.path.isfile(filename):
            return
        value = _np.loadtxt(filename)
        if dtype.startswith('en'):
            okl = self.set_enbllist(intlk, value)
        else:
            okl = self.set_intlk_lims(intlk, value)
        if okl:
            msg = f'Loaded {intlk} {msg}!'
        else:
            msg = f'ERR:Problem loading {intlk} {msg} from file.'
        self._update_log(msg)
        return okl

    def _save_file(self, intlk, value, dtype):
        suff = '_enbl_fname' if dtype.startswith('en') else '_lim_fname'
        msg = 'enable list' if dtype.startswith('en') else 'limits'
        try:
            filename = getattr(self._const, intlk+suff)
            path = _os.path.split(filename)[0]
            _os.makedirs(path, exist_ok=True)
            _np.savetxt(filename, value)
        except FileNotFoundError:
            self._update_log(
                f'WARN:Could not save {intlk} {msg} to file.')
