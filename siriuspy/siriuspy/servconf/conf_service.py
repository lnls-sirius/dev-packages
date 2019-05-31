
"""Define a class to communicate with configuration database API."""

import json as _json
import datetime as _datetime
from urllib import parse as _parse
from urllib.request import Request as _Request, urlopen as _urlopen
from urllib.error import URLError as _URLError
import dateutil.parser
import numpy as _np

import siriuspy.envars as _envars
import siriuspy.servconf.conf_types as _config_types


class ConfigDBClient:
    """Perform operation on configuration database."""

    _INVALID_CHARACTERS = '\\/:;,?!$'

    def __init__(self, url=None):
        """Class constructor.

        Parameters
        ----------
        url : str | None
            Configuration service host address. For default 'None' value
            the URL defined in siripy.envars is used.

        """
        self._url = url or _envars.server_url_configdb

    @property
    def url(self):
        """Server URL."""
        return self._url

    @property
    def connected(self):
        """Return connection state."""
        try:
            self.get_dbsize()
        except _URLError:
            return False
        return True

    def get_dbsize(self):
        """Return estimated size of configuration database."""
        url = self._create_url(stats=True)
        value = self._make_request(url)
        return value['size']

    def get_dbsize_discarded(self):
        """Return estimated size of discarded configurations data."""
        pass

    def get_nrconfigs(self):
        """Return estimated size of configuration database."""
        url = self._create_url(stats=True)
        value = self._make_request(url)
        return value['count']

    def get_config_types(self):
        """Get all configuration types."""
        return self._make_request(self._create_url())

    def find_configs(self,
                     config_type,
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
        find_dict = dict(config_type=config_type)
        if name is not None:
            find_dict['name'] = name
        if begin is not None or end is not None:
            find_dict['created'] = {}
            if begin is not None:
                find_dict['created']['$gte'] = begin
            if end is not None:
                find_dict['created']['$lte'] = end

        url = self._create_url(config_type=config_type, discarded=discarded)
        return self._make_request(url, data=find_dict)

    def get_config_value(self, config_type, name, discarded=False):
        """Mark a valid configuration as discarded."""
        url = self._create_url(
            config_type=config_type, name=name, discarded=discarded)
        return self._make_request(url)['value']

    def get_config_info(self, config_type, name, discarded=False):
        """Mark a valid configuration as discarded."""
        res = self.find_configs(config_type, name=name, discarded=discarded)
        if not res:
            raise ConfigDBException(
                {'code': 404, 'message': 'Configuration no found.'})
        return res[0]

    def rename_config(self, config_type, oldname, newname):
        """Rename configuration in database."""
        if not isinstance(newname, str):
            raise TypeError(
                'Config name must be str, not {}!'.format(type(newname)))
        if not self.check_valid_configname(newname):
            raise ValueError("There are invalid characters in config name!")

        url = self._create_url(
            config_type=config_type, name=oldname, newname=newname)
        return self._make_request(url, method='POST')

    def insert_config(self, config_type, name, value):
        """Insert configuration into database."""
        if not isinstance(name, str):
            raise TypeError(
                'Config name must be str, not {}!'.format(type(name)))
        if not self.check_valid_configname(name):
            raise ValueError("There are invalid characters in config name!")
        if not _config_types.check_value(config_type, value):
            raise TypeError('Incompatible configuration value!')

        url = self._create_url(config_type=config_type, name=name)
        self._make_request(url, method='POST', data=value)

    def delete_config(self, config_type, name):
        """Mark a valid configuration as discarded."""
        url = self._create_url(config_type=config_type, name=name)
        return self._make_request(url, method='DELETE')

    def retrieve_config(self, config_type, name):
        """Mark a discarded configuration as valid."""
        url = self._create_url(
            config_type=config_type, name=name, discarded=True)
        return self._make_request(url, method='POST')

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
        return _parse.quote(url)

    def _make_request(self, url, method='GET', data=None):
        if data is None:
            request = _Request(url=url, method=method)
        else:
            request = _Request(
                url=url, method=method,
                headers={"Content-Type": "application/json"},
                data=_json.dumps(data, default=_jsonify_numpy).encode())

        try:
            response = _json.loads(_urlopen(request).read().decode("utf-8"))
        except _json.JSONDecodeError:
            response = {"code": -1, "message": "JSON decode error"}

        # print(response)
        if response['code'] != 200:
            raise ConfigDBException(response)
        return response['result']


class ConfigDBException(Exception):
    """Default exception raised for configDB server errors."""

    def __init__(self, response):
        super().__init__('{code:d}: {message:s}.'.format(**response))
        self.server_code = response['code']
        self.server_message = response['message']


def _jsonify_numpy(self, obj):
    if isinstance(obj, _np.ndarray):
        return obj.tolist()
    raise TypeError('Object is not JSON serializable.')
