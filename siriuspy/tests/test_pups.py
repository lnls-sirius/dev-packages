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

    @mock.patch("siriuspy.pulsedps.model._PUData", autospec=True)
    def setUp(self, mock_data):
        """Executed before every test case."""
        self.ps = PulsedPowerSupply("FakePS")

    @mock.patch.object(epics.Device, "put", autospec=True)
    def test_set_tension(self, mock_put):
        """Test set the tension via epics channel."""
        attr = properties.TensionSP
        self.ps.tension_sp = 10
        mock_put.assert_called_with(self.ps._controller, attr, 10)

    @mock.patch.object(epics.Device, "put", autospec=True)
    def test_set_pwrstate_sel(self, mock_put):
        """Test setting the ps on."""
        attr = properties.PwrStateSel
        self.ps.pwrstate_sel = 1
        mock_put.assert_called_with(self.ps._controller, attr, 1)

    @mock.patch.object(epics.Device, "put", autospec=True)
    def test_enable_pulses(self, mock_put):
        """Test enabling pulses."""
        attr = properties.EnablePulsesSel
        self.ps.enablepulses_sel = 1
        mock_put.assert_called_with(self.ps._controller, attr, 1)


if __name__ == "__main__":
    unittest.main()
