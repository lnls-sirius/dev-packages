#!/usr/bin/env python-sirius

"""Unittest module for util.py."""

import unittest
from unittest import mock
from io import StringIO

import epics

import siriuspy.util as util


class TestUtil(unittest.TestCase):
    """Test util."""

    def test_conv_splims_labels(self):
        """Test conv_splims_labels."""
        self.assertEqual(util.conv_splims_labels('HOPR'), 'hilim')
        self.assertEqual(util.conv_splims_labels('lolo'), 'LOLO')
        self.assertIs(util.conv_splims_labels('dumb'), None)

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

    def test_save_ioc_pv_list(self):
        m = mock.mock_open()
        db = ['pv1', 'pv2']
        with mock.patch('siriuspy.util.open', m, create=True):
            util.save_ioc_pv_list('ioc', ('p0', 'p1'), db)

        # print(m.mock_calls)
        calls = [mock.call('p1\n'), mock.call('p0pv1\n'),
                 mock.call('p0pv2\n')]
        self.assertEqual(m().write.call_args_list, calls)

    def test_print_ioc_banner(self):
        """Test print_ioc_banner."""
        db = {}
        db.update({'PV01': None, 'PV02': None, 'PV03': None, 'PV04': None, })
        db.update({'PV05': None, 'PV06': None, 'PV07': None, 'PV08': None, })
        file = StringIO()
        util.print_ioc_banner('test-ioc', db,
                              'Test-ioc for util module unittest',
                              '1.0.0', 'PREFIX', file=file)
        text = file.getvalue()
        self.assertEqual(len(text.splitlines()), 10)
        db.update({'PV09': None, 'PV10': None, 'PV11': None, 'PV12': None, })
        db.update({'PV13': None, 'PV14': None, 'PV15': None, 'PV16': None, })
        file = StringIO()
        util.print_ioc_banner('test-ioc', db,
                              'Test-ioc for util module unittest',
                              '1.0.0', 'PREFIX', file=file)
        text = file.getvalue()
        self.assertEqual(len(text.splitlines()), 12)

    def test_check_running_ioc(self):
        """Test check_running_ioc."""
        with mock.patch.object(epics.PV,
                               "wait_for_connection",
                               return_value=True) as mock_conn:
            status = util.check_running_ioc("FakePV")
        self.assertEqual(status, True)
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

    def test_get_strength_units(self):
        """Test get_strength_units."""
        self.assertEqual("GeV", util.get_strength_units("dipole"))
        self.assertEqual("1/m", util.get_strength_units("quadrupole"))
        self.assertEqual("1/m", util.get_strength_units("quadrupole-skew"))
        self.assertEqual("1/m^2", util.get_strength_units("sextupole"))
        self.assertEqual(
            "urad", util.get_strength_units("corrector-horizontal", "SI"))
        self.assertEqual(
            "urad", util.get_strength_units("corrector-horizontal", "BO"))
        self.assertEqual(
            "urad", util.get_strength_units("corrector-vertical", "SI"))
        self.assertEqual(
            "urad", util.get_strength_units("corrector-vertical", "BO"))
        self.assertEqual(
            "mrad", util.get_strength_units("corrector-horizontal", "TB"))
        self.assertEqual(
            "mrad", util.get_strength_units("corrector-horizontal", "TS"))
        self.assertEqual(
            "mrad", util.get_strength_units("corrector-horizontal", "LI"))
        self.assertEqual(
            "mrad", util.get_strength_units("corrector-vertical", "TB"))
        self.assertEqual(
            "mrad", util.get_strength_units("corrector-vertical", "TS"))
        self.assertEqual(
            "mrad", util.get_strength_units("corrector-vertical", "LI"))


if __name__ == "__main__":
    unittest.main()
