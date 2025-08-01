"""Module to deal with orbit acquisition."""
import logging as _log

import numpy as _np

from ..diagbeam.bpm.csdev import Const as _CSBPM
from ..envars import VACA_PREFIX as LL_PREF
from ..epics import PV as _PV
from ..search import HLTimeSearch as _HLTimesearch
from ..timesys.csdev import Const as _TIConst
from .base_class import BaseTimingConfig as _BaseTimingConfig

TIMEOUT = 0.05


class BPM(_BaseTimingConfig):
    """."""

    def __init__(self, name, callback=None):
        """."""
        super().__init__(name[:2], callback)
        self.has_news = True

        self._name = name
        self._orb_conv_unit = self._csorb.ORBIT_CONVERSION_UNIT
        pvpref = LL_PREF + ("-" if LL_PREF else "") + self._name + ":"
        opt = {"connection_timeout": TIMEOUT, "auto_monitor": False}
        self._pvs['poskx'] = _PV(pvpref + "PosKx-RB", **opt)
        self._pvs['posky'] = _PV(pvpref + "PosKy-RB", **opt)
        self._pvs['ksum'] = _PV(pvpref + "PosKsum-RB", **opt)
        self._pvs['polyx'] = _PV(pvpref + "GEN_PolyXArrayCoeff-RB", **opt)
        self._pvs['polyy'] = _PV(pvpref + "GEN_PolyYArrayCoeff-RB", **opt)
        self._pvs['arraya'] = _PV(pvpref + "GENAmplAData", **opt)
        self._pvs['arrayb'] = _PV(pvpref + "GENAmplBData", **opt)
        self._pvs['arrayc'] = _PV(pvpref + "GENAmplCData", **opt)
        self._pvs['arrayd'] = _PV(pvpref + "GENAmplDData", **opt)
        self._pvs['arrayx'] = _PV(pvpref + "GENPosXData", **opt)
        self._pvs['arrayy'] = _PV(pvpref + "GENPosYData", **opt)
        self._pvs['arrays'] = _PV(pvpref + "GENSumData", **opt)
        opt.pop("auto_monitor")
        self._pvs['offsetx'] = _PV(pvpref + "PosXOffset-RB", **opt)
        self._pvs['offsety'] = _PV(pvpref + "PosYOffset-RB", **opt)
        self._config_ok_vals = {
            "SwMode": _CSBPM.SwModes.switching,
            "ACQChannel": _CSBPM.AcqChan.ADCSwp,
            "ACQShots": 1,
            "ACQUpdateTime": 0.001,
            "ACQSamplesPre": 0,
            "ACQSamplesPost": 382,
            "ACQTriggerEvent": _CSBPM.AcqEvents.Stop,
            "ACQTrigger": _CSBPM.AcqTrigTyp.External,
            "ACQTriggerRep": _CSBPM.AcqRepeat.Repetitive,
            "ACQDataTrigChan": _CSBPM.AcqChan.ADC,
            "TbTPhaseSyncEn": _CSBPM.DsblEnbl.disabled,  # Enable TbT sync
            "FOFBPhaseSyncEn": _CSBPM.DsblEnbl.disabled,  # Enable FOFB sync
            "FAcqPhaseSyncEn": _CSBPM.DsblEnbl.disabled,  # Enable FAcq sync
            "MonitPhaseSyncEn": _CSBPM.DsblEnbl.disabled,  # Enable Monit sync
            "TbTDataMaskEn": _CSBPM.DsblEnbl.disabled,  # Enable use of mask
            "TbTDataMaskSamplesBeg": 0,
            "TbTDataMaskSamplesEnd": 0,
            "XYPosCal": _CSBPM.DsblEnbl.enabled,
            "SumPosCal": _CSBPM.DsblEnbl.enabled,
            "SwPhaseSyncEn": _CSBPM.DsblEnbl.enabled,  # Enable Switching sync
            "TestDataEn": _CSBPM.DsblEnbl.disabled,
        }
        if self._name.sec in {'SI', 'BO'}:
            self._config_ok_vals["ACQChannel"] = _CSBPM.AcqChan.TbT
        pvs = {
            "SwMode": "SwMode-Sel",
            "ACQChannel": "GENChannel-Sel",
            "ACQShots": "GENShots-SP",
            "ACQUpdateTime": "GENUpdateTime-SP",
            "ACQSamplesPre": "GENSamplesPre-SP",
            "ACQSamplesPost": "GENSamplesPost-SP",
            "ACQTriggerEvent": "GENTriggerEvent-Cmd",
            "ACQTrigger": "GENTrigger-Sel",
            "ACQTriggerRep": "GENTriggerRep-Sel",
            "ACQDataTrigChan": "GENDataTrigChan-Sel",
            "TbTPhaseSyncEn": "TbTPhaseSyncEn-Sel",  # Enable TbT sync
            "FOFBPhaseSyncEn": "FOFBPhaseSyncEn-Sel",  # Enable FOFB sync
            "FAcqPhaseSyncEn": "FAcqPhaseSyncEn-Sel",  # Enable FAcq sync
            "MonitPhaseSyncEn": "MonitPhaseSyncEn-Sel",  # Enable Monit sync
            "TbTDataMaskEn": "TbTDataMaskEn-Sel",  # Enable use of mask
            "TbTDataMaskSamplesBeg": "TbTDataMaskSamplesBeg-SP",
            "TbTDataMaskSamplesEnd": "TbTDataMaskSamplesEnd-SP",
            "XYPosCal": "XYPosCal-Sel",
            "SumPosCal": "SumPosCal-Sel",
            "SwPhaseSyncEn": "SwPhaseSyncEn-Sel",  # Enable Switching sync
            "TestDataEn": "TestDataEn-Sel",
        }
        self._config_pvs_sp = {
            k: _PV(pvpref + v, **opt) for k, v in pvs.items()
        }
        pvs = {
            "INFOClkFreq": "INFOClkFreq-RB",
            "INFOHarmonicNumber": "INFOHarmonicNumber-RB",
            "INFOTbTRate": "INFOTbTRate-RB",
            "INFOFOFBRate": "INFOFOFBRate-RB",
            "INFOMONITRate": "INFOMONITRate-RB",
            "INFOFAcqRate": "INFOFAcqRate-RB",
            "SwMode": "SwMode-Sts",
            "ACQChannel": "GENChannel-Sts",
            "ACQShots": "GENShots-RB",
            "ACQUpdateTime": "GENUpdateTime-RB",
            "ACQSamplesPre": "GENSamplesPre-RB",
            "ACQSamplesPost": "GENSamplesPost-RB",
            "ACQTriggerEvent": "GENTriggerEvent-Cmd",
            "ACQCount": "GENCount-Mon",
            "ACQStatus": "GENStatus-Mon",
            "ACQTrigger": "GENTrigger-Sts",
            "ACQTriggerRep": "GENTriggerRep-Sts",
            "ACQDataTrigChan": "GENDataTrigChan-Sts",
            "TbTPhaseSyncEn": "TbTPhaseSyncEn-Sts",
            "FOFBPhaseSyncEn": "FOFBPhaseSyncEn-Sts",
            "FAcqPhaseSyncEn": "FAcqPhaseSyncEn-Sts",
            "MonitPhaseSyncEn": "MonitPhaseSyncEn-Sts",
            "TbTDataMaskEn": "TbTDataMaskEn-Sts",
            "TbTDataMaskSamplesBeg": "TbTDataMaskSamplesBeg-RB",
            "TbTDataMaskSamplesEnd": "TbTDataMaskSamplesEnd-RB",
            "XYPosCal": "XYPosCal-Sts",
            "SumPosCal": "SumPosCal-Sts",
            "SwPhaseSyncEn": "SwPhaseSyncEn-Sel",
            "TestDataEn": "TestDataEn-Sel",
        }
        self._config_pvs_rb = {
            k: _PV(pvpref + v, **opt) for k, v in pvs.items()
        }
        self._config_pvs_rb["ACQCount"].auto_monitor = True
        self._config_pvs_rb["ACQCount"].add_callback(
            self._reset_has_news
        )

    @property
    def name(self):
        """."""
        return self._name

    @property
    def is_ok(self):
        """."""
        if not super().is_ok:
            return False

        pvobj = self._config_pvs_rb["ACQStatus"]
        stts = _CSBPM.AcqStates
        okay = pvobj.value not in {
            stts.Error,
            stts.No_Memory,
            stts.No_Samples,
            stts.Too_Many_Samples,
            stts.Overflow,
            stts.Bad_Post_Samples,
        }

        if self._config_ok_vals["ACQTriggerEvent"] == _CSBPM.AcqEvents.Start:
            okay &= pvobj.value != stts.Idle
        else:
            okay &= pvobj.value not in {
                stts.Waiting,
                stts.External_Trig,
                stts.Data_Trig,
                stts.Software_Trig,
                stts.Acquiring,
            }
        if not okay:
            msg = "ERR: Error in {0:s}".format(pvobj.pvname)
            self.run_callbacks("Log-Mon", msg)
            _log.warning(msg[5:])
        return okay

    @property
    def switching_mode(self):
        """."""
        pvobj = self._config_pvs_rb["SwMode"]
        if pvobj.connected:
            return pvobj.value
        return None

    @switching_mode.setter
    def switching_mode(self, val):
        """."""
        pvobj = self._config_pvs_sp["SwMode"]
        self._config_ok_vals["SwMode"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def adcfreq(self):
        """."""
        defv = 218446014.0 if self._csorb.acc == "BO" else 220870069.0
        pvobj = self._config_pvs_rb["INFOClkFreq"]
        val = pvobj.value if pvobj.connected else defv
        return val if val else defv

    @property
    def tbtrate(self):
        """."""
        defv = 362 if self._csorb.acc == "BO" else 382
        pvobj = self._config_pvs_rb["INFOTbTRate"]
        val = pvobj.value if pvobj.connected else defv
        return val if val else defv

    @property
    def tbtperiod(self):
        """."""
        return self.tbtrate / self.adcfreq

    @property
    def fofbrate(self):
        """."""
        defv = (362 if self._csorb.acc == "BO" else 382) * 24
        pvobj = self._config_pvs_rb["INFOFOFBRate"]
        val = pvobj.value if pvobj.connected else defv
        return val if val else defv

    @property
    def fofbperiod(self):
        """."""
        return self.fofbrate / self.adcfreq

    @property
    def monitrate(self):
        """."""
        defv = (362 if self._csorb.acc == "BO" else 382) * 59904
        pvobj = self._config_pvs_rb["INFOMONITRate"]
        val = pvobj.value if pvobj.connected else defv
        return val if val else defv

    @property
    def monitperiod(self):
        """."""
        return self.monitrate / self.adcfreq

    @property
    def facqrate(self):
        """."""
        defv = (362 if self._csorb.acc == "BO" else 382) * 603
        pvobj = self._config_pvs_rb["INFOFAcqRate"]
        val = pvobj.value if pvobj.connected else defv
        return val if val else defv

    @property
    def facqperiod(self):
        """."""
        return self.facqrate / self.adcfreq

    @property
    def poskx(self):
        """."""
        defv = 1
        pvobj = self._pvs['poskx']
        val = pvobj.value if pvobj.connected else defv
        return val if val else defv

    @property
    def posky(self):
        """."""
        defv = 1
        pvobj = self._pvs['posky']
        val = pvobj.value if pvobj.connected else defv
        return val if val else defv

    @property
    def polyx(self):
        """."""
        pvobj = self._pvs['polyx']
        if pvobj.connected:
            val = pvobj.value
            if val is not None:
                return val
        defv = _np.zeros(15, dtype=float)
        defv[0] = 1
        return defv

    @property
    def polyy(self):
        """."""
        pvobj = self._pvs['polyy']
        if pvobj.connected:
            val = pvobj.value
            if val is not None:
                return val
        defv = _np.zeros(15, dtype=float)
        defv[0] = 1
        return defv

    @property
    def ksum(self):
        """."""
        defv = 1
        pvobj = self._pvs['ksum']
        val = pvobj.value if pvobj.connected else defv
        return val if val else defv

    @property
    def arraya(self):
        """."""
        pvobj = self._pvs['arraya']
        return pvobj.get() if pvobj.connected else None

    @property
    def arrayb(self):
        """."""
        pvobj = self._pvs['arrayb']
        return pvobj.get() if pvobj.connected else None

    @property
    def arrayc(self):
        """."""
        pvobj = self._pvs['arrayc']
        return pvobj.get() if pvobj.connected else None

    @property
    def arrayd(self):
        """."""
        pvobj = self._pvs['arrayd']
        return pvobj.get() if pvobj.connected else None

    @property
    def mtposx(self):
        """."""
        pvobj = self._pvs['arrayx']
        val = pvobj.get() if pvobj.connected else None
        if val is not None:
            return self._orb_conv_unit * val

    @property
    def mtposy(self):
        """."""
        pvobj = self._pvs['arrayy']
        val = pvobj.get() if pvobj.connected else None
        if val is not None:
            return self._orb_conv_unit * val

    @property
    def mtsum(self):
        """."""
        pvobj = self._pvs['arrays']
        val = pvobj.get() if pvobj.connected else None
        if val is not None:
            return val

    @property
    def offsetx(self):
        """."""
        pvobj = self._pvs['offsetx']
        val = pvobj.value if pvobj.connected else None
        if val is not None:
            return self._orb_conv_unit * val

    @property
    def offsety(self):
        """."""
        pvobj = self._pvs['offsety']
        val = pvobj.value if pvobj.connected else None
        if val is not None:
            return self._orb_conv_unit * val

    @property
    def ctrl(self):
        """."""
        # pvobj = self._config_pvs_rb['ACQCtrl']
        pvobj = self._config_pvs_rb["ACQTriggerEvent"]
        return pvobj.value if pvobj.connected else None

    @ctrl.setter
    def ctrl(self, val):
        """."""
        # pvobj = self._config_pvs_sp['ACQCtrl']
        pvobj = self._config_pvs_sp["ACQTriggerEvent"]
        # self._config_ok_vals['ACQCtrl'] = val
        self._config_ok_vals["ACQTriggerEvent"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def acq_type(self):
        """."""
        pvobj = self._config_pvs_rb["ACQChannel"]
        return pvobj.value if pvobj.connected else None

    @acq_type.setter
    def acq_type(self, val):
        """."""
        pvobj = self._config_pvs_sp["ACQChannel"]
        self._config_ok_vals["ACQChannel"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def acq_trigger(self):
        """."""
        # pvobj = self._config_pvs_rb['ACQTriggerType']
        pvobj = self._config_pvs_rb["ACQTrigger"]
        return pvobj.value if pvobj.connected else None

    @acq_trigger.setter
    def acq_trigger(self, val):
        """."""
        # pvobj = self._config_pvs_sp['ACQTriggerType']
        pvobj = self._config_pvs_sp["ACQTrigger"]
        # self._config_ok_vals['ACQTriggerType'] = val
        self._config_ok_vals["ACQTrigger"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def acq_repeat(self):
        """."""
        pvobj = self._config_pvs_rb["ACQTriggerRep"]
        return pvobj.value if pvobj.connected else None

    @acq_repeat.setter
    def acq_repeat(self, val):
        """."""
        pvobj = self._config_pvs_sp["ACQTriggerRep"]
        self._config_ok_vals["ACQTriggerRep"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def acq_trig_datatype(self):
        """."""
        # pvobj = self._config_pvs_rb['ACQTriggerDataChan']
        pvobj = self._config_pvs_rb["ACQDataTrigChan"]
        return pvobj.value if pvobj.connected else None

    @acq_trig_datatype.setter
    def acq_trig_datatype(self, val):
        """."""
        # pvobj = self._config_pvs_sp['ACQTriggerDataChan']
        pvobj = self._config_pvs_sp["ACQDataTrigChan"]
        # self._config_ok_vals['ACQTriggerDataChan'] = val
        self._config_ok_vals["ACQDataTrigChan"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def tbt_sync_enbl(self):
        """."""
        pvobj = self._config_pvs_rb["TbTPhaseSyncEn"]
        return pvobj.value if pvobj.connected else None

    @tbt_sync_enbl.setter
    def tbt_sync_enbl(self, val):
        """."""
        pvobj = self._config_pvs_sp["TbTPhaseSyncEn"]
        self._config_ok_vals["TbTPhaseSyncEn"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def fofb_sync_enbl(self):
        """."""
        pvobj = self._config_pvs_rb["FOFBPhaseSyncEn"]
        return pvobj.value if pvobj.connected else None

    @fofb_sync_enbl.setter
    def fofb_sync_enbl(self, val):
        """."""
        pvobj = self._config_pvs_sp["FOFBPhaseSyncEn"]
        self._config_ok_vals["FOFBPhaseSyncEn"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def sw_sync_enbl(self):
        """."""
        pvobj = self._config_pvs_rb["SwPhaseSyncEn"]
        return pvobj.value if pvobj.connected else None

    @sw_sync_enbl.setter
    def sw_sync_enbl(self, val):
        """."""
        pvobj = self._config_pvs_sp["SwPhaseSyncEn"]
        self._config_ok_vals["SwPhaseSyncEn"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def facq_sync_enbl(self):
        """."""
        pvobj = self._config_pvs_rb["FAcqPhaseSyncEn"]
        return pvobj.value if pvobj.connected else None

    @facq_sync_enbl.setter
    def facq_sync_enbl(self, val):
        """."""
        pvobj = self._config_pvs_sp["FAcqPhaseSyncEn"]
        self._config_ok_vals["FAcqPhaseSyncEn"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def monit_sync_enbl(self):
        """."""
        pvobj = self._config_pvs_rb["MonitPhaseSyncEn"]
        return pvobj.value if pvobj.connected else None

    @monit_sync_enbl.setter
    def monit_sync_enbl(self, val):
        """."""
        pvobj = self._config_pvs_sp["MonitPhaseSyncEn"]
        self._config_ok_vals["MonitPhaseSyncEn"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def test_data_enbl(self):
        """."""
        pvobj = self._config_pvs_rb["TestDataEn"]
        return pvobj.value if pvobj.connected else None

    @test_data_enbl.setter
    def test_data_enbl(self, val):
        """."""
        pvobj = self._config_pvs_sp["TestDataEn"]
        self._config_ok_vals["TestDataEn"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def tbt_mask_enbl(self):
        """."""
        pvobj = self._config_pvs_rb["TbTDataMaskEn"]
        return pvobj.value if pvobj.connected else None

    @tbt_mask_enbl.setter
    def tbt_mask_enbl(self, val):
        """."""
        pvobj = self._config_pvs_sp["TbTDataMaskEn"]
        self._config_ok_vals["TbTDataMaskEn"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def tbt_mask_begin(self):
        """."""
        pvobj = self._config_pvs_rb["TbTDataMaskSamplesBeg"]
        return pvobj.value if pvobj.connected else None

    @tbt_mask_begin.setter
    def tbt_mask_begin(self, val):
        """."""
        pvobj = self._config_pvs_sp["TbTDataMaskSamplesBeg"]
        self._config_ok_vals["TbTDataMaskSamplesBeg"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def tbt_mask_end(self):
        """."""
        pvobj = self._config_pvs_rb["TbTDataMaskSamplesEnd"]
        return pvobj.value if pvobj.connected else None

    @tbt_mask_end.setter
    def tbt_mask_end(self, val):
        """."""
        pvobj = self._config_pvs_sp["TbTDataMaskSamplesEnd"]
        self._config_ok_vals["TbTDataMaskSamplesEnd"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def polycal(self):
        """."""
        pvobj = self._config_pvs_rb["XYPosCal"]
        return pvobj.value if pvobj.connected else None

    @polycal.setter
    def polycal(self, val):
        """."""
        val = _CSBPM.DsblEnbl.enabled if val else _CSBPM.DsblEnbl.disabled
        pv1 = self._config_pvs_sp["XYPosCal"]
        pv2 = self._config_pvs_sp["SumPosCal"]
        self._config_ok_vals["XYPosCal"] = val
        self._config_ok_vals["SumPosCal"] = val
        if self.put_enable and pv1.connected:
            pv1.put(val, wait=False)
        if self.put_enable and pv2.connected:
            pv2.put(val, wait=False)

    @property
    def nrsamplespost(self):
        """."""
        pvobj = self._config_pvs_rb["ACQSamplesPost"]
        return pvobj.value if pvobj.connected else None

    @nrsamplespost.setter
    def nrsamplespost(self, val):
        """."""
        pvobj = self._config_pvs_sp["ACQSamplesPost"]
        self._config_ok_vals["ACQSamplesPost"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def nrsamplespre(self):
        """."""
        pvobj = self._config_pvs_rb["ACQSamplesPre"]
        return pvobj.value if pvobj.connected else None

    @nrsamplespre.setter
    def nrsamplespre(self, val):
        """."""
        pvobj = self._config_pvs_sp["ACQSamplesPre"]
        self._config_ok_vals["ACQSamplesPre"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def nrshots(self):
        """."""
        pvobj = self._config_pvs_rb["ACQShots"]
        return pvobj.value if pvobj.connected else None

    @nrshots.setter
    def nrshots(self, val):
        """."""
        pvobj = self._config_pvs_sp["ACQShots"]
        self._config_ok_vals["ACQShots"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    def calc_sp_multiturn_pos(self, **kwargs):
        """."""
        nturns = kwargs.get("nturns", 1)
        refx = kwargs.get("refx", 0.0)
        refy = kwargs.get("refy", 0.0)
        refsum = kwargs.get("refsum", 0.0)
        maskbeg = kwargs.get("maskbeg", 0)
        maskend = kwargs.get("maskend", 0)

        wsize = self.tbtrate
        maskbeg = min(maskbeg, wsize - 2)
        maskend = min(maskend, wsize - maskbeg - 2)
        mask = slice(maskbeg, wsize - maskend)

        # NOTE: I have to invert array B with C here because of the way
        # the ADCSWAP rate works. Fixed in 2020/07/01 after talking to
        # Daniel Tavares.
        vals = {
            "A": self.arraya,
            "C": self.arrayb,
            "B": self.arrayc,
            "D": self.arrayd,
        }
        siz = None
        for _, val in vals.items():
            if val is None or val.size == 0:
                siz = 0
                break
            nzrs = val.size
            siz = nzrs if siz is None else min(siz, nzrs)

        x_cal = _np.full(nturns, refx)
        y_cal = _np.full(nturns, refy)
        s_cal = _np.full(nturns, refsum)

        # handle cases where length read is smaller than required.
        rnts = min(siz // wsize, nturns)
        if not (siz and rnts):
            return x_cal, y_cal, s_cal

        for key, val in vals.items():
            val = val[: (rnts * wsize)]
            val = val.reshape(-1, wsize)[:, mask]
            vals[key] = _np.std(val, axis=1)

        sum1, sum2 = vals["A"] + vals["C"], vals["D"] + vals["B"]
        not_zero = _np.logical_not(_np.isclose(sum1, 0.0))
        not_zero &= _np.logical_not(_np.isclose(sum2, 0.0))
        diff1 = (vals["A"][not_zero] - vals["C"][not_zero]) / sum1[not_zero]
        diff2 = (vals["D"][not_zero] - vals["B"][not_zero]) / sum2[not_zero]
        x_raw = (diff1 + diff2) / 2
        y_raw = (diff1 - diff2) / 2
        if self._config_ok_vals["XYPosCal"] == _CSBPM.DsblEnbl.enabled:
            x_raw, y_raw = self._apply_polyxy(x_raw, y_raw)

        x_cal[:rnts][not_zero] = x_raw * self.poskx
        y_cal[:rnts][not_zero] = y_raw * self.posky
        x_cal[:rnts][not_zero] *= self._orb_conv_unit
        y_cal[:rnts][not_zero] *= self._orb_conv_unit
        x_cal[:rnts][not_zero] -= self.offsetx or 0.0
        y_cal[:rnts][not_zero] -= self.offsety or 0.0
        s_cal[:rnts] = (sum1 + sum2) * self.ksum
        return x_cal, y_cal, s_cal

    def _apply_polyxy(self, x_raw, y_raw):
        """."""
        x_pol = self._calc_poly(x_raw, y_raw, plane="x")
        y_pol = self._calc_poly(y_raw, x_raw, plane="y")
        return x_pol, y_pol

    def _calc_poly(self, th1, ot1, plane="x"):
        """."""
        ot2 = ot1 * ot1
        ot4 = ot2 * ot2
        ot6 = ot4 * ot2
        ot8 = ot4 * ot4
        th2 = th1 * th1
        th3 = th2 * th1
        th5 = th3 * th2
        th7 = th5 * th2
        th9 = th7 * th2
        pol = self.polyx if plane == "x" else self.polyy

        return (
            th1
            * (
                pol[0]
                + ot2 * pol[1]
                + ot4 * pol[2]
                + ot6 * pol[3]
                + ot8 * pol[4]
            )
            + th3 * (pol[5] + ot2 * pol[6] + ot4 * pol[7] + ot6 * pol[8])
            + th5 * (pol[9] + ot2 * pol[10] + ot4 * pol[11])
            + th7 * (pol[12] + ot2 * pol[13])
            + th9 * pol[14]
        )

    def _reset_has_news(self, *args, **kwargs):
        _ = args, kwargs
        self.has_news = True


class TimingConfig(_BaseTimingConfig):
    """."""

    def __init__(self, acc, callback=None):
        """."""
        super().__init__(acc, callback=callback)
        trig = self._csorb.trigger_acq_name
        evg = self._csorb.evg_name
        opt = {"connection_timeout": TIMEOUT}
        self._config_ok_vals = {
            "NrPulses": 1,
            "State": _TIConst.TrigStates.Enbl,
        }
        if _HLTimesearch.has_delay_type(trig):
            self._config_ok_vals["RFDelayType"] = _TIConst.TrigDlyTyp.Manual
        pref_name = LL_PREF + trig + ":"
        self._config_pvs_rb = {
            "Delay": _PV(pref_name + "Delay-RB", **opt),
            "TotalDelay": _PV(pref_name + "TotalDelay-Mon", **opt),
            "NrPulses": _PV(pref_name + "NrPulses-RB", **opt),
            "Duration": _PV(pref_name + "Duration-RB", **opt),
            "State": _PV(pref_name + "State-Sts", **opt),
            "Injecting": _PV(LL_PREF + evg + ":InjectionEvt-Sts", **opt),
            "EGTrig": _PV("LI-01:EG-TriggerPS:status", **opt),
        }
        self._config_pvs_sp = {
            "NrPulses": _PV(pref_name + "NrPulses-SP", **opt),
            "State": _PV(pref_name + "State-Sel", **opt),
        }
        if _HLTimesearch.has_delay_type(trig):
            self._config_pvs_rb["RFDelayType"] = _PV(
                pref_name + "RFDelayType-Sts", **opt
            )
            self._config_pvs_sp["RFDelayType"] = _PV(
                pref_name + "RFDelayType-Sel", **opt
            )

    @property
    def injecting(self):
        """."""
        inj = bool(self._config_pvs_rb["Injecting"].value)
        eg_trig = bool(self._config_pvs_rb["EGTrig"].value)
        return inj and eg_trig

    @property
    def nrpulses(self):
        """."""
        pvobj = self._config_pvs_rb["NrPulses"]
        return pvobj.value if pvobj.connected else None

    @nrpulses.setter
    def nrpulses(self, val):
        """."""
        pvobj = self._config_pvs_sp["NrPulses"]
        self._config_ok_vals["NrPulses"] = val
        if self.put_enable and pvobj.connected:
            pvobj.put(val, wait=False)

    @property
    def duration(self):
        """."""
        pvobj = self._config_pvs_rb["Duration"]
        return pvobj.value if pvobj.connected else None

    @property
    def delay(self):
        """."""
        pvobj = self._config_pvs_rb["Delay"]
        return pvobj.value if pvobj.connected else None

    @property
    def totaldelay(self):
        """."""
        pvobj = self._config_pvs_rb["TotalDelay"]
        return pvobj.value if pvobj.connected else None
