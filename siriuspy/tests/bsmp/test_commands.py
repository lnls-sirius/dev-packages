"""Test BSMP Commands."""
import unittest
from unittest.mock import Mock
import struct

from siriuspy.bsmp import Package, Message, Types, Variable, VariablesGroup, \
    Function, BSMP
from siriuspy.util import check_public_interface_namespace


class TestBSMPAPI(unittest.TestCase):
    """Test BSMP."""

    api = (
        'entities', 'channel',
        'consult_protocol_version',
        'consult_variables_list',
        'consult_groups_list',
        'consult_group_variables',
        'consult_curves_list',
        'consult_curve_checksum',
        'consult_functions_list',
        'read_variable',
        'read_group_variables',
        'write_variable',
        'write_group_variables',
        'binop_variable',
        'binop_group_variables',
        'write_read_variable',
        'create_group',
        'remove_all_groups',
        'read_curve_block',
        'write_curve_block',
        'calc_curve_checksum',
        'execute_function',
    )

    def test_api(self):
        """Test API."""
        self.assertTrue(check_public_interface_namespace(BSMP, self.api))


class TestBSMP0x0(unittest.TestCase):
    """Test BSMP consulting methods."""

    def setUp(self):
        """Common setup for all tests."""
        self.serial = Mock()
        self.entities = None
        self.bsmp = BSMP(self.serial, 1, self.entities)

    def test_consult_protocol_version(self):
        """Test consult_protocol_version."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.consult_protocol_version()

    def test_consult_variables_list(self):
        """Test consult_variables_list."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.consult_variables_list()

    def test_consult_groups_list(self):
        """Test consult_groups_list."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.consult_groups_list()

    def test_consult_group_variables(self):
        """Test consult_group_variables."""
        p = Package.package(
            0, Message.message(0x07, load=[chr(0), chr(1), chr(2), chr(3)]))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.consult_group_variables(1)

        self.assertEqual(response, (0xE0, [0, 1, 2, 3]))

    def test_consult_group_variables_error(self):
        """Test consult_group_variables return error code."""
        p = Package.package(0, Message.message(0xE3))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.consult_group_variables(1)
        self.assertEqual(response, (0xE3, None))

    def test_consult_group_variables_fail(self):
        """Test consult_group_variables return None when cmd is unexpected."""
        p = Package.package(0, Message.message(0xE9))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.consult_group_variables(1)
        self.assertEqual(response, (None, None))

    def test_consult_curves_list(self):
        """Test consult_curves_list."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.consult_curves_list()

    def test_consult_curve_checksum(self):
        """Test consult_curve_checksum."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.consult_curve_checksum(1)

    def test_consult_functions_list(self):
        """Test consult_functions_list."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.consult_functions_list()


class TestBSMP0x1(unittest.TestCase):
    """Test BSMP read methods."""

    def setUp(self):
        """Common setup for all tests."""
        self.serial = Mock()
        self.entities = Mock()
        self.entities.variables = [
            Variable(0, False, Types.t_uint16, 1),
            Variable(1, False, Types.t_float, 1),
            Variable(2, False, Types.t_float, 2),
            Variable(3, False, Types.t_char, 64)]
        self.entities.groups = [
            VariablesGroup(0, False, self.entities.variables),
        ]
        self.bsmp = BSMP(self.serial, 1, self.entities)

    def test_read_int2_variable(self):
        """Test read_variable."""
        load = list(map(chr, struct.pack('<h', 1020)))
        p = Package.package(0, Message.message(0x11, load=load))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.read_variable(0)
        self.assertEqual(response, (0xE0, 1020))

    def test_read_float_variable(self):
        """Test read_variable."""
        load = list(map(chr, struct.pack('<f', 50.52)))
        p = Package.package(0, Message.message(0x11, load=load))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.read_variable(1)
        self.assertEqual(response[0], 0xE0)
        self.assertAlmostEqual(response[1], 50.52, places=2)

    def test_read_arrfloat_variable(self):
        """Test read_variable."""
        values = [1.1234567, 2.7654321]
        load = list(map(chr, struct.pack('<f', 1.1234567)))
        load.extend(list(map(chr, struct.pack('<f', 2.7654321))))
        p = Package.package(0, Message.message(0x11, load=load))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.read_variable(2)
        self.assertEqual(response[0], 0xE0)
        for i, value in enumerate(response[1]):
            self.assertAlmostEqual(value, values[i], places=7)

    def test_read_string_variable(self):
        """Test read_variable."""
        load = ['t', 'e', 's', 't', 'e']
        while len(load) < 64:
            load.append(chr(0))
        p = Package.package(0, Message.message(0x11, load=load))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.read_variable(3)
        self.assertEqual(response, (0xE0, 'teste'))

    def test_read_variable_error(self):
        """Test read variable returns error code."""
        p = Package.package(0, Message.message(0xE3))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.read_variable(1)
        self.assertEqual(response, (0xE3, None))

    def test_read_variable_failure(self):
        """Test read variable returns error code."""
        p = Package.package(0, Message.message(0xFF))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.read_variable(1)
        self.assertEqual(response, (None, None))

    def test_read_group_variables(self):
        """Test read_group_variables."""
        values = [1020, 40.7654321, [1.7654321, 0.0123456], 'teste']
        load = list(map(chr, struct.pack('<h', 1020)))
        load.extend(list(map(chr, struct.pack('<f', 40.7654321))))
        load.extend(list(map(chr, struct.pack('<f', 1.7654321))))
        load.extend(list(map(chr, struct.pack('<f', 0.0123456))))
        load.extend(['t', 'e', 's', 't', 'e'])
        for i in range(64 - len(values[3])):
            load.append(chr(0))
        p = Package.package(0, Message.message(0x13, load=load))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.read_group_variables(0)
        self.assertEqual(response[0], 0xE0)
        self.assertEqual(response[1][0], values[0])
        self.assertAlmostEqual(response[1][1], values[1], places=5)
        self.assertAlmostEqual(response[1][2][0], values[2][0])
        self.assertAlmostEqual(response[1][2][1], values[2][1])
        self.assertEqual(response[1][3], values[3])

    def test_read_group_variable_error(self):
        """Test read variable returns error code."""
        p = Package.package(0, Message.message(0xE3))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.read_group_variables(0)
        self.assertEqual(response, (0xE3, None))

    def test_read_group_variable_fail(self):
        """Test read variable returns error code."""
        p = Package.package(0, Message.message(0xFF))
        self.serial.UART_read.return_value = p.stream
        response = self.bsmp.read_group_variables(0)
        self.assertEqual(response, (None, None))


