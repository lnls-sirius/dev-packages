"""Main Module of the IOC Logic."""

import time as _time
import epics as _epics
from siriuspy.csdevice.currinfo import Const as _Const
import as_ap_currinfo.current.pvs as _pvs

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

        if _pvs.get_pvs_section().upper() == 'BO':
            self._current_bo_pv = _epics.PV(
                _pvs.get_pvs_vaca_prefix()+'BO-35D:DI-DCCT:Current-Mon')
            self._storedebeam_bo_pv = _epics.PV(
                _pvs.get_pvs_vaca_prefix()+'BO-35D:DI-DCCT:StoredEBeam-Mon')

            self._current_bo_pv.add_callback(self._callback_get_current_bo)
            self._storedebeam_bo_pv.add_callback(
                self._callback_get_storedebeam_bo)
            if not self._storedebeam_bo_pv.connected:
                self._getebeamcbindex = self._current_bo_pv.add_callback(
                    self._callback_get_ebeam_fromcurrent_bo)

        elif _pvs.get_pvs_section().upper() == 'SI':
            self._current_13C4_pv = _epics.PV(
                _pvs.get_pvs_vaca_prefix()+'SI-13C4:DI-DCCT:Current-Mon',
                connection_callback=self._connection_callback_current_DCCT13C4,
                callback=self._callback_get_dcct_current)
            self._current_14C4_pv = _epics.PV(
                _pvs.get_pvs_vaca_prefix()+'SI-14C4:DI-DCCT:Current-Mon',
                connection_callback=self._connection_callback_current_DCCT14C4,
                callback=self._callback_get_dcct_current)
            self._storedebeam_13C4_pv = _epics.PV(
                _pvs.get_pvs_vaca_prefix()+'SI-13C4:DI-DCCT:StoredEBeam-Mon',
                callback=self._callback_get_storedebeam)
            self._storedebeam_14C4_pv = _epics.PV(
                _pvs.get_pvs_vaca_prefix()+'SI-14C4:DI-DCCT:StoredEBeam-Mon',
                callback=self._callback_get_storedebeam)
            self._reliablemeas_13C4_pv = _epics.PV(
                _pvs.get_pvs_vaca_prefix()+'SI-13C4:DI-DCCT:ReliableMeas-Mon',
                callback=self._callback_get_reliablemeas)
            self._reliablemeas_14C4_pv = _epics.PV(
                _pvs.get_pvs_vaca_prefix()+'SI-14C4:DI-DCCT:ReliableMeas-Mon',
                callback=self._callback_get_reliablemeas)

            self._dcct_mode = _Const.DCCT.Avg
            self._dcctfltcheck_mode = _Const.DCCTFltCheck.Off
            self._reliablemeas_13C4_value = 0
            self._reliablemeas_14C4_value = 0
            self._storedebeam_value = 0
            self._storedebeam_13C4_value = 0
            self._storedebeam_14C4_value = 0
            if not self._storedebeam_13C4_pv.connected:
                self._getebeam13C4cbindex = self._current_13C4_pv.add_callback(
                                        self._callback_get_ebeam_fromcurrent)
            if not self._storedebeam_14C4_pv.connected:
                self._getebeam14C4cbindex = self._current_14C4_pv.add_callback(
                                        self._callback_get_ebeam_fromcurrent)

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
            if self._dcctfltcheck_mode == _Const.DCCTFltCheck.Off:
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

    # BO-AP-CurrInfo Methods

    def _callback_get_current_bo(self, value, **kws):
        self.driver.setParam('Current-Mon', value)
        self.driver.updatePVs()

    def _callback_get_storedebeam_bo(self, value, **kws):
        self.driver.setParam('StoredEBeam-Mon', value)
        self.driver.updatePVs()

    def _callback_get_ebeam_fromcurrent_bo(self, value, **kws):
        if value > 0:
            self.driver.setParam('StoredEBeam-Mon', 1)
        else:
            self.driver.setParam('StoredEBeam-Mon', 0)
        self.driver.updatePVs()

    # SI-AP-CurrInfo Methods

    def _update_dcct_mode(self, value):
        if self._dcct_mode != value:
            self._dcct_mode = value

    def _update_dcct_mode_from_reliablemeas(self):
        mode = self._dcct_mode
        if (self._reliablemeas_13C4_value == 0
                and self._reliablemeas_14C4_value == 0):
            mode = _Const.DCCT.Avg
        elif (self._reliablemeas_13C4_value == 0
                and self._reliablemeas_14C4_value != 0):
            mode = _Const.DCCT.DCCT13C4
        elif (self._reliablemeas_13C4_value != 0
                and self._reliablemeas_14C4_value == 0):
            mode = _Const.DCCT.DCCT14C4
        if mode != self._dcct_mode:
            self._dcct_mode = mode
            self.driver.setParam('DCCT-Sts', self._dcct_mode)
            self.driver.updatePVs()

    def _update_dcctfltcheck_mode(self, value):
        if self._dcctfltcheck_mode != value:
            if value == _Const.DCCTFltCheck.On:
                self._update_dcct_mode_from_reliablemeas()
            self._dcctfltcheck_mode = value

    def _connection_callback_current_DCCT13C4(self, pvname, conn, **kws):
        mode = self._dcct_mode
        if conn:
            self._current_13C4_value = self._current_13C4_pv.value
            if self._current_14C4_pv.connected:
                mode = _Const.DCCT.Avg
            else:
                mode = _Const.DCCT.DCCT13C4
        else:
            if self._current_14C4_pv.connected:
                mode = _Const.DCCT.DCCT14C4
        if mode != self._dcct_mode:
            self._dcct_mode = mode
            self.driver.setParam('DCCT-Sts', self._dcct_mode)
            self.driver.updatePVs()

    def _connection_callback_current_DCCT14C4(self, pvname, conn, **kws):
        mode = self._dcct_mode
        if conn:
            self._current_14C4_value = self._current_14C4_pv.value
            if self._current_13C4_pv.connected:
                mode = _Const.DCCT.Avg
            else:
                mode = _Const.DCCT.DCCT14C4
        else:
            if self._current_13C4_pv.connected:
                mode = _Const.DCCT.DCCT13C4
        if mode != self._dcct_mode:
            self._dcct_mode = mode
            self.driver.setParam('DCCT-Sts', self._dcct_mode)
            self.driver.updatePVs()

    def _callback_get_dcct_current(self, pvname, value, **kws):
        if '13C4' in pvname:
            self._current_13C4_value = value
        elif '14C4' in pvname:
            self._current_14C4_value = value

        if self._dcct_mode == _Const.DCCT.Avg:
            if (self._current_13C4_value is not None and
                    self._current_14C4_value is not None):
                self._current_value = (self._current_13C4_value +
                                       self._current_14C4_value)/2
            else:
                self._current_value = None
        elif self._dcct_mode == _Const.DCCT.DCCT13C4:
                self._current_value = self._current_13C4_value
        elif self._dcct_mode == _Const.DCCT.DCCT14C4:
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
        if '13C4' in pvname:
            self._storedebeam_13C4_value = value
        elif '14C4' in pvname:
            self._storedebeam_14C4_value = value

        elif self._dcct_mode == _Const.DCCT.Avg:
            self._storedebeam_value = (self._storedebeam_13C4_value and
                                       self._storedebeam_14C4_value)
        elif self._dcct_mode == _Const.DCCT.DCCT13C4:
            self._storedebeam_value = self._storedebeam_13C4_value
        elif self._dcct_mode == _Const.DCCT.DCCT14C4:
            self._storedebeam_value = self._storedebeam_14C4_value
        self.driver.setParam('StoredEBeam-Mon', self._storedebeam_value)
        self.driver.updatePVs()

    def _callback_get_ebeam_fromcurrent(self, value, **kws):
        if value > 0:
            self.driver.setParam('StoredEBeam-Mon', 1)
        else:
            self.driver.setParam('StoredEBeam-Mon', 0)
        self.driver.updatePVs()

    def _callback_get_reliablemeas(self, pvname, value, **kws):
        if '13C4' in pvname:
            self._reliablemeas_13C4_value = value
        elif '14C4' in pvname:
            self._reliablemeas_14C4_value = value

        if self._dcctfltcheck_mode == _Const.DCCTFltCheck.On:
            self._update_dcct_mode_from_reliablemeas()
