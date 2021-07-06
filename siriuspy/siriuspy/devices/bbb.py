"""."""

import time as _time

import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from ..namesys import SiriusPVName as _PVName

from .device import Device as _Device, Devices as _Devices, \
    ProptyDevice as _ProptyDevice
from .dcct import DCCT
from .rf import RFCav


class BunchbyBunch(_Devices):
    """BunchbyBunch Device."""

    _devices = {
        'H': 'SI-Glob:DI-BbBProc-H',
        'V': 'SI-Glob:DI-BbBProc-V',
        'L': 'SI-Glob:DI-BbBProc-L'}
    DEVICES = _get_namedtuple('Devices', *zip(*_devices.items()))

    def __init__(self, devname):
        """."""
        devname = BunchbyBunch.process_device_name(devname)
        self.dcct = DCCT(DCCT.DEVICES.SI_13C4)
        self.rfcav = RFCav(RFCav.DEVICES.SI)
        self.info = SystemInfo(devname)
        self.timing = Timing(devname)
        self.sram = Acquisition(devname, acqtype='SRAM')
        self.bram = Acquisition(devname, acqtype='BRAM')
        self.single_bunch = SingleBunch(devname)
        self.phase_track = PhaseTracking(devname)
        self.coeffs = Coefficients(devname)
        self.feedback = Feedback(devname)
        self.drive = Drive(devname)
        self.bunch_clean = BunchClean(devname)
        self.fbe = FrontBackEnd()
        devs = [
            self.info, self.timing, self.sram, self.bram, self.coeffs,
            self.feedback, self.drive, self.bunch_clean, self.fbe, self.dcct,
            self.rfcav, self.single_bunch, self.phase_track]

        if devname.endswith('-L'):
            self.pwr_amp1 = PwrAmpL(devname, num=0)
            self.pwr_amp2 = PwrAmpL(devname, num=1)
            devs.append(self.pwr_amp1)
            devs.append(self.pwr_amp2)
        else:
            self.pwr_amp = PwrAmpT(devname)
            devs.append(self.pwr_amp)

        super().__init__(devname, devices=devs)

    @staticmethod
    def process_device_name(devname):
        """Check whether device exist."""
        if devname in BunchbyBunch.DEVICES:
            devname = devname
        elif devname in BunchbyBunch.DEVICES._fields:
            devname = BunchbyBunch.DEVICES[
                BunchbyBunch.DEVICES._fields.index(devname)]
        else:
            raise NotImplementedError(devname)
        return _PVName(devname)

    def sweep_phase_shifter(self, values, wait=2, mon_type='mean'):
        """Sweep Servo Phase for each `value` in `values`."""
        mon_values = []
        ctrl, mon = 'FBE Out Phase', 'SRAM Mean'
        print(f'Idx: {ctrl:15s} {mon:15s}')

        if self.devname.endswith('L'):
            propty = 'FBELT_SERVO_SETPT'
        elif self.devname.endswith('H'):
            propty = 'FBELT_X_PHASE_SETPT'
        else:
            propty = 'FBELT_Y_PHASE_SETPT'

        init_val = self.fbe[propty]
        for i, val in enumerate(values):
            self.fbe[propty] = val
            self.fbe._wait(propty, val)
            _time.sleep(wait)
            if mon_type.lower() in 'mean':
                mon_val = self.sram.data_mean
            else:
                mon_val = self.sram.spec_marker1_mag
            mon_values.append(mon_val)
            print(f'{i:03d}: {val:15.6f} {_np.mean(mon_val):15.6f}')
        self.fbe[propty] = init_val
        return _np.array(mon_values)

    def sweep_adc_delay(self, values, wait=2, mon_type='mean'):
        """Sweep ADC Delay for each `value` in `values`."""
        mon_values = []
        ctrl, mon = 'ADC Delay', 'SRAM Mean'
        print(f'Idx: {ctrl:15s} {mon:15s}')

        init_val = self.timing.adc_delay
        for i, val in enumerate(values):
            self.timing.adc_delay = val
            self.timing._wait('TADC', val)
            _time.sleep(wait)
            if mon_type.lower() in 'mean':
                mon_val = self.sram.data_mean
            else:
                mon_val = self.sram.spec_marker1_mag
            mon_values.append(mon_val)
            print(f'{i:03d}: {val:15.6f} {_np.mean(mon_val):15.6f}')
        self.timing.adc_delay = init_val
        return _np.array(mon_values)

    def sweep_backend_phase(self, values, wait=2, mon_type='peak'):
        """Sweep Backend Phase for each `value` in `values`."""
        mon_values = []
        ctrl, mon = 'Backend Phase', 'Peak magnitude'
        print(f'Idx: {ctrl:15s} {mon:15s}')

        init_val = self.fbe.be_phase
        for i, val in enumerate(values):
            self.fbe.be_phase = val
            self.fbe._wait('FBE_BE_PHASE', val)
            _time.sleep(wait)
            if mon_type.lower() in 'peak':
                mon_val = self.sram.spec_marker1_mag
            else:
                mon_val = self.sram.data_rms
            mon_values.append(mon_val)
            print(f'{i:03d}: {val:15.6f} {_np.mean(mon_val):15.6f}')
        self.fbe.be_phase = init_val
        return _np.array(mon_values)

    def sweep_dac_delay(self, values, wait=2, mon_type='peak'):
        """Sweep DAC Delay for each `value` in `values`."""
        mon_values = []
        ctrl, mon = 'DAC Delay', 'Peak Magnitude'
        print(f'Idx: {ctrl:15s} {mon:15s}')

        init_val = self.timing.dac_delay
        for i, val in enumerate(values):
            self.timing.dac_delay = val
            self.timing._wait('TDAC', val)
            _time.sleep(wait)
            if mon_type.lower() in 'peak':
                mon_val = self.sram.spec_marker1_mag
            else:
                mon_val = self.sram.data_rms
            mon_values.append(mon_val)
            print(f'{i:03d}: {val:15.6f} {_np.mean(mon_val):15.6f}')
        self.timing.dac_delay = init_val
        return _np.array(mon_values)

    def sweep_feedback_phase(self, values, wait=2, mon_type='peak'):
        """Sweep Feedback Phase for each `value` in `values`."""
        mon_values = []
        ctrl, mon = 'Coeff. Phase', 'Peak Magnitude'
        print(f'Idx: {ctrl:15s} {mon:15s}')

        init_val = self.coeffs.edit_phase
        for i, val in enumerate(values):
            self.coeffs.edit_phase = val
            self.coeffs.cmd_edit_apply()
            _time.sleep(wait)
            if mon_type.lower() in 'peak':
                mon_val = self.sram.spec_marker1_mag
            else:
                mon_val = self.sram.data_rms
            mon_values.append(mon_val)
            print(f'{i:03d}: {val:15.6f} {_np.mean(mon_val):15.6f}')
        self.coeffs.edit_phase = init_val
        self.coeffs.cmd_edit_apply()
        return _np.array(mon_values)

    def sweep_rf_phase(self, values, wait=2, mon_type='mean'):
        """Sweep RF Phase for each `value` in `values`."""
        mon_values = []
        ctrl, mon = 'RF Phase', 'SRAM Mean'
        print(f'Idx: {ctrl:15s} {mon:15s}')

        llrf = self.rfcav.dev_llrf
        init_val = llrf.phase
        for i, val in enumerate(values):
            self.rfcav.set_phase(val)
            _time.sleep(wait)
            if mon_type.lower() in 'mean':
                mon_val = self.sram.data_mean
            else:
                mon_val = self.sram.spec_marker1_mag
            mon_values.append(mon_val)
            print(f'{i:03d}: {val:15.6f} {_np.mean(mon_val):15.6f}')
        llrf.value = init_val
        return _np.array(mon_values)


