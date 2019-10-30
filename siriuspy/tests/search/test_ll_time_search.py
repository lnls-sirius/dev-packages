#!/usr/bin/env python-sirius

"""Unittest module for ll_time_search.py."""

from unittest import TestCase
import re
from siriuspy import util
from siriuspy.search import ll_time_search

mock_flag = True

public_interface = (
    'LLTimeSearch',
)


class TestModule(TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                ll_time_search,
                public_interface)
        self.assertTrue(valid)


class TestLLTimeSearch(TestCase):
    """Test LLTimeSearch class."""

    public_interface = (
        'LLRegExp',
        'In2OutMap',
        'Out2InMap',
        'get_channel_input',
        'get_channel_output_port_pvname',
        'get_channel_internal_trigger_pvname',
        'get_device_names',
        'get_evg_name',
        'get_triggersource_devices',
        'get_trigsrc2fout_mapping',
        'get_fout2trigsrc_mapping',
        'get_device_tree',
        'reset',
        'server_online',
        'get_connections_from_evg',
        'get_connections_twds_evg',
        'get_top_chain_senders',
        'get_final_receivers',
        'get_relations_from_evg',
        'get_relations_twds_evg',
        'has_clock',
        'has_delay_type',
        'get_trigger_name',
        'get_fout_channel',
        'get_evg_channel',
    )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            ll_time_search.LLTimeSearch, TestLLTimeSearch.public_interface)
        self.assertTrue(valid)

    def test_LLRegExp(self):
        """Test LLRegExp."""
        typ = type(re.compile('dummy_input'))
        self.assertIsInstance(ll_time_search.LLTimeSearch.LLRegExp, typ)

    def test_In2OutMap(self):
        """Test In2OutMap."""
        self.assertIsInstance(ll_time_search.LLTimeSearch.In2OutMap, dict)

    def test_Out2InMap(self):
        """Test Out2InMap."""
        self.assertIsInstance(ll_time_search.LLTimeSearch.Out2InMap, dict)

    def test_get_channel_input(self):
        """Test get_channel_input."""
        # TODO: implement test!
        pass

    def test_add_crates_info(self):
        """Test add_crates_info."""
        # TODO: implement test!
        pass

    def test_add_bbb_info(self):
        """Test add_bbb_info."""
        # TODO: implement test!
        pass

    def test_get_device_names(self):
        """Test get_devices."""
        # TODO: implement test!
        pass

    def test_get_device_tree(self):
        """Test get_device_tree."""
        # TODO: implement test!
        pass

    def test_reset(self):
        """Test reset."""
        # TODO: implement test!
        pass

    def test_server_online(self):
        """Test server_online."""
        # TODO: implement test!
        pass

    def test_get_connections_from_evg(self):
        """Test get_connections_from_evg."""
        # TODO: implement test!
        pass

    def test_get_connections_twds_evg(self):
        """Test get_connections_twds_evg."""
        # TODO: implement test!
        pass

    def test_get_top_chain_senders(self):
        """Test get_top_chain_senders."""
        # TODO: implement test!
        pass

    def test_get_final_receivers(self):
        """Test get_final_receivers."""
        # TODO: implement test!
        pass

    def test_get_relations_from_evg(self):
        """Test get_relations_from_evg."""
        # TODO: implement test!
        pass

    def test_get_relations_twds_evg(self):
        """Test get_relations_twds_evg."""
        # TODO: implement test!
        pass

    def test_get_hierarchy_list(self):
        """Test get_hierarchy_list."""
        # TODO: implement test!
        pass
