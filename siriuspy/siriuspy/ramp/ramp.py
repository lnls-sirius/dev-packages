"""Module with BO ramp and SI mig classes."""

import numpy as _np
from copy import deepcopy as _dcopy

from siriuspy.csdevice.pwrsupply import MAX_WFMSIZE as _MAX_WFMSIZE
from siriuspy.search import MASearch as _MASearch
from siriuspy.namesys import SiriusPVName
from siriuspy.clientconfigdb import ConfigDBDocument as _ConfigDBDocument
from siriuspy.magnet.util import \
    get_section_dipole_name as _get_section_dipole_name, \
    get_magnet_family_name as _get_magnet_family_name
from siriuspy.ramp.exceptions import \
    RampInvalidDipoleWfmParms as _RampInvalidDipoleWfmParms, \
    RampInvalidNormConfig as _RampInvalidNormConfig, \
    RampInvalidRFParms as _RampInvalidRFParms
from siriuspy.ramp.util import MAX_RF_RAMP_DURATION as _MAX_RF_RAMP_DURATION
from siriuspy.ramp.waveform import \
    WaveformDipole as _WaveformDipole, \
    Waveform as _Waveform


class BoosterNormalized(_ConfigDBDocument):
    """Booster normalized configuration."""

    def __init__(self, name=None):
        """Constructor."""
        super().__init__('bo_normalized', name=name)
        self._value = self.get_value_template()

        self._manames2index = dict()
        for index, data in enumerate(self._value['pvs']):
            maname = SiriusPVName(data[0]).device_name
            self._manames2index[maname] = index

    @property
    def manames(self):
        """List of power supply names."""
        return list(self._manames2index.keys())

    def _get_item(self, maname):
        index = self._manames2index[maname]
        value = self._value['pvs'][index][1]
        return float(value)

    def _set_item(self, maname, value):
        index = self._manames2index[maname]
        self._value['pvs'][index][1] = value

    def __str__(self):
        """Return string representation of configuration."""
        if not self._value:
            st = 'name: {}'.format(self.name)
            return st
        st = ''
        k = [data[0] for data in self._value['pvs']]
        v1 = [data[1] for data in self._value['pvs']]
        v2 = [data[2] for data in self._value['pvs']]
        maxlen = max(tuple(len(ky) for ky in k) + (len('name'),))
        fmtstr1 = '{:<'+str(maxlen)+'}, {:+.6f}, {:+.6f}\n'
        fmtstr2 = '{:<'+str(maxlen)+'}: {}\n'
        st = fmtstr2.format('name', self.name)
        for i in range(len(k)):
            st += fmtstr1.format(k[i], v1[i], v2[i])
        return st