class SystemInfo(_Device):
    """."""

    _properties = (
        'ERRSUM', 'CLKMISS', 'CLKMISS_COUNT', 'PLL_UNLOCK',
        'PLL_UNLOCK_COUNT', 'DCM_UNLOCK', 'DCM_UNLOCK_COUNT', 'ADC_OVR',
        'ADC_OVR_COUNT', 'SAT', 'SAT_COUNT', 'FID_ERR', 'FID_ERR_COUNT',
        'RST_COUNT', 'CNTRST', 'RF_FREQ', 'HARM_NUM', 'REVISION', 'GW_TYPE',
        'IP_ADDR')

    def __init__(self, devname):
        """."""
        devname = BunchbyBunch.process_device_name(devname)

        # call base class constructor
        super().__init__(devname, properties=SystemInfo._properties)

    @property
    def status(self):
        """."""
        return self['ERRSUM']

    @property
    def clock_miss(self):
        """."""
        return self['CLKMISS']

    @property
    def clock_miss_count(self):
        """."""
        return self['CLKMISS_COUNT']

    @property
    def pll_unlock(self):
        """."""
        return self['PLL_UNLOCK']

    @property
    def pll_unlock_count(self):
        """."""
        return self['PLL_UNLOCK_COUNT']

    @property
    def dcm_unlock(self):
        """."""
        return self['DCM_UNLOCK']

    @property
    def dcm_unlock_count(self):
        """."""
        return self['DCM_UNLOCK_COUNT']

    @property
    def adc_overrange(self):
        """."""
        return self['ADC_OVR']

    @property
    def adc_overrange_count(self):
        """."""
        return self['ADC_OVR_COUNT']

    @property
    def output_saturated(self):
        """."""
        return self['SAT']

    @property
    def output_saturated_count(self):
        """."""
        return self['SAT_COUNT']

    @property
    def fiducial_error(self):
        """."""
        return self['FID_ERR']

    @property
    def fiducial_error_count(self):
        """."""
        return self['FID_ERR_COUNT']

    @property
    def time_since_last_reset(self):
        """."""
        return self['RST_COUNT']

    def cmd_reset_counts(self):
        """."""
        self['CNTRST'] = 1
        _time.sleep(0.2)
        self['CNTRST'] = 0

    @property
    def rf_freq_nom(self):
        """."""
        return self['RF_FREQ'] * 1e6

    @property
    def harmonic_number(self):
        """."""
        return self['HARM_NUM']

    @property
    def gateway_revision(self):
        """."""
        return self['REVISION']

    @property
    def gateway_type(self):
        """."""
        return self['GW_TYPE']

    @property
    def ip_address(self):
        """."""
        return self['IP_ADDR']


