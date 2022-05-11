#!/usr/local/bin/python-sirius
"""Application module."""

import time as _time
from threading import Thread as _Thread

from ..envars import VACA_PREFIX as _VACA_PREFIX
from ..callbacks import Callback as _Callback
from ..thread import QueueThread as _QueueThread


class App(_Callback):
    """Main application responsible for updating DB."""

    SCAN_FREQUENCY = 2

    def __init__(self, *args):
        """Create Computed PVs."""
        super().__init__()
        self._prefix = _VACA_PREFIX
        self._queue = _QueueThread()
        self.pvs = list()
        self.scanning = False
        self.quit = False
        self._create_computed_pvs(*args)

        self.thread = _Thread(target=self.scan, daemon=True)
        self.thread.start()

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        return None

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        return False  # return True to invoke super().write of PCASDriver

    def _create_computed_pvs(self):
        raise NotImplementedError

    def _update_pvs(self):
        raise NotImplementedError

    def scan(self):
        """Run as a thread scanning PVs."""
        while not self.quit:
            if self.scanning:
                self._update_pvs()
            _time.sleep(1.0/App.SCAN_FREQUENCY)
