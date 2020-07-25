
"""Define a class to communicate with configuration database API."""

import json as _json
import datetime as _datetime
from urllib import parse as _parse
from urllib.request import Request as _Request, urlopen as _urlopen
from urllib.error import URLError as _URLError
import dateutil.parser
import numpy as _np

from .. import envars as _envars

from . import _templates


class ConfigDBClient:
    """Perform operation on configuration database."""

    _TIMEOUT_DEFAULT = 2.0
    _INVALID_CHARACTERS = '\\/:;,?!$'

    def __init__(self, url=None, config_type=None):
        """Class constructor.

        Parameters
        ----------
        url : str | None
            Configuration service host address. For default 'None' value
            the URL defined in siripy.envars is used.

        """
        self._url = url or _envars.SRVURL_CONFIGDB
        self._config_type = config_type

    @property
    def config_type(self):
        """Type of configuration."""
        return self._config_type

    @config_type.setter
    def config_type(self, name):
        if isinstance(name, str):
            self._config_type = name

    @property
    def url(self):
        """Server URL."""
        return self._url

    @property
    def connected(self):
        """Return connection state."""
        try:
            self.get_dbsize()
        except ConfigDBException as err:
            return not err.server_code == -2
        return True

    def get_dbsize(self):
        """Return estimated size of configuration database."""
        return self._make_request(stats=True)['size']

    def get_nrconfigs(self):
        """Return estimated size of configuration database."""
        return self._make_request(stats=True)['count']

    def get_config_types(self):
        """Get configuration types existing as database entries."""
        return self._make_request()

    @staticmethod
    def get_config_types_from_templates():
        """Return list of configuration types as defined in templates."""
        return list(_templates.get_config_types())

    def find_configs(self,
                     name=None,
                     begin=None,
                     end=None,
                     config_type=None,
                     discarded=False):
        """Find configurations matching search criteria.

        Parameters
        ----------
            discarded : True | False (default) | None
            If True, return only discarded configurations, if False, return
            only configurations in use. If None, return all configurations
            matching the other criteria.

        """
        config_type = self._process_config_type(config_type)
        # build search dictionary
        find_dict = dict(config_type=config_type)
        if name is not None:
            find_dict['name'] = name
        if begin is not None or end is not None:
            find_dict['created'] = {}
            if begin is not None:
                find_dict['created']['$gte'] = begin
            if end is not None:
                find_dict['created']['$lte'] = end

        return self._make_request(
            config_type=config_type, discarded=discarded, data=find_dict)

    def get_config_value(self, name, config_type=None, discarded=False):
        """Get value field of a given configuration."""
        config_type = self._process_config_type(config_type)
        return self._make_request(
            config_type=config_type, name=name, discarded=discarded)['value']

    def get_config_info(self, name, config_type=None, discarded=False):
        """Get information of a given configuration."""
        config_type = self._process_config_type(config_type)
        res = self.find_configs(
            name=name, config_type=config_type, discarded=discarded)
        if not res:
            raise ConfigDBException(
                {'code': 404, 'message': 'Configuration no found.'})
        return res[0]

    def rename_config(self, oldname, newname, config_type=None):
        """Rename configuration in database."""
        config_type = self._process_config_type(config_type)
        if not isinstance(newname, str):
            raise TypeError(
                'Config name must be str, not {}!'.format(type(newname)))
        if not self.check_valid_configname(newname):
            raise ValueError("There are invalid characters in config name!")

        return self._make_request(
            config_type=config_type, name=oldname, newname=newname,
            method='POST')

    def insert_config(self, name, value, config_type=None):
        """Insert configuration into database."""
        config_type = self._process_config_type(config_type)
        if not isinstance(name, str):
            raise TypeError(
                'Config name must be str, not {}!'.format(type(name)))
        if not self.check_valid_configname(name):
            raise ValueError("There are invalid characters in config name!")
        if not self.check_valid_value(value, config_type=config_type):
            raise TypeError('Incompatible configuration value!')

        self._make_request(
            config_type=config_type, name=name, method='POST', data=value)

    def delete_config(self, name, config_type=None):
        """Mark a valid configuration as discarded."""
        config_type = self._process_config_type(config_type)
        return self._make_request(
            config_type=config_type, name=name, method='DELETE')

    def retrieve_config(self, name, config_type=None):
        """Mark a discarded configuration as valid."""
        config_type = self._process_config_type(config_type)
        return self._make_request(
            config_type=config_type, name=name, discarded=True, method='POST')

    def get_value_from_template(self, config_type=None):
        """Return value of a configuration type."""
        config_type = self._process_config_type(config_type)
        return _templates.get_template(config_type)

    def check_valid_value(self, value, config_type=None):
        """Check whether values data corresponds to a configuration type."""
        config_type = self._process_config_type(config_type)
        return _templates.check_value(config_type, value)

    @classmethod
    def check_valid_configname(cls, name):
        "Check if `name` is a valid name for configurations."
        return not set(name) & set(cls._INVALID_CHARACTERS)

    @staticmethod
    def conv_timestamp_txt_2_flt(timestamp):
        """Convert timestamp format from text to float."""
        return dateutil.parser.parse(timestamp).timestamp()

    @staticmethod
    def conv_timestamp_flt_2_txt(timestamp):
        """Convert timestamp format from float to text."""
        return str(_datetime.datetime.fromtimestamp(timestamp))

    # --- private methods ---

    def _process_config_type(self, config_type):
        config_type = config_type or self._config_type
        if not config_type:
            raise ValueError(
                'You must define a `config_type` attribute or' +
                ' provide it in method call.')
        return config_type

    def _make_request(self, method='GET', data=None, **kwargs):
        try:
            return self._request(method, data, **kwargs)
        except ConfigDBException as err:
            if err.server_code == -2:
                self._rotate_server_url()
                return self._request(method, data, **kwargs)
            else:
                raise err

    def _request(self, method='GET', data=None, **kwargs):
        url = self._create_url(**kwargs)

        if data is None:
            request = _Request(url=url, method=method)
        else:
            request = _Request(
                url=url, method=method,
                headers={"Content-Type": "application/json"},
                data=_json.dumps(data, default=_jsonify_numpy).encode())

        try:
            url_conn = _urlopen(
                request, timeout=ConfigDBClient._TIMEOUT_DEFAULT)
            response = _json.loads(url_conn.read().decode("utf-8"))
        except _json.JSONDecodeError:
            response = {"code": -1, "message": "JSON decode error"}
        except _URLError as err:
            response = {'code': -2, 'message': str(err)}

        # print(response)
        if response['code'] != 200:
            raise ConfigDBException(response)
        return response['result']

    def _rotate_server_url(self):
        if self._url != _envars.SRVURL_CONFIGDB_2:
            self._url = _envars.SRVURL_CONFIGDB_2
        else:
            self._url = _envars.SRVURL_CONFIGDB

    def _create_url(self, config_type=None, name=None, discarded=False,
                    stats=False, newname=None):
        url = self.url
        if stats:
            return url + '/stats'
        url += '/configs'
        if newname:
            url += '/rename'
        if discarded:
            url += '/discarded'
        if config_type:
            url += '/' + config_type
        if name:
            url += '/' + name
        if newname:
            url += '/' + newname
        return _parse.quote(url, safe='/:')


class ConfigDBException(Exception):
    """Default exception raised for configDB server errors."""

    def __init__(self, response):
        """."""
        super().__init__('{code:d}: {message:s}.'.format(**response))
        self.server_code = response['code']
        self.server_message = response['message']


def _jsonify_numpy(obj):
    if isinstance(obj, _np.ndarray):
        return obj.tolist()
    raise TypeError('Object is not JSON serializable.')
