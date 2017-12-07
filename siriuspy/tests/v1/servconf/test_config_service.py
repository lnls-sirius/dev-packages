"""Test the configuration service class."""
import unittest
from unittest import mock
import json

from siriuspy.servconf.conf_service import ConfigService

# Dependecis
#   - _config_types (get_config_types, check_value)
#   - _urlopen (read)


class TestConfigService(unittest.TestCase):
    """Test ConfigService."""

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

        self.conf_mock.get_config_types.return_value = ("conf1", "conf2")
        self.conf_mock.check_value.return_value = True
        self.url_mock.return_value.read.return_value = \
            b'{"code": 200, "message": "ok", "response": 1}'
        self.req_mock.return_value = "FakeRequest"

        self.fake_resp = {"code": 200, "message": "ok", "response": 1}
        self.cs = ConfigService()

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


class TestInsertConfigService(unittest.TestCase):
    """Test insert config meets requirements."""

    def setUp(self):
        """Common setup for all tests."""
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
            "name": "FakeName",
            "config_type": "FakeConfigType",
            "value": "FakeValue",
            "discarded": False}
        self.update_config = {
            "name": "FakeName",
            "value": "FakeValue",
            "discarded": False}
        self.fake_url = self.cs._url + ConfigService.CONFIGS_ENDPOINT +\
            "/{}".format(self.fake_config["_id"])

class TestUpdateAndDeleteConfigService(unittest.TestCase):
    """Test update and delete config meets requirements."""

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

    def test_insert_request_creation(self):
        """Test insert_config creates a valid request."""
        # Call insert_config
        self.cs.insert_config(
            self.insert_config["config_type"],
            self.insert_config["name"], self.fake_config["value"])
        # Assert request is created
        self.req_mock.assert_called_once_with(
            url=self.insert_url, method="POST",
            headers={"Content-Type": "application/json"},
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

    def test_update_request_creation(self):
        """Test update_config creates a valid request."""
        # Call update
        self.cs.update_config(self.fake_config)
        # Assert request is created
        self.req_mock.assert_called_once_with(
            url=self.fake_url, method="PUT",
            headers={"Content-Type": "application/json"},
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

    def test_delete_request_creation(self):
        """Test delete_config creates a valid request."""
        # Call update
        self.cs.delete_config(self.fake_config)
        # Assert request is created
        self.req_mock.assert_called_once_with(
            url=self.fake_url, method="PUT",
            headers={"Content-Type": "application/json"},
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

    # find

    # make_req?

if __name__ == "__main__":
    unittest.main()
