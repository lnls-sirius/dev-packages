"""Module with BO ramp class."""

from copy import deepcopy as _dcopy

from siriuspy.ramp.conn import ConnConfig_BORamp as _CCBORamp
from siriuspy.ramp.conn import ConnConfig_BONormalized as _CCBONormalized
from siriuspy.ramp.srvconfig import ConfigSrv as _ConfigSrv


class BoosterNormalized(_ConfigSrv):
    """Booster normalized configuration."""

    _conn = _CCBONormalized()

    def __init__(self, name=None):
        """Constructor."""
        _ConfigSrv.__init__(self, name=name)

    def _get_item(self, index):
        return self._configuration[index]

    def _set_item(self, index, value):
        self._configuration[index] = value

    def _set_configuration(self, value):
        self._configuration = value


class BoosterRamp(_ConfigSrv):
    """Booster ramp class."""

    # ConfigSrv connector object
    _conn = _CCBORamp()

    def __init__(self, name=None):
        """Constructor."""
        _ConfigSrv.__init__(self, name=name)
        self._update_normalized_configs()

    # --- BOConfig API ---

    @property
    def configsrv_synchronized(self):
        """Synchronization state between object and configuration in server."""
        if not self._synchronized:
            return False
        for config in self.normalized_configs.values():
            if not config.configsrv_synchronized:
                return False
        return True

    def configsrv_load(self):
        """Load configuration from config server."""
        # load booster ramp configuration
        _ConfigSrv.configsrv_load(self)
        self._synchronized = False  # in case cannot load norm config
        # update normalized configs
        self._update_normalized_configs()
        # load normalized configurations one by one
        for config in self._normalized_configs.values():
            config.configsrv_load()
        self._synchronized = True  # all went well

    def configsrv_load_normalized_configs(self):
        """Load normalized configurations from config server."""
        # load normalized configurations one by one
        for config in self._normalized_configs.values():
            config.configsrv_load()

    def configsrv_update(self):
        """Update configuration in config server."""
        # update ramp config
        _ConfigSrv.configsrv_update(self)
        self._synchronized = False  # in case cannot load norm config
        # update or save normalized configs
        for config in self.normalized_configs.values():
            if config.configsrv_synchronized:
                # already exists, just update
                config.configsrv_update()
            else:
                if config.configsrv_check():
                    # already exists, just update
                    config.configsrv_update()
                else:
                    # create new normalized configuration
                    config.configsrv_save()
        self._synchronized = True  # all went well

    def configsrv_save(self):
        """Save configuration to config server."""
        # save booster ramp
        _ConfigSrv.configsrv_save(self)
        self._synchronized = False  # in case cannot load norm config
        # save each normalized configuration
        for config in self._normalized_configs.values():
            config.configsrv_save()
        self._synchronized = True  # all went well

    @property
    def delay_pwrsupply(self):
        """Power supplies general delay [us]."""
        return _dcopy(self._configuration['pwrsupply_delay'])

    @delay_pwrsupply.setter
    def delay_pwrsupply(self, value):
        """Set power supplies general delay [us]."""
        self._configuration['pwrsupply_delay'] = value
        self._synchronized = False

    @property
    def delay_rf(self):
        """RF delay."""
        return self._configuration['rf_parameters']['delay']

    @delay_rf.setter
    def delay_rf(self, value):
        """Set RF delay."""
        self._configuration['rf_parameters']['delay'] = value
        self._synchronized = False

    @property
    def ramp_dipole_duration(self):
        """Dipole ramp duration."""
        return self._configuration['ramp_dipole']['duration']

    @ramp_dipole_duration.setter
    def ramp_dipole_duration(self, value):
        """Set dipole ramp duration."""
        self._configuration['ramp_dipole']['duration'] = value
        self._synchronized = False

    @property
    def ramp_dipole_time(self):
        """Dipole ramp time."""
        return _dcopy(self._configuration['ramp_dipole']['time'])

    @ramp_dipole_time.setter
    def ramp_dipole_time(self, value):
        """Set dipole ramp time."""
        self._configuration['ramp_dipole']['time'] = _dcopy(value)
        self._synchronized = False

    @property
    def ramp_dipole_energy(self):
        """Dipole ramp energy."""
        return _dcopy(self._configuration['ramp_dipole']['energy'])

    @ramp_dipole_energy.setter
    def ramp_dipole_energy(self, value):
        """Set dipole ramp energy."""
        self._configuration['ramp_dipole']['energy'] = _dcopy(value)
        self._synchronized = False

    @property
    def normalized_configs(self):
        """Normalized config list."""
        return _dcopy(self._configuration['normalized_configs*'])

    @normalized_configs.setter
    def normalized_configs(self, value):
        """Set normalized config list."""
        self._configuration['normalized_configs*'] = _dcopy(value)
        self._update_normalized_configs()

    def get_normalized_configs_time(self):
        """Return time instants corresponding to normalized configs."""
        time, _ = zip(*self._configuration['normalized_configs*'])
        return time

    def get_normalized_configs_name(self):
        """Return names corresponding to normalized configs."""
        _, name = zip(*self._configuration['normalized_configs*'])
        return name

    def check_value(self):
        """Check current configuration."""
        # firs check ramp config
        if not _ConfigSrv.check_value(self):
            return False
        # then check each normalized config
        for config in self._normalized_configs.values():
            if not config.check_value():
                return False
        return True

    def __len__(self):
        """Number of normalized configurations."""
        return len(self._normalized_configs)

    def _get_item(self, name):
        return self._normalized_configs[name]

    def _set_item(self, name, value):
        self._normalized_configs[name] = value

    def _set_configuration(self, value):
        self._configuration = _dcopy(value)
        self._update_normalized_configs()

    def _update_normalized_configs(self):
        self._synchronized = False
        self._normalized_configs = dict()
        if self._configuration is None:
            return
        for t, name in self._configuration['normalized_configs*']:
            self._normalized_configs[name] = BoosterNormalized(name)
