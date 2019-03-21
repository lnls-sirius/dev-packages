#!/usr/local/bin/python-sirius

import time
from siriuspy.epics.computed_pv import ComputedPV
from siriuspy.thread import QueueThread
from siriuspy.computer import Computer


class DiffPV(Computer):
    """Diff of a setpoint and a readback."""

    OPMODE_SEL = 0
    OPMODE_STS = 1
    CURRENT_SP = 2
    CURRENT_MON = 3

    def __init__(self, e):
        self._e = e

    def compute_update(self, computed_pv, updated_pv_name, value):
        """Compare PVs to check wether they are equal."""
        opmode_sts = computed_pv.pvs[DiffPV.OPMODE_STS].get()
        if opmode_sts != 3:  # Slowref
            return {'value': 0}  # Ok
        else:
            sp = computed_pv.pvs[DiffPV.CURRENT_SP].get()
            rb = computed_pv.pvs[DiffPV.CURRENT_MON].get()
            if abs(sp - rb) > self._e:
                return {'value': 1}
            else:
                return {'value': 0}

    def compute_put(self, computed_pv, value):
        """Not needed."""

    def compute_limits(self, computed_pv, updated_pv_name=None):
        """Not needed."""


def callback(pvname, value, **kwargs):
    """Test callback."""
    print(pvname, value)


if __name__ == '__main__':
    queue = QueueThread()
    computer = DiffPV(2e-2)
    pvs = [
        'guilherme-TB-Fam:PS-B:OpMode-Sel', 'guilherme-TB-Fam:PS-B:OpMode-Sts',
        'guilherme-TB-Fam:PS-B:Current-SP', 'guilherme-TB-Fam:PS-B:Current-Mon']
    pv = ComputedPV('TB-Fam:PS-B:Diff-Mon', computer, queue, pvs, False)
    pv.add_callback(callback)

    while True:
        # print("Connected: {}\nValue: {}".format(pv.connected, pv.get()))
        pv.get()
        time.sleep(0.5)
