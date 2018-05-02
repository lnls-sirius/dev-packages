#!/usr/bin/env python3.6

"""Module to test AS-AP-PosAng Soft IOC pvs module."""

import unittest
from unittest import mock
import siriuspy.util as util
import as_ap_posang.pvs as pvs


valid_interface = (
    'select_ioc',
    'get_pvs_section',
    'get_pvs_vaca_prefix',
    'get_pvs_prefix',
    'get_pvs_database',
    'print_banner_and_save_pv_list',
)


class TestASAPPosAngPvs(unittest.TestCase):
    """Test AS-AP-PosAng Soft IOC."""

    def setUp(self):
        """Setup tests."""
        csdevice_patcher = mock.patch(
            "as_ap_posang.pvs._get_database",
            autospec=True)
        self.addCleanup(csdevice_patcher.stop)
        self.mock_csdevice = csdevice_patcher.start()

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(pvs, valid_interface,
                                                      print_flag=True)
        self.assertTrue(valid)

    def test_select_ioc(self):
        """Test select_ioc."""
        pvs.select_ioc('TransportLine')
        tl = pvs.get_pvs_section()
        vaca_prefix = pvs.get_pvs_vaca_prefix()
        prefix = pvs.get_pvs_prefix()
        self.assertIsInstance(tl, str)
        self.assertIsInstance(vaca_prefix, str)
        self.assertIsInstance(prefix, str)
        self.assertIn(tl.lower(), prefix.lower())
        self.assertIn(vaca_prefix.lower(), prefix.lower())
        self.assertIn('PosAng', prefix)

    def test_get_pvs_section(self):
        """Test get_pvs_section."""
        pvs.select_ioc('TransportLine')
        self.assertIsInstance(pvs.get_pvs_section(), str)
        self.assertEqual(pvs.get_pvs_section().lower(),
                         'TransportLine'.lower())

    def test_get_pvs_vaca_prefix(self):
        """Test get_pvs_vaca_prefix."""
        self.assertIsInstance(pvs.get_pvs_vaca_prefix(), str)

    def test_get_pvs_prefix(self):
        """Test get_pvs_prefix."""
        pvs.select_ioc('TransportLine')
        self.assertIsInstance(pvs.get_pvs_prefix(), str)
        self.assertIn('PosAng', pvs.get_pvs_prefix())

    def test_get_pvs_database(self):
        """Test get_pvs_database."""
        pvs.get_pvs_database()
        self.mock_csdevice.assert_called()

    @mock.patch("as_ap_posang.pvs._util")
    def test_print_banner_and_save_pv_list(self, util):
        """Test print_banner_and_save_pv_list."""
        pvs.select_ioc('TransportLine')
        pvs.print_banner_and_save_pv_list()
        util.print_ioc_banner.assert_called_once()
        util.save_ioc_pv_list.assert_called_once()


if __name__ == "__main__":
    unittest.main()
