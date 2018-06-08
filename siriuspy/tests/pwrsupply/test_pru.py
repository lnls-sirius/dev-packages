#!/usr/bin/env python-sirius

"""Test PRU module."""
import unittest
# from unittest import mock

from siriuspy import util
from siriuspy.pwrsupply import pru
from siriuspy.pwrsupply.pru import Const
from siriuspy.pwrsupply.pru import PRUInterface
from siriuspy.pwrsupply.pru import PRU
from siriuspy.pwrsupply.pru import PRUSim


public_interface = (
    'Const',
    'PRUInterface',
    'PRU',
    'PRUSim',
)


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                pru,
                public_interface)
        self.assertTrue(valid)


class TestConst(unittest.TestCase):
    """Test Const class interface."""

    public_interface = (
        'RETURN',
        'SYNC_MODE',
        'SYNC_STATE',
    )

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                Const,
                TestConst.public_interface)
        self.assertTrue(valid)

    def test_RETURN(self):
        """Test RETURN."""
        self.assertIn('SYNC_OFF', dir(Const.RETURN))
        self.assertIn('SYNC_OFF', dir(Const.RETURN))
        self.assertIn('SYNC_ON', dir(Const.RETURN))
        self.assertIn('OK', dir(Const.RETURN))

    def test_SYNC_MODE(self):
        """Test SYNC_MODE."""
        modes = ('MIGINT', 'MIGEND', 'RMPINT', 'RMPEND', 'BRDCST')
        self.assertIn('ALL', dir(Const.SYNC_MODE))
        self.assertIsInstance(Const.SYNC_MODE.ALL, tuple)
        for mode in modes:
            self.assertIn(mode, dir(Const.SYNC_MODE))
            self.assertIn(getattr(Const.SYNC_MODE, mode), Const.SYNC_MODE.ALL)

    def test_SYNC_STATE(self):
        """Test SYNC_STATE."""
        # TODO: implement test!
        self.assertIn('OFF', dir(Const.SYNC_STATE))
        self.assertIn('ON', dir(Const.SYNC_STATE))


class TestPRUInterface(unittest.TestCase):
    """Test PRUInterface API."""

    public_interface = (
        'VERSION',
        'simulated',
        'sync_mode',
        'sync_status',
        'sync_start',
        'sync_stop',
        'sync_abort',
        'sync_pulse_count',
        'clear_pulse_count_sync',
        'UART_write',
        'UART_read',
        'curve',
        'read_curve_pointer',
        'set_curve_pointer',
        'set_curve_block',
        'read_curve_block',
        'close',
    )

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(util.check_public_interface_namespace(
            PRUInterface, TestPRUInterface.public_interface))

    def test_VERSION(self):
        """Test VERSION."""
        self.assertIsInstance(PRUInterface.VERSION, str)

    def test_simulated(self):
        """Test simulated."""
        # TODO: implement test!
        pass

    def test_sync_mode(self):
        """Test sync_mode."""
        # TODO: implement test!
        pass

    def test_sync_status(self):
        """Test sync_status."""
        # TODO: implement test!
        pass

    def test_sync_start(self):
        """Test sync_start."""
        # TODO: implement test!
        pass

    def test_sync_stop(self):
        """Test sync_stop."""
        # TODO: implement test!
        pass

    def test_sync_abort(self):
        """Test sync_abort."""
        # TODO: implement test!
        pass

    def test_sync_pulse_count(self):
        """Test sync_pulse_count."""
        # TODO: implement test!
        pass

    def test_clear_pulse_count_sync(self):
        """Test clear_pulse_count_sync."""
        # TODO: implement test!
        pass

    def test_UART_write(self):
        """Test UART_write."""
        # TODO: implement test!
        pass

    def test_UART_read(self):
        """Test UART_read."""
        # TODO: implement test!
        pass

    def test_curve(self):
        """Test curve."""
        # TODO: implement test!
        pass

    def test_read_curve_pointer(self):
        """Test read_curve_pointer."""
        # TODO: implement test!
        pass

    def test_set_curve_pointer(self):
        """Test set_curve_pointer."""
        # TODO: implement test!
        pass

    def test_set_curve_block(self):
        """Test set_curve_block."""
        # TODO: implement test!
        pass

    def test_read_curve_block(self):
        """Test read_curve_block."""
        # TODO: implement test!
        pass

    def test_close(self):
        """Test close."""
        # TODO: implement test!
        pass


