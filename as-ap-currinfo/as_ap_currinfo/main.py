"""Main Module of the IOC Logic."""

import time as _time
from datetime import datetime as _datetime
import numpy as _np
import epics as _epics
from siriuspy.csdevice.currinfo import Const as _Const
from siriuspy.clientarch import ClientArchiver as _ClientArch
import as_ap_currinfo.pvs as _pvs


BO_REV_PERIOD = 1.6571334792998411 * 1e-6 / 3600  # [h]
BO_ENERGY2TIME = {  # energy vs. time[s]
    '150MeV': 0.0000,
    '1GeV': 0.0859,
    '2GeV': 0.1863,
    '3GeV': 0.2850,
}
CURR_LIM = 0.002


def _get_value_from_arch(pvname):
    carch = _ClientArch()
    datetime = _datetime.now().isoformat() + '-03:00'
    data = carch.getData(pvname, datetime, datetime)
    return data


class BOApp:
    """Main Class of the IOC Logic."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _pvs.print_banner()

        self._driver = driver

        # consts
        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()
        self._PREFIX = _pvs.get_pvs_prefix()
        self._DCCT = 'BO-35D:DI-DCCT'

        # initialize vars
        self._samplecnt = None
        self._measperiod = None
        self._reliablemeas = None
        self._last_raw_reading = None
        self._rampeff = None
        self._currents = dict()
        self._charges = dict()
        for k in BO_ENERGY2TIME.keys():
            # currents
            self._currents[k] = 0.0
            # charges
            ppty = 'Charge'+k+'-Mon'
            charge = _get_value_from_arch(self._PREFIX+':'+ppty)
            if charge is None:
                charge = 0.0
            self._charges[k] = charge
            self.driver.setParam(ppty, charge)
        self.driver.updatePVs()

        # PVs
        self._rawreadings_pv = _epics.PV(
            self._PREFIX_VACA+self._DCCT+':RawReadings-Mon',
            callback=self._callback_get_rawreadings,
            auto_monitor=True)
        self._samplecnt_pv = _epics.PV(
            self._PREFIX_VACA+self._DCCT+':FastSampleCnt-RB',
            connection_timeout=0.05, callback=self._callback_get_samplecnt)
        self._measperiod_pv = _epics.PV(
            self._PREFIX_VACA+self._DCCT+':FastMeasPeriod-RB',
            connection_timeout=0.05, callback=self._callback_get_measperiod)
        self._reliablemeas_pv = _epics.PV(
            self._PREFIX_VACA+self._DCCT+':ReliableMeas-Mon',
            connection_timeout=0.05, callback=self._callback_get_reliablemeas)

    @staticmethod
    def init_class():
        """Init class."""
        BOApp.pvs_database = _pvs.get_pvs_database()

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
        return status

    # ----- callbacks -----

    def _callback_get_samplecnt(self, value, **kws):
        """Get SampleCnt-RB value."""
        self._samplecnt = value

    def _callback_get_measperiod(self, value, **kws):
        """Get MeasPeriod-RB value."""
        self._measperiod = value

    def _callback_get_reliablemeas(self, value, **kws):
        """Get ReliableMeas-Mon value."""
        self._reliablemeas = value

    def _callback_get_rawreadings(self, value, **kws):
        self._last_raw_reading = value
        self._update_pvs()
        self.driver.setParam('RawReadings-Mon', value)
        self.driver.updatePVs()

    # ----- auxiliar methods -----

    def _update_pvs(self):
        """Update current, charges and ramp efficiency."""
        if self._samplecnt is None or self._measperiod is None:
            # ignore None values in initializations
            return
        if self._reliablemeas != 0:
            # do not calculate if dcct measure is not reliable
            return
        if len(self._last_raw_reading) != self._samplecnt:
            # ignore dcct measurements with wrong sample count
            return

        times = _np.linspace(0.0, self._measperiod, self._samplecnt)  # [ms]
        for energy, time in BO_ENERGY2TIME.items():
            idx = _np.where(_np.isclose(times, time, atol=0.0005))[0]
            if len(idx):
                # currents
                current = self._last_raw_reading[idx[0]]
                self._currents[energy] = current
                self.driver.setParam('Current'+str(energy)+'-Mon',
                                     self._currents[energy])
                # charges
                self._charges[energy] += current/1000 * BO_REV_PERIOD
                self.driver.setParam('Charge'+str(energy)+'-Mon',
                                     self._charges[energy])
        # ramp efficiency
        c150mev = self._currents['150MeV']
        inj_curr = c150mev if c150mev > CURR_LIM else CURR_LIM
        c3gev = self._currents['3GeV']
        eje_curr = c3gev if c3gev > 0 else 0
        if inj_curr > eje_curr:
            self._rampeff = 100*eje_curr/inj_curr
            self.driver.setParam('RampEff-Mon', self._rampeff)

        self.driver.updatePVs()


class SIApp:
    """Main Class of the IOC Logic."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _pvs.print_banner()

        self._driver = driver

        # consts
        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()
        self._PREFIX = _pvs.get_pvs_prefix()

        # initialize vars
        self._time0 = _time.time()
        self._current_value = None
        self._current_13C4_value = None
        self._current_14C4_value = None
        self._dcct_mode = _Const.DCCT.Avg
        self._dcctfltcheck_mode = _Const.DCCTFltCheck.Off
        self._reliablemeas_13C4_value = 0
        self._reliablemeas_14C4_value = 0
        self._storedebeam_value = 0
        self._storedebeam_13C4_value = 0
        self._storedebeam_14C4_value = 0
        self._chargecalcintvl = 100.0
        self._charge = _get_value_from_arch(self._PREFIX+':Charge-Mon')
        if self._charge is None:
            self._charge = 0.0

        # pvs
        self._current_13C4_pv = _epics.PV(
            self._PREFIX_VACA+'SI-13C4:DI-DCCT:Current-Mon',
            callback=self._callback_get_dcct_current)
        self._current_14C4_pv = _epics.PV(
            self._PREFIX_VACA+'SI-14C4:DI-DCCT:Current-Mon',
            callback=self._callback_get_dcct_current)
        self._storedebeam_13C4_pv = _epics.PV(
            self._PREFIX_VACA+'SI-13C4:DI-DCCT:StoredEBeam-Mon',
            callback=self._callback_get_storedebeam)
        self._storedebeam_14C4_pv = _epics.PV(
            self._PREFIX_VACA+'SI-14C4:DI-DCCT:StoredEBeam-Mon',
            callback=self._callback_get_storedebeam)
        self._reliablemeas_13C4_pv = _epics.PV(
            self._PREFIX_VACA+'SI-13C4:DI-DCCT:ReliableMeas-Mon',
            callback=self._callback_get_reliablemeas)
        self._reliablemeas_14C4_pv = _epics.PV(
            self._PREFIX_VACA+'SI-14C4:DI-DCCT:ReliableMeas-Mon',
            callback=self._callback_get_reliablemeas)

        # set initial pv values
        self.driver.setParam('Charge-Mon', self._charge)
        self.driver.updatePVs()

    @staticmethod
    def init_class():
        """Init class."""
        SIApp.pvs_database = _pvs.get_pvs_database()

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
                status = True
        elif reason == 'DCCTFltCheck-Sel':
            self._update_dcctfltcheck_mode(value)
            self.driver.setParam('DCCTFltCheck-Sts', self._dcctfltcheck_mode)
            status = True
        elif reason == 'ChargeCalcIntvl-SP':
            self._update_chargecalcintvl(value)
            self.driver.setParam('ChargeCalcIntvl-RB', self._chargecalcintvl)
            status = True
        if status:
            self.driver.updatePVs()
        return status

    # ----- handle writes -----

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

    def _update_chargecalcintvl(self, value):
        if self._chargecalcintvl != value:
            self._chargecalcintvl = value

    # ----- callbacks -----

    def _callback_get_dcct_current(self, pvname, value, timestamp, **kws):
        if '13C4' in pvname:
            self._current_13C4_value = value
        elif '14C4' in pvname:
            self._current_14C4_value = value

        # update current and charge
        current = self._get_current()
        if current is None:
            return
        self._current_value = current
        self._charge += self._calculate_inc_charge(timestamp)

        # update pvs
        self.driver.setParam('Current-Mon', self._current_value)
        self.driver.setParam('Charge-Mon', self._charge)
        self.driver.updatePVs()

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

    def _callback_get_reliablemeas(self, pvname, value, **kws):
        if '13C4' in pvname:
            self._reliablemeas_13C4_value = value
        elif '14C4' in pvname:
            self._reliablemeas_14C4_value = value

        if self._dcctfltcheck_mode == _Const.DCCTFltCheck.On:
            self._update_dcct_mode_from_reliablemeas()

    # ----- auxiliar methods -----

    def _get_current(self):
        if self._dcct_mode == _Const.DCCT.Avg:
            if (self._current_13C4_value is not None and
                    self._current_14C4_value is not None):
                current = (self._current_13C4_value+self._current_14C4_value)/2
            else:
                current = None
        elif self._dcct_mode == _Const.DCCT.DCCT13C4:
            current = self._current_13C4_value
        elif self._dcct_mode == _Const.DCCT.DCCT14C4:
            current = self._current_14C4_value
        return current

    def _calculate_inc_charge(self, timestamp):
        dt = (timestamp - self._time0)  # Delta t [s]
        if dt <= self._chargecalcintvl:
            return 0.0
        self._time0 = timestamp
        inc_charge = self._current_value/1000 * dt/3600  # Charge [A.h]
        return inc_charge
