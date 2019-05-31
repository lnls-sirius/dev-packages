"""Configurations connection classes."""

import time as _time
import datetime as _datetime
import re as _re
from copy import deepcopy as _dcopy

from .configdb_type import ConfigDBType as _ConfigDBType


class ConfigDBDocument(_ConfigDBType):
    """Abstract configuration class."""

    def __init__(self, config_type, name=None, url=None):
        """Constructor."""
        super().__init__(config_type, url=url)
        self._name = name or self._generate_config_name()
        self._info = None
        self._value = None
        self._synchronized = False
        if self.exist():
            self.load()

    @property
    def name(self):
        """Name of configuration."""
        return self._name

    @name.setter
    def name(self, value):
        """Set name of configuration."""
        if self.check_valid_configname(value):
            self._name = value
            self._synchronized = False

    @property
    def info(self):
        """Metadata of configuration."""
        return dict(self._info)

    @property
    def created(self):
        return self._info['created']

    @property
    def modified(self):
        return self._info['modified'][-1]

    @property
    def modified_count(self):
        return len(self._info['modified'])

    def discarded(self):
        return self._info['discarded']

    @property
    def value(self):
        """Get configuration."""
        return _dcopy(self._value)

    @value.setter
    def value(self, value):
        """Set configuration."""
        self._set_value(value)
        self._synchronized = False

    @property
    def synchronized(self):
        """Return sync state of object and configuration in server."""
        return self._synchronized

    def get_config_value(self, discarded=False):
        """Mark a valid configuration as discarded."""
        return super().get_config_value(self._name, discarded=discarded)

    def get_config_info(self, discarded=False):
        """Mark a valid configuration as discarded."""
        return super().get_config_info(self._name, discarded=discarded)

    def rename_config(self, newname):
        """Rename configuration in database."""
        return super().rename_config(self._name, newname)

    def insert_config(self, value):
        """Insert configuration into database."""
        return super().insert_config(self._name, value)

    def delete_config(self):
        """Mark a valid configuration as discarded."""
        return super().delete_config(self._name)

    def retrieve_config(self):
        """Mark a discarded configuration as valid."""
        return super().retrieve_config(self._config_type, self._name)

    def exist(self):
        """Return True if configuration exists in ConfigServer."""
        info = self.find_configs(name=self._name)
        return len(info) > 0

    def load(self):
        """Load configuration from ConfigServer."""
        self._info = self.get_config_info()
        self._value = self.get_config_value()
        self._synchronized = True

    def save(self, new_name=None):
        """Save configuration to ConfigServer."""
        # if config is syncronyzed, it is not necessary to save an identical
        # one in server
        if self.synchronized and not new_name:
            return

        # check if data format is ok
        if not self.check_valid_value(self._value):
            raise ValueError(
                'Configuration value with inconsistent format.')

        # if new_name is given, apply
        if new_name is not None:
            self._name = new_name

        self.insert_config(self._value)
        self._info = self.get_config_info()
        self._synchronized = True

    def delete(self):
        """Delete configuration from server."""
        # TODO: should this method be easily available?
        if self.exist():
            self.delete_config()
            self._synchronized = False

    def _set_value(self, value):
        if self.check_valid_value(value):
            self._value = _dcopy(value)

    def _get_item(self, index):
        return

    def _set_item(self, index, value):
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
        self._synchronized = False

    @classmethod
    def _generate_config_name(cls, name=None):
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

    @staticmethod
    def _get_timestamp(now=None):
        """."""
        if now is None:
            now = _time.time()
        return _datetime.datetime.fromtimestamp(now).strftime('%y%m%d-%H%M%S')
