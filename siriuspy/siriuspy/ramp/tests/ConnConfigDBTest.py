#!/usr/local/bin/python-sirius
"""Test ConnConfigDB class."""
import unittest
from unittest import mock

from siriuspy.ramp.conn import ConnConfigDB
from siriuspy.ramp.wfmset import WfmSet
# will be mocked
from siriuspy.servconf.conf_service import ConfigService
from siriuspy.search import MASearch
import siriuspy.servconf.conf_types as _config_types


class ConnConfigDBCheckType(unittest.TestCase):
    """Test types used by ConnConfigDB."""

    def test_rmp_bo_pvs_type(self):
        """Test if the set of pvs is correct."""
        devices = MASearch.get_manames({"section": "BO", "discipline": "MA"})
        pvs = [device + ":WfmData-SP" for device in devices]
        obj = {}
        ref_array = [0.0 for _ in range(4000)]
        for pv in pvs:
            obj[pv] = ref_array
        self.assertTrue(_config_types.check_value("rmp_bo_ps", obj))


class ConnConfigDBInsertTest(unittest.TestCase):
    """Test configuration insertion."""

    def setUp(self):
        """Setup test object."""
        self.db = ConnConfigDB()
        self.db_serv = self.db._conn

        self.expected_insert_value = {}
        devices = MASearch.get_manames({"section": "BO", "discipline": "MA"})

        self.wfmset = WfmSet("BO-Fam:MA-B")
        value = [1.0 for _ in range(4000)]
        for device in devices:
            self.wfmset.set_wfm_current(device)
            self.expected_insert_value[device + ":WfmData-SP"] = value

    @mock.patch.object(ConfigService, "insert_config", autospec=True)
    def test_insert_config(self, mock_db_serv):
        """Test insertion of a configuraiton based on a WfmSet."""
        config_name = "test"
        self.db.insert_config(wfmset=self.wfmset, name=config_name)
        config_type = "rmp_bo_ps"
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

        devices = MASearch.get_manames({"section": "BO", "discipline": "MA"})
        self.retrieved_value = {}
        value = [0.0 for _ in range(4000)]
        for i, device in enumerate(devices):
            self.retrieved_value[device + ":WfmData-SP"] = value

        self.expected_obj = {
            "code": 200,
            "message": "ok",
            "result": {
                "_id": -1,
                "config_type": "rmp_bo_ps",
                "name": "test",
                "created": -1,
                "modified": [-1, ],
                "value": self.retrieved_value}
        }

    @mock.patch.object(ConfigService, "get_config", autospec=True)
    def test_get_config_set_values(self, mock_get):
        """Test get config set wfmset value correctly."""
        config_type = "rmp_bo_ps"
        name = "test"
        mock_get.return_value = self.expected_obj
        self.db.get_config(self.wfmset, "test")
        # Assert the service function was called with right params
        mock_get.assert_called_with(
            self.db_serv, config_type=config_type, name=name)
        # Assert wfm object was set with right values
        for pv, value in self.retrieved_value.items():
            ma = ":".join(pv.split(":")[:-1])
            self.assertEqual(self.wfmset.get_wfm_current(ma), value)


if __name__ == "__main__":
    unittest.main()
