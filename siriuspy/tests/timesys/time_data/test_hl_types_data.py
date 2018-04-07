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
    'Events',
    'Clocks',
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


class TestEvents(unittest.TestCase):
    """Test Events class."""

    public_interface = (
        'HL2LL_MAP',
        'LL2HL_MAP',
        'LL_TMP',
        'LL_RGX',
        'HL_RGX',
        'HL_PREF',
        'LL_CODES',
        'LL_EVENTS',
        'MODES',
        'DELAY_TYPES',
    )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            hl_types_data.Events, TestEvents.public_interface)
        self.assertTrue(valid)

    def test_HL2LL_MAP(self):
        """Test HL2LL_MAP."""
        # TODO: implement test!
        pass

    def test_LL2HL_MAP(self):
        """Test LL2HL_MAP."""
        # TODO: implement test!
        pass

    def test_LL_TMP(self):
        """Test LL_TMP."""
        # TODO: implement test!
        pass

    def test_LL_RGX(self):
        """Test LL_RGX."""
        # TODO: implement test!
        pass

    def test_HL_RGX(self):
        """Test HL_RGX."""
        # TODO: implement test!
        pass

    def test_HL_PREF(self):
        """Test HL_PREF."""
        # TODO: implement test!
        pass

    def test_LL_CODES(self):
        """Test LL_CODES."""
        # TODO: implement test!
        pass

    def test_LL_EVENTS(self):
        """Test LL_EVENTS."""
        # TODO: implement test!
        pass

    def test_MODES(self):
        """Test MODES."""
        # TODO: implement test!
        pass

    def test_DELAY_TYPES(self):
        """Test DELAY_TYPES."""
        # TODO: implement test!
        pass


class TestClocks(unittest.TestCase):
    """Test Clocks class."""

    public_interface = (
        'STATES',
        'LL_TMP',
        'HL_TMP',
        'HL_PREF',
        'HL2LL_MAP',
        'LL2HL_MAP',
    )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            hl_types_data.Clocks, TestClocks.public_interface)
        self.assertTrue(valid)

    def test_STATES(self):
        """Test STATES."""
        # TODO: implement test!
        pass

    def test_LL_TMP(self):
        """Test LL_TMP."""
        # TODO: implement test!
        pass

    def test_HL_TMP(self):
        """Test HL_TMP."""
        # TODO: implement test!
        pass

    def test_HL_PREF(self):
        """Test HL_PREF."""
        # TODO: implement test!
        pass

    def test_HL2LL_MAP(self):
        """Test HL2LL_MAP."""
        # TODO: implement test!
        pass

    def test_LL2HL_MAP(self):
        """Test LL2HL_MAP."""
        # TODO: implement test!
        pass


class TestTriggers(unittest.TestCase):
    """Test Triggers class."""

    public_interface = (
        'STATES',
        'INTLK',
        'POLARITIES',
        'DELAY_TYPES',
        'SRC_LL',
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

    def test_STATES(self):
        """Test STATES."""
        # TODO: implement test!
        pass

    def test_INTLK(self):
        """Test INTLK."""
        # TODO: implement test!
        pass

    def test_POLARITIES(self):
        """Test POLARITIES."""
        # TODO: implement test!
        pass

    def test_DELAY_TYPES(self):
        """Test DELAY_TYPES."""
        # TODO: implement test!
        pass

    def test_SRC_LL(self):
        """Test SRC_LL."""
        # TODO: implement test!
        pass

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
