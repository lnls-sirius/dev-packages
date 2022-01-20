#!/usr/bin/env python-sirius

"""Test commands module."""

import struct
from unittest import TestCase
from unittest.mock import Mock

from siriuspy.bsmp import (
    BSMP,
    Function,
    Message,
    Package,
    SerialAnomResp,
    Types,
    Variable,
    VariablesGroup,
)
from siriuspy.util import check_public_interface_namespace


class TestBSMPAPI(TestCase):
    """Test BSMP."""

    api = (
        'entities',
        'channel',
        'query_protocol_version',
        'query_list_of_variables',
        'query_list_of_group_of_variables',
        'query_group_of_variables',
        'query_list_of_curves',
        'query_curve_checksum',
        'query_list_of_functions',
        'read_variable',
        'read_group_of_variables',
        'write_variable',
        'write_group_of_variables',
        'binoperation_variable',
        'binoperation_group',
        'write_and_read_variable',
        'create_group_of_variables',
        'remove_all_groups_of_variables',
        'request_curve_block',
        'curve_block',
        'recalculate_curve_checksum',
        'execute_function',
        'anomalous_response',
    )

    def test_api(self):
        """Test API."""
        self.assertTrue(check_public_interface_namespace(BSMP, self.api))


class TestBSMP0x0(TestCase):
    """Test BSMP consulting methods."""

    def setUp(self):
        """Common setup for all tests."""
        self.serial = Mock()
        # self.serial.len.return_value = 30
        self.entities = None
        self.bsmp = BSMP(self.serial, 1, self.entities)

    def test_query_protocol_version(self):
        """Test query_protocol_version."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.query_protocol_version()

    def test_query_list_of_variables(self):
        """Test query_list_of_variables."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.query_list_of_variables()

    # def test_query_list_of_group_of_variables(self):
    #     """Test query_list_of_group_of_variables."""
    #     self.bsmp.query_list_of_group_of_variables(timeout=100)

    def test_query_group_of_variables(self):
        """Test query_group_of_variables."""
        p = Package.package(
            0, Message.message(0x07, payload=[chr(0), chr(1), chr(2), chr(3)])
        )
        self.serial.UART_request.return_value = p.stream
        response = self.bsmp.query_group_of_variables(1, timeout=100)
        self.assertEqual(response, (0xE0, [0, 1, 2, 3]))

    def _test_query_group_of_variables_error(self):
        """Test query_group_of_variables return error code."""
        p = Package.package(0, Message.message(0xE3))
        self.serial.UART_read.return_value = p.stream
        with self.assertRaises(TypeError):
            self.bsmp.query_group_of_variables(1)
        response = self.bsmp.query_group_of_variables(1, timeout=100)
        self.assertEqual(response, (0xE3, None))

    def test_query_group_of_variables_fail(self):
        """Test query_group_of_variables return None when cmd is unexpected."""
        p = Package.package(0, Message.message(0xE9))
        self.serial.UART_request.return_value = p.stream
        # with self.assertRaises(TypeError):
        with self.assertRaises(SerialAnomResp):
            self.bsmp.query_group_of_variables(1, timeout=100)

    def test_query_list_of_curves(self):
        """Test query_list_of_curves."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.query_list_of_curves()

    def test_query_curve_checksum(self):
        """Test query_curve_checksum."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.query_curve_checksum(1)

    def test_query_list_of_functions(self):
        """Test query_list_of_functions."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.query_list_of_functions()


class TestBSMP0x1(TestCase):
    """Test BSMP read methods."""

    def setUp(self):
        """Set commons for all tests."""
        self.serial = Mock()
        self.entities = Mock()
        self.entities.variables = [
            Variable(0, False, Types.T_UINT16, 1),
            Variable(1, False, Types.T_FLOAT, 1),
            Variable(2, False, Types.T_FLOAT, 2),
            Variable(3, False, Types.T_CHAR, 64),
        ]
        self.entities.groups = [
            VariablesGroup(0, False, self.entities.variables),
        ]
        self.bsmp = BSMP(self.serial, 1, self.entities)

    def test_read_int2_variable(self):
        """Test read_variable."""
        load = list(map(chr, struct.pack('<h', 1020)))
        pck = Package.package(0, Message.message(0x11, payload=load))
        self.serial.UART_request.return_value = pck.stream
        response = self.bsmp.read_variable(0, 100)
        self.assertEqual(response, (0xE0, 1020))

    def test_read_float_variable(self):
        """Test read_variable."""
        load = list(map(chr, struct.pack('<f', 50.52)))
        pck = Package.package(0, Message.message(0x11, payload=load))
        self.serial.UART_request.return_value = pck.stream
        response = self.bsmp.read_variable(1, 100)
        self.assertEqual(response[0], 0xE0)
        self.assertAlmostEqual(response[1], 50.52, places=2)

    def test_read_arrfloat_variable(self):
        """Test read_variable."""
        values = [1.1234567, 2.7654321]
        load = list(map(chr, struct.pack('<f', 1.1234567)))
        load.extend(list(map(chr, struct.pack('<f', 2.7654321))))
        pck = Package.package(0, Message.message(0x11, payload=load))
        self.serial.UART_request.return_value = pck.stream
        response = self.bsmp.read_variable(2, 100)
        self.assertEqual(response[0], 0xE0)
        for i, value in enumerate(response[1]):
            self.assertAlmostEqual(value, values[i], places=7)

    def test_read_string_variable(self):
        """Test read_variable."""
        load = ['t', 'e', 's', 't', 'e']
        while len(load) < 64:
            load.append(chr(0))
        expected_value = [c.encode() for c in load]
        pck = Package.package(0, Message.message(0x11, payload=load))
        self.serial.UART_request.return_value = pck.stream
        response = self.bsmp.read_variable(3, 100)
        self.assertEqual(response, (0xE0, expected_value))

    def test_read_variable_error(self):
        """Test read variable returns error code."""
        pck = Package.package(0, Message.message(0xE3))
        self.serial.UART_request.return_value = pck.stream
        response = self.bsmp.read_variable(1, 100)
        self.assertEqual(response, (0xE3, None))

    def test_read_variable_failure(self):
        """Test read variable returns error code."""
        pck = Package.package(0, Message.message(0xFF))
        self.serial.UART_request.return_value = pck.stream
        with self.assertRaises(SerialAnomResp):
            self.bsmp.read_variable(1, 100)

    def test_read_group_of_variables(self):
        """Test read_group_of_variables."""
        ld_string = ['t', 'e', 's', 't', 'e']
        for _ in range(64 - len(ld_string)):
            ld_string.append(chr(0))
        val_string = [c.encode() for c in ld_string]
        values = [1020, 40.7654321, [1.7654321, 0.0123456], val_string]
        load = list(map(chr, struct.pack('<h', 1020)))
        load.extend(list(map(chr, struct.pack('<f', 40.7654321))))
        load.extend(list(map(chr, struct.pack('<f', 1.7654321))))
        load.extend(list(map(chr, struct.pack('<f', 0.0123456))))
        load.extend(ld_string)
        pck = Package.package(0, Message.message(0x13, payload=load))
        self.serial.UART_request.return_value = pck.stream
        response = self.bsmp.read_group_of_variables(0, timeout=100)
        self.assertEqual(response[0], 0xE0)
        self.assertEqual(response[1][0], values[0])
        self.assertAlmostEqual(response[1][1], values[1], places=5)
        self.assertAlmostEqual(response[1][2][0], values[2][0])
        self.assertAlmostEqual(response[1][2][1], values[2][1])
        self.assertEqual(response[1][3], values[3])

    def test_read_group_variable_error(self):
        """Test read variable returns error code."""
        p = Package.package(0, Message.message(0xE3))
        self.serial.UART_request.return_value = p.stream
        response = self.bsmp.read_group_of_variables(0, timeout=100)
        self.assertEqual(response, (0xE3, None))

    def test_read_group_variable_fail(self):
        """Test read variable returns error code."""
        pck = Package.package(0, Message.message(0xFF))
        self.serial.UART_request.return_value = pck.stream
        with self.assertRaises(TypeError):
            # forget pylint: not having required timeout arg is the test
            self.bsmp.query_group_of_variables(1)
        with self.assertRaises(SerialAnomResp):
            self.bsmp.read_group_of_variables(0, timeout=100)


class TestBSMP0x2(TestCase):
    """Test BSMP write methods."""

    def setUp(self):
        """Common setup for all tests."""
        self.serial = Mock()
        self.entities = Mock()
        self.entities.variables = None
        self.bsmp = BSMP(self.serial, 1, self.entities)

    def test_write_variable(self):
        """Test write_variable."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.write_variable(1, 1.5)

    def test_write_group_of_variables(self):
        """Test write_group_of_variables."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.write_group_of_variables(2, [2, 3, 5.0])

    def test_binoperation_variable(self):
        """Test binoperation_variable."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.binoperation_variable(0, 'and', 0xFF)

    def test_binoperation_group(self):
        """Test binoperation_group."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.binoperation_group(2, 'and', [0xFF, 0xFF])

    def test_write_and_read_variable(self):
        """Test write_and_read_variable."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.write_and_read_variable(0, 1, 10)


