from collections import OrderedDict as _OrderedDict
from epics import PV as _PV
import siriuspy.csdevice.bpms as _csbpm
from .bpm_plugins import BPMEpics, BPMFake, get_prop_and_suffix

pvDB = _csbpm.get_bpm_database()
_sp_prop = """
@property
def {0}_{1}(self):
    return _copy.deepcopy(self._{0}_{1})

@{0}_{1}.setter
def {0}_{1}(self, new_val):
    self._{0}_{1} = new_val
    for bpm in self.values():
        bpm.{0}_{1} = new_val
"""

_rb_prop = """
@property
def {0}_{1}(self):
    return str(self._{0}_{1})
"""


class BPMSet(_OrderedDict):

    def __init__(self, bpm_names, bpm_class=None):
        self.bpm_names = list(bpm_names)
        self.bpm_class = bpm_class if bpm_class else BPMFake
        for bpm in bpm_names:
            self[bpm] = self.bpm_class(bpm)

        for pv, db in pvDB.items():
            prop, suf = get_prop_and_suffix(pv)
            # Create all properties
            attr = '{0}_{1}'.format(prop, suf)
            if suf in ('sp', 'cmd', 'sel'):
                val = getattr(self[self.bpm_names[0]], attr)
                setattr(self, '_'+attr, val)
            elif suf in ('rb', 'sts'):
                setattr(self, '_'+attr, 'Inconsistent')

        self._operation_mode = ''
        self._configuration_acquisition = dict()
        self._configuration_acquisition_auto_trigger = dict()

    for pv, db in pvDB.items():
        prop, suf = get_prop_and_suffix(pv)
        # Create all properties
        if suf in ('sp', 'cmd', 'sel'):
            exec(_sp_prop.format(prop, suf))
        elif suf in ('rb', 'sts'):
            exec(_rb_prop.format(prop, suf))
    del pv, db, prop, suf

    def set_operation_mode(self, mode='Continuous'):
        ok = True
        mode = _csbpm.OpModes._fields.index(mode)
        for name, bpm in self.items():
            bpm.opmode_sel = mode
            ok &= bpm.opmode_sel == mode
        return ok

    def get_operation_mode(self):
        _mode = self[self.bpm_names[0]].opmode_sts
        for name, bpm in self.items():
            if bpm.opmode_sts != _mode:
                return None
        return _mode

    def set_configuration_acquisition(self,
                                      AcqRate='TbT',
                                      NrSamplePre=1000,
                                      NrSamplePos=1000,
                                      NrShots=1,
                                      Delay=0.0,
                                      TriggerType='External',
                                      ExternalTrigger='Trig1',
                                      RearmTrigger=False,
                                      ):
        ok = True
        if isinstance(AcqRate, str):
            AcqRate = _csbpm.AcqTyp._fields.index(AcqRate)
        if isinstance(TriggerType, str):
            TriggerType = _csbpm.AcqTrigTyp._fields.index(TriggerType)
        if isinstance(ExternalTrigger, str):
            ExternalTrigger = _csbpm.AcqTrigExter._fields.index(ExternalTrigger)
        rearm_trig = 0 if RearmTrigger else 1
        for name, bpm in self.items():
            bpm.acqrate_sel = AcqRate
            ok &= bpm.acqrate_sel == AcqRate

            bpm.acqnrsmplspre_sp = NrSamplePre
            ok &= bpm.acqnrsmplspre_sp == NrSamplePre

            bpm.acqnrsmplspos_sp = NrSamplePos
            ok &= bpm.acqnrsmplspos_sp == NrSamplePos

            bpm.acqnrshots_sp = NrShots
            ok &= bpm.acqnrshots_sp == NrShots

            bpm.acqdelay_sp = Delay
            ok &= bpm.acqdelay_sp == Delay

            bpm.acqtrigtype_sel = TriggerType
            ok &= bpm.acqtrigtype_sel == TriggerType

            bpm.acqtrigext_sel = ExternalTrigger
            ok &= bpm.acqtrigext_sel == ExternalTrigger

            bpm.acqtrigrep_sel = rearm_trig
            ok &= bpm.acqtrigrep_sel == rearm_trig
        return ok

    def get_configuration_acquisition(self):
        bpm = self[self.bpm_names[0]]
        AcqRate = bpm.acqrate_sts
        NrSamplePre = bpm.acqnrsmplspre_sp
        NrSamplePos = bpm.acqnrsmplspos_sp
        NrShots = bpm.acqnrshots_sp
        Delay = bpm.acqdelay_sp
        TriggerType = bpm.acqtrigtype_sts
        ExternalTrigger = bpm.acqtrigext_sts
        RearmTrigger = bpm.acqtrigrep_sts
        for name, bpm in self.items():
            if bpm.acqrate_sts != AcqRate:
                AcqRate = None
            if bpm.acqnrsmplspre_rb != NrSamplePre:
                NrSamplePre = None
            if bpm.acqnrsmplspos_rb != NrSamplePos:
                NrSamplePos = None
            if bpm.acqnrshots_rb != NrShots:
                NrShots = None
            if bpm.acqdelay_rb != Delay:
                Delay = None
            if bpm.acqtrigtype_sts != TriggerType:
                TriggerType = None
            if bpm.acqtrigext_sts != ExternalTrigger:
                ExternalTrigger = None
            if bpm.acqtrigrep_sts != RearmTrigger:
                RearmTrigger = None
        dic_ = dict()
        dic_['AcqRate'] = AcqRate
        dic_['NrSamplePre'] = NrSamplePre
        dic_['NrSamplePos'] = NrSamplePos
        dic_['NrShots'] = NrShots
        dic_['Delay'] = Delay
        dic_['TriggerType'] = TriggerType
        dic_['ExternalTrigger'] = ExternalTrigger
        dic_['RearmTrigger'] = RearmTrigger
        return dic_

    def set_configuration_acquisition_auto_trigger(self,
                                                   Type='TbT',
                                                   Channel='Sum',
                                                   Threshold=1,
                                                   Slope='Positive',
                                                   Hysteresis=1
                                                   ):
        ok = True
        if isinstance(Type, str):
            Type = _csbpm.AcqTyp._fields.index(Type)
        if isinstance(Channel, str):
            Channel = _csbpm.AcqDataTyp._fields.index(Channel)
        if isinstance(Slope, str):
            Slope = _csbpm.Polarity._fields.index(Slope)
        for name, bpm in self.items():
            bpm.acqtrigauto_sel = Type
            ok &= bpm.acqtrigauto_sel == Type

            bpm.acqtrigautoch_sel = Channel
            ok &= bpm.acqtrigautoch_sel == Channel

            bpm.acqtrigautothres_sp = Threshold
            ok &= bpm.acqtrigautothres_sp == Threshold

            bpm.acqtrigautoslope_sel = Slope
            ok &= bpm.acqtrigautoslope_sel == Slope

            bpm.acqtrigautohyst_sp = Hysteresis
            ok &= bpm.acqtrigautohyst_sp == Hysteresis

        return ok

    def get_configuration_acquisition_auto_trigger(self):
        bpm = self[self.bpm_names[0]]
        Type = bpm.acqtrigauto_sel
        Channel = bpm.acqtrigautoch_sel
        Threshold = bpm.acqtrigautothres_sp
        Slope = bpm.acqtrigautoslope_sel
        Hysteresis = bpm.acqtrigautohyst_sp
        for name, bpm in self.items():
            if bpm.acqtrigauto_sel != Type:
                Type = None
            if bpm.acqtrigautoch_sel != Channel:
                Channel = None
            if bpm.acqtrigautothres_sp != Threshold:
                Threshold = None
            if bpm.acqtrigautoslope_sel != Slope:
                Slope = None
            if bpm.acqtrigautohyst_sp != Hysteresis:
                Hysteresis = None
        dic_ = dict()
        dic_['Type'] = Type
        dic_['Channel'] = Channel
        dic_['Threshold'] = Threshold
        dic_['Slope'] = Slope
        dic_['Hysteresis'] = Hysteresis
        return dic_

    def is_acquisition_started(self):
        ok = True
        for name, bpm in self.items():
            ok &= bpm.acqstate_sts in ('Waiting', 'Acquiring')
        return ok

    def set_start_acquisition(self):
        for name, bpm in self.items():
            bpm.acqstart_cmd = 1

    def stop_acquisition(self):
        for name, bpm in self.items():
            bpm.acqstop_cmd = 1

    def is_acquisition_finished(self):
        ok = True
        for name, bpm in self.items():
            ok &= bpm.acqstate_sts in ('Idle', 'Error', 'Aborted')
        return ok
