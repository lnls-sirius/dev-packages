#!/usr/bin/env python-sirius
"""Test public API of PowerSupply/Magnet class."""
import unittest
from unittest import mock

from siriuspy.pwrsupply.model import PowerSupply
from siriuspy.util import check_public_interface_namespace


class TestPowerSupplyAPI(unittest.TestCase):
    """Test PowerSupply class."""

    api = (
        'controller',
        'pwrstate_sts',
        'opmode_sts',
        'current_rb',
        'currentref_mon',
        'cycleenbl_mon',
        'cycletype_sts',
        'cyclenrcycles_rb',
        'cycleindex_mon',
        'cyclefreq_rb',
        'cycleampl_rb',
        'cycleoffset_rb',
        'cycleauxparam_rb',
        'intlksoft_mon',
        'intlkhard_mon',
        'current_mon',
        'read_group',
        'create_group',
        'read_all_variables',
        'turn_on',
        'turn_off',
        'select_op_mode',
        'set_slowref',
        'cfg_siggen',
        'set_siggen',
        'enable_siggen',
        'disable_siggen',
        'reset_interlocks',
    )

    def test_api(self):
        """Test API."""
        self.assertTrue(
            check_public_interface_namespace(PowerSupply, self.api))


class TestPowerSupply(unittest.TestCase):
    """Test power supply.

    Test methods read_variable, execute_function and method that read and parse
    the BSMP `ps_state` variable.
    """

    def setUp(self):
        """Common setup for all tests."""
        self.controller = mock.Mock()
        self.ps = PowerSupply(self.controller)

    def test_read_variable(self):
        """Test read variable method."""
        self.controller.read_variable.return_value = (0xE0, 10.5)
        self.assertEqual(self.ps._read_variable(1), 10.5)

    def test_read_variable_error(self):
        """Test read_variable return None on BSMP error code."""
        self.controller.read_variable.return_value = (0xE8, None)
        self.assertIsNone(self.ps._read_variable(1))

    def test_execute_function(self):
        """Test execute function returns true on success."""
        self.controller.execute_function.return_value = (0xE0, None)
        self.assertTrue(self.ps._execute_function(1))

    def test_execute_function_error(self):
        """Test execute function returns true on success."""
        self.controller.execute_function.return_value = (0xE3, None)
        self.assertFalse(self.ps._execute_function(1))

    def test_pwrstate_sts_off(self):
        """Test pwrstate sts."""
        # Off - Off
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000000)
        self.assertEqual(self.ps.pwrstate_sts, 0)
        self.controller.read_variable.return_value = (0xE0, 0b1111111111110000)
        self.assertEqual(self.ps.pwrstate_sts, 0)

    def test_pwrstate_sts_interlock(self):
        """Test pwrstate sts."""
        # Interlock - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000001)
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_initializing(self):
        """Test pwrstate sts."""
        # Initializing - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000010)
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_slowref(self):
        """Test pwrstate sts."""
        # SlowRef - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000011)
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_slowrefsync(self):
        """Test pwrstate sts."""
        # SlowRefSync - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000100)
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_cycle(self):
        """Test pwrstate sts."""
        # Cycle - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000101)
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_rmpwfm(self):
        """Test pwrstate sts."""
        # RmpWfm - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000110)
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_migwfm(self):
        """Test pwrstate sts."""
        # MigWfm - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000111)
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_pwrstate_sts_fastref(self):
        """Test pwrstate sts."""
        # FastRef - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000001000)
        self.assertEqual(self.ps.pwrstate_sts, 1)

    def test_opmode_sts_off(self):
        """Test opmode_sts."""
        # Off - SlowRef
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000000)
        self.assertEqual(self.ps.opmode_sts, 0)

    def test_opmode_sts_interlock(self):
        """Test opmode sts."""
        # Interlock - SlowRef
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000001)
        self.assertEqual(self.ps.opmode_sts, 0)

    def test_opmode_sts_initializing(self):
        """Test opmode sts."""
        # Initializing - SlowRef
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000010)
        self.assertEqual(self.ps.opmode_sts, 0)

    def test_opmode_sts_slowref(self):
        """Test opmode sts."""
        # SlowRef
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000011)
        self.assertEqual(self.ps.opmode_sts, 0)

    def test_opmode_sts_slowrefsync(self):
        """Test opmode sts."""
        # SlowRefSync
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000100)
        self.assertEqual(self.ps.opmode_sts, 1)

    def test_opmode_sts_cycle(self):
        """Test opmode sts."""
        # Cycle - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000101)
        self.assertEqual(self.ps.opmode_sts, 2)

    def test_opmode_sts_rmpwfm(self):
        """Test opmode sts."""
        # RmpWfm - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000110)
        self.assertEqual(self.ps.opmode_sts, 3)

    def test_opmode_sts_migwfm(self):
        """Test opmode sts."""
        # MigWfm - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000000111)
        self.assertEqual(self.ps.opmode_sts, 4)

    def test_opmode_sts_fastref(self):
        """Test opmode sts."""
        # FastRef - On
        self.controller.read_variable.return_value = (0xE0, 0b0000000000001000)
        self.assertEqual(self.ps.opmode_sts, 5)

    def test_read_group(self):
        """Test read group creation."""
        """Test reading from group -1."""
        variables = [0, 3, 6, 7]
        values = [0b0000000000000110,
                  [b't', b'e', b's', b't', b'e', b'\x00', b'\x00', b'\x00'],
                  0, 0]
        self.controller.read_group_variables.return_value = (0xE0, values)
        self.controller.entities.list_variables.return_value = variables
        self.assertEqual(self.ps.read_group(3), {
            'PwrState-Sts': 1,
            'OpMode-Sts': 3,
            'Version-Cte': 'teste',
            'CycleEnbl-Mon': values[2],
            'CycleType-Sts': values[3]})

    def test_create_group_return_true(self):
        """Test create group return true."""
        self.controller.create_group.return_value = (0xE0, None)
        self.assertTrue(self.ps.create_group(['CurrentRef-Mon']))

    def test_create_group(self):
        """Test correct stream is sent."""
        # Create group with currents
        self.controller.create_group.return_value = (0xE0, None)
        self.ps.create_group(['CurrentRef-Mon', 'Current-Mon', 'Current-RB'])
        self.controller.create_group.assert_called_with({1, 2, 27})

    def test_create_group_field_with_same_id(self):
        """Test creating group with fields that have same id."""
        # Create group with 2 field that map to the same id
        self.controller.create_group.return_value = (0xE0, None)
        self.ps.create_group(['PwrState-Sts', 'OpMode-Sts'])
        self.controller.create_group.assert_called_with({0})

    def test_create_group_error(self):
        """Test create_group returns false when error occurs."""
        self.controller.create_group.return_value = (0xE3, None)
        self.assertFalse(self.ps.create_group(['CurrentRef-Mon']))

    def test_turn_on_delay(self):
        """Test turn on is executed correctly."""


