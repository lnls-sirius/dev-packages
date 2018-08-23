#!/usr/bin/env python-sirius

"""Unittest module for time_simul.py."""

import unittest
# import re
# from unittest import mock

from siriuspy import util
from siriuspy.timesys.time_simul import time_simul

mock_flag = True

public_interface = (
    'TimingSimulation',
)


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                time_simul,
                public_interface)
        self.assertTrue(valid)


class TestTimingSimulation(unittest.TestCase):
    """Test TimingSimulation class."""

    public_interface = (
        'EVG_PREFIX',
        'EVRs',
        'EVEs',
        'AMCFPGAEVRs',
        'Fouts',
        'get_database',
        'add_injection_callback',
        'remove_injection_callback',
        'get_propty',
        'set_propty',
    )

    def test_public_interface(self):
        """Test class public interface."""
        valid = util.check_public_interface_namespace(
            time_simul.TimingSimulation, TestTimingSimulation.public_interface)
        self.assertTrue(valid)

    def test_EVG_PREFIX(self):
        """Test EVG_PREFIX."""
        # TODO: implement test!
        pass

    def test_EVRs(self):
        """Test EVRs."""
        # TODO: implement test!
        pass

    def test_EVEs(self):
        """Test EVEs."""
        # TODO: implement test!
        pass

    def test_AMCFPGAEVRs(self):
        """Test AMCFPGAEVRs."""
        # TODO: implement test!
        pass

    def test_Fouts(self):
        """Test Fouts."""
        # TODO: implement test!
        pass

    def test_get_database(self):
        """Test get_database."""
        # TODO: implement test!
        pass

    def test_add_injection_callback(self):
        """Test add_injection_callback."""
        # TODO: implement test!
        pass

    def test_remove_injection_callback(self):
        """Test remove_injection_callback."""
        # TODO: implement test!
        pass

    def test_get_propty(self):
        """Test get_propty."""
        # TODO: implement test!
        pass

    def test_set_propty(self):
        """Test set_propty."""
        # TODO: implement test!
        pass
