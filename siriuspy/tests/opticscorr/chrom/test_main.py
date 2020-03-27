#!/usr/bin/env python-sirius

"""Module to test AS-AP-ChromCorr Soft IOC main module."""

import unittest
from unittest import mock
import siriuspy.util as util
from as_ap_opticscorr.chrom.main import App


valid_interface = (
    'pvs_database',
    'init_database',
    'process',
    'write',
)


class TestASAPChromCorrMain(unittest.TestCase):
    """Test AS-AP-ChromCorr Soft IOC."""

    def setUp(self):
        """Initialize Soft IOC."""
        self.q_ok = {
            'matrix': [
                [1.2105, 0.5759, 0.3767, 0.6833, 0.2642,
                 2.4732, 1.154, 0.8185, 1.3816, 0.4859,
                 1.2563, 0.5672, 0.4101, 0.7106, 0.2702],
                [-1.0285, -0.3025, -1.1841, -1.2897, -0.6505,
                 -2.0764, -0.6426, -2.372, -2.6034, -1.2536,
                 -1.0478, -0.3373, -1.1728, -1.2834, -0.6496]],
            'nominal SLs': [
                28.7743, 22.6154, -24.448, -13.3281, -20.9911,
                34.1822, 29.6731, -21.2454, -18.3342, -26.0719,
                34.3874, 29.7755, -21.3459, -18.3422, -26.1236],
            'nominal chrom': [2.5756, 2.5033]}
        self.sfams = ['SFA1', 'SFA2', 'SDA1', 'SDA2', 'SDA3',
                      'SFB1', 'SFB2', 'SDB1', 'SDB2', 'SDB3',
                      'SFP1', 'SFP2', 'SDP1', 'SDP2', 'SDP3']
        cs_patcher = mock.patch(
            "as_ap_opticscorr.chrom.main._ConfigDBClient", autospec=True)
        self.addCleanup(cs_patcher.stop)
        self.mock_cs = cs_patcher.start()
        self.mock_cs().get_config_value.return_value = self.q_ok
        pv_patcher = mock.patch(
            "as_ap_opticscorr.chrom.main._PV", autospec=True)
        self.addCleanup(pv_patcher.stop)
        self.mock_pv = pv_patcher.start()
        self.app = App('SI')

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            App, valid_interface, print_flag=True)
        self.assertTrue(valid)

    def test_write_ok_syncoff_ApplyDelta(self):
        """Test write on ApplyDelta-Cmd in normal operation, sync mode off."""
        self.app._sync_corr = 0

        self.app._status = 0
        self.assertFalse(self.app.write('ApplyDelta-Cmd', 0))
        count = self.mock_pv.return_value.put.call_count
        self.assertEqual(count, len(self.sfams))

        self.app._status = 0b10000
        self.assertFalse(self.app.write('ApplyDelta-Cmd', 0))
        count = self.mock_pv.return_value.put.call_count
        self.assertEqual(count, 2*len(self.sfams))

    def test_write_ok_syncon_ApplyDelta(self):
        """Test write on ApplyDelta-Cmd in normal operation, sync mode on."""
        self.app._sync_corr = 1
        self.app._status = 0
        self.assertFalse(self.app.write('ApplyDelta-Cmd', 0))
        count = self.mock_pv.return_value.put.call_count
        self.assertEqual(count, 1+len(self.sfams))

    def test_write_statuserror_ApplyDelta(self):
        """Test write on ApplyDelta-Cmd on status error."""
        self.app._sync_corr = 1
        self.app._status = 0b10000
        self.assertFalse(self.app.write('ApplyDelta-Cmd', 0))
        self.mock_pv.return_value.put.assert_not_called()

    def test_write_ok_ConfigName(self):
        """Test write on ConfigName-SP in normal operation."""
        self.app._status = 0
        self.assertTrue(self.app.write('ConfigName-SP', 'Default'))
        self.assertEqual(self.app._config_name, 'Default')
        self.assertAlmostEqual(
            self.app._nominal_matrix,
            [item for sublist in self.q_ok['matrix']
             for item in sublist])
        self.assertAlmostEqual(
            self.app._nomchrom, self.q_ok['nominal chrom'])
        self.assertAlmostEqual(
            self.app._sfam_nomsl, self.q_ok['nominal SLs'])

    def test_write_CorrMeth(self):
        """Test write on CorrMeth-Sel."""
        self.assertTrue(self.app.write('CorrMeth-Sel', 1))
        self.assertEqual(self.app._corr_method, 1)

    def test_write_SyncCorr(self):
        """Test write on SyncCorr-Sel."""
        self.mock_pv.return_value.connected = True
        self.assertTrue(self.app.write('SyncCorr-Sel', 1))
        self.assertEqual(self.app._sync_corr, 1)

    def test_write_ok_ConfigPS(self):
        """Test write on ConfigPS-Cmd in normal operation."""
        self.mock_pv.return_value.connected = True
        self.assertFalse(self.app.write('ConfigPS-Cmd', 0))
        count = self.mock_pv.return_value.put.call_count
        self.assertEqual(count, 2*len(self.sfams))

    def test_write_connerror_ConfigPS(self):
        """Test write on ConfigPS-Cmd on connection error."""
        self.mock_pv.return_value.connected = False
        self.assertFalse(self.app.write('ConfigPS-Cmd', 0))
        self.mock_pv.return_value.put.assert_not_called()

    def test_write_ok_ConfigTiming(self):
        """Test write on ConfigTiming-Cmd in normal operation."""
        self.mock_pv.return_value.connected = True
        self.assertFalse(self.app.write('ConfigTiming-Cmd', 0))
        count = self.mock_pv.return_value.put.call_count
        self.assertEqual(count, 9)

    def test_write_connerror_ConfigTiming(self):
        """Test write on ConfigTiming-Cmd in connection errorn."""
        self.mock_pv.return_value.connected = False
        self.assertFalse(self.app.write('ConfigTiming-Cmd', 0))
        self.mock_pv.return_value.put.assert_not_called()


if __name__ == "__main__":
    unittest.main()
