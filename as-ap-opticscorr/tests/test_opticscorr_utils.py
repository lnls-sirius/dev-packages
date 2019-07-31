#!/usr/bin/env python3.6

"""Module to test optics corr utils class."""

import unittest
from siriuspy import util
from as_ap_opticscorr import opticscorr_utils
from as_ap_opticscorr.opticscorr_utils import get_config_name, set_config_name


valid_interface_functions = (
    'get_config_name',
    'set_config_name'
)


class TestOpticsCorrUtils(unittest.TestCase):
    """Test opticscorr utils class."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            opticscorr_utils, valid_interface_functions, print_flag=True)
        self.assertTrue(valid)

    def test_get_config_name(self):
        """Test get_config_name function."""
        with self.assertRaises(ValueError):
            get_config_name('', 'tune')
        with self.assertRaises(ValueError):
            get_config_name('si', '')
        self.assertIsInstance(get_config_name('si', 'tune'), str)

    def test_set_config_name(self):
        """Test set_config_name function."""
        with self.assertRaises(ValueError):
            set_config_name('', 'tune', 'Default')
        with self.assertRaises(ValueError):
            set_config_name('si', '', 'Default')
        with self.assertRaises(TypeError):
            set_config_name('si', 'tune', 1)


if __name__ == "__main__":
    unittest.main()
