"""Test E2SController class."""
import unittest
from unittest import mock

from siriuspy.csdevice.pwrsupply import get_ps_propty_database
from tests.pwrsupply.variables import values, dict_values
from siriuspy.pwrsupply.e2scontroller import DeviceInfo, E2SController


def read_variables(device_id, variable_id):
    """Mock PRUController read_variables."""
    return values[variable_id]


class TestE2SController(unittest.TestCase):
    """Test E2SController public methods behaviour."""

    def setUp(self):
        """Watcher class is mocked. Set up E2SController object."""
        self.database = self._get_db()
        # print(self.database.keys())
        self.devices_info = {'BO-01U:PS-CH': DeviceInfo('BO-01U:PS-CH', 1),
                             'BO-01U:PS-CV': DeviceInfo('BO-01U:PS-CV', 2)}
        self.pru_controller = mock.Mock()
        self.pru_controller.read_variables.side_effect = read_variables
        self.pru_controller.pru_curve_read.return_value = \
            self.database['WfmData-RB']['value']
        self.pru_controller.pru_sync_mode = 92
        self.pru_controller.pru_curve_block = 1
        self.pru_controller.pru_sync_pulse_count = 10
        self.pru_controller.queue_length = 0

        self.hw_values = values
        self.hw_dict_values = dict_values
        self.hw_dict_values.update({
            'Reset-Cmd': 0,
            'Abort-Cmd': 0,
            'WfmData-RB': self.database['WfmData-RB']['value'],
            'PRUSyncMode-Mon': 1,
            'PRUBlockIndex-Mon': 1,
            'PRUSyncPulseCount-Mon': 10,
            'PRUCtrlQueueSize-Mon': 0})

        self.controller = E2SController(
            self.pru_controller, self.devices_info, 'FBP', self.database)

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

    def _append_dev_name(self, dev_name):
        new_dict = {}
        for key, val in self.hw_dict_values.items():
            new_dict[dev_name + ':' + key] = val
        return new_dict

    # def test_epics_2_bsmp_dict(self):
    #     """Test epics_2_bsmp constant dict values."""
    #     self.assertEqual(len(self.controller.epics_2_bsmp), 18)
    #     self.assertEqual(self.controller.epics_2_bsmp['PwrState-Sts'], 0)
    #     self.assertEqual(self.controller.epics_2_bsmp['OpenLoop-Mon'], 0)
    #     self.assertEqual(self.controller.epics_2_bsmp['OpMode-Sts'], 0)
    #     self.assertEqual(self.controller.epics_2_bsmp['CtrlMode-Mon'], 0)
    #     self.assertEqual(self.controller.epics_2_bsmp['Current-RB'], 1)
    #     self.assertEqual(self.controller.epics_2_bsmp['CurrentRef-Mon'], 2)
    #     self.assertEqual(self.controller.epics_2_bsmp['Version-Cte'], 3)
    #     self.assertEqual(self.controller.epics_2_bsmp['CycleEnbl-Mon'], 6)
    #     self.assertEqual(self.controller.epics_2_bsmp['CycleType-Sts'], 7)
    #     self.assertEqual(self.controller.epics_2_bsmp['CycleNrCycles-RB'], 8)
    #     self.assertEqual(self.controller.epics_2_bsmp['CycleIndex-Mon'], 9)
    #     self.assertEqual(self.controller.epics_2_bsmp['CycleFreq-RB'], 10)
    #     self.assertEqual(self.controller.epics_2_bsmp['CycleAmpl-RB'], 11)
    #     self.assertEqual(self.controller.epics_2_bsmp['CycleOffset-RB'], 12)
    #     self.assertEqual(self.controller.epics_2_bsmp['CycleAuxParam-RB'], 13)
    #     self.assertEqual(self.controller.epics_2_bsmp['IntlkSoft-Mon'], 25)
    #     self.assertEqual(self.controller.epics_2_bsmp['IntlkHard-Mon'], 26)
    #     self.assertEqual(self.controller.epics_2_bsmp['Current-Mon'], 27)

    def test_setpoint_initialization(self):
        """Test object setpoints is correctly initialized."""
        setpoints = ('PwrState-Sel', 'OpMode-Sel', 'Current-SP',
                     'CycleType-Sel', 'CycleNrCycles-SP', 'CycleFreq-SP',
                     'CycleAmpl-SP', 'CycleOffset-SP', 'CycleAuxParam-SP',
                     'Reset-Cmd', 'Abort-Cmd', 'WfmData-SP')
        dict_values.update({
            'Reset-Cmd': 0,
            'Abort-Cmd': 0,
            'WfmData-RB': self.database['WfmData-RB']['value']})
        for dev_name in self.devices_info:
            # self.assertEqual(
            #     len(self.controller._setpoints[dev_name]), len(setpoints))
            for setpoint in setpoints:
                self.assertIn(setpoint, self.controller._fields)
                readback = \
                    setpoint.replace('-Sel', '-Sts').replace('-SP', '-RB')
                self.assertEqual(
                    dict_values[readback],
                    self.controller._fields[setpoint][dev_name].value)

    def test_read_all(self):
        """Test read all method."""
        for dev_name in self.devices_info:
            dict_values = self._append_dev_name(dev_name)
            values = self.controller.read_all(dev_name)
            for key, val in dict_values.items():
                self.assertIn(key, values)
                self.assertEqual(val, values[key])

    def test_read(self):
        """Test read method."""
        val = self.controller.read('BO-01U:PS-CH', 'PwrState-Sel')
        self.assertEqual(val, 1)
        val = self.controller.read('BO-01U:PS-CH', 'PwrState-Sts')
        self.assertEqual(val, 1)
        val = self.controller.read('BO-01U:PS-CH', 'WfmData-RB')
        self.assertEqual(val, [0.0 for _ in range(4000)])

    def test_write_pwrstate_off(self):
        """Test setting pwrstate."""
        dev = 'BO-01U:PS-CH'
        field = 'PwrState-Sel'
        value = 0
        self.controller.write(dev, field, value)
        self.pru_controller.exec_functions.assert_called_with((1,), 1)
        self.assertEqual(self.controller.read(dev, field), value)
        self.assertEqual(self.controller.read(dev, 'Current-SP'), 0.0)
        self.assertEqual(self.controller.read(dev, 'OpMode-Sel'), 0)

    def test_write_pwrstate_on(self):
        """Test setting pwrstate."""
        dev = 'BO-01U:PS-CH'
        field = 'PwrState-Sel'
        value = 1
        # Call turn on and close loop
        calls = [mock.call((1,), 0), mock.call((1,), 3)]
        self.controller.write(dev, field, value)
        # time.sleep.assert_called_with(0.3)
        self.assertEqual(
            self.pru_controller.exec_functions.call_args_list, calls)
        self.assertEqual(self.controller.read(dev, field), value)
        self.assertEqual(self.controller.read(dev, 'Current-SP'), 0.0)
        self.assertEqual(self.controller.read(dev, 'OpMode-Sel'), 0)

    def test_write_opmode_slowref(self):
        """Test setting opmode to SlowRef."""
        dev = 'BO-01U:PS-CH'
        field = 'OpMode-Sel'
        value = 0
        # Set opmode to slowref
        self.controller.write(dev, field, value)

        # Call set_slowref and disable_siggen
        expected_calls = [mock.call((1,), 4, 3), mock.call((1,), 26)]
        calls = self.pru_controller.exec_functions.call_args_list
        self.assertEqual(calls, expected_calls)

        # Assert opmode setpoint is set
        self.assertEqual(self.controller.read(dev, field), 0)
        # How to _stop_watchers was called?

    def test_write_opmode_slowrefsync(self):
        """Test setting opmode to SlowRef."""
        dev = 'BO-01U:PS-CH'
        field = 'OpMode-Sel'
        value = 1
        # Set opmode to slowref
        self.controller.write(dev, field, value)

        # Call set_slowrefsync and disable_siggen
        # self.pru_controller.pru_curve_write_slowref_sync.assert_called()
        self.pru_controller.exec_functions.assert_called_with((1,), 4, 4)

        # Assert opmode setpoint is set
        self.assertEqual(self.controller.read(dev, field), 1)

    @mock.patch('siriuspy.pwrsupply.e2scontroller._Watcher', autospec=True)
    def test_write_opmode_cycle(self, watcher):
        """Test setting opmode to SlowRef."""
        dev = 'BO-01U:PS-CH'
        field = 'OpMode-Sel'
        value = 2
        # Set opmode to slowref
        self.controller.write(dev, field, value)

        # Call set_slowrefsync and disable_siggen
        expected_calls = [mock.call((1,), 16, 0.0), mock.call((1,), 4, 5)]
        calls = self.pru_controller.exec_functions.call_args_list
        self.assertEqual(calls, expected_calls)

        # Assert opmode setpoint is set
        self.assertEqual(self.controller.read(dev, field), 2)

        # Watcher thread is started
        watcher.assert_called_with(
            self.controller, dev, value)
        watcher.return_value.start.assert_called()

    @mock.patch('siriuspy.pwrsupply.e2scontroller._Watcher', autospec=True)
    def test_write_opmode_rmpwfm(self, watcher):
        """Test setting opmode to SlowRef."""
        dev = 'BO-01U:PS-CH'
        field = 'OpMode-Sel'
        value = 3
        # Set opmode to slowref
        self.controller.write(dev, field, value)

        # Call set_slowrefsync and disable_siggen
        self.pru_controller.exec_functions.assert_called_with((1,), 4, 3)

        # Assert opmode setpoint is set
        self.assertEqual(self.controller.read(dev, field), 3)

        # Watcher thread is started
        watcher.assert_called_with(
            self.controller, dev, value)
        watcher.return_value.start.assert_called()

    @mock.patch('siriuspy.pwrsupply.e2scontroller._Watcher', autospec=True)
    def test_write_opmode_migwfm(self, watcher):
        """Test setting opmode to SlowRef."""
        dev = 'BO-01U:PS-CH'
        field = 'OpMode-Sel'
        value = 4
        # Set opmode to slowref
        self.controller.write(dev, field, value)

        # Call set_slowrefsync and disable_siggen
        self.pru_controller.exec_functions.assert_called_with((1,), 4, 3)

        # Assert opmode setpoint is set
        self.assertEqual(self.controller.read(dev, field), 4)

        # Watcher thread is started
        watcher.assert_called_with(
            self.controller, dev, value)
        watcher.return_value.start.assert_called()

    def test_write_opmode_strange(self):
        """Test strange value."""
        dev = 'BO-01U:PS-CH'
        field = 'OpMode-Sel'
        value = 10
        # Set opmode to strange value
        self.controller.write(dev, field, value)

        # exec_functions not called
        self.pru_controller.exec_functions.assert_not_called()
        self.assertNotEqual(self.controller.read(dev, field), value)

    def test_write_reset(self):
        """Test reset command."""
        dev = ('BO-01U:PS-CH', 'BO-01U:PS-CV')
        field = 'Reset-Cmd'
        value = 10
        # Send resert command
        self.controller.write(dev, field, value)

        # Assert exec_functions was assert_called
        self.pru_controller.exec_functions.assert_called_with((1, 2), 6)
        self.assertEqual(self.controller.read(dev[0], field), 1)
        self.assertEqual(self.controller.read(dev[1], field), 1)

    def _test_write_abort(self):
        """Test reset command."""
        with self.assertRaises(NotImplementedError):
            self.controller.write('BO-01U:PS-CH', 'Abort-Cmd', 1)

    def test_write_set_cycle_type(self):
        """Test set cycle type."""
        dev = 'BO-01U:PS-CH'
        field = 'CycleType-Sel'
        value = 1
        # Set
        self.controller.write(dev, field, value)
        # Assert
        self.pru_controller.exec_functions.assert_called_with(
            (1,), 23, [1, 1, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0])
        self.assertEqual(self.controller.read(dev, field), 1)

    def test_write_set_cycle_nr_cycle(self):
        """Test set number of cycles."""
        dev = 'BO-01U:PS-CH'
        field = 'CycleNrCycles-SP'
        value = 100
        # Set
        self.controller.write(dev, field, value)
        # Assert
        self.pru_controller.exec_functions.assert_called_with(
            (1,), 23, [2, 100, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0])
        self.assertEqual(self.controller.read(dev, field), 100)

    def test_write_set_cycle_frequency(self):
        """Test set cycle frequency."""
        dev = 'BO-01U:PS-CH'
        field = 'CycleFreq-SP'
        value = 0.3
        # Set
        self.controller.write(dev, field, value)
        # Assert
        self.pru_controller.exec_functions.assert_called_with(
            (1,), 23, [2, 1, 0.3, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0])
        self.assertEqual(self.controller.read(dev, field), 0.3)

    def test_write_set_cycle_amplitude(self):
        """Test set cycle amplitude."""
        dev = 'BO-01U:PS-CH'
        field = 'CycleAmpl-SP'
        value = 5.0
        # Set
        self.controller.write(dev, field, value)
        # Assert
        self.pru_controller.exec_functions.assert_called_with(
            (1,), 23, [2, 1, 0.0, 5.0, 0.0, 1.0, 1.0, 1.0, 0.0])
        self.assertEqual(self.controller.read(dev, field), 5.0)

    def test_write_set_cycle_offset(self):
        """Test set cycle offset."""
        dev = 'BO-01U:PS-CH'
        field = 'CycleOffset-SP'
        value = 0.5
        # Set
        self.controller.write(dev, field, value)
        # Assert
        self.pru_controller.exec_functions.assert_called_with(
            (1,), 23, [2, 1, 0.0, 1.0, 0.5, 1.0, 1.0, 1.0, 0.0])
        self.assertEqual(self.controller.read(dev, field), 0.5)

    def test_write_set_aux_params(self):
        """Test set cycle aux params."""
        dev = 'BO-01U:PS-CH'
        field = 'CycleAuxParam-SP'
        value = [2.0, 2.0, 2.0, 2.0]
        # Set
        self.controller.write(dev, field, value)
        # Assert
        self.pru_controller.exec_functions.assert_called_with(
            (1,), 23, [2, 1, 0.0, 1.0, 0.0, 2.0, 2.0, 2.0, 2.0])
        self.assertEqual(
            self.controller.read(dev, field), value)

    def _test_write_set_wfmdata_sp(self):
        """Test set wfmdata sp."""
        dev = 'BO-01U:PS-CH'
        field = 'WfmData-SP'
        value = list(range(4000))
        # Set
        self.controller.write(dev, field, value)
        # Assert
        # self.assertEqual(self.controller.read(dev, field), value)
        self.pru_controller.pru_curve_write.assert_called_with(
            self.devices_info[dev].id, value)


if __name__ == '__main__':
    unittest.main()
