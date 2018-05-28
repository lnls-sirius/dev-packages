#!/usr/bin/env python-sirius
"""Magnet class test module."""

import unittest
import numpy
from siriuspy import util
from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE as _MAX_WFMSIZE
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


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                waveform,
                public_interface)
        self.assertTrue(valid)


class TestWaveformParam(unittest.TestCase):
    """Test WaveformParam class."""

    public_interface = (
        'start_value',
        'rampup_start_index',
        'rampup_start_value',
        'rampup_start_time',
        'rampup_stop_index',
        'rampup_stop_value',
        'rampup_stop_time',
        'plateau_start_index',
        'plateau_start_time',
        'plateau_stop_index',
        'plateau_stop_time',
        'plateau_value',
        'rampdown_start_index',
        'rampdown_start_value',
        'rampdown_start_time',
        'rampdown_stop_index',
        'rampdown_stop_value',
        'rampdown_stop_time',
        'stop_value',
        'waveform',
        'boundary_indices',
        'boundary_times',
        'wfm_nrpoints',
        'duration',
        'deprecated',
        'rampup_change',
        'rampdown_change',
        'update',
        'check',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                WaveformParam,
                TestWaveformParam.public_interface)
        self.assertTrue(valid)

    def test_start_value(self):
        """Test start_value."""
        # TODO: implement it!
        pass

    def test_rampup_start_index(self):
        """Test rampup_start_index."""
        w = WaveformParam()
        ind = w.boundary_indices
        i = w.rampup_start_index
        self.assertIn(i, ind)
        self.assertTrue(i >= ind[0])

    def test_rampup_start_value(self):
        """Test rampup_start_value."""
        w = WaveformParam()
        v = w.rampup_start_value
        self.assertIsInstance(v, float)

    def test_rampup_stop_index(self):
        """Test rampup_stop_index."""
        w = WaveformParam()
        ind = w.boundary_indices
        i1 = w.rampup_start_index
        i2 = w.rampup_start_index
        self.assertIn(i2, ind)
        self.assertTrue(i2 >= i1)

    def test_rampup_stop_value(self):
        """Test rampup_stop_value."""
        w = WaveformParam()
        v1 = w.rampup_start_value
        v2 = w.rampup_stop_value
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def _test_plateau_start_index(self):
        """Test plateau_start_index."""
        # TODO: implement it!
        pass

    def _test_plateau_stop_index(self):
        """Test plateau_stop_index."""
        # TODO: implement it!
        pass

    def _test_plateau_value(self):
        """Test plateau_value."""
        # TODO: implement it!
        pass

    def _test_rampdown_start_index(self):
        """Test rampdown_start_index."""
        # TODO: implement it!
        pass

    def _test_rampdown_start_value(self):
        """Test rampdown_start_value."""
        # TODO: implement it!
        pass

    def _test_rampdown_stop_index(self):
        """Test rampdown_stop_index."""
        # TODO: implement it!
        pass

    def _test_rampdown_stop_value(self):
        """Test rampdown_stop_value."""
        # TODO: implement it!
        pass

    def _test_stop_value(self):
        """Test stop_value."""
        # TODO: implement it!
        pass

    def test_waveform(self):
        """Test waveform."""
        w = WaveformParam()
        wfm = w.waveform
        self.assertIsInstance(wfm, numpy.ndarray)

    def test_boundary_indices(self):
        """Test boundary_indices."""
        w = WaveformParam()
        ind = w.boundary_indices
        self.assertIsInstance(ind, list)
        self.assertEqual(len(ind), 8)

    def test_wfm_nrpoints(self):
        """Test size."""
        w = WaveformParam()
        self.assertIsInstance(w.wfm_nrpoints, int)

    def test_deprecated(self):
        """Test deprecated."""
        w = WaveformParam()
        self.assertFalse(w.deprecated)
        w.rampup_start_index = 2
        self.assertTrue(w.deprecated)

    def _test_rampup_change(self):
        """Test rampup_change."""
        # TODO: implement it!
        pass

    def _test_rampdown_change(self):
        """Test rampdown_change."""
        # TODO: implement it!
        pass


class TestWaveformDipole(unittest.TestCase):
    """Test WaveformDipole class."""

    public_interface = ()

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                WaveformDipole,
                TestWaveformDipole.public_interface)
        self.assertTrue(valid)

    def test_constructor(self):
        """Test class constructor."""
        # default arguments
        w = WaveformDipole()
        self.assertEqual(w.maname, 'BO-Fam:MA-B')
        c = w.currents
        self.assertIsInstance(c, numpy.ndarray)
        self.assertEqual(len(c), _MAX_WFMSIZE)
        s = w.strengths
        self.assertIsInstance(s, numpy.ndarray)
        self.assertEqual(len(s), _MAX_WFMSIZE)


class TestWaveform(unittest.TestCase):
    """Test Waveform class."""

    public_interface = (
        'update',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                Waveform,
                TestWaveform.public_interface)
        self.assertTrue(valid)

    def test_update(self):
        """Test update."""
        bo_b = WaveformDipole()
        qd = Waveform(maname='BO-Fam:MA-QD', dipole=bo_b)
        c1 = qd.currents
        bo_b.rampup_start_value *= 1.01
        c2 = qd.currents
        self.assertTrue((c1 != c2).any())


if __name__ == "__main__":
    unittest.main()
