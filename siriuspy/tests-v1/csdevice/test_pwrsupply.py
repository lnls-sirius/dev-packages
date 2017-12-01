#!/usr/bin/env python-sirius

"""Unittest module for enumtypes.py."""

import unittest
import siriuspy.csdevice.pwrsupply as pwrsupply
import siriuspy.util as util


public_interface = (
    'default_wfmsize',
    'default_wfmlabels',
    'default_intlklabels',
    'default_ps_current_precision',
    'default_ps_current_unit',
    'get_common_propty_database',
    'get_common_ps_propty_database',
    'get_ps_propty_database',
    'get_pu_propty_database',
    'get_ma_propty_database',
    'get_pm_propty_database',
)


class TestPwrSupply(unittest.TestCase):
    """Test pwrsupply module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface(pwrsupply, public_interface)
        self.assertTrue(valid)

    def test_common_propty_database(self):
        """Test common_propty_database."""
        db = pwrsupply.get_common_propty_database()
        self.assertIsInstance(db, dict)
        for prop in db:
            self.assertIsInstance(db[prop], dict)

    def test_common_ps_propty_database(self):
        """Test common_ps_propty_database."""
        db = pwrsupply.get_common_ps_propty_database()
        self.assertIsInstance(db, dict)
        for prop in db:
            self.assertIsInstance(db[prop], dict)
        # test precision consistency
        proptys = ('Current-SP', 'Current-RB', 'CurrentRef-Mon', 'Current-Mon',
                   'WfmData-SP', 'WfmData-RB')
        for propty in proptys:
            self.assertEqual(db[propty]['prec'],
                             pwrsupply.default_ps_current_precision)


if __name__ == "__main__":
    unittest.main()
