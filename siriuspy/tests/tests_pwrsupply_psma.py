#!/usr/bin/env python3

import unittest
import epics
import time
import numpy

from siriuspy.pwrsupply.model import PowerSupplyEpics
from siriuspy.pwrsupply.model import PowerSupplySync
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.magnet.model import ControllerSync


class TestSet1(unittest.TestCase):

    def setUp(self):

        self.ps = ControllerSync(maname='SI-Fam:MA-B1B2',
                                 use_vaca=True)
        self.ps.opmode_sel = _et.idx.SlowRef
        self.ps.pwrstate_sel = _et.idx.On
        self.ps.current_sp = 0.0

    def wait_for(self, value, attr, timeout):
        t0 = time.time();
        while (time.time() - t0 < timeout) and getattr(self.ps, attr) != value:
            pass

    # def test_basics(self):
    #     self.assertEqual(self.ps.connected, True)
    #     self.assertEqual(self.ps.opmode_sel, _et.idx.SlowRef)
    #     self.assertEqual(self.ps.pwrstate_sel, _et.idx.On)
    #     self.assertEqual(self.ps.current_sp, 0.0)
    #
    # def test_set_current_sp(self):
    #     """ Test setting current sp """
    #     self.ps.current_sp = 10.0
    #     self.assertEqual(self.ps.current_sp, 10.0)

    # def test_set_current_sp_exhaust(self):
    #     """ Test setting current sp exhaustively """
    #     for i in range(1000):
    #         self.ps.current_sp = float(i)
    #
    #     self.assertEqual(self.ps.current_sp, 999.0)

    def test_current_rb_callback(self):
        """ Test current_rb set up when current_sp is set """
        self.ps.opmode_sel = _et.idx.SlowRef
        self.ps.pwrstate_sel = _et.idx.On
        self.wait_for(_et.idx.On,'pwrstate_sel',3.0)
        values = numpy.linspace(-10.0, 10.0, 5001)
        for value in values:
            self.ps.current_sp = value
        self.wait_for(values[-1],'current_mon',3.0)
        self.assertEqual(self.ps.current_sp, values[-1])
        self.assertEqual(self.ps.current_sp, values[-1])

        #time.sleep(3.0)
        #self.assertEqual(self.ps._pvs['Current-SP']['SI-Fam:PS-B1B2-1'].get(), maxv-1)
        #self.assertEqual(self.ps._pvs['Current-SP']['SI-Fam:PS-B1B2-2'].get(), maxv-1)
        #self.assertEqual(self.ps.current_rb, maxv-1)

    # def test_currentref_mon_callback(self):
    #     """ Test currentref_mon set up when current_sp is set """
    #     self.ps.current_sp = 10.0
    #     self.assertEqual(self.ps._pvs['CurrentRef-Mon']['SI-Fam:PS-B1B2-1'].get(), 10.0)
    #     self.assertEqual(self.ps._pvs['CurrentRef-Mon']['SI-Fam:PS-B1B2-2'].get(), 10.0)
    #     self.assertEqual(self.ps.currentref_mon, 10.0)
    #
    # def test_current_mon_callback(self):
    #     """ Test current_mon set up when current_sp is set """
    #     self.ps.current_sp = 10.0
    #     self.assertEqual(self.ps._pvs['Current-Mon']['SI-Fam:PS-B1B2-1'].get(), 10.0)
    #     self.assertEqual(self.ps._pvs['Current-Mon']['SI-Fam:PS-B1B2-2'].get(), 10.0)
    #     self.assertEqual(self.ps.current_mon, 10.0)


# class TestEpicsQDA(unittest.TestCase, TestSet1, PS_QDA):
#
#     def setUp(self):
#         self.ps = PowerSupplyEpics(psname = self.psname(), use_vaca=True, enum_keys=True)
#         if not self.ps.connected:
#             raise Exception('Please run a power supply IOC with default VACA prefix!')
#         self.timeout = 3.0
#
#
# class TestEpicsB1B2_1(unittest.TestCase, TestSet1, PS_B1B2_1):
#
#     def setUp(self):
#         self.ps = PowerSupplyEpics(psname = self.psname(), use_vaca=True, enum_keys=True)
#         if not self.ps.connected:
#             raise Exception('Please run a power supply IOC with default VACA prefix!')
#         self.timeout = 3.0


# class TestEpicsSyncB1B2(unittest.TestCase, TestSet1, PSSync_B1B2):
#
#     def setUp(self):
#         self.ps = self.create_obj()
#         self.timeout = 3.0

# class TestEpicsSyncQDA(unittest.TestCase, TestSet1, PSSync_QDA):
#
#     def setUp(self):
#         self.ps = self.create_obj()
#         self.timeout = 3.0


if __name__ == '__main__':
   unittest.main()
