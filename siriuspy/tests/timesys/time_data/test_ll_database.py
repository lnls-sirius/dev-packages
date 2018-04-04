#!/usr/bin/env python-sirius

"""Unittest module for ll_database.py."""

import unittest
# import re
# from unittest import mock

from siriuspy import util
from siriuspy.timesys.time_data import ll_database

mock_flag = True

public_interface = (
    'TimingDevDb',
)


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                ll_database,
                public_interface)
        self.assertTrue(valid)


class TestTimingDevDb(unittest.TestCase):
    """Test TimingDevDb class."""

    public_interface = (
        'get_otp_database',
        'get_out_database',
        'get_afc_out_database',
        'get_evr_database',
        'get_eve_database',
        'get_afc_database',
        'get_fout_database',
        'get_event_database',
        'get_clock_database',
        'get_evg_database',
    )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            ll_database.TimingDevDb, TestTimingDevDb.public_interface)
        self.assertTrue(valid)

    def test_get_otp_database(self):
        """Test get_otp_database."""
        # TODO: implement test!
        pass

    def test_get_out_database(self):
        """Test get_out_database."""
        # TODO: implement test!
        pass

    def test_get_afc_out_database(self):
        """Test get_afc_out_database."""
        # TODO: implement test!
        pass

    def test_get_evr_database(self):
        """Test get_evr_database."""
        # TODO: implement test!
        pass

    def test_get_eve_database(self):
        """Test get_eve_database."""
        # TODO: implement test!
        pass

    def test_get_afc_database(self):
        """Test get_afc_database."""
        # TODO: implement test!
        pass

    def test_get_fout_database(self):
        """Test get_fout_database."""
        # TODO: implement test!
        pass

    def test_get_event_database(self):
        """Test get_event_database."""
        # TODO: implement test!
        pass

    def test_get_clock_database(self):
        """Test get_clock_database."""
        # TODO: implement test!
        pass

    def test_get_evg_database(self):
        """Test get_evg_database."""
        # TODO: implement test!
        pass


if __name__ == "__main__":
    unittest.main()
