#!/usr/bin/env python-sirius

"""Unittest module for callbacks.py."""

from unittest import mock, TestCase
import siriuspy.util as util
import siriuspy.callbacks as callbacks


public_interface = (
    'Callback',
)


class TestCallbacks(TestCase):
    """Test util."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                                        callbacks, public_interface)
        self.assertTrue(valid)


class TestCallbackClass(TestCase):
    """Test Callback Class."""

    public_interface = (
        'add_callback',
        'remove_callback',
        'clear_callbacks',
        'run_callbacks',
        'run_callback',
        )

    def test_public_interface(self):
        """Test class's public interface."""
        valid = util.check_public_interface_namespace(
            callbacks.Callback, TestCallbackClass.public_interface)
        self.assertTrue(valid)

    def test_constructor(self):
        """Test class constructor."""
        self.assertRaises(ValueError, callbacks.Callback, 2)
        self.assertRaises(ValueError, callbacks.Callback, [2, 4])
        c = callbacks.Callback(self._run_tes0)
        self.assertEqual(1, len(c._callbacks))
        c = callbacks.Callback([self._run_tes0, self._run_tes1])
        self.assertEqual(2, len(c._callbacks))

    def test_add_callback(self):
        """Test add_callback method."""
        c = callbacks.Callback()
        self.assertRaises(ValueError, c.add_callback, callback=4)
        self.assertEqual(0, c.add_callback(callback=lambda x: x))
        self.assertEqual(
            4, c.add_callback(callback=lambda x: x, index=4))
        self.assertEqual(
            5, c.add_callback(callback=lambda x: x, a=4))

    def test_remove_callback(self):
        """Test remove_callback method."""
        c = callbacks.Callback()
        ind = c.add_callback(callback=lambda x: x)
        ind = c.add_callback(callback=lambda x: x)
        c.remove_callback(index=ind)
        self.assertEqual(1, len(c._callbacks))
        c.remove_callback()
        self.assertEqual(1, len(c._callbacks))
        c.remove_callback(index=ind)
        self.assertEqual(1, len(c._callbacks))

    def test_clear_callbacks(self):
        """Test clear_callbacks method."""
        c = callbacks.Callback()
        c.add_callback(callback=lambda x: x)
        c.add_callback(callback=lambda x: x)
        c.clear_callbacks()
        self.assertEqual(0, len(c._callbacks))

    def test_run_callbacks(self):
        """Test run_callbacks method."""
        self.TES = 0
        c = callbacks.Callback()
        c.add_callback(callback=self._run_tes0)
        c.run_callbacks(2)
        self.assertEqual(self.TES, 2)
        c.add_callback(callback=self._run_tes0)
        c.run_callbacks(3)
        self.assertEqual(self.TES, 8)

    def test_run_callback(self):
        """Test run_callback method."""
        self.TES = 0
        c = callbacks.Callback()
        ind1 = c.add_callback(callback=self._run_tes1)
        ind2 = c.add_callback(callback=self._run_tes2)
        c.run_callback(ind1)
        self.assertEqual(self.TES, 1)
        c.run_callbacks(ind2)
        self.assertEqual(self.TES, 2)

    def _run_tes0(self, a, *args, **kwargs):
        self.TES += a

    def _run_tes1(self, *args, **kwargs):
        self.TES = 1

    def _run_tes2(self, *args, **kwargs):
        self.TES = 2
