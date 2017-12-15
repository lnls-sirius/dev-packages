#!/usr/bin/env python-sirius
"""Test public API of PowerSupply/Magnet class."""
import unittest
from unittest import mock

from siriuspy.powersupply.model import PowerSupply


class PowerSupplyTest(unittest.TestCase):
    """Tests."""

    @mock.patch.object(PowerSupply, '_get_base_db', autospec=True)
    def setUp(self, mock_db):
        """Common setup for all test."""
        self.db = {
            "attr1": {"value": {'a': 'a', 'b': 'b', 'c': 'c'}},
            "attr2": {"value": 10},
            "attr3": {"value": [1, 2, 3, 4, 5]},
            "attr4": {"value": 'string'},
            "attr5": {"value": 0}
        }
        mock_db.return_value = self.db

        def read_db(attr):
            return self.db[attr]

        self.controller = mock.Mock()
        self.controller.read.side_effect = read_db
        self.ps = PowerSupply(('FakePV', ), controller=self.controller)

    def test_write(self):
        """Test write method."""
        self.ps.write("attr2", 100)
        self.assertEqual(
            self.controller.write.call_args_list, [mock.call('attr2', 100)])

    def test_read(self):
        """Test read method."""
        r = self.ps.read('attr2')
        self.assertEqual(
            self.controller.read.call_args_list, [mock.call('attr2')])
        self.assertEqual(r, self.db['attr2'])

    def test_set_callback(self):
        """Test set callback is called."""
        def dummy_callback(x):
            print(x)
        # Assert callback were set
        self.ps.add_callback(dummy_callback)
        self.assertEqual(
            self.controller.add_callback.call_args_list,
            [mock.call(dummy_callback)])

    def test_get_database(self):
        """Test database is returned."""
        db = self.ps.get_database()
        calls = []
        for field in self.db:
            calls.append(mock.call(field))
        self.assertEqual(self.controller.read.call_args_list, calls)
        self.assertEqual(db, self.db)


if __name__ == "__main__":
    unittest.main()
