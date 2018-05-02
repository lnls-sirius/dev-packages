#!/usr/bin/env python-sirius

"""Module to test AS-AP-ChromCorr Soft IOC pvs module."""

import unittest
from unittest import mock
from siriuspy import util
from siriuspy.csdevice.opticscorr import Const
import as_ap_opticscorr.chrom.pvs as pvs


valid_interface = (
    'select_ioc',
    'get_pvs_section',
    'get_pvs_vaca_prefix',
    'get_pvs_prefix',
    'get_corr_fams',
    'get_pvs_database',
    'print_banner_and_save_pv_list',
)


class TestASAPOpticsCorrChromPvs(unittest.TestCase):
    """Test AS-AP-ChromCorr Soft IOC."""

    def setUp(self):
        """Setup tests."""
        self.si_sfams = Const.SI_SFAMS_CHROMCORR
        self.bo_sfams = Const.BO_SFAMS_CHROMCORR
        csdevice_patcher = mock.patch(
            "as_ap_opticscorr.chrom.pvs._get_database",
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
        for accelerator in ['SI', 'BO']:
            pvs.select_ioc(accelerator)
            acc = pvs.get_pvs_section()
            vaca_prefix = pvs.get_pvs_vaca_prefix()
            prefix = pvs.get_pvs_prefix()
            sfams = pvs.get_corr_fams()
            self.assertIn(acc.lower(), prefix.lower())
            self.assertIn(vaca_prefix.lower(), prefix.lower())
            self.assertIn('ChromCorr', prefix)
            self.assertGreaterEqual(len(sfams), 2)

    def test_get_pvs_section(self):
        """Test get_pvs_section."""
        for accelerator in ['SI', 'BO']:
            pvs.select_ioc(accelerator)
            self.assertIsInstance(pvs.get_pvs_section(), str)
            self.assertEqual(pvs.get_pvs_section().lower(),
                             accelerator.lower())

    def test_get_pvs_vaca_prefix(self):
        """Test get_pvs_vaca_prefix."""
        self.assertIsInstance(pvs.get_pvs_vaca_prefix(), str)

    def test_get_pvs_prefix(self):
        """Test get_pvs_prefix."""
        for accelerator in ['SI', 'BO']:
            pvs.select_ioc(accelerator)
            self.assertIsInstance(pvs.get_pvs_prefix(), str)
            self.assertIn('ChromCorr', pvs.get_pvs_prefix())

    def test_get_corr_fams(self):
        """Test get_corr_fams."""
        pvs.select_ioc('SI')
        self.assertIsInstance(pvs.get_corr_fams(), tuple)
        self.assertEqual(len(pvs.get_corr_fams()), 15)
        for fam in self.si_sfams:
            self.assertIn(fam, pvs.get_corr_fams())

        pvs.select_ioc('BO')
        self.assertIsInstance(pvs.get_corr_fams(), tuple)
        self.assertEqual(len(pvs.get_corr_fams()), 2)
        for fam in self.bo_sfams:
            self.assertIn(fam, pvs.get_corr_fams())

    def test_get_pvs_database(self):
        """Test get_pvs_database."""
        pvs.get_pvs_database()
        self.mock_csdevice.assert_called()

    @mock.patch("as_ap_opticscorr.chrom.pvs._util")
    def test_print_banner_and_save_pv_list(self, util):
        """Test print_banner_and_save_pv_list."""
        for accelerator in ['SI', 'BO']:
            pvs.select_ioc(accelerator)
            pvs.print_banner_and_save_pv_list()
            util.print_ioc_banner.assert_called()
            util.save_ioc_pv_list.assert_called()


if __name__ == "__main__":
    unittest.main()
