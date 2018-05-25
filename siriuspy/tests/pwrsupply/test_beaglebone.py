#!/usr/bin/env python-sirius
"""Test beaglebone module."""
import time
import unittest
from unittest import mock

from siriuspy import util
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.util import check_public_interface_namespace
import siriuspy.pwrsupply.beaglebone as bbb
from siriuspy.csdevice.pwrsupply import get_ps_propty_database
from tests.pwrsupply.variables import dict_values


def read_variables(device_id, field):
    """Mock PRUController read_variables."""
    return dict_values[field]


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


@mock.patch('siriuspy.pwrsupply.beaglebone._time')
class TestCycleWatcher(unittest.TestCase):
    """Test watcher."""

    def setUp(self):
        """Test common setup."""
        self.setpoints = mock.Mock()
        self.controller = mock.Mock()
        self.dev_name = 'FakeName'
        self.op_mode = _PSConst.OpMode.Cycle
        self.watcher = bbb._Watcher(
            self.setpoints, self.controller, self.dev_name, self.op_mode)

        # Mock controller read values
        self.values = {
            'FakeName:OpMode-Sts': 0,
            'FakeName:CycleEnbl-Mon': 0}
        self.controller.read.side_effect = \
            lambda dev_name, field: self.values[dev_name + ':' + field]
        self.controller.pru_controller.pru_sync_status = 0
        self.controller.pru_controller.pru_sync_pulse_count = 0

        self.watcher.start()

    def tearDown(self):
        """Common teardown."""
        self.watcher.stop()
        self.watcher.join()

    def test_init(self, time):
        """Test init."""
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_OPMODE)

    def test_cycle_stop(self, mock_time):
        """Test cycle mode."""
        self.assertFalse(self.watcher.exit)
        time.sleep(1e-1)
        self.watcher.stop()
        self.assertTrue(self.watcher.exit)
        mock_time.sleep.assert_called()

    def test_cycle_opmode_trigger(self, mock_time):
        """Test cycle wait opmode state."""
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_OPMODE)
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.Cycle
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_OPMODE)
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_TRIGGER)
        self.assertTrue(self.watcher.is_alive())

    def test_cycle_opmode_cycle(self, mock_time):
        """Test watcher goes to wait cycle when sync already pulsed."""
        self.values['FakeName:OpMode-Sts'] = 2
        self.values['FakeName:CycleEnbl-Mon'] = 1
        self.controller.pru_controller.pru_sync_pulse_count = 1
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_CYCLE)
        self.assertTrue(self.watcher.is_alive())

    def test_cycle_trigger_change_op_mode(self, mock_time):
        """Watcher ends if op mode changes while waiting for trigger."""
        # Wait trigger mode
        self.values['FakeName:OpMode-Sts'] = 2
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        # Change op mode
        self.values['FakeName:OpMode-Sts'] = 0
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_TRIGGER)
        self.assertFalse(self.watcher.is_alive())

    def test_cycle_trigger_sync_stopped(self, mock_time):
        """Watcher ends if sync is stopped when cycle has not."""
        # Wait trigger mode
        self.values['FakeName:OpMode-Sts'] = 2
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        # Stop sync
        self.controller.pru_controller.pru_sync_status = 0
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_TRIGGER)
        self.assertFalse(self.watcher.is_alive())

    def test_cycle_trigger_sync_stopped_and_cycle_started(self, mock_time):
        """Watcher go to wait cycle when sync stops and cycle has started."""
        # Wait trigger mode
        self.values['FakeName:OpMode-Sts'] = 2
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        # Stop sync and start cycle
        self.controller.pru_controller.pru_sync_status = 0
        self.controller.pru_controller.pru_sync_pulse_count = 1
        self.values['FakeName:CycleEnbl-Mon'] = 1
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_CYCLE)
        self.assertTrue(self.watcher.is_alive())

    def test_cycle_wait_cycle_change_op_mode(self, mock_time):
        """Watcher ends if op mode changes while waiting for trigger."""
        self.values['FakeName:OpMode-Sts'] = 2
        self.values['FakeName:CycleEnbl-Mon'] = 1
        self.controller.pru_controller.pru_sync_pulse_count = 1
        time.sleep(1e-1)
        # Change op mode
        self.values['FakeName:OpMode-Sts'] = 0
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_CYCLE)
        self.assertFalse(self.watcher.is_alive())

    def test_cycle_wait_cycle_stopped(self, mock_time):
        """"Watcher finishes when."""
        # Wait cycle mode
        self.values['FakeName:OpMode-Sts'] = 2
        self.values['FakeName:CycleEnbl-Mon'] = 1
        self.controller.pru_controller.pru_sync_pulse_count = 1
        time.sleep(1e-1)
        # End Cycle
        self.values['FakeName:CycleEnbl-Mon'] = 0
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_CYCLE)
        self.setpoints.set.assert_called()
        self.controller.write.assert_called()
        self.assertFalse(self.watcher.is_alive())


