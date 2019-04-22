#!/usr/bin/env python-sirius

"""Module to test AS-AP-CurrInfo Charge Soft IOC pvs module."""

import unittest
from unittest import mock
import siriuspy.util as util
import as_ap_currinfo.charge.pvs as pvs


valid_interface = (
    'get_pvs_vaca_prefix',
    'get_pvs_prefix',
    'get_pvs_database',
    'print_banner',
)


class TestASAPCurrInfoChargePvs(unittest.TestCase):
    """Test AS-AP-CurrInfo Charge Soft IOC."""

    def setUp(self):
        """Set tests up."""
        csdevice_patcher = mock.patch(
            "as_ap_currinfo.charge.pvs._get_database",
            autospec=True)
        self.addCleanup(csdevice_patcher.stop)
        self.mock_csdevice = csdevice_patcher.start()

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(pvs, valid_interface,
                                                      print_flag=True)
        self.assertTrue(valid)

    def test_get_pvs_vaca_prefix(self):
        """Test get_pvs_vaca_prefix."""
        self.assertIsInstance(pvs.get_pvs_vaca_prefix(), str)

    def test_get_pvs_prefix(self):
        """Test get_pvs_prefix."""
        self.assertIsInstance(pvs.get_pvs_prefix(), str)
        self.assertIn('CurrInfo', pvs.get_pvs_prefix())

    def test_get_pvs_database(self):
        """Test get_pvs_database."""
        pvs.get_pvs_database()
        self.mock_csdevice.assert_called()

    @mock.patch("as_ap_currinfo.charge.pvs._util")
    def test_print_banner(self, util):
        """Test print_banner."""
        pvs.print_banner()
        util.print_ioc_banner.assert_called_once()


if __name__ == "__main__":
    unittest.main()
