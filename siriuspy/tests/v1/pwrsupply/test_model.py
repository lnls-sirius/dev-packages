#!/usr/bin/env python-sirius
"""Test public API of PowerSupply/Magnet class."""
import unittest
from unittest import mock

from siriuspy.pwrsupply.model import PowerSupply

database = {'Abort-Cmd': {'type': 'int', 'value': 0},
 'CtrlMode-Mon': {'enums': ('Remote', 'Local', 'PCHost'),
  'type': 'enum',
  'value': 0},
 'Current-Mon': {'high': 165.0,
  'hihi': 165.0,
  'hilim': 160.0,
  'lolim': 0.0,
  'lolo': 0.0,
  'low': 0.0,
  'prec': 4,
  'type': 'float',
  'unit': ['A', 'Ampere'],
  'value': 0.0},
 'Current-RB': {'high': 165.0,
  'hihi': 165.0,
  'hilim': 160.0,
  'lolim': 0.0,
  'lolo': 0.0,
  'low': 0.0,
  'prec': 4,
  'type': 'float',
  'unit': ['A', 'Ampere'],
  'value': 0.0},
 'Current-SP': {'high': 165.0,
  'hihi': 165.0,
  'hilim': 160.0,
  'lolim': 0.0,
  'lolo': 0.0,
  'low': 0.0,
  'prec': 4,
  'type': 'float',
  'unit': ['A', 'Ampere'],
  'value': 0.0},
 'CurrentRef-Mon': {'high': 165.0,
  'hihi': 165.0,
  'hilim': 160.0,
  'lolim': 0.0,
  'lolo': 0.0,
  'low': 0.0,
  'prec': 4,
  'type': 'float',
  'unit': ['A', 'Ampere'],
  'value': 0.0},
 'IntlkHard-Mon': {'type': 'int', 'value': 0},
 'IntlkHardLabels-Cte': {'count': 32,
  'type': 'string',
  'value': ('Overvoltage on load',
   'Overvoltage on DC-Link',
   'Undervoltage on DC-Link',
   'DC-Link input relay fail',
   'DC-Link input fuse fail',
   'Fail on module drivers',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved')},
 'IntlkSoft-Mon': {'type': 'int', 'value': 0},
 'IntlkSoftLabels-Cte': {'count': 32,
  'type': 'string',
  'value': ('Overtemperature on module',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved',
   'Reserved')},
 'OpMode-Sel': {'enums': ('SlowRef',
   'SlowRefSync',
   'FastRef',
   'RmpWfm',
   'MigWfm',
   'Cycle'),
  'type': 'enum',
  'value': 0},
 'OpMode-Sts': {'enums': ('SlowRef',
   'SlowRefSync',
   'FastRef',
   'RmpWfm',
   'MigWfm',
   'Cycle'),
  'type': 'enum',
  'value': 0},
 'PwrState-Sel': {'enums': ('Off', 'On', 'Initializing'),
  'type': 'enum',
  'value': 0},
 'PwrState-Sts': {'enums': ('Off', 'On'), 'type': 'enum', 'value': 0},
 'Reset-Cmd': {'type': 'int', 'value': 0},
 'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
 'WfmData-RB': {'count': 4000,
  'prec': 4,
  'type': 'float',
  'unit': ['A', 'Ampere'],
  'value': []},
 'WfmData-SP': {'count': 4000,
  'prec': 4,
  'type': 'float',
  'unit': ['A', 'Ampere'],
  'value': []},
 'WfmIndex-Mon': {'type': 'int', 'value': 0}}

class PowerSupplyTest(unittest.TestCase):
    """Tests."""

    def setUp(self):
        """Common setup for all test."""
        thread_patcher = mock.patch('siriuspy.pwrsupply.model._Thread')
        self.addCleanup(thread_patcher.stop)
        self.thread_mock = thread_patcher.start()

        data_patcher = mock.patch('siriuspy.pwrsupply.model._PSData')
        self.addCleanup(data_patcher.stop)
        self.data_mock = data_patcher.start()
        self.data_mock.return_value.propty_database = database

        self.controller = mock.Mock()
        # Set read return value to 'read'
        self.controller.read.return_value = 'read'

        self.ps = PowerSupply(
            psname='SI-Fam:PS-QDA', controller=self.controller)

    def test_read_sp(self):
        """Test read method."""
        self.assertEqual(self.ps.read('Current-SP'), 'read')

    def test_read_cte(self):
        """Test reading a cte."""
        self.assertEqual(len(self.ps.read('IntlkSoftLabels-Cte')), 32)
        self.assertEqual(len(self.ps.read('IntlkHardLabels-Cte')), 32)

    def test_read_mon(self):
        """Test read a mon pv."""
        field = "Current-Mon"
        value = self.ps.read(field)
        self.assertEqual(value, 'read')
        self.controller.read.assert_called_with(field)

    def test_write(self):
        """Test write method."""
        field = 'Current-SP'
        value = 10.9
        self.ps.write(field, value)
        self.controller.write.assert_called_with(field, value)
        self.assertEqual(self.ps.read(field), value)

    def test_write_readable(self):
        """Test an exception is raised when trying to set a read-only field."""
        # with self.assertRaises(KeyError):
        self.assertEqual(self.ps.write('Current-Mon', 10.0), None)

    def _test_set_callback(self):
        """Test set callback is called."""
        pass

    def _test_get_database(self):
        """Test database is returned."""
        pass


if __name__ == "__main__":
    unittest.main()