class Timing(_Device):
    """."""

    _properties = (
        'TADC', 'TDAC', 'DELAY', 'OFF_FIDS', 'FID_DELAY', 'CLKRST',
        'FREQ_CNT_CH0', 'FREQ_CNT_CH1', 'FREQ_CNT_CH2', 'FREQ_CNT_CH3',
        'FREQ_CNT_CH4',
        'ECLDEL0', 'ECLDEL1', 'ECLDEL2', 'ECLDEL3',
        'ECLDEL0_SUBWR', 'ECLDEL1_SUBWR', 'ECLDEL2_SUBWR', 'ECLDEL3_SUBWR',
        )

    def __init__(self, devname):
        """."""
        devname = BunchbyBunch.process_device_name(devname)

        # call base class constructor
        super().__init__(devname, properties=Timing._properties)

    @property
    def adc_delay(self):
        """."""
        return self['TADC']

    @adc_delay.setter
    def adc_delay(self, value):
        self['TADC'] = value

    @property
    def dac_delay(self):
        """."""
        return self['TDAC']

    @dac_delay.setter
    def dac_delay(self, value):
        self['TDAC'] = value

    @property
    def output_delay(self):
        """."""
        return self['DELAY']

    @output_delay.setter
    def output_delay(self, value):
        self['DELAY'] = value

    @property
    def fiducial_offset(self):
        """."""
        return self['OFF_FIDS']

    @fiducial_offset.setter
    def fiducial_offset(self, value):
        self['OFF_FIDS'] = int(value)

    @property
    def fiducial_delay(self):
        """."""
        return self['FID_DELAY']

    @fiducial_delay.setter
    def fiducial_delay(self, value):
        self['FID_DELAY'] = value

    def cmd_reset_clock(self):
        """."""
        self['CLKRST'] = 1
        _time.sleep(0.2)
        self['CLKRST'] = 0

    @property
    def adc_clock(self):
        """."""
        return self['ECLDEL0']

    @adc_clock.setter
    def adc_clock(self, value):
        self['ECLDEL0'] = int(value)

    @property
    def fiducial_clock(self):
        """."""
        return self['ECLDEL1']

    @fiducial_clock.setter
    def fiducial_clock(self, value):
        self['ECLDEL1'] = int(value)

    @property
    def fiducial(self):
        """."""
        return self['ECLDEL2']

    @fiducial.setter
    def fiducial(self, value):
        self['ECLDEL2'] = int(value)

    @property
    def dac_clock(self):
        """."""
        return self['ECLDEL3']

    @dac_clock.setter
    def dac_clock(self, value):
        self['ECLDEL3'] = int(value)

    @property
    def adc_clock_ok(self):
        """."""
        return self['ECLDEL0_SUBWR']

    @property
    def fiducial_clock_ok(self):
        """."""
        return self['ECLDEL1_SUBWR']

    @property
    def fiducial_ok(self):
        """."""
        return self['ECLDEL2_SUBWR']

    @property
    def dac_clock_ok(self):
        """."""
        return self['ECLDEL3_SUBWR']

    @property
    def freq_input_clock(self):
        """."""
        return self['FREQ_CNT_CH0']

    @property
    def freq_rf_over_2(self):
        """."""
        return self['FREQ_CNT_CH1']

    @property
    def freq_rf_over_3(self):
        """."""
        return self['FREQ_CNT_CH2']

    @property
    def freq_dac_clock(self):
        """."""
        return self['FREQ_CNT_CH3']

    @property
    def freq_rf_over_4(self):
        """."""
        return self['FREQ_CNT_CH4']


class Coefficients(_Device):
    """."""

    _properties = (
        'CSET0', 'CSET1', 'CSET2', 'CSET3', 'COEFF',
        'DESC_CSET0', 'DESC_CSET1', 'DESC_CSET2', 'DESC_CSET3', 'DESC_COEFF',
        'CVERIFY.C', 'CVERIFY.D', 'CVERIFY.G', 'CVERIFY.H',
        'LDSET', 'BO_CVERIFY', 'BO_CPCOEFF',
        'FLT_GAIN', 'FLT_FREQ', 'FLT_PHASE', 'FLT_TAPS',
        'FTF_MAG', 'FTF_PHASE', 'FTF_FREQ',
        'FTF_TUNE', 'FTF_GTUNE', 'FTF_PTUNE',
        )

    DEF_TIMEOUT = 10  # [s]
    OFF, ON = 0, 1
    FPGA_BITS = 2**15

    def __init__(self, devname):
        """."""
        devname = BunchbyBunch.process_device_name(devname)

        # call base class constructor
        super().__init__(devname, properties=Coefficients._properties)

    @property
    def set0(self):
        """."""
        return self['CSET0']/self.FPGA_BITS

    @set0.setter
    def set0(self, value):
        self['CSET0'] = _np.array(value) * self.FPGA_BITS

    @property
    def set1(self):
        """."""
        return self['CSET1'] / self.FPGA_BITS

    @set1.setter
    def set1(self, value):
        self['CSET1'] = _np.array(value) * self.FPGA_BITS

    @property
    def set2(self):
        """."""
        return self['CSET2'] / self.FPGA_BITS

    @set2.setter
    def set2(self, value):
        self['CSET2'] = _np.array(value) * self.FPGA_BITS

    @property
    def set3(self):
        """."""
        return self['CSET3'] / self.FPGA_BITS

    @set3.setter
    def set3(self, value):
        self['CSET3'] = _np.array(value) * self.FPGA_BITS

    @property
    def set0_desc(self):
        """."""
        return self['DESC_CSET0']

    @property
    def set1_desc(self):
        """."""
        return self['DESC_CSET1']

    @property
    def set2_desc(self):
        """."""
        return self['DESC_CSET2']

    @property
    def set3_desc(self):
        """."""
        return self['DESC_CSET3']

    @property
    def set0_status(self):
        """."""
        return self['CVERIFY.C']

    @property
    def set1_status(self):
        """."""
        return self['CVERIFY.D']

    @property
    def set2_status(self):
        """."""
        return self['CVERIFY.G']

    @property
    def set3_status(self):
        """."""
        return self['CVERIFY.H']

    @property
    def edit_choose_set(self):
        """."""
        return self['LDSET']

    @edit_choose_set.setter
    def edit_choose_set(self, value):
        """."""
        self['LDSET'] = value

    @property
    def edit_set(self):
        """."""
        return self['COEFF'] / self.FPGA_BITS

    @edit_set.setter
    def edit_set(self, value):
        """."""
        self['COEFF'] = _np.array(value) * self.FPGA_BITS

    @property
    def edit_set_desc(self):
        """."""
        return self['DESC_COEFF']

    @property
    def edit_set_status(self):
        """."""
        return self['BO_CVERIFY']

    @property
    def edit_ftf_magnitude(self):
        """."""
        return self['FTF_MAG']

    @property
    def edit_ftf_phase(self):
        """."""
        return self['FTF_PHASE']

    @property
    def edit_ftf_freq(self):
        """."""
        return self['FTF_FREQ']

    @property
    def edit_marker_freq(self):
        """."""
        return self['FTF_TUNE']

    @property
    def edit_marker_mag(self):
        """."""
        return self['FTF_GTUNE'][0]

    @property
    def edit_marker_phase(self):
        """."""
        return self['FTF_PTUNE'][0]

    @property
    def edit_gain(self):
        """."""
        return self['FLT_GAIN']

    @edit_gain.setter
    def edit_gain(self, value):
        """."""
        self['FLT_GAIN'] = value

    @property
    def edit_freq(self):
        """."""
        return self['FLT_FREQ']

    @edit_freq.setter
    def edit_freq(self, value):
        """."""
        self['FLT_FREQ'] = value

    @property
    def edit_phase(self):
        """."""
        return self['FLT_PHASE']

    @edit_phase.setter
    def edit_phase(self, value):
        """."""
        self['FLT_PHASE'] = value

    @property
    def edit_nrpoints(self):
        """."""
        return self['FLT_TAPS']

    @edit_nrpoints.setter
    def edit_nrpoints(self, value):
        """."""
        self['FLT_TAPS'] = value

    def cmd_edit_apply(self):
        """."""
        self['BO_CPCOEFF'] = 1

    def cmd_edit_verify(self):
        """."""
        self['BO_CVERIFY'] = 1


