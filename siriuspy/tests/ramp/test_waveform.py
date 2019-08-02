#!/usr/bin/env python-sirius
"""Magnet class test module."""

from unittest import TestCase
import numpy
from siriuspy import util
from siriuspy.csdevice.pwrsupply import DEF_WFMSIZE as _DEF_WFMSIZE
from siriuspy.ramp import waveform
from siriuspy.ramp.waveform import WaveformParam
from siriuspy.ramp.waveform import WaveformDipole
from siriuspy.ramp.waveform import Waveform

# import siriuspy.search as _search


public_interface = (
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
                public_interface)
        self.assertTrue(valid)


class TestWaveformParam(TestCase):
    """Test WaveformParam class."""

    public_interface = (
        'N',
        'duration',
        'start_energy',
        'rampup1_start_time',
        'rampup1_start_energy',
        'rampup2_start_time',
        'rampup2_start_energy',
        'rampdown_start_time',
        'rampdown_start_energy',
        'rampdown_stop_energy',
        'rampdown_stop_time',
        'rampup_range',
        'rampup_delta',
        'rampdown_range',
        'rampdown_delta',
        'rampup1_slope',
        'rampup2_slope',
        'rampdown_slope',
        'eval_at',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                WaveformParam,
                TestWaveformParam.public_interface)
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

    def test_start_energy(self):
        """Test start_energy."""
        w = WaveformParam()
        v1 = 0.0
        v2 = w.start_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 >= v1)

    def test_rampup1_start_energy(self):
        """Test rampup1_start_energy."""
        w = WaveformParam()
        v1 = w.start_energy
        v2 = w.rampup1_start_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampup2_start_energy(self):
        """Test rampup2_start_energy."""
        w = WaveformParam()
        v1 = w.rampup1_start_energy
        v2 = w.rampup2_start_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampdown_start_energy(self):
        """Test rampdown_start_energy."""
        w = WaveformParam()
        v1 = w.rampup2_start_energy
        v2 = w.rampdown_start_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampdown_stop_energy(self):
        """Test rampdown_stop_energy."""
        w = WaveformParam()
        v1 = w.rampdown_start_energy
        v2 = w.rampdown_stop_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 < v1)

    def test_rampup_range(self):
        """Test rampup_range."""
        w = WaveformParam()
        v1 = w.rampup_range
        self.assertIsInstance(v1, float)
        self.assertTrue(v1 > 0)

    def test_rampup_delta(self):
        """Test rampup_delta."""
        w = WaveformParam()
        v1 = w.rampup_delta
        self.assertIsInstance(v1, float)

    def test_rampdown_range(self):
        """Test rampdown_range."""
        w = WaveformParam()
        v1 = w.rampdown_range
        self.assertIsInstance(v1, float)
        self.assertTrue(v1 > 0)

    def test_rampup_delta(self):
        """Test rampdown_delta."""
        w = WaveformParam()
        v1 = w.rampdown_delta
        self.assertIsInstance(v1, float)


class TestWaveformDipole(TestCase):
    """Test WaveformDipole class."""

    public_interface = (
        'update',
        'waveform',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                WaveformDipole,
                TestWaveformDipole.public_interface)
        self.assertTrue(valid)

    def _test_constructor(self):
        """Test class constructor."""
        # TODO: implement using mock to substitute server
        # default arguments
        w = WaveformDipole()
        c = w.currents
        self.assertIsInstance(c, numpy.ndarray)
        self.assertEqual(len(c), _DEF_WFMSIZE)
        s = w.strengths
        self.assertIsInstance(s, list)
        self.assertEqual(len(s), _DEF_WFMSIZE)

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

    public_interface = (
        'wfm_nrpoints',
        'duration',
        'update',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                Waveform,
                TestWaveform.public_interface)
        self.assertTrue(valid)

    def test_wfm_nrpoints(self):
        """Test wfm_nrpoints."""
        # TODO: implement it!
        pass

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
