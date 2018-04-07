#!/usr/bin/env python-sirius

"""Unittest module for hl_types_data.py."""

import unittest
# import re
# from unittest import mock

from siriuspy import util
from siriuspy.timesys.time_data import hl_types_data

mock_flag = True

public_interface = (
    'AC_FREQUENCY',
    'RF_DIVISION',
    'RF_FREQUENCY',
    'BASE_FREQUENCY',
    'RF_PERIOD',
    'BASE_DELAY',
    'RF_DELAY',
    'FINE_DELAY',
    'Triggers',
)


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                hl_types_data,
                public_interface)
        self.assertTrue(valid)


class TestTriggers(unittest.TestCase):
    """Test Triggers class."""

    public_interface = (
        'hl_triggers',
        'check_triggers_consistency',
        'get_ll_trigger_names',
        'has_delay_type',
        'has_clock',
    )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            hl_types_data.Triggers, TestTriggers.public_interface)
        self.assertTrue(valid)

    def test_hl_triggers(self):
        """Test hl_triggers."""
        # TODO: implement test!
        pass

    def test_get_ll_trigger_names(self):
        """Test get_ll_trigger_names."""
        # TODO: implement test!
        pass

    def test_has_delay_type(self):
        """Test has_delay_type."""
        # TODO: implement test!
        pass

    def test_has_clock(self):
        """Test has_clock."""
        # TODO: implement test!
        pass

    def test_check_triggers_consistency(self):
        """Test check_triggers_consistency."""
        # TODO: implement test!
        pass


if __name__ == "__main__":
    unittest.main()
