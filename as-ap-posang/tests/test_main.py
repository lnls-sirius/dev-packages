#!/usr/bin/env python-sirius

"""Module to test AS-AP-PosAng Soft IOC main module."""

import numpy as np
import unittest
from unittest import mock
import siriuspy.util as util
from as_ap_posang.as_ap_posang import _PCASDriver
from as_ap_posang.main import App
from as_ap_posang.pvs import select_ioc


valid_interface = (
    'init_class',
    'driver',
    'process',
    'read',
    'write',
    'pvs_database'
)


class TestASAPPosAngMain(unittest.TestCase):
    """Test AS-AP-PosAng Soft IOC."""

    def setUp(self):
        """Initialize Soft IOC."""
        self.mock_driver = mock.create_autospec(_PCASDriver)
        select_ioc('ts')
        App.init_class()
        self.q_ok = {'code': 200,
                     'result': {'value': {'respm-x': [[4.3444644271865913,
                                                       0.28861438350278495],
                                                      [0.93275939885026393,
                                                       1.0003702976563984]],
                                          'respm-y': [[5.6604558827773026,
                                                       2.4137865916000418],
                                                      [1.065850170973988,
                                                       0.9767489447759754]]}}}
        self.q_error = {'code': 404,
                        'result': {'value': {'respm-x': [],
                                             'respm-y': []}}}
        self.get_value = 100
        cs_patcher = mock.patch("as_ap_posang.main._ConfigService",
                                autospec=True)
        epics_patcher = mock.patch("as_ap_posang.main._epics", autospec=True)
        printbanner_patcher = mock.patch(
            "as_ap_posang.pvs.print_banner_and_save_pv_list",
            autospec=True)
        self.addCleanup(cs_patcher.stop)
        self.addCleanup(epics_patcher.stop)
        self.addCleanup(printbanner_patcher.stop)
        self.mock_cs = cs_patcher.start()
        self.mock_epics = epics_patcher.start()
        self.mock_printbanner = printbanner_patcher.start()

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(App, valid_interface,
                                                      print_flag=True)
        self.assertTrue(valid)

    def test_write_ok_DeltaPosAngX(self):
        """Test write DeltaPosX-SP & DeltaAngX-SP in normal operation."""
        self.mock_epics.PV.return_value.get.return_value = self.get_value
        self.mock_cs().get_config.return_value = self.q_ok

        mx = np.array(self.q_ok['result']['value']['respm-x'])
        app = App(self.mock_driver)
        app._status = 0

        app.write('DeltaPosX-SP', 0.01)  # Input in mm
        app.write('DeltaAngX-SP', 0.01)  # Input in mrad
        put_call_list = self.mock_epics.PV.return_value.put.call_args_list
        delta_kick_pos = np.array([[put_call_list[0][0][0]],
                                   [put_call_list[1][0][0]]])
        delta_kick_ang = np.array([[put_call_list[2][0][0]],
                                   [put_call_list[3][0][0]]])
        delta_pos = 0.01/1000  # Output in m
        delta_ang = 0.01/1000  # Output in rad
        self.assertAlmostEqual(np.dot(mx, delta_kick_pos)[0][0], delta_pos)
        self.assertAlmostEqual(np.dot(mx, delta_kick_ang)[1][0], delta_ang)

    def test_write_ok_DeltaPosAngY(self):
        """Test write DeltaPosY-SP & DeltaAngY-SP in normal operation."""
        self.mock_epics.PV.return_value.get.return_value = self.get_value
        self.mock_cs().get_config.return_value = self.q_ok

        my = np.array(self.q_ok['result']['value']['respm-y'])
        app = App(self.mock_driver)
        app._status = 0

        app.write('DeltaPosY-SP', 0.01)  # Input in mm
        app.write('DeltaAngY-SP', 0.01)  # Input in mrad
        put_call_list = self.mock_epics.PV.return_value.put.call_args_list
        delta_kick_pos = np.array([[put_call_list[0][0][0]],
                                   [put_call_list[1][0][0]]])
        delta_kick_ang = np.array([[put_call_list[2][0][0]],
                                   [put_call_list[3][0][0]]])
        delta_pos = 0.01/1000  # Output in m
        delta_ang = 0.01/1000  # Output in rad
        self.assertAlmostEqual(np.dot(my, delta_kick_pos)[0][0], delta_pos)
        self.assertAlmostEqual(np.dot(my, delta_kick_ang)[1][0], delta_ang)

    def test_write_statuserror_DeltaPosAng(self):
        """Test write DeltaPosY-SP & DeltaAngY-SP on status error."""
        self.mock_cs().get_config.return_value = self.q_ok

        app = App(self.mock_driver)
        app._status = 0x1

        app.write('DeltaPosX-SP', 0.01)
        app.write('DeltaAngX-SP', 0.01)
        app.write('DeltaPosY-SP', 0.01)
        app.write('DeltaAngY-SP', 0.01)
        self.mock_epics.PV.return_value.put.assert_not_called()

    def test_write_ok_SetNewRefKick(self):
        """Test write SetNewRefKick-Cmd in normal operation."""
        self.mock_epics.PV.return_value.get.return_value = self.get_value
        self.mock_cs().get_config.return_value = self.q_ok

        app = App(self.mock_driver)
        app._status = 0
        app.write('SetNewRefKick-Cmd', 0)
        calls = [mock.call('DeltaPosX-SP', 0),
                 mock.call('DeltaPosX-RB', 0),
                 mock.call('DeltaAngX-SP', 0),
                 mock.call('DeltaAngX-RB', 0),
                 mock.call('DeltaPosY-SP', 0),
                 mock.call('DeltaPosY-RB', 0),
                 mock.call('DeltaAngY-SP', 0),
                 mock.call('DeltaAngY-RB', 0),
                 mock.call('RefKickCH1-Mon', self.get_value*1000),  # mrad
                 mock.call('RefKickCH2-Mon', self.get_value*1000),  # mrad
                 mock.call('RefKickCV1-Mon', self.get_value*1000),  # mrad
                 mock.call('RefKickCV2-Mon', self.get_value*1000),  # mrad
                 mock.call('SetNewRefKick-Cmd', 1)]
        self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

    def test_write_ok_ConfigMA(self):
        """Test write ConfigPS-Cmd in normal operation."""
        self.mock_cs().get_config.return_value = self.q_ok
        self.mock_epics.PV.return_value.connected = True

        app = App(self.mock_driver)

        app.write('ConfigMA-Cmd', 0)
        self.mock_epics.PV.return_value.put.assert_has_calls(
            [mock.call(1), mock.call(1), mock.call(1), mock.call(1),
             mock.call(0), mock.call(0), mock.call(0)], any_order=True)
        self.mock_driver.setParam.assert_called_with('ConfigMA-Cmd', 1)

    def test_write_connerror_Cmds(self):
        """Test write SetNewRefKick-Cmd/ConfigMA-Cmd on connection error."""
        self.mock_cs().get_config.return_value = self.q_ok
        self.mock_epics.PV.return_value.connected = False

        app = App(self.mock_driver)

        app.write('SetNewRefKick-Cmd', 0)
        app.write('ConfigMA-Cmd', 0)
        self.mock_epics.PV.return_value.get.assert_not_called()
        self.mock_epics.PV.return_value.put.assert_not_called()

    def test_write_ok_ConfigName(self):
        """Test write ConfigName-SP in normal operation."""
        self.mock_cs().get_config.return_value = self.q_ok

        app = App(self.mock_driver)
        app._status = 0

        app.write('ConfigName-SP', 'Default')
        flat_mx = [item for sublist in self.q_ok['result']['value']['respm-x']
                   for item in sublist]
        flat_my = [item for sublist in self.q_ok['result']['value']['respm-y']
                   for item in sublist]
        calls = [mock.call('RespMatX-Mon', flat_mx),
                 mock.call('RespMatY-Mon', flat_my)]
        self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

    def test_write_configdberror_ConfigName(self):
        """Test write DeltaPosY-SP & DeltaAngY-SP on configdb error."""
        self.mock_epics.PV.return_value.get.return_value = self.get_value
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0

        self.mock_cs().get_config.return_value = self.q_error
        app.write('RespMatConfigName-SP', 'Testing')
        self.mock_epics.PV.return_value.put.assert_not_called()


if __name__ == "__main__":
    unittest.main()
