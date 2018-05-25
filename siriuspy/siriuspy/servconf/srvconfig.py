"""Configurations connection classes."""

from copy import deepcopy as _dcopy
from http import HTTPStatus as _HTTPStatus

from siriuspy import envars as _envars
from siriuspy import util as _util
from siriuspy.servconf import exceptions as _exceptions
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from siriuspy.servconf.conf_types import check_value as _check_value


class ConnConfigService:
    """Syntactic sugar class for ConfigService."""

    def __init__(self, config_type, url=_envars.server_url_configdb):
        """Contructor."""
        if config_type not in ('bo_ramp', 'bo_normalized'):
            raise ValueError('Invalid configuration type!')
        self._config_type = config_type
        self._srvconf = _ConfigService(url=url)

    def config_get(self, name):
        """Get configuration by its name."""
        r = self._srvconf.get_config(self._config_type, name)
        return ConnConfigService._process_return(r)

    def config_insert(self, name, value):
        """Insert a new configuration."""
        r = self._srvconf.insert_config(self._config_type, name, value)
        return ConnConfigService._process_return(r)

    def config_find(self,
                    name=None,
                    begin=None,
                    end=None,
                    discarded=False):
        """Return configurations."""
        r = self._srvconf.find_configs(config_type=self._config_type,
                                       name=name, begin=begin, end=end,
                                       discarded=discarded)
        return ConnConfigService._process_return(r)

    def config_find_nr(self,
                       name=None,
                       begin=None,
                       end=None,
                       discarded=False):
        """Return nr of configurations."""
        r = self._srvconf.find_nr_configs(config_type=self._config_type,
                                          name=name, begin=begin, end=end,
                                          discarded=discarded)
        return ConnConfigService._process_return(r)

    def config_update(self, metadata, configuration):
        """Update existing configuration."""
        config = dict(metadata)
        config.update({'value': configuration})
        r = self._srvconf.update_config(config)
        return ConnConfigService._process_return(r)

    def config_delete(self, metadata):
        """Mark a configuration as discarded."""
        r = self._srvconf.delete_config(metadata)
        return ConnConfigService._process_return(r)

    def check_value(self, value):
        """Return True or False depending whether value matches config type."""
        return _check_value(self._config_type, value)

    def get_config_type_template(self):
        """Return template dictionary of config type."""
        return self._srvconf.get_config_type_template(self._config_type)

    @staticmethod
    def _response_check(r):
        """Check response."""
        if r['code'] == _HTTPStatus.OK:
            return
        st = 'Error code {}: {}'.format(r['code'], r['message'])
        if r['code'] == _HTTPStatus.NOT_FOUND:
            raise _exceptions.SrvConfigNotFound(st)
        elif r['code'] == _HTTPStatus.CONFLICT:
            raise _exceptions.SrvConfigConflict(st)
        else:
            raise _exceptions.SrvCouldNotConnect(st)

    @staticmethod
    def _process_return(r):
        ConnConfigService._response_check(r)
        # print(r)
        if 'result' in r:
            metadata = r['result']
            configuration = None
            if isinstance(metadata, dict):
                metadata = dict(metadata)  # copy
                configuration = dict(metadata['value'])
                del metadata['value']
            return configuration, metadata


class ConfigSrv:
    """Abstract configuration class."""

    def __init__(self, name=None):
        """Constructor."""
        if name is None:
            self._name = '_ConfigSrv_' + _util.get_timestamp()
        else:
            self._name = name
        self._metadata = None
        self._configuration = dict()
        self._synchronized = False

    @property
    def name(self):
        """Configuration name."""
        return self._name

    @name.setter
    def name(self, value):
        """Configuration name."""
        self._name = value
        self._synchronized = False

    @property
    def metadata(self):
        """Configuration metadata."""
        return dict(self._metadata)

    @property
    def configuration(self):
        """Configuration data."""
        return _dcopy(self._configuration)

    @configuration.setter
    def configuration(self, value):
        """Configuration data."""
        self._set_configuration(value)
        self._synchronized = False

    @property
    def configsrv_synchronized(self):
        """Synchronization state of object and configuration in server."""
        return self._synchronized

    @property
    def configsrv_connector(self):
        """Connector to ConfigServer."""
        return self._conn

    def configsrv_check(self):
        """Return True if configuration exists in ConfigServer."""
        _, metadata = self._conn.config_find(name=self.name)
        return len(metadata) > 0

    def configsrv_load(self):
        """Load configuration from ConfigServer."""
        configuration, metadata = self._conn.config_get(self.name)
        self._configuration = configuration
        self._metadata = metadata
        self._synchronized = True

    def configsrv_update(self):
        """Update configuration in ConfigServer."""
        if not isinstance(self.name, str):
            raise _exceptions.SrvConfigInvalidName()
        # check of metadat is present
        if not self._metadata:
            raise _exceptions.SrvMetadataInvalid()
        # check if data format is ok
        if not self._conn.check_value(self._configuration):
            raise _exceptions.SrvConfigFormatError()
        # update config server with metadata and valid configuration
        if self.name != self._metadata['name']:
            raise _exceptions.SrvConfigConflict()
        self._conn.config_update(self._metadata, self._configuration)
        # update metadata
        configuration, metadata = self._conn.config_get(name=self.name)
        self._configuration = configuration
        self._metadata = metadata
        self._synchronized = True

    def configsrv_save(self):
        """Save configuration to ConfigServer."""
        # check if config name is not None
        if not isinstance(self.name, str):
            raise _exceptions.SrvConfigInvalidName()
        # check if data format is ok
        if not self._conn.check_value(self._configuration):
            raise _exceptions.SrvConfigFormatError()
        # check if config name already exists
        r = self.configsrv_check()
        if r is True:
            # already exists
            if not self._metadata:
                raise _exceptions.SrvMetadataInvalid()
            if self.name != self._metadata['name']:
                configuration, metadata = self._conn.config_get(self.name)
                self._metadata = metadata
            self.configsrv_update()
        else:
            # new configuration
            configuration, metadata = \
                self._conn.config_insert(self.name, self._configuration)
            self._configuration = configuration
            self._metadata = metadata
        self._synchronized = True

    def configsrv_delete(self):
        """Delete configuration from server."""
        # TODO: should this method be easily available?
        if self.configsrv_check():
            _, metadata = self._conn.config_get(name=self.name)
            self._conn.config_delete(metadata)
            self._synchronized = False

    def configsrv_find(self):
        """Get list of configurations."""
        _, metadata = self._conn.config_find()
        return metadata

    def get_config_type_template(self):
        """Return a template dictionary of the configuration."""
        return self._conn.get_config_type_template()

    def check_value(self):
        """Check configuration validity."""
        return self._conn.check_value(self._configuration)

    def __len__(self):
        """Length of configuration."""
        if self._configuration is None:
            return 0
        else:
            return len(self._configuration)

    def __getitem__(self, index):
        """Return configuration item."""
        return self._get_item(index)

    def __setitem__(self, index, value):
        """Set configuration item."""
        self._set_item(index, value)
        self._synchronized = False
