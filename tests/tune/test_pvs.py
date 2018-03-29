#!/usr/bin/env python3.6

"""Module to test AS-AP-TuneCorr Soft IOC pvs module."""

import unittest
from unittest import mock
import siriuspy.util as util
import as_ap_opticscorr.tune.pvs as pvs


valid_interface = (
    'select_ioc',
    'get_pvs_section',
    'get_pvs_vaca_prefix',
    'get_pvs_prefix',
    'get_corr_fams',
    'get_pvs_database',
    'print_banner_and_save_pv_list',
)


class TestASAPOpticsCorrTunePvs(unittest.TestCase):
    """Test AS-AP-TuneCorr Soft IOC."""

    def setUp(self):
        """Setup tests."""
        self.si_qfams = ['QFA', 'QFB', 'QFP',
                         'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2']
        self.bo_qfams = ['QF', 'QD']

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
            qfams = pvs.get_corr_fams()
            self.assertIn(acc.lower(), prefix.lower())
            self.assertIn(vaca_prefix.lower(), prefix.lower())
            self.assertIn('TuneCorr', prefix)
            self.assertGreaterEqual(len(qfams), 2)

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
            self.assertIn('TuneCorr', pvs.get_pvs_prefix())

    def test_get_corr_fams(self):
        """Test get_corr_fams."""
        pvs.select_ioc('SI')
        self.assertIsInstance(pvs.get_corr_fams(), list)
        self.assertEqual(len(pvs.get_corr_fams()), 8)
        for fam in self.si_qfams:
            self.assertIn(fam, pvs.get_corr_fams())

        pvs.select_ioc('BO')
        self.assertIsInstance(pvs.get_corr_fams(), list)
        self.assertEqual(len(pvs.get_corr_fams()), 2)
        for fam in self.bo_qfams:
            self.assertIn(fam, pvs.get_corr_fams())

    def test_get_pvs_database(self):
        """Test get_pvs_database."""
        for accelerator in ['SI', 'BO']:
            if accelerator == 'SI':
                qfams = self.si_qfams
            elif accelerator == 'BO':
                qfams = self.bo_qfams
            pvs.select_ioc(accelerator)
            db = pvs.get_pvs_database()
            self.assertIsInstance(db, dict)
            self.assertTrue('Version-Cte' in db)
            self.assertTrue('Log-Mon' in db)
            self.assertTrue('DeltaTuneX-SP' in db)
            self.assertTrue('DeltaTuneX-RB' in db)
            self.assertTrue('DeltaTuneY-SP' in db)
            self.assertTrue('DeltaTuneY-RB' in db)
            self.assertTrue('ApplyCorr-Cmd' in db)
            self.assertTrue('ConfigName-SP' in db)
            self.assertTrue('ConfigName-RB' in db)
            self.assertTrue('RespMat-Mon' in db)
            self.assertTrue('NominalKL-Mon' in db)
            self.assertTrue('CorrFactor-SP' in db)
            self.assertTrue('CorrFactor-RB' in db)
            self.assertTrue('ConfigMA-Cmd' in db)
            self.assertTrue('Status-Mon' in db)
            self.assertTrue('Status-Cte' in db)

            for fam in qfams:
                self.assertTrue('RefKL' + fam + '-Mon' in db)
                self.assertEqual(db['RefKL' + fam + '-Mon']['unit'], '1/m')
                self.assertTrue('DeltaKL' + fam + '-Mon' in db)
                self.assertEqual(db['DeltaKL' + fam + '-Mon']['unit'],
                                 '1/m')
            if accelerator == 'SI':
                self.assertTrue('CorrMeth-Sel' in db)
                self.assertTrue('CorrMeth-Sts' in db)
                self.assertTrue('SyncCorr-Sel' in db)
                self.assertTrue('SyncCorr-Sts' in db)
                self.assertTrue('ConfigTiming-Cmd' in db)

    @mock.patch("as_ap_opticscorr.tune.pvs._util")
    def test_print_banner_and_save_pv_list(self, util):
        """Test print_banner_and_save_pv_list."""
        for accelerator in ['SI', 'BO']:
            pvs.select_ioc(accelerator)
            pvs.print_banner_and_save_pv_list()
            util.print_ioc_banner.assert_called()
            util.save_ioc_pv_list.assert_called()


if __name__ == "__main__":
    unittest.main()
