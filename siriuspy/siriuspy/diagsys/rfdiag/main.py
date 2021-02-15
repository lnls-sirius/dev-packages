#!/usr/local/bin/python-sirius
"""Driver module."""

from pcaspy import Alarm as _Alarm, Severity as _Severity

from ...namesys import SiriusPVName
from ..app import App as _App
from ..pvs import ComputedPV as _ComputedPV

from .csdev import Const as _Const
from .pvs import BORFStatusPV as _BORFStatusPV, \
    SIRFStatusPV as _SIRFStatusPV, \
    SICheckAmpErrPV as _SICheckAmpErrPV, \
    SICheckPhsErrPV as _SICheckPhsErrPV, \
    SICheckDTuneErrPV as _SICheckDTuneErrPV


class RFDiagApp(_App):
    """Main application responsible for updating DB."""

    def _create_computed_pvs(self, *args):
        # BO
        devname = SiriusPVName(_Const.BO_DEV)

        # DiagStatus-Mon
        pvs = [None]*4
        pvs[_BORFStatusPV.PV_SIRIUS_INTLK] = \
            'RA-RaBO02:RF-IntlkCtrl:IntlkSirius-Mon'
        pvs[_BORFStatusPV.PV_LLRF_INTLK] = 'RA-RaBO01:RF-LLRF:Intlk-Mon'
        pvs[_BORFStatusPV.PV_RMP_ENBLD] = 'BR-RF-DLLRF-01:RmpEnbl-Sts'
        pvs[_BORFStatusPV.PV_RMP_READY] = 'BR-RF-DLLRF-01:RmpReady-Mon'
        pvo = _ComputedPV(
            devname + ':DiagStatus-Mon', _BORFStatusPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)

        # SI
        devname = SiriusPVName(_Const.SI_DEV)

        # DiagAmpErrSts-Mon
        pvs = [None]*1
        pvs[_SICheckAmpErrPV.PV_ERR] = 'SR-RF-DLLRF-01:SL:ERR:AMP'
        pvo = _ComputedPV(
            devname + ':DiagAmpErrSts-Mon', _SICheckAmpErrPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)

        # DiagPhsErrSts-Mon
        pvs = [None]*1
        pvs[_SICheckPhsErrPV.PV_ERR] = 'SR-RF-DLLRF-01:SL:ERR:PHS'
        pvo = _ComputedPV(
            devname + ':DiagPhsErrSts-Mon', _SICheckPhsErrPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)

        # DiagDTuneErrSts-Mon
        pvs = [None]*1
        pvs[_SICheckDTuneErrPV.PV_ERR] = 'SR-RF-DLLRF-01:TUNE:DEPHS'
        pvo = _ComputedPV(
            devname + ':DiagDTuneErrSts-Mon', _SICheckDTuneErrPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)

        # DiagStatus-Mon
        pvs = [None]*5
        pvs[_SIRFStatusPV.PV_SIRIUS_INTLK] = \
            'RA-RaSIA02:RF-IntlkCtrl:IntlkSirius-Mon'
        pvs[_SIRFStatusPV.PV_LLRF_INTLK] = 'RA-RaSIA01:RF-LLRF:Intlk-Mon'
        pvs[_SIRFStatusPV.PV_AMPL_ERR] = devname + ':DiagAmpErrSts-Mon'
        pvs[_SIRFStatusPV.PV_PHSE_ERR] = devname + ':DiagPhsErrSts-Mon'
        pvs[_SIRFStatusPV.PV_DTUN_ERR] = devname + ':DiagDTuneErrSts-Mon'
        pvo = _ComputedPV(
            devname + ':DiagStatus-Mon', _SIRFStatusPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)

        self._pvs_connected = {pv: False for pv in self.pvs}

    def _update_pvs(self):
        for pvo in self.pvs:
            if not pvo.connected:
                if self._pvs_connected[pvo]:
                    self.run_callbacks(
                        pvo.pvname, alarm=_Alarm.TIMEOUT_ALARM,
                        severity=_Severity.INVALID_ALARM,
                        field='status')
                self._pvs_connected[pvo] = False
                if 'DiagStatus' in pvo.pvname:
                    self.run_callbacks(pvo.pvname, value=pvo.value)
            else:
                if not self._pvs_connected[pvo]:
                    self.run_callbacks(
                        pvo.pvname, alarm=_Alarm.NO_ALARM,
                        severity=_Severity.NO_ALARM, field='status')
                self._pvs_connected[pvo] = True
                self.run_callbacks(pvo.pvname, value=pvo.value)
