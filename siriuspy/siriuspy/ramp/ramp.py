"""Module with BO ramp class."""

import numpy as _np
from copy import deepcopy as _dcopy

from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE as _MAX_WFMSIZE
from siriuspy.servconf.srvconfig import ConfigSrv as _ConfigSrv
from siriuspy.ramp.exceptions import RampInvalidDipoleWfmParms as \
    _RampInvalidDipoleWfmParms
from siriuspy.ramp.exceptions import RampInvalidNormConfig as \
    _RampInvalidNormConfig
from siriuspy.ramp.conn import ConnConfig_BORamp as _CCBORamp
from siriuspy.ramp.conn import ConnConfig_BONormalized as _CCBONormalized
from siriuspy.ramp.waveform import WaveformDipole as _WaveformDipole
from siriuspy.ramp.waveform import Waveform as _Waveform


class BoosterNormalized(_ConfigSrv):
    """Booster normalized configuration."""

    _conn = _CCBONormalized()
    _manames = None

    def __init__(self, name=None):
        """Constructor."""
        _ConfigSrv.__init__(self, name=name)
        # init class _psnames
        if BoosterNormalized._manames is None:
            BoosterNormalized._manames = \
                list(self.get_config_type_template().keys())

    @property
    def maname(self):
        """List of power supply names."""
        return BoosterNormalized._manames.copy()

    def _get_item(self, index):
        return float(self._configuration[index])

    def _set_item(self, index, value):
        self._configuration[index] = float(value)

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
        self._wfms_changed = True  # so that waveforms need calculation again

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
        self._wfms_changed = True

    def configsrv_load_normalized_configs(self):
        """Load normalized configurations from config server."""
        # load normalized configurations one by one
        for config in self._normalized_configs.values():
            config.configsrv_load()
        self._wfms_changed = True

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
        self._wfms_changed = True

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
    def delay_rf(self):
        """RF delay."""
        return self._configuration['rf_parameters']['delay']

    @delay_rf.setter
    def delay_rf(self, value):
        """Set RF delay."""
        self._configuration['rf_parameters']['delay'] = value
        self._synchronized = False

    @property
    def ramp_dipole_delay(self):
        """Dipole ramp delay."""
        return self._configuration['ramp_dipole']['delay']

    @ramp_dipole_delay.setter
    def ramp_dipole_delay(self, value):
        """Set power supplies general delay [us]."""
        value = float(value)
        self._configuration['ramp_dipole']['delay'] = value
        self._synchronized = False

    @property
    def ramp_dipole_duration(self):
        """Dipole ramp duration."""
        return self._configuration['ramp_dipole']['duration']

    @ramp_dipole_duration.setter
    def ramp_dipole_duration(self, value):
        """Set dipole ramp duration."""
        self._configuration['ramp_dipole']['duration'] = float(value)
        self._synchronized = False
        self._wfms_changed = True

    @property
    def ramp_dipole_time(self):
        """Dipole ramp times."""
        return list(self._configuration['ramp_dipole']['time'])

    @ramp_dipole_time.setter
    def ramp_dipole_time(self, value):
        """Set dipole ramp times."""
        if len(value) != 8:
            raise ValueError('Invalid number of elements int dipole ramp time')
        for v in value:
            if v > self.ramp_dipole_duration:
                raise ValueError(('All dipole ramp times should be '
                                  'smaller than ramp duration.'))
        self._configuration['ramp_dipole']['time'] = list(value)
        self._synchronized = False
        self._wfms_changed = True

    @property
    def ramp_dipole_energy(self):
        """Dipole ramp energy."""
        return list(self._configuration['ramp_dipole']['energy'])

    @ramp_dipole_energy.setter
    def ramp_dipole_energy(self, value):
        """Set dipole ramp energies."""
        if len(value) != 8:
            raise ValueError(('Invalid number of elements in '
                              'dipole ramp energy'))
        for v in value:
            if v > self.ramp_dipole_duration:
                raise ValueError(('All dipole ramp times should be '
                                  'smaller than ramp duration.'))
        self._configuration['ramp_dipole']['energy'] = list(value)
        self._synchronized = False
        self._wfms_changed = True

    @property
    def ramp_dipole_wfm_nrpoints(self):
        """Dipole ramp waveform number of points."""
        return self._configuration['ramp_dipole']['wfm_nrpoints']

    @ramp_dipole_wfm_nrpoints.setter
    def ramp_dipole_wfm_nrpoints(self, value):
        """Set dipole ramp waveform number of points."""
        value = int(value)
        if value > _MAX_WFMSIZE:
            raise ValueError('Invalid number of points for waveforms.')
        self._configuration['ramp_dipole']['wfm_nrpoints'] = value
        self._synchronized = False
        self._wfms_changed = True

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
        self._wfms_changed = True

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

    def get_waveform_currents(self, psname):
        """Return waveform for a given power supply."""
        self._update_waveforms()
        waveform = self._waveforms[psname]
        return waveform.currents.copy()

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
            'delay_rf [us]',
            'ramp_dipole_delay [us]',
            'ramp_dipole_duration [ms]',
            'ramp_dipole_time_energy [ms] [GeV]',
            'normalized_configs [ms] [name]',
        )
        st = ''
        maxlen = max(tuple(len(l) for l in labels) + (len('name'),))
        strfmt1 = '{:<' + str(maxlen) + 's}: {}\n'
        strfmt2 = strfmt1.replace('{}', '{:.6f} {:+.6f}')
        strfmt3 = strfmt1.replace('{}', '{:.6f} {}')
        st += strfmt1.format('name', self.name)
        st += strfmt1.format(labels[0], self.delay_rf)
        st += strfmt1.format(labels[1], self.ramp_dipole_delay)
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
        self._wfms_changed = True

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
                self._wfms_changed = True
                norm_configs[name] = BoosterNormalized(name)
        self._normalized_configs = norm_configs

    def _update_waveform(self, maname):
        if 'BO-Fam:MA-B' not in self._waveforms:
            self._update_waveform_dipole()
        if maname != 'BO-Fam:MA-B':
            self._update_waveform_not_dipole(maname)

    def _update_waveform_not_dipole(self, maname):
        self._update_normalized_configs()
        times = self.normalized_configs_time
        names = self.normalized_configs_name
        times, names = \
            [list(x) for x in zip(*sorted(zip(times, names),
             key=lambda pair: pair[0]))]  # sort by time
        # build strength
        stren = []
        for i in range(len(times)):
            nconfig = self._normalized_configs[names[i]]
            if maname not in nconfig:
                raise _RampInvalidNormConfig
            stren.append(nconfig[maname])
        # get dipole
        if 'BO-Fam:MA-B' not in self._waveforms:
            self._update_waveform_dipole()



        energy = self._configuration['ramp_dipole']['energy']

    def _update_waveform_dipole(self):
        time = self._configuration['ramp_dipole']['time']
        energy = self._configuration['ramp_dipole']['energy']
        duration = self._configuration['ramp_dipole']['duration']
        wfm_nrpoints = self._configuration['ramp_dipole']['wfm_nrpoints']
        interval = duration / (wfm_nrpoints - 1.0)
        indices = [round(t/interval) for t in time]
        dipole = _WaveformDipole(
            scale=1.0,
            start_value=energy[0],
            stop_value=energy[0],
            boundary_indices=indices,
            boundary_values=energy,
            wfm_nrpoints=wfm_nrpoints,
            duration=duration)
        if not dipole.check():
            raise _RampInvalidDipoleWfmParms()
        self._waveforms['BO-Fam:MA-B'] = dipole
