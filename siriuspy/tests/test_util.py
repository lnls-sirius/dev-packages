#!/usr/bin/env python-sirius

"""Unittest module for util.py."""

import unittest
import siriuspy.util as util
from io import StringIO


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


if __name__ == "__main__":
    unittest.main()
