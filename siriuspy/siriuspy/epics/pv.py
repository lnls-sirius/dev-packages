"""Sirius PV class."""


import epics as _epics


class PV(_epics.pv.PV):
    """PV class."""

    def set_auto_monitor(self, value):
        """Set auto_monitor property."""
        self.auto_monitor = value
