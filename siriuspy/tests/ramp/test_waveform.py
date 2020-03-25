#!/usr/bin/env python-sirius
"""Magnet class test module."""

from unittest import TestCase
import numpy

from siriuspy import util
from siriuspy.pwrsupply.csdev import DEF_WFMSIZE_OTHERS as \
    _DEF_WFMSIZE_OTHERS
from siriuspy.ramp import waveform
from siriuspy.ramp.waveform import WaveformParam
from siriuspy.ramp.waveform import WaveformDipole
from siriuspy.ramp.waveform import Waveform


PUBLIC_INTERFACE = (
    'WaveformParam',
    'WaveformDipole',
    'Waveform',
)


class TestModule(TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                waveform,
                PUBLIC_INTERFACE)
        self.assertTrue(valid)


class TestWaveformParam(TestCase):
    """Test WaveformParam class."""

    PUBLIC_INTERFACE = (
        'N',
        'duration',
        'start_value',
        'rampup1_start_time',
        'rampup1_start_value',
        'rampup2_start_time',
        'rampup2_start_value',
        'rampdown_start_time',
        'rampdown_start_value',
        'rampdown_stop_value',
        'rampdown_stop_time',
        'rampup_smooth_intvl',
        'rampup_smooth_value',
        'rampdown_smooth_intvl',
        'rampdown_smooth_value',
        'rampup1_slope',
        'rampup2_slope',
        'rampdown_slope',
        'eval_at',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                WaveformParam,
                TestWaveformParam.PUBLIC_INTERFACE)
        self.assertTrue(valid)

    def test_rampup1_start_time(self):
        """Test rampup1_start_time."""
        w = WaveformParam()
        v1 = 0.0
        v2 = w.rampup1_start_time
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampup2_start_time(self):
        """Test rampup2_start_time."""
        w = WaveformParam()
        v1 = w.rampup1_start_time
        v2 = w.rampup2_start_time
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampdown_start_time(self):
        """Test rampdown_start_time."""
        w = WaveformParam()
        v1 = w.rampup2_start_time
        v2 = w.rampdown_start_time
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampdown_stop_time(self):
        """Test rampdown_stop_time."""
        w = WaveformParam()
        v1 = w.rampdown_start_time
        v2 = w.rampdown_stop_time
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_duration(self):
        """Test duration."""
        w = WaveformParam()
        v1 = w.rampdown_stop_time
        v2 = w.duration
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_start_value(self):
        """Test start_value."""
        w = WaveformParam()
        v1 = 0.0
        v2 = w.start_value
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 >= v1)

    def test_rampup1_start_value(self):
        """Test rampup1_start_value."""
        w = WaveformParam()
        v1 = w.start_value
        v2 = w.rampup1_start_value
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampup2_start_value(self):
        """Test rampup2_start_value."""
        w = WaveformParam()
        v1 = w.rampup1_start_value
        v2 = w.rampup2_start_value
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampdown_start_value(self):
        """Test rampdown_start_value."""
        w = WaveformParam()
        v1 = w.rampup2_start_value
        v2 = w.rampdown_start_value
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampdown_stop_value(self):
        """Test rampdown_stop_value."""
        w = WaveformParam()
        v1 = w.rampdown_start_value
        v2 = w.rampdown_stop_value
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 < v1)

    def test_rampup_smooth_intvl(self):
        """Test rampup_smooth_intvl."""
        w = WaveformParam()
        v1 = w.rampup_smooth_intvl
        self.assertIsInstance(v1, float)
        self.assertTrue(v1 > 0)

    def test_rampup_smooth_value(self):
        """Test rampup_smooth_value."""
        w = WaveformParam()
        v1 = w.rampup_smooth_value
        self.assertIsInstance(v1, float)

    def test_rampdown_smooth_intvl(self):
        """Test rampdown_smooth_intvl."""
        w = WaveformParam()
        v1 = w.rampdown_smooth_intvl
        self.assertIsInstance(v1, float)
        self.assertTrue(v1 > 0)

    def test_rampdown_smooth_value(self):
        """Test rampdown_smooth_value."""
        w = WaveformParam()
        v1 = w.rampdown_smooth_value
        self.assertIsInstance(v1, float)


class TestWaveformDipole(TestCase):
    """Test WaveformDipole class."""

    PUBLIC_INTERFACE = (
        'waveform',
        'start_energy',
        'rampup1_start_energy',
        'rampup2_start_energy',
        'rampdown_start_energy',
        'rampdown_stop_energy',
        'rampup_smooth_energy',
        'rampdown_smooth_energy',
        'start_value',
        'rampup1_start_value',
        'rampup2_start_value',
        'rampdown_start_value',
        'rampdown_stop_value',
        'rampup_smooth_value',
        'rampdown_smooth_value',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                WaveformDipole,
                TestWaveformDipole.PUBLIC_INTERFACE)
        self.assertTrue(valid)

    def _test_constructor(self):
        """Test class constructor."""
        # TODO: implement using mock to substitute server
        # default arguments
        w = WaveformDipole()
        c = w.currents
        self.assertIsInstance(c, numpy.ndarray)
        self.assertEqual(len(c), _DEF_WFMSIZE_OTHERS)
        s = w.strengths
        self.assertIsInstance(s, list)
        self.assertEqual(len(s), _DEF_WFMSIZE_OTHERS)

    def test_waveform(self):
        """Test waveform."""
        # TODO: implement it!
        pass

    def test_update(self):
        """Test update."""
        # TODO: implement it!
        pass


class TestWaveform(TestCase):
    """Test Waveform class."""

    PUBLIC_INTERFACE = (
        'duration',
        'update',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                Waveform,
                TestWaveform.PUBLIC_INTERFACE)
        self.assertTrue(valid)

    def test_duration(self):
        """Test duration."""
        # TODO: implement it!
        pass

    def _test_update(self):
        """Test update."""
        # TODO: implement using mock to substitute server
        bo_b = WaveformDipole()
        qd = Waveform(maname='BO-Fam:MA-QD', dipole=bo_b)
        c1 = qd.currents
        bo_b.rampup_start_energy *= 1.01
        c2 = qd.currents
        self.assertTrue((c1 != c2).any())
