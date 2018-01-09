#!/usr/bin/env python-sirius
"""Test simulation of pulsed power supply."""
import unittest
from unittest import mock
from siriuspy.pulsedps.model import PulsedPowerSupplySim


def mock_psdata(testcase):
    """Mock PSData."""
    data_patcher = mock.patch(
        'siriuspy.pulsedps.model._PSData', autospec=True)
    testcase.addCleanup(data_patcher.stop)
    testcase.data_mock = data_patcher.start()
    type(testcase.data_mock.return_value).propty_database = \
        mock.PropertyMock(return_value={
            'Voltage-RB': {'hihi': 12, 'lolo': 0},
            'Voltage-Mon': {'hihi': 12, 'lolo': 0}})


class TestPUPowerSupplySimOff(unittest.TestCase):
    """Test pulsed power supply behaviour.

    pwr_state == off;
    ctrl_mode == remote.
    """

    def setUp(self):
        """Create a power supply."""
        mock_psdata(self)
        self._ps = PulsedPowerSupplySim(psname='SI-01SA:PU-InjDpK')

    def test_init(self):
        """Test initial values."""
        self.assertEqual(self._ps.pwrstate_sts, 0)
        self.assertEqual(self._ps.ctrlmode_mon, 0)

    def test_get_voltage_sp(self):
        """Test reading voltage_sp."""
        self.assertEqual(self._ps.voltage_sp, 0)

    def test_set_voltage_sp(self):
        """Test reading voltage_sp."""
        self._ps.voltage_sp = 10.5
        self.assertEqual(self._ps.voltage_sp, 10.5)

    def test_voltage_rb_is_set(self):
        """Test voltage_rb is set when we set the set point."""
        self._ps.voltage_sp = 10.5
        self.assertEqual(self._ps.voltage_rb, 10.5)

    def test_voltage_mon(self):
        """Test voltageref_mon is not set we set voltage sp."""
        self._ps.voltage_sp = 10.5
        self.assertEqual(self._ps.voltage_mon, 0)

    def test_pwrstate_sel(self):
        """Test prwstate_sel."""
        self.assertEqual(self._ps.pwrstate_sel, 0)

    def test_set_pwrstate_sel(self):
        """Test prwstate_sel."""
        self._ps.pwrstate_sel = 1
        self.assertEqual(self._ps.pwrstate_sel, 1)

    def test_pwrstate_sts(self):
        """Test prwstate_sts."""
        self._ps.pwrstate_sel = 1
        self.assertEqual(self._ps.pwrstate_sts, 1)

    def test_pulsed_sel(self):
        """Test pulsed_sel."""
        self.assertEqual(self._ps.pulsed_sel, 0)

    def test_set_pulsed_sel(self):
        """Test pulsed_sel."""
        self._ps.pulsed_sel = 1
        self.assertEqual(self._ps.pulsed_sel, 1)

    def test_pulsed_sts(self):
        """Test pulsed_sts is not set."""
        self._ps.pulsed_sel = 1
        self.assertEqual(self._ps.pulsed_sts, 0)


class TestPUPowerSupplySimOn(unittest.TestCase):
    """Test pulsed power supply behaviour.

    pwr_state == on;
    ctrl_mode == remote.
    """

    def setUp(self):
        """Create a power supply."""
        # Mock PSData
        mock_psdata(self)
        self._ps = PulsedPowerSupplySim(psname='SI-01SA:PU-InjDpK')
        self._ps.pwrstate_sel = 1

    def test_init(self):
        """Test initial values."""
        self.assertEqual(self._ps.pwrstate_sts, 1)
        self.assertEqual(self._ps.ctrlmode_mon, 0)

    def test_get_voltage_sp(self):
        """Test reading voltage_sp."""
        self.assertEqual(self._ps.voltage_sp, 0)

    def test_set_voltage_sp(self):
        """Test reading voltage_sp."""
        self._ps.voltage_sp = 10.5
        self.assertEqual(self._ps.voltage_sp, 10.5)

    def test_voltage_rb_is_set(self):
        """Test voltage_rb is set when we set the set point."""
        self._ps.voltage_sp = 10.5
        self.assertEqual(self._ps.voltage_rb, 10.5)

    def test_voltage_mon(self):
        """Test voltageref_mon is not set we set voltage sp."""
        self._ps.voltage_sp = 10.5
        self.assertEqual(self._ps.voltage_mon, 10.5)

    def test_pwrstate_sel(self):
        """Test prwstate_sel."""
        self.assertEqual(self._ps.pwrstate_sel, 1)

    def test_set_pwrstate_sel(self):
        """Test prwstate_sel."""
        self._ps.pwrstate_sel = 1
        self.assertEqual(self._ps.pwrstate_sel, 1)

    def test_pwrstate_sts(self):
        """Test prwstate_sts."""
        self._ps.pwrstate_sel = 1
        self.assertEqual(self._ps.pwrstate_sts, 1)

    def test_pulsed_sel(self):
        """Test pulsed_sel."""
        self.assertEqual(self._ps.pulsed_sel, 0)

    def test_set_pulsed_sel(self):
        """Test pulsed_sel."""
        self._ps.pulsed_sel = 1
        self.assertEqual(self._ps.pulsed_sel, 1)

    def test_pulsed_sts(self):
        """Test pulsed_sts is not set."""
        self._ps.pulsed_sel = 1
        self.assertEqual(self._ps.pulsed_sts, 1)


