"""Module to deal with correctors."""

import time as _time
import numpy as _np
import epics as _epics
import siriuspy.util as _util
import siriuspy.csdevice.orbitcorr as _csorb
from siriuspy.search.hl_time_search import HLTimeSearch as _HLTimeSearch
from siriuspy.csdevice.pwrsupply import Const as _PwrSplyConst
from siriuspy.csdevice.timesys import events_modes as _EVT_MODES
from siriuspy.envars import vaca_prefix as LL_PREF
from .base_class import BaseClass as _BaseClass

TIMEOUT = 0.05


class Corrector:

    def __init__(self, corr_name):
        self._opmode_ok = False
        self._ready = False
        self._applied = False
        self._name = corr_name

    @property
    def name(self):
        return self._name

    @property
    def ready(self):
        return self._ready

    @property
    def applied(self):
        return self._applied

    @property
    def value(self):
        self._sp.value

    @value.setter
    def value(self, val):
        self._sp.value = val

    def equalKick(self, value):
        return _np.isclose(self._sp.value, value, rtol=1e-12, atol=1e-12)

    def _isReady(self, pvname, value, **kwargs):
        self._ready = self.equalKick(value)

    def _kickApplied(self, pvname, value, **kwargs):
        self._applied = self.equalKick(value)


class RFCtrl(Corrector):

    def __init__(self):
        super().__init__(_csorb.RF_GEN_NAME)
        self._sp = _epics.PV(
                            LL_PREF + self._name + ':Freq-SP',
                            connection_timeout=_TIMEOUT)
        self._rb = _epics.PV(
                            LL_PREF + self._name + ':Freq-RB',
                            callback=self._isReady,
                            connection_timeout=TIMEOUT)

    @property
    def is_connected(self):
        conn = self._sp.connected
        conn &= self._rb.connected
        return conn

    def _isReady(self, pvname, value, **kwargs):
        super()._isReady(pvname, value, **kwargs)
        self._kickApplied(self, pvname, value, **kwargs)


class CHCV(Corrector):

    def __init__(self, corr_name):
        super().__init__(corr_name)
        opt = {'connection_timeout': TIMEOUT}
        self._opmode = None
        self._sp = _epics.PV(LL_PREF + self._name + ':Current-SP', **opt)
        self._rb = _epics.PV(
                            LL_PREF + self._name + ':Current-RB',
                            callback=self._isReady, **opt)
        self._ref = _epics.PV(
                            LL_PREF + self._name + ':CurrentRef-Mon',
                            callback=self._kickApplied, **opt)
        self._opmode_sel = _epics.PV(LL_PREF+self._name+':OpMode-Sel', **opt)
        self._opmode_sts = _epics.PV(LL_PREF+self._name+':OpMode-Sts', **opt)

    @property
    def is_connected(self):
        conn = self._sp.connected
        conn &= self._rb.connected
        conn &= self._ref.connected
        conn &= self._opmode_sel.connected
        conn &= self._opmode_sts.connected
        return conn

    @property
    def opmode_ok(self):
        return (self._opmode == self._opmode_sts.value)

    @property
    def opmode(self):
        return self._opmode_sts.value

    @opmode.setter
    def opmode(self, val):
        self._opmode = val
        self._opmode_sel.value = val


class TimingConfig:

    def __init__(self, acc):
        if acc == 'SI':
            evt = 'OrbSI'
            trig = 'SI-Glob:TI-Corrs'
        elif acc == 'BO':
            evt = 'OrbBO'
            trig = 'BO-Glob:TI-Corrs'
        pref_name = LL_PREF + _csorb.EVG_NAME + ':' + evt
        opt = {'connection_timeout': TIMEOUT}
        self._evt_sender = _epics.PV(pref_name + 'ExtTrig-Cmd', **opt)
        self._evt_mode_sp = _epics.PV(pref_name + 'Mode-Sel', **opt)
        self._evt_mode_rb = _epics.PV(pref_name + 'Mode-Sts', **opt)
        self._trig_ok_vals = {
            'Src': _HLTimeSearch.get_hl_trigger_sources(trig).index(evt),
            'Delay': 0.0, 'DelayType': 0, 'NrPulses': 1,
            'Duration': 0.1, 'State': 1, 'ByPassIntlk': 0, 'Polarity': 1,
            }
        pref_name = LL_PREF + trig + ':'
        self._trig_pvs_rb = {
            'Src': _epics.PV(pref_name + 'Src-Sts', **opt),
            'Delay': _epics.PV(pref_name + 'Delay-RB', **opt),
            'DelayType': _epics.PV(pref_name + 'DelayType-Sts', **opt),
            'NrPulses': _epics.PV(pref_name + 'NrPulses-RB', **opt),
            'Duration': _epics.PV(pref_name + 'Duration-RB', **opt),
            'State': _epics.PV(pref_name + 'State-Sts', **opt),
            'ByPassIntlk': _epics.PV(pref_name + 'ByPassIntlk-Sts', **opt),
            'Polarity': _epics.PV(pref_name + 'Polarity-Sts', **opt),
            }
        self._trig_pvs_sp = {
            'Src': _epics.PV(pref_name + 'Src-Sel', **opt),
            'Delay': _epics.PV(pref_name + 'Delay-SP', **opt),
            'DelayType': _epics.PV(pref_name + 'DelayType-Sel', **opt),
            'NrPulses': _epics.PV(pref_name + 'NrPulses-SP', **opt),
            'Duration': _epics.PV(pref_name + 'Duration-SP', **opt),
            'State': _epics.PV(pref_name + 'State-Sel', **opt),
            'ByPassIntlk': _epics.PV(pref_name + 'ByPassIntlk-Sel', **opt),
            'Polarity': _epics.PV(pref_name + 'Polarity-Sel', **opt),
            }

    def send_evt(self):
        self._evt_sender.value = 1

    @property
    def is_connected(self):
        conn = True
        conn &= self._evt_sender.connected
        conn &= self._evt_mode_sp.connected
        conn &= self._evt_mode_rb.connected
        for k, pv in self._trig_pvs_rb.items():
            conn &= pv.connected
        for k, pv in self._trig_pvs_sp.items():
            conn &= pv.connected
        return conn

    @property
    def is_ok(self):
        ok = self.is_connected
        ok &= self._evt_mode_rb.value == _EVT_MODES.External
        for k, pv in self._trig_pvs_rb.items():
            ok &= self._trig_ok_vals[k] == pv.value

    def configure(self):
        if not self.is_connected:
            return
        self._evt_mode_sp.value = _EVT_MODES.External
        for k, pv in self._trig_pvs_sp.items():
            pv.value = self._trig_ok_vals[k]


