#!/usr/bin/env python-sirius
"""Test PRU module."""
import unittest
from unittest import mock

from siriuspy.pwrsupply.pru import PRUInterface, PRU
from siriuspy.util import check_public_interface_namespace


class TestPRUInterface(unittest.TestCase):
    """Test PRUInterface API."""

    api = (
        'sync_mode',
        'sync_pulse_count',
        'UART_write',
        'UART_read',
        'curve',
    )

    def test_api(self):
        """Test API."""
        self.assertTrue(check_public_interface_namespace(
            PRUInterface, TestPRUInterface.api))


class TestPRU(unittest.TestCase):
    """Test PRU."""

    def setUp(self):
        """Common setup."""
        serial_patcher = mock.patch('siriuspy.pwrsupply.pru._PRUserial485')
        self.addCleanup(serial_patcher.stop)
        self.serial_mock = serial_patcher.start()
        self.pru = PRU()

        self.serial_mock.PRUserial485_read.return_value = ['\x00', '\x01']

    def test_init(self):
        """Test initial param values."""
        self.serial_mock.PRUserial485_open.assert_called_with(6, b"M")

    def test_sync_mode(self):
        """Test setting sync mode."""
        self.pru.sync_mode = True
        self.serial_mock.PRUserial485_sync_start.assert_called_with(1, 100)
        self.pru.sync_mode = False
        self.serial_mock.PRUserial485_sync_stop.assert_called_once()

    def test_uart_write(self):
        """Test UART write."""
        self.pru.UART_write(['\x00'], 1.0)
        self.serial_mock.PRUserial485_write.assert_called_with(['\x00'], 1.0)

    def test_uart_read(self):
        """Test UART write."""
        stream = self.pru.UART_read()
        self.serial_mock.PRUserial485_read.assert_called_once()
        self.assertEqual(stream, ['\x00', '\x01'])

    def test_curve(self):
        """Test curve."""
        self.pru.curve('curve1', 'curve2', 'curve3', 'curve4')
        self.serial_mock.PRUserial485_curve.assert_called_with(
            'curve1', 'curve2', 'curve3', 'curve4')


if __name__ == "__main__":
    unittest.main()
