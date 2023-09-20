"""High Level FOFB main application."""

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

    def __init__(self, tests=False):
        """Class constructor."""
        super().__init__()
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
            'posx_min': _np.zeros(self._const.nr_bpms, dtype=float),
            'posx_max': _np.zeros(self._const.nr_bpms, dtype=float),
            'posy_min': _np.zeros(self._const.nr_bpms, dtype=float),
            'posy_max': _np.zeros(self._const.nr_bpms, dtype=float),
            'angx_min': _np.zeros(self._const.nr_bpms, dtype=float),
            'angx_max': _np.zeros(self._const.nr_bpms, dtype=float),
            'angy_min': _np.zeros(self._const.nr_bpms, dtype=float),
            'angy_max': _np.zeros(self._const.nr_bpms, dtype=float),
            'minsum': _np.zeros(self._const.nr_bpms, dtype=float),
        }
        self._acq_chan = self._pvs_database['PsMtmAcqChannel-Sel']['value']
        self._acq_spre = self._pvs_database['PsMtmAcqSamplesPre-SP']['value']
        self._acq_spost = self._pvs_database['PsMtmAcqSamplesPost-SP']['value']

        # devices and connections
        self._evg_dev = _EVG(
            props2init=[
                'IntlkCtrlEnbl-Sel', 'IntlkCtrlEnbl-Sts',
                'IntlkCtrlRst-Sel', 'IntlkCtrlRst-Sts'])

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

        havebeam_pvname = _PVName(
            'SI-Glob:AP-CurrInfo:StoredEBeam-Mon').substitute(
                prefix=_vaca_prefix)
        self._havebeam_pv = _PV(
            havebeam_pvname, connection_timeout=0.05,
            callback=self._callback_havebeam)

        # pvs to write methods
        self.map_pv2write = {
            'State-Sel': self.set_state,
            'BPMPosEnblList-SP': _part(self.set_enbllist, 'pos'),
            'BPMAngEnblList-SP': _part(self.set_enbllist, 'ang'),
            'BPMMinSumEnblList-SP': _part(self.set_enbllist, 'minsum'),
            'PosMinLimX-SP': _part(self.set_intlk_lims, 'posx_min'),
            'PosMaxLimX-SP': _part(self.set_intlk_lims, 'posx_max'),
            'PosMinLimY-SP': _part(self.set_intlk_lims, 'posy_min'),
            'PosMaxLimY-SP': _part(self.set_intlk_lims, 'posy_max'),
            'AngMinLimX-SP': _part(self.set_intlk_lims, 'angx_min'),
            'AngMaxLimX-SP': _part(self.set_intlk_lims, 'angx_max'),
            'AngMinLimY-SP': _part(self.set_intlk_lims, 'angy_min'),
            'AngMaxLimY-SP': _part(self.set_intlk_lims, 'angy_max'),
            'MinSumLim-SP': _part(self.set_intlk_lims, 'minsum'),
            'ResetBPMGen-Cmd': _part(self.cmd_reset, 'bpm_gen'),
            'ResetBPMPos-Cmd': _part(self.cmd_reset, 'bpm_pos'),
            'ResetBPMAng-Cmd': _part(self.cmd_reset, 'bpm_ang'),
            'ResetBPM-Cmd': _part(self.cmd_reset, 'bpm_all'),
            'Reset-Cmd': _part(self.cmd_reset, 'all'),
            'PsMtmAcqChannel-Sel': self.set_acq_channel,
            'PsMtmAcqSamplesPre-SP': self.set_acq_nrspls_pre,
            'PsMtmAcqSamplesPost-SP': self.set_acq_nrspls_post,
            'PsMtmAcqConfig-Cmd': self.cmd_config_acq,
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
            'State-Sel': self._state,
            'State-Sts': self._state,
            'BPMStatus-Mon': self._bpm_status,
            'EVGStatus-Mon': self._evg_status,
            'PosMinLimX-SP': self._limits['posx_min'],
            'PosMinLimX-RB': self._limits['posx_min'],
            'PosMaxLimX-SP': self._limits['posx_max'],
            'PosMaxLimX-RB': self._limits['posx_max'],
            'PosMinLimY-SP': self._limits['posy_min'],
            'PosMinLimY-RB': self._limits['posy_min'],
            'PosMaxLimY-SP': self._limits['posy_max'],
            'PosMaxLimY-RB': self._limits['posy_max'],
            'AngMinLimX-SP': self._limits['angx_min'],
            'AngMinLimX-RB': self._limits['angx_min'],
            'AngMaxLimX-SP': self._limits['angx_max'],
            'AngMaxLimX-RB': self._limits['angx_max'],
            'AngMinLimY-SP': self._limits['angy_min'],
            'AngMinLimY-RB': self._limits['angy_min'],
            'AngMaxLimY-SP': self._limits['angy_max'],
            'AngMaxLimY-RB': self._limits['angy_max'],
            'MinSumLim-SP': self._limits['minsum'],
            'MinSumLim-RB': self._limits['minsum'],
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
            pvn = f'BPM{ilk}EnblList-SP'
            enb = self._enable_lists[ilk]
            self.run_callbacks(pvn, enb)
            if not okl:
                self.run_callbacks(
                    pvn.replace('SP', 'RB').replace('Sel', 'Sts'), enb)
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

    @property
    def havebeam(self):
        """Return if there is stored beam."""
        return self._havebeam_pv.connected and self._havebeam_pv.value

    # --- interlock control ---

    def set_state(self, value):
        """Set orbit interlock state.
        Configure global BPM interlock enable and EVG interlock enable."""
        if not 0 <= value < len(_ETypes.OFF_ON):
            return False

        if value:
            pos, ang = self._enable_lists['pos'], self._enable_lists['ang']
            glob_en = _np.logical_or(pos, ang)
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
        self.run_callbacks('LoopState-Sts', self._state)
        return True

    # --- enable lists ---

    def set_enbllist(self, intlk, value):
        """Set enable list for interlock type."""
        self._update_log('Setting {0:s} EnblList'.format(intlk.upper()))

        # check size
        bkup = self._enable_lists[intlk]
        new = _np.array(value, dtype=bool)
        if bkup.size != new.size:
            self._update_log(
                'ERR: Wrong {0:s} EnblList size.'.format(intlk.upper()))
            return False

        self._enable_lists[intlk] = new

        # do not set enable lists and save to file in initialization
        if self._init:
            # handle devices enable configuration
            fun = getattr(self._orbintlk_dev, f'set_{intlk}_enable')
            fun(list(value))
            # set_gen_enable


            # save to autosave files
            self._save_enbllist(intlk, _np.array([value], dtype=bool))

        # update readback pv
        self.run_callbacks(intlk.upper()+'EnblList-RB', new)
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
            filename = getattr(self._const, intlk+'enbl_fname')
            path = _os.path.split(filename)[0]
            _os.makedirs(path, exist_ok=True)
            _np.savetxt(filename, value)
        except FileNotFoundError:
            self._update_log(
                f'WARN:Could not save {intlk} enable list to file.')

    # --- limits ---

    def set_intlk_lims(self, intlk_lim, value):


    # --- callbacks ---

    def _callback_havebeam(self, value, **kws):
        if not value and self._loop_state == self._const.LoopState.Closed:
            self._update_log('FATAL:We do not have stored beam!')
            self._update_log('FATAL:Opening FOFB loop...')
            self.set_loop_state(self._const.LoopState.Open, abort=True)

    def _callback_intlk(self, pvname, value, **kws):
        sub = _PVName(pvname).sub[:2]
        old = self._intlk_values[pvname]
        orbdis = _get_bit(value, 0) and not _get_bit(old, 0)
        paclos = _get_bit(value, 1) and not _get_bit(old, 1)
        self._intlk_values[pvname] = value
        if value != 0:
            pref = ('FATAL' if self._loop_state else 'WARN') + \
                ':Ctrlr.' + sub + ' detected '
            if orbdis:
                self._update_log(pref + 'large orb.dist.!')
            if paclos:
                self._update_log(pref + 'packet loss!')

            if self._loop_state != self._const.LoopState.Closed:
                return

            if self._thread_loopstate is None or \
                    (self._thread_loopstate is not None and
                     not self._thread_loopstate.is_alive()) or \
                    (self._thread_loopstate is not None and
                     self._thread_loopstate.is_alive() and
                     self._loop_state_lastsp != self._const.LoopState.Open):
                self._update_log('FATAL:Opening FOFB loop...')
                self.run_callbacks('LoopState-Sel', self._const.LoopState.Open)
                self.run_callbacks('LoopState-Sts', self._const.LoopState.Open)
                self.set_loop_state(self._const.LoopState.Open, abort=True)

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

    def _check_configs(self):
        tplanned = 1.0/App.SCAN_FREQUENCY
        while not self.quit:
            if not self.scanning:
                _time.sleep(tplanned)
                continue

            _t0 = _time.time()

            # bpm status
            value = 0
            if self._orbintlk_dev.connected:
                idcs = _np.where(self.corr_enbllist[:-1] == 1)[0]
                # PwrStateOn
                state = self._const.OffOn.On
                if not self._corrs_dev.check_pwrstate(
                        state, psindices=idcs, timeout=0.2):
                    value = _updt_bit(value, 1, 1)
                # OpModeConfigured
                opmode = self._corrs_dev.OPMODE_STS.manual \
                    if self._loop_state == self._const.LoopState.Open \
                    else self._corrs_dev.OPMODE_STS.fofb
                if not self._corrs_dev.check_opmode(
                        opmode, psindices=idcs, timeout=0.2):
                    value = _updt_bit(value, 2, 1)
                # AccFreezeConfigured
                freeze = self._get_corrs_fofbacc_freeze_desired()
                if not self._corrs_dev.check_fofbacc_freeze(
                        freeze, timeout=0.2):
                    value = _updt_bit(value, 3, 1)
                # InvRespMatRowSynced
                if not self._corrs_dev.check_invrespmat_row(self._pscoeffs):
                    value = _updt_bit(value, 4, 1)
                # AccGainSynced
                if not self._corrs_dev.check_fofbacc_gain(self._psgains):
                    value = _updt_bit(value, 5, 1)
                # AccSatLimsSynced
                chn, chl = self._const.ch_names, self._ch_maxacccurr
                cvn, cvl = self._const.cv_names, self._cv_maxacccurr
                isok = self._corrs_dev.check_fofbacc_satmax(chl, psnames=chn)
                isok &= self._corrs_dev.check_fofbacc_satmin(-chl, psnames=chn)
                isok &= self._corrs_dev.check_fofbacc_satmax(cvl, psnames=cvn)
                isok &= self._corrs_dev.check_fofbacc_satmin(-cvl, psnames=cvn)
                if not isok:
                    value = _updt_bit(value, 6, 1)
                # AccDecimationSynced
                dec = self._corr_accdec_val
                if not self._corrs_dev.check_fofbacc_decimation(dec):
                    value = _updt_bit(value, 7, 1)
            else:
                value = 0b11111111

            self._corr_status = value
            self.run_callbacks('BPMStatus-Mon', self._corr_status)

            ttook = _time.time() - _t0
            tsleep = tplanned - ttook
            if tsleep > 0:
                _time.sleep(tsleep)
            else:
                _log.warning(
                    'Corrector configuration check took more than planned... '
                    '{0:.3f}/{1:.3f} s'.format(ttook, tplanned))
