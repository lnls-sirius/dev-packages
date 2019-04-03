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
            'ACQTriggerDataHyst': 0}
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
            'ACQTriggerDataHyst': 'ACQTriggerDataHyst-SP'}
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
            'ACQTriggerDataHyst': 'ACQTriggerDataHyst-RB'}
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
        # Not implemented in BPMs IOCs yet.
        # pv = self._config_pvs_rb['INFOMONIT1Rate']
        # val = pv.value if pv.connected else defv
        # return val if val else defv
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

        size = self.tbtrate
        maskbeg = min(maskbeg, size - 2)
        maskend = min(maskend, size - maskbeg - 2)
        mask = slice(maskbeg, size - maskend)

        an = {
            'A': self.spanta, 'B': self.spantb,
            'C': self.spantc, 'D': self.spantd}
        vs = dict()
        siz = None
        for a, v in an.items():
            if v is None or v.size == 0:
                siz = 0
                break
            nzrs = v.size  # _np.sum(v != 0)
            siz = nzrs if siz is None else min(siz, nzrs)
            vs[a] = v

        x = _np.full(nturns, refx)
        y = _np.full(nturns, refy)
        s = _np.full(nturns, refsum)

        # handle cases where length read is smaller than required.
        rnts = min(siz//downs, nturns)
        if not (siz and rnts):
            return x, y, s

        for a, v in vs.items():
            v = v[:(rnts*downs)]
            v = v.reshape(-1, downs)[:, mask]
            vs[a] = _np.std(v, axis=1)

        s1, s2 = vs['A'] + vs['B'], vs['D'] + vs['C']
        d1 = (vs['A'] - vs['B']) / s1
        d2 = (vs['D'] - vs['C']) / s2
        x[:rnts] = (d1 + d2)*self.kx/2 * self.ORB_CONV
        y[:rnts] = (d1 - d2)*self.ky/2 * self.ORB_CONV
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
            'Src': src_val,
            'Delay': 0.0,
            'NrPulses': 1,
            'Duration': 100.0,
            'State': _cstime.Const.TrigStates.Enbl,
            'Polarity': _cstime.Const.TrigPol.Normal}
        if _HLTimesearch.has_delay_type(trig):
            self._config_ok_vals['RFDelayType'] = \
                                    _cstime.Const.TrigDlyTyp.Manual
        pref_name = LL_PREF + trig + ':'
        self._config_pvs_rb = {
            'Src': _PV(pref_name + 'Src-Sts', **opt),
            'Delay': _PV(pref_name + 'Delay-RB', **opt),
            'NrPulses': _PV(pref_name + 'NrPulses-RB', **opt),
            'Duration': _PV(pref_name + 'Duration-RB', **opt),
            'State': _PV(pref_name + 'State-Sts', **opt),
            'Polarity': _PV(pref_name + 'Polarity-Sts', **opt)}
        self._config_pvs_sp = {
            'Src': _PV(pref_name + 'Src-Sel', **opt),
            'Delay': _PV(pref_name + 'Delay-SP', **opt),
            'NrPulses': _PV(pref_name + 'NrPulses-SP', **opt),
            'Duration': _PV(pref_name + 'Duration-SP', **opt),
            'State': _PV(pref_name + 'State-Sel', **opt),
            'Polarity': _PV(pref_name + 'Polarity-Sel', **opt)}
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

    @duration.setter
    def duration(self, val):
        pv = self._config_pvs_sp['Duration']
        if pv.connected:
            self._config_ok_vals['Duration'] = val
            pv.put(val, wait=False)

    @property
    def delay(self):
        pv = self._config_pvs_rb['Delay']
        return pv.value if pv.connected else None

    @delay.setter
    def delay(self, val):
        pv = self._config_pvs_sp['Delay']
        if pv.connected:
            self._config_ok_vals['Delay'] = val
            pv.put(val, wait=False)

    @property
    def evtsrc(self):
        pv = self._config_pvs_rb['Src']
        return pv.value if pv.connected else None

    @evtsrc.setter
    def evtsrc(self, val):
        pv = self._config_pvs_sp['Src']
        self._config_ok_vals['Src'] = val
        if pv.connected:
            pv.put(val, wait=False)