class Acquisition(_ProptyDevice):
    """."""

    ACQTYPE = _get_namedtuple('Devices', ('SRAM', 'BRAM'))

    _properties = (
        'GDTIME', 'HOLDTIME', 'POSTTIME', 'ACQTIME',
        'REC_DS', 'POSTSEL', 'ACQ_EN', 'ACQ_SINGLE',
        'EXTEN', 'TRIG_IN_SEL', 'ARM', 'ARM_MON', 'BR_ARM',
        'DUMP', 'RAW_SAMPLES', 'RAW', 'ACQ_TURNS', 'POST_TURNS',
        'MEAN', 'RMS', 'XSC', 'SPEC', 'MAXRMS', 'TSC', 'FREQ',
        'ACQ_MASK', 'ACQ_PATTERN',
        'SP_LOW1', 'SP_HIGH1', 'SP_SEARCH1', 'PEAKFREQ1', 'PEAK1',
        'SP_LOW2', 'SP_HIGH2', 'SP_SEARCH2', 'PEAKFREQ2', 'PEAK2',
        )

    DEF_TIMEOUT = 10  # [s]

    def __init__(self, devname, acqtype='BRAM'):
        """."""
        devname = BunchbyBunch.process_device_name(devname)
        acqtype = Acquisition.process_acquisition_type(acqtype)

        # call base class constructor
        super().__init__(
            devname, propty_prefix=acqtype+'_',
            properties=Acquisition._properties)

    # ########### Acquisition Config Properties ###########
    @property
    def acq_type(self):
        """."""
        return self['POSTSEL']

    @acq_type.setter
    def acq_type(self, value):
        self['POSTSEL'] = value

    @property
    def acq_enbl(self):
        """."""
        return self['ACQ_EN']

    @acq_enbl.setter
    def acq_enbl(self, value):
        self['ACQ_EN'] = value

    @property
    def acq_mode(self):
        """."""
        return self['ACQ_SINGLE']

    @acq_mode.setter
    def acq_mode(self, value):
        self['ACQ_SINGLE'] = value

    @property
    def growthtime(self):
        """."""
        return self['GDTIME']

    @growthtime.setter
    def growthtime(self, value):
        self['GDTIME'] = value

    @property
    def acqtime(self):
        """."""
        return self['ACQTIME']

    @acqtime.setter
    def acqtime(self, value):
        self['ACQTIME'] = value

    @property
    def holdtime(self):
        """."""
        return self['HOLDTIME']

    @holdtime.setter
    def holdtime(self, value):
        self['HOLDTIME'] = value

    @property
    def posttime(self):
        """."""
        return self['POSTTIME']

    @posttime.setter
    def posttime(self, value):
        self['POSTTIME'] = value

    @property
    def downsample(self):
        """."""
        return self['REC_DS']

    @downsample.setter
    def downsample(self, value):
        self['REC_DS'] = value

    # ########### Trigger Properties ###########
    @property
    def trigger_type(self):
        """."""
        return self['EXTEN']

    @trigger_type.setter
    def trigger_type(self, value):
        self['EXTEN'] = value

    @property
    def trigger_sel(self):
        """."""
        return self['TRIG_IN_SEL']

    @trigger_sel.setter
    def trigger_sel(self, value):
        self['TRIG_IN_SEL'] = value

    @property
    def trigger_armed(self):
        """."""
        return self['ARM_MON']

    @trigger_armed.setter
    def trigger_armed(self, value):
        self['ARM'] = value

    @property
    def trigger_rearm(self):
        """."""
        return self['BR_ARM']

    @trigger_rearm.setter
    def trigger_rearm(self, value):
        self['BR_ARM'] = value

    # ########### Data Properties ###########
    @property
    def data_size(self):
        """."""
        return self['RAW_SAMPLES']

    @data_size.setter
    def data_size(self, value):
        self['RAW_SAMPLES'] = value

    @property
    def data_raw(self):
        """."""
        data = self['RAW']
        size = self.data_size
        if size is not None:
            data = data[:size]
        return data

    @property
    def data_bunch_index(self):
        """."""
        return self['XSC']

    @property
    def data_mean(self):
        """."""
        return self['MEAN']

    @property
    def data_rms(self):
        """."""
        return self['RMS']

    @property
    def data_nrturns(self):
        """."""
        return self['ACQ_TURNS']

    @property
    def data_nrturns_posttriger(self):
        """."""
        return self['POST_TURNS']

    def cmd_data_acquire(self, timeout=None):
        """."""
        self.acq_enbl = 1
        if timeout is None:
            timeout = Acquisition.DEF_TIMEOUT
        if timeout > 0:
            self._wait('ACQ_EN', 1, timeout=timeout)

    def cmd_data_dump(self, timeout=None):
        """."""
        self['DUMP'] = 1
        if timeout is None:
            timeout = Acquisition.DEF_TIMEOUT
        if timeout > 0:
            self.wait_data_dump(timeout)

    def wait_data_dump(self, timeout=None):
        """."""
        timeout = timeout or Acquisition.DEF_TIMEOUT
        if not self._wait('DUMP', False, timeout=timeout):
            print('WARN: Timed out waiting data dump.')

    # ########### Spectrometer Properties ###########
    @property
    def spec_mag(self):
        """."""
        return self['SPEC']

    @property
    def spec_freq(self):
        """."""
        return self['FREQ']

    @property
    def spec_data(self):
        """."""
        return self['MAXRMS']

    @property
    def spec_time(self):
        """."""
        return self['TSC']

    @property
    def spec_mask(self):
        """."""
        return self['ACQ_MASK']

    @spec_mask.setter
    def spec_mask(self, value):
        self['ACQ_MASK'] = _np.array(value)

    @property
    def spec_mask_pattern(self):
        """."""
        return self['ACQ_PATTERN']

    @spec_mask_pattern.setter
    def spec_mask_pattern(self, value):
        self['ACQ_PATTERN'] = str(value)

    @property
    def spec_marker1_freq_min(self):
        """."""
        return self['SP_LOW1']

    @spec_marker1_freq_min.setter
    def spec_marker1_freq_min(self, value):
        self['SP_LOW1'] = value

    @property
    def spec_marker1_freq_max(self):
        """."""
        return self['SP_HIGH1']

    @spec_marker1_freq_max.setter
    def spec_marker1_freq_max(self, value):
        self['SP_HIGH1'] = value

    @property
    def spec_marker1_search_mode(self):
        """."""
        return self['SP_SEARCH1']

    @spec_marker1_search_mode.setter
    def spec_marker1_search_mode(self, value):
        self['SP_SEARCH1'] = value

    @property
    def spec_marker1_freq(self):
        """."""
        return self['PEAKFREQ1']

    @property
    def spec_marker1_mag(self):
        """."""
        return self['PEAK1']

    @property
    def spec_marker2_freq_min(self):
        """."""
        return self['SP_LOW2']

    @spec_marker2_freq_min.setter
    def spec_marker2_freq_min(self, value):
        self['SP_LOW2'] = value

    @property
    def spec_marker2_freq_max(self):
        """."""
        return self['SP_HIGH2']

    @spec_marker2_freq_max.setter
    def spec_marker2_freq_max(self, value):
        self['SP_HIGH2'] = value

    @property
    def spec_marker2_search_mode(self):
        """."""
        return self['SP_SEARCH2']

    @spec_marker2_search_mode.setter
    def spec_marker2_search_mode(self, value):
        self['SP_SEARCH2'] = value

    @property
    def spec_marker2_freq(self):
        """."""
        return self['PEAKFREQ2']

    @property
    def spec_marker2_mag(self):
        """."""
        return self['PEAK2']

    @staticmethod
    def process_acquisition_type(acqtype):
        """."""
        if acqtype in Acquisition.ACQTYPE:
            acqtype = Acquisition.ACQTYPE._fields[acqtype]
        elif acqtype in Acquisition.ACQTYPE._fields:
            acqtype = acqtype
        else:
            raise NotImplementedError(acqtype)
        return acqtype