class TestBSMP0x3(TestCase):
    """Test BSMP group management methods."""

    def setUp(self):
        """Set commons for all tests."""
        self.serial = Mock()
        self.entities = Mock()
        self.entities.variables = None
        self.bsmp = BSMP(self.serial, 1, self.entities)

    def test_create_group_of_variables(self):
        """Test create group."""
        resp_p = Package.package(0, Message.message(0xE0))
        send_p = Package.package(1, Message.message(0x30, [chr(1), chr(3)]))
        self.serial.UART_request.return_value = resp_p.stream

        response = self.bsmp.create_group_of_variables([1, 3], timeout=100)

        self.serial.UART_request.assert_called_once_with(send_p.stream, timeout=100)
        self.assertEqual(response, (0xE0, None))

    def test_create_group_of_variables_error(self):
        """Test create_group_of_variables."""
        resp_p = Package.package(0, Message.message(0xE8))
        self.serial.UART_request.return_value = resp_p.stream
        with self.assertRaises(TypeError):
            self.bsmp.query_group_of_variables(1)
        response = self.bsmp.create_group_of_variables([1, 3], timeout=100)
        self.assertEqual(response, (0xE8, None))

    def test_create_group_of_variables_fail(self):
        """Test create_group_of_variables."""
        resp_p = Package.package(0, Message.message(0xFF))
        self.serial.UART_request.return_value = resp_p.stream
        with self.assertRaises(SerialAnomResp):
            self.bsmp.create_group_of_variables([1, 3], timeout=100)

    def test_remove_all_groups_of_variables(self):
        """Test remove_all_groups_of_variables."""
        resp_p = Package.package(0, Message.message(0xE0))
        send_p = Package.package(1, Message.message(0x32))
        self.serial.UART_request.return_value = resp_p.stream

        response = self.bsmp.remove_all_groups_of_variables(timeout=100)

        self.serial.UART_request.assert_called_once_with(send_p.stream, timeout=100)
        self.assertEqual(response, (0xE0, None))

    def test_remove_all_groups_of_variables_error(self):
        """Test remove_all_groups_of_variables."""
        resp_p = Package.package(0, Message.message(0xE8))
        self.serial.UART_request.return_value = resp_p.stream
        with self.assertRaises(TypeError):
            self.bsmp.remove_all_groups_of_variables()
        response = self.bsmp.remove_all_groups_of_variables(timeout=100)
        self.assertEqual(response, (0xE8, None))

    def test_remove_all_groups_of_variables_fail(self):
        """Test remove_all_groups_of_variables."""
        resp_p = Package.package(0, Message.message(0x11))
        self.serial.UART_request.return_value = resp_p.stream
        with self.assertRaises(SerialAnomResp):
            self.bsmp.remove_all_groups_of_variables(timeout=100)


