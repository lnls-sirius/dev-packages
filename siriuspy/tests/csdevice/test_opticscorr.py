#!/usr/bin/env python-sirius

"""Unittest module for opticscorr.py."""

import unittest
from siriuspy import util
from siriuspy.csdevice import opticscorr
from siriuspy.csdevice.opticscorr import (
    get_chrom_database,
    get_tune_database,
)


public_interface = (
        'OFFONTYP',
        'PROPADDTYP',
        'Const',
        'get_chrom_database',
        'get_tune_database',
    )


class TestOpticsCorrCSDevice(unittest.TestCase):
    """Test siriuspy.csdevice.opticscorr module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                opticscorr,
                public_interface)
        self.assertTrue(valid)

    def test_get_chrom_database(self):
        """Test get_chrom_database."""
        for accelerator in ['SI', 'BO']:
            if accelerator == 'SI':
                sfams = ('SFA1', 'SFA2', 'SDA1', 'SDA2', 'SDA3',
                         'SFB1', 'SFB2', 'SDB1', 'SDB2', 'SDB3',
                         'SFP1', 'SFP2', 'SDP1', 'SDP2', 'SDP3')
            elif accelerator == 'BO':
                sfams = ('SF', 'SD')
            db = get_chrom_database(accelerator)
            self.assertIsInstance(db, dict)
            self.assertTrue('Version-Cte' in db)
            self.assertTrue('Log-Mon' in db)
            self.assertTrue('ChromX-SP' in db)
            self.assertTrue('ChromX-RB' in db)
            self.assertTrue('ChromY-SP' in db)
            self.assertTrue('ChromY-RB' in db)
            self.assertTrue('ApplyCorr-Cmd' in db)
            self.assertTrue('ConfigName-SP' in db)
            self.assertTrue('ConfigName-RB' in db)
            self.assertTrue('RespMat-Mon' in db)
            self.assertTrue('NominalChrom-Mon' in db)
            self.assertTrue('NominalSL-Mon' in db)
            self.assertTrue('ConfigMA-Cmd' in db)
            self.assertTrue('Status-Mon' in db)
            self.assertTrue('StatusLabels-Cte' in db)

            for fam in sfams:
                self.assertTrue('SL' + fam + '-Mon' in db)
                self.assertEqual(db['SL' + fam + '-Mon']['unit'], '1/m^2')
            if accelerator == 'SI':
                self.assertTrue('CorrMeth-Sel' in db)
                self.assertTrue('CorrMeth-Sts' in db)
                self.assertTrue('SyncCorr-Sel' in db)
                self.assertTrue('SyncCorr-Sts' in db)
                self.assertTrue('ConfigTiming-Cmd' in db)

    def test_get_tune_database(self):
        """Test get_tune_database."""
        for accelerator in ['SI', 'BO']:
            if accelerator == 'SI':
                qfams = ('QFA', 'QFB', 'QFP',
                         'QDA', 'QDB1', 'QDB2', 'QDP1', 'QDP2')
            elif accelerator == 'BO':
                qfams = ('QF', 'QD')
            db = get_tune_database(accelerator)
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
            self.assertTrue('StatusLabels-Cte' in db)

            for fam in qfams:
                self.assertTrue('RefKL' + fam + '-Mon' in db)
                self.assertEqual(db['RefKL' + fam + '-Mon']['unit'], '1/m')
                self.assertTrue('DeltaKL' + fam + '-Mon' in db)
                self.assertEqual(db['DeltaKL' + fam + '-Mon']['unit'], '1/m')
            if accelerator == 'SI':
                self.assertTrue('CorrMeth-Sel' in db)
                self.assertTrue('CorrMeth-Sts' in db)
                self.assertTrue('SyncCorr-Sel' in db)
                self.assertTrue('SyncCorr-Sts' in db)
                self.assertTrue('ConfigTiming-Cmd' in db)


if __name__ == "__main__":
    unittest.main()
