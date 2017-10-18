
"""Define a class to communicate with configuration database API."""
import json
import logging
import os
from urllib.request import Request, urlopen
from urllib.error import URLError

logging.basicConfig(level=logging.DEBUG)


class ConfigurationService:
    """Perform CRUD operation on configuration database."""

    CONFIGS_ENDPOINT = '/configs'

    def __init__(self, url=None):
        """Class constructor.

        Parameters:
            - url: configuration service host address
        """
        if url is None:
            self._url = os.getenv("SIRIUS_URL_CONFIGDB")
        else:
            self._url = url

        logging.info("HTTP request will be made to {}".format(self._url))

    # def get_result(self):
    #     """Get result from last operation."""
    #     return self._result

    def _make_request(self, request):
        try:
            response = json.loads(urlopen(request).read().decode("utf-8"))
        except URLError as e:
            return {"code": 111, "message": "Connection refused"}
        except json.JSONDecodeError as e:
            return {"code": -1, "message": "JSON decode error"}
        except Exception as e:
            logging.critical("{}".format(e))
        else:
            return response

    # Configs collection
    def get_all_configs(self, find_params=None):
        """Get all configs or find config that meet `find_params`."""
        url = self._url + self.CONFIGS_ENDPOINT
        if find_params is None:
            request = Request(url=url, method="GET")
        else:
            if type(find_params) is not dict:
                raise AttributeError("`find_params` must be a dict")
            request = Request(url=url, method="GET",
                              headers={"Content-Type": "application/json"},
                              data=json.dumps(find_params).encode())
        return self._make_request(request)

    def insert_config(self, name, config_type, value):
        """Insert a new list.

        Value must me a list.
        """
        url = self._url + self.CONFIGS_ENDPOINT
        data = {"name": name, "config_type": config_type, "value": value}
        request = Request(url=url, method="POST",
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data).encode())
        return self._make_request(request)

    def get_config(self, name, config_type):
        """Get lists by name and config."""
        url_params = "/{}/{}".format(config_type, name)
        url = self._url + self.CONFIGS_ENDPOINT + url_params
        request = Request(url=url, method="GET")
        return self._make_request(request)

    def update_config(self, name, config_type, update_params):
        """Update a list.

        `update_params` must have at least on of the following keys
        to update the config:
            - name, config_type or value
        """
        url_params = "/{}/{}".format(config_type, name)
        url = self._url + self.CONFIGS_ENDPOINT + url_params
        if type(update_params) is not dict:
            raise AttributeError("`update_params` must be dict")
        request = Request(url=url, method="PUT",
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(update_params).encode())
        return self._make_request(request)

    def delete_config(self, name, config_type):
        """Delete a config."""
        url_params = "/{}/{}".format(config_type, name)
        url = self._url + self.CONFIGS_ENDPOINT + url_params
        request = Request(url=url, method="DELETE")
        return self._make_request(request)

    # Pv Configuration
    # def get_pv_configurations(self, data=None):
    #     """Return all pv configurations."""
    #     url = "http://{}/pvs".format(self._host)
    #     if data is None:
    #         request = Request(url=url, method="GET")
    #     else:
    #         request = Request(url=url, method="GET",
    #                           headers={"Content-Type": "application/json"},
    #                           data=json.dumps(data).encode())
    #     return self._make_request(request)
    #
    # def insert_pv_configuration(self, name, config_type, values=[]):
    #     """Insert new PV convfiguration."""
    #     url = "http://{}/pvs".format(self._host)
    #     data = {"name": name, "config_type": config_type,
    #             "values": values}
    #     request = Request(url=url, method="POST",
    #                       headers={"Content-Type": "application/json"},
    #                       data=json.dumps(data).encode())
    #     return self._make_request(request)
    #
    # def get_pv_configuration_by_id(self, id):
    #     """Return a pv configuration."""
    #     url = "http://{}/pvs/{}".format(self._host, id)
    #     request = Request(url=url, method="GET")
    #     return self._make_request(request)
    #
    # def update_pv_configuration(self, id, name=None, config_type=None):
    #     """Update a PV configuration.
    #
    #     The data can be passed as a dict in `data` or as parameters.
    #     """
    #     url = "http://{}/pvs/{}".format(self._host, id)
    #     data = {}
    #     if name is not None:
    #         data["name"] = name
    #     if config_type is not None:
    #         data["config_type"] = config_type
    #     request = Request(url=url, method="PUT",
    #                       headers={"Content-Type": "application/json"},
    #                       data=json.dumps(data).encode())
    #     return self._make_request(request)
    #
    # def delete_pv_configuration(self, id):
    #     """Delete pv configuration."""
    #     url = "http://{}/pvs/{}".format(self._host, id)
    #     request = Request(url=url, method="DELETE")
    #     return self._make_request(request)
    #
    # def insert_pv_configuration_item(self, id, pv_name, value):
    #     """Insert new pv into configuration."""
    #     url = "http://{}/pvs/{}/values".format(self._host, id)
    #     # Build data
    #     data = {}
    #     data["pv_name"] = pv_name
    #     # data["pv_type"] = str(type(value))
    #     data["value"] = value
    #     # Build request
    #     request = Request(url=url, method="POST",
    #                       headers={"Content-Type": "application/json"},
    #                       data=json.dumps(data).encode())
    #     return self._make_request(request)
    #
    # def insert_pv_configuration_items(self, id, data):
    #     """Insert more than one pv into configuration."""
    #     url = "http://{}/pvs/{}/values".format(self._host, id)
    #     request = Request(url=url, method="POST",
    #                       headers={"Content-Type": "application/json"},
    #                       data=json.dumps(data).encode())
    #     return self._make_request(request)
    #
    # def update_pv_configuration_item(self, id, pv_name, value=None):
    #     """Update a pv configuration item."""
    #     url = "http://{}/pvs/{}/values/{}".format(self._host, id, pv_name)
    #     data = {}
    #     if value is not None:
    #         data["value"] = value
    #     request = Request(url=url, method="PUT",
    #                       headers={"Content-Type": "application/json"},
    #                       data=json.dumps(data).encode())
    #     return self._make_request(request)
    #
    # def delete_pv_configuration_item(self, id, pv_name):
    #     """Delete a pv configuration value document."""
    #     url = "http://{}/pvs/{}/values/{}".format(self._host, id, pv_name)
    #     request = Request(url=url, method="DELETE")
    #     return self._make_request(request)
