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


PUB_INTERFACE = (
    'WaveformParam',
    'WaveformDipole',
    'Waveform',
)


class TestModule(TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(waveform, PUB_INTERFACE)
        self.assertTrue(valid)


class TestWaveformParam(TestCase):
    """Test WaveformParam class."""

    PUB_INTERFACE = (
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
            WaveformParam, TestWaveformParam.PUB_INTERFACE)
        self.assertTrue(valid)

    def test_rampup1_start_time(self):
        """Test rampup1_start_time."""
        wfm = WaveformParam()
        val1 = 0.0
        val2 = wfm.rampup1_start_time
        self.assertIsInstance(val2, float)
        self.assertTrue(val2 > val1)

    def test_rampup2_start_time(self):
        """Test rampup2_start_time."""
        wfm = WaveformParam()
        val1 = wfm.rampup1_start_time
        val2 = wfm.rampup2_start_time
        self.assertIsInstance(val2, float)
        self.assertTrue(val2 > val1)

    def test_rampdown_start_time(self):
        """Test rampdown_start_time."""
        wfm = WaveformParam()
        val1 = wfm.rampup2_start_time
        val2 = wfm.rampdown_start_time
        self.assertIsInstance(val2, float)
        self.assertTrue(val2 > val1)

    def test_rampdown_stop_time(self):
        """Test rampdown_stop_time."""
        wfm = WaveformParam()
        val1 = wfm.rampdown_start_time
        val2 = wfm.rampdown_stop_time
        self.assertIsInstance(val2, float)
        self.assertTrue(val2 > val1)

    def test_duration(self):
        """Test duration."""
        wfm = WaveformParam()
        val1 = wfm.rampdown_stop_time
        val2 = wfm.duration
        self.assertIsInstance(val2, float)
        self.assertTrue(val2 > val1)

    def test_start_value(self):
        """Test start_value."""
        wfm = WaveformParam()
        val1 = 0.0
        val2 = wfm.start_value
        self.assertIsInstance(val2, float)
        self.assertTrue(val2 >= val1)

    def test_rampup1_start_value(self):
        """Test rampup1_start_value."""
        wfm = WaveformParam()
        val1 = wfm.start_value
        val2 = wfm.rampup1_start_value
        self.assertIsInstance(val2, float)
        self.assertTrue(val2 > val1)

    def test_rampup2_start_value(self):
        """Test rampup2_start_value."""
        wfm = WaveformParam()
        val1 = wfm.rampup1_start_value
        val2 = wfm.rampup2_start_value
        self.assertIsInstance(val2, float)
        self.assertTrue(val2 > val1)

    def test_rampdown_start_value(self):
        """Test rampdown_start_value."""
        wfm = WaveformParam()
        val1 = wfm.rampup2_start_value
        val2 = wfm.rampdown_start_value
        self.assertIsInstance(val2, float)
        self.assertTrue(val2 > val1)

    def test_rampdown_stop_value(self):
        """Test rampdown_stop_value."""
        wfm = WaveformParam()
        val1 = wfm.rampdown_start_value
        val2 = wfm.rampdown_stop_value
        self.assertIsInstance(val2, float)
        self.assertTrue(val2 < val1)

    def test_rampup_smooth_intvl(self):
        """Test rampup_smooth_intvl."""
        wfm = WaveformParam()
        val1 = wfm.rampup_smooth_intvl
        self.assertIsInstance(val1, float)
        self.assertTrue(val1 > 0)

    def test_rampup_smooth_value(self):
        """Test rampup_smooth_value."""
        wfm = WaveformParam()
        val1 = wfm.rampup_smooth_value
        self.assertIsInstance(val1, float)

    def test_rampdown_smooth_intvl(self):
        """Test rampdown_smooth_intvl."""
        wfm = WaveformParam()
        val1 = wfm.rampdown_smooth_intvl
        self.assertIsInstance(val1, float)
        self.assertTrue(val1 > 0)

    def test_rampdown_smooth_value(self):
        """Test rampdown_smooth_value."""
        wfm = WaveformParam()
        val1 = wfm.rampdown_smooth_value
        self.assertIsInstance(val1, float)


class TestWaveformDipole(TestCase):
    """Test WaveformDipole class."""

    PUB_INTERFACE = (
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
            WaveformDipole, TestWaveformDipole.PUB_INTERFACE)
        self.assertTrue(valid)

    def _test_constructor(self):
        """Test class constructor."""
        # TODO: implement using mock to substitute server
        # default arguments
        wfm = WaveformDipole()
        curr = wfm.currents
        self.assertIsInstance(curr, numpy.ndarray)
        self.assertEqual(len(curr), _DEF_WFMSIZE_OTHERS)
        stren = wfm.strengths
        self.assertIsInstance(stren, list)
        self.assertEqual(len(stren), _DEF_WFMSIZE_OTHERS)

    def test_waveform(self):
        """Test waveform."""
        # TODO: implement it!

    def test_update(self):
        """Test update."""
        # TODO: implement it!


class TestWaveform(TestCase):
    """Test Waveform class."""

    PUB_INTERFACE = (
        'duration',
        'update',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
            Waveform, TestWaveform.PUB_INTERFACE)
        self.assertTrue(valid)

    def test_duration(self):
        """Test duration."""
        # TODO: implement it!

    def _test_update(self):
        """Test update."""
        # TODO: implement using mock to substitute server
        bo_b = WaveformDipole()
        defoc = Waveform(psname='BO-Fam:MA-QD', dipole=bo_b)
        curr1 = defoc.currents
        bo_b.rampup1_start_energy *= 1.01
        curr2 = defoc.currents
        self.assertTrue((curr1 != curr2).any())
