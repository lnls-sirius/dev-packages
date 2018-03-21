#!/usr/bin/env python-sirius
"""BSMP class tests."""
import struct
import unittest
from unittest.mock import Mock

from siriuspy.bsmp import Message, Package, Channel, Variable
from siriuspy.util import check_public_interface_namespace


class TestBSMPMessage(unittest.TestCase):
    """Test BSMP Message class."""

    api = (
        'init_stream',
        'cmd',
        'load',
        'to_stream',
    )

    def test_api(self):
        """Test API."""
        self.assertTrue(check_public_interface_namespace(Message, self.api))

    def test_init_with_no_load(self):
        """Test constructor with no load."""
        m = Message(cmd=0x00)
        self.assertEqual(m.cmd, 0x00)
        self.assertIsNone(m.load)

    def test_init_with_load(self):
        """Test constructor with load."""
        m = Message(cmd=0x10, load=[1, ])
        self.assertEqual(m.cmd, 0x10)
        self.assertEqual(m.load, [1, ])

    def test_init_with_extraneous_load(self):
        """Test constructor with loads that are not list."""
        loads = [1, 'string', (1, 2, 3), 63.7]
        for load in loads:
            with self.assertRaises(TypeError):
                Message(cmd=0x10, load=load)

    def test_init_with_big_load(self):
        """Test constructor with load bigger than 65535."""
        load = [0 for _ in range(65536)]
        with self.assertRaises(ValueError):
            Message(cmd=0x10, load=load)

    def test_init_stream(self):
        """Test constructor that creates object from stream."""
        stream = ['\x01', '\x00', '\x03', '\x02', '\n', '\x00']
        m = Message.init_stream(stream)
        # Check properties
        self.assertEqual(m.cmd, chr(0x01))
        self.assertEqual(m.load, [chr(2), chr(10), chr(0)])
        # Convert message to stream
        self.assertEqual(m.to_stream(), stream)

    def test_conv_to_stream(self):
        """Test conversion from message to stream."""
        # Example in 3.8.2 of BSMP protocol document
        curve_id = chr(0x07)
        blk_n = [chr(0x40), chr(0x00)]
        blk_load = [chr(0xdd) for _ in range(16384)]
        load = [curve_id] + blk_n + blk_load
        m = Message(cmd=chr(0x41), load=load)

        expected_stream = [chr(0x41), chr(0x40), chr(0x03)] + load

        self.assertEqual(m.to_stream(), expected_stream)


class TestBSMPPackage(unittest.TestCase):
    """Test BSMP Package class."""

    # Tuples with address, message and checksum
    data = [
        (chr(1), chr(0x10), [chr(3)], ['\x01', '\x10', '\x00', '\x01', '\x03',
         chr(235)], 235),
        (chr(0), chr(0x11), [chr(3), chr(255), chr(255)],
         ['\x00', '\x11', '\x00', '\x03', '\x03', '\xFF', '\xFF', chr(235)],
         235),
        (chr(2), chr(0x20), [chr(4), chr(1), chr(187), chr(187)],
         ['\x02', '\x20', '\x00', '\x04', '\x04', '\x01', '\xBB', '\xBB',
          chr(95)], 95),
        (chr(3), chr(0x22), [chr(2), chr(1), chr(187), chr(187), chr(1),
         chr(187), chr(187), chr(1), chr(187), chr(187), chr(1), chr(187),
         chr(187), chr(204)],
         ['\x03', '\x22', '\x00', '\x0E', '\x02', '\x01', '\xBB', '\xBB',
          '\x01', '\xBB', '\xBB', '\x01', '\xBB', '\xBB', '\x01', '\xBB',
          '\xBB', '\xCC', chr(35)], 35),
    ]

    api = (
        'init_stream',
        'address',
        'message',
        'checksum',
        'to_stream',
        'calc_checksum',
        'verify_checksum',
    )

    def test_api(self):
        """Test API."""
        self.assertTrue(check_public_interface_namespace(Package, self.api))

    def test_init(self):
        """Test constructor."""
        address = 1
        m = Message(0x00)
        p = Package(address=address, message=m)

        self.assertEqual(p.address, address)
        self.assertEqual(p.message, m)

    def test_init_stream(self):
        """Test constructor that creates object from stream."""
        for d in self.data:
            stream = d[3]
            p = Package.init_stream(stream)
            self.assertEqual(p.address, d[0])
            self.assertEqual(p.message.cmd, d[1])
            self.assertEqual(p.message.load, d[2])

    def test_parse_small_stream(self):
        """Test constructor that tries to parse strem smaller than 5."""
        stream = ['\x02', '\x00', '\x00', chr(254)]
        with self.assertRaises(ValueError):
            Package.init_stream(stream)

    def test_checksum(self):
        """Test checksum value."""
        for d in self.data:
            p = Package(d[0], Message(d[1], d[2]))
            self.assertEqual(p.checksum, d[4])

    def test_conv_to_stream(self):
        """Test conversion of package to stream."""
        for d in self.data:
            p = Package(d[0], Message(d[1], d[2]))
            self.assertEqual(p.to_stream(), d[3])

    def test_verify_checksum(self):
        """Verify checksum sucessfully."""
        for d in self.data:
            stream = d[3]
            self.assertTrue(Package.verify_checksum(stream))

    def test_verify_false_checksum(self):
        """Verify checksums fail."""
        for d in self.data:
            stream, checksum = d[3][:-1], ord(d[3][-1])
            stream += [chr(checksum + 1)]
            self.assertFalse(Package.verify_checksum(stream))


