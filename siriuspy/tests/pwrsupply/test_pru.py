#!/usr/bin/env python-sirius

"""Test PRU module."""
from unittest import TestCase

from siriuspy import util
from siriuspy.pwrsupply import pru
from siriuspy.pwrsupply.pru import PRUInterface
from siriuspy.pwrsupply.pru import PRU
from siriuspy.pwrsupply.pru import PRUSim


public_interface = (
    'PRUInterface',
    'PRU',
    'PRUSim',
)


class TestModule(TestCase):
    """Test module interface."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(
                pru,
                public_interface)
        self.assertTrue(valid)


class TestPRUInterface(TestCase):
    """Test PRUInterface API."""

    public_interface = (
        'OK',
        'simulated',
        'UART_write',
        'UART_read',
        'close',
        'wr_duration',
        'wr_duration_reset',
    )

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(util.check_public_interface_namespace(
            PRUInterface, TestPRUInterface.public_interface))

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

    public_interface = ()

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(util.check_public_interface_namespace(
            PRU, TestPRU.public_interface))

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


class TestPRUSim(TestCase):
    """Test PRUSim API."""

    public_interface = (
        'timing_trigger_callback',
        'add_callback',
        'issue_callbacks',
        'TIMING_PV'
    )

    def test_public_interface(self):
        """Test class public interface."""
        self.assertTrue(util.check_public_interface_namespace(
            PRUSim, TestPRUSim.public_interface))

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

    def test_emulate_trigger(self):
        """Test emulate_trigger."""
        # TODO: implement test!
        pass
