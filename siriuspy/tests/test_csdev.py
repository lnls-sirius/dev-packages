#!/usr/bin/env python-sirius

"""Unittest module for csdev.py."""

from unittest import TestCase
import siriuspy.util as util
import siriuspy.csdev as csdev

PUB_INTERFACE = (
    'ETypes',
    'Const',
    'add_pvslist_cte',
    'get_device_2_ioc_ip',
)


class TestUtil(TestCase):
    """Test util module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            csdev, PUB_INTERFACE)
        self.assertTrue(valid)

    def test_adds_pvslist_cte(self):
        """Test adds_pvslist_cte."""
        dbase = {'a': {}, 'b': {}}
        dbase = csdev.add_pvslist_cte(dbase)
        self.assertEqual(len(dbase), 3)
        self.assertIn('Properties-Cte', dbase)
        self.assertEqual(dbase['Properties-Cte']['count'], 18)
        self.assertEqual(dbase['Properties-Cte']['value'], 'Properties-Cte a b')

    def test_get_device_2_ioc_ip(self):
        """Test get_device_2_ioc_ip."""
        # TODO: implement!
