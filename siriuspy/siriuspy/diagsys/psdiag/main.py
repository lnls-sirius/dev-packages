#!/usr/local/bin/python-sirius
"""Driver module."""

from pcaspy import Alarm as _Alarm, Severity as _Severity

from ...namesys import SiriusPVName
from ...pwrsupply.csdev import get_ps_interlocks as _get_ps_interlocks
from ..app import App as _App
from ..pvs import ComputedPV as _ComputedPV
from .pvs import PSStatusPV as _PSStatusPV, PSDiffPV as _PSDiffPV


class PSDiagApp(_App):
    """Main application responsible for updating DB."""

    def _create_computed_pvs(self, psnames):
        self._psnames = psnames
        for psname in self._psnames:
            devname = SiriusPVName(psname).substitute(prefix=self._prefix)

            # DiagCurrentDiff-Mon
            nrpvs = 4 if devname.sec != 'LI' else 2
            pvs = [None]*nrpvs
            pvs[_PSDiffPV.CURRT_SP] = devname + ':Current-SP'
            pvs[_PSDiffPV.CURRT_MON] = devname + ':Current-Mon'
            if devname.sec != 'LI':
                pvs[_PSDiffPV.CURRT_REF] = devname + ':CurrentRef-Mon'
                pvs[_PSDiffPV.OPMODESTS] = devname + ':OpMode-Sts'
            pvo = _ComputedPV(
                psname + ':DiagCurrentDiff-Mon', _PSDiffPV(), self._queue,
                pvs, monitor=False)
            self.pvs.append(pvo)

            # DiagStatus-Mon
            computer = _PSStatusPV()
            if devname.sec != 'LI':
                intlks = _get_ps_interlocks(psname=psname)
                if psname.dev in ['FCH', 'FCV']:
                    intlk_list = [':' + p for p in intlks if 'Ltc' not in p]
                    alarm_list = [':' + p for p in intlks if 'Ltc' in p]
                else:
                    intlk_list = [':' + p for p in intlks if 'Intlk' in p]
                    alarm_list = [':' + p for p in intlks if 'Alarm' in p]

                if psname in ['BO-Fam:PS-B-1', 'BO-Fam:PS-B-2']:
                    for aux in ['a', 'b', 'c']:
                        intlk_list.extend(
                            [aux+':'+ilk for ilk in intlks if 'Intlk' in ilk
                             if 'Soft' not in ilk and 'Hard' not in ilk])
                        alarm_list.extend(
                            [aux+':'+alm for alm in intlks if 'Alarm' in alm])

                nbpvs = 5
                pvs = [None]*(nbpvs+len(intlk_list)+len(alarm_list))
                pvs[_PSStatusPV.PWRSTE_STS] = devname + ':PwrState-Sts'
                pvs[_PSStatusPV.CURRT_DIFF] = devname + ':DiagCurrentDiff-Mon'
                pvs[_PSStatusPV.OPMODE_SEL] = devname + ':OpMode-Sel'
                pvs[_PSStatusPV.OPMODE_STS] = devname + ':OpMode-Sts'
                if psname.dev not in ['FCH', 'FCV']:
                    pvs[_PSStatusPV.WAVFRM_MON] = devname + ':Wfm-Mon'
                else:
                    pvs[_PSStatusPV.TRIGEN_STS] = devname + ':TrigEn-Sts'

                computer.INTLK_PVS = list()
                for idx, intlk in enumerate(intlk_list):
                    pvidx = idx + nbpvs
                    computer.INTLK_PVS.append(pvidx)
                    pvs[pvidx] = devname + intlk
                computer.ALARM_PVS = list()
                for idx, alarm in enumerate(alarm_list):
                    pvidx = idx + nbpvs + len(intlk_list)
                    computer.ALARM_PVS.append(pvidx)
                    pvs[pvidx] = devname + alarm
            else:
                pvs = [None]*5
                pvs[_PSStatusPV.PWRSTE_STS] = devname + ':PwrState-Sts'
                pvs[_PSStatusPV.CURRT_DIFF] = devname + ':DiagCurrentDiff-Mon'
                pvs[_PSStatusPV.INTRLCK_LI] = devname + ':StatusIntlk-Mon'
                pvs[_PSStatusPV.WARNSTS_LI] = devname + ':IntlkWarn-Mon'
                pvs[_PSStatusPV.CONNCTD_LI] = devname + ':Connected-Mon'

            pvo = _ComputedPV(
                psname + ':DiagStatus-Mon', computer, self._queue,
                pvs, monitor=False)
            self.pvs.append(pvo)
        self._pvs_connected = {pvo: False for pvo in self.pvs}

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
