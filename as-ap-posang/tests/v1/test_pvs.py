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
        pvs.select_ioc('TransportLine')
        self.assertIsInstance(pvs.get_pvs_database(), dict)

        # Test IOC interface: pv names
        self.assertTrue('Version-Cte' in pvs.get_pvs_database())
        self.assertTrue('Log-Mon' in pvs.get_pvs_database())
        self.assertTrue('DeltaPosX-SP' in pvs.get_pvs_database())
        self.assertTrue('DeltaPosX-RB' in pvs.get_pvs_database())
        self.assertTrue('DeltaAngX-SP' in pvs.get_pvs_database())
        self.assertTrue('DeltaAngX-RB' in pvs.get_pvs_database())
        self.assertTrue('DeltaPosY-SP' in pvs.get_pvs_database())
        self.assertTrue('DeltaPosY-RB' in pvs.get_pvs_database())
        self.assertTrue('DeltaAngY-SP' in pvs.get_pvs_database())
        self.assertTrue('DeltaAngY-RB' in pvs.get_pvs_database())
        self.assertTrue('ConfigName-SP' in pvs.get_pvs_database())
        self.assertTrue('ConfigName-RB' in pvs.get_pvs_database())
        self.assertTrue('RespMatX-Mon' in pvs.get_pvs_database())
        self.assertTrue('RespMatY-Mon' in pvs.get_pvs_database())
        self.assertTrue('RefKickCH1-Mon' in pvs.get_pvs_database())
        self.assertTrue('RefKickCH2-Mon' in pvs.get_pvs_database())
        self.assertTrue('RefKickCV1-Mon' in pvs.get_pvs_database())
        self.assertTrue('RefKickCV2-Mon' in pvs.get_pvs_database())
        self.assertTrue('SetNewRefKick-Cmd' in pvs.get_pvs_database())
        self.assertTrue('ConfigMA-Cmd' in pvs.get_pvs_database())
        self.assertTrue('Status-Mon' in pvs.get_pvs_database())
        self.assertTrue('Status-Cte' in pvs.get_pvs_database())

        # Test IOC interface: pvs units
        self.assertEqual(
            pvs.get_pvs_database()['DeltaPosX-SP']['unit'], 'mm')
        self.assertEqual(
            pvs.get_pvs_database()['DeltaPosX-RB']['unit'], 'mm')
        self.assertEqual(
            pvs.get_pvs_database()['DeltaAngX-SP']['unit'], 'mrad')
        self.assertEqual(
            pvs.get_pvs_database()['DeltaAngX-RB']['unit'], 'mrad')
        self.assertEqual(
            pvs.get_pvs_database()['DeltaPosY-SP']['unit'], 'mm')
        self.assertEqual(
            pvs.get_pvs_database()['DeltaPosY-RB']['unit'], 'mm')
        self.assertEqual(
            pvs.get_pvs_database()['DeltaAngY-SP']['unit'], 'mrad')
        self.assertEqual(
            pvs.get_pvs_database()['DeltaAngY-RB']['unit'], 'mrad')
        self.assertEqual(
            pvs.get_pvs_database()['RefKickCH1-Mon']['unit'], 'mrad')
        self.assertEqual(
            pvs.get_pvs_database()['RefKickCH2-Mon']['unit'], 'mrad')
        self.assertEqual(
            pvs.get_pvs_database()['RefKickCV1-Mon']['unit'], 'mrad')
        self.assertEqual(
            pvs.get_pvs_database()['RefKickCV2-Mon']['unit'], 'mrad')

    @mock.patch("as_ap_posang.pvs._util")
    def test_print_banner_and_save_pv_list(self, util):
        """Test print_banner_and_save_pv_list."""
        pvs.select_ioc('TransportLine')
        pvs.print_banner_and_save_pv_list()
        util.print_ioc_banner.assert_called_once()
        util.save_ioc_pv_list.assert_called_once()


if __name__ == "__main__":
    unittest.main()
