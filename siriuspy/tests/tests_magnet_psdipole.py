#!/usr/bin/env python3

import unittest
import time
import math
from siriuspy.magnet.model import MagnetPowerSupplyDipole

class MagnetPowerSupplyDipoleTest(unittest.TestCase):

    UPPER_CURRENT_LIMIT = 1000.0
    LOWER_CURRENT_LIMIT = 0.0

    UPPER_STRENGTH_LIMIT = 5.834711
    LOWER_STRENGTH_LIMIT = 1.156212

    def assertEqualTimeout(self, value, obj, attr, timeout):
        t0 = time.time();
        while (time.time() - t0 < timeout) and getattr(obj, attr) != value:
            pass
        self.assertEqual(getattr(obj, attr), value)

    def setUp(self):
        self.ma = MagnetPowerSupplyDipole("SI-Fam:MA-B1B2", use_vaca=True)
        self.ma.opmode_sel = 0
        self.ma.pwrstate_sel = 1
        self.ma.current_sp = 0.0

    def tearDown(self):
        self.ma.finished()

    def test_setup(self):
        self.assertEqual(self.ma.opmode_sel, 0)
        self.assertEqual(self.ma.pwrstate_sel, 1)

    #test strength
    def test_set_strength(self):
        """ Test setting the strength attribute """
        self.ma.strength_sp = 0.1 #self.UPPER_STRENGTH_LIMIT
        self.assertEqual(self.ma.strength_sp, 0.1)#self.UPPER_STRENGTH_LIMIT)

    #test callbacks
    def test_strength_rb_callback(self):
        self.ma.strength_sp = 1.2
        self.assertEqual(self.ma.strength_rb, 1.2)

    def test_strengthref_mon_callback(self):
        self.ma.strength_sp = self.UPPER_STRENGTH_LIMIT
        self.assertEqualTimeout(self.UPPER_STRENGTH_LIMIT, self.ma, 'strengthref_mon', timeout=2.0)

    def test_strength_mon_callback(self):
        self.ma.strength_sp = self.UPPER_STRENGTH_LIMIT
        self.assertEqualTimeout(self.UPPER_STRENGTH_LIMIT, self.ma, 'strength_mon', timeout=2.0)

    def test_loop_set_strength(self):
        values = [1.5, 2.1, 2.6, 3.2, 4.3]

        for i in range(len(values)):
            self.ma.strength_sp = values[i]

        self.assertEqualTimeout(values[-1], self.ma, 'strength_sp', timeout=2.0)
        #self.assertEqualTimeout(2*values[-1], self.ma, 'current_sp', timeout=2.0)
        self.assertEqualTimeout(values[-1], self.ma, 'strength_rb', timeout=2.0)
        self.assertEqualTimeout(values[-1], self.ma, 'strengthref_mon', timeout=2.0)
        self.assertEqualTimeout(values[-1], self.ma, 'strength_mon', timeout=2.0)

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
