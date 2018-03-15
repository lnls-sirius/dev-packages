#!/usr/bin/env python-sirius

"""Unittest module for enumtypes.py."""

import unittest
import siriuspy.csdevice.enumtypes as enumtypes
from siriuspy.csdevice.enumtypes import EnumTypes
import siriuspy.util as util

public_interface = ('EnumTypes', )


class TestEnumtypes(unittest.TestCase):
    """Test enumtype module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            enumtypes, public_interface)
        self.assertTrue(valid)


class TestEnumTypes(unittest.TestCase):
    """Test EnumTypes class."""

    public_interface = (
        'enums',
        'conv_key2idx',
        'conv_idx2key',
        'indices',
        'types',
        'names',
        'idx',
    )

    def test_public_interface(self):
        """Test EnumTypes class interface."""
        valid = util.check_public_interface_namespace(
            EnumTypes, TestEnumTypes.public_interface)
        self.assertTrue(valid)

    def test_types(self):
        """Test types."""
        # check format of output
        types = EnumTypes.types()
        self.assertIn('OffOnTyp', types)
        self.assertIn('OffOnInitTyp', types)
        self.assertIn('DsblEnblTyp', types)
        self.assertIn('PSRmtLocTyp', types)
        self.assertIn('PSPwrStateTyp', types)
        self.assertIsInstance(types, dict)
        for typ in types:
            self.assertIsInstance(typ, str)
            tup = types[typ]
            self.assertIsInstance(tup, tuple)
            for v in tup:
                self.assertIsInstance(v, str)

    def test_indices(self):
        """Test indices."""
        self.assertRaises(KeyError, EnumTypes.indices, typ='')
        indices = EnumTypes.indices('OffOnTyp')
        self.assertIsInstance(indices, (tuple, list))
        self.assertEqual(1+max(indices), len(indices))
        indices = EnumTypes.indices('DsblEnblTyp')
        self.assertIsInstance(indices, (tuple, list))
        self.assertEqual(1+max(indices), len(indices))

    def test_enums(self):
        """Test enums."""
        # check format of output
        types = EnumTypes.types()
        self.assertIn('OffOnTyp', types)
        self.assertIn('OffOnTyp', types)
        self.assertIn('DsblEnblTyp', types)
        self.assertIn('OffOnInitTyp', types)
        self.assertIn('PSRmtLocTyp', types)
        self.assertIsInstance(types, dict)
        for typ in types:
            self.assertIsInstance(typ, str)
            tup = types[typ]
            self.assertIsInstance(tup, tuple)
            for v in tup:
                self.assertIsInstance(v, str)
        self.assertRaises(KeyError, EnumTypes.enums, '')
        values = EnumTypes.enums('OffOnTyp')
        self.assertEqual(len(values), 2)

    def test_conv_key2idx(self):
        """Test conv_key2idx."""
        self.assertRaises(ValueError, EnumTypes.conv_key2idx,
                          typ='OffOnTyp', key='')
        self.assertEqual(EnumTypes.conv_key2idx('OffOnTyp', 'Off'), 0)
        self.assertEqual(EnumTypes.conv_key2idx('OffOnTyp', 'On'), 1)
        self.assertEqual(EnumTypes.conv_key2idx('OffOnInitTyp', 'Off'), 0)
        self.assertEqual(EnumTypes.conv_key2idx('OffOnInitTyp', 'On'), 1)
        self.assertEqual(EnumTypes.conv_key2idx('OffOnInitTyp',
                                                'Initializing'), 2)

    def test_conv_idx2key(self):
        """Test conv_idx2key."""
        self.assertRaises(TypeError, EnumTypes.conv_idx2key,
                          typ='OffOnTyp', idx='')
        self.assertRaises(IndexError, EnumTypes.conv_idx2key,
                          typ='OffOnTyp', idx=5)
        self.assertEqual(EnumTypes.conv_idx2key('OffOnTyp', 0), 'Off')
        self.assertEqual(EnumTypes.conv_idx2key('OffOnTyp', 1), 'On')
        self.assertEqual(EnumTypes.conv_idx2key('OffOnInitTyp', 0), 'Off')
        self.assertEqual(EnumTypes.conv_idx2key('OffOnInitTyp', 1), 'On')
        self.assertEqual(EnumTypes.conv_idx2key('OffOnInitTyp', 2),
                         'Initializing')

    def test_idx(self):
        """Test a few class indices."""
        self.assertEqual(EnumTypes.idx.Off, 0)
        self.assertEqual(EnumTypes.idx.On, 1)
        self.assertEqual(EnumTypes.idx.Initializing, 2)
        self.assertEqual(EnumTypes.idx.Remote, 0)
        self.assertEqual(EnumTypes.idx.Local, 1)
        self.assertEqual(EnumTypes.idx.PCHost, 2)
        self.assertEqual(EnumTypes.idx.Dsbl, 0)
        self.assertEqual(EnumTypes.idx.Enbl, 1)


if __name__ == "__main__":
    unittest.main()
