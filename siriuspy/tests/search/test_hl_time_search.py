#!/usr/bin/env python-sirius

"""Unittest module for hl_time_search.py."""

from unittest import TestCase
from siriuspy import util
from siriuspy.search import hl_time_search

mock_flag = True

public_interface = ('HLTimeSearch', )


class TestModule(TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                hl_time_search,
                public_interface)
        self.assertTrue(valid)


class TestHLTimeSearch(TestCase):
    """Test HLTimeSearch class."""

    public_interface = (
        'get_hl_events',
        'get_hl_triggers',
        'get_hl_trigger_database',
        'get_hl_trigger_sources',
        'get_hl_trigger_prop_value',
        'get_hl_trigger_prop_limits',
        'get_hl_trigger_interface',
        'get_ll_trigger_names',
        'get_hl_from_ll_triggers',
        'has_delay_type',
        'has_clock',
        'check_hl_triggers_consistency',
        'reset',
    )

    def get_hl_triggers(self):
        """Test get_hl_triggers."""
        # TODO: implement test!
        pass

    def get_hl_trigger_database(self):
        """Test get_hl_trigger_database."""
        # TODO: implement test!
        pass

    def get_hl_trigger_sources(self):
        """Test get_hl_trigger_sources."""
        # TODO: implement test!
        pass

    def get_hl_trigger_prop_value(self):
        """Test get_hl_trigger_prop_value."""
        # TODO: implement test!
        pass

    def get_hl_trigger_prop_limits(self):
        """Test get_hl_trigger_prop_limits."""
        # TODO: implement test!
        pass

    def get_hl_trigger_interface(self):
        """Test get_hl_trigger_interface."""
        # TODO: implement test!
        pass

    def get_ll_trigger_names(self):
        """Test get_ll_trigger_names."""
        # TODO: implement test!
        pass
    
    def get_hl_from_triggers(self):
        """Test get_hl_from_ll_triggers."""
        # TODO: implement test!
        pass

    def has_delay_type(self):
        """Test has_delay_type."""
        # TODO: implement test!
        pass

    def has_clock(self):
        """Test has_clock."""
        # TODO: implement test!
        pass

    def check_hl_triggers_consistency(self):
        """Test check_hl_triggers_consistency."""
        # TODO: implement test!
        pass