@mock.patch('siriuspy.pwrsupply.beaglebone._time')
class TestRmpWatcher(unittest.TestCase):
    """Test Ramp Watcher."""

    def setUp(self):
        """Test common setup."""
        self.setpoints = mock.Mock()
        self.controller = mock.Mock()
        self.dev_name = 'FakeName'
        self.op_mode = _PSConst.OpMode.RmpWfm
        self.watcher = bbb._Watcher(
            self.setpoints, self.controller, self.dev_name, self.op_mode)

        # Mock controller read values
        self.values = {
            'FakeName:OpMode-Sts': 0,
            'FakeName:CycleEnbl-Mon': 0}
        self.controller.read.side_effect = \
            lambda dev_name, field: self.values[dev_name + ':' + field]
        self.controller.pru_controller.pru_sync_status = 0
        self.controller.pru_controller.pru_sync_pulse_count = 0

        self.watcher.start()

    def tearDown(self):
        """Common teardown."""
        self.watcher.stop()
        self.watcher.join()

    def test_ramp_stop(self, mock_time):
        """Test cycle mode."""
        self.assertFalse(self.watcher.exit)
        time.sleep(1e-1)
        self.watcher.stop()
        self.assertTrue(self.watcher.exit)
        mock_time.sleep.assert_called()

    def test_ramp_opmode_trigger(self, mock_time):
        """Test ramp opmode."""
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_OPMODE)
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.RmpWfm
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_OPMODE)
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_RMP)
        self.assertTrue(self.watcher.is_alive())

    def test_ramp_opmode_wait_ramp_changed_mode(self, mock_time):
        """Test wait_rampmode end when change op mode."""
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.RmpWfm
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        # Change op mode
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.SlowRef
        time.sleep(1e-1)
        # Assert thread died
        self.assertFalse(self.watcher.is_alive())

    def test_ramp_opmode_wait_ramp_sync_stopped(self, mock_time):
        """Test wait_rampmode end when change op mode."""
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.RmpWfm
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        # Change op mode
        self.controller.pru_controller.pru_sync_status = 0
        time.sleep(1e-1)
        # Assert thread died
        self.assertFalse(self.watcher.is_alive())

    def test_ramp_op_mode_finish(self, mock_time):
        """Test ramp thread finishes."""
        self.values['FakeName:WfmData-RB'] = [i + 1 for i in range(4000)]
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.RmpWfm
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        # Sync was pulsed and Change op mode
        self.controller.pru_controller.pru_sync_pulse_count = 12000
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.SlowRef
        time.sleep(1e-1)
        # Assert set current is called and thread leaves
        self.setpoints.set.assert_called_with('Current-SP', 4000)
        self.controller.write.assert_called_with(
            'FakeName', 'Current-SP', 4000)
        self.assertFalse(self.watcher.is_alive())