class TestPRU(unittest.TestCase):
    """Test PRU API."""

    public_interface = ()

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(util.check_public_interface_namespace(
            PRU, TestPRU.public_interface))

    def test_sync_status(self):
        """Test sync_status."""
        # TODO: implement test!
        pass

    def test_sync_start(self):
        """Test sync_start."""
        # TODO: implement test!
        pass

    def test_sync_stop(self):
        """Test sync_stop."""
        # TODO: implement test!
        pass

    def test_sync_abort(self):
        """Test sync_abort."""
        # TODO: implement test!
        pass

    def test_sync_pulse_count(self):
        """Test sync_pulse_count."""
        # TODO: implement test!
        pass

    def test_clear_pulse_count_sync(self):
        """Test clear_pulse_count_sync."""
        # TODO: implement test!
        pass

    def test_UART_write(self):
        """Test UART_write."""
        # TODO: implement test!
        pass

    def test_UART_read(self):
        """Test UART_read."""
        # TODO: implement test!
        pass

    def test_curve(self):
        """Test curve."""
        # TODO: implement test!
        pass

    def test_read_curve_pointer(self):
        """Test read_curve_pointer."""
        # TODO: implement test!
        pass

    def test_set_curve_pointer(self):
        """Test set_curve_pointer."""
        # TODO: implement test!
        pass

    def test_set_curve_block(self):
        """Test set_curve_block."""
        # TODO: implement test!
        pass

    def test_read_curve_block(self):
        """Test read_curve_block."""
        # TODO: implement test!
        pass

    def test_close(self):
        """Test close."""
        # TODO: implement test!
        pass


class TestPRUSim(unittest.TestCase):
    """Test PRUSim API."""

    public_interface = (
        'emulate_trigger',
        'add_callback'
    )

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(util.check_public_interface_namespace(
            PRUSim, TestPRUSim.public_interface))

    def test_sync_status(self):
        """Test sync_status."""
        # TODO: implement test!
        pass

    def test_sync_start(self):
        """Test sync_start."""
        # TODO: implement test!
        pass

    def test_sync_stop(self):
        """Test sync_stop."""
        # TODO: implement test!
        pass

    def test_sync_abort(self):
        """Test sync_abort."""
        # TODO: implement test!
        pass

    def test_sync_pulse_count(self):
        """Test sync_pulse_count."""
        # TODO: implement test!
        pass

    def test_clear_pulse_count_sync(self):
        """Test clear_pulse_count_sync."""
        # TODO: implement test!
        pass

    def test_UART_write(self):
        """Test UART_write."""
        # TODO: implement test!
        pass

    def test_UART_read(self):
        """Test UART_read."""
        # TODO: implement test!
        pass

    def test_curve(self):
        """Test curve."""
        # TODO: implement test!
        pass

    def test_read_curve_pointer(self):
        """Test read_curve_pointer."""
        # TODO: implement test!
        pass

    def test_set_curve_pointer(self):
        """Test set_curve_pointer."""
        # TODO: implement test!
        pass

    def test_set_curve_block(self):
        """Test set_curve_block."""
        # TODO: implement test!
        pass

    def test_read_curve_block(self):
        """Test read_curve_block."""
        # TODO: implement test!
        pass

    def test_close(self):
        """Test close."""
        # TODO: implement test!
        pass

    def test_emulate_trigger(self):
        """Test emulate_trigger."""
        # TODO: implement test!
        pass


if __name__ == "__main__":
    unittest.main()
