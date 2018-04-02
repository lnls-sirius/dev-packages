#!/usr/bin/env python-sirius
"""Test public API of PowerSupply/Magnet class."""
import unittest
from unittest.mock import Mock

from siriuspy.pwrsupply.model import PowerSupply
from siriuspy.util import check_public_interface_namespace
from variables import bsmp_values, dict_values


class TestPowerSupply(unittest.TestCase):
    """Test PowerSupply class."""

    api = (
        'bsmp',
        'database',
        'pwrstate_sts',
        'opmode_sts',
        'current_rb',
        'currentref_mon',
        'current_mon',
        'intlksoft_mon',
        'intlkhard_mon',
        'read_group',
        'create_group',
        'read_all_variables',
        'turn_on',
        'turn_off',
        'select_op_mode',
        'set_slowref',
        'reset_interlocks',
    )

    def setUp(self):
        """Common setup for all tests."""
        self.serial = Mock()
        self.serial.UART_read.return_value = \
            ['\x00', '\x13', '\x00', '\x02', '\x03', '\x00', 'è']
        self.ps = PowerSupply(self.serial, 1)

    def test_api(self):
        """Test API."""
        self.assertTrue(
            check_public_interface_namespace(PowerSupply, self.api))

    def test_pwrstate_sts_off(self):
        """Test pwrstate sts."""
        # Off - Off
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x00', '\x00', 'í']
        self.assertEqual(self.ps.pwrstate_sts, 0)

    def test_pwrstate_sts_interlock(self):
        """Test pwrstate sts."""
        # Interlock - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x01', '\x00', 'ì']
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_initializing(self):
        """Test pwrstate sts."""
        # Initializing - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x02', '\x00', 'ë']
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_slowref(self):
        """Test pwrstate sts."""
        # SlowRef - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x03', '\x00', 'ê']
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_slowrefsync(self):
        """Test pwrstate sts."""
        # SlowRefSync - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x04', '\x00', 'é']
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_cycle(self):
        """Test pwrstate sts."""
        # Cycle - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x05', '\x00', 'è']
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_rmpwfm(self):
        """Test pwrstate sts."""
        # RmpWfm - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x06', '\x00', 'ç']
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_migwfm(self):
        """Test pwrstate sts."""
        # MigWfm - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x07', '\x00', 'æ']
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_fastref(self):
        """Test pwrstate sts."""
        # FastRef - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x08', '\x00', 'å']
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_opmode_sts_off(self):
        """Test opmode_sts."""
        # Off - SlowRef
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x00', '\x00', 'í']
        self.assertEqual(self.ps.opmode_sts, 0)

    def test_opmode_sts_interlock(self):
        """Test opmode sts."""
        # Interlock - SlowRef
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x01', '\x00', 'ì']
        self.assertEqual(self.ps.opmode_sts, 0)

    def test_opmode_sts_initializing(self):
        """Test opmode sts."""
        # Initializing - SlowRef
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x02', '\x00', 'ë']
        self.assertEqual(self.ps.opmode_sts, 0)

    def test_opmode_sts_slowref(self):
        """Test opmode sts."""
        # SlowRef
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x03', '\x00', 'ê']
        self.assertEqual(self.ps.opmode_sts, 0)

    def test_opmode_sts_slowrefsync(self):
        """Test opmode sts."""
        # SlowRefSync
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x04', '\x00', 'é']
        self.assertEqual(self.ps.opmode_sts, 1)

    def test_opmode_sts_cycle(self):
        """Test opmode sts."""
        # Cycle - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x05', '\x00', 'è']
        self.assertEqual(self.ps.opmode_sts, 2)

    def test_opmode_sts_rmpwfm(self):
        """Test opmode sts."""
        # RmpWfm - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x06', '\x00', 'ç']
        self.assertEqual(self.ps.opmode_sts, 3)

    def test_opmode_sts_migwfm(self):
        """Test opmode sts."""
        # MigWfm - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x07', '\x00', 'æ']
        self.assertEqual(self.ps.opmode_sts, 4)

    def test_opmode_sts_fastref(self):
        """Test opmode sts."""
        # FastRef - On
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x02', '\x08', '\x00', 'å']
        self.assertEqual(self.ps.opmode_sts, 5)

    def test_current_rb(self):
        """Test curren rb."""
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x04', '\x00', '\x00', '(', 'A', '\x82']
        self.assertEqual(self.ps.current_rb, 10.5)

    def test_currentref_mon(self):
        """Test currenref mon."""
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x04', '\x00', '\x00', '(', 'A', '\x82']
        self.assertEqual(self.ps.currentref_mon, 10.5)

    def test_current_mon(self):
        """Test curren mon."""
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x04', '\x00', '\x00', '(', 'A', '\x82']
        self.assertEqual(self.ps.current_mon, 10.5)

    def test_intlksoft_mon(self):
        """Test intlsoft_mon."""
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x04', 'Þ', '\x04', '\x00', '\x00', '\t']
        self.assertEqual(self.ps.intlksoft_mon, 1246)

    def test_intlkhard_mon(self):
        """Test intlkhard_mon."""
        self.serial.UART_read.return_value = \
            ['\x00', '\x11', '\x00', '\x04', 'Þ', '\x04', '\x00', '\x00', '\t']
        self.assertEqual(self.ps.intlkhard_mon, 1246)

    def test_read_group(self):
        """Test read group creation."""
        # Tested in test_read_all_variables
        pass

    def test_create_group(self):
        """Test the creation of groups from fields."""
        with self.assertRaises(NotImplementedError):
            self.ps.create_group(['PwrState-Sts', 'OpMode-Sts', 'Current-RB'])

    def test_read_all_variables(self):
        """Test reading from group 0."""
        self.serial.UART_read.return_value = bsmp_values
        self.assertEqual(self.ps.read_all_variables(), dict_values)

    def test_turn_on(self):
        """Test turn on function."""
        self.serial.UART_read.return_value = \
            ['\x00', 'Q', '\x00', '\x01', 'à', 'Î']
        self.assertTrue(self.ps.turn_on())

    def test_turn_on_error(self):
        """Test turn on function when an error occurs."""
        self.serial.UART_read.return_value = \
            ['\x00', 'S', '\x00', '\x00', '\xad']
        self.assertFalse(self.ps.turn_on())

    def test_turn_off(self):
        """Test turn off function."""
        self.serial.UART_read.return_value = \
            ['\x00', 'Q', '\x00', '\x01', 'à', 'Î']
        self.assertTrue(self.ps.turn_off())

    def test_turn_off_error(self):
        """Test turn off function when it return error."""
        self.serial.UART_read.return_value = \
            ['\x00', 'S', '\x00', '\x00', '\xad']
        self.assertFalse(self.ps.turn_off())

    def test_select_op_mode(self):
        """Test select op mode."""
        self.serial.UART_read.return_value = \
            ['\x00', 'Q', '\x00', '\x01', 'à', 'Î']
        self.assertTrue(self.ps.select_op_mode(1))

    def test_select_op_mode_error(self):
        """Test select op mode when error occurs."""
        self.serial.UART_read.return_value = \
            ['\x00', 'S', '\x00', '\x00', '\xad']
        self.assertFalse(self.ps.select_op_mode(1))

    def test_reset_interlocks(self):
        """Test reset_interlocks."""
        self.serial.UART_read.return_value = \
            ['\x00', 'Q', '\x00', '\x01', 'à', 'Î']
        self.assertTrue(self.ps.reset_interlocks())

    def test_reset_interlocks_error(self):
        """Test reset_interlocks when error occurs."""
        self.serial.UART_read.return_value = \
            ['\x00', 'S', '\x00', '\x00', '\xad']
        self.assertFalse(self.ps.reset_interlocks())

    def test_set_slowref(self):
        """Test set_slowref."""
        self.serial.UART_read.return_value = \
            ['\x00', 'Q', '\x00', '\x01', 'à', 'Î']
        self.assertTrue(self.ps.set_slowref(1.0))

    def test_set_slowref_error(self):
        """Test set_slowref when error occurs."""
        self.serial.UART_read.return_value = \
            ['\x00', 'S', '\x00', '\x00', '\xad']
        self.assertFalse(self.ps.set_slowref(1.0))


class TestPowerSupplySim(unittest.TestCase):
    """Test simulated PowerSupplySim class."""

    pass


if __name__ == "__main__":
    unittest.main()
