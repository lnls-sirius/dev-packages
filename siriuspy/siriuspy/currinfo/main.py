"""Main Module of the IOC Logic."""

import time as _time
from datetime import datetime as _datetime
import logging as _log
from copy import deepcopy as _dcopy

import numpy as _np
from epics import PV as _PV

from mathphys.functions import _get_namedtuple

from ..callbacks import Callback as _Callback
from ..epics import SiriusPVTimeSerie as _SiriusPVTimeSerie
from ..envars import VACA_PREFIX as _vaca_prefix
from ..clientarch import ClientArchiver as _ClientArch
from ..pwrsupply.csdev import Const as _PSc

from .csdev import Const as _Const, \
    get_currinfo_database as _get_database


# BO Constants
BO_HARMNUM = 828
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
SI_HARMNUM = 864
SI_CHARGE_CALC_INTVL = 1 / 60.0  # 1 min [h]


def _get_value_from_arch(pvname):
    carch = _ClientArch()
    datetime = _datetime.now().isoformat() + '-03:00'
    data = carch.getData(pvname, datetime, datetime)
    return data


class _ASCurrInfoApp(_Callback):
    """."""

    INDICES = _get_namedtuple(
        'Indices',
        ('NAME', 'CURR', 'AVG', 'MIN', 'MAX', 'STD', 'COUNT'))

    OSC_IP = 'scope-dig-linac-ict'
    ACC = ''
    ICT1 = ''
    ICT2 = ''

    def __init__(self, resource_manager):
        super().__init__()
        self._pvs_database = _get_database(self.ACC)
        self.resource_manager = resource_manager
        # open communication with Oscilloscope
        self.osc_socket = resource_manager.open_resource(
            'TCPIP::'+self.OSC_IP+'::inst0::INSTR')

    def init_database(self):
        """."""

    @property
    def pvs_database(self):
        """."""
        return _dcopy(self._pvs_database)

    def read(self, reason):
        """."""
        _ = reason
        return None

    def write(self, reason, value):
        """."""
        _, _ = reason, value
        return True

    def close(self):
        """."""
        self.osc_socket.close()

    def process(self, interval):
        """."""
        tini = _time.time()
        try:
            self._update_pvs()
        except Exception as err:
            _log.error('Problem reading data: {:s}'.format(str(err)))

        dtim = _time.time() - tini
        if dtim <= interval:
            _time.sleep(interval - dtim)
        else:
            _log.warning(
                'IOC took {0:.3f} ms in update loop.'.format(dtim*1000))

    def _update_pvs(self):
        """."""
        meas = self.osc_socket.query(":MEASure:RESults?")
        meas = meas.split(',')

        name = self.ACC+'-ICT1'
        idxict1 = [i for i, val in enumerate(meas) if name in val].pop()
        chg1 = float(meas[idxict1 + self.INDICES.CURR]) * 1e9
        ave1 = float(meas[idxict1 + self.INDICES.AVG]) * 1e9
        min1 = float(meas[idxict1 + self.INDICES.MIN]) * 1e9
        max1 = float(meas[idxict1 + self.INDICES.MAX]) * 1e9
        std1 = float(meas[idxict1 + self.INDICES.STD]) * 1e9
        cnt1 = int(float(meas[idxict1 + self.INDICES.COUNT]))

        name = self.ACC+'-ICT2'
        idxict2 = [i for i, val in enumerate(meas) if name in val].pop()
        chg2 = float(meas[idxict2 + self.INDICES.CURR]) * 1e9
        ave2 = float(meas[idxict2 + self.INDICES.AVG]) * 1e9
        min2 = float(meas[idxict2 + self.INDICES.MIN]) * 1e9
        max2 = float(meas[idxict2 + self.INDICES.MAX]) * 1e9
        std2 = float(meas[idxict2 + self.INDICES.STD]) * 1e9
        cnt2 = int(float(meas[idxict2 + self.INDICES.COUNT]))

        eff = 100 * chg2/chg1
        effave = 100 * ave2/ave1

        self.run_callbacks(self.ICT1 + ':Charge-Mon', chg1)
        self.run_callbacks(self.ICT1 + ':ChargeAvg-Mon', ave1)
        self.run_callbacks(self.ICT1 + ':ChargeMin-Mon', min1)
        self.run_callbacks(self.ICT1 + ':ChargeMax-Mon', max1)
        self.run_callbacks(self.ICT1 + ':ChargeStd-Mon', std1)
        self.run_callbacks(self.ICT1 + ':PulseCount-Mon', cnt1)
        self.run_callbacks(self.ICT2 + ':Charge-Mon', chg2)
        self.run_callbacks(self.ICT2 + ':ChargeAvg-Mon', ave2)
        self.run_callbacks(self.ICT2 + ':ChargeMin-Mon', min2)
        self.run_callbacks(self.ICT2 + ':ChargeMax-Mon', max2)
        self.run_callbacks(self.ICT2 + ':ChargeStd-Mon', std2)
        self.run_callbacks(self.ICT2 + ':PulseCount-Mon', cnt2)
        if chg1 <= 0.05:
            return
        name = self.ACC + '-Glob:AP-CurrInfo:'
        self.run_callbacks(name + 'TranspEff-Mon', eff)
        self.run_callbacks(name + 'TranspEffAvg-Mon', effave)


