#!/usr/bin/env python-sirius

"""Module to test AS-AP-TuneCorr Soft IOC main module."""

import unittest
from unittest import mock
import siriuspy.util as util
from as_ap_opticscorr.tune.main import App


valid_interface = (
    'pvs_database',
    'init_database',
    'process',
    'write',
)


class TestASAPTuneCorrMain(unittest.TestCase):
    """Test AS-AP-TuneCorr Soft IOC."""

    def setUp(self):
        """Initialize Soft IOC."""
        self.q_ok = {
            'matrix': [
                [2.7280, 8.5894, 4.2995, 0.5377,
                 1.0906, 2.0004, 0.5460, 1.0012],
                [-1.3651, -3.5532, -1.7657, -2.3652,
                 -4.7518, -1.9781, -2.3601, -0.9839]],
            'nominal KLs': [0.7146, 1.2344, 1.2344, -0.2270,
                            -0.2809, -0.4783, -0.2809, -0.4783]}
        self.qfams = ['QFA', 'QFB', 'QFP',
                      'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2']
        cs_patcher = mock.patch(
            "as_ap_opticscorr.tune.main._ConfigDBClient", autospec=True)
        self.addCleanup(cs_patcher.stop)
        self.mock_cs = cs_patcher.start()
        self.mock_cs().get_config_value.return_value = self.q_ok
        pv_patcher = mock.patch(
            "as_ap_opticscorr.tune.main._PV", autospec=True)
        self.addCleanup(pv_patcher.stop)
        self.mock_pv = pv_patcher.start()
        self.app = App('SI')

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            App, valid_interface, print_flag=True)
        self.assertTrue(valid)

    def test_write_ok_syncoff_ApplyDelta(self):
        """Test write on ApplyDelta-Cmd in normal operation, sync off."""
        self.app._sync_corr = 0

        self.app._status = 0
        self.assertFalse(self.app.write('ApplyDelta-Cmd', 0))
        count = self.mock_pv.return_value.put.call_count
        self.assertEqual(count, len(self.qfams))

        self.app._status = 0b10000
        self.assertFalse(self.app.write('ApplyDelta-Cmd', 0))
        count = self.mock_pv.return_value.put.call_count
        self.assertEqual(count, 2*len(self.qfams))

    def test_write_ok_syncon_ApplyDelta(self):
        """Test write on ApplyDelta-Cmd in normal operation, sync on."""
        self.app._sync_corr = 1
        self.app._status = 0
        self.assertFalse(self.app.write('ApplyDelta-Cmd', 0))
        count = self.mock_pv.return_value.put.call_count
        self.assertEqual(count, 1+len(self.qfams))

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
        self.assertEqual(self.app._nominal_matrix,
                         [item for sublist in self.q_ok['matrix']
                          for item in sublist])
        self.assertEqual(self.app._qfam_nomkl, self.q_ok['nominal KLs'])

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
        self.assertTrue(count, 2*len(self.qfams))

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
        self.assertTrue(count, 6)

    def test_write_connerror_ConfigTiming(self):
        """Test write on ConfigTiming-Cmd in connection error."""
        self.mock_pv.return_value.connected = False
        self.assertFalse(self.app.write('ConfigTiming-Cmd', 0))
        self.mock_pv.return_value.put.assert_not_called()

    def test_write_ok_SetNewRefKL(self):
        """Test write on SetNewRefKL-Cmd in normal operation."""
        self.mock_pv.return_value.get.return_value = 0.0
        self.app._status = 0
        self.assertFalse(self.app.write('SetNewRefKL-Cmd', 0))
        self.assertEqual(self.app._delta_tunex, 0)
        self.assertEqual(self.app._delta_tuney, 0)
        for i in range(len(self.qfams)):
            self.assertEqual(self.app._lastcalc_deltakl[i], 0)

    def test_write_connerror_SetNewRefKL(self):
        """Test write on SetNewRefKL-Cmd on connection error."""
        self.app._status = 0b00001
        self.assertFalse(self.app.write('SetNewRefKL-Cmd', 0))
        self.mock_pv.return_value.get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
