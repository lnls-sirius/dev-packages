"""."""
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
        'INFOClkFreq-RB', 'INFOHarmonicNumber-RB', 'INFOTBTRate-RB',
        'INFOFOFBRate-RB', 'INFOMONITRate-RB', 'INFOMONIT1Rate-RB',
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
        'ACQStatus-Sts',
        'ACQTrigger-Sel', 'ACQTrigger-Sts',
        'ACQTriggerRep-Sel', 'ACQTriggerRep-Sts',
        'ACQDataTrigChan-Sel', 'ACQDataTrigChan-Sts',
        'ACQTriggerDataSel-SP', 'ACQTriggerDataSel-RB',
        'ACQTriggerDataThres-SP', 'ACQTriggerDataThres-RB',
        'ACQTriggerDataPol-Sel', 'ACQTriggerDataPol-Sts',
        'ACQTriggerDataHyst-SP', 'ACQTriggerDataHyst-RB',
        'SwTagEn-Sel', 'SwTagEn-Sts',
        'TbtTagEn-Sel', 'TbtTagEn-Sts',
        'Monit1TagEn-Sel', 'Monit1TagEn-Sts',
        'MonitTagEn-Sel', 'MonitTagEn-Sts',
        'TbtDataMaskEn-Sel', 'TbtDataMaskEn-Sts',
        'TbtDataMaskSamplesBeg-SP', 'TbtDataMaskSamplesBeg-RB',
        'TbtDataMaskSamplesEnd-SP', 'TbtDataMaskSamplesEnd-RB',
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
        properties = {self._get_propname(p) for p in BPM._properties}

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
        stts = _csbpm.AcqStates
        okay = self.acq_status not in {
            stts.Error, stts.No_Memory, stts.Too_Few_Samples,
            stts.Too_Many_Samples, stts.Acq_Overflow}
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
        return self['INFOTBTRate-RB']

    @property
    def tbt_period(self):
        """."""
        return self.tbt_rate / self.adcfreq

    @property
    def tbt_sync_enbl(self):
        """."""
        return self['TbtTagEn-Sts']

    @tbt_sync_enbl.setter
    def tbt_sync_enbl(self, val):
        """."""
        self['TbtTagEn-Sel'] = val

    @property
    def tbt_mask_enbl(self):
        """."""
        return self['TbtDataMaskEn-Sts']

    @tbt_mask_enbl.setter
    def tbt_mask_enbl(self, val):
        """."""
        self['TbtDataMaskEn-Sel'] = val

    @property
    def tbt_mask_beg(self):
        """."""
        return self['TbtDataMaskSamplesBeg-RB']

    @tbt_mask_beg.setter
    def tbt_mask_beg(self, val):
        """."""
        self['TbtDataMaskSamplesBeg-SP'] = val

    @property
    def tbt_mask_end(self):
        """."""
        return self['TbtDataMaskSamplesEnd-RB']

    @tbt_mask_end.setter
    def tbt_mask_end(self, val):
        """."""
        self['TbtDataMaskSamplesEnd-SP'] = val

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
    def monit1_rate(self):
        """."""
        return self['INFOMONIT1Rate-RB']

    @property
    def monit1_period(self):
        """."""
        return self.monit1_rate / self.adcfreq

    @property
    def monit1_sync_enbl(self):
        """."""
        return self['Monit1TagEn']

    @monit1_sync_enbl.setter
    def monit1_sync_enbl(self, val):
        """."""
        self['Monit1TagEn-Sel'] = val

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
        prop = self._get_propname('GEN_XArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mt_posy(self):
        """."""
        prop = self._get_propname('GEN_YArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mt_possum(self):
        """."""
        prop = self._get_propname('GEN_SUMArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mt_posq(self):
        """."""
        prop = self._get_propname('GEN_QArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mt_ampla(self):
        """."""
        prop = self._get_propname('GEN_AArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mt_amplb(self):
        """."""
        prop = self._get_propname('GEN_BArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mt_amplc(self):
        """."""
        prop = self._get_propname('GEN_CArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mt_ampld(self):
        """."""
        prop = self._get_propname('GEN_DArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mt_polyx(self):
        """."""
        prop = self._get_propname('GEN_PolyXArrayCoeff-RB')
        return self[prop] * self.CONV_NM2UM

    @mt_polyx.setter
    def mt_polyx(self, value):
        """."""
        prop = self._get_propname('GEN_PolyXArrayCoeff-SP')
        self[prop] = _np.array(value)

    @property
    def mt_polyy(self):
        """."""
        prop = self._get_propname('GEN_PolyYArrayCoeff-RB')
        return self[prop] * self.CONV_NM2UM

    @mt_polyy.setter
    def mt_polyy(self, value):
        """."""
        prop = self._get_propname('GEN_PolyYArrayCoeff-SP')
        self[prop] = _np.array(value)

    @property
    def mt_polysum(self):
        """."""
        prop = self._get_propname('GEN_PolySUMArrayCoeff-RB')
        return self[prop] * self.CONV_NM2UM

    @mt_polysum.setter
    def mt_polysum(self, value):
        """."""
        prop = self._get_propname('GEN_PolySUMArrayCoeff-SP')
        self[prop] = _np.array(value)

    @property
    def mt_polyq(self):
        """."""
        prop = self._get_propname('GEN_PolyQArrayCoeff-RB')
        return self[prop] * self.CONV_NM2UM

    @mt_polyq.setter
    def mt_polyq(self, value):
        """."""
        prop = self._get_propname('GEN_PolyQArrayCoeff-SP')
        self[prop] = _np.array(value)

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
        prop = self._get_propname('GEN_RawXArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mtraw_posy(self):
        """Multi turn raw Y array data."""
        prop = self._get_propname('GEN_RawYArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mtraw_possum(self):
        """Multi turn raw sum array data."""
        prop = self._get_propname('GEN_RawSUMArrayData')
        return self[prop] * self.CONV_NM2UM

    @property
    def mtraw_posq(self):
        """Multi turn raw Q array data."""
        prop = self._get_propname('GEN_RawQArrayData')
        return self[prop] * self.CONV_NM2UM

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
        prop = self._get_propname('ACQBPMMode-Sts')
        return self[prop] * self.CONV_NM2UM

    @acq_mode.setter
    def acq_mode(self, mode):
        """."""
        self[self._get_propname('ACQBPMMode-Sel')] = mode

    @property
    def acq_ctrl(self):
        """."""
        prop = self._get_propname('ACQTriggerEvent-Sts')
        return self[prop] * self.CONV_NM2UM

    @acq_ctrl.setter
    def acq_ctrl(self, val):
        """."""
        self[self._get_propname('ACQTriggerEvent-Sel')] = val

    @property
    def acq_status(self):
        """."""
        prop = self._get_propname('ACQStatus-Sts')
        return self[prop] * self.CONV_NM2UM

    @property
    def acq_channel(self):
        """."""
        prop = self._get_propname('ACQChannel-Sts')
        return self[prop] * self.CONV_NM2UM

    @acq_channel.setter
    def acq_channel(self, val):
        """."""
        self[self._get_propname('ACQChannel-Sel')] = val

    @property
    def acq_trigger(self):
        """."""
        prop = self._get_propname('ACQTrigger-Sts')
        return self[prop] * self.CONV_NM2UM

    @acq_trigger.setter
    def acq_trigger(self, val):
        """."""
        self[self._get_propname('ACQTrigger-Sel')] = val

    @property
    def acq_repeat(self):
        """."""
        prop = self._get_propname('ACQTriggerRep-Sts')
        return self[prop] * self.CONV_NM2UM

    @acq_repeat.setter
    def acq_repeat(self, val):
        """."""
        self[self._get_propname('ACQTriggerRep-Sel')] = val

    @property
    def acq_update_time(self):
        """."""
        prop = self._get_propname('ACQUpdateTime-RB') / 1e3
        return self[prop] * self.CONV_NM2UM

    @acq_update_time.setter
    def acq_update_time(self, val):
        """."""
        self[self._get_propname('ACQUpdateTime-SP')] = val * 1e3

    @property
    def acq_trig_datachan(self):
        """."""
        prop = self._get_propname('ACQDataTrigChan-Sts')
        return self[prop] * self.CONV_NM2UM

    @acq_trig_datachan.setter
    def acq_trig_datachan(self, val):
        """."""
        self[self._get_propname('ACQDataTrigChan-Sel')] = val

    @property
    def acq_trig_datasel(self):
        """."""
        prop = self._get_propname('ACQTriggerDataSel-RB')
        return self[prop] * self.CONV_NM2UM

    @acq_trig_datasel.setter
    def acq_trig_datasel(self, val):
        """."""
        self[self._get_propname('ACQTriggerDataSel-SP')] = val

    @property
    def acq_trig_datathres(self):
        """."""
        prop = self._get_propname('ACQTriggerDataThres-RB')
        return self[prop] * self.CONV_NM2UM

    @acq_trig_datathres.setter
    def acq_trig_datathres(self, val):
        """."""
        self[self._get_propname('ACQTriggerDataThres-SP')] = val

    @property
    def acq_trig_datahyst(self):
        """."""
        prop = self._get_propname('ACQTriggerDataHyst-RB')
        return self[prop] * self.CONV_NM2UM

    @acq_trig_datahyst.setter
    def acq_trig_datahyst(self, val):
        """."""
        self[self._get_propname('ACQTriggerDataHyst-SP')] = val

    @property
    def acq_trig_datapol(self):
        """."""
        prop = self._get_propname('ACQTriggerDataPol-RB')
        return self[prop] * self.CONV_NM2UM

    @acq_trig_datapol.setter
    def acq_trig_datapol(self, val):
        """."""
        self[self._get_propname('ACQTriggerDataPol-SP')] = val

    @property
    def acq_nrsamples_post(self):
        """."""
        prop = self._get_propname('ACQSamplesPost-RB')
        return self[prop] * self.CONV_NM2UM

    @acq_nrsamples_post.setter
    def acq_nrsamples_post(self, val):
        """."""
        self[self._get_propname('ACQSamplesPost-SP')] = val

    @property
    def acq_nrsamples_pre(self):
        """."""
        prop = self._get_propname('ACQSamplesPre-RB')
        return self[prop] * self.CONV_NM2UM

    @acq_nrsamples_pre.setter
    def acq_nrsamples_pre(self, val):
        """."""
        self[self._get_propname('ACQSamplesPre-SP')] = val

    @property
    def acq_nrshots(self):
        """."""
        prop = self._get_propname('ACQShots-RB')
        return self[prop] * self.CONV_NM2UM

    @acq_nrshots.setter
    def acq_nrshots(self, val):
        """."""
        self[self._get_propname('ACQShots-SP')] = val

    def wait_acq_finish(self, timeout=10):
        """Wait Acquisition to finish."""
        vals = {
            _csbpm.AcqStates.Idle, _csbpm.AcqStates.Error,
            _csbpm.AcqStates.Aborted, _csbpm.AcqStates.Too_Many_Samples,
            _csbpm.AcqStates.Too_Few_Samples, _csbpm.AcqStates.No_Memory,
            _csbpm.AcqStates.Acq_Overflow}
        prop = self._get_propname('ACQStatus-Sts')
        return self._wait(
            prop, vals, timeout=timeout, comp=lambda x, y: x in y)

    def wait_acq_start(self, timeout=10):
        """Wait Acquisition to start."""
        vals = {
            _csbpm.AcqStates.Waiting, _csbpm.AcqStates.External_Trig,
            _csbpm.AcqStates.Data_Trig, _csbpm.AcqStates.Software_Trig,
            _csbpm.AcqStates.Acquiring}
        prop = self._get_propname('ACQStatus-Sts')
        return self._wait(
            prop, vals, timeout=timeout, comp=lambda x, y: x in y)

    def cmd_acq_start(self):
        """Command Start Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Start
        prop = self._get_propname('ACQTriggerEvent-Sts')
        return self._wait(prop, _csbpm.AcqEvents.Start)

    def cmd_acq_stop(self):
        """Command Stop Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Stop
        prop = self._get_propname('ACQTriggerEvent-Sts')
        return self._wait(prop, _csbpm.AcqEvents.Stop)

    def cmd_acq_abort(self):
        """Command Abort Acquisition."""
        self.acq_ctrl = _csbpm.AcqEvents.Abort
        prop = self._get_propname('ACQTriggerEvent-Sts')
        return self._wait(prop, _csbpm.AcqEvents.Abort)

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
        return self._wait('TbtTagEn-Sts', 0)

    def cmd_sync_fofb(self):
        """Synchronize FOFB acquisitions with Timing System."""
        self.fofb_sync_enbl = 1
        _time.sleep(0.1)
        self.fofb_sync_enbl = 0
        return self._wait('SwTagEn-Sts', 0)

    def cmd_sync_monit1(self):
        """Synchronize Monit1 acquisitions with Timing System."""
        self.monit1_sync_enbl = 1
        _time.sleep(0.1)
        self.monit1_sync_enbl = 0
        return self._wait('Monit1TagEn-Sts', 0)

    def cmd_sync_monit(self):
        """Synchronize Monit acquisitions with Timing System."""
        self.monit_sync_enbl = 1
        _time.sleep(0.1)
        self.monit_sync_enbl = 0
        return self._wait('Monit1TagEn-Sts', 0)

    def _get_propname(self, prop):
        if not self._ispost_mortem:
            return prop
        if prop.startswith('GEN'):
            return prop.replace('GEN', 'PM')
        elif prop.startswith('ACQ'):
            return prop.replace('ACQ', 'ACQ_PM')
        return prop


class FamBPMs(_Devices):
    """."""

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

    def get_sampling_frequency(
            self, rf_freq: float, acq_rate='Monit1') -> float:
        """Return the sampling frequency of the acquisition.

        Args:
            rf_freq (float): RF frequency.
            acq_rate (str, optional): acquisition rate. Defaults to 'Monit1'.

        Returns:
            float: acquisition frequency.

        """
        bpm = self._devices[0]
        fadc = rf_freq / bpm.harmonic_number * bpm.tbt_rate
        if acq_rate.lower().startswith('tbt'):
            return fadc / bpm.tbt_rate
        elif acq_rate.lower().startswith('fofb'):
            return fadc / bpm.fofb_rate
        elif acq_rate.lower().startswith('monit1'):
            return fadc / bpm.monit1_rate
        return fadc / bpm.monit_rate

    def mturn_config_acquisition(
            self, nr_points_after: int, nr_points_before=0,
            acq_rate='Monit1', repeat=True, external=True) -> int:
        """Configure acquisition for BPMs.

        Args:
            nr_points_after (int): number of points after trigger.
            nr_points_before (int): number of points after trigger.
                Defaults to 0.
            acq_rate (str, optional): Acquisition rate ('TbT', 'FOFB',
                'Monit1'). Defaults to 'Monit1'.
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
        if acq_rate.lower().startswith('monit1'):
            acq_rate = self._csbpm.AcqChan.Monit1
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

    def mturn_update_initial_orbit(self, consider_sum=False):
        """Call this method before acquisition to get orbit for comparison."""
        self._initial_orbs = self.get_mturn_orbit(return_sum=consider_sum)

    def mturn_wait_update_orbit(self, timeout=10, consider_sum=False) -> int:
        """Call this method after acquisition to check if orbit was updated.

        For this method to work it is necessary to call
            mturn_update_initial_orbit
        before the acquisition starts, so that a reference for comparison is
        created.

        Args:
            timeout (int, optional): Waiting timeout. Defaults to 10.
            consider_sum (bool, optional): Whether to also wait for sum signal
                to be updated. Defaults to False.

        Returns:
            int: code describing what happened:
                -4: unknown error;
                -3: initial orbit was not acquired before acquisition;
                -2: TypeError ocurred (maybe because some of them are None);
                -1: Orbits have different sizes;
                =0: Orbit updated.
                >0: Index of the first BPM which did not update plus 1.

        """
        orbs0, self._initial_orbs = self._initial_orbs, None
        if orbs0 is None:
            return -3
        while timeout > 0:
            t00 = _time.time()
            orbs = self.get_mturn_orbit(return_sum=consider_sum)
            typ = False
            try:
                sizes = [
                    min(o.shape[0], o0.shape[0]) for o, o0 in zip(orbs, orbs0)]
                continue_ = max(sizes) != min(sizes)
                errs = _np.any([
                    _np.all(_np.isclose(o[:s], o0[:s]), axis=0)
                    for o, o0, s in zip(orbs, orbs0, sizes)], axis=0)
                continue_ |= _np.any(errs)
            except TypeError:
                typ = True
                continue_ = True
            if not continue_:
                return 0
            _time.sleep(0.1)
            timeout -= _time.time() - t00

        if typ:
            return -1
        elif max(sizes) != min(sizes):
            return -2
        elif _np.any(errs):
            return int(errs.nonzero()[0][0])+1
        return -4

    def mturn_wait_update(self, timeout=10, consider_sum=False) -> int:
        """Combine wait_acquistion_finish and mturn_wait_update_orbit.

        Args:
            timeout (int, optional): Waiting timeout. Defaults to 10.
            consider_sum (bool, optional): Whether to also wait for sum signal
                to be updated. Defaults to False.

        Returns:
            int: code describing what happened:
                -4: unknown error;
                -3: initial orbit was not acquired before acquisition;
                -2: TypeError ocurred (maybe because some of them are None);
                -1: Orbits have different sizes;
                =0: Orbit updated.
                >0: Index of the first BPM which did not update plus 1.

        """
        t00 = _time.time()
        ret = self.wait_acquisition_finish(timeout)
        if ret > 0:
            return ret
        timeout -= _time.time() - t00

        return self.mturn_wait_update_orbit(timeout, consider_sum=consider_sum)


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