class TestBSMPChannel(unittest.TestCase):
    """Test Channel class of BSMP package."""

    api = ('read', 'write', 'request')

    def setUp(self):
        """Common setup for all tests."""
        self.serial = Mock()
        self.channel = Channel(self.serial, 1)

    def test_api(self):
        """Test API."""
        self.assertTrue(check_public_interface_namespace(Channel, self.api))

    def test_read_calls_serial_method(self):
        """Test UART_read is called."""
        response = Message(chr(0x11), [chr(10)])
        self.serial.UART_read.return_value = \
            Package(chr(0x01), response).to_stream()
        self.channel.read()
        self.serial.UART_read.assert_called_once()

    def test_read(self):
        """Test read method."""
        response = Message(chr(0x11), [chr(10)])
        self.serial.UART_read.return_value = \
            Package(chr(0x01), response).to_stream()
        recv = self.channel.read()
        self.assertEqual(recv.cmd, response.cmd)
        self.assertEqual(recv.load, response.load)

    def test_write_calls_serial_method(self):
        """Test write calls UART_write."""
        message = Message(chr(0x10), [chr(1)])
        expected_stream = \
            Package(chr(self.channel.address), message).to_stream()
        self.channel.write(message, 1000)
        self.serial.UART_write.assert_called_with(
            expected_stream, timeout=1000)

    def test_request(self):
        """Test request."""
        response = Message(chr(0x11), [chr(10)])
        self.serial.UART_read.return_value = \
            Package(chr(0x01), response).to_stream()
        recv = self.channel.request(Message(chr(0x01), [chr(1)]), timeout=1)
        self.assertEqual(recv.cmd, response.cmd)
        self.assertEqual(recv.load, response.load)


