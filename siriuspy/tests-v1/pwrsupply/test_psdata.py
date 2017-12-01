#!/usr/bin/env python-sirius

"""Test PSData class.

Test PSData properties:
    psname
    pstype
    polarity
    magfunc
    splims
    splims_unit
    splims_labels
    propty_database
    excdata
"""
import unittest
from unittest import mock

from siriuspy.pwrsupply.data import PSData


class TestPSDataProperties(unittest.TestCase):
    """Test PSData properties are set correctly."""

    @mock.patch('siriuspy.pwrsupply.data._get_ps_propty_database',
                autospec=True)
    @mock.patch('siriuspy.pwrsupply.data._PSSearch', autospec=True)
    def setUp(self, mock_search, mock_db):
        """Common setup for all test.

        Mock the search class PSSearch and the function to get the ps
        database.
        """
        # Fake properties
        self.properties = {
            'psname': 'FakePS',
            'pstype': 'FakePSType',
            'polarity': 'FakePSPolarity',
            'magfunc': 'FakePSMagFunc',
            'splims': {'lolo': 0, 'hihi': 1000},
            'splims_unit': 'FakePSUnit',
            'excdata': 'FakePSExcData'}
        # Fake db
        self.db = {
            'FakeField': 0,
            'FakeField2': {'FakeInnerField1': 'x', 'FakeInnerField2': 10},
            'FakeField3': "string"}

        # Set functions return value
        mock_search.get_psnames.return_value = [self.properties['psname']]
        mock_search.conv_psname_2_pstype.return_value = \
            self.properties['pstype']
        mock_search.conv_pstype_2_polarity.return_value = \
            self.properties['polarity']
        mock_search.conv_pstype_2_magfunc.return_value = \
            self.properties['magfunc']
        mock_search.conv_pstype_2_splims.return_value = \
            self.properties['splims']
        mock_search.get_splims_unit.return_value = \
            self.properties['splims_unit']
        mock_search.conv_psname_2_excdata.return_value = \
            self.properties['excdata']

        mock_db.return_value = self.db

        # Object to be tested
        self.data = PSData(self.properties['psname'])
        self.mock_search = mock_search
        self.mock_db = mock_db

    def test_setup(self):
        """Test if all calls to get PSData properties are made."""
        self.mock_search.get_psnames.assert_called()
        self.mock_search.conv_psname_2_pstype.assert_called_with(
            self.properties['psname'])
        self.mock_search.conv_pstype_2_polarity.assert_called_with(
            self.properties['pstype'])
        self.mock_search.conv_pstype_2_magfunc.assert_called_with(
            self.properties['pstype'])
        self.mock_search.conv_pstype_2_splims.assert_called_with(
            self.properties['pstype'])
        self.mock_search.get_splims_unit.assert_called()
        self.mock_search.conv_psname_2_excdata.assert_called_with(
            self.properties['psname'])

        self.mock_db.assert_called_with(self.properties['pstype'])

    def test_psname(self):
        """Test wether psname property is set correctly."""
        self.assertEqual(self.data.psname, self.properties['psname'])

    def test_pstype(self):
        """Test wether pstype property is set correctly."""
        self.assertEqual(self.data.pstype, self.properties['pstype'])

    def test_polarity(self):
        """Test wether polarity is set correctly."""
        self.assertEqual(self.data.polarity, self.properties['polarity'])

    def test_magfunc(self):
        """Test wether magfunc is set correctly."""
        self.assertEqual(self.data.magfunc, self.properties['magfunc'])

    def test_splims(self):
        """Test wether splims is set correctly."""
        self.assertEqual(self.data.splims, self.properties['splims'])

    def test_splims_unit(self):
        """Test wether splims_unit is set correctly."""
        self.assertEqual(self.data.splims_unit, self.properties['splims_unit'])

    def test_splims_labels(self):
        """Test wether splims_labels is set correctly."""
        self.assertEqual(
            self.data.splims_labels, sorted(self.properties['splims']))

    def test_excdata(self):
        """Test wether splims_excdata is set correctly."""
        self.assertEqual(self.data.excdata, self.properties['excdata'])

    def test_propty_database(self):
        """Test wether the database is set correctly."""
        self.assertEqual(self.data.propty_database, self.db)


class TestPSDataException(unittest.TestCase):
    """Test PSDAta failes when PS is not found."""

    @mock.patch('siriuspy.pwrsupply.data._PSSearch', autospec=True)
    def test_init(self, mock_search):
        """Test exception is risen when unknown pv is passed to PSData."""
        mock_search.get_psnames.return_value = ["RealPS1", "RealPS2"]
        with self.assertRaises(ValueError):
            PSData("NonExistentPS")


if __name__ == "__main__":
    unittest.main()
