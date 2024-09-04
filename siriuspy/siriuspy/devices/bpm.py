"""BPM devices."""

import time as _time

import numpy as _np

from ..diagbeam.bpm.csdev import Const as _csbpm
from ..search import BPMSearch as _BPMSearch
from .device import Device as _Device

# from threading import Event as _Flag


class BPM(_Device):
    """BPM Device."""

    ACQSTATES_NOTOK = {
        _csbpm.AcqStates.Error, _csbpm.AcqStates.No_Memory,
        _csbpm.AcqStates.Bad_Post_Samples, _csbpm.AcqStates.No_Samples,
        _csbpm.AcqStates.Too_Many_Samples, _csbpm.AcqStates.Overflow}
    ACQSTATES_STARTED = {
        _csbpm.AcqStates.Waiting, _csbpm.AcqStates.External_Trig,
        _csbpm.AcqStates.Data_Trig, _csbpm.AcqStates.Software_Trig,
        _csbpm.AcqStates.Acquiring}
    ACQSTATES_FINISHED = {_csbpm.AcqStates.Idle}
    ACQSTATES_FINISHED |= ACQSTATES_NOTOK

    PROPERTIES_ACQ = (
        'INFOClkFreq-RB', 'INFOHarmonicNumber-RB', 'INFOTbTRate-RB',
        'INFOFOFBRate-RB', 'INFOMONITRate-RB', 'INFOFAcqRate-RB',
        'GENAmplAData', 'GENAmplBData', 'GENAmplCData', 'GENAmplDData',
        'GENPosXData', 'GENPosYData', 'GENSumData',
        'GENPosQData',
        'GENChannel-Sel', 'GENChannel-Sts',
        'GENShots-SP', 'GENShots-RB',
        'GENUpdateTime-SP', 'GENUpdateTime-RB',
        'GENSamplesPre-SP', 'GENSamplesPre-RB',
        'GENSamplesPost-SP', 'GENSamplesPost-RB',
        'GENTriggerEvent-Cmd',
        'GENStatus-Mon', 'GENCount-Mon',
        'GENTrigger-Sel', 'GENTrigger-Sts',
        'GENTriggerRep-Sel', 'GENTriggerRep-Sts',
        'GENDataTrigChan-Sel', 'GENDataTrigChan-Sts',
        'GENTriggerDataSel-SP', 'GENTriggerDataSel-RB',
        'GENTriggerDataThres-SP', 'GENTriggerDataThres-RB',
        'GENTriggerDataPol-Sel', 'GENTriggerDataPol-Sts',
        'GENTriggerDataHyst-SP', 'GENTriggerDataHyst-RB',
        )

    PROPERTIES_DEFAULT = PROPERTIES_ACQ + (
        'SwMode-Sel', 'SwMode-Sts',
        'RFFEAtt-SP', 'RFFEAtt-RB',
        'PosX-Mon', 'PosY-Mon', 'Sum-Mon', 'PosQ-Mon',
        'AmplA-Mon', 'AmplB-Mon', 'AmplC-Mon', 'AmplD-Mon',
        'GEN_PolyXArrayCoeff-SP', 'GEN_PolyXArrayCoeff-RB',
        'GEN_PolyYArrayCoeff-SP', 'GEN_PolyYArrayCoeff-RB',
        'GEN_PolySUMArrayCoeff-SP', 'GEN_PolySUMArrayCoeff-RB',
        'GEN_PolyQArrayCoeff-SP', 'GEN_PolyQArrayCoeff-RB',
        'SwDirGainA-SP', 'SwDirGainB-SP', 'SwDirGainC-SP', 'SwDirGainD-SP',
        'SwDirGainA-RB', 'SwDirGainB-RB', 'SwDirGainC-RB', 'SwDirGainD-RB',
        'SwInvGainA-SP', 'SwInvGainB-SP', 'SwInvGainC-SP', 'SwInvGainD-SP',
        'SwInvGainA-RB', 'SwInvGainB-RB', 'SwInvGainC-RB', 'SwInvGainD-RB',
        'PosKx-SP', 'PosKx-RB',
        'PosKy-RB', 'PosKy-SP',
        'PosKsum-SP', 'PosKsum-RB',
        'PosKq-SP', 'PosKq-RB',
        'PosXOffset-SP', 'PosXOffset-RB',
        'PosYOffset-SP', 'PosYOffset-RB',
        'PosQOffset-SP', 'PosQOffset-RB',
        'FOFBPhaseSyncEn-Sel', 'FOFBPhaseSyncEn-Sts', 'SwDivClk-RB',
        'TbTPhaseSyncEn-Sel', 'TbTPhaseSyncEn-Sts',
        'FAcqPhaseSyncEn-Sel', 'FAcqPhaseSyncEn-Sts',
        'MonitPhaseSyncEn-Sel', 'MonitPhaseSyncEn-Sts',
        'TbTDataMaskEn-Sel', 'TbTDataMaskEn-Sts',
        'TbTDataMaskSamplesBeg-SP', 'TbTDataMaskSamplesBeg-RB',
        'TbTDataMaskSamplesEnd-SP', 'TbTDataMaskSamplesEnd-RB',
        'XYPosCal-Sel', 'XYPosCal-Sts',
        'SumPosCal-Sel', 'SumPosCal-Sts',
        'QPosCal-Sel', 'QPosCal-Sts',
        )

    CONV_NM2UM = 1e-3  # [nm] --> [um]

    def __init__(
            self, devname, props2init='all', auto_monitor_mon=True,
            ispost_mortem=False):
        """."""
        # call base class constructor
        self._ispost_mortem = ispost_mortem

        if props2init == 'all' and _BPMSearch.is_photon_bpm(devname):
            props2init = set(BPM.PROPERTIES_DEFAULT)
            props2init -= {'RFFEAtt-SP', 'RFFEAtt-RB'}
            props2init = list(props2init)
        elif isinstance(props2init, str) and props2init.startswith('acq'):
            props2init = list(self.PROPERTIES_ACQ)

        super().__init__(
            devname, props2init=props2init, auto_monitor_mon=auto_monitor_mon)
        self.csdata = _csbpm

    def __str__(self):
        """."""
        stg = '################### Summary Status ###################\n'
        stg += '    Switching Mode: '
        stg += f'{_csbpm.SwModes._fields[self.switching_mode]:s}\n'
        stg += '\nAcquisition Parameters:\n'
        stg += f'    - Status: {_csbpm.AcqStates._fields[self.acq_status]:s}\n'
        stg += f'    - Channel: {_csbpm.AcqChan._fields[self.acq_channel]:s}\n'
        stg += f'    - Nr Shots: {self.acq_nrshots:d}\n'
        stg += f'    - Update Time: {self.acq_update_time:.1f} ms\n'
        stg += f'    - Repeat: {_csbpm.AcqRepeat._fields[self.acq_repeat]:s}\n'
        stg += '    - Trigger Type: '
        stg += f'{_csbpm.AcqTrigTyp._fields[self.acq_trigger]:s}\n'
        if self.acq_trigger == _csbpm.AcqTrigTyp.Data:
            stg += '        - Channel: '
            stg += f'{_csbpm.AcqChan._fields[self.acq_trig_datachan]:s}\n'
            stg += '        - Source: '
            stg += f'{_csbpm.AcqDataTyp._fields[self.acq_trig_datasel]:s}\n'
            stg += '        - Polarity: '
            stg += f'{_csbpm.Polarity._fields[self.acq_trig_datapol]:s}\n'
            stg += f'        - Threshold: {self.acq_trig_datathres:.1f}\n'
            stg += f'        - Hysteresis: {self.acq_trig_datahyst:d}\n'
        stg += '\n'
        return stg

    @property
    def is_ok(self):
        """."""
        okay = self.acq_status not in self.ACQSTATES_NOTOK
        return okay

    @property
    def rffe_att(self):
        """."""
        if 'RFFEAtt-RB' not in self._pvs:
            return None
        return self['RFFEAtt-RB']

    @rffe_att.setter
    def rffe_att(self, val):
        """."""
        if 'RFFEAtt-SP' in self._pvs:
            self['RFFEAtt-SP'] = val

    @property
    def switching_mode(self):
        """."""
        return self['SwMode-Sts']

    @switching_mode.setter
    def switching_mode(self, val):
        """."""
        self['SwMode-Sel'] = val

    @property
    def switching_mode_str(self):
        """."""
        return _csbpm.SwModes._fields[self.switching_mode]

    @property
    def switching_rate(self):
        """Switching rate manifested at BPM readings.

        NOTE: Actually this property maps the rate of the effect of
        switching on the orbit, which is twice the switching rate,
        because the switching has two states.

        """
        return self['SwDivClk-RB'] * 2

    @property
    def switching_period(self):
        """Switching period manifested at BPM readings."""
        return self.switching_rate / self.adcfreq

    @property
    def gain_direct_a(self):
        """."""
        return self['SwDirGainA-RB']

    @gain_direct_a.setter
    def gain_direct_a(self, val):
        self['SwDirGainA-SP'] = val

    @property
    def gain_direct_b(self):
        """."""
        return self['SwDirGainB-RB']

    @gain_direct_b.setter
    def gain_direct_b(self, val):
        self['SwDirGainB-SP'] = val

    @property
    def gain_direct_c(self):
        """."""
        return self['SwDirGainC-RB']

    @gain_direct_c.setter
    def gain_direct_c(self, val):
        self['SwDirGainC-SP'] = val

    @property
    def gain_direct_d(self):
        """."""
        return self['SwDirGainD-RB']

    @gain_direct_d.setter
    def gain_direct_d(self, val):
        self['SwDirGainD-SP'] = val

    @property
    def gain_inverse_a(self):
        """."""
        return self['SwInvGainA-RB']

    @gain_inverse_a.setter
    def gain_inverse_a(self, val):
        self['SwInvGainA-SP'] = val

    @property
    def gain_inverse_b(self):
        """."""
        return self['SwInvGainB-RB']

    @gain_inverse_b.setter
    def gain_inverse_b(self, val):
        self['SwInvGainB-SP'] = val

    @property
    def gain_inverse_c(self):
        """."""
        return self['SwInvGainC-RB']

    @gain_inverse_c.setter
    def gain_inverse_c(self, val):
        self['SwInvGainC-SP'] = val

    @property
    def gain_inverse_d(self):
        """."""
        return self['SwInvGainD-RB']

    @gain_inverse_d.setter
    def gain_inverse_d(self, val):
        self['SwInvGainD-SP'] = val

    @property
    def harmonic_number(self):
        """."""
        return self['INFOHarmonicNumber-RB']

    @property
    def adcfreq(self):
        """."""
        return self['INFOClkFreq-RB']

    @property
    def tbt_rate(self):
        """Divisor or TbT in relation to ADC."""
        return self['INFOTbTRate-RB']

    @property
    def tbt_period(self):
        """."""
        return self.tbt_rate / self.adcfreq

    @property
    def tbt_sync_enbl(self):
        """."""
        return self['TbTPhaseSyncEn-Sts']

    @tbt_sync_enbl.setter
    def tbt_sync_enbl(self, val):
        """."""
        self['TbTPhaseSyncEn-Sel'] = val

    @property
    def tbt_mask_enbl(self):
        """."""
        return self['TbTDataMaskEn-Sts']

    @tbt_mask_enbl.setter
    def tbt_mask_enbl(self, val):
        """."""
        self['TbTDataMaskEn-Sel'] = val

    @property
    def tbt_mask_beg(self):
        """."""
        return self['TbTDataMaskSamplesBeg-RB']

    @tbt_mask_beg.setter
    def tbt_mask_beg(self, val):
        """."""
        self['TbTDataMaskSamplesBeg-SP'] = val

    @property
    def tbt_mask_end(self):
        """."""
        return self['TbTDataMaskSamplesEnd-RB']

    @tbt_mask_end.setter
    def tbt_mask_end(self, val):
        """."""
        self['TbTDataMaskSamplesEnd-SP'] = val

    @property
    def fofb_sync_enbl(self):
        """."""
        return self['FOFBPhaseSyncEn-Sts']

    @fofb_sync_enbl.setter
    def fofb_sync_enbl(self, val):
        """."""
        self['FOFBPhaseSyncEn-Sel'] = val

    @property
    def fofb_rate(self):
        """Divisor or FOFB in relation to ADC."""
        return self['INFOFOFBRate-RB']

    @property
    def fofb_period(self):
        """."""
        return self.fofb_rate / self.adcfreq

    @property
    def facq_rate(self):
        """Divisor or FAcq in relation to ADC."""
        return self['INFOFAcqRate-RB']

    @property
    def facq_period(self):
        """."""
        return self.facq_rate / self.adcfreq

    @property
    def facq_sync_enbl(self):
        """."""
        return self['FAcqPhaseSyncEn-Sts']

    @facq_sync_enbl.setter
    def facq_sync_enbl(self, val):
        """."""
        self['FAcqPhaseSyncEn-Sel'] = val

    @property
    def monit_rate(self):
        """Divisor or Monit in relation to ADC."""
        return self['INFOMONITRate-RB']

    @property
    def monit_period(self):
        """."""
        return self.monit_rate / self.adcfreq

    @property
    def monit_sync_enbl(self):
        """."""
        return self['MonitPhaseSyncEn-Sts']

    @monit_sync_enbl.setter
    def monit_sync_enbl(self, val):
        """."""
        self['MonitPhaseSyncEn-Sel'] = val

    @property
    def posx_gain(self):
        """."""
        return self['PosKx-RB'] * self.CONV_NM2UM

    @posx_gain.setter
    def posx_gain(self, value):
        self['PosKx-SP'] = float(value) / self.CONV_NM2UM

    @property
    def posy_gain(self):
        """."""
        return self['PosKy-RB'] * self.CONV_NM2UM

    @posy_gain.setter
    def posy_gain(self, value):
        self['PosKy-SP'] = float(value) / self.CONV_NM2UM

    @property
    def possum_gain(self):
        """."""
        return self['PosKsum-RB']

    @possum_gain.setter
    def possum_gain(self, value):
        self['PosKsum-SP'] = float(value)

    @property
    def posq_gain(self):
        """."""
        return self['PosKq-RB']

    @posq_gain.setter
    def posq_gain(self, value):
        self['PosKq-SP'] = float(value)

    @property
    def posx_offset(self):
        """."""
        return self['PosXOffset-RB'] * self.CONV_NM2UM

    @posx_offset.setter
    def posx_offset(self, value):
        self['PosXOffset-SP'] = float(value) / self.CONV_NM2UM

    @property
    def posy_offset(self):
        """."""
        return self['PosYOffset-RB'] * self.CONV_NM2UM

    @posy_offset.setter
    def posy_offset(self, value):
        self['PosYOffset-SP'] = float(value) / self.CONV_NM2UM

    @property
    def posq_offset(self):
        """."""
        return self['PosQOffset-RB']

    @posq_offset.setter
    def posq_offset(self, value):
        self['PosQOffset-SP'] = float(value)

    @property
    def posx(self):
        """."""
        return self['PosX-Mon'] * self.CONV_NM2UM

    @property
    def posy(self):
        """."""
        return self['PosY-Mon'] * self.CONV_NM2UM

    @property
    def possum(self):
        """."""
        return self['Sum-Mon']

    @property
    def posq(self):
        """."""
        return self['PosQ-Mon']

    @property
    def ampla(self):
        """."""
        return self['AmplA-Mon']

    @property
    def amplb(self):
        """."""
        return self['AmplB-Mon']

    @property
    def amplc(self):
        """."""
        return self['AmplC-Mon']

    @property
    def ampld(self):
        """."""
        return self['AmplD-Mon']

    @property
    def mt_posx(self):
        """."""
        return self['GENPosXData'] * self.CONV_NM2UM

    @property
    def mt_posy(self):
        """."""
        return self['GENPosYData'] * self.CONV_NM2UM

    @property
    def mt_possum(self):
        """."""
        return self['GENSumData']

    @property
    def mt_posq(self):
        """."""
        return self['GENPosQData']

    @property
    def mt_ampla(self):
        """."""
        return self['GENAmplAData']

    @property
    def mt_amplb(self):
        """."""
        return self['GENAmplBData']

    @property
    def mt_amplc(self):
        """."""
        return self['GENAmplCData']

    @property
    def mt_ampld(self):
        """."""
        return self['GENAmplDData']

    @property
    def mt_polyx(self):
        """."""
        return self['GEN_PolyXArrayCoeff-RB']

    @mt_polyx.setter
    def mt_polyx(self, value):
        """."""
        self['GEN_PolyXArrayCoeff-SP'] = _np.array(value)

    @property
    def mt_polyy(self):
        """."""
        return self['GEN_PolyYArrayCoeff-RB']

    @mt_polyy.setter
    def mt_polyy(self, value):
        """."""
        self['GEN_PolyYArrayCoeff-SP'] = _np.array(value)

    @property
    def mt_polysum(self):
        """."""
        return self['GEN_PolySUMArrayCoeff-RB']

    @mt_polysum.setter
    def mt_polysum(self, value):
        """."""
        self['GEN_PolySUMArrayCoeff-SP'] = _np.array(value)

    @property
    def mt_polyq(self):
        """."""
        return self['GEN_PolyQArrayCoeff-RB']

    @mt_polyq.setter
    def mt_polyq(self, value):
        """."""
        self['GEN_PolyQArrayCoeff-SP'] = _np.array(value)

    @property
    def mt_polyxy_enbl(self):
        """."""
        return self['XYPosCal-Sts']

    @mt_polyxy_enbl.setter
    def mt_polyxy_enbl(self, val):
        """."""
        self['XYPosCal-Sel'] = val

    @property
    def mt_polysum_enbl(self):
        """."""
        return self['SumPosCal-Sts']

    @mt_polysum_enbl.setter
    def mt_polysum_enbl(self, val):
        """."""
        self['SumPosCal-Sel'] = val

    @property
    def mt_polyq_enbl(self):
        """."""
        return self['QPosCal-Sts']

    @mt_polyq_enbl.setter
    def mt_polyq_enbl(self, val):
        """."""
        self['QPosCal-Sel'] = val

    @property
    def acq_ctrl(self):
        """."""
        return self['GENTriggerEvent-Cmd']

    @acq_ctrl.setter
    def acq_ctrl(self, val):
        """."""
        self['GENTriggerEvent-Cmd'] = val

    @property
    def acq_status(self):
        """."""
        return self['GENStatus-Mon']

    @property
    def acq_count(self):
        """Counter of number of acquisitions so far."""
        return self['GENCount-Mon']

    @property
    def acq_channel(self):
        """."""
        return self['GENChannel-Sts']

    @acq_channel.setter
    def acq_channel(self, val):
        """."""
        self['GENChannel-Sel'] = val

    @property
    def acq_channel_str(self):
        """."""
        return _csbpm.AcqChan._fields[self.acq_channel]

    @property
    def acq_trigger(self):
        """."""
        return self['GENTrigger-Sts']

    @acq_trigger.setter
    def acq_trigger(self, val):
        """."""
        self['GENTrigger-Sel'] = val

    @property
    def acq_repeat(self):
        """."""
        return self['GENTriggerRep-Sts']

    @acq_repeat.setter
    def acq_repeat(self, val):
        """."""
        self['GENTriggerRep-Sel'] = val

    @property
    def acq_update_time(self):
        """BPMs update time in [s]."""
        return self['GENUpdateTime-RB']

    @acq_update_time.setter
    def acq_update_time(self, val):
        """BPMs update time in [s]."""
        self['GENUpdateTime-SP'] = val

    @property
    def acq_trig_datachan(self):
        """."""
        return self['GENDataTrigChan-Sts']

    @acq_trig_datachan.setter
    def acq_trig_datachan(self, val):
        """."""
        self['GENDataTrigChan-Sel'] = val

    @property
    def acq_trig_datasel(self):
        """."""
        return self['GENTriggerDataSel-RB']

    @acq_trig_datasel.setter
    def acq_trig_datasel(self, val):
        """."""
        self['GENTriggerDataSel-SP'] = val

    @property
    def acq_trig_datathres(self):
        """."""
        return self['GENTriggerDataThres-RB']

    @acq_trig_datathres.setter
    def acq_trig_datathres(self, val):
        """."""
        self['GENTriggerDataThres-SP'] = val

    @property
    def acq_trig_datahyst(self):
        """."""
        return self['GENTriggerDataHyst-RB']

    @acq_trig_datahyst.setter
    def acq_trig_datahyst(self, val):
        """."""
        self['GENTriggerDataHyst-SP'] = val

    @property
    def acq_trig_datapol(self):
        """."""
        return self['GENTriggerDataPol-RB']

    @acq_trig_datapol.setter
    def acq_trig_datapol(self, val):
        """."""
        self['GENTriggerDataPol-SP'] = val

    @property
    def acq_nrsamples_post(self):
        """."""
        return self['GENSamplesPost-RB']

    @acq_nrsamples_post.setter
    def acq_nrsamples_post(self, val):
        """."""
        self['GENSamplesPost-SP'] = val

    @property
    def acq_nrsamples_pre(self):
        """."""
        return self['GENSamplesPre-RB']

    @acq_nrsamples_pre.setter
    def acq_nrsamples_pre(self, val):
        """."""
        self['GENSamplesPre-SP'] = val

    @property
    def acq_nrshots(self):
        """."""
        return self['GENShots-RB']

    @acq_nrshots.setter
    def acq_nrshots(self, val):
        """."""
        self['GENShots-SP'] = val

    def wait_acq_finish(self, timeout=10):
        """Wait Acquisition to finish."""
        return self._wait(
            'GENStatus-Mon', self.ACQSTATES_FINISHED, timeout=timeout,
            comp=lambda x, y: x in y)

    def wait_acq_start(self, timeout=10):
        """Wait Acquisition to start."""
        return self._wait(
            'GENStatus-Mon', self.ACQSTATES_STARTED, timeout=timeout,
            comp=lambda x, y: x in y)

    def cmd_acq_start(self):
        """Command Start Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Start
        return True

    def cmd_acq_stop(self):
        """Command Stop Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Stop
        return True

    def cmd_turn_on_switching(self):
        """Command Turn on Switching."""
        self.switching_mode = _csbpm.SwModes.switching
        return self._wait('SwMode-Sts', _csbpm.SwModes.switching)

    def cmd_turn_off_switching(self):
        """Command Turn off Switching."""
        self.switching_mode = _csbpm.SwModes.direct
        return self._wait('SwMode-Sts', _csbpm.SwModes.direct)

    def cmd_sync_tbt(self):
        """Synchronize TbT acquisitions with Timing System."""
        self.tbt_sync_enbl = 1
        _time.sleep(0.1)
        self.tbt_sync_enbl = 0
        return self._wait('TbTPhaseSyncEn-Sts', 0)

    def cmd_sync_fofb(self):
        """Synchronize FOFB acquisitions with Timing System."""
        self.fofb_sync_enbl = 1
        _time.sleep(0.1)
        self.fofb_sync_enbl = 0
        return self._wait('FOFBPhaseSyncEn-Sts', 0)

    def cmd_sync_facq(self):
        """Synchronize FAcq acquisitions with Timing System."""
        self.facq_sync_enbl = 1
        _time.sleep(0.1)
        self.facq_sync_enbl = 0
        return self._wait('FAcqPhaseSyncEn-Sts', 0)

    def cmd_sync_monit(self):
        """Synchronize Monit acquisitions with Timing System."""
        self.monit_sync_enbl = 1
        _time.sleep(0.1)
        self.monit_sync_enbl = 0
        return self._wait('MonitPhaseSyncEn-Sts', 0)

    def get_sampling_frequency(
            self, rf_freq: float, acq_rate='') -> float:
        """Return the sampling frequency of the acquisition.

        Args:
            rf_freq (float): RF frequency.
            acq_rate (str, optional): acquisition rate. Defaults to ''.
            If empty string, it gets the configured acq. rate on BPMs

        Returns:
            float: acquisition frequency.

        """
        acq_rate = self.acq_channel_str if not acq_rate else acq_rate
        fadc = rf_freq / self.harmonic_number * self.tbt_rate
        if acq_rate.lower().startswith('tbt'):
            return fadc / self.tbt_rate
        elif acq_rate.lower().startswith('fofb'):
            return fadc / self.fofb_rate
        elif acq_rate.lower().startswith('facq'):
            return fadc / self.facq_rate
        return fadc / self.monit_rate

    def get_switching_frequency(self, rf_freq: float) -> float:
        """Return the switching frequency.

        Args:
            rf_freq (float): RF frequency.

        Returns:
            float: switching frequency.

        """
        fadc = rf_freq / self.harmonic_number * self.tbt_rate
        return fadc / self.switching_rate

    def get_propname(self, prop):
        """Get appropriate property name in case of triggered acquisitions."""
        if not self._ispost_mortem:
            return prop
        if prop.startswith('GEN'):
            return prop.replace('GEN', 'PM')
        return prop

    def _get_pvname(self, propty):
        propty = self.get_propname(propty)
        return super()._get_pvname(propty)
