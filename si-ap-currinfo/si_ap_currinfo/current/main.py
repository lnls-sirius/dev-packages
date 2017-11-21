"""Main Module of the IOC Logic."""

import time as _time
import epics as _epics
import siriuspy as _siriuspy
import siriuspy.envars as _siriuspy_envars
import siriuspy.util as _siriuspy_util
import si_ap_currinfo.current.pvs as _pvs

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
            ioc_name='si-ap-currinfo-current',
            db=App.pvs_database,
            description='SI-AP-CurrInfo-Current Soft IOC',
            version=__version__,
            prefix=_pvs._PREFIX)
        _siriuspy.util.save_ioc_pv_list('si-ap-currinfo-current',
                                        (_pvs._DEVICE,
                                         _pvs._PREFIX_VACA),
                                        App.pvs_database)
        self._driver = driver
        self._pvs_database = App.pvs_database

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
        return status

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
