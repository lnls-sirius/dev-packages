#!/usr/bin/env python-sirius

"""Unittest module for computer.py."""

from unittest import TestCase
import siriuspy.util as util
import siriuspy.computer as computer


public_interface = (
    'Computer',
)


class TestComputer(TestCase):
    """Test computer module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(computer,
                                                      public_interface)
        self.assertTrue(valid)


class TestComputerClass(TestCase):
    """Test Computer Class."""

    public_interface = (
        'compute_update',
        'compute_put',
        'compute_limits',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            computer.Computer,
            TestComputerClass.public_interface)
        self.assertTrue(valid)

    def test_computer_update(self):
        """Test compute_update method."""
        c = computer.Computer()
        self.assertRaises(NotImplementedError, c.compute_update,
                          computed_pv=None,
                          updated_pv_name=None,
                          value=None)

    def test_computer_put(self):
        """Test compute_put method."""
        c = computer.Computer()
        self.assertRaises(NotImplementedError, c.compute_put,
                          computed_pv=None,
                          value=None)

    def test_computer_limits(self):
        """Test compute_put method."""
        c = computer.Computer()
        self.assertRaises(NotImplementedError, c.compute_limits,
                          computed_pv=None,)