class LICurrInfoApp(_ASCurrInfoApp):
    """."""

    OSC_IP = 'scope-dig-linac-ict'
    ACC = 'LI'
    ICT1 = 'LI-01:DI-ICT-1'
    ICT2 = 'LI-01:DI-ICT-2'


class TBCurrInfoApp(_ASCurrInfoApp):
    """."""

    OSC_IP = 'scope-dig-linac-ict'
    ACC = 'TB'
    ICT1 = 'TB-02:DI-ICT'
    ICT2 = 'TB-04:DI-ICT'


class TSCurrInfoApp(_ASCurrInfoApp):
    """."""

    OSC_IP = 'scope-dig-fctdig'
    ACC = 'TS'
    ICT1 = 'TS-01:DI-ICT'
    ICT2 = 'TS-04:DI-ICT'


class BOCurrInfoApp(_Callback):
    """Main Class."""

    def __init__(self):
        """Class constructor."""
        super().__init__()

        # consts
        self._pvs_database = _get_database('BO')
        self._DCCT = 'BO-35D:DI-DCCT'

        # initialize vars
        self._samplecnt = None
        self._measperiod = None
        self._reliablemeas = None
        self._last_raw_reading = None

        currthold_db = self._pvs_database['CurrThold-SP']
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
            data = _get_value_from_arch('BO-Glob:AP-CurrInfo:'+ppty)
            if data is None:
                charge = 0.0
            else:
                charge = data[1][0]
            self._charges[k] = charge

        data = _get_value_from_arch(
            'BO-Glob:AP-CurrInfo:IntCurrent3GeV-Mon')
        if data is None:
            self._intcurrent3gev = 0.0
        else:
            self._intcurrent3gev = data[1][0]

        # PVs
        self._rawreadings_pv = _PV(
            _vaca_prefix+self._DCCT+':RawReadings-Mon',
            connection_timeout=0.05, callback=self._callback_get_rawreadings,
            auto_monitor=True)
        self._samplecnt_pv = _PV(
            _vaca_prefix+self._DCCT+':FastSampleCnt-RB',
            connection_timeout=0.05, callback=self._callback_get_samplecnt)
        self._measperiod_pv = _PV(
            _vaca_prefix+self._DCCT+':FastMeasPeriod-RB',
            connection_timeout=0.05, callback=self._callback_get_measperiod)
        self._reliablemeas_pv = _PV(
            _vaca_prefix+self._DCCT+':ReliableMeas-Mon',
            connection_timeout=0.05, callback=self._callback_get_reliablemeas)

    def init_database(self):
        """."""
        for k in BO_ENERGY2TIME.keys():
            ppty = 'Charge'+k+'-Mon'
            self.run_callbacks(ppty, self._charges[k])
        self.run_callbacks('IntCurrent3GeV-Mon', self._intcurrent3gev)

    @property
    def pvs_database(self):
        """."""
        return _dcopy(self._pvs_database)

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        _ = reason
        return None

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'CurrThold-SP':
            if self._currthold_lolim < value < self._currthold_hilim:
                self._currthold = value
                self.run_callbacks('CurrThold-RB', value)
                status = True
        return status

    def close(self):
        """."""

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
        self.run_callbacks('RawReadings-Mon', value)

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
                self.run_callbacks('Current'+str(energy)+'-Mon',
                                   self._currents[energy])
                # charges
                self._charges[energy] += current * BO_REV_PERIOD
                self.run_callbacks('Charge'+str(energy)+'-Mon',
                                   self._charges[energy])

        c150mev = self._currents['150MeV']
        c3gev = self._currents['3GeV']

        # integrated current in 3GeV
        self._intcurrent3gev += c3gev * INTCURR_INTVL  # [mA.h]
        self.run_callbacks('IntCurrent3GeV-Mon', self._intcurrent3gev)

        # ramp efficiency
        if c150mev > c3gev:
            self._rampeff = 100*c3gev/c150mev
            self.run_callbacks('RampEff-Mon', self._rampeff)


