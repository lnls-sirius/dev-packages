#!/usr/bin/env python-sirius

"""Module to test CurrInfo Lifetime Soft IOC main module."""

import unittest
import siriuspy.util as util
from as_ap_currinfo.lifetime.main import App


valid_interface = (
    'pvs_database',
    'process',
    'read',
    'write',
)


class TestASAPCurrInfoLifetimeMain(unittest.TestCase):
    """Test AS-AP-CurrInfo Lifetime Soft IOC."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            App, valid_interface, print_flag=True)
        self.assertTrue(valid)

    def test_write_MinIntvlBtwSpl(self):
        """Test write MinIntvlBtwSmpl-SP."""
        app = App()

        app.write('MinIntvlBtwSpl-SP', -1)
        self.assertEqual(app._min_intvl_btw_spl, 0)

        app.write('MinIntvlBtwSpl-SP', 0)
        self.assertEqual(app._min_intvl_btw_spl, 0)

        app.write('MinIntvlBtwSpl-SP', 1)
        self.assertEqual(app._min_intvl_btw_spl, 1)

    def test_write_SplIntvl(self):
        """Test write SplIntvl-SP."""
        app = App()
        app.write('SplIntvl-SP', 100)
        self.assertEqual(app._sampling_interval, 100)

    def test_write_LtFitMode(self):
        """Test write LtFitMode-Sel."""
        app = App()
        app.write('LtFitMode-Sel', 1)
        self.assertEqual(app._mode, 1)

    def test_write_CurrOffset(self):
        """Test write CurrOffset-SP."""
        app = App()
        app.write('CurrOffset-SP', 1)
        self.assertEqual(app._current_offset, 1)


if __name__ == "__main__":
    unittest.main()