class SingleBunch(_ProptyDevice):
    """."""

    _properties = (
        'ACQTIME', 'ACQ_SAMPLES', 'ACQ_EN', 'ACQ_SINGLE',
        'BUNCH_ID', 'RAW_BUNCH_ID',
        'EXTEN', 'TRIG_IN_SEL', 'ARM', 'ARM_MON', 'BR_ARM',
        'RAW_SAMPLES', 'TSC', 'RAW', 'FREQ', 'MAG', 'PHASE', 'TF_ENABLE',
        'NFFT', 'NOVERLAP', 'DEL_CAL', 'SP_AVG',
        'MEANVAL', 'RMSVAL', 'AMP_PP',
        'SP_LOW1', 'SP_HIGH1', 'PEAKFREQ1', 'PEAK1', 'SP_SEARCH1', 'PHASE1',
        )

    DEF_TIMEOUT = 10  # [s]

    def __init__(self, devname):
        """."""
        devname = BunchbyBunch.process_device_name(devname)

        # call base class constructor
        super().__init__(
            devname, propty_prefix='SB_', properties=SingleBunch._properties)

    @property
    def acqtime(self):
        """."""
        return self['ACQTIME']

    @acqtime.setter
    def acqtime(self, value):
        self['ACQTIME'] = value

    @property
    def acq_enbl(self):
        """."""
        return self['ACQ_EN']

    @acq_enbl.setter
    def acq_enbl(self, value):
        self['ACQ_EN'] = value

    @property
    def acq_mode(self):
        """."""
        return self['ACQ_SINGLE']

    @acq_mode.setter
    def acq_mode(self, value):
        self['ACQ_SINGLE'] = value

    @property
    def bunch_id(self):
        """."""
        return self['RAW_BUNCH_ID']

    @bunch_id.setter
    def bunch_id(self, value):
        self['BUNCH_ID'] = value

    # ########### Trigger Properties ###########
    @property
    def trigger_type(self):
        """."""
        return self['EXTEN']

    @trigger_type.setter
    def trigger_type(self, value):
        self['EXTEN'] = value

    @property
    def trigger_sel(self):
        """."""
        return self['TRIG_IN_SEL']

    @trigger_sel.setter
    def trigger_sel(self, value):
        self['TRIG_IN_SEL'] = value

    @property
    def trigger_armed(self):
        """."""
        return self['ARM_MON']

    @trigger_armed.setter
    def trigger_armed(self, value):
        self['ARM'] = value

    @property
    def trigger_rearm(self):
        """."""
        return self['BR_ARM']

    @trigger_rearm.setter
    def trigger_rearm(self, value):
        self['BR_ARM'] = value

    # ########### Data Properties ###########
    @property
    def data_size(self):
        """."""
        return self['RAW_SAMPLES']

    @data_size.setter
    def data_size(self, value):
        self['RAW_SAMPLES'] = value

    @property
    def data_raw(self):
        """."""
        data = self['RAW']
        size = self.data_size
        if size is not None:
            data = data[:size]
        return data

    @property
    def data_time(self):
        """."""
        return self['TSC']

    ##
    @property
    def fft_size(self):
        """."""
        return self['NFFT']

    @fft_size.setter
    def fft_size(self, value):
        self['NFFT'] = value

    @property
    def fft_overlap(self):
        """."""
        return self['NOVERLAP']

    @fft_overlap.setter
    def fft_overlap(self, value):
        self['NOVERLAP'] = value

    @property
    def delay_calibration(self):
        """."""
        return self['DEL_CAL']

    @delay_calibration.setter
    def delay_calibration(self, value):
        self['DEL_CAL'] = value

    @property
    def nr_averages(self):
        """."""
        return self['SP_AVG']

    @nr_averages.setter
    def nr_averages(self, value):
        self['SP_AVG'] = value

    @property
    def transfer_function_enable(self):
        """."""
        return self['TF_ENABLE']

    @transfer_function_enable.setter
    def transfer_function_enable(self, value):
        self['TF_ENABLE'] = value

    @property
    def amplitude_mean(self):
        """."""
        return self['MEANVAL']

    @amplitude_mean.setter
    def amplitude_mean(self, value):
        self['MEANVAL'] = value

    @property
    def amplitude_rms(self):
        """."""
        return self['RMSVAL']

    @amplitude_rms.setter
    def amplitude_rms(self, value):
        self['RMSVAL'] = value

    @property
    def amplitude_pp(self):
        """."""
        return self['AMP_PP']

    @amplitude_pp.setter
    def amplitude_pp(self, value):
        self['AMP_PP'] = value

    @property
    def spec_mag(self):
        """."""
        return self['MAG']

    @property
    def spec_phase(self):
        """."""
        return self['PHASE']

    @property
    def spec_freq(self):
        """."""
        return self['FREQ']

    @property
    def spec_marker1_freq_min(self):
        """."""
        return self['SP_LOW1']

    @spec_marker1_freq_min.setter
    def spec_marker1_freq_min(self, value):
        self['SP_LOW1'] = value

    @property
    def spec_marker1_freq_max(self):
        """."""
        return self['SP_HIGH1']

    @spec_marker1_freq_max.setter
    def spec_marker1_freq_max(self, value):
        self['SP_HIGH1'] = value

    @property
    def spec_marker1_search_mode(self):
        """."""
        return self['SP_SEARCH1']

    @spec_marker1_search_mode.setter
    def spec_marker1_search_mode(self, value):
        self['SP_SEARCH1'] = value

    @property
    def spec_marker1_freq(self):
        """."""
        return self['PEAKFREQ1']

    @property
    def spec_marker1_mag(self):
        """."""
        return self['PEAK1']

    @property
    def spec_marker1_phase(self):
        """."""
        return self['PHASE1']

    def cmd_enable_transfer_function(self, timeout=DEF_TIMEOUT):
        self.transfer_function_enable = 1
        self._wait('TF_ENABLE', value=1, timeout=timeout)


