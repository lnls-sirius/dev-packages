#!/usr/local/bin/python-sirius
"""Test ConnConfigDB class."""
import unittest
from unittest import mock

from siriuspy.ramp.conn import ConnConfigDB
from siriuspy.ramp.wfmset import WfmSet
# will be mocked
from siriuspy.servconf.conf_service import ConfigService


class ConnConfigDBInsertTest(unittest.TestCase):
    """Test configuration insertion."""

    def setUp(self):
        """Setup test object."""
        self.db = ConnConfigDB()
        self.db_serv = self.db._conn

        self.wfmset = WfmSet("BO-Fam:MA-B")
        self.wfmset.set_wfm_current("BO-Fam:MA-QD")
        self.wfmset.set_wfm_current("BO-Fam:MA-QF")
        self.wfmset.set_wfm_current("BO-Fam:MA-SD")
        self.wfmset.set_wfm_current("BO-Fam:MA-SF")

        self.expected_insert_value = {
            "BO-Fam:MA-B:WfmData-SP":
                self.wfmset.get_wfm_current("BO-Fam:MA-B"),
            "BO-Fam:MA-QD:WfmData-SP":
                self.wfmset.get_wfm_current("BO-Fam:MA-QD"),
            "BO-Fam:MA-QF:WfmData-SP":
                self.wfmset.get_wfm_current("BO-Fam:MA-QF"),
            "BO-Fam:MA-SD:WfmData-SP":
                self.wfmset.get_wfm_current("BO-Fam:MA-SD"),
            "BO-Fam:MA-SF:WfmData-SP":
                self.wfmset.get_wfm_current("BO-Fam:MA-SF")
        }

    @mock.patch.object(ConfigService, "insert_config", autospec=True)
    def test_insert_config(self, mock_db_serv):
        """Test insertion of a configuraiton based on a WfmSet."""
        config_name = "test"
        self.db.insert_config(wfmset=self.wfmset, name=config_name)
        config_type = "bo_ramp_ps"
        mock_db_serv.assert_called_with(
            self.db_serv, config_type=config_type, name=config_name,
            value=self.expected_insert_value)


class ConnConfigDBRetrieveTest(unittest.TestCase):
    """Test wfmset configuration retrieval."""

    def setUp(self):
        """Setup test object."""
        self.db = ConnConfigDB()
        self.db_serv = self.db._conn

        self.wfmset = WfmSet("BO-Fam:MA-B")

        self.retrieved_value = {
            "BO-Fam:MA-B:WfmData-SP": list(range(4000)),
            "BO-Fam:MA-QD:WfmData-SP": list(range(4000)),
            "BO-Fam:MA-QF:WfmData-SP": list(range(4000)),
            "BO-Fam:MA-SD:WfmData-SP": list(range(4000)),
            "BO-Fam:MA-SF:WfmData-SP": list(range(4000))
        }

        self.expected_obj = {
            "code": 200,
            "message": "ok",
            "result": {
                "_id": -1,
                "config_type": "bo_ramp_ps",
                "name": "test",
                "created": -1,
                "modified": [-1, ],
                "value": self.retrieved_value}
        }

    @mock.patch.object(ConfigService, "get_config", autospec=True)
    def test_get_config_retrieve_values(self, mock_get):
        """Test get config retrieve values."""
        mock_get.return_value = self.expected_obj
        config_type = "bo_ramp_ps"
        name = "test"

        self.db.get_config(self.wfmset, name)
        # Assert the service function was called with right params
        mock_get.assert_called_with(
            self.db_serv, config_type=config_type, name=name)

    @mock.patch.object(ConfigService, "get_config", autospec=True)
    def test_get_config_set_values(self, mock_get):
        """Test get config set wfmset value correctly."""
        mock_get.return_value = self.expected_obj
        self.db.get_config(self.wfmset, "test")
        # Assert wfm object was set with right values
        for pv, value in self.retrieved_value.items():
            ma = ":".join(pv.split(":")[:-1])
            self.assertEqual(self.wfmset.get_wfm_current(ma), value)


if __name__ == "__main__":
    unittest.main()
