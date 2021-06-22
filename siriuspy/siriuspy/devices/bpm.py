"""."""

import numpy as _np

from .device import Device as _Device
from ..diagbeam.bpm.csdev import Const as _csbpm
from ..search import BPMSearch as _BPMSearch


class BPM(_Device):
    """BPM Device"""

    _properties = (
        'asyn.ENBL', 'asyn.CNCT', 'SwMode-Sel', 'SwMode-Sts',
        'RFFEAtt-SP', 'RFFEAtt-RB',
        'SP_AArrayData', 'SP_BArrayData', 'SP_CArrayData', 'SP_DArrayData',
        'GEN_AArrayData', 'GEN_BArrayData', 'GEN_CArrayData', 'GEN_DArrayData',
        'GEN_XArrayData', 'GEN_YArrayData', 'GEN_SUMArrayData',
        'GEN_QArrayData',
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

    def __init__(self, devname):
        """."""
        # call base class constructor
        if not _BPMSearch.is_valid_devname(devname):
            raise ValueError(devname + ' is no a valid BPM or PBPM name.')
        super().__init__(devname, properties=BPM._properties)
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
        return self['RFFEAtt-RB']

    @rffe_att.setter
    def rffe_att(self, val):
        """."""
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
    def adcfreq(self):
        """."""
        return self['INFOClkFreq-RB']

    @property
    def tbt_rate(self):
        """."""
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
    def fofb_rate(self):
        """."""
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
        """."""
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
    def acq_channel(self):
        """."""
        return self['ACQChannel-Sts']

    @acq_channel.setter
    def acq_channel(self, val):
        """."""
        self['ACQChannel-Sel'] = val

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
        """."""
        return self['ACQUpdateTime-RB'] / 1e3

    @acq_update_time.setter
    def acq_update_time(self, val):
        """."""
        self['ACQUpdateTime-SP'] = val * 1e3

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

    def cmd_acq_start(self):
        self.acq_ctrl = _csbpm.AcqEvents.Start

    def cmd_acq_stop(self):
        self.acq_ctrl = _csbpm.AcqEvents.Stop

    def cmd_acq_abort(self):
        self.acq_ctrl = _csbpm.AcqEvents.Abort
