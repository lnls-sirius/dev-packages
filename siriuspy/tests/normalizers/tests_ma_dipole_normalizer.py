"""Test DipoleNormalizer.

Requirements:
    convert current to strength
    convert strength to current
    all sections: TB, BO, TS, SI
"""
import unittest

from siriuspy.magnet.model import DipoleNormalizer


class DipoleNormalizerTest(unittest.TestCase):
    """Test conversion of current/energy in dipoles."""

    settings = {
        "TB": {"name": "TB-Fam:MA-B",
               "current": 476.0,
               "strength": 0.15},
        "BO": {"name": "BO-Fam:MA-B",
               "current": 981.778,
               "strength": 3.0},
        "TS": {"name": "TS-Fam:MA-B",
               "current": 680.1,
               "strength": 3.0},
        "SI": {"name": "SI-Fam:MA-B1B2",
               "current": 394.1,
               "strength": 3.0}
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

    def test_tb_strength_conversion(self):
        """Test TB conversion of energy to current."""
        self._convert_strength("TB")

    def test_bo_current_conversion(self):
        """Test BO conversion of current to energy."""
        self._convert_current("BO")

    def test_bo_strength_conversion(self):
        """Test BO conversion of energy to current."""
        self._convert_strength("BO")

    def test_ts_current_conversion(self):
        """Test TS conversion of current to energy."""
        self._convert_current("TS")

    def test_ts_strength_conversion(self):
        """Test TS conversion of energy to current."""
        self._convert_strength("TS")

    def test_si_current_conversion(self):
        """Test SI conversion of current to energy."""
        self._convert_current("SI")

    def test_si_strength_conversion(self):
        """Test SI conversion of energy to current."""
        self._convert_strength("SI")


if __name__ == "__main__":
    unittest.main()
