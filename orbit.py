"""Module to deal with orbit acquisition."""
import os as _os
import time as _time
from copy import deepcopy as _dcopy
from math import ceil as _ceil
import logging as _log
from functools import partial as _part
from threading import Lock
import numpy as _np
from epics import PV as _PV
import siriuspy.util as _util
import siriuspy.csdevice.bpms as _csbpm
import siriuspy.csdevice.timesys as _cstime
from siriuspy.search import HLTimeSearch as _HLTimesearch
from siriuspy.thread import RepeaterThread as _Repeat
from siriuspy.envars import vaca_prefix as LL_PREF
from .base_class import (
    BaseClass as _BaseClass,
    BaseTimingConfig as _BaseTimingConfig)

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

    def calc_sp_multiturn_pos(self, nturns, refx=0, refy=0, refsum=0):
        downs = self.tbtrate
        samp = downs * nturns
        an = {
            'A': self.spanta, 'B': self.spantb,
            'C': self.spantc, 'D': self.spantd}
        vs = dict()
        zrs = np.zeros(samp*[0], dtype=bool)
        for a, v in an.items():
            nv = _np.full(samp, 0)
            if v is None:
                pass
            elif v.size < samp:
                nv[:v.size] = v
            elif v.size >= samp:
                nv = v[:samp]
            zrs &= nv == 0
            vs[a] = _np.std(nv.reshape(-1, downs), axis=1)

        # handle cases where length read is smaller than required.
        vld = _np.sum(zrs.reshape(-1, downs, axis=1)) == 0
        vs = {a: v[vld] for a, v in vs.items()}

        d1 = (vs['A'] - vs['B']) / (vs['A'] + vs['B'])
        d2 = (vs['D'] - vs['C']) / (vs['D'] + vs['C'])
        x = _np.full(nturns, refx)
        y = _np.full(nturns, refy)
        s = _np.full(nturns, refsum)
        x[vld] = (d1 + d2)*self.kx/2
        y[vld] = (d1 - d2)*self.ky/2
        s[vld] = _np.sum(vs.values()) * self.ksum
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


class BaseOrbit(_BaseClass):
    pass