class PhaseTracking(_ProptyDevice):
    """."""

    _properties = (
        'GAIN', 'SETPT', 'RANGE', 'DECIM', 'RATE', 'BANDWIDTH', 'LOOPCTRL',
        'MAG', 'TFGAIN', 'SHIFT', 'PHASE', 'ERROR', 'FREQ', 'TUNE')

    DEF_TIMEOUT = 10  # [s]

    def __init__(self, devname):
        """."""
        devname = BunchbyBunch.process_device_name(devname)

        # call base class constructor
        super().__init__(
            devname, propty_prefix='PHTRK_',
            properties=PhaseTracking._properties)

    @property
    def gain(self):
        """."""
        return self['GAIN']

    @gain.setter
    def gain(self, value):
        self['GAIN'] = value

    @property
    def setpoint(self):
        """Phase setpoint in degrees."""
        return self['SETPT']

    @setpoint.setter
    def setpoint(self, value):
        self['SETPT'] = value

    @property
    def range(self):
        """Frequency range in kHz."""
        return self['RANGE']

    @range.setter
    def range(self, value):
        self['RANGE'] = value

    @property
    def decimation(self):
        """."""
        return self['DECIM']

    @decimation.setter
    def decimation(self, value):
        self['DECIM'] = value

    @property
    def loop_state(self):
        """Loop State."""
        return self['LOOPCTRL']

    @loop_state.setter
    def loop_state(self, value):
        self['LOOPCTRL'] = value

    @property
    def rate(self):
        """."""
        return self['RATE']

    @property
    def bandwidth(self):
        """."""
        return self['BANDWIDTH']

    @property
    def magnitude(self):
        """."""
        return self['MAG']

    @property
    def transfer_gain(self):
        """."""
        return self['TFGAIN']

    @property
    def normalizing_shift(self):
        """."""
        return self['SHIFT']

    @property
    def phase(self):
        """Phase monitor in degrees."""
        return self['PHASE']

    @property
    def error(self):
        """Error in degrees."""
        return self['ERROR']

    @property
    def frequency(self):
        """."""
        return self['FREQ']

    @property
    def tune(self):
        """."""
        return self['TUNE']


