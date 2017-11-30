#!/usr/bin/env python-sirius

"""Unittest module for enumtypes.py."""

import unittest
import siriuspy.csdevice.enumtypes as enumtypes
import siriuspy.util as util

valid_interface = ('EnumTypes', )


class TestEnumTypes(unittest.TestCase):
    """Test EnumTypes."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface(enumtypes, valid_interface)
        self.assertTrue(valid)

    def test_class_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface(enumtypes, valid_interface)
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()
