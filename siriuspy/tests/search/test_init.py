
"""Unittest module for search package."""

import unittest

from siriuspy import util
from siriuspy import search

public_interface = (
    'PSSearch',
    'MASearch',
    'HLTimeSearch',
    'LLTimeSearch',
)


class TestSearch(unittest.TestCase):
    """Test Search module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(search, public_interface)
        self.assertTrue(valid)