class FrontBackEnd(_Device):
    """."""

    _properties = (
        'FBE_Z_ATT', 'FBE_Z_PHASE', 'FBELT_SERVO_SETPT',
        'FBE_BE_ATT', 'FBE_BE_PHASE',
        'FBE_X_ATT', 'FBE_X_PHASE', 'FBELT_X_PHASE_SETPT',
        'FBE_Y_ATT', 'FBE_Y_PHASE', 'FBELT_Y_PHASE_SETPT',
        )

    FPGA_BITS = 2**15

    def __init__(self):
        """."""
        # call base class constructor
        super().__init__(
            BunchbyBunch.DEVICES.L, properties=FrontBackEnd._properties)

    @property
    def z_att(self):
        """."""
        return self['FBE_Z_ATT']

    @z_att.setter
    def z_att(self, value):
        """."""
        self['FBE_Z_ATT'] = value

    @property
    def be_att(self):
        """."""
        return self['FBE_BE_ATT']

    @be_att.setter
    def be_att(self, value):
        """."""
        self['FBE_BE_ATT'] = value

    @property
    def x_att(self):
        """."""
        return self['FBE_X_ATT']

    @x_att.setter
    def x_att(self, value):
        """."""
        self['FBE_X_ATT'] = value

    @property
    def y_att(self):
        """."""
        return self['FBE_Y_ATT']

    @y_att.setter
    def y_att(self, value):
        """."""
        self['FBE_Y_ATT'] = value

    @property
    def z_phase(self):
        """."""
        return self['FBE_Z_PHASE']

    @z_phase.setter
    def z_phase(self, value):
        """."""
        self['FBELT_SERVO_SETPT'] = value

    @property
    def be_phase(self):
        """."""
        return self['FBE_BE_PHASE']

    @be_phase.setter
    def be_phase(self, value):
        """."""
        self['FBE_BE_PHASE'] = value

    @property
    def x_phase(self):
        """."""
        return self['FBE_X_PHASE']

    @x_phase.setter
    def x_phase(self, value):
        """."""
        self['FBELT_X_PHASE_SETPT'] = value

    @property
    def y_phase(self):
        """."""
        return self['FBE_Y_PHASE']

    @y_phase.setter
    def y_phase(self, value):
        """."""
        self['FBELT_Y_PHASE_SETPT'] = value


class Feedback(_Device):
    """."""

    _properties = (
        'PROC_DS', 'FBCTRL', 'SHIFTGAIN', 'SETSEL', 'SAT_THRESHOLD',
        'FB_MASK', 'FB_PATTERN', 'CF_MASK', 'CF_PATTERN',
        'CF_PATTERN_SUB.VALB', 'GDEN',
        )

    def __init__(self, devname):
        """."""
        devname = BunchbyBunch.process_device_name(devname)

        # call base class constructor
        super().__init__(devname, properties=Feedback._properties)

    @property
    def downsample(self):
        """."""
        return self['PROC_DS']

    @downsample.setter
    def downsample(self, value):
        self['PROC_DS'] = int(value)

    @property
    def loop_state(self):
        """."""
        return self['FBCTRL']

    @loop_state.setter
    def loop_state(self, value):
        self['FBCTRL'] = int(value)

    @property
    def shift_gain(self):
        """."""
        return self['SHIFTGAIN']

    @shift_gain.setter
    def shift_gain(self, value):
        self['SHIFTGAIN'] = int(value)

    @property
    def coeff_set(self):
        """."""
        return self['SETSEL']

    @coeff_set.setter
    def coeff_set(self, value):
        self['SETSEL'] = int(value)

    @property
    def saturation_threshold(self):
        """."""
        return self['SAT_THRESHOLD']

    @saturation_threshold.setter
    def saturation_threshold(self, value):
        self['SAT_THRESHOLD'] = value

    @property
    def mask(self):
        """."""
        return self['FB_MASK']

    @mask.setter
    def mask(self, value):
        self['FB_MASK'] = _np.array(value)

    @property
    def mask_pattern(self):
        """."""
        return self['FB_PATTERN']

    @mask_pattern.setter
    def mask_pattern(self, value):
        self['FB_PATTERN'] = str(value)

    @property
    def alternate_mask(self):
        """."""
        return self['CF_MASK']

    @alternate_mask.setter
    def alternate_mask(self, value):
        self['CF_MASK'] = _np.array(value)

    @property
    def alternate_mask_pattern(self):
        """."""
        return self['CF_PATTERN']

    @alternate_mask_pattern.setter
    def alternate_mask_pattern(self, value):
        self['CF_PATTERN'] = str(value)

    @property
    def alternate_nr_bunches(self):
        """."""
        return self['CF_PATTERN_SUB.VALB']

    @property
    def alternate_inuse(self):
        """."""
        return bool(self.alternate_nr_bunches)

    @property
    def grow_damp_state(self):
        """."""
        return self['GDEN']

    @grow_damp_state.setter
    def grow_damp_state(self, value):
        self['GDEN'] = int(value)


