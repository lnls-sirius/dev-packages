"""Test of pwrtsupply/controller module."""
import unittest
from unittest.mock import Mock

from siriuspy.util import check_public_interface_namespace
from siriuspy.pwrsupply.controller import PSController, InvalidValue
from db import bo_db


class TestPSController(unittest.TestCase):
    """Test PSController behaviour."""

    api = (
        'device',
        'setpoints',
        'pwrstate_sel',
        'opmode_sel',
        'current_sp',
        'reset_cmd',
        'read',
        'write',
        'read_all_variables',
    )

    def setUp(self):
        """Common setup for all tests."""
        self.device = Mock()
        self.device.database = bo_db
        self.controller = PSController(self.device)

    def test_api(self):
        """Test API."""
        self.assertTrue(
            check_public_interface_namespace(PSController, self.api))

    def test_device(self):
        """Test device property."""
        self.assertIsInstance(self.controller.device, Mock)

    def test_setpoints(self):
        """Test setpoints."""
        self.assertIn('PwrState-Sel', self.controller.setpoints)
        self.assertIn('OpMode-Sel', self.controller.setpoints)
        self.assertIn('Current-SP', self.controller.setpoints)

    def test_get_pwrstate_sel(self):
        """Test get pwrstate setpoint."""
        self.assertEqual(self.controller.pwrstate_sel, 0)

    def test_set_pwrstate_sel(self):
        """Test get pwrstate setpoint."""
        self.controller.pwrstate_sel = 1
        self.assertEqual(self.controller.pwrstate_sel, 1)

    def test_set_strange_value_pwrstate_sel(self):
        """Test set a strange value to pwrstate setpoint."""
        with self.assertRaises(InvalidValue):
            self.controller.pwrstate_sel = 2

    def test_get_opmode_sel(self):
        """Test getter of opmode_sel."""
        self.assertEqual(self.controller.opmode_sel, 0)

    def test_set_opmode_sel(self):
        """Test setter of opmode_sel."""
        self.controller.opmode_sel = 4
        self.assertEqual(self.controller.opmode_sel, 4)

    def test_set_opmode_sel_too_small(self):
        """Test setting invalid opmode."""
        with self.assertRaises(InvalidValue):
            self.controller.opmode_sel = -1

    def test_set_opmode_sel_too_big(self):
        """Test setting invalid opmode."""
        with self.assertRaises(InvalidValue):
            self.controller.opmode_sel = 10

    def test_get_current_sp(self):
        """Test current sp getter."""
        self.assertEqual(self.controller.current_sp, 0)

    def test_set_current_sp(self):
        """Test current sp setter."""
        self.controller.current_sp = 9.0
        self.assertEqual(self.controller.current_sp, 9.0)

    def test_set_current_sp_too_small(self):
        """Test current sp setter."""
        self.controller.current_sp = -10.0
        self.assertEqual(self.controller.current_sp, -9.0)

    def test_set_current_sp_too_big(self):
        """Test current sp setter."""
        self.controller.current_sp = 16.0
        self.assertEqual(self.controller.current_sp, 9.0)

    def test_reset_cmd(self):
        """Test reset cmd."""
        self.controller.reset_cmd = 0
        self.assertEqual(self.controller.reset_cmd, 0)
        self.controller.reset_cmd = 10
        self.assertEqual(self.controller.reset_cmd, 1)


if __name__ == '__main__':
    unittest.main()
