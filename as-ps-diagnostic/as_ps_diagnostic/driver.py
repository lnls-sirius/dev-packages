#!/usr/local/bin/python-sirius
"""Driver module."""

import time
from threading import Thread
from pcaspy import Driver as _Driver

from siriuspy.epics.computed_pv import ComputedPV as _ComputedPV
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.thread import QueueThread as _QueueThread
from siriuspy.epics.diff_pv import PSDiagPV as _PSDiagPV


# TODO: this should be taken from a static table, one value per PS.
_epsilon = 0.0


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

        for device in devices:
            pvs = [None, None, None, None]
            devname = _vaca_prefix + device
            pvs[_PSDiagPV.OPMODE_SEL] = devname + ':OpMode-Sel'
            pvs[_PSDiagPV.OPMODE_STS] = devname + ':OpMode-Sts'
            pvs[_PSDiagPV.CURRENT_SP] = devname + ':Current-SP'
            pvs[_PSDiagPV.CURRENT_MON] = devname + ':Current-Mon'
            self.pvs.append(_ComputedPV(device + ':Diag-Mon',
                                        _PSDiagPV(_epsilon),
                                        self._queue,
                                        pvs,
                                        monitor=False))
            self.pvs[-1].add_callback(self.update_db)

        self.t = Thread(target=self.scan, daemon=True)
        self.t.start()

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
