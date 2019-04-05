"""Test watcher module."""
import time
from unittest import mock, TestCase

from siriuspy.pwrsupply.watcher import Watcher
from siriuspy.csdevice.pwrsupply import Const as _PSConst
from siriuspy.pwrsupply.model_factory import PRUCParms_FBP


def wait(condition, timelimit=0.5):
    """Wait condition or timelimit."""
    d = 0
    t = time.time()

    while (not condition() and d < timelimit):
        d = time.time() - t


def wait_die(watcher, timelimit=0.5):
    """Wait thread die."""
    d = 0
    t = time.time()

    while (watcher.is_alive() and d < timelimit):
        d = time.time() - t


def wait_state(watcher, state, timelimit=0.5):
    """Wait thread reach state."""
    d = 0
    t = time.time()

    while (not (watcher.state == state) and d < timelimit):
        d = time.time() - t


@mock.patch('siriuspy.pwrsupply.watcher._time')
class TestCycleWatcher(TestCase):
    """Test watcher."""

    def setUp(self):
        """Test common setup."""
        self.writers = {'OpMode-Sel': mock.Mock(), 'Current-SP': mock.Mock()}
        self.controller = mock.Mock()
        self.controller.pru_controller.params.FREQ_SCAN = \
            PRUCParms_FBP.FREQ_SCAN
        self.dev_name = 'FakeName'
        self.op_mode = _PSConst.OpMode.Cycle
        self.watcher = Watcher(
            self.writers, self.controller, self.dev_name, self.op_mode)

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
        """Set common teardown."""
        self.watcher.stop()
        self.watcher.join()

    def test_init(self, time):
        """Test init."""
        self.assertEqual(self.watcher.state, Watcher.WAIT_OPMODE)

    def test_cycle_stop(self, mock_time):
        """Test cycle mode."""
        self.assertFalse(self.watcher.exit)
        time.sleep(1e-1)
        self.watcher.stop()
        self.assertTrue(self.watcher.exit)
        mock_time.sleep.assert_called()

    def test_cycle_opmode_trigger(self, mock_time):
        """Test cycle wait opmode state."""
        self.assertEqual(self.watcher.state, Watcher.WAIT_OPMODE)
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.Cycle
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_TRIGGER)
        self.assertEqual(self.watcher.state, Watcher.WAIT_TRIGGER)
        self.assertTrue(self.watcher.is_alive())

    def test_cycle_opmode_cycle(self, mock_time):
        """Test watcher goes to wait cycle when sync already pulsed."""
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.Cycle
        self.values['FakeName:CycleEnbl-Mon'] = 1
        self.controller.pru_controller.pru_sync_pulse_count = 1
        wait_state(self.watcher, Watcher.WAIT_CYCLE)
        self.assertEqual(self.watcher.state, Watcher.WAIT_CYCLE)
        self.assertTrue(self.watcher.is_alive())

    def test_cycle_trigger_change_op_mode(self, mock_time):
        """Watcher ends if op mode changes while waiting for trigger."""
        # Wait trigger mode
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.Cycle
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_TRIGGER)
        # Change op mode
        self.values['FakeName:OpMode-Sts'] = 0
        wait_die(self.watcher)
        self.assertEqual(self.watcher.state, Watcher.WAIT_TRIGGER)
        self.assertFalse(self.watcher.is_alive())

    def test_cycle_trigger_sync_stopped(self, mock_time):
        """Watcher ends if sync is stopped when cycle has not."""
        # Wait trigger mode
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.Cycle
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_TRIGGER)
        # Stop sync
        self.controller.pru_controller.pru_sync_status = 0
        wait_die(self.watcher)
        self.assertEqual(self.watcher.state, Watcher.WAIT_TRIGGER)
        self.assertFalse(self.watcher.is_alive())

    def test_cycle_trigger_sync_stopped_and_cycle_started(self, mock_time):
        """Watcher go to wait cycle when sync stops and cycle has started."""
        # Wait trigger mode
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.Cycle
        self.controller.pru_controller.pru_sync_status = 1
        # wait_state(self.watcher, Watcher.WAIT_TRIGGER)
        # Stop sync and start cycle
        self.controller.pru_controller.pru_sync_status = 0
        self.controller.pru_controller.pru_sync_pulse_count = 1
        self.values['FakeName:CycleEnbl-Mon'] = 1
        wait_die(self.watcher)
        self.assertEqual(self.watcher.state, Watcher.WAIT_CYCLE)
        self.assertTrue(self.watcher.is_alive())

    def test_cycle_wait_cycle_change_op_mode(self, mock_time):
        """Watcher ends if op mode changes while waiting for trigger."""
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.Cycle
        self.values['FakeName:CycleEnbl-Mon'] = 1
        self.controller.pru_controller.pru_sync_pulse_count = 1
        wait_state(self.watcher, Watcher.WAIT_CYCLE)
        # Change op mode
        self.values['FakeName:OpMode-Sts'] = 0
        wait_die(self.watcher)
        self.assertFalse(self.watcher.is_alive())

    def test_cycle_wait_cycle_stopped(self, mock_time):
        """Watcher finishes when."""
        # Wait cycle mode
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.Cycle
        self.values['FakeName:CycleEnbl-Mon'] = 1
        self.controller.pru_controller.pru_sync_pulse_count = 1
        wait_state(self.watcher, Watcher.WAIT_CYCLE)
        # End Cycle
        self.values['FakeName:CycleEnbl-Mon'] = 0
        wait_die(self.watcher)
        self.assertEqual(self.watcher.state, Watcher.WAIT_CYCLE)
        self.writers['OpMode-Sel'].execute.assert_called_with(0)
        # self.controller.write.assert_called()
        self.assertFalse(self.watcher.is_alive())