class Drive(_ProptyDevice):
    """."""

    _properties = (
        'MOD', 'AMPL', 'WAVEFORM', 'FREQ', 'FREQ_ACT', 'SPAN', 'SPAN_ACT',
        'PERIOD', 'PERIOD_ACT', 'MASK', 'PATTERN',
        )

    def __init__(self, devname):
        """."""
        devname = BunchbyBunch.process_device_name(devname)
        super().__init__(
            devname, propty_prefix='DRIVE_', properties=Drive._properties)

    @property
    def state(self):
        """."""
        return self['MOD']

    @state.setter
    def state(self, value):
        self['MOD'] = int(value)

    @property
    def waveform(self):
        """."""
        return self['WAVEFORM']

    @waveform.setter
    def waveform(self, value):
        self['WAVEFORM'] = int(value)

    @property
    def amplitude(self):
        """."""
        return self['AMPL']

    @amplitude.setter
    def amplitude(self, value):
        self['AMPL'] = value

    @property
    def frequency(self):
        """."""
        return self['FREQ_ACT']

    @frequency.setter
    def frequency(self, value):
        self['FREQ'] = value

    @property
    def span(self):
        """."""
        return self['SPAN_ACT']

    @span.setter
    def span(self, value):
        self['SPAN'] = value

    @property
    def period(self):
        """."""
        return self['PERIOD_ACT']

    @period.setter
    def period(self, value):
        self['PERIOD'] = value

    @property
    def mask(self):
        """."""
        return self['MASK']

    @mask.setter
    def mask(self, value):
        self['MASK'] = _np.array(value)

    @property
    def mask_pattern(self):
        """."""
        return self['PATTERN']

    @mask_pattern.setter
    def mask_pattern(self, value):
        self['PATTERN'] = str(value)


class BunchClean(_ProptyDevice):
    """."""

    _properties = (
        'ENABLE', 'AMPL', 'TUNE', 'PATTERN',
        )

    def __init__(self, devname):
        """."""
        devname = BunchbyBunch.process_device_name(devname)
        super().__init__(
            devname, propty_prefix='CLEAN_', properties=BunchClean._properties)

    @property
    def state(self):
        """."""
        return self['ENABLE']

    @state.setter
    def state(self, value):
        self['ENABLE'] = int(value)

    @property
    def amplitude(self):
        """."""
        return self['AMPL']

    @amplitude.setter
    def amplitude(self, value):
        self['AMPL'] = value

    @property
    def frequency(self):
        """."""
        return self['TUNE']

    @frequency.setter
    def frequency(self, value):
        self['TUNE'] = value

    @property
    def mask_pattern(self):
        """."""
        return self['PATTERN']

    @mask_pattern.setter
    def mask_pattern(self, value):
        self['PATTERN'] = str(value)


class PwrAmpL(_ProptyDevice):
    """."""

    _properties = ('FAULT', 'TEMP', 'FWDLOSS', 'REVLOSS', 'FWD', 'REV')

    DEF_TIMEOUT = 10  # [s]

    def __init__(self, devname, num=0):
        """."""
        devname = BunchbyBunch.process_device_name(devname)

        # call base class constructor
        super().__init__(
            devname, propty_prefix=f'MCLRAW_{num:d}_',
            properties=PwrAmpL._properties)

    @property
    def status(self):
        """."""
        return self['FAULT']

    @property
    def forward_loss(self):
        """."""
        return self['FWDLOSS']

    @forward_loss.setter
    def forward_loss(self, value):
        self['FWDLOSS'] = value

    @property
    def reverse_loss(self):
        """."""
        return self['REVLOSS']

    @reverse_loss.setter
    def reverse_loss(self, value):
        self['REVLOSS'] = value

    @property
    def forward(self):
        """."""
        return self['FWD']

    @property
    def reverse(self):
        """."""
        return self['REV']

    @property
    def temperature(self):
        """."""
        return self['TEMP']


class PwrAmpT(_Device):
    """."""

    _properties = (
        'Rst-Cmd', 'Enbl-Sts', 'Enbl-Sel', 'GainAuto-Sts', 'GainAuto-Sel',
        'Gain-SP', 'Gain-RB', 'GainStep-SP', 'GainStep-RB',
        )

    def __init__(self, devname):
        """."""
        devname = BunchbyBunch.process_device_name(devname)
        devname = devname.substitute(dev='BbBAmp'+devname.idx, idx='')

        # call base class constructor
        super().__init__(devname, properties=PwrAmpT._properties)

    @property
    def enable(self):
        """."""
        return self['Enbl-Sts']

    @enable.setter
    def enable(self, value):
        self['Enbl-Sel'] = int(value)

    @property
    def auto_gain(self):
        """."""
        return self['GainAuto-Sts']

    @auto_gain.setter
    def auto_gain(self, value):
        self['GainAuto-Sel'] = int(value)

    @property
    def gain(self):
        """."""
        return self['Gain-RB']

    @gain.setter
    def gain(self, value):
        self['Gain-SP'] = value

    @property
    def gain_step(self):
        """."""
        return self['GainStep-RB']

    @gain_step.setter
    def gain_step(self, value):
        self['GainStep-SP'] = value

    def cmd_reset(self):
        """."""
        self['Rst-Cmd'] = 1
        _time.sleep(0.2)
        self['Rst-Cmd'] = 0
