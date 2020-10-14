#!/usr/bin/env python-sirius

"""Unittest module for posang.py."""

from unittest import TestCase
from siriuspy import util
from siriuspy.posang import csdev
from siriuspy.posang.csdev import get_posang_database


PUB_INTERFACE = (
        'ETypes',
        'Const',
        'get_posang_database',
    )


class TestPosAngCSDevice(TestCase):
    """Test siriuspy.posanf.csdev module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(csdev, PUB_INTERFACE)
        self.assertTrue(valid)

    def test_get_posang_database(self):
        """Test get_posang_database."""
        dbase = get_posang_database('TB')
        self.assertIsInstance(dbase, dict)

        # PV names
        self.assertTrue('Version-Cte' in dbase)
        self.assertTrue('Log-Mon' in dbase)
        self.assertTrue('DeltaPosX-SP' in dbase)
        self.assertTrue('DeltaPosX-RB' in dbase)
        self.assertTrue('DeltaAngX-SP' in dbase)
        self.assertTrue('DeltaAngX-RB' in dbase)
        self.assertTrue('DeltaPosY-SP' in dbase)
        self.assertTrue('DeltaPosY-RB' in dbase)
        self.assertTrue('DeltaAngY-SP' in dbase)
        self.assertTrue('DeltaAngY-RB' in dbase)
        self.assertTrue('ConfigName-SP' in dbase)
        self.assertTrue('ConfigName-RB' in dbase)
        self.assertTrue('RespMatX-Mon' in dbase)
        self.assertTrue('RespMatY-Mon' in dbase)
        self.assertTrue('CH1-Cte' in dbase)
        self.assertTrue('CH2-Cte' in dbase)
        self.assertTrue('CV1-Cte' in dbase)
        self.assertTrue('CV2-Cte' in dbase)
        self.assertTrue('RefKickCH1-Mon' in dbase)
        self.assertTrue('RefKickCH2-Mon' in dbase)
        self.assertTrue('RefKickCV1-Mon' in dbase)
        self.assertTrue('RefKickCV2-Mon' in dbase)
        self.assertTrue('SetNewRefKick-Cmd' in dbase)
        self.assertTrue('NeedRefUpdate-Mon' in dbase)
        self.assertTrue('ConfigPS-Cmd' in dbase)
        self.assertTrue('Status-Mon' in dbase)
        self.assertTrue('StatusLabels-Cte' in dbase)

        # PVs units
        self.assertEqual(dbase['DeltaPosX-SP']['unit'], 'mm')
        self.assertEqual(dbase['DeltaPosX-RB']['unit'], 'mm')
        self.assertEqual(dbase['DeltaAngX-SP']['unit'], 'mrad')
        self.assertEqual(dbase['DeltaAngX-RB']['unit'], 'mrad')
        self.assertEqual(dbase['DeltaPosY-SP']['unit'], 'mm')
        self.assertEqual(dbase['DeltaPosY-RB']['unit'], 'mm')
        self.assertEqual(dbase['DeltaAngY-SP']['unit'], 'mrad')
        self.assertEqual(dbase['DeltaAngY-RB']['unit'], 'mrad')
        self.assertEqual(dbase['RefKickCH1-Mon']['unit'], 'urad')
        self.assertEqual(dbase['RefKickCH2-Mon']['unit'], 'mrad')
        self.assertEqual(dbase['RefKickCV1-Mon']['unit'], 'urad')
        self.assertEqual(dbase['RefKickCV2-Mon']['unit'], 'urad')