class BoosterRamp(_ConfigDBDocument):
    """Booster ramp class."""

    # Dipole maname
    MANAME_DIPOLE = 'BO-Fam:MA-B'

    def __init__(self, name=None, auto_update=False):
        """Constructor."""
        super().__init__('bo_ramp', name=name)
        self._auto_update = auto_update
        self._ps_nconfigs = dict()
        self._ps_waveforms = dict()
        self.value = self.get_value_template()

    # --- ConfigSrv API ---

    @property
    def synchronized(self):
        """Return synchronization state between object and config in server."""
        if not self._synchronized:
            return False
        for config in self._ps_nconfigs.values():
            if not config.synchronized:
                return False
        return True

    def load(self):
        """Load configuration from config server."""
        # load booster ramp configuration
        super().load()
        self._synchronized = False  # in case cannot load ps norm config
        # update ps normalized configs
        self._update_ps_normalized_configs_objects()
        # load ps normalized configurations one by one
        for config in self._ps_nconfigs.values():
            config.load()
        self._synchronized = True  # all went well
        self._invalidate_ps_waveforms(True)

    def load_normalized_configs(self):
        """Load ps normalized configurations from config server."""
        # load ps normalized configurations one by one
        for config in self._ps_nconfigs.values():
            config.load()
        self._invalidate_ps_waveforms()

    def save(self, new_name=None):
        """Save configuration to config server."""
        # save each ps normalized configuration
        for config in self._ps_nconfigs.values():
            if config.exist():
                if self._check_ps_normalized_modified(config):
                    # save changes in an existing normalized config
                    old_nconfig_name = config.name
                    new_nconfig_name = config.generate_config_name(
                        old_nconfig_name)
                    config.save(new_nconfig_name)

                    # replace old config from normalized configs dict
                    del(self._ps_nconfigs[old_nconfig_name])
                    self._ps_nconfigs[new_nconfig_name] = config

                    # replace old name in normalized configs list
                    nconfigs = self.ps_normalized_configs
                    for i in range(len(nconfigs)):
                        if nconfigs[i][1] == old_nconfig_name:
                            nconfigs[i][1] = new_nconfig_name
                    self._value['ps_normalized_configs*'] = nconfigs
            else:
                config.save()

        # save booster ramp
        super().save(new_name)

        self._synchronized = True  # all went well

    # ---- ps_normalized_configs ----

    @property
    def ps_normalized_configs(self):
        """List of ps normalized config."""
        return _dcopy(self._value['ps_normalized_configs*'])

    @property
    def ps_normalized_configs_times(self):
        """Return time instants corresponding to ps normalized configs."""
        time, _ = zip(*self._value['ps_normalized_configs*'])
        return list(time)

    @property
    def ps_normalized_configs_names(self):
        """Return names corresponding to ps normalized configs."""
        _, name = zip(*self._value['ps_normalized_configs*'])
        return list(name)

    def ps_normalized_configs_delete(self, index):
        """Delete a ps normalized config either by its index or its name."""
        names = self.ps_normalized_configs_names
        if isinstance(index, str):
            index = names.index(index)
        times = self.ps_normalized_configs_times
        names.pop(index)
        times.pop(index)
        nconfigs = [[times[i], names[i]] for i in range(len(times))]
        self._set_ps_normalized_configs(nconfigs)
        self._synchronized = False
        self._invalidate_ps_waveforms()

    def ps_normalized_configs_insert(self, time, name=None, nconfig=None):
        """Insert a ps normalized configuration."""
        # process ps normalized config name
        if not isinstance(name, str) or len(name) == 0:
            name = self.generate_config_name()

        # add new entry to list with ps normalized configs metadata
        otimes = self.ps_normalized_configs_times
        onames = self.ps_normalized_configs_names
        times = otimes.copy()
        names = onames.copy()
        if time in times:
            if nconfig is not None:
                index = times.index(time)
                names[index] = name
            else:
                raise _RampInvalidNormConfig(
                    'There is already a configuration at this time.')
        else:
            times.append(time)
            names.append(name)
        times, names = \
            [list(x) for x in zip(*sorted(zip(times, names),
             key=lambda pair: pair[0]))]  # sort by time
        nconfigs = [[times[i], names[i]] for i in range(len(times))]

        # triggers updates for new ps normalized configs table
        self._set_ps_normalized_configs(nconfigs)

        # interpolate nconfig, if necessary
        if nconfig is None:
            for ma in self._ps_nconfigs[name].manames:
                if ma == self.MANAME_DIPOLE:
                    continue
                ovalues = [self._ps_nconfigs[n][ma] for n in onames]
                self._ps_nconfigs[name][ma] = _np.interp(time, otimes, ovalues)

            self._update_ps_normalized_config_energy(
                self._ps_nconfigs[name], time)
        else:
            self._ps_nconfigs[name].value = nconfig

        return name

    def ps_normalized_configs_change_time(self, index, new_time,
                                          change_energy=False):
        """Change the time of an existing config either by index or name."""
        names = self.ps_normalized_configs_names
        if isinstance(index, str):
            name = index
            index = names.index(name)
        else:
            name = names[index]
        times = self.ps_normalized_configs_times
        times[index] = new_time

        # set config energy appropriately if needed
        if change_energy:
            self._update_ps_normalized_config_energy(
                self._ps_nconfigs[name], new_time)

        nconfigs = [[times[i], names[i]] for i in range(len(times))]
        self._set_ps_normalized_configs(nconfigs)  # with waveform invalidation
        self._synchronized = False

    # ---- ps ramp parameters ----

    @property
    def ps_ramp_duration(self):
        """Power supplies ramp duration."""
        return self._value['ps_ramp']['duration']

    @ps_ramp_duration.setter
    def ps_ramp_duration(self, value):
        """Set power supplies duration."""
        value = float(value)
        if value != self._value['ps_ramp']['duration']:
            if not self.ps_ramp_rampdown_stop_time < value:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid duration for waveforms.')
            self._value['ps_ramp']['duration'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_wfm_nrpoints(self):
        """Power supplies waveform number of points."""
        rdip = self._value['ps_ramp']
        return rdip['wfm_nrpoints']

    @ps_ramp_wfm_nrpoints.setter
    def ps_ramp_wfm_nrpoints(self, value):
        """Set power supplies waveform number of points."""
        value = int(value)
        rdip = self._value['ps_ramp']
        if value != rdip['wfm_nrpoints']:
            if not 1 <= value <= _MAX_WFMSIZE:
                raise _RampInvalidDipoleWfmParms(
                    'Invalid number of points for waveforms.')
            rdip['wfm_nrpoints'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_times(self):
        """Return ps ramp times."""
        v = (self.ps_ramp_rampup_start_time,
             self.ps_ramp_rampup_stop_time,
             self.ps_ramp_plateau_start_time,
             self.ps_ramp_plateau_stop_time,
             self.ps_ramp_rampdown_start_time,
             self.ps_ramp_rampdown_stop_time,)
        return v

    @property
    def ps_ramp_energies(self):
        """Return ps ramp times."""
        v = (self.ps_ramp_rampup_start_energy,
             self.ps_ramp_rampup_stop_energy,
             self.ps_ramp_plateau_energy,
             self.ps_ramp_plateau_energy,
             self.ps_ramp_rampdown_start_energy,
             self.ps_ramp_rampdown_stop_energy,)
        return v

    @property
    def ps_ramp_start_energy(self):
        """Return."""
        return self._value['ps_ramp']['start_energy']

    @ps_ramp_start_energy.setter
    def ps_ramp_start_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['start_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.start_energy = value
            self._verify_ps_waveform_invalid(w, 'start_energy')
            if self._auto_update:
                w.strengths  # triggers waveform interpolation

            rdip['start_energy'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampup_start_energy(self):
        """Return."""
        return self._value['ps_ramp']['rampup_start_energy']

    @ps_ramp_rampup_start_energy.setter
    def ps_ramp_rampup_start_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampup_start_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.rampup_start_energy = value
            self._verify_ps_waveform_invalid(w, 'rampup_start_energy')
            if self._auto_update:
                w.strengths  # triggers waveform interpolation

            rdip['rampup_start_energy'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampup_start_time(self):
        """Return."""
        return self._value['ps_ramp']['rampup_start_time']

    @ps_ramp_rampup_start_time.setter
    def ps_ramp_rampup_start_time(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampup_start_time']:
            w = self._create_new_ps_waveform_dipole()
            w.rampup_start_time = value
            self._verify_ps_waveform_invalid(w, 'rampup_start_time')
            if self._auto_update:
                w.strengths  # triggers waveform interpolation

            rdip['rampup_start_time'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampup_stop_energy(self):
        """Return."""
        return self._value['ps_ramp']['rampup_stop_energy']

    @ps_ramp_rampup_stop_energy.setter
    def ps_ramp_rampup_stop_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampup_stop_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.rampup_stop_energy = value
            self._verify_ps_waveform_invalid(w, 'rampup_stop_energy')
            if self._auto_update:
                w.strengths  # triggers waveform interpolation

            rdip['rampup_stop_energy'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampup_stop_time(self):
        """Return."""
        return self._value['ps_ramp']['rampup_stop_time']

    @ps_ramp_rampup_stop_time.setter
    def ps_ramp_rampup_stop_time(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampup_stop_time']:
            w = self._create_new_ps_waveform_dipole()
            w.rampup_stop_time = value
            self._verify_ps_waveform_invalid(w, 'rampup_stop_time')
            if self._auto_update:
                w.strengths  # triggers waveform interpolation

            rdip['rampup_stop_time'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_plateau_start_time(self):
        """Return."""
        w = self.ps_waveform_get(self.MANAME_DIPOLE)
        return w.plateau_start_time

    @property
    def ps_ramp_plateau_stop_time(self):
        """Return."""
        w = self.ps_waveform_get(self.MANAME_DIPOLE)
        return w.plateau_stop_time

    @property
    def ps_ramp_plateau_energy(self):
        """Return."""
        return self._value['ps_ramp']['plateau_energy']

    @ps_ramp_plateau_energy.setter
    def ps_ramp_plateau_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['plateau_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.plateau_energy = value
            self._verify_ps_waveform_invalid(w, 'plateau_energy')
            if self._auto_update:
                w.strengths  # triggers waveform interpolation

            rdip['plateau_energy'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampdown_start_energy(self):
        """Return."""
        return self._value['ps_ramp']['rampdown_start_energy']

    @ps_ramp_rampdown_start_energy.setter
    def ps_ramp_rampdown_start_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampdown_start_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.rampdown_start_energy = value
            self._verify_ps_waveform_invalid(w, 'rampdown_start_energy')
            if self._auto_update:
                w.strengths  # triggers waveform interpolation

            rdip['rampdown_start_energy'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampdown_start_time(self):
        """Return."""
        return self._value['ps_ramp']['rampdown_start_time']

    @ps_ramp_rampdown_start_time.setter
    def ps_ramp_rampdown_start_time(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampdown_start_time']:
            w = self._create_new_ps_waveform_dipole()
            w.rampdown_start_time = value
            self._verify_ps_waveform_invalid(w, 'rampdown_start_time')
            if self._auto_update:
                w.strengths  # triggers waveform interpolation

            rdip['rampdown_start_time'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampdown_stop_energy(self):
        """Return."""
        return self._value['ps_ramp']['rampdown_stop_energy']

    @ps_ramp_rampdown_stop_energy.setter
    def ps_ramp_rampdown_stop_energy(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampdown_stop_energy']:
            w = self._create_new_ps_waveform_dipole()
            w.rampdown_stop_energy = value
            self._verify_ps_waveform_invalid(w, 'rampdown_stop_energy')
            if self._auto_update:
                w.strengths  # triggers waveform interpolation

            rdip['rampdown_stop_energy'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    @property
    def ps_ramp_rampdown_stop_time(self):
        """Return."""
        return self._value['ps_ramp']['rampdown_stop_time']

    @ps_ramp_rampdown_stop_time.setter
    def ps_ramp_rampdown_stop_time(self, value):
        """Return."""
        value = float(value)
        rdip = self._value['ps_ramp']
        if value != rdip['rampdown_stop_time']:
            w = self._create_new_ps_waveform_dipole()
            w.rampdown_stop_time = value
            self._verify_ps_waveform_invalid(w, 'rampdown_stop_time')
            if self._auto_update:
                w.strengths  # triggers waveform interpolation

            rdip['rampdown_stop_time'] = value
            self._synchronized = False
            self._invalidate_ps_waveforms(True)

    # ---- rf ramp parameters ----

    @property
    def rf_ramp_duration(self):
        """RF ramp duration."""
        d = self.rf_ramp_bottom_duration + \
            self.rf_ramp_rampup_duration + \
            self.rf_ramp_top_duration + \
            self.rf_ramp_rampdown_duration
        return d

    @property
    def rf_ramp_times(self):
        """Time instants to define RF ramp."""
        t = (self.ti_params_rf_ramp_delay,      # = RF ramp start, bottom start
             self.rf_ramp_rampup_start_time,    # = RF bottom stop
             self.rf_ramp_rampup_stop_time,     # = RF top start
             self.rf_ramp_rampdown_start_time,  # = RF top stop
             self.rf_ramp_duration)             # = RF rampdown stop
        return t

    @property
    def rf_ramp_voltages(self):
        """List of voltages to define RF ramp."""
        v = (self.rf_ramp_bottom_voltage,
             self.rf_ramp_bottom_voltage,
             self.rf_ramp_top_voltage,
             self.rf_ramp_top_voltage,
             self.rf_ramp_bottom_voltage)
        return v

    @property
    def rf_ramp_phases(self):
        """List of phases to define RF ramp."""
        p = (self.rf_ramp_bottom_phase,
             self.rf_ramp_bottom_phase,
             self.rf_ramp_top_phase,
             self.rf_ramp_top_phase,
             self.rf_ramp_bottom_phase)
        return p

    def rf_ramp_interp_voltages(self, time):
        """Return voltages related to times."""
        v = _np.interp(time, self.rf_ramp_times, self.rf_ramp_voltages)
        return v

    @property
    def rf_ramp_rampup_start_time(self):
        """RF ramp rampup start time."""
        t = self.ti_params_rf_ramp_delay + \
            float(self._value['rf_ramp']['bottom_duration'])
        return t

    @rf_ramp_rampup_start_time.setter
    def rf_ramp_rampup_start_time(self, value):
        value = float(value)
        if value == self.rf_ramp_rampup_start_time:
            return
        if not self.ti_params_rf_ramp_delay <= value < \
                self.rf_ramp_rampup_stop_time:
            raise _RampInvalidRFParms('Invalid rampup start time.')

        delay = self.ti_params_rf_ramp_delay
        rampup_stop_time = self.rf_ramp_rampup_stop_time
        self._value['rf_ramp']['bottom_duration'] = \
            value - delay
        self._value['rf_ramp']['rampup_duration'] = \
            rampup_stop_time - value
        self._synchronized = False

    @property
    def rf_ramp_rampup_stop_time(self):
        """RF ramp rampup stop time."""
        t = self.ti_params_rf_ramp_delay + \
            float(self._value['rf_ramp']['bottom_duration']) + \
            float(self._value['rf_ramp']['rampup_duration'])
        return t

    @rf_ramp_rampup_stop_time.setter
    def rf_ramp_rampup_stop_time(self, value):
        value = float(value)
        if value == self.rf_ramp_rampup_stop_time:
            return
        if not self.rf_ramp_rampup_start_time < value <= \
                self.rf_ramp_rampdown_start_time:
            raise _RampInvalidRFParms('Invalid rampup stop time.')

        rampup_start_time = self.rf_ramp_rampup_start_time
        rampdown_start_time = self.rf_ramp_rampdown_start_time
        self._value['rf_ramp']['rampup_duration'] = \
            value - rampup_start_time
        self._value['rf_ramp']['top_duration'] = \
            rampdown_start_time - value
        self._synchronized = False

    @property
    def rf_ramp_rampdown_start_time(self):
        """RF ramp rampdown start time."""
        t = self.ti_params_rf_ramp_delay + \
            float(self._value['rf_ramp']['bottom_duration']) + \
            float(self._value['rf_ramp']['rampup_duration']) + \
            float(self._value['rf_ramp']['top_duration'])
        return t

    @rf_ramp_rampdown_start_time.setter
    def rf_ramp_rampdown_start_time(self, value):
        value = float(value)
        if value == self.rf_ramp_rampdown_start_time:
            return
        if not self.rf_ramp_rampup_stop_time <= value < \
                self.rf_ramp_rampdown_stop_time:
            raise _RampInvalidRFParms('Invalid rampdown start time.')

        rampup_stop_time = self.rf_ramp_rampup_stop_time
        rampdown_stop_time = self.rf_ramp_rampdown_stop_time
        self._value['rf_ramp']['top_duration'] = \
            value - rampup_stop_time
        self._value['rf_ramp']['rampdown_duration'] = \
            rampdown_stop_time - value
        self._synchronized = False

    @property
    def rf_ramp_rampdown_stop_time(self):
        """RF ramp rampdown start time."""
        t = self.ti_params_rf_ramp_delay + \
            float(self._value['rf_ramp']['bottom_duration']) + \
            float(self._value['rf_ramp']['rampup_duration']) + \
            float(self._value['rf_ramp']['top_duration']) + \
            float(self._value['rf_ramp']['rampdown_duration'])
        return t

    @rf_ramp_rampdown_stop_time.setter
    def rf_ramp_rampdown_stop_time(self, value):
        value = float(value)
        if value == self.rf_ramp_rampdown_stop_time:
            return
        if not self.rf_ramp_rampdown_start_time < value <= \
                self.ti_params_rf_ramp_delay + _MAX_RF_RAMP_DURATION:
            raise _RampInvalidRFParms('Invalid rampdown stop time.')

        rampdown_start_time = self.rf_ramp_rampdown_start_time
        self._value['rf_ramp']['rampdown_duration'] = \
            value - rampdown_start_time
        self._synchronized = False

    @property
    def rf_ramp_bottom_duration(self):
        """Bottom duration, in ms."""
        return self._value['rf_ramp']['bottom_duration']

    @property
    def rf_ramp_rampup_duration(self):
        """Rampup duration, in ms."""
        return self._value['rf_ramp']['rampup_duration']

    @property
    def rf_ramp_top_duration(self):
        """Top duration, in ms."""
        return self._value['rf_ramp']['top_duration']

    @property
    def rf_ramp_rampdown_duration(self):
        """Rampdown duration, in ms."""
        return self._value['rf_ramp']['rampdown_duration']

    @property
    def rf_ramp_bottom_voltage(self):
        """RF ramp bottom voltage, in kV."""
        return self._value['rf_ramp']['bottom_voltage']

    @rf_ramp_bottom_voltage.setter
    def rf_ramp_bottom_voltage(self, value):
        value = float(value)
        if value == self._value['rf_ramp']['bottom_voltage']:
            return
        if not 0 <= value <= self.rf_ramp_top_voltage:
            raise _RampInvalidRFParms('Invalid value to bottom voltage.')

        self._value['rf_ramp']['bottom_voltage'] = value
        self._synchronized = False

    @property
    def rf_ramp_top_voltage(self):
        """RF ramp top voltage, in kV."""
        return self._value['rf_ramp']['top_voltage']

    @rf_ramp_top_voltage.setter
    def rf_ramp_top_voltage(self, value):
        value = float(value)
        if value == self._value['rf_ramp']['top_voltage']:
            return
        if not value >= self._value['rf_ramp']['bottom_voltage']:
            raise _RampInvalidRFParms('Invalid value to top voltage.')

        self._value['rf_ramp']['top_voltage'] = value
        self._synchronized = False

    @property
    def rf_ramp_bottom_phase(self):
        """RF ramp bottom phase, in degrees."""
        return self._value['rf_ramp']['bottom_phase']

    @rf_ramp_bottom_phase.setter
    def rf_ramp_bottom_phase(self, value):
        value = float(value)
        if value == self._value['rf_ramp']['bottom_phase']:
            return
        if not -180 < value < 360:
            raise _RampInvalidRFParms('Invalid value to bottom phase.')

        self._value['rf_ramp']['bottom_phase'] = value
        self._synchronized = False

    @property
    def rf_ramp_top_phase(self):
        """RF ramp top phase, in degrees."""
        return self._value['rf_ramp']['top_phase']

    @rf_ramp_top_phase.setter
    def rf_ramp_top_phase(self, value):
        value = float(value)
        if value == self._value['rf_ramp']['top_phase']:
            return
        if not -180 < value < 360:
            raise _RampInvalidRFParms('Invalid value to top phase.')

        self._value['rf_ramp']['top_phase'] = value
        self._synchronized = False

    @property
    def rf_ramp_rampinc_duration(self):
        """RF ramp ramping increase duration."""
        return self._value['rf_ramp']['rampinc_duration']

    @rf_ramp_rampinc_duration.setter
    def rf_ramp_rampinc_duration(self, value):
        value = float(value)
        if value == self._value['rf_ramp']['rampinc_duration']:
            return
        if not 0.0 < value < 28.0:
            raise _RampInvalidRFParms(
                'Invalid value to ramping increase duration.')

        self._value['rf_ramp']['rampinc_duration'] = value
        self._synchronized = False

    # --- timing parameters ---

    @property
    def ti_params_injection_time(self):
        """Injection time instant."""
        return float(self._value['ti_params']['injection_time'])

    @ti_params_injection_time.setter
    def ti_params_injection_time(self, value):
        """Set injection time instant."""
        # TODO: verify value
        if value == self._value['ti_params']['injection_time']:
            return
        self._value['ti_params']['injection_time'] = value
        self._synchronized = False

    @property
    def ti_params_ejection_time(self):
        """Ejection time instant."""
        return float(self._value['ti_params']['ejection_time'])

    @ti_params_ejection_time.setter
    def ti_params_ejection_time(self, value):
        """Set ejection time instant."""
        # TODO: verify value
        if value == self._value['ti_params']['ejection_time']:
            return
        self._value['ti_params']['ejection_time'] = value
        self._synchronized = False

    @property
    def ti_params_ps_ramp_delay(self):
        """PS ramp delay."""
        return float(self._value['ti_params']['ps_ramp_delay'])

    @ti_params_ps_ramp_delay.setter
    def ti_params_ps_ramp_delay(self, value):
        """Set ps ramp delay [us]."""
        value = float(value)
        if value == self._value['ti_params']['ps_ramp_delay']:
            return
        self._value['ti_params']['ps_ramp_delay'] = value
        self._synchronized = False

    @property
    def ti_params_rf_ramp_delay(self):
        """RF delay."""
        return float(self._value['ti_params']['rf_ramp_delay'])

    @ti_params_rf_ramp_delay.setter
    def ti_params_rf_ramp_delay(self, value):
        """Set RF ramp delay [us]."""
        # TODO: verify value
        if value == self._value['ti_params']['rf_ramp_delay']:
            return
        self._value['ti_params']['rf_ramp_delay'] = value
        self._synchronized = False

    # --- API for waveforms ---

    @property
    def ps_waveform_anomalies(self):
        """Return ps waveform anomalies."""
        self._update_ps_waveform(self.MANAME_DIPOLE)
        w = self._ps_waveforms[self.MANAME_DIPOLE]
        return w.anomalies

    @property
    def ps_waveform_manames_exclimits(self):
        """Return a list of manames whose waveform exceeds current limits."""
        manames = BoosterNormalized().manames
        manames_exclimits = list()
        for maname in manames:
            self._update_ps_waveform(maname)
            w_currents = self._ps_waveforms[maname].currents
            limits = _MASearch.conv_maname_2_splims(maname)
            highlim = limits['HOPR']
            lowlim = limits['LOPR']
            if _np.any(w_currents > highlim) or _np.any(w_currents < lowlim):
                manames_exclimits.append(maname)
        return manames_exclimits

    def ps_waveform_get(self, maname):
        """Return ps waveform for a given power supply."""
        self._update_ps_waveform(maname)
        waveform = self._ps_waveforms[maname]
        return waveform

    def ps_waveform_set(self, maname, waveform):
        """Set ps waveform for a given power supply."""
        # self._update_ps_waveform(maname)
        self._ps_waveforms[maname] = _dcopy(waveform)

    def ps_waveform_get_times(self):
        """Return ramp energy at a given time."""
        self._update_ps_waveform(self.MANAME_DIPOLE)
        times = self._ps_waveforms[self.MANAME_DIPOLE].times
        return times

    def ps_waveform_get_currents(self, maname):
        """Return ps waveform current for a given power supply."""
        self._update_ps_waveform(maname)
        waveform = self._ps_waveforms[maname]
        return waveform.currents.copy()

    def ps_waveform_get_strengths(self, maname):
        """Return ps waveform strength for a given power supply."""
        self._update_ps_waveform(maname)
        waveform = self._ps_waveforms[maname]
        return waveform.strengths.copy()

    def ps_waveform_interp_time(self, energy):
        """Return ps ramp time at a given energy.

        Use only energies until rampup-stop time.
        """
        rampup_stop_time = self.ps_ramp_rampup_stop_time
        times = [time for time in self.ps_waveform_get_times()
                 if time < rampup_stop_time]
        energies = self._ps_waveforms[self.MANAME_DIPOLE].strengths[
                 0:len(times)]
        time = _np.interp(energy, energies, times)
        return time

    def ps_waveform_interp_strengths(self, maname, time):
        """Return ps ramp strength at a given time."""
        times = self.ps_waveform_get_times()
        strengths = self._ps_waveforms[maname].strengths
        strength = _np.interp(time, times, strengths)
        return strength

    def ps_waveform_interp_currents(self, maname, time):
        """Return ps ramp current at a given time."""
        times = self.ps_waveform_get_times()
        currents = self._ps_waveforms[maname].currents
        current = _np.interp(time, times, currents)
        return current

    def ps_waveform_interp_energy(self, time):
        """Return ps ramp energy at a given time."""
        return self.ps_waveform_interp_strengths(self.MANAME_DIPOLE, time)

    # --- private methods ---

    def __len__(self):
        """Return number of ps normalized configurations."""
        return len(self._ps_nconfigs)

    def __str__(self):
        """Return string representation of configuration."""
        if not self._value:
            st = 'name: {}'.format(self.name)
            return st
        labels = (
            'ti_params_rf_ramp_delay [us]',
            'ti_params_ps_ramp_delay [us]',
            'ti_params_injection_time [ms]',
            'ti_params_ejection_time [ms]',
            'ps_ramp_duration [ms]',
            'ps_ramp_time_energy [ms] [GeV]',
            'ps_normalized_configs [ms] [name]',
        )
        st = ''
        maxlen = max(tuple(len(l) for l in labels) + (len('name'),))
        strfmt1 = '{:<' + str(maxlen) + 's}: {}\n'
        strfmt2 = strfmt1.replace('{}', '{:07.3f} {:+08.3f} {:<s}')
        strfmt3 = strfmt1.replace('{}', '{:07.3f} {}')
        strfmt4 = strfmt1.replace('{}', '{:07.3f}')
        st += strfmt1.format('name', self.name)
        st += strfmt1.format(labels[0], self.ti_params_rf_ramp_delay)
        st += strfmt1.format(labels[1], self.ti_params_ps_ramp_delay)
        st += strfmt4.format(labels[2], self.ti_params_injection_time)
        st += strfmt4.format(labels[3], self.ti_params_ejection_time)
        st += strfmt1.format(labels[4], self.ps_ramp_duration)
        st += strfmt1.format(labels[5], '')
        st += strfmt2.format('', 0.0,
                             self.ps_ramp_start_energy, '(start)')
        st += strfmt2.format('', self.ps_ramp_rampup_start_time,
                             self.ps_ramp_rampup_start_energy,
                             '(rampup_start)')
        st += strfmt2.format('', self.ps_ramp_rampup_stop_time,
                             self.ps_ramp_rampup_stop_energy,
                             '(rampup_stop)')
        st += strfmt2.format('', self.ps_ramp_plateau_start_time,
                             self.ps_ramp_plateau_energy,
                             '(plateau_start)')
        st += strfmt2.format('', self.ps_ramp_plateau_stop_time,
                             self.ps_ramp_plateau_energy,
                             '(plateau_stop)')
        st += strfmt2.format('', self.ps_ramp_rampdown_start_time,
                             self.ps_ramp_rampdown_start_energy,
                             '(rampdown_start)')
        st += strfmt2.format('', self.ps_ramp_rampdown_stop_time,
                             self.ps_ramp_rampdown_stop_energy,
                             '(rampdown_stop)')
        st += strfmt2.format('', self.ps_ramp_duration,
                             self.ps_ramp_start_energy, '(stop)')
        st += strfmt1.format(labels[6], '')
        time = self.ps_normalized_configs_times
        name = self.ps_normalized_configs_names
        for i in range(len(time)):
            st += strfmt3.format('', time[i], name[i])
        return st

    def _get_item(self, name):
        return _dcopy(self._ps_nconfigs[name])

    def _set_item(self, name, value):
        self._ps_nconfigs[name] = value
        self._invalidate_ps_waveforms()

    def _set_value(self, value):
        super()._set_value(value)
        self._update_ps_normalized_configs_objects()

    def _set_ps_normalized_configs(self, value):
        """Set ps normalized config list."""
        self._value['ps_normalized_configs*'] = _dcopy(value)
        self._update_ps_normalized_configs_objects()

    def _update_ps_normalized_configs_objects(self):
        norm_configs = dict()
        for _, name in self._value['ps_normalized_configs*']:
            if name in self._ps_nconfigs:
                norm_configs[name] = self._ps_nconfigs[name]
            else:
                self._synchronized = False
                self._invalidate_ps_waveforms()
                norm_configs[name] = BoosterNormalized(name)
        self._ps_nconfigs = norm_configs

    def _update_ps_normalized_config_energy(self, nconfig_obj, time):
        indices = self._conv_times_2_indices([time])
        strengths = self.ps_waveform_get_strengths(self.MANAME_DIPOLE)
        strength = _np.interp(indices[0],
                              list(range(self.ps_ramp_wfm_nrpoints)),
                              strengths)
        nconfig_obj[self.MANAME_DIPOLE] = strength
        return nconfig_obj

    def _update_ps_waveform(self, maname):

        # update dipole if necessary
        if self.MANAME_DIPOLE not in self._ps_waveforms:
            self._update_ps_waveform_dipole()

        # update family if necessary
        family = _get_magnet_family_name(maname)
        if family is not None and family not in self._ps_waveforms:
            self._update_ps_waveform(family)

        # update magnet waveform if it is not a dipole
        dipole = _get_section_dipole_name(maname)
        if dipole is not None and maname not in self._ps_waveforms:
            self._update_ps_waveform_not_dipole(maname, dipole, family)

    def _update_ps_waveform_not_dipole(self, maname, dipole, family=None):
        # sort ps normalized configs
        self._update_ps_normalized_configs_objects()
        nconf_times = self.ps_normalized_configs_times
        nconf_names = self.ps_normalized_configs_names
        nconf_times, nconf_names = \
            [list(x) for x in zip(*sorted(zip(nconf_times, nconf_names),
             key=lambda pair: pair[0]))]  # sort by time

        # build strength
        nconf_strength = []
        for i in range(len(nconf_times)):
            nconfig = self._ps_nconfigs[nconf_names[i]]
            if maname not in nconfig.manames:
                raise _RampInvalidNormConfig()
            nconf_strength.append(nconfig[maname])

        # interpolate strengths
        wfm_nrpoints = self._value['ps_ramp']['wfm_nrpoints']
        nconf_indices = self._conv_times_2_indices(nconf_times)
        wfm_indices = [i for i in range(wfm_nrpoints)]
        wfm_strengths = _np.interp(wfm_indices, nconf_indices, nconf_strength)

        # create waveform object with given strengths
        dipole = self._ps_waveforms[dipole]
        if family is not None:
            family = self._ps_waveforms[family]
        self._ps_waveforms[maname] = _Waveform(maname=maname,
                                               dipole=dipole,
                                               family=family,
                                               strengths=wfm_strengths)

    def _update_ps_waveform_dipole(self):
        dipole = self._create_new_ps_waveform_dipole()
        self._ps_waveforms[self.MANAME_DIPOLE] = dipole

    def _create_new_ps_waveform_dipole(self):
        rdip = self._value['ps_ramp']
        dipole = _WaveformDipole(
            maname=self.MANAME_DIPOLE,
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
        return dipole

    def _conv_times_2_indices(self, times):
        rdip = self._value['ps_ramp']
        duration = rdip['duration']
        wfm_nrpoints = rdip['wfm_nrpoints']
        interval = duration / (wfm_nrpoints - 1.0)
        indices = [t/interval for t in times]
        return indices

    def _invalidate_ps_waveforms(self, include_dipole=False):
        manames = tuple(self._ps_waveforms.keys())
        for maname in manames:
            if maname != self.MANAME_DIPOLE or include_dipole:
                del(self._ps_waveforms[maname])

    def _verify_ps_waveform_invalid(self, waveform, propty=''):
        if propty == '':
            propty = 'parameters'
        if waveform.invalid:  # triggers waveform check invalid parameters
            raise _RampInvalidDipoleWfmParms(
                'Invalid ps waveform {}.'.format(propty))

    def _check_ps_normalized_modified(self, nconfig):
        # load original nconfig from server
        oconfig = BoosterNormalized(name=nconfig.name)
        oconfig.load()

        # compare values. If identical, return False
        for mag in oconfig.manames:
            if oconfig[mag] != nconfig[mag]:
                return True
        return False


class SiriusMig(BoosterRamp):
    """Sirius migration class."""

    MANAME_DIPOLE = 'SI-Fam:MA-B1B2'