class TestBSMPVariable(unittest.TestCase):
    """Test Variable class."""

    api = ('load_to_value', 'value_to_load')

    def setUp(self):
        """Common setup for all tests."""
        self.channel = Mock()

    def test_api(self):
        """Test API."""
        self.assertTrue(check_public_interface_namespace(Variable, self.api))

    def test_int_value_to_load(self):
        """Test value to load method."""
        value = 10
        expected_load = chr(10)
        var = Variable(1, False, 2, 'int')
        self.assertEqual(var.value_to_load(value), expected_load)

    def test_float_value_to_load(self):
        """Test value to load method."""
        value = 10.5
        expected_load = struct.pack('<f', value)
        var = Variable(1, False, 4, 'float')
        self.assertEqual(var.value_to_load(value), expected_load)

    def test_string_value_to_load(self):
        """Test value to load method."""
        value = 'V1.0 2018-03-21'

        expected_load = []
        for c in value:
            expected_load.append(c)
        while len(expected_load) <= 128:
            expected_load.append(chr(0))
        var = Variable(1, False, 0, 'string')
        self.assertEqual(var.value_to_load(value), expected_load)

    def test_arr_float_value_to_load(self):
        """Test value to load method."""
        value = [1.0, 2.0, 3.0, 4.0]
        expected_load = bytes()
        for v in value:
            expected_load += struct.pack('<f', v)
        var = Variable(1, False, 16, 'arr_float')
        self.assertEqual(var.value_to_load(value), expected_load)

    def test_int_load_to_value(self):
        """Test load to value conversion method."""
        for i in range(1, 6):
            var = Variable(1, False, i, 'int')
            load = [chr(1) for _ in range(i)]
            expected_value = 0
            for j in range(i):
                expected_value += 1 << j*8
            self.assertEqual(var.load_to_value(load), expected_value)

    def test_float_load_to_value(self):
        """Test load to value conversion method."""
        load = struct.pack('<f', 10.5)
        expected_value = 10.5
        var = Variable(1, False, 4, 'float')
        self.assertEqual(var.load_to_value(load), expected_value)

    def test_string_load_to_value(self):
        """Test load to value conversion method."""
        load = 'V1.0 2018-03-21'.encode()

        while len(load) < 127:
            load += chr(0).encode()

        expected_value = 'V1.0 2018-03-21'
        var = Variable(1, False, 0, 'string')
        self.assertEqual(var.load_to_value(load), expected_value)

    def test_arr_float_load_to_value(self):
        """Test load to value conversion method."""
        expected_value = [1.0, 2.0, 3.0, 4.0]
        load = bytes()
        for value in expected_value:
            load += struct.pack('<f', value)
        var = Variable(1, False, 16, 'arr_float')
        self.assertEqual(var.load_to_value(load), expected_value)


# class _TestBSMP(unittest.TestCase):
#     """Test BSMP class."""
#
#     api = (
#         'ID_device',
#         'variables',
#         'functions',
#         'parse_stream',
#     )
#
#     def test_api(self):
#         """Test API."""
#         self.assertTrue(check_public_interface_namespace(BSMP, TestBSMP.api))
#
#     def test_init(self):
#         """Test parameters are initialized correctly."""
#         id_device = 0
#         variables = {'var1': 'val1', 'var2': 'val2'}
#         functions = {'func1': print, 'func2': BSMP.parse_stream}
#
#         bsmp = BSMP(id_device, variables, functions)
#
#         self.assertEqual(bsmp.ID_device, 0)
#         self.assertEqual(bsmp.variables, variables)
#         self.assertEqual(bsmp.functions, functions)
#
#     def test_parse_stream_small_stream(self):
#         """Test ValueError is raised when stream is too small."""
#         with self.assertRaises(ValueError):
#             BSMP.parse_stream(['\x30', '\x00', '\x25', '\x00'])
#
#     def test_parse_stream_no_checksum(self):
#         """Test ValueError is raised when checksum fails."""
#         stream = ['\x30', '\x00', '\x25', '\x00', '\x00', '\x00']
#         with self.assertRaises(ValueError):
#             BSMP.parse_stream(stream)
#
#     def test_parse_stream(self):
#         """Test stream is correctly parsed."""
#         stream = ['\x00', '\x0A', '\x02', '\x00', '\x00', '\x00']
#         stream = StreamChecksum.includeChecksum(stream)
#         id_receiver, id_cmd, load_size, load = BSMP.parse_stream(stream)
#         # print(id_receiver, id_cmd, load_size, load)
#         self.assertEqual(id_receiver, '\x00')
#         self.assertEqual(id_cmd, 10)
#         self.assertEqual(load_size, 2)
#         self.assertEqual(load, ['\x00', '\x00'])


