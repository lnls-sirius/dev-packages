#!/usr/bin/env python3
"""Test of the MagnetPowerSupply class."""

import unittest
import time
import numpy
from siriuspy.magnet.model import MagnetPowerSupplyDipole, MagnetPowerSupply, \
    MagnetPowerSupplyTrim


class MagnetPowerSupplyTrimTest(unittest.TestCase):
    """Test MagnetPowerSupplyTrim class.

    Test setting the strength.
    Test setting the strength repeatedly.
    Test changing the dipole current.
    Test changing the dipole strength.
    Test changing the family current.
    Test changing the family strength.
    """

    def setUp(self):
        """Execute before every test."""
        self.dipole = MagnetPowerSupplyDipole("SI-Fam:MA-B1B2", use_vaca=True)
        self.dipole.current_sp = 394.0
        self.fam = MagnetPowerSupply(
            "SI-Fam:MA-QDA", self.dipole, use_vaca=True)
        self.fam.strength_sp = 0.0
        self.ma = MagnetPowerSupplyTrim(
            "SI-01M1:MA-QDA", self.dipole, self.fam, use_vaca=True)

        self.dipole.opmode_sel = 0
        self.dipole.pwrstate_sel = 1

        self.fam.opmode_sel = 0
        self.fam.pwrstate_sel = 1

        self.ma.opmode_sel = 0
        self.ma.pwrstate_sel = 1
        time.sleep(0.6)

    def tearDown(self):
        """Execute after every test."""
        self.ma.disconnect()
        self.fam.disconnect()
        self.dipole.disconnect()

    def test_set_strength_sp(self):
        """Test setting strength set point."""
        #fam_strength = -3.0
        trim_strength = 0.25
        #self.fam.strength_sp = fam_strength
        self.ma.strength_sp = trim_strength
        self.assertEqual(trim_strength, self.ma.strength_sp)
        time.sleep(0.2)
        self.assertEqual(trim_strength, self.ma.strength_rb)
        self.assertEqual(trim_strength, self.ma.strengthref_mon)
        self.assertEqual(trim_strength, self.ma.strength_mon)

    # def test_loop_set_strength(self):
    #     """Test setting strength set point repeatedly."""
    #     currents = numpy.linspace(0, 10.0, 101)
    #     strengths = [self.ma._conv_current_2_strength(current,
    #                  self.ma._dipole.current_sp, self.ma._fam.current_sp)
    #                  for current in currents]
    #     for strength in strengths:
    #         self.ma.strength_sp = strength
    #         time.sleep(0.01)
    #     self.assertEqualTimeout(
    #         strengths[-1], self.ma, 'strength_sp', timeout=2.0)
    #     self.assertEqualTimeout(
    #         strengths[-1], self.ma, 'strength_rb', timeout=2.0)
    #     self.assertEqualTimeout(
    #         strengths[-1], self.ma, 'strengthref_mon', timeout=2.0)
    #     self.assertEqualTimeout(
    #         strengths[-1], self.ma, 'strength_mon', timeout=2.0)
    #     self.assertEqualTimeout(
    #         currents[-1], self.ma, 'current_sp', timeout=2.0)
    #
    # def test_change_dipole_current(self):
    #     """Change dipole current and assert magnet strength is set properly."""
    #     sp = self.ma.strength_sp
    #     self.dipole.current_sp = 400
    #     self.assertEqualTimeout(400, self.dipole, 'current_sp', 2.0)
    #     expected_strength = \
    #         self.ma._conv_current_2_strength(
    #             self.ma.current_sp, 400, self.fam.current_sp)
    #     self.assertEqualTimeout(
    #         sp, self.ma, 'strength_sp', 3.0)
    #     self.assertEqualTimeout(
    #         expected_strength, self.ma, 'strength_rb', 2.0)
    #     self.assertEqualTimeout(
    #         expected_strength, self.ma, 'strengthref_mon', 2.0)
    #     self.assertEqualTimeout(
    #         expected_strength, self.ma, 'strength_mon', 2.0)
    #
    # def test_change_dipole_strength(self):
    #     """Change dipole energy and assert magnet strength is set properly."""
    #     sp = self.ma.strength_sp
    #     self.dipole.strength_sp = 2.0
    #     self.assertEqualTimeout(2.0, self.dipole, 'strength_sp', 2.0)
    #     expected_strength = self.ma._conv_current_2_strength(
    #         self.ma.current_sp, self.dipole.current_sp, self.fam.current_sp)
    #     self.assertEqualTimeout(
    #         sp, self.ma, 'strength_sp', 2.0)
    #     self.assertEqualTimeout(
    #         expected_strength, self.ma, 'strength_rb', 2.0)
    #     self.assertEqualTimeout(
    #         expected_strength, self.ma, 'strengthref_mon', 2.0)
    #     self.assertEqualTimeout(
    #         expected_strength, self.ma, 'strength_mon', 2.0)
    #
    # def test_change_family_current(self):
    #     """Change fam current and assert magnet strength is set properly."""
    #     self.ma.current_sp = 5
    #     self.fam.current_sp = -20.0
    #     self.assertEqualTimeout(-20.0, self.fam, 'current_sp', 2.0)
    #     time.sleep(0.5)
    #     sp_1 = self.ma.strength_mon
    #     self.fam.current_sp = -40.0
    #     self.assertEqualTimeout(-40.0, self.fam, 'current_sp', 2.0)
    #     time.sleep(0.5)
    #     sp_2 = self.ma.strength_mon
    #     self.assertNotEqual(sp_1, sp_2)
    #
    # def test_change_family_strength(self):
    #     """Change fam strength and assert magnet strength is set properly."""
    #     self.ma.current_sp = 5
    #     self.fam.current_sp = 0.0
    #     self.assertEqualTimeout(0.0, self.fam, 'current_sp', 2.0)
    #     time.sleep(0.5)
    #     sp = self.ma.strength_mon
    #     self.fam.strength_sp = -1.5
    #     self.assertEqualTimeout(-1.5, self.fam, 'strength_mon', 2.0)
    #     self.assertEqualTimeout(-1.5 + sp, self.ma, 'strength_rb', 2.0)
    #     self.assertEqualTimeout(-1.5 + sp, self.ma, 'strengthref_mon', 2.0)
    #     self.assertEqualTimeout(-1.5 + sp, self.ma, 'strength_mon', 2.0)

    def assertEqualTimeout(self, value, obj, attr, timeout):
        """Wait timeout and assert if obj attribute is set to the value."""
        t0 = time.time()
        while (time.time() - t0 < timeout) and getattr(obj, attr) != value:
            pass
        self.assertEqual(getattr(obj, attr), value)


if __name__ == "__main__":
    unittest.main()
