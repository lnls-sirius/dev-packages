#!/usr/bin/env python3

import unittest
import time
import numpy
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.pwrsupply.model import PowerSupplyEpicsSync
#from siriuspy.pwrsupply.model import PowerSupplyEpicsSync2
#from siriuspy.pwrsupply.model import PowerSupplyEpicsSync3
from siriuspy.search import PSSearch as _PSSearch


new_pses=True


class TestSet1B1B2(unittest.TestCase):


    def create_ps(self,
                  use_vaca,
                  vaca_prefix,
                  lock,
                  with_ioc,
                  pses_type):

            if pses_type == 2:
                ps = PowerSupplyEpicsSync2(psnames=['SI-Fam:PS-B1B2-1','SI-Fam:PS-B1B2-2'],
                                           use_vaca=use_vaca,
                                           vaca_prefix=vaca_prefix,
                                           lock=lock)
                b1b2_1 = PowerSupplyEpicsSync2(psnames=['SI-Fam:PS-B1B2-1',],
                                               use_vaca=use_vaca,
                                               vaca_prefix=vaca_prefix,
                                               lock=False)
                b1b2_2 = PowerSupplyEpicsSync2(psnames=['SI-Fam:PS-B1B2-2',],
                                               use_vaca=use_vaca,
                                               vaca_prefix=vaca_prefix,
                                               lock=False)
                if with_ioc:
                    if not ps.wait_for_connection(timeout=5.0):
                        raise Exception('Epics IOC does not seem to be running!!!')
                else:
                    self.assertEqual(ps.wait_for_connection(timeout=1.0), False)
            elif pses_type == 1:
                ps = PowerSupplyEpicsSync(maname='SI-Fam:MA-B1B2',
                                          use_vaca=use_vaca,
                                          lock=lock,
                                          connection_timeout=3.0)


            elif pses_type == 3:
                ps = PowerSupplyEpicsSync(psnames=['SI-Fam:PS-B1B2-1','SI-Fam:PS-B1B2-2'],
                                           use_vaca=use_vaca,
                                           vaca_prefix=vaca_prefix,
                                           lock=lock)
                # b1b2_1 = PowerSupplyEpicsSync3(psnames=['SI-Fam:PS-B1B2-1',],
                #                                use_vaca=use_vaca,
                #                                vaca_prefix=vaca_prefix,
                #                                lock=False)
                # b1b2_2 = PowerSupplyEpicsSync3(psnames=['SI-Fam:PS-B1B2-2',],
                #                                use_vaca=use_vaca,
                #                                vaca_prefix=vaca_prefix,
                #                                lock=False)
                if with_ioc:
                    if not ps.wait_for_connection(timeout=5.0):
                        raise Exception('Epics IOC does not seem to be running!!!')
                else:
                    self.assertEqual(ps.wait_for_connection(timeout=1.0), False)

            return ps
            #return ps, b1b2_1, b1b2_2

    # def assertEqualTimeout(self, value, obj, attr, timeout):
    #     t0 = time.time();
    #     while (time.time() - t0 < timeout) and getattr(obj, attr) != value:
    #         pass
    #     self.assertEqual(getattr(obj, attr), value)

    def assertEqualTimeoutCurrents(self, value, obj, timeout, tol=0.0):
        # t0 = time.time();
        # while (time.time() - t0 < timeout and
        #        (obj.current_sp != value or
        #         obj.current_rb != value or
        #         obj.currentref_mon != value or
        #         abs(obj.current_mon - value) > tol)):
        #     pass
        self.assertEqual(getattr(obj, 'current_sp'), value)
        self.assertEqual(getattr(obj, 'current_rb'), value)
        self.assertEqual(getattr(obj, 'currentref_mon'), value)
        self.assertLessEqual(abs(getattr(obj, 'current_mon')-value), tol)

    def get_pvs(self, ps, propty):
        pvs = []
        for pvname, pv in ps._pvs.items():
            if propty in pvname:
                pvs.append(pv)
        return pvs

    def setUp(self):
        self.upper_alarm_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','HIHI')
        self.upper_warning_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','HIGH')
        self.upper_disp_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','HOPR')
        self.lower_disp_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','LOPR')
        self.lower_warning_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','LOW')
        self.lower_alarm_limit = _PSSearch.get_splim('si-dipole-b1b2-fam','LOLO')

    def tearDown(self):
        self.ps.disconnect()

    def test_init_write_noIOC_lockFalse(self):
        #print('test_init_write_noIOC_lockFalse')
        self.ps = self.create_ps(use_vaca=True, vaca_prefix='DummyPrefix', lock=False, with_ioc=False, pses_type=3)
        self.assertEqual(self.ps.opmode_sel, None)
        self.assertEqual(self.ps.opmode_sts, None)
        self.assertEqual(self.ps.pwrstate_sel, None)
        self.assertEqual(self.ps.pwrstate_sts, None)
        self.ps.opmode_sel = _et.idx.SlowRef
        self.assertEqual(self.ps.opmode_sel, _et.idx.SlowRef)
        self.assertEqual(self.ps.opmode_sts, None)
        self.ps.pwrstate_sel = _et.idx.On
        self.assertEqual(self.ps.pwrstate_sel, _et.idx.On)
        self.assertEqual(self.ps.pwrstate_sts, None)
        value = 13.34; self.ps.current_sp = value
        self.assertEqual(self.ps.current_sp, value)
        self.assertEqual(self.ps.current_rb, None)
        self.assertEqual(self.ps.currentref_mon, None)
        self.assertEqual(self.ps.current_mon, None)

    def _test_limits_lockFalse(self):
        ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=False, with_ioc=True, pses_type=3)
        self.assertEqual(self.ps.upper_alarm_limit, self.upper_alarm_limit)
        self.assertEqual(self.ps.upper_warning_limit, self.upper_warning_limit)
        self.assertEqual(self.ps.upper_disp_limit, self.upper_disp_limit)
        self.assertEqual(self.ps.lower_disp_limit, self.lower_disp_limit)
        self.assertEqual(self.ps.lower_warning_limit, self.lower_warning_limit)
        self.assertEqual(self.ps.lower_alarm_limit, self.lower_alarm_limit)

    def test_lockTrue_pwrstate_sel(self):
        #print('test_lockTrue_pwrstate_sel')
        self.ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, pses_type=3)
        # inits
        self.ps.opmode_sel = 0
        self.ps.pwrstate_sel = 1
        self.ps.process_puts(wait=1.0)
        self.assertEqual(0, self.ps.opmode_sel)
        self.assertEqual(1, self.ps.pwrstate_sel)
        # loops
        values = [0,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0,1]
        pv1, pv2 = self.get_pvs(self.ps, 'PwrState-Sel')
        for value in values:
            self.ps.pwrstate_sel = value
            pv1.put(0, wait=True)
            pv2.put(0, wait=True)
        # test
        self.ps.process_puts(wait=0.5); time.sleep(1.0)
        value = values[-1]
        self.assertEqual(value, self.ps.pwrstate_sel)
        self.assertEqual(value, self.ps.pwrstate_sts)
        self.assertEqual(value, pv1.value)
        self.assertEqual(value, pv2.value)

    def test_lockTrue_opmode_sel(self):
        #print('test_lockTrue_opmode_sel')
        # init and test
        self.ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, pses_type=3)
        self.ps.opmode_sel = 0
        self.ps.pwrstate_sel = 1
        self.assertEqual(0, self.ps.opmode_sel)
        self.assertEqual(1, self.ps.pwrstate_sel)
        self.ps.process_puts(wait=0.5); time.sleep(0.2)
        pv1, pv2 = self.get_pvs(self.ps, 'OpMode-Sts')
        self.assertEqual(0, pv1.value)
        self.assertEqual(0, pv2.value)
        pv1, pv2 = self.get_pvs(self.ps, 'PwrState-Sts')
        self.assertEqual(1, pv1.value)
        self.assertEqual(1, pv2.value)
        # loop
        values = [0,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0]
        pv1, pv2 = self.get_pvs(self.ps, 'OpMode-Sel')
        for value in values:
            self.ps.opmode_sel = value
            pv1.put(1, wait=True)
            pv2.put(1, wait=True)
        # test
        self.ps.process_puts(wait=0.2); time.sleep(0.2)
        value = values[-1]
        self.assertEqual(value, self.ps.opmode_sel)
        self.assertEqual(value, self.ps.opmode_sts)
        self.assertEqual(value, pv1.value)
        self.assertEqual(value, pv2.value)

    def test_lockTrue_current_sp(self):
        #print('test_lockTrue_current_sp')
        # init and test
        self.ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, pses_type=3)
        self.ps.opmode_sel = 0
        self.ps.pwrstate_sel = 1
        self.ps.process_puts(wait=0.5); time.sleep(0.2)
        pv1, pv2 = self.get_pvs(self.ps, 'OpMode-Sts')
        self.assertEqual(0, pv1.value)
        self.assertEqual(0, pv2.value)
        pv1, pv2 = self.get_pvs(self.ps, 'PwrState-Sts')
        self.assertEqual(1, pv1.value)
        self.assertEqual(1, pv2.value)
        # loop
        pv1, pv2 = self.get_pvs(self.ps, 'Current-SP')
        values = numpy.linspace(0, 10.0, 51)
        for value in values:
            self.ps.current_sp = value
            pv1.put(1.0, wait=True)
            pv2.put(2.0, wait=True)
        # test
        self.ps.process_puts(wait=0.2); time.sleep(0.2)
        value = values[-1]
        self.assertEqual(value, self.ps.current_sp)
        self.assertEqual(value, self.ps.current_rb)
        self.assertEqual(value, self.ps.currentref_mon)
        self.assertEqual(value, self.ps.current_mon)
        pv1, pv2 = self.get_pvs(self.ps, 'Current-SP')
        self.assertEqual(value, pv1.value)
        self.assertEqual(value, pv2.value)
        pv1, pv2 = self.get_pvs(self.ps, 'Current-RB')
        self.assertEqual(value, pv1.value)
        self.assertEqual(value, pv2.value)
        pv1, pv2 = self.get_pvs(self.ps, 'CurrentRef-Mon')
        self.assertEqual(value, pv1.value)
        self.assertEqual(value, pv2.value)
        pv1, pv2 = self.get_pvs(self.ps, 'Current-Mon')
        self.assertEqual(value, pv1.value)
        self.assertEqual(value, pv2.value)

    def test_lockTrue_current_sp_long_loops(self):
        #print('test_lockTrue_current_sp_long_loops')
        # init
        self.ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, pses_type=3)
        self.ps.opmode_sel = 0
        self.ps.pwrstate_sel = 1
        self.ps.process_puts(wait=0.2); time.sleep(0.2)
        pv1, pv2 = self.get_pvs(self.ps, 'OpMode-Sts')
        self.assertEqual(0, pv1.value)
        self.assertEqual(0, pv2.value)
        pv1, pv2 = self.get_pvs(self.ps, 'PwrState-Sts')
        self.assertEqual(1, pv1.value)
        self.assertEqual(1, pv2.value)
        # loop
        """ Test current_rb set up when current_sp is set """
        values = numpy.linspace(0, 10.0, 51)
        for value in values:
            self.ps.current_sp = value
        self.ps.process_puts(wait=0.2); time.sleep(0.2); value=values[-1]
        self.assertEqual(value, self.ps.current_sp)
        pv1, pv2 = self.get_pvs(self.ps, 'Current-SP')
        self.assertEqual(value, pv1.value)
        self.assertEqual(value, pv2.value)
        pv1, pv2 = self.get_pvs(self.ps, 'Current-RB')
        self.assertEqual(value, pv1.value)
        self.assertEqual(value, pv2.value)
        pv1, pv2 = self.get_pvs(self.ps, 'CurrentRef-Mon')
        self.assertEqual(value, pv1.value)
        self.assertEqual(value, pv2.value)
        pv1, pv2 = self.get_pvs(self.ps, 'Current-Mon')
        self.assertEqual(value, pv1.value)
        self.assertEqual(value, pv2.value)

    def test_write_lockFalse(self):
        #print('test_write_lockFalse')
        self.ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=False, with_ioc=True, pses_type=3)
        self.ps.opmode_sel = 0
        self.ps.pwrstate_sel = 1
        self.ps.process_puts(wait=0.2); time.sleep(0.2)
        pv1, pv2 = self.get_pvs(self.ps, 'OpMode-Sts')
        self.assertEqual(0, pv1.value)
        self.assertEqual(0, pv2.value)
        pv1, pv2 = self.get_pvs(self.ps, 'PwrState-Sts')
        self.assertEqual(1, pv1.value)
        self.assertEqual(1, pv2.value)
        # tests
        self.ps.opmode_sel = _et.idx.SlowRefSync
        self.ps.process_puts(wait=0.2); time.sleep(0.2)
        self.assertEqual(self.ps.opmode_sel, _et.idx.SlowRefSync)
        self.assertEqual(_et.idx.SlowRefSync, self.ps.opmode_sts)
        pv1, pv2 = self.get_pvs(self.ps, 'OpMode-Sel')
        pv1.put(_et.idx.SlowRef, wait=True)
        self.ps.process_puts(wait=0.2); time.sleep(0.2)
        self.assertEqual(self.ps.opmode_sel, _et.idx.SlowRef)
        pv1, pv2 = self.get_pvs(self.ps, 'OpMode-Sts')
        self.assertEqual(pv1.value, _et.idx.SlowRef)
        self.assertEqual(pv2.value, _et.idx.SlowRef)
        value = 1.2345; self.ps.current_sp = value
        self.ps.process_puts(wait=0.2); time.sleep(0.2)
        self.assertEqualTimeoutCurrents(value, self.ps, 3.0, 0.0)
        pv1, pv2 = self.get_pvs(self.ps, 'Current-SP')
        value = 2.0; pv2.value = value
        self.ps.process_puts(wait=0.2); time.sleep(0.2)
        self.assertEqualTimeoutCurrents(value, self.ps, 3.0, 0.0)
        pv1, pv2 = self.get_pvs(self.ps, 'Current-Mon')
        self.assertEqual(pv1.value, value)
        self.assertEqual(pv2.value, value)

    def test_loopwrite_lockTrue(self):
        #print('test_loopwrite_lockTrue')
        # init
        self.ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, pses_type=3)
        self.ps.pwrstate_sel = _et.idx.On
        self.ps.opmode_sel = _et.idx.SlowRef
        self.ps.process_puts(wait=0.2); time.sleep(0.2)
        self.assertEqual(self.ps.opmode_sel, _et.idx.SlowRef)
        self.assertEqual(_et.idx.On, self.ps.pwrstate_sts)
        # loop
        pv1, pv2 = self.get_pvs(self.ps, 'Current-SP')
        for i in range(401):
            value = 4.2345; self.ps.current_sp = value
            self.assertEqual(self.ps.current_sp, value)
            value = 6.4321; self.ps.current_sp = value
            self.assertEqual(self.ps.current_sp, value)
        self.ps.process_puts(wait=0.2); time.sleep(1.0)
        self.assertEqualTimeoutCurrents(value, self.ps, 3.0, 0.0)

    def test_loopwrite_externalput_lockTrue(self):
        #print('test_loopwrite_externalput_lockTrue')
        # init
        self.ps = self.create_ps(use_vaca=True, vaca_prefix=None, lock=True, with_ioc=True, pses_type=3)
        self.ps.pwrstate_sel = _et.idx.On
        self.ps.opmode_sel = _et.idx.SlowRef
        self.ps.process_puts(wait=0.2); time.sleep(0.2)
        self.assertEqual(self.ps.opmode_sel, _et.idx.SlowRef)
        self.assertEqual(_et.idx.On, self.ps.pwrstate_sts)
        # loop
        pv1, pv2 = self.get_pvs(self.ps, 'Current-SP')
        for i in range(401):
            value = 7.2345; self.ps.current_sp = value
            self.assertEqual(self.ps.current_sp, value)
            pv1.put(13,wait=True); pv2.put(12,wait=True)
            value = 8.4321; self.ps.current_sp = value
            self.assertEqual(self.ps.current_sp, value)
        self.ps.process_puts(wait=0.2); time.sleep(1.0)
        self.assertEqualTimeoutCurrents(value, self.ps, 3.0, 0.0)






if __name__ == '__main__':
   unittest.main()
