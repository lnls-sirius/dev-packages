#!/usr/bin/env python-sirius
"""Test public API of PowerSupply/Magnet class."""
import unittest
from unittest import mock

from siriuspy.pwrsupply.model import PowerSupply


class PowerSupplyTest(unittest.TestCase):
    """Tests."""

    def setUp(self):
        """Common setup for all test."""
        thread_patcher = mock.patch('siriuspy.pwrsupply.model._Thread')
        self.addCleanup(thread_patcher.stop)
        self.thread_mock = thread_patcher.start()
        self.controller = mock.Mock()
        # Set read return value to 'read'
        self.controller.read.return_value = 'read'

        self.ps = PowerSupply(
            psname='SI-Fam:PS-QDA', controller=self.controller)

    def test_read_sp(self):
        """Test read method."""
        self.assertEqual(self.ps.read('Current-SP'), 'read')

    def test_read_cte(self):
        """Test reading a cte."""
        self.assertEqual(len(self.ps.read('IntlkSoftLabels-Cte')), 32)

    def test_read_mon(self):
        """Test read a mon pv."""
        field = "Current-Mon"
        value = self.ps.read(field)
        self.assertEqual(value, 'read')
        self.controller.read.assert_called_with(field)

    def test_write(self):
        """Test write method."""
        field = 'Current-SP'
        value = 10.9
        self.ps.write(field, value)
        self.controller.write.assert_called_with(field, value)
        self.assertEqual(self.ps.read(field), value)

    def test_write_readable(self):
        """Test an exception is raised when trying to set a read-only field."""
        with self.assertRaises(KeyError):
            self.ps.write('Current-Mon', 10.0)

    def _test_set_callback(self):
        """Test set callback is called."""
        pass

    def _test_get_database(self):
        """Test database is returned."""
        pass


if __name__ == "__main__":
    unittest.main()
