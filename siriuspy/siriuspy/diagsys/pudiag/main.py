#!/usr/local/bin/python-sirius
"""Driver module."""

from pcaspy import Alarm as _Alarm, Severity as _Severity

from ...namesys import SiriusPVName
from ..app import App as _App
from ..pvs import ComputedPV as _ComputedPV
from .pvs import PUStatusPV as _PUStatusPV, PUDiffPV as _PUDiffPV


class PUDiagApp(_App):
    """Main application responsible for updating DB."""

    def _create_computed_pvs(self, punames):
        self._punames = punames
        for puname in self._punames:
            devname = SiriusPVName(puname).substitute(prefix=self._prefix)

            # DiagVoltageDiff-Mon
            pvs = [None, None]
            pvs[_PUDiffPV.VOLTAGE_SP] = devname + ':Voltage-SP'
            pvs[_PUDiffPV.VOLTAGE_MON] = devname + ':Voltage-Mon'
            pv = _ComputedPV(
                puname + ':DiagVoltageDiff-Mon', _PUDiffPV(), self._queue,
                pvs, monitor=False)
            self.pvs.append(pv)

            # DiagStatus-Mon
            pvs = [None]*11 if 'Sept' not in puname else [None]*10
            pvs[_PUStatusPV.PWRST_STS] = devname + ':PwrState-Sts'
            pvs[_PUStatusPV.PULSE_STS] = devname + ':Pulse-Sts'
            pvs[_PUStatusPV.DIFFVOLTG] = devname + ':DiagVoltageDiff-Mon'
            pvs[_PUStatusPV.INTRLCK_1] = devname + ':Intlk1-Mon'
            pvs[_PUStatusPV.INTRLCK_2] = devname + ':Intlk2-Mon'
            pvs[_PUStatusPV.INTRLCK_3] = devname + ':Intlk3-Mon'
            pvs[_PUStatusPV.INTRLCK_4] = devname + ':Intlk4-Mon'
            pvs[_PUStatusPV.INTRLCK_5] = devname + ':Intlk5-Mon'
            pvs[_PUStatusPV.INTRLCK_6] = devname + ':Intlk6-Mon'
            pvs[_PUStatusPV.INTRLCK_7] = devname + ':Intlk7-Mon'
            if 'Sept' not in puname:
                pvs[_PUStatusPV.INTRLCK_8] = devname + ':Intlk8-Mon'
            pv = _ComputedPV(
                puname + ':DiagStatus-Mon', _PUStatusPV(), self._queue,
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
