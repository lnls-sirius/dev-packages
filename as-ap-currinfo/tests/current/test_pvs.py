#!/usr/bin/env python3.6

"""Module to test AS-AP-CurrInfo Current Soft IOC pvs module."""

import unittest
from unittest import mock
import siriuspy.util as util
import as_ap_currinfo.current.pvs as pvs


valid_interface = (
    'select_ioc',
    'get_pvs_section',
    'get_pvs_vaca_prefix',
    'get_pvs_prefix',
    'get_pvs_database',
    'print_banner_and_save_pv_list',
)


class TestASAPCurrInfoCurrentPvs(unittest.TestCase):
    """Test AS-AP-CurrInfo Current Soft IOC."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(pvs, valid_interface,
                                                      print_flag=True)
        self.assertTrue(valid)

    def test_select_ioc(self):
        """Test select_ioc."""
        pvs.select_ioc('Accelerator')
        acc = pvs.get_pvs_section()
        vaca_prefix = pvs.get_pvs_vaca_prefix()
        prefix = pvs.get_pvs_prefix()
        self.assertIsInstance(acc, str)
        self.assertIsInstance(vaca_prefix, str)
        self.assertIsInstance(prefix, str)
        self.assertIn(acc.lower(), prefix.lower())
        self.assertIn(vaca_prefix.lower(), prefix.lower())
        self.assertIn('CurrInfo', prefix)

    def test_get_pvs_section(self):
        """Test get_pvs_section."""
        pvs.select_ioc('Accelerator')
        self.assertIsInstance(pvs.get_pvs_section(), str)
        self.assertEqual(pvs.get_pvs_section().lower(),
                         'Accelerator'.lower())

    def test_get_pvs_vaca_prefix(self):
        """Test get_pvs_vaca_prefix."""
        self.assertIsInstance(pvs.get_pvs_vaca_prefix(), str)

    def test_get_pvs_prefix(self):
        """Test get_pvs_prefix."""
        pvs.select_ioc('Accelerator')
        self.assertIsInstance(pvs.get_pvs_prefix(), str)
        self.assertIn('CurrInfo', pvs.get_pvs_prefix())

    def test_get_pvs_database(self):
        """Test get_pvs_database."""

        # Test IOC interface: pv names
        pvs.select_ioc('Accelerator')
        self.assertIsInstance(pvs.get_pvs_database(), dict)
        self.assertTrue('Version-Cte' in pvs.get_pvs_database())
        self.assertTrue('Current-Mon' in pvs.get_pvs_database())
        self.assertTrue('StoredEBeam-Mon' in pvs.get_pvs_database())

        pvs.select_ioc('SI')
        self.assertIsInstance(pvs.get_pvs_database(), dict)
        self.assertTrue('DCCT-Sel' in pvs.get_pvs_database())
        self.assertTrue('DCCT-Sts' in pvs.get_pvs_database())
        self.assertTrue('DCCTFltCheck-Sel' in pvs.get_pvs_database())
        self.assertTrue('DCCTFltCheck-Sts' in pvs.get_pvs_database())

        pvs.select_ioc('BO')
        self.assertIsInstance(pvs.get_pvs_database(), dict)
        self.assertFalse('DCCT-Sel' in pvs.get_pvs_database())
        self.assertFalse('DCCT-Sts' in pvs.get_pvs_database())
        self.assertFalse('DCCTFltCheck-Sel' in pvs.get_pvs_database())
        self.assertFalse('DCCTFltCheck-Sts' in pvs.get_pvs_database())

        # Test IOC interface: pvs units
        self.assertEqual(pvs.get_pvs_database()['Current-Mon']['unit'], 'mA')

    @mock.patch("as_ap_currinfo.current.pvs._util")
    def test_print_banner_and_save_pv_list(self, util):
        """Test print_banner_and_save_pv_list."""
        pvs.print_banner_and_save_pv_list()
        util.print_ioc_banner.assert_called_once()
        util.save_ioc_pv_list.assert_called_once()


if __name__ == "__main__":
    unittest.main()
