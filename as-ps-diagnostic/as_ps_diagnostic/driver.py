#!/usr/local/bin/python-sirius
"""Driver module."""

import time
from threading import Thread as _Thread
from pcaspy import Driver as _Driver

from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.epics.psdiff_pv import PSDiffPV as _PSDiffPV
from siriuspy.epics.psstatus_pv import PSStatusPV as _PSStatusPV


class PSDiagDriver(_Driver):
    """Driver responsible for updating DB."""

    def __init__(self, devices):
        """Create Computed PVs."""
        super().__init__()
        self._queue = _QueueThread()
        self.pvs = list()
        self.frequency = 2  # [Hz]
        self.scanning = False
        self.quit = False

        self._create_computed_pvs(devices)

        self.t = _Thread(target=self.scan, daemon=True)
        self.t.start()

    def _create_computed_pvs(self, devices):
        for device in devices:
            devname = _vaca_prefix + device
            # CurrentDiff-Mon
            dtol = devices[device]
            pvs = [None, None]
            pvs[_PSDiffPV.CURRT_SP] = devname + ':Current-SP'
            pvs[_PSDiffPV.CURRT_MON] = devname + ':Current-Mon'
            pv = _ComputedPV(device + ':CurrentDiff-Mon',
                             _PSDiffPV(dtol),
                             self._queue,
                             pvs,
                             monitor=False)
            pv.add_callback(self.update_db)
            self.pvs.append(pv)
            # Status-Mon
            pvs = [None, None, None, None, None]
            pvs[_PSStatusPV.OPMODE_SEL] = devname + ':OpMode-Sel'
            pvs[_PSStatusPV.OPMODE_STS] = devname + ':OpMode-Sts'
            pvs[_PSStatusPV.INTLK_SOFT] = devname + ':IntlkSoft-Mon'
            pvs[_PSStatusPV.INTLK_HARD] = devname + ':IntlkHard-Mon'
            pvs[_PSStatusPV.CURRT_DIFF] = devname + ':CurrentDiff-Mon'
            pv = _ComputedPV(device + ':Status-Mon',
                             _PSStatusPV(),
                             self._queue,
                             pvs,
                             monitor=False)
            pv.add_callback(self.update_db)
            self.pvs.append(pv)

    def scan(self):
        """Run as a thread scanning PVs SP/Mon."""
        while True:
            if self.scanning:
                for pv in self.pvs:
                    pv.get()
            if self.quit:
                break
            time.sleep(1.0/self.frequency)

    def update_db(self, pvname, value, **kwargs):
        """Update database callback function."""
        self.setParam(pvname, value)
        self.updatePV(pvname)
