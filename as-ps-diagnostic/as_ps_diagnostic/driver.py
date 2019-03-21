#!/usr/local/bin/python-sirius

import time
from threading import Thread

import epics
from pcaspy import Driver, SimpleServer

from siriuspy.epics.computed_pv import ComputedPV
from siriuspy.envars import vaca_prefix
from siriuspy.thread import QueueThread

from siriuspy.epics.diff_pv import DiffPV


class DiffPVs(Driver):

    def __init__(self, devices):
        super().__init__()
        self._queue = QueueThread()
        self.pvs = list()
        self.frequency = 2
        self.scanning = False
        self.quit = False

        for device in devices:
            pvs = [vaca_prefix + device + ':OpMode-Sel',
                   vaca_prefix + device + ':OpMode-Sts',
                   vaca_prefix + device + ':Current-SP',
                   vaca_prefix + device + ':Current-Mon']
            self.pvs.append(ComputedPV(device + ':Diff-Mon',
                                       DiffPV(2e-2),
                                       self._queue,
                                       pvs,
                                       monitor=False))
            self.pvs[-1].add_callback(self.update_db)

        self.t = Thread(target=self.scan, daemon=True)
        self.t.start()

    def scan(self):
        while True:
            if self.scanning:
                for pv in self.pvs:
                    pv.get()
            if self.quit:
                break
            time.sleep(1/self.frequency)

    def update_db(self, pvname, value, **kwargs):
        self.setParam(pvname, value)
        self.updatePV(pvname)

