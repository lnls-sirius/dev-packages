#!/usr/local/bin/python-sirius
"""Test PulsedPowerSupply class.

Requirements:
    Analog Signals:
    - Set tension
    - Read tension
    - Read pulsed current waveform
    Digital Signals:
    - On/Off
    - Enable/Disable pulses
    - Reset command
    Read:
    - External interlock
    - Local/Remote
"""
import unittest
from unittest import mock

import epics

from siriuspy.pulsedps import properties
from siriuspy.pulsedps.model import PulsedPowerSupply


class PulsedPowerSupplyTest(unittest.TestCase):
    """Basic test suite for PulsedPowerSupply."""

    @mock.patch.object(PulsedPowerSupply, "_get_db", autospec=True)
    def setUp(self, mock_db):
        """Executed before every test case."""
        mock_db.return_value = \
            {properties.TensionSP: {"hilim": 11.0, "lolim": 0.0}}
        self.ps = PulsedPowerSupply("SI-Fam:PS-QDA")

    @mock.patch.object(epics.PV, "put", autospec=True)
    def test_set_tension(self, mock_put):
        """Test set the tension via epics channel."""
        attr = properties.TensionSP
        self.ps.tension_sp = 10
        mock_put.assert_called_with(self.ps._controller[attr], 10)

    @mock.patch.object(epics.PV, "put", autospec=True)
    def test_tension_hilim(self, mock_put):
        """Test set the tension via epics channel."""
        attr = properties.TensionSP
        self.ps.tension_sp = 12
        mock_put.assert_called_with(self.ps._controller[attr], 11)

    @mock.patch.object(epics.PV, "put", autospec=True)
    def test_tension_lolim(self, mock_put):
        """Test set the tension via epics channel."""
        attr = properties.TensionSP
        self.ps.tension_sp = -1
        mock_put.assert_called_with(self.ps._controller[attr], 0)

    @mock.patch.object(epics.PV, "put", autospec=True)
    def test_set_pwrstate_sel(self, mock_put):
        """Test setting the ps on."""
        attr = properties.PwrStateSel
        self.ps.pwrstate_sel = 1
        mock_put.assert_called_with(self.ps._controller[attr], 1)

    @mock.patch.object(epics.PV, "put", autospec=True)
    def test_enable_pulses(self, mock_put):
        """Test enabling pulses."""
        attr = properties.EnablePulsesSel
        self.ps.enablepulses_sel = 1
        mock_put.assert_called_with(self.ps._controller[attr], 1)

    @mock.patch.object(epics.PV, "add_callback", autospec=True)
    def test_callback(self, mock_dev):
        """Test setting a callback."""
        def foo():
            print("x")
        self.ps.add_callback_to_pv(properties.TensionSP, foo)
        mock_dev.assert_called_with(
            self.ps._controller[properties.TensionSP], foo)

    @mock.patch.object(epics.Device, "add_callback", autospec=True)
    def test_callback_exception(self, mock_dev):
        """Test exception is raised when a non callable is passed as cb."""
        foo = 1
        self.assertRaises(
            AssertionError,
            self.ps.add_callback_to_pv, properties.TensionSP, foo)
        mock_dev.assert_not_called()


if __name__ == "__main__":
    unittest.main()
