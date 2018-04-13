#!/usr/bin/env python-sirius
"""Test public API of PowerSupply/Magnet class."""
import unittest
from unittest import mock

from siriuspy.bsmp import SerialError
from siriuspy.pwrsupply.model import FBPPowerSupply
from siriuspy.csdevice.pwrsupply import get_ps_propty_database
from siriuspy.util import check_public_interface_namespace


mock_read = [
    8579, 6.7230000495910645, 6.7230000495910645,
    [b'S', b'i', b'm', b'u'], 5, 8617, 0, 2, 1, 0.0, 0.0, 1.0, 0.0,
    [1.0, 1.0, 1.0, 0.0], 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0, 0, 0,
    6.722831726074219, 1.23291015625, 5.029296875, 53.0]


def mock_splims(pstype, label):
    """Return limits value."""
    if label in ('lolo', 'low', 'lolim'):
        return 0.0
    else:
        return 165.0


class TestPowerSupplyAPI(unittest.TestCase):
    """Test PowerSupply class."""

    api = (
        # 'controller',
        # 'database',
        # 'setpoints',
        # 'connected',
        # 'read',
        # 'write',
        # 'read_group',
        # 'create_group',
        # 'read_all_variables',
        'read_ps_variables',
        'read_status',
        'bsmp_2_epics',
        'epics_2_bsmp',
    )

    def test_api(self):
        """Test API."""
        self.assertTrue(
            check_public_interface_namespace(FBPPowerSupply, self.api))


