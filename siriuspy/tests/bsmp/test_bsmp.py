#!/usr/bin/env python-sirius
"""BSMP class tests."""
import unittest
from unittest.mock import Mock, PropertyMock

from siriuspy.bsmp import Message, Package
from siriuspy.bsmp import BSMP, BSMPQuery, BSMPResponse
from siriuspy.pwrsupply.bsmp import StreamChecksum
from siriuspy.util import check_public_interface_namespace


class TestBSMPMessage(unittest.TestCase):
    """Test BSMP Message class."""

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

    def test_parse_stream(self):
        """Test constructor that creates object from stream."""
        stream = ['\x01', '\x00', '\x03', '\x02', '\n', '\x00']
        m = Message.parse_stream(stream)
        # Check properties
        self.assertEqual(m.cmd, 0x01)
        self.assertEqual(m.load, [2, 10, 0])
        # Convert message to stream
        self.assertEqual(m.to_stream(), stream)

    def test_conv_to_stream(self):
        """Test conversion from message to stream."""
        # Example in 3.8.2 of BSMP protocol document
        curve_id = 0x07
        blk_n = [0x40, 0x00]
        blk_load = [0xdd for _ in range(16384)]
        load = [curve_id] + blk_n + blk_load
        m = Message(cmd=0x41, load=load)

        expected_stream = [chr(0x41), chr(0x40), chr(0x03)] + \
            [chr(x) for x in load]

        self.assertEqual(m.to_stream(), expected_stream)

    def test_encode_cmd(self):
        """Test method that encodes the command id."""
        cmds = [0x00, 0x02, 0x10, 0x30]
        for cmd in cmds:
            self.assertEqual(Message.encode_cmd(cmd), chr(cmd))

    def test_decode_cmd(self):
        """Test method that decodes the command id."""
        cmds = ['\x00', '@', '\x03']
        for cmd in cmds:
            self.assertEqual(Message.decode_cmd(cmd), ord(cmd))

    def test_encode_load(self):
        """Test load encoding."""
        loads = [[], [1, ], [1, 2, 3]]
        for load in loads:
            self.assertEqual(Message.encode_load(load), [chr(l) for l in load])

    def test_decode_load(self):
        """Test load encoding."""
        loads = [[], ['\x01', ], ['\x01', '\x02', '\x03']]
        for load in loads:
            self.assertEqual(Message.decode_load(load), [ord(l) for l in load])


class TestBSMPPackage(unittest.TestCase):
    """Test BSMP Package class."""

    # Tuples with address, message and checksum
    data = [
        (1, 0x10, [3], ['\x01', '\x10', '\x00', '\x01', '\x03', chr(235)],
         235),
        (0, 0x11, [3, 255, 255],
         ['\x00', '\x11', '\x00', '\x03', '\x03', '\xFF', '\xFF', chr(235)],
         235),
        (2, 0x20, [4, 1, 187, 187],
         ['\x02', '\x20', '\x00', '\x04', '\x04', '\x01', '\xBB', '\xBB',
          chr(95)], 95),
        (3, 0x22, [2, 1, 187, 187, 1, 187, 187, 1, 187, 187, 1, 187, 187, 204],
         ['\x03', '\x22', '\x00', '\x0E', '\x02', '\x01', '\xBB', '\xBB',
          '\x01', '\xBB', '\xBB', '\x01', '\xBB', '\xBB', '\x01', '\xBB',
          '\xBB', '\xCC', chr(35)], 35),
    ]

    def test_init(self):
        """Test constructor."""
        address = 1
        m = Message(0x00)
        p = Package(address=address, message=m)

        self.assertEqual(p.address, address)
        self.assertEqual(p.message, m)

    def test_parse_stream(self):
        """Test constructor that creates object from stream."""
        for d in self.data:
            stream = d[3]
            p = Package.parse_stream(stream)
            self.assertEqual(p.address, d[0])
            self.assertEqual(p.message.cmd, d[1])
            self.assertEqual(p.message.load, d[2])

    def test_parse_small_stream(self):
        """Test constructor that tries to parse strem smaller than 5."""
        stream = ['\x02', '\x00', '\x00', chr(254)]
        with self.assertRaises(ValueError):
            Package.parse_stream(stream)

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
