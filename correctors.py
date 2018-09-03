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
    TINY_KICK = 1e-3

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

    @state.setter
    def state(self, value):
        self._setonstate(value)

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
        return self._get_value()

    @value.setter
    def value(self, val):
        self._sp.put(val, wait=False)
        # self._sp.value = val

    def equalKick(self, value):
        return abs(self._sp.value - value) <= self.TINY_KICK

    def _get_value(self):
        return self._rb.value

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

    def _setonstate(self, boo):
        val = _PwrSplyConst.PwrState.On if boo else _PwrSplyConst.PwrState.Off
        self._pwrstt_sel.value = val


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
        # self._evt_sender = _PV(
        #     'guilherme-AS-Glob:PS-Timing:Trigger-Cmd', **opt)
        self._evt_mode_sp = _PV(pref_name + 'Mode-Sel', **opt)
        self._evt_mode_rb = _PV(pref_name + 'Mode-Sts', **opt)
        self._trig_ok_vals = {
            'Src': _HLTimeSearch.get_hl_trigger_sources(trig).index(evt),
            'Delay': 0.0, 'DelayType': 0, 'NrPulses': 1,
            'Duration': 0.1, 'State': 1, 'Polarity': 1,
            }
        pref_name = LL_PREF + trig
        self._trig_pvs_rb = {
            'Src': _PV(pref_name + 'Src-Sts', **opt),
            'Delay': _PV(pref_name + 'Delay-RB', **opt),
            'DelayType': _PV(pref_name + 'DelayType-Sts', **opt),
            'NrPulses': _PV(pref_name + 'NrPulses-RB', **opt),
            'Duration': _PV(pref_name + 'Duration-RB', **opt),
            'State': _PV(pref_name + 'State-Sts', **opt),
            'Polarity': _PV(pref_name + 'Polarity-Sts', **opt),
            }
        self._trig_pvs_sp = {
            'Src': _PV(pref_name + 'Src-Sel', **opt),
            'Delay': _PV(pref_name + 'Delay-SP', **opt),
            'DelayType': _PV(pref_name + 'DelayType-Sel', **opt),
            'NrPulses': _PV(pref_name + 'NrPulses-SP', **opt),
            'Duration': _PV(pref_name + 'Duration-SP', **opt),
            'State': _PV(pref_name + 'State-Sel', **opt),
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
        return ok

    def configure(self):
        if not self.connected:
            return False
        self._evt_mode_sp.value = _EVT_MODES.External
        for k, pv in self._trig_pvs_sp.items():
            pv.value = self._trig_ok_vals[k]
        return True


class BaseCorrectors(_BaseClass):
    pass


class EpicsCorrectors(BaseCorrectors):
    """Class to deal with correctors."""
    TINY_INTERVAL = 0.005
    NUM_TIMEOUT = 1000

    def get_database(self):
        """Get the database of the class."""
        db = _csorb.get_corrs_database(self.acc)
        prop = 'fun_set_pv'
        db['SyncKicks-Sel'][prop] = self.set_chcvs_mode
        db['ConfigTiming-Cmd'][prop] = self.configure_timing
        db['ConfigCorrs-Cmd'][prop] = self.configure_correctors
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

    def apply_kicks(self, values):
        """Apply kicks."""
        strn = '{0:20s}: {1:7.3f}'
        # apply the RF kick
        t0 = _time.time()
        self.put_value_in_corr(self._rf_ctrl, values[-1], False)
        t1 = _time.time()
        # print(strn.format('send rf:', 1000*(t1-t0)))

        # Send correctors setpoint
        for i, corr in enumerate(self._chcvs):
            self.put_value_in_corr(corr, values[i])
        t2 = _time.time()
        # print(strn.format('send sp:', 1000*(t2-t1)))

        # Wait for readbacks to be updated
        if self._timed_out(mode='ready'):
            self._update_log('ERR: timeout waiting correctors RB')
            return
        t3 = _time.time()
        # print(strn.format('check ready:', 1000*(t3-t2)))

        # Send trigger signal for implementation
        _time.sleep(0.450)
        self.send_evt()
        t4 = _time.time()
        # print(strn.format('send evt:', 1000*(t4-t3)))

        # Wait for references to be updated
        if self._timed_out(mode='applied'):
            self._update_log('ERR: timeout waiting correctors Ref')
        t5 = _time.time()
        # print(strn.format('check applied:', 1000*(t5-t4)))
        # print(strn.format('total:', 1000*(t5-t0)))
        # print()

    def put_value_in_corr(self, corr, value, flag=True):
        if corr.equalKick(value):
            return
        if not corr.connected:
            self._update_log('ERR: ' + corr.name + ' not connected.')
        elif not corr.state:
            self._update_log('ERR: ' + corr.name + ' is off.')
        elif flag and not corr.opmode_ok:
            self._update_log('ERR: ' + corr.name + ' mode not configured.')
        else:
            corr.value = value

    def send_evt(self):
        if not self._synced_kicks:
            return
            if not self._timing.connected:
                self._update_log('ERR: timing disconnected.')
                return
            elif not self._timing.is_ok:
                self._update_log('ERR: timing not configured.')
                return
            self._timing.send_evt()

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
        return True

    def _update_corrs_strength(self):
        corr_vals = self.get_strength()
        self.run_callbacks('KicksCH-Mon', corr_vals[:self._const.NR_CH])
        self.run_callbacks('KicksCV-Mon', corr_vals[self._const.NR_CH:-1])
        self.run_callbacks('KicksRF-Mon', corr_vals[-1])

    def set_chcvs_mode(self, value):
        self._synced_kicks = value
        if self._synced_kicks == _csorb.SyncKicks.On:
            val = _PwrSplyConst.OpMode.SlowRefSync
        elif self._synced_kicks == _csorb.SyncKicks.Off:
            val = _PwrSplyConst.OpMode.SlowRef

        for corr in self._chcvs:
            if corr.connected:
                corr.opmode = val
            else:
                self._update_log('ERR: Failed to configure correctors')
                return False
        self._update_log(
            'Correctors set to {0:s} Mode'.format('Sync' if value else 'Async')
            )
        self.run_callbacks('SyncKicks-Sts', value)
        return True

    def configure_timing(self, _):
        if not self._timing.configure():
            self._update_log('ERR: Failed to configure timing')
            return False
        return True

    def configure_correctors(self, _):
        if self._synced_kicks == _csorb.SyncKicks.On:
            val = _PwrSplyConst.OpMode.SlowRefSync
        elif self._synced_kicks == _csorb.SyncKicks.Off:
            val = _PwrSplyConst.OpMode.SlowRef

        if self._rf_ctrl.connected:
            self._rf_ctrl.state = True
        else:
            self._update_log('ERR: Failed to configure correctors')
            return False

        for corr in self._chcvs:
            if corr.connected:
                corr.state = True
                corr.opmode = val
            else:
                self._update_log('ERR: Failed to configure correctors')
                return False
        return True

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
        corrs = list()
        corrs.extend(self._chcvs)
        corrs.append(self._rf_ctrl)
        for _ in range(self.NUM_TIMEOUT):
            okg = True
            for i, corr in enumerate(corrs):
                okl = corr.ready if mode == 'ready' else corr.applied
                if okl:
                    del corrs[i]
                okg &= okl
            if okg:
                return False
            _time.sleep(self.TINY_INTERVAL)
        return True
