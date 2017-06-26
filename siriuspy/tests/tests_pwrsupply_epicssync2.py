#!/usr/bin/env python3

import unittest
import epics
import time
import numpy
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.pwrsupply.model import PowerSupplyEpicsSync
from siriuspy.pwrsupply.model import PowerSupplyEpicsSync2
import random as _random
from siriuspy.search import PSSearch as _PSSearch



new_pses=False


class TestSet1B1B2(unittest.TestCase):


    def create_ps(self,
                  use_vaca,
                  vaca_prefix,
                  lock,
                  with_ioc,
                  new_pses):

            if new_pses:
                ps = PowerSupplyEpicsSync2(psnames=['SI-Fam:PS-B1B2-1','SI-Fam:PS-B1B2-2'],
                                           use_vaca=use_vaca,
                                           vaca_prefix=vaca_prefix,
                                           lock=lock)
                if with_ioc:
                    if not ps.wait_for_connection(timeout=5.0):
                        raise Exception('Epics IOC does not seem to be running!!!')
                else:
                    self.assertEqual(ps.wait_for_connection(timeout=1.0), False)
            else:
                ps = PowerSupplyEpicsSync(maname='SI-Fam:MA-B1B2',
                                          use_vaca=use_vaca,
                                          lock=lock,
                                          connection_timeout=3.0)
            return ps

    def assertEqualTimeout(self, value, obj, attr, timeout):
        t0 = time.time();
        while (time.time() - t0 < timeout) and getattr(obj, attr) != value:
            pass
        self.assertEqual(getattr(obj, attr), value)

    def assertEqualTimeoutCurrents(self, value, obj, timeout, tol=0.0):
        t0 = time.time();
        while (time.time() - t0 < timeout and
               (obj.current_sp != value or
                obj.current_rb != value or
                obj.currentref_mon != value or
                abs(obj.current_mon - value) > tol)):
            pass
        self.assertEqual(getattr(obj, 'current_sp'), value)
        self.assertEqual(getattr(obj, 'current_rb'), value)
        self.assertEqual(getattr(obj, 'currentref_mon'), value)
        self.assertLessEqual(abs(getattr(obj, 'current_mon')-value), tol)

    def setUp(self):
        self.upper_alarm_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','HIHI')
        self.upper_warning_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','HIGH')
        self.upper_disp_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','HOPR')
        self.lower_disp_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','LOPR')
        self.lower_warning_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','LOW')
        self.lower_alarm_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','LOLO')

    def test_init_write_noIOC_lockFalse(self):
        ps = self.create_ps(use_vaca=True, vaca_prefix='DummyPrefix', lock=False, with_ioc=False, new_pses=True)

        self.assertEqual(ps.opmode_sel, None)
        self.assertEqual(ps.opmode_sts, None)
        self.assertEqual(ps.pwrstate_sel, None)
        self.assertEqual(ps.pwrstate_sts, None)

        ps.opmode_sel = _et.idx.SlowRef
        self.assertEqual(ps.opmode_sel, _et.idx.SlowRef)
        self.assertEqual(ps.opmode_sts, None)

        ps.pwrstate_sel = _et.idx.On
        self.assertEqual(ps.pwrstate_sel, _et.idx.On)
        self.assertEqual(ps.pwrstate_sts, None)

        value = 13.34; ps.current_sp = value
        self.assertEqual(ps.current_sp, value)
        self.assertEqual(ps.current_rb, None)
        self.assertEqual(ps.currentref_mon, None)
        self.assertEqual(ps.current_mon, None)

        ps.disconnect()

    def test_limits_lockFalse(self):
        ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=False, with_ioc=True, new_pses=new_pses)
        self.assertEqual(ps.upper_alarm_limit, self.upper_alarm_limit)
        self.assertEqual(ps.upper_warning_limit, self.upper_warning_limit)
        self.assertEqual(ps.upper_disp_limit, self.upper_disp_limit)
        self.assertEqual(ps.lower_disp_limit, self.lower_disp_limit)
        self.assertEqual(ps.lower_warning_limit, self.lower_warning_limit)
        self.assertEqual(ps.lower_alarm_limit, self.lower_alarm_limit)

    def test_lockTrue_pwrstate_sel(self):
        ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, new_pses=new_pses)

        psname = ps._psnames[0]
        values = [0,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0,1]
        for value in values:
            ps.pwrstate_sel = value
            ps._pvs['PwrState-Sel'][psname].put(0, wait=True)
        self.assertEqualTimeout(values[-1],ps._pvs['PwrState-Sel'][psname],'value',3.0)
        ps.disconnect()

    def test_lockTrue_opmode_sel(self):
        ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, new_pses=new_pses)
        psname = ps._psnames[0]
        values = [0,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0]
        for value in values:
            ps.opmode_sel = value
            ps._pvs['OpMode-Sel'][psname].put(1, wait=True)
        self.assertEqualTimeout(values[-1],ps._pvs['OpMode-Sel'][psname],'value',3.0)

    def test_lockTrue_current_sp(self):
        ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, new_pses=new_pses)
        psname = ps._psnames[0]
        values = numpy.linspace(0, 10.0, 51)
        for value in values:
            ps.current_sp = value
            ps._pvs['Current-SP'][psname].put(1.0, wait=True)
        self.assertEqualTimeout(values[-1],ps._pvs['Current-SP'][psname],'value',3.0)

    def test_lockTrue_current_sp_long_loops(self):
        ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, new_pses=new_pses)

        """ Test current_rb set up when current_sp is set """
        values = numpy.linspace(0, 10.0, 51)
        for value in values:
            ps.current_sp = value
        self.assertEqualTimeoutCurrents(values[-1], ps, 3.0, 0.0)
        self.assertEqualTimeout(values[-1],ps._pvs['Current-Mon']['SI-Fam:PS-B1B2-1'],'value',3.0)
        self.assertEqualTimeout(values[-1],ps._pvs['Current-Mon']['SI-Fam:PS-B1B2-2'],'value',3.0)
        ps.disconnect()

    def test_write_lockFalse(self):
        ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=False, with_ioc=True, new_pses=new_pses)

        ps.opmode_sel = _et.idx.SlowRef
        self.assertEqual(ps.opmode_sel, _et.idx.SlowRef)
        self.assertEqualTimeout(_et.idx.SlowRef, ps, 'opmode_sts', 3.0)
        ps.opmode_sel = _et.idx.SlowRefSync
        self.assertEqual(ps.opmode_sel, _et.idx.SlowRefSync)
        self.assertEqualTimeout(_et.idx.SlowRefSync, ps, 'opmode_sts', 3.0)

        ps.pwrstate_sel = _et.idx.On
        self.assertEqual(ps.pwrstate_sel, _et.idx.On)
        self.assertEqualTimeout(_et.idx.On, ps, 'pwrstate_sts', 3.0)
        ps.pwrstate_sel = _et.idx.Off
        self.assertEqual(ps.pwrstate_sel, _et.idx.Off)
        self.assertEqualTimeout(_et.idx.Off, ps, 'pwrstate_sts', 3.0)

        value = 1.2345; ps.current_sp = value
        self.assertEqualTimeoutCurrents(value, ps, 3.0, 0.0)
        value = 5.4321; ps.current_sp = value
        self.assertEqualTimeoutCurrents(value, ps, 3.0, 0.0)
        ps.disconnect()

    def _test_loopwrite_lockTrue(self):
        ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, new_pses=new_pses)

        ps.opmode_sel = _et.idx.SlowRef
        self.assertEqual(ps.opmode_sel, _et.idx.SlowRef)
        self.assertEqualTimeout(_et.idx.SlowRef, ps, 'opmode_sts', 3.0)
        ps.opmode_sel = _et.idx.SlowRefSync
        self.assertEqual(ps.opmode_sel, _et.idx.SlowRefSync)
        self.assertEqualTimeout(_et.idx.SlowRefSync, ps, 'opmode_sts', 3.0)

        ps.pwrstate_sel = _et.idx.On
        self.assertEqual(ps.pwrstate_sel, _et.idx.On)
        self.assertEqualTimeout(_et.idx.On, ps, 'pwrstate_sts', 3.0)
        ps.pwrstate_sel = _et.idx.Off
        self.assertEqual(ps.pwrstate_sel, _et.idx.Off)
        self.assertEqualTimeout(_et.idx.Off, ps, 'pwrstate_sts', 3.0)

        for i in range(11):
            #print(i)
            value = 4.2345; ps.current_sp = value
            self.assertEqual(ps.current_sp, value)
            self.assertEqualTimeout(value, ps, 'current_rb', 3.0)
            self.assertEqualTimeout(value, ps, 'currentref_mon', 3.0)
            self.assertEqualTimeout(value, ps, 'current_mon', 3.0)
            value = 6.4321; ps.current_sp = value
            self.assertEqual(ps.current_sp, value)
            ps._pvs['Current-SP']['SI-Fam:PS-B1B2-1'].put(13,wait=True)
            ps._pvs['Current-SP']['SI-Fam:PS-B1B2-2'].put(12,wait=True)
            self.assertEqualTimeout(value, ps, 'current_mon', 3.0)
        ps.disconnect()

    def _test_loopwrite_externalput_lockTrue(self):
        ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, new_pses=new_pses)

        ps.opmode_sel = _et.idx.SlowRef
        self.assertEqual(ps.opmode_sel, _et.idx.SlowRef)
        self.assertEqualTimeout(_et.idx.SlowRef, ps, 'opmode_sts', 3.0)
        ps.opmode_sel = _et.idx.SlowRefSync
        self.assertEqual(ps.opmode_sel, _et.idx.SlowRefSync)
        self.assertEqualTimeout(_et.idx.SlowRefSync, ps, 'opmode_sts', 3.0)

        ps.pwrstate_sel = _et.idx.On
        self.assertEqual(ps.pwrstate_sel, _et.idx.On)
        self.assertEqualTimeout(_et.idx.On, ps, 'pwrstate_sts', 3.0)
        ps.pwrstate_sel = _et.idx.Off
        self.assertEqual(ps.pwrstate_sel, _et.idx.Off)
        self.assertEqualTimeout(_et.idx.Off, ps, 'pwrstate_sts', 3.0)

        for i in range(41):
            #print(i)
            value = 1.2345; ps.current_sp = value
            self.assertEqual(ps.current_sp, value)
            self.assertEqualTimeout(value, ps, 'current_rb', 3.0)
            ps._pvs['Current-SP']['SI-Fam:PS-B1B2-1'].put(13,wait=True)
            ps._pvs['Current-SP']['SI-Fam:PS-B1B2-2'].put(12,wait=True)
            self.assertEqualTimeout(value, ps, 'currentref_mon', 3.0)
            self.assertEqualTimeout(value, ps, 'current_mon', 3.0)
            value = 5.4321; ps.current_sp = value
            self.assertEqual(ps.current_sp, value)
            self.assertEqualTimeout(value, ps, 'current_rb', 3.0)
            self.assertEqualTimeout(value, ps, 'currentref_mon', 3.0)
            ps._pvs['Current-SP']['SI-Fam:PS-B1B2-1'].put(13,wait=True)
            ps._pvs['Current-SP']['SI-Fam:PS-B1B2-2'].put(12,wait=True)
            self.assertEqualTimeout(value, ps, 'current_mon', 3.0)
        ps.disconnect()





if __name__ == '__main__':
   unittest.main()
