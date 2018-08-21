"""Module to deal with correctors."""

import time as _time
import numpy as _np
from epics import PV as _PV
import siriuspy.util as _util
import siriuspy.csdevice.orbitcorr as _csorb
from siriuspy.thread import RepeaterThread as _Repeat
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
        self._state = False
        self._name = corr_name
        self._sp = None
        self._rb = None
        self._pwrstt_sel = None
        self._pwrstt_sts = None

    @property
    def name(self):
        return self._name

    @property
    def connected(self):
        self._isConnected()
        return self._connected

    @property
    def state(self):
        self._isTurnedOn()
        return self._state

    @property
    def ready(self):
        self._isReady()
        return self._ready

    @property
    def applied(self):
        self._kickApplied()
        return self._applied

    @property
    def value(self):
        self._rb.value

    @value.setter
    def value(self, val):
        self._sp.value = val

    def equalKick(self, value):
        return _np.isclose(self._sp.value, value, rtol=1e-12, atol=1e-12)

    def _isConnected(self):
        self._connected = self._sp.connected
        self._connected &= self._rb.connected
        self._connected &= self._pwrstt_sel.connected
        self._connected &= self._pwrstt_sts.connected

    def _isTurnedOn(self):
        self._state = self._pwrstt_sts.value == _PwrSplyConst.PwrState.On

    def _isReady(self):
        self._ready = self.equalKick(self._rb.value)

    def _kickApplied(self):
        self._isReady()
        self._applied = self._ready


class RFCtrl(Corrector):

    def __init__(self):
        super().__init__(_csorb.RF_GEN_NAME)
        opt = {'connection_timeout': TIMEOUT}
        self._sp = _PV(LL_PREF+self._name+':Freq-SP', **opt)
        self._rb = _PV(LL_PREF+self._name+':Freq-RB', **opt)
        self._pwrstt_sel = _PV(LL_PREF+self._name+':PwrState-Sel', **opt)
        self._pwrstt_sts = _PV(LL_PREF+self._name+':PwrState-Sts', **opt)

    def _isTurnedOn(self):
        self._state = self._pwrstt_sts.value == 1  # TODO: database of RF GEN


class CHCV(Corrector):

    def __init__(self, corr_name):
        super().__init__(corr_name)
        opt = {'connection_timeout': TIMEOUT}
        self._opmode = None
        self._sp = _PV(LL_PREF + self._name + ':Current-SP', **opt)
        self._rb = _PV(LL_PREF + self._name + ':Current-RB', **opt)
        self._ref = _PV(LL_PREF + self._name + ':CurrentRef-Mon', **opt)
        self._opmode_sel = _PV(LL_PREF+self._name+':OpMode-Sel', **opt)
        self._opmode_sts = _PV(LL_PREF+self._name+':OpMode-Sts', **opt)
        self._pwrstt_sel = _PV(LL_PREF+self._name+':PwrState-Sel', **opt)
        self._pwrstt_sts = _PV(LL_PREF+self._name+':PwrState-Sts', **opt)

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

    def _isConnected(self):
        self._connected = self._sp.connected
        self._connected &= self._rb.connected
        self._connected &= self._ref.connected
        self._connected &= self._opmode_sel.connected
        self._connected &= self._opmode_sts.connected
        self._connected &= self._pwrstt_sel.connected
        self._connected &= self._pwrstt_sts.connected

    def _kickApplied(self):
        self._applied = self.equalKick(self._ref.value)


