"""Main Module of the IOC Logic."""

import si_ap_currinfo.pvs as _pvs
import epics as _epics
import siriuspy as _siriuspy
import siriuspy.envars as _siriuspy_envars
import siriuspy.epics as _siriuspy_epics
import siriuspy.util as _siriuspy_util
import numpy as _numpy
import time as _time

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
            ioc_name='si-ap-currinfo-' + _pvs._INFO,
            db=App.pvs_database,
            description='SI AP CURRINFO ' + _pvs._INFO.upper() + ' Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX)
        _siriuspy.util.save_ioc_pv_list('si-ap-currinfo-' + _pvs._INFO,
                                        ('',
                                         _pvs._PREFIX),
                                        App.pvs_database)
        self._driver = driver
        self._pvs_database = App.pvs_database

        if _pvs._INFO == 'current':
            self._current_13C4_pv = _epics.PV(
                _ioc_prefix + 'SI-13C4:DI-DCCT:Current-Mon',
                connection_callback=self._connection_callback_current_DCCT13C4,
                connection_timeout=0.05)
            self._current_14C4_pv = _epics.PV(
                _ioc_prefix + 'SI-14C4:DI-DCCT:Current-Mon',
                connection_callback=self._connection_callback_current_DCCT14C4,
                connection_timeout=0.05)
            self._storedebeam_13C4_pv = _epics.PV(
                _ioc_prefix + 'SI-13C4:DI-DCCT:StoredEBeam-Mon',
                connection_timeout=0.05)
            self._storedebeam_14C4_pv = _epics.PV(
                _ioc_prefix + 'SI-14C4:DI-DCCT:StoredEBeam-Mon',
                connection_timeout=0.05)
            self._hwflt_13C4_pv = _epics.PV(
                _ioc_prefix + 'SI-13C4:DI-DCCT:HwFlt-Mon',
                connection_timeout=0.05)
            self._hwflt_14C4_pv = _epics.PV(
                _ioc_prefix + 'SI-14C4:DI-DCCT:HwFlt-Mon',
                connection_timeout=0.05)

            self._dcct_mode = 0
            self._dcctfltcheck_mode = 0
            self._hwflt_13C4_value = 0
            self._hwflt_14C4_value = 0
            if not self._storedebeam_13C4_pv.connected:
                self._getebeam13C4cbindex = self._current_13C4_pv.add_callback(
                                        self._callback_get_ebeam_fromcurrent)
            if not self._storedebeam_14C4_pv.connected:
                self._getebeam14C4cbindex = self._current_14C4_pv.add_callback(
                                        self._callback_get_ebeam_fromcurrent)

            self._current_13C4_pv.add_callback(self._callback_get_dcct_current)
            self._current_14C4_pv.add_callback(self._callback_get_dcct_current)
            self._storedebeam_13C4_pv.add_callback(
                                            self._callback_get_storedebeam)
            self._storedebeam_14C4_pv.add_callback(
                                            self._callback_get_storedebeam)
            self._hwflt_13C4_pv.add_callback(self._callback_get_hwflt)
            self._hwflt_14C4_pv.add_callback(self._callback_get_hwflt)

        elif _pvs._INFO == 'lifetime':
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

        elif _pvs._INFO == 'charge':
            self._chargecalcintvl = 100.0
            self._current_pv = _epics.PV(
                _ioc_prefix + 'SI-Glob:AP-CurrInfo:Current-Mon',
                connection_timeout=0.05)
            self._current_pv.add_callback(self._callback_calccharge)
            self._time0 = _time.time()
            self._arq = open(
                        ('/home/fac_files/lnls-sirius/machine-applications/'
                         'si-ap-currinfo/si_ap_currinfo/charge.txt'), 'r')
            self._charge = float(self._arq.readline())
            self._arq.close()
            self.driver.setParam('Charge-Mon', self._charge)
            self.driver.updatePVs()

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

        # Current Soft IOC reasons
        if reason == 'DCCT-Sel':
            if self._dcctfltcheck_mode == 1:  # DCCTFltCheck Off
                self._update_dcct_mode(value)
                self.driver.setParam('DCCT-Sts', self._dcct_mode)
                self.driver.updatePVs()
                status = True
        elif reason == 'DCCTFltCheck-Sel':
            self._update_dcctfltcheck_mode(value)
            self.driver.setParam('DCCTFltCheck-Sts', self._dcctfltcheck_mode)
            self.driver.updatePVs()
            status = True

        # Lifetime Soft IOC reasons
        elif reason == 'BuffSizeMax-SP':
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
            self._clear_buffer()
        elif reason == 'BuffAutoRst-Sel':
            self._update_buffautorst_mode(value)
            self.driver.setParam('BuffAutoRst-Sts', self._buffautorst_mode)
            self.driver.updatePVs()
            status = True

        # Charge Soft IOC reasons
        elif reason == 'ChargeCalcIntvl-SP':
            self._update_chargecalcintvl(value)
            self.driver.setParam('ChargeCalcIntvl-RB', self._chargecalcintvl)
            self.driver.updatePVs()
            status = True
        return status

    # Current Soft IOC Modules
    def _update_dcct_mode(self, value):
        if self._dcct_mode != value:
            self._dcct_mode = value

    def _update_dcct_mode_fromhwflt(self):
        mode = self._dcct_mode
        if self._hwflt_13C4_value == 0 and self._hwflt_14C4_value == 0:
            mode = 0
        elif self._hwflt_13C4_value == 0 and self._hwflt_14C4_value != 0:
            mode = 1
        elif self._hwflt_13C4_value != 0 and self._hwflt_14C4_value == 0:
            mode = 2
        if mode != self._dcct_mode:
            self._dcct_mode = mode
            self.driver.setParam('DCCT-Sts', self._dcct_mode)
            self.driver.updatePVs()

    def _update_dcctfltcheck_mode(self, value):
        if self._dcctfltcheck_mode != value:
            if value == 0:
                self._update_dcct_mode_fromhwflt()
            self._dcctfltcheck_mode = value

    def _connection_callback_current_DCCT13C4(self, pvname, conn, **kws):
        mode = self._dcct_mode
        if conn:
            self._current_13C4_value = self._current_13C4_pv.value
            if self._current_14C4_pv.connected:
                mode = 0
            else:
                mode = 1
        else:
            if self._current_14C4_pv.connected:
                mode = 2
        if mode != self._dcct_mode:
            self._dcct_mode = mode
            self.driver.setParam('DCCT-Sts', self._dcct_mode)
            self.driver.updatePVs()

    def _connection_callback_current_DCCT14C4(self, pvname, conn, **kws):
        mode = self._dcct_mode
        if conn:
            self._current_14C4_value = self._current_14C4_pv.value
            if self._current_13C4_pv.connected:
                mode = 0
            else:
                mode = 2
        else:
            if self._current_13C4_pv.connected:
                mode = 1
        if mode != self._dcct_mode:
            self._dcct_mode = mode
            self.driver.setParam('DCCT-Sts', self._dcct_mode)
            self.driver.updatePVs()

    def _callback_get_dcct_current(self, pvname, value, **kws):
        if pvname == _ioc_prefix + 'SI-13C4:DI-DCCT:Current-Mon':
            self._current_13C4_value = value
        elif pvname == _ioc_prefix + 'SI-14C4:DI-DCCT:Current-Mon':
            self._current_14C4_value = value

        if self._dcct_mode == 0:  # Avg
            if (self._current_13C4_value is not None and
                    self._current_14C4_value is not None):
                self._current_value = (self._current_13C4_value +
                                       self._current_14C4_value)/2
            else:
                self._current_value = None
        elif self._dcct_mode == 1:  # 13C4
                self._current_value = self._current_13C4_value
        elif self._dcct_mode == 2:  # 14C4
            self._current_value = self._current_14C4_value
        self.driver.setParam('Current-Mon', self._current_value)
        self.driver.updatePVs()

    def _connection_callback_storedebeam_DCCT13C4(self, pvname, conn, **kws):
        if conn:
            self._current_13C4_pv.remove_callback(self._getebeam13C4cbindex)
        else:
            self._current_13C4_pv.add_callback(
                                        self._callback_get_ebeam_fromcurrent)

    def _connection_callback_storedebeam_DCCT14C4(self, pvname, conn, **kws):
        if conn:
            self._current_14C4_pv.remove_callback(self._getebeam14C4cbindex)
        else:
            self._current_14C4_pv.add_callback(
                                        self._callback_get_ebeam_fromcurrent)

    def _callback_get_storedebeam(self, pvname, value, **kws):
        if pvname == _ioc_prefix + 'SI-13C4:DI-DCCT:StoredEBeam-Mon':
            self._storedebeam_13C4_value = value
        elif pvname == _ioc_prefix + 'SI-14C4:DI-DCCT:StoredEBeam-Mon':
            self._storedebeam_14C4_value = value

        elif self._dcct_mode == 0:  # Avg
            self._storedebeam_value = (self._storedebeam_13C4_value and
                                       self._storedebeam_14C4_value)
        elif self._dcct_mode == 1:  # 13C4
            self._storedebeam_value = self._storedebeam_13C4_value
        elif self._dcct_mode == 2:  # 14C4
            self._storedebeam_value = self._storedebeam_14C4_value
        self.driver.setParam('StoredEBeam-Mon', self._storedebeam_value)
        self.driver.updatePVs()

    def _callback_get_ebeam_fromcurrent(self, value, **kws):
        if value > 0:
            self.driver.setParam('StoredEBeam-Mon', 1)
        else:
            self.driver.setParam('StoredEBeam-Mon', 0)
        self.driver.updatePVs()

    def _callback_get_hwflt(self, pvname, value, **kws):
        if pvname == _ioc_prefix + 'SI-13C4:DI-DCCT:HwFlt-Mon':
            self._hwflt_13C4_value = value
        elif pvname == _ioc_prefix + 'SI-14C4:DI-DCCT:HwFlt-Mon':
            self._hwflt_14C4_value = value

        if self._dcctfltcheck_mode == 0:  # DCCTFltCheck On
            self._update_dcct_mode_fromhwflt()

    # Lifetime Soft IOC Modules
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

    # Charge Soft IOC Modules
    def _update_chargecalcintvl(self, value):
        if self._chargecalcintvl != value:
            self._chargecalcintvl = value

    def _callback_calccharge(self, value, timestamp, **kws):
        if (timestamp - self._time0) >= self._chargecalcintvl:
            self._current_value = value  # Current in mA
            self._time1 = timestamp      # Timestamp in s
            self._charge += (1/3600000)*self._current_value*(
                            self._time1 - self._time0)  # Charge in A.h
            self._arq = open(
                        ('/home/fac_files/lnls-sirius/machine-applications/'
                         'si-ap-currinfo/si_ap_currinfo/charge.txt'), 'w')
            self._arq.write(str(self._charge))
            self._arq.close()
            self._time0 = self._time1
            self.driver.setParam('Charge-Mon', self._charge)
            self.driver.updatePVs()
