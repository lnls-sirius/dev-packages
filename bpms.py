"""Module to deal with orbit acquisition."""
import logging as _log
import numpy as _np
from epics import PV as _PV
import siriuspy.csdevice.bpms as _csbpm
import siriuspy.csdevice.timesys as _cstime
from siriuspy.search import HLTimeSearch as _HLTimesearch
from siriuspy.envars import vaca_prefix as LL_PREF
from .base_class import BaseTimingConfig as _BaseTimingConfig

TIMEOUT = 0.05


class BPM(_BaseTimingConfig):

    def __init__(self, name):
        super().__init__(name[:2])
        self._name = name
        self.ORB_CONV = self._csorb.ORBIT_CONVERSION_UNIT
        opt = {'connection_timeout': TIMEOUT}
        self._kx = _PV(LL_PREF + self._name + ':PosKx-RB', **opt)
        self._ky = _PV(LL_PREF + self._name + ':PosKy-RB', **opt)
        self._ksum = _PV(LL_PREF + self._name + ':PosKsum-RB', **opt)
        self._posx = _PV(LL_PREF + self._name + ':PosX-Mon', **opt)
        self._posy = _PV(LL_PREF + self._name + ':PosY-Mon', **opt)
        self._spposx = _PV(LL_PREF + self._name + ':SPPosX-Mon', **opt)
        self._spposy = _PV(LL_PREF + self._name + ':SPPosY-Mon', **opt)
        self._spsum = _PV(LL_PREF + self._name + ':SPSum-Mon', **opt)
        self._spanta = _PV(LL_PREF + self._name + ':SP_AArrayData', **opt)
        self._spantb = _PV(LL_PREF + self._name + ':SP_BArrayData', **opt)
        self._spantc = _PV(LL_PREF + self._name + ':SP_CArrayData', **opt)
        self._spantd = _PV(LL_PREF + self._name + ':SP_DArrayData', **opt)
        self._arrayx = _PV(LL_PREF + self._name + ':GEN_XArrayData', **opt)
        self._arrayy = _PV(LL_PREF + self._name + ':GEN_YArrayData', **opt)
        self._arrays = _PV(LL_PREF + self._name + ':GEN_SUMArrayData', **opt)
        self._offsetx = _PV(LL_PREF + self._name + ':PosXOffset-RB', **opt)
        self._offsety = _PV(LL_PREF + self._name + ':PosYOffset-RB', **opt)
        self._config_ok_vals = {
            'asyn.ENBL': _csbpm.EnblTyp.Enable,
            'ACQBPMMode': _csbpm.OpModes.MultiBunch,
            'ACQChannel': _csbpm.AcqChan.ADC,
            # 'ACQNrShots': 1,
            'ACQShots': 1,
            # 'ACQTriggerHwDly': 0.0,  # NOTE: leave this property commented
            'ACQUpdateTime': 0.001,
            # 'ACQNrSamplesPre': 0,
            'ACQSamplesPre': 50,
            # 'ACQNrSamplesPost': 200,
            'ACQSamplesPost': 50,
            # 'ACQCtrl': _csbpm.AcqEvents.Stop,
            'ACQTriggerEvent': _csbpm.AcqEvents.Stop,
            # 'ACQTriggerType': _csbpm.AcqTrigTyp.External,
            'ACQTrigger': _csbpm.AcqTrigTyp.External,
            'ACQTriggerRep': _csbpm.AcqRepeat.Normal,
            # 'ACQTriggerDataChan': _csbpm.AcqChan.Monit1,
            'ACQDataTrigChan': _csbpm.AcqChan.ADC,
            'ACQTriggerDataSel': _csbpm.AcqDataTyp.A,
            'ACQTriggerDataThres': 1,
            'ACQTriggerDataPol': _csbpm.Polarity.Positive,
            'ACQTriggerDataHyst': 0,
            'TbtTagEn': _csbpm.EnbldDsbld.disabled,  # Enable TbT sync Timing
            'TbtDataMaskEn': _csbpm.EnbldDsbld.disabled,  # Enable use of mask
            'TbtDataMaskSamplesBeg': 0,
            'TbtDataMaskSamplesEnd': 0}
        pvs = {
            'asyn.ENBL': 'asyn.ENBL',
            'ACQBPMMode': 'ACQBPMMode-Sel',
            'ACQChannel': 'ACQChannel-Sel',
            # 'ACQNrShots': 'ACQNrShots-SP',
            'ACQShots': 'ACQShots-SP',
            # 'ACQTriggerHwDly': 'ACQTriggerHwDly-SP',
            'ACQUpdateTime': 'ACQUpdateTime-SP',
            # 'ACQNrSamplesPre': 'ACQNrSamplesPre-SP',
            'ACQSamplesPre': 'ACQSamplesPre-SP',
            # 'ACQNrSamplesPost': 'ACQNrSamplesPost-SP',
            'ACQSamplesPost': 'ACQSamplesPost-SP',
            # 'ACQCtrl': 'ACQCtrl-Sel',
            'ACQTriggerEvent': 'ACQTriggerEvent-Sel',
            # 'ACQTriggerType': 'ACQTriggerType-Sel',
            'ACQTrigger': 'ACQTrigger-Sel',
            'ACQTriggerRep': 'ACQTriggerRep-Sel',
            # 'ACQTriggerDataChan': 'ACQTriggerDataChan-Sel',
            'ACQDataTrigChan': 'ACQDataTrigChan-Sel',
            # 'ACQTriggerDataSel': 'ACQTriggerDataSel-Sel',
            'ACQTriggerDataSel': 'ACQTriggerDataSel-SP',
            'ACQTriggerDataThres': 'ACQTriggerDataThres-SP',
            'ACQTriggerDataPol': 'ACQTriggerDataPol-Sel',
            'ACQTriggerDataHyst': 'ACQTriggerDataHyst-SP',
            'TbtTagEn': 'TbtTagEn-Sel',  # Enable TbT sync with timing
            'TbtDataMaskEn': 'TbtDataMaskEn-Sel',  # Enable use of mask
            'TbtDataMaskSamplesBeg': 'TbtDataMaskSamplesBeg-SP',
            'TbtDataMaskSamplesEnd': 'TbtDataMaskSamplesEnd-SP'}
        self._config_pvs_sp = {
            k: _PV(LL_PREF+self.name+':'+v, **opt) for k, v in pvs.items()}
        pvs = {
            'asyn.ENBL': 'asyn.ENBL',
            'asyn.CNCT': 'asyn.CNCT',
            'INFOClkFreq': 'INFOClkFreq-RB',
            'INFOHarmonicNumber': 'INFOHarmonicNumber-RB',
            'INFOTBTRate': 'INFOTBTRate-RB',
            'INFOFOFBRate': 'INFOFOFBRate-RB',
            'INFOMONITRate': 'INFOMONITRate-RB',
            'INFOMONIT1Rate': 'INFOMONIT1Rate-RB',
            'ACQBPMMode': 'ACQBPMMode-Sts',
            'ACQChannel': 'ACQChannel-Sts',
            # 'ACQNrShots': 'ACQNrShots-RB',
            'ACQShots': 'ACQShots-RB',
            # 'ACQTriggerHwDly': 'ACQTriggerHwDly-RB',
            'ACQUpdateTime': 'ACQUpdateTime-RB',
            # 'ACQNrSamplesPre': 'ACQNrSamplesPre-RB',
            'ACQSamplesPre': 'ACQSamplesPre-RB',
            # 'ACQNrSamplesPost': 'ACQNrSamplesPost-RB',
            'ACQSamplesPost': 'ACQSamplesPost-RB',
            # 'ACQCtrl': 'ACQCtrl-Sts',
            'ACQTriggerEvent': 'ACQTriggerEvent-Sts',
            # 'ACQStatus': 'ACQStatus-Mon',
            'ACQStatus': 'ACQStatus-Sts',
            # 'ACQTriggerType': 'ACQTriggerType-Sts',
            'ACQTrigger': 'ACQTrigger-Sts',
            'ACQTriggerRep': 'ACQTriggerRep-Sts',
            # 'ACQTriggerDataChan': 'ACQTriggerDataChan-Sts',
            'ACQDataTrigChan': 'ACQDataTrigChan-Sts',
            # 'ACQTriggerDataSel': 'ACQTriggerDataSel-Sts',
            'ACQTriggerDataSel': 'ACQTriggerDataSel-RB',
            'ACQTriggerDataThres': 'ACQTriggerDataThres-RB',
            'ACQTriggerDataPol': 'ACQTriggerDataPol-Sts',
            'ACQTriggerDataHyst': 'ACQTriggerDataHyst-RB',
            'TbtTagEn': 'TbtTagEn-Sts',
            'TbtDataMaskEn': 'TbtDataMaskEn-Sts',
            'TbtDataMaskSamplesBeg': 'TbtDataMaskSamplesBeg-RB',
            'TbtDataMaskSamplesEnd': 'TbtDataMaskSamplesEnd-RB'}
        self._config_pvs_rb = {
            k: _PV(LL_PREF+self.name+':'+v, **opt) for k, v in pvs.items()}

    @property
    def name(self):
        return self._name

    @property
    def connected(self):
        conn = super().connected
        pvs = (
            self._posx, self._posy,
            self._spposx, self._spposy, self._spsum,
            self._arrayx, self._arrayy, self._arrays,
            self._offsetx, self._offsety,
            self._spanta, self._spantb, self._spantc, self._spantd,
            self._kx, self._ky, self._ksum)
        for pv in pvs:
            if not pv.connected:
                _log.debug('NOT CONN: ' + pv.pvname)
            conn &= pv.connected
        return conn

    @property
    def is_ok(self):
        ok = super().is_ok
        pv = self._config_pvs_rb['ACQStatus']
        stts = _csbpm.AcqStates
        return ok and pv.value not in (
            stts.Error, stts.No_Memory,
            stts.Too_Few_Samples, stts.Too_Many_Samples)

    @property
    def state(self):
        pv = self._config_pvs_rb['asyn.ENBL']
        return pv.value == _csbpm.EnblTyp.Enable if pv.connected else False

    @state.setter
    def state(self, boo):
        val = _csbpm.EnblTyp.Enable if boo else _csbpm.EnblTyp.Disable
        pv = self._config_pvs_sp['asyn.ENBL']
        self._config_ok_vals['asyn.ENBL'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def adcfreq(self):
        defv = 218446014.0 if self._csorb.acc == 'BO' else 220870069.0
        pv = self._config_pvs_rb['INFOClkFreq']
        val = pv.value if pv.connected else defv
        return val if val else defv

    @property
    def tbtrate(self):
        defv = 362 if self._csorb.acc == 'BO' else 382
        pv = self._config_pvs_rb['INFOTBTRate']
        val = pv.value if pv.connected else defv
        return val if val else defv

    @property
    def tbtperiod(self):
        return self.tbtrate / self.adcfreq

    @property
    def fofbrate(self):
        defv = (362 if self._csorb.acc == 'BO' else 382) * 24
        pv = self._config_pvs_rb['INFOFOFBRate']
        val = pv.value if pv.connected else defv
        return val if val else defv

    @property
    def fofbperiod(self):
        return self.fofbrate / self.adcfreq

    @property
    def monitrate(self):
        defv = (362 if self._csorb.acc == 'BO' else 382) * 59904
        pv = self._config_pvs_rb['INFOMONITRate']
        val = pv.value if pv.connected else defv
        return val if val else defv

    @property
    def monitperiod(self):
        return self.monitrate / self.adcfreq

    @property
    def monit1rate(self):
        defv = (362 if self._csorb.acc == 'BO' else 382) * 603
        pv = self._config_pvs_rb['INFOMONIT1Rate']
        val = pv.value if pv.connected else defv
        return val if val else defv
        return defv

    @property
    def monit1period(self):
        return self.monit1rate / self.adcfreq

    @property
    def kx(self):
        defv = 1
        pv = self._kx
        val = pv.value if pv.connected else defv
        return val if val else defv

    @property
    def ky(self):
        defv = 1
        pv = self._ky
        val = pv.value if pv.connected else defv
        return val if val else defv

    @property
    def ksum(self):
        defv = 1
        pv = self._ksum
        val = pv.value if pv.connected else defv
        return val if val else defv

    @property
    def mode(self):
        pv = self._config_pvs_rb['ACQBPMMode']
        return pv.value if pv.connected else _csbpm.OpModes.MultiBunch

    @mode.setter
    def mode(self, mo):
        pv = self._config_pvs_sp['ACQBPMMode']
        self._config_ok_vals['ACQBPMMode'] = mo
        if pv.connected:
            pv.value = mo

    @property
    def posx(self):
        pv = self._posx
        val = pv.value if pv.connected else None
        if val is not None:
            return self.ORB_CONV*val

    @property
    def posy(self):
        pv = self._posy
        val = pv.value if pv.connected else None
        if val is not None:
            return self.ORB_CONV*val

    @property
    def spposx(self):
        pv = self._spposx
        val = pv.value if pv.connected else None
        if val is not None:
            return self.ORB_CONV*val

    @property
    def spposy(self):
        pv = self._spposy
        val = pv.value if pv.connected else None
        if val is not None:
            return self.ORB_CONV*val

    @property
    def spsum(self):
        pv = self._spsum
        return pv.value if pv.connected else None

    @property
    def spanta(self):
        pv = self._spanta
        return pv.get() if pv.connected else None

    @property
    def spantb(self):
        pv = self._spantb
        return pv.get() if pv.connected else None

    @property
    def spantc(self):
        pv = self._spantc
        return pv.get() if pv.connected else None

    @property
    def spantd(self):
        pv = self._spantd
        return pv.get() if pv.connected else None

    @property
    def mtposx(self):
        pv = self._arrayx
        val = pv.get() if pv.connected else None
        if val is not None:
            return self.ORB_CONV*val

    @property
    def mtposy(self):
        pv = self._arrayy
        val = pv.get() if pv.connected else None
        if val is not None:
            return self.ORB_CONV*val

    @property
    def mtsum(self):
        pv = self._arrays
        return pv.get() if pv.connected else None

    @property
    def offsetx(self):
        pv = self._offsetx
        val = pv.value if pv.connected else None
        if val is not None:
            return self.ORB_CONV*val

    @property
    def offsety(self):
        pv = self._offsety
        val = pv.value if pv.connected else None
        if val is not None:
            return self.ORB_CONV*val

    @property
    def ctrl(self):
        # pv = self._config_pvs_rb['ACQCtrl']
        pv = self._config_pvs_rb['ACQTriggerEvent']
        return pv.value if pv.connected else None

    @ctrl.setter
    def ctrl(self, val):
        # pv = self._config_pvs_sp['ACQCtrl']
        pv = self._config_pvs_sp['ACQTriggerEvent']
        # self._config_ok_vals['ACQCtrl'] = val
        self._config_ok_vals['ACQTriggerEvent'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def acq_type(self):
        pv = self._config_pvs_rb['ACQChannel']
        return pv.value if pv.connected else None

    @acq_type.setter
    def acq_type(self, val):
        pv = self._config_pvs_sp['ACQChannel']
        self._config_ok_vals['ACQChannel'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def acq_trigger(self):
        # pv = self._config_pvs_rb['ACQTriggerType']
        pv = self._config_pvs_rb['ACQTrigger']
        return pv.value if pv.connected else None

    @acq_trigger.setter
    def acq_trigger(self, val):
        # pv = self._config_pvs_sp['ACQTriggerType']
        pv = self._config_pvs_sp['ACQTrigger']
        # self._config_ok_vals['ACQTriggerType'] = val
        self._config_ok_vals['ACQTrigger'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def acq_repeat(self):
        pv = self._config_pvs_rb['ACQTriggerRep']
        return pv.value if pv.connected else None

    @acq_repeat.setter
    def acq_repeat(self, val):
        pv = self._config_pvs_sp['ACQTriggerRep']
        self._config_ok_vals['ACQTriggerRep'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def acq_trig_datatype(self):
        # pv = self._config_pvs_rb['ACQTriggerDataChan']
        pv = self._config_pvs_rb['ACQDataTrigChan']
        return pv.value if pv.connected else None

    @acq_trig_datatype.setter
    def acq_trig_datatype(self, val):
        # pv = self._config_pvs_sp['ACQTriggerDataChan']
        pv = self._config_pvs_sp['ACQDataTrigChan']
        # self._config_ok_vals['ACQTriggerDataChan'] = val
        self._config_ok_vals['ACQDataTrigChan'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def acq_trig_datasel(self):
        pv = self._config_pvs_rb['ACQTriggerDataSel']
        return pv.value if pv.connected else None

    @acq_trig_datasel.setter
    def acq_trig_datasel(self, val):
        pv = self._config_pvs_sp['ACQTriggerDataSel']
        self._config_ok_vals['ACQTriggerDataSel'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def acq_trig_datathres(self):
        pv = self._config_pvs_rb['ACQTriggerDataThres']
        return pv.value if pv.connected else None

    @acq_trig_datathres.setter
    def acq_trig_datathres(self, val):
        pv = self._config_pvs_sp['ACQTriggerDataThres']
        self._config_ok_vals['ACQTriggerDataThres'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def acq_trig_datahyst(self):
        pv = self._config_pvs_rb['ACQTriggerDataHyst']
        return pv.value if pv.connected else None

    @acq_trig_datahyst.setter
    def acq_trig_datahyst(self, val):
        pv = self._config_pvs_sp['ACQTriggerDataHyst']
        self._config_ok_vals['ACQTriggerDataHyst'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def acq_trig_datapol(self):
        pv = self._config_pvs_rb['ACQTriggerDataPol']
        return pv.value if pv.connected else None

    @acq_trig_datapol.setter
    def acq_trig_datapol(self, val):
        pv = self._config_pvs_sp['ACQTriggerDataPol']
        self._config_ok_vals['ACQTriggerDataPol'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def tbt_sync_enbl(self):
        pv = self._config_pvs_rb['TbtTagEn']
        return pv.value if pv.connected else None

    @tbt_sync_enbl.setter
    def tbt_sync_enbl(self, val):
        pv = self._config_pvs_sp['TbtTagEn']
        self._config_ok_vals['TbtTagEn'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def tbt_mask_enbl(self):
        pv = self._config_pvs_rb['TbtDataMaskEn']
        return pv.value if pv.connected else None

    @tbt_mask_enbl.setter
    def tbt_mask_enbl(self, val):
        pv = self._config_pvs_sp['TbtDataMaskEn']
        self._config_ok_vals['TbtDataMaskEn'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def tbt_mask_begin(self):
        pv = self._config_pvs_rb['TbtDataMaskSamplesBeg']
        return pv.value if pv.connected else None

    @tbt_mask_begin.setter
    def tbt_mask_begin(self, val):
        pv = self._config_pvs_sp['TbtDataMaskSamplesBeg']
        self._config_ok_vals['TbtDataMaskSamplesBeg'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def tbt_mask_end(self):
        pv = self._config_pvs_rb['TbtDataMaskSamplesEnd']
        return pv.value if pv.connected else None

    @tbt_mask_end.setter
    def tbt_mask_end(self, val):
        pv = self._config_pvs_sp['TbtDataMaskSamplesEnd']
        self._config_ok_vals['TbtDataMaskSamplesEnd'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def nrsamplespost(self):
        # pv = self._config_pvs_rb['ACQNrSamplesPost']
        pv = self._config_pvs_rb['ACQSamplesPost']
        return pv.value if pv.connected else None

    @nrsamplespost.setter
    def nrsamplespost(self, val):
        # pv = self._config_pvs_sp['ACQNrSamplesPost']
        pv = self._config_pvs_sp['ACQSamplesPost']
        # self._config_ok_vals['ACQNrSamplesPost'] = val
        self._config_ok_vals['ACQSamplesPost'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def nrsamplespre(self):
        # pv = self._config_pvs_rb['ACQNrSamplesPre']
        pv = self._config_pvs_rb['ACQSamplesPre']
        return pv.value if pv.connected else None

    @nrsamplespre.setter
    def nrsamplespre(self, val):
        # pv = self._config_pvs_sp['ACQNrSamplesPre']
        pv = self._config_pvs_sp['ACQSamplesPre']
        # self._config_ok_vals['ACQNrSamplesPre'] = val
        self._config_ok_vals['ACQSamplesPre'] = val
        if pv.connected:
            pv.put(val, wait=False)

    @property
    def nrshots(self):
        # pv = self._config_pvs_rb['ACQNrShots']
        pv = self._config_pvs_rb['ACQShots']
        return pv.value if pv.connected else None

    @nrshots.setter
    def nrshots(self, val):
        # pv = self._config_pvs_sp['ACQNrShots']
        pv = self._config_pvs_sp['ACQShots']
        # self._config_ok_vals['ACQNrShots'] = val
        self._config_ok_vals['ACQShots'] = val
        if pv.connected:
            pv.put(val, wait=False)

    def calc_sp_multiturn_pos(self, **kwargs):
        nturns = kwargs.get('nturns', 1)
        refx = kwargs.get('refx', 0.0)
        refy = kwargs.get('refy', 0.0)
        refsum = kwargs.get('refsum', 0.0)
        maskbeg = kwargs.get('maskbeg', 0)
        maskend = kwargs.get('maskend', 0)
        bg = kwargs.get('bg', dict())

        wsize = self.tbtrate
        maskbeg = min(maskbeg, wsize - 2)
        maskend = min(maskend, wsize - maskbeg - 2)
        mask = slice(maskbeg, wsize - maskend)

        vs = {
            'A': self.spanta, 'B': self.spantb,
            'C': self.spantc, 'D': self.spantd}
        siz = None
        for a, v in vs.items():
            if v is None or v.size == 0:
                siz = 0
                break
            nzrs = v.size
            siz = nzrs if siz is None else min(siz, nzrs)
            if bg and bg[a].size >= v.size:
                vs[a] -= bg[a][:v.size]

        x = _np.full(nturns, refx)
        y = _np.full(nturns, refy)
        s = _np.full(nturns, refsum)

        # handle cases where length read is smaller than required.
        rnts = min(siz//wsize, nturns)
        if not (siz and rnts):
            return x, y, s

        for a, v in vs.items():
            v = v[:(rnts*wsize)]
            v = v.reshape(-1, wsize)[:, mask]
            vs[a] = _np.std(v, axis=1)

        s1, s2 = vs['A'] + vs['B'], vs['D'] + vs['C']
        m1 = _np.logical_not(_np.isclose(s1, 0.0))
        m2 = _np.logical_not(_np.isclose(s2, 0.0))
        d1 = (vs['A'][m1] - vs['B'][m1]) / s1[m1]
        d2 = (vs['D'][m2] - vs['C'][m2]) / s2[m2]
        x[:rnts][m1] = (d1 + d2) * self.kx/2 * self.ORB_CONV
        y[:rnts][m2] = (d1 - d2) * self.ky/2 * self.ORB_CONV
        s[:rnts] = (s1 + s2) * self.ksum
        return x, y, s


class TimingConfig(_BaseTimingConfig):

    def __init__(self, acc):
        super().__init__(acc)
        trig = self._csorb.TRIGGER_ACQ_NAME
        opt = {'connection_timeout': TIMEOUT}
        evt = self._csorb.EVT_ACQ_NAME
        src_val = self._csorb.AcqExtEvtSrc._fields.index(evt)
        src_val = self._csorb.AcqExtEvtSrc[src_val]
        self._config_ok_vals = {
            'NrPulses': 1,
            'State': _cstime.Const.TrigStates.Enbl}
        if _HLTimesearch.has_delay_type(trig):
            self._config_ok_vals['RFDelayType'] = \
                                    _cstime.Const.TrigDlyTyp.Manual
        pref_name = LL_PREF + trig + ':'
        self._config_pvs_rb = {
            'Delay': _PV(pref_name + 'Delay-RB', **opt),
            'NrPulses': _PV(pref_name + 'NrPulses-RB', **opt),
            'Duration': _PV(pref_name + 'Duration-RB', **opt),
            'State': _PV(pref_name + 'State-Sts', **opt)}
        self._config_pvs_sp = {
            'NrPulses': _PV(pref_name + 'NrPulses-SP', **opt),
            'State': _PV(pref_name + 'State-Sel', **opt)}
        if _HLTimesearch.has_delay_type(trig):
            self._config_pvs_rb['RFDelayType'] = _PV(
                            pref_name + 'RFDelayType-Sts', **opt)
            self._config_pvs_sp['RFDelayType'] = _PV(
                            pref_name + 'RFDelayType-Sel', **opt)

    @property
    def nrpulses(self):
        pv = self._config_pvs_rb['NrPulses']
        return pv.value if pv.connected else None

    @nrpulses.setter
    def nrpulses(self, val):
        pv = self._config_pvs_sp['NrPulses']
        if pv.connected:
            self._config_ok_vals['NrPulses'] = val
            pv.put(val, wait=False)

    @property
    def duration(self):
        pv = self._config_pvs_rb['Duration']
        return pv.value if pv.connected else None

    @property
    def delay(self):
        pv = self._config_pvs_rb['Delay']
        return pv.value if pv.connected else None
