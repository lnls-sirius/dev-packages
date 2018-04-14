#!/usr/bin/env python-sirius
"""Test PRU module."""
import unittest
from unittest import mock


from siriuspy import util
from siriuspy.pwrsupply import pru
from siriuspy.pwrsupply.pru import PRUInterface
from siriuspy.util import check_public_interface_namespace


public_interface = (
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


class TestPRUInterface(unittest.TestCase):
    """Test PRUInterface API."""

    public_interface = (
        'VERSION',
        'SYNC_MIGINT',
        'SYNC_MIGEND',
        'SYNC_RMPINT',
        'SYNC_RMPEND',
        'SYNC_CYCLE',
        'SYNC_MODES',
        'sync_mode',
        'sync_status',
        'sync_start',
        'sync_stop',
        'sync_pulse_count',
        'UART_write',
        'UART_read',
        'curve',
        'set_curve_block',
        'read_curve_block',
        'close',
    )

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(check_public_interface_namespace(
            PRUInterface, TestPRUInterface.public_interface))

    def test_VERSION(self):
        """Test VERSION."""
        self.assertIsInstance(PRUInterface.VERSION, str)

    def test_SYNC_MIGINT(self):
        """Test SYNC_MIGINT."""
        self.assertIsInstance(PRUInterface.SYNC_MIGINT, int)

    def test_SYNC_MIGEND(self):
        """Test SYNC_MIGEND."""
        self.assertIsInstance(PRUInterface.SYNC_MIGEND, int)

    def test_SYNC_RMPINT(self):
        """Test SYNC_RMPINT."""
        self.assertIsInstance(PRUInterface.SYNC_RMPINT, int)

    def test_SYNC_RMPEND(self):
        """Test SYNC_RMPEND."""
        self.assertIsInstance(PRUInterface.SYNC_RMPEND, int)

    def test_SYNC_CYCLE(self):
        """Test SYNC_CYCLE."""
        self.assertIsInstance(PRUInterface.SYNC_CYCLE, int)

    def test_SYNC_MODES(self):
        """Test SYNC_MODES."""
        self.assertIsInstance(PRUInterface.SYNC_MODES, tuple)
        for mode in PRUInterface.SYNC_MODES:
            self.assertIsInstance(mode, int)

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

    def test_sync_pulse_count(self):
        """Test sync_pulse_count."""
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


# class TestPRU(unittest.TestCase):
#     """Test PRU."""
#
#     def setUp(self):
#         """Common setup."""
#         serial_patcher = mock.patch('siriuspy.pwrsupply.pru._PRUserial485')
#         self.addCleanup(serial_patcher.stop)
#         self.serial_mock = serial_patcher.start()
#         self.pru = PRU()
#
#         self.serial_mock.PRUserial485_read.return_value = ['\x00', '\x01']
#
#     def test_init(self):
#         """Test initial param values."""
#         self.serial_mock.PRUserial485_open.assert_called_with(6, b"M")
#
#     def test_sync_mode(self):
#         """Test setting sync mode."""
#         self.pru.sync_mode = True
#         self.serial_mock.PRUserial485_sync_start.assert_called_with(1, 100)
#         self.pru.sync_mode = False
#         self.serial_mock.PRUserial485_sync_stop.assert_called_once()
#
#     def test_uart_write(self):
#         """Test UART write."""
#         self.pru.UART_write(['\x00'], 1.0)
#         self.serial_mock.PRUserial485_write.assert_called_with(['\x00'], 1.0)
#
#     def test_uart_read(self):
#         """Test UART write."""
#         stream = self.pru.UART_read()
#         self.serial_mock.PRUserial485_read.assert_called_once()
#         self.assertEqual(stream, ['\x00', '\x01'])
#
#     def test_curve(self):
#         """Test curve."""
#         self.pru.curve('curve1', 'curve2', 'curve3', 'curve4')
#         self.serial_mock.PRUserial485_curve.assert_called_with(
#             'curve1', 'curve2', 'curve3', 'curve4')
#

if __name__ == "__main__":
    unittest.main()