@mock.patch('siriuspy.pwrsupply.watcher._time')
class TestRmpWatcher(TestCase):
    """Test Ramp Watcher."""

    def setUp(self):
        """Test common setup."""
        self.writers = {'OpMode-Sel': mock.Mock(), 'Current-SP': mock.Mock()}
        self.controller = mock.Mock()
        self.controller.pru_controller.params.FREQ_SCAN = \
            PRUCParms_FBP.FREQ_SCAN
        self.dev_name = 'FakeName'
        self.op_mode = _PSConst.OpMode.RmpWfm
        self.watcher = Watcher(
            self.writers, self.controller, self.dev_name, self.op_mode)

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
        """Set common teardown."""
        self.watcher.stop()
        self.watcher.join()

    def test_ramp_stop(self, mock_time):
        """Test cycle mode."""
        self.assertFalse(self.watcher.exit)
        # time.sleep(1e-1)  # Wait at least one loop
        t = 0
        timeout = 1
        init = time.time()
        while not mock_time.sleep.call_args_list and t < timeout:
            time.sleep(1e-3)
            t = time.time() - init
        mock_time.sleep.assert_called()
        self.watcher.stop()
        self.assertTrue(self.watcher.exit)

    def test_ramp_opmode_trigger(self, mock_time):
        """Test ramp opmode."""
        self.assertEqual(self.watcher.state, Watcher.WAIT_OPMODE)
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.RmpWfm
        # time.sleep(1e-1)
        # self.assertEqual(self.watcher.state, Watcher.WAIT_OPMODE)
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_RMP)
        self.assertEqual(self.watcher.state, Watcher.WAIT_RMP)
        self.assertTrue(self.watcher.is_alive())

    def test_ramp_opmode_wait_ramp_changed_mode(self, mock_time):
        """Test wait_rampmode end when change op mode."""
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.RmpWfm
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_RMP)
        # Change op mode
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.SlowRef
        wait(lambda: not self.watcher.is_alive())
        # Assert thread died
        self.assertFalse(self.watcher.is_alive())

    def test_ramp_opmode_wait_ramp_sync_stopped(self, mock_time):
        """Test wait_rampmode end when change op mode."""
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.RmpWfm
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_RMP)
        # Change op mode
        self.controller.pru_controller.pru_sync_status = 0
        wait_die(self.watcher)
        # Assert thread died
        self.assertFalse(self.watcher.is_alive())

    def test_ramp_op_mode_finish(self, mock_time):
        """Test ramp thread finishes."""
        self.values['FakeName:WfmData-RB'] = [i + 1 for i in range(4000)]
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.RmpWfm
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_RMP)
        # Sync was pulsed and Change op mode
        self.controller.pru_controller.pru_sync_pulse_count = 12000
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.SlowRef
        wait_die(self.watcher)
        # Assert set current is called and thread leaves
        self.writers['Current-SP'].execute.assert_called_with(4000)
        # self.controller.write.assert_called_with(
        #     'FakeName', 'Current-SP', 4000)
        self.assertFalse(self.watcher.is_alive())


@mock.patch('siriuspy.pwrsupply.watcher._time')
class TestMigWatcher(TestCase):
    """Test MigWfm Watcher."""

    def setUp(self):
        """Test common setup."""
        self.writers = {'OpMode-Sel': mock.Mock(), 'Current-SP': mock.Mock()}
        self.controller = mock.Mock()
        self.controller.pru_controller.params.FREQ_SCAN = \
            PRUCParms_FBP.FREQ_SCAN
        self.dev_name = 'FakeName'
        self.op_mode = _PSConst.OpMode.MigWfm
        self.watcher = Watcher(
            self.writers, self.controller, self.dev_name, self.op_mode)

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
        """Set common teardown."""
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
        self.assertEqual(self.watcher.state, Watcher.WAIT_OPMODE)
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.MigWfm
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_MIG)
        self.assertEqual(self.watcher.state, Watcher.WAIT_MIG)
        self.assertTrue(self.watcher.is_alive())

    def test_wait_mig_change_op_mode(self, mock_time):
        """Test watcher stops."""
        # WAIT_MIG
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.MigWfm
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_MIG)
        # Change op mode
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.SlowRef
        wait_die(self.watcher)
        # Assert watcher stopped
        self.assertFalse(self.watcher.is_alive())

    def test_wait_mig_sync_stopped_but_not_pulsed(self, mock_time):
        """Test watcher stops."""
        # WAIT_MIG
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.MigWfm
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_MIG)
        # Change op mode
        self.controller.pru_controller.pru_sync_pulse_count = 0
        self.controller.pru_controller.pru_sync_status = 0
        wait_die(self.watcher)
        # Assert watcher stopped
        self.assertFalse(self.watcher.is_alive())

    def test_wait_mig_sync_stopped_and_pulsed(self, mock_time):
        """Test watcher stops."""
        # Fake wfmdata value
        self.values['FakeName:WfmData-RB'] = [i + 1 for i in range(4000)]
        # WAIT_MIG
        self.values['FakeName:OpMode-Sts'] = _PSConst.States.MigWfm
        self.controller.pru_controller.pru_sync_status = 1
        wait_state(self.watcher, Watcher.WAIT_MIG)
        # Change op mode
        self.controller.pru_controller.pru_sync_pulse_count = 4000
        self.controller.pru_controller.pru_sync_status = 0
        wait_die(self.watcher)
        # Assert watcher stopped and set curretn and opmode calls were made
        self.writers['Current-SP'].execute.assert_called_with(4000)
        self.writers['OpMode-Sel'].execute.assert_called_with(0)
        self.assertFalse(self.watcher.is_alive())