# class _TestBSMPQuery(unittest.TestCase):
#     """Test BSMPQuery class."""
#
#     api = (
#         'slaves',
#         'add_slave',
#         'cmd_0x00',
#         'cmd_0x10',
#         'cmd_0x12',
#         'cmd_0x30',
#         'cmd_0x32',
#         'cmd_0x50'
#     )
#
#     def setUp(self):
#         """Common setup for all tests."""
#         self.variables = {'var1': 'val1', 'var2': 'val2'}
#         self.functions = {'func1': print, 'func2': BSMP.parse_stream}
#         self.slaves = list()
#         for i in range(3):
#             mock = Mock()
#             id_device = PropertyMock(return_value=i+1)
#             type(mock).ID_device = id_device
#             self.slaves.append(mock)
#
#         self.bsmp = BSMPQuery(self.variables, self.functions, self.slaves)
#
#     def test_api(self):
#         """Test API."""
#         self.assertTrue(
#             check_public_interface_namespace(BSMPQuery, TestBSMPQuery.api))
#
#     def test_init(self):
#         """Test initial values passed in the constructor."""
#         self.assertEqual(self.bsmp.ID_device, 0)
#         self.assertEqual(self.bsmp.variables, self.variables)
#         self.assertEqual(self.bsmp.functions, self.functions)
#
#     def test_cmd_0x00(self):
#         """Test query is called with correct parameters."""
#         self.bsmp.cmd_0x00(1)
#         self.bsmp.slaves[1].query.assert_called_with(0x00, ID_receiver=1)
#
#     def test_cmd_0x10(self):
#         """Test query is called with correct parameters."""
#         self.bsmp.cmd_0x10(1, 2)
#         self.bsmp.slaves[1].query.assert_called_with(
#             0x10, ID_receiver=1, ID_variable=2)
#
#     def test_cmd_0x12(self):
#         """Test query is called with correct parameters."""
#         self.bsmp.cmd_0x12(2, 1)
#         self.bsmp.slaves[2].query.assert_called_with(
#             0x12, ID_receiver=2, ID_group=1)
#
#     def test_cmd_0x30(self):
#         """Test query is called with correct parameters."""
#         self.bsmp.cmd_0x30(3, 4, 2)
#         self.bsmp.slaves[3].query.assert_called_with(
#             0x30, ID_receiver=3, ID_group=4, IDs_variable=2)
#
#     def test_cmd_0x30_exc(self):
#         """Test query is called with correct parameters."""
#         with self.assertRaises(ValueError):
#             self.bsmp.cmd_0x30(3, 2, 2)
#
#     def test_cmd_0x32(self):
#         """Test query is called with correct parameters."""
#         self.bsmp.cmd_0x32(3)
#         self.bsmp.slaves[3].query.assert_called_with(0x32, ID_receiver=3)
#
#     def test_cmd_0x50(self):
#         """Test query is called with correct parameters."""
#         self.bsmp.cmd_0x50(ID_receiver=1)
#         self.bsmp.slaves[1].query.assert_called_with(0x50, ID_receiver=1)


# class _TestBSMPResponse(unittest.TestCase):
#     """Test BSMPResponse class."""
#
#     api = (
#         'query',
#         'create_group',
#         'remove_groups',
#         'cmd_0x01',
#         'cmd_0x11',
#         'cmd_0x13',
#         'cmd_0x51'
#     )
#
#     def test_api(self):
#         """Test API."""
#         self.assertTrue(
#             check_public_interface_namespace(
#                 BSMPResponse, TestBSMPResponse.api))
#
#     def test_query_2_resp(self):
#         """Test mapping from query to response is correct."""
#         self.assertEqual(BSMPResponse._query2resp[0x00], 'cmd_0x01')
#         self.assertEqual(BSMPResponse._query2resp[0x10], 'cmd_0x11')
#         self.assertEqual(BSMPResponse._query2resp[0x12], 'cmd_0x13')
#         self.assertEqual(BSMPResponse._query2resp[0x30], 'create_group')
#         self.assertEqual(BSMPResponse._query2resp[0x32], 'remove_groups')
#         self.assertEqual(BSMPResponse._query2resp[0x50], 'cmd_0x51')


if __name__ == "__main__":
    unittest.main()
