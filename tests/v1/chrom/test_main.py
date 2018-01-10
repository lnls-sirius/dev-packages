#!/usr/bin/env python3.6

"""Module to test AS-AP-ChromCorr Soft IOC main module."""

import unittest
from unittest import mock
import siriuspy.util as util
from as_ap_opticscorr.chrom.chrom import _PCASDriver
from as_ap_opticscorr.chrom.main import App
from as_ap_opticscorr.chrom.pvs import select_ioc


valid_interface = (
    'init_class',
    'driver',
    'process',
    'read',
    'write',
    'pvs_database'
)


class TestASAPChromCorrMain(unittest.TestCase):
    """Test AS-AP-ChromCorr Soft IOC."""

    def setUp(self):
        """Initialize Soft IOC."""
        self.mock_driver = mock.create_autospec(_PCASDriver)
        select_ioc('si')
        App.init_class()
        self.q_ok = {'code': 200,
                     'result': {'value': {
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
                        'nominal chrom': [2.5756, 2.5033]}}}
        self.q_error = {'code': 404,
                        'result': {'value': {'matrix': [],
                                             'nominal SLs': [],
                                             'nominal chrom': []}}}
        self.sfams = ['SFA1', 'SFA2', 'SDA1', 'SDA2', 'SDA3',
                      'SFB1', 'SFB2', 'SDB1', 'SDB2', 'SDB3',
                      'SFP1', 'SFP2', 'SDP1', 'SDP2', 'SDP3']
        self.get_value = 100
        cs_patcher = mock.patch("as_ap_opticscorr.chrom.main._ConfigService",
                                autospec=True)
        epics_patcher = mock.patch("as_ap_opticscorr.chrom.main._epics",
                                   autospec=True)
        self.addCleanup(cs_patcher.stop)
        self.addCleanup(epics_patcher.stop)
        self.mock_cs = cs_patcher.start()
        self.mock_epics = epics_patcher.start()

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(App, valid_interface,
                                                      print_flag=True)
        self.assertTrue(valid)

    def test_write_ok_syncoff_ApplySL(self):
        """Test write on ApplySL-Cmd in normal operation, on sync mode off."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._sync_corr = 0

        app._status = 0
        self.assertFalse(app.write('ApplySL-Cmd', 0))
        count = self.mock_epics.PV.return_value.put.call_count
        self.assertEqual(count, len(self.sfams))

        app._status = 0b10000
        self.assertFalse(app.write('ApplySL-Cmd', 0))
        count = self.mock_epics.PV.return_value.put.call_count
        self.assertEqual(count, 2*len(self.sfams))

    def test_write_ok_syncon_ApplySL(self):
        """Test write on ApplySL-Cmd in normal operation, on sync mode on."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._sync_corr = 1
        app._status = 0
        self.assertFalse(app.write('ApplySL-Cmd', 0))
        count = self.mock_epics.PV.return_value.put.call_count
        self.assertEqual(count, 1+len(self.sfams))

    def test_write_statuserror_ApplySL(self):
        """Test write on ApplySL-Cmd on status error."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._sync_corr = 1
        app._status = 0b10000
        self.assertFalse(app.write('ApplySL-Cmd', 0))
        self.mock_epics.PV.return_value.put.assert_not_called()

    def test_write_ok_CorrParamsConfigName(self):
        """Test write on CorrParamsConfigName-SP in normal operation."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0

        self.assertTrue(app.write('CorrParamsConfigName-SP', 'Default'))
        calls = [mock.call('CorrParamsConfigName-RB', 'Default'),
                 mock.call('CorrMat-Mon',
                           [item for sublist in
                            self.q_ok['result']['value']['matrix']
                            for item in sublist]),
                 mock.call('NominalChrom-Mon',
                           self.q_ok['result']['value']['nominal chrom']),
                 mock.call('NominalSL-Mon',
                           self.q_ok['result']['value']['nominal SLs'])]
        self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

        call_list = self.mock_driver.setParam.call_args_list
        count = 0
        for call in call_list:
            if 'LastCalcd' in call[0][0]:
                count += 1
        self.assertEqual(count, len(self.sfams))

    def test_write_configdberror_CorrParamsConfigName(self):
        """Test write on CorrParamsConfigName-SP on configdb error."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0

        self.mock_cs().get_config.return_value = self.q_error
        self.assertFalse(app.write('CorrParamsConfigName-SP', 'Testing'))

    def test_write_CorrMeth(self):
        """Test write on CorrMeth-Sel."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)

        self.assertTrue(app.write('CorrMeth-Sel', 1))
        calls = [mock.call('CorrMeth-Sts', 1)]
        self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

        call_list = self.mock_driver.setParam.call_args_list
        count = 0
        for call in call_list:
            if 'LastCalcd' in call[0][0]:
                count += 1
        self.assertEqual(count, len(self.sfams))

    def test_write_Chrom_nearnominal(self):
        """Test write nominal values on ChromX-SP and ChromY-SP pvs."""
        self.mock_cs().get_config.return_value = self.q_ok

        app = App(self.mock_driver)
        app._status = 0
        for i in [0, 1]:
            app.write('CorrMeth-Sel', i)
            app.write('ChromX-SP', 2.5756)
            app.write('ChromY-SP', 2.5033)
            calls = []
            for fam in self.sfams:
                fam_index = self.sfams.index(fam)
                calls.append(mock.call(
                    'LastCalcd' + fam + 'SL-Mon',
                    self.q_ok['result']['value']['nominal SLs'][fam_index]))
            self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

    def test_write_Chrom_anyvalue_ProportionalMeth(self):
        """Test write any values on ChromX-SP and ChromY-SP pvs."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0

        sl_prop = [28.40235571,  22.37126168, -23.80279572, -13.19538641,
                   -20.76940978,  33.06864496,  28.87618811, -20.31464041,
                   -17.82846745, -25.38801553,  33.80336158,  29.40794805,
                   -20.88520228, -18.10825997, -25.78754156]

        app.write('CorrMeth-Sel', 0)
        app.write('ChromX-SP', 0.0)
        app.write('ChromY-SP', 0.0)
        call_list = self.mock_driver.setParam.call_args_list
        for call in call_list:
            if 'LastCalcd' in call[0][0]:
                fam = call[0][0].split('LastCalcd')[1].split('SL-Mon')[0]
                fam_index = self.sfams.index(fam)
                self.assertAlmostEqual(call[0][1], sl_prop[fam_index])

    def test_write_Chrom_anyvalue_AdditionalMeth(self):
        """Test write any values on ChromX-SP and ChromY-SP pvs."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0

        sl_add = [28.259838, 22.22098842, -23.91592367, -13.05041964,
                  -20.7621013, 33.11110243, 28.91196549, -20.2501808,
                  -17.77619777, -25.60488439, 33.83776046, 29.41858556,
                  -20.85980462, -18.09975068, -25.90195616]

        app.write('CorrMeth-Sel', 1)
        app.write('ChromX-SP', 0.0)
        app.write('ChromY-SP', 0.0)
        call_list = self.mock_driver.setParam.call_args_list
        for call in call_list:
            if 'LastCalcd' in call[0][0]:
                fam = call[0][0].split('LastCalcd')[1].split('SL-Mon')[0]
                fam_index = self.sfams.index(fam)
                self.assertAlmostEqual(call[0][1], sl_add[fam_index])

    def test_write_SyncCorr(self):
        """Test write on SyncCorr-Sel."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)

        self.assertTrue(app.write('SyncCorr-Sel', 1))
        calls = [mock.call('SyncCorr-Sts', 1),
                 mock.call('Status-Mon', app._status)]
        self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

    def test_write_ok_ConfigPS(self):
        """Test write on ConfigPS-Cmd in normal operation."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)

        self.mock_epics.PV.return_value.connected = True
        self.assertFalse(app.write('ConfigPS-Cmd', 0))
        count = self.mock_epics.PV.return_value.put.call_count
        self.assertTrue(count, 2*len(self.sfams))

    def test_write_connerror_ConfigPS(self):
        """Test write on ConfigPS-Cmd on configdb error."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)

        self.mock_epics.PV.return_value.connected = False
        self.assertFalse(app.write('ConfigPS-Cmd', 0))
        self.mock_epics.PV.return_value.put.assert_not_called()

    def test_write_ok_ConfigTiming(self):
        """Test write on ConfigTiming-Cmd in normal operation."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)

        self.mock_epics.PV.return_value.connected = True
        self.assertFalse(app.write('ConfigTiming-Cmd', 0))
        count = self.mock_epics.PV.return_value.put.call_count
        self.assertTrue(count, 6)

    def test_write_connerror_ConfigTiming(self):
        """Test write on ConfigTiming-Cmd in normal operation."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)

        self.mock_epics.PV.return_value.connected = False
        self.assertFalse(app.write('ConfigTiming-Cmd', 0))
        self.mock_epics.PV.return_value.put.assert_not_called()


if __name__ == "__main__":
    unittest.main()
