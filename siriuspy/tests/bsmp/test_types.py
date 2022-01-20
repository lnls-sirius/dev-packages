#!/usr/bin/env python-sirius

"""Test type module."""

from unittest import TestCase

from siriuspy.bsmp import Types


class TestBSMPTypes(TestCase):
    """Test BSMP Types."""

    def test_char_type(self):
        """Test char type properties."""
        t = Types.T_CHAR

        self.assertEqual(t.type, 'char')
        self.assertEqual(t.size, 1)
        self.assertEqual(t.fmt, '<c')
        self.assertFalse(t.check(1))
        self.assertFalse(t.check(1.5))
        self.assertTrue(t.check('c'))

    def test_uint8_type(self):
        """Test uint8 type properties."""
        t = Types.T_UINT8

        self.assertEqual(t.type, 'uint8')
        self.assertEqual(t.size, 1)
        self.assertEqual(t.fmt, '<B')
        self.assertFalse(t.check(1.5))
        self.assertFalse(t.check('c'))
        self.assertTrue(t.check(1))

    def test_uint16_type(self):
        """Test uint16 type properties."""
        t = Types.T_UINT16

        self.assertEqual(t.type, 'uint16')
        self.assertEqual(t.size, 2)
        self.assertEqual(t.fmt, '<H')
        self.assertFalse(t.check(1.5))
        self.assertFalse(t.check('c'))
        self.assertTrue(t.check(1))

    def test_uint32_type(self):
        """Test uint32 type properties."""
        t = Types.T_UINT32

        self.assertEqual(t.type, 'uint32')
        self.assertEqual(t.size, 4)
        self.assertEqual(t.fmt, '<I')
        self.assertFalse(t.check(1.5))
        self.assertFalse(t.check('c'))
        self.assertTrue(t.check(1))

    def test_float_type(self):
        """Test float type properties."""
        t = Types.T_FLOAT

        self.assertEqual(t.type, 'float')
        self.assertEqual(t.size, 4)
        self.assertEqual(t.fmt, '<f')
        self.assertTrue(t.check(1.5))
        self.assertFalse(t.check('c'))
        self.assertFalse(t.check(1))
