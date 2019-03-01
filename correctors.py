"""Module to deal with correctors."""

import time as _time
import math as _math
import logging as _log
import numpy as _np
from epics import PV as _PV
import siriuspy.util as _util
from siriuspy.thread import RepeaterThread as _Repeat
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.csdevice.timesys import Const as _TIConst
from siriuspy.search import HLTimeSearch as _HLTimesearch
from siriuspy.envars import vaca_prefix as LL_PREF
from .base_class import (
    BaseClass as _BaseClass,
    BaseTimingConfig as _BaseTimingConfig)

TIMEOUT = 0.05


class Corrector(_BaseTimingConfig):
    """Corrector class."""

    TINY_KICK = 1e-3  # urad

    def __init__(self, corr_name):
        """Init method."""
        super().__init__(corr_name[:2])
        self._name = corr_name
        self._sp = None
        self._rb = None

    @property
    def name(self):
        """Corrector name."""
        return self._name

    @property
    def connected(self):
        """Status connected."""
        conn = super().connected
        pvs = (self._sp, self._rb)
        for pv in pvs:
            if not pv.connected:
                _log.debug('NOT CONN: ' + pv.pvname)
            conn &= pv.connected
        return conn

    @property
    def state(self):
        """State."""
        pv = self._config_pvs_rb['PwrState']
        return pv.value == _PSConst.PwrStateSel.On if pv.connected else False

    @state.setter
    def state(self, boo):
        val = _PSConst.PwrStateSel.On if boo else _PSConst.PwrStateSel.Off
        pv = self._config_pvs_sp['PwrState']
        if pv.connected:
            self._config_ok_vals['PwrState'] = val
            pv.put(val, wait=False)

    @property
    def ready(self):
        """Ready status."""
        return self.equalKick(self._rb.value)

    @property
    def applied(self):
        """Status applied."""
        return self.equalKick(self._rb.value)

    @property
    def value(self):
        """Value."""
        return self._rb.value

    @value.setter
    def value(self, val):
        self._sp.put(val, wait=False)

    def equalKick(self, value):
        """Equal kick."""
        return _math.isclose(self._sp.value, value, abs_tol=self.TINY_KICK)


class RFCtrl(Corrector):
    """RF control class."""

    def __init__(self, acc):
        """Init method."""
        super().__init__(acc)
        self._name = self._csorb.RF_GEN_NAME
        opt = {'connection_timeout': TIMEOUT}
        self._sp = _PV(LL_PREF+self._name+':Freq-SP', **opt)
        self._rb = _PV(LL_PREF+self._name+':Freq-RB', **opt)
        self._config_ok_vals = {'PwrState': 1}
        self._config_pvs_sp = {
            'PwrState': _PV(LL_PREF+self._name+':PwrState-Sel', **opt)}
        self._config_pvs_rb = {
            'PwrState': _PV(LL_PREF+self._name+':PwrState-Sts', **opt)}

    @property
    def state(self):
        """State."""
        # TODO: database of RF GEN
        pv = self._config_pvs_rb['PwrState']
        return pv.value == 1 if pv.connected else False

    @state.setter
    def state(self, boo):
        # TODO: database of RF GEN
        val = 1 if boo else 0
        pv = self._config_pvs_sp['PwrState']
        if pv.connected:
            self._config_ok_vals['PwrState'] = val
            pv.put(val, wait=False)


