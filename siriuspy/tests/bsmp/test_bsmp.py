# #!/usr/bin/env python-sirius
# """BSMP class tests."""
# import unittest
# from unittest.mock import Mock
#
# from siriuspy.util import check_public_interface_namespace
#
#
# class _TestBSMP(TestCase):
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
#
#
# class _TestBSMPQuery(TestCase):
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
#
#
# class _TestBSMPResponse(TestCase):
#     """Test BSMPResponse class."""
#
#     api = (
#         'query',
#         'create_group_of_variables',
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
#         self.assertEqual(BSMPResponse._query2resp[0x30], 'create_group_of_variables')
#         self.assertEqual(BSMPResponse._query2resp[0x32], 'remove_groups')
#         self.assertEqual(BSMPResponse._query2resp[0x50], 'cmd_0x51')
