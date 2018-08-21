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
        'start_energy',
        'rampup_start_energy',
        'rampup_start_time',
        'rampup_stop_energy',
        'rampup_stop_time',
        'plateau_start_time',
        'plateau_energy',
        'plateau_stop_time',
        'rampdown_start_energy',
        'rampdown_start_time',
        'rampdown_stop_energy',
        'rampdown_stop_time',
        'duration',
        'update',
        'changed',
        'anomalies',
        'invalid',
        'eval_at',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                WaveformParam,
                TestWaveformParam.public_interface)
        self.assertTrue(valid)

    def _test_start_energy(self):
        """Test start_energy."""
        w = WaveformParam()
        v1 = util.get_electron_rest_energy()
        v2 = w.start_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampup_start_energy(self):
        """Test rampup_start_energy."""
        w = WaveformParam()
        v1 = w.start_energy
        v2 = w.rampup_start_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampup_start_time(self):
        """Test rampup_start_time."""
        w = WaveformParam()
        v1 = 0
        v2 = w.rampup_start_time
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampup_stop_energy(self):
        """Test rampup_stop_energy."""
        w = WaveformParam()
        v1 = w.rampup_start_energy
        v2 = w.rampup_stop_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampup_stop_time(self):
        """Test rampup_stop_time."""
        w = WaveformParam()
        v1 = w.rampup_start_time
        v2 = w.rampup_stop_time
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_plateau_energy(self):
        """Test plateau_energy."""
        w = WaveformParam()
        v1 = w.rampup_stop_energy
        v2 = w.plateau_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_plateau_start_time(self):
        """Test plateau_start_time."""
        w = WaveformParam()
        v1 = w.rampup_stop_time
        v2 = w.plateau_start_time
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_plateau_stop_time(self):
        """Test plateau_stop_time."""
        w = WaveformParam()
        v1 = w.plateau_start_time
        v2 = w.plateau_stop_time
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampdown_start_energy(self):
        """Test rampdown_start_energy."""
        w = WaveformParam()
        v1 = w.plateau_energy
        v2 = w.rampdown_start_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 < v1)

    def test_rampdown_start_time(self):
        """Test rampdown_start_time."""
        w = WaveformParam()
        v1 = w.plateau_stop_time
        v2 = w.rampdown_start_time
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_rampdown_stop_energy(self):
        """Test rampdown_stop_energy."""
        w = WaveformParam()
        v1 = w.rampdown_start_energy
        v2 = w.rampdown_stop_energy
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 < v1)

    def test_rampdown_stop_time(self):
        """Test rampdown_stop_time."""
        w = WaveformParam()
        v1 = w.rampdown_start_time
        v2 = w.rampdown_stop_time
        self.assertIsInstance(v2, float)
        self.assertTrue(v2 > v1)

    def test_changed(self):
        """Test changed."""
        w = WaveformParam()
        self.assertTrue(w.changed)
        w.update()
        self.assertFalse(w.changed)
        w.start_energy = 0.05
        self.assertTrue(w.changed)
        w.update()
        self.assertFalse(w.changed)

    def test_duration(self):
        """Test duration."""
        # TODO: implement it!
        pass

    def test_update(self):
        """Test update."""
        # TODO: implement it!
        pass

    def test_anomalies(self):
        """Test rampdown_stop_time."""
        # TODO: implement it!
        pass

    def test_invalid(self):
        """Test rampdown_stop_time."""
        # TODO: implement it!
        pass

    def test_eval_at(self):
        """Test rampdown_stop_time."""
        # TODO: implement it!
        pass


class TestWaveformDipole(unittest.TestCase):
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

    def test_constructor(self):
        """Test class constructor."""
        # default arguments
        w = WaveformDipole()
        c = w.currents
        self.assertIsInstance(c, numpy.ndarray)
        self.assertEqual(len(c), _MAX_WFMSIZE)
        s = w.strengths
        self.assertIsInstance(s, list)
        self.assertEqual(len(s), _MAX_WFMSIZE)

    def test_waveform(self):
        """Test waveform."""
        # TODO: implement it!
        pass

    def test_update(self):
        """Test update."""
        # TODO: implement it!
        pass


class TestWaveform(unittest.TestCase):
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

    def test_update(self):
        """Test update."""
        bo_b = WaveformDipole()
        qd = Waveform(maname='BO-Fam:MA-QD', dipole=bo_b)
        c1 = qd.currents
        bo_b.rampup_start_energy *= 1.01
        c2 = qd.currents
        self.assertTrue((c1 != c2).any())


if __name__ == "__main__":
    unittest.main()
