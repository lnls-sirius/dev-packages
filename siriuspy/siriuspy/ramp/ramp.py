"""Module with BO ramp class."""

# from http import HTTPStatus as _HTTPStatus

# from siriuspy.ramp import util as _util
from siriuspy.ramp import exceptions as _exceptions
from siriuspy.ramp.conn import ConnConfig_BORamp as _CCBORamp
from siriuspy.ramp.conn import ConnConfig_BONormalized as _CCBONormalized


class _BOConfigs:
    """Abstract Booster configuration class."""

    def __init__(self, name=None):
        """Constructor."""
        self._name = name
        self._metadata = None
        self._configuration = None
        self._synchronized = False

    @property
    def name(self):
        """Configuration name of BO normalized."""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._synchronized = False

    @property
    def metadata(self):
        """Configuration metadata."""
        return dict(self._metadata)

    @property
    def configuration(self):
        """Normalized magnet strengths configuration."""
        return self._configuration.copy()

    @configuration.setter
    def configuration(self, value):
        """Set normalized magnet strengths configuration."""
        self._set_configuration(value)
        self._synchronized = False

    @property
    def servconf_synchronized(self):
        """Synchronization state between object and configuration in server."""
        return self._synchronized

    @property
    def servconf_connector(self):
        """Config server connector."""
        return self._conn

    def servconf_check(self):
        """Return True if config name exists in serv config."""
        _, metadata = self._conn.config_find(name=self.name)
        return len(metadata) > 0

    def servconf_load(self):
        """Load configuration from config server."""
        configuration, metadata = self._conn.config_get(self.name)
        self._configuration = configuration
        self._metadata = metadata
        self._synchronized = True

    def servconf_update(self):
        """Update configuration in config server."""
        if self.name is None:
            raise _exceptions.RampConfigNameNotDefined()
        # check of metadat is present
        if not self._metadata:
            raise _exceptions.RampMetadataInvalid()
        # check if data format is ok
        if not self._conn.check_value(self._configuration):
            raise _exceptions.RampConfigFormatError()
        # update config server with metadata and valid configuration
        self._metadata['name'] = self.name
        self._conn.config_update(self._metadata, self._configuration)
        # update metadata
        configuration, metadata = self._conn.config_get(name=self.name)
        self._configuration = configuration
        self._metadata = metadata
        self._synchronized = True

    def servconf_save(self):
        """Save configuration to config server."""
        # check if config name is not None
        if self.name is None:
            raise _exceptions.RampConfigNameNotDefined()
        # check if data format is ok
        if not self._conn.check_value(self._configuration):
            raise _exceptions.RampConfigFormatError()
        # check if config name already exists
        r = self.servconf_check()
        if r is True:
            # already exists
            self.servconf_update()
        else:
            # new configuration
            self._conn.config_insert(self.name, self._configuration)
        self._synchronized = True

    def get_config_type_template(self):
        """Return a tmeplate dictionary of normalized config."""
        return self._conn.get_config_type_template()

    def check_value(self):
        """Check current configuration."""
        return self._conn.check_value(self._configuration)

    def __len__(self):
        """Length of configuration."""
        if self._configuration is None:
            return 0
        else:
            return len(self._configuration)

    def __getitem__(self, index):
        """Return normalized strength of a given magnet."""
        return self._get_item(index)

    def __setitem__(self, index, value):
        """Set normalized strength of a given magnet."""
        self._set_item(index, value)
        self._synchronized = False


class BONormalized(_BOConfigs):
    """Booster normalized configuration class."""

    _conn = _CCBONormalized()

    def __init__(self, name=None):
        """Constructor."""
        _BOConfigs.__init__(self, name=name)

    def _get_item(self, index):
        return self._configuration[index]

    def _set_item(self, index, value):
        self._configuration[index] = value

    def _set_configuration(self, value):
        self._configuration = value


class BORamp(_BOConfigs):
    """Booster ramp class."""

    _conn = _CCBORamp()

    def __init__(self, name=None):
        """Constructor."""
        _BOConfigs.__init__(self, name=name)

    def _get_item(self, index):
        if isinstance(index, int):
            return self._configuration[index]
        else:
            t, n = zip(*self._configuration)
            index = n.index(index)
            return self._configuration[index]

    def _set_item(self, index, value):
        if isinstance(index, int):
            self._configuration[index] = value
        else:
            t, n = zip(*self._configuration)
            index = n.index(index)
            self._configuration[index] = value

    def _set_configuration(self, value):
        self._configuration = value