class SICurrInfoApp(_Callback):
    """Main Class."""

    def __init__(self):
        """Class constructor."""
        super().__init__()
        self._pvs_database = _get_database('SI')

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
        data = _get_value_from_arch('SI-Glob:AP-CurrInfo:Charge-Mon')
        if data is None:
            self._charge = 0.0
        else:
            self._charge = data[1][0]

        # pvs
        self._current_13C4_pv = _PV(
            _vaca_prefix+'SI-13C4:DI-DCCT:Current-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_dcct_current)
        self._current_14C4_pv = _PV(
            _vaca_prefix+'SI-14C4:DI-DCCT:Current-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_dcct_current)
        self._storedebeam_13C4_pv = _PV(
            _vaca_prefix+'SI-13C4:DI-DCCT:StoredEBeam-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_storedebeam)
        self._storedebeam_14C4_pv = _PV(
            _vaca_prefix+'SI-14C4:DI-DCCT:StoredEBeam-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_storedebeam)
        self._reliablemeas_13C4_pv = _PV(
            _vaca_prefix+'SI-13C4:DI-DCCT:ReliableMeas-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_reliablemeas)
        self._reliablemeas_14C4_pv = _PV(
            _vaca_prefix+'SI-14C4:DI-DCCT:ReliableMeas-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_reliablemeas)
        self._dipole_opmode_pv = _PV(
            _vaca_prefix+'SI-Fam:PS-B1B2-1:OpMode-Sts',
            connection_timeout=0.05,
            callback=self._callback_get_dipole_opmode)
        self._bo_curr3gev_pv = _PV(
            _vaca_prefix+'BO-Glob:AP-CurrInfo:Current3GeV-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_bo_curr3gev)

        self._current_13C4_buffer = _SiriusPVTimeSerie(
            pv=self._current_13C4_pv, time_window=0.4, use_pv_timestamp=False)
        self._current_14C4_buffer = _SiriusPVTimeSerie(
            pv=self._current_14C4_pv, time_window=0.4, use_pv_timestamp=False)

    def init_database(self):
        """Set initial PV values."""
        self.run_callbacks('Charge-Mon', self._charge)

    @property
    def pvs_database(self):
        """."""
        return _dcopy(self._pvs_database)

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
                self.run_callbacks('Charge-Mon', self._charge)
                value = self._charge
            self._time0 = timestamp
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'DCCT-Sel':
            if self._dcctfltcheck_mode == _Const.DCCTFltCheck.Off:
                self._update_dcct_mode(value)
                self.run_callbacks('DCCT-Sts', self._dcct_mode)
                status = True
        elif reason == 'DCCTFltCheck-Sel':
            self._update_dcctfltcheck_mode(value)
            self.run_callbacks('DCCTFltCheck-Sts', self._dcctfltcheck_mode)
            status = True
        return status

    def close(self):
        """."""

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
            self.run_callbacks('DCCT-Sts', self._dcct_mode)

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
        self.run_callbacks('Current-Mon', self._current_value)

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
        self.run_callbacks('StoredEBeam-Mon', self._storedebeam_value)

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
        self._injeff = 100*(delta_curr/value)*(SI_HARMNUM/BO_HARMNUM)

        # update pvs
        self.run_callbacks('InjEff-Mon', self._injeff)

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
