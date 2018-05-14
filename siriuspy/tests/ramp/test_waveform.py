#!/usr/bin/env python-sirius
"""Magnet class test module."""

import unittest
import numpy
from siriuspy import util
from siriuspy.ramp import waveform
from siriuspy.ramp.waveform import WaveformDipole
# import siriuspy.search as _search


public_interface = (
    'WaveformDipole',
)


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                waveform,
                public_interface)
        self.assertTrue(valid)


class TestWaveformDipole(unittest.TestCase):
    """Test Waveform class."""

    public_interface = (
        'start_value',
        'rampup_start_index',
        'rampup_start_value',
        'rampup_stop_index',
        'rampup_stop_value',
        'plateau_start_index',
        'plateau_stop_index',
        'plateau_value',
        'rampdown_start_index',
        'rampdown_start_value',
        'rampdown_stop_index',
        'rampdown_stop_value',
        'stop_value',
        'waveform',
        'boundary_indices',
        'size',
        'deprecated',
        'rampup_change',
        'rampdown_change',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                WaveformDipole,
                TestWaveformDipole.public_interface)
        self.assertTrue(valid)

    def test_start_value(self):
        """Test start_value."""
        # TODO: implement it!
        pass

    def test_rampup_start_index(self):
        """Test rampup_start_index."""
        w = WaveformDipole()
        ind = w.boundary_indices
        i = w.rampup_start_index
        self.assertIn(i, ind)
        self.assertTrue(i >= ind[0])

    def test_rampup_start_value(self):
        """Test rampup_start_value."""
        w = WaveformDipole()
        v = w.rampup_start_value
        self.assertIsInstance(v, float)

    def test_rampup_stop_index(self):
        """Test rampup_stop_index."""
        w = WaveformDipole()
        ind = w.boundary_indices
        i1 = w.rampup_start_index
        i2 = w.rampup_start_index
        self.assertIn(i2, ind)
        self.assertTrue(i2 >= i1)

    def test_rampup_stop_value(self):
        """Test rampup_stop_value."""
        w = WaveformDipole()
        v1 = w.rampup_start_value
        v2 = w.rampup_stop_value
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_plateau_start_index(self):
        """Test plateau_start_index."""
        # TODO: implement it!
        pass

    def test_plateau_stop_index(self):
        """Test plateau_stop_index."""
        # TODO: implement it!
        pass

    def test_plateau_value(self):
        """Test plateau_value."""
        # TODO: implement it!
        pass

    def test_rampdown_start_index(self):
        """Test rampdown_start_index."""
        # TODO: implement it!
        pass

    def test_rampdown_start_value(self):
        """Test rampdown_start_value."""
        # TODO: implement it!
        pass

    def test_rampdown_stop_index(self):
        """Test rampdown_stop_index."""
        # TODO: implement it!
        pass

    def test_rampdown_stop_value(self):
        """Test rampdown_stop_value."""
        # TODO: implement it!
        pass

    def test_stop_value(self):
        """Test stop_value."""
        # TODO: implement it!
        pass

    def test_waveform(self):
        """Test waveform."""
        w = WaveformDipole()
        wfm = w.waveform
        self.assertIsInstance(wfm, numpy.ndarray)

    def test_boundary_indices(self):
        """Test boundary_indices."""
        w = WaveformDipole()
        ind = w.boundary_indices
        self.assertIsInstance(ind, list)
        self.assertTrue(len(ind) == 8)

    def test_size(self):
        """Test size."""
        w = WaveformDipole()
        self.assertIsInstance(w.size, int)

    def test_deprecated(self):
        """Test deprecated."""
        w = WaveformDipole()
        self.assertFalse(w.deprecated)
        w.rampup_start_index = 2
        self.assertTrue(w.deprecated)

    def test_rampup_change(self):
        """Test rampup_change."""
        # TODO: implement it!
        pass

    def test_rampdown_change(self):
        """Test rampdown_change."""
        # TODO: implement it!
        pass


if __name__ == "__main__":
    unittest.main()
