#!/usr/bin/env python-sirius

"""Test PSController class."""

# TODO: E2SController now is an auxilliary class!
# this unittest module does not conform to standard we have been using.

import unittest
from unittest import mock

# from siriuspy.csdevice.pwrsupply import get_ps_propty_database
from siriuspy.pwrsupply.controller import StandardPSController
from siriuspy.csdevice.pwrsupply import Const as PSConst
from siriuspy.pwrsupply.pru import Const as PRUConst


class TestStandardController(unittest.TestCase):
    """Test E2SController public methods behaviour."""

    def setUp(self):
        """Watcher class is mocked. Set up E2SController object."""
        # self.database = self._get_db()
        # print(self.database.keys())
        self.devices = {'BO-01U:PS-CH': 1, 'BO-01U:PS-CV': 2}
        self.readers = {'BO-01U:PS-CH:OpMode-Sts': mock.Mock(),
                        'BO-01U:PS-CH:OpMode-Sel': mock.Mock(),
                        'BO-01U:PS-CV:OpMode-Sel': mock.Mock(),
                        'BO-01U:PS-CH:PwrState-Sel': mock.Mock(),
                        'BO-01U:PS-CH:PwrState-Sts': mock.Mock(),
                        'BO-01U:PS-CH:CycleOffset-RB': mock.Mock(),
                        'BO-01U:PS-CV:CycleOffset-RB': mock.Mock(),
                        'BO-01U:PS-CH:Current-SP': mock.Mock(),
                        'BO-01U:PS-CH:CycleType-Sel': mock.Mock(),
                        'BO-01U:PS-CH:CycleNrCycles-SP': mock.Mock(),
                        'BO-01U:PS-CH:CycleFreq-SP': mock.Mock(),
                        'BO-01U:PS-CH:CycleAmpl-SP': mock.Mock(),
                        'BO-01U:PS-CH:CycleOffset-SP': mock.Mock(),
                        'BO-01U:PS-CH:CycleAuxParam-SP': mock.Mock()}
        self.readers['BO-01U:PS-CH:OpMode-Sts'].read.return_value = \
            PSConst.States.SlowRef
        self.writers = {
            'BO-01U:PS-CH:OpMode-Sel': mock.Mock(),
            'BO-01U:PS-CH:CycleType-Sel': mock.Mock(),
            'BO-01U:PS-CH:CycleNrCycles-SP': mock.Mock(),
            'BO-01U:PS-CH:CycleFreq-SP': mock.Mock(),
            'BO-01U:PS-CH:CycleAmpl-SP': mock.Mock(),
            'BO-01U:PS-CH:CycleOffset-SP': mock.Mock(),
            'BO-01U:PS-CH:CycleAuxParam-SP': mock.Mock(),
            'BO-01U:PS-CH:PwrState-Sel': mock.Mock(),
            'BO-01U:PS-CH:Current-SP': mock.Mock(),
            'BO-01U:PS-CV:Current-SP': mock.Mock()}
        self.connections = {}
        self.pru_controller = mock.Mock()
        self.controller = StandardPSController(
            self.readers, self.writers, self.connections,
            self.pru_controller, self.devices)
        self.controller._watchers['BO-01U:PS-CH'] = mock.Mock()

    def test_pru_controller(self):
        """Test pru_controller property."""
        self.assertEqual(self.controller.pru_controller, self.pru_controller)

    # Read method
    def test_read(self):
        """Test read method."""
        reader = self.readers['BO-01U:PS-CH:PwrState-Sts']
        ret = self.controller.read('BO-01U:PS-CH', 'PwrState-Sts')
        reader.read.assert_called()
        self.assertEqual(ret, reader.read.return_value)

    def test_read_strange_key(self):
        """Test KeyError is raised when device or field does not exist."""
        with self.assertRaises(KeyError):
            self.controller.read('WrongDevice', 'OpMode-Sts')
        with self.assertRaises(KeyError):
            self.controller.read('BO-01U:PS-CH', 'StrangeField')

    def test_read_operation_mode_checks_watcher(self):
        """Test device watcher is checked."""
        self.controller._watchers['BO-01U:PS-CH'].op_mode = \
            PSConst.OpMode.Cycle
        self.controller.read('BO-01U:PS-CH', 'OpMode-Sts')
        self.controller._watchers['BO-01U:PS-CH'].is_alive.assert_called()

    def test_read_operation_mode_watcher_dead(self):
        """Test watcher status is verified and returned."""
        self.controller._watchers['BO-01U:PS-CH'].is_alive.return_value = False
        ret = self.controller.read('BO-01U:PS-CH', 'OpMode-Sts')
        self.assertEqual(
            ret, self.readers['BO-01U:PS-CH:OpMode-Sts'].read.return_value)

    def test_read_operation_mode_watcher_alive(self):
        """Test watcher status is verified and returned."""
        self.controller._watchers['BO-01U:PS-CH'].is_alive.return_value = True
        self.controller._watchers['BO-01U:PS-CH'].op_mode = \
            PSConst.OpMode.Cycle
        ret = self.controller.read('BO-01U:PS-CH', 'OpMode-Sts')
        self.assertEqual(ret, PSConst.States.Cycle)

    # Write method
    def test_write(self):
        """Test write method."""
        writer = self.writers['BO-01U:PS-CH:Current-SP']
        self.controller.write('BO-01U:PS-CH', 'Current-SP', 1.0)
        writer.execute.assert_called_with(1.0)

    def test_write_strange_key(self):
        """Test write method with strange key."""
        v = self.controller.write('StrangeDevice', 'Current-SP', 1.0)
        self.assertIsNone(v)
        v = self.controller.write('BO-01U:PS-CH', 'StrangeField', 1.0)
        self.assertIsNone(v)

    def test_write_operation_mode_slowref_pru(self):
        """Test writing slowref pru controller methods."""
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.SlowRef)
        self.pru_controller.pru_sync_stop.assert_called()

    def test_write_operation_mode_slowref(self):
        """Test writing slowref sync stop is called."""
        writer = self.writers['BO-01U:PS-CH:OpMode-Sel']
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.SlowRef)
        writer.execute.assert_called_with(PSConst.OpMode.SlowRef)

    def test_write_operation_mode_slowref_sync_pru(self):
        """Test writing slowref sync calls pru methods."""
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.SlowRefSync)
        self.pru_controller.pru_sync_stop.assert_called()

    def test_write_operation_mode_slowrefsync(self):
        """Test writing slowrefsync."""
        writer = self.writers['BO-01U:PS-CH:OpMode-Sel']
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.SlowRefSync)
        writer.execute.assert_called_with(PSConst.OpMode.SlowRefSync)

    @mock.patch('siriuspy.pwrsupply.controller._Watcher')
    def test_write_operation_mode_cycle_pru(self, watcher):
        """Test writing cycle operation mode calls pru methods."""
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.Cycle)
        self.pru_controller.pru_sync_stop.assert_called()
        self.pru_controller.pru_sync_start(PRUConst.SYNC_MODE.BRDCST)

    @mock.patch('siriuspy.pwrsupply.controller._Watcher')
    def test_write_operation_mode_cycle_set_current(self, watcher):
        """Test current is set with cycle offset."""
        self.readers['BO-01U:PS-CH:CycleOffset-RB'].read.return_value = 5.0
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.Cycle)
        cur_writer = self.writers['BO-01U:PS-CH:Current-SP']
        cur_writer.execute.assert_called_with(5.0)

    @mock.patch('siriuspy.pwrsupply.controller._Watcher')
    def test_write_operation_mode_cycle(self, watcher):
        """Test writing cycle operation mode."""
        writer = self.writers['BO-01U:PS-CH:OpMode-Sel']
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.Cycle)
        writer.execute.assert_called_with(PSConst.OpMode.Cycle)

    @mock.patch('siriuspy.pwrsupply.controller._Watcher')
    def test_write_operation_mode_migwfm_pru(self, watcher):
        """Test writing migwfm operation mode."""
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.MigWfm)
        self.pru_controller.pru_sync_stop.assert_called()
        self.pru_controller.pru_sync_start(PRUConst.SYNC_MODE.MIGEND)

    @mock.patch('siriuspy.pwrsupply.controller._Watcher')
    def test_write_operation_mode_migwfm(self, watcher):
        """Test writing cycle operation mode."""
        writer = self.writers['BO-01U:PS-CH:OpMode-Sel']
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.MigWfm)
        writer.execute.assert_called_with(PSConst.OpMode.MigWfm)

    @mock.patch('siriuspy.pwrsupply.controller._Watcher')
    def test_write_operation_mode_rmpwfm_pru(self, watcher):
        """Test writing migwfm operation mode."""
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.MigWfm)
        self.pru_controller.pru_sync_stop.assert_called()
        self.pru_controller.pru_sync_start(PRUConst.SYNC_MODE.RMPEND)

    @mock.patch('siriuspy.pwrsupply.controller._Ramp')
    @mock.patch('siriuspy.pwrsupply.controller._Watcher')
    def test_write_operation_mode_rmpwfm(self, watcher, ramp):
        """Test writing cycle operation mode."""
        writer = self.writers['BO-01U:PS-CH:OpMode-Sel']
        self.controller.write(
            'BO-01U:PS-CH', 'OpMode-Sel', PSConst.OpMode.RmpWfm)
        writer.execute.assert_called_with(PSConst.OpMode.RmpWfm)

    def test_write_pwrstate_on(self):
        """Test turn power supply on."""
        self.readers['BO-01U:PS-CH:PwrState-Sel'].value = 0
        sp = self.readers['BO-01U:PS-CH:Current-SP']
        writer = self.writers['BO-01U:PS-CH:PwrState-Sel']
        self.controller.write('BO-01U:PS-CH', 'PwrState-Sel', 1)
        sp.apply.assert_called_with(0.0)
        writer.execute.assert_called_with(1)

    def test_write_pwrstate_off(self):
        """Test turn power supply on."""
        self.readers['BO-01U:PS-CH:PwrState-Sel'].value = 0
        sp = self.readers['BO-01U:PS-CH:Current-SP']
        writer = self.writers['BO-01U:PS-CH:PwrState-Sel']
        self.controller.write('BO-01U:PS-CH', 'PwrState-Sel', 0)
        sp.apply.assert_called_with(0.0)
        writer.execute.assert_called_with(0)

    @mock.patch.object(StandardPSController, '_get_siggen_arg_values')
    def test_write_cycle_type(self, cfg):
        """Test writing cycle type."""
        cfg.return_value = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        writer = self.writers['BO-01U:PS-CH:CycleType-Sel']
        self.controller.write('BO-01U:PS-CH', 'CycleType-Sel', 1)
        writer.execute.assert_called_with(
            [1, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    @mock.patch.object(StandardPSController, '_get_siggen_arg_values')
    def test_write_cycle_number_cycles(self, cfg):
        """Test writing cycle type."""
        cfg.return_value = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        writer = self.writers['BO-01U:PS-CH:CycleNrCycles-SP']
        self.controller.write('BO-01U:PS-CH', 'CycleNrCycles-SP', 10)
        writer.execute.assert_called_with(
            [0, 10, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    @mock.patch.object(StandardPSController, '_get_siggen_arg_values')
    def test_write_set_cycle_frequency(self, cfg):
        """Test writing cycle type."""
        cfg.return_value = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        writer = self.writers['BO-01U:PS-CH:CycleFreq-SP']
        self.controller.write('BO-01U:PS-CH', 'CycleFreq-SP', 0.3)
        writer.execute.assert_called_with(
            [0, 0, 0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    @mock.patch.object(StandardPSController, '_get_siggen_arg_values')
    def test_write_cycle_amplitude(self, cfg):
        """Test writing cycle type."""
        cfg.return_value = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        writer = self.writers['BO-01U:PS-CH:CycleAmpl-SP']
        self.controller.write('BO-01U:PS-CH', 'CycleAmpl-SP', 1.0)
        writer.execute.assert_called_with(
            [0, 0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    @mock.patch.object(StandardPSController, '_get_siggen_arg_values')
    def test_write_cycle_offset(self, cfg):
        """Test writing cycle type."""
        cfg.return_value = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        writer = self.writers['BO-01U:PS-CH:CycleOffset-SP']
        self.controller.write('BO-01U:PS-CH', 'CycleOffset-SP', 1.0)
        writer.execute.assert_called_with(
            [0, 0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])

    @mock.patch.object(StandardPSController, '_get_siggen_arg_values')
    def test_write_cycle_aux_param(self, cfg):
        """Test writing cycle type."""
        cfg.return_value = [0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        writer = self.writers['BO-01U:PS-CH:CycleAuxParam-SP']
        self.controller.write(
            'BO-01U:PS-CH', 'CycleAuxParam-SP', [1.0, 1.0, 1.0, 1.0])
        writer.execute.assert_called_with(
            [0, 0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0])


if __name__ == '__main__':
    unittest.main()
