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

    def setUp(self):
        """Common setup for all test.

        Mock the search class PSSearch and the function to get the ps
        database.
        """
        # Create mock
        search_patcher = mock.patch(
            'siriuspy.pwrsupply.data._PSSearch', autospec=True)
        db_patcher = mock.patch(
            'siriuspy.pwrsupply.data._get_ps_propty_database', autospec=True)
        self.addCleanup(search_patcher.stop)
        self.addCleanup(db_patcher.stop)
        self.search_mock = search_patcher.start()
        self.db_mock = db_patcher.start()
        # Fake properties
        self.properties = {
            'psname': 'Fake-SI-Fam:PS-B1B2-1',
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
        self.search_mock.get_psnames.return_value = [self.properties['psname']]
        self.search_mock.check_psname_ispulsed.return_value = False
        self.search_mock.conv_psname_2_pstype.return_value = \
            self.properties['pstype']
        self.search_mock.conv_pstype_2_polarity.return_value = \
            self.properties['polarity']
        self.search_mock.conv_pstype_2_magfunc.return_value = \
            self.properties['magfunc']
        self.search_mock.conv_pstype_2_splims.return_value = \
            self.properties['splims']
        self.search_mock.get_splims_unit.return_value = \
            self.properties['splims_unit']
        self.search_mock.conv_psname_2_excdata.return_value = \
            self.properties['excdata']
        self.search_mock.conv_psname_2_psmodel.return_value = 'FBP'

        self.db_mock.return_value = self.db

        # Object to be tested
        self.data = PSData(self.properties['psname'])

    def test_setup(self):
        """Test if all calls to get PSData properties are made."""
        self.search_mock.get_psnames.assert_called()
        self.search_mock.conv_psname_2_pstype.assert_called_with(
            self.properties['psname'])
        self.search_mock.conv_pstype_2_polarity.assert_called_with(
            self.properties['pstype'])
        self.search_mock.conv_pstype_2_magfunc.assert_called_with(
            self.properties['pstype'])
        self.search_mock.conv_pstype_2_splims.assert_called_with(
            self.properties['pstype'])
        self.search_mock.get_splims_unit.assert_called()
        self.search_mock.conv_psname_2_excdata.assert_called_with(
            self.properties['psname'])

        self.db_mock.assert_called_with(self.properties['pstype'])

    def test_psname(self):
        """Test wether psname property is set correctly."""
        self.assertEqual(self.data.psname, self.properties['psname'])

    def test_pstype(self):
        """Test whether pstype property is set correctly."""
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


class TestPSDataDb(unittest.TestCase):
    """Test right database is called."""

    def setUp(self):
        """Common setup for all tests."""
        # Create mock
        search_patcher = mock.patch(
            'siriuspy.pwrsupply.data._PSSearch', autospec=True)
        ps_db_patcher = mock.patch(
            'siriuspy.pwrsupply.data._get_ps_propty_database', autospec=True)
        pu_db_patcher = mock.patch(
            'siriuspy.pwrsupply.data._get_pu_propty_database', autospec=True)
        self.addCleanup(search_patcher.stop)
        self.addCleanup(ps_db_patcher.stop)
        self.addCleanup(pu_db_patcher.stop)
        self.search_mock = search_patcher.start()
        self.ps_db_mock = ps_db_patcher.start()
        self.pu_db_mock = pu_db_patcher.start()

        self.psname = "Fake-SI-Fam:PS-QDA"
        self.puname = "Fake-SI-Fam:PU-QDA"
        self.pstype = "FakeType"

        self.search_mock.get_psnames.return_value = [self.psname, self.puname]
        self.search_mock.conv_psname_2_pstype.return_value = self.pstype
        self.search_mock.conv_psname_2_psmodel.return_value = 'FBP'

    def test_ps_db(self):
        """Test ps db is called when a ps is passed."""
        self.search_mock.check_psname_ispulsed.return_value = False
        PSData(self.psname)
        self.pu_db_mock.assert_not_called()
        self.ps_db_mock.assert_called_once_with(pstype=self.pstype)

    def test_pu_db(self):
        """Test pu db is called when a pu is passed."""
        self.search_mock.check_psname_ispulsed.return_value = True
        PSData(self.psname)
        self.pu_db_mock.assert_called_once_with(pstype=self.pstype)
        self.ps_db_mock.assert_not_called()


class TestPSDataException(unittest.TestCase):
    """Test PSDAta fails when PS is not found."""

    @mock.patch('siriuspy.pwrsupply.data._PSSearch', autospec=True)
    def test_init(self, mock_search):
        """Test exception is raised when unknown pv is passed to PSData."""
        mock_search.get_psnames.return_value = ["RealPS1", "RealPS2"]
        with self.assertRaises(ValueError):
            PSData("NonExistentPS")


if __name__ == "__main__":
    unittest.main()
