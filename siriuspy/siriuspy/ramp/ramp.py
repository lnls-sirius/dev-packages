"""Module with BO ramp class."""

import numpy as _np
from copy import deepcopy as _dcopy

from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE as _MAX_WFMSIZE
from siriuspy.servconf.srvconfig import ConfigSrv as _ConfigSrv
# from siriuspy.magnet.util import magnet_class as _magnet_class
from siriuspy.magnet.util import get_section_dipole_name as \
    _get_section_dipole_name
from siriuspy.magnet.util import get_magnet_family_name as \
    _get_magnet_family_name
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
        for config in self._normalized_configs.values():
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
            raise _RampInvalidDipoleWfmParms(
                'Invalid number of elements int dipole ramp time')
        for v in value:
            if v > self.ramp_dipole_duration:
                raise _RampInvalidDipoleWfmParms(
                    'All dipole ramp times should be '
                    'smaller than ramp duration.')
        # TODO: verify monotonic ascending times
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
            raise _RampInvalidDipoleWfmParms('Invalid number of elements in '
                                             'dipole ramp energy')
        for v in value:
            if v > self.ramp_dipole_duration:
                raise _RampInvalidDipoleWfmParms(
                    'All dipole ramp times should be '
                    'smaller than ramp duration.')
        # TODO: verify values
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
            raise _RampInvalidDipoleWfmParms('Invalid number of points for '
                                             'waveforms.')
        self._configuration['ramp_dipole']['wfm_nrpoints'] = value
        self._synchronized = False
        self._wfms_changed = True

    @property
    def ramp_start_value(self):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        return self._waveforms['BO-Fam:MA-B'].start_value

    @ramp_start_value.setter
    def ramp_start_value(self, value):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        w = self._waveforms['BO-Fam:MA-B']
        try:
            w.start_value = value
        except ValueError as e:
            raise _RampInvalidDipoleWfmParms(e)
        self._configuration['ramp_dipole']['energy'][0] = value
        self._configuration['ramp_dipole']['energy'][-1] = value
        # TODO: verify values
        self._synchronized = False
        self._wfms_changed = True

    @property
    def rampup_start_value(self):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        return self._waveforms['BO-Fam:MA-B'].rampup_start_value

    @rampup_start_value.setter
    def rampup_start_value(self, value):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        w = self._waveforms['BO-Fam:MA-B']
        try:
            w.rampup_start_value = value
        except ValueError as e:
            raise _RampInvalidDipoleWfmParms(e)
        self._configuration['ramp_dipole']['energy'][1] = value
        # TODO: verify values
        self._synchronized = False
        self._wfms_changed = True

    @property
    def rampup_start_time(self):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        return self._waveforms['BO-Fam:MA-B'].rampup_start_time

    @rampup_start_time.setter
    def rampup_start_time(self, value):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        w = self._waveforms['BO-Fam:MA-B']
        try:
            w.rampup_start_time = value
        except ValueError as e:
            raise _RampInvalidDipoleWfmParms(e)
        self._configuration['ramp_dipole']['time'][1] = value
        # TODO: > [0] and < [2]
        self._synchronized = False
        self._wfms_changed = True

    @property
    def rampup_stop_value(self):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        return self._waveforms['BO-Fam:MA-B'].rampup_stop_value

    @rampup_stop_value.setter
    def rampup_stop_value(self, value):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        w = self._waveforms['BO-Fam:MA-B']
        try:
            w.rampup_stop_value = value
        except ValueError as e:
            raise _RampInvalidDipoleWfmParms(e)
        self._configuration['ramp_dipole']['energy'][2] = value
        # TODO: verify values
        self._synchronized = False
        self._wfms_changed = True

    @property
    def rampup_stop_time(self):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        return self._waveforms['BO-Fam:MA-B'].rampup_stop_time

    @rampup_stop_time.setter
    def rampup_stop_time(self, value):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        w = self._waveforms['BO-Fam:MA-B']
        try:
            w.rampup_stop_time = value
        except ValueError as e:
            raise _RampInvalidDipoleWfmParms(e)
        self._configuration['ramp_dipole']['time'][2] = value
        # TODO: > [1] and < [3]
        self._synchronized = False
        self._wfms_changed = True

    @property
    def ramp_plateau_value(self):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        return self._waveforms['BO-Fam:MA-B'].plateau_value

    @ramp_plateau_value.setter
    def ramp_plateau_value(self, value):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        w = self._waveforms['BO-Fam:MA-B']
        try:
            w.plateau_value = value
        except ValueError as e:
            raise _RampInvalidDipoleWfmParms(e)
        self._configuration['ramp_dipole']['energy'][3] = value
        self._configuration['ramp_dipole']['energy'][4] = value
        # TODO: verify values
        self._synchronized = False
        self._wfms_changed = True

    @property
    def rampdown_start_value(self):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        return self._waveforms['BO-Fam:MA-B'].rampdown_start_value

    @rampdown_start_value.setter
    def rampdown_start_value(self, value):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        w = self._waveforms['BO-Fam:MA-B']
        try:
            w.rampdown_start_value = value
        except ValueError as e:
            raise _RampInvalidDipoleWfmParms(e)
        self._configuration['ramp_dipole']['energy'][5] = value
        # TODO: verify values
        self._synchronized = False
        self._wfms_changed = True

    @property
    def rampdown_start_time(self):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        return self._waveforms['BO-Fam:MA-B'].rampdown_start_time

    @rampdown_start_time.setter
    def rampdown_start_time(self, value):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        w = self._waveforms['BO-Fam:MA-B']
        try:
            w.rampdown_start_time = value
        except ValueError as e:
            raise _RampInvalidDipoleWfmParms(e)
        self._configuration['ramp_dipole']['time'][5] = value
        # TODO: > [4] and < [6]
        self._synchronized = False
        self._wfms_changed = True

    @property
    def rampdown_stop_value(self):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        return self._waveforms['BO-Fam:MA-B'].rampdown_stop_value

    @rampdown_stop_value.setter
    def rampdown_stop_value(self, value):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        w = self._waveforms['BO-Fam:MA-B']
        try:
            w.rampdown_stop_value = value
        except ValueError as e:
            raise _RampInvalidDipoleWfmParms(e)
        self._configuration['ramp_dipole']['energy'][6] = value
        # TODO: verify values
        self._synchronized = False
        self._wfms_changed = True

    @property
    def rampdown_stop_time(self):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        return self._waveforms['BO-Fam:MA-B'].rampdown_stop_time

    @rampdown_stop_time.setter
    def rampdown_stop_time(self, value):
        """Return."""
        self._update_waveform('BO-Fam:MA-B')
        w = self._waveforms['BO-Fam:MA-B']
        try:
            w.rampdown_stop_time = value
        except ValueError as e:
            raise _RampInvalidDipoleWfmParms(e)
        self._configuration['ramp_dipole']['time'][6] = value
        # TODO: > [5] and < [7]
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
        self._set_normalized_configs(nconfigs)
        self._wfms_changed = True

    def normalized_configs_insert(self, time, name=None, nconfig=None):
        """Insert a normalized configuration."""
        if not isinstance(name, str) or len(name) == 0:
            # get name from BoosterNormalized constructor
            bn = BoosterNormalized()
            name = bn.name
        # add new entry to list with normalized configs metadata
        otimes = self.normalized_configs_time
        onames = self.normalized_configs_name
        times = otimes.copy()
        names = onames.copy()
        if time in times:
            if nconfig is not None:
                index = times.index(time)
                names[index] = name
            else:
                raise _RampInvalidNormConfig(
                    'Invalid interpolation at existing time value.')
        else:
            times.append(time)
            names.append(name)
        times, names = \
            [list(x) for x in zip(*sorted(zip(times, names),
             key=lambda pair: pair[0]))]  # sort by time
        nconfigs = [[times[i], names[i]] for i in range(len(times))]
        self._set_normalized_configs(nconfigs)
        self._update_normalized_configs()

        # interpolate nconfig, if necessary
        if nconfig is None:
            nconfig = self._normalized_configs[name].get_config_type_template()
            for k in nconfig.keys():
                # ovalues = [0.0 for n in onames]
                if k == 'BO-Fam:MA-B':
                    # TODO: when k == 'BO-Fam:MA-B' we have to use waveform
                    # linear numpy interpolation with left=right=None
                    pass
                else:
                    # linear numpy interpolation with left=right=None
                    ovalues = [self._normalized_configs[n][k] for n in onames]
                    nconfig[k] = _np.interp(time, otimes, ovalues)

        # set config energy appropriately
        indices = self._conv_times_2_indices([time])
        strengths = self.get_waveform_strengths('BO-Fam:MA-B')
        strength = _np.interp(indices[0],
                              list(range(self.ramp_dipole_wfm_nrpoints)),
                              strengths)
        nconfig['BO-Fam:MA-B'] = strength

        # normalized configuration was given
        self._normalized_configs[name].configuration = nconfig

        return name

    def normalized_configs_change_time(self, index, new_time):
        """Change the time of an existing config either by index or name."""
        names = self.normalized_configs_name
        if isinstance(index, str):
            index = names.index(index)
        times = self.normalized_configs_time
        times[index] = new_time
        nconfigs = [[times[i], names[i]] for i in range(len(times))]
        self._set_normalized_configs(nconfigs)
        self._wfms_changed = True

    # --- API for waveforms ---

    # @property
    # def dipole_waveform(self):
    #     """Dipole waveform."""
    #     self._update_waveform('BO-Fam:MA-B')
    #     self._wfms_changed = True
    #     return self._waveforms['BO-Fam:MA-B']

    def get_waveform(self, maname):
        """Return waveform for a given power supply."""
        self._update_waveform(maname)
        waveform = self._waveforms[maname]
        return _dcopy(waveform)

    def set_waveform(self, maname, waveform):
        """Set waveform for a given power supply."""
        # self._update_waveform(maname)
        self._waveforms[maname] = _dcopy(waveform)

    def get_waveform_times(self):
        """Return ramp energy at a given time."""
        maname = 'BO-Fam:MA-B'
        self._update_waveform(maname)
        times = self._waveforms[maname].times
        return times

    def get_waveform_currents(self, maname):
        """Return waveform current for a given power supply."""
        self._update_waveform(maname)
        waveform = self._waveforms[maname]
        return waveform.currents.copy()

    def get_waveform_strengths(self, maname):
        """Return waveform strength for a given power supply."""
        self._update_waveform(maname)
        waveform = self._waveforms[maname]
        return waveform.strengths.copy()

    def get_waveform_energy(self, time):
        """Return ramp energy at a given time."""
        times = self.get_waveform_times()
        energies = self._waveforms['BO-Fam:MA-B'].strengths
        energy = _np.interp(time, times, energies)
        return energy

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
        return _dcopy(self._normalized_configs[name])

    def _set_item(self, name, value):
        self._normalized_configs[name] = value
        self._wfms_changed = True

    def _set_configuration(self, value):
        self._configuration = _dcopy(value)
        self._update_normalized_configs()

    def _set_normalized_configs(self, value):
        """Set normalized config list."""
        self._configuration['normalized_configs*'] = _dcopy(value)
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

        # update dipole if necessary
        if self._wfms_changed or 'BO-Fam:M-B' not in self._waveforms:
            self._update_waveform_dipole()
        self._wfms_changed = False

        # update family if necessary
        family = _get_magnet_family_name(maname)
        if family is not None and family not in self._waveforms:
            self._update_waveform(family)

        # update magnet waveform if it is not a dipole
        dipole = _get_section_dipole_name(maname)
        if dipole is not None and maname not in self._waveforms:
            self._update_waveform_not_dipole(maname, dipole, family)

    def _update_waveform_not_dipole(self, maname, dipole, family=None):
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
            if maname not in nconfig.configuration:
                raise _RampInvalidNormConfig
            stren.append(nconfig[maname])

        # interpolate strengths
        wfm_nrpoints = self._configuration['ramp_dipole']['wfm_nrpoints']
        indices = self._conv_times_2_indices(times)
        wfm_indices = [i for i in range(wfm_nrpoints)]
        strengths = _np.interp(wfm_indices, indices, stren)

        # create waveform object with given strengths
        dipole = self._waveforms[dipole]
        if family is not None:
            family = self._waveforms[family]
        self._waveforms[maname] = _Waveform(maname=maname,
                                            dipole=dipole,
                                            family=family,
                                            strengths=strengths)

    def _update_waveform_dipole(self):
        time = self._configuration['ramp_dipole']['time']
        energy = self._configuration['ramp_dipole']['energy']
        duration = self._configuration['ramp_dipole']['duration']
        wfm_nrpoints = self._configuration['ramp_dipole']['wfm_nrpoints']
        indices = self._conv_times_2_indices(time)
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

    def _conv_times_2_indices(self, times):
        duration = self._configuration['ramp_dipole']['duration']
        wfm_nrpoints = self._configuration['ramp_dipole']['wfm_nrpoints']
        interval = duration / (wfm_nrpoints - 1.0)
        indices = [round(t/interval) for t in times]
        return indices