class CHCV(Corrector):
    """CHCV class."""

    def __init__(self, corr_name):
        """Init method."""
        super().__init__(corr_name)
        opt = {'connection_timeout': TIMEOUT}
        self._sp = _PV(LL_PREF + self._name + ':Current-SP', **opt)
        self._rb = _PV(LL_PREF + self._name + ':Current-RB', **opt)
        self._ref = _PV(LL_PREF + self._name + ':CurrentRef-Mon', **opt)
        self._config_ok_vals = {
            'OpMode': _PSConst.States.SlowRefSync,
            'PwrState': _PSConst.PwrStateSel.On}
        self._config_pvs_sp = {
            'OpMode': _PV(LL_PREF+self._name+':OpMode-Sel', **opt),
            'PwrState': _PV(LL_PREF+self._name+':PwrState-Sel', **opt)}
        self._config_pvs_rb = {
            'OpMode': _PV(LL_PREF+self._name+':OpMode-Sts', **opt),
            'PwrState': _PV(LL_PREF+self._name+':PwrState-Sts', **opt)}

    @property
    def opmode_ok(self):
        """Opmode ok status."""
        return self.opmode == self._config_ok_vals['OpMode']

    @property
    def opmode(self):
        """Opmode."""
        pv = self._config_pvs_rb['OpMode']
        return pv.value if pv.connected else None

    @opmode.setter
    def opmode(self, val):
        pv = self._config_pvs_sp['OpMode']
        if pv.connected:
            self._config_ok_vals['OpMode'] = val
            pv.put(val, wait=False)

    @property
    def connected(self):
        """Status connected."""
        conn = super().connected
        conn &= self._ref.connected
        if not self._ref.connected:
            _log.debug('NOT CONN: ' + self._ref.pvname)
        return conn

    @property
    def applied(self):
        """Status applied."""
        return self.equalKick(self._ref.value)


class TimingConfig(_BaseTimingConfig):
    """Timing configuration class."""

    def __init__(self, acc):
        """Init method."""
        super().__init__(acc)
        evt = self._csorb.EVT_COR_NAME
        pref_name = LL_PREF + self._csorb.EVG_NAME + ':' + evt
        trig = self._csorb.TRIGGER_COR_NAME
        opt = {'connection_timeout': TIMEOUT}
        self._evt_sender = _PV(pref_name + 'ExtTrig-Cmd', **opt)
        src_val = self._csorb.OrbitCorExtEvtSrc._fields.index(evt)
        src_val = self._csorb.OrbitCorExtEvtSrc[src_val]
        self._config_ok_vals = {
            'Mode': _TIConst.EvtModes.External,
            'Src': src_val,
            'Delay': 0.0,
            'NrPulses': 1, 'Duration': 0.1, 'State': 1, 'Polarity': 1,
            }
        if _HLTimesearch.has_delay_type(trig):
            self._config_ok_vals['RFDelayType'] = _TIConst.TrigDlyTyp.Manual
        pref_trig = LL_PREF + trig + ':'
        self._config_pvs_rb = {
            'Mode': _PV(pref_name + 'Mode-Sts', **opt),
            'Src': _PV(pref_trig + 'Src-Sts', **opt),
            'Delay': _PV(pref_trig + 'Delay-RB', **opt),
            'NrPulses': _PV(pref_trig + 'NrPulses-RB', **opt),
            'Duration': _PV(pref_trig + 'Duration-RB', **opt),
            'State': _PV(pref_trig + 'State-Sts', **opt),
            'Polarity': _PV(pref_trig + 'Polarity-Sts', **opt),
            }
        self._config_pvs_sp = {
            'Mode': _PV(pref_name + 'Mode-Sel', **opt),
            'Src': _PV(pref_trig + 'Src-Sel', **opt),
            'Delay': _PV(pref_trig + 'Delay-SP', **opt),
            'NrPulses': _PV(pref_trig + 'NrPulses-SP', **opt),
            'Duration': _PV(pref_trig + 'Duration-SP', **opt),
            'State': _PV(pref_trig + 'State-Sel', **opt),
            'Polarity': _PV(pref_trig + 'Polarity-Sel', **opt),
            }
        if _HLTimesearch.has_delay_type(trig):
            self._config_pvs_rb['RFDelayType'] = _PV(
                            pref_trig + 'RFDelayType-Sts', **opt)
            self._config_pvs_sp['RFDelayType'] = _PV(
                            pref_trig + 'RFDelayType-Sel', **opt)

    def send_evt(self):
        """Send event method."""
        self._evt_sender.value = 1

    @property
    def connected(self):
        """Status connected."""
        conn = super().connected
        conn &= self._evt_sender.connected
        if not self._evt_sender.connected:
            _log.debug('NOT CONN: ' + self._evt_sender.pvname)
        return conn


