#!/usr/local/bin/python-sirius
"""Driver module."""

import time as _time
from threading import Thread as _Thread
from pcaspy import Driver as _Driver
from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.epics.psdiag_pv import PSStatusPV as _PSStatusPV
from siriuspy.epics.psdiag_pv import PSDiffPV as _PSDiffPV


SCAN_FREQUENCY = 2  # [Hz]


class PSDiagDriver(_Driver):
    """Driver responsible for updating DB."""

    def __init__(self, psnames):
        """Create Computed PVs."""
        super().__init__()
        self._psnames = psnames
        self._queue = _QueueThread()
        self.pvs = list()
        self.scanning = False
        self.quit = False

        self._create_computed_pvs()

        self.t = _Thread(target=self.scan, daemon=True)
        self.t.start()

    def _create_computed_pvs(self):
        for psname in self._psnames:
            devname = _vaca_prefix + psname
            # CurrentDiff-Mon
            pvs = [None, None]
            pvs[_PSDiffPV.CURRT_SP] = devname + ':Current-SP'
            pvs[_PSDiffPV.CURRT_MON] = devname + ':Current-Mon'
            pv = _ComputedPV(psname + ':DiagCurrentDiff-Mon',
                             _PSDiffPV(),
                             self._queue,
                             pvs,
                             monitor=False)
            self.pvs.append(pv)
            # Status-Mon
            pvs = [None, None, None, None, None]
            pvs[_PSStatusPV.OPMODE_SEL] = devname + ':OpMode-Sel'
            pvs[_PSStatusPV.OPMODE_STS] = devname + ':OpMode-Sts'
            pvs[_PSStatusPV.CURRT_DIFF] = devname + ':DiagCurrentDiff-Mon'
            pvs[_PSStatusPV.INTLK_SOFT] = devname + ':IntlkSoft-Mon'
            pvs[_PSStatusPV.INTLK_HARD] = devname + ':IntlkHard-Mon'
            # TODO: Add other interlocks for PS types that hav them
            pv = _ComputedPV(psname + ':DiagStatus-Mon',
                             _PSStatusPV(),
                             self._queue,
                             pvs,
                             monitor=False)
            self.pvs.append(pv)

    def scan(self):
        """Run as a thread scanning PVs."""
        connected = False
        while not self.quit:
            if self.scanning:
                for pv in self.pvs:
                    if not pv.connected:
                        connected = False
                        self.setParamStatus(pv.pvname,
                                            _Alarm.TIMEOUT_ALARM,
                                            _Severity.INVALID_ALARM)
                    else:
                        if not connected:
                            self.setParamStatus(pv.pvname,
                                                _Alarm.NO_ALARM,
                                                _Severity.NO_ALARM)
                        connected = True
                        self.setParam(pv.pvname, pv.value)
                self.updatePVs()
            _time.sleep(1.0/SCAN_FREQUENCY)
