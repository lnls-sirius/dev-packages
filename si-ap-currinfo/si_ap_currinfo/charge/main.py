"""Main Module of the IOC Logic."""

import time as _time
import epics as _epics
import siriuspy as _siriuspy
import siriuspy.envars as _siriuspy_envars
import siriuspy.util as _siriuspy_util
import si_ap_currinfo.charge.pvs as _pvs

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
            ioc_name='si-ap-currinfo-charge',
            db=App.pvs_database,
            description='SI-AP-CurrInfo-Charge Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX)
        _siriuspy.util.save_ioc_pv_list('si-ap-currinfo-charge',
                                        (_pvs._DEVICE,
                                         _pvs._PREFIX_VACA),
                                        App.pvs_database)
        self._driver = driver
        self._pvs_database = App.pvs_database

        self._chargecalcintvl = 100.0
        self._current_pv = _epics.PV(
            _ioc_prefix + 'SI-Glob:AP-CurrInfo:Current-Mon',
            connection_timeout=0.05)
        self._current_pv.add_callback(self._callback_calccharge)
        self._time0 = _time.time()
        self._arq = open('/home/fac_files/lnls-sirius/machine-applications/'
                         'si-ap-currinfo/si_ap_currinfo/charge/charge.txt',
                         'r')
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
        # Charge Soft IOC reasons
        if reason == 'ChargeCalcIntvl-SP':
            self._update_chargecalcintvl(value)
            self.driver.setParam('ChargeCalcIntvl-RB', self._chargecalcintvl)
            self.driver.updatePVs()
            status = True
        return status

    def _update_chargecalcintvl(self, value):
        if self._chargecalcintvl != value:
            self._chargecalcintvl = value

    def _callback_calccharge(self, value, timestamp, **kws):
        if (timestamp - self._time0) >= self._chargecalcintvl:
            self._current_value = value  # Current in mA
            self._time1 = timestamp      # Timestamp in s
            self._charge += (1/3600000)*self._current_value*(
                            self._time1 - self._time0)  # Charge in A.h
            self._arq = open('/home/fac_files/lnls-sirius'
                             '/machine-applications/si-ap-currinfo'
                             '/si_ap_currinfo/charge/charge.txt',
                             'w')
            self._arq.write(str(self._charge))
            self._arq.close()
            self._time0 = self._time1
            self.driver.setParam('Charge-Mon', self._charge)
            self.driver.updatePVs()