@mock.patch('siriuspy.pwrsupply.beaglebone._time')
class TestMigWatcher(unittest.TestCase):
    """Test MigWfm Watcher."""

    def setUp(self):
        """Test common setup."""
        self.setpoints = mock.Mock()
        self.controller = mock.Mock()
        self.dev_name = 'FakeName'
        self.op_mode = _PSConst.OpMode.MigWfm
        self.watcher = bbb._Watcher(
            self.setpoints, self.controller, self.dev_name, self.op_mode)

        # Mock controller read values
        self.values = {
            'FakeName:OpMode-Sts': 0,
            'FakeName:CycleEnbl-Mon': 0}
        self.controller.read.side_effect = \
            lambda dev_name, field: self.values[dev_name + ':' + field]
        self.controller.pru_controller.pru_sync_status = 0
        self.controller.pru_controller.pru_sync_pulse_count = 0

        self.watcher.start()

    def tearDown(self):
        """Common teardown."""
        self.watcher.stop()
        self.watcher.join()

    def test_mig_stop(self, mock_time):
        """Test cycle mode."""
        self.assertFalse(self.watcher.exit)
        time.sleep(1e-1)
        self.watcher.stop()
        self.assertTrue(self.watcher.exit)
        mock_time.sleep.assert_called()

    def test_wait_opmode(self, mock_time):
        """Test mig starts loop in wait mode."""
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_OPMODE)
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.MigWfm
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_OPMODE)
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        self.assertEqual(self.watcher.state, bbb._Watcher.WAIT_MIG)
        self.assertTrue(self.watcher.is_alive())

    def test_wait_mig_change_op_mode(self, mock_time):
        """Test watcher stops."""
        # WAIT_MIG
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.MigWfm
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        # Change op mode
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.SlowRef
        time.sleep(1e-1)
        # Assert watcher stopped
        self.assertFalse(self.watcher.is_alive())

    def test_wait_mig_sync_stopped_but_not_pulsed(self, mock_time):
        """Test watcher stops."""
        # WAIT_MIG
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.MigWfm
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        # Change op mode
        self.controller.pru_controller.pru_sync_pulse_count = 0
        self.controller.pru_controller.pru_sync_status = 0
        time.sleep(1e-1)
        # Assert watcher stopped
        self.assertFalse(self.watcher.is_alive())

    def test_wait_mig_sync_stopped_and_pulsed(self, mock_time):
        """Test watcher stops."""
        # Fake wfmdata value
        self.values['FakeName:WfmData-RB'] = [i + 1 for i in range(4000)]
        # WAIT_MIG
        self.values['FakeName:OpMode-Sts'] = _PSConst.OpMode.MigWfm
        self.controller.pru_controller.pru_sync_status = 1
        time.sleep(1e-1)
        # Change op mode
        self.controller.pru_controller.pru_sync_pulse_count = 4000
        self.controller.pru_controller.pru_sync_status = 0
        time.sleep(1e-1)
        # Assert watcher stopped and set curretn and opmode calls were made
        expected_setpoint_calls = [
            mock.call('Current-SP', 4000),
            mock.call('OpMode-Sel', _PSConst.OpMode.SlowRef)]
        actual_setpoint_calls = self.setpoints.set.call_args_list
        expected_controller_calls = [
            mock.call('FakeName', 'Current-SP', 4000),
            mock.call('FakeName', 'OpMode-Sel', _PSConst.OpMode.SlowRef)]
        actual_controller_calls = self.controller.write.call_args_list
        self.assertEqual(expected_setpoint_calls, actual_setpoint_calls)
        self.assertEqual(expected_controller_calls, actual_controller_calls)
        self.assertFalse(self.watcher.is_alive())


class TestDeviceSetpoints(unittest.TestCase):
    """Test device setpoints class."""

    def setUp(self):
        """Common setup for all tests."""
        sp_patch = mock.patch('siriuspy.pwrsupply.beaglebone._Setpoint')
        self.addCleanup(sp_patch.stop)
        self.sp_mock = sp_patch.start()
        self.sp_mock.match.return_value = True

        self.db = {'Fake-SP': mock.Mock(),
                   'Fake-Sel': mock.Mock(),
                   'Fake-Cmd': mock.Mock()}

        self.setpoints = bbb._DeviceSetpoints(self.db)

    def test_fields(self):
        """Test fields return db fields."""
        self.assertEqual(
            self.setpoints.fields(), self.db.keys())

    def test_get(self):
        """Test get."""
        self.setpoints._setpoints['Fake-SP'].value = 10
        self.assertEqual(self.setpoints.get('Fake-SP'), 10)

    def test_set(self):
        """Test set."""
        self.setpoints.set('Fake-SP', 1)
        self.setpoints._setpoints['Fake-SP'].apply.assert_called_with(1)