class EpicsOrbit(BaseOrbit):
    """Class to deal with orbit acquisition."""

    def get_database(self):
        """Get the database of the class."""
        db = self._csorb.get_orbit_database()
        prop = 'fun_set_pv'
        db['SOFBMode-Sel'][prop] = self.set_orbit_mode
        db['TrigAcqConfig-Cmd'][prop] = self.trig_acq_config_bpms
        db['TrigAcqCtrl-Sel'][prop] = self.set_trig_acq_control
        db['TrigAcqChan-Sel'][prop] = self.set_trig_acq_channel
        db['TrigDataChan-Sel'][prop] = self.set_trig_acq_datachan
        db['TrigAcqTrigger-Sel'][prop] = self.set_trig_acq_trigger
        db['TrigAcqRepeat-Sel'][prop] = self.set_trig_acq_repeat
        db['TrigDataSel-Sel'][prop] = self.set_trig_acq_datasel
        db['TrigDataThres-SP'][prop] = self.set_trig_acq_datathres
        db['TrigDataHyst-SP'][prop] = self.set_trig_acq_datahyst
        db['TrigDataPol-Sel'][prop] = self.set_trig_acq_datapol
        db['TrigExtDuration-SP'][prop] = self.set_trig_acq_extduration
        db['TrigExtDelay-SP'][prop] = self.set_trig_acq_extdelay
        db['TrigExtEvtSrc-Sel'][prop] = self.set_trig_acq_extsource
        db['TrigNrSamplesPre-SP'][prop] = _part(
            self.set_trig_acq_nrsamples, ispost=False)
        db['TrigNrSamplesPost-SP'][prop] = _part(
            self.set_trig_acq_nrsamples, ispost=True)
        db['RefOrbX-SP'][prop] = _part(self.set_ref_orbit, 'X')
        db['RefOrbY-SP'][prop] = _part(self.set_ref_orbit, 'Y')
        db['OfflineOrbX-SP'][prop] = _part(self.set_offline_orbit, 'X')
        db['OfflineOrbY-SP'][prop] = _part(self.set_offline_orbit, 'Y')
        db['SmoothNrPts-SP'][prop] = self.set_smooth_npts
        db['SmoothMethod-Sel'][prop] = self.set_smooth_method
        db['SmoothReset-Cmd'][prop] = self.set_smooth_reset
        db['OrbAcqRate-SP'][prop] = self.set_orbit_acq_rate
        db['TrigNrShots-SP'][prop] = self.set_trig_acq_nrshots
        if self.isring:
            db['MTurnIdx-SP'][prop] = self.set_orbit_multiturn_idx
            db['MTurnDownSample-SP'][prop] = self.set_trig_acq_downsample

        db = super().get_database(db)
        return db

    def __init__(self, acc, prefix='', callback=None):
        """Initialize the instance."""
        super().__init__(acc, prefix=prefix, callback=callback)

        self._mode = self._csorb.SOFBMode.Offline
        self.ref_orbs = {
                'X': _np.zeros(self._csorb.NR_BPMS),
                'Y': _np.zeros(self._csorb.NR_BPMS)}
        self._load_ref_orbs()
        self.raw_orbs = {'X': [], 'Y': []}
        self.raw_sporbs = {'X': [], 'Y': [], 'Sum': []}
        self.raw_mtorbs = {'X': [], 'Y': [], 'Sum': []}
        self._lock_raw_orbs = Lock()
        self.smooth_orb = {'X': None, 'Y': None}
        self.smooth_sporb = {'X': None, 'Y': None, 'Sum': None}
        self.smooth_mtorb = {'X': None, 'Y': None, 'Sum': None}
        self.offline_orbit = {
                'X': _np.zeros(self._csorb.NR_BPMS),
                'Y': _np.zeros(self._csorb.NR_BPMS)}
        self._smooth_npts = 1
        self._smooth_meth = self._csorb.SmoothMeth.Average
        self._acqrate = 10
        self._oldacqrate = self._acqrate
        self._acqtrignrsamplespre = 50
        self._acqtrignrsamplespost = 50
        self._acqtrignrshots = 1
        self._multiturnidx = 0
        self._acqtrigdownsample = 1
        self._timevector = None
        self._ring_extension = 1
        self.bpms = [BPM(name) for name in self._csorb.BPM_NAMES]
        self.timing = TimingConfig(acc)
        self._orbit_thread = _Repeat(
                        1/self._acqrate, self._update_orbits, niter=0)
        self._orbit_thread.start()
        self._update_time_vector()

    @property
    def mode(self):
        return self._mode

    @property
    def acqtrignrsamples(self):
        return self._acqtrignrsamplespre + self._acqtrignrsamplespost

    def set_ring_extension(self, val):
        maval = self._csorb.MAX_RINGSZ
        val = 1 if val < 1 else int(val)
        val = maval if val > maval else val
        if val == self.ring_extension:
            return True
        with self._lock_raw_orbs:
            self._reset_orbs()
            self.ring_extension = val
            nrb = val * self._csorb.NR_BPMS
            for pln in self.offline_orbit.keys():
                orb = self.offline_orbit[pln]
                if orb.size < nrb:
                    orb2 = np.zeros(nrb, dtype=float)
                    orb2[:orb.size] = orb
                    orb = orb2
                self.offline_orbit[plane] = orb
                self.run_callbacks('OfflineOrb'+plane+'-RB', orb[:nrb])
                orb = self.ref_orbs[pln]
                if orb.size < nrb:
                    nrep = _ceil(nrb/orb.size)
                    orb2 = _np.tile(orb, nrep)
                    orb = orb2[:nrb]
                self.ref_orbs[plane] = orb
                self.run_callbacks('RefOrb'+plane+'-RB', orb[:nrb])
        self._save_ref_orbits()
        return True

    def get_orbit(self, reset=False):
        """Return the orbit distortion."""
        nrb = self.ring_extension * self._csorb.NR_BPMS
        refx = self.ref_orbs['X'][:nrb]
        refy = self.ref_orbs['Y'][:nrb]
        if self._mode == self._csorb.SOFBMode.Offline:
            orbx = self.offline_orbit['X'][:nrb]
            orby = self.offline_orbit['Y'][:nrb]
            return _np.hstack([orbx-refx, orby-refy])

        if reset:
            with self._lock_raw_orbs:
                self._reset_orbs()
            _time.sleep(self._smooth_npts/self._acqrate)

        if self.isring and self._mode == self._csorb.SOFBMode.MultiTurn:
            orbs = self.smooth_mtorb
            getorb = self._get_orbit_multiturn
        elif self._mode == self._csorb.SOFBMode.SinglePass:
            orbs = self.smooth_sporb
            getorb = self._get_orbit_singlepass
        elif self.isring and self._mode == self._csorb.SOFBMode.SlowOrb:
            orbs = self.smooth_orb
            getorb = self._get_orbit_online

        for _ in range(3 * self._smooth_npts):
            if orbs['X'] is None or orbs['Y'] is None:
                _time.sleep(1/self._acqrate)
                continue
            orbx, orby = getorb(orbs)
            break
        else:
            msg = 'ERR: get orbit function timeout.'
            self._update_log(msg)
            _log.error(msg[5:])
            orbx = refx
            orby = refy
        return _np.hstack([orbx-refx, orby-refy])

    def _get_orbit_online(self, orbs):
        return orbs['X'], orbs['Y']

    def _get_orbit_singlepass(self, orbs):
        return orbs['X'], orbs['Y']

    def _get_orbit_multiturn(self, orbs):
        idx = self._multiturnidx
        return orbs['X'][idx, :], orbs['Y'][idx, :]

    def set_offline_orbit(self, plane, orb):
        msg = 'Setting New Offline Orbit.'
        self._update_log(msg)
        _log.info(msg)
        orb = _np.array(orb, dtype=float)
        nrb = self.ring_extension * self._csorb.NR_BPMS
        if orb.size % self._csorb.NR_BPMS:
            msg = 'ERR: Wrong OfflineOrb Size.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        elif orb.size < nrb:
            orb2 = np.zeros(nrb, dtype=float)
            orb2[:orb.size] = orb
            orb = orb2
        self.offline_orbit[plane] = orb
        self.run_callbacks('OfflineOrb'+plane+'-RB', orb[:nrb])
        return True

    def set_smooth_npts(self, num):
        self._smooth_npts = num
        self.run_callbacks('SmoothNrPts-RB', num)
        return True

    def set_smooth_method(self, meth):
        self._smooth_meth = meth
        self.run_callbacks('SmoothMethod-Sts', meth)
        return True

    def set_smooth_reset(self, _):
        with self._lock_raw_orbs:
            self._reset_orbs()
        return True

    def set_ref_orbit(self, plane, orb):
        msg = 'Setting New Reference Orbit.'
        self._update_log(msg)
        _log.info(msg)
        orb = _np.array(orb, dtype=float)
        nrb = self._csorb.NR_BPMS * self.ring_extension
        if orb.size % self._csorb.NR_BPMS:
            msg = 'ERR: Wrong RefOrb Size.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        elif orb.size < nrb:
            msg = 'WARN: Orb Size is too small. Replicating...'
            self._update_log(msg)
            _log.error(msg[6:])
            nrep = int(nrb//orb.size) + 1
            orb2 = _np.repmat(orb, nrep)
            orb = orb2[:nrb]
        self.ref_orbs[plane] = orb
        self._save_ref_orbits()
        with self._lock_raw_orbs:
            self._reset_orbs()
        self.run_callbacks('RefOrb'+plane+'-RB', orb[:nrb])
        return True

    def set_orbit_acq_rate(self, value):
        trigmds = [self._csorb.SOFBMode.SinglePass, ]
        if self.isring:
            trigmds.append(self._csorb.SOFBMode.MultiTurn)
        if self._mode in trigmds and value > 2:
            msg = 'ERR: In triggered mode cannot set rate > 2.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        self._acqrate = value
        self._orbit_thread.interval = 1/value
        self.run_callbacks('OrbAcqRate-RB', value)
        return True

    def set_orbit_mode(self, value):
        trigmds = [self._csorb.SOFBMode.SinglePass, ]
        if self.isring:
            trigmds.append(self._csorb.SOFBMode.MultiTurn)
        bo1 = self._mode in trigmds
        bo2 = value not in trigmds
        self._mode = value
        if bo1 == bo2:
            acqrate = 2 if not bo2 else self._oldacqrate
            self._oldacqrate = self._acqrate
            self.run_callbacks('OrbAcqRate-SP', acqrate)
            self.set_orbit_acq_rate(acqrate)
        self.run_callbacks('SOFBMode-Sts', value)
        with self._lock_raw_orbs:
            self._reset_orbs()
            if self._mode in trigmds:
                self.trig_acq_config_bpms()
        return True

    def set_orbit_multiturn_idx(self, value):
        maxidx = self.acqtrignrsamples // self._acqtrigdownsample
        maxidx *= self._acqtrignrshots
        if value >= maxidx:
            value = maxidx-1
            msg = 'WARN: MTurnIdx is too large. Redefining...'
            self._update_log(msg)
            _log.warning(msg[6:])
        with self._lock_raw_orbs:
            self._multiturnidx = int(value)
        self.run_callbacks('MTurnIdx-RB', self._multiturnidx)
        self.run_callbacks(
            'MTurnIdxTime-Mon', self._timevector[self._multiturnidx])
        return True

    def trig_acq_config_bpms(self, *args):
        trigmds = [self._csorb.SOFBMode.SinglePass, ]
        if self.isring:
            trigmds.append(self._csorb.SOFBMode.MultiTurn)
        if self._mode not in trigmds:
            msg = 'ERR: Change to a Triggered mode first.'
            self._update_log(msg)
            _log.error(msg[5:])
            return False
        for bpm in self.bpms:
            if self.isring and self._mode == self._csorb.SOFBMode.MultiTurn:
                bpm.mode = _csbpm.OpModes.MultiBunch
            else:
                bpm.mode = _csbpm.OpModes.SinglePass
            bpm.configure()
        self.timing.configure()
        return True

    def set_trig_acq_control(self, value):
        for bpm in self.bpms:
            bpm.ctrl = value
        self.run_callbacks('TrigAcqCtrl-Sts', value)
        return True

    def set_trig_acq_channel(self, value):
        try:
            val = self._csorb.TrigAcqChan._fields[value]
            val = _csbpm.AcqChan._fields.index(val)
        except (IndexError, ValueError):
            return False
        for bpm in self.bpms:
            bpm.acq_type = val
        self.run_callbacks('TrigAcqChan-Sts', value)
        self._update_time_vector(channel=value)
        return True

    def set_trig_acq_trigger(self, value):
        val = _csbpm.AcqTrigTyp.Data
        if value == self._csorb.TrigAcqTrig.External:
            val = _csbpm.AcqTrigTyp.External
        for bpm in self.bpms:
            bpm.acq_trigger = val
        self.run_callbacks('TrigAcqTrigger-Sts', value)
        return True

    def set_trig_acq_repeat(self, value):
        for bpm in self.bpms:
            bpm.acq_repeat = value
        self.run_callbacks('TrigAcqRepeat-Sts', value)
        return True

    def set_trig_acq_datachan(self, value):
        try:
            val = self._csorb.TrigAcqDataChan._fields[value]
            val = _csbpm.AcqChan._fields.index(val)
        except (IndexError, ValueError):
            return False
        for bpm in self.bpms:
            bpm.acq_trig_datatype = val
        self.run_callbacks('TrigDataChan-Sts', value)
        return True

    def set_trig_acq_datasel(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datasel = value
        self.run_callbacks('TrigDataSel-Sts', value)
        return True

    def set_trig_acq_datathres(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datathres = value
        self.run_callbacks('TrigDataThres-RB', value)
        return True

    def set_trig_acq_datahyst(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datahyst = value
        self.run_callbacks('TrigDataHyst-RB', value)
        return True

    def set_trig_acq_datapol(self, value):
        for bpm in self.bpms:
            bpm.acq_trig_datapol = value
        self.run_callbacks('TrigDataPol-Sts', value)
        return True

    def set_trig_acq_extduration(self, value):
        self.timing.duration = value
        self._update_time_vector(duration=value)
        self.run_callbacks('TrigExtDuration-RB', value)
        return True

    def set_trig_acq_extdelay(self, value):
        self.timing.delay = value
        self._update_time_vector(delay=value)
        self.run_callbacks('TrigExtDelay-RB', value)
        return True

    def set_trig_acq_extsource(self, value):
        self.timing.evtsrc = self._csorb.AcqExtEvtSrc[value]
        self.run_callbacks('TrigExtEvtSrc-Sts', value)
        return True

    def set_trig_acq_nrsamples(self, value, ispost=True):
        Nmax = self._csorb.MAX_MT_ORBS // self._acqtrignrshots
        Nmax *= self._acqtrigdownsample
        suf = 'post' if ispost else 'pre'
        osuf = 'pre' if ispost else 'post'
        value += getattr(self, '_acqtrignrsamples'+osuf)

        nval = value if value <= Nmax else Nmax
        nval = self._find_new_nrsamples(nval, self._acqtrigdownsample)
        if nval != value:
            value = nval
            msg = 'WARN: Not possible to set NrSamples. Redefining..'
            self._update_log(msg)
            _log.warning(msg[6:])

        value -= getattr(self, '_acqtrignrsamples'+osuf)
        with self._lock_raw_orbs:
            for bpm in self.bpms:
                setattr(bpm, 'nrsamples'+suf, value)
            self._reset_orbs()
            setattr(self, '_acqtrignrsamples'+suf, value)
        self.run_callbacks('TrigNrSamples'+suf.title()+'-RB', value)
        self._update_time_vector()
        return True

    def set_trig_acq_nrshots(self, value):
        pntspshot = self.acqtrignrsamples // self._acqtrigdownsample
        nrpoints = pntspshot * value
        if nrpoints > self._csorb.MAX_MT_ORBS:
            value = self._csorb.MAX_MT_ORBS // pntspshot
            msg = 'WARN: Not possible to set NrShots. Redefining...'
            self._update_log(msg)
            _log.warning(msg[6:])
        with self._lock_raw_orbs:
            for bpm in self.bpms:
                bpm.nrshots = value
            self.timing.nrpulses = value
            self._reset_orbs()
            self._acqtrignrshots = value
        self.run_callbacks('TrigNrShots-RB', value)
        self._update_time_vector()
        return True

    def set_trig_acq_downsample(self, value):
        down = self._find_new_downsample(self.acqtrignrsamples, value)
        nrpoints = (self.acqtrignrsamples // down) * self._acqtrignrshots
        if nrpoints > self._csorb.MAX_MT_ORBS:
            down = self._find_new_downsample(
                self.acqtrignrsamples, value, onlyup=True)
        if down != value:
            value = down
            msg = 'WARN: DwnSpl Must divide NRSamples. Redefining...'
            self._update_log(msg)
            _log.warning(msg[6:])
        self._acqtrigdownsample = value
        self.run_callbacks('MTurnDownSample-RB', value)
        self._update_time_vector()
        return True

    def _update_time_vector(self, delay=None, duration=None, channel=None):
        if not self.isring:
            return
        dl = (delay or self.timing.delay or 0.0) * 1e-6  # from us to s
        dur = (duration or self.timing.duration or 0.0) * 1e-6  # from us to s
        channel = channel or self.bpms[0].acq_type or 0
        # revolution period in s
        if channel == self._csorb.TrigAcqChan.Monit1:
            dt = self.bpms[0].monit1period
        elif channel == self._csorb.TrigAcqChan.FOFB:
            dt = self.bpms[0].fofbperiod
        else:
            dt = self.bpms[0].tbtperiod
        dt *= self._acqtrigdownsample
        nrptpst = self.acqtrignrsamples // self._acqtrigdownsample
        offset = self._acqtrignrsamplespre / self._acqtrigdownsample
        nrst = self._acqtrignrshots
        a = _np.arange(nrst)
        b = _np.arange(nrptpst, dtype=float) + (0.5 - offset)
        vect = dl + dur/nrst*a[:, None] + dt*b[None, :]
        self._timevector = vect.flatten()
        self.run_callbacks('MTurnTime-Mon', self._timevector)
        self.set_orbit_multiturn_idx(self._multiturnidx)

    def _load_ref_orbs(self):
        if _os.path.isfile(self._csorb.REFORBFNAME):
            self.ref_orbs['X'], self.ref_orbs['Y'] = _np.loadtxt(
                                        self._csorb.REFORBFNAME, unpack=True)

    def _save_ref_orbits(self):
        orbs = _np.array([self.ref_orbs['X'], self.ref_orbs['Y']]).T
        try:
            path = _os.path.split(self._csorb.REFORBFNAME)[0]
            if not _os.path.isdir(path):
                _os.mkdir(path)
            _np.savetxt(self._csorb.REFORBFNAME, orbs)
        except FileNotFoundError:
            msg = 'WARN: Could not save reference orbit in file.'
            self._update_log(msg)
            _log.warning(msg[6:])

    def _reset_orbs(self):
        self.raw_orbs = {'X': [], 'Y': []}
        self.smooth_orb = {'X': None, 'Y': None}
        self.raw_sporbs = {'X': [], 'Y': [], 'Sum': []}
        self.smooth_sporb = {'X': None, 'Y': None, 'Sum': None}
        self.raw_mtorbs = {'X': [], 'Y': [], 'Sum': []}
        self.smooth_mtorb = {'X': None, 'Y': None, 'Sum': None}

    def _update_orbits(self):
        count = 0
        if self.isring and self._mode == self._csorb.SOFBMode.MultiTurn:
            self._update_multiturn_orbits()
            count = len(self.raw_mtorbs['X'])
        elif self._mode == self._csorb.SOFBMode.SinglePass:
            self._update_online_orbits(sp=True)
            # self._update_singlepass_orbits()
            count = len(self.raw_sporbs['X'])
        elif self.isring:
            self._update_online_orbits(sp=False)
            count = len(self.raw_orbs['X'])
        self.run_callbacks('BufferCount-Mon', count)

    def _update_online_orbits(self, sp=False):
        orb = _np.zeros(self._csorb.NR_BPMS, dtype=float)
        orbs = {'X': orb, 'Y': orb.copy(), 'Sum': orb.copy()}
        ref = self.ref_orbs
        for i, bpm in enumerate(self.bpms):
            pos = bpm.spposx if sp else bpm.posx
            orbs['X'][i] = ref['X'][i] if pos is None else pos
            pos = bpm.spposy if sp else bpm.posy
            orbs['Y'][i] = ref['Y'][i] if pos is None else pos
            pos = bpm.spsum if sp else 0.0
            orbs['Sum'][i] = 0.0 if pos is None else pos

        planes = ('X', 'Y', 'Sum') if sp else ('X', 'Y')
        smooth = self.smooth_sporb if sp else self.smooth_orb
        for plane in planes:
            with self._lock_raw_orbs:
                raws = self.raw_sporbs if sp else self.raw_orbs
                raws[plane].append(orbs[plane])
                raws[plane] = raws[plane][-self._smooth_npts:]
                if self._smooth_meth == self._csorb.SmoothMeth.Average:
                    orb = _np.mean(raws[plane], axis=0)
                else:
                    orb = _np.median(raws[plane], axis=0)
            smooth[plane] = orb
            pref = 'SPass' if sp else 'Slow'
            name = ('Orb' if plane != 'Sum' else '') + plane
            self.run_callbacks(pref + name + '-Mon', list(orb))

    def _update_multiturn_orbits(self):
        orbs = {'X': [], 'Y': [], 'Sum': []}
        with self._lock_raw_orbs:  # I need the lock here to assure consistency
            samp = self.acqtrignrsamples * self._acqtrignrshots
            nr_bpms = self._csorb.NR_BPMS
            down = self._acqtrigdownsample
            idx = self._multiturnidx
            nr_pts = self._smooth_npts
            for i, bpm in enumerate(self.bpms):
                posx = bpm.mtposx
                if posx is None or posx.size < samp:
                    posx = _np.full(samp, self.ref_orbs['X'][i])
                posy = bpm.mtposy
                if posy is None or posy.size < samp:
                    posy = _np.full(samp, self.ref_orbs['Y'][i])
                psum = bpm.mtsum
                if psum is None or psum.size < samp:
                    psum = _np.full(samp, 0)
                orbs['X'].append(posx[:samp])
                orbs['Y'].append(posy[:samp])
                orbs['Sum'].append(psum[:samp])

            for pln, raw in self.raw_mtorbs.items():
                norb = _np.array(orbs[pln], dtype=float)
                raw.append(norb)
                del raw[:-nr_pts]
                if self._smooth_meth == self._csorb.SmoothMeth.Average:
                    orb = _np.mean(raw, axis=0)
                else:
                    orb = _np.median(raw, axis=0)
                if down > 1:
                    orb = _np.mean(orb.reshape(nr_bpms, -1, down), axis=2)
                orb = orb.transpose()
                self.smooth_mtorb[pln] = orb
                orbs[pln] = orb
        for pln, orb in orbs.items():
            name = ('Orb' if pln != 'Sum' else '') + pln
            self.run_callbacks('MTurn' + name + '-Mon', orb.flatten())
            self.run_callbacks(
                'MTurnIdx' + name + '-Mon', orb[idx, :].flatten())

    def _update_singlepass_orbits(self):
        orbs = {'X': [], 'Y': [], 'Sum': []}
        nr_turns = 10
        with self._lock_raw_orbs:  # I need the lock here to assure consistency
            nr_pts = self._smooth_npts
            for i, bpm in enumerate(self.bpms):
                orbx, orby, Sum = bpm.calc_sp_multiturn_pos(
                    nr_turns, self.ref_orbs['X'][i], self.ref_orbs['Y'][i])
                orbs['X'].append(orbx)
                orbs['Y'].append(orby)
                orbs['Sum'].append(Sum)

            for pln, raw in self.raw_sporbs.items():
                norb = _np.array(orbs[pln], dtype=float)
                raw.append(norb)
                del raw[:-nr_pts]
                if self._smooth_meth == self._csorb.SmoothMeth.Average:
                    orb = _np.mean(raw, axis=0)
                else:
                    orb = _np.median(raw, axis=0)
                orb = orb.flatten()
                self.smooth_sporb[pln] = orb
                name = ('Orb' if pln != 'Sum' else '') + pln
                self.run_callbacks('SPass' + name + '-Mon', list(orb))

    def _update_status(self):
        status = 0b11111
        status = _util.update_bit(
                    status, bit_pos=0, bit_val=not self.timing.connected)
        status = _util.update_bit(
                    status, bit_pos=1, bit_val=not self.timing.is_ok)

        nok = not all(bpm.connected for bpm in self.bpms)
        status = _util.update_bit(v=status, bit_pos=2, bit_val=nok)

        nok = not all(bpm.state for bpm in self.bpms)
        status = _util.update_bit(v=status, bit_pos=3, bit_val=nok)

        nok = not all(bpm.is_ok for bpm in self.bpms)
        status = _util.update_bit(v=status, bit_pos=4, bit_val=nok)

        self._status = status
        self.run_callbacks('OrbStatus-Mon', status)
        self._update_bpmoffsets()

    def _update_bpmoffsets(self):
        orbx = _np.zeros(self._csorb.NR_BPMS, dtype=float)
        orby = orbx.copy()
        for i, bpm in enumerate(self.bpms):
            orbx[i] = bpm.offsetx or 0
            orby[i] = bpm.offsety or 0
        self.run_callbacks('BPMOffsetX-Mon', orbx)
        self.run_callbacks('BPMOffsetY-Mon', orby)

    @staticmethod
    def _find_new_downsample(N, d, onlyup=False):
        if d > N:
            return N
        if not N % d:
            return d
        lim = min(N-d+1, d) if not onlyup else N-d+1
        for i in range(1, lim):
            if not N % (d+i):
                return d+i
            elif not onlyup and not N % (d-i):
                return d-i

    @staticmethod
    def _find_new_nrsamples(N, d):
        return d*(N//d) if N >= d else d
