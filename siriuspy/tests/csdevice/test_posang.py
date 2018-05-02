#!/usr/bin/env python-sirius

"""Unittest module for opticscorr.py."""

import unittest
from siriuspy import util
from siriuspy.csdevice import posang
from siriuspy.csdevice.posang import get_posang_database


public_interface = (
        'Const',
        'get_posang_database',
    )


class TestOpticsCorrCSDevice(unittest.TestCase):
    """Test siriuspy.csdevice.opticscorr module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                posang,
                public_interface)
        self.assertTrue(valid)

    def test_get_posang_database(self):
        """Test get_posang_database."""
        db = get_posang_database()
        self.assertIsInstance(db, dict)

        # Test IOC interface: pv names
        self.assertTrue('Version-Cte' in db)
        self.assertTrue('Log-Mon' in db)
        self.assertTrue('DeltaPosX-SP' in db)
        self.assertTrue('DeltaPosX-RB' in db)
        self.assertTrue('DeltaAngX-SP' in db)
        self.assertTrue('DeltaAngX-RB' in db)
        self.assertTrue('DeltaPosY-SP' in db)
        self.assertTrue('DeltaPosY-RB' in db)
        self.assertTrue('DeltaAngY-SP' in db)
        self.assertTrue('DeltaAngY-RB' in db)
        self.assertTrue('ConfigName-SP' in db)
        self.assertTrue('ConfigName-RB' in db)
        self.assertTrue('RespMatX-Mon' in db)
        self.assertTrue('RespMatY-Mon' in db)
        self.assertTrue('RefKickCH1-Mon' in db)
        self.assertTrue('RefKickCH2-Mon' in db)
        self.assertTrue('RefKickCV1-Mon' in db)
        self.assertTrue('RefKickCV2-Mon' in db)
        self.assertTrue('SetNewRefKick-Cmd' in db)
        self.assertTrue('ConfigMA-Cmd' in db)
        self.assertTrue('Status-Mon' in db)
        self.assertTrue('StatusLabels-Cte' in db)

        # Test IOC interface: pvs units
        self.assertEqual(db['DeltaPosX-SP']['unit'], 'mm')
        self.assertEqual(db['DeltaPosX-RB']['unit'], 'mm')
        self.assertEqual(db['DeltaAngX-SP']['unit'], 'mrad')
        self.assertEqual(db['DeltaAngX-RB']['unit'], 'mrad')
        self.assertEqual(db['DeltaPosY-SP']['unit'], 'mm')
        self.assertEqual(db['DeltaPosY-RB']['unit'], 'mm')
        self.assertEqual(db['DeltaAngY-SP']['unit'], 'mrad')
        self.assertEqual(db['DeltaAngY-RB']['unit'], 'mrad')
        self.assertEqual(db['RefKickCH1-Mon']['unit'], 'mrad')
        self.assertEqual(db['RefKickCH2-Mon']['unit'], 'mrad')
        self.assertEqual(db['RefKickCV1-Mon']['unit'], 'mrad')
        self.assertEqual(db['RefKickCV2-Mon']['unit'], 'mrad')


if __name__ == "__main__":
    unittest.main()
