"""Main Module of the IOC Logic."""

import time as _time
from datetime import datetime as _datetime
import numpy as _np
import epics as _epics
from siriuspy.pwrsupply.csdev import Const as _PSc
from siriuspy.csdevice.currinfo import Const as _Const
from siriuspy.clientarch import ClientArchiver as _ClientArch
from siriuspy.epics import SiriusPVTimeSerie as _SiriusPVTimeSerie
import as_ap_currinfo.pvs as _pvs


# BO Constants

BO_HarmNum = 828
BO_REV_PERIOD = 1.6571334792998411  # [us]
BO_ENERGY2TIME = {  # energy: time[s]
    '150MeV': 0.0000,
    '1GeV': 0.0859,
    '2GeV': 0.1863,
    '3GeV': 0.2750,
}
INTCURR_INTVL = 53.5 * 1e-3 / 3600  # [h]
BO_CURR_THRESHOLD = 0.06

# SI Constants

SI_HarmNum = 864
SI_CHARGE_CALC_INTVL = 1 / 60.0  # 1 min [h]


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

        currthold_db = self.pvs_database['CurrThold-SP']
        self._currthold = currthold_db['value']
        self._currthold_lolim = currthold_db['lolim']
        self._currthold_hilim = currthold_db['hilim']

        self._rampeff = None
        self._currents = dict()
        self._charges = dict()
        for k in BO_ENERGY2TIME.keys():
            # currents
            self._currents[k] = 0.0
            # charges
            ppty = 'Charge'+k+'-Mon'
            data = _get_value_from_arch(self._PREFIX+ppty)
            if data is None:
                charge = 0.0
            else:
                charge = data[1][0]
            self._charges[k] = charge
            self.driver.setParam(ppty, charge)

        intcurr_ppty = 'IntCurrent3GeV-Mon'
        data = _get_value_from_arch(self._PREFIX+intcurr_ppty)
        if data is None:
            self._intcurrent3gev = 0.0
        else:
            self._intcurrent3gev = data[1][0]
        self.driver.setParam(intcurr_ppty, self._intcurrent3gev)
        self.driver.updatePV(intcurr_ppty)

        # PVs
        self._rawreadings_pv = _epics.PV(
            self._PREFIX_VACA+self._DCCT+':RawReadings-Mon',
            callback=self._callback_get_rawreadings, auto_monitor=True)
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
        if reason == 'CurrThold-SP':
            if self._currthold_lolim < value < self._currthold_hilim:
                self._currthold = value
                self.driver.setParam('CurrThold-RB', value)
                self.driver.updatePV('CurrThold-RB')
                status = True
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
        self.driver.updatePV('RawReadings-Mon')

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

        # calculate offset
        time_offset = BO_ENERGY2TIME['3GeV'] + 0.0250
        idx_offset = _np.where(_np.isclose(times, time_offset, atol=0.0005))[0]
        try:
            samples_offset = self._last_raw_reading[idx_offset[0]:]
            offset = _np.mean(samples_offset)
        except Exception:
            offset = 0.0

        # update pvs
        for energy, time in BO_ENERGY2TIME.items():
            idx = _np.where(_np.isclose(times, time, atol=0.0005))[0]
            if len(idx):
                # currents
                current = self._last_raw_reading[idx[0]] - offset
                if current < self._currthold:
                    current = 0.0
                self._currents[energy] = current
                self.driver.setParam('Current'+str(energy)+'-Mon',
                                     self._currents[energy])
                # charges
                self._charges[energy] += current * BO_REV_PERIOD
                self.driver.setParam('Charge'+str(energy)+'-Mon',
                                     self._charges[energy])

        c150mev = self._currents['150MeV']
        c3gev = self._currents['3GeV']

        # integrated current in 3GeV
        self._intcurrent3gev += c3gev * INTCURR_INTVL  # [mA.h]
        self.driver.setParam('IntCurrent3GeV-Mon', self._intcurrent3gev)

        # ramp efficiency
        if c150mev > c3gev:
            self._rampeff = 100*c3gev/c150mev
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
        self._dcct_mode = _Const.DCCT.DCCT13C4
        self._dcctfltcheck_mode = _Const.DCCTFltCheck.Off
        self._reliablemeas_13C4_value = 0
        self._reliablemeas_14C4_value = 0
        self._storedebeam_value = 0
        self._storedebeam_13C4_value = 0
        self._storedebeam_14C4_value = 0
        self._is_cycling = False
        data = _get_value_from_arch(self._PREFIX+'Charge-Mon')
        if data is None:
            self._charge = 0.0
        else:
            self._charge = data[1][0]

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
        self._dipole_opmode_pv = _epics.PV(
            self._PREFIX_VACA+'SI-Fam:PS-B1B2-1:OpMode-Sts',
            callback=self._callback_get_dipole_opmode)
        self._bo_curr3gev_pv = _epics.PV(
            self._PREFIX_VACA+'BO-Glob:AP-CurrInfo:Current3GeV-Mon',
            callback=self._callback_get_bo_curr3gev)

        self._current_13C4_buffer = _SiriusPVTimeSerie(
            pv=self._current_13C4_pv, time_window=0.4, use_pv_timestamp=False)
        self._current_14C4_buffer = _SiriusPVTimeSerie(
            pv=self._current_14C4_pv, time_window=0.4, use_pv_timestamp=False)

        # set initial pv values
        self.driver.setParam('Charge-Mon', self._charge)
        self.driver.updatePV('Charge-Mon')

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
        if 'Charge' in reason:
            timestamp = _time.time()
            if self._storedebeam_value and not self._is_cycling:
                dt = (timestamp - self._time0)  # Delta t [s]
                inc_charge = self._current_value/1000 * dt/3600  # Charge [A.h]
                self._charge += inc_charge
                self.driver.setParam('Charge-Mon', self._charge)
                self.driver.updatePV('Charge-Mon')
                value = self._charge
            self._time0 = timestamp
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'DCCT-Sel':
            if self._dcctfltcheck_mode == _Const.DCCTFltCheck.Off:
                self._update_dcct_mode(value)
                self.driver.setParam('DCCT-Sts', self._dcct_mode)
                self.driver.updatePV('DCCT-Sts')
                status = True
        elif reason == 'DCCTFltCheck-Sel':
            self._update_dcctfltcheck_mode(value)
            self.driver.setParam('DCCTFltCheck-Sts', self._dcctfltcheck_mode)
            self.driver.updatePV('DCCTFltCheck-Sts')
            status = True
        return status

    # ----- handle writes -----

    def _update_dcct_mode(self, value):
        if self._dcct_mode != value:
            self._dcct_mode = value

    def _update_dcct_mode_from_reliablemeas(self):
        if (self._reliablemeas_13C4_value == 0 and
                self._reliablemeas_14C4_value == 0):
            mode = _Const.DCCT.Avg
        elif self._reliablemeas_13C4_value == 0:
            mode = _Const.DCCT.DCCT13C4
        elif self._reliablemeas_14C4_value == 0:
            mode = _Const.DCCT.DCCT14C4
        else:
            mode = self._dcct_mode
        if mode != self._dcct_mode:
            self._dcct_mode = mode
            self.driver.setParam('DCCT-Sts', self._dcct_mode)
            self.driver.updatePV('DCCT-Sts')

    def _update_dcctfltcheck_mode(self, value):
        if self._dcctfltcheck_mode != value:
            if value == _Const.DCCTFltCheck.On:
                self._update_dcct_mode_from_reliablemeas()
            self._dcctfltcheck_mode = value

    # ----- callbacks -----

    def _callback_get_dcct_current(self, pvname, value, **kws):
        if '13C4' in pvname:
            self._current_13C4_value = value
            self._current_13C4_buffer.acquire()
        elif '14C4' in pvname:
            self._current_14C4_value = value
            self._current_14C4_buffer.acquire()

        # update current and charge
        current = self._get_current()
        if current is None:
            return
        self._current_value = current

        # update pvs
        self.driver.setParam('Current-Mon', self._current_value)
        self.driver.updatePV('Current-Mon')

    def _callback_get_storedebeam(self, pvname, value, **kws):
        if '13C4' in pvname:
            self._storedebeam_13C4_value = value
        elif '14C4' in pvname:
            self._storedebeam_14C4_value = value

        if self._dcct_mode == _Const.DCCT.Avg:
            self._storedebeam_value = (self._storedebeam_13C4_value and
                                       self._storedebeam_14C4_value)
        elif self._dcct_mode == _Const.DCCT.DCCT13C4:
            self._storedebeam_value = self._storedebeam_13C4_value
        elif self._dcct_mode == _Const.DCCT.DCCT14C4:
            self._storedebeam_value = self._storedebeam_14C4_value
        self.driver.setParam('StoredEBeam-Mon', self._storedebeam_value)
        self.driver.updatePV('StoredEBeam-Mon')

    def _callback_get_reliablemeas(self, pvname, value, **kws):
        if '13C4' in pvname:
            self._reliablemeas_13C4_value = value
        elif '14C4' in pvname:
            self._reliablemeas_14C4_value = value

        if self._dcctfltcheck_mode == _Const.DCCTFltCheck.On:
            self._update_dcct_mode_from_reliablemeas()

    def _callback_get_dipole_opmode(self, value, **kws):
        self._is_cycling = bool(value == _PSc.States.Cycle)

    def _callback_get_bo_curr3gev(self, value, timestamp, **kws):
        """Get BO Current3GeV-Mon and update InjEff PV."""
        # choose current PV
        buffer = self._current_13C4_buffer \
            if self._dcct_mode in [_Const.DCCT.Avg, _Const.DCCT.DCCT13C4] \
            else self._current_14C4_buffer
        timestamp_dq, value_dq = buffer.serie

        # check buffer not empty
        if not len(timestamp_dq):
            return

        # check if there is valid current in Booster
        if value < BO_CURR_THRESHOLD:
            return

        # calculate efficiency
        delta_curr = max(value_dq[-1] - value_dq[0], 0)
        self._injeff = 100*(delta_curr/value)*(SI_HarmNum/BO_HarmNum)

        # update pvs
        self.driver.setParam('InjEff-Mon', self._injeff)
        self.driver.updatePV('InjEff-Mon')

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
