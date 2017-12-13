"""Main Module of the IOC Logic."""

import time as _time
import epics as _epics
import as_ap_currinfo.charge.pvs as _pvs

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
        _pvs.print_banner_and_save_pv_list()

        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()
        self._PREFIX = _pvs.get_pvs_prefix()

        self._driver = driver

        self._chargecalcintvl = 100.0
        self._current_pv = _epics.PV(
            self._PREFIX_VACA + 'SI-Glob:AP-CurrInfo:Current-Mon',
            connection_timeout=0.05)
        self._current_pv.add_callback(self._callback_calccharge)
        self._time0 = _time.time()
        self._arq = open('/home/fac_files/lnls-sirius/machine-applications/'
                         'as-ap-currinfo/as_ap_currinfo/charge/charge.txt',
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
                             '/machine-applications/as-ap-currinfo'
                             '/as_ap_currinfo/charge/charge.txt',
                             'w')
            self._arq.write(str(self._charge))
            self._arq.close()
            self._time0 = self._time1
            self.driver.setParam('Charge-Mon', self._charge)
            self.driver.updatePVs()
