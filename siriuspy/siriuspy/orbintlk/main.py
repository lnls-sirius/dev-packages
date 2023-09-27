"""High Level Orbit Interlock main application."""

import os as _os
import logging as _log
import time as _time
from functools import partial as _part
import epics as _epics
import numpy as _np

from ..util import update_bit as _updt_bit, get_bit as _get_bit
from ..epics import PV as _PV
from ..callbacks import Callback as _Callback
from ..envars import VACA_PREFIX as _vaca_prefix
from ..namesys import SiriusPVName as _PVName
from ..devices import OrbitInterlock as _OrbitIntlk, FamBPMs as _FamBPMs, \
    EVG as _EVG

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
        self._state = self._const.OffOn.Off
        self._bpm_status = self._pvs_database['BPMStatus-Mon']['value']
        self._evg_status = self._pvs_database['EVGStatus-Mon']['value']
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

        # devices and connections
        self._evg_dev = _EVG(
            props2init=[
                'IntlkCtrlEnbl-Sel', 'IntlkCtrlEnbl-Sts',
                'IntlkCtrlRst-Sel', 'IntlkCtrlRst-Sts',
                'IntlkEvtStatus-Mon'])
        self._evg_intlk_pv = self._evg_dev.pv_object('IntlkEvtStatus-Mon')  # TODO> confirmar com maurício se é essa PV mesmo
        self._evg_intlk_pv.auto_monitor = True
        self._evg_intlk_pv.add_callback(self._callback_intlk)

        self._orbintlk_dev = _OrbitIntlk()

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
            ])

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
        }

        # configuration scanning
        self.quit = False
        self.scanning = False
        self.thread_check_configs = _epics.ca.CAThread(
            target=self._check_configs, daemon=True)
        self.thread_check_configs.start()

    def init_database(self):
        """Set initial PV values."""
        pvn2vals = {
            'Enable-Sel': self._state,
            'Enable-Sts': self._state,
            'BPMStatus-Mon': self._bpm_status,
            'EVGStatus-Mon': self._evg_status,
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
            okl = self._load_enbllist(ilk)
            pvn = f'{ilk}EnblList'
            enb = self._enable_lists[ilk]
            self.run_callbacks(pvn+'-SP', enb)
            if not okl:
                self.run_callbacks(pvn+'-RB', enb)

        # limits
        for ilk in ['Pos', 'Ang']:
            for pln in ['X', 'Y']:
                for lim in ['Min', 'Max']:
                    atn = f'{ilk}_{pln}_{lim}'.lower()
                    pvn = f'{ilk}{pln}{lim}Lim'
                    okl = self._load_limits(atn)
                    val = self._limits[atn]
                    self.run_callbacks(pvn+'-SP', val)
                    if not okl:
                        self.run_callbacks(pvn+'-RB', val)
        
        okl = self._load_limits('minsum')
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
        value = None
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        _log.info('Write received for: %s --> %s', reason, str(value))
        if reason in self.map_pv2write.keys():
            status = self.map_pv2write[reason](value)
            _log.info('%s Write for: %s --> %s',
                      str(status).upper(), reason, str(value))
            return status
        _log.warning('PV %s does not have a set function.', reason)
        return False

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
        """FamBPMs device."""
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
            glob_en = _np.zeros(self._const.nr_bpms)
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
        bkup = self._enable_lists[intlk]
        new = _np.array(value, dtype=bool)
        if bkup.size != new.size:
            self._update_log(f'ERR: Wrong {intlkname} EnblList size.')
            return False

        self._enable_lists[intlk] = new

        # do not set enable lists and save to file in initialization
        if self._init:
            # handle device enable configuration

            # set BPM interlock specific enable state
            fun = getattr(self._orbintlk_dev, f'set_{intlk}_enable')
            if not fun(list(value)):
                self._update_log(f'ERR:Could not set BPM {intlkname}')
                self._update_log('ERR:interlock enable.')
                return False
            
            # if interlock is already enabled, update BPM general enable state
            if self._state and intlk in ['pos', 'ang']:
                glob_en = self._get_gen_bpm_intlk()
                if not self._orbintlk_dev.set_gen_enable(list(glob_en)):
                    self._update_log('ERR:Could not set BPM general')
                    self._update_log('ERR:interlock enable.')
                    return False

            # save to autosave files
            self._save_enbllist(intlk, _np.array([value], dtype=bool))

        # update readback pv
        self.run_callbacks(f'{intlkname}EnblList-RB', new)
        return True

    def _load_enbllist(self, intlk):
        filename = getattr(self._const, intlk+'_enbl_fname')
        if not _os.path.isfile(filename):
            return
        okl = self.set_enbllist(intlk, _np.loadtxt(filename))
        if okl:
            msg = f'Loaded {intlk} enable list!'
        else:
            msg = f'ERR:Problem loading {intlk} enable list from file.'
        self._update_log(msg)
        return okl

    def _save_enbllist(self, intlk, value):
        try:
            filename = getattr(self._const, intlk+'_enbl_fname')
            path = _os.path.split(filename)[0]
            _os.makedirs(path, exist_ok=True)
            _np.savetxt(filename, value)
        except FileNotFoundError:
            self._update_log(
                f'WARN:Could not save {intlk} enable list to file.')

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
        bkup = self._limits[intlk_lim]
        new = _np.array(value, dtype=int)
        if bkup.size != new.size:
            self._update_log(f'ERR: Wrong {limname} limits size.')
            return False

        self._limits[intlk_lim] = new

        # do not set limits and save to file in initialization
        if self._init:
            # handle device limits configuration

            # set BPM interlock limits
            fun = getattr(self._orbintlk_dev, f'set_{intlk_lim}_thres')
            if not fun(list(value)):
                self._update_log(f'ERR:Could not set BPM {limname}')
                self._update_log('ERR:interlock limits.')
                return False

            # save to autosave files
            self._save_limits(intlk_lim, _np.array([value]))

        # update readback pv
        self.run_callbacks(f'{limname}Lim-RB', new)
        return True

    def _load_limits(self, intlk_lim):
        filename = getattr(self._const, intlk_lim+'_lim_fname')
        if not _os.path.isfile(filename):
            return
        okl = self.set_intlk_lims(intlk_lim, _np.loadtxt(filename))
        if okl:
            msg = f'Loaded {intlk_lim} limits!'
        else:
            msg = f'ERR:Problem loading {intlk_lim} limits from file.'
        self._update_log(msg)
        return okl
    
    def _save_limits(self, intlk_lim, value):
        try:
            filename = getattr(self._const, intlk_lim+'_lim_fname')
            path = _os.path.split(filename)[0]
            _os.makedirs(path, exist_ok=True)
            _np.savetxt(filename, value)
        except FileNotFoundError:
            self._update_log(
                f'WARN:Could not save {intlk_lim} limits to file.')

    # --- reset ---

    def cmd_reset(self, state):
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
        if self._thread_acq is None or not self._thread_acq.is_alive():
            self._thread_acq = _epics.ca.CAThread(
                target=self._acq_config, daemon=True)
            self._thread_acq.start()
            return True
        else:
            self._update_log('WARN:BPM configuration already in progress.')
            return False

    def _acq_config(self):
        self._update_log('Aborting BPM acquisition...')
        ret = self._fambpm_dev.cmd_mturn_acq_abort()
        if ret > 0:
            self._update_log('ERR:Failed to abort BPM acquisition.')
            return
        self._update_log('...done. Configuring BPM acquisition...')
        for bpm in self._fambpm_dev.devices:
            bpm.acq_repeat = self._const.AcqRepeat.Normal
            bpm.acq_channel = self._acq_chan
            bpm.acq_trigger = self._const.AcqTrigTyp.External
            bpm.acq_nrsamples_pre = self._acq_spre
            bpm.acq_nrsamples_post = self._acq_spost
        self._update_log('...done. Starting BPM acquisition...')
        ret = self.cmd_mturn_acq_start()
        if ret > 0:
            self._update_log('ERR:Failed to start BPM acquisition.')
            return
        self._update_log('...done!')

    # --- callbacks ---

    def _callback_intlk(self, pvname, value, **kws):
        if value != 0:  # TODO> confirmar o valor que a PV assume em caso de interlock
            self._update_log('FATAL:Orbit interlock raised by EVG.')

        if self._is_dry_run:
            self._update_log('Waiting a little before rearming (dry run)...')
            _time.sleep(self._const.DEF_TIME2WAIT_DRYRUN)
        
        # reset latch flags for BPM interlock core and EVG 
        self.cmd_reset('all')

        # reconfigure BPM configuration
        self.cmd_acq_config()

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

    # --- auxiliary status methods ---

    def _get_gen_bpm_intlk(self):
        pos, ang = self._enable_lists['pos'], self._enable_lists['ang']
        return _np.logical_or(pos, ang)

    def _check_configs(self):
        tplanned = 1.0/App.SCAN_FREQUENCY
        while not self.quit:
            if not self.scanning:
                _time.sleep(tplanned)
                continue

            _t0 = _time.time()

            # bpm status
            dev = self._orbintlk_dev
            value = 0
            if dev.connected:
                # PosEnblSynced
                val = dev.pos_enable == self._enable_lists['pos']
                value = _updt_bit(value, 1, val)
                # AngEnblSynced
                val = dev.ang_enable == self._enable_lists['ang']
                value = _updt_bit(value, 2, val)
                # MinSumEnblSynced
                val = dev.minsum_enable == self._enable_lists['minsum']
                value = _updt_bit(value, 3, val)
                # GlobEnblSynced
                val = dev.gen_enable == self._get_gen_bpm_intlk()
                value = _updt_bit(value, 4, val)
                # PosLimsSynced           
                okp = dev.pos_x_min_thres == self._limits['pos_x_min']
                okp = dev.pos_x_max_thres == self._limits['pos_x_max']
                okp = dev.pos_y_min_thres == self._limits['pos_y_min']
                okp = dev.pos_y_max_thres == self._limits['pos_y_max']
                value = _updt_bit(value, 5, okp)
                # AngLimsSynced
                oka = dev.ang_x_min_thres == self._limits['ang_x_min']
                oka = dev.ang_x_max_thres == self._limits['ang_x_max']
                oka = dev.ang_y_min_thres == self._limits['ang_y_min']
                oka = dev.ang_y_max_thres == self._limits['ang_y_max']
                value = _updt_bit(value, 6, oka)
                # MinSumLimsSynced
                oks = dev.minsum_thres == self._limits['minsum']
                value = _updt_bit(value, 7, oks)
            else:
                value = 0b11111111

            self._bpm_status = value
            self.run_callbacks('BPMStatus-Mon', self._bpm_status)

            # evg status
            dev = self._evg_dev
            value = 0
            if dev.connected:
                # IntlkEnblSynced
                val = dev['IntlkCtrlEnbl-Sts'] == self._state
                value = _updt_bit(value, 1, val)
            else:
                value = 0b11

            self._evg_status = value
            self.run_callbacks('EVGStatus-Mon', self._evg_status)

            # check time elapsed
            ttook = _time.time() - _t0
            tsleep = tplanned - ttook
            if tsleep > 0:
                _time.sleep(tsleep)
            else:
                _log.warning(
                    'Configuration check took more than planned... '
                    '{0:.3f}/{1:.3f} s'.format(ttook, tplanned))
