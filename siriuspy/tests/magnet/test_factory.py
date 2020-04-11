#!/usr/bin/env python-sirius

"""Unittest module for factory.py."""

from unittest import mock, TestCase
import siriuspy.util as util
import siriuspy.magnet.factory as factory
from siriuspy.magnet.factory import NormalizerFactory
from siriuspy.magnet.normalizer \
    import DipoleNormalizer, MagnetNormalizer, TrimNormalizer


PUB_INTERFACE = (
    'NormalizerFactory',
)


# @mock.patch('siriuspy.factory._MAData', autospec=True)
class TestMagnetFactory(TestCase):
    """Test MagnetFactory."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(factory, PUB_INTERFACE)
        self.assertTrue(valid)

    @mock.patch('siriuspy.magnet.factory._norm.DipoleNormalizer', autospec=True)
    def test_dipole_creation(self, mock_data):
        """Test Factory.create. dipole creation."""
        maname = 'SI-Fam:MA-B1B2'
        mock_data.return_value.magfunc.return_value = 'dipole'
        magnet = NormalizerFactory.create(maname=maname)
        self.assertIsInstance(magnet, DipoleNormalizer)

    @mock.patch('siriuspy.magnet.factory._norm.MagnetNormalizer', autospec=True)
    def test_magnet_creation(self, mock_data):
        """Test Factory.create magnet creation."""
        maname = 'SI-Fam:MA-QDA'
        mock_data.return_value.magfunc.return_value = 'quadrupole'
        magnet = NormalizerFactory.create(maname=maname)
        self.assertIsInstance(magnet, MagnetNormalizer)

    @mock.patch('siriuspy.magnet.factory._norm.MagnetNormalizer', autospec=True)
    def test_pulsed_magnet_creation(self, mock_data):
        """Test Factory.create magnet creation."""
        maname = 'SI-01SA:PM-InjDpKckr'
        mock_data.return_value.magfunc.return_value = 'corrector-vertical'
        magnet = NormalizerFactory.create(maname=maname)
        self.assertIsInstance(magnet, MagnetNormalizer)

    @mock.patch('siriuspy.magnet.factory._norm.TrimNormalizer', autospec=True)
    def test_trim_creation(self, mock_data):
        """Test Factory.create trim creation."""
        maname = 'SI-01M1:MA-QDA'
        mock_data.return_value.magfunc.return_value = 'quadrupole'
        magnet = NormalizerFactory.create(maname=maname)
        self.assertIsInstance(magnet, TrimNormalizer)
