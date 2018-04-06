"""Test of pwrtsupply/controller module."""
import unittest
from unittest import mock
from unittest.mock import Mock

from siriuspy.csdevice.pwrsupply import get_ps_propty_database
from siriuspy.util import check_public_interface_namespace
from siriuspy.pwrsupply.dispatcher import PSDispatcher
from db import bo_db
from variables import dict_values


mock_read = {'PwrState-Sts': 1,
             'OpMode-Sts': 1,
             'Current-RB': 1.0,
             'CycleType-Sts': 2,
             'CycleNrCycles-RB': 1,
             'CycleFreq-RB': 2.0,
             'CycleAmpl-RB': 1.0,
             'CycleOffset-RB': 0.0,
             'CycleAuxParam-RB': [0.0, 0.0, 0.0, 0.0],
             'WfmData-RB': [0 for _ in range(4000)]}


def mock_splims(pstype, label):
    """Return limits value."""
    if label in ('lolo', 'low', 'lolim'):
        return 0.0
    else:
        return 165.0


class TestPSDispatcher(unittest.TestCase):
    """Test PSDispatcher behaviour."""

    api = (
        'read',
        'write',
        'read_all_variables',
        'device',
        'database',
        'connected',
        'setpoints',
    )

    @mock.patch('siriuspy.csdevice.pwrsupply.get_ps_current_unit')
    @mock.patch('siriuspy.csdevice.pwrsupply._PSSearch')
    def setUp(self, search, unit):
        """Common setup for all tests."""
        search.get_splims.side_effect = mock_splims
        unit.return_value = 'A'
        db = get_ps_propty_database('bo-quadrupole-qd-fam')
        self.device = Mock()
        self.device.read_all_variables.return_value = mock_read

        self.ioc_c = PSDispatcher(self.device, database=db)

    def test_api(self):
        """Test API."""
        self.assertTrue(
            check_public_interface_namespace(PSDispatcher, self.api))

    def test_device(self):
        """Test device property."""
        self.assertIsInstance(self.ioc_c.device, Mock)

    def test_setpoints(self):
        """Test setpoints."""
        self.assertIn('PwrState-Sel', self.ioc_c.setpoints)
        self.assertIn('OpMode-Sel', self.ioc_c.setpoints)
        self.assertIn('Current-SP', self.ioc_c.setpoints)

    def test_read_readback(self):
        """Test read method."""
        self.device.pwrstate_sts = 1
        self.device.cycletype_sts = 2
        self.device.current_mon = 1.0
        self.assertEqual(self.ioc_c.read('PwrState-Sts'), 1)
        self.assertEqual(self.ioc_c.read('CycleType-Sts'), 2)
        self.assertEqual(self.ioc_c.read('Current-Mon'), 1.0)

    def test_read_setpoint(self):
        """Test read method."""
        self.assertEqual(
            self.ioc_c.read('PwrState-Sel'), 1)
        self.assertEqual(
            self.ioc_c.read('Current-SP'), 1.0)

    def test_write_readback(self):
        """Test write method returns false a read only field is passed."""
        self.assertTrue(self.ioc_c.write('Current-RB', 10))

    def test_write_setpoint(self):
        """Test write method."""
        self.assertTrue(self.ioc_c.write('Current-SP', 5.1))

    def test_set_pwrstate_setpoint(self):
        """Test get pwrstate setpoint."""
        self.ioc_c.write('PwrState-Sel', 1)
        self.assertEqual(self.ioc_c.read('PwrState-Sel'), 1)
        self.ioc_c.write('PwrState-Sel', 0)
        self.assertEqual(self.ioc_c.read('PwrState-Sel'), 0)

    def test_set_pwrstate_calls(self):
        """Test device methods are called."""
        self.ioc_c.write('PwrState-Sel', 1)
        self.device.turn_on.assert_called_once()
        self.ioc_c.write('PwrState-Sel', 0)
        self.device.turn_off.assert_called_once()

    def test_set_pwrstate_on_zero_setpoints(self):
        """Test setting pwrstate set current and opmode sp to 0."""
        self.device.turn_on.return_value = True
        self.ioc_c.write('PwrState-Sel', 1)
        self.assertEqual(self.ioc_c.setpoints['Current-SP']['value'], 0.0)
        self.assertEqual(self.ioc_c.setpoints['OpMode-Sel']['value'], 0)

    def test_set_pwrstate_off_zero_setpoints(self):
        """Test setting pwrstate set current and opmode sp to 0."""
        self.device.turn_off.return_value = True
        self.ioc_c.write('PwrState-Sel', 0)
        self.assertEqual(self.ioc_c.read('Current-SP'), 0.0)
        self.assertEqual(self.ioc_c.read('OpMode-Sel'), 0)

    def test_set_opmode_setpoint(self):
        """Test get pwrstate setpoint."""
        self.ioc_c.write('OpMode-Sel', 3)
        self.assertEqual(self.ioc_c.read('OpMode-Sel'), 3)
        self.device.select_op_mode.assert_called_with(3)

    def test_set_current(self):
        """Set set current."""
        self.ioc_c.write('Current-SP', 100.0)
        self.assertEqual(self.ioc_c.read('Current-SP'), 100.0)
        self.device.set_slowref.assert_called_with(100.0)

    def test_set_current_min(self):
        """Set test current too low."""
        self.ioc_c.write('Current-SP', -1.0)
        self.assertEqual(self.ioc_c.read('Current-SP'), 0.0)

    def test_set_current_max(self):
        """Set test current too low."""
        self.ioc_c.write('Current-SP', 170.0)
        self.assertEqual(self.ioc_c.read('Current-SP'), 165.0)

    def test_reset(self):
        """Test reset command."""
        self.ioc_c.write('Reset-Cmd', 1)
        self.assertEqual(self.ioc_c.read('Reset-Cmd'), 1)
        self.device.reset_interlocks.assert_called_once()

    def test_reset_zero(self):
        """Test reset command send zero."""
        self.ioc_c.write('Reset-Cmd', 0)
        self.assertEqual(self.ioc_c.read('Reset-Cmd'), 0)
        self.device.reset_interlocks.assert_not_called()

    def test_reset_counter(self):
        """Test resert count."""
        for i in range(10):
            self.ioc_c.write('Reset-Cmd', 1)
        self.assertEqual(self.ioc_c.read('Reset-Cmd'), 10)

    def test_enable_siggen(self):
        """Test enable_siggen command."""
        self.ioc_c.write('CycleEnbl-Cmd', 1)
        self.assertEqual(self.ioc_c.read('CycleEnbl-Cmd'), 1)
        self.device.enable_siggen.assert_called_once()

    def test_enable_siggen_zero(self):
        """Test enable_siggen command send zero."""
        self.ioc_c.write('CycleEnbl-Cmd', 0)
        self.assertEqual(self.ioc_c.read('CycleEnbl-Cmd'), 0)
        self.device.enable_siggen.assert_not_called()

    def test_enable_siggen_counter(self):
        """Test enable_siggen count."""
        for i in range(10):
            self.ioc_c.write('CycleEnbl-Cmd', 1)
        self.assertEqual(self.ioc_c.read('CycleEnbl-Cmd'), 10)

    def test_disable_siggen(self):
        """Test disable_siggen command."""
        self.ioc_c.write('CycleDsbl-Cmd', 1)
        self.assertEqual(self.ioc_c.read('CycleDsbl-Cmd'), 1)
        self.device.disable_siggen.assert_called_once()

    def test_disable_siggen_zero(self):
        """Test disable_siggen command send zero."""
        self.ioc_c.write('CycleDsbl-Cmd', 0)
        self.assertEqual(self.ioc_c.read('CycleDsbl-Cmd'), 0)
        self.device.disable_siggen.assert_not_called()

    def test_disable_siggen_counter(self):
        """Test disable_siggen count."""
        for i in range(10):
            self.ioc_c.write('CycleDsbl-Cmd', 1)
        self.assertEqual(self.ioc_c.read('CycleDsbl-Cmd'), 10)

    def test_set_cycle_type(self):
        """Test setting cycle type."""
        self.ioc_c.write('CycleType-Sel', 1)
        self.assertEqual(self.ioc_c.read('CycleType-Sel'), 1)
        self.device.cfg_siggen.assert_called_with(
            1, 1, 2.0, 1.0, 0.0, [0.0, 0.0, 0.0, 0.0])

    def test_cycle_nr_cycles(self):
        """Test setting number of cycles."""
        self.ioc_c.write('CycleNrCycles-SP', 100)
        self.assertEqual(self.ioc_c.read('CycleNrCycles-SP'), 100)
        self.device.cfg_siggen.assert_called_with(
            2, 100, 2.0, 1.0, 0.0, [0.0, 0.0, 0.0, 0.0])

    def test_cycle_frequency(self):
        """Test setting cycle frequency."""
        self.ioc_c.write('CycleFreq-SP', 10.0)
        self.assertEqual(self.ioc_c.read('CycleFreq-SP'), 10.0)
        self.device.cfg_siggen.assert_called_with(
            2, 1, 10.0, 1.0, 0.0, [0.0, 0.0, 0.0, 0.0])

    def test_cycle_amplitude(self):
        """Test setting cycle amplitude."""
        self.ioc_c.write('CycleAmpl-SP', 1.5)
        self.assertEqual(self.ioc_c.read('CycleAmpl-SP'), 1.5)
        self.device.cfg_siggen.assert_called_with(
            2, 1, 2.0, 1.5, 0.0, [0.0, 0.0, 0.0, 0.0])

    def test_cycle_offset(self):
        """Test setting cycle offset."""
        self.ioc_c.write('CycleOffset-SP', 1.0)
        self.assertEqual(self.ioc_c.read('CycleOffset-SP'), 1.0)
        self.device.cfg_siggen.assert_called_with(
            2, 1, 2.0, 1.0, 1.0, [0.0, 0.0, 0.0, 0.0])

    def test_cycle_aux_params(self):
        """Test setting cycle aux params."""
        self.ioc_c.write('CycleAuxParam-SP', [1.0, 1.0, 1.0, 1.0])
        self.assertEqual(
            self.ioc_c.read('CycleAuxParam-SP'), [1.0, 1.0, 1.0, 1.0])
        self.device.cfg_siggen.assert_called_with(
            2, 1, 2.0, 1.0, 0.0, [1.0, 1.0, 1.0, 1.0])

    def _test_read_all_variables(self):
        """Test reading all variables."""
        dev_db = {'Current-Mon': 0.0, 'PwrState-Sts': 1}
        self.device.read_all_variables.return_value = \
            {'Current-Mon': 0.0, 'PwrState-Sts': 1}

        for field in db:
            if 'SP' in field or 'Sel' in field or 'Cmd' in field:
                dev_db[field] = bo_db[field]['value']

        d1 = self.controller.read_all_variables()
        self.assertDictEqual(d1, dev_db)

    def _test_read_all_variables_error(self):
        """Test reading all variables."""
        self.device.read_all_variables.return_value = None
        self.assertIsNone(self.controller.read_all_variables())


if __name__ == '__main__':
    unittest.main()
