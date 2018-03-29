#!/usr/bin/env python3.6

"""Module to test AS-AP-CurrInfo Lifetime Soft IOC main module."""

import unittest
from unittest import mock
import siriuspy.util as util
from as_ap_currinfo.lifetime.lifetime import _PCASDriver
from as_ap_currinfo.lifetime.main import App
import as_ap_currinfo.lifetime.pvs as pvs


valid_interface = (
    'init_class',
    'driver',
    'process',
    'read',
    'write',
    'pvs_database'
)


class TestASAPCurrInfoLifetimeMain(unittest.TestCase):
    """Test AS-AP-CurrInfo Lifetime Soft IOC."""

    def setUp(self):
        """Initialize Soft IOC."""
        self.mock_driver = mock.create_autospec(_PCASDriver)
        pvs.select_ioc('si')
        App.init_class()
        printbanner_patcher = mock.patch(
            "as_ap_currinfo.lifetime.pvs.print_banner_and_save_pv_list",
            autospec=True)
        self.addCleanup(printbanner_patcher.stop)
        self.mock_printbanner = printbanner_patcher.start()

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(App, valid_interface,
                                                      print_flag=True)
        self.assertTrue(valid)

    def test_write_BuffSizeMax(self):
        """Test write BuffSizeMax-SP."""
        app = App(self.mock_driver)

        app.write('BuffSizeMax-SP', -1)
        self.assertEqual(app._current_buffer.nr_max_points, None)
        self.mock_driver.setParam.assert_called_with('BuffSizeMax-RB', 0)

        app.write('BuffSizeMax-SP', 0)
        self.assertEqual(app._current_buffer.nr_max_points, None)
        self.mock_driver.setParam.assert_called_with('BuffSizeMax-RB', 0)

        app.write('BuffSizeMax-SP', 100)
        self.assertEqual(app._current_buffer.nr_max_points, 100)
        self.mock_driver.setParam.assert_called_with('BuffSizeMax-RB', 100)

    def test_write_SplIntvl(self):
        """Test write SplIntvl-SP."""
        app = App(self.mock_driver)

        app.write('SplIntvl-SP', 100)
        self.assertEqual(app._current_buffer.time_window, 100)
        self.mock_driver.setParam.assert_called_with('SplIntvl-RB', 100)

    @mock.patch("as_ap_currinfo.lifetime.main._siriuspy_epics")
    def test_write_BuffRst_Cmd(self, epics):
        """Test write BuffRst-Cmd."""
        app = App(self.mock_driver)
        app.write('BuffRst-Cmd', 0)
        epics.SiriusPVTimeSerie.return_value.clearserie.assert_called_once()

    def test_write_BuffAutoRst(self):
        """Test write BuffAutoRst-Sel."""
        app = App(self.mock_driver)

        app.write('BuffAutoRst-Sel', 1)
        self.mock_driver.setParam.assert_called_with('BuffAutoRst-Sts', 1)


if __name__ == "__main__":
    unittest.main()
