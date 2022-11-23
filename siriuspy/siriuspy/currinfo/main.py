"""Main Module of the IOC Logic."""

import time as _time
from datetime import datetime as _datetime
import logging as _log
from copy import deepcopy as _dcopy
from threading import Thread as _Thread

import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from ..callbacks import Callback as _Callback
from ..epics import SiriusPVTimeSerie as _SiriusPVTimeSerie, PV as _PV
from ..envars import VACA_PREFIX as _vaca_prefix
from ..clientarch import ClientArchiver as _ClientArch
from ..pwrsupply.csdev import Const as _PSc
from ..search import LLTimeSearch as _LLTimeSearch

from .csdev import Const as _Const, \
    get_currinfo_database as _get_database


class _CurrInfoApp(_Callback):
    """."""

    def __init__(self):
        """."""
        super().__init__()
        self._pvs_database = None

    def init_database(self):
        """."""

    @property
    def pvs_database(self):
        """."""
        return _dcopy(self._pvs_database)

    def process(self, interval):
        """."""
        _time.sleep(interval)

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

    @staticmethod
    def _get_value_from_arch(pvname):
        carch = _ClientArch()
        datetime = _datetime.now().isoformat() + '-03:00'
        return carch.getData(pvname, datetime, datetime)


class _ASCurrInfoApp(_CurrInfoApp):
    """."""

    INDICES = _get_namedtuple(
        'Indices',
        ('NAME', 'CURR', 'AVG', 'MIN', 'MAX', 'STD', 'COUNT'))

    OSC_IP = 'scope-dig-linac-ict'
    ACC = ''
    ICT1 = ''
    ICT2 = ''
    CHARGE_THRESHOLD = 0.05  # [nC]

    def __init__(self, resource_manager):
        super().__init__()
        self._pvs_database = _get_database(self.ACC)
        self._meas = None
        self.resource_manager = resource_manager
        # open communication with Oscilloscope
        self.osc_socket = resource_manager.open_resource(
            'TCPIP::'+self.OSC_IP+'::inst0::INSTR')

    def close(self):
        """."""
        self.osc_socket.close()

    def process(self, interval):
        """."""
        tini = _time.time()
        self._get_measurement()
        self._update_pvs(self.ACC, self.ICT1, self.ICT2)
        dtim = _time.time() - tini
        if dtim <= interval:
            _time.sleep(interval - dtim)
        else:
            _log.warning(
                'IOC took {0:.3f} ms in update loop.'.format(dtim*1000))

    def _get_measurement(self):
        try:
            meas = self.osc_socket.query(":MEASure:RESults?")
            self._meas = meas.split(',')
        except Exception as err:
            errst = str(err)
            _log.error('Problem reading data: {:s}'.format(errst))
            if 'wrong xid in reply' in errst:
                # NOTE: this is a workaround suggested in
                # https://github.com/pyvisa/pyvisa-py/issues/172
                # for a similar problem.
                _log.info('Trying to fix error, reseting lastxid...')
                xid = int(errst.split()[4])
                rsman = self.resource_manager
                soc = self.osc_socket
                rsman.visalib.sessions[soc.session].interface.lastxid = xid
            self._meas = None
            return

    def _update_pvs(self, acc, ict1, ict2):
        """."""
        meas = self._meas
        if meas is None:
            return
        name = acc + '-ICT1'
        idxict1 = [i for i, val in enumerate(meas) if name in val].pop()
        chg1 = float(meas[idxict1 + self.INDICES.CURR]) * 1e9
        ave1 = float(meas[idxict1 + self.INDICES.AVG]) * 1e9
        min1 = float(meas[idxict1 + self.INDICES.MIN]) * 1e9
        max1 = float(meas[idxict1 + self.INDICES.MAX]) * 1e9
        std1 = float(meas[idxict1 + self.INDICES.STD]) * 1e9
        cnt1 = int(float(meas[idxict1 + self.INDICES.COUNT]))

        name = acc + '-ICT2'
        idxict2 = [i for i, val in enumerate(meas) if name in val].pop()
        chg2 = float(meas[idxict2 + self.INDICES.CURR]) * 1e9
        ave2 = float(meas[idxict2 + self.INDICES.AVG]) * 1e9
        min2 = float(meas[idxict2 + self.INDICES.MIN]) * 1e9
        max2 = float(meas[idxict2 + self.INDICES.MAX]) * 1e9
        std2 = float(meas[idxict2 + self.INDICES.STD]) * 1e9
        cnt2 = int(float(meas[idxict2 + self.INDICES.COUNT]))

        eff = 0 if chg1 == 0 else min(100 * chg2/chg1, 110)
        effave = 0 if ave1 == 0 else 100 * ave2/ave1

        self.run_callbacks(ict1 + ':Charge-Mon', chg1)
        self.run_callbacks(ict1 + ':ChargeAvg-Mon', ave1)
        self.run_callbacks(ict1 + ':ChargeMin-Mon', min1)
        self.run_callbacks(ict1 + ':ChargeMax-Mon', max1)
        self.run_callbacks(ict1 + ':ChargeStd-Mon', std1)
        self.run_callbacks(ict1 + ':PulseCount-Mon', cnt1)
        self.run_callbacks(ict2 + ':Charge-Mon', chg2)
        self.run_callbacks(ict2 + ':ChargeAvg-Mon', ave2)
        self.run_callbacks(ict2 + ':ChargeMin-Mon', min2)
        self.run_callbacks(ict2 + ':ChargeMax-Mon', max2)
        self.run_callbacks(ict2 + ':ChargeStd-Mon', std2)
        self.run_callbacks(ict2 + ':PulseCount-Mon', cnt2)
        if chg1 <= self.CHARGE_THRESHOLD:
            return
        name = acc + '-Glob:AP-CurrInfo:'
        self.run_callbacks(name + 'TranspEff-Mon', eff)
        self.run_callbacks(name + 'TranspEffAvg-Mon', effave)


