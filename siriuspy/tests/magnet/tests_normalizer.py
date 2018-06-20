#!/usr/bin/env python-sirius

"""Test DipoleNormalizer.

Requirements:
    convert current to strength
    convert strength to current
    all sections: TB, BO, TS, SI
"""
import unittest

from siriuspy.magnet.normalizer import DipoleNormalizer


class DipoleNormalizerTest(unittest.TestCase):
    """Test conversion of current/energy in dipoles."""

    settings = {
        "TB": {"name": "TB-Fam:MA-B",
               "current": 476.0,
               "strength": 0.14998905968836743},
        "BO": {"name": "BO-Fam:MA-B",
               "current": 981.778,
               "strength": 2.9999833123899702},
        "TS": {"name": "TS-Fam:MA-B",
               "current": 680.1,
               "strength": 3.0001213317838813},
        "SI": {"name": "SI-Fam:MA-B1B2",
               "current": 394.1,
               "strength": 3.0000383740663543}
    }

    def setUp(self):
        """Create strength object."""
        self.str_obj = {}
        for dipole, config in self.settings.items():
            self.str_obj[dipole] = DipoleNormalizer(config["name"])

    def _convert_current(self, dipole):
        strength = self.str_obj[dipole].conv_current_2_strength(
            self.settings[dipole]["current"])
        self.assertAlmostEqual(
            strength, self.settings[dipole]["strength"], places=7)

    def _convert_strength(self, dipole):
        current = self.str_obj[dipole].conv_strength_2_current(
            self.settings[dipole]["strength"])
        self.assertAlmostEqual(
            current, self.settings[dipole]["current"], places=7)

    def test_tb_current_conversion(self):
        """Test TB conversion of current to energy."""
        self._convert_current("TB")

    def _test_tb_strength_conversion(self):
        """Test TB conversion of energy to current."""
        self._convert_strength("TB")

    def _test_bo_current_conversion(self):
        """Test BO conversion of current to energy."""
        self._convert_current("BO")

    def _test_bo_strength_conversion(self):
        """Test BO conversion of energy to current."""
        self._convert_strength("BO")

    def _test_ts_current_conversion(self):
        """Test TS conversion of current to energy."""
        self._convert_current("TS")

    def _test_ts_strength_conversion(self):
        """Test TS conversion of energy to current."""
        self._convert_strength("TS")

    def _test_si_current_conversion(self):
        """Test SI conversion of current to energy."""
        self._convert_current("SI")

    def _test_si_strength_conversion(self):
        """Test SI conversion of energy to current."""
        self._convert_strength("SI")


if __name__ == "__main__":
    unittest.main()
