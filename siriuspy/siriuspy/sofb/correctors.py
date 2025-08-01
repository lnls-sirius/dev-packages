"""Module to deal with correctors."""

import logging as _log
import time as _time
import traceback as _traceback

import numpy as _np

from .. import util as _util
from ..epics import PV as _PV
from ..thread import RepeaterThread as _Repeat
from ..pwrsupply.csdev import Const as _PSConst
from ..timesys.csdev import Const as _TIConst
from ..search import HLTimeSearch as _HLTimesearch
from ..envars import VACA_PREFIX as LL_PREF
from ..namesys import SiriusPVName as _PVName

from .base_class import BaseClass as _BaseClass, \
    BaseTimingConfig as _BaseTimingConfig, compare_kicks as _compare_kicks

TIMEOUT = 0.05
WAIT_CORRS = False


class Corrector(_BaseTimingConfig):
    """Corrector class."""

    def __init__(self, corr_name):
        """Init method."""
        super().__init__(corr_name[:2])
        self._name = _PVName(corr_name)
        self._pvs['sp'] = None
        self._pvs['rb'] = None

    @property
    def name(self):
        """Corrector name."""
        return self._name

    @property
    def opmode_ok(self):
        """Opmode ok status."""
        return self.connected

    @property
    def opmode(self):
        """Opmode."""
        return 1

    @opmode.setter
    def opmode(self, val):
        """."""

    @property
    def state(self):
        """State."""
        pv = self._config_pvs_rb["PwrState"]
        return pv.value == _PSConst.PwrStateSel.On if pv.connected else False

    @state.setter
    def state(self, boo):
        """."""
        val = _PSConst.PwrStateSel.On if boo else _PSConst.PwrStateSel.Off
        pv = self._config_pvs_sp["PwrState"]
        self._config_ok_vals["PwrState"] = val
        if self.put_enable and pv.connected:
            pv.put(val, wait=False)

    @property
    def value(self):
        """Value."""
        if self._pvs['rb'].connected:
            return self._pvs['rb'].value

    @value.setter
    def value(self, val):
        """."""
        self._pvs['sp'].put(val, wait=False)

    @property
    def refvalue(self):
        """."""
        return self.value