class TestSetpointMatch(unittest.TestCase):
    """Test setpoint match."""

    def test_match_sp(self):
        """Test sp."""
        self.assertTrue(bbb._Setpoint.match('Fake-SP'))

    def test_match_sel(self):
        """Test sel."""
        self.assertTrue(bbb._Setpoint.match('Fake-Sel'))

    def test_match_cmd(self):
        """Test cmd."""
        self.assertTrue(bbb._Setpoint.match('Fake-Cmd'))

    def test_match_strange(self):
        """Test strange fields."""
        self.assertFalse(bbb._Setpoint.match('Fake-RB'))
        self.assertFalse(bbb._Setpoint.match('Fake-Sts'))


class TestCmdSetpoint(unittest.TestCase):
    """Test setpoint class."""

    def setUp(self):
        """Common setup."""
        self.field = 'Fake-Cmd'
        self.db = {'type': 'int', 'value': 0}
        self.setpoint = bbb._Setpoint(self.field, self.db)

    def test_apply_returns_false(self):
        """Test apply setpoint with value 0 returns false."""
        self.assertFalse(self.setpoint.apply(0))
        self.assertFalse(self.setpoint.apply(-1))

    def test_check_returns_false(self):
        """Test check setpoint with value 0 returns false."""
        self.assertFalse(self.setpoint.check(0))
        self.assertFalse(self.setpoint.check(-1))

    def test_apply_returns_true(self):
        """Test apply setpoint with value > 0 returns True."""
        self.assertTrue(self.setpoint.apply(1))
        self.assertTrue(self.setpoint.apply(10))

    def test_check_returns_true(self):
        """Test check setpoint with value > 0 returns True."""
        self.assertTrue(self.setpoint.check(1))
        self.assertTrue(self.setpoint.check(10))

    def test_apply_increment_value(self):
        """Test apply increments setpoint by 1."""
        self.assertEqual(self.setpoint.value, 0)
        self.setpoint.apply(1)
        self.assertEqual(self.setpoint.value, 1)
        self.setpoint.apply(1)
        self.assertEqual(self.setpoint.value, 2)


class TestPSetpoint(unittest.TestCase):
    """Test setpoints sp."""

    def setUp(self):
        """Common setup."""
        self.field = 'Fake-SP'
        self.db = {'type': 'float',
                   'value': 0.0,
                   'lolo': -10.0,
                   'hihi': 10.0}
        self.setpoint = bbb._Setpoint(self.field, self.db)

    def test_init(self):
        """Test constructor."""
        self.assertEqual(self.setpoint.value, 0.0)
        self.assertEqual(self.setpoint.field, self.field)
        self.assertEqual(self.setpoint.database, self.db)
        self.assertFalse(self.setpoint.is_cmd)
        self.assertEqual(self.setpoint.type, 'float')
        self.assertIsNone(self.setpoint.count)
        self.assertEqual(self.setpoint.enums, None)
        self.assertEqual(self.setpoint.low, -10.0)
        self.assertEqual(self.setpoint.high, 10.0)

    def test_apply_above_limit(self):
        """Test apply setpoint with value above limit returns false."""
        self.assertEqual(self.setpoint.value, 0.0)
        self.assertFalse(self.setpoint.apply(11.0))
        self.assertEqual(self.setpoint.value, 0.0)

    def test_apply_below_limit(self):
        """Test apply setpoint with value below limit returns false."""
        self.assertEqual(self.setpoint.value, 0.0)
        self.assertFalse(self.setpoint.apply(-11.0))
        self.assertEqual(self.setpoint.value, 0.0)

    def test_check_returns_false(self):
        """Test check setpoint with value 0 returns false."""
        self.assertFalse(self.setpoint.check(11.0))
        self.assertFalse(self.setpoint.check(-11.0))

    def test_check_returns_true(self):
        """Test check setpoint with value > 0 returns True."""
        self.assertTrue(self.setpoint.check(9.0))
        self.assertTrue(self.setpoint.check(-9.0))

    def test_apply_returns_true(self):
        """Test apply setpoint with value > 0 returns True."""
        self.assertEqual(self.setpoint.value, 0.0)
        self.assertTrue(self.setpoint.apply(9.0))
        self.assertEqual(self.setpoint.value, 9.0)


