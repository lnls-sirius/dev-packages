#!/usr/bin/env python-sirius

"""Unittest module for factory.py."""

import unittest
from siriuspy.factory import MagnetFactory


class TestMagnetFactory(unittest.TestCase):
    """Test MagnetFactory."""

    def test_manames_getsplim(self):
        """Test get_pwrsupply_manames and getsplim."""
        maname = 'SI-Fam:MA-B1B2'
        magnet = MagnetFactory.factory(maname=maname,
                                       use_vaca=False,
                                       vaca_prefix=None, lock=False)
        self.assertEqual(magnet.maname, maname)


if __name__ == "__main__":
    unittest.main()
