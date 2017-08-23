"""Main Module of the IOC Logic."""

import si_ap_currlt.pvs as _pvs
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
            ioc_name='si-ap-currlt',
            db=_pvs.pvs_database,
            description='SI AP Current and Lifetime Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX)
        _siriuspy.util.save_ioc_pv_list('si-ap-currlt',
                                        ('',
                                         _pvs._PREFIX),
                                        App.pvs_database)
        self._driver = driver
        self._pvs_database = _pvs.pvs_database
        self._current_13C4_pv = _epics.PV(
                _ioc_prefix + 'SI-13C4:DI-DCCT:Current-Mon',
                connection_timeout=0.05)
        self._current_14C4_pv = _epics.PV(
                _ioc_prefix + 'SI-14C4:DI-DCCT:Current-Mon',
                connection_timeout=0.05)
        # self._ebeamflag_13C4_pv = _epics.PV(
        #         _ioc_prefix + 'SI-13C4:DI-DCCT:EBeamFlag',
        #         connection_timeout=0.05)
        # self._ebeamflag_14C4_pv = _epics.PV(
        #         _ioc_prefix + 'SI-14C4:DI-DCCT:EBeamFlag',
        #         connection_timeout=0.05)
        # self._hwflt_13C4_pv = _epics.PV(
        #        _ioc_prefix + 'SI-13C4:DI-DCCT:HwFlt-Mon',
        #        connection_timeout=0.05)
        # self._hwflt_14C4_pv = _epics.PV(
        #        _ioc_prefix + 'SI-14C4:DI-DCCT:HwFlt-Mon',
        #        connection_timeout=0.05)
        self._current_13C4_pv.add_callback(self._read_current,
                                           self._current_13C4_pv.value)
        self._current_14C4_pv.add_callback(self._read_current,
                                           self._current_14C4_pv.value)
        self._mode = 0
        self._sampling_time = 10.0
        self._buffer_size = 100
        self._scan_time = self._sampling_time/self._buffer_size
        self._current_13C4_buffer = _siriuspy_epics.SiriusPVTimeSerie(
                            pv=self._current_13C4_pv,
                            time_window=self._sampling_time,
                            nr_max_points=self._buffer_size,
                            time_min_interval=self._scan_time,
                            mode=0)
        self._current_14C4_buffer = _siriuspy_epics.SiriusPVTimeSerie(
                            pv=self._current_14C4_pv,
                            time_window=self._sampling_time,
                            nr_max_points=self._buffer_size,
                            time_min_interval=self._scan_time,
                            mode=0)
        self._currdecayintvl = 100.0

    @staticmethod
    def init_class():
        """Init class."""
        App.pvs_database = _pvs.get_pvs_database()

    def finilize(self):
        """Class destructor."""
        self._current_13C4_pv.disconnect()
        self._current_14C4_pv.disconnect()
        self._current_13C4_pv = None
        self._current_14C4_pv = None

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
        if reason == 'Version':
            acquireflag13C4 = False
            acquireflag14C4 = False
            if (self._current_13C4_pv.connected):  # and
                    # (self._ebeamflag_13C4_pv.value) and
                    # (self._hwflt_13C4_pv.value == 0)):
                acquireflag13C4 = self._current_13C4_buffer.acquire()
                self._test_current_abrupt_variation(self._current_13C4_buffer)
            if (self._current_14C4_pv.connected):  # and
                    # (self._ebeamflag_14C4_pv.value) and
                    # (self._hwflt_14C4_pv.value == 0)
                acquireflag14C4 = self._current_14C4_buffer.acquire()
                self._test_current_abrupt_variation(self._current_14C4_buffer)
            if acquireflag13C4 or acquireflag14C4:
                lifetime = self._calclifetime()
                if lifetime is not None:
                    # if lifetime<0:
                    #     a,b = self._current_13C4_buffer.serie
                    #     print('list')
                    #     for i in range(len(a)):
                    #         print(str(a[i])+' '+str(b[i]))
                    #     print(str(len(a)))
                    self.driver.setParam('CurrLT-Mon', lifetime)
                self.driver.setParam('SplNr-Sts',
                                     len(self._current_13C4_buffer.serie[0]))
                self.driver.updatePVs()
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'DCCT-Sel':
            # if ((value==0 and self._hwflt_13C4_pv.value==0) or
            #     (value==1 and self._hwflt_14C4_pv.value==0) or
            #     (value==2 and self._hwflt_13C4_pv.value==0 and
            #      self._hwflt_14C4_pv.value==0)):
            self._update_mode(value)
            self.driver.setParam('DCCT-Sts', self._mode)
            self.driver.updatePVs()
            status = True
        elif reason == 'SplNr-Sel':
            self._update_splnr(value)
            status = True
        elif reason == 'TotTs':
            self._update_totts(value)
            status = True
        elif reason == 'DeltaCurrMinLT':
            self._currdecayintvl = value
            status = True
        elif reason == 'RstBuffLT':
            self._clear_buffer()
        return status

    def _update_mode(self, value):
        self._mode = value

    def _update_splnr(self, value):
        self._buffer_size = value
        self._scan_time = self._sampling_time/self._buffer_size
        self._current_13C4_buffer.time_min_interval = self._scan_time
        self._current_13C4_buffer.nr_max_points = value
        self._current_14C4_buffer.time_min_interval = self._scan_time
        self._current_14C4_buffer.nr_max_points = value

    def _update_totts(self, value):
        self._sampling_time = value
        self._scan_time = self._sampling_time/self._buffer_size
        self._current_13C4_buffer.time_min_interval = self._scan_time
        self._current_13C4_buffer.time_window = value
        self._current_14C4_buffer.time_min_interval = self._scan_time
        self._current_14C4_buffer.time_window = value

    def _clear_buffer(self):
        self._current_13C4_buffer.clearserie()
        self._current_14C4_buffer.clearserie()

    def _calclifetime(self):

        def lifetime_lsf_exponential(_timestamp, _value):
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

        if self._mode == 0:
            [self._timestamp_DCCT13C4, self._value_DCCT13C4] = (
                                            self._current_13C4_buffer.serie)
            if len(self._timestamp_DCCT13C4) > min(20, self._buffer_size/2):
                return lifetime_lsf_exponential(self._timestamp_DCCT13C4,
                                                self._value_DCCT13C4)
            else:
                return None

        elif self._mode == 1:
            [self._timestamp_DCCT14C4, self._value_DCCT14C4] = (
                                            self._current_14C4_buffer.serie)
            if len(self._timestamp_DCCT14C4) > min(20, self._buffer_size/2):
                return lifetime_lsf_exponential(self._timestamp_DCCT14C4,
                                                self._value_DCCT14C4)
            else:
                return None

        elif self._mode == 2:
            [self._timestamp_DCCT13C4, self._value_DCCT13C4] = (
                                            self._current_13C4_buffer.serie)
            [self._timestamp_DCCT14C4, self._value_DCCT14C4] = (
                                            self._current_14C4_buffer.serie)
            if len(self._timestamp_DCCT13C4) > min(20, self._buffer_size/2):
                ltDCCT13C4 = lifetime_lsf_exponential(self._timestamp_DCCT13C4,
                                                      self._value_DCCT13C4)
                ltDCCT14C4 = lifetime_lsf_exponential(self._timestamp_DCCT14C4,
                                                      self._value_DCCT14C4)
                return (ltDCCT13C4+ltDCCT14C4)/2
            else:
                return None

    def _read_current(self, value, **kwargs):
        if (self._mode == 0 and self._current_13C4_pv.connected):
                # and self._hwflt_13C4_pv.value == 0):
            self._current_value = self._current_13C4_pv.value
        elif (self._mode == 1 and self._current_14C4_pv.connected):
                # and self._hwflt_14C4_pv.value==0)
            self._current_value = self._current_14C4_pv.value
        elif (self._mode == 2 and self._current_13C4_pv.connected
                and self._current_14C4_pv.connected):
                # and self._hwflt_13C4_pv.value == 0
                # and self._hwflt_14C4_pv.value == 0):
            self._current_value = self._current_13C4_pv.value
        self.driver.setParam('Current-Mon', self._current_value)
        self.driver.updatePVs()

    def _test_current_abrupt_variation(self, _current_buffer):
        """Check if occurred an abrupt variation of current.

        Compare the rate of change with a max rate of change
        based on the mean current value
        """
        timestamp, value = _current_buffer.serie
        if len(timestamp) >= 2:
            rate = abs((value[-1] - value[-2]))/(timestamp[-1] - timestamp[-2])
            if min(_numpy.mean(value), 300)/self._currdecayintvl < rate:
                _current_buffer.clearserie()
