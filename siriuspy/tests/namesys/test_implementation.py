#!/usr/bin/env python-sirius

"""Test implementation.py."""

from unittest import TestCase

import siriuspy.util as util
import siriuspy.namesys as namesys


mock_flag = True

public_interface = (
    'get_siriuspvname_attrs',
    'join_name',
    'split_name',
    'get_pair_sprb',
    'SiriusPVName',
    'Filter',
)


class TestImplementation(TestCase):
    """Test Implementation module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            namesys, public_interface)
        self.assertTrue(valid)

    def test_get_siriuspvname_attrs(self):
        """Test  get_siriuspvname_attrs."""
        _attrs = [
            'channel_type',
            'prefix',
            'sec',
            'sub',
            'area_name',
            'dis',
            'dev',
            'idx',
            'device_name',
            'propty_name',
            'propty_suffix',
            'propty',
            'device_propty',
            'field',
        ]
        attrs = namesys.get_siriuspvname_attrs()
        self.assertEqual(sorted(_attrs), sorted(attrs))

    def test_join_name(self):
        """Test join_name."""
        # invalid arguments
        self.assertRaises(TypeError, namesys.join_name)
        self.assertRaises(TypeError, namesys.join_name,
                          sec='SI')
        self.assertRaises(TypeError, namesys.join_name,
                          sec='SI', sub='Fam', dis='PS')
        name = namesys.join_name(sec='SI', sub='Fam', dis='PS', dev='QDA')
        self.assertEqual(name, 'SI-Fam:PS-QDA')
        name = namesys.join_name(sec='BO', sub='Fam', dis='PS', dev='B',
                                 idx='1')
        self.assertEqual(name, 'BO-Fam:PS-B-1')
        name = namesys.join_name(sec='BO', sub='Fam', dis='PS', dev='B',
                                 idx='1', propty='PwrState-Sel')
        self.assertEqual(name, 'BO-Fam:PS-B-1:PwrState-Sel')
        name = namesys.join_name(sec='BO', sub='Fam', dis='PS', dev='B',
                                 idx='1', propty='Current-Mon', field='AVG')
        self.assertEqual(name, 'BO-Fam:PS-B-1:Current-Mon.AVG')

    def test_split_name(self):
        """Test split_name."""
        # empty string
        d = namesys.split_name('')
        self.assertEqual(len(d), len(namesys.get_siriuspvname_attrs()))
        for k, v in d.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, str)
            self.assertEqual(v, '')
        # Complete
        d = namesys.split_name(
            'ca://TEST-SI-Fam:PS-B1B2-1:PwrCurrent-SP.AVG')
        self.assertEqual(d['channel_type'], 'ca')
        self.assertEqual(d['prefix'], 'TEST')
        self.assertEqual(d['sec'], 'SI')
        self.assertEqual(d['sub'], 'Fam')
        self.assertEqual(d['dis'], 'PS')
        self.assertEqual(d['dev'], 'B1B2')
        self.assertEqual(d['idx'], '1')
        self.assertEqual(d['propty'], 'PwrCurrent-SP')
        self.assertEqual(d['field'], 'AVG')
        # one field
        self.assertRaises(IndexError, namesys.split_name, pvname='A:B')
        self.assertRaises(IndexError, namesys.split_name, pvname='A:B:C')
        self.assertRaises(IndexError, namesys.split_name, pvname='A:B-C:D')
        self.assertRaises(IndexError, namesys.split_name, pvname='A:B-C:D.F')


class TestSiriusPVName(TestCase):
    """Test SiriusPVName module."""

    public_interface = (
        'substitute',
        'device_name',
        'get_nickname',
        'is_write_pv',
        'is_sp_pv',
        'is_cmd_pv',
        'is_cte_pv',
        'is_rb_pv',
        'from_sp2rb',
        'from_rb2sp',
        'strip',
        'replace',
    )

    def test_public_interface(self):
        """Test SiriusPVName public interface."""
        valid = util.check_public_interface_namespace(
            namesys.SiriusPVName, TestSiriusPVName.public_interface)
        self.assertTrue(valid)

    def test_constructor(self):
        """Test constructor."""
        n = namesys.SiriusPVName('ca://PREFIX-SI-Fam:PS-B1B2-1:Current-SP.AVG')
        self.assertEqual(n.channel_type, 'ca')
        self.assertEqual(n.prefix, 'PREFIX')
        self.assertEqual(n.sec, 'SI')
        self.assertEqual(n.sub, 'Fam')
        self.assertEqual(n.dis, 'PS')
        self.assertEqual(n.dev, 'B1B2')
        self.assertEqual(n.idx, '1')
        self.assertEqual(n.device_name, 'SI-Fam:PS-B1B2-1')
        self.assertEqual(n.propty_name, 'Current')
        self.assertEqual(n.propty_suffix, 'SP')
        self.assertEqual(n.propty, 'Current-SP')
        self.assertEqual(n.device_propty, 'B1B2-1:Current-SP.AVG')
        self.assertEqual(n.field, 'AVG')

    def test_string(self):
        """Test string."""
        n = namesys.SiriusPVName('ca://PREFIX-SI-Fam:PS-B1B2-1:Current-SP.AVG')
        self.assertIsInstance(n, str)
