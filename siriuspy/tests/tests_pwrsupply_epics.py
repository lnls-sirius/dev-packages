#!/usr/bin/env python3

import unittest
import epics
import time

from siriuspy.pwrsupply.model import PowerSupplyEpics
from siriuspy.csdevice.enumtypes import EnumTypes as _et


class PS:

    def psname(self):
        return ''


class QDA(PS):

    def psname(self):
        return 'SI-Fam:PS-QDA'


class B1B2_1(PS):

    def psname(self):
        return 'SI-Fam:PS-B1B2-1'


class TestPowerSupplyEpics(PS):

    def wait_for(self, value, attr, timeout):
        t0 = time.time();
        while (time.time() - t0 < timeout) and getattr(self.ps, attr) != value:
            pass

    def test_basics(self):
        # reset, turn-off ps
        self.ps.reset_cmd = 1
        self.ps.opmode_sel = 'SlowRef'
        self.ps.pwrstate_sel = 'Off'
        self.wait_for('Off','pwrstate_sts',3.0)
        self.assertEqual(self.ps.opmode_sel, 'SlowRef')
        self.assertEqual(self.ps.opmode_sts, 'SlowRef')
        self.assertEqual(self.ps.pwrstate_sel, 'Off')
        self.assertEqual(self.ps.pwrstate_sts, 'Off')
        # turn on ps
        self.ps.pwrstate_sel = 'On'
        self.wait_for('On','pwrstate_sts',3.0)
        self.assertEqual(self.ps.pwrstate_sel, 'On')
        self.assertEqual(self.ps.pwrstate_sts, 'On')
        # set current sp
        self.ps.current_sp = 10.0
        self.wait_for(10.0,'current_mon',3.0)
        self.assertEqual(self.ps.current_sp, 10.0)
        self.assertEqual(self.ps.current_rb, 10.0)
        self.assertEqual(self.ps.currentref_mon, 10.0)
        self.assertEqual(self.ps.current_mon, 10.0)
        # change mode to SlowRefSync
        self.ps.opmode_sel = 'SlowRefSync'
        self.ps.current_sp = 2.0
        self.wait_for(2.0,'current_sp',3.0)
        self.wait_for(2.0,'current_rb',3.0)
        self.wait_for(10.0,'currentref_mon',3.0)
        self.wait_for(10.0,'current_mon',3.0)


class TestQDA(unittest.TestCase, TestPowerSupplyEpics, QDA):

    def setUp(self):
        self.ps = PowerSupplyEpics(psname = self.psname(), use_vaca=True, enum_keys=True)
        if not self.ps.connected:
            raise Exception('Please run a power supply IOC with default VACA prefix!')


class TestB1B2_1(unittest.TestCase, TestPowerSupplyEpics, B1B2_1):

    def setUp(self):
        self.ps = PowerSupplyEpics(psname = self.psname(), use_vaca=True, enum_keys=True)
        if not self.ps.connected:
            raise Exception('Please run a power supply IOC with default VACA prefix!')


if __name__ == '__main__':
   unittest.main()
