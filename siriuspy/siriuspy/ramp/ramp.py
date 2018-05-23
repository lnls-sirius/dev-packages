"""Module with BO ramp class."""

import numpy as _np
from copy import deepcopy as _dcopy

from siriuspy.ramp.conn import ConnConfig_BORamp as _CCBORamp
from siriuspy.ramp.conn import ConnConfig_BONormalized as _CCBONormalized
from siriuspy.ramp.srvconfig import ConfigSrv as _ConfigSrv
# from siriuspy.ramp import exceptions as _exceptions


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

    def __str__(self):
        """String representation of configuration."""
        if not self._configuration:
            st = 'name: {}'.format(self.name)
            return st
        st = ''
        k = tuple(self._configuration.keys())
        v = tuple(self._configuration.values())
        maxlen = max(tuple(len(ky) for ky in k) + (len('name'),))
        fmtstr1 = '{:<'+str(maxlen)+'}: {:+.6f}\n'
        fmtstr2 = fmtstr1.replace('{:+.6f}', '{}')
        st = fmtstr2.format('name', self.name)
        for i in range(len(k)):
            st += fmtstr1.format(k[i], v[i])
        return st


class BoosterRamp(_ConfigSrv):
    """Booster ramp class."""

    # ConfigSrv connector object
    _conn = _CCBORamp()

    def __init__(self, name=None):
        """Constructor."""
        _ConfigSrv.__init__(self, name=name)
        self._normalized_configs = dict()
        self._waveforms = dict()
        # self._update_normalized_configs()

    # --- ConfigSrv API ---

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
        for config in self._normalized_configs.values():
            if config.configsrv_synchronized and config.configsrv_check():
                # already exists, just update
                config.configsrv_update()
            else:
                # save a new normalized configuration
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
        return self._configuration['delay_pwrsupply']

    @delay_pwrsupply.setter
    def delay_pwrsupply(self, value):
        """Set power supplies general delay [us]."""
        self._configuration['delay_pwrsupply'] = value
        self._synchronized = False

    @property
    def delay_rf(self):
        """RF delay."""
        return self._configuration['rf_parameters']['delay_rf']

    @delay_rf.setter
    def delay_rf(self, value):
        """Set RF delay."""
        self._configuration['rf_parameters']['delay_rf'] = value
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

    @property
    def ramp_dipole_energy(self):
        """Dipole ramp energy."""
        return _dcopy(self._configuration['ramp_dipole']['energy'])

    def set_ramp_dipole(self, time, energy):
        """Set dipole ramp."""
        self._configuration['ramp_dipole']['time'] = _dcopy(time)
        self._configuration['ramp_dipole']['energy'] = _dcopy(energy)
        self._synchronized = False

    # @ramp_dipole_time.setter
    # def ramp_dipole_time(self, value):
    #     """Set dipole ramp time."""
    #     self._configuration['ramp_dipole']['time'] = _dcopy(value)
    #     self._synchronized = False
    #
    # @ramp_dipole_energy.setter
    # def ramp_dipole_energy(self, value):
    #     """Set dipole ramp energy."""
    #     self._configuration['ramp_dipole']['energy'] = _dcopy(value)
    #     self._synchronized = False

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

    # --- API for manipulating normalized configurations ---

    @property
    def normalized_configs(self):
        """Normalized config list."""
        return _dcopy(self._configuration['normalized_configs*'])

    @normalized_configs.setter
    def normalized_configs(self, value):
        """Set normalized config list."""
        self._configuration['normalized_configs*'] = _dcopy(value)
        self._update_normalized_configs()

    @property
    def normalized_configs_time(self):
        """Return time instants corresponding to normalized configs."""
        time, _ = zip(*self._configuration['normalized_configs*'])
        return list(time)

    @property
    def normalized_configs_name(self):
        """Return names corresponding to normalized configs."""
        _, name = zip(*self._configuration['normalized_configs*'])
        return list(name)

    def normalized_configs_delete(self, index):
        """Delete a normalized config either by its index or its name."""
        names = self.normalized_configs_name
        if isinstance(index, str):
            index = names.index(index)
        times = self.normalized_configs_time
        names.pop(index)
        times.pop(index)
        nconfigs = [[times[i], names[i]] for i in range(len(times))]
        self.normalized_configs = nconfigs

    def normalized_configs_insert(self, time, name=None, nconfig=None):
        """Insert a normalized configuration."""
        if not isinstance(name, str):
            # get name from BoosterNormalized constructor
            bn = BoosterNormalized()
            name = bn.name
        # add new entry to list with normalized configs metadata
        otimes = self.normalized_configs_time
        onames = self.normalized_configs_name
        times = otimes.copy()
        names = onames.copy()
        if time in times:
            index = times.index(time)
            names[index] = name
        else:
            times.append(time)
            names.append(name)
        times, names = \
            [list(x) for x in zip(*sorted(zip(times, names),
             key=lambda pair: pair[0]))]  # sort by time
        nconfigs = [[times[i], names[i]] for i in range(len(times))]
        self.normalized_configs = nconfigs
        self._update_normalized_configs()

        # interpolate nconfig, if necessary
        if nconfig is None:
            nconfig = self._normalized_configs[name].get_config_type_template()
            for k in nconfig.keys():
                # ovalues = [0.0 for n in onames]
                if k == 'BO-Fam:MA-B':
                    # TODO: when k == 'BO-Fam:MA-B' we have to use waveform
                    # linear numpy interpolation with left=right=None
                    ovalues = [self._normalized_configs[n][k] for n in onames]
                    nconfig[k] = _np.interp(time, otimes, ovalues)
                else:
                    # linear numpy interpolation with left=right=None
                    ovalues = [self._normalized_configs[n][k] for n in onames]
                    nconfig[k] = _np.interp(time, otimes, ovalues)

        # normalized configuration was given
        self._normalized_configs[name].configuration = nconfig

        return name

    # --- API for waveforms ---



    # --- private methods ---

    def __len__(self):
        """Number of normalized configurations."""
        return len(self._normalized_configs)

    def __str__(self):
        """String representation of configuration."""
        if not self._configuration:
            st = 'name: {}'.format(self.name)
            return st
        labels = (
            'delay_pwrsupply [us]',
            'delay_rf [us]',
            'ramp_dipole_duration [s]',
            'ramp_dipole_time_energy [s] [GeV]',
            'normalized_configs [s] [name]',
        )
        st = ''
        maxlen = max(tuple(len(l) for l in labels) + (len('name'),))
        strfmt1 = '{:<' + str(maxlen) + 's}: {}\n'
        strfmt2 = strfmt1.replace('{}', '{:.6f} {:+.6f}')
        strfmt3 = strfmt1.replace('{}', '{:.6f} {}')
        st += strfmt1.format('name', self.name)
        st += strfmt1.format(labels[0], self.delay_pwrsupply)
        st += strfmt1.format(labels[1], self.delay_rf)
        st += strfmt1.format(labels[2], self.ramp_dipole_duration)
        st += strfmt1.format(labels[3], '')
        time = self.ramp_dipole_time
        energy = self.ramp_dipole_energy
        for i in range(len(time)):
            st += strfmt2.format('', time[i], energy[i])
        st += strfmt1.format(labels[4], '')
        time = self.normalized_configs_time
        name = self.normalized_configs_name
        for i in range(len(time)):
            st += strfmt3.format('', time[i], name[i])
        return st

    def _get_item(self, name):
        return self._normalized_configs[name]

    def _set_item(self, name, value):
        self._normalized_configs[name] = value

    def _set_configuration(self, value):
        self._configuration = _dcopy(value)
        self._update_normalized_configs()

    def _update_normalized_configs(self):
        norm_configs = dict()
        for time, name in self._configuration['normalized_configs*']:
            if name in self._normalized_configs:
                norm_configs[name] = self._normalized_configs[name]
            else:
                self._synchronized = False
                norm_configs[name] = BoosterNormalized(name)
        self._normalized_configs = norm_configs

    def _update_waveforms(self):
        names = tuple(self._normalized_configs.keys())
        if not names:
            return
        else:
            psnames = tuple(self._normalized_configs[names[0]].keys())