class TestPowerSupply(unittest.TestCase):
    """Test power supply.

    Test methods read_variable, execute_function and method that read and parse
    the BSMP `ps_state` variable.
    """

    @mock.patch('siriuspy.csdevice.pwrsupply.get_ps_current_unit')
    @mock.patch('siriuspy.csdevice.pwrsupply._PSSearch')
    def setUp(self, search, unit):
        """Common setup for all tests."""
        search.get_splims.side_effect = mock_splims
        unit.return_value = 'A'
        db = get_ps_propty_database('bo-quadrupole-qd-fam')
        self.controller = mock.MagicMock()
        self.device = mock.Mock()
        self.controller.__getitem__.return_value = self.device
        self.device.execute_function.return_value = (0xE0, None)
        self.device.read_group_variables.return_value = (0xE0, mock_read)
        self.device.entities.list_variables.return_value = \
            [id for id in range(len(mock_read))]
        # self.controller.read_all_variables.return_value = (0xE0, mock_read)
        # self.controller.read_group_variables.return_value = (0xE0, mock_read)
        self.ps = FBPPowerSupply(self.controller, 1, 'name', db)

    def test_read_variable(self):
        """Test read variable method."""
        self.device.read_variable.return_value = (0xE0, 10.5)
        self.assertEqual(self.ps.read('Current-RB'), 10.5)

    def test_read_variable_error(self):
        """Test read_variable return None on BSMP error code."""
        self.device.read_variable.return_value = (0xE8, None)
        self.assertIsNone(self.ps.read('Current-RB'))

    def test_execute_function(self):
        """Test execute function returns true on success."""
        self.device.execute_function.return_value = (0xE0, None)
        self.assertTrue(self.ps.write('Current-SP', 1))

    def test_execute_function_error(self):
        """Test execute function returns true on success."""
        self.device.execute_function.side_effect = SerialError
        self.assertFalse(self.ps.write('Current-SP', 1))

    def test_pwrstate_sts_off(self):
        """Test pwrstate sts."""
        # Off - Off
        self.device.read_variable.return_value = (0xE0, 0b0000000000000000)
        self.assertEqual(self.ps.read('PwrState-Sts'), 0)
        self.device.read_variable.return_value = (0xE0, 0b1111111111110000)
        self.assertEqual(self.ps.read('PwrState-Sts'), 0)

    def test_pwrstate_sts_interlock(self):
        """Test pwrstate sts."""
        # Interlock - Off
        self.device.read_variable.return_value = (0xE0, 0b0000000000000001)
        self.assertEqual(self.ps.read('PwrState-Sts'), 0)

    def test_pwrstate_sts_initializing(self):
        """Test pwrstate sts."""
        # Initializing - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000000010)
        self.assertEqual(self.ps.read('PwrState-Sts'), 1)

    def test_pwrstate_sts_slowref(self):
        """Test pwrstate sts."""
        # SlowRef - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000000011)
        self.assertEqual(self.ps.read('PwrState-Sts'), 1)

    def test_pwrstate_sts_slowrefsync(self):
        """Test pwrstate sts."""
        # SlowRefSync - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000000100)
        self.assertEqual(self.ps.read('PwrState-Sts'), 1)

    def test_pwrstate_sts_cycle(self):
        """Test pwrstate sts."""
        # Cycle - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000000101)
        self.assertEqual(self.ps.read('PwrState-Sts'), 1)

    def test_pwrstate_sts_rmpwfm(self):
        """Test pwrstate sts."""
        # RmpWfm - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000000110)
        self.assertEqual(self.ps.read('PwrState-Sts'), 1)

    def test_pwrstate_sts_migwfm(self):
        """Test pwrstate sts."""
        # MigWfm - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000000111)
        self.assertEqual(self.ps.read('PwrState-Sts'), 1)

    def test_pwrstate_sts_fastref(self):
        """Test pwrstate sts."""
        # FastRef - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000001000)
        self.assertEqual(self.ps.read('PwrState-Sts'), 1)

    def test_opmode_sts_off(self):
        """Test opmode_sts."""
        # Off - SlowRef
        self.device.read_variable.return_value = (0xE0, 0b0000000000000000)
        self.assertEqual(self.ps.read('OpMode-Sts'), 0)

    def test_opmode_sts_interlock(self):
        """Test opmode sts."""
        # Interlock - SlowRef
        self.device.read_variable.return_value = (0xE0, 0b0000000000000001)
        self.assertEqual(self.ps.read('OpMode-Sts'), 0)

    def test_opmode_sts_initializing(self):
        """Test opmode sts."""
        # Initializing - SlowRef
        self.device.read_variable.return_value = (0xE0, 0b0000000000000010)
        self.assertEqual(self.ps.read('OpMode-Sts'), 0)

    def test_opmode_sts_slowref(self):
        """Test opmode sts."""
        # SlowRef
        self.device.read_variable.return_value = (0xE0, 0b0000000000000011)
        self.assertEqual(self.ps.read('OpMode-Sts'), 0)

    def test_opmode_sts_slowrefsync(self):
        """Test opmode sts."""
        # SlowRefSync
        self.device.read_variable.return_value = (0xE0, 0b0000000000000100)
        self.assertEqual(self.ps.read('OpMode-Sts'), 1)

    def test_opmode_sts_cycle(self):
        """Test opmode sts."""
        # Cycle - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000000101)
        self.assertEqual(self.ps.read('OpMode-Sts'), 2)

    def test_opmode_sts_rmpwfm(self):
        """Test opmode sts."""
        # RmpWfm - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000000110)
        self.assertEqual(self.ps.read('OpMode-Sts'), 3)

    def test_opmode_sts_migwfm(self):
        """Test opmode sts."""
        # MigWfm - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000000111)
        self.assertEqual(self.ps.read('OpMode-Sts'), 4)

    def test_opmode_sts_fastref(self):
        """Test opmode sts."""
        # FastRef - On
        self.device.read_variable.return_value = (0xE0, 0b0000000000001000)
        self.assertEqual(self.ps.read('OpMode-Sts'), 5)

    def test_read_group(self):
        """Test read group creation."""
        """Test reading from group -1."""
        variables = [0, 3, 6, 7]
        values = [0b0000000000000110,
                  [b't', b'e', b's', b't', b'e', b'\x00', b'\x00', b'\x00'],
                  0, 0]
        self.device.read_group_variables.return_value = (0xE0, values)
        self.device.entities.list_variables.return_value = variables
        self.assertEqual(self.ps._read_group(3), {
            'PwrState-Sts': 1,
            'OpMode-Sts': 3,
            'CtrlMode-Mon': 0,
            'Version-Cte': 'teste',
            'CycleEnbl-Mon': values[2],
            'CycleType-Sts': values[3]})

    def test_create_group_return_true(self):
        """Test create group return true."""
        self.device.create_group.return_value = (0xE0, None)
        self.assertTrue(self.ps._create_group(['CurrentRef-Mon']))

    def test_create_group(self):
        """Test correct stream is sent."""
        # Create group with currents
        self.device.create_group.return_value = (0xE0, None)
        self.ps._create_group(['CurrentRef-Mon', 'Current-Mon', 'Current-RB'])
        self.device.create_group.assert_called_with({1, 2, 27})

    def test_create_group_field_with_same_id(self):
        """Test creating group with fields that have same id."""
        # Create group with 2 field that map to the same id
        self.device.create_group.return_value = (0xE0, None)
        self.ps._create_group(['PwrState-Sts', 'OpMode-Sts'])
        self.device.create_group.assert_called_with({0})

    def test_create_group_error(self):
        """Test create_group returns false when error occurs."""
        self.device.create_group.return_value = (0xE3, None)
        self.assertFalse(self.ps._create_group(['CurrentRef-Mon']))


