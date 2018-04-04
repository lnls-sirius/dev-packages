#!/usr/bin/env python-sirius

"""Unittest module for connections.py."""

import unittest
import re
# from unittest import mock

from siriuspy import util
from siriuspy.timesys.time_data import connections

mock_flag = True

public_interface = (
    'IOs',
    'Connections',
)


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                connections,
                public_interface)
        self.assertTrue(valid)


class TestIOs(unittest.TestCase):
    """Test IOs class."""

    public_interface = (
        'LL_RGX',
        'I2O_MAP',
        'O2I_MAP',
        'get_channel_input',
    )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            connections.IOs, TestIOs.public_interface)
        self.assertTrue(valid)

    def test_LL_RGX(self):
        """Test LL_RGX."""
        typ = type(re.compile('dummy_input'))
        self.assertIsInstance(connections.IOs.LL_RGX, typ)

    def test_I2O_MAP(self):
        """Test I2O_MAP."""
        self.assertIsInstance(connections.IOs.I2O_MAP, dict)

    def test_O2I_MAP(self):
        """Test O2I_MAP."""
        self.assertIsInstance(connections.IOs.O2I_MAP, dict)

    def test_get_channel_input(self):
        """Test get_channel_input."""
        # TODO: implement test!
        pass


class TestConnections(unittest.TestCase):
    """Test Connections class."""

    public_interface = (
        'reset',
        'server_online',
        'get_connections_from_evg',
        'get_connections_twds_evg',
        'get_top_chain_senders',
        'get_final_receivers',
        'get_relations_from_evg',
        'get_relations_twds_evg',
        'get_hierarchy_list',
        'get_devices',
        'get_device_tree',
        'add_bbb_info',
        'add_crates_info',
        'plot_network',
    )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            connections.Connections, TestConnections.public_interface)
        self.assertTrue(valid)

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

    def test_get_devices(self):
        """Test get_devices."""
        # TODO: implement test!
        pass

    def test_get_device_tree(self):
        """Test get_device_tree."""
        # TODO: implement test!
        pass

    def test_add_bbb_info(self):
        """Test add_bbb_info."""
        # TODO: implement test!
        pass

    def test_add_crates_info(self):
        """Test add_crates_info."""
        # TODO: implement test!
        pass

    def test_plot_network(self):
        """Test plot_network."""
        # TODO: implement test!
        pass


if __name__ == "__main__":
    unittest.main()
