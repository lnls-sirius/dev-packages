"""BPM devices."""

import time as _time
from threading import Event as _Flag
import numpy as _np

from .device import Device as _Device, Devices as _Devices, \
    ProptyDevice as _ProptyDevice
from ..diagbeam.bpm.csdev import Const as _csbpm
from ..search import BPMSearch as _BPMSearch
from ..namesys import SiriusPVName as _PVName


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

    _properties = (
        'asyn.ENBL', 'asyn.CNCT', 'SwMode-Sel', 'SwMode-Sts',
        'RFFEAtt-SP', 'RFFEAtt-RB',
        'SP_AArrayData', 'SP_BArrayData', 'SP_CArrayData', 'SP_DArrayData',
        'GEN_AArrayData', 'GEN_BArrayData', 'GEN_CArrayData', 'GEN_DArrayData',
        'GEN_XArrayData', 'GEN_YArrayData', 'GEN_SUMArrayData',
        'GEN_QArrayData',
        'GEN_RawXArrayData', 'GEN_RawYArrayData', 'GEN_RawSUMArrayData',
        'GEN_RawQArrayData',
        'SPPosX-Mon', 'SPPosY-Mon', 'SPSum-Mon', 'SPPosQ-Mon',
        'SPAmplA-Mon', 'SPAmplB-Mon', 'SPAmplC-Mon', 'SPAmplD-Mon',
        'PosX-Mon', 'PosY-Mon', 'Sum-Mon', 'PosQ-Mon',
        'AmplA-Mon', 'AmplB-Mon', 'AmplC-Mon', 'AmplD-Mon',
        'INFOClkFreq-RB', 'INFOHarmonicNumber-RB', 'INFOTbTRate-RB',
        'INFOFOFBRate-RB', 'INFOMONITRate-RB', 'INFOFAcqRate-RB',
        'GEN_PolyXArrayCoeff-SP', 'GEN_PolyXArrayCoeff-RB',
        'GEN_PolyYArrayCoeff-SP', 'GEN_PolyYArrayCoeff-RB',
        'GEN_PolySUMArrayCoeff-SP', 'GEN_PolySUMArrayCoeff-RB',
        'GEN_PolyQArrayCoeff-SP', 'GEN_PolyQArrayCoeff-RB',
        'PosKx-SP', 'PosKx-RB',
        'PosKy-RB', 'PosKy-SP',
        'PosKsum-SP', 'PosKsum-RB',
        'PosKq-SP', 'PosKq-RB',
        'PosXOffset-SP', 'PosXOffset-RB',
        'PosYOffset-SP', 'PosYOffset-RB',
        'PosSumOffset-SP', 'PosSumOffset-RB',
        'PosQOffset-SP', 'PosQOffset-RB',
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
        'SwTagEn-Sel', 'SwTagEn-Sts', 'SwDivClk-RB',
        'TbTTagEn-Sel', 'TbTTagEn-Sts',
        'FAcqTagEn-Sel', 'FAcqTagEn-Sts',
        'MonitTagEn-Sel', 'MonitTagEn-Sts',
        'TbTDataMaskEn-Sel', 'TbTDataMaskEn-Sts',
        'TbTDataMaskSamplesBeg-SP', 'TbTDataMaskSamplesBeg-RB',
        'TbTDataMaskSamplesEnd-SP', 'TbTDataMaskSamplesEnd-RB',
        'XYPosCal-Sel', 'XYPosCal-Sts',
        'SUMPosCal-Sel', 'SUMPosCal-Sts',
        'QPosCal-Sel', 'QPosCal-Sts',
        )

    CONV_NM2UM = 1e-3  # [nm] --> [um]

    def __init__(self, devname, auto_mon=True, ispost_mortem=False):
        """."""
        # call base class constructor
        if not _BPMSearch.is_valid_devname(devname):
            raise ValueError(devname + ' is not a valid BPM or PBPM name.')

        self._ispost_mortem = ispost_mortem
        properties = {self.get_propname(p) for p in BPM._properties}

        if _BPMSearch.is_photon_bpm(devname):
            properties -= {'RFFEAtt-SP', 'RFFEAtt-RB'}
        properties = list(properties)

        super().__init__(
            devname, properties=properties, auto_mon=auto_mon)
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
        return self['TbTTagEn-Sts']

    @tbt_sync_enbl.setter
    def tbt_sync_enbl(self, val):
        """."""
        self['TbTTagEn-Sel'] = val

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
        return self['SwTagEn-Sts']

    @fofb_sync_enbl.setter
    def fofb_sync_enbl(self, val):
        """."""
        self['SwTagEn-Sel'] = val

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
        return self['FAcqTagEn']

    @facq_sync_enbl.setter
    def facq_sync_enbl(self, val):
        """."""
        self['FAcqTagEn-Sel'] = val

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
        return self['MonitTagEn-Sts']

    @monit_sync_enbl.setter
    def monit_sync_enbl(self, val):
        """."""
        self['MonitTagEn-Sel'] = val

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
        return self[self.get_propname('GEN_XArrayData')] * self.CONV_NM2UM

    @property
    def mt_posy(self):
        """."""
        return self[self.get_propname('GEN_YArrayData')] * self.CONV_NM2UM

    @property
    def mt_possum(self):
        """."""
        return self[self.get_propname('GEN_SUMArrayData')]

    @property
    def mt_posq(self):
        """."""
        return self[self.get_propname('GEN_QArrayData')]

    @property
    def mt_ampla(self):
        """."""
        return self[self.get_propname('GEN_AArrayData')]

    @property
    def mt_amplb(self):
        """."""
        return self[self.get_propname('GEN_BArrayData')]

    @property
    def mt_amplc(self):
        """."""
        return self[self.get_propname('GEN_CArrayData')]

    @property
    def mt_ampld(self):
        """."""
        return self[self.get_propname('GEN_DArrayData')]

    @property
    def mt_polyx(self):
        """."""
        return self[self.get_propname('GEN_PolyXArrayCoeff-RB')]

    @mt_polyx.setter
    def mt_polyx(self, value):
        """."""
        self[self.get_propname('GEN_PolyXArrayCoeff-SP')] = _np.array(value)

    @property
    def mt_polyy(self):
        """."""
        return self[self.get_propname('GEN_PolyYArrayCoeff-RB')]

    @mt_polyy.setter
    def mt_polyy(self, value):
        """."""
        self[self.get_propname('GEN_PolyYArrayCoeff-SP')] = _np.array(value)

    @property
    def mt_polysum(self):
        """."""
        return self[self.get_propname('GEN_PolySUMArrayCoeff-RB')]

    @mt_polysum.setter
    def mt_polysum(self, value):
        """."""
        self[self.get_propname('GEN_PolySUMArrayCoeff-SP')] = _np.array(value)

    @property
    def mt_polyq(self):
        """."""
        return self[self.get_propname('GEN_PolyQArrayCoeff-RB')]

    @mt_polyq.setter
    def mt_polyq(self, value):
        """."""
        self[self.get_propname('GEN_PolyQArrayCoeff-SP')] = _np.array(value)

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
        return self[self.get_propname('GEN_RawXArrayData')] * self.CONV_NM2UM

    @property
    def mtraw_posy(self):
        """Multi turn raw Y array data."""
        return self[self.get_propname('GEN_RawYArrayData')] * self.CONV_NM2UM

    @property
    def mtraw_possum(self):
        """Multi turn raw sum array data."""
        return self[self.get_propname('GEN_RawSUMArrayData')]

    @property
    def mtraw_posq(self):
        """Multi turn raw Q array data."""
        return self[self.get_propname('GEN_RawQArrayData')]

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
        return self[self.get_propname('ACQBPMMode-Sts')]

    @acq_mode.setter
    def acq_mode(self, mode):
        """."""
        self[self.get_propname('ACQBPMMode-Sel')] = mode

    @property
    def acq_ctrl(self):
        """."""
        return self[self.get_propname('ACQTriggerEvent-Sts')]

    @acq_ctrl.setter
    def acq_ctrl(self, val):
        """."""
        self[self.get_propname('ACQTriggerEvent-Sel')] = val

    @property
    def acq_status(self):
        """."""
        return self[self.get_propname('ACQStatus-Sts')]

    @property
    def acq_count(self):
        """Counter of number of acquisitions so far."""
        return self[self.get_propname('ACQCount-Mon')]

    @property
    def acq_channel(self):
        """."""
        return self[self.get_propname('ACQChannel-Sts')]

    @acq_channel.setter
    def acq_channel(self, val):
        """."""
        self[self.get_propname('ACQChannel-Sel')] = val

    @property
    def acq_channel_str(self):
        """."""
        return _csbpm.AcqChan._fields[self.acq_channel]

    @property
    def acq_trigger(self):
        """."""
        return self[self.get_propname('ACQTrigger-Sts')]

    @acq_trigger.setter
    def acq_trigger(self, val):
        """."""
        self[self.get_propname('ACQTrigger-Sel')] = val

    @property
    def acq_repeat(self):
        """."""
        return self[self.get_propname('ACQTriggerRep-Sts')]

    @acq_repeat.setter
    def acq_repeat(self, val):
        """."""
        self[self.get_propname('ACQTriggerRep-Sel')] = val

    @property
    def acq_update_time(self):
        """."""
        return self[self.get_propname('ACQUpdateTime-RB')]  / 1e3

    @acq_update_time.setter
    def acq_update_time(self, val):
        """."""
        self[self.get_propname('ACQUpdateTime-SP')] = val * 1e3

    @property
    def acq_trig_datachan(self):
        """."""
        return self[self.get_propname('ACQDataTrigChan-Sts')]

    @acq_trig_datachan.setter
    def acq_trig_datachan(self, val):
        """."""
        self[self.get_propname('ACQDataTrigChan-Sel')] = val

    @property
    def acq_trig_datasel(self):
        """."""
        return self[self.get_propname('ACQTriggerDataSel-RB')]

    @acq_trig_datasel.setter
    def acq_trig_datasel(self, val):
        """."""
        self[self.get_propname('ACQTriggerDataSel-SP')] = val

    @property
    def acq_trig_datathres(self):
        """."""
        return self[self.get_propname('ACQTriggerDataThres-RB')]

    @acq_trig_datathres.setter
    def acq_trig_datathres(self, val):
        """."""
        self[self.get_propname('ACQTriggerDataThres-SP')] = val

    @property
    def acq_trig_datahyst(self):
        """."""
        return self[self.get_propname('ACQTriggerDataHyst-RB')]

    @acq_trig_datahyst.setter
    def acq_trig_datahyst(self, val):
        """."""
        self[self.get_propname('ACQTriggerDataHyst-SP')] = val

    @property
    def acq_trig_datapol(self):
        """."""
        return self[self.get_propname('ACQTriggerDataPol-RB')]

    @acq_trig_datapol.setter
    def acq_trig_datapol(self, val):
        """."""
        self[self.get_propname('ACQTriggerDataPol-SP')] = val

    @property
    def acq_nrsamples_post(self):
        """."""
        return self[self.get_propname('ACQSamplesPost-RB')]

    @acq_nrsamples_post.setter
    def acq_nrsamples_post(self, val):
        """."""
        self[self.get_propname('ACQSamplesPost-SP')] = val

    @property
    def acq_nrsamples_pre(self):
        """."""
        return self[self.get_propname('ACQSamplesPre-RB')]

    @acq_nrsamples_pre.setter
    def acq_nrsamples_pre(self, val):
        """."""
        self[self.get_propname('ACQSamplesPre-SP')] = val

    @property
    def acq_nrshots(self):
        """."""
        return self[self.get_propname('ACQShots-RB')]

    @acq_nrshots.setter
    def acq_nrshots(self, val):
        """."""
        self[self.get_propname('ACQShots-SP')] = val

    def wait_acq_finish(self, timeout=10):
        """Wait Acquisition to finish."""
        return self._wait(
            self.get_propname('ACQStatus-Sts'), self.ACQSTATES_FINISHED,
            timeout=timeout, comp=lambda x, y: x in y)

    def wait_acq_start(self, timeout=10):
        """Wait Acquisition to start."""
        return self._wait(
            self.get_propname('ACQStatus-Sts'), self.ACQSTATES_STARTED,
            timeout=timeout, comp=lambda x, y: x in y)

    def cmd_acq_start(self):
        """Command Start Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Start
        return self._wait(
            self.get_propname('ACQTriggerEvent-Sts'), _csbpm.AcqEvents.Start)

    def cmd_acq_stop(self):
        """Command Stop Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Stop
        return self._wait(
            self.get_propname('ACQTriggerEvent-Sts'), _csbpm.AcqEvents.Stop)

    def cmd_acq_abort(self):
        """Command Abort Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Abort
        return self._wait(
            self.get_propname('ACQTriggerEvent-Sts'), _csbpm.AcqEvents.Abort)

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
        return self._wait('TbTTagEn-Sts', 0)

    def cmd_sync_fofb(self):
        """Synchronize FOFB acquisitions with Timing System."""
        self.fofb_sync_enbl = 1
        _time.sleep(0.1)
        self.fofb_sync_enbl = 0
        return self._wait('SwTagEn-Sts', 0)

    def cmd_sync_facq(self):
        """Synchronize FAcq acquisitions with Timing System."""
        self.facq_sync_enbl = 1
        _time.sleep(0.1)
        self.facq_sync_enbl = 0
        return self._wait('FAcqTagEn-Sts', 0)

    def cmd_sync_monit(self):
        """Synchronize Monit acquisitions with Timing System."""
        self.monit_sync_enbl = 1
        _time.sleep(0.1)
        self.monit_sync_enbl = 0
        return self._wait('FAcqTagEn-Sts', 0)

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
        if not self._ispost_mortem:
            return prop
        if prop.startswith('GEN'):
            return prop.replace('GEN', 'PM')
        elif prop.startswith('ACQ'):
            return prop.replace('ACQ', 'ACQ_PM')
        return prop


class FamBPMs(_Devices):
    """Family of BPMs."""

    TIMEOUT = 10
    RFFEATT_MAX = 30

    class DEVICES:
        """."""

        SI = 'SI-Fam:DI-BPM'
        BO = 'BO-Fam:DI-BPM'
        ALL = (BO, SI)

    def __init__(self, devname=None, ispost_mortem=False):
        """."""
        if devname is None:
            devname = self.DEVICES.SI
        if devname not in self.DEVICES.ALL:
            raise ValueError('Wrong value for devname')

        devname = _PVName(devname)
        bpm_names = _BPMSearch.get_names(
            filters={'sec': devname.sec, 'dev': devname.dev})
        self._ispost_mortem = ispost_mortem
        devs = [
            BPM(dev, auto_mon=False, ispost_mortem=ispost_mortem)
            for dev in bpm_names]

        super().__init__(devname, devs)
        self._bpm_names = bpm_names
        self._csbpm = devs[0].csdata
        self._initial_timestamps = None

        self._mturn_flags = dict()
        # NOTE: ACQCount-Mon need to be fixed on BPM's IOC
        # for bpm in devs:
        #     pvo = bpm.pv_object(bpm.get_propname('ACQCount-Mon'))
        #     pvo.auto_monitor = True
        #     self._mturn_flags[pvo.pvname] = _Flag()
        #     pvo.add_callback(self._mturn_set_flag)

    @property
    def bpm_names(self):
        """Return BPM names."""
        return self._bpm_names

    @property
    def csbpm(self):
        """Return control system BPM constants class."""
        return self._csbpm

    def set_attenuation(self, value=RFFEATT_MAX, timeout=TIMEOUT):
        """."""
        for bpm in self:
            bpm.rffe_att = value

        mstr = ''
        okall = True
        t0 = _time.time()
        for bpm in self:
            tout = timeout - (_time.time() - t0)
            if not bpm._wait('RFFEAtt-RB', value, timeout=tout):
                okall = False
                mstr += (
                    f'\n{bpm.devname:<20s}: ' +
                    f'rb {bpm.rffe_att:.0f} != sp {value:.0f}')

        print('RFFE attenuation set confirmed in all BPMs', end='')
        print(', except:' + mstr if mstr else '.')
        return okall

    def get_slow_orbit(self):
        """Get slow orbit vectors.

        Returns:
            orbx (numpy.ndarray, 160): Horizontal Orbit.
            orby (numpy.ndarray, 160): Vertical Orbit.

        """
        orbx, orby = [], []
        for bpm in self._devices:
            orbx.append(bpm.posx)
            orby.append(bpm.posy)
        orbx = _np.array(orbx)
        orby = _np.array(orby)
        return orbx, orby

    def get_mturn_orbit(self, return_sum=False):
        """Get Multiturn orbit matrices.

        Args:
            return_sum (bool, optional): Whether or not to return BPMs sum.
                Defaults to False.

        Returns:
            orbx (numpy.ndarray, Nx160): Horizontal Orbit.
            orby (numpy.ndarray, Nx160): Vertical Orbit.
            possum (numpy.ndarray, Nx160): BPMs Sum signal.

        """
        orbx, orby = [], []
        if return_sum:
            possum = []

        mini = None
        for bpm in self._devices:
            mtx = bpm.mt_posx
            mty = bpm.mt_posy
            orbx.append(mtx)
            orby.append(mty)

            if mini is None:
                mini = mtx.size
            mini = _np.min([mini, mtx.size, mty.size])

            if return_sum:
                mts = bpm.mt_possum
                possum.append(mts)
                mini = min(mini, mts.size)

        for i, (obx, oby) in enumerate(zip(orbx, orby)):
            orbx[i] = obx[:mini]
            orby[i] = oby[:mini]
            if return_sum:
                possum[i] = possum[i][:mini]
        orbx = _np.array(orbx).T
        orby = _np.array(orby).T

        if not return_sum:
            return orbx, orby
        return orbx, orby, _np.array(possum).T

    def get_mturn_timestamps(self, return_sum=False):
        """Get Multiturn data timestamps.

        Args:
            return_sum (bool, optional): Whether or not to return BPMs sum
                timestamps. Defaults to False.

        Returns:
            tsmps (numpy.ndarray, (160, N)): The i-th row has the timestamp of
                the i-th bpm for the [horizontal, vertical, sum] signals
                respectively. If return_sum is False, then N=2 instead of 3.

        """
        tsmps = _np.zeros((len(self._devices), 2+return_sum), dtype=float)
        for i, bpm in enumerate(self._devices):
            pvx = bpm.pv_object(bpm.get_propname('GEN_XArrayData'))
            pvy = bpm.pv_object(bpm.get_propname('GEN_YArrayData'))
            vax = pvx.get_timevars(timeout=self.TIMEOUT)
            vay = pvy.get_timevars()
            tsmps[i, 0] = pvx.timestamp if vax is None else vax['timestamp']
            tsmps[i, 1] = pvy.timestamp if vay is None else vay['timestamp']
            if not return_sum:
                continue
            pvs = bpm.pv_object(bpm.get_propname('GEN_SUMArrayData'))
            vas = pvs.get_timevars()
            tsmps[i, 2] = pvs.timestamp if vas is None else vas['timestamp']
        return tsmps

    def get_sampling_frequency(self, rf_freq: float, acq_rate='') -> float:
        """Return the sampling frequency of the acquisition.

        Args:
            rf_freq (float): RF frequency.
            acq_rate (str, optional): acquisition rate. Defaults to ''.
            If empty string, it gets the configured acq. rate on BPMs

        Returns:
            float: acquisition frequency.

        """
        fs_bpms = {
            dev.get_sampling_frequency(rf_freq, acq_rate)
            for dev in self.devices}
        if len(fs_bpms) == 1:
            return fs_bpms.pop()
        else:
            print('BPMs are not configured with the same ACQChannel.')
            return None

    def get_switching_frequency(self, rf_freq: float) -> float:
        """Return the switching frequency.

        Args:
            rf_freq (float): RF frequency.

        Returns:
            float: switching frequency.

        """
        fsw_bpms = {
            dev.get_switching_frequency(rf_freq) for dev in self.devices}
        if len(fsw_bpms) == 1:
            return fsw_bpms.pop()
        else:
            print('BPMs are not configured with the same SwMode.')
            return None

    def mturn_config_acquisition(
            self, nr_points_after: int, nr_points_before=0,
            acq_rate='FAcq', repeat=True, external=True) -> int:
        """Configure acquisition for BPMs.

        Args:
            nr_points_after (int): number of points after trigger.
            nr_points_before (int): number of points after trigger.
                Defaults to 0.
            acq_rate (str, optional): Acquisition rate ('TbT', 'FOFB',
                'FAcq'). Defaults to 'FAcq'.
            repeat (bool, optional): Whether or not acquisition should be
                repetitive. Defaults to True.
            external (bool, optional): Whether or not external trigger should
                be used. Defaults to True.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                <0: Index of the first BPM which did not stop last acq. plus 1.
                >0: Index of the first BPM which is not ready for acq. plus 1.

        """
        if acq_rate.lower().startswith('facq'):
            acq_rate = self._csbpm.AcqChan.FAcq
        elif acq_rate.lower().startswith('fofb'):
            acq_rate = self._csbpm.AcqChan.FOFB
        elif acq_rate.lower().startswith('tbt'):
            acq_rate = self._csbpm.AcqChan.TbT
        else:
            raise ValueError(acq_rate + ' is not a valid acquisition rate.')

        if repeat:
            repeat = self._csbpm.AcqRepeat.Repetitive
        else:
            repeat = self._csbpm.AcqRepeat.Normal

        if external:
            trig = self._csbpm.AcqTrigTyp.External
        else:
            trig = self._csbpm.AcqTrigTyp.Now

        ret = self.cmd_mturn_acq_abort()
        if ret > 0:
            return -ret

        for bpm in self._devices:
            bpm.acq_repeat = repeat
            bpm.acq_channel = acq_rate
            bpm.acq_trigger = trig
            bpm.acq_nrsamples_pre = nr_points_before
            bpm.acq_nrsamples_post = nr_points_after

        return self.cmd_mturn_acq_start()

    def cmd_mturn_acq_abort(self, wait=True, timeout=10) -> int:
        """Abort BPMs acquistion.

        Args:
            wait (bool, optional): whether or not to wait BPMs get ready.
                Defaults to True.
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                >0: Index of the first BPM which did not update plus 1.

        """
        for bpm in self._devices:
            bpm.acq_ctrl = self._csbpm.AcqEvents.Abort

        if wait:
            return self.wait_acquisition_finish(timeout=timeout)
        return 0

    def wait_acquisition_finish(self, timeout=10) -> int:
        """Wait for all BPMs to be ready for acquisition.

        Args:
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                >0: Index of the first BPM which did not update plus 1.

        """
        for i, bpm in enumerate(self._devices):
            t0_ = _time.time()
            if not bpm.wait_acq_finish(timeout):
                return i + 1
            timeout -= _time.time() - t0_
        return 0

    def cmd_mturn_acq_start(self, wait=True, timeout=10) -> int:
        """Start BPMs acquisition.

        Args:
            wait (bool, optional): whether or not to wait BPMs get ready.
                Defaults to True.
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                >0: Index of the first BPM which did not update plus 1.

        """
        for bpm in self._devices:
            bpm.acq_ctrl = self._csbpm.AcqEvents.Start
        if wait:
            return self.wait_acquisition_start(timeout=timeout)
        return 0

    def wait_acquisition_start(self, timeout=10) -> bool:
        """Wait for all BPMs to be ready for acquisition.

        Args:
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                >0: Index of the first BPM which did not update plus 1.

        """
        for i, bpm in enumerate(self._devices):
            t0_ = _time.time()
            if not bpm.wait_acq_start(timeout):
                return i + 1
            timeout -= _time.time() - t0_
        return 0

    def set_switching_mode(self, mode='direct'):
        """Set switching mode of BPMS.

        Args:
            mode ((str, int), optional): Desired mode, must be in
                {'direct', 'switching', 1, 3}. Defaults to 'direct'.

        Raises:
            ValueError: When mode is not in {'direct', 'switching', 1, 3}.

        """
        if mode not in ('direct', 'switching', 1, 3):
            raise ValueError('Value must be in ("direct", "switching", 1, 3).')

        for bpm in self._devices:
            bpm.switching_mode = mode

    def mturn_update_initial_timestamps(self, consider_sum=False):
        """Call this method before acquisition to get orbit for comparison."""
        self._initial_timestamps = self.get_mturn_timestamps(
            return_sum=consider_sum)

    def mturn_reset_flags(self):
        """Reset Multiturn flags to wait for a new orbit update."""
        for flag in self._mturn_flags.values():
            flag.clear()

    def mturn_reset_flags_and_update_initial_timestamps(
            self, consider_sum=False):
        """Set initial state to wait for orbit acquisition to start."""
        self.mturn_reset_flags()
        self.mturn_update_initial_timestamps(consider_sum)

    def mturn_wait_update_flags(self, timeout=10):
        """Wait for all acquisition flags to be updated.

        Args:
            timeout (int, optional): Time to wait. Defaults to 10.

        Returns:
            int: code describing what happened:
                =0: BPMs are ready.
                >0: Index of the first BPM which did not update plus 1.

        """
        for i, flag in enumerate(self._mturn_flags.values()):
            t00 = _time.time()
            if not flag.wait(timeout=timeout):
                return i + 1
            timeout -= _time.time() - t00
            timeout = max(timeout, 0)
        return 0

    def mturn_wait_update_timestamps(
            self, timeout=10, consider_sum=False) -> int:
        """Call this method after acquisition to check if data was updated.

        For this method to work it is necessary to call
            mturn_update_initial_timestamps
        before the acquisition starts, so that a reference for comparison is
        created.

        Args:
            timeout (int, optional): Waiting timeout. Defaults to 10.
            consider_sum (bool, optional): Whether to also wait for sum signal
                to be updated. Defaults to False.

        Returns:
            int: code describing what happened:
                -1: initial timestamps were not defined;
                =0: data updated.
                >0: index of the first BPM which did not update plus 1.

        """
        if self._initial_timestamps is None:
            return -1

        tsmp0 = self._initial_timestamps
        while timeout > 0:
            t00 = _time.time()
            tsmp = self.get_mturn_timestamps(return_sum=consider_sum)
            errors = _np.any(_np.equal(tsmp, tsmp0), axis=1)
            if not _np.any(errors):
                return 0
            _time.sleep(0.1)
            timeout -= _time.time() - t00

        return int(_np.nonzero(errors)[0][0])+1

    def mturn_wait_update(self, timeout=10, consider_sum=False) -> int:
        """Combine all methods to wait update data.

        Args:
            timeout (int, optional): Waiting timeout. Defaults to 10.
            consider_sum (bool, optional): Whether to also wait for sum signal
                to be updated. Defaults to False.

        Returns:
            int: code describing what happened:
                -1: initial timestamps were not defined;
                =0: data updated.
                >0: index of the first BPM which did not update plus 1.

        """
        t00 = _time.time()
        ret = self.mturn_wait_update_flags(timeout)
        if ret > 0:
            return ret
        timeout -= _time.time() - t00

        return self.mturn_wait_update_timestamps(
            timeout, consider_sum=consider_sum)

    def _mturn_set_flag(self, pvname, **kwargs):
        _ = kwargs
        self._mturn_flags[pvname].set()


class BPMLogicalTrigger(_ProptyDevice):
    """BPM Logical Trigger device."""

    _properties = (
        'RcvSrc-Sel', 'RcvSrc-Sts',
        'RcvInSel-SP', 'RcvInSel-RB',
        'TrnSrc-Sel', 'TrnSrc-Sts',
        'TrnOutSel-SP', 'TrnOutSel-RB',
    )

    def __init__(self, bpmname, index):
        """Init."""
        if not _BPMSearch.is_valid_devname(bpmname):
            raise NotImplementedError(bpmname)
        if not 0 <= int(index) <= 23:
            raise NotImplementedError(index)
        super().__init__(
            bpmname, 'TRIGGER'+str(index),
            properties=BPMLogicalTrigger._properties)

    @property
    def receiver_source(self):
        """Receiver source."""
        return self['RcvSrc-Sts']

    @receiver_source.setter
    def receiver_source(self, value):
        self['RcvSrc-Sel'] = value

    @property
    def receiver_in_sel(self):
        """Receiver in selection."""
        return self['RcvInSel-RB']

    @receiver_in_sel.setter
    def receiver_in_sel(self, value):
        self['RcvInSel-SP'] = value

    @property
    def transmitter_source(self):
        """Transmitter source."""
        return self['TrnSrc-Sts']

    @transmitter_source.setter
    def transmitter_source(self, value):
        self['TrnSrc-Sel'] = value

    @property
    def transmitter_out_sel(self):
        """Transmitter out selection."""
        return self['TrnOutSel-RB']

    @transmitter_out_sel.setter
    def transmitter_out_sel(self, value):
        self['TrnOutSel-SP'] = value
