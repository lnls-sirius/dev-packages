#!/usr/bin/env python3

import unittest
import epics
import time

from siriuspy.pwrsupply.model import PowerSupplyEpics
from siriuspy.pwrsupply.model import PowerSupplySync
from siriuspy.csdevice.enumtypes import EnumTypes as _et


class PS:

    def psname(self):
        return ''

    def create_obj(self):
        return None

class PS_QDA(PS):

    def psname(self):
        return 'SI-Fam:PS-QDA'

class PS_B1B2_1(PS):

    def psname(self):
        return 'SI-Fam:PS-B1B2-1'

class PSSync_B1B2(PS):

    def create_obj(self):
        return PowerSupplySync(psnames=['SI-Fam:PS-B1B2-1','SI-Fam:PS-B1B2-2'],
                               #psnames=['SI-Fam:PS-B1B2-1',],
                               controller_type='ControllerEpics',
                               lock=True,
                               use_vaca=True,
                               enum_keys=True)

class PSSync_QDA(PS):

    def create_obj(self):
        return PowerSupplySync(psnames=['SI-Fam:PS-QDA',],
                               controller_type='ControllerEpics',
                               lock=False,
                               use_vaca=True,
                               enum_keys=True)


class TestSet1(PS):

    def wait_for(self, value, attr, timeout):
        t0 = time.time();
        while (time.time() - t0 < timeout) and getattr(self.ps, attr) != value:
            pass

    def test_basics(self):
        # reset, turn-off ps
        # self.ps.reset_cmd = 1
        self.ps.opmode_sel = 'SlowRef'
        self.ps.pwrstate_sel = 'Off'
        self.wait_for('Off','pwrstate_sts',self.timeout)

        self.assertEqual(self.ps.opmode_sel, 'SlowRef')
        self.assertEqual(self.ps.opmode_sts, 'SlowRef')
        self.assertEqual(self.ps.pwrstate_sel, 'Off')
        self.assertEqual(self.ps.pwrstate_sts, 'Off')
        # turn on ps
        self.ps.pwrstate_sel = 'On'
        self.wait_for('On','pwrstate_sts',self.timeout)
        self.assertEqual(self.ps.pwrstate_sel, 'On')
        self.assertEqual(self.ps.pwrstate_sts, 'On')
        # set current sp
        ref_value1 = 14.1
        self.ps.current_sp = ref_value1
        self.wait_for(ref_value1,'current_mon',self.timeout)
        self.assertEqual(self.ps.current_sp, ref_value1)
        self.assertEqual(self.ps.currentref_mon, ref_value1)
        self.assertEqual(self.ps.current_mon, ref_value1)
        self.assertEqual(self.ps.current_rb, ref_value1)
        # change mode to SlowRefSync
        self.ps.opmode_sel = 'SlowRefSync'
        self.ps.current_sp = 3.0
        self.wait_for(3.0,'current_sp',self.timeout)
        self.wait_for(3.0,'current_rb',self.timeout)
        self.wait_for(ref_value1,'currentref_mon',self.timeout)
        self.wait_for(ref_value1,'current_mon',self.timeout)


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


class TestEpicsSyncB1B2(unittest.TestCase, TestSet1, PSSync_B1B2):

    def setUp(self):
        self.ps = self.create_obj()
        self.timeout = 3.0

# class TestEpicsSyncQDA(unittest.TestCase, TestSet1, PSSync_QDA):
#
#     def setUp(self):
#         self.ps = self.create_obj()
#         self.timeout = 3.0


if __name__ == '__main__':
   unittest.main()
