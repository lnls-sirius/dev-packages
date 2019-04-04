#!/usr/bin/env python-sirius

"""Unittest module for ll_time_search.py."""

from unittest import TestCase
from siriuspy import util
from siriuspy.timesys import plot_network

mock_flag = True

public_interface = ('PlotNetwork', )


class TestModule(TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                                            plot_network, public_interface)
        self.assertTrue(valid)


class TestPlotNetwork(TestCase):
    """Test PlotNetwork class."""

    public_interface = ('plot', )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            plot_network.PlotNetwork, TestPlotNetwork.public_interface)
        self.assertTrue(valid)

    def test_plot(self):
        """Test plot."""
        # TODO: implement test!
        pass
