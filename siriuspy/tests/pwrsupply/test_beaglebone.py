#!/usr/bin/env python-sirius
"""Test beaglebone module."""
import unittest

from siriuspy import util
import siriuspy.pwrsupply.beaglebone as bbb
from siriuspy.util import check_public_interface_namespace


public_interface = (
    'BeagleBone',
)


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                bbb,
                public_interface)
        self.assertTrue(valid)


class TestBeagleBone(unittest.TestCase):
    """Test PRUInterface API."""

    public_interface = (
        'psnames',
        'devices_database',
        'pru_controller',
        'e2s_controller',
        'read',
        'write',
        'check_connected',
    )

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(check_public_interface_namespace(
            bbb.BeagleBone, TestBeagleBone.public_interface))

    def test_psnames(self):
        """Test psnames."""
        # TODO: implement test!
        pass

    def test_pru_controller(self):
        """Test pru_controller."""
        # TODO: implement test!
        pass

    def test_e2s_controller(self):
        """Test e2s_controller."""
        # TODO: implement test!
        pass

    def test_read(self):
        """Test read."""
        # TODO: implement test!
        pass

    def test_write(self):
        """Test write."""
        # TODO: implement test!
        pass

    def test_check_connected(self):
        """Test check_connected."""
        # TODO: implement test!
        pass


if __name__ == "__main__":
    unittest.main()
