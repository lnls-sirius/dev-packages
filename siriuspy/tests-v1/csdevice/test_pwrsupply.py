#!/usr/bin/env python-sirius

"""Unittest module for enumtypes.py."""

import unittest
from siriuspy.search import PSSearch
import siriuspy.csdevice.pwrsupply as pwrsupply
import siriuspy.util as util


public_interface = (
    'default_wfmsize',
    'default_wfmlabels',
    'default_intlklabels',
    'default_ps_current_precision',
    'default_pu_current_precision',
    'get_ps_current_unit',
    'get_pu_current_unit',
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
        valid = util.check_public_interface_namespace(
            pwrsupply, public_interface)
        self.assertTrue(valid)

    def test_ps_current_unit(self):
        """Test  ps_current_unit."""
        pass

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

    def test_ps_propty_database(self):
        """Test ps_propty_database."""
        current_alarm = ('Current-SP', 'Current-RB',
                         'CurrentRef-Mon', 'Current-Mon', )
        current_pvs = current_alarm + ('WfmData-SP', 'WfmData-RB')
        pstypes = PSSearch.get_pstype_names()
        for pstype in pstypes:
            db = pwrsupply.get_ps_propty_database(pstype)
            unit = db['Current-SP']['unit']
            for propty, dbi in db.items():
                # set setpoint limits in database
                if propty in current_alarm:
                    self.assertLessEqual(dbi['lolo'], dbi['low'])
                    self.assertLessEqual(dbi['low'], dbi['lolim'])
                    self.assertLessEqual(dbi['lolim'], dbi['hilim'])
                    self.assertLessEqual(dbi['hilim'], dbi['high'])
                    self.assertLessEqual(dbi['high'], dbi['hihi'])
                if propty in current_pvs:
                    self.assertEqual(dbi['unit'], unit)

    def test_pu_propty_database(self):
        """Test pu_propty_database."""
        pstypes = PSSearch.get_pstype_names()
        for pstype in pstypes:
            db = pwrsupply.get_ps_propty_database(pstype)

if __name__ == "__main__":
    unittest.main()
