"""Module with BO ramp class."""

from http import HTTPStatus as _HTTPStatus
from siriuspy.ramp.conn import ConnConfig_BORamp as _CCBORamp
from siriuspy.ramp.conn import ConnConfig_BONormalized as _CCBONormalized


class BONormalized:

    _ccnorm = _CCBONormalized()

    def __init__(self, name=None):
        self._name = name
        self._normalized = dict()

    @property
    def name(self):
        """Configuration name of BO normalized."""
        return self._name

    @property
    def normalized(self):
        """Normalized magnet strengths."""
        return self._normalized

    @normalized.setter
    def normalized(slef, value):
        """Set normalized magnet strengths."""
        self._normalized = value

    def load_from_configdb(self):
        """Load configuration from config server."""
        r = self._ccnorm.get_config(self, self.name)
        if r['code'] != _HTTPStatus.OK:
            print('{}: {}!'.format(self.name, r['message']))
            return False
        self._normalized = r['result'].copy()
        return True

    def check_in_configdb(self):
        """Return True if config name exists in serv config."""
        r = self._ccnorm.find_configs()
        if not self._ccnorm.response_check(r):
            return None
        return len(r['result']) > 0

    def save_to_configdb(self):
        """Save configuration to config server."""
        # check if config name is not None
        if self.name is None:
            print('Undefined configuration name!')
            return False
        # check if data format is ok
        if not self._ccnorm.check_value(self._normalized):
            print('Incorrect value format!')
            return False
        # check if config name already exists
        r = self.is_in_configdb()
        if r is None:
            return False
        if r is True:
            # already exists
            r = self._ccnorm.get_config(self.name)
            if not self.response_check(r):
                return False
            r = self._ccnorm.update_config(r['result'])
            if not self._ccnorm.response_check(r):
                return False
        else:
            # new configuration
            r = self._ccnorm.insert_config(self.name, self._normalized)
            if not self._ccnorm.response_check(r):
                return False
        return True

    def check_value(self):
        """Check current configuration."""
        return self._ccnorm.check_value(self._normalized)

    def get_config_type_template(self):
        """Return a tmeplate dictionary of normalized config."""
        return self._ccnorm.get_config_type_template()

    def __getitem__(self, index):
        """Return normalized strength of a given magnet."""
        return self._normalized[index]

    def __setitem__(self, index, value):
        """Set normalized strength of a given magnet."""
        self._normalized[index] = Value



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
