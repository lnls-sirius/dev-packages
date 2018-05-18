"""Module with BO ramp class."""

from http import HTTPStatus as _HTTPStatus
from siriuspy.ramp.conn import ConnConfig_BORamp as _CCBORamp
from siriuspy.ramp.conn import ConnConfig_BONormalized as _CCBONormalized


class BONormalized:

    def __init__(self, name=None):
        self._name = name
        self._ccnorm = _CCBONormalized()
        self._normalized = dict()

    @property
    def name(self):
        """Configuration name of BO normalized."""
        return self._name

    def load_from_configdb(self):
        """Load configuration from config server."""
        r = self._ccnorm.get_config(self, self.name)
        if r['code'] != _HTTPStatus.OK:
            print('{}: {}!'.format(self.name, r['message']))
            return False
        self._normalized = r['result'].copy()
        return True

    def save_to_configdb(self):
        """Save configuration to config server."""
        # check if config name is not None
        if self.name is None:
            print('Undefined configuration name!')
            return False
        # check if data format is ok
        if not self.check_value(self._normalized):
            print('Incorrect value format!')
            return False
        # check if config name already exists
        r = self.find_configs()
        if not self.response_check(r):
            return False
        if len(r['result']) > 0:
            # already exists
            r = self.get_config(self.name)
            if not self.response_check(r):
                return False
            r = self.update_config(r['result'])
            if not self.response_check(r):
                return False
        else:
            # new configuration
            r = self.insert_config(self.name, self._normalized)
            if not self.response_check(r):
                return False
        return True

    def check_value(self):
        """Check current configuration."""
        return self._ccnorm.check_value(self._normalized)


class BORamp:
    """Booster ramp class."""

    def __init__(self, name=None):
        """Constructor."""
        self._name = name
        self._config = dict()
        self._normalized_table = []

        # create connectors to configuration service
        self._ccramp = _CCBORamp()
        self._ccnorm = _CCBONormalized()

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
        return self._ccramp.connected and self._ccnorm.connected

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
            r = self._ccnorm.get_config(name)
            # check if norm config exists
            if not self.response_check(r):
                return False
            else:
                normalized = r['value']
                print(time, name)
                print(normalized)
        return status