class TestPUPowerSupplySimReset(unittest.TestCase):
    """Test pulsed power supply behaviour.

    pwr_state == on;
    ctrl_mode == remote.
    """

    def setUp(self):
        """Set PS properties and then issue a reset."""
        # Mock PSData
        mock_psdata(self)
        self._ps = PulsedPowerSupplySim(psname='SI-01SA:PU-InjDpK')

        self._ps.pwrstate_sel = 1
        self._ps.voltage_sp = 10.5
        self._ps.pulsed_sel = 1

        self._ps.reset = 10

    def test_reset(self):
        """Test reset incremented."""
        self.assertEqual(self._ps.reset, 1)

    def test_voltage_sp_not_changed(self):
        """Test voltage sp remains the same after reset is issued."""
        self.assertEqual(self._ps.voltage_sp, 10.5)

    def test_voltage_rb_resets(self):
        """Test voltage rb is reseted."""
        self.assertEqual(self._ps.voltage_rb, 0)

    def test_voltage_mon_resets(self):
        """Test voltage mon is reseted."""
        self.assertEqual(self._ps.voltage_mon, 0)

    def test_pwrstate_sel_not_changed(self):
        """Test that pwr state sel remains the same after reset is issued."""
        self.assertEqual(self._ps.pwrstate_sel, 1)

    def test_pwrstate_sts_resets(self):
        """Test pwrstate sts is reseted."""
        self.assertEqual(self._ps.pwrstate_sts, 0)

    def test_pulsed_sel_not_changed(self):
        """Test that pulsed sel reamins the same after reset is issued."""
        self.assertEqual(self._ps.pulsed_sel, 1)

    def test_pulsed_sts_resets(self):
        """Test that pulsed sts is reset."""
        self.assertEqual(self._ps.pwrstate_sts, 0)


class TestPUPowerSupplySimLocalMode(unittest.TestCase):
    """Test pulsed power supply behaviour when ps is in local mode."""

    def setUp(self):
        """Create and set ps to local mode."""
        mock_psdata(self)
        self._ps = PulsedPowerSupplySim(psname='SI-01SA:PU-InjDpK')

        self._ps.pwrstate_sel = 1
        self._ps.voltage_sp = 10.5
        self._ps.pulsed_sel = 1

        self._ps._ctrlmode_mon = 1

    def test_reset(self):
        """Test reset does not affect the ps."""
        self._ps.reset = 10
        self.assertEqual(self._ps.reset, 0)
        self.assertEqual(self._ps.voltage_rb, 10.5)
        self.assertEqual(self._ps.voltage_mon, 10.5)
        self.assertEqual(self._ps.pwrstate_sel, 1)
        self.assertEqual(self._ps.pwrstate_sts, 1)
        self.assertEqual(self._ps.pulsed_sel, 1)
        self.assertEqual(self._ps.pulsed_sts, 1)

    def test_voltage_sp(self):
        """Test voltage sp does not affect the ps."""
        self._ps.voltage_sp = 5.1
        self.assertEqual(self._ps.voltage_sp, 10.5)
        self.assertEqual(self._ps.voltage_rb, 10.5)
        self.assertEqual(self._ps.voltage_mon, 10.5)

    def test_pwrstate_sel(self):
        """Test voltage sp does not affect the ps."""
        self._ps.pwrstate_sel = 0
        self.assertEqual(self._ps.pwrstate_sel, 1)
        self.assertEqual(self._ps.pwrstate_sts, 1)

    def test_pulsed_sel(self):
        """Test pulsed sel does not affect the ps."""
        self._ps.pulsed_sel = 0
        self.assertEqual(self._ps.pulsed_sel, 1)
        self.assertEqual(self._ps.pulsed_sts, 1)


class TestPUPowerSupplySimLimits(unittest.TestCase):
    """Test voltage limits."""

    def setUp(self):
        """Create ps."""
        mock_psdata(self)
        self._ps = PulsedPowerSupplySim(psname='SI-01SA:PU-InjDpK')

        self._ps.pwrstate_sel = 1

    def test_set_voltage_above_limit(self):
        """Test setting voltage sp above limit."""
        self._ps.voltage_sp = 12.5
        self.assertEqual(self._ps.voltage_sp, 12.5)
        self.assertEqual(self._ps.voltage_rb, 12)
        self.assertEqual(self._ps.voltage_mon, 12)

    def test_set_voltage_below_limit(self):
        """Test setting voltage sp below limit."""
        self._ps.voltage_sp = -1.5
        self.assertEqual(self._ps.voltage_sp, -1.5)
        self.assertEqual(self._ps.voltage_rb, 0)
        self.assertEqual(self._ps.voltage_mon, 0)


if __name__ == "__main__":
    unittest.main()
