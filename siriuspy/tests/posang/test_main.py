#!/usr/bin/env python-sirius

"""Module to test AS-AP-PosAng Soft IOC main module."""

import unittest
from unittest import mock
import siriuspy.util as util
from as_ap_posang.main import App


valid_interface = (
    'init_database',
    'pvs_database',
    'process',
    'write',
)


class TestASAPPosAngMain(unittest.TestCase):
    """Test AS-AP-PosAng Soft IOC."""

    def setUp(self):
        """Initialize Soft IOC."""
        self.q_ok = {
            'respm-x': [[4.3444644271865913, 0.28861438350278495],
                        [0.93275939885026393, 1.0003702976563984]],
            'respm-y': [[5.6604558827773026, 2.4137865916000418],
                        [1.065850170973988, 0.9767489447759754]]}
        cs_patcher = mock.patch(
            "as_ap_posang.main._ConfigDBClient", autospec=True)
        self.addCleanup(cs_patcher.stop)
        self.mock_cs = cs_patcher.start()
        self.mock_cs().get_config_value.return_value = self.q_ok
        ps_patcher = mock.patch("as_ap_posang.main._PV", autospec=True)
        self.addCleanup(ps_patcher.stop)
        self.mock_pv = ps_patcher.start()
        self.app = App('TB', 'ch-sept')

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            App, valid_interface, print_flag=True)
        self.assertTrue(valid)

    def test_write_statuserror_DeltaPosAng(self):
        """Test write DeltaPosY-SP & DeltaAngY-SP on status error."""
        self.app._status = 0x1
        self.app.write('DeltaPosX-SP', 0.01)
        self.app.write('DeltaAngX-SP', 0.01)
        self.app.write('DeltaPosY-SP', 0.01)
        self.app.write('DeltaAngY-SP', 0.01)
        self.mock_pv.return_value.put.assert_not_called()

    def test_write_ok_SetNewRefKick(self):
        """Test write SetNewRefKick-Cmd in normal operation."""
        self.app._status = 0
        self.app.write('SetNewRefKick-Cmd', 0)
        self.assertEqual(self.app._orbx_deltapos, 0)
        self.assertEqual(self.app._orbx_deltaang, 0)
        self.assertEqual(self.app._orby_deltapos, 0)
        self.assertEqual(self.app._orby_deltaang, 0)

    def test_write_ok_ConfigPS(self):
        """Test write ConfigPS-Cmd in normal operation."""
        self.mock_pv.return_value.connected = True
        self.app.write('ConfigPS-Cmd', 0)
        count = self.mock_pv.return_value.put.call_count
        self.assertTrue(count, 2*2)

    def test_write_connerror_Cmds(self):
        """Test write SetNewRefKick-Cmd/ConfigPS-Cmd on connection error."""
        self.mock_pv.return_value.connected = False
        self.app.write('SetNewRefKick-Cmd', 0)
        self.app.write('ConfigPS-Cmd', 0)
        self.mock_pv.return_value.get.assert_not_called()
        self.mock_pv.return_value.put.assert_not_called()

    def test_write_ok_ConfigName(self):
        """Test write ConfigName-SP in normal operation."""
        self.app._status = 0
        self.app.write('ConfigName-SP', 'Default')
        flat_mx = [item for sublist in self.q_ok['respm-x']
                   for item in sublist]
        flat_my = [item for sublist in self.q_ok['respm-y']
                   for item in sublist]
        self.assertEqual(self.app._respmat_x, flat_mx)
        self.assertEqual(self.app._respmat_y, flat_my)


if __name__ == "__main__":
    unittest.main()
