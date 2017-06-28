#!/usr/bin/env python3
"""Test of the MagnetPowerSupply class."""

import unittest
import time
import numpy
from siriuspy.magnet.model import MagnetPowerSupplyDipole, MagnetPowerSupply


class MagnetPowerSupplyFamilyTest(unittest.TestCase):
    """Test MagnetPowerSupply class.

    Test setting the strength.
    Test setting the strength repeatedly.
    Test changing the dipole current.
    Test changing the dipole strength.
    """

    def setUp(self):
        """Execute before every test."""
        self.dipole = MagnetPowerSupplyDipole("SI-Fam:MA-B1B2", use_vaca=True)
        self.dipole.current_sp = 394.0
        self.ma = MagnetPowerSupply(
           "SI-Fam:MA-QDA", self.dipole, use_vaca=True)

        self.dipole.opmode_sel = 0
        self.dipole.pwrstate_sel = 1

        self.ma.opmode_sel = 0
        self.ma.pwrstate_sel = 1

    def tearDown(self):
        """Execute after every test."""
        self.ma.disconnect()
        self.dipole.disconnect()

    def test_set_strength_sp(self):
        """Test setting strength set point."""
        self.ma.strength_sp = -3.0
        self.assertEqualTimeout(-3.0, self.ma, 'strength_sp', 2.0)
        self.assertEqualTimeout(-3.0, self.ma, 'strength_rb', 2.0)
        self.assertEqualTimeout(-3.0, self.ma, 'strengthref_mon', 2.0)
        self.assertEqualTimeout(-3.0, self.ma, 'strength_mon', 2.0)

    def test_loop_set_strength(self):
        """Test setting strength set point repeatedly."""
        timeout = 2.0
        currents = numpy.linspace(0, 120.0, 100)
        strengths = [self.ma._conv_current_2_strength(
            current, self.ma._dipole.current_sp) for current in currents]
        for strength in strengths:
            time.sleep(0.01)
            self.ma.strength_sp = strength
        self.assertEqualTimeout(
            strengths[-1], self.ma, 'strength_sp', timeout=timeout)
        self.assertEqualTimeout(
            strengths[-1], self.ma, 'strengthref_mon', timeout=timeout)
        self.assertEqualTimeout(
            strengths[-1], self.ma, 'strength_mon', timeout=timeout)
        self.assertEqualTimeout(
            strengths[-1], self.ma, 'strength_rb', timeout=timeout)
        self.assertEqualTimeout(
            currents[-1], self.ma, 'current_sp', timeout=timeout)

    def test_change_dipole_current(self):
        """Change dipole current and assert magnet strength is set properly."""
        sp = self.ma.strength_sp
        self.dipole.current_sp = 400
        self.assertEqualTimeout(400, self.dipole, 'current_sp', 2.0)
        expected_strength = \
            self.ma._conv_current_2_strength(self.ma.current_sp, 400)
        self.assertEqualTimeout(
            sp, self.ma, 'strength_sp', 3.0)
        self.assertEqualTimeout(
            expected_strength, self.ma, 'strength_rb', 2.0)
        self.assertEqualTimeout(
            expected_strength, self.ma, 'strengthref_mon', 2.0)
        self.assertEqualTimeout(
            expected_strength, self.ma, 'strength_mon', 2.0)

    def test_change_dipole_strength(self):
        """Change dipole energy and assert magnet strength is set properly."""
        sp = self.ma.strength_sp
        self.dipole.strength_sp = 2.0
        self.assertEqualTimeout(2.0, self.dipole, 'strength_sp', 2.0)
        expected_strength = self.ma._conv_current_2_strength(
            self.ma.current_sp, self.dipole.current_sp)
        self.assertEqualTimeout(
            sp, self.ma, 'strength_sp', 2.0)
        self.assertEqualTimeout(
            expected_strength, self.ma, 'strength_rb', 2.0)
        self.assertEqualTimeout(
            expected_strength, self.ma, 'strengthref_mon', 2.0)
        self.assertEqualTimeout(
            expected_strength, self.ma, 'strength_mon', 2.0)

    def assertEqualTimeout(self, value, obj, attr, timeout):
        """Wait timeout and assert if obj attribute is set to the value."""
        t0 = time.time()
        while (time.time() - t0 < timeout) and getattr(obj, attr) != value:
            pass
        self.assertEqual(getattr(obj, attr), value)


if __name__ == "__main__":
    unittest.main()