class BaseCorrectors(_BaseClass):
    """Base correctors class."""

    pass


class EpicsCorrectors(BaseCorrectors):
    """Class to deal with correctors."""

    TINY_INTERVAL = 0.005
    NUM_TIMEOUT = 1000

    def get_database(self):
        """Get the database of the class."""
        db = self._csorb.get_corrs_database()
        prop = 'fun_set_pv'
        db['ConfigCorrs-Cmd'][prop] = self.configure_correctors
        db['KickAcqRate-SP'][prop] = self.set_kick_acq_rate
        if self.isring:
            db['SyncKicks-Sel'][prop] = self.set_chcvs_mode
            db['NominalFreqRF-SP'][prop] = self.set_nominal_rf_freq
        db = super().get_database(db)
        return db

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)
        self._synced_kicks = True
        self._acq_rate = 10
        self._names = self._csorb.CH_NAMES + self._csorb.CV_NAMES
        self._chcvs = {CHCV(dev) for dev in self._names}
        if self.isring:
            self._rf_ctrl = RFCtrl(self.acc)
            self._rf_nom_freq = self._csorb.RF_NOM_FREQ
            self.timing = TimingConfig(acc)
        self._corrs_thread = _Repeat(
                1/self._acq_rate, self._update_corrs_strength, niter=0)
        self._corrs_thread.start()

    def apply_kicks(self, values):
        """Apply kicks."""
        strn = '    TIMEIT: {0:20s} - {1:7.3f}'
        # apply the RF kick
        _log.debug('    TIMEIT: BEGIN')
        t0 = _time.time()
        if self.isring:
            self.put_value_in_corr(
                self._rf_ctrl, values[-1] + self._rf_nom_freq, False)
        t1 = _time.time()
        _log.debug(strn.format('send rf:', 1000*(t1-t0)))

        # Send correctors setpoint
        for i, corr in enumerate(self._chcvs):
            self.put_value_in_corr(corr, values[i])
        t2 = _time.time()
        _log.debug(strn.format('send sp:', 1000*(t2-t1)))

        # Wait for readbacks to be updated
        if self._timed_out(mode='ready'):
            msg = 'ERR: timeout waiting correctors RB'
            self._update_log(msg)
            _log.error(msg[5:])
            return
        t3 = _time.time()
        _log.debug(strn.format('check ready:', 1000*(t3-t2)))

        # Send trigger signal for implementation
        # _time.sleep(0.450)
        self.send_evt()
        t4 = _time.time()
        _log.debug(strn.format('send evt:', 1000*(t4-t3)))

        # Wait for references to be updated
        if self._timed_out(mode='applied'):
            msg = 'ERR: timeout waiting correctors Ref'
            self._update_log(msg)
            _log.error(msg[5:])
        t5 = _time.time()
        _log.debug(strn.format('check applied:', 1000*(t5-t4)))
        _log.debug('    TIMEIT: END')

    def put_value_in_corr(self, corr, value, flag=True):
        """Put value in corrector method."""
        if not corr.connected:
            msg = 'ERR: ' + corr.name + ' not connected.'
            self._update_log(msg)
            _log.error(msg[5:])
        elif not corr.state:
            msg = 'ERR: ' + corr.name + ' is off.'
            self._update_log(msg)
            _log.error(msg[5:])
        elif flag and not corr.opmode_ok:
            msg = 'ERR: ' + corr.name + ' mode not configured.'
            self._update_log(msg)
            _log.error(msg[5:])
        elif not corr.equalKick(value):
            corr.value = value

    def send_evt(self):
        """Send event method."""
        if not self.isring and not self._synced_kicks:
            return
        if not self.timing.connected:
            msg = 'ERR: timing disconnected.'
            self._update_log(msg)
            _log.error(msg[5:])
            return
        elif not self.timing.is_ok:
            msg = 'ERR: timing not configured.'
            self._update_log(msg)
            _log.error(msg[5:])
            return
        self.timing.send_evt()

    def get_strength(self):
        """Get the correctors strengths."""
        corr_values = _np.zeros(self._csorb.NR_CORRS, dtype=float)
        for i, corr in enumerate(self._chcvs):
            if corr.connected:
                corr_values[i] = corr.value
        if self.isring and self._rf_ctrl.connected:
            corr_values[-1] = self._rf_ctrl.value - self._rf_nom_freq
        return corr_values

    def set_kick_acq_rate(self, value):
        """Set kick caq rate method."""
        self._acq_rate = value
        self._corrs_thread.interval = 1/value
        self.run_callbacks('KickAcqRate-RB', value)
        return True

    def set_nominal_rf_freq(self, value):
        """Set nominal RF frequency method."""
        self._rf_nom_freq = value

    def _update_corrs_strength(self):
        corr_vals = self.get_strength()
        self.run_callbacks('KicksCH-Mon', corr_vals[:self._csorb.NR_CH])
        self.run_callbacks(
            'KicksCV-Mon', corr_vals[self._csorb.NR_CH:self._csorb.NR_CHCV])
        if self.isring:
            self.run_callbacks('KicksRF-Mon', corr_vals[-1])

    def set_chcvs_mode(self, value):
        """Set mode of CHs and CVs method."""
        self._synced_kicks = value
        if self._synced_kicks == self._csorb.SyncKicks.On:
            val = _PSConst.OpMode.SlowRefSync
        elif self._synced_kicks == self._csorb.SyncKicks.Off:
            val = _PSConst.OpMode.SlowRef

        for corr in self._chcvs:
            if corr.connected:
                corr.opmode = val
            else:
                msg = 'ERR: Failed to configure correctors'
                self._update_log(msg)
                _log.error(msg[5:])
                return False
        msg = 'Correctors set to {0:s} Mode'.format(
                                    'Sync' if value else 'Async')
        self._update_log(msg)
        _log.info(msg)
        self.run_callbacks('SyncKicks-Sts', value)
        return True

    def configure_correctors(self, _):
        """Configure correctors method."""
        if self.isring and self._synced_kicks == self._csorb.SyncKicks.On:
            val = _PSConst.OpMode.SlowRefSync
        else:
            val = _PSConst.OpMode.SlowRef
        for corr in self._chcvs:
            if corr.connected:
                corr.state = True
                corr.opmode = val
            else:
                msg = 'ERR: Failed to configure correctors'
                self._update_log(msg)
                _log.error(msg[5:])
                return False
        if not self.isring:
            return True

        if not self.timing.configure():
            msg = 'ERR: Failed to configure timing'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        if self._rf_ctrl.connected:
            self._rf_ctrl.state = True
        else:
            msg = 'ERR: Failed to configure correctors'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        return True

    def _update_status(self):
        status = 0b1111111
        status = _util.update_bit(
            status, bit_pos=0,
            bit_val=not all(corr.connected for corr in self._chcvs))
        status = _util.update_bit(
            status, bit_pos=1,
            bit_val=not all(corr.opmode_ok for corr in self._chcvs))
        status = _util.update_bit(
            status, bit_pos=2,
            bit_val=not all(corr.state for corr in self._chcvs))
        if self.isring:
            status = _util.update_bit(
                status, bit_pos=3, bit_val=not self.timing.connected)
            status = _util.update_bit(
                status, bit_pos=4, bit_val=not self.timing.is_ok)
            status = _util.update_bit(
                status, bit_pos=5, bit_val=not self._rf_ctrl.connected)
            status = _util.update_bit(
                status, bit_pos=6, bit_val=not self._rf_ctrl.state)
        self._status = status
        self.run_callbacks('CorrStatus-Mon', status)

    def _timed_out(self, mode='ready'):
        corrs = list()
        corrs.extend(self._chcvs)
        if self.isring:
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