class TestPowerSupplyFunctions(unittest.TestCase):
    """Test functions."""

    @mock.patch('siriuspy.csdevice.pwrsupply.get_ps_current_unit')
    @mock.patch('siriuspy.csdevice.pwrsupply._PSSearch')
    def setUp(self, search, unit):
        """Controller execute_function returns ok."""
        search.get_splims.side_effect = mock_splims
        unit.return_value = 'A'
        db = get_ps_propty_database('bo-quadrupole-qd-fam')
        self.controller = mock.MagicMock()
        self.device = mock.Mock()
        self.controller.__getitem__.return_value = self.device
        self.device.execute_function.return_value = (0xE0, None)
        self.device.read_group_variables.return_value = (0xE0, mock_read)
        self.device.entities.list_variables.return_value = \
            [id for id in range(len(mock_read))]
        self.ps = FBPPowerSupply(self.controller, 'name', 1, db)

    def test_set_pwrstate_setpoint(self):
        """Test get pwrstate setpoint."""
        self.ps.write('PwrState-Sel', 1)
        self.assertEqual(self.ps.read('PwrState-Sel'), 1)
        self.ps.write('PwrState-Sel', 0)
        self.assertEqual(self.ps.read('PwrState-Sel'), 0)

    def test_set_pwrstate_on_call(self):
        """Test device methods are called."""
        self.ps.write('PwrState-Sel', 1)
        self.device.execute_function.assert_any_call(0, None)

    def test_set_pwrstate_on_closes_loop(self):
        """Test device methods are called."""
        self.ps.write('PwrState-Sel', 1)
        self.device.execute_function.assert_called_with(3, None)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_set_pwrstate_on_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.ps.write('PwrState-Sel', 1)
        time.sleep.assert_called_with(0.3)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_set_pwrstate_on_error_no_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.device.execute_function.return_value = (0xE3, None)
        self.ps.write('PwrState-Sel', 1)
        time.sleep.assert_not_called()

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_set_pwrstate_off_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.ps.write('PwrState-Sel', 0)
        time.sleep.assert_called_with(0.3)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_set_pwrstate_off_on_error_no_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.device.execute_function.return_value = (0xE3, None)
        self.ps.write('PwrState-Sel', 0)
        time.sleep.assert_not_called()

    def test_set_pwrstate_on_zero_setpoints(self):
        """Test setting pwrstate set current and opmode sp to 0."""
        self.device.execute_function.return_value = (0xE0, None)
        self.ps.write('PwrState-Sel', 1)
        self.assertEqual(self.ps.setpoints['Current-SP']['value'], 0.0)
        self.assertEqual(self.ps.setpoints['OpMode-Sel']['value'], 0)

    def test_set_pwrstate_off_zero_setpoints(self):
        """Test setting pwrstate set current and opmode sp to 0."""
        self.device.execute_function.return_value = (0xE0, None)
        self.ps.write('PwrState-Sel', 0)
        self.assertEqual(self.ps.read('Current-SP'), 0.0)
        self.assertEqual(self.ps.read('OpMode-Sel'), 0)

    def test_set_opmode_setpoint(self):
        """Test get pwrstate setpoint."""
        self.ps.write('OpMode-Sel', 3)
        self.device.execute_function.assert_called_with(4, 3)
        self.assertEqual(self.ps.read('OpMode-Sel'), 3)

    def test_set_current(self):
        """Set set current."""
        self.ps.write('Current-SP', 100.0)
        self.assertEqual(self.ps.read('Current-SP'), 100.0)

    def test_set_current_call(self):
        """Test controller is called."""
        self.ps.write('Current-SP', 100.0)
        self.device.execute_function.assert_called_with(16, 100.0)

    def test_set_current_min(self):
        """Set test current too low."""
        self.ps.write('Current-SP', -1.0)
        self.assertEqual(self.ps.read('Current-SP'), 0.0)

    def test_set_current_max(self):
        """Set test current too low."""
        self.ps.write('Current-SP', 170.0)
        self.assertEqual(self.ps.read('Current-SP'), 165.0)

    def test_reset(self):
        """Test reset command."""
        self.ps.write('Reset-Cmd', 1)
        self.assertEqual(self.ps.read('Reset-Cmd'), 1)

    def test_reset_zero(self):
        """Test reset command send zero."""
        self.ps.write('Reset-Cmd', 0)
        self.assertEqual(self.ps.read('Reset-Cmd'), 0)

    def test_reset_counter(self):
        """Test resert count."""
        for i in range(10):
            self.ps.write('Reset-Cmd', 1)
        self.assertEqual(self.ps.read('Reset-Cmd'), 10)

    def test_reset_calls(self):
        """Test reset interlock is called correctly."""
        self.ps.write('Reset-Cmd', 1)
        self.device.execute_function.assert_called_with(6, None)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_reset_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.ps.write('Reset-Cmd', 1)
        time.sleep.assert_called_with(0.1)

    @mock.patch('siriuspy.pwrsupply.model._time')
    def test_reset_on_error_no_sleep(self, time):
        """Test turn on has delay after turn on function."""
        self.device.execute_function.return_value = (0xE3, None)
        self.ps.write('Reset-Cmd', 1)
        time.sleep.assert_not_called()

    def test_enable_siggen(self):
        """Test enable_siggen command."""
        self.ps.write('CycleEnbl-Cmd', 1)
        self.assertEqual(self.ps.read('CycleEnbl-Cmd'), 1)
        self.device.execute_function.assert_called_with(25, None)

    def test_enable_siggen_zero(self):
        """Test enable_siggen command send zero."""
        self.ps.write('CycleEnbl-Cmd', 0)
        self.assertEqual(self.ps.read('CycleEnbl-Cmd'), 0)
        self.assertEqual(self.device.execute_function.call_args_list,
                         [mock.call(3)])

    def test_enable_siggen_counter(self):
        """Test enable_siggen count."""
        for i in range(10):
            self.ps.write('CycleEnbl-Cmd', 1)
        self.assertEqual(self.ps.read('CycleEnbl-Cmd'), 10)

    def test_disable_siggen(self):
        """Test disable_siggen command."""
        self.ps.write('CycleDsbl-Cmd', 1)
        self.assertEqual(self.ps.read('CycleDsbl-Cmd'), 1)
        self.device.execute_function.assert_called_with(26, None)

    def test_disable_siggen_zero(self):
        """Test disable_siggen command send zero."""
        self.ps.write('CycleDsbl-Cmd', 0)
        self.assertEqual(self.ps.read('CycleDsbl-Cmd'), 0)
        self.assertEqual(self.device.execute_function.call_args_list,
                         [mock.call(3)])

    def test_disable_siggen_counter(self):
        """Test disable_siggen count."""
        for i in range(10):
            self.ps.write('CycleDsbl-Cmd', 1)
        self.assertEqual(self.ps.read('CycleDsbl-Cmd'), 10)

    def test_set_cycle_type(self):
        """Test setting cycle type."""
        self.ps.write('CycleType-Sel', 1)
        self.assertEqual(self.ps.read('CycleType-Sel'), 1)
        self.device.execute_function.assert_called_with(
            23, [1, 1, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0])

    def test_cycle_nr_cycles(self):
        """Test setting number of cycles."""
        self.ps.write('CycleNrCycles-SP', 100)
        self.assertEqual(self.ps.read('CycleNrCycles-SP'), 100)
        self.device.execute_function.assert_called_with(
            23, [2, 100, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0])

    def test_cycle_frequency(self):
        """Test setting cycle frequency."""
        self.ps.write('CycleFreq-SP', 10.0)
        self.assertEqual(self.ps.read('CycleFreq-SP'), 10.0)
        self.device.execute_function.assert_called_with(
            23, [2, 1, 10.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0])

    def test_cycle_amplitude(self):
        """Test setting cycle amplitude."""
        self.ps.write('CycleAmpl-SP', 1.5)
        self.assertEqual(self.ps.read('CycleAmpl-SP'), 1.5)
        self.device.execute_function.assert_called_with(
            23, [2, 1, 0.0, 1.5, 0.0, 1.0, 1.0, 1.0, 0.0])

    def test_cycle_offset(self):
        """Test setting cycle offset."""
        self.ps.write('CycleOffset-SP', 1.0)
        self.assertEqual(self.ps.read('CycleOffset-SP'), 1.0)
        self.device.execute_function.assert_called_with(
            23, [2, 1, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0])

    def test_cycle_aux_params(self):
        """Test setting cycle aux params."""
        self.ps.write('CycleAuxParam-SP', [0.0, 1.5, 3.0, 4.5])
        self.assertEqual(
            self.ps.read('CycleAuxParam-SP'), [0.0, 1.5, 3.0, 4.5])
        self.device.execute_function.assert_called_with(
            23, [2, 1, 0.0, 1.0, 0.0, 0.0, 1.5, 3.0, 4.5])

    # def test_set_siggen(self):
    #     """Test set_siggen is called correctly."""
    #     self.ps.set_siggen(1.0, 1.0, 1.0)
    #     self.controller.execute_function.assert_called_with(
    #         24, [1.0, 1.0, 1.0])


if __name__ == "__main__":
    unittest.main()