class TSCurrInfoApp(_ASCurrInfoApp):
    """."""

    OSC_IP = 'as-di-fctdig'
    ACC = 'TS'
    ICT1 = 'TS-01:DI-ICT'
    ICT2 = 'TS-04:DI-ICT'


class LICurrInfoApp(_ASCurrInfoApp):
    """Linac IOC will Also provide TB PVs."""

    OSC_IP = 'li-di-ictosc'
    ACC = 'LI'
    LIICT1 = 'LI-01:DI-ICT-1'
    LIICT2 = 'LI-01:DI-ICT-2'
    TBICT1 = 'TB-02:DI-ICT'
    TBICT2 = 'TB-04:DI-ICT'

    def _update_pvs(self, *args):
        super()._update_pvs('LI', self.LIICT1, self.LIICT2)
        super()._update_pvs('TB', self.TBICT1, self.TBICT2)


class BOCurrInfoApp(_CurrInfoApp):
    """Main Class."""

    HARMNUM = 828
    INTCURR_INTVL = 53.5 * 1e-3 / 3600  # [h]
    MAX_CURRENT = 1.0  # [A]
    ENERGY2TIME = {  # energy: time[s]
        '150MeV': 0.0000,
        '1GeV': 0.0859,
        '2GeV': 0.1863,
        '3GeV': 0.2750}

    def __init__(self):
        """Class constructor."""
        super().__init__()

        # consts
        self._pvs_database = _get_database('BO')
        self._prefix = _vaca_prefix + ('-' if _vaca_prefix else '')
        self._dcct = 'BO-35D:DI-DCCT'

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
        for k in self.ENERGY2TIME:
            # currents
            self._currents[k] = 0.0
            # charges
            ppty = 'Charge'+k+'-Mon'
            data = self._get_value_from_arch('BO-Glob:AP-CurrInfo:'+ppty)
            if data is None:
                charge = 0.0
            else:
                charge = data['value'][0]
            self._charges[k] = charge

        data = self._get_value_from_arch(
            'BO-Glob:AP-CurrInfo:IntCurrent3GeV-Mon')
        if data is None:
            self._intcurrent3gev = 0.0
        else:
            self._intcurrent3gev = data['value'][0]

        # PVs
        self._rawreadings_pv = _PV(
            self._prefix+self._dcct+':RawReadings-Mon',
            connection_timeout=0.05, callback=self._callback_get_rawreadings,
            auto_monitor=True)
        self._samplecnt_pv = _PV(
            self._prefix+self._dcct+':FastSampleCnt-RB',
            connection_timeout=0.05, callback=self._callback_get_samplecnt)
        self._measperiod_pv = _PV(
            self._prefix+self._dcct+':FastMeasPeriod-RB',
            connection_timeout=0.05, callback=self._callback_get_measperiod)
        self._reliablemeas_pv = _PV(
            self._prefix+self._dcct+':ReliableMeas-Mon',
            connection_timeout=0.05, callback=self._callback_get_reliablemeas)
        self._rffreq_pv = _PV(
            self._prefix+'RF-Gen:GeneralFreq-RB', connection_timeout=0.05)

    def init_database(self):
        """Set initial PV values."""
        for k in self.ENERGY2TIME:
            ppty = 'Charge'+k+'-Mon'
            self.run_callbacks(ppty, self._charges[k])
            ppty = 'Current'+k+'-Mon'
            self.run_callbacks(ppty, self._currents[k])
        self.run_callbacks('RawReadings-Mon', self._last_raw_reading)
        self.run_callbacks('IntCurrent3GeV-Mon', self._intcurrent3gev)

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'CurrThold-SP':
            if self._currthold_lolim < value < self._currthold_hilim:
                self._currthold = value
                self.run_callbacks('CurrThold-RB', value)
                status = True
        return status

    # ----- callbacks -----

    def _callback_get_samplecnt(self, value, **kws):
        """Get SampleCnt-RB value."""
        _ = kws
        self._samplecnt = value

    def _callback_get_measperiod(self, value, **kws):
        """Get MeasPeriod-RB value."""
        _ = kws
        self._measperiod = value

    def _callback_get_reliablemeas(self, value, **kws):
        """Get ReliableMeas-Mon value."""
        _ = kws
        self._reliablemeas = value

    def _callback_get_rawreadings(self, value, **kws):
        _ = kws
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
        time_offset = self.ENERGY2TIME['3GeV'] + 0.0250
        idx_offset = _np.where(_np.isclose(times, time_offset, atol=0.0005))[0]
        try:
            samples_offset = self._last_raw_reading[idx_offset[0]:]
            offset = _np.mean(samples_offset)
        except (IndexError, TypeError):
            offset = 0.0

        # update pvs
        for energy, time in self.ENERGY2TIME.items():
            idx = _np.where(_np.isclose(times, time, atol=0.0005))[0]
            if idx.size:
                # currents
                current = self._last_raw_reading[idx[0]] - offset
                if current < self._currthold:
                    current = 0.0
                self._currents[energy] = current
                self.run_callbacks('Current'+str(energy)+'-Mon',
                                   self._currents[energy])
                # charges
                if current < self.MAX_CURRENT:
                    self._charges[energy] += \
                        1e6 * current * self.HARMNUM / self._rffreq_pv.value
                    if energy == '3GeV':
                        self._intcurrent3gev += \
                            current * self.INTCURR_INTVL  # [mA.h]
                        self.run_callbacks(
                            'IntCurrent3GeV-Mon', self._intcurrent3gev)
                else:
                    _log.warning(
                        'Current {0} value is too high: '
                        '{1:.3g}A.'.format(energy, current))
                self.run_callbacks('Charge'+str(energy)+'-Mon',
                                   self._charges[energy])

        c150mev = self._currents['150MeV']
        c3gev = self._currents['3GeV']

        # ramp efficiency
        if c150mev > c3gev:
            self._rampeff = 100*c3gev/c150mev
            self.run_callbacks('RampEff-Mon', self._rampeff)


