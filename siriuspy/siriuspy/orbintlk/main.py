"""High Level Orbit Interlock main application."""

import os as _os
import logging as _log
import time as _time
from functools import partial as _part

import numpy as _np

from ..util import update_bit as _updt_bit
from ..namesys import SiriusPVName as _SiriusPVName
from ..thread import RepeaterThread as _Repeat
from ..epics import CAThread as _CAThread
from ..callbacks import Callback as _Callback
from ..devices import OrbitInterlock as _OrbitIntlk, FamBPMs as _FamBPMs, \
    EVG as _EVG, ASLLRF as _ASLLRF, Trigger as _Trigger, Device as _Device

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
            'pos': _np.ones(self._const.nr_bpms, dtype=bool),
            'ang': _np.ones(self._const.nr_bpms, dtype=bool),
            'minsum': _np.ones(self._const.nr_bpms, dtype=bool),
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
        self._thread_cb = None

        # devices and connections
        self._fout_devs = {
            idx: _Device(
                f'CA-RaTim:TI-Fout-{idx}',
                props2init=[
                    'RxEnbl-SP', 'RxEnbl-RB',
                ])
            for idx in self._const.FOUTS_CONFIGS
        }

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
            ])
        pvo = self._evg_dev.pv_object('IntlkEvtStatus-Mon')
        pvo.auto_monitor = True
        pvo.add_callback(self._callback_intlk)

        self._llrf_trig = _Trigger(
            trigname='SI-Glob:TI-LLRF-PsMtn', props2init=[
                'Src-Sel', 'Src-Sts',
                'DelayRaw-SP', 'DelayRaw-RB',
                'State-Sel', 'State-Sts',
                'WidthRaw-SP', 'WidthRaw-RB',
                'Status-Mon',
            ])

        self._bpmpstmn_trig = _Trigger(
            trigname='SI-Fam:TI-BPM-PsMtn', props2init=[
                'Src-Sel', 'Src-Sts',
                'DelayRaw-SP', 'DelayRaw-RB',
                'State-Sel', 'State-Sts',
                'WidthRaw-SP', 'WidthRaw-RB',
                'Status-Mon',
            ])

        self._orbintlk_trig = _Trigger(
            trigname='SI-Fam:TI-BPM-OrbIntlk', props2init=[
                'Src-Sel', 'Src-Sts',
                'DelayRaw-SP', 'DelayRaw-RB',
                'State-Sel', 'State-Sts',
                'WidthRaw-SP', 'WidthRaw-RB',
                'Direction-Sel', 'Direction-Sts',
                'Status-Mon',
            ])

        self._afcti_devs = {
            idx+1: _Device(
                f'IA-{idx+1:02}RaBPM:TI-AMCFPGAEVR',
                props2init=[
                    'RTMClkLockedLtc-Mon', 'ClkLockedLtcRst-Cmd',
                ], auto_monitor_mon=True)
            for idx in range(20)
        }
        for dev in self._afcti_devs.values():
            pvo = dev.pv_object('RTMClkLockedLtc-Mon')
            pvo.add_callback(self._callback_rtmlock)

        self._orbintlk_dev = _OrbitIntlk()

        self._llrf = _ASLLRF(devname=_ASLLRF.DEVICES.SI, props2init=[
            'ILK:BEAM:TRIP:S', 'ILK:BEAM:TRIP',
            ])

        self._fambpm_dev = _FamBPMs(
            devname=_FamBPMs.DEVICES.SI, ispost_mortem=True,
            props2init=[
                'ACQChannel-Sel', 'ACQChannel-Sts',
                'ACQSamplesPre-SP', 'ACQSamplesPre-RB',
                'ACQSamplesPost-SP', 'ACQSamplesPost-RB',
                'ACQTriggerRep-Sel', 'ACQTriggerRep-Sts',
                'ACQTrigger-Sel', 'ACQTrigger-Sts',
                'ACQTriggerEvent-Sel', 'ACQTriggerEvent-Sts',
                'ACQStatus-Sts'])

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
            'IntlkStateConfig-Cmd': self.cmd_state_config}

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
            glob_en = self._get_gen_bpm_intlk()
        else:
            glob_en = _np.zeros(self._const.nr_bpms, dtype=bool)
        if not self._orbintlk_dev.set_gen_enable(list(glob_en)):
            self._update_log('ERR:Could not set BPM general')
            self._update_log('ERR:interlock enable.')
            return False
        self._update_log('Configured BPM general interlock enable.')

        self._evg_dev['IntlkCtrlEnbl-Sel'] = value
        if not self._evg_dev._wait(
                'IntlkCtrlEnbl-Sts', value, timeout=self._const.DEF_TIMEOUT):
            self._update_log('ERR:Could not set EVG interlock enable.')
            return False
        self._update_log('Configured EVG interlock enable.')

        self._state = value
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
        if not self._check_valid_enablelist(new):
            self._update_log('ERR:BPM should be enabled in pairs')
            self._update_log('ERR:(M1/M2,C1-1/C1-2,C2/C3-1,C3-2/C4)')
            return False

        self._enable_lists[intlk] = new

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
        if not self._check_valid_limits(new):
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

        # update readback pv
        self.run_callbacks(f'{limname}Lim-RB', new)
        return True

    # --- reset ---

    def cmd_reset(self, state, value=None):
        """Reset interlock states."""
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
        if not self._config_timing():
            return False
        if not self._config_llrf():
            return False
        return True

    def _config_timing(self):
        # EVG
        dev = self._evg_dev
        for prp, val in self._const.EVG_CONFIGS:
            dev[prp] = val
            prp_rb = prp.replace('-SP', '-RB').replace('-Sel', '-Sts')
            if not dev._wait(prp_rb, val):
                self._update_log(f'ERR:Failed to configure EVG PV {prp:s}')
                return False
        # Fouts
        for idx, configs in self._const.FOUTS_CONFIGS.items():
            dev = self._fout_devs[idx]
            for prp, val in configs:
                dev[prp] = val
                prp_rb = prp.replace('-SP', '-RB').replace('-Sel', '-Sts')
                if not dev._wait(prp_rb, val):
                    self._update_log(
                        f'ERR:Failed to configure Fout {idx} PV {prp:s}')
                    return False
        # Orbit Interlock Trigger
        dev = self._orbintlk_trig
        for prp, val in self._const.ORBINTLKTRIG_CONFIG:
            dev[prp] = val
            prp_rb = prp.replace('-SP', '-RB').replace('-Sel', '-Sts')
            if not dev._wait(prp_rb, val):
                self._update_log(
                    f'ERR:Failed to configure OrbIntlk Trigger PV {prp:s}')
                return False
        # LLRF PsMtn Trigger
        dev = self._llrf_trig
        for prp, val in self._const.LLRFTRIG_CONFIG:
            dev[prp] = val
            prp_rb = prp.replace('-SP', '-RB').replace('-Sel', '-Sts')
            if not dev._wait(prp_rb, val):
                self._update_log(
                    f'ERR:Failed to configure LLRF PsMtn Trigger PV {prp:s}')
                return False
        # BPM PsMtn Trigger
        dev = self._bpmpstmn_trig
        for prp, val in self._const.BPMPSMTNTRIG_CONFIG:
            dev[prp] = val
            prp_rb = prp.replace('-SP', '-RB').replace('-Sel', '-Sts')
            if not dev._wait(prp_rb, val):
                self._update_log(
                    f'ERR:Failed to configure BPM PsMtn Trigger PV {prp:s}')
                return False
        return True

    def _config_llrf(self):
        self._llrf['ILK:BEAM:TRIP:S'] = self._llrf_intlk_state
        if not self._llrf._wait('ILK:BEAM:TRIP', self._llrf_intlk_state):
            self._update_log('ERR:Failed to configure LLRF.')
            return False
        return True

    def _get_gen_bpm_intlk(self):
        pos, ang = self._enable_lists['pos'], self._enable_lists['ang']
        return _np.logical_or(pos, ang)

    def _check_valid_enablelist(self, enbllist):
        aux = _np.roll(enbllist, 1)
        # check if pairs have the same enable state
        return not any(_np.sum(aux.reshape(-1, 2), axis=1) == 1)

    def _check_valid_limits(self, limits):
        aux = _np.roll(limits, 1)
        # check if pairs have the same limit
        return not any(_np.diff(aux.reshape(-1, 2), axis=1) != 0)

    def _check_configs(self):
        _t0 = _time.time()

        # bpm status
        dev = self._orbintlk_dev
        value = 0b11111111
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
        if all(devs[idx].connected for idx in self._const.FOUTS_CONFIGS):
            okg = True
            for idx, configs in self._const.FOUTS_CONFIGS.items():
                dev = self._fout_devs[idx]
                for prp, val in configs:
                    prp_rb = prp.replace('-SP', '-RB').replace('-Sel', '-Sts')
                    okg &= dev[prp_rb] == val
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
        # LLRF PsMtn trigger
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
        # BPM PsMtn trigger
        dev = self._bpmpstmn_trig
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

        self._timing_status = value
        self.run_callbacks('TimingStatus-Mon', self._timing_status)

        # LLRF Status
        value = 0b11
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

    # --- callbacks ---

    def _callback_intlk(self, value, **kws):
        _ = kws
        if not self._state:
            return
        if not self._init:
            return
        if self._thread_cb and self._thread_cb.is_alive():
            return
        self._thread_cb = _CAThread(
            target=self._do_callback_intlk, args=(value, ), daemon=True)
        self._thread_cb.start()

    def _do_callback_intlk(self, value):
        if value == 0:
            return

        self._update_log('FATAL:Orbit interlock raised by EVG.')

        if self._is_dry_run:
            self._update_log('Waiting a little before rearming (dry run)...')
            _time.sleep(self._const.DEF_TIME2WAIT_DRYRUN)

        # reset latch flags for BPM interlock core and EVG
        self.cmd_reset('all')

        # reconfigure BPM configuration
        self.cmd_acq_config()

    def _callback_rtmlock(self, pvname, value, **kws):
        if value == 1:
            return
        devidx = int(_SiriusPVName(pvname).sub.split('Ra')[0])
        dev = self._afcti_devs[devidx]
        self._update_log(f'WARN:AFC Timing {devidx} raised RTM clock loss')
        _time.sleep(1)  # sleep a little before reseting
        self._update_log(f'WARN:reseting AFC Timing {devidx} lock latchs.')
        dev['ClkLockedLtcRst-Cmd'] = 1

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

    # ---------------- File handlers ---------------------

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
