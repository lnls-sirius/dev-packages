#!/usr/bin/env python-sirius

"""Unittest module for currinfo.py."""

from unittest import TestCase
from siriuspy import util
from siriuspy.csdevice import currinfo
from siriuspy.csdevice.currinfo import (
    get_currinfo_database,
    get_lifetime_database,
)

public_interface = (
        'ETypes',
        'Const',
        'get_currinfo_database',
        'get_lifetime_database'
    )


class TestCurrInfoCSDevice(TestCase):
    """Test siriuspy.csdevice.currinfo module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                currinfo,
                public_interface)
        self.assertTrue(valid)

    def test_get_currinfo_database(self):
        """Test get_currinfo_database."""

        # ---- SI ----
        db = get_currinfo_database('SI')
        self.assertIsInstance(db, dict)

        # PV names
        self.assertTrue('Version-Cte' in db)
        self.assertTrue('Current-Mon' in db)
        self.assertTrue('StoredEBeam-Mon' in db)
        self.assertTrue('DCCT-Sel' in db)
        self.assertTrue('DCCT-Sts' in db)
        self.assertTrue('DCCTFltCheck-Sel' in db)
        self.assertTrue('DCCTFltCheck-Sts' in db)
        self.assertTrue('Charge-Mon' in db)

        # PVs units
        self.assertEqual(db['Current-Mon']['unit'], 'mA')
        self.assertEqual(db['Charge-Mon']['unit'], 'A.h')

        # ---- BO ----
        db = get_currinfo_database('BO')
        self.assertIsInstance(db, dict)

        # PV names
        self.assertTrue('RawReadings-Mon' in db)
        self.assertTrue('Current150MeV-Mon' in db)
        self.assertTrue('Current1GeV-Mon' in db)
        self.assertTrue('Current2GeV-Mon' in db)
        self.assertTrue('Current3GeV-Mon' in db)
        self.assertTrue('Charge150MeV-Mon' in db)
        self.assertTrue('Charge1GeV-Mon' in db)
        self.assertTrue('Charge2GeV-Mon' in db)
        self.assertTrue('Charge3GeV-Mon' in db)
        self.assertTrue('RampEff-Mon' in db)

        # PVs units
        self.assertEqual(db['RawReadings-Mon']['unit'], 'mA')
        self.assertEqual(db['Current150MeV-Mon']['unit'], 'mA')
        self.assertEqual(db['Current1GeV-Mon']['unit'], 'mA')
        self.assertEqual(db['Current2GeV-Mon']['unit'], 'mA')
        self.assertEqual(db['Current3GeV-Mon']['unit'], 'mA')
        self.assertEqual(db['Charge150MeV-Mon']['unit'], 'nC')
        self.assertEqual(db['Charge1GeV-Mon']['unit'], 'nC')
        self.assertEqual(db['Charge2GeV-Mon']['unit'], 'nC')
        self.assertEqual(db['Charge3GeV-Mon']['unit'], 'nC')
        self.assertEqual(db['RampEff-Mon']['unit'], '%')

    def test_get_lifetime_database(self):
        """Test get_lifetime_database."""
        db = get_lifetime_database()
        self.assertIsInstance(db, dict)

        # PV names
        self.assertTrue('VersionLifetime-Cte' in db)
        self.assertTrue('Lifetime-Mon' in db)
        self.assertTrue('LifetimeBPM-Mon' in db)
        self.assertTrue('SplIntvl-SP' in db)
        self.assertTrue('SplIntvl-RB' in db)
        self.assertTrue('BuffSize-Mon' in db)
        self.assertTrue('BuffSizeBPM-Mon' in db)
        self.assertTrue('LtFitMode-Sel' in db)
        self.assertTrue('LtFitMode-Sts' in db)
        self.assertTrue('CurrOffset-SP' in db)
        self.assertTrue('CurrOffset-RB' in db)
        self.assertTrue('BuffSize-Mon' in db)
        self.assertTrue('BuffSizeTot-Mon' in db)
        self.assertTrue('BufferValue-Mon' in db)
        self.assertTrue('BufferTimestamp-Mon' in db)
        self.assertTrue('BuffSizeBPM-Mon' in db)
        self.assertTrue('BuffSizeTotBPM-Mon' in db)
        self.assertTrue('BufferValueBPM-Mon' in db)
        self.assertTrue('BufferTimestampBPM-Mon' in db)

        # PVs units
        self.assertEqual(db['Lifetime-Mon']['unit'], 's')
        self.assertEqual(db['LifetimeBPM-Mon']['unit'], 's')
        self.assertEqual(db['SplIntvl-SP']['unit'], 's')
        self.assertEqual(db['SplIntvl-RB']['unit'], 's')
        self.assertEqual(db['MinIntvlBtwSpl-SP']['unit'], 's')
        self.assertEqual(db['MinIntvlBtwSpl-RB']['unit'], 's')
        self.assertEqual(db['CurrOffset-SP']['unit'], 'mA')
        self.assertEqual(db['CurrOffset-RB']['unit'], 'mA')