class TestPowerSupplyFunctions(unittest.TestCase):
    """Test functions."""

    def setUp(self):
        """Controller execute_function returns ok."""
        self.controller = mock.Mock()
        self.controller.execute_function.return_value = (0xE0, None)
        # Mock alias
        self.ef = self.controller.execute_function
        self.ps = PowerSupply(self.controller)

    def test_turn_on(self):
        """Test turn on function is called."""
        self.ps.turn_on()
        self.controller.execute_function.assert_any_call(0, None)

    def test_turn_on_closes_loop(self):
        """Test turn on calls method to close ps control loop."""
        self.ps.turn_on()
        self.controller.execute_function.assert_called_with(3, None)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_turn_on_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.ps.turn_on()
        time.sleep.assert_called_with(0.3)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_turn_on_error_no_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.controller.execute_function.return_value = (0xE3, None)
        self.ps.turn_on()
        time.sleep.assert_not_called()

    def test_turn_off(self):
        """Test turn off."""
        self.ps.turn_off()
        self.controller.execute_function.assert_called_with(1, None)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_turn_off_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.ps.turn_off()
        time.sleep.assert_called_with(0.3)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_turn_off_on_error_no_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.controller.execute_function.return_value = (0xE3, None)
        self.ps.turn_off()
        time.sleep.assert_not_called()

    def test_select_op_mode(self):
        """Test select op mode called correctly."""
        self.ps.select_op_mode(0)
        self.controller.execute_function.assert_called_with(4, 3)

    def test_reset_interlocks(self):
        """Test reset interlock is called correctly."""
        self.ps.reset_interlocks()
        self.controller.execute_function.assert_called_with(6, None)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_reset_interlock_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.ps.reset_interlocks()
        time.sleep.assert_called_with(0.1)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_reset_interlocks_on_error_no_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.controller.execute_function.return_value = (0xE3, None)
        self.ps.reset_interlocks()
        time.sleep.assert_not_called()

    def test_set_slowref(self):
        """Test set slowred is called correctly."""
        self.ps.set_slowref(15.5)
        self.controller.execute_function.assert_called_with(16, 15.5)

    def test_cfg_siggen(self):
        """Test cfg_siggen is called correctly."""
        self.ps.cfg_siggen(0, 0, 1.0, 1.0, 1.0, [0.0, 0.0, 0.0, 0.0])
        self.controller.execute_function.assert_called_with(
            23, [0, 0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0])

    def test_set_siggen(self):
        """Test set_siggen is called correctly."""
        self.ps.set_siggen(1.0, 1.0, 1.0)
        self.controller.execute_function.assert_called_with(
            24, [1.0, 1.0, 1.0])

    def test_enable_siggen(self):
        """Test enable_siggen is called correctly."""
        self.ps.enable_siggen()
        self.controller.execute_function.assert_called_with(25, None)

    def test_disable_siggen(self):
        """Test disable_siggen is called correctly."""
        self.ps.disable_siggen()
        self.controller.execute_function.assert_called_with(26, None)


if __name__ == "__main__":
    unittest.main()
