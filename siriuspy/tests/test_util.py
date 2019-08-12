#!/usr/bin/env python-sirius

"""Unittest module for util.py."""

from io import StringIO
import logging
import numpy as np
from unittest import mock, TestCase
import siriuspy.util as util


public_interface = (
    'conv_splims_labels',
    'get_last_commit_hash',
    'get_timestamp',
    'read_text_data',
    'print_ioc_banner',
    'configure_log_file',
    'beam_rigidity',
    'check_pv_online',
    'get_strength_label',
    'get_strength_units',
    'update_bit',
    'get_bit',
    'mode',
    'check_public_interface_namespace',
    'get_namedtuple',
)


class TestUtil(TestCase):
    """Test util."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(util, public_interface)
        self.assertTrue(valid)

    def test_conv_splims_labels(self):
        """Test conv_splims_labels."""
        self.assertEqual(util.conv_splims_labels('HOPR'), 'hilim')
        self.assertEqual(util.conv_splims_labels('lolo'), 'LOLO')
        self.assertRaises(KeyError, util.conv_splims_labels, label='dummmy')

    def test_get_last_commit_hash(self):
        """Test get_signal_names."""
        lc = util.get_last_commit_hash()
        self.assertIsInstance(lc, str)

    def test_get_timestamp(self):
        """Test get_timestamp."""
        ts = util.get_timestamp()
        self.assertEqual(len(ts), 23)
        date, minute, second = ts.split(':')
        year, month, day, hour = date.split('-')
        second, msecond = second.split('.')
        self.assertTrue(year.isnumeric())
        self.assertTrue(month.isnumeric())
        self.assertTrue(day.isnumeric())
        self.assertTrue(hour.isnumeric())
        self.assertTrue(minute.isnumeric())
        self.assertTrue(second.isnumeric())
        self.assertTrue(msecond.isnumeric())
        self.assertGreater(int(year), 2016)
        self.assertLess(int(month), 13)
        self.assertGreater(int(month), 0)
        self.assertLess(int(day), 32)
        self.assertGreater(int(day), 0)
        self.assertLess(int(hour), 24)
        self.assertGreater(int(hour), -1)
        self.assertLess(int(minute), 60)
        self.assertGreater(int(minute), -1)
        self.assertLess(int(second), 60)
        self.assertGreater(int(second), -1)
        self.assertLess(int(msecond), 1000)
        self.assertGreater(int(msecond), -1)

    def test_read_text_data(self):
        """Test read_text_data."""
        text = '\n'
        text += '# comment line 1\n'
        text += '# comment line 2 #\n'
        text += '# comment line 3 ## - test text !@#$&!&\n'
        text += '\n'
        text += '# comment line 4 after empty line\n'
        text += '\n'
        text += '\n'
        text += ' # comment line 5 starting wih space\n'
        text += '     # comment line 6 starting wih multiple spaces\n'
        text += ' # [parameter1] v1\n'  # comment line parameter
        text += ' #[parameter2] v2  \n'  # comment line with parameter
        text += '# [parameter3] v3 v4 v5  \n'  # comment line with parameter
        text += 'datum1 datum2 datum3\n'  # line with data
        text += 'datum4 datum5 datum6\n'  # line with data
        text += '\n'  # empty line between data
        text += '# comment line 5 after empty line\n'  # comment between data
        text += 'datum7\n'  # line with data
        data, parameters = util.read_text_data(text)
        self.assertEqual(len(parameters), 3)
        self.assertEqual(len(parameters['parameter1']), 1)
        self.assertEqual(parameters['parameter1'][0], 'v1')
        self.assertEqual(len(parameters['parameter2']), 1)
        self.assertEqual(parameters['parameter2'][0], 'v2')
        self.assertEqual(len(parameters['parameter3']), 3)
        self.assertEqual(parameters['parameter3'][0], 'v3')
        self.assertEqual(parameters['parameter3'][1], 'v4')
        self.assertEqual(parameters['parameter3'][2], 'v5')

    def test_print_ioc_banner(self):
        """Test print_ioc_banner."""
        db = {}
        db.update({'PV01': None, 'PV02': None, 'PV03': None, 'PV04': None, })
        db.update({'PV05': None, 'PV06': None, 'PV07': None, 'PV08': None, })
        fi = StringIO()
        logging.root.handlers = []
        util.configure_log_file(stream=fi)
        util.print_ioc_banner('test-ioc', db,
                              'Test-ioc for util module unittest',
                              '1.0.0', 'PREFIX')
        text = fi.getvalue()
        self.assertEqual(len(text.splitlines()), 18)
        db.update({'PV09': None, 'PV10': None, 'PV11': None, 'PV12': None, })
        db.update({'PV13': None, 'PV14': None, 'PV15': None, 'PV16': None, })
        util.print_ioc_banner('test-ioc', db,
                              'Test-ioc for util module unittest',
                              '1.0.0', 'PREFIX')
        text = fi.getvalue()
        self.assertEqual(len(text.splitlines()), 26+18)

    def test_configure_log_file(self):
        """Test configure_log_file."""
        fi = StringIO()
        logging.root.handlers = []
        util.configure_log_file(stream=fi)
        logging.info('test')
        logging.debug('test')
        text = fi.getvalue()
        self.assertEqual(len(text.splitlines()), 1)

        fi = StringIO()
        logging.root.handlers = []
        util.configure_log_file(stream=fi, debug=True)
        logging.info('test')
        logging.debug('test')
        text = fi.getvalue()
        self.assertEqual(len(text.splitlines()), 2)

    def test_beam_rigidity(self):
        """Test beam_rigidity."""
        e0 = 510998.92760316096/1e9  # electron rest energy [GeV]
        tol = 1e-12
        # float arg
        r, b, g = util.beam_rigidity(3.0)
        self.assertIsInstance(r, float)
        self.assertAlmostEqual(r, 10.00692271077752, delta=tol)
        self.assertAlmostEqual(b, 0.9999999854933386, delta=tol)
        self.assertAlmostEqual(g, 5870.853807994258, delta=tol)
        r, *_ = util.beam_rigidity(energy=1.001*e0)
        self.assertIsInstance(r, float)
        self.assertAlmostEqual(r, 7.624701218711276e-05, delta=tol)
        r, b, g = util.beam_rigidity(0.0)
        self.assertEqual(r, 0.0)
        # self.assertRaises(ValueError, util.beam_rigidity, energy=0.0)
        r, b, g = util.beam_rigidity(0.999*e0)
        self.assertEqual(r, 0.0)
        # self.assertRaises(ValueError, util.beam_rigidity, energy=0.999*e0)
        # list arg
        r, *_ = util.beam_rigidity([0.5, 3.0])
        self.assertIsInstance(r, np.ndarray)
        self.assertAlmostEqual(r[0], 1.6678196049882876, delta=tol)
        self.assertAlmostEqual(r[1], 10.00692271077752, delta=tol)
        # tuple arg
        r, *_ = util.beam_rigidity((0.5, 3.0))
        self.assertIsInstance(r, np.ndarray)
        self.assertAlmostEqual(r[0], 1.6678196049882876, delta=tol)
        self.assertAlmostEqual(r[1], 10.00692271077752, delta=tol)
        # numpy.ndarray arg
        r, *_ = util.beam_rigidity(np.array([0.5, 3.0]))
        self.assertIsInstance(r, np.ndarray)
        self.assertAlmostEqual(r[0], 1.6678196049882876, delta=tol)
        self.assertAlmostEqual(r[1], 10.00692271077752, delta=tol)
        r, *_ = util.beam_rigidity(energy=np.array([1.001*e0, 3.0]))
        self.assertIsInstance(r, np.ndarray)
        self.assertAlmostEqual(r[0], 7.624701218711276e-05, delta=tol)
        # self.assertRaises(ValueError, util.beam_rigidity,
        #                   energy=np.array([0.0, 3]))
        # self.assertRaises(ValueError, util.beam_rigidity,
        #                   energy=np.array([0.999*e0, 3.0]))

    def test_check_pv_online(self):
        """Test check_pv_online."""
        with mock.patch('siriuspy.util._epics.PV') as mock_conn:
            mock_conn.return_value.wait_for_connection.return_value = True
            status = util.check_pv_online("FakePV")
        self.assertEqual(status, True)
        mock_conn.assert_called()
        with mock.patch('siriuspy.util._epics.PV') as mock_conn:
            mock_conn.return_value.wait_for_connection.return_value = False
            status = util.check_pv_online("FakePV")
        self.assertEqual(status, False)
        mock_conn.assert_called()

    def test_get_strength_label(self):
        """Test get_strength_label."""
        self.assertEqual("Energy", util.get_strength_label("dipole"))
        self.assertEqual("KL", util.get_strength_label("quadrupole"))
        self.assertEqual("KL", util.get_strength_label("quadrupole-skew"))
        self.assertEqual("SL", util.get_strength_label("sextupole"))
        self.assertEqual("Kick",
                         util.get_strength_label("corrector-horizontal"))
        self.assertEqual("Kick", util.get_strength_label("corrector-vertical"))
        self.assertRaises(ValueError, util.get_strength_label, magfunc='')

    def test_get_strength_units(self):
        """Test get_strength_units."""
        self.assertEqual("GeV", util.get_strength_units("dipole"))
        self.assertEqual("1/m", util.get_strength_units("quadrupole"))
        self.assertEqual("1/m", util.get_strength_units("quadrupole-skew"))
        self.assertEqual("1/m^2", util.get_strength_units("sextupole"))
        self.assertEqual(
            "urad", util.get_strength_units("corrector-horizontal", False))
        self.assertEqual(
            "urad", util.get_strength_units("corrector-vertical", False))
        self.assertEqual(
            "mrad", util.get_strength_units("corrector-horizontal", True))
        self.assertEqual(
            "mrad", util.get_strength_units("corrector-vertical", True))
        self.assertRaises(ValueError, util.get_strength_units, magfunc='')

    def test_update_bit(self):
        """Test update_bit."""
        with self.assertRaises(TypeError):
            util.update_bit(v=0.1, bit_pos=0, bit_val=0)
        with self.assertRaises(TypeError):
            util.update_bit(v=0x2, bit_pos=1.0, bit_val=2)
        with self.assertRaises(ValueError):
            util.update_bit(v=-5, bit_pos=1, bit_val=0)
        with self.assertRaises(ValueError):
            util.update_bit(v=5, bit_pos=-1, bit_val=0)
        self.assertEqual(0xff, util.update_bit(v=0xdf, bit_pos=5, bit_val=1))
        self.assertEqual(0x00, util.update_bit(v=0x10, bit_pos=4, bit_val=0))
        self.assertEqual(0x00, util.update_bit(v=0x10, bit_pos=4, bit_val=[]))
        self.assertEqual(0x10, util.update_bit(v=0x10, bit_pos=4, bit_val=45))

    def test_get_bit(self):
        """Test get_bit."""
        with self.assertRaises(TypeError):
            util.get_bit(v=0.1, bit_pos=0)
        with self.assertRaises(TypeError):
            util.get_bit(v=0x2, bit_pos=1.0)
        with self.assertRaises(ValueError):
            util.get_bit(v=-5, bit_pos=1)
        with self.assertRaises(ValueError):
            util.get_bit(v=5, bit_pos=-1)
        self.assertEqual(0, util.get_bit(v=0xdf, bit_pos=5))
        self.assertEqual(1, util.get_bit(v=0x10, bit_pos=4))

    def test_mode(self):
        self.assertEqual((3, 2), util.mode([1, 2, 3, 4, 5, 6, 3]))

    def test_check_public_interface_namespace(self):
        """Test check_public_interface_namespace."""
        class namespace:
            A = None
            B = None
        public_interface = ('A', 'B', )
        valid = util.check_public_interface_namespace(
            namespace, public_interface)
        self.assertTrue(valid)
        namespace.C = None
        valid = util.check_public_interface_namespace(
            namespace, public_interface, print_flag=False)
        self.assertFalse(valid)
        public_interface = ('A', 'B', 'missing_symbol')
        valid = util.check_public_interface_namespace(
            namespace, public_interface, print_flag=False)
        self.assertFalse(valid)

    def test_get_namedtuple(self):
        """Test get_namedtuple."""
        fields = ('a', 'b', 'c')
        values = (1, 4, 5)
        a = util.get_namedtuple('A', fields, values)
        self.assertTrue(a.__class__.__name__ == 'A')
        self.assertTrue(a._fields == fields)
        self.assertTrue(a.a == 1 and a.b == 4 and a.c == 5)
        fields = ('a', 'b', 'c')
        a = util.get_namedtuple('A', fields)
        self.assertTrue(a.a == 0 and a.b == 1 and a.c == 2)
        fields = ('a a', 'b b', 'c')
        a = util.get_namedtuple('A', fields)
        self.assertTrue(a._fields == ('a_a', 'b_b', 'c'))
