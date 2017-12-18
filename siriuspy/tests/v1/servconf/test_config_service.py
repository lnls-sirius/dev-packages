#!/usr/bin/env python-sirius

"""Test the configuration service class."""
import unittest
from unittest import mock
import json
from urllib.error import URLError

from siriuspy.servconf.conf_service import ConfigService
import siriuspy.util as util

# Dependecies
#   - _config_types (get_config_types, check_value)
#   - _urlopen (read)
#   - _Request


class TestConfigService(unittest.TestCase):
    """Test update and delete config meets requirements."""

    api = {
        "CONFIGS_ENDPOINT",
        "get_config_types",
        "get_config",
        "update_config",
        "insert_config",
        "find_configs",
        "find_nr_configs",
        "request_count",
        "request_configs",
        "delete_config",
        "query_db_size",
        "query_db_size_discarded",
        "conv_timestamp",
    }

    def setUp(self):
        """Common setup for all test."""
        # Create Mocks
        conf_patcher = mock.patch(
            'siriuspy.servconf.conf_service._config_types', autospec=True)
        url_patcher = mock.patch(
            'siriuspy.servconf.conf_service._urlopen', autospec=True)
        req_patcher = mock.patch(
            'siriuspy.servconf.conf_service._Request', autospec=True)
        self.addCleanup(conf_patcher.stop)
        self.addCleanup(url_patcher.stop)
        self.addCleanup(req_patcher.stop)
        self.conf_mock = conf_patcher.start()
        self.url_mock = url_patcher.start()
        self.req_mock = req_patcher.start()
        # Mocked values
        self.conf_mock.get_config_types.return_value = ("conf1", "conf2")
        self.conf_mock.check_value.return_value = True
        self.url_mock.return_value.read.return_value = \
            b'{"code": 200, "message": "ok", "response": 1}'
        self.req_mock.return_value = "FakeRequest"
        # Test object
        self.cs = ConfigService()
        # Fake values
        self.fake_resp = {"code": 200, "message": "ok", "response": 1}
        self.fake_config = {
            "_id": "FakeId",
            "config_type": "FakeConfigType",
            "name": "FakeName",
            "value": "FakeValue",
            "discarded": False}
        self.update_config = {
            "name": "FakeName",
            "value": "FakeValue",
            "discarded": False}
        self.insert_config = {
            "config_type": "FakeConfigType",
            "name": "FakeName",
            "value": "FakeValue",
        }
        self.fake_url = self.cs._url + ConfigService.CONFIGS_ENDPOINT +\
            "/{}".format(self.fake_config["_id"])
        self.insert_url = self.cs._url + ConfigService.CONFIGS_ENDPOINT
        self.header = {"Content-Type": "application/json"}
        self.url_error_reponse = {"code": 111, "message": "Connection refused"}
        self.decode_error_reponse = \
            {"code": -1, "message": "JSON decode error"}

    def test_api(self):
        """Test api."""
        valid = util.check_public_interface_namespace(
            ConfigService, TestConfigService.api)
        self.assertTrue(valid)

    def test_get_config_types(self):
        """Test get_config_types."""
        self.assertEqual(ConfigService.get_config_types(), ("conf1", "conf2"))

    def test_get_config(self):
        """Test get_config."""
        resp = self.cs.get_config("FakeConfigType", "FakeConfig")
        fake_url = self.cs._url + ConfigService.CONFIGS_ENDPOINT + \
            '/{}/{}'.format("FakeConfigType", "FakeConfig")
        # Assert request is created
        self.req_mock.assert_called_once_with(url=fake_url, method="GET")
        # Assert request is made
        self.url_mock.assert_called_once_with("FakeRequest")
        self.url_mock.return_value.read.assert_called_once()
        # Assert response
        self.assertEqual(resp, self.fake_resp)

    def test_get_config_response_exceptions(self):
        """Test get_config response exceptions."""
        # Set exception and call get config
        self.url_mock.return_value.read.side_effect = URLError("FakeError")
        resp = self.cs.get_config("FakeConfigType", "FakeConfig")
        self.assertEqual(resp, self.url_error_reponse)
        # Set JSON errpr and call get config
        self.url_mock.return_value.read.side_effect = \
            json.JSONDecodeError("FakeError", "FakeDoc", 0)
        resp = self.cs.get_config("FakeConfigType", "FakeConfig")
        self.assertEqual(resp, self.decode_error_reponse)

    # Insert
    def test_insert_request_creation(self):
        """Test insert_config creates a valid request."""
        # Call insert_config
        self.cs.insert_config(
            self.insert_config["config_type"],
            self.insert_config["name"], self.fake_config["value"])
        # Assert request is created
        self.req_mock.assert_called_once_with(
            url=self.insert_url, method="POST",
            headers=self.header,
            data=json.dumps(self.insert_config).encode())

    def test_insert_url_request(self):
        """Test update_config makes the request."""
        # Call insert
        self.cs.insert_config(
            self.insert_config["config_type"],
            self.insert_config["name"], self.fake_config["value"])
        # Assert request is made
        self.url_mock.assert_called_once_with("FakeRequest")
        self.url_mock.return_value.read.assert_called_once()

    def test_insert_response(self):
        """Test update_config returns valid response."""
        # Call insert
        resp = self.cs.insert_config(
            self.insert_config["config_type"],
            self.insert_config["name"], self.fake_config["value"])
        # Assert response
        self.assertEqual(resp, self.fake_resp)

    def test_insert_value_check(self):
        """Test update_config checks value it is being passed."""
        # Call insert
        self.cs.insert_config(
            self.insert_config["config_type"],
            self.insert_config["name"], self.fake_config["value"])
        # Assert a value check is made
        self.conf_mock.check_value.assert_called_once_with(
            self.fake_config['config_type'], self.fake_config['value'])

    def test_insert_value_check_exception(self):
        """Assert exception is raised when check value fails."""
        self.conf_mock.check_value.return_value = False
        with self.assertRaises(TypeError):
            self.cs.insert_config(
                self.insert_config["config_type"],
                self.insert_config["name"], self.fake_config["value"])

    def test_insert_response_exceptions(self):
        """Test insert_config response exceptions."""
        # Set exception and call get config
        self.url_mock.return_value.read.side_effect = URLError("FakeError")
        resp = self.cs.insert_config(
            self.insert_config["config_type"],
            self.insert_config["name"], self.fake_config["value"])
        self.assertEqual(resp, self.url_error_reponse)
        # Set JSON errpr and call get config
        self.url_mock.return_value.read.side_effect = \
            json.JSONDecodeError("FakeError", "FakeDoc", 0)
        resp = self.cs.insert_config(
            self.insert_config["config_type"],
            self.insert_config["name"], self.fake_config["value"])
        self.assertEqual(resp, self.decode_error_reponse)

    # Update
    def test_update_request_creation(self):
        """Test update_config creates a valid request."""
        # Call update
        self.cs.update_config(self.fake_config)
        # Assert request is created
        self.req_mock.assert_called_once_with(
            url=self.fake_url, method="PUT",
            headers=self.header,
            data=json.dumps(self.update_config).encode())

    def test_update_url_request(self):
        """Test update_config makes the request."""
        # Call update
        self.cs.update_config(self.fake_config)
        # Assert request is made
        self.url_mock.assert_called_once_with("FakeRequest")
        self.url_mock.return_value.read.assert_called_once()

    def test_update_response(self):
        """Test update_config returns valid response."""
        # Call update
        resp = self.cs.update_config(self.fake_config)
        # Assert response
        self.assertEqual(resp, self.fake_resp)

    def test_update_value_check(self):
        """Test update_config checks value it is being passed."""
        # Call update
        self.cs.update_config(self.fake_config)
        # Assert a value check is made
        self.conf_mock.check_value.assert_called_once_with(
            self.fake_config['config_type'], self.fake_config['value'])

    def test_update_value_check_exception(self):
        """Assert exception is raised when check value fails."""
        self.conf_mock.check_value.return_value = False
        with self.assertRaises(TypeError):
            self.cs.update_config(self.fake_config)

    def test_update_input_type_exception(self):
        """Assert exception is raised when the input is not a dict."""
        self.assertRaises(ValueError, self.cs.update_config, obj_dict=1)
        self.assertRaises(ValueError, self.cs.update_config, obj_dict=[1, 2])
        self.assertRaises(ValueError, self.cs.update_config, obj_dict="String")

    def test_update_response_exceptions(self):
        """Test update_config response exceptions."""
        # Set exception and call get config
        self.url_mock.return_value.read.side_effect = URLError("FakeError")
        resp = self.cs.update_config(self.fake_config)
        self.assertEqual(resp, self.url_error_reponse)
        # Set JSON errpr and call get config
        self.url_mock.return_value.read.side_effect = \
            json.JSONDecodeError("FakeError", "FakeDoc", 0)
        resp = self.cs.update_config(self.fake_config)
        self.assertEqual(resp, self.decode_error_reponse)

    # Delete
    def test_delete_request_creation(self):
        """Test delete_config creates a valid request."""
        # Call update
        self.cs.delete_config(self.fake_config)
        # Assert request is created
        self.req_mock.assert_called_once_with(
            url=self.fake_url, method="PUT",
            headers=self.header,
            data=json.dumps({"discarded": True}).encode())

    def test_delete_url_request(self):
        """Test update_config makes the request."""
        # Call update
        self.cs.delete_config(self.fake_config)
        # Assert request is made
        self.url_mock.assert_called_once_with("FakeRequest")
        self.url_mock.return_value.read.assert_called_once()

    def test_delete_response(self):
        """Test update_config returns valid response."""
        # Call update
        resp = self.cs.delete_config(self.fake_config)
        # Assert response
        self.assertEqual(resp, self.fake_resp)

    def test_delete_response_exceptions(self):
        """Test delete_config response exceptions."""
        # Set exception and call get config
        self.url_mock.return_value.read.side_effect = URLError("FakeError")
        resp = self.cs.delete_config(self.fake_config)
        self.assertEqual(resp, self.url_error_reponse)
        # Set JSON errpr and call get config
        self.url_mock.return_value.read.side_effect = \
            json.JSONDecodeError("FakeError", "FakeDoc", 0)
        resp = self.cs.delete_config(self.fake_config)
        self.assertEqual(resp, self.decode_error_reponse)

    # Find/Request/Count
    def test_find_config_request_creation_no_params(self):
        """Test find_config passing no parameters."""
        # Call with no parameters
        self.cs.find_configs()
        # Assert request created
        self.req_mock.assert_called_once_with(
            url=self.insert_url, method="GET", headers=self.header,
            data=json.dumps({"discarded": False}).encode())

    def test_find_config_request_creation_empty_filter(self):
        """Test find_config with empty filter."""
        # Call with no filters
        self.cs.find_configs(discarded=None)
        # Assert request created
        self.req_mock.assert_called_with(
            url=self.insert_url, method="GET")

    def test_find_config_request_creation_with_params(self):
        """Test find_config with params."""
        # Call with filters
        self.cs.find_configs(
            config_type="FakeConfigType", name="FakeName", begin=1, end=10)
        # Assert request created
        self.req_mock.assert_called_with(
            url=self.insert_url, method="GET", headers=self.header,
            data=json.dumps({
                "config_type": "FakeConfigType", "name": "FakeName",
                "created": {"$gte": 1, "$lte": 10}, "discarded": False}
            ).encode())

    def test_find_config_url_request(self):
        """Test update_config makes the request."""
        # Call update
        self.cs.find_configs()
        # Assert request is made
        self.url_mock.assert_called_once_with("FakeRequest")
        self.url_mock.return_value.read.assert_called_once()

    def test_find_config_response(self):
        """Test update_config returns valid response."""
        # Call update
        resp = self.cs.find_configs()
        # Assert response
        self.assertEqual(resp, self.fake_resp)

    def test_request_config_input_type_exception(self):
        """Assert exception is raised when the input is not a dict."""
        self.assertRaises(ValueError, self.cs.request_configs, find_dict=1)
        self.assertRaises(
            ValueError, self.cs.request_configs, find_dict=[1, 2])
        self.assertRaises(
            ValueError, self.cs.request_configs, find_dict="String")

    def test_find_config_response_exceptions(self):
        """Test find_configs response exceptions."""
        # Set exception and call get config
        self.url_mock.return_value.read.side_effect = URLError("FakeError")
        resp = self.cs.find_configs()
        self.assertEqual(resp, self.url_error_reponse)
        # Set JSON errpr and call get config
        self.url_mock.return_value.read.side_effect = \
            json.JSONDecodeError("FakeError", "FakeDoc", 0)
        resp = self.cs.find_configs()
        self.assertEqual(resp, self.decode_error_reponse)

    # Query db size
    def test_query_db_size_request_creation(self):
        """Test query_db_size request creation."""
        # Call method
        self.cs.query_db_size()
        # Assert a request object was created
        self.req_mock.assert_called_once_with(
            url=self.insert_url + '/stats/size', method="GET")

    def test_query_db_size_response(self):
        """Test query_db_size issue a url request."""
        # Call method
        resp = self.cs.query_db_size()
        # Assert response
        self.assertEqual(resp, self.fake_resp)

    def test_query_db_size_response_exceptions(self):
        """Test find_configs response exceptions."""
        # Set exception and call get config
        self.url_mock.return_value.read.side_effect = URLError("FakeError")
        resp = self.cs.query_db_size()
        self.assertEqual(resp, self.url_error_reponse)
        # Set JSON errpr and call get config
        self.url_mock.return_value.read.side_effect = \
            json.JSONDecodeError("FakeError", "FakeDoc", 0)
        resp = self.cs.query_db_size()
        self.assertEqual(resp, self.decode_error_reponse)


class TestConfigServiceConTimestamp(unittest.TestCase):
    """Test response error handling."""

    def test_conv_timestamp(self):
        """Test timestamp conversion."""
        cs = ConfigService()
        samples = {
            ("Dec 11, 2017", 1512957600.0),
            ("12/11/2017", 1512957600.0),
            ("2017/12/11", 1512957600.0),
            ("2017-12-11", 1512957600.0),
            ("Dec 11 2017 14:00:00", 1513008000.0),
            ("12/11/2017 14:00:00", 1513008000.0),
            ("2017/12/11 14:00:00", 1513008000.0),
            ("2017-12-11 14:00:00", 1513008000.0),
            ("2017-12-11T14:00:00", 1513008000.0),
            ("2017-12-11 14:00:00+01:00", 1512997200.0),
            ("2017-12-11T14:00:00+01:00", 1512997200.0),
            ("2017-12-11T14:00:00.45", 1513008000.45),
        }

        for sample in samples:
            date_string = sample[0]
            timestamp = sample[1]
            self.assertEqual(cs.conv_timestamp(date_string), timestamp)


if __name__ == "__main__":
    unittest.main()