class RFCtrl(Corrector):
    """RF control class."""

    TINY_VAR = 0.01  # [Hz]
    LARGE_VAR = 10000  # [Hz]
    MAX_DELTA = 200  # [Hz]

    def __init__(self, acc):
        """Init method."""
        super().__init__(acc)
        self._name = self._csorb.RF_GEN_NAME
        opt = {"connection_timeout": TIMEOUT}
        pvpref = LL_PREF + ("-" if LL_PREF else "") + self._name
        self._pvs['sp'] = _PV(pvpref + ":GeneralFreq-SP", **opt)
        self._pvs['rb'] = _PV(pvpref + ":GeneralFreq-RB", **opt)
        self._config_ok_vals = {"PwrState": 1}
        self._config_pvs_sp = dict()
        self._config_pvs_rb = dict()

    @property
    def value(self):
        """Value."""
        if self._pvs['rb'].connected:
            return self._pvs['rb'].value

    @value.setter
    def value(self, freq):
        """."""
        freq0 = self.value
        if freq0 is None or freq is None:
            return
        delta = abs(freq - freq0)
        if delta < self.TINY_VAR or delta > self.LARGE_VAR:
            return
        npoints = int(delta // self.MAX_DELTA) + 2
        freq_span = _np.linspace(freq0, freq, npoints)[1:]
        for i, freq in enumerate(freq_span, 1):
            self._pvs['sp'].put(freq, wait=False)
            if i != freq_span.size:
                _time.sleep(1)

    @property
    def state(self):
        """State."""
        return True

    @state.setter
    def state(self, boo):
        """."""
        return


class CHCV(Corrector):
    """CHCV class."""

    def __init__(self, corr_name):
        """Init method."""
        super().__init__(corr_name)
        opt = {"connection_timeout": TIMEOUT}
        pvsp = self._name.substitute(
            prefix=LL_PREF, propty_name="Kick", propty_suffix="SP"
        )
        pvrb = pvsp.substitute(propty_suffix="RB")
        pvref = pvsp.substitute(propty_name="KickRef", propty_suffix="Mon")
        self._pvs['sp'] = _PV(pvsp, **opt)
        self._pvs['rb'] = _PV(pvrb, **opt)
        self._pvs['ref'] = _PV(pvref, **opt)

        pvoffwfmsp = self._name.substitute(
            prefix=LL_PREF, propty_name='WfmOffsetKick', propty_suffix='SP')
        pvoffwfmrb = self._name.substitute(
            prefix=LL_PREF, propty_name='WfmOffsetKick', propty_suffix='RB')
        self._pvs['wfm_offset_sp'] = _PV(pvoffwfmsp)
        self._pvs['wfm_offset_rb'] = _PV(pvoffwfmrb)
        self._config_ok_vals = {
            'OpMode': _PSConst.OpMode.SlowRef,
            'PwrState': _PSConst.PwrStateSel.On}
        pvpref = self._name.substitute(prefix=LL_PREF)
        self._config_pvs_sp = {
            'OpMode': _PV(pvpref.substitute(propty='OpMode-Sel'), **opt),
            'PwrState': _PV(pvpref.substitute(propty='PwrState-Sel'), **opt)}
        self._config_pvs_rb = {
            'OpMode': _PV(pvpref.substitute(propty='OpMode-Sts'), **opt),
            'PwrState': _PV(pvpref.substitute(propty='PwrState-Sts'), **opt)}

    @property
    def opmode_ok(self):
        """Opmode ok status."""
        isok = self.opmode == self._config_ok_vals["OpMode"]
        if not isok:
            msg = "OpMode not Ok {0:s}".format(self.name)
            _log.warning(msg)
        return isok

    @property
    def opmode(self):
        """Opmode."""
        pvobj = self._config_pvs_rb["OpMode"]
        if not pvobj.connected:
            return None
        elif pvobj.value == _PSConst.States.SlowRefSync:
            return _PSConst.OpMode.SlowRefSync
        elif pvobj.value == _PSConst.States.SlowRef:
            return _PSConst.OpMode.SlowRef
        elif pvobj.value == _PSConst.States.RmpWfm:
            return _PSConst.OpMode.RmpWfm
        return pvobj.value

    @opmode.setter
    def opmode(self, val):
        """."""
        pvobj = self._config_pvs_sp["OpMode"]
        self._config_ok_vals["OpMode"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def value(self):
        """Value."""
        if not self._pvs['rb'].connected:
            return None
        if self._config_ok_vals['OpMode'] == _PSConst.OpMode.RmpWfm:
            return self.wfm_offset_kick
        return self._pvs['rb'].value

    @value.setter
    def value(self, val):
        """."""
        if self._config_ok_vals['OpMode'] == _PSConst.OpMode.RmpWfm:
            self.wfm_offset_kick = val
        else:
            self._pvs['sp'].put(val, wait=False)

    @property
    def wfm_offset_kick(self):
        """."""
        if not self._pvs['wfm_offset_rb'].connected:
            return None
        return self._pvs['wfm_offset_rb'].value

    @wfm_offset_kick.setter
    def wfm_offset_kick(self, val):
        """."""
        self._pvs['wfm_offset_sp'].put(val, wait=False)

    @property
    def refvalue(self):
        """."""
        if not self._pvs['ref'].connected:
            return None
        if self._config_ok_vals['OpMode'] == _PSConst.OpMode.RmpWfm:
            return self.wfm_offset_kick
        return self._pvs['ref'].value

    def configure(self):
        """Configure method."""
        if not self.connected:
            return False

        if not self.put_enable:
            return True
        for k, pvo in self._config_pvs_sp.items():
            if k in self._config_ok_vals:
                pvo.put(self._config_ok_vals[k], wait=False)
        return True


class Septum(Corrector):
    """Septum class."""

    def __init__(self, corr_name):
        """Init method."""
        super().__init__(corr_name)
        opt = {"connection_timeout": TIMEOUT}
        pvsp = self._name.substitute(
            prefix=LL_PREF, propty_name="Kick", propty_suffix="SP"
        )
        pvrb = pvsp.substitute(propty_suffix="RB")
        self._pvs['sp'] = _PV(pvsp, **opt)
        self._pvs['rb'] = _PV(pvrb, **opt)
        self._nominalkick = 98.55  # mrad
        self._config_ok_vals = {
            "Pulse": 1,
            "PwrState": _PSConst.PwrStateSel.On,
        }
        pvpref = self._name.substitute(prefix=LL_PREF)
        self._config_pvs_sp = {
            "Pulse": _PV(pvpref.substitute(propty="Pulse-Sel"), **opt),
            "PwrState": _PV(pvpref.substitute(propty="PwrState-Sel"), **opt),
        }
        self._config_pvs_rb = {
            "Pulse": _PV(pvpref.substitute(propty="Pulse-Sts"), **opt),
            "PwrState": _PV(pvpref.substitute(propty="PwrState-Sts"), **opt),
        }

    @property
    def opmode_ok(self):
        """Opmode ok status."""
        return self.opmode == self._config_ok_vals["Pulse"]

    @property
    def opmode(self):
        """Opmode."""
        pv = self._config_pvs_rb["Pulse"]
        if not pv.connected:
            return None
        return pv.value

    @opmode.setter
    def opmode(self, val):
        """."""
        pv = self._config_pvs_sp["Pulse"]
        self._config_ok_vals["Pulse"] = val
        if self.put_enable and pv.connected and pv.value != val:
            pv.put(val, wait=False)

    @property
    def value(self):
        """Value."""
        if self._pvs['rb'].connected:
            val = self._pvs['rb'].value
            if val is not None:
                return -(val + self._nominalkick) * 1e3

    @value.setter
    def value(self, val):
        """."""
        val = val / 1e3 + self._nominalkick
        self._pvs['sp'].put(-val, wait=False)


def get_corr(name):
    """."""
    if name.dis == "PU":
        return Septum(name)
    else:
        return CHCV(name)


class TimingConfig(_BaseTimingConfig):
    """Timing configuration class."""

    def __init__(self, acc):
        """Init method."""
        super().__init__(acc)
        evt = self._csorb.evt_cor_name
        pref = LL_PREF + ("-" if LL_PREF else "")
        pref_name = pref + self._csorb.evg_name + ":" + evt
        trig = self._csorb.trigger_cor_name
        opt = {"connection_timeout": TIMEOUT}
        self._pvs['evt_sender'] = _PV(pref_name + "ExtTrig-Cmd", **opt)
        src_val = self._csorb.CorrExtEvtSrc._fields.index(evt)
        src_val = self._csorb.CorrExtEvtSrc[src_val]
        self.EVT = src_val

        src_val = self._csorb.CorrExtEvtSrc._fields.index(
            self._csorb.evt_rmpbo
        )
        src_val = self._csorb.CorrExtEvtSrc[src_val]
        self.RMPBO = src_val

        src_val = self._csorb.CorrExtEvtSrc._fields.index(
            self._csorb.clk_cor_name
        )
        src_val = self._csorb.CorrExtEvtSrc[src_val]
        self.CLK = src_val

        self._config_ok_vals = {
            "Mode": _TIConst.EvtModes.External,
            "Src": src_val,
            "NrPulses": 1,
            "Duration": 150.0,
            "State": 1,
            "Polarity": 0,
        }
        if _HLTimesearch.has_delay_type(trig):
            self._config_ok_vals["RFDelayType"] = _TIConst.TrigDlyTyp.Manual
        pref_trig = pref + trig + ":"
        self._config_pvs_rb = {
            "Mode": _PV(pref_name + "Mode-Sts", **opt),
            "Src": _PV(pref_trig + "Src-Sts", **opt),
            "DelayRaw": _PV(pref_trig + "DelayRaw-RB", **opt),
            "DeltaDelayRaw": _PV(pref_trig + "DeltaDelayRaw-RB", **opt),
            "NrPulses": _PV(pref_trig + "NrPulses-RB", **opt),
            "Duration": _PV(pref_trig + "Duration-RB", **opt),
            "State": _PV(pref_trig + "State-Sts", **opt),
            "Polarity": _PV(pref_trig + "Polarity-Sts", **opt),
        }
        self._config_pvs_sp = {
            "Mode": _PV(pref_name + "Mode-Sel", **opt),
            "Src": _PV(pref_trig + "Src-Sel", **opt),
            "DelayRaw": _PV(pref_trig + "DelayRaw-SP", **opt),
            "DeltaDelayRaw": _PV(pref_trig + "DeltaDelayRaw-SP", **opt),
            "NrPulses": _PV(pref_trig + "NrPulses-SP", **opt),
            "Duration": _PV(pref_trig + "Duration-SP", **opt),
            "State": _PV(pref_trig + "State-Sel", **opt),
            "Polarity": _PV(pref_trig + "Polarity-Sel", **opt),
        }
        if _HLTimesearch.has_delay_type(trig):
            self._config_pvs_rb["RFDelayType"] = _PV(
                pref_trig + "RFDelayType-Sts", **opt
            )
            self._config_pvs_sp["RFDelayType"] = _PV(
                pref_trig + "RFDelayType-Sel", **opt
            )

    def send_evt(self):
        """Send event method."""
        self._pvs['evt_sender'].value = 1

    @property
    def state(self):
        """State."""
        pv = self._config_pvs_rb['State']
        return pv.value if pv.connected else 0

    @state.setter
    def state(self, val):
        """."""
        pv = self._config_pvs_sp['State']
        self._config_ok_vals['State'] = val
        if self.put_enable and pv.connected:
            pv.put(val, wait=False)

    @property
    def sync_type(self):
        """."""
        return self._config_pvs_rb["Src"].value

    @sync_type.setter
    def sync_type(self, value):
        """."""
        if value not in (self.EVT, self.CLK, self.RMPBO):
            return
        self._config_ok_vals["Src"] = value
        pvobj = self._config_pvs_sp["Src"]
        if self.put_enable and pvobj.connected:
            pvobj.value = value

    @property
    def delayraw(self):
        """."""
        defv = 0
        pvobj = self._config_pvs_rb["DelayRaw"]
        val = pvobj.value if pvobj.connected else defv
        return val if val else defv

    @delayraw.setter
    def delayraw(self, value):
        """."""
        # Make sure Delta Delay is zero:
        pvobj = self._config_pvs_sp["DeltaDelayRaw"]
        if self.put_enable and pvobj.connected:
            pvobj.value *= 0

        pvobj = self._config_pvs_sp["DelayRaw"]
        if self.put_enable and pvobj.connected:
            pvobj.value = int(value)


class BaseCorrectors(_BaseClass):
    """Base correctors class."""


class EpicsCorrectors(BaseCorrectors):
    """Class to deal with correctors."""

    TINY_INTERVAL = 0.005
    NUM_TIMEOUT = 1000
    MAX_PROB = 5
    ACQRATE = 2

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)
        self._sofb = None

        self._names = self._csorb.ch_names + self._csorb.cv_names
        self._corrs = [get_corr(dev) for dev in self._names]
        if self.isring:
            self._corrs.append(RFCtrl(self.acc))

        if self.acc == 'SI':
            self.sync_kicks = self._csorb.CorrSync.Off
            self.timing = TimingConfig(acc)
        self._corrs_thread = _Repeat(
            1 / self.ACQRATE, self._update_corrs_strength, niter=0
        )
        self._corrs_thread.start()

    @property
    def connected(self):
        """."""
        for cor in self._corrs:
            if not cor.connected:
                return False
        if self.acc == 'SI' and not self.timing.connected:
            return False
        return True

    @property
    def sofb(self):
        """."""
        return self._sofb

    @sofb.setter
    def sofb(self, sofb):
        self._sofb = sofb

    @property
    def corrs(self):
        """."""
        return self._corrs

    def wait_for_connection(self, timeout=10):
        """."""
        t0_ = _time.time()
        for cor in self._corrs:
            tout = timeout - (_time.time() - t0_)
            if tout <= 0 or not cor.wait_for_connection(tout):
                return False
        if self.acc != 'SI':
            return True
        tout = timeout - (_time.time() - t0_)
        if tout <= 0 or not self.timing.wait_for_connection(tout):
            return False
        return True

    def shutdown(self):
        """Shutdown threads."""
        self._corrs_thread.resume()
        self._corrs_thread.stop()
        self._corrs_thread.join()

    def get_map2write(self):
        """Get the write methods of the class."""
        dbase = {"CorrConfig-Cmd": self.configure_correctors}
        if self.acc == "SI":
            dbase["CorrSync-Sel"] = self.set_corrs_mode
        return dbase

    def apply_kicks(self, values):
        """Apply kicks.

        Will return -2 if there is a problem with some PS.
        Will return -1 if PS did not finish applying last kick.
        Will return 0 if all previous kick were implemented.
        Will return >0 indicating how many previous kicks were not implemented.
        """
        if self.acc == "BO":
            msg = "ERR: Cannot correct Orbit in Booster. Use Ramp Interface!"
            self._update_log(msg)
            _log.error(msg[5:])
            return 0

        strn = '    TIMEIT: {0:20s} - {1:7.3f}'
        _log.debug('    TIMEIT: BEGIN')
        time1 = _time.time()

        not_nan_idcs = ~_np.isnan(values)
        # Send correctors setpoint
        for i, corr in enumerate(self._corrs):
            if not_nan_idcs[i]:
                self.put_value_in_corr(corr, values[i])
        time2 = _time.time()
        _log.debug(strn.format('send sp:', 1000*(time2-time1)))

        # Wait for readbacks to be updated
        if WAIT_CORRS and self._timed_out(values, mode='ready'):
            return -1
        time3 = _time.time()
        _log.debug(strn.format('check ready:', 1000*(time3-time2)))

        # Send trigger signal for implementation
        self.send_evt()
        time4 = _time.time()
        _log.debug(strn.format('send evt:', 1000*(time4-time3)))

        # Wait for references to be updated
        if WAIT_CORRS:
            self._timed_out(values, mode='applied')
        time5 = _time.time()
        _log.debug(strn.format('check applied:', 1000*(time5-time4)))
        _log.debug('    TIMEIT: END')
        return 0

    def put_value_in_corr(self, corr, value):
        """Put value in corrector method."""
        if not corr.connected:
            msg = "ERR: " + corr.name + " not connected."
            self._update_log(msg)
            _log.error(msg[5:])
        elif not corr.state:
            msg = "ERR: " + corr.name + " is off."
            self._update_log(msg)
            _log.error(msg[5:])
        elif not corr.opmode_ok:
            msg = "ERR: " + corr.name + " mode not configured."
            self._update_log(msg)
            _log.error(msg[5:])
        else:
            corr.value = value

    def send_evt(self):
        """Send event method."""
        if self.acc != "SI" or self.sync_kicks != self._csorb.CorrSync.Event:
            return
        if not self.timing.connected:
            msg = "ERR: timing disconnected."
            self._update_log(msg)
            _log.error(msg[5:])
            return
        elif not self.timing.is_ok:
            msg = "ERR: timing not configured."
            self._update_log(msg)
            _log.error(msg[5:])
            return
        self.timing.send_evt()

    def get_strength(self):
        """Get the correctors strengths."""
        corr_values = _np.zeros(self._csorb.nr_corrs, dtype=float)

        for i, corr in enumerate(self._corrs):
            if corr.connected and corr.value is not None:
                corr_values[i] = corr.refvalue
            else:
                msg = "ERR: Failed to get value from "
                msg += corr.name
                self._update_log(msg)
                _log.error(msg[5:])
        return corr_values

    def _update_corrs_strength(self):
        try:
            corr_vals = self.get_strength()
            self.run_callbacks("KickCH-Mon", corr_vals[: self._csorb.nr_ch])
            self.run_callbacks(
                "KickCV-Mon",
                corr_vals[self._csorb.nr_ch : self._csorb.nr_chcv],
            )
            if self.isring and corr_vals[-1] > 0:
                # NOTE: I have to check whether the RF frequency is larger
                # than zero not to take the inverse of 0. It will be 0 in case
                # there is a failure to get the RF frequency from its PV.
                rfv = corr_vals[-1]
                circ = 1 / rfv * self._csorb.harm_number * 299792458
                self.run_callbacks("KickRF-Mon", rfv)
                self.run_callbacks("OrbLength-Mon", circ)
        except Exception as err:
            self._update_log("ERR: " + str(err))
            _log.error(_traceback.format_exc())

    def set_corrs_mode(self, value):
        """Set mode of CHs and CVs method. Only called when acc==SI."""
        if value not in self._csorb.CorrSync:
            return False

        self.timing.state = 0
        self.sync_kicks = value
        refs = [c.value for c in self._corrs[:-1]]
        val = _PSConst.OpMode.SlowRefSync
        if value == self._csorb.CorrSync.Off:
            self.set_timing_delay(0)
            val = _PSConst.OpMode.SlowRef
        elif value == self._csorb.CorrSync.Event:
            self.set_timing_delay(0)
            self.timing.sync_type = self.timing.EVT
        elif value == self._csorb.CorrSync.Clock:
            self.set_timing_delay(self._csorb.CORR_DEF_DELAY)
            self.timing.sync_type = self.timing.CLK
        elif value == self._csorb.CorrSync.RmpBO:
            self.set_timing_delay(0)
            self.timing.sync_type = self.timing.RMPBO
            val = _PSConst.OpMode.RmpWfm

        # Time to wait any waveform to finish
        _time.sleep(0.6)

        mask = self._get_mask()
        for i, corr in enumerate(self._corrs[:-1]):
            if mask[i] and not corr.connected:
                msg = "ERR: Failed to configure "
                msg += corr.name
                self._update_log(msg)
                _log.error(msg[5:])
                return False
            corr.put_enable = mask[i]
            corr.opmode = val
            corr.value = refs[i]

        self.timing.state = 1
        strsync = self._csorb.CorrSync._fields[self.sync_kicks]
        msg = "Synchronization set to {0:s}".format(strsync)
        self._update_log(msg)
        _log.info(msg)
        self.run_callbacks("CorrSync-Sts", value)
        return True

    def set_timing_delay(self, value):
        """."""
        frf = 499666 / 4  # [kHz]
        raw = int(value * frf)
        self.timing.delayraw = raw
        return True

    def configure_correctors(self, val):
        """Configure correctors method."""
        _ = val
        corrs = self._get_used_corrs(include_rf=True)
        for corr in corrs:
            if not corr.connected:
                msg = "ERR: Failed to configure "
                msg += corr.name
                self._update_log(msg)
                _log.error(msg[5:])
                continue
            # Do not configure opmode in BO corrs because they are ramping.
            if self.acc == "BO":
                corr.state = True
                continue
            corr.configure()
        if not self.isring:
            return True
        if self.acc == "SI" and self.sync_kicks != self._csorb.CorrSync.Off:
            if not self.timing.configure():
                msg = "ERR: Failed to configure timing"
                self._update_log(msg)
                _log.error(msg[5:])
        return True

    def _update_status(self):
        status = 0b0000111
        if self.acc == "SI":
            status = 0b1111111
        elif self.isring:
            status = 0b0011111

        chcvs = self._get_used_corrs(include_rf=False)

        status = _util.update_bit(
            status,
            bit_pos=0,
            bit_val=not all(corr.connected for corr in chcvs),
        )
        # Do not check mode of BO correctors because they are ramping.
        opmode_ok = True
        if self.acc != "BO":
            opmode_ok = all(corr.opmode_ok for corr in chcvs)
        status = _util.update_bit(status, bit_pos=1, bit_val=not opmode_ok)
        status = _util.update_bit(
            status, bit_pos=2, bit_val=not all(corr.state for corr in chcvs)
        )
        if self.acc == "SI" and self.sync_kicks != self._csorb.CorrSync.Off:
            tim_conn = self.timing.connected
            tim_conf = self.timing.is_ok
        else:
            tim_conn = tim_conf = True
        status = _util.update_bit(status, bit_pos=3, bit_val=not tim_conn)
        status = _util.update_bit(status, bit_pos=4, bit_val=not tim_conf)
        if self.isring:
            rfctrl = self._corrs[-1]
            status = _util.update_bit(
                status, bit_pos=5, bit_val=not rfctrl.connected
            )
            status = _util.update_bit(
                status, bit_pos=6, bit_val=not rfctrl.state
            )
        self._status = status
        self.run_callbacks("CorrStatus-Mon", status)

    def _timed_out(self, values, mode="ready"):
        okg = [False] * len(self._corrs)
        for _ in range(self.NUM_TIMEOUT):
            for i, corr in enumerate(self._corrs):
                if okg[i]:
                    continue
                if _np.isnan(values[i]):
                    okg[i] = True
                    continue
                val = corr.value if mode == "ready" else corr.refvalue
                if val is None:
                    continue
                if isinstance(corr, RFCtrl):
                    okg[i] = _compare_kicks(
                        values[i], val, atol=RFCtrl.TINY_VAR
                    )
                else:
                    okg[i] = _compare_kicks(values[i], val)
            if all(okg):
                return False
            _time.sleep(self.TINY_INTERVAL)

        self._print_guilty(okg, mode=mode)
        return True

    def _print_guilty(
        self, okg, mode="ready", fret=None, currs=None, refs=None
    ):
        msg_tmpl = "ERR: timeout {0:3s}: {1:s}"
        data = [tuple()] * len(self._corrs)
        if mode == "prob_code":
            msg_tmpl = "ERR: {0:s} --> {1:s}: code={2:d}"
            data = zip(fret)
        elif mode == "prob_curr":
            msg_tmpl = "ERR: {0:s} --> {1:s}: curr={2:.4g}, ref={3:.4g}"
            data = zip(currs, refs)
        elif mode == "diff":
            msg_tmpl = "ERR: Corrector {1:s} diff from setpoint!"
        for oki, corr, args in zip(okg, self._corrs, data):
            if not oki:
                msg = msg_tmpl.format(mode, corr.name, *args)
                self._update_log(msg)
                _log.error(msg[5:])

    def _get_mask(self):
        if self.sofb is not None and self.sofb.matrix is not None:
            mask = self.sofb.matrix.corrs_enbllist
        else:
            mask = _np.ones(len(self._corrs), dtype=bool)
        return mask

    def _get_used_corrs(self, include_rf=False):
        corrs = []
        nrc = None if include_rf else self._csorb.nr_chcv
        mask = self._get_mask()[:nrc]
        for i, corr in enumerate(self._corrs[:nrc]):
            corr.put_enable = mask[i]
            if mask[i]:
                corrs.append(corr)
        return corrs
