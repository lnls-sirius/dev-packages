#!/usr/bin/env python3

import unittest
import time
import numpy
from siriuspy.magnet.model import MagnetPowerSupplyDipole, MagnetPowerSupply, MagnetPowerSupplyTrim

class MagnetPowerSupplyFamilyTest(unittest.TestCase):

    def setUp(self):
        dipole = MagnetPowerSupplyDipole("SI-Fam:MA-B1B2", use_vaca=True)
        dipole.current_sp = 394.0
        fam = MagnetPowerSupply("SI-Fam:MA-QDA", dipole, use_vaca=True)
        self.ma = MagnetPowerSupplyTrim("SI-01M1:MA-QDA", dipole, fam, use_vaca=True)

        self.ma.opmode_sel = 0
        self.ma.pwrstate_sel = 1

    def tearDown(self):
        self.ma.finished()

    def test_set_strength_sp(self):
        self.ma.strength_sp = -3.0
        self.assertEqualTimeout(-3.0, self.ma, 'strength_sp', 3.0)
        self.assertEqualTimeout(-3.0, self.ma, 'strength_rb', 3.0)
        self.assertEqualTimeout(-3.0, self.ma, 'strengthref_mon', 3.0)
        self.assertEqualTimeout(-3.0, self.ma, 'strength_mon', 3.0)

    def test_loop_set_strength(self):
        currents = numpy.linspace(0,120.0,101)
        strengths = [self.ma._conv_current_2_strength(current, self.ma._dipole.current_sp, self.ma._fam.current_sp) for current in currents]
        for strength in strengths:
            self.ma.strength_sp = strength
        self.assertEqualTimeout(strengths[-1], self.ma, 'strength_sp', timeout=2.0)
        self.assertEqualTimeout(strengths[-1], self.ma, 'strength_rb', timeout=2.0)
        self.assertEqualTimeout(strengths[-1], self.ma, 'strengthref_mon', timeout=2.0)
        self.assertEqualTimeout(strengths[-1], self.ma, 'strength_mon', timeout=2.0)
        self.assertEqualTimeout(currents[-1], self.ma, 'current_sp', timeout=2.0)

    def assertEqualTimeout(self, value, obj, attr, timeout):
        t0 = time.time();
        while (time.time() - t0 < timeout) and getattr(obj, attr) != value:
            pass
        self.assertEqual(getattr(obj, attr), value)

if __name__ == "__main__":
    unittest.main()
