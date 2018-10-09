"""Configurations connection classes."""

from copy import deepcopy as _dcopy
from http import HTTPStatus as _HTTPStatus

from siriuspy import envars as _envars
from siriuspy.servconf import util as _util
from siriuspy.servconf import exceptions as _exceptions
from siriuspy.servconf.conf_service import ConfigService as _ConfigService
from siriuspy.servconf.conf_types import check_value as _check_value


class ConnConfigService:
    """Syntactic sugar class for ConfigService."""

    def __init__(self, config_type, url=_envars.server_url_configdb):
        """Contructor."""
        self._config_type = config_type
        self._srvconf = _ConfigService(url=url)

    @property
    def config_type(self):
        """Type of configuration."""
        return self._config_type

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
            self._name = _util.generate_config_name()
        else:
            self._name = name
        self._metadata = None
        self._configuration = dict()
        self._synchronized = False

    @property
    def config_type(self):
        """Type of configuration."""
        return self._conn.config_type

    @property
    def name(self):
        """Name of configuration."""
        return self._name

    @name.setter
    def name(self, value):
        """Set name of configuration."""
        self._name = value
        self._synchronized = False

    @property
    def metadata(self):
        """Metadata of configuration."""
        return dict(self._metadata)

    @property
    def configuration(self):
        """Get configuration."""
        return _dcopy(self._configuration)

    @configuration.setter
    def configuration(self, value):
        """Set configuration."""
        self._set_configuration(value)
        self._synchronized = False

    @property
    def configsrv_synchronized(self):
        """Return sync state of object and configuration in server."""
        return self._synchronized

    @property
    def configsrv_connector(self):
        """Connector to ConfigServer."""
        return self._conn

    def configsrv_exist(self):
        """Return True if configuration exists in ConfigServer."""
        _, metadata = self._conn.config_find(name=self.name)
        return len(metadata) > 0

    def configsrv_load(self):
        """Load configuration from ConfigServer."""
        configuration, metadata = self._conn.config_get(self.name)
        self._configuration = configuration
        self._metadata = metadata
        self._synchronized = True

    def configsrv_save(self, new_name=None):
        """Save configuration to ConfigServer."""
        # if config is syncronyzed, it is not necessary to save an identical
        # one in server
        if self.configsrv_synchronized:
            return

        # check if data format is ok
        if not self._conn.check_value(self._configuration):
            raise _exceptions.SrvConfigFormatError(
                'Configuration value with inconsistent format.')

        # if new_name is given, apply
        if new_name is not None:
            self._name = new_name

        # check if config name already exists
        if self.configsrv_exist():
            raise _exceptions.SrvConfigAlreadyExists(
                'A configuration with the given name already exists in '
                'server.')

        configuration, metadata = \
            self._conn.config_insert(self._name, self._configuration)
        self._configuration = configuration
        self._metadata = metadata
        self._synchronized = True

    def configsrv_delete(self):
        """Delete configuration from server."""
        # TODO: should this method be easily available?
        if self.configsrv_exist():
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

    @staticmethod
    def conv_timestamp_txt_2_flt(timestamp):
        """Convert timestamp format from text to float."""
        return _ConfigService.conv_timestamp_txt_2_flt(timestamp)

    @staticmethod
    def conv_timestamp_flt_2_txt(timestamp):
        """Convert timestamp format from float to text."""
        return _ConfigService.conv_timestamp_flt_2_txt(timestamp)
