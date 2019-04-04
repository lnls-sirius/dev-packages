#!/usr/bin/env python-sirius

"""Unittest module for ll_time_search.py."""

import unittest

from siriuspy import util
from ..mock_servweb import MockServConf


mock_flag = True

public_interface = ('PlotNetwork', )


class TestModule(MockServConf):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        from siriuspy.timesys import plot_network
        valid = util.check_public_interface_namespace(
                                            plot_network, public_interface)
        self.assertTrue(valid)


class TestPlotNetwork(MockServConf):
    """Test PlotNetwork class."""

    public_interface = ('plot', )

    def test_public_interface(self):
        """Test class public interface."""
        from siriuspy.timesys import plot_network
        valid = util.check_public_interface_namespace(
            plot_network.PlotNetwork, TestPlotNetwork.public_interface)
        self.assertTrue(valid)

    def test_plot(self):
        """Test plot."""
        # TODO: implement test!
        pass


if __name__ == "__main__":
    unittest.main()
