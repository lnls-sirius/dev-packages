#!/usr/local/bin/python-sirius
"""Driver module."""

import time as _time
from threading import Thread as _Thread

from pcaspy import Alarm as _Alarm, Severity as _Severity

from ..callbacks import Callback as _Callback
from ..thread import QueueThread as _QueueThread
from ..epics.pv_psdiag import \
    ComputedPV as _ComputedPV, \
    PSStatusPV as _PSStatusPV, \
    PSDiffPV as _PSDiffPV

SCAN_FREQUENCY = 2


class App(_Callback):
    """Main application responsible for updating DB."""

    def __init__(self, prefix, psnames):
        """Create Computed PVs."""
        super().__init__()
        self._prefix = prefix
        self._psnames = psnames
        self._queue = _QueueThread()
        self.pvs = list()
        self.scanning = False
        self.quit = False
        self._create_computed_pvs()

        self.t = _Thread(target=self.scan, daemon=True)
        self.t.start()

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        return None

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        return status  # return True to invoke super().write of PCASDriver

    def _create_computed_pvs(self):
        for psname in self._psnames:
            devname = self._prefix + psname
            # DiagCurrentDiff-Mon
            pvs = [None, None]
            pvs[_PSDiffPV.CURRT_SP] = devname + ':Current-SP'
            pvs[_PSDiffPV.CURRT_MON] = devname + ':Current-Mon'
            pv = _ComputedPV(
                psname + ':DiagCurrentDiff-Mon', _PSDiffPV(), self._queue,
                pvs, monitor=False)
            self.pvs.append(pv)
            # DiagStatus-Mon
            pvs = [None]*7
            pvs[_PSStatusPV.PWRSTE_STS] = devname + ':PwrState-Sts'
            pvs[_PSStatusPV.INTLK_SOFT] = devname + ':IntlkSoft-Mon'
            pvs[_PSStatusPV.INTLK_HARD] = devname + ':IntlkHard-Mon'
            pvs[_PSStatusPV.OPMODE_SEL] = devname + ':OpMode-Sel'
            pvs[_PSStatusPV.OPMODE_STS] = devname + ':OpMode-Sts'
            pvs[_PSStatusPV.CURRT_DIFF] = devname + ':DiagCurrentDiff-Mon'
            pvs[_PSStatusPV.WAVFRM_MON] = devname + ':Wfm-Mon'
            # TODO: Add other interlocks for PS types that have them
            pv = _ComputedPV(
                psname + ':DiagStatus-Mon', _PSStatusPV(), self._queue,
                pvs, monitor=False)
            self.pvs.append(pv)

    def scan(self):
        """Run as a thread scanning PVs."""
        connected = {pv: False for pv in self.pvs}
        while not self.quit:
            if self.scanning:
                for pv in self.pvs:
                    if not pv.connected:
                        if connected[pv]:
                            self.run_callbacks(
                                pv.pvname, _Alarm.TIMEOUT_ALARM,
                                _Severity.INVALID_ALARM, field='status')
                        connected[pv] = False
                        if 'DiagStatus' in pv.pvname:
                            self.run_callbacks(pv.pvname, pv.value)
                    else:
                        if not connected[pv]:
                            self.run_callbacks(
                                pv.pvname, _Alarm.NO_ALARM, _Severity.NO_ALARM,
                                field='status')
                        connected[pv] = True
                        self.run_callbacks(pv.pvname, pv.value)
            _time.sleep(1.0/SCAN_FREQUENCY)
