#!/usr/bin/env python-sirius
"""Test beaglebone module."""
import unittest

from siriuspy import util
from siriuspy.pwrsupply import pru
import siriuspy.pwrsupply.beaglebone as bbb
from siriuspy.util import check_public_interface_namespace


public_interface = (
    'BeagleBone',
)


class TestModule(unittest.TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                bbb,
                public_interface)
        self.assertTrue(valid)


class TestBeagleBone(unittest.TestCase):
    """Test PRUInterface API."""

    public_interface = (
        'psnames',
        'power_supplies',
        'controller',
        'pru',
        'write',
    )

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(check_public_interface_namespace(
            bbb.BeagleBone, TestBeagleBone.public_interface))

    def test_psnames(self):
        """Test psnames."""
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
        """Test curve        ."""
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
