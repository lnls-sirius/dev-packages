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
        pass

    def mysetUp(self):
        self.ma = MagnetPowerSupplyDipole("SI-Fam:MA-B1B2", use_vaca=True)
        self.ma.opmode_sel = _et.idx.SlowRef
        self.ma.pwrstate_sel = _et.idx.On
        self.ma.current_sp = 0.0
        self.ma.process_puts(wait=0.2); time.sleep(0.2)

    def tearDown(self):
        self.ma.disconnect()

    #test strength
    def test_set_strength(self):
        self.mysetUp()
        self.assertEqual(_et.idx.SlowRef, self.ma.opmode_sel)
        self.assertEqual(_et.idx.SlowRef, self.ma.opmode_sts)
        self.assertEqual(_et.idx.On, self.ma.pwrstate_sel)
        self.assertEqual(_et.idx.On, self.ma.pwrstate_sts)
        self.assertAlmostEqual(0.0, self.ma.current_sp)
        self.assertAlmostEqual(0.0, self.ma.current_rb)
        self.assertAlmostEqual(0.0, self.ma.currentref_mon)
        self.assertAlmostEqual(0.0, self.ma.current_mon)
        self.assertEqual(1.1562121579074833, self.ma.strength_sp)
        self.assertEqual(1.1562121579074833, self.ma.strength_rb)
        self.assertEqual(1.1562121579074833, self.ma.strengthref_mon)
        self.assertEqual(1.1562121579074833, self.ma.strength_mon)

        """ Test setting the strength attribute """
        self.ma.strength_sp = 0.101
        self.assertAlmostEqual(0.101, self.ma.strength_sp)

    #test callbacks
    def test_strength_rb_callback(self):
        self.mysetUp()
        self.ma.strength_sp = 1.2
        self.ma.process_puts(wait=0.2); time.sleep(0.2)
        self.assertAlmostEqual(1.2, self.ma.strength_rb, places=12)

    def test_strengthref_mon_callback(self):
        self.mysetUp()
        self.ma.strength_sp = 1.3
        self.ma.process_puts(wait=0.2); time.sleep(0.2)
        self.assertAlmostEqual(1.3, self.ma.strengthref_mon, places=12)

    def test_strength_mon_callback(self):
        self.mysetUp()
        self.ma.strength_sp = 1.4
        self.ma.process_puts(wait=0.2); time.sleep(0.2)
        self.assertAlmostEqual(1.4, self.ma.strength_mon, places=12)

    def test_loop_set_strength(self):
        self.mysetUp()
        currents = numpy.linspace(0, 120.0, 101)
        strengths = [self.ma.conv_current_2_strength(current)
                     for current in currents]
        for strength in strengths:
            self.ma.strength_sp = strength
            #time.sleep(0.01)
        self.ma.process_puts(wait=0.2); time.sleep(0.2)
        self.assertAlmostEqual(strengths[-1], self.ma.strength_sp, places=12)
        self.assertAlmostEqual(strengths[-1], self.ma.strength_rb, places=12)
        self.assertAlmostEqual(strengths[-1], self.ma.strengthref_mon, places=12)
        self.assertAlmostEqual(strengths[-1], self.ma.strength_mon, places=12)
        self.assertAlmostEqual(currents[-1], self.ma.current_sp, places=12)


if __name__ == "__main__":
    unittest.main()
