#!/usr/bin/env python-sirius

"""Unittest module for factory.py."""

import unittest
from unittest import mock
import siriuspy.util as util
import siriuspy.factory as factory
from siriuspy.factory import NormalizerFactory
from siriuspy.magnet.normalizer \
    import DipoleNormalizer, MagnetNormalizer, TrimNormalizer


valid_interface = (
    'NormalizerFactory',
)


@mock.patch('siriuspy.factory._MAData', autospec=True)
class TestMagnetFactory(unittest.TestCase):
    """Test MagnetFactory."""

    def test_public_interface(self, mock_data):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(factory, valid_interface)
        self.assertTrue(valid)

    @mock.patch('siriuspy.factory._norm.DipoleNormalizer', autospec=True)
    def test_dipole_creation(self, mock_ma, mock_data):
        """Test Factory.create. dipole creation."""
        maname = 'SI-Fam:MA-B1B2'
        mock_data.return_value.magfunc.return_value = 'dipole'
        magnet = NormalizerFactory.create(maname=maname)
        self.assertIsInstance(magnet, DipoleNormalizer)

    @mock.patch('siriuspy.factory._norm.MagnetNormalizer', autospec=True)
    def test_magnet_creation(self, mock_ma, mock_data):
        """Test Factory.create magnet creation."""
        maname = 'SI-Fam:MA-QDA'
        mock_data.return_value.magfunc.return_value = 'quadrupole'
        magnet = NormalizerFactory.create(maname=maname)
        self.assertIsInstance(magnet, MagnetNormalizer)

    @mock.patch('siriuspy.factory._norm.MagnetNormalizer', autospec=True)
    def test_pulsed_magnet_creation(self, mock_ma, mock_data):
        """Test Factory.create magnet creation."""
        maname = 'SI-01SA:PM-InjDpKckr'
        mock_data.return_value.magfunc.return_value = 'corrector-vertical'
        magnet = NormalizerFactory.create(maname=maname)
        self.assertIsInstance(magnet, MagnetNormalizer)

    @mock.patch('siriuspy.factory._norm.TrimNormalizer', autospec=True)
    def test_trim_creation(self, mock_ma, mock_data):
        """Test Factory.create trim creation."""
        maname = 'SI-01M1:MA-QDA'
        mock_data.return_value.magfunc.return_value = 'quadrupole'
        magnet = NormalizerFactory.create(maname=maname)
        self.assertIsInstance(magnet, TrimNormalizer)


if __name__ == "__main__":
    unittest.main()
