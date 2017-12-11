#!/usr/bin/env python-sirius

"""Unittest module for factory.py."""

import unittest
from unittest import mock
import siriuspy.util as util
import siriuspy.factory as factory
from siriuspy.factory import MagnetFactory
from siriuspy.magnet.model import \
    MagnetPowerSupplyDipole, MagnetPowerSupply, MagnetPowerSupplyTrim


valid_interface = (
    'MagnetFactory',
)


class TestMagnetFactory(unittest.TestCase):
    """Test MagnetFactory."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(factory, valid_interface)
        self.assertTrue(valid)

    @mock.patch('siriuspy.factory._MagnetPowerSupplyDipole', autospec=True)
    def test_dipole_creation(self, mock_ma):
        """Test Factory.factory. dipole creation."""
        maname = 'SI-Fam:MA-B1B2'
        magnet = MagnetFactory.factory(maname=maname,
                                       use_vaca=False,
                                       vaca_prefix=None, lock=False)
        self.assertIsInstance(magnet, MagnetPowerSupplyDipole)

    @mock.patch('siriuspy.factory._MagnetPowerSupply', autospec=True)
    def test_magnet_creation(self, mock_ma):
        """Test Factory.factory magnet creation."""
        maname = 'SI-Fam:MA-QDA'
        magnet = MagnetFactory.factory(maname=maname,
                                       use_vaca=False,
                                       vaca_prefix=None, lock=False)
        self.assertIsInstance(magnet, MagnetPowerSupply)

    @mock.patch('siriuspy.factory._MagnetPowerSupplyTrim', autospec=True)
    def test_trim_creation(self, mock_ma):
        """Test Factory.factory. trim creation."""
        maname = 'SI-01M1:MA-QDA'
        magnet = MagnetFactory.factory(maname=maname,
                                       use_vaca=False,
                                       vaca_prefix=None, lock=False)
        self.assertIsInstance(magnet, MagnetPowerSupply)
        self.assertIsInstance(magnet, MagnetPowerSupplyTrim)


if __name__ == "__main__":
    unittest.main()
