#!/usr/bin/env python-sirius

"""Unittest module for ll_time_search.py."""

import unittest
import re
# from unittest import mock

from siriuspy import util
from siriuspy.search import ll_time_search

mock_flag = True

public_interface = (
    'LLTimeSearch',
)


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                ll_time_search,
                public_interface)
        self.assertTrue(valid)


class TestLLTimeSearch(unittest.TestCase):
    """Test LLTimeSearch class."""

    public_interface = (
        'll_rgx',
        'i2o_map',
        'o2i_map',
        'get_channel_input',
        'plot_network',
        'add_crates_info',
        'add_bbb_info',
        'get_devices_by_type',
        'get_device_tree',
        'reset',
        'server_online',
        'get_connections_from_evg',
        'get_connections_twds_evg',
        'get_top_chain_senders',
        'get_final_receivers',
        'get_relations_from_evg',
        'get_relations_twds_evg',
        'get_hierarchy_list',
    )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            ll_time_search.LLTimeSearch, TestLLTimeSearch.public_interface)
        self.assertTrue(valid)

    def test_ll_rgx(self):
        """Test LL_RGX."""
        typ = type(re.compile('dummy_input'))
        self.assertIsInstance(ll_time_search.LLTimeSearch.ll_rgx, typ)

    def test_i2o_map(self):
        """Test I2O_MAP."""
        self.assertIsInstance(ll_time_search.LLTimeSearch.i2o_map, dict)

    def test_o2i_map(self):
        """Test O2I_MAP."""
        self.assertIsInstance(ll_time_search.LLTimeSearch.o2i_map, dict)

    def test_get_channel_input(self):
        """Test get_channel_input."""
        # TODO: implement test!
        pass

    def test_plot_network(self):
        """Test plot_network."""
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

    def test_get_devices_by_type(self):
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


if __name__ == "__main__":
    unittest.main()