class TimingConfig:

    def __init__(self, acc):
        if acc == 'SI':
            evt = 'OrbSI'
            trig = 'SI-Glob:TI-Corrs:'
        elif acc == 'BO':
            evt = 'OrbBO'
            trig = 'BO-Glob:TI-Corrs:'
        pref_name = LL_PREF + _csorb.EVG_NAME + ':' + evt
        opt = {'connection_timeout': TIMEOUT}
        self._evt_sender = _PV(pref_name + 'ExtTrig-Cmd', **opt)
        self._evt_mode_sp = _PV(pref_name + 'Mode-Sel', **opt)
        self._evt_mode_rb = _PV(pref_name + 'Mode-Sts', **opt)
        self._trig_ok_vals = {
            'Src': _HLTimeSearch.get_hl_trigger_sources(trig).index(evt),
            'Delay': 0.0, 'DelayType': 0, 'NrPulses': 1,
            'Duration': 0.1, 'State': 1, 'ByPassIntlk': 0, 'Polarity': 1,
            }
        pref_name = LL_PREF + trig
        self._trig_pvs_rb = {
            'Src': _PV(pref_name + 'Src-Sts', **opt),
            'Delay': _PV(pref_name + 'Delay-RB', **opt),
            'DelayType': _PV(pref_name + 'DelayType-Sts', **opt),
            'NrPulses': _PV(pref_name + 'NrPulses-RB', **opt),
            'Duration': _PV(pref_name + 'Duration-RB', **opt),
            'State': _PV(pref_name + 'State-Sts', **opt),
            'ByPassIntlk': _PV(pref_name + 'ByPassIntlk-Sts', **opt),
            'Polarity': _PV(pref_name + 'Polarity-Sts', **opt),
            }
        self._trig_pvs_sp = {
            'Src': _PV(pref_name + 'Src-Sel', **opt),
            'Delay': _PV(pref_name + 'Delay-SP', **opt),
            'DelayType': _PV(pref_name + 'DelayType-Sel', **opt),
            'NrPulses': _PV(pref_name + 'NrPulses-SP', **opt),
            'Duration': _PV(pref_name + 'Duration-SP', **opt),
            'State': _PV(pref_name + 'State-Sel', **opt),
            'ByPassIntlk': _PV(pref_name + 'ByPassIntlk-Sel', **opt),
            'Polarity': _PV(pref_name + 'Polarity-Sel', **opt),
            }

    def send_evt(self):
        self._evt_sender.value = 1

    @property
    def connected(self):
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
        ok = self.connected
        ok &= self._evt_mode_rb.value == _EVT_MODES.External
        for k, pv in self._trig_pvs_rb.items():
            ok &= self._trig_ok_vals[k] == pv.value

    def configure(self):
        if not self.connected:
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
        prop = 'fun_set_pv'
        db['SyncKicks-Sel'][prop] = self.set_chcvs_mode
        db['ConfigTiming-Cmd'][prop] = self.configure_timing
        db['KickAcqRate-SP'][prop] = self.set_kick_acq_rate
        db = super().get_database(db)
        return db

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)
        self._synced_kicks = True
        self._acq_rate = 10
        self._names = self._const.CH_NAMES + self._const.CV_NAMES
        self._chcvs = {CHCV(dev) for dev in self._names}
        self._rf_ctrl = RFCtrl()
        self._timing = TimingConfig(acc)
        self._corrs_thread = _Repeat(
                1/self._acq_rate, self._update_corrs_strength, niter=0)
        self._corrs_thread.start()

    def apply_corr(self, values):
        """Apply kicks."""
        # apply the RF kick
        if not self._rf_ctrl.equalKick(values[-1]):
            if not self._rf_ctrl.connected:
                self._update_log('ERR: '+self._rf_ctrl.name+' not connected.')
                return
            self._rf_ctrl.value = values[-1]
        # Send correctors setpoint
        for i, corr in enumerate(self._chcvs):
            if corr.equalKick(values[i]):
                continue
            if not corr.connected:
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
            if not self._timing.connected:
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
        corr_values = _np.zeros(self._const.NR_CORRS, dtype=float)
        for i, corr in enumerate(self._chcvs):
            if corr.connected:
                corr_values[i] = corr.value
        corr_values[-1] = self._rf_ctrl.value
        return corr_values

    def set_kick_acq_rate(self, value):
        self._acq_rate = value
        self._corrs_thread.interval = 1/value

    def _update_corrs_strength(self):
        corr_vals = self.get_strength()
        self.run_callbacks('KicksCH-Mon', corr_vals[:self._const.NR_CH])
        self.run_callbacks('KicksCV-Mon', corr_vals[self._const.NR_CH:-1])
        self.run_callbacks('KicksRF-Mon', corr_vals[-1])

    def set_chcvs_mode(self, value):
        self._synced_kicks = value
        if self._synced_kicks == _csorb.SyncKicks.On:
            val = _PwrSplyConst.SlowRefSync
        elif self._synced_kicks == _csorb.SyncKicks.Off:
            val = _PwrSplyConst.SlowRef

        for corr in self._chcvs:
            if corr.connected:
                corr.opmode = val
        self._update_log(
            'Correctors set to {0:s} Mode'.format('Sync' if value else 'Async')
            )
        self.run_callbacks('SyncKicks-Sts', value)
        return True

    def configure_timing(self):
        self._timing.configure()

    def _update_status(self):
        status = 0b1111111
        status = _util.update_bit(
                    status, bit_pos=0, bit_val=not self._timing.connected)
        status = _util.update_bit(
                    status, bit_pos=1, bit_val=not self._timing.is_ok)
        status = _util.update_bit(
                    status, bit_pos=2, bit_val=not self._rf_ctrl.connected)
        status = _util.update_bit(
                    status, bit_pos=3, bit_val=not self._rf_ctrl.state)
        status = _util.update_bit(
                    status, bit_pos=4,
                    bit_val=not all(corr.connected for corr in self._chcvs))
        status = _util.update_bit(
                    status, bit_pos=5,
                    bit_val=not all(corr.opmode_ok for corr in self._chcvs))
        status = _util.update_bit(
                    status, bit_pos=6,
                    bit_val=not all(corr.state for corr in self._chcvs))
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
