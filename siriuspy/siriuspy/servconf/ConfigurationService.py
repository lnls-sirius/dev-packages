
"""Define a class to communicate with configuration database API."""
import json
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError

logging.basicConfig(level=logging.DEBUG)


class ConfigurationService:
    """Perform CRUD operation on configuration database."""

    def __init__(self, host):
        """Class constructor.

        Parameters:
            - host: configuration service host address
        """
        self._host = host
        self._result = None

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

    # Pv Configuration
    def get_pv_configurations(self, data=None):
        """Return all pv configurations."""
        url = "http://{}/pvs".format(self._host)
        if data is None:
            request = Request(url=url, method="GET")
        else:
            request = Request(url=url, method="GET",
                              headers={"Content-Type": "application/json"},
                              data=json.dumps(data).encode())
        return self._make_request(request)

    def insert_pv_configuration(self, name, config_type, values=[]):
        """Insert new PV convfiguration."""
        url = "http://{}/pvs".format(self._host)
        data = {"name": name, "config_type": config_type,
                "values": values}
        request = Request(url=url, method="POST",
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data).encode())
        return self._make_request(request)

    def get_pv_configuration_by_id(self, id):
        """Return a pv configuration."""
        url = "http://{}/pvs/{}".format(self._host, id)
        request = Request(url=url, method="GET")
        return self._make_request(request)

    def update_pv_configuration(self, id, name=None, config_type=None):
        """Update a PV configuration.

        The data can be passed as a dict in `data` or as parameters.
        """
        url = "http://{}/pvs/{}".format(self._host, id)
        data = {}
        if name is not None:
            data["name"] = name
        if config_type is not None:
            data["config_type"] = config_type
        request = Request(url=url, method="PUT",
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data).encode())
        return self._make_request(request)

    def delete_pv_configuration(self, id):
        """Delete pv configuration."""
        url = "http://{}/pvs/{}".format(self._host, id)
        request = Request(url=url, method="DELETE")
        return self._make_request(request)

    def insert_pv_configuration_item(self, id, pv_name, value):
        """Insert new pv into configuration."""
        url = "http://{}/pvs/{}/values".format(self._host, id)
        # Build data
        data = {}
        data["pv_name"] = pv_name
        # data["pv_type"] = str(type(value))
        data["value"] = value
        # Build request
        request = Request(url=url, method="POST",
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data).encode())
        return self._make_request(request)

    def insert_pv_configuration_items(self, id, data):
        """Insert more than one pv into configuration."""
        url = "http://{}/pvs/{}/values".format(self._host, id)
        request = Request(url=url, method="POST",
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data).encode())
        return self._make_request(request)

    def update_pv_configuration_item(self, id, pv_name, value=None):
        """Update a pv configuration item."""
        url = "http://{}/pvs/{}/values/{}".format(self._host, id, pv_name)
        data = {}
        if value is not None:
            data["value"] = value
        request = Request(url=url, method="PUT",
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data).encode())
        return self._make_request(request)

    def delete_pv_configuration_item(self, id, pv_name):
        """Delete a pv configuration value document."""
        url = "http://{}/pvs/{}/values/{}".format(self._host, id, pv_name)
        request = Request(url=url, method="DELETE")
        return self._make_request(request)

    # List collection
    def get_all_lists(self, data=None):
        """Get all lists."""
        url = "http://{}/lists".format(self._host)
        if data is None:
            request = Request(url=url, method="GET")
        else:
            request = Request(url=url, method="GET",
                              headers={"Content-Type": "application/json"},
                              data=json.dumps(data).encode())
        return self._make_request(request)

    def insert_list(self, name, config_type, value=None):
        """Insert a new list.

        Value must me a list.
        """
        url = "http://{}/lists".format(self._host)
        data = {"name": name, "config_type": config_type}
        if value is not None:
            data["value"] = value
        request = Request(url=url, method="POST",
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data).encode())
        return self._make_request(request)

    def get_list_by_name(self, name):
        """Get lists by name."""
        url = "http://{}/lists/{}".format(self._host, name)
        request = Request(url=url, method="GET")
        return self._make_request(request)

    def update_list(self, name, new_name=None, value=None):
        """Update a list."""
        url = "http://{}/lists/{}".format(self._host, name)
        data = {}
        if new_name is not None:
            data["name"] = new_name
        if value is not None:
            if type(value) is not list:
                raise AttributeError("`value` attribute must be a list")
            data["value"] = value
        request = Request(url=url, method="PUT",
                          headers={"Content-Type": "application/json"},
                          data=json.dumps(data).encode())
        return self._make_request(request)

    def delete_list(self, name):
        """Delete a list."""
        url = "http://{}/lists/{}".format(self._host, name)
        request = Request(url=url, method="DELETE")
        return self._make_request(request)
