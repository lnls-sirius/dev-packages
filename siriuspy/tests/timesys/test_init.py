"""Unittest module for timesys package."""

import unittest

from siriuspy import util
from siriuspy import timesys

public_interface = ('PlotNetwork', 'time_simul')


class TestSearch(unittest.TestCase):
    """Test timesys package."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                                                timesys, public_interface)
        self.assertTrue(valid)
