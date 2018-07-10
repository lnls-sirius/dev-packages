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

    def __init__(self, name=None):
        """Constructor."""
        _ConfigSrv.__init__(self, name=name)
        self.configuration = self.get_config_type_template()

    @property
    def manames(self):
        """List of power supply names."""
        return list(self._configuration.keys())

    def _get_item(self, index):
        return float(self._configuration[index])

    def _set_item(self, index, value):
        self._configuration[index] = float(value)

    def _set_configuration(self, value):
        self._configuration = value

    def __str__(self):
        """Return string representation of configuration."""
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
        self._nconfigs = dict()
        self._waveforms = dict()
        self.configuration = self.get_config_type_template()

    # --- ConfigSrv API ---

    @property
    def configsrv_synchronized(self):
        """Return synchronization state between object and config in server."""
        if not self._synchronized:
            return False
        for config in self._nconfigs.values():
            if not config.configsrv_synchronized:
                return False
        return True

    def configsrv_load(self):
        """Load configuration from config server."""
        # load booster ramp configuration
        _ConfigSrv.configsrv_load(self)
        self._synchronized = False  # in case cannot load norm config
        # update normalized configs
        self._update_normalized_configs_objects()
        # load normalized configurations one by one
        for config in self._nconfigs.values():
            config.configsrv_load()
        self._synchronized = True  # all went well
        self._invalidate_waveforms(True)

    def configsrv_load_normalized_configs(self):
        """Load normalized configurations from config server."""
        # load normalized configurations one by one
        for config in self._nconfigs.values():
            config.configsrv_load()
        self._invalidate_waveforms()

    def configsrv_update(self):
        """Update configuration in config server."""
        # update ramp config
        _ConfigSrv.configsrv_update(self)
        self._synchronized = False  # in case cannot load norm config
        # update or save normalized configs
        for config in self._nconfigs.values():
            if config.configsrv_synchronized and config.configsrv_exist():
                # already exists, just update
                config.configsrv_update()
            else:
                # save a new normalized configuration
                config.configsrv_save()
        self._synchronized = True  # all went well
        self._invalidate_waveforms(True)  # TODO: check if it is necessary

    def configsrv_save(self):
        """Save configuration to config server."""
        # save booster ramp
        _ConfigSrv.configsrv_save(self)
        self._synchronized = False  # in case cannot load norm config
        # save each normalized configuration
        for config in self._nconfigs.values():
            config.configsrv_save()
        self._synchronized = True  # all went well

    # --- bo_ramp configuration ---

    @property
    def injection_time(self):
        """Injection time instant."""
        return self._configuration['injection_time']

    @injection_time.setter
    def injection_time(self, value):
        """Set injection time instant."""
        # TODO: verify value
        if value == self._configuration['injection_time']:
            return
        self._configuration['injection_time'] = value
        self._synchronized = False

    @property
    def ejection_time(self):
        """Ejection time instant."""
        return self._configuration['ejection_time']

    @ejection_time.setter
    def ejection_time(self, value):
        """Set ejection time instant."""
        # TODO: verify value
        if value == self._configuration['ejection_time']:
            return
        self._configuration['ejection_time'] = value
        self._synchronized = False

    # ---- rf_parameters ----

    @property
    def delay_rf(self):
        """RF delay."""
        return self._configuration['rf_parameters']['delay']

    @delay_rf.setter
    def delay_rf(self, value):
        """Set RF delay."""
        # TODO: verify value
        if value == self._configuration['rf_parameters']['delay']:
            return
        self._configuration['rf_parameters']['delay'] = value
        self._synchronized = False

    # ---- normalized_configs* ----

    @property
    def normalized_configs(self):
        """List of normalized config."""
        return _dcopy(self._configuration['normalized_configs*'])

    @property
    def normalized_configs_times(self):
        """Return time instants corresponding to normalized configs."""
        time, _ = zip(*self._configuration['normalized_configs*'])
        return list(time)

    @property
    def normalized_configs_names(self):
        """Return names corresponding to normalized configs."""
        _, name = zip(*self._configuration['normalized_configs*'])
        return list(name)

    def normalized_configs_delete(self, index):
        """Delete a normalized config either by its index or its name."""
        names = self.normalized_configs_names
        if isinstance(index, str):
            index = names.index(index)
        times = self.normalized_configs_times
        names.pop(index)
        times.pop(index)
        nconfigs = [[times[i], names[i]] for i in range(len(times))]
        self._set_normalized_configs(nconfigs)
        self._synchronized = False
        self._invalidate_waveforms()

    def normalized_configs_insert(self, time, name=None, nconfig=None):
        """Insert a normalized configuration."""
        # process normalized config name
        if not isinstance(name, str) or len(name) == 0:
            bn = BoosterNormalized()
            name = bn.name

        # add new entry to list with normalized configs metadata
        otimes = self.normalized_configs_times
        onames = self.normalized_configs_names
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

        # triggers updates for new normalized configs table
        self._set_normalized_configs(nconfigs)
        self._update_normalized_configs_objects()  # TODO: invoked twice?

        # interpolate nconfig, if necessary
        if nconfig is None:
            nconfig = self._nconfigs[name].get_config_type_template()
            for k in nconfig.keys():
                if k != 'BO-Fam:MA-B':
                    ovalues = [self._nconfigs[n][k] for n in onames]
                    nconfig[k] = _np.interp(time, otimes, ovalues)

        # set config energy appropriately
        indices = self._conv_times_2_indices([time])
        strengths = self.waveform_get_strengths('BO-Fam:MA-B')
        strength = _np.interp(indices[0],
                              list(range(self.ramp_dipole_wfm_nrpoints)),
                              strengths)
        nconfig['BO-Fam:MA-B'] = strength

        # normalized configuration was given
        self._nconfigs[name].configuration = nconfig

        return name

    def normalized_configs_change_time(self, index, new_time):
        """Change the time of an existing config either by index or name."""
        names = self.normalized_configs_names
        if isinstance(index, str):
            index = names.index(index)
        times = self.normalized_configs_times
        times[index] = new_time
        nconfigs = [[times[i], names[i]] for i in range(len(times))]
        self._set_normalized_configs(nconfigs)  # waveform invalidation within
        self._synchronized = False

    @property
    def ramp_dipole_delay(self):
        """Dipole ramp delay."""
        return self._configuration['ramp_dipole']['delay']

    @ramp_dipole_delay.setter
    def ramp_dipole_delay(self, value):
        """Set power supplies general delay [us]."""
        value = float(value)
        if value != self._configuration['ramp_dipole']['delay']:
            self._configuration['ramp_dipole']['delay'] = value
            self._synchronized = False

    @property
    def ramp_dipole_duration(self):
        """Dipole ramp duration."""
        return self._configuration['ramp_dipole']['duration']

    @ramp_dipole_duration.setter
    def ramp_dipole_duration(self, value):
        value = float(value)
        """Set dipole ramp duration."""
        if value != self._configuration['ramp_dipole']['duration']:
            self._configuration['ramp_dipole']['duration'] = value
            self._synchronized = False
            self._invalidate_waveforms(True)

    # @property
    # def ramp_dipole_time(self):
    #     """Dipole ramp times."""
    #     return list(self._configuration['ramp_dipole']['time'])

    # @ramp_dipole_time.setter
    # def ramp_dipole_time(self, value):
    #     """Set dipole ramp times."""
    #     if value == self._configuration['ramp_dipole']['time']:
    #         return
    #     if len(value) != 8:
    #         raise _RampInvalidDipoleWfmParms(
    #             'Invalid number of elements int dipole ramp time')
    #     for v in value:
    #         if v > self.ramp_dipole_duration:
    #             raise _RampInvalidDipoleWfmParms(
    #                 'All dipole ramp times should be '
    #                 'smaller than ramp duration.')
    #     # TODO: verify monotonic ascending times
    #     self._configuration['ramp_dipole']['time'] = list(value)
    #     self._synchronized = False
    #     self._invalidate_waveforms(True)

    # @property
    # def ramp_dipole_energy(self):
    #     """Dipole ramp energy."""
    #     return list(self._configuration['ramp_dipole']['energy'])
    #
    # @ramp_dipole_energy.setter
    # def ramp_dipole_energy(self, value):
    #     """Set dipole ramp energies."""
    #     if value == self._configuration['ramp_dipole']['energy']:
    #         return
    #     if len(value) != 8:
    #         raise _RampInvalidDipoleWfmParms('Invalid number of elements in '
    #                                          'dipole ramp energy')
    #     for v in value:
    #         if v > self.ramp_dipole_duration:
    #             raise _RampInvalidDipoleWfmParms(
    #                 'All dipole ramp times should be '
    #                 'smaller than ramp duration.')
    #     # TODO: verify values
    #     self._configuration['ramp_dipole']['energy'] = list(value)
    #     self._synchronized = False
    #     self._invalidate_waveforms(True)

    @property
    def ramp_dipole_wfm_nrpoints(self):
        """Dipole ramp waveform number of points."""
        rdip = self._configuration['ramp_dipole']
        return rdip['wfm_nrpoints']

    @ramp_dipole_wfm_nrpoints.setter
    def ramp_dipole_wfm_nrpoints(self, value):
        """Set dipole ramp waveform number of points."""
        value = int(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['wfm_nrpoints']:
            if not 1 <= value <= _MAX_WFMSIZE:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid number of points for waveforms.')
            rdip['wfm_nrpoints'] = value
            self._synchronized = False
            self._invalidate_waveforms(True)

    @property
    def ramp_dipole_times(self):
        """Return dipole times."""
        v = (self.rampup_start_time,
             self.rampup_stop_time,
             self.plateau_start_time,
             self.plateau_stop_time,
             self.rampdown_start_time,
             self.rampdown_stop_time,)
        return v

    @property
    def ramp_dipole_energies(self):
        """Return dipole times."""
        v = (self.rampup_start_energy,
             self.rampup_stop_energy,
             self.plateau_energy,
             self.plateau_energy,
             self.rampdown_start_energy,
             self.rampdown_stop_energy,)
        return v

    @property
    def start_energy(self):
        """Return."""
        return self._configuration['ramp_dipole']['start_energy']

    @start_energy.setter
    def start_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['start_energy']:
            self._update_waveform('BO-Fam:MA-B')
            w = self._waveforms['BO-Fam:MA-B']
            w.start_value = value
            if w.invalid:  # triggers update in w
                raise _RampInvalidDipoleWfmParms(
                    'Invalid start_energy')
            rdip['start_energy'] = value
            # TODO: verify values
            self._synchronized = False
            self._invalidate_waveforms(True)

    @property
    def rampup_start_energy(self):
        """Return."""
        return self._configuration['ramp_dipole']['rampup_start_energy']

    @rampup_start_energy.setter
    def rampup_start_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['rampup_start_energy']:
            self._update_waveform('BO-Fam:MA-B')
            w = self._waveforms['BO-Fam:MA-B']
            w.rampup_start_energy = value
            if w.invalid:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid rampup_start_energy')
            rdip['rampup_start_energy'] = value
            # TODO: verify values
            self._synchronized = False
            self._invalidate_waveforms(True)

    @property
    def rampup_start_time(self):
        """Return."""
        return self._configuration['ramp_dipole']['rampup_start_time']

    @rampup_start_time.setter
    def rampup_start_time(self, value):
        """Return."""
        value = float(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['rampup_start_time']:
            self._update_waveform('BO-Fam:MA-B')
            w = self._waveforms['BO-Fam:MA-B']
            w.rampup_start_time = value
            if w.invalid:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid rampup_start_time')
            rdip['rampup_start_time'] = value
            # TODO: > [0] and < [2]
            self._synchronized = False
            self._invalidate_waveforms(True)

    @property
    def rampup_stop_energy(self):
        """Return."""
        return self._configuration['ramp_dipole']['rampup_stop_energy']

    @rampup_stop_energy.setter
    def rampup_stop_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['rampup_stop_energy']:
            self._update_waveform('BO-Fam:MA-B')
            w = self._waveforms['BO-Fam:MA-B']
            w.rampup_stop_energy = value
            if w.invalid:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid rampup_stop_energy')
            rdip['rampup_stop_energy'] = value
            # TODO: verify values
            self._synchronized = False
            self._invalidate_waveforms(True)

    @property
    def rampup_stop_time(self):
        """Return."""
        return self._configuration['ramp_dipole']['rampup_stop_time']

    @rampup_stop_time.setter
    def rampup_stop_time(self, value):
        """Return."""
        value = float(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['rampup_stop_time']:
            self._update_waveform('BO-Fam:MA-B')
            w = self._waveforms['BO-Fam:MA-B']
            w.rampup_stop_time = value
            if w.invalid:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid rampup_stop_time')
            rdip['rampup_stop_time'] = value
            # TODO: > [1] and < [3]
            self._synchronized = False
            self._invalidate_waveforms(True)

    @property
    def plateau_start_time(self):
        """Return."""
        w = self.waveform_get('BO-Fam:MA-B')
        return w.plateau_start_time

    @property
    def plateau_stop_time(self):
        """Return."""
        w = self.waveform_get('BO-Fam:MA-B')
        return w.plateau_stop_time

    @property
    def plateau_energy(self):
        """Return."""
        return self._configuration['ramp_dipole']['plateau_energy']

    @plateau_energy.setter
    def plateau_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['plateau_energy']:
            self._update_waveform('BO-Fam:MA-B')
            w = self._waveforms['BO-Fam:MA-B']
            w.plateau_value = value
            if w.invalid:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid plateau_energy')
            rdip['plateau_energy'] = value
            # TODO: verify values
            self._synchronized = False
            self._invalidate_waveforms(True)

    @property
    def rampdown_start_energy(self):
        """Return."""
        return self._configuration['ramp_dipole']['rampdown_start_energy']

    @rampdown_start_energy.setter
    def rampdown_start_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['rampdown_start_energy']:
            self._update_waveform('BO-Fam:MA-B')
            w = self._waveforms['BO-Fam:MA-B']
            w.rampdown_start_energy = value
            if w.invalid:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid rampdown_start_energy')
            rdip['rampdown_start_energy'] = value
            # TODO: verify values
            self._synchronized = False
            self._invalidate_waveforms(True)

    @property
    def rampdown_start_time(self):
        """Return."""
        return self._configuration['ramp_dipole']['rampdown_start_time']

    @rampdown_start_time.setter
    def rampdown_start_time(self, value):
        """Return."""
        value = float(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['rampdown_start_time']:
            self._update_waveform('BO-Fam:MA-B')
            w = self._waveforms['BO-Fam:MA-B']
            w.rampdown_start_time = value
            if w.invalid:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid rampdown_start_time')
            rdip['rampdown_start_time'] = value
            # TODO: > [4] and < [6]
            self._synchronized = False
            self._invalidate_waveforms(True)

    @property
    def rampdown_stop_energy(self):
        """Return."""
        return self._configuration['ramp_dipole']['rampdown_stop_energy']

    @rampdown_stop_energy.setter
    def rampdown_stop_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['rampdown_stop_energy']:
            self._update_waveform('BO-Fam:MA-B')
            w = self._waveforms['BO-Fam:MA-B']
            w.rampdown_stop_energy = value
            if w.invalid:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid rampdown_stop_energy')
            rdip['rampdown_stop_energy'] = value
            # TODO: verify values
            self._synchronized = False
            self._invalidate_waveforms(True)

    @property
    def rampdown_stop_time(self):
        """Return."""
        return self._configuration['ramp_dipole']['rampdown_stop_time']

    @rampdown_stop_time.setter
    def rampdown_stop_time(self, value):
        """Return."""
        value = float(value)
        rdip = self._configuration['ramp_dipole']
        if value != rdip['rampdown_stop_time']:
            self._update_waveform('BO-Fam:MA-B')
            w = self._waveforms['BO-Fam:MA-B']
            w.rampdown_stop_time = value
            if w.invalid:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid rampdown_stop_time')
            rdip['rampdown_stop_time'] = value
            # TODO: > [5] and < [7]
            self._synchronized = False
            self._invalidate_waveforms(True)

    def check_value(self):
        """Check current configuration."""
        # firs check ramp config
        if not _ConfigSrv.check_value(self):
            return False
        # then check each normalized config
        for config in self._nconfigs.values():
            if not config.check_value():
                return False
        return True

    # --- API for waveforms ---

    @property
    def waveform_anomalies(self):
        """Waveform anomalies."""
        self._update_waveform('BO-Fam:MA-B')
        dip_wfm = self._waveforms['BO-Fam:MA-B']
        return dip_wfm.anomalies

    def waveform_get(self, maname):
        """Return waveform for a given power supply."""
        self._update_waveform(maname)
        waveform = self._waveforms[maname]
        return _dcopy(waveform)

    def waveform_set(self, maname, waveform):
        """Set waveform for a given power supply."""
        # self._update_waveform(maname)
        self._waveforms[maname] = _dcopy(waveform)

    def waveform_get_times(self):
        """Return ramp energy at a given time."""
        maname = 'BO-Fam:MA-B'
        self._update_waveform(maname)
        times = self._waveforms[maname].times
        return times

    def waveform_get_currents(self, maname):
        """Return waveform current for a given power supply."""
        self._update_waveform(maname)
        waveform = self._waveforms[maname]
        return waveform.currents.copy()

    def waveform_get_strengths(self, maname):
        """Return waveform strength for a given power supply."""
        self._update_waveform(maname)
        waveform = self._waveforms[maname]
        return waveform.strengths.copy()

    def waveform_interp_strengths(self, maname, time):
        """Return ramp strength at a given time."""
        times = self.waveform_get_times()
        strengths = self._waveforms[maname].strengths
        strength = _np.interp(time, times, strengths)
        return strength

    def waveform_interp_energy(self, time):
        """Return ramp energy at a given time."""
        return self.waveform_interp_strengths('BO-Fam:MA-B', time)

    # --- private methods ---

    def __len__(self):
        """Return number of normalized configurations."""
        return len(self._nconfigs)

    def __str__(self):
        """Return string representation of configuration."""
        if not self._configuration:
            st = 'name: {}'.format(self.name)
            return st
        labels = (
            'delay_rf [us]',
            'ramp_dipole_delay [us]',
            'ramp_dipole_duration [ms]',
            'ramp_dipole_time_energy [ms] [GeV]',
            'injection_time [ms]',
            'ejection_time [ms]',
            'normalized_configs [ms] [name]',
        )
        st = ''
        maxlen = max(tuple(len(l) for l in labels) + (len('name'),))
        strfmt1 = '{:<' + str(maxlen) + 's}: {}\n'
        strfmt2 = strfmt1.replace('{}', '{:07.3f} {:+08.3f} {:<s}')
        strfmt3 = strfmt1.replace('{}', '{:07.3f} {}')
        strfmt4 = strfmt1.replace('{}', '{:07.3f}')
        st += strfmt1.format('name', self.name)
        st += strfmt1.format(labels[0], self.delay_rf)
        st += strfmt1.format(labels[1], self.ramp_dipole_delay)
        st += strfmt1.format(labels[2], self.ramp_dipole_duration)
        st += strfmt4.format(labels[4], self.injection_time)
        st += strfmt4.format(labels[5], self.ejection_time)
        st += strfmt1.format(labels[3], '')
        st += strfmt2.format('', 0.0, self.start_energy, '(start)')
        st += strfmt2.format('', self.rampup_start_time,
                             self.rampup_start_energy, '(rampup_start)')
        st += strfmt2.format('', self.rampup_stop_time,
                             self.rampup_stop_energy, '(rampup_stop)')
        st += strfmt2.format('', self.plateau_start_time,
                             self.plateau_energy, '(plateau_start)')
        st += strfmt2.format('', self.plateau_stop_time,
                             self.plateau_energy,  '(plateau_stop)')
        st += strfmt2.format('', self.rampdown_start_time,
                             self.rampdown_start_energy,  '(rampdown_start)')
        st += strfmt2.format('', self.rampdown_stop_time,
                             self.rampdown_stop_energy, '(rampdown_stop)')
        st += strfmt2.format('', self.ramp_dipole_duration,
                             self.start_energy, '(stop)')
        st += strfmt1.format(labels[6], '')
        time = self.normalized_configs_times
        name = self.normalized_configs_names
        for i in range(len(time)):
            st += strfmt3.format('', time[i], name[i])
        return st

    def _get_item(self, name):
        return _dcopy(self._nconfigs[name])

    def _set_item(self, name, value):
        self._nconfigs[name] = value
        self._invalidate_waveforms()

    def _set_configuration(self, value):
        self._configuration = _dcopy(value)
        self._update_normalized_configs_objects()

    def _set_normalized_configs(self, value):
        """Set normalized config list."""
        self._configuration['normalized_configs*'] = _dcopy(value)
        self._update_normalized_configs_objects()

    def _update_normalized_configs_objects(self):
        norm_configs = dict()
        for time, name in self._configuration['normalized_configs*']:
            if name in self._nconfigs:
                norm_configs[name] = self._nconfigs[name]
            else:
                self._synchronized = False
                self._invalidate_waveforms()
                norm_configs[name] = BoosterNormalized(name)
        self._nconfigs = norm_configs

    def _update_waveform(self, maname):

        # update dipole if necessary
        if 'BO-Fam:M-B' not in self._waveforms:
            self._update_waveform_dipole()

        # update family if necessary
        family = _get_magnet_family_name(maname)
        if family is not None and family not in self._waveforms:
            self._update_waveform(family)

        # update magnet waveform if it is not a dipole
        dipole = _get_section_dipole_name(maname)
        if dipole is not None and maname not in self._waveforms:
            self._update_waveform_not_dipole(maname, dipole, family)

    def _update_waveform_not_dipole(self, maname, dipole, family=None):
        # sort normalized configs
        self._update_normalized_configs_objects()
        nconf_times = self.normalized_configs_times
        nconf_names = self.normalized_configs_names
        nconf_times, nconf_names = \
            [list(x) for x in zip(*sorted(zip(nconf_times, nconf_names),
             key=lambda pair: pair[0]))]  # sort by time

        # build strength
        nconf_strength = []
        for i in range(len(nconf_times)):
            nconfig = self._nconfigs[nconf_names[i]]
            if maname not in nconfig.configuration:
                raise _RampInvalidNormConfig
            nconf_strength.append(nconfig[maname])

        # interpolate strengths
        wfm_nrpoints = self._configuration['ramp_dipole']['wfm_nrpoints']
        nconf_indices = self._conv_times_2_indices(nconf_times)
        wfm_indices = [i for i in range(wfm_nrpoints)]
        wfm_strengths = _np.interp(wfm_indices, nconf_indices, nconf_strength)

        # create waveform object with given strengths
        dipole = self._waveforms[dipole]
        if family is not None:
            family = self._waveforms[family]
        self._waveforms[maname] = _Waveform(maname=maname,
                                            dipole=dipole,
                                            family=family,
                                            strengths=wfm_strengths)

    # def _update_waveform_dipole(self):
    #     time = self._configuration['ramp_dipole']['time']
    #     energy = self._configuration['ramp_dipole']['energy']
    #     duration = self._configuration['ramp_dipole']['duration']
    #     wfm_nrpoints = self._configuration['ramp_dipole']['wfm_nrpoints']
    #     indices = self._conv_times_2_indices(time)
    #     dipole = _WaveformDipole(
    #         scale=1.0,
    #         start_value=energy[0],
    #         stop_value=energy[0],
    #         boundary_indices=indices,
    #         boundary_values=energy,
    #         wfm_nrpoints=wfm_nrpoints,
    #         duration=duration)
    #     if not dipole.check():
    #         raise _RampInvalidDipoleWfmParms()
    #     self._waveforms['BO-Fam:MA-B'] = dipole

    def _update_waveform_dipole(self):
        rdip = self._configuration['ramp_dipole']
        dipole = _WaveformDipole(
            maname='BO-Fam:MA-B',
            wfm_nrpoints=rdip['wfm_nrpoints'],
            duration=rdip['duration'],
            start_energy=rdip['start_energy'],
            rampup_start_time=rdip['rampup_start_time'],
            rampup_start_energy=rdip['rampup_start_energy'],
            rampup_stop_time=rdip['rampup_stop_time'],
            rampup_stop_energy=rdip['rampup_stop_energy'],
            plateau_energy=rdip['plateau_energy'],
            rampdown_start_time=rdip['rampdown_start_time'],
            rampdown_start_energy=rdip['rampdown_start_energy'],
            rampdown_stop_time=rdip['rampdown_stop_time'],
            rampdown_stop_energy=rdip['rampdown_stop_energy'])
        if dipole.invalid:
            raise _RampInvalidDipoleWfmParms()
        self._waveforms['BO-Fam:MA-B'] = dipole

    def _conv_times_2_indices(self, times):
        rdip = self._configuration['ramp_dipole']
        duration = rdip['duration']
        wfm_nrpoints = rdip['wfm_nrpoints']
        interval = duration / (wfm_nrpoints - 1.0)
        indices = [t/interval for t in times]
        return indices

    def _invalidate_waveforms(self, include_dipole=False):
        manames = tuple(self._waveforms.keys())
        for maname in manames:
            if maname != 'BO-Fam:MA-B' or include_dipole:
                del(self._waveforms[maname])
