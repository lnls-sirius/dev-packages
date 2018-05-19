"""Module with BO ramp class."""

from http import HTTPStatus as _HTTPStatus

from siriuspy.ramp import util as _util
from siriuspy.ramp import exceptions as _exceptions
from siriuspy.ramp.conn import ConnConfig_BORamp as _CCBORamp
from siriuspy.ramp.conn import ConnConfig_BONormalized as _CCBONormalized


class BONormalized:
    """Booster normalized configuration class."""

    _conn = _CCBONormalized()

    def __init__(self, name=None):
        """Constructor."""
        self._name = name
        self._metadata = dict()
        self._configuration = dict()

    @property
    def name(self):
        """Configuration name of BO normalized."""
        return self._name

    @property
    def servconf_connector(self):
        """Config server connector."""
        return self._conn

    @property
    def configuration(self):
        """Normalized magnet strengths configuration."""
        return dict(self._configuration)

    @configuration.setter
    def configuration(self, value):
        """Set normalized magnet strengths configuration."""
        self._configuration = value

    def servconf_load_from(self):
        """Load configuration from config server."""
        r = self._conn.config_get(self.name)
        self._conn.response_check(r)
        self._metadata = dict(r['result'])
        self._configuration = dict(self._metadata['value'])
        del self._metadata['value']

    def servconf_check_exists(self):
        """Return True if config name exists in serv config."""
        r = self._conn.config_find(name=self.name)
        self._conn.response_check(r)
        return len(r['result']) > 0

    def servconf_save_to(self):
        """Save configuration to config server."""
        # check if config name is not None
        if self.name is None:
            raise _exceptions.RampConfigNameNotDefined()
        # check if data format is ok
        if not self._conn.check_value(self._configuration):
            raise _exceptions.RampConfigFormatError()
        # check if config name already exists
        r = self.servconf_check_exists()
        if r is True:
            # already exists
            r = self._conn.config_get(self.name)
            self._conn.response_check(r)
            r = self._conn.config_update(r['result'])
            self.response_check(r)
        else:
            # new configuration
            r = self._conn.config_insert(self.name, self._configuration)
            self._conn.response_check(r)

    def check_value(self):
        """Check current configuration."""
        return self._conn.check_value(self._configuration)

    def get_config_type_template(self):
        """Return a tmeplate dictionary of normalized config."""
        return self._conn.get_config_type_template()

    def __getitem__(self, index):
        """Return normalized strength of a given magnet."""
        return self._configuration[index]

    def __setitem__(self, index, value):
        """Set normalized strength of a given magnet."""
        self._configuration[index] = value


class BORamp:
    """Booster ramp class."""

    _ccramp = _CCBORamp()

    def __init__(self, name=None):
        """Constructor."""
        self._name = name
        self._config = dict()
        self._ramp = []

    @property
    def name(self):
        """Configuration name of BO ramp."""
        return self._name

    def load_from_configdb(self):
        """Load configuration from config server."""
        # load ramp
        if not self._load_ramp_and_check():
            return False
        # load configs
        if not self._load_normalized_and_check():
            return False
        return True

    @property
    def connected(self):
        """Connection state."""
        return self._ccramp.connected and self._conn.connected

    def _load_ramp_and_check(self):
        if self.name is not None and self.connected:
            r = self._ccramp.get_config(self._name)
            if not self.response_check(r):
                return False
            else:
                self._config = r['result']
        return True

    def _load_normalized_and_check(self):
        data = self._config['value']
        status = True
        for time, name in data['normalized_configurations*']:
            r = self._conn.get_config(name)
            # check if norm config exists
            if not self.response_check(r):
                return False
            else:
                normalized = r['value']
                print(time, name)
                print(normalized)
        return status
