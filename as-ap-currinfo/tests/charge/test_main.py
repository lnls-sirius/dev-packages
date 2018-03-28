#!/usr/bin/env python3.6

"""Module to test AS-AP-CurrInfo Charge Soft IOC main module."""

import unittest
from unittest import mock
import siriuspy.util as util
from as_ap_currinfo.charge.charge import _PCASDriver
from as_ap_currinfo.charge.main import App


valid_interface = (
    'init_class',
    'driver',
    'process',
    'read',
    'write',
    'pvs_database'
)


class TestASAPCurrInfoChargeMain(unittest.TestCase):
    """Test AS-AP-CurrInfo Charge Soft IOC."""

    def setUp(self):
        """Initialize Soft IOC."""
        self.mock_driver = mock.create_autospec(_PCASDriver)
        App.init_class()

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(App, valid_interface,
                                                      print_flag=True)
        self.assertTrue(valid)

    def test_write_ChargeCalcIntvl(self):
        """Test write ChargeCalcIntvl-SP."""
        app = App(self.mock_driver)
        app.write('ChargeCalcIntvl-SP', 100)
        self.mock_driver.setParam.assert_called_with(
            'ChargeCalcIntvl-RB', 100)


if __name__ == "__main__":
    unittest.main()
