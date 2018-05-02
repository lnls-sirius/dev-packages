#!/usr/bin/env python-sirius

"""Unittest module for currinfo.py."""

import unittest
from siriuspy import util
from siriuspy.csdevice import currinfo
from siriuspy.csdevice.currinfo import (
    get_charge_database,
    get_current_database,
    get_lifetime_database,
)

public_interface = (
        'OFFONTYP',
        'DCCTSELECTIONTYP',
        'BUFFAUTORSTTYP',
        'Const',
        'get_charge_database',
        'get_current_database',
        'get_lifetime_database'
    )


class TestCurrInfoCSDevice(unittest.TestCase):
    """Test siriuspy.csdevice.currinfo module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                currinfo,
                public_interface)
        self.assertTrue(valid)

    def test_get_charge_database(self):
        """Test get_charge_database."""
        db = get_charge_database()
        self.assertIsInstance(db, dict)

        # Test IOC interface: pv names
        self.assertTrue('Version-Cte' in db)
        self.assertTrue('Charge-Mon' in db)
        self.assertTrue('ChargeCalcIntvl-SP' in db)
        self.assertTrue('ChargeCalcIntvl-RB' in db)

        # Test IOC interface: pvs units
        self.assertEqual(db['Charge-Mon']['unit'], 'A.h')
        self.assertEqual(db['ChargeCalcIntvl-SP']['unit'], 's')
        self.assertEqual(db['ChargeCalcIntvl-RB']['unit'], 's')

    def test_get_current_database(self):
        """Test get_current_database."""
        # Test IOC interface: pv names
        db = get_current_database('Accelerator')
        self.assertIsInstance(db, dict)
        self.assertTrue('Version-Cte' in db)
        self.assertTrue('Current-Mon' in db)
        self.assertTrue('StoredEBeam-Mon' in db)

        db = get_current_database('SI')
        self.assertIsInstance(db, dict)
        self.assertTrue('DCCT-Sel' in db)
        self.assertTrue('DCCT-Sts' in db)
        self.assertTrue('DCCTFltCheck-Sel' in db)
        self.assertTrue('DCCTFltCheck-Sts' in db)

        db = get_current_database('BO')
        self.assertIsInstance(db, dict)
        self.assertFalse('DCCT-Sel' in db)
        self.assertFalse('DCCT-Sts' in db)
        self.assertFalse('DCCTFltCheck-Sel' in db)
        self.assertFalse('DCCTFltCheck-Sts' in db)

        # Test IOC interface: pvs units
        self.assertEqual(db['Current-Mon']['unit'], 'mA')

    def test_get_lifetime_database(self):
        """Test get_lifetime_database."""
        db = get_lifetime_database()
        self.assertIsInstance(db, dict)

        # Test IOC interface: pv names
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

        # Test IOC interface: pvs units
        self.assertEqual(db['Lifetime-Mon']['unit'], 's')
        self.assertEqual(db['SplIntvl-SP']['unit'], 's')
        self.assertEqual(db['SplIntvl-RB']['unit'], 's')
        self.assertEqual(db['DCurrFactor-Cte']['unit'], 'mA')


if __name__ == "__main__":
    unittest.main()
