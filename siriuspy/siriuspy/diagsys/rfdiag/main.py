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
        pref = self._prefix + ('-' if self._prefix else '')

        # BO
        devname = SiriusPVName(_Const.BO_DEV)
        bollrf_prefix = 'RA-RaBO01:RF-LLRF'
        bollrfintlk_pvn = bollrf_prefix + ':Intlk-Mon'
        bointlk_pvn = "RA-RaBO02:RF-IntlkCtrl:IntlkSirius-Mon"

        # DiagStatus-Mon
        pvs = [None]*4
        pvs[_BORFStatusPV.PV_SIRIUS_INTLK] = pref + bointlk_pvn
        pvs[_BORFStatusPV.PV_LLRF_INTLK] = pref + bollrfintlk_pvn
        pvs[_BORFStatusPV.PV_RMP_ENBLD] = pref+bollrf_prefix+':RmpEnbl-Sts'
        pvs[_BORFStatusPV.PV_RMP_READY] = pref+bollrf_prefix+':RmpReady-Mon'
        pvo = _ComputedPV(
            devname + ':DiagStatus-Mon', _BORFStatusPV(),
            self._queue, pvs, monitor=False)
        self.pvs.append(pvo)

        # SI
        for devid, devname in _Const.SI_DEVS.items():
            devname = SiriusPVName(devname)
            prefname = devname.substitute(prefix=self._prefix)

            sillrf_prefix = f'RA-RaSI{devid}01:RF-LLRF'
            sillrfintlk_pvn = sillrf_prefix + ':Intlk-Mon'
            siintlk_pvn = f'RA-RaSI{devid}02:RF-IntlkCtrl:IntlkSirius-Mon'

            # DiagAmpErrSts-Mon
            pvs = [None]*1
            pvs[_SICheckAmpErrPV.PV_ERR] = pref+sillrf_prefix+':SLErrorAmp-Mon'
            pvo = _ComputedPV(
                devname + ':DiagAmpErrSts-Mon', _SICheckAmpErrPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagPhsErrSts-Mon
            pvs = [None]*1
            pvs[_SICheckPhsErrPV.PV_ERR] = pref+sillrf_prefix+':SLErrorPhs-Mon'
            pvo = _ComputedPV(
                devname + ':DiagPhsErrSts-Mon', _SICheckPhsErrPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagDTuneErrSts-Mon
            pvs = [None]*1
            pvs[_SICheckDTuneErrPV.PV_ERR] = pref+sillrf_prefix+':TuneDephs-Mon'
            pvo = _ComputedPV(
                devname + ':DiagDTuneErrSts-Mon', _SICheckDTuneErrPV(),
                self._queue, pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagStatus-Mon
            pvs = [None]*5
            pvs[_SIRFStatusPV.PV_SIRIUS_INTLK] = pref + siintlk_pvn
            pvs[_SIRFStatusPV.PV_LLRF_INTLK] = pref + sillrfintlk_pvn
            pvs[_SIRFStatusPV.PV_AMPL_ERR] = prefname + ':DiagAmpErrSts-Mon'
            pvs[_SIRFStatusPV.PV_PHSE_ERR] = prefname + ':DiagPhsErrSts-Mon'
            pvs[_SIRFStatusPV.PV_DTUN_ERR] = prefname + ':DiagDTuneErrSts-Mon'
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
