
"""Define a class to communicate with configuration database API."""
# import copy as _copy
import json as _json
import logging as _logging
import dateutil.parser
from urllib.request import Request as _Request
from urllib.request import urlopen as _urlopen
from urllib.error import URLError as _URLError

import siriuspy.envars as _envars
import siriuspy.servconf.conf_types as _config_types

# Creates a main logger specific to this module and set level to WARNING
ch = _logging.StreamHandler()
formatter = _logging.Formatter(
    '%(asctime)s %(levelname)8s %(name)s | %(message)s')
ch.setFormatter(formatter)

logger = _logging.getLogger(__name__)
logger.addHandler(ch)
logger.setLevel(_logging.WARNING)  # This toggles all the logging in your app


class ConfigService:
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
        _logging.getLogger(__name__).\
            info("HTTP request will be made to {}".format(self._url))

    @staticmethod
    def get_config_types():
        """Get all configuration types."""
        return _config_types.get_config_types()

    def get_config(self, config_type, name):
        """Get lists by name and config."""
        url_params = "/{}/{}".format(config_type, name)
        url = self._url + self.CONFIGS_ENDPOINT + url_params
        request = _Request(url=url, method="GET")
        return self._make_request(request)

    def update_config(self, obj_dict):
        """Update an existing configuration."""
        if type(obj_dict) is not dict:
            raise ValueError('"obj_dict" is not a dictionary')
        id = obj_dict["_id"]
        config_type = obj_dict['config_type']
        # Check value format
        if not _config_types.check_value(config_type, obj_dict['value']):
            raise TypeError('Incompatible configuration value!')
        # Get params allowed to be updated
        update_dict = {
            "name": obj_dict["name"],
            "value": obj_dict["value"],
            "discarded": obj_dict["discarded"]
        }
        # Build URL a make PUT request
        url_params = "/{}".format(id)
        url = self._url + self.CONFIGS_ENDPOINT + url_params
        request = _Request(url=url, method="PUT",
                           headers={"Content-Type": "application/json"},
                           data=_json.dumps(update_dict).encode())
        return self._make_request(request)

    def insert_config(self, config_type, name, value):
        """Insert configuration into database."""
        if not _config_types.check_value(config_type, value):
            raise TypeError('Incompatible configuration value!')
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
                     end=None,
                     discarded=False):
        """Find configurations matching search criteria.

        Parameters
        ----------
            discarded : True | False (default) | None
            If True, return only discarded configurations, if False, return
            only configurations in use. If None, return all configurations
            matching the other criteria.
        """
        # build search dictionary
        find_dict = {}
        if config_type is not None:
            find_dict['config_type'] = config_type
        if name is not None:
            find_dict['name'] = name
        if begin is not None or end is not None:
            find_dict['created'] = {}
            if begin is not None:
                find_dict['created']['$gte'] = begin
            if end is not None:
                find_dict['created']['$lte'] = end
        if discarded is not None:
            find_dict["discarded"] = discarded

        # request data
        return self.request_configs(find_dict=find_dict)

    def find_nr_configs(self,
                        config_type=None,
                        name=None,
                        begin=None,
                        end=None,
                        discarded=False):
        """Return number of configurations matching search criteria.

        Parameters
        ----------
        config_type: Configuration type.
        name:        Name of the configuration.
        begin:       Begin timestamp elapsed since Unix time epoch (double).
        end:         End timestamp elapsed since Unix time epoch (double).
        discarded:   False | True | None
                     For False the search returns the valid configurations.
                     For True, the discarded configurations.
                     For None, the valid and the discarded configurations.
        """
        # build search dictionary
        find_dict = {}
        if config_type is not None:
            find_dict['config_type'] = config_type
        if name is not None:
            find_dict['name'] = name
        if begin is not None or end is not None:
            find_dict['created'] = {}
            if begin is not None:
                find_dict['created']['$gte'] = begin
            if end is not None:
                find_dict['created']['$lte'] = end
        if discarded is not None:
            find_dict["discarded"] = discarded

        return self.request_count(find_dict=find_dict)

    def request_count(self, find_dict=None):
        """Return number of configurations matching search criteria."""
        url = self._url + self.CONFIGS_ENDPOINT + "/count"
        if find_dict is None or not find_dict:
            request = _Request(url=url, method="GET")
        else:
            if type(find_dict) is not dict:
                raise AttributeError("`find_dict` is not a dict")
            request = _Request(url=url, method="GET",
                               headers={"Content-Type": "application/json"},
                               data=_json.dumps(find_dict).encode())
        return self._make_request(request)

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

    def delete_config(self, obj_dict):
        """Mark a configuration as discarded."""
        url_params = "/{}".format(obj_dict["_id"])
        url = self._url + self.CONFIGS_ENDPOINT + url_params
        request = _Request(url=url, method="PUT",
                           headers={"Content-Type": "application/json"},
                           data=_json.dumps({"discarded": True}).encode())
        return self._make_request(request)

    def query_db_size(self):
        """Return estimated size of configuration database."""
        url = self._url + self.CONFIGS_ENDPOINT + "/stats/size"
        request = _Request(url=url, method="GET")
        return self._make_request(request)

    def query_db_size_discarded(self):
        """Return estimated size of discarded configurations data."""
        pass

    @staticmethod
    def conv_timestamp(datestring):
        """Convert timestamp format from text to double."""
        return dateutil.parser.parse(datestring).timestamp()

    # --- private methods ---

    def _make_request(self, request):
        try:
            response = _json.loads(_urlopen(request).read().decode("utf-8"))
        except _URLError as e:
            return {"code": 111, "message": "Connection refused"}
        except _json.JSONDecodeError as e:
            return {"code": -1, "message": "JSON decode error"}
        except Exception as e:
            _logging.getLogger(__name__).critical("{}".format(e))
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
