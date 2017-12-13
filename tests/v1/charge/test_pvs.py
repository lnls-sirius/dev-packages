#!/usr/bin/env python3.6

"""Module to test AS-AP-CurrInfo Charge Soft IOC pvs module."""

import unittest
from unittest import mock
import siriuspy.util as util
import as_ap_currinfo.charge.pvs as pvs


valid_interface = (
    'get_pvs_vaca_prefix',
    'get_pvs_prefix',
    'get_pvs_database',
    'print_banner_and_save_pv_list',
)


class TestASAPCurrInfoChargePvs(unittest.TestCase):
    """Test AS-AP-CurrInfo Charge Soft IOC."""

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
        self.assertIsInstance(pvs.get_pvs_database(), dict)

        self.assertTrue('Version-Cte' in pvs.get_pvs_database())
        self.assertTrue('Charge-Mon' in pvs.get_pvs_database())
        self.assertTrue('ChargeCalcIntvl-SP' in pvs.get_pvs_database())
        self.assertTrue('ChargeCalcIntvl-RB' in pvs.get_pvs_database())

        self.assertEqual(
            pvs.get_pvs_database()['Charge-Mon']['unit'], 'A.h')
        self.assertEqual(
            pvs.get_pvs_database()['ChargeCalcIntvl-SP']['unit'], 's')
        self.assertEqual(
            pvs.get_pvs_database()['ChargeCalcIntvl-RB']['unit'], 's')

    @mock.patch("as_ap_currinfo.charge.pvs._util")
    def test_print_banner_and_save_pv_list(self, util):
        """Test print_banner_and_save_pv_list."""
        pvs.print_banner_and_save_pv_list()
        util.print_ioc_banner.assert_called_once()
        util.save_ioc_pv_list.assert_called_once()


if __name__ == "__main__":
    unittest.main()
