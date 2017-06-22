#!/usr/bin/env python3

import unittest
import epics
import time
import numpy
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.pwrsupply.model import PowerSupplyEpicsSync
import random as _random
from siriuspy.search import PSSearch as _PSSearch


class TestSet1(unittest.TestCase):


    def assertEqualTimeout(self, value, obj, attr, timeout):
        t0 = time.time();
        while (time.time() - t0 < timeout) and getattr(obj, attr) != value:
            pass
        self.assertEqual(getattr(obj, attr), value)

    def setUp(self):
        self.ps = PowerSupplyEpicsSync(maname='SI-Fam:MA-B1B2',
                                       use_vaca=True,
                                       lock=True)
        self.ps.opmode_sel = _et.idx.SlowRef
        self.ps.pwrstate_sel = _et.idx.On
        self.ps.current_sp = 5.5
        self.assertEqualTimeout(_et.idx.SlowRef,self.ps,'opmode_sts',3.0)
        self.assertEqualTimeout(_et.idx.On,self.ps,'pwrstate_sts',3.0)
        self.assertEqualTimeout(5.5,self.ps,'current_sp',3.0)
        self.assertEqualTimeout(5.5,self.ps,'current_mon',3.0)

        self.upper_alarm_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','HIHI')
        self.upper_warning_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','HIGH')
        self.upper_disp_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','HOPR')
        self.lower_disp_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','LOPR')
        self.lower_warning_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','LOW')
        self.lower_alarm_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','LOLO')

    def tearDown(self):
        self.ps.finished()

    def test_limits(self):
        self.assertEqual(self.ps.upper_alarm_limit, self.upper_alarm_limit)
        self.assertEqual(self.ps.upper_warning_limit, self.upper_warning_limit)
        self.assertEqual(self.ps.upper_disp_limit, self.upper_disp_limit)
        self.assertEqual(self.ps.lower_disp_limit, self.lower_disp_limit)
        self.assertEqual(self.ps.lower_warning_limit, self.lower_warning_limit)
        self.assertEqual(self.ps.lower_alarm_limit, self.lower_alarm_limit)

    def test_lock_pwrstate_sel(self):
        psname = self.ps._psnames[0]
        values = [0,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0,1]
        for value in values:
            self.ps.pwrstate_sel = value
            self.ps._pvs['PwrState-Sel'][psname].put(0, wait=True)
        self.assertEqualTimeout(values[-1],self.ps._pvs['PwrState-Sel'][psname],'value',3.0)
        self.ps.finished()

    def test_lock_opmode_sel(self):
        psname = self.ps._psnames[0]
        values = [0,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0]
        for value in values:
            self.ps.opmode_sel = value
            self.ps._pvs['OpMode-Sel'][psname].put(1, wait=True)
        self.assertEqualTimeout(values[-1],self.ps._pvs['OpMode-Sel'][psname],'value',3.0)

    def test_lock_current_sp(self):
        psname = self.ps._psnames[0]
        values = numpy.linspace(0, 10.0, 51)
        for value in values:
            self.ps.current_sp = value
            self.ps._pvs['Current-SP'][psname].put(1.0, wait=True)
        self.assertEqualTimeout(values[-1],self.ps._pvs['Current-SP'][psname],'value',3.0)

    def test_current_sp_long_loops(self):
        """ Test current_rb set up when current_sp is set """
        values = numpy.linspace(0, 10.0, 51)
        for value in values:
            self.ps.current_sp = value
        self.assertEqualTimeout(values[-1],self.ps, 'current_mon',0.1)
        self.assertEqual(self.ps.current_sp, values[-1])
        self.assertEqual(self.ps.current_rb, values[-1])
        self.assertEqual(self.ps.currentref_mon, values[-1])
        self.assertEqual(self.ps.current_mon, values[-1])
        self.assertEqualTimeout(values[-1],self.ps._pvs['Current-Mon']['SI-Fam:PS-B1B2-1'],'value',3.0)
        self.assertEqualTimeout(values[-1],self.ps._pvs['Current-Mon']['SI-Fam:PS-B1B2-2'],'value',3.0)
        self.ps.finished()


if __name__ == '__main__':
   unittest.main()
