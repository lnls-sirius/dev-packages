#!/usr/bin/env python3

import unittest
import time
import math
import numpy
from siriuspy.csdevice.enumtypes import EnumTypes as _et
from siriuspy.magnet.model import MagnetPowerSupplyDipole


class MagnetPowerSupplyDipoleTest(unittest.TestCase):


    def assertEqualTimeout(self, value, obj, attr, timeout):
        t0 = time.time()
        while (time.time() - t0 < timeout) and getattr(obj, attr) != value:
            pass
        self.assertEqual(getattr(obj, attr), value)

    def assertAlmostEqualTimeout(self, value, obj, attr, timeout):
        t0 = time.time()
        while (time.time() - t0 < timeout) and getattr(obj, attr) != value:
            pass
        self.assertAlmostEqual(getattr(obj, attr), value)

    def setUp(self):
        self.ma = MagnetPowerSupplyDipole("SI-Fam:MA-B1B2", use_vaca=True)
        self.ma.opmode_sel = _et.idx.SlowRef
        self.ma.pwrstate_sel = _et.idx.On
        self.ma.current_sp = 0.0
        self.assertEqualTimeout(_et.idx.SlowRef, self.ma, 'opmode_sel', 2.0)
        self.assertEqualTimeout(_et.idx.SlowRef, self.ma, 'opmode_sts', 2.0)
        self.assertEqualTimeout(_et.idx.On, self.ma, 'pwrstate_sel', 2.0)
        self.assertEqualTimeout(_et.idx.On, self.ma, 'pwrstate_sts', 2.0)
        self.assertAlmostEqualTimeout(0.0, self.ma, 'current_sp', 2.0)
        self.assertAlmostEqualTimeout(0.0, self.ma, 'current_rb', 2.0)
        self.assertAlmostEqualTimeout(0.0, self.ma, 'currentref_mon', 2.0)
        self.assertAlmostEqualTimeout(0.0, self.ma, 'current_mon', 2.0)

    def tearDown(self):
        self.ma.disconnect()

    #test strength
    def test_set_strength(self):
        """ Test setting the strength attribute """
        self.ma.strength_sp = 0.101
        self.assertAlmostEqualTimeout(0.101, self.ma, 'strength_sp', 2.0)

    #test callbacks
    def test_strength_rb_callback(self):
        self.ma.strength_sp = 1.2
        self.assertAlmostEqualTimeout(1.2, self.ma, 'strength_rb', 2.0)

    def test_strengthref_mon_callback(self):
        self.ma.strength_sp = 1.3
        self.assertAlmostEqualTimeout(1.3, self.ma, 'strengthref_mon', 2.0)

    def test_strength_mon_callback(self):
        self.ma.strength_sp = 1.4
        self.assertAlmostEqualTimeout(1.4, self.ma, 'strength_mon', 2.0)

    def test_loop_set_strength(self):
        currents = numpy.linspace(0, 120.0, 101)
        strengths = [self.ma.conv_current_2_strength(current)
                     for current in currents]
        for strength in strengths:
            self.ma.strength_sp = strength
            time.sleep(0.01)
        self.assertAlmostEqualTimeout(
            strengths[-1], self.ma, 'strength_sp', timeout=2.0)
        self.assertAlmostEqualTimeout(
            strengths[-1], self.ma, 'strength_rb', timeout=2.0)
        self.assertAlmostEqualTimeout(
            strengths[-1], self.ma, 'strengthref_mon', timeout=2.0)
        self.assertAlmostEqualTimeout(
            strengths[-1], self.ma, 'strength_mon', timeout=2.0)
        self.assertAlmostEqualTimeout(
            currents[-1], self.ma, 'current_sp', timeout=2.0)

    #
    # def test_strength_limit(self):
    #     self.set_current_sp = 0
    #
    # def test_current_sp_after_set_strength(self):
    #     strength = 5.0
    #     expected_current = 821.585676
    #
    #     self.ma.strength_sp = strength
    #     self.assertAlmostEqual(self.ma.current_sp, expected_current)


if __name__ == "__main__":
    unittest.main()