class BaseCorrectors(_BaseClass):
    pass


class EpicsCorrectors(BaseCorrectors):
    """Class to deal with correctors."""
    TINY_INTERVAL = 0.01
    NUM_TIMEOUT = 1000

    def get_database(self):
        """Get the database of the class."""
        db = _csorb.get_corrs_database(self.acc)
        db['SyncKicks-Sel']['fun_set_pv'] = self.set_chcvs_mode
        db['ConfigTiming-Cmd']['fun_set_pv'] = self.configure_timing
        db = {self.prefix + k: v for k, v in db.items()}
        return db

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)
        self._synced_kicks = True
        self._names = self._const.CH_NAMES + self._const.CV_NAMES
        self._chcvs = {CHCV(dev) for dev in self._names}
        self._rf_ctrl = RFCtrl()
        self._timing = TimingConfig(acc)

    def apply_corr(self, values):
        """Apply kicks."""
        # apply the RF kick
        if not self._rf_ctrl.equalKick(values[-1]):
            if not self._rf_ctrl.is_connected:
                self._update_log('ERR: '+self.rf_sp.pvname+' not connected.')
                return
            self._rf_ctrl.value = values[-1]
        # Send correctors setpoint
        for i, corr in enumerate(self._chcvs):
            if corr.equalKick(values[i]):
                continue
            if not corr.is_connected:
                self._update_log('ERR: ' + corr.name + ' not connected.')
                return
            elif not corr.opmode_ok:
                self._update_log('ERR: ' + corr.name + 'mode not configured.')
                return
            corr.value = values[i]
        # Wait for readbacks to be updated
        if self._timed_out(mode='ready'):
            self._update_log('ERR: timeout waiting correctors RB')
            return
        # Send trigger signal for implementation
        if self._synced_kicks:
            if not self._timing.is_connected:
                self._update_log('ERR: timing disconnected.')
                return
            elif not self._timing.is_ok:
                self._update_log('ERR: timing not configured.')
                return
            self._timing.send_evt()
        # Wait for references to be updated
        if self._timed_out(mode='applied'):
            self._update_log('ERR: timeout waiting correctors Ref')

    def get_strength(self):
        """Get the correctors strengths."""
        corr_values = _np.zeros(len(self._names)+1, dtype=float)
        for i, corr in enumerate(self._chcvs):
            corr_values[i] = corr.value
        corr_values[-1] = self._rf_ctrl.value
        return corr_values

    def _update_log(self, value):
        self.run_callbacks(self.prefix + 'Log-Mon', value)

    def set_chcvs_mode(self, value):
        self._synced_kicks = value
        if self._synced_kicks == _csorb.SyncKicks.On:
            val = _PwrSplyConst.SlowRefSync
        elif self._synced_kicks == _csorb.SyncKicks.Off:
            val = _PwrSplyConst.SlowRef

        for corr in self._chcvs:
            if corr.is_connected:
                corr.opmode = val
        self._update_log(
            'Correctors set to {0:s} Mode'.format('Sync' if value else 'Async')
            )
        self.run_callbacks('SyncKicks-Sts', value)
        return True

    def configure_timing(self):
        self._timing.configure()

    def _update_status(self):
        status = 0b11111
        status = _util.update_bit(
                    status, bit_pos=0, bit_val=not self._timing.is_connected)
        status = _util.update_bit(
                    status, bit_pos=1, bit_val=not self._timing.is_ok)
        status = _util.update_bit(
                    status, bit_pos=2, bit_val=not self._rf_ctrl.is_connected)
        status = _util.update_bit(
                    status, bit_pos=3,
                    bit_val=not all(corr.is_connected for corr in self._chcvs))
        status = _util.update_bit(
                    status, bit_pos=4,
                    bit_val=not all(corr.opmode_ok for corr in self._chcvs))
        self._status = status
        self.run_callbacks('CorrStatus-Mon', status)

    def _timed_out(self, mode='ready'):
        """Timed out."""
        for _ in range(self.NUM_TIMEOUT):
            ok = True
            for corr in self._chcvs:
                if mode == 'ready':
                    ok &= corr.is_ready
                elif mode == 'applied':
                    ok &= corr.is_applied
            if ok:
                return False
            _time.sleep(self.TINY_INTERVAL)
        return True
