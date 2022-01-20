#!/usr/bin/env python-sirius

"""Unittest module for util.py."""

from io import StringIO
import logging
from unittest import mock, TestCase
import numpy as np

import siriuspy.util as util


PUB_INTERFACE = (
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
    'ClassProperty',
    )


class TestUtil(TestCase):
    """Test util."""

    def test_public_interface(self):
        """Test module's public interface."""
        valid = util.check_public_interface_namespace(util, PUB_INTERFACE)
        self.assertTrue(valid)

    def test_conv_splims_labels(self):
        """Test conv_splims_labels."""
        self.assertEqual(util.conv_splims_labels('HOPR'), 'hilim')
        self.assertEqual(util.conv_splims_labels('lolo'), 'LOLO')
        self.assertRaises(KeyError, util.conv_splims_labels, label='dummmy')

    def test_get_last_commit_hash(self):
        """Test get_signal_names."""
        lst_comm = util.get_last_commit_hash()
        self.assertIsInstance(lst_comm, str)

    def test_get_timestamp(self):
        """Test get_timestamp."""
        stime = util.get_timestamp()
        self.assertEqual(len(stime), 23)
        date, minute, second = stime.split(':')
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
        _, params = util.read_text_data(text)
        self.assertEqual(len(params), 3)
        self.assertEqual(len(params['parameter1']), 1)
        self.assertEqual(params['parameter1'][0], 'v1')
        self.assertEqual(len(params['parameter2']), 1)
        self.assertEqual(params['parameter2'][0], 'v2')
        self.assertEqual(len(params['parameter3']), 3)
        self.assertEqual(params['parameter3'][0], 'v3')
        self.assertEqual(params['parameter3'][1], 'v4')
        self.assertEqual(params['parameter3'][2], 'v5')

    def test_print_ioc_banner(self):
        """Test print_ioc_banner."""
        dbase = {}
        dbase.update(
            {'PV01': None, 'PV02': None, 'PV03': None, 'PV04': None, })
        dbase.update(
            {'PV05': None, 'PV06': None, 'PV07': None, 'PV08': None, })
        fil = StringIO()
        logging.root.handlers = []
        util.configure_log_file(stream=fil)
        util.print_ioc_banner(
            'test-ioc', dbase, 'Test-ioc for util module unittest',
            '1.0.0', 'PREFIX')
        text = fil.getvalue()
        self.assertEqual(len(text.splitlines()), 17)
        dbase.update(
            {'PV09': None, 'PV10': None, 'PV11': None, 'PV12': None, })
        dbase.update(
            {'PV13': None, 'PV14': None, 'PV15': None, 'PV16': None, })
        util.print_ioc_banner(
            'test-ioc', dbase, 'Test-ioc for util module unittest',
            '1.0.0', 'PREFIX')
        text = fil.getvalue()
        self.assertEqual(len(text.splitlines()), 25+17)

    def test_configure_log_file(self):
        """Test configure_log_file."""
        fil = StringIO()
        logging.root.handlers = []
        util.configure_log_file(stream=fil)
        logging.info('test')
        logging.debug('test')
        text = fil.getvalue()
        self.assertEqual(len(text.splitlines()), 1)

        fil = StringIO()
        logging.root.handlers = []
        util.configure_log_file(stream=fil, debug=True)
        logging.info('test')
        logging.debug('test')
        text = fil.getvalue()
        self.assertEqual(len(text.splitlines()), 2)

    def test_beam_rigidity(self):
        """Test beam_rigidity."""
        en0 = 510998.92760316096/1e9  # electron rest energy [GeV]
        tol = 1e-12
        # float arg
        ret, beta, gamma = util.beam_rigidity(3.0)
        self.assertIsInstance(ret, float)
        self.assertAlmostEqual(ret, 10.00692271077752, delta=tol)
        self.assertAlmostEqual(beta, 0.9999999854933386, delta=tol)
        self.assertAlmostEqual(gamma, 5870.853550721619, delta=tol)
        ret, *_ = util.beam_rigidity(energy=1.001*en0)
        self.assertIsInstance(ret, float)
        self.assertAlmostEqual(ret, 7.624534235479652e-05, delta=tol)
        ret, *_ = util.beam_rigidity(0.0)
        self.assertEqual(ret, 0.0)
        ret, *_ = util.beam_rigidity(0.999*en0)
        self.assertEqual(ret, 0.0)
        # list arg
        ret, *_ = util.beam_rigidity([0.5, 3.0])
        self.assertIsInstance(ret, np.ndarray)
        self.assertAlmostEqual(ret[0], 1.6678196049882876, delta=tol)
        self.assertAlmostEqual(ret[1], 10.00692271077752, delta=tol)
        # tuple arg
        ret, *_ = util.beam_rigidity((0.5, 3.0))
        self.assertIsInstance(ret, np.ndarray)
        self.assertAlmostEqual(ret[0], 1.6678196049882876, delta=tol)
        self.assertAlmostEqual(ret[1], 10.00692271077752, delta=tol)
        # numpy.ndarray arg
        ret, *_ = util.beam_rigidity(np.array([0.5, 3.0]))
        self.assertIsInstance(ret, np.ndarray)
        self.assertAlmostEqual(ret[0], 1.6678196049882876, delta=tol)
        self.assertAlmostEqual(ret[1], 10.00692271077752, delta=tol)
        ret, *_ = util.beam_rigidity(energy=np.array([1.001*en0, 3.0]))
        self.assertIsInstance(ret, np.ndarray)
        self.assertAlmostEqual(ret[0], 7.624534235479652e-05, delta=tol)

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
        self.assertEqual(
            "Kick", util.get_strength_label("corrector-horizontal"))
        self.assertEqual("Kick", util.get_strength_label("corrector-vertical"))
        self.assertRaises(ValueError, util.get_strength_label, magfunc='')

    def test_get_strength_units(self):
        """Test get_strength_units."""
        self.assertEqual("GeV", util.get_strength_units("dipole"))
        self.assertEqual("1/m", util.get_strength_units("quadrupole"))
        self.assertEqual("1/m", util.get_strength_units("quadrupole-skew"))
        self.assertEqual("1/m^2", util.get_strength_units("sextupole"))
        self.assertEqual(
            "urad",
            util.get_strength_units("corrector-horizontal", None, False))
        self.assertEqual(
            "urad", util.get_strength_units("corrector-vertical", None, False))
        self.assertEqual(
            "mrad",
            util.get_strength_units("corrector-horizontal", None, True))
        self.assertEqual(
            "mrad", util.get_strength_units("corrector-vertical", None, True))
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
        """Test test_mode."""
        self.assertEqual((3, 2), util.mode([1, 2, 3, 4, 5, 6, 3]))

    def test_check_public_interface_namespace(self):
        """Test check_public_interface_namespace."""
        class NameSpace:
            """."""

            A = None
            B = None

        public_interface = ('A', 'B', )
        valid = util.check_public_interface_namespace(
            NameSpace, public_interface)
        self.assertTrue(valid)
        NameSpace.C = None
        valid = util.check_public_interface_namespace(
            NameSpace, public_interface, print_flag=False)
        self.assertFalse(valid)
        public_interface = ('A', 'B', 'missing_symbol')
        valid = util.check_public_interface_namespace(
            NameSpace, public_interface, print_flag=False)
        self.assertFalse(valid)
