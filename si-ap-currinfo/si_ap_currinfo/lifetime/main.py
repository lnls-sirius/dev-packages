"""Main Module of the IOC Logic."""

import time as _time
import numpy as _numpy
import epics as _epics
import siriuspy as _siriuspy
import siriuspy.envars as _siriuspy_envars
import siriuspy.epics as _siriuspy_epics
import siriuspy.util as _siriuspy_util
import si_ap_currinfo.lifetime.pvs as _pvs

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

__version__ = _pvs._COMMIT_HASH
_ioc_prefix = _siriuspy_envars.vaca_prefix


class App:
    """Main Class of the IOC Logic."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _siriuspy_util.print_ioc_banner(
            ioc_name='si-ap-currinfo-lifetime',
            db=App.pvs_database,
            description='SI-AP-CurrInfo-Lifetime Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX)
        _siriuspy.util.save_ioc_pv_list('si-ap-currinfo-lifetime',
                                        (_pvs._DEVICE,
                                         _pvs._PREFIX_VACA),
                                        App.pvs_database)
        self._driver = driver
        self._pvs_database = App.pvs_database

        self._current_pv = _epics.PV(
            _ioc_prefix + 'SI-Glob:AP-CurrInfo:Current-Mon',
            connection_timeout=0.05)
        self._storedebeam_pv = _epics.PV(
            _ioc_prefix + 'SI-Glob:AP-CurrInfo:StoredEBeam-Mon')
        self._storedebeam_pv.wait_for_connection(timeout=0.05)
        self._injstate_pv = _epics.PV(
            _ioc_prefix + 'AS-Glob:TI-EVG:InjectionState-Sts',
            connection_timeout=0.05)

        self._lifetime = 0
        self._rstbuff_cmd_count = 0
        self._buffautorst_mode = 0
        if self._injstate_pv.connected:
            self._is_injecting = self._injstate_pv.value
            self._changeinjstate_timestamp = self._injstate_pv.timestamp
        else:
            self._is_injecting = 0
            self._changeinjstate_timestamp = _time.time() - 0.5
        self._dcurrfactor = 0.01
        self._sampling_time = 10.0
        self._buffer_max_size = 0
        self._current_buffer = _siriuspy_epics.SiriusPVTimeSerie(
                               pv=self._current_pv,
                               time_window=self._sampling_time,
                               nr_max_points=None,
                               time_min_interval=0.0,
                               mode=0)

        self._injstate_pv.add_callback(self._callback_get_injstate)
        self._current_pv.add_callback(self._callback_calclifetime)

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
            self.driver.updatePVs()
            status = True
        elif reason == 'SplIntvl-SP':
            self._update_splintvl(value)
            self.driver.setParam('SplIntvl-RB', self._sampling_time)
            self.driver.updatePVs()
            status = True
        elif reason == 'BuffRst-Cmd':
            self._rstbuff_cmd_count += 1
            self.driver.setParam('BuffRst-Cmd', self._rstbuff_cmd_count)
            self._clear_buffer()
        elif reason == 'BuffAutoRst-Sel':
            self._update_buffautorst_mode(value)
            self.driver.setParam('BuffAutoRst-Sts', self._buffautorst_mode)
            self.driver.updatePVs()
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
            timestamp = _numpy.array(_timestamp)
            value = _numpy.array(_value)
            value = _numpy.log(value)
            n = len(_timestamp)
            x = _numpy.sum(timestamp)
            x2 = _numpy.sum(_numpy.power(timestamp, 2))
            y = _numpy.sum(value)
            xy = _numpy.sum(timestamp*value)
            b = -(n*x2 - x*x)/(n*xy - x*y)
            # a  = _numpy.exp((x2*y - xy*x)/(n*x2 - x*x))
            # model = a*_numpy.exp(timestamp*b)
            return b

        acquireflag = self._current_buffer.acquire()
        if acquireflag:
            if self._buffautorst_mode != 2:
                self._buffautorst_check()

            # Check min number of points in buffer to calculate lifetime
            [timestamp, value] = self._current_buffer.serie
            if self._buffer_max_size > 0:
                if len(value) > min(20, self._buffer_max_size/2):
                    self._lifetime = _lsf_exponential(timestamp, value)
            else:
                if len(value) > 20:
                    self._lifetime = _lsf_exponential(timestamp, value)

            self.driver.setParam('Lifetime-Mon', self._lifetime)
            self.driver.setParam('BuffSize-Mon', len(value))
            self.driver.updatePVs()

    def _buffautorst_check(self):
        """Choose mode and check situations to clear internal buffer.

        PVsTrig Mode: Check if there is EBeam and check injection activity
        with minimum increase of current of 300uA (=0.3mA).
        DCurrCheck Mode: Check abrupt variation of current by a factor of 35
        times the dcct fluctuation/resolution.
        """
        [timestamp, value] = self._current_buffer.serie
        if self._buffautorst_mode == 0:
            if (self._storedebeam_pv.connected and
                    self._storedebeam_pv.value == 0):
                self._current_buffer.clearserie()
                self._lifetime = 0
            elif ((self._is_injecting == 1 or
                   self._dtime_lastchangeinjstate < 1) and
                  (len(value) >= 2 and
                   (abs(value[-1] - value[-2]) > 0.1))):
                self._current_buffer.clearserie()
        elif self._buffautorst_mode == 1:
            if (len(value) >= 2 and
                    abs(value[-1] - value[-2]) > 100*self._dcurrfactor):
                self._current_buffer.clearserie()

    def _callback_get_injstate(self, value, timestamp, **kws):
        if value == 1:
            self._is_injecting = 1
        else:
            self._changeinjstate_timestamp = timestamp
            self._is_injecting = 0
