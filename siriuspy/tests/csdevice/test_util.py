#!/usr/bin/env python-sirius

"""Unittest module for util.py."""

import unittest
import siriuspy.util as util
import siriuspy.csdevice.util as cutil

public_interface = (
    'ETypes',
    'Const',
    'add_pvslist_cte'
)


class TestUtil(unittest.TestCase):
    """Test util module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            cutil, public_interface)
        self.assertTrue(valid)

    def test_adds_pvslist_cte(self):
        """Test adds_pvslist_cte."""
        db = {'a': {}, 'b': {}}
        db = cutil.add_pvslist_cte(db)
        self.assertEqual(len(db), 3)
        self.assertIn('Properties-Cte', db)
        self.assertEqual(db['Properties-Cte']['count'], 3)
        self.assertEqual(db['Properties-Cte']['value'],
                         ['Properties-Cte', 'a', 'b'])
