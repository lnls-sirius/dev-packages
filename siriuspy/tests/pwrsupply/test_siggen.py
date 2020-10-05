#!/usr/bin/env python-sirius

"""Unittest module for siggen.py."""

from unittest import TestCase
import siriuspy.util as util
import siriuspy.pwrsupply.siggen as siggen


public_interface = (
    'DEFAULT_SIGGEN_CONFIG',
    'Signal',
    'SignalSine',
    'SignalDampedNSine',
    'SignalDampedSine',
    'SignalDampedSquaredSine',
    'SignalTrapezoidal',
    'SignalSquare',
    'SigGenFactory',
)


class TestModule(TestCase):
    """Test Module."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(siggen, public_interface)
        self.assertTrue(valid)

    def test_DEFAULT_SIGGEN_CONFIG(self):
        """Test DEFAULT_SIGGEN_CONFIG."""
        defconfig = siggen.DEFAULT_SIGGEN_CONFIG
        self.assertIsInstance(defconfig, tuple)
        self.assertTrue(len(defconfig), 9)


class TestSigGenConfig(TestCase):
    """Test SigGenconfig class."""

    public_interface = (
        'duration',
        'value',
        'cycle_time',
        'rampup_time',
        'theta_begin',
        'rampdown_time',
        'theta_end',
        'plateau_time',
        'decay_time',
        'get_waveform',
        'reset',
    )

    def test_public_interface(self):
        """Test class's public interface."""
        valid = util.check_public_interface_namespace(
            siggen.Signal, TestSigGenConfig.public_interface)
        self.assertTrue(valid)

    def test_duration(self):
        """Test duration."""
        # TODO: implement test!
        pass

    def test_rampup_time(self):
        """Test rampup_time."""
        # TODO: implement test!
        pass

    def test_theta_begin(self):
        """Test theta_begin."""
        # TODO: implement test!
        pass

    def test_rampdown_time(self):
        """Test rampdown_time."""
        # TODO: implement test!
        pass

    def test_theta_end(self):
        """Test theta_end."""
        # TODO: implement test!
        pass

    def test_plateau_time(self):
        """Test plateau_time."""
        # TODO: implement test!
        pass

    def test_decay_time(self):
        """Test decay_time."""
        # TODO: implement test!
        pass

    def test_get_waveform(self):
        """Test get_waveform."""
        # TODO: implement test!
        pass