class TestBSMP0x4(TestCase):
    """Test BSMP curve methods."""

    def setUp(self):
        """Set commons for all tests."""
        self.serial = Mock()
        self.entities = Mock()
        self.entities.variables = None
        self.bsmp = BSMP(self.serial, 1, self.entities)

    # def test_request_curve_block(self):
    #     """Test request_curve_block."""
    #     with self.assertRaises(NotImplementedError):
    #         self.bsmp.request_curve_block(1, 1, 100)

    # def test_curve_block(self):
    #     """Test curve_block."""
    #     with self.assertRaises(NotImplementedError):
    #         self.bsmp.curve_block(1, 2, [], timeout=100)

    # def test_recalculate_curve_checksum(self):
    #     """Test recalculate_curve_checksum."""
    #     with self.assertRaises(NotImplementedError):
    #         self.bsmp.recalculate_curve_checksum(1)


class TestBSMP0x5(TestCase):
    """Test BSMP function methods."""

    def setUp(self):
        """Set commons for all tests."""
        self.serial = Mock()
        self.entities = Mock()
        self.entities.functions = [
            Function(0, [Types.T_FLOAT], [Types.T_UINT8]),
        ]
        self.bsmp = BSMP(self.serial, 1, self.entities)

    def test_execute_function(self):
        """Test execute_function."""
        resp_p = Package.package(0, Message.message(0x51, payload=[chr(0)]))
        send_load = [chr(0x00)] + list(map(chr, struct.pack('<f', 1.5)))
        send_p = Package.package(1, Message.message(0x50, payload=send_load))
        self.serial.UART_request.return_value = resp_p.stream

        response = self.bsmp.execute_function(0, 1.5)
        self.serial.UART_request.assert_called_once_with(send_p.stream, timeout=100)
        self.assertEqual(response, (0xE0, 0))
