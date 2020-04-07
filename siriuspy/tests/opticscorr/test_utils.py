#!/usr/bin/env python3.6

"""Module to test optics corr utils class."""

import unittest
from siriuspy import util
from siriuspy.opticscorr import utils
from siriuspy.opticscorr.utils import HandleConfigNameFile


PUB_INTERFACE = (
    'HandleConfigNameFile',
    'get_default_config_name'
)


class TestOpticsCorrUtils(unittest.TestCase):
    """Test opticscorr utils class."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            utils, PUB_INTERFACE, print_flag=True)
        self.assertTrue(valid)

    def test_HandleConfigNameFile(self):
        """Test HandleConfigNameFile class."""
        with self.assertRaises(ValueError):
            _ = HandleConfigNameFile('', 'tune')
        with self.assertRaises(ValueError):
            _ = HandleConfigNameFile('SI', '')

    def test_set_config_name(self):
        """Test set_config_name function."""
        cn_handler = HandleConfigNameFile('SI', 'tune')
        with self.assertRaises(TypeError):
            cn_handler.set_config_name(1)


if __name__ == "__main__":
    unittest.main()
