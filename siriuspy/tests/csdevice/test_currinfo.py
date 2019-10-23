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
        self.assertTrue('ChargeCalcIntvl-SP' in db)
        self.assertTrue('ChargeCalcIntvl-RB' in db)

        # PVs units
        self.assertEqual(db['Current-Mon']['unit'], 'mA')
        self.assertEqual(db['Charge-Mon']['unit'], 'A.h')
        self.assertEqual(db['ChargeCalcIntvl-SP']['unit'], 's')
        self.assertEqual(db['ChargeCalcIntvl-RB']['unit'], 's')

        # ---- BO ----
        db = get_currinfo_database('BO')
        self.assertIsInstance(db, dict)

        # PV names
        self.assertTrue(['RawReadings-Mon'] in db)
        self.assertTrue(['Current150MeV-Mon'] in db)
        self.assertTrue(['Current1GeV-Mon'] in db)
        self.assertTrue(['Current2GeV-Mon'] in db)
        self.assertTrue(['Current3GeV-Mon'] in db)
        self.assertTrue(['Charge150MeV-Mon'] in db)
        self.assertTrue(['Charge1GeV-Mon'] in db)
        self.assertTrue(['Charge2GeV-Mon'] in db)
        self.assertTrue(['Charge3GeV-Mon'] in db)
        self.assertTrue(['RampEff-Mon'] in db)

        # PVs units
        self.assertEqual(db['RawReadings-Mon']['unit'], 'mA')
        self.assertEqual(db['Current150MeV-Mon']['unit'], 'mA')
        self.assertEqual(db['Current1GeV-Mon']['unit'], 'mA')
        self.assertEqual(db['Current2GeV-Mon']['unit'], 'mA')
        self.assertEqual(db['Current3GeV-Mon']['unit'], 'mA')
        self.assertEqual(db['Charge150MeV-Mon']['unit'], 'A.h')
        self.assertEqual(db['Charge1GeV-Mon']['unit'], 'A.h')
        self.assertEqual(db['Charge2GeV-Mon']['unit'], 'A.h')
        self.assertEqual(db['Charge3GeV-Mon']['unit'], 'A.h')
        self.assertEqual(db['RampEff-Mon']['unit'], '%')

    def test_get_lifetime_database(self):
        """Test get_lifetime_database."""
        db = get_lifetime_database()
        self.assertIsInstance(db, dict)

        # PV names
        self.assertTrue('Version-Cte' in db)
        self.assertTrue('Lifetime-Mon' in db)
        self.assertTrue('BuffSizeMax-SP' in db)
        self.assertTrue('BuffSizeMax-RB' in db)
        self.assertTrue('BuffSize-Mon' in db)
        self.assertTrue('SplIntvl-SP' in db)
        self.assertTrue('SplIntvl-RB' in db)
        self.assertTrue('BuffRst-Cmd' in db)
        self.assertTrue('BuffAutoRst-Sel' in db)
        self.assertTrue('BuffAutoRst-Sts' in db)
        self.assertTrue('DCurrFactor-Cte' in db)

        # PVs units
        self.assertEqual(db['Lifetime-Mon']['unit'], 's')
        self.assertEqual(db['SplIntvl-SP']['unit'], 's')
        self.assertEqual(db['SplIntvl-RB']['unit'], 's')
        self.assertEqual(db['DCurrFactor-Cte']['unit'], 'mA')
