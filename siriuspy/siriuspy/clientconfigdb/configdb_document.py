"""Configurations connection classes."""

import time as _time
import datetime as _datetime
import re as _re
from copy import deepcopy as _dcopy

from .configdb_client import ConfigDBClient as _ConfigDBClient


class ConfigDBDocument():
    """Abstract configuration class."""

    def __init__(self, config_type, name=None, url=None):
        """Constructor."""
        self._configdbclient = \
            _ConfigDBClient(url=url, config_type=config_type)
        self._name = name or self.generate_config_name()
        self._info = None
        self._value = None
        self._synchronized = False

    @property
    def configdbclient(self):
        """."""
        return self._configdbclient

    @property
    def url(self):
        """."""
        return self._configdbclient.url

    @property
    def config_type(self):
        """."""
        return self._configdbclient.config_type

    @property
    def connected(self):
        """."""
        return self._configdbclient.connected

    @property
    def name(self):
        """Name of configuration."""
        return self._name

    @name.setter
    def name(self, value):
        """Set name of configuration."""
        if self._configdbclient.check_valid_configname(value):
            self._name = value
            self._synchronized = False

    @property
    def info(self):
        """Metadata of configuration."""
        return dict(self._info)

    @property
    def created(self):
        """."""
        return self._info['created']

    @property
    def modified(self):
        """."""
        return self._info['modified'][-1]

    @property
    def modified_count(self):
        """."""
        return len(self._info['modified'])

    @property
    def discarded(self):
        """."""
        return self._info['discarded']

    @property
    def value(self):
        """Get configuration."""
        return _dcopy(self._value)

    @value.setter
    def value(self, value):
        """Set configuration."""
        self._set_value(value)

    @property
    def synchronized(self):
        """Return sync state of object and configuration in server."""
        return self._synchronized

    def exist(self):
        """Return True if configuration exists in ConfigServer."""
        info = self._configdbclient.find_configs(name=self._name)
        return len(info) > 0

    def load(self):
        """Load configuration from ConfigServer."""
        self._info = self._configdbclient.get_config_info(name=self._name)
        self._value = self._configdbclient.get_config_value(name=self._name)
        self._synchronized = True

    def save(self, new_name=None):
        """Save configuration to ConfigServer."""
        # if config is syncronyzed, it is not necessary to save an identical
        # one in server
        if self.exist() and self._synchronized and not new_name:
            return

        # check if data format is ok
        if not self._configdbclient.check_valid_value(self._value):
            raise ValueError(
                'Configuration value with inconsistent format.')

        # if new_name is given, apply
        if new_name is not None:
            self._name = new_name

        self._configdbclient.insert_config(self._name, self._value)
        self._info = self._configdbclient.get_config_info(name=self._name)
        self._synchronized = True

    def delete(self):
        """Delete configuration from server."""
        # NOTE: should this method be easily available?
        if self.exist():
            self._configdbclient.delete_config(self._name)
            self._synchronized = False

    def check_valid_value(self, value):
        """."""
        return self._configdbclient.check_valid_value(value)

    def get_value_from_template(self):
        """."""
        return self._configdbclient.get_value_from_template()

    @classmethod
    def generate_config_name(cls, name=None):
        """Generate a configuration name using current imestamp."""
        if name is None:
            name = ''
        name = name.strip()
        # tsf = _re.compile('^\d\d\d\d\d\d-\d\d\d\d\d\d')
        tsf = _re.compile('^[\d]{6}-[\d]{6}')
        if tsf.match(name):
            new_name = cls._get_timestamp() + name[13:]
        else:
            if name:
                new_name = cls._get_timestamp() + ' ' + name
            else:
                new_name = cls._get_timestamp()
        return new_name

    def _set_value(self, value):
        if self.check_valid_value(value):
            self._value = _dcopy(value)
            self._synchronized = False
        else:
            raise ValueError('Invalid value.')

    def _get_item(self, index):
        return

    def _set_item(self, index, value):
        self._synchronized = False
        return

    def __len__(self):
        """Length of configuration."""
        return len(self._value) if hasattr(self._value, '__len__') else 0

    def __getitem__(self, index):
        """Return configuration item."""
        return self._get_item(index)

    def __setitem__(self, index, value):
        """Set configuration item."""
        self._set_item(index, value)

    @staticmethod
    def _get_timestamp(now=None):
        """."""
        if now is None:
            now = _time.time()
        return _datetime.datetime.fromtimestamp(now).strftime('%y%m%d-%H%M%S')
