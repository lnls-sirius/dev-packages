#!/usr/bin/env python3.6

"""Module to test AS-AP-TuneCorr Soft IOC main module."""

import unittest
from unittest import mock
import siriuspy.util as util
from as_ap_opticscorr.tune.tune import _PCASDriver
from as_ap_opticscorr.tune.main import App
from as_ap_opticscorr.tune.pvs import select_ioc


valid_interface = (
    'init_class',
    'driver',
    'process',
    'read',
    'write',
    'pvs_database'
)


class TestASAPTuneCorrMain(unittest.TestCase):
    """Test AS-AP-TuneCorr Soft IOC."""

    def setUp(self):
        """Initialize Soft IOC."""
        self.mock_driver = mock.create_autospec(_PCASDriver)
        select_ioc('si')
        App.init_class()
        self.q_ok = {'code': 200,
                     'result': {'value': {
                        'matrix': [
                            [2.7280, 8.5894, 4.2995, 0.5377,
                             1.0906, 2.0004, 0.5460, 1.0012],
                            [-1.3651, -3.5532, -1.7657, -2.3652,
                             -4.7518, -1.9781, -2.3601, -0.9839]],
                        'nominal KLs': [0.7146, 1.2344, 1.2344, -0.2270,
                                        -0.2809, -0.4783, -0.2809, -0.4783]}}}
        self.q_error = {'code': 404,
                        'result': {'value': {'matrix': [],
                                             'nominal KLs': []}}}
        self.qfams = ['QFA', 'QFB', 'QFP',
                      'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2']
        self.get_value = 100
        cs_patcher = mock.patch("as_ap_opticscorr.tune.main._ConfigService",
                                autospec=True)
        epics_patcher = mock.patch("as_ap_opticscorr.tune.main._epics",
                                   autospec=True)
        printbanner_patcher = mock.patch(
            "as_ap_opticscorr.tune.pvs.print_banner_and_save_pv_list",
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

    def test_write_ok_syncoff_ApplyCorr(self):
        """Test write on ApplyCorr-Cmd in normal operation, sync off."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._sync_corr = 0

        app._status = 0
        self.assertFalse(app.write('ApplyCorr-Cmd', 0))
        count = self.mock_epics.PV.return_value.put.call_count
        self.assertEqual(count, len(self.qfams))

        app._status = 0b10000
        self.assertFalse(app.write('ApplyCorr-Cmd', 0))
        count = self.mock_epics.PV.return_value.put.call_count
        self.assertEqual(count, 2*len(self.qfams))

    def test_write_ok_syncon_ApplyCorr(self):
        """Test write on ApplyCorr-Cmd in normal operation, sync on."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._sync_corr = 1
        app._status = 0
        self.assertFalse(app.write('ApplyCorr-Cmd', 0))
        count = self.mock_epics.PV.return_value.put.call_count
        self.assertEqual(count, 1+len(self.qfams))

    def test_write_statuserror_ApplyCorr(self):
        """Test write on ApplyCorr-Cmd on status error."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._sync_corr = 1
        app._status = 0b10000
        self.assertFalse(app.write('ApplyCorr-Cmd', 0))
        self.mock_epics.PV.return_value.put.assert_not_called()

    def test_write_ok_ConfigName(self):
        """Test write on ConfigName-SP in normal operation."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0

        self.assertTrue(app.write('ConfigName-SP', 'Default'))
        calls = [mock.call('ConfigName-RB', 'Default'),
                 mock.call('RespMat-Mon',
                           [item for sublist in
                            self.q_ok['result']['value']['matrix']
                            for item in sublist]),
                 mock.call('NominalKL-Mon',
                           self.q_ok['result']['value']['nominal KLs'])]
        self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

        call_list = self.mock_driver.setParam.call_args_list
        count = 0
        for call in call_list:
            if 'DeltaKL' in call[0][0]:
                count += 1
        self.assertEqual(count, len(self.qfams))

    def test_write_configdberror_ConfigName(self):
        """Test write on ConfigName-SP on configdb error."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0

        self.mock_cs().get_config.return_value = self.q_error
        self.assertFalse(app.write('ConfigName-SP', 'Testing'))

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
            if 'DeltaKL' in call[0][0]:
                count += 1
        self.assertEqual(count, len(self.qfams))

    def test_write_CorrFactor(self):
        """Test write on CorrFactor-SP."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)

        self.assertTrue(app.write('CorrFactor-SP', 100))
        calls = [mock.call('CorrFactor-RB', 100)]
        self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

    def test_write_DeltaTune_nearnominal(self):
        """Test write nominal values on DeltaTuneX-SP and DeltaTuneY-SP pvs."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0
        app._qfam_refkl = {'QFA': 0.7146,
                           'QFB': 1.2344,
                           'QFP': 1.2344,
                           'QDA': -0.2270,
                           'QDB1': -0.2809,
                           'QDB2': -0.4783,
                           'QDP1': -0.2809,
                           'QDP2': -0.4783}

        for i in [0, 1]:
            app.write('CorrMeth-Sel', i)
            app.write('DeltaTuneX-SP', 0)
            app.write('DeltaTuneY-SP', 0)
            calls = []
            for fam in self.qfams:
                calls.append(mock.call('DeltaKL' + fam + '-Mon', 0.0))
            self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

    def test_write_DeltaTuneX_anyvalue_ProportionalMeth(self):
        """Test write any values on DeltaTuneX-SP pvs."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0
        app._qfam_refkl = {'QFA': 0.7146,
                           'QFB': 1.2344,
                           'QFP': 1.2344,
                           'QDA': -0.2270,
                           'QDB1': -0.2809,
                           'QDB2': -0.4783,
                           'QDP1': -0.2809,
                           'QDP2': -0.4783}
        deltakl_prop_x = [0.00102019, 0.00176227, 0.00176227, -0.00061849,
                          -0.00076535, -0.00130319, -0.00076535, -0.00130319]

        app.write('CorrFactor-SP', 100)
        app.write('CorrMeth-Sel', 0)
        app.write('DeltaTuneX-SP', 0.02)
        call_list = self.mock_driver.setParam.call_args_list
        for call in call_list:
            # Ignores the first call by app.write('CorrFactor-Sel', 100)
            if ('DeltaKL' in call[0][0]) and call[0][1] != 0.0:
                fam = call[0][0].split('DeltaKL')[1].split('-Mon')[0]
                fam_index = self.qfams.index(fam)
                self.assertAlmostEqual(call[0][1], deltakl_prop_x[fam_index])

    def test_write_DeltaTuneY_anyvalue_ProportionalMeth(self):
        """Test write any values on DeltaTuneY-SP pvs."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0
        app._qfam_refkl = {'QFA': 0.7146,
                           'QFB': 1.2344,
                           'QFP': 1.2344,
                           'QDA': -0.2270,
                           'QDB1': -0.2809,
                           'QDB2': -0.4783,
                           'QDP1': -0.2809,
                           'QDP2': -0.4783}
        deltakl_prop_y = [0.00026044, 0.00044988, 0.00044988, -0.00073238,
                          -0.00090628, -0.00154316, -0.00090628, -0.00154316]

        app.write('CorrFactor-SP', 100)
        app.write('CorrMeth-Sel', 0)
        app.write('DeltaTuneY-SP', 0.01)
        call_list = self.mock_driver.setParam.call_args_list
        for call in call_list:
            # Ignores the first call by app.write('CorrFactor-Sel', 100)
            if ('DeltaKL' in call[0][0]) and call[0][1] != 0.0:
                fam = call[0][0].split('DeltaKL')[1].split('-Mon')[0]
                fam_index = self.qfams.index(fam)
                self.assertAlmostEqual(call[0][1], deltakl_prop_y[fam_index])

    def test_write_DeltaTuneX_anyvalue_AdditionalMeth(self):
        """Test write any values on DeltaTuneX-SP pvs."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0
        app._qfam_refkl = {'QFA': 0.7146,
                           'QFB': 1.2344,
                           'QFP': 1.2344,
                           'QDA': -0.2270,
                           'QDB1': -0.2809,
                           'QDB2': -0.4783,
                           'QDP1': -0.2809,
                           'QDP2': -0.4783}
        deltakl_add_x = [0.00155816, 0.00155816, 0.00155816, -0.00083726,
                         -0.00083726, -0.00083726, -0.00083726, -0.00083726]

        app.write('CorrFactor-SP', 100)
        app.write('CorrMeth-Sel', 1)
        app.write('DeltaTuneX-SP', 0.02)
        call_list = self.mock_driver.setParam.call_args_list
        for call in call_list:
            # Ignores the first call by app.write('CorrFactor-Sel', 100)
            if ('DeltaKL' in call[0][0]) and call[0][1] != 0.0:
                fam = call[0][0].split('DeltaKL')[1].split('-Mon')[0]
                fam_index = self.qfams.index(fam)
                self.assertAlmostEqual(call[0][1], deltakl_add_x[fam_index])

    def test_write_DeltaTuneY_anyvalue_AdditionalMeth(self):
        """Test write any values on DeltaTuneY-SP pvs."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0
        app._qfam_refkl = {'QFA': 0.7146,
                           'QFB': 1.2344,
                           'QFP': 1.2344,
                           'QDA': -0.2270,
                           'QDB1': -0.2809,
                           'QDB2': -0.4783,
                           'QDP1': -0.2809,
                           'QDP2': -0.4783}
        deltakl_add_y = [0.00032417, 0.00032417, 0.00032417, -0.00097811,
                         -0.00097811, -0.00097811, -0.00097811, -0.00097811]

        app.write('CorrFactor-SP', 100)
        app.write('CorrMeth-Sel', 1)
        app.write('DeltaTuneY-SP', 0.01)
        call_list = self.mock_driver.setParam.call_args_list
        for call in call_list:
            # Ignores the first call by app.write('CorrFactor-Sel', 100)
            if ('DeltaKL' in call[0][0]) and call[0][1] != 0.0:
                fam = call[0][0].split('DeltaKL')[1].split('-Mon')[0]
                fam_index = self.qfams.index(fam)
                self.assertAlmostEqual(call[0][1], deltakl_add_y[fam_index])

    def test_write_SyncCorr(self):
        """Test write on SyncCorr-Sel."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)

        self.mock_epics.PV.return_value.connected = True
        self.assertTrue(app.write('SyncCorr-Sel', 1))
        calls = [mock.call('SyncCorr-Sts', 1),
                 mock.call('Status-Mon', app._status)]
        self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

    def test_write_ok_ConfigMA(self):
        """Test write on ConfigMA-Cmd in normal operation."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)

        self.mock_epics.PV.return_value.connected = True
        self.assertFalse(app.write('ConfigMA-Cmd', 0))
        count = self.mock_epics.PV.return_value.put.call_count
        self.assertTrue(count, 2*len(self.qfams))

    def test_write_connerror_ConfigMA(self):
        """Test write on ConfigMA-Cmd on configdb error."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)

        self.mock_epics.PV.return_value.connected = False
        self.assertFalse(app.write('ConfigMA-Cmd', 0))
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

    def test_write_ok_SetNewRefKL(self):
        """Test write on SetNewRefKL-Cmd in normal operation."""
        self.mock_epics.PV.return_value.get.return_value = 0.0
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0

        self.assertFalse(app.write('SetNewRefKL-Cmd', 0))
        calls = [mock.call('DeltaTuneX-SP', 0),
                 mock.call('DeltaTuneY-SP', 0),
                 mock.call('DeltaTuneX-RB', 0),
                 mock.call('DeltaTuneY-RB', 0)]
        self.mock_driver.setParam.assert_has_calls(calls, any_order=True)

        call_list = self.mock_driver.setParam.call_args_list
        count_lastcalcd = 0
        count_refkl = 0
        for call in call_list:
            if 'DeltaKL' in call[0][0]:
                count_lastcalcd += 1
            elif 'RefKL' in call[0][0] and '-Mon' in call[0][0]:
                count_refkl += 1
        self.assertEqual(count_lastcalcd, len(self.qfams))
        self.assertEqual(count_refkl, len(self.qfams))

    def test_write_connerror_SetNewRefKL(self):
        """Test write on SetNewRefKL-Cmd on connection error."""
        self.mock_cs().get_config.return_value = self.q_ok
        app = App(self.mock_driver)
        app._status = 0b00001

        self.assertFalse(app.write('SetNewRefKL-Cmd', 0))
        self.mock_epics.PV.return_value.get.assert_not_called()

        call_list = self.mock_driver.setParam.call_args_list
        count_deltatune = 0
        count_lastcalcd = 0
        count_refkl = 0
        for call in call_list:
            if 'DeltaTune' in call[0][0]:
                count_deltatune += 1
            elif 'DeltaKL' in call[0][0]:
                count_lastcalcd += 1
            elif 'RefKL' in call[0][0] and '-Mon' in call[0][0]:
                count_refkl += 1
        self.assertEqual(count_deltatune, 0)
        self.assertEqual(count_lastcalcd, 0)
        self.assertEqual(count_refkl, 0)


if __name__ == "__main__":
    unittest.main()
