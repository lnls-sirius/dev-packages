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
        _csbpm.AcqStates.Too_Few_Samples,
        _csbpm.AcqStates.Too_Many_Samples, _csbpm.AcqStates.Acq_Overflow}
    ACQSTATES_STARTED = {
        _csbpm.AcqStates.Waiting, _csbpm.AcqStates.External_Trig,
        _csbpm.AcqStates.Data_Trig, _csbpm.AcqStates.Software_Trig,
        _csbpm.AcqStates.Acquiring}
    ACQSTATES_FINISHED = {_csbpm.AcqStates.Idle, _csbpm.AcqStates.Aborted}
    ACQSTATES_FINISHED |= ACQSTATES_NOTOK

    PROPERTIES_ACQ = (
        'INFOClkFreq-RB', 'INFOHarmonicNumber-RB', 'INFOTbTRate-RB',
        'INFOFOFBRate-RB', 'INFOMONITRate-RB', 'INFOFAcqRate-RB',
        'GEN_AArrayData', 'GEN_BArrayData', 'GEN_CArrayData', 'GEN_DArrayData',
        'GEN_XArrayData', 'GEN_YArrayData', 'GEN_SUMArrayData',
        'GEN_QArrayData',
        'ACQBPMMode-Sel', 'ACQBPMMode-Sts',
        'ACQChannel-Sel', 'ACQChannel-Sts',
        'ACQShots-SP', 'ACQShots-RB',
        'ACQUpdateTime-SP', 'ACQUpdateTime-RB',
        'ACQSamplesPre-SP', 'ACQSamplesPre-RB',
        'ACQSamplesPost-SP', 'ACQSamplesPost-RB',
        'ACQTriggerEvent-Sel', 'ACQTriggerEvent-Sts',
        'ACQStatus-Sts', 'ACQCount-Mon',
        'ACQTrigger-Sel', 'ACQTrigger-Sts',
        'ACQTriggerRep-Sel', 'ACQTriggerRep-Sts',
        'ACQDataTrigChan-Sel', 'ACQDataTrigChan-Sts',
        'ACQTriggerDataSel-SP', 'ACQTriggerDataSel-RB',
        'ACQTriggerDataThres-SP', 'ACQTriggerDataThres-RB',
        'ACQTriggerDataPol-Sel', 'ACQTriggerDataPol-Sts',
        'ACQTriggerDataHyst-SP', 'ACQTriggerDataHyst-RB',
        )

    PROPERTIES_DEFAULT = PROPERTIES_ACQ + (
        'asyn.ENBL', 'asyn.CNCT', 'SwMode-Sel', 'SwMode-Sts',
        'RFFEAtt-SP', 'RFFEAtt-RB',
        'SP_AArrayData', 'SP_BArrayData', 'SP_CArrayData', 'SP_DArrayData',
        'GEN_RawXArrayData', 'GEN_RawYArrayData', 'GEN_RawSUMArrayData',
        'GEN_RawQArrayData',
        'SPPosX-Mon', 'SPPosY-Mon', 'SPSum-Mon', 'SPPosQ-Mon',
        'SPAmplA-Mon', 'SPAmplB-Mon', 'SPAmplC-Mon', 'SPAmplD-Mon',
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
        'PosSumOffset-SP', 'PosSumOffset-RB',
        'PosQOffset-SP', 'PosQOffset-RB',
        'FOFBPhaseSyncEn-Sel', 'FOFBPhaseSyncEn-Sts', 'SwDivClk-RB',
        'TbTPhaseSyncEn-Sel', 'TbTPhaseSyncEn-Sts',
        'FAcqPhaseSyncEn-Sel', 'FAcqPhaseSyncEn-Sts',
        'MonitPhaseSyncEn-Sel', 'MonitPhaseSyncEn-Sts',
        'TbTDataMaskEn-Sel', 'TbTDataMaskEn-Sts',
        'TbTDataMaskSamplesBeg-SP', 'TbTDataMaskSamplesBeg-RB',
        'TbTDataMaskSamplesEnd-SP', 'TbTDataMaskSamplesEnd-RB',
        'XYPosCal-Sel', 'XYPosCal-Sts',
        'SUMPosCal-Sel', 'SUMPosCal-Sts',
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
        stg += 'asyn:\n'
        stg += f'    Enabled: {_csbpm.EnblTyp._fields[self.asyn_state]:s}\n'
        stg += '    Connected: '
        stg += '    Switching Mode: '
        stg += f'{_csbpm.SwModes._fields[self.switching_mode]:s}\n'
        stg += f'{_csbpm.ConnTyp._fields[self.asyn_connected]:s}\n'
        stg += '\nAcquisition Parameters:\n'
        stg += f'    - Status: {_csbpm.AcqStates._fields[self.acq_status]:s}\n'
        stg += f'    - Mode: {_csbpm.OpModes._fields[self.acq_mode]:s}\n'
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
        okay &= self.asyn_connected == _csbpm.ConnTyp.Connected
        okay &= self.asyn_state == _csbpm.EnblTyp.Enable
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
    def asyn_state(self):
        """."""
        return self['asyn.ENBL']

    @asyn_state.setter
    def asyn_state(self, boo):
        """."""
        val = _csbpm.EnblTyp.Enable if boo else _csbpm.EnblTyp.Disable
        self['asyn.ENBL'] = val

    @property
    def asyn_connected(self):
        """."""
        return self['asyn.CNCT']

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
    def possum_offset(self):
        """."""
        return self['PosSumOffset-RB']

    @possum_offset.setter
    def possum_offset(self, value):
        self['PosSumOffset-SP'] = float(value)

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
        return self['GEN_XArrayData'] * self.CONV_NM2UM

    @property
    def mt_posy(self):
        """."""
        return self['GEN_YArrayData'] * self.CONV_NM2UM

    @property
    def mt_possum(self):
        """."""
        return self['GEN_SUMArrayData']

    @property
    def mt_posq(self):
        """."""
        return self['GEN_QArrayData']

    @property
    def mt_ampla(self):
        """."""
        return self['GEN_AArrayData']

    @property
    def mt_amplb(self):
        """."""
        return self['GEN_BArrayData']

    @property
    def mt_amplc(self):
        """."""
        return self['GEN_CArrayData']

    @property
    def mt_ampld(self):
        """."""
        return self['GEN_DArrayData']

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
        return self['SUMPosCal-Sts']

    @mt_polysum_enbl.setter
    def mt_polysum_enbl(self, val):
        """."""
        self['SUMPosCal-Sel'] = val

    @property
    def mt_polyq_enbl(self):
        """."""
        return self['QPosCal-Sts']

    @mt_polyq_enbl.setter
    def mt_polyq_enbl(self, val):
        """."""
        self['QPosCal-Sel'] = val

    @property
    def mtraw_posx(self):
        """Multi turn raw X array data."""
        return self['GEN_RawXArrayData'] * self.CONV_NM2UM

    @property
    def mtraw_posy(self):
        """Multi turn raw Y array data."""
        return self['GEN_RawYArrayData'] * self.CONV_NM2UM

    @property
    def mtraw_possum(self):
        """Multi turn raw sum array data."""
        return self['GEN_RawSUMArrayData']

    @property
    def mtraw_posq(self):
        """Multi turn raw Q array data."""
        return self['GEN_RawQArrayData']

    @property
    def sp_posx(self):
        """."""
        return self['SPPosX-Mon'] * self.CONV_NM2UM

    @property
    def sp_posy(self):
        """."""
        return self['SPPosY-Mon'] * self.CONV_NM2UM

    @property
    def sp_possum(self):
        """."""
        return self['SPSum-Mon']

    @property
    def sp_posq(self):
        """."""
        return self['SPPosQ-Mon']

    @property
    def sp_ampla(self):
        """."""
        return self['SPAmplA-Mon']

    @property
    def sp_amplb(self):
        """."""
        return self['SPAmplB-Mon']

    @property
    def sp_amplc(self):
        """."""
        return self['SPAmplC-Mon']

    @property
    def sp_ampld(self):
        """."""
        return self['SPAmplD-Mon']

    @property
    def sp_arraya(self):
        """."""
        return self['SP_AArrayData']

    @property
    def sp_arrayb(self):
        """."""
        return self['SP_BArrayData']

    @property
    def sp_arrayc(self):
        """."""
        return self['SP_CArrayData']

    @property
    def sp_arrayd(self):
        """."""
        return self['SP_DArrayData']

    @property
    def acq_mode(self):
        """."""
        return self['ACQBPMMode-Sts']

    @acq_mode.setter
    def acq_mode(self, mode):
        """."""
        self['ACQBPMMode-Sel'] = mode

    @property
    def acq_ctrl(self):
        """."""
        return self['ACQTriggerEvent-Sts']

    @acq_ctrl.setter
    def acq_ctrl(self, val):
        """."""
        self['ACQTriggerEvent-Sel'] = val

    @property
    def acq_status(self):
        """."""
        return self['ACQStatus-Sts']

    @property
    def acq_count(self):
        """Counter of number of acquisitions so far."""
        return self['ACQCount-Mon']

    @property
    def acq_channel(self):
        """."""
        return self['ACQChannel-Sts']

    @acq_channel.setter
    def acq_channel(self, val):
        """."""
        self['ACQChannel-Sel'] = val

    @property
    def acq_channel_str(self):
        """."""
        return _csbpm.AcqChan._fields[self.acq_channel]

    @property
    def acq_trigger(self):
        """."""
        return self['ACQTrigger-Sts']

    @acq_trigger.setter
    def acq_trigger(self, val):
        """."""
        self['ACQTrigger-Sel'] = val

    @property
    def acq_repeat(self):
        """."""
        return self['ACQTriggerRep-Sts']

    @acq_repeat.setter
    def acq_repeat(self, val):
        """."""
        self['ACQTriggerRep-Sel'] = val

    @property
    def acq_update_time(self):
        """BPMs update time in [s]."""
        return self['ACQUpdateTime-RB']

    @acq_update_time.setter
    def acq_update_time(self, val):
        """BPMs update time in [s]."""
        self['ACQUpdateTime-SP'] = val

    @property
    def acq_trig_datachan(self):
        """."""
        return self['ACQDataTrigChan-Sts']

    @acq_trig_datachan.setter
    def acq_trig_datachan(self, val):
        """."""
        self['ACQDataTrigChan-Sel'] = val

    @property
    def acq_trig_datasel(self):
        """."""
        return self['ACQTriggerDataSel-RB']

    @acq_trig_datasel.setter
    def acq_trig_datasel(self, val):
        """."""
        self['ACQTriggerDataSel-SP'] = val

    @property
    def acq_trig_datathres(self):
        """."""
        return self['ACQTriggerDataThres-RB']

    @acq_trig_datathres.setter
    def acq_trig_datathres(self, val):
        """."""
        self['ACQTriggerDataThres-SP'] = val

    @property
    def acq_trig_datahyst(self):
        """."""
        return self['ACQTriggerDataHyst-RB']

    @acq_trig_datahyst.setter
    def acq_trig_datahyst(self, val):
        """."""
        self['ACQTriggerDataHyst-SP'] = val

    @property
    def acq_trig_datapol(self):
        """."""
        return self['ACQTriggerDataPol-RB']

    @acq_trig_datapol.setter
    def acq_trig_datapol(self, val):
        """."""
        self['ACQTriggerDataPol-SP'] = val

    @property
    def acq_nrsamples_post(self):
        """."""
        return self['ACQSamplesPost-RB']

    @acq_nrsamples_post.setter
    def acq_nrsamples_post(self, val):
        """."""
        self['ACQSamplesPost-SP'] = val

    @property
    def acq_nrsamples_pre(self):
        """."""
        return self['ACQSamplesPre-RB']

    @acq_nrsamples_pre.setter
    def acq_nrsamples_pre(self, val):
        """."""
        self['ACQSamplesPre-SP'] = val

    @property
    def acq_nrshots(self):
        """."""
        return self['ACQShots-RB']

    @acq_nrshots.setter
    def acq_nrshots(self, val):
        """."""
        self['ACQShots-SP'] = val

    def wait_acq_finish(self, timeout=10):
        """Wait Acquisition to finish."""
        return self._wait(
            'ACQStatus-Sts', self.ACQSTATES_FINISHED, timeout=timeout,
            comp=lambda x, y: x in y)

    def wait_acq_start(self, timeout=10):
        """Wait Acquisition to start."""
        return self._wait(
            'ACQStatus-Sts', self.ACQSTATES_STARTED, timeout=timeout,
            comp=lambda x, y: x in y)

    def cmd_acq_start(self):
        """Command Start Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Start
        return self._wait('ACQTriggerEvent-Sts', _csbpm.AcqEvents.Start)

    def cmd_acq_stop(self):
        """Command Stop Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Stop
        return self._wait('ACQTriggerEvent-Sts', _csbpm.AcqEvents.Stop)

    def cmd_acq_abort(self):
        """Command Abort Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Abort
        return self._wait('ACQTriggerEvent-Sts', _csbpm.AcqEvents.Abort)

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
        elif prop.startswith('ACQ'):
            return prop.replace('ACQ', 'ACQ_PM')
        return prop

    def _get_pvname(self, propty):
        propty = self.get_propname(propty)
        return super()._get_pvname(propty)
