#!/usr/bin/env python-sirius
"""Magnet class test module."""

import unittest
import siriuspy.search as _search


class TestMagnet(unittest.TestCase):
    """TestMagnet."""

    class Modules:
        """Modules class."""

        pass

    ps_manames = _search.MASearch.get_pwrsupply_manames()
    conv_maname_2_splims = _search.MASearch.conv_maname_2_splims

    def setUp(self):
        """Setup method."""
        import siriuspy.ramp.magnet as _mod
        self.modules = TestMagnet.Modules()
        self.modules.magnet = _mod

    def _test_constructor(self):
        """Test create magnets.

        - Create a magnet for each maname in MASearchs.get_manames().
        """
        for maname in TestMagnet.ps_manames:
            magnet = self.modules.magnet.Magnet(maname=maname)
            splims = TestMagnet.conv_maname_2_splims(maname)
            self.assertEqual(magnet.maname, maname)
            self.assertEqual(magnet.current_max, splims['DRVH'])
            self.assertEqual(magnet.current_min, splims['DRVL'])
            self.assertIn(magnet.dipole_name, (None,
                                               'SI-Fam:MA-B1B2',
                                               'BO-Fam:MA-B',
                                               'TB-Fam:MA-B',
                                               'TS-Fam:MA-B'))

    def test_conversions(self):
        """Test conversion current 2 strength."""
        for maname in TestMagnet.ps_manames:
            if 'MA' not in maname:
                print(maname)
                magnet = self.modules.magnet.Magnet(maname=maname)
                splims = TestMagnet.conv_maname_2_splims(maname)
                currents1 = list(splims.values())
                strengths = magnet.conv_current_2_strength(
                    currents1,
                    currents_dipole=10.0,
                    currents_family=10.0)
                currents2 = magnet.conv_strength_2_current(
                    strengths,
                    currents_dipole=10.0,
                    currents_family=10.0)
                for i in range(len(currents1)):
                    self.assertAlmostEqual(currents1[i], currents2[i])


if __name__ == "__main__":
    unittest.main()
