#!/usr/local/bin/python-sirius
"""Driver module."""

from pcaspy import Alarm as _Alarm, Severity as _Severity

from ...namesys import SiriusPVName
from ..app import App as _App
from ..pvs import ComputedPV as _ComputedPV
from .pvs import PSStatusPV as _PSStatusPV, PSDiffPV as _PSDiffPV


class PSDiagApp(_App):
    """Main application responsible for updating DB."""

    def _create_computed_pvs(self, psnames):
        self._psnames = psnames
        for psname in self._psnames:
            devname = SiriusPVName(self._prefix + psname)

            # DiagCurrentDiff-Mon
            pvs = [None, None]
            pvs[_PSDiffPV.CURRT_SP] = devname + ':Current-SP'
            pvs[_PSDiffPV.CURRT_MON] = devname + ':Current-Mon'
            pv = _ComputedPV(
                psname + ':DiagCurrentDiff-Mon', _PSDiffPV(), self._queue,
                pvs, monitor=False)
            self.pvs.append(pv)

            # DiagStatus-Mon
            if devname.sec != 'LI':
                pvs = [None]*7
                pvs[_PSStatusPV.PWRSTE_STS] = devname + ':PwrState-Sts'
                pvs[_PSStatusPV.CURRT_DIFF] = devname + ':DiagCurrentDiff-Mon'
                pvs[_PSStatusPV.INTLK_SOFT] = devname + ':IntlkSoft-Mon'
                pvs[_PSStatusPV.INTLK_HARD] = devname + ':IntlkHard-Mon'
                pvs[_PSStatusPV.OPMODE_SEL] = devname + ':OpMode-Sel'
                pvs[_PSStatusPV.OPMODE_STS] = devname + ':OpMode-Sts'
                pvs[_PSStatusPV.WAVFRM_MON] = devname + ':Wfm-Mon'
                # TODO: Add other interlocks for PS types that have them
            else:
                pvs = [None]*3
                pvs[_PSStatusPV.PWRSTE_STS] = devname + ':PwrState-Sts'
                pvs[_PSStatusPV.CURRT_DIFF] = devname + ':DiagCurrentDiff-Mon'
                pvs[_PSStatusPV.INTRLCK_LI] = devname + ':StatusIntlk-Mon'
            pv = _ComputedPV(
                psname + ':DiagStatus-Mon', _PSStatusPV(), self._queue,
                pvs, monitor=False)
            self.pvs.append(pv)
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
