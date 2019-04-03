#!/usr/local/bin/python-sirius
"""Driver module."""

import time as _time
from threading import Thread as _Thread

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.search.ma_search import MASearch as _MASearch
from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.epics.psdiag_pv import PSStatusPV as _PSStatusPV
from siriuspy.epics.psdiag_pv import PSDiffPV as _PSDiffPV

SCAN_FREQUENCY = 2


class App:
    """Main application responsible for updating DB."""

    def __init__(self, driver, prefix, psnames):
        """Create Computed PVs."""
        self._driver = driver

        self._psnames = psnames
        self._queue = _QueueThread()
        self._prefix = prefix
        self.pvs = list()
        self.scanning = False
        self.quit = False
        self._create_computed_pvs()

        self.t = _Thread(target=self.scan, daemon=True)
        self.t.start()

    @property
    def driver(self):
        """Return driver."""
        return self._driver

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
            magname = self._prefix + _MASearch.conv_psname_2_psmaname(psname)
            # DiagCurrentDiff-Mon
            pvs = [None, None]
            pvs[_PSDiffPV.CURRT_SP] = devname + ':Current-SP'
            pvs[_PSDiffPV.CURRT_MON] = devname + ':Current-Mon'
            pv = _ComputedPV(psname + ':DiagCurrentDiff-Mon',
                             _PSDiffPV(),
                             self._queue,
                             pvs,
                             monitor=False)
            self.pvs.append(pv)
            # DiagStatus-Mon
            pvs = [None, None, None, None, None, None]
            pvs[_PSStatusPV.OPMODE_SEL] = devname + ':OpMode-Sel'
            pvs[_PSStatusPV.OPMODE_STS] = devname + ':OpMode-Sts'
            pvs[_PSStatusPV.CURRT_DIFF] = devname + ':DiagCurrentDiff-Mon'
            pvs[_PSStatusPV.MAOPMD_SEL] = magname + ':OpMode-Sel'
            pvs[_PSStatusPV.INTLK_SOFT] = devname + ':IntlkSoft-Mon'
            pvs[_PSStatusPV.INTLK_HARD] = devname + ':IntlkHard-Mon'
            # TODO: Add other interlocks for PS types that have them
            pv = _ComputedPV(psname + ':DiagStatus-Mon',
                             _PSStatusPV(),
                             self._queue,
                             pvs,
                             monitor=False)
            self.pvs.append(pv)

    def scan(self):
        """Run as a thread scanning PVs."""
        connected = dict()
        for pv in self.pvs:
            connected[pv] = False
        while not self.quit:
            if self.scanning:
                for pv in self.pvs:
                    if not pv.connected:
                        if connected[pv]:
                            self.driver.setParamStatus(pv.pvname,
                                                       _Alarm.TIMEOUT_ALARM,
                                                       _Severity.INVALID_ALARM)
                        connected[pv] = False
                        if 'DiagStatus' in pv.pvname:
                            self.driver.setParam(pv.pvname, pv.value)
                    else:
                        if not connected[pv]:
                            self.driver.setParamStatus(pv.pvname,
                                                       _Alarm.NO_ALARM,
                                                       _Severity.NO_ALARM)
                        connected[pv] = True
                        self.driver.setParam(pv.pvname, pv.value)
                self.driver.updatePVs()
            _time.sleep(1.0/SCAN_FREQUENCY)
