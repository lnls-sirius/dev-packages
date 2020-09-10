"""."""

import time as _time

import numpy as _np

from mathphys.functions import get_namedtuple as _get_namedtuple

from .device import Device as _Device, Devices as _Devices


class BbB(_Devices):
    """BbB Device."""

    _devices = {
        'H': 'SI-Glob:DI-BbBProc-H',
        'V': 'SI-Glob:DI-BbBProc-V',
        'L': 'SI-Glob:DI-BbBProc-L'}
    DEVICES = _get_namedtuple('Devices', *zip(*_devices.items()))

    def __init__(self, devname):
        """."""
        devname = BbB.process_device_name(devname)
        self.sram = AcqProc(devname, acqtype='SRAM')
        self.bram = AcqProc(devname, acqtype='BRAM')
        self.fbe = FrontBackEnd()
        self.coeffs = CoeffProc(devname)

        devs = [self.sram, self.bram, self.fbe, self.coeffs]
        super().__init__(devname, devices=devs)

    # @property
    # def version(self):
    #     """."""
    #     return self['REVISION']

    # @property
    # def output_delay(self):
    #     """."""
    #     return self['DELAY']

    # @output_delay.setter
    # def output_delay(self, value):
    #     self['DELAY'] = value

    # @property
    # def info_rffreq(self):
    #     """."""
    #     return self['RF_FREQ']

    # @property
    # def info_harmnum(self):
    #     """."""
    #     return self['HARM_NUM']

    # @property
    # def proc_downsample(self):
    #     """."""
    #     return self['PROC_DS']

    # @proc_downsample.setter
    # def proc_downsample(self, value):
    #     self['PROC_DS'] = int(value)

    @staticmethod
    def process_device_name(devname):
        """Check whether device exist."""
        if devname in BbB.DEVICES:
            devname = devname
        elif devname in BbB.DEVICES._fields:
            devname = BbB.DEVICES[BbB.DEVICES._fields.index(devname)]
        else:
            raise NotImplementedError(devname)
        return devname


class CoeffProc(_Device):
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
        devname = BbB.process_device_name(devname)

        # call base class constructor
        super().__init__(devname, properties=CoeffProc._properties)

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


class _ProptyDevice(_Device):

    def __init__(self, devname, propty_prefix, properties):
        """."""
        self._propty_prefix = propty_prefix
        # call base class constructor
        super().__init__(devname, properties=properties)

    def _get_pvname(self, devname, propty):
        if devname:
            func = devname.substitute
            pvname = func(propty=self._propty_prefix + propty)
        else:
            pvname = self._propty_prefix + propty
        return pvname


class AcqProc(_ProptyDevice):
    """."""

    ACQTYPE = _get_namedtuple('Devices', ('SRAM', 'BRAM'))

    _properties = (
        'GDTIME', 'HOLDTIME', 'POSTTIME', 'ACQTIME',
        'REC_DS', 'POSTSEL', 'ACQ_EN', 'ACQ_SINGLE',
        'EXTEN', 'TRIG_IN_SEL', 'ARM', 'ARM_MON', 'BR_ARM',
        'DUMP', 'RAW_SAMPLES', 'RAW', 'ACQ_TURNS', 'POST_TURNS',
        'MEAN', 'RMS', 'XSC', 'SPEC', 'MAXRMS', 'TSC', 'FREQ',
        'MASK', 'ACQ_PATTERN',
        'SP_LOW1', 'SP_HIGH1', 'SP_SEARCH1', 'SP_PEAKFREQ1', 'SP_PEAK1',
        'SP_LOW2', 'SP_HIGH2', 'SP_SEARCH2', 'SP_PEAKFREQ2', 'SP_PEAK2',
        )

    DEF_TIMEOUT = 10  # [s]
    OFF, ON = 0, 1
    FPGA_BITS = 2**15

    def __init__(self, devname, acqtype='BRAM'):
        """."""
        devname = BbB.process_device_name(devname)
        acqtype = AcqProc.process_acquisition_type(acqtype)

        # call base class constructor
        super().__init__(
            devname, propty_prefix=acqtype+'_', properties=AcqProc._properties)

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
        return self['RAW']

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

    def cmd_data_dump(self):
        """."""
        self['DUMP'] = 1

    def wait_data_dump(self, timeout=None):
        """."""
        timeout = timeout or AcqProc.DEF_TIMEOUT
        interval = 0.050  # [s]
        ntrials = int(timeout/interval)
        _time.sleep(10*interval)
        for _ in range(ntrials):
            if not self['DUMP']:
                break
            _time.sleep(interval)
        else:
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
        return self['MASK']

    @spec_mask.setter
    def spec_mask(self, value):
        self['MASK'] = _np.array(value)

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
        return self['SP_PEAKFREQ1']

    @property
    def spec_marker1_mag(self):
        """."""
        return self['SP_PEAK1']

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
        return self['SP_PEAKFREQ2']

    @property
    def spec_marker2_mag(self):
        """."""
        return self['SP_PEAK2']

    @staticmethod
    def process_acquisition_type(acqtype):
        """."""
        if acqtype in AcqProc.ACQTYPE:
            acqtype = AcqProc.ACQTYPE._fields[acqtype]
        elif acqtype in AcqProc.ACQTYPE._fields:
            acqtype = acqtype
        else:
            raise NotImplementedError(acqtype)
        return acqtype


class FrontBackEnd(_Device):
    """."""

    _properties = (
        'FBE_Z_ATT', 'FBE_Z_PHASE', 'FBELT_SERVO_SETPT',
        'FBE_BE_ATT', 'FBE_BE_PHASE',
        'FBE_X_ATT', 'FBE_X_PHASE', 'FBELT_X_PHASE_SETPT',
        'FBE_Y_ATT', 'FBE_Y_PHASE', 'FBELT_Y_PHASE_SETPT',
        )

    DEF_TIMEOUT = 10  # [s]
    OFF, ON = 0, 1
    FPGA_BITS = 2**15

    def __init__(self):
        """."""
        # call base class constructor
        super().__init__(BbB.DEVICES.L, properties=FrontBackEnd._properties)

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