class TestBSMP0x2(unittest.TestCase):
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

    def test_write_group_variables(self):
        """Test write_group_variables."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.write_group_variables(2, [2, 3, 5.0])

    def test_binop_variable(self):
        """Test binop_variable."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.binop_variable(0, 'and', 0xFF)

    def test_binop_group_variables(self):
        """Test binop_group_variables."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.binop_group_variables(2, 'and', [0xFF, 0xFF])

    def test_write_read_variable(self):
        """Test write_read_variable."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.write_read_variable(0, 1, 10)


class TestBSMP0x3(unittest.TestCase):
    """Test BSMP group management methods."""

    def setUp(self):
        """Common setup for all tests."""
        self.serial = Mock()
        self.entities = Mock()
        self.entities.variables = None
        self.bsmp = BSMP(self.serial, 1, self.entities)

    def test_create_group(self):
        """Test create group."""
        resp_p = Package.package(0, Message.message(0xE0))
        send_p = Package.package(1, Message.message(0x30, [chr(1), chr(3)]))
        self.serial.UART_read.return_value = resp_p.stream

        response = self.bsmp.create_group([1, 3])

        self.serial.UART_write.assert_called_once_with(
            send_p.stream, timeout=100)
        self.assertEqual(response, (0xE0, None))

    def test_create_group_error(self):
        """Test create_group."""
        resp_p = Package.package(0, Message.message(0xE8))
        self.serial.UART_read.return_value = resp_p.stream
        response = self.bsmp.create_group([1, 3])
        self.assertEqual(response, (0xE8, None))

    def test_create_group_fail(self):
        """Test create_group."""
        resp_p = Package.package(0, Message.message(0xFF))
        self.serial.UART_read.return_value = resp_p.stream
        response = self.bsmp.create_group([1, 3])
        self.assertEqual(response, (None, None))

    def test_remove_all_groups(self):
        """Test remove_all_groups."""
        resp_p = Package.package(0, Message.message(0xE0))
        send_p = Package.package(1, Message.message(0x32))
        self.serial.UART_read.return_value = resp_p.stream

        response = self.bsmp.remove_all_groups()

        self.serial.UART_write.assert_called_once_with(
            send_p.stream, timeout=100)
        self.assertEqual(response, (0xE0, None))

    def test_remove_all_groups_error(self):
        """Test remove_all_groups."""
        resp_p = Package.package(0, Message.message(0xE8))
        self.serial.UART_read.return_value = resp_p.stream
        response = self.bsmp.remove_all_groups()
        self.assertEqual(response, (0xE8, None))

    def test_remove_all_groups_fail(self):
        """Test remove_all_groups."""
        resp_p = Package.package(0, Message.message(0x11))
        self.serial.UART_read.return_value = resp_p.stream
        response = self.bsmp.remove_all_groups()
        self.assertEqual(response, (None, None))


class TestBSMP0x4(unittest.TestCase):
    """Test BSMP curve methods."""

    def setUp(self):
        """Common setup for all tests."""
        self.serial = Mock()
        self.entities = Mock()
        self.entities.variables = None
        self.bsmp = BSMP(self.serial, 1, self.entities)

    def test_read_curve_block(self):
        """Test read_curve_block."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.read_curve_block(1, 1)

    def test_write_curve_block(self):
        """Test write_curve_block."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.write_curve_block(1, 2, [])

    def test_calc_curve_checksum(self):
        """Test calc_curve_checksum."""
        with self.assertRaises(NotImplementedError):
            self.bsmp.calc_curve_checksum(1)


class TestBSMP0x5(unittest.TestCase):
    """Test BSMP function methods."""

    def setUp(self):
        """Common setup for all tests."""
        self.serial = Mock()
        self.entities = Mock()
        self.entities.functions = [
            Function(0, 1, Types.t_float, 1, Types.t_uint8),
        ]
        self.bsmp = BSMP(self.serial, 1, self.entities)

    def test_execute_function(self):
        """Test execute_function."""
        resp_p = Package.package(0, Message.message(0x51, load=[chr(0)]))
        send_load = [chr(0x00)] + list(map(chr, struct.pack('<f', 1.5)))
        send_p = Package.package(1, Message.message(0x50, load=send_load))
        self.serial.UART_read.return_value = resp_p.stream

        response = self.bsmp.execute_function(0, 1.5)
        self.serial.UART_write.assert_called_once_with(
            send_p.stream, timeout=100)
        self.assertEqual(response, (0xE0, 0))


if __name__ == '__main__':
    unittest.main()
