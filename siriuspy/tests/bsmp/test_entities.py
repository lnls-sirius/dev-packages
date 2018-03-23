"""Test BSMP Entities."""
import unittest
import struct

from siriuspy.bsmp import Types
from siriuspy.bsmp import Variable, VariablesGroup, Curve, Function
from siriuspy.util import check_public_interface_namespace


class TestBSMPVariable(unittest.TestCase):
    """Test Variable class."""

    api = ('load_to_value', 'value_to_load')

    def test_api(self):
        """Test API."""
        self.assertTrue(check_public_interface_namespace(Variable, self.api))

    def test_int_value_to_load(self):
        """Test value to load method."""
        value = 10
        expected_load = [chr(b) for b in struct.pack('<b', 10)]
        var = Variable(1, False, Types.t_uint8, 1)
        self.assertEqual(var.value_to_load(value), expected_load)

    def test_float_value_to_load(self):
        """Test value to load method."""
        value = 10.5
        expected_load = [chr(b) for b in struct.pack('<f', value)]
        var = Variable(1, False, Types.t_float, 1)
        self.assertEqual(var.value_to_load(value), expected_load)

    def test_string_value_to_load(self):
        """Test value to load method."""
        value = 'V0.07 2018-03-14V0.07 2018-03-14'

        expected_load = ['V', '0', '.', '0', '7', ' ', '2', '0', '1', '8', '-',
                         '0', '3', '-', '1', '4', 'V', '0', '.', '0', '7', ' ',
                         '2', '0', '1', '8', '-', '0', '3', '-', '1', '4',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                         '\x00', '\x00', '\x00', '\x00', '\x00', '\x00']

        var = Variable(1, False, Types.t_char, 128)
        self.assertEqual(var.value_to_load(value), expected_load)

    def test_arr_float_value_to_load(self):
        """Test value to load method."""
        value = [1.0, 2.0, 3.0, 4.0]
        expected_load = []
        for v in value:
            expected_load.extend(list(map(chr, struct.pack('<f', v))))
        var = Variable(1, False, Types.t_float, 4)
        self.assertEqual(var.value_to_load(value), expected_load)

    def test_int_load_to_value(self):
        """Test load to value conversion method."""
        expected_value = 257
        load = [chr(1) for _ in range(2)]
        var = Variable(1, False, Types.t_uint16, 1)
        self.assertEqual(var.load_to_value(load), expected_value)

    def test_float_load_to_value(self):
        """Test load to value conversion method."""
        load = [chr(v) for v in struct.pack('<f', 10.5)]
        expected_value = 10.5
        var = Variable(1, False, Types.t_float, 1)
        self.assertEqual(var.load_to_value(load), expected_value)

    def test_string_load_to_value(self):
        """Test load to value conversion method."""
        load = ['V', '0', '.', '0', '7', ' ', '2', '0', '1', '8', '-', '0',
                '3', '-', '1', '4', 'V', '0', '.', '0', '7', ' ', '2', '0',
                '1', '8', '-', '0', '3', '-', '1', '4', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00',
                '\x00', '\x00', '\x00', '\x00', '\x00']

        expected_value = 'V0.07 2018-03-14V0.07 2018-03-14'
        var = Variable(1, False, Types.t_char, 128)
        self.assertEqual(var.load_to_value(load), expected_value)

    def test_arr_float_load_to_value(self):
        """Test load to value conversion method."""
        load = ['\x00', '\x00', '\x80', '?', '\x00', '\x00', '\x80', '?',
                '\x00', '\x00', '\x80', '?', '\x00', '\x00', '\x00', '\x00']
        expected_value = [1.0, 1.0, 1.0, 0.0]
        var = Variable(1, False, Types.t_float, 4)
        self.assertEqual(var.load_to_value(load), expected_value)


class TestBSMPVariablesGroup(unittest.TestCase):
    """Test VariablesGroup class."""

    api = ('load_to_value', 'value_to_load', 'variables_size')

    def setUp(self):
        """Common setup for all test."""
        variables = [
            Variable(0, False, Types.t_uint8, 1),
            Variable(1, False, Types.t_uint16, 1),
            Variable(2, False, Types.t_uint32, 1),
            Variable(3, False, Types.t_float, 1),
            Variable(4, False, Types.t_float, 4),
            Variable(5, False, Types.t_char, 8),
        ]

        self.group = VariablesGroup(3, False, variables)

    def test_api(self):
        """Test API."""
        self.assertTrue(
            check_public_interface_namespace(VariablesGroup, self.api))

    def _conv_value(self, fmt, value):
        return list(map(chr, struct.pack(fmt, value)))

    def test_load_to_value(self):
        """Test load conversion to value."""
        c = self._conv_value
        string = ['t', 'e', 's', 't', 'e', chr(0), chr(0), chr(0)]
        load = c('<b', 5) + c('<h', 15) + c('<i', 25) + c('<f', 1.5) + \
            c('<f', 1.6) + c('<f', 1.7) + c('<f', 1.8) + c('<f', 1.9) + \
            string
        expected_value = [5, 15, 25, 1.5, [1.6, 1.7, 1.8, 1.9], 'teste']
        value = self.group.load_to_value(load)
        self.assertEqual(value[:4], expected_value[:4])
        for i, f in enumerate(value[4]):
            self.assertAlmostEqual(f, expected_value[4][i])
        self.assertEqual(value[-1], expected_value[-1])

    def test_value_to_load(self):
        """Test value conversion to load."""
        c = self._conv_value
        string = ['t', 'e', 's', 't', 'e', chr(0), chr(0), chr(0)]
        expected_load = c('<b', 5) + c('<h', 15) + c('<i', 25) + \
            c('<f', 1.5) + c('<f', 1.6) + c('<f', 1.7) + c('<f', 1.8) + \
            c('<f', 1.9) + string
        value = [5, 15, 25, 1.5, [1.6, 1.7, 1.8, 1.9], 'teste']
        load = self.group.value_to_load(value)
        self.assertEqual(load, expected_load)


