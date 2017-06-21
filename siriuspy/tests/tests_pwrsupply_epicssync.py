#!/usr/bin/env python3

import unittest
import epics
import time
import numpy

#from siriuspy.pwrsupply.model import PowerSupplyEpics
#from siriuspy.pwrsupply.model import PowerSupplySync
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.pwrsupply.model import PowerSupplyEpicsSync
import random as _random

class TestSet1(unittest.TestCase):

    def setUp(self):
        self.ps = PowerSupplyEpicsSync(maname='SI-Fam:MA-B1B2',
                                 use_vaca=True,
                                 lock=True)

    def wait_for(self, value, obj, attr, timeout):
        t0 = time.time();
        while (time.time() - t0 < timeout) and getattr(obj, attr) != value:
            pass
        if getattr(obj, attr) != value:
            raise Exception('timeout!')

    def test_lock_pwrstate_sel(self):

        self.ps.opmode_sel = _et.idx.SlowRef
        self.ps.pwrstate_sel = _et.idx.On
        self.ps.current_sp = 5.5
        self.wait_for(_et.idx.SlowRef,self.ps,'opmode_sts',3.0)
        self.wait_for(_et.idx.On,self.ps,'pwrstate_sts',3.0)
        self.wait_for(5.5,self.ps,'current_sp',3.0)
        self.wait_for(5.5,self.ps,'current_mon',3.0)

        psname = self.ps._psnames[0]
        values = [0,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0,1]
        for value in values:
            self.ps.pwrstate_sel = value
            self.ps._pvs['PwrState-Sel'][psname].put(0, wait=True)
        self.wait_for(values[-1],self.ps._pvs['PwrState-Sel'][psname],'value',3.0)
        self.ps.finished()

    def test_lock_opmode_sel(self):

        self.ps.opmode_sel = _et.idx.SlowRef
        self.ps.pwrstate_sel = _et.idx.On
        self.ps.current_sp = 5.5
        self.wait_for(_et.idx.SlowRef,self.ps,'opmode_sts',3.0)
        self.wait_for(_et.idx.On,self.ps,'pwrstate_sts',3.0)
        self.wait_for(5.5,self.ps,'current_sp',3.0)
        self.wait_for(5.5,self.ps,'current_mon',3.0)

        psname = self.ps._psnames[0]
        values = [0,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0]
        for value in values:
            self.ps.opmode_sel = value
            self.ps._pvs['OpMode-Sel'][psname].put(1, wait=True)
        self.wait_for(values[-1],self.ps._pvs['OpMode-Sel'][psname],'value',3.0)
        self.ps.finished()

    def test_lock_current_sp(self):
        self.ps.opmode_sel = _et.idx.SlowRef
        self.ps.pwrstate_sel = _et.idx.On
        self.ps.current_sp = 5.5
        self.wait_for(_et.idx.SlowRef,self.ps,'opmode_sts',3.0)
        self.wait_for(_et.idx.On,self.ps,'pwrstate_sts',3.0)
        self.wait_for(5.5,self.ps,'current_sp',3.0)
        self.wait_for(5.5,self.ps,'current_mon',3.0)
        psname = self.ps._psnames[0]
        values = numpy.linspace(0, 10.0, 51)
        for value in values:
            self.ps.current_sp = value
            self.ps._pvs['Current-SP'][psname].put(1.0, wait=True)
        self.wait_for(values[-1],self.ps._pvs['Current-SP'][psname],'value',3.0)
        self.ps.finished()

    def test_current_sp_long_loops(self):
        """ Test current_rb set up when current_sp is set """
        self.ps.opmode_sel = _et.idx.SlowRef
        self.ps.pwrstate_sel = _et.idx.On
        self.wait_for(_et.idx.SlowRef,self.ps,'opmode_sts',3.0)
        self.wait_for(_et.idx.On,self.ps,'pwrstate_sts',3.0)
        self.ps.current_sp = _random.random()
        values = numpy.linspace(0, 10.0, 51)
        for value in values:
            #time.sleep(0.01)
            self.ps.current_sp = value
        self.wait_for(values[-1],self.ps, 'current_mon',0.1)
        self.assertEqual(self.ps.current_sp, values[-1])
        self.assertEqual(self.ps.current_rb, values[-1])
        self.assertEqual(self.ps.currentref_mon, values[-1])
        self.assertEqual(self.ps.current_mon, values[-1])
        self.wait_for(values[-1],self.ps._pvs['Current-Mon']['SI-Fam:PS-B1B2-1'],'value',3.0)
        self.wait_for(values[-1],self.ps._pvs['Current-Mon']['SI-Fam:PS-B1B2-2'],'value',3.0)
        self.ps.finished()



    #     pass
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
