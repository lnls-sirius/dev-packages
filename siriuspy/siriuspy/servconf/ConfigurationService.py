
"""Define a class to communicate with configuration database API."""
import copy as _copy
import json as _json
import logging as _logging
import siriuspy.envars as _envars
from urllib.request import Request as _Request
from urllib.request import urlopen as _urlopen
from urllib.error import URLError as _URLError
import siriuspy.servconf.ConfigType as _ConfigType

_logging.basicConfig(level=_logging.WARNING)


class ConfigurationService:
    """Perform CRUD operation on configuration database."""

    CONFIGS_ENDPOINT = '/configs'

    def __init__(self, url=None):
        """Class constructor.

        Parameters
        ----------
        url : str | None
            Configuration service host address. For default 'None' value
            the URL defined in siripy.envars is used.
        """
        if url is None:
            self._url = _envars.server_url_configdb
        else:
            self._url = url
        _logging.info("HTTP request will be made to {}".format(self._url))

    @staticmethod
    def get_config_types():
        """Get all configuration types."""
        return _ConfigType.get_config_types()

    def get_config(self, config_type, name):
        """Get lists by name and config."""
        url_params = "/{}/{}".format(config_type, name)
        url = self._url + self.CONFIGS_ENDPOINT + url_params
        request = _Request(url=url, method="GET")
        return self._make_request(request)

    def update_config(self, obj_dict, new_name=None):
        """Update an existing configuration."""
        if type(obj_dict) is not dict:
            raise AttributeError('"obj_dict" is not a dictionary')
        obj_dict = _copy.deepcopy(obj_dict)
        config_type = obj_dict['config_type']
        name = obj_dict['name']
        if new_name is not None:
            obj_dict['name'] = new_name
        if not _ConfigType.check_value(config_type, obj_dict['value']):
            raise TypeError('Incompatible configuration value!')

        obj_dict.pop('timestamp', None)
        obj_dict.pop('_id', None)
        url_params = "/{}/{}".format(config_type, name)
        url = self._url + self.CONFIGS_ENDPOINT + url_params
        request = _Request(url=url, method="PUT",
                           headers={"Content-Type": "application/json"},
                           data=_json.dumps(obj_dict).encode())
        return self._make_request(request)

    def insert_config(self, config_type, name, value):
        """Insert configuration into database."""
        if not _ConfigType.check_value(config_type, value):
            raise ValueError('Incompatible configuration value!')
        url = self._url + self.CONFIGS_ENDPOINT
        data = {"config_type": config_type, "name": name, "value": value}
        request = _Request(url=url, method="POST",
                           headers={"Content-Type": "application/json"},
                           data=_json.dumps(data).encode())
        return self._make_request(request)

    def find_configs(self,
                     config_type=None,
                     name=None,
                     begin=None,
                     end=None):
        """Find configurations matching search criteria."""
        # build search dictionary
        find_dict = {}
        if config_type is not None:
            find_dict['config_type'] = config_type
        if name is not None:
            find_dict['name'] = name
        if None not in (begin, end):
            find_dict['timestamp'] = {}
            if begin is not None:
                find_dict['timestamp']['$gte'] = begin
            if end is not None:
                find_dict['timestamp']['$lte'] = end

        # request data
        return self.request_configs(find_dict=find_dict)

    def request_configs(self, find_dict=None):
        """Request configurations matching search criteria."""
        url = self._url + self.CONFIGS_ENDPOINT
        if find_dict is None or not find_dict:
            request = _Request(url=url, method="GET")
        else:
            if type(find_dict) is not dict:
                raise AttributeError("`find_dict` is not a dict")
            request = _Request(url=url, method="GET",
                               headers={"Content-Type": "application/json"},
                               data=_json.dumps(find_dict).encode())
        return self._make_request(request)

    def delete_config(self, name, config_type):
        """Mark a configuration as deletable."""
        url_params = "/{}/{}".format(config_type, name)
        url = self._url + self.CONFIGS_ENDPOINT + url_params
        request = _Request(url=url, method="DELETE")
        return self._make_request(request)

    def query_db_size(self):
        """Return estimated size of configuration database."""
        pass

    def query_db_size_deletable(self):
        """Return estimated size of deleted configurations data."""
        pass

    # --- private methods ---

    def _make_request(self, request):
        try:
            response = _json.loads(_urlopen(request).read().decode("utf-8"))
        except _URLError as e:
            return {"code": 111, "message": "Connection refused"}
        except _json.JSONDecodeError as e:
            return {"code": -1, "message": "JSON decode error"}
        except Exception as e:
            _logging.critical("{}".format(e))
        else:
            return response


    # Pv Configuration
    # def get_pv_configurations(self, data=None):
    #     """Return all pv configurations."""
    #     url = "http://{}/pvs".format(self._host)
    #     if data is None:
    #         request = Request(url=url, method="GET")
    #     else:
    #         request = Request(url=url, method="GET",
    #                           headers={"Content-Type": "application/json"},
    #                           data=_json.dumps(data).encode())
    #     return self._make_request(request)
    #
    # def insert_pv_configuration(self, name, config_type, values=[]):
    #     """Insert new PV convfiguration."""
    #     url = "http://{}/pvs".format(self._host)
    #     data = {"name": name, "config_type": config_type,
    #             "values": values}
    #     request = Request(url=url, method="POST",
    #                       headers={"Content-Type": "application/json"},
    #                       data=_json.dumps(data).encode())
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
