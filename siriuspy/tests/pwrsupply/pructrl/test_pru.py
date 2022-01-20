#!/usr/bin/env python-sirius

"""Test PRU module."""
from unittest import TestCase

from siriuspy import util
from siriuspy.pwrsupply.pructrl import pru
from siriuspy.pwrsupply.pructrl.pru import PRUInterface
from siriuspy.pwrsupply.pructrl.pru import PRU


PUB_INTERFACE = (
    'PRUInterface',
    'PRU',
)


class TestModule(TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(pru, PUB_INTERFACE)
        self.assertTrue(valid)


class TestPRUInterface(TestCase):
    """Test PRUInterface API."""

    PUB_INTERFACE = (
        'open',
        'close',
        'UART_write',
        'UART_read',
        'UART_request',
        'wr_duration',
        'wr_duration_reset',
    )

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(util.check_public_interface_namespace(
            PRUInterface, TestPRUInterface.PUB_INTERFACE))

    def test_simulated(self):
        """Test simulated."""
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

    def test_close(self):
        """Test close."""
        # TODO: implement test!
        pass


class TestPRU(TestCase):
    """Test PRU API."""

    PUB_INTERFACE = (
        'bbbname',
        'ip_address',
    )

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(util.check_public_interface_namespace(
            PRU, TestPRU.PUB_INTERFACE))

    def test_bbbname(self):
        """Test bbbname."""
        # TODO: implement test!
        pass

    def test_ip_address(self):
        """Test bbbname."""
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

    def test_close(self):
        """Test close."""
        # TODO: implement test!
        pass