class TestBSMPCurve(unittest.TestCase):
    """Test Curve class."""

    pass


class TestBSMPFunction(unittest.TestCase):
    """Test Function class."""

    api = ('value_to_load', 'load_to_value')

    def test_api(self):
        """Test API."""
        self.assertTrue(check_public_interface_namespace(Function, self.api))

    def test_small_input_size(self):
        """Test input size smaller than 0."""
        with self.assertRaises(ValueError):
            Function(1, -1, Types.t_uint16, 1, Types.t_uint16)

    def test_small_output_size(self):
        """Test output size smaller than 0."""
        with self.assertRaises(ValueError):
            Function(1, 1, Types.t_uint16, -1, Types.t_uint16)

    def test_big_input_size(self):
        """Test input size bigger than 0."""
        with self.assertRaises(ValueError):
            Function(1, 16, Types.t_uint16, 1, Types.t_uint16)

    def test_big_putput_size(self):
        """Test output size bigger than 0."""
        with self.assertRaises(ValueError):
            Function(1, 1, Types.t_uint16, 17, Types.t_uint16)

    def test_null_value_to_load(self):
        """Test empty list is returned."""
        ret = \
            Function(1, 1, Types.t_uint16, 1,
                     Types.t_uint16).value_to_load(None)
        self.assertEqual(ret, [])

    def test_strange_value_to_load(self):
        """Test empty list is returned."""
        with self.assertRaises(TypeError):
            Function(1, 1, Types.t_uint16, 1,
                     Types.t_uint16).value_to_load(1.5)
        with self.assertRaises(TypeError):
            Function(1, 1, Types.t_char, 1, Types.t_uint16).value_to_load(15)

    def test_int_value_to_load(self):
        """Test value to load method."""
        value = 10
        expected_load = [chr(b) for b in struct.pack('<b', 10)]
        func = Function(1, 1, Types.t_uint8, 1, Types.t_uint8)
        self.assertEqual(func.value_to_load(value), expected_load)

    def test_float_value_to_load(self):
        """Test value to load method."""
        value = 10.5
        expected_load = [chr(b) for b in struct.pack('<f', value)]
        func = Function(1, 1, Types.t_float, 1, Types.t_uint8)
        self.assertEqual(func.value_to_load(value), expected_load)

    def test_string_value_to_load(self):
        """Test value to load method."""
        value = 'V0.07 2018-03'
        expected_load = ['V', '0', '.', '0', '7', ' ', '2', '0', '1', '8', '-',
                         '0', '3', '\x00', '\x00']

        func = Function(1, 15, Types.t_char, 1, Types.t_uint8)
        self.assertEqual(func.value_to_load(value), expected_load)

    def test_arr_float_value_to_load(self):
        """Test value to load method."""
        value = [1.0, 2.0]
        expected_load = []
        for v in value:
            expected_load.extend(list(map(chr, struct.pack('<f', v))))
        func = Function(1, 2, Types.t_float, 1, Types.t_uint8)
        self.assertEqual(func.value_to_load(value), expected_load)

    def test_null_load_to_value(self):
        """Test empty list is returned."""
        ret = \
            Function(1, 1, Types.t_uint8, 1, Types.t_uint8).load_to_value(None)
        self.assertIsNone(ret)

    def test_empty_load_to_value(self):
        """Test empty list is returned."""
        ret = Function(1, 1, Types.t_uint8, 1, Types.t_uint8).load_to_value([])
        self.assertIsNone(ret)

    def test_int_load_to_value(self):
        """Test load to value conversion method."""
        expected_value = 1
        load = [chr(1)]
        func = Function(1, 1, Types.t_uint8, 1, Types.t_uint8)
        self.assertEqual(func.load_to_value(load), expected_value)

    def test_float_load_to_value(self):
        """Test load to value conversion method."""
        load = [chr(v) for v in struct.pack('<f', 10.5)]
        expected_value = 10.5
        func = Function(1, 1, Types.t_uint8, 1, Types.t_float)
        self.assertEqual(func.load_to_value(load), expected_value)

    def test_string_load_to_value(self):
        """Test load to value conversion method."""
        load = ['V', '0', '.', '0', '7', ' ', '2', '0', '1', '8', '\x00',
                '\x00', '\x00', '\x00', '\x00']

        expected_value = 'V0.07 2018'
        func = Function(1, 1, Types.t_uint8, 15, Types.t_char)
        self.assertEqual(func.load_to_value(load), expected_value)

    def test_arr_float_load_to_value(self):
        """Test load to value conversion method."""
        load = ['\x00', '\x00', '\x80', '?', '\x00', '\x00', '\x00', '\x00']
        expected_value = [1.0, 0.0]
        func = Function(1, 1, Types.t_uint8, 2, Types.t_float)
        self.assertEqual(func.load_to_value(load), expected_value)


class TestBSMPEntities(unittest.TestCase):
    """This class only has propertyies."""

    pass


if __name__ == '__main__':
    unittest.main()