class SICurrInfoApp(_CurrInfoApp):
    """Main Class."""

    HARMNUM = 864
    HARMNUM_RATIO = 864 / 828
    CURR_THRESHOLD = 0.02  # [mA]
    MAX_CURRENT = 1.0  # [A]

    def __init__(self):
        """Class constructor."""
        super().__init__()
        self._pvs_database = _get_database('SI')
        self._prefix = _vaca_prefix + ('-' if _vaca_prefix else '')

        # initialize vars
        self._time0 = _time.time()
        self._thread = None
        self._current_value = 0
        self._current_13c4_value = None
        self._current_14c4_value = None
        self._dcct_mode = _Const.DCCT.DCCT13C4
        self._dcctfltcheck_mode = _Const.DCCTFltCheck.Off
        self._reliablemeas_13c4_value = 0
        self._reliablemeas_14c4_value = 0
        self._storedebeam_value = 0
        self._storedebeam_13c4_value = 0
        self._storedebeam_14c4_value = 0
        self._is_cycling = False
        self._injeff = 0.0
        self._injcurr = 0.0
        self._injcharge = 0.0
        self._injcount = 0
        data = self._get_value_from_arch('SI-Glob:AP-CurrInfo:Charge-Mon')
        if data is None:
            self._charge = 0.0
        else:
            self._charge = data['value'][0]

        # pvs
        self._current_13c4_pv = _PV(
            self._prefix+'SI-13C4:DI-DCCT:Current-Mon',
            connection_timeout=0.05)
        self._current_14c4_pv = _PV(
            self._prefix+'SI-14C4:DI-DCCT:Current-Mon',
            connection_timeout=0.05)
        self._storedebeam_13c4_pv = _PV(
            self._prefix+'SI-13C4:DI-DCCT:StoredEBeam-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_storedebeam)
        self._storedebeam_14c4_pv = _PV(
            self._prefix+'SI-14C4:DI-DCCT:StoredEBeam-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_storedebeam)
        self._reliablemeas_13c4_pv = _PV(
            self._prefix+'SI-13C4:DI-DCCT:ReliableMeas-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_reliablemeas)
        self._reliablemeas_14c4_pv = _PV(
            self._prefix+'SI-14C4:DI-DCCT:ReliableMeas-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_reliablemeas)
        self._dipole_opmode_pv = _PV(
            self._prefix+'SI-Fam:PS-B1B2-1:OpMode-Sts',
            connection_timeout=0.05,
            callback=self._callback_get_dipole_opmode)
        self._bo_curr3gev_pv = _PV(
            self._prefix+'BO-Glob:AP-CurrInfo:Current3GeV-Mon',
            connection_timeout=0.05)
        self._ti_injcount_pv = _PV(
            self._prefix+_LLTimeSearch.get_evg_name()+':InjCount-Mon',
            connection_timeout=0.05,
            callback=self._callback_get_injcount)
        self._eg_trigps_pv = _PV(
            self._prefix+'LI-01:EG-TriggerPS:status',
            connection_timeout=0.05)
        self._rffreq_pv = _PV(
            self._prefix+'RF-Gen:GeneralFreq-RB', connection_timeout=0.05)

        self._current_13c4_buffer = _SiriusPVTimeSerie(
            pv=self._current_13c4_pv, time_window=0.5, use_pv_timestamp=False)
        self._current_14c4_buffer = _SiriusPVTimeSerie(
            pv=self._current_14c4_pv, time_window=0.5, use_pv_timestamp=False)

        self._current_13c4_pv.add_callback(self._callback_get_dcct_current)
        self._current_14c4_pv.add_callback(self._callback_get_dcct_current)
        self._bo_curr3gev_pv.add_callback(self._callback_get_bo_curr3gev)

    def init_database(self):
        """Set initial PV values."""
        self.run_callbacks(
            'SI-Glob:AP-CurrInfo:StoredEBeam-Mon', self._storedebeam_value)
        self.run_callbacks(
            'SI-Glob:AP-CurrInfo:Current-Mon', self._current_value)
        self.run_callbacks(
            'SI-Glob:AP-CurrInfo:InjEff-Mon', self._injeff)
        self.run_callbacks(
            'SI-Glob:AP-CurrInfo:Charge-Mon', self._charge)
        self.run_callbacks(
            'AS-Glob:AP-CurrInfo:InjCount-Mon', self._injcount)
        self.run_callbacks(
            'SI-Glob:AP-CurrInfo:InjCurr-Mon', self._injcurr)
        self.run_callbacks(
            'SI-Glob:AP-CurrInfo:InjCharge-Mon', self._injcharge)

    def read(self, reason):
        """Read from IOC database."""
        value = None
        if 'Charge' in reason:
            timestamp = _time.time()
            if self._storedebeam_value and not self._is_cycling:
                dtm = (timestamp - self._time0)  # Delta t [s]
                current = self._current_value/1000  # Current [A]
                if current < self.MAX_CURRENT:
                    inc_charge = current*dtm/3600  # Charge [A.h]
                    self._charge += inc_charge
                    self.run_callbacks(
                        'SI-Glob:AP-CurrInfo:Charge-Mon', self._charge)
                else:
                    _log.warning(
                        'Current value is too high: {0:.3f}A.'.format(current))
                value = self._charge
            self._time0 = timestamp
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'SI-Glob:AP-CurrInfo:DCCT-Sel':
            if self._dcctfltcheck_mode == _Const.DCCTFltCheck.Off:
                done = self._update_dcct_mode(value)
                if done:
                    self.run_callbacks(
                        'SI-Glob:AP-CurrInfo:DCCT-Sts', self._dcct_mode)
                    status = True
        elif reason == 'SI-Glob:AP-CurrInfo:DCCTFltCheck-Sel':
            self._update_dcctfltcheck_mode(value)
            self.run_callbacks(
                'SI-Glob:AP-CurrInfo:DCCTFltCheck-Sts',
                self._dcctfltcheck_mode)
            status = True
        return status

    # ----- handle writes -----
    def _update_dcct_mode(self, value):
        if self._dcct_mode == value:
            return False
        if value in [_Const.DCCT.DCCT13C4, _Const.DCCT.DCCT14C4]:
            self._dcct_mode = value
            return True
        return False

    def _update_dcct_mode_by_relblmeas(self):
        if self._reliablemeas_13c4_value == 0:
            mode = _Const.DCCT.DCCT13C4
        elif self._reliablemeas_14c4_value == 0:
            mode = _Const.DCCT.DCCT14C4
        else:
            mode = self._dcct_mode
        if mode != self._dcct_mode:
            self._dcct_mode = mode
            self.run_callbacks('SI-Glob:AP-CurrInfo:DCCT-Sts', self._dcct_mode)

    def _update_dcctfltcheck_mode(self, value):
        if self._dcctfltcheck_mode != value:
            if value == _Const.DCCTFltCheck.On:
                self._update_dcct_mode_by_relblmeas()
            self._dcctfltcheck_mode = value

    # ----- callbacks -----
    def _callback_get_dcct_current(self, pvname, value, **kws):
        _ = kws
        if '13C4' in pvname:
            self._current_13c4_value = value
            self._current_13c4_buffer.acquire()
        elif '14C4' in pvname:
            self._current_14c4_value = value
            self._current_14c4_buffer.acquire()

        # update current and charge
        current = self._get_current()
        if current is None:
            return
        self._current_value = current

        # update pvs
        self.run_callbacks(
            'SI-Glob:AP-CurrInfo:Current-Mon', self._current_value)

    def _callback_get_storedebeam(self, pvname, value, **kws):
        _ = kws
        if '13C4' in pvname:
            self._storedebeam_13c4_value = value
        elif '14C4' in pvname:
            self._storedebeam_14c4_value = value

        if self._dcct_mode == _Const.DCCT.DCCT13C4:
            self._storedebeam_value = self._storedebeam_13c4_value
        elif self._dcct_mode == _Const.DCCT.DCCT14C4:
            self._storedebeam_value = self._storedebeam_14c4_value
        self.run_callbacks(
            'SI-Glob:AP-CurrInfo:StoredEBeam-Mon', self._storedebeam_value)

    def _callback_get_reliablemeas(self, pvname, value, **kws):
        _ = kws
        if '13C4' in pvname:
            self._reliablemeas_13c4_value = value
        elif '14C4' in pvname:
            self._reliablemeas_14c4_value = value

        if self._dcctfltcheck_mode == _Const.DCCTFltCheck.On:
            self._update_dcct_mode_by_relblmeas()

    def _callback_get_dipole_opmode(self, value, **kws):
        _ = kws
        self._is_cycling = bool(value == _PSc.States.Cycle)

    def _callback_get_bo_curr3gev(self, value, timestamp, **kws):
        """Get BO Current3GeV-Mon and update InjEff PV."""
        _ = value
        _ = kws
        _ = timestamp
        self._thread = _Thread(target=self._update_injeff, daemon=True)
        self._thread.start()

    def _callback_get_injcount(self, value, **kws):
        _ = kws
        if value == 0:
            self._injcount = 0
        else:
            if self._eg_trigps_pv.value:
                self._injcount += 1
        self.run_callbacks('AS-Glob:AP-CurrInfo:InjCount-Mon', self._injcount)

    def _update_injeff(self):
        # Sleep some time here to ensure SI DCCT will have been updated
        _time.sleep(0.21)

        # get booster current
        bo_curr = self._bo_curr3gev_pv.value

        # choose current PV
        if self._dcct_mode == _Const.DCCT.DCCT13C4:
            buffer = self._current_13c4_buffer
        else:
            buffer = self._current_14c4_buffer
        timestamp_dq, value_dq = buffer.serie
        timestamp_dq = _np.asarray(timestamp_dq)
        value_dq = _np.asarray(value_dq)

        # check buffer not empty
        if not timestamp_dq.size:
            return

        # check if there is valid current in Booster
        if bo_curr < self.CURR_THRESHOLD:
            return

        # calculate efficiency
        self._injcurr = value_dq.max() - value_dq.min()  # mA
        self._injeff = 100*(self._injcurr/bo_curr) * self.HARMNUM_RATIO

        # calculate injected charge: 1e6 * mA / Hz = nC
        self._injcharge = 1e6*self._injcurr*self.HARMNUM/self._rffreq_pv.value

        # update pvs
        self.run_callbacks('SI-Glob:AP-CurrInfo:InjEff-Mon', self._injeff)
        self.run_callbacks('SI-Glob:AP-CurrInfo:InjCurr-Mon', self._injcurr)
        self.run_callbacks(
            'SI-Glob:AP-CurrInfo:InjCharge-Mon', self._injcharge)

    # ----- auxiliar methods -----

    def _get_current(self):
        if self._dcct_mode == _Const.DCCT.DCCT13C4:
            current = self._current_13c4_value
        elif self._dcct_mode == _Const.DCCT.DCCT14C4:
            current = self._current_14c4_value
        return current
