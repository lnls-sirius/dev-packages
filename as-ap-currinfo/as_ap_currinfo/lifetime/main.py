"""Main Module of the IOC Logic."""

import time as _time
import numpy as _np
import epics as _epics
from siriuspy.epics import SiriusPVTimeSerie as _SiriusPVTimeSerie
from siriuspy.csdevice.currinfo import Const as _Const
import as_ap_currinfo.lifetime.pvs as _pvs

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be
#      easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive'
#      (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes,
#      suffixes, etc)


class App:
    """Main Class of the IOC Logic."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _pvs.print_banner()

        self._driver = driver
        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()
        self._PREFIX = _pvs.get_pvs_prefix()

        self._current_pv = _epics.PV(
            self._PREFIX+'Current-Mon',
            callback=self._callback_calclifetime)
        self._storedebeam_pv = _epics.PV(
            self._PREFIX+'StoredEBeam-Mon')
        self._injstate_pv = _epics.PV(
            self._PREFIX_VACA+'AS-RaMO:TI-EVG:InjectionEvt-Sts',
            callback=self._callback_get_injstate)

        self._mode = _Const.Fit.Exponential
        self._lifetime = 0
        self._rstbuff_cmd_count = 0
        self._buffautorst_mode = _Const.BuffAutoRst.Off
        if self._injstate_pv.connected:
            self._is_injecting = self._injstate_pv.value
            self._changeinjstate_timestamp = self._injstate_pv.timestamp
        else:
            self._is_injecting = 0
            self._changeinjstate_timestamp = _time.time() - 0.5
        self._dcurrfactor = 0.01
        self._sampling_time = 2000.0
        self._buffer_max_size = 1000
        self._current_buffer = _SiriusPVTimeSerie(
                               pv=self._current_pv,
                               time_window=self._sampling_time,
                               nr_max_points=None,
                               time_min_interval=0.0,
                               mode=0)

    @staticmethod
    def init_class():
        """Init class."""
        App.pvs_database = _pvs.get_pvs_database()

    @property
    def driver(self):
        """Return driver."""
        return self._driver

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        value = None
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'BuffSizeMax-SP':
            self._update_buffsizemax(value)
            self.driver.setParam('BuffSizeMax-RB', self._buffer_max_size)
            self.driver.updatePV('BuffSizeMax-RB')
            status = True
        elif reason == 'SplIntvl-SP':
            self._update_splintvl(value)
            self.driver.setParam('SplIntvl-RB', self._sampling_time)
            self.driver.updatePV('SplIntvl-RB')
            status = True
        elif reason == 'BuffRst-Cmd':
            self._clear_buffer()
            self._rstbuff_cmd_count += 1
            self.driver.setParam('BuffRst-Cmd', self._rstbuff_cmd_count)
            self.driver.updatePV('BuffRst-Cmd')
            status = True
        elif reason == 'BuffAutoRst-Sel':
            self._update_buffautorst_mode(value)
            self.driver.setParam('BuffAutoRst-Sts', self._buffautorst_mode)
            self.driver.updatePVs()
            status = True
        elif reason == 'LtFitMode-Sel':
            self._mode = value
            self.driver.setParam('LtFitMode-Sts', value)
            self.driver.updatePV('LtFitMode-Sts')
            status = True
        return status

    def _update_buffsizemax(self, value):
        if value < 1:
            self._buffer_max_size = 0
            self._current_buffer.nr_max_points = None
        else:
            self._buffer_max_size = value
            self._current_buffer.nr_max_points = value

    def _update_splintvl(self, value):
        self._sampling_time = value
        self._current_buffer.time_window = value

    def _clear_buffer(self):
        self._current_buffer.clearserie()

    def _update_buffautorst_mode(self, value):
        if self._buffautorst_mode != value:
            self._buffautorst_mode = value

    def _callback_calclifetime(self, timestamp, **kws):
        self._dtime_lastchangeinjstate = (timestamp -
                                          self._changeinjstate_timestamp)

        def _lsf_exponential(_timestamp, _value):
            timestamp = _np.array(_timestamp)
            value = _np.array(_value)
            value = _np.log(value)
            n = len(_timestamp)
            x = _np.sum(timestamp)
            y = _np.sum(value)
            x2 = _np.sum(_np.power(timestamp, 2))
            xy = _np.sum(timestamp*value)
            b = (n*xy - x*y)/(n*x2 - x*x)
            lt = - 1/b
            return lt

        def _lsf_linear(_timestamp, _value):
            timestamp = _np.array(_timestamp)
            value = _np.array(_value)
            n = len(_value)

            # for exponential fit
            timestamp_exp = timestamp
            value_exp = _np.log(value)
            x = _np.sum(timestamp_exp)
            y = _np.sum(value_exp)
            x2 = _np.sum(_np.power(timestamp_exp, 2))
            xy = _np.sum(timestamp_exp*value_exp)
            a = _np.exp((x2*y - xy*x)/(n*x2 - x*x))

            # for linear fit
            timestamp_lin = timestamp - _np.mean(timestamp)
            value_lin = value - _np.mean(value)
            x2 = _np.sum(_np.power(timestamp_lin, 2))
            xy = _np.sum(timestamp_lin*value_lin)
            b = xy/x2

            lt = - a/b
            return lt

        fun = _lsf_exponential if self._mode == _Const.Fit.Exponential \
            else _lsf_linear

        acquireflag = self._current_buffer.acquire()
        if acquireflag:
            if self._buffautorst_mode != _Const.BuffAutoRst.Off:
                self._buffautorst_check()

            # Check min number of points in buffer to calculate lifetime
            [timestamp, value] = self._current_buffer.serie
            if self._buffer_max_size > 0:
                if len(value) > min(20, self._buffer_max_size/2):
                    self._lifetime = fun(timestamp, value)
            else:
                if len(value) > 20:
                    self._lifetime = fun(timestamp, value)

            self.driver.setParam('Lifetime-Mon', self._lifetime)
            self.driver.updatePV('Lifetime-Mon')
            self.driver.setParam('BuffSize-Mon', len(value))
            self.driver.updatePV('BuffSize-Mon')

    def _buffautorst_check(self):
        """Choose mode and check situations to clear internal buffer.

        PVsTrig Mode: Check if there is EBeam and check injection activity
        with minimum increase of current of 300uA (=0.3mA).
        DCurrCheck Mode: Check abrupt variation of current by a factor of 35
        times the dcct fluctuation/resolution.
        """
        [timestamp, value] = self._current_buffer.serie
        if self._buffautorst_mode == _Const.BuffAutoRst.PVsTrig:
            if (self._storedebeam_pv.connected and
                    self._storedebeam_pv.value == 0):
                self._current_buffer.clearserie()
                self._lifetime = 0
            elif ((self._is_injecting == 1 or
                   self._dtime_lastchangeinjstate < 1) and
                  (len(value) >= 2 and
                   (abs(value[-1] - value[-2]) > 0.1))):
                self._current_buffer.clearserie()
        elif self._buffautorst_mode == _Const.BuffAutoRst.DCurrCheck:
            if (len(value) >= 2 and
                    abs(value[-1] - value[-2]) > 100*self._dcurrfactor):
                self._current_buffer.clearserie()

    def _callback_get_injstate(self, value, timestamp, **kws):
        if value == 1:
            self._is_injecting = 1
        else:
            self._changeinjstate_timestamp = timestamp
            self._is_injecting = 0