class TestSelSetpoint(unittest.TestCase):
    """Test sel setpoints."""

    def setUp(self):
        """Common setup."""
        self.field = 'Fake-Sel'
        self.db = {'type': 'enum',
                   'value': 0,
                   'enums': ('StateA', 'StateB', 'StateC')}
        self.setpoint = bbb._Setpoint(self.field, self.db)

    def test_init(self):
        """Test constructor."""
        self.assertEqual(self.setpoint.value, 0)
        self.assertEqual(self.setpoint.field, self.field)
        self.assertEqual(self.setpoint.database, self.db)
        self.assertFalse(self.setpoint.is_cmd)
        self.assertEqual(self.setpoint.type, 'enum')
        self.assertIsNone(self.setpoint.count)
        self.assertEqual(self.setpoint.enums, ('StateA', 'StateB', 'StateC'))
        self.assertEqual(self.setpoint.low, None)
        self.assertEqual(self.setpoint.high, None)

    def test_apply_above_limit(self):
        """Test apply setpoint out of range."""
        self.assertEqual(self.setpoint.value, 0)
        self.assertFalse(self.setpoint.apply(4))
        self.assertEqual(self.setpoint.value, 0)

    def test_apply_below_limit(self):
        """Test apply setpoint out of range."""
        self.assertEqual(self.setpoint.value, 0)
        self.assertFalse(self.setpoint.apply(-1))
        self.assertEqual(self.setpoint.value, 0)

    def test_check_returns_false(self):
        """Test check setpoint out of range."""
        self.assertFalse(self.setpoint.check(4))
        self.assertFalse(self.setpoint.check(-1))

    def test_check_returns_true(self):
        """Test check setpoint out of range."""
        self.assertTrue(self.setpoint.check(0))
        self.assertTrue(self.setpoint.check(1))
        self.assertTrue(self.setpoint.check(2))

    def test_apply(self):
        """Test apply with value in range."""
        self.assertEqual(self.setpoint.value, 0)
        self.setpoint.apply(1)
        self.assertEqual(self.setpoint.value, 1)


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

    @mock.patch('siriuspy.csdevice.pwrsupply.get_ps_current_unit')
    @mock.patch('siriuspy.csdevice.pwrsupply._PSSearch')
    def _get_db(self, search, unit):
        def mock_splims(pstype, label):
            """Return limits value."""
            if label in ('lolo', 'low', 'lolim'):
                return 0.0
            else:
                return 165.0
        search.get_splims.side_effect = mock_splims
        unit.return_value = 'A'
        return get_ps_propty_database('FAC', 'bo-quadrupole-qd-fam')

    def setUp(self):
        """Common setup for all tests."""
        # Mock PRUController
        pru_patch = mock.patch('siriuspy.pwrsupply.beaglebone._PRUController')
        self.addCleanup(pru_patch.stop)
        self.pru_mock = pru_patch.start()
        # Mock E2SController
        e2s_patch = mock.patch('siriuspy.pwrsupply.beaglebone._E2SController')
        self.addCleanup(e2s_patch.stop)
        self.e2s_mock = e2s_patch.start()

        self.e2s_mock = self.e2s_mock.return_value
        self.e2s_mock.read.side_effect = read_variables
        self.pru_mock = self.pru_mock.return_value

        # Mock e2s_controller read_all method
        self.e2s_mock.read_all.return_value = \
            {'BO-01U:PS-CH' + ':' + 'OpMode-Sts': 0}

        bbbname = 'BO-01:CO-PSCtrl-1'
        self.bbb = bbb.BeagleBone(bbbname, simulate=True)

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(check_public_interface_namespace(
            bbb.BeagleBone, TestBeagleBone.public_interface))

    def _test_psnames(self):
        """Test psnames."""
        # TODO: implement test!
        pass

    def _test_pru_controller(self):
        """Test pru_controller."""
        # TODO: implement test!
        pass

    def _test_e2s_controller(self):
        """Test e2s_controller."""
        # TODO: implement test!
        pass

    def test_read_rb(self):
        """Test read."""
        dev_name = 'BO-01U:PS-CH'
        field = 'OpMode-Sts'
        self.assertEqual(self.bbb.read(dev_name)[dev_name + ':' + field], 0)

    def test_read_sp(self):
        """Test read setpoint."""
        dev_name = 'BO-01U:PS-CH'
        field = 'OpMode-Sel'
        self.assertEqual(self.bbb.read(dev_name)[dev_name + ':' + field], 0)

    def test_write_opmode_slowref(self):
        """Test write."""
        dev_name = ['BO-01U:PS-CH', 'BO-01U:PS-CV']
        field = 'OpMode-Sel'
        value = 0
        self.bbb.write('BO-01U:PS-CH', field, value)
        self.e2s_mock.write_to_many.assert_called_with(
            dev_name, field, value)

    def test_write_opmode_slowrefsync(self):
        """Test write."""
        dev_name = ['BO-01U:PS-CH', 'BO-01U:PS-CV']
        field = 'OpMode-Sel'
        value = 1
        self.bbb.write('BO-01U:PS-CV', field, value)
        self.e2s_mock.write_to_many.assert_called_with(
            dev_name, field, value)

    def _assert_thread(self, watcher, dev_names, op_mode):
        sp1 = self.bbb._setpoints[dev_names[0]]
        sp2 = self.bbb._setpoints[dev_names[1]]
        c = self.bbb.e2s_controller
        expected_calls = [mock.call(sp1, c, dev_names[0], op_mode),
                          mock.call(sp2, c, dev_names[1], op_mode)]
        calls = watcher.call_args_list
        self.assertEqual(expected_calls, calls)
        for w in self.bbb._watchers.values():
            w.start.assert_called()

    @mock.patch('siriuspy.pwrsupply.beaglebone._Watcher')
    def test_write_opmode_cycle(self, watcher):
        """Test write."""
        dev_name = ['BO-01U:PS-CH', 'BO-01U:PS-CV']
        field = 'OpMode-Sel'
        offset = 'CycleOffset-RB'
        value = 2
        # Stop PRU
        # self.pru_mock.pru_sync_stop.assert_called()
        # Mock Offset-RB
        self.e2s_mock.read.return_value = 1.5
        # Call write
        self.bbb.write('BO-01U:PS-CH', field, value)
        # Set cycling offset
        expected_calls = [mock.call(dev_name[0], offset),
                          mock.call(dev_name[1], offset)]
        calls = self.e2s_mock.read.call_args_list[-2:]
        self.assertEqual(expected_calls, calls)
        # Write to e2scontroller
        self.e2s_mock.write_to_many.assert_called_with(
            dev_name, field, value)
        # Start thread
        self._assert_thread(watcher, dev_name, 2)
        # Start pru cycle mode
        self.pru_mock.pru_sync_start.assert_called_with(
            self.pru_mock.PRU.SYNC_MODE.BRDCST)

    @mock.patch('siriuspy.pwrsupply.beaglebone._Watcher')
    def test_write_opmode_rmpwfm(self, watcher):
        """Test write opmode rmpwfm."""
        dev_name = ['BO-01U:PS-CH', 'BO-01U:PS-CV']
        field = 'OpMode-Sel'
        value = 3
        # Stop PRU
        # self.pru_mock.pru_sync_stop.assert_called()
        # Call write
        self.bbb.write('BO-01U:PS-CH', field, value)
        # Write to e2scontroller
        self.e2s_mock.write_to_many.assert_called_with(
            dev_name, field, 3)
        # Start thread
        self._assert_thread(watcher, dev_name, 3)
        # Start pru cycle mode
        self.pru_mock.pru_sync_start.assert_called_with(
            self.pru_mock.PRU.SYNC_MODE.RMPEND)

    @mock.patch('siriuspy.pwrsupply.beaglebone._Watcher')
    def test_write_opmode_migwfm(self, watcher):
        """Test write opmode migwfm."""
        dev_name = ['BO-01U:PS-CH', 'BO-01U:PS-CV']
        field = 'OpMode-Sel'
        value = 4
        # Stop PRU
        # self.pru_mock.pru_sync_stop.assert_called()
        # Call write
        self.bbb.write('BO-01U:PS-CH', field, value)
        # Write to e2scontroller
        self.e2s_mock.write_to_many.assert_called_with(
            dev_name, field, 4)
        # Start thread
        self._assert_thread(watcher, dev_name, 4)
        # Start pru cycle mode
        self.pru_mock.pru_sync_start.assert_called_with(
            self.pru_mock.PRU.SYNC_MODE.MIGEND)


if __name__ == "__main__":
    unittest.main()
