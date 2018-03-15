#!/usr/bin/env python-sirius
"""Test PRU module."""
import unittest
from unittest import mock

from siriuspy.pwrsupply.pru import _PRUInterface, PRUSim, PRU, SerialComm
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
            _PRUInterface, TestPRUInterface.api))


class TestPRUSim(unittest.TestCase):
    """Test PRUSim."""

    api = (
        'process_sync_signal',
    )

    def setUp(self):
        """Common setup for all tests."""
        self.pru = PRUSim()

    def test_api(self):
        """Test API."""
        self.assertTrue(check_public_interface_namespace(
            PRUSim, TestPRUSim.api))

    def test_init(self):
        """Test inital params values."""
        self.assertFalse(self.pru.sync_mode)
        self.assertEqual(self.pru.sync_pulse_count, 0)

    def test_sync_mode(self):
        """Test setting sync mode."""
        self.sync_mode = True
        self.assertTrue(self.sync_mode)
        self.sync_mode = False
        self.assertFalse(self.sync_mode)

    def test_process_sync_signal(self):
        """Test simulated sync signal."""
        self.pru.process_sync_signal()
        self.assertEqual(self.pru.sync_pulse_count, 1)
        self.pru.process_sync_signal()
        self.assertEqual(self.pru.sync_pulse_count, 2)

    def test_uart_write(self):
        """Test uart write."""
        with self.assertRaises(NotImplementedError):
            self.pru.UART_write(['\x00'], 1.0)

    def test_uart_read(self):
        """Test uart write."""
        with self.assertRaises(NotImplementedError):
            self.pru.UART_read()

    def test_curve(self):
        """Test curve."""
        pass


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


class TestSerialComm(unittest.TestCase):
    """Test SerialComm."""

    def setUp(self):
        """Common setup for all tests."""
        thread_patcher = mock.patch('siriuspy.pwrsupply.pru._Thread')
        self.addCleanup(thread_patcher.stop)
        self.thread_mock = thread_patcher.start()
        pru_patcher = mock.patch('siriuspy.pwrsupply.pru.PRU')
        self.addCleanup(pru_patcher.stop)
        self.pru_mock = pru_patcher.start()
        self.pru_mock.return_value.sync_pulse_count = 10
        self.pru_mock.return_value.UART_read.return_value = ['\x00']
        # pru.sync_mode = mock.PropertyMock(return_value=True)
        slaves = list()
        # for i in range(3):
        #     mock_obj = mock.Mock()
        #     slaves.append(mock_obj)
        slaves = list()
        for i in range(3):
            mock_obj = mock.Mock()
            id_device = mock.PropertyMock(return_value=i+1)
            type(mock_obj).ID_device = id_device
            slaves.append(mock_obj)
        self.serial_comm = SerialComm(simulate=False, slaves=slaves)

    def test_sync_mode(self):
        """Test sync mode."""
        self.serial_comm.sync_mode = True
        self.assertTrue(self.serial_comm.sync_mode)
        self.serial_comm.sync_mode = False
        self.assertFalse(self.serial_comm.sync_mode)

    def test_sync_pulse_count(self):
        """Test sync pulse count."""
        self.assertEqual(self.serial_comm.sync_pulse_count, 10)

    def test_set_scanning(self):
        """Test scanning property."""
        self.assertEqual(self.serial_comm.scanning, False)
        self.serial_comm.scanning = True
        self.assertEqual(self.serial_comm.scanning, True)

    def test_write(self):
        """Test write."""
        self.assertEqual(self.serial_comm.write(['\x00'], 1.0), ['\x00'])

    def test_add_slave(self):
        """Test add slave."""
        pass

    def test_put(self):
        """Test put."""
        pass


if __name__ == "__main__":
    unittest.main()
