"""Main Module of the IOC Logic."""

import warnings
import time as _time
from collections import deque as _deque
import numpy as _np
import epics as _epics
from siriuspy.epics import SiriusPVTimeSerie as _SiriusPVTimeSerie
from siriuspy.csdevice.currinfo import Const as _Const
import as_ap_currinfo.lifetime.pvs as _pvs

warnings.filterwarnings('error')

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


_MAX_BUFFER_SIZE = 100000


class App:
    """Main Class of the IOC Logic."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _pvs.print_banner()

        self._driver = driver
        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()
        self._PREFIX = _pvs.get_pvs_prefix()

        self._mode = _Const.Fit.Exponential
        self._lifetime = 0
        self._lifetime_bpm = 0
        self._current_offset = 0.0
        self._sampling_interval = 2000.0
        self._min_intvl_btw_spl = 0.0
        self._is_stored = 0

        self._current_pv = _epics.PV(self._PREFIX+'Current-Mon')
        self._bpmsum_pv = _epics.PV(self._PREFIX_VACA+'SI-01M1:DI-BPM:Sum-Mon')
        self._storedebeam_pv = _epics.PV(self._PREFIX+'StoredEBeam-Mon')

        self._current_buffer = _SiriusPVTimeSerie(
            pv=self._current_pv, mode=0, nr_max_points=_MAX_BUFFER_SIZE)
        self._bpmsum_buffer = _SiriusPVTimeSerie(
            pv=self._bpmsum_pv, mode=0, nr_max_points=_MAX_BUFFER_SIZE)

        self._lifetime_dcct_buffer = _deque(maxlen=_MAX_BUFFER_SIZE)
        self._lifetime_bpm_buffer = _deque(maxlen=_MAX_BUFFER_SIZE)

        self._current_pv.add_callback(self._callback_calclifetime)
        self._bpmsum_pv.add_callback(self._callback_calclifetime)
        self._storedebeam_pv.add_callback(self._callback_get_storedebeam)

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
        if reason == 'SplIntvl-SP':
            self._update_splintvl(value)
            self.driver.setParam('SplIntvl-RB', self._sampling_interval)
            self.driver.updatePV('SplIntvl-RB')
            status = True
        elif reason == 'MinIntvlBtwSpl-SP':
            self._update_min_intvl_btw_spl(value)
            self.driver.setParam('MinIntvlBtwSpl-RB', self._min_intvl_btw_spl)
            self.driver.updatePV('MinIntvlBtwSpl-RB')
            status = True
        elif reason == 'LtFitMode-Sel':
            self._mode = value
            self.driver.setParam('LtFitMode-Sts', value)
            self.driver.updatePV('LtFitMode-Sts')
            status = True
        elif reason == 'CurrOffset-SP':
            self._current_offset = value
            self.driver.setParam('CurrOffset-RB', value)
            self.driver.updatePV('CurrOffset-RB')
            status = True
        return status

    def _update_min_intvl_btw_spl(self, value):
        if value < 0:
            value = 0
        self._min_intvl_btw_spl = value

    def _update_splintvl(self, value):
        self._sampling_interval = value

    def _callback_get_storedebeam(self, value, **kws):
        self._is_stored = value

    def _callback_calclifetime(self, pvname, timestamp, **kws):
        # check DCCT StoredEBeam PV
        if not self._is_stored:
            return

        is_bpm = 'BPM' in pvname
        lt_type = 'BPM' if is_bpm else ''
        lt_name = '_lifetime'+('_bpm' if is_bpm else '')
        buffer_dt = self._bpmsum_buffer if is_bpm else self._current_buffer
        buffer_lt = self._lifetime_bpm_buffer \
            if is_bpm else self._lifetime_dcct_buffer

        # try to add a new point to buffer
        acquireflag = buffer_dt.acquire()
        if not acquireflag:
            return

        # check min number of points in buffer to calculate lifetime
        [ts_abs_dqorg, val_abs_dqorg] = buffer_dt.get_serie(time_absolute=True)
        buffer_dt_aux = _SiriusPVTimeSerie(
            pv=None,
            timestamp_init_data=ts_abs_dqorg,
            value_init_data=val_abs_dqorg)
        buffer_dt_aux.time_min_interval = self._min_intvl_btw_spl
        buffer_dt_aux.time_window = self._sampling_interval
        ts_dq, val_dq = buffer_dt_aux.get_serie()
        ts_dq = _np.array(ts_dq)
        val_dq = _np.array(val_dq)
        if not len(ts_dq):
            setattr(self, lt_name, 0)
        else:
            val_dq -= self._current_offset
            if len(val_dq) > 100:
                fit = 'exp' if self._mode == _Const.Fit.Exponential else 'lin'
                lt = self._least_squares_fit(ts_dq, val_dq, fit=fit)
                setattr(self, lt_name, lt)
                buffer_lt.append(lt)

        # update pvs
        self.driver.setParam('BufferValue'+lt_type+'-Mon', val_dq)
        self.driver.updatePV('BufferValue'+lt_type+'-Mon')
        self.driver.setParam('BufferTimestamp'+lt_type+'-Mon', ts_dq)
        self.driver.updatePV('BufferTimestamp'+lt_type+'-Mon')
        self.driver.setParam('Lifetime'+lt_type+'-Mon', getattr(self, lt_name))
        self.driver.updatePV('Lifetime'+lt_type+'-Mon')
        self.driver.setParam('BuffSize'+lt_type+'-Mon', len(val_dq))
        self.driver.updatePV('BuffSize'+lt_type+'-Mon')
        self.driver.setParam('BuffSizeTot'+lt_type+'-Mon', len(val_abs_dqorg))
        self.driver.updatePV('BuffSizeTot'+lt_type+'-Mon')

    @staticmethod
    def _least_squares_fit(timestamp, value, fit='exp'):
        if fit == 'exp':
            try:
                value = _np.log(value)
            except Exception:
                return 0.0
        n = len(timestamp)
        x = _np.sum(timestamp)
        y = _np.sum(value)
        x2 = _np.sum(_np.power(timestamp, 2))
        xy = _np.sum(timestamp*value)
        a = (x2*y - xy*x)/(n*x2 - x*x)
        b = (n*xy - x*y)/(n*x2 - x*x)

        if fit == 'exp':
            lt = - 1/b
        else:
            lt = - a/b
        return lt
